import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_requirements_coverage import reviewed_baseline
from test_comparison import approve
from test_validation import manifest
from feature_parity.cli import main
from feature_parity.validation import load_json, validate_schema


ROOT = Path(__file__).resolve().parents[1]


class CoverageCliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        baseline, reviews = reviewed_baseline()
        self.baseline = self.root / "baseline.json"
        self.reviews = self.root / "reviews.json"
        self.target = self.root / "target.json"
        for path, document in ((self.baseline, baseline), (self.reviews, reviews), (self.target, approve(manifest()))):
            path.write_text(json.dumps(document), encoding="utf-8")
        self.output = self.root / "results"

    def run_cli(self, *extra, template=False):
        arguments = ["parity", "requirements-review-template" if template else "cover-requirements",
                     "--baseline", str(self.baseline), "--output", str(self.output)]
        if not template:
            arguments.extend(["--reviews", str(self.reviews), "--target", str(self.target)])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main([*arguments, *extra])

    def test_coverage_writes_valid_results_without_mutating_inputs(self):
        original = [path.read_bytes() for path in (self.baseline, self.reviews, self.target)]
        self.assertEqual(self.run_cli("--fail-on", "unverified"), 0)
        result = load_json(self.output / "requirements-coverage.json")
        validate_schema(result, "feature-requirements-coverage-schema.json")
        validate_schema(load_json(self.output / "requirements-comparison-log.json"), "feature-requirements-comparison-log-schema.json")
        self.assertEqual(result["statistics"]["coveragePercent"], 100)
        self.assertEqual([path.read_bytes() for path in (self.baseline, self.reviews, self.target)], original)
        self.assertEqual(len(list(self.output.iterdir())), 3)

    def test_gate_failure_is_after_persistence(self):
        reviews = load_json(self.reviews)
        reviews["decisions"] = []
        self.reviews.write_text(json.dumps(reviews), encoding="utf-8")
        self.assertEqual(self.run_cli("--fail-on", "unverified"), 6)
        self.assertTrue((self.output / "requirements-coverage.json").exists())

    def test_stale_reviews_fail_without_writes(self):
        reviews = load_json(self.reviews)
        reviews["baselineDigest"] = "0" * 64
        self.reviews.write_text(json.dumps(reviews), encoding="utf-8")
        self.assertEqual(self.run_cli(), 3)
        self.assertFalse(self.output.exists())

    def test_dry_run_and_existing_output(self):
        self.assertEqual(self.run_cli("--dry-run"), 0)
        self.assertFalse(self.output.exists())
        self.output.mkdir()
        self.assertEqual(self.run_cli(), 5)

    def test_unapproved_template_is_rejected(self):
        self.assertEqual(self.run_cli(template=True), 0)
        exported = self.output / "requirements-reviews.json"
        self.reviews = exported
        self.output = self.root / "coverage"
        self.assertEqual(self.run_cli(), 3)
        self.assertFalse(self.output.exists())

    def test_missing_reviews_is_access_failure(self):
        self.reviews.unlink()
        self.assertEqual(self.run_cli(), 2)

    def test_real_entry_point_from_unrelated_directory(self):
        completed = subprocess.run([
            sys.executable, "-B", str(ROOT / "cli.py"), "parity", "cover-requirements",
            "--baseline", str(self.baseline), "--reviews", str(self.reviews),
            "--target", str(self.target), "--output", str(self.output), "--fail-on", "unverified",
        ], cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["coveredCount"], 1)