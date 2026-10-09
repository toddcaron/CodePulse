import copy
import unittest

from test_validation import manifest
from feature_parity.comparison import compare_manifests, gate_failed
from feature_parity.identity import contract_digest, digest
from feature_parity.identity_mappings import identity_mappings_template
from feature_parity.validation import ArtifactError, validate_manifest


def approve(document):
    for feature in document["features"]:
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

    def test_approved_rename_mapping_preserves_contract_comparison(self):
        baseline = approve(manifest())
        target = manifest()
        target["features"][0]["id"] = "identity.register-user"
        target = approve(target)
        mappings = identity_mappings_template(baseline, target)
        mappings["mappings"].append({
            "mappingType": "one-to-one", "baselineFeatureIds": ["identity.create-user"],
            "targetFeatureIds": ["identity.register-user"],
            "decision": "same-capability", "rationale": "Reviewed rename",
            "differences": [], "approvedReference": "Architecture review 12",
        })

        result = compare_manifests(baseline, target, mappings)

        self.assertEqual(result["matches"][0]["matchingStage"], "approved-mapping")
        self.assertEqual(result["matches"][0]["status"], "equivalent")
        self.assertEqual(result["matches"][0]["targetFeatureIds"], ["identity.register-user"])
        self.assertEqual(result["statistics"]["byStatus"]["new-in-target"], 0)
        self.assertEqual(result["mappingDigest"], digest(mappings))

    def test_intentional_difference_is_not_equivalent_coverage(self):
        baseline = approve(manifest())
        target = manifest()
        target["features"][0]["id"] = "identity.register-user"
        target["features"][0]["behaviors"][0]["description"] = "Registers an account"
        target = approve(target)
        mappings = identity_mappings_template(baseline, target)
        mappings["mappings"].append({
            "mappingType": "one-to-one", "baselineFeatureIds": ["identity.create-user"],
            "targetFeatureIds": ["identity.register-user"],
            "decision": "intentional-difference", "rationale": "Approved behavior change",
            "differences": ["Account registration behavior changed"], "approvedReference": "Change 42",
        })

        result = compare_manifests(baseline, target, mappings)

        self.assertEqual(result["matches"][0]["status"], "changed-intentionally")
        self.assertIn("Account registration behavior changed", result["matches"][0]["differences"])
        self.assertEqual(result["statistics"]["equivalentCount"], 0)
        self.assertEqual(result["statistics"]["coveragePercent"], 0)
        self.assertTrue(gate_failed(result, "partial"))

    def test_stale_and_conflicting_identity_mappings_are_rejected(self):
        baseline = approve(manifest())
        target = manifest()
        target["features"][0]["id"] = "identity.register-user"
        target = approve(target)
        mappings = identity_mappings_template(baseline, target)
        mapping = {
            "mappingType": "one-to-one", "baselineFeatureIds": ["identity.create-user"],
            "targetFeatureIds": ["identity.register-user"],
            "decision": "same-capability", "rationale": "Reviewed rename",
            "differences": [], "approvedReference": "Review 12",
        }
        mappings["mappings"] = [mapping]
        stale = copy.deepcopy(mappings)
        stale["targetDigest"] = "0" * 64
        with self.assertRaises(ArtifactError):
            compare_manifests(baseline, target, stale)

        duplicate = copy.deepcopy(mappings)
        duplicate["mappings"].append(copy.deepcopy(mapping))
        with self.assertRaises(ArtifactError):
            compare_manifests(baseline, target, duplicate)

        exact_target = manifest()
        conflicting = identity_mappings_template(baseline, exact_target)
        conflicting["mappings"] = [dict(mapping, targetFeatureIds=["identity.create-user"])]
        with self.assertRaises(ArtifactError):
            compare_manifests(baseline, exact_target, conflicting)

    def test_split_mapping_compares_children_without_double_counting(self):
        baseline = manifest()
        baseline["features"][0]["behaviors"].append({
            "id": "assign-permissions", "description": "Assigns initial permissions",
            "mandatory": True, "evidenceRefs": ["evidence-1"],
        })
        baseline = approve(baseline)
        target = manifest()
        target["features"][0]["id"] = "identity.create-user"
        second = copy.deepcopy(target["features"][0])
        second["id"] = "identity.assign-permissions"
        second["name"] = "Assign Permissions"
        second["behaviors"] = [{
            "id": "assign-permissions", "description": "Assigns initial permissions",
            "mandatory": True, "evidenceRefs": ["evidence-1"],
        }]
        target["features"][0]["behaviors"] = [target["features"][0]["behaviors"][0]]
        target["features"].append(second)
        target = approve(target)
        mappings = identity_mappings_template(baseline, target)
        mappings["mappings"].append({
            "mappingType": "split", "baselineFeatureIds": ["identity.create-user"],
            "targetFeatureIds": ["identity.create-user", "identity.assign-permissions"],
            "decision": "same-capability", "rationale": "Capability was split into two modules",
            "differences": [], "approvedReference": "Architecture review 14",
        })

        result = compare_manifests(baseline, target, mappings)

        self.assertEqual(len(result["matches"]), 1)
        self.assertEqual(result["matches"][0]["mappingType"], "split")
        self.assertEqual(result["matches"][0]["status"], "equivalent")
        self.assertEqual(result["matches"][0]["targetFeatureIds"], ["identity.assign-permissions", "identity.create-user"])
        self.assertEqual(result["statistics"]["verifiedDenominator"], 1)
        self.assertEqual(result["statistics"]["equivalentCount"], 1)

        weaker_child = copy.deepcopy(target)
        weaker_child["features"][1]["preconditions"] = ["Anonymous access"]
        weaker_child = approve(weaker_child)
        weaker_mappings = identity_mappings_template(baseline, weaker_child)
        weaker_mappings["mappings"].append(copy.deepcopy(mappings["mappings"][0]))
        weaker_result = compare_manifests(baseline, weaker_child, weaker_mappings)
        self.assertEqual(weaker_result["matches"][0]["status"], "needs-sme-validation")
        self.assertIn("preconditions differ", weaker_result["matches"][0]["differences"])

    def test_merge_mapping_accounts_for_each_baseline_once(self):
        baseline = manifest()
        second = copy.deepcopy(baseline["features"][0])
        second["id"] = "identity.assign-permissions"
        second["name"] = "Assign Permissions"
        second["behaviors"] = [{
            "id": "assign-permissions", "description": "Assigns initial permissions",
            "mandatory": True, "evidenceRefs": ["evidence-1"],
        }]
        baseline["features"].append(second)
        baseline = approve(baseline)
        target = manifest()
        target["features"][0]["id"] = "identity.create-user"
        target["features"][0]["behaviors"].append({
            "id": "assign-permissions", "description": "Assigns initial permissions",
            "mandatory": True, "evidenceRefs": ["evidence-1"],
        })
        target = approve(target)
        mappings = identity_mappings_template(baseline, target)
        mappings["mappings"].append({
            "mappingType": "merge", "baselineFeatureIds": ["identity.create-user", "identity.assign-permissions"],
            "targetFeatureIds": ["identity.create-user"],
            "decision": "same-capability", "rationale": "Capabilities were consolidated",
            "differences": [], "approvedReference": "Architecture review 15",
        })

        result = compare_manifests(baseline, target, mappings)

        self.assertEqual(len(result["matches"]), 2)
        self.assertTrue(all(item["mappingType"] == "merge" for item in result["matches"]))
        self.assertTrue(all(item["status"] == "equivalent" for item in result["matches"]))
        self.assertEqual(result["statistics"]["verifiedDenominator"], 2)
        self.assertEqual(result["statistics"]["equivalentCount"], 2)
        self.assertEqual(result["statistics"]["byStatus"]["new-in-target"], 0)

        broader_target = copy.deepcopy(target)
        broader_target["features"][0]["actors"] = ["Administrator", "Auditor"]
        broader_target = approve(broader_target)
        broader_mappings = identity_mappings_template(baseline, broader_target)
        broader_mappings["mappings"].append(copy.deepcopy(mappings["mappings"][0]))
        broader_result = compare_manifests(baseline, broader_target, broader_mappings)
        self.assertTrue(all(item["status"] == "needs-sme-validation" for item in broader_result["matches"]))
        self.assertTrue(all("actors differ" in item["differences"] for item in broader_result["matches"]))


if __name__ == "__main__":
    unittest.main()