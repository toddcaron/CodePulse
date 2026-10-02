import json
import tempfile
import unittest
from pathlib import Path

from test_finder import openapi
from feature_parity.finder import find_repository


class FinderPolicyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for name in ("src", "tests", "private", "node_modules"):
            directory = self.root / name
            directory.mkdir()
            (directory / "openapi.json").write_text(json.dumps(openapi()), encoding="utf-8")

    def write_config(self, settings):
        (self.root / "codepulse.config.json").write_text(json.dumps({"featureParity": settings}), encoding="utf-8")

    def test_includes_narrow_scan_without_bypassing_security(self):
        self.write_config({"include": ["src/**", "node_modules/**"]})
        artifacts = find_repository(self.root)
        self.assertEqual(len(artifacts["feature-manifest.json"]["features"]), 2)
        records = {record["path"]: record for record in artifacts["repository-inventory.json"]}
        self.assertEqual(records["tests/openapi.json"]["exclusionReason"], "outside-includes")
        self.assertEqual(records["node_modules"]["exclusionReason"], "dependency-or-generated-directory")

    def test_exclusions_and_forbidden_paths_are_distinct(self):
        self.write_config({"exclude": ["tests/**"], "forbiddenPaths": ["private/**"]})
        artifacts = find_repository(self.root)
        records = {record["path"]: record for record in artifacts["repository-inventory.json"]}
        self.assertEqual(records["tests"]["exclusionReason"], "configured-exclusion")
        self.assertEqual(records["private"]["exclusionReason"], "forbidden-path-policy")
        self.assertFalse(any(record["path"].startswith("private/") for record in records.values()))

    def test_confidence_threshold_preserves_candidates_and_review(self):
        self.write_config({"include": ["src/**"], "minimumConfidence": "high"})
        artifacts = find_repository(self.root)
        self.assertEqual(len(artifacts["feature-manifest.json"]["features"]), 2)
        self.assertTrue(all(not feature["admitted"] for feature in artifacts["feature-manifest.json"]["features"]))
        self.assertEqual(len(artifacts["review-queue.json"]), 2)
        self.assertEqual(artifacts["discovery-log.json"]["statistics"]["belowThreshold"], 2)

    def test_low_threshold_admits_but_never_confirms(self):
        self.write_config({"include": ["src/**"], "minimumConfidence": "low"})
        artifacts = find_repository(self.root)
        self.assertTrue(all(feature["admitted"] for feature in artifacts["feature-manifest.json"]["features"]))
        self.assertTrue(all(feature["status"] == "needs-review" for feature in artifacts["feature-manifest.json"]["features"]))

    def test_scope_filters_extraction_not_inventory(self):
        self.write_config({"defaultScope": ["ui"]})
        artifacts = find_repository(self.root)
        self.assertEqual(artifacts["feature-manifest.json"]["features"], [])
        self.assertTrue(artifacts["repository-inventory.json"])

    def test_effective_policy_affects_digest(self):
        first = find_repository(self.root)["feature-manifest.json"]["scan"]["configurationDigest"]
        self.write_config({"minimumConfidence": "low"})
        second = find_repository(self.root)["feature-manifest.json"]["scan"]["configurationDigest"]
        self.assertNotEqual(first, second)

    def test_configured_file_limit_is_applied(self):
        self.write_config({"limits": {"maxFileBytes": 10}})
        artifacts = find_repository(self.root)
        self.assertEqual(artifacts["feature-manifest.json"]["features"], [])
        self.assertTrue(any(record["exclusionReason"] == "file-size-limit" for record in artifacts["repository-inventory.json"]))


if __name__ == "__main__":
    unittest.main()