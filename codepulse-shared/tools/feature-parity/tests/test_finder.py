import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from test_validation import manifest
from feature_parity.finder import find_repository
from feature_parity.inventory import InventoryPolicyError, inventory_repository
from feature_parity.validation import validate_manifest, validate_schema


def openapi():
    return {"openapi": "3.0.3", "paths": {
        "/users": {"post": {"responses": {"201": {"description": "created"}}},
                   "get": {"responses": {"200": {"description": "listed"}}}},
    }}


class FinderTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "openapi.json").write_text(json.dumps(openapi()), encoding="utf-8")

    def test_structured_operations_are_provisional_and_traceable(self):
        artifacts = find_repository(self.root)
        document = artifacts["feature-manifest.json"]
        validate_manifest(document)
        self.assertEqual(len(document["features"]), 2)
        self.assertEqual(document["scan"]["coverage"], "incomplete")
        self.assertTrue(all(feature["requiresHumanValidation"] for feature in document["features"]))
        self.assertTrue(all(item["verification"] == "partially-verified" for item in document["evidence"]))
        for evidence in document["evidence"]:
            self.assertTrue((self.root / evidence["location"]).exists())

    def test_exclusions_and_no_source_excerpts(self):
        dependency = self.root / "node_modules"
        dependency.mkdir()
        (dependency / "api.json").write_text(json.dumps(openapi()), encoding="utf-8")
        (self.root / "appsettings.json").write_text('{"password": "secret-sentinel"}', encoding="utf-8")
        (self.root / ".env").write_text("PASSWORD=secret-sentinel", encoding="utf-8")
        (self.root / "random.json").write_text('{"token": "secret-sentinel"}', encoding="utf-8")
        document = openapi()
        document["paths"]["/users"]["get"]["summary"] = "secret-sentinel"
        (self.root / "openapi.json").write_text(json.dumps(document), encoding="utf-8")
        artifacts = find_repository(self.root)
        self.assertNotIn("secret-sentinel", json.dumps(artifacts))
        self.assertEqual(len(artifacts["feature-manifest.json"]["features"]), 2)
        exclusions = {item["path"]: item["exclusionReason"] for item in artifacts["repository-inventory.json"]}
        self.assertEqual(exclusions["node_modules"], "dependency-or-generated-directory")
        self.assertEqual(exclusions["appsettings.json"], "sensitive-file-policy")

    def test_oversize_and_binary_excluded(self):
        (self.root / "large.txt").write_bytes(b"a" * 20)
        (self.root / "binary.dat").write_bytes(b"\x00\x01")
        records, issues = inventory_repository(self.root, max_file_bytes=10)
        exclusions = {item["path"]: item["exclusionReason"] for item in records}
        self.assertEqual(exclusions["large.txt"], "file-size-limit")
        self.assertEqual(exclusions["binary.dat"], "binary-file")
        self.assertTrue(issues)

    def test_bounded_inventory(self):
        with self.assertRaises(InventoryPolicyError):
            inventory_repository(self.root, max_entries=0)

    def test_repeatable_manifest(self):
        self.assertEqual(find_repository(self.root), find_repository(self.root))

    def test_inventory_schema(self):
        artifacts = find_repository(self.root)
        validate_schema(artifacts["repository-inventory.json"], "feature-repository-inventory-schema.json")

    def test_source_changes_between_inventory_and_extraction(self):
        records, issues = inventory_repository(self.root)
        (self.root / "openapi.json").write_text(json.dumps({"openapi": "3.0.3", "paths": {}}), encoding="utf-8")
        with patch("feature_parity.finder.inventory_repository", return_value=(records, issues)):
            artifacts = find_repository(self.root)
        self.assertEqual(artifacts["feature-manifest.json"]["features"], [])
        self.assertTrue(any("changed" in item for item in artifacts["discovery-log.json"]["limitations"]))

    def test_source_removed_between_inventory_and_extraction(self):
        records, issues = inventory_repository(self.root)
        (self.root / "openapi.json").unlink()
        with patch("feature_parity.finder.inventory_repository", return_value=(records, issues)):
            artifacts = find_repository(self.root)
        self.assertEqual(artifacts["feature-manifest.json"]["features"], [])
        self.assertTrue(any("parsed" in item for item in artifacts["discovery-log.json"]["limitations"]))

    def test_file_exactly_at_size_limit_is_included(self):
        (self.root / "exact.txt").write_bytes(b"a" * 10)
        records, issues = inventory_repository(self.root, max_file_bytes=10)
        exact = next(record for record in records if record["path"] == "exact.txt")
        self.assertIsNone(exact["exclusionReason"])
        self.assertIsNotNone(exact["contentHash"])

    def test_depth_limit_is_disclosed(self):
        nested = self.root / "nested"
        nested.mkdir()
        (nested / "hidden.json").write_text(json.dumps(openapi()), encoding="utf-8")
        records, issues = inventory_repository(self.root, max_depth=0)
        self.assertIn("Directory depth limit reached", issues)
        self.assertFalse(any(record["path"].startswith("nested/") for record in records))

    def test_generic_fallback_does_not_invent_features(self):
        (self.root / "openapi.json").unlink()
        (self.root / "app.cs").write_text("public class CreateUser {}", encoding="utf-8")
        artifacts = find_repository(self.root)
        self.assertEqual(artifacts["feature-manifest.json"]["features"], [])
        self.assertEqual(artifacts["repository-inventory.json"][0]["language"], "csharp")

    def test_invalid_json_reports_limitation(self):
        (self.root / "openapi.json").write_text("{", encoding="utf-8")
        artifacts = find_repository(self.root)
        self.assertEqual(artifacts["feature-manifest.json"]["features"], [])
        self.assertTrue(any("parsed" in item for item in artifacts["discovery-log.json"]["limitations"]))

    def test_linked_directory_is_not_followed(self):
        with tempfile.TemporaryDirectory() as outside:
            (Path(outside) / "api.json").write_text(json.dumps(openapi()), encoding="utf-8")
            try:
                (self.root / "linked").symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("Creating symlinks requires OS permission")
            records, issues = inventory_repository(self.root)
            self.assertTrue(any(item["exclusionReason"] == "link-or-junction" for item in records))
            self.assertFalse(any("linked/" in item["path"] for item in records))

    def test_link_policy_without_os_permission(self):
        with patch("feature_parity.inventory.is_link", return_value=True):
            records, issues = inventory_repository(self.root)
        self.assertEqual(records[0]["exclusionReason"], "link-or-junction")
        self.assertIsNone(records[0]["contentHash"])
        self.assertTrue(issues)

    def test_duplicate_properties_not_silently_accepted(self):
        (self.root / "openapi.json").write_text(
            '{"openapi":"3.0.3","paths":{},"paths":{}}', encoding="utf-8"
        )
        artifacts = find_repository(self.root)
        self.assertEqual(artifacts["feature-manifest.json"]["features"], [])
        self.assertTrue(any("parsed" in item for item in artifacts["discovery-log.json"]["limitations"]))


if __name__ == "__main__":
    unittest.main()