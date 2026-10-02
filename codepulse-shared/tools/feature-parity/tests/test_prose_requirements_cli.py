import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import test_validation
from feature_parity.cli import main
from feature_parity.identity import digest
from feature_parity.requirements import validate_requirements_baseline
from feature_parity.validation import ArtifactError, load_json


ROOT = Path(__file__).resolve().parents[1]


class ProseCliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "requirements.md"
        self.output = self.root / "results"
        self.source.write_bytes(b"# Overview\r\n\r\n## Requirement: Create account\r\nAccept a profile.\r\n")

    def run_cli(self, *extra):
        self.stdout = io.StringIO()
        with contextlib.redirect_stdout(self.stdout), contextlib.redirect_stderr(io.StringIO()):
            return main(["parity", "ingest-requirements", "--source", str(self.source),
                         "--output", str(self.output), *extra])

    def test_markdown_records_exact_bytes_and_line_ranges(self):
        original = self.source.read_bytes()
        self.assertEqual(self.run_cli("--application-name", "Synthetic Accounts"), 0)
        baseline = load_json(self.output / "requirements-baseline.json")
        validate_requirements_baseline(baseline)
        self.assertEqual(baseline["document"]["applicationName"], "Synthetic Accounts")
        self.assertEqual(baseline["sourceDigest"], hashlib.sha256(original).hexdigest())
        self.assertEqual([baseline["evidence"][0]["lineStart"], baseline["evidence"][0]["lineEnd"]], [3, 4])
        self.assertEqual(self.source.read_bytes(), original)
        self.assertEqual(json.loads(self.stdout.getvalue())["ambiguousRequirements"], 1)

    def test_text_and_dry_run(self):
        renamed = self.source.with_suffix(".txt")
        self.source.rename(renamed)
        self.source = renamed
        self.assertEqual(self.run_cli("--dry-run"), 0)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.run_cli(), 0)

    def test_unmarked_document_is_incomplete_zero_not_complete_scope(self):
        self.source.write_text("The system shall create accounts.\n", encoding="utf-8")
        self.assertEqual(self.run_cli(), 0)
        baseline = load_json(self.output / "requirements-baseline.json")
        self.assertEqual(baseline["document"]["requirements"], [])
        self.assertEqual(baseline["sourceMap"]["ignoredNonemptyLines"], 1)
        self.assertEqual(baseline["coverage"], "incomplete")

    def test_binary_text_and_invalid_application_label_fail_without_writes(self):
        self.source.write_bytes(b"Requirement: Account\x00")
        self.assertEqual(self.run_cli(), 3)
        self.assertFalse(self.output.exists())
        self.source.write_text("Requirement: Account", encoding="utf-8")
        self.assertEqual(self.run_cli("--application-name", " "), 3)
        self.assertFalse(self.output.exists())

    def test_mandatory_claim_and_range_tampering_fail_validation(self):
        self.assertEqual(self.run_cli(), 0)
        path = self.output / "requirements-baseline.json"
        for mutation in ("mandatory", "range"):
            baseline = load_json(path)
            if mutation == "mandatory":
                baseline["document"]["requirements"][0]["behaviors"][0]["mandatory"] = True
                baseline["inputDigest"] = digest(baseline["document"])
            else:
                baseline["evidence"][0]["lineStart"] = 1
            with self.subTest(mutation=mutation), self.assertRaises(ArtifactError):
                validate_requirements_baseline(baseline)

    def test_real_cli_ingest_and_offline_validate(self):
        result = subprocess.run([
            sys.executable, "-B", str(ROOT / "cli.py"), "parity", "ingest-requirements",
            "--source", str(self.source), "--output", str(self.output),
        ], cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([
            sys.executable, "-B", str(ROOT / "cli.py"), "parity", "validate",
            "--requirements-baseline", str(self.output / "requirements-baseline.json"),
        ], cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)