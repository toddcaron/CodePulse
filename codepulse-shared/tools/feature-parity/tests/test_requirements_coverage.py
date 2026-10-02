import copy
import unittest

from test_requirements import requirements_document
from test_validation import manifest
from test_comparison import approve
from feature_parity.identity import digest
from feature_parity.requirements import ingest_requirements
from feature_parity.requirements_coverage import compare_requirements, coverage_gate_failed, requirements_review_template, validate_requirements_reviews
from feature_parity.validation import ArtifactError


def reviewed_baseline():
    baseline = ingest_requirements(requirements_document(), "requirements.json", "a" * 64, 10)["requirements-baseline.json"]
    reviews = requirements_review_template(baseline)
    decision = reviews["decisions"][0]
    decision["approvedReference"] = "Synthetic product-owner review"
    decision["criteriaMappings"][0]["behaviorIds"] = ["create-account"]
    return baseline, reviews


class RequirementsCoverageTests(unittest.TestCase):
    def test_reviewed_contract_and_supported_target_are_covered(self):
        baseline, reviews = reviewed_baseline()
        before = copy.deepcopy((baseline, reviews))
        result = compare_requirements(baseline, reviews, approve(manifest()))
        self.assertEqual(result["statistics"]["coveredCount"], 1)
        self.assertEqual(result["matches"][0]["coveredCriteria"], ["One account is created"])
        self.assertEqual((baseline, reviews), before)
        self.assertEqual(baseline["evidence"][0]["verification"], "partially-verified")

    def test_unreviewed_requirement_receives_no_credit(self):
        baseline, reviews = reviewed_baseline()
        reviews["decisions"] = []
        result = compare_requirements(baseline, reviews, approve(manifest()))
        self.assertEqual(result["statistics"]["coveragePercent"], 0)
        self.assertEqual(result["matches"][0]["status"], "unable-to-verify")

    def test_invalid_review_and_criterion_mappings_reject_batch(self):
        mutations = [
            lambda review: review.update(baselineDigest="0" * 64),
            lambda review: review["decisions"][0].update(expectedRequirementDigest="0" * 64),
            lambda review: review["decisions"].append(copy.deepcopy(review["decisions"][0])),
            lambda review: review["decisions"][0].update(approvedReference=" "),
            lambda review: review["decisions"][0]["contract"].update(ambiguities=["Unresolved role"]),
            lambda review: review["decisions"][0]["contract"].update(actors=[]),
            lambda review: review["decisions"][0]["criteriaMappings"].clear(),
            lambda review: review["decisions"][0]["criteriaMappings"][0].update(behaviorIds=["unknown"]),
            lambda review: review["decisions"][0]["contract"].update(acceptanceCriteria=[]),
            lambda review: review["decisions"][0]["contract"]["behaviors"][0].update(description="Rewritten obligation"),
        ]
        for mutation in mutations:
            baseline, reviews = reviewed_baseline()
            mutation(reviews)
            with self.subTest(mutation=mutation), self.assertRaises(ArtifactError):
                validate_requirements_reviews(baseline, reviews)

    def test_partial_requires_explicit_uncovered_mandatory_behavior(self):
        baseline, reviews = reviewed_baseline()
        contract = reviews["decisions"][0]["contract"]
        contract["behaviors"].append({"id": "send-notice", "description": "Sends account notice", "mandatory": True})
        result = compare_requirements(baseline, reviews, approve(manifest()))
        self.assertEqual(result["matches"][0]["status"], "partial")
        self.assertEqual(result["matches"][0]["unresolvedBehaviorIds"], ["send-notice"])

    def test_constraints_or_extra_behaviors_cannot_receive_credit(self):
        baseline, reviews = reviewed_baseline()
        for field in ("actors", "outputs", "preconditions"):
            target = manifest()
            target["features"][0][field] = ["Different contract"]
            result = compare_requirements(baseline, reviews, approve(target))
            self.assertEqual(result["matches"][0]["status"], "needs-sme-validation")
            self.assertEqual(result["matches"][0]["coveredBehaviorIds"], [])

    def test_unsupported_or_document_only_targets_cannot_cover(self):
        baseline, reviews = reviewed_baseline()
        for mutation in (
            lambda target: target["evidence"][0].update(verification="partially-verified"),
            lambda target: target["features"][0].update(admitted=False),
            lambda target: target["evidence"][0].update(type="requirement"),
            lambda target: target["application"].update(sourceType="requirements"),
        ):
            target = manifest()
            mutation(target)
            result = compare_requirements(baseline, reviews, approve(target))
            self.assertEqual(result["statistics"]["coveredCount"], 0)

    def test_unmatched_is_not_missing_and_empty_percentage_is_null(self):
        baseline, reviews = reviewed_baseline()
        target = manifest()
        target["features"] = []
        result = compare_requirements(baseline, reviews, target)
        self.assertEqual(result["matches"][0]["status"], "unable-to-verify")
        document = requirements_document()
        document["requirements"] = []
        empty = ingest_requirements(document, "requirements.json", "a" * 64, 1)["requirements-baseline.json"]
        result = compare_requirements(empty, requirements_review_template(empty), target)
        self.assertIsNone(result["statistics"]["coveragePercent"])

    def test_template_cannot_approve_requirements(self):
        baseline, _ = reviewed_baseline()
        with self.assertRaises(ArtifactError):
            validate_requirements_reviews(baseline, requirements_review_template(baseline))

    def test_review_cannot_demote_original_mandatory_behavior(self):
        baseline, reviews = reviewed_baseline()
        contract = reviews["decisions"][0]["contract"]
        contract["behaviors"][0]["mandatory"] = False
        contract["behaviors"].append({"id": "substitute", "description": "Creates an account", "mandatory": True})
        reviews["decisions"][0]["criteriaMappings"][0]["behaviorIds"] = ["substitute"]
        with self.assertRaises(ArtifactError):
            validate_requirements_reviews(baseline, reviews)

    def test_criterion_requires_all_mapped_mandatory_behaviors(self):
        baseline, reviews = reviewed_baseline()
        decision = reviews["decisions"][0]
        decision["contract"]["behaviors"].append({"id": "send-notice", "description": "Sends notice", "mandatory": True})
        decision["criteriaMappings"][0]["behaviorIds"].append("send-notice")
        result = compare_requirements(baseline, reviews, approve(manifest()))
        record = result["matches"][0]
        self.assertEqual(record["status"], "partial")
        self.assertEqual(record["coveredCriteria"], [])
        self.assertEqual(record["unresolvedCriteria"], ["One account is created"])
        self.assertTrue(coverage_gate_failed(result, "partial"))
        self.assertFalse(coverage_gate_failed(result, "never"))

    def test_unreviewed_requirement_stays_in_coverage_denominator(self):
        document = requirements_document()
        second = copy.deepcopy(document["requirements"][0])
        second["id"] = "identity.disable-user"
        document["requirements"].append(second)
        baseline = ingest_requirements(document, "requirements.json", "a" * 64, 10)["requirements-baseline.json"]
        reviews = requirements_review_template(baseline)
        reviews["decisions"] = [item for item in reviews["decisions"] if item["requirementId"] == "identity.create-user"]
        reviews["decisions"][0]["approvedReference"] = "Synthetic review"
        reviews["decisions"][0]["criteriaMappings"][0]["behaviorIds"] = ["create-account"]
        result = compare_requirements(baseline, reviews, approve(manifest()))
        self.assertEqual(result["statistics"]["requirementCount"], 2)
        self.assertEqual(result["statistics"]["coveragePercent"], 50)
        self.assertEqual(result["statistics"]["unresolvedCount"], 1)
        self.assertTrue(coverage_gate_failed(result, "unverified"))
        self.assertFalse(coverage_gate_failed(result, "partial"))

    def test_additional_target_behavior_requires_review(self):
        baseline, reviews = reviewed_baseline()
        target = manifest()
        target["features"][0]["behaviors"].append({"id": "additional", "description": "Additional action", "mandatory": False,
                                                    "evidenceRefs": ["evidence-1"]})
        result = compare_requirements(baseline, reviews, approve(target))
        self.assertEqual(result["matches"][0]["status"], "needs-sme-validation")
        self.assertEqual(result["matches"][0]["coveredCriteria"], [])

    def test_resolved_prose_review_does_not_change_original_proposal(self):
        from feature_parity.prose_requirements import extract_prose_requirements

        document, source_map = extract_prose_requirements("Requirement: Create User\n", "Synthetic Requirements")
        baseline = ingest_requirements(document, "requirements.md", "a" * 64, 1, source_map)["requirements-baseline.json"]
        reviews = requirements_review_template(baseline)
        decision = reviews["decisions"][0]
        identifier = decision["requirementId"]
        contract = copy.deepcopy(requirements_document()["requirements"][0])
        contract["id"] = identifier
        decision["contract"] = contract
        decision["approvedReference"] = "Synthetic resolved prose review"
        decision["criteriaMappings"] = [{"criterion": "One account is created", "behaviorIds": ["create-account"]}]
        target = manifest()
        target["features"][0]["id"] = identifier
        result = compare_requirements(baseline, reviews, approve(target))
        self.assertEqual(result["statistics"]["coveredCount"], 1)
        self.assertFalse(baseline["document"]["requirements"][0]["behaviors"][0]["mandatory"])
        self.assertTrue(baseline["document"]["requirements"][0]["ambiguities"])
        self.assertEqual(result, compare_requirements(baseline, reviews, approve(target)))