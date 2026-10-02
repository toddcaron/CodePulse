import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from test_validation import manifest
from test_reviews import review_batch
from feature_parity.cli import main
from feature_parity.validation import load_json, validate_manifest, validate_schema


class ReviewCliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.manifest_path = self.root / "manifest.json"
        self.reviews_path = self.root / "reviews.json"
        self.output = self.root / "reviewed"
        document = manifest()
        self.manifest_path.write_text(json.dumps(document), encoding="utf-8")
        self.reviews_path.write_text(json.dumps(review_batch(document)), encoding="utf-8")

    def run_cli(self, *extra, command="reconcile"):
        argv = ["parity", command, "--manifest", str(self.manifest_path), "--output", str(self.output)]
        if command == "reconcile":
            argv.extend(["--reviews", str(self.reviews_path)])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main([*argv, *extra])

    def test_reconcile_writes_valid_new_artifacts(self):
        original = self.manifest_path.read_bytes()
        self.assertEqual(self.run_cli(), 0)
        reviewed = load_json(self.output / "feature-manifest.json")
        validate_manifest(reviewed)
        self.assertEqual(reviewed["features"][0]["status"], "confirmed")
        validate_schema(load_json(self.output / "reconciliation-log.json"), "feature-reconciliation-log-schema.json")
        self.assertEqual(self.manifest_path.read_bytes(), original)
        self.assertEqual(len(list(self.output.iterdir())), 3)

    def test_stale_reviews_fail_before_writing(self):
        batch = load_json(self.reviews_path)
        batch["baseManifestDigest"] = "0" * 64
        self.reviews_path.write_text(json.dumps(batch), encoding="utf-8")
        self.assertEqual(self.run_cli(), 3)
        self.assertFalse(self.output.exists())

    def test_dry_run_does_not_write(self):
        self.assertEqual(self.run_cli("--dry-run"), 0)
        self.assertFalse(self.output.exists())

    def test_existing_output_never_overwritten(self):
        self.output.mkdir()
        self.assertEqual(self.run_cli(), 5)

    def test_missing_reviews_are_access_error(self):
        self.reviews_path.unlink()
        self.assertEqual(self.run_cli(), 2)

    def test_template_does_not_approve_features(self):
        self.assertEqual(self.run_cli(command="review-template"), 0)
        exported = load_json(self.output / "review-decisions.json")
        self.assertEqual(exported["decisions"][0]["approvedReference"], "")
        self.reviews_path.write_text(json.dumps(exported), encoding="utf-8")
        self.output = self.root / "reconcile-template"
        self.assertEqual(self.run_cli(), 3)
        self.assertFalse(self.output.exists())

    def test_empty_template_is_explicit_failure(self):
        document = manifest()
        document["features"] = []
        self.manifest_path.write_text(json.dumps(document), encoding="utf-8")
        self.assertEqual(self.run_cli(command="review-template"), 1)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()