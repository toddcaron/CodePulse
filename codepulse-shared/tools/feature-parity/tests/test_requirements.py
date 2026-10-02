import copy
import unittest
from pathlib import Path

from test_validation import manifest
from feature_parity.comparison import compare_manifests
from feature_parity.requirements import ingest_requirements, validate_requirements_baseline
from feature_parity.validation import ArtifactError, load_json, validate_manifest, validate_schema


def requirements_document():
    feature = manifest()["features"][0]
    requirement = {key: copy.deepcopy(feature[key]) for key in (
        "id", "name", "domain", "capabilityType", "actors", "inputs", "outputs", "preconditions"
    )}
    requirement["behaviors"] = [{key: behavior[key] for key in ("id", "description", "mandatory")}
                                for behavior in feature["behaviors"]]
    requirement.update(acceptanceCriteria=["One account is created"], ambiguities=[])
    return {"schemaVersion": "1.0", "applicationName": "Synthetic Requirements", "requirements": [requirement]}


class RequirementsTests(unittest.TestCase):
    def ingest(self, document=None, location="requirements.json"):
        return ingest_requirements(document or requirements_document(), location, "a" * 64, 12)

    def test_preserves_input_and_declared_criteria(self):
        document = requirements_document()
        before = copy.deepcopy(document)
        artifacts = self.ingest(document)
        self.assertEqual(document, before)
        baseline = artifacts["requirements-baseline.json"]
        validate_schema(baseline, "feature-requirements-baseline-schema.json")
        self.assertEqual(baseline["document"], document)
        self.assertEqual(baseline["evidence"][0]["lineEnd"], 12)
        validate_manifest(artifacts["feature-manifest.json"])

    def test_import_never_confirms_admits_or_establishes_parity(self):
        imported = self.ingest()["feature-manifest.json"]
        feature = imported["features"][0]
        self.assertEqual(feature["status"], "needs-review")
        self.assertFalse(feature["admitted"])
        self.assertEqual(imported["evidence"][0]["verification"], "partially-verified")
        self.assertEqual(compare_manifests(imported, imported)["statistics"]["equivalentCount"], 0)

    def test_ambiguity_is_preserved_and_queued(self):
        document = requirements_document()
        document["requirements"][0]["ambiguities"] = ["Approval role is unspecified"]
        result = self.ingest(document)
        self.assertIn("ambiguity", result["review-queue.json"][0]["reason"])
        self.assertEqual(result["requirements-log.json"]["statistics"]["ambiguousRequirements"], 1)

    def test_invalid_fields_duplicates_paths_and_approvals_fail(self):
        mutations = [
            lambda doc: doc.update(schemaVersion="2.0"),
            lambda doc: doc["requirements"].append(copy.deepcopy(doc["requirements"][0])),
            lambda doc: doc["requirements"][0].update(name=" "),
            lambda doc: doc["requirements"][0].update(review={"approvedReference": "Agent"}),
            lambda doc: doc["requirements"][0]["behaviors"].append(copy.deepcopy(doc["requirements"][0]["behaviors"][0])),
        ]
        for mutation in mutations:
            document = requirements_document()
            mutation(document)
            with self.subTest(mutation=mutation), self.assertRaises(ArtifactError):
                self.ingest(document)
        with self.assertRaises(ArtifactError):
            self.ingest(location="../requirements.json")

    def test_empty_and_replay_are_explicit(self):
        document = requirements_document()
        document["requirements"] = []
        result = self.ingest(document)
        self.assertEqual(result["requirements-log.json"]["statistics"]["requirements"], 0)
        self.assertEqual(result["feature-manifest.json"]["scan"]["coverage"], "incomplete")
        self.assertEqual(self.ingest(), self.ingest())

    def test_baseline_tampering_and_dangling_links_are_rejected(self):
        mutations = [
            lambda item: item.update(inputDigest="0" * 64),
            lambda item: item.update(sourceDigest="0" * 64),
            lambda item: item["evidence"][0].update(location="../private.json"),
            lambda item: item["evidence"][0].update(verification="verified-original"),
            lambda item: item["featureLinks"][0].update(featureId="unknown"),
            lambda item: item["featureLinks"][0].update(evidenceRefs=["unknown"]),
            lambda item: item["featureLinks"].clear(),
            lambda item: item["featureLinks"].append(copy.deepcopy(item["featureLinks"][0])),
        ]
        for mutation in mutations:
            baseline = self.ingest()["requirements-baseline.json"]
            mutation(baseline)
            with self.subTest(mutation=mutation), self.assertRaises(ArtifactError):
                validate_requirements_baseline(baseline)

    def test_declaration_order_is_preserved_but_features_are_sorted(self):
        document = requirements_document()
        second = copy.deepcopy(document["requirements"][0])
        second["id"] = "accounts.disable-user"
        document["requirements"].append(second)
        result = self.ingest(document)
        self.assertEqual(result["requirements-baseline.json"]["document"], document)
        validate_requirements_baseline(result["requirements-baseline.json"])
        self.assertEqual(result["feature-manifest.json"]["features"][0]["id"], second["id"])

    def test_empty_input_still_validates_source_metadata(self):
        document = requirements_document()
        document["requirements"] = []
        with self.assertRaises(ArtifactError):
            self.ingest(document, location="../requirements.json")

    def test_checked_in_example_is_provisional_with_explicit_ambiguity(self):
        document = load_json(Path(__file__).resolve().parents[1] / "examples" / "requirements.json")
        artifacts = self.ingest(document)
        self.assertEqual(artifacts["requirements-log.json"]["statistics"]["requirements"], 2)
        self.assertEqual(artifacts["requirements-log.json"]["statistics"]["ambiguousRequirements"], 1)
        self.assertEqual(artifacts["requirements-baseline.json"]["document"], document)


if __name__ == "__main__":
    unittest.main()