import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_requirements import requirements_document
from test_reviews import review_batch
from feature_parity.cli import main
from feature_parity.comparison import compare_manifests
from feature_parity.reviews import reconcile_manifest
from feature_parity.validation import load_json, validate_manifest, validate_schema


ROOT = Path(__file__).resolve().parents[1]


class RequirementsCliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "requirements.json"
        self.output = self.root / "results"
        self.source.write_text(json.dumps(requirements_document(), indent=2), encoding="utf-8")

    def run_cli(self, *extra):
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        with contextlib.redirect_stdout(self.stdout), contextlib.redirect_stderr(self.stderr):
            return main(["parity", "ingest-requirements", "--source", str(self.source),
                         "--output", str(self.output), *extra])

    def test_import_writes_four_valid_artifacts_and_preserves_source(self):
        original = self.source.read_bytes()
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(self.source.read_bytes(), original)
        self.assertEqual(len(list(self.output.iterdir())), 4)
        baseline = load_json(self.output / "requirements-baseline.json")
        validate_schema(baseline, "feature-requirements-baseline-schema.json")
        validate_manifest(load_json(self.output / "feature-manifest.json"))
        validate_schema(load_json(self.output / "requirements-log.json"), "feature-requirements-log-schema.json")
        self.assertEqual(baseline["sourceDigest"], hashlib.sha256(original).hexdigest())
        self.assertEqual(baseline["evidence"][0]["location"], self.source.name)
        self.assertEqual(json.loads(self.stdout.getvalue())["confirmedFeatures"], 0)

    def test_dry_run_validates_without_creating_output_parent(self):
        self.output = self.root / "missing-parent" / "results"
        self.assertEqual(self.run_cli("--dry-run"), 0)
        self.assertFalse(self.output.parent.exists())

    def test_invalid_batch_never_publishes(self):
        document = requirements_document()
        invalid = dict(document["requirements"][0], id="identity.disable-user", name=" ")
        document["requirements"].append(invalid)
        self.source.write_text(json.dumps(document), encoding="utf-8")
        self.assertEqual(self.run_cli(), 3)
        self.assertFalse(self.output.exists())

    def test_invalid_json_duplicate_keys_and_encoding_fail_safely(self):
        for content in (b'{"schemaVersion":"1.0","schemaVersion":"1.0"}', b'{"number":NaN}', b'\xff', b'not JSON'):
            with self.subTest(content=content):
                self.source.write_bytes(content)
                self.assertEqual(self.run_cli(), 3)
                self.assertFalse(self.output.exists())

    def test_unsupported_formats_require_conversion(self):
        for suffix in (".pdf", ".docx", ".yaml"):
            with self.subTest(suffix=suffix):
                self.source = self.source.with_suffix(suffix)
                self.assertEqual(self.run_cli(), 1)
                self.assertFalse(self.output.exists())

    def test_missing_file_is_access_failure(self):
        self.source.unlink()
        self.assertEqual(self.run_cli(), 2)
        self.assertFalse(self.output.exists())

    def test_sensitive_and_linked_sources_are_excluded(self):
        with patch("feature_parity.requirements.is_link", return_value=True):
            self.assertEqual(self.run_cli(), 5)
        renamed = self.root / "credentials.json"
        self.source.rename(renamed)
        self.source = renamed
        self.assertEqual(self.run_cli(), 5)
        self.assertFalse(self.output.exists())

    def test_oversized_source_is_policy_failure(self):
        self.source.write_bytes(b" " * (1024 * 1024 + 1))
        self.assertEqual(self.run_cli(), 5)
        self.assertFalse(self.output.exists())

    def test_existing_output_and_input_overlap_are_not_overwritten(self):
        self.output.mkdir()
        sentinel = self.output / "keep.txt"
        sentinel.write_text("existing user content", encoding="utf-8")
        self.assertEqual(self.run_cli(), 5)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "existing user content")
        self.output = self.source
        original = self.source.read_bytes()
        self.assertEqual(self.run_cli(), 5)
        self.assertEqual(self.source.read_bytes(), original)

    def test_confirmation_cannot_upgrade_imported_requirements(self):
        self.assertEqual(self.run_cli(), 0)
        imported = load_json(self.output / "feature-manifest.json")
        reviewed = reconcile_manifest(imported, review_batch(imported))["feature-manifest.json"]
        self.assertFalse(reviewed["features"][0]["admitted"])
        self.assertEqual(reviewed["evidence"][0]["verification"], "partially-verified")
        self.assertEqual(compare_manifests(reviewed, reviewed)["statistics"]["equivalentCount"], 0)

    def test_offline_baseline_validation_checks_integrity(self):
        self.assertEqual(self.run_cli(), 0)
        baseline_path = self.output / "requirements-baseline.json"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["parity", "validate", "--requirements-baseline", str(baseline_path)]), 0)
            baseline = load_json(baseline_path)
            baseline["inputDigest"] = "0" * 64
            baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
            self.assertEqual(main(["parity", "validate", "--requirements-baseline", str(baseline_path)]), 3)

    def test_bom_hash_and_line_range_refer_to_exact_parsed_bytes(self):
        content = b"\xef\xbb\xbf" + self.source.read_bytes()
        self.source.write_bytes(content)
        self.assertEqual(self.run_cli(), 0)
        baseline = load_json(self.output / "requirements-baseline.json")
        self.assertEqual(baseline["sourceDigest"], hashlib.sha256(content).hexdigest())
        self.assertEqual(baseline["evidence"][0]["lineEnd"], len(content.decode("utf-8-sig").splitlines()))

    def test_real_ingestion_and_review_export_from_unrelated_directory(self):
        result = subprocess.run([
            sys.executable, "-B", str(ROOT / "cli.py"), "parity", "ingest-requirements",
            "--source", str(self.source), "--output", str(self.output),
        ], cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([
            sys.executable, "-B", str(ROOT / "cli.py"), "parity", "review-template",
            "--manifest", str(self.output / "feature-manifest.json"),
            "--output", str(self.root / "reviews"),
        ], cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(load_json(self.root / "reviews" / "review-decisions.json")["decisions"][0]["approvedReference"], "")


if __name__ == "__main__":
    unittest.main()