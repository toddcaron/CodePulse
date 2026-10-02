import copy
import unittest

from test_validation import manifest
from feature_parity.comparison import compare_manifests, gate_failed
from feature_parity.identity import contract_digest
from feature_parity.validation import ArtifactError, validate_manifest


def approve(document):
    feature = document["features"][0]
    feature["status"] = "confirmed"
    feature["requiresHumanValidation"] = False
    feature["review"] = {
        "approvedReference": "Fixture approval",
        "contractDigest": contract_digest(feature, document["evidence"]),
    }
    return document


class ComparisonTests(unittest.TestCase):
    def test_same_id_without_review_is_not_equivalent(self):
        result = compare_manifests(manifest(), manifest())
        self.assertEqual(result["matches"][0]["status"], "needs-sme-validation")
        self.assertIsNone(result["statistics"]["coveragePercent"])

    def test_below_threshold_candidate_cannot_supply_equivalence(self):
        target = manifest()
        target["features"][0]["admitted"] = False
        result = compare_manifests(approve(manifest()), approve(target))
        self.assertEqual(result["matches"][0]["status"], "needs-sme-validation")
        self.assertEqual(result["statistics"]["equivalentCount"], 0)

    def test_reviewed_contract_agreement(self):
        document = approve(manifest())
        result = compare_manifests(document, copy.deepcopy(document))
        self.assertEqual(result["matches"][0]["status"], "equivalent")
        self.assertEqual(result["statistics"]["coveragePercent"], 100)
        self.assertFalse(gate_failed(result, "unverified"))

    def test_missing_behavior_does_not_pass_exact_id(self):
        baseline = manifest()
        baseline["features"][0]["behaviors"].append({
            "id": "assign-permissions", "description": "Assigns initial permissions",
            "mandatory": True, "evidenceRefs": ["evidence-1"],
        })
        result = compare_manifests(approve(baseline), approve(manifest()))
        self.assertEqual(result["matches"][0]["status"], "partial")
        self.assertEqual(result["matches"][0]["unresolvedBehaviorIds"], ["assign-permissions"])
        self.assertTrue(gate_failed(result, "partial"))

    def test_changed_authorization_requires_review(self):
        target = manifest()
        target["features"][0]["preconditions"] = ["Anonymous access"]
        result = compare_manifests(approve(manifest()), approve(target))
        self.assertEqual(result["matches"][0]["status"], "needs-sme-validation")

    def test_extra_target_behavior_requires_review(self):
        target = manifest()
        target["features"][0]["behaviors"].append({
            "id": "send-data", "description": "Sends profile to an external service",
            "mandatory": True, "evidenceRefs": ["evidence-1"],
        })
        result = compare_manifests(approve(manifest()), approve(target))
        self.assertEqual(result["matches"][0]["status"], "needs-sme-validation")

    def test_results_reference_both_input_evidence_indexes(self):
        result = compare_manifests(approve(manifest()), approve(manifest()))
        self.assertEqual(result["matches"][0]["baselineEvidenceRefs"], ["evidence-1"])
        self.assertEqual(result["matches"][0]["targetEvidenceRefs"], ["evidence-1"])

    def test_missing_target_is_unverified_even_with_complete_scope(self):
        target = manifest()
        target["features"] = []
        target["scan"]["coverage"] = "complete-in-scope"
        result = compare_manifests(approve(manifest()), target)
        self.assertEqual(result["matches"][0]["status"], "unable-to-verify")
        self.assertTrue(gate_failed(result, "unverified"))
        self.assertFalse(gate_failed(result, "missing"))

    def test_stale_approval_rejected(self):
        document = approve(manifest())
        document["evidence"][0]["contentHash"] = "d" * 64
        with self.assertRaises(ArtifactError):
            validate_manifest(document)

    def test_unverified_evidence_cannot_establish_equivalence(self):
        document = manifest()
        document["evidence"][0]["verification"] = "unverified"
        document = approve(document)
        result = compare_manifests(document, document)
        self.assertEqual(result["matches"][0]["status"], "needs-sme-validation")

    def test_reproducible_result(self):
        baseline = approve(manifest())
        self.assertEqual(compare_manifests(baseline, baseline), compare_manifests(baseline, baseline))


if __name__ == "__main__":
    unittest.main()