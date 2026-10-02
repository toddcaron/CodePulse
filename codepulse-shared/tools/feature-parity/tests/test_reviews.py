import copy
import unittest

from test_validation import manifest
from test_comparison import approve
from feature_parity.comparison import compare_manifests
from feature_parity.identity import contract_digest, digest
from feature_parity.reviews import reconcile_manifest, review_template
from feature_parity.validation import ArtifactError, validate_manifest


def review_batch(document, decision="confirmed", updates=None):
    feature = document["features"][0]
    return {
        "schemaVersion": "1.0", "baseManifestDigest": digest(document),
        "decisions": [{
            "featureId": feature["id"], "expectedContractDigest": contract_digest(feature, document["evidence"]),
            "decision": decision, "approvedReference": "Product review fixture",
            "updates": updates or {}, "reviewerNote": "Synthetic reviewed workflow",
        }],
    }


class ReviewTests(unittest.TestCase):
    def test_confirm_computes_digest_and_preserves_original(self):
        document = manifest()
        before = copy.deepcopy(document)
        artifacts = reconcile_manifest(document, review_batch(document))
        feature = artifacts["feature-manifest.json"]["features"][0]
        self.assertEqual(feature["status"], "confirmed")
        self.assertFalse(feature["requiresHumanValidation"])
        validate_manifest(artifacts["feature-manifest.json"])
        self.assertEqual(document, before)
        self.assertEqual(artifacts["reconciliation-log.json"]["statistics"]["appliedDecisions"], 1)

    def test_rename_preserves_identity_and_fingerprint(self):
        document = manifest()
        result = reconcile_manifest(document, review_batch(document, updates={"name": "Provision User", "domain": "Administration", "aliases": ["Create User"]}))
        feature = result["feature-manifest.json"]["features"][0]
        self.assertEqual(feature["id"], document["features"][0]["id"])
        self.assertEqual(feature["fingerprint"], document["features"][0]["fingerprint"])
        self.assertEqual(feature["name"], "Provision User")

    def test_confirm_does_not_upgrade_evidence_confidence_or_admission(self):
        document = manifest()
        document["features"][0]["admitted"] = False
        document["evidence"][0]["verification"] = "partially-verified"
        reviewed = reconcile_manifest(document, review_batch(document))["feature-manifest.json"]
        self.assertEqual(reviewed["evidence"], document["evidence"])
        self.assertEqual(reviewed["features"][0]["confidence"], document["features"][0]["confidence"])
        self.assertFalse(reviewed["features"][0]["admitted"])
        self.assertEqual(len(reviewed["reviewQueue"]), 1)
        self.assertEqual(compare_manifests(reviewed, reviewed)["statistics"]["equivalentCount"], 0)

    def test_attach_existing_evidence_and_update_behavior(self):
        document = manifest()
        added = copy.deepcopy(document["evidence"][0])
        added["id"] = "evidence-2"
        added["type"] = "test"
        added["location"] = "tests/users.cs"
        document["evidence"].append(added)
        behavior = {"id": "create-account", "description": "Creates an account",
                    "mandatory": True, "evidenceRefs": ["evidence-1", "evidence-2"]}
        batch = review_batch(document, updates={"evidenceRefs": ["evidence-1", "evidence-2"], "behaviors": [behavior]})
        result = reconcile_manifest(document, batch)["feature-manifest.json"]
        validate_manifest(result)
        self.assertEqual(result["features"][0]["behaviors"][0]["evidenceRefs"], ["evidence-1", "evidence-2"])
        self.assertEqual(result["evidence"], document["evidence"])

    def test_batch_failure_is_atomic(self):
        document = manifest()
        second = copy.deepcopy(document["features"][0])
        second["id"] = "identity.disable-user"
        document["features"].append(second)
        before = copy.deepcopy(document)
        batch = review_batch(document)
        batch["decisions"].append({
            "featureId": second["id"], "expectedContractDigest": "0" * 64,
            "decision": "confirmed", "approvedReference": "Fixture review",
        })
        with self.assertRaises(ArtifactError):
            reconcile_manifest(document, batch)
        self.assertEqual(document, before)

    def test_unreviewed_features_and_queue_are_preserved(self):
        document = manifest()
        second = copy.deepcopy(document["features"][0])
        second["id"] = "identity.disable-user"
        document["features"].append(second)
        document["reviewQueue"] = [{"featureId": second["id"], "reason": "Original unresolved issue", "evidenceRefs": ["evidence-1"]}]
        result = reconcile_manifest(document, review_batch(document))["feature-manifest.json"]
        self.assertEqual(result["features"][1], second)
        self.assertEqual(result["reviewQueue"], document["reviewQueue"])

    def test_alias_metadata_does_not_automatically_match_features(self):
        document = manifest()
        batch = review_batch(document, updates={"aliases": ["Provision Account"]})
        reviewed = reconcile_manifest(document, batch)["feature-manifest.json"]
        target = approve(manifest())
        target["features"][0]["id"] = "accounts.provision-account"
        target = approve(target)
        result = compare_manifests(reviewed, target)
        self.assertEqual(result["statistics"]["equivalentCount"], 0)

    def test_stale_manifest_or_contract_rejected(self):
        document = manifest()
        for field in ("baseManifestDigest", "expectedContractDigest"):
            with self.subTest(field=field):
                batch = review_batch(document)
                target = batch if field == "baseManifestDigest" else batch["decisions"][0]
                target[field] = "0" * 64
                with self.assertRaises(ArtifactError):
                    reconcile_manifest(document, batch)

    def test_duplicate_unknown_and_unsafe_updates_rejected(self):
        document = manifest()
        mutations = [
            lambda batch: batch["decisions"].append(copy.deepcopy(batch["decisions"][0])),
            lambda batch: batch["decisions"][0].update(featureId="unknown.feature"),
            lambda batch: batch["decisions"][0].update(approvedReference=" "),
            lambda batch: batch["decisions"][0]["updates"].update(admitted=True),
            lambda batch: batch["decisions"][0]["updates"].update(confidence={"score": 1}),
            lambda batch: batch["decisions"][0]["updates"].update(id="new.id"),
            lambda batch: batch["decisions"][0]["updates"].update(evidenceRefs=["unknown"]),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                batch = review_batch(document)
                mutation(batch)
                with self.assertRaises(ArtifactError):
                    reconcile_manifest(document, batch)

    def test_reject_deprecate_and_reopen(self):
        original = approve(manifest())
        for decision in ("rejected", "deprecated", "needs-review"):
            with self.subTest(decision=decision):
                result = reconcile_manifest(original, review_batch(original, decision))["feature-manifest.json"]
                self.assertNotIn("review", result["features"][0])
                self.assertEqual(len(result["reviewQueue"]), int(decision == "needs-review"))
                self.assertEqual(result["features"][0]["status"], decision)

    def test_behavior_update_requires_existing_owned_evidence(self):
        document = manifest()
        behavior = {"id": "assign-role", "description": "Assigns initial role", "mandatory": True, "evidenceRefs": ["unknown"]}
        with self.assertRaises(ArtifactError):
            reconcile_manifest(document, review_batch(document, updates={"behaviors": [behavior]}))

    def test_template_is_deliberately_unapproved(self):
        document = manifest()
        template = review_template(document)
        self.assertEqual(template["decisions"][0]["approvedReference"], "")
        with self.assertRaises(ArtifactError):
            reconcile_manifest(document, template)

    def test_replay_from_same_inputs_is_reproducible(self):
        document = manifest()
        batch = review_batch(document)
        self.assertEqual(reconcile_manifest(document, batch), reconcile_manifest(document, batch))


if __name__ == "__main__":
    unittest.main()