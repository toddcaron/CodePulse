"""Apply explicit human attestations without promoting static evidence."""

import copy
from collections import Counter

from . import __version__
from .identity import contract_digest, digest
from .validation import ArtifactError, validate_manifest, validate_schema


def review_template(manifest):
    validate_manifest(manifest)
    return {
        "schemaVersion": "1.0", "baseManifestDigest": digest(manifest),
        "decisions": [{
            "featureId": feature["id"],
            "expectedContractDigest": contract_digest(feature, manifest["evidence"]),
            "decision": "needs-review", "approvedReference": "",
            "reviewerNote": "",
        } for feature in sorted(manifest["features"], key=lambda item: item["id"])
            if feature["status"] in {"discovered", "confirmed", "needs-review"}],
    }


def reconcile_manifest(manifest, reviews):
    validate_manifest(manifest)
    validate_schema(reviews, "feature-review-decision-schema.json")
    if reviews["baseManifestDigest"] != digest(manifest):
        raise ArtifactError("Review batch is stale for this manifest")
    decisions = reviews["decisions"]
    identifiers = [decision["featureId"] for decision in decisions]
    if len(identifiers) != len(set(identifiers)):
        raise ArtifactError("Conflicting or duplicate review decisions")
    originals = {feature["id"]: feature for feature in manifest["features"]}
    for decision in decisions:
        original = originals.get(decision["featureId"])
        if original is None:
            raise ArtifactError("Review references an unknown feature")
        if original["status"] in {"merged", "split"}:
            raise ArtifactError("Lineage review actions are not supported in this milestone")
        if decision["expectedContractDigest"] != contract_digest(original, manifest["evidence"]):
            raise ArtifactError("Review decision is stale for current behavior or evidence")
    result = copy.deepcopy(manifest)
    features = {feature["id"]: feature for feature in result["features"]}
    reviewed_ids = set(identifiers)
    result["reviewQueue"] = [item for item in result["reviewQueue"] if item["featureId"] not in reviewed_ids]
    changes = []
    for decision in sorted(decisions, key=lambda item: item["featureId"]):
        feature = features[decision["featureId"]]
        before_digest = digest(feature)
        feature.update(copy.deepcopy(decision.get("updates", {})))
        feature["status"] = decision["decision"]
        feature["requiresHumanValidation"] = decision["decision"] != "confirmed"
        feature.pop("review", None)
        if "reviewerNote" in decision:
            feature["reviewerNote"] = decision["reviewerNote"]
        if feature["status"] == "confirmed":
            evidence_ids = {item["id"] for item in result["evidence"]}
            if not set(feature["evidenceRefs"]).issubset(evidence_ids):
                raise ArtifactError("Reviewed feature references unknown evidence")
            feature["review"] = {
                "approvedReference": decision["approvedReference"],
                "contractDigest": contract_digest(feature, result["evidence"]),
            }
            referenced = [item for item in result["evidence"] if item["id"] in feature["evidenceRefs"]]
            if not feature.get("admitted", True) or any(
                item["verification"] not in {"verified-original", "verified-tool-output"} for item in referenced
            ):
                result["reviewQueue"].append({
                    "featureId": feature["id"],
                    "reason": "Feature reviewed; evidence verification or confidence admission remains insufficient for parity",
                    "evidenceRefs": feature["evidenceRefs"],
                })
        elif feature["status"] == "needs-review":
            result["reviewQueue"].append({
                "featureId": feature["id"], "reason": "Human reviewer requested further validation",
                "evidenceRefs": feature["evidenceRefs"],
            })
        changes.append({
            "featureId": feature["id"], "decision": decision["decision"],
            "approvedReference": decision["approvedReference"],
            "beforeDigest": before_digest, "afterDigest": digest(feature),
        })
    result["reviewQueue"].sort(key=lambda item: (item["featureId"], item["reason"]))
    validate_manifest(result)
    counts = Counter(feature["status"] for feature in result["features"])
    artifacts = {
        "feature-manifest.json": result,
        "review-queue.json": result["reviewQueue"],
        "reconciliation-log.json": {
            "schemaVersion": "1.0", "engineVersion": __version__,
            "inputManifestDigest": digest(manifest), "reviewBatchDigest": digest(reviews),
            "outputManifestDigest": digest(result), "changes": changes,
            "statistics": {
                "appliedDecisions": len(changes), "confirmedFeatures": counts["confirmed"],
                "rejectedFeatures": counts["rejected"], "deprecatedFeatures": counts["deprecated"],
                "needsReview": counts["needs-review"] + counts["discovered"],
                "reviewQueueItems": len(result["reviewQueue"]),
            },
            "evidenceVerificationChanged": False, "confidenceChanged": False,
            "applicationCodeExecuted": False,
        },
    }
    validate_schema(artifacts["reconciliation-log.json"], "feature-reconciliation-log-schema.json")
    return artifacts