import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from test_finder import openapi
from feature_parity.cli import main
from feature_parity.validation import load_json, validate_manifest


class FindCliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "openapi.json").write_text(json.dumps(openapi()), encoding="utf-8")
        self.output = self.root / "results"

    def run_cli(self, *extra):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main(["parity", "find", "--source", str(self.source),
                         "--output", str(self.output), *extra])

    def test_successful_find_writes_valid_artifacts(self):
        self.assertEqual(self.run_cli(), 0)
        document = load_json(self.output / "feature-manifest.json")
        validate_manifest(document)
        self.assertEqual(len(document["features"]), 2)
        self.assertEqual(load_json(self.output / "discovery-log.json")["statistics"]["needsReview"], 2)
        self.assertEqual(len(list(self.output.iterdir())), 5)

    def test_dry_run_does_not_scan_or_write(self):
        (self.source / "openapi.json").write_text("invalid", encoding="utf-8")
        self.assertEqual(self.run_cli("--dry-run"), 0)
        self.assertFalse(self.output.exists())

    def test_output_in_source_rejected(self):
        self.output = self.source / "results"
        self.assertEqual(self.run_cli(), 5)
        self.assertFalse(self.output.exists())

    def test_existing_output_rejected(self):
        self.output.mkdir()
        self.assertEqual(self.run_cli(), 5)

    def test_missing_source_is_access_error(self):
        self.source = self.root / "missing"
        self.assertEqual(self.run_cli(), 2)

    def test_scan_does_not_mutate_source(self):
        before = {path.name: path.read_bytes() for path in self.source.iterdir()}
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.source.iterdir()})

    def test_invalid_configuration_rejected_before_dry_run(self):
        (self.source / "codepulse.config.json").write_text(
            '{"featureParity":{"minimumConfidence":"unknown"}}', encoding="utf-8"
        )
        self.assertEqual(self.run_cli("--dry-run"), 1)
        self.assertFalse(self.output.exists())

    def test_invalid_scope_rejected(self):
        self.assertEqual(self.run_cli("--scope", "unknown"), 1)
        self.assertFalse(self.output.exists())

    def test_cli_threshold_overrides_config(self):
        (self.source / "codepulse.config.json").write_text(
            '{"featureParity":{"minimumConfidence":"high","applicationName":"Configured"}}', encoding="utf-8"
        )
        self.assertEqual(self.run_cli("--confidence-threshold", "low", "--application-name", "Explicit"), 0)
        document = load_json(self.output / "feature-manifest.json")
        self.assertEqual(document["application"]["name"], "Explicit")
        self.assertTrue(all(feature["admitted"] for feature in document["features"]))

    def test_configured_entry_limit_fails_without_outputs(self):
        (self.source / "codepulse.config.json").write_text(
            '{"featureParity":{"limits":{"maxEntries":1}}}', encoding="utf-8"
        )
        self.assertEqual(self.run_cli(), 5)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()