import json
import tempfile
import unittest
from pathlib import Path

from test_validation import manifest
from test_finder import openapi
from feature_parity.finder import find_repository
from feature_parity.validation import validate_manifest


class DotnetFinderTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "UsersController.cs").write_text(
            '// [HttpGet] disabled\n[HttpPost("/private-secret-sentinel")]\n'
            'public void CreateUser() {}\napp.MapGet("/users", Handler);\n', encoding="utf-8"
        )

    def test_detects_two_provisional_operations_with_line_evidence(self):
        artifacts = find_repository(self.root)
        document = artifacts["feature-manifest.json"]
        validate_manifest(document)
        self.assertEqual(len(document["features"]), 2)
        self.assertEqual({item["lineStart"] for item in document["evidence"]}, {2, 4})
        self.assertTrue(all(item["type"] == "endpoint" for item in document["evidence"]))
        self.assertNotIn("private-secret-sentinel", json.dumps(artifacts))
        self.assertTrue(all(not feature["admitted"] for feature in document["features"]))

    def test_generated_and_conditional_sources_are_not_promoted(self):
        (self.root / "UsersController.cs").write_text('#if false\n[HttpGet]\n#endif', encoding="utf-8")
        (self.root / "Users.g.cs").write_text('[HttpPost]', encoding="utf-8")
        artifacts = find_repository(self.root)
        self.assertEqual(artifacts["feature-manifest.json"]["features"], [])
        self.assertTrue(any(item["exclusionReason"] == "generated-file" for item in artifacts["repository-inventory.json"]))
        self.assertTrue(any("Conditional" in issue for issue in artifacts["discovery-log.json"]["limitations"]))

    def test_mixed_stack_keeps_unconsolidated_evidence_provisional(self):
        (self.root / "openapi.json").write_text(json.dumps(openapi()), encoding="utf-8")
        artifacts = find_repository(self.root)
        self.assertEqual(len(artifacts["feature-manifest.json"]["features"]), 4)
        self.assertEqual({item["adapter"] for item in artifacts["repository-inventory.json"]}, {"openapi-json", "dotnet-lexical"})
        self.assertTrue(all(feature["requiresHumanValidation"] for feature in artifacts["feature-manifest.json"]["features"]))


if __name__ == "__main__":
    unittest.main()