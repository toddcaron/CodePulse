import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_validation import manifest
from feature_parity.config import ConfigurationError, match_patterns, resolve_policy
from feature_parity.inventory import InventoryPolicyError


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def write_config(self, settings):
        (self.root / "codepulse.config.json").write_text(json.dumps({"featureParity": settings}), encoding="utf-8")

    def test_defaults(self):
        policy = resolve_policy(self.root)
        self.assertEqual(policy["minimumConfidence"], "medium")
        self.assertEqual(len(policy["scopes"]), 8)

    def test_cli_overrides_config(self):
        self.write_config({"applicationName": "Configured", "defaultScope": ["ui"], "minimumConfidence": "high"})
        policy = resolve_policy(self.root, overrides={"applicationName": "Explicit", "scopes": ["api"], "minimumConfidence": "low"})
        self.assertEqual(policy["applicationName"], "Explicit")
        self.assertEqual(policy["scopes"], ["api"])
        self.assertEqual(policy["minimumConfidence"], "low")

    def test_invalid_policy_rejected(self):
        for settings in ({"unknownOption": True}, {"limits": {"maxFileBytes": 2000000}},
                         {"defaultScope": ["all", "api"]}, {"applicationName": " "},
                         {"exclude": ["../private/**"]}, {"include": ["!src/**"]},
                         {"forbiddenPaths": ["C:/private"]}, {"include": ["src\\**"]}):
            with self.subTest(settings=settings):
                self.write_config(settings)
                with self.assertRaises(ConfigurationError):
                    resolve_policy(self.root)

    def test_globs_handle_root_and_nested_paths(self):
        self.assertTrue(match_patterns("openapi.json", ["**/*.json"]))
        self.assertTrue(match_patterns("src/api/openapi.json", ["src/**"]))
        self.assertTrue(match_patterns("private", ["private/**"], directory=True))
        self.assertFalse(match_patterns("test/openapi.json", ["src/**"]))

    def test_other_codepulse_sections_are_allowed(self):
        (self.root / "codepulse.config.json").write_text(
            '{"health":{"enabled":true},"featureParity":{}}', encoding="utf-8"
        )
        self.assertEqual(resolve_policy(self.root)["minimumConfidence"], "medium")

    def test_missing_explicit_config_is_not_silently_ignored(self):
        with self.assertRaises(OSError):
            resolve_policy(self.root, self.root / "missing.json")

    def test_configuration_link_policy(self):
        self.write_config({})
        with patch("feature_parity.config.is_link", return_value=True):
            with self.assertRaises(InventoryPolicyError):
                resolve_policy(self.root)

    def test_oversized_configuration_rejected(self):
        (self.root / "codepulse.config.json").write_bytes(b" " * 1048577)
        with self.assertRaises(ConfigurationError):
            resolve_policy(self.root)


if __name__ == "__main__":
    unittest.main()