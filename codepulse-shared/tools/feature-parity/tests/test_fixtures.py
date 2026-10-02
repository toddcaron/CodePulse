import subprocess
import json
from collections import Counter
import sys
import tempfile
import unittest
from pathlib import Path

from test_validation import manifest
from feature_parity.validation import load_json, validate_manifest, validate_schema
from feature_parity.finder import find_repository


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class FixtureTests(unittest.TestCase):
    def test_real_review_workflow_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export = root / "template"
            source = FIXTURES / "target.json"
            completed = subprocess.run([
                sys.executable, "-B", str(ROOT / "cli.py"), "parity", "review-template",
                "--manifest", str(source), "--output", str(export),
            ], cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            batch = load_json(export / "review-decisions.json")
            batch["decisions"][0]["decision"] = "confirmed"
            batch["decisions"][0]["approvedReference"] = "Synthetic product-owner review"
            batch["decisions"][0]["updates"] = {"name": "Provision User"}
            reviews = root / "reviews.json"
            reviews.write_text(json.dumps(batch), encoding="utf-8")
            output = root / "reviewed"
            completed = subprocess.run([
                sys.executable, "-B", str(ROOT / "cli.py"), "parity", "reconcile",
                "--manifest", str(source), "--reviews", str(reviews), "--output", str(output),
            ], cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            document = load_json(output / "feature-manifest.json")
            validate_manifest(document)
            self.assertEqual(document["features"][0]["name"], "Provision User")
            self.assertEqual(document["features"][0]["id"], "identity.create-user")

    def test_mixed_ui_legacy_cli_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "results"
            completed = subprocess.run([
                sys.executable, "-B", str(ROOT / "cli.py"), "parity", "find",
                "--source", str(FIXTURES / "ui-legacy-app"), "--output", str(output),
            ], cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            statistics = json.loads(completed.stdout)
            self.assertEqual(statistics["needsReview"], 15)
            self.assertEqual(statistics["confirmedFeatures"], 0)
            self.assertEqual(statistics["belowThreshold"], 15)
            document = load_json(output / "feature-manifest.json")
            validate_manifest(document)
            self.assertEqual(len(document["reviewQueue"]), 15)

    def test_ui_legacy_summary_snapshot(self):
        artifacts = find_repository(FIXTURES / "ui-legacy-app")
        document = artifacts["feature-manifest.json"]
        summary = {
            "candidateCount": len(document["features"]),
            "byCapabilityType": dict(Counter(feature["capabilityType"] for feature in document["features"])),
            "byEvidenceType": dict(Counter(item["type"] for item in document["evidence"])),
            "confirmedCount": sum(feature["status"] == "confirmed" for feature in document["features"]),
            "admittedCount": sum(feature["admitted"] for feature in document["features"]),
            "reviewCount": len(document["reviewQueue"]),
        }
        expected = load_json(Path(__file__).resolve().parent / "snapshots" / "ui-legacy-summary.json")
        self.assertEqual(summary, expected)

    def test_checked_in_dotnet_fixture(self):
        artifacts = find_repository(FIXTURES / "dotnet-app")
        self.assertEqual(len(artifacts["feature-manifest.json"]["features"]), 2)
        self.assertTrue(all(item["type"] == "endpoint" for item in artifacts["evidence-index.json"]))
        self.assertEqual(artifacts["discovery-log.json"]["statistics"]["belowThreshold"], 2)

    def test_real_find_and_compare_entry_points(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outputs = [root / "baseline", root / "target"]
            for output in outputs:
                completed = subprocess.run([
                    sys.executable, "-B", str(ROOT / "cli.py"), "parity", "find",
                    "--source", str(FIXTURES / "openapi-app"), "--output", str(output),
                ], cwd=directory, capture_output=True, text=True, timeout=30)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                document = load_json(output / "feature-manifest.json")
                validate_manifest(document)
                self.assertEqual(len(document["features"]), 2)
            completed = subprocess.run([
                sys.executable, "-B", str(ROOT / "cli.py"), "parity", "compare",
                "--source", str(outputs[0] / "feature-manifest.json"),
                "--target", str(outputs[1] / "feature-manifest.json"),
                "--output", str(root / "parity"), "--fail-on", "unverified",
            ], cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertEqual(completed.returncode, 6, completed.stderr)
            result = load_json(root / "parity" / "parity-results.json")
            self.assertEqual(result["statistics"]["equivalentCount"], 0)
            self.assertEqual(result["statistics"]["unresolvedCount"], 2)

    def test_checked_in_manifests_validate(self):
        for path in FIXTURES.glob("*.json"):
            with self.subTest(path=path.name):
                validate_manifest(load_json(path))

    def test_real_entry_point_from_unrelated_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "results"
            completed = subprocess.run([
                sys.executable, str(ROOT / "cli.py"), "parity", "compare",
                "--source", str(FIXTURES / "baseline.json"),
                "--target", str(FIXTURES / "target.json"),
                "--output", str(output), "--fail-on", "unverified",
            ], cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertEqual(completed.returncode, 6, completed.stderr)
            result = load_json(output / "parity-results.json")
            validate_schema(result, "feature-parity-result-schema.json")
            self.assertEqual(result["matches"][0]["status"], "needs-sme-validation")


if __name__ == "__main__":
    unittest.main()