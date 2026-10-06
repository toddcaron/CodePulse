"""Persist evidence-bound agent proposals without approval or verification credit."""

import copy

from . import __version__
from .identity import contract_digest, digest
from .validation import ArtifactError, validate_manifest, validate_schema


def enrichment_template(manifest):
    validate_manifest(manifest)
    active = [item for item in manifest["features"] if item["status"] in {"discovered", "confirmed", "needs-review"}]
    if not active or len(active) > 100:
        raise ArtifactError("Enrichment template requires between 1 and 100 active features")
    evidence = {item["id"]: item for item in manifest["evidence"]}
    return {
        "schemaVersion": "1.0", "baseManifestDigest": digest(manifest),
        "inventoryDigest": manifest["scan"]["inventoryDigest"],
        "provenance": {"agent": "", "model": "", "version": ""},
        "proposals": [{
            "id": feature["id"], "featureId": feature["id"],
            "expectedContractDigest": contract_digest(feature, manifest["evidence"]),
            "evidence": [{"id": identifier, "contentHash": evidence[identifier]["contentHash"],
                          "recordDigest": digest(evidence[identifier])} for identifier in sorted(feature["evidenceRefs"])],
            "updates": {}, "rationale": "",
        } for feature in sorted(active, key=lambda item: item["id"])],
    }


def import_enrichment(manifest, enrichment):
    validate_manifest(manifest)
    validate_schema(enrichment, "feature-enrichment-schema.json")
    if enrichment["baseManifestDigest"] != digest(manifest):
        raise ArtifactError("Enrichment is stale for this manifest")
    if enrichment["inventoryDigest"] != manifest["scan"]["inventoryDigest"]:
        raise ArtifactError("Enrichment inventory digest does not match")
    features = {item["id"]: item for item in manifest["features"]}
    evidence = {item["id"]: item for item in manifest["evidence"]}
    proposal_ids = set()
    feature_ids = set()
    for proposal in enrichment["proposals"]:
        identifier = proposal["featureId"]
        if proposal["id"] in proposal_ids or identifier in feature_ids:
            raise ArtifactError("Duplicate or conflicting enrichment proposals")
        proposal_ids.add(proposal["id"])
        feature_ids.add(identifier)
        feature = features.get(identifier)
        if feature is None or feature["status"] not in {"discovered", "confirmed", "needs-review"}:
            raise ArtifactError("Enrichment must reference an active existing feature")
        if proposal["expectedContractDigest"] != contract_digest(feature, manifest["evidence"]):
            raise ArtifactError("Enrichment feature contract is stale")
        cited = set()
        for citation in proposal["evidence"]:
            record = evidence.get(citation["id"])
            if record is None or citation["id"] in cited:
                raise ArtifactError("Unknown or duplicate enrichment evidence")
            if citation["contentHash"] != record["contentHash"] or citation["recordDigest"] != digest(record):
                raise ArtifactError("Enrichment evidence is stale")
            cited.add(citation["id"])
        required = set(feature["evidenceRefs"]) | set(proposal["updates"].get("evidenceRefs", []))
        if cited != required:
            raise ArtifactError("Enrichment must cite current and proposed feature evidence exactly")
    result = copy.deepcopy(manifest)
    result_features = {item["id"]: item for item in result["features"]}
    changes = []
    for proposal in sorted(enrichment["proposals"], key=lambda item: item["featureId"]):
        feature = result_features[proposal["featureId"]]
        before = digest(feature)
        withdrawn = "review" in feature
        feature.update(copy.deepcopy(proposal["updates"]))
        feature.pop("review", None)
        feature["status"] = "needs-review"
        feature["requiresHumanValidation"] = True
        reason = "Unapproved agent enrichment requires independent human review"
        if not any(item["featureId"] == feature["id"] and item["reason"] == reason for item in result["reviewQueue"]):
            result["reviewQueue"].append({"featureId": feature["id"], "reason": reason, "evidenceRefs": list(feature["evidenceRefs"])})
        changes.append({"proposalId": proposal["id"], "featureId": feature["id"],
                        "beforeDigest": before, "afterDigest": digest(feature), "approvalWithdrawn": withdrawn})
    result["reviewQueue"].sort(key=lambda item: (item["featureId"], item["reason"]))
    validate_manifest(result)
    log = {
        "schemaVersion": "1.0", "engineVersion": __version__, "inputManifestDigest": digest(manifest),
        "enrichmentDigest": digest(enrichment), "outputManifestDigest": digest(result), "changes": changes,
        "statistics": {"importedProposals": len(changes), "approvalsWithdrawn": sum(item["approvalWithdrawn"] for item in changes),
                       "reviewQueueItems": len(result["reviewQueue"])},
        "evidenceVerificationChanged": False, "confidenceChanged": False,
        "admissionChanged": False, "applicationCodeExecuted": False,
    }
    validate_schema(log, "feature-enrichment-log-schema.json")
    return {"feature-manifest.json": result, "enrichment-proposals.json": copy.deepcopy(enrichment),
            "review-queue.json": result["reviewQueue"], "enrichment-log.json": log}