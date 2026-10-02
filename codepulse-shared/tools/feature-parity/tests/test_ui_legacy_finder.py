import json
import tempfile
import unittest
from pathlib import Path

from test_validation import manifest
from feature_parity.finder import find_repository
from feature_parity.validation import validate_manifest, validate_schema


class UiLegacyFinderTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "Users.vue").write_text(
            '<template><button @click="secret_sentinel">Save</button></template>', encoding="utf-8"
        )
        (self.root / "routes.js").write_text('$routeProvider.when("/secret_sentinel", {});', encoding="utf-8")
        (self.root / "legacy.html").write_text('<a ui-sref="secret_sentinel">Users</a>', encoding="utf-8")
        (self.root / "legacy.cfm").write_text(
            '<cfhttp url="https://secret_sentinel"><cfreport template="secret_sentinel">'
            '<cfschedule task="secret_sentinel"><cffunction access="remote" name="secret_sentinel">',
            encoding="utf-8"
        )

    def test_capabilities_are_distinct_scope_correct_and_provisional(self):
        artifacts = find_repository(self.root)
        document = artifacts["feature-manifest.json"]
        validate_manifest(document)
        validate_schema(artifacts["repository-inventory.json"], "feature-repository-inventory-schema.json")
        self.assertEqual(len(document["features"]), 7)
        self.assertEqual({feature["capabilityType"] for feature in document["features"]}, {"ui", "api", "integrations", "reports", "jobs"})
        self.assertTrue(all(feature["requiresHumanValidation"] and not feature["admitted"] for feature in document["features"]))
        self.assertNotIn("secret_sentinel", json.dumps(artifacts))

    def test_scope_filter_preserves_inventory_and_reports_skips(self):
        (self.root / "codepulse.config.json").write_text(
            '{"featureParity":{"defaultScope":["jobs"]}}', encoding="utf-8"
        )
        artifacts = find_repository(self.root)
        self.assertEqual(len(artifacts["feature-manifest.json"]["features"]), 1)
        self.assertEqual(artifacts["feature-manifest.json"]["features"][0]["capabilityType"], "jobs")
        self.assertEqual(artifacts["discovery-log.json"]["statistics"]["excludedCandidates"], 6)
        self.assertEqual(len(artifacts["repository-inventory.json"]), 5)

    def test_repeatable_results(self):
        self.assertEqual(find_repository(self.root), find_repository(self.root))


if __name__ == "__main__":
    unittest.main()