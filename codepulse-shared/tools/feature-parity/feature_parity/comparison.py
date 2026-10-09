"""Conservative comparison of reviewed, explicit behavior contracts."""

from collections import Counter

from .identity import digest
from .identity_mappings import validate_identity_mappings
from .validation import validate_manifest


STATUSES = (
    "equivalent", "partial", "changed-intentionally", "replaced", "missing",
    "new-in-target", "not-applicable", "unable-to-verify", "needs-sme-validation",
)
ACTIVE_STATUSES = {"confirmed", "discovered", "needs-review"}
VERIFIED = {"verified-original", "verified-tool-output"}
CONSTRAINTS = ("actors", "inputs", "outputs", "preconditions")


def _supported(feature, manifest):
    evidence = {item["id"]: item for item in manifest["evidence"]}
    return (
        feature["status"] == "confirmed"
        and feature.get("admitted", True)
        and not feature["requiresHumanValidation"]
        and all(feature[field] for field in CONSTRAINTS)
        and all(evidence[identifier]["verification"] in VERIFIED for identifier in feature["evidenceRefs"])
        and any(behavior["mandatory"] for behavior in feature["behaviors"])
    )


def compare_manifests(baseline, target, identity_mappings=None):
    validate_manifest(baseline)
    validate_manifest(target)
    mapping_decisions = validate_identity_mappings(baseline, target, identity_mappings) if identity_mappings is not None else {}
    matches = []
    used_targets = set()
    baseline_by_id = {feature["id"]: feature for feature in baseline["features"]}
    target_by_id = {
        feature["id"]: feature for feature in target["features"]
        if feature["status"] in ACTIVE_STATUSES
    }
    for feature in baseline["features"]:
        if feature["status"] not in ACTIVE_STATUSES:
            continue
        mapping = mapping_decisions.get(feature["id"])
        target_ids = mapping["targetFeatureIds"] if mapping else ([feature["id"]] if feature["id"] in target_by_id else [])
        candidates = [target_by_id[identifier] for identifier in target_ids]
        group_baselines = [baseline_by_id[identifier] for identifier in mapping["baselineFeatureIds"]] if mapping else [feature]
        mapping_type = mapping["mappingType"] if mapping else None
        for candidate in candidates:
            used_targets.add(candidate["id"])
        record = {
            "baselineFeatureId": feature["id"],
            "targetFeatureIds": sorted(candidate["id"] for candidate in candidates),
            "matchingStage": "approved-mapping" if mapping and candidates else "exact-id" if candidates else "unresolved",
            "mappingType": mapping_type,
            "mappingDecision": mapping["decision"] if mapping else None,
            "status": "unable-to-verify",
            "baselineEvidenceRefs": feature["evidenceRefs"],
            "targetEvidenceRefs": sorted({reference for candidate in candidates for reference in candidate["evidenceRefs"]}),
            "coveredBehaviorIds": [],
            "unresolvedBehaviorIds": [behavior["id"] for behavior in feature["behaviors"] if behavior["mandatory"]],
            "differences": [],
            "rationale": ["No corresponding target identified; absence is not proven"],
            "requiresHumanValidation": True,
        }
        if candidates:
            record["status"] = "needs-sme-validation"
            record["rationale"] = ["Approved mapping identifies candidate features, not behavioral equivalence"] if mapping else ["Exact ID identifies a candidate, not behavioral equivalence"]
            if not feature.get("admitted", True) or any(not candidate.get("admitted", True) for candidate in candidates):
                record["rationale"].append("A candidate is below its discovery confidence threshold")
            if all(_supported(item, baseline) for item in group_baselines) and all(_supported(candidate, target) for candidate in candidates):
                descriptions = {behavior["description"] for candidate in candidates for behavior in candidate["behaviors"]}
                baseline_descriptions = {behavior["description"] for item in group_baselines for behavior in item["behaviors"]}
                mandatory = [behavior for behavior in feature["behaviors"] if behavior["mandatory"]]
                record["coveredBehaviorIds"] = [behavior["id"] for behavior in mandatory if behavior["description"] in descriptions]
                record["unresolvedBehaviorIds"] = [behavior["id"] for behavior in mandatory if behavior["description"] not in descriptions]
                for field in CONSTRAINTS:
                    expected_values = set(feature[field])
                    if any(expected_values != set(candidate[field]) for candidate in candidates):
                        record["differences"].append(f"{field} differ")
                if descriptions - baseline_descriptions:
                    record["differences"].append("Target has additional behaviors requiring review")
                if record["differences"]:
                    record["rationale"].append("Contract constraints differ; SME interpretation is required")
                elif record["unresolvedBehaviorIds"]:
                    record["status"] = "partial" if record["coveredBehaviorIds"] else "needs-sme-validation"
                    record["rationale"].append("Mandatory behaviors lack matching target contract evidence")
                else:
                    record["status"] = "equivalent"
                    record["requiresHumanValidation"] = False
                    record["rationale"].append("Reviewed mandatory behavior descriptions and constraints agree")
                if mapping and mapping["decision"] == "intentional-difference":
                    record["status"] = "changed-intentionally"
                    record["differences"] = sorted(set(record["differences"] + mapping["differences"]))
                    record["requiresHumanValidation"] = False
                    record["rationale"].append("Human-approved intentional difference; not counted as equivalent")
        matches.append(record)
    for identifier in sorted(set(target_by_id) - used_targets):
        matches.append({
            "baselineFeatureId": None, "targetFeatureIds": [identifier],
            "matchingStage": "unresolved", "mappingType": None, "mappingDecision": None, "status": "new-in-target",
            "baselineEvidenceRefs": [], "targetEvidenceRefs": target_by_id[identifier]["evidenceRefs"],
            "coveredBehaviorIds": [], "unresolvedBehaviorIds": [], "differences": [],
            "rationale": ["No exact-ID baseline candidate; renamed features may remain unresolved"],
            "requiresHumanValidation": True,
        })
    matches.sort(key=lambda record: (record["baselineFeatureId"] or "", record["targetFeatureIds"]))
    counts = Counter(record["status"] for record in matches)
    denominator = counts["equivalent"] + counts["partial"] + counts["changed-intentionally"] + counts["missing"]
    return {
        "schemaVersion": "1.0",
        "baselineDigest": digest(baseline), "targetDigest": digest(target),
        "mappingDigest": digest(identity_mappings) if identity_mappings is not None else None,
        "methodology": "Reviewed static contracts; no application build, execution or runtime parity proof",
        "limitations": [
            "One-to-one, split and merge identity mappings are human attestations; alias-based matching is not implemented",
            "Different behavior descriptions require SME review, even if semantically equivalent",
            "Unmatched features remain unverified; complete-in-scope does not prove absence",
            "Approval references are supplied attestations; identity and approval authority are not authenticated",
        ],
        "matches": matches,
        "statistics": {
            "byStatus": {status: counts[status] for status in STATUSES},
            "verifiedDenominator": denominator,
            "equivalentCount": counts["equivalent"],
            "coveragePercent": 100 * counts["equivalent"] / denominator if denominator else None,
            "unresolvedCount": counts["unable-to-verify"] + counts["needs-sme-validation"],
        },
    }


def gate_failed(result, policy):
    if policy == "never":
        return False
    statuses = {"missing"}
    if policy in {"partial", "unverified"}:
        statuses.update({"partial", "changed-intentionally"})
    if policy == "unverified":
        statuses.update({"unable-to-verify", "needs-sme-validation"})
    if policy not in {"missing", "partial", "unverified"}:
        raise ValueError("Unsupported gate policy")
    return any(record["status"] in statuses for record in result["matches"])