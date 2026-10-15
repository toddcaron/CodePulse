import copy
import unittest

from test_validation import manifest
from feature_parity.comparison import compare_manifests, gate_failed
from feature_parity.identity import contract_digest, digest
from feature_parity.identity_mappings import (
    identity_mappings_template, identity_suggestions, reconcile_identity_aliases,
)
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
        with self.assertRaises(ValueError):
            gate_failed(result, "missing")

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

    def test_alias_suggestion_is_digest_bound_and_never_grants_parity_credit(self):
        baseline = manifest()
        baseline["features"][0]["aliases"] = ["Register User"]
        baseline = approve(baseline)
        target = manifest()
        target["features"][0]["id"] = "identity.register-user"
        target["features"][0]["name"] = "Register User"
        target = approve(target)

        suggestions = identity_suggestions(baseline, target)
        result = compare_manifests(baseline, target)

        self.assertEqual(suggestions["baselineDigest"], digest(baseline))
        self.assertEqual(suggestions["targetDigest"], digest(target))
        self.assertEqual(suggestions["suggestions"][0]["matchBasis"], "shared-alias")
        self.assertEqual(suggestions["suggestions"][0]["sharedLabels"], ["Register User"])
        self.assertEqual(result["statistics"]["equivalentCount"], 0)
        self.assertEqual(result["matches"][0]["matchingStage"], "unresolved")

    def test_contract_term_suggestion_is_explanatory_and_advisory(self):
        baseline = approve(manifest())
        baseline["features"][0]["name"] = "Create User"
        target = manifest()
        target["features"][0]["id"] = "identity.register-member"
        target["features"][0]["name"] = "Register Member"
        target = approve(target)

        suggestions = identity_suggestions(baseline, target)
        result = compare_manifests(baseline, target)

        self.assertEqual(len(suggestions["suggestions"]), 1)
        self.assertEqual(suggestions["suggestions"][0]["matchBasis"], "shared-contract-terms")
        self.assertGreaterEqual(len(suggestions["suggestions"][0]["sharedContractTerms"]), 2)
        self.assertIsInstance(suggestions["suggestions"][0]["similarityScore"], float)
        self.assertEqual(result["matches"][0]["matchingStage"], "unresolved")
        self.assertEqual(result["statistics"]["equivalentCount"], 0)

    def test_unrelated_contracts_do_not_receive_similarity_suggestions(self):
        baseline = manifest()
        target = copy.deepcopy(baseline)
        target["features"][0].update({
            "id": "inventory.restock-product", "name": "Restock Product", "domain": "Inventory",
            "actors": ["Warehouse operator"], "inputs": ["Supplier shipment"],
            "outputs": ["Stock quantity"], "preconditions": ["Shipment received"],
            "behaviors": [{
                "id": "restock", "description": "Adds delivered units to available inventory",
                "mandatory": True, "evidenceRefs": ["evidence-1"],
            }],
        })

        suggestions = identity_suggestions(baseline, target)

        self.assertEqual(suggestions["suggestions"], [])

    def test_approved_identity_aliases_persist_for_later_scans(self):
        baseline = approve(manifest())
        target = manifest()
        target["features"][0]["id"] = "identity.register-user"
        target["features"][0]["name"] = "Register User"
        target = approve(target)
        mappings = identity_mappings_template(baseline, target)
        mappings["mappings"].append({
            "mappingType": "one-to-one", "baselineFeatureIds": ["identity.create-user"],
            "targetFeatureIds": ["identity.register-user"], "decision": "same-capability",
            "rationale": "Reviewed rename", "differences": [], "approvedReference": "Review 18",
        })

        artifacts = reconcile_identity_aliases(baseline, target, mappings)
        reconciled = artifacts["feature-manifest.json"]
        later_scan = manifest()
        later_scan["features"][0]["id"] = "identity.onboard-user"
        later_scan["features"][0]["name"] = "Onboard Account"
        later_scan["features"][0]["aliases"] = [baseline["features"][0]["name"]]

        suggestions = identity_suggestions(reconciled, later_scan)

        self.assertIn(baseline["features"][0]["name"], reconciled["features"][0]["aliases"])
        self.assertEqual(reconciled["features"][0]["status"], "confirmed")
        self.assertEqual(suggestions["suggestions"][0]["targetFeatureId"], "identity.onboard-user")
        self.assertEqual(artifacts["identity-reconciliation-log.json"]["statistics"]["reconciledMappings"], 1)

    def test_identity_reconciliation_rejects_intentional_differences(self):
        baseline = approve(manifest())
        target = manifest()
        target["features"][0]["id"] = "identity.register-user"
        target = approve(target)
        mappings = identity_mappings_template(baseline, target)
        mappings["mappings"].append({
            "mappingType": "one-to-one", "baselineFeatureIds": ["identity.create-user"],
            "targetFeatureIds": ["identity.register-user"], "decision": "intentional-difference",
            "rationale": "Approved change", "differences": ["Behavior changed"],
            "approvedReference": "Review 19",
        })

        with self.assertRaises(ArtifactError):
            reconcile_identity_aliases(baseline, target, mappings)

    def test_identity_reconciliation_carries_aliases_across_split_and_merge(self):
        baseline = approve(manifest())
        split_target = manifest()
        split_target["features"][0]["id"] = "identity.create-account"
        split_target["features"][0]["name"] = "Create Account"
        child = copy.deepcopy(split_target["features"][0])
        child["id"] = "identity.assign-permissions"
        child["name"] = "Assign Permissions"
        split_target["features"].append(child)
        split_target = approve(split_target)
        split_mappings = identity_mappings_template(baseline, split_target)
        split_mappings["mappings"].append({
            "mappingType": "split", "baselineFeatureIds": ["identity.create-user"],
            "targetFeatureIds": ["identity.create-account", "identity.assign-permissions"],
            "decision": "same-capability", "rationale": "Reviewed capability split",
            "differences": [], "approvedReference": "Review 21",
        })

        split_artifacts = reconcile_identity_aliases(baseline, split_target, split_mappings)
        split_result = split_artifacts["feature-manifest.json"]
        self.assertTrue(all("Create User" in feature["aliases"] for feature in split_result["features"]))
        self.assertEqual(split_artifacts["identity-reconciliation-log.json"]["statistics"]["addedAliases"], 2)

        merge_baseline = copy.deepcopy(baseline)
        second_baseline = copy.deepcopy(merge_baseline["features"][0])
        second_baseline["id"] = "identity.assign-permissions"
        second_baseline["name"] = "Assign Permissions"
        merge_baseline["features"].append(second_baseline)
        merge_target = manifest()
        merge_target["features"][0]["id"] = "identity.manage-identity"
        merge_target["features"][0]["name"] = "Manage Identity"
        merge_baseline = approve(merge_baseline)
        merge_target = approve(merge_target)
        merge_mappings = identity_mappings_template(merge_baseline, merge_target)
        merge_mappings["mappings"].append({
            "mappingType": "merge",
            "baselineFeatureIds": ["identity.create-user", "identity.assign-permissions"],
            "targetFeatureIds": ["identity.manage-identity"],
            "decision": "same-capability", "rationale": "Reviewed capability merge",
            "differences": [], "approvedReference": "Review 22",
        })

        merge_artifacts = reconcile_identity_aliases(merge_baseline, merge_target, merge_mappings)
        merged_feature = merge_artifacts["feature-manifest.json"]["features"][0]
        self.assertEqual(set(merged_feature["aliases"]), {"Create User", "Assign Permissions"})
        self.assertEqual(merge_artifacts["identity-reconciliation-log.json"]["statistics"]["addedAliases"], 2)

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