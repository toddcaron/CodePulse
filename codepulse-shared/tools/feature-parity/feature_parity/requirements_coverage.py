"""Evaluate human-reviewed obligations against independently supported targets."""

import copy
from collections import Counter

from .comparison import ACTIVE_STATUSES, CONSTRAINTS, _supported
from .identity import digest
from .requirements import validate_requirements_baseline, validate_requirements_input
from .validation import ArtifactError, validate_manifest, validate_schema


def requirements_review_template(baseline):
    validate_requirements_baseline(baseline)
    return {
        "schemaVersion": "1.0", "baselineDigest": digest(baseline),
        "decisions": [{
            "requirementId": requirement["id"], "expectedRequirementDigest": digest(requirement),
            "approvedReference": "", "contract": copy.deepcopy(requirement),
            "criteriaMappings": [{"criterion": criterion, "behaviorIds": []}
                                 for criterion in requirement["acceptanceCriteria"]],
        } for requirement in sorted(baseline["document"]["requirements"], key=lambda item: item["id"])],
    }


def validate_requirements_reviews(baseline, reviews):
    validate_requirements_baseline(baseline)
    validate_schema(reviews, "feature-requirements-review-schema.json")
    if reviews["baselineDigest"] != digest(baseline):
        raise ArtifactError("Requirements reviews are stale for this baseline")
    originals = {item["id"]: item for item in baseline["document"]["requirements"]}
    reviewed = {}
    for decision in reviews["decisions"]:
        identifier = decision["requirementId"]
        if identifier not in originals or identifier in reviewed:
            raise ArtifactError("Unknown or duplicate requirement review")
        original = originals[identifier]
        if decision["expectedRequirementDigest"] != digest(original):
            raise ArtifactError("Requirement review is stale for this declaration")
        contract = decision["contract"]
        validate_requirements_input({"schemaVersion": "1.0", "applicationName": baseline["document"]["applicationName"],
                                     "requirements": [contract]})
        if contract["id"] != identifier or contract["capabilityType"] != original["capabilityType"]:
            raise ArtifactError("Requirement review cannot change identity or capability type")
        if contract["ambiguities"] or not all(contract[field] for field in CONSTRAINTS):
            raise ArtifactError("Reviewed requirement must resolve ambiguities and contract constraints")
        mandatory = {item["id"] for item in contract["behaviors"] if item["mandatory"]}
        if not mandatory:
            raise ArtifactError("Reviewed requirement needs at least one explicit mandatory behavior")
        original_mandatory = {(item["id"], item["description"]) for item in original["behaviors"] if item["mandatory"]}
        reviewed_mandatory = {(item["id"], item["description"]) for item in contract["behaviors"] if item["mandatory"]}
        if not original_mandatory.issubset(reviewed_mandatory):
            raise ArtifactError("Review cannot discard or rewrite declared mandatory behaviors")
        if not set(original["acceptanceCriteria"]).issubset(contract["acceptanceCriteria"]):
            raise ArtifactError("Review cannot discard declared acceptance criteria")
        criteria = set()
        for mapping in decision["criteriaMappings"]:
            if mapping["criterion"] in criteria or not set(mapping["behaviorIds"]).issubset(mandatory):
                raise ArtifactError("Duplicate criterion or invalid mandatory behavior mapping")
            criteria.add(mapping["criterion"])
        if criteria != set(contract["acceptanceCriteria"]):
            raise ArtifactError("Every reviewed acceptance criterion requires an explicit behavior mapping")
        reviewed[identifier] = decision
    return reviewed


def compare_requirements(baseline, reviews, target):
    reviewed = validate_requirements_reviews(baseline, reviews)
    validate_manifest(target)
    candidates = {item["id"]: item for item in target["features"] if item["status"] in ACTIVE_STATUSES}
    links = {item["requirementId"]: item["evidenceRefs"] for item in baseline["featureLinks"]}
    records = []
    for original in sorted(baseline["document"]["requirements"], key=lambda item: item["id"]):
        identifier = original["id"]
        decision = reviewed.get(identifier)
        contract = decision["contract"] if decision else original
        mandatory = [item for item in contract["behaviors"] if item["mandatory"]]
        candidate = candidates.get(identifier)
        record = {
            "requirementId": identifier, "targetFeatureId": candidate["id"] if candidate else None,
            "status": "unable-to-verify", "baselineEvidenceRefs": links[identifier],
            "targetEvidenceRefs": candidate["evidenceRefs"] if candidate else [],
            "coveredBehaviorIds": [], "unresolvedBehaviorIds": [item["id"] for item in mandatory],
            "coveredCriteria": [], "unresolvedCriteria": list(contract["acceptanceCriteria"]),
            "differences": [], "rationale": ["Requirement has no current human-approved contract"],
            "requiresHumanValidation": True,
        }
        if decision:
            record["rationale"] = ["No exact-ID target candidate; absence is not proven"]
            if candidate:
                record["status"] = "needs-sme-validation"
                record["rationale"] = ["Target candidate needs independently supported reviewed implementation evidence"]
                if _supported(candidate, target) and target["application"]["sourceType"] == "repository":
                    target_evidence = {item["id"]: item for item in target["evidence"]}
                    implementation_types = {"route", "ui", "endpoint", "service", "handler", "job", "integration",
                                            "authorization", "data-operation", "test", "report"}
                    implementation_backed = all(any(target_evidence[reference]["type"] in implementation_types
                                                    for reference in behavior["evidenceRefs"])
                                                for behavior in candidate["behaviors"])
                    if implementation_backed:
                        descriptions = {item["description"] for item in candidate["behaviors"]}
                        for field in CONSTRAINTS:
                            if set(contract[field]) != set(candidate[field]):
                                record["differences"].append(field + " differ")
                        if contract["capabilityType"] != candidate["capabilityType"]:
                            record["differences"].append("capabilityType differs")
                        if descriptions - {item["description"] for item in contract["behaviors"]}:
                            record["differences"].append("Target has additional behaviors requiring review")
                        if not record["differences"]:
                            covered = {item["id"] for item in mandatory if item["description"] in descriptions}
                            record["coveredBehaviorIds"] = sorted(covered)
                            record["unresolvedBehaviorIds"] = sorted(item["id"] for item in mandatory if item["id"] not in covered)
                            record["coveredCriteria"] = sorted(mapping["criterion"] for mapping in decision["criteriaMappings"]
                                                               if set(mapping["behaviorIds"]).issubset(covered))
                            record["unresolvedCriteria"] = sorted(set(contract["acceptanceCriteria"]) - set(record["coveredCriteria"]))
                            if not record["unresolvedBehaviorIds"] and not record["unresolvedCriteria"]:
                                record["status"] = "covered"
                                record["requiresHumanValidation"] = False
                            elif covered:
                                record["status"] = "partial"
                            record["rationale"] = ["Reviewed static behavior contracts and explicit criterion mappings evaluated; no runtime proof"]
                            if not covered:
                                record["rationale"].append("No mandatory behavior descriptions matched the supported target contract")
        records.append(record)
    counts = Counter(item["status"] for item in records)
    result = {
        "schemaVersion": "1.0", "baselineDigest": digest(baseline), "reviewsDigest": digest(reviews),
        "targetDigest": digest(target), "methodology": "Reviewed static requirements coverage; no runtime acceptance testing",
        "limitations": [
            "Exact-ID candidates only; unknown targets never prove absence",
            "Criterion mappings and resolved contracts are human attestations, not authenticated authority",
            "Coverage denominator includes every declared requirement, including unresolved records",
            "Partial records receive no full-requirement credit; source scope remains incomplete",
        ],
        "matches": records,
        "statistics": {"requirementCount": len(records), "reviewedCount": len(reviewed),
                       "coveredCount": counts["covered"], "partialCount": counts["partial"],
                       "unresolvedCount": counts["unable-to-verify"] + counts["needs-sme-validation"],
                       "coveragePercent": 100 * counts["covered"] / len(records) if records else None},
    }
    validate_schema(result, "feature-requirements-coverage-schema.json")
    return result


def coverage_gate_failed(result, policy):
    if policy == "never":
        return False
    if policy not in {"partial", "unverified"}:
        raise ValueError("Unsupported requirements coverage gate")
    statuses = {"partial"}
    if policy == "unverified":
        statuses.update({"unable-to-verify", "needs-sme-validation"})
    return any(item["status"] in statuses for item in result["matches"])