import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from test_comparison import approve
from test_validation import manifest
from feature_parity.cli import main
from feature_parity.validation import load_json, validate_schema


class CliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "source.json"
        self.target = self.root / "target.json"
        self.source.write_text(json.dumps(approve(manifest())), encoding="utf-8")
        self.target.write_text(json.dumps(manifest()), encoding="utf-8")
        self.output = self.root / "output"

    def run_cli(self, *extra):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main(["parity", "compare", "--source", str(self.source),
                         "--target", str(self.target), "--output", str(self.output), *extra])

    def test_gate_writes_valid_results_before_failure(self):
        self.assertEqual(self.run_cli("--fail-on", "unverified"), 6)
        result = load_json(self.output / "parity-results.json")
        validate_schema(result, "feature-parity-result-schema.json")
        self.assertEqual(result["statistics"]["unresolvedCount"], 1)
        self.assertEqual(len(load_json(self.output / "review-queue.json")), 1)

    def test_default_does_not_gate(self):
        self.assertEqual(self.run_cli(), 0)

    def test_dry_run_writes_nothing(self):
        before = set(self.root.iterdir())
        self.assertEqual(self.run_cli("--dry-run"), 0)
        self.assertEqual(before, set(self.root.iterdir()))

    def test_output_never_overwrites(self):
        self.output.mkdir()
        self.assertEqual(self.run_cli(), 5)

    def test_source_equals_target_is_rejected(self):
        self.target = self.source
        self.assertEqual(self.run_cli(), 1)

    def test_incomplete_discovery_invocation_is_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["parity", "find", "--source", str(self.root)]), 1)

    def test_invalid_manifest_is_rejected(self):
        self.source.write_text('{"schemaVersion": "2.0"}', encoding="utf-8")
        self.assertEqual(self.run_cli(), 3)

    def test_missing_source(self):
        self.source.unlink()
        self.assertEqual(self.run_cli(), 2)

    def test_no_user_values_in_schema_errors(self):
        self.source.write_text('{"password": "synthetic-secret-value"}', encoding="utf-8")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertEqual(main(["parity", "validate", "--manifest", str(self.source)]), 3)
        self.assertNotIn("synthetic-secret-value", stderr.getvalue())

    def test_duplicate_json_keys_rejected(self):
        self.source.write_text('{"schemaVersion": "1.0", "schemaVersion": "2.0"}', encoding="utf-8")
        self.assertEqual(self.run_cli(), 3)

    def test_non_finite_json_rejected(self):
        self.source.write_text('{"score": NaN}', encoding="utf-8")
        self.assertEqual(self.run_cli(), 3)


if __name__ == "__main__":
    unittest.main()