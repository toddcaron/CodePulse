"""Conservative comparison of reviewed, explicit behavior contracts."""

from collections import Counter

from .identity import digest
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


def compare_manifests(baseline, target):
    validate_manifest(baseline)
    validate_manifest(target)
    matches = []
    used_targets = set()
    target_by_id = {
        feature["id"]: feature for feature in target["features"]
        if feature["status"] in ACTIVE_STATUSES
    }
    for feature in baseline["features"]:
        if feature["status"] not in ACTIVE_STATUSES:
            continue
        candidate = target_by_id.get(feature["id"])
        record = {
            "baselineFeatureId": feature["id"],
            "targetFeatureIds": [candidate["id"]] if candidate else [],
            "matchingStage": "exact-id" if candidate else "unresolved",
            "status": "unable-to-verify",
            "baselineEvidenceRefs": feature["evidenceRefs"],
            "targetEvidenceRefs": candidate["evidenceRefs"] if candidate else [],
            "coveredBehaviorIds": [],
            "unresolvedBehaviorIds": [behavior["id"] for behavior in feature["behaviors"] if behavior["mandatory"]],
            "differences": [],
            "rationale": ["No corresponding target identified; absence is not proven"],
            "requiresHumanValidation": True,
        }
        if candidate:
            used_targets.add(candidate["id"])
            record["status"] = "needs-sme-validation"
            record["rationale"] = ["Exact ID identifies a candidate, not behavioral equivalence"]
            if not feature.get("admitted", True) or not candidate.get("admitted", True):
                record["rationale"].append("A candidate is below its discovery confidence threshold")
            if _supported(feature, baseline) and _supported(candidate, target):
                descriptions = {behavior["description"] for behavior in candidate["behaviors"]}
                mandatory = [behavior for behavior in feature["behaviors"] if behavior["mandatory"]]
                record["coveredBehaviorIds"] = [behavior["id"] for behavior in mandatory if behavior["description"] in descriptions]
                record["unresolvedBehaviorIds"] = [behavior["id"] for behavior in mandatory if behavior["description"] not in descriptions]
                for field in CONSTRAINTS:
                    if set(feature[field]) != set(candidate[field]):
                        record["differences"].append(f"{field} differ")
                if descriptions - {behavior["description"] for behavior in feature["behaviors"]}:
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
        matches.append(record)
    for identifier in sorted(set(target_by_id) - used_targets):
        matches.append({
            "baselineFeatureId": None, "targetFeatureIds": [identifier],
            "matchingStage": "unresolved", "status": "new-in-target",
            "baselineEvidenceRefs": [], "targetEvidenceRefs": target_by_id[identifier]["evidenceRefs"],
            "coveredBehaviorIds": [], "unresolvedBehaviorIds": [], "differences": [],
            "rationale": ["No exact-ID baseline candidate; renamed features may remain unresolved"],
            "requiresHumanValidation": True,
        })
    matches.sort(key=lambda record: (record["baselineFeatureId"] or "", record["targetFeatureIds"]))
    counts = Counter(record["status"] for record in matches)
    denominator = counts["equivalent"] + counts["partial"] + counts["missing"]
    return {
        "schemaVersion": "1.0",
        "baselineDigest": digest(baseline), "targetDigest": digest(target),
        "methodology": "Reviewed static contracts; no application build, execution or runtime parity proof",
        "limitations": [
            "Exact-ID candidate selection only; aliases, split/merge and approved mappings are not implemented",
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
        statuses.add("partial")
    if policy == "unverified":
        statuses.update({"unable-to-verify", "needs-sme-validation"})
    if policy not in {"missing", "partial", "unverified"}:
        raise ValueError("Unsupported gate policy")
    return any(record["status"] in statuses for record in result["matches"])