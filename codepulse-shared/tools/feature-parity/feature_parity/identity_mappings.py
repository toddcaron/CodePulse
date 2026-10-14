"""Digest-bound human decisions for feature identity and lineage mappings."""

import copy
import re

from . import __version__
from .identity import digest
from .validation import ArtifactError, validate_manifest, validate_schema


ACTIVE_STATUSES = {"confirmed", "discovered", "needs-review"}
CONTRACT_DIMENSIONS = ("domain", "actors", "inputs", "outputs", "preconditions", "behaviors")
GENERIC_TERMS = {
    "account", "administrator", "application", "business", "create", "data",
    "feature", "manage", "record", "system", "user",
}


def _normalize_label(value):
    return " ".join(value.casefold().split())


def _contract_terms(feature):
    values = {
        "domain": [feature["domain"]],
        "actors": feature["actors"],
        "inputs": feature["inputs"],
        "outputs": feature["outputs"],
        "preconditions": feature["preconditions"],
        "behaviors": [behavior["description"] for behavior in feature["behaviors"]],
    }
    return {
        dimension: {
            token for value in dimension_values
            for token in re.findall(r"[a-z0-9]+", value.casefold())
            if len(token) > 2 and token not in GENERIC_TERMS
        }
        for dimension, dimension_values in values.items()
    }


def identity_mappings_template(baseline, target):
    validate_manifest(baseline)
    validate_manifest(target)
    return {
        "schemaVersion": "1.1",
        "baselineDigest": digest(baseline),
        "targetDigest": digest(target),
        "mappings": [],
    }


def identity_suggestions(baseline, target):
    validate_manifest(baseline)
    validate_manifest(target)
    suggestions = []
    baseline_features = [item for item in baseline["features"] if item["status"] in ACTIVE_STATUSES]
    target_features = [item for item in target["features"] if item["status"] in ACTIVE_STATUSES]
    for baseline_feature in baseline_features:
        baseline_name = _normalize_label(baseline_feature["name"])
        baseline_aliases = {
            _normalize_label(alias): alias
            for alias in baseline_feature["aliases"]
            if _normalize_label(alias)
        }
        for target_feature in target_features:
            if baseline_feature["id"] == target_feature["id"]:
                continue
            target_name = _normalize_label(target_feature["name"])
            target_aliases = {
                _normalize_label(alias): alias
                for alias in target_feature["aliases"]
                if _normalize_label(alias)
            }
            target_labels = ({target_name: target_feature["name"]} if target_name else {})
            target_labels.update(target_aliases)
            baseline_labels = ({baseline_name} if baseline_name else set()) | set(baseline_aliases)
            shared = sorted(baseline_labels & set(target_labels))
            suggestion = {
                "baselineFeatureId": baseline_feature["id"],
                "targetFeatureId": target_feature["id"],
                "sharedLabels": [],
                "sharedContractTerms": [],
                "similarityScore": None,
            }
            if shared:
                suggestion["matchBasis"] = "shared-name" if baseline_name == target_name else "shared-alias"
                suggestion["sharedLabels"] = sorted({
                    min(baseline_feature["name"] if label == baseline_name else baseline_aliases[label],
                        target_labels[label])
                    for label in shared
                }, key=str.casefold)
                suggestions.append(suggestion)
                continue

            baseline_dimensions = _contract_terms(baseline_feature)
            target_dimensions = _contract_terms(target_feature)
            shared_terms = set().union(*(
                baseline_dimensions[dimension] & target_dimensions[dimension]
                for dimension in CONTRACT_DIMENSIONS
            ))
            shared_dimensions = sum(
                bool(baseline_dimensions[dimension] & target_dimensions[dimension])
                for dimension in CONTRACT_DIMENSIONS
            )
            baseline_terms = set().union(*baseline_dimensions.values())
            target_terms = set().union(*target_dimensions.values())
            union = baseline_terms | target_terms
            score = len(shared_terms) / len(union) if union else 0
            if len(shared_terms) >= 2 and shared_dimensions >= 2 and score >= 0.12:
                suggestion.update({
                    "matchBasis": "shared-contract-terms",
                    "sharedContractTerms": sorted(shared_terms),
                    "similarityScore": round(score, 3),
                })
                suggestions.append(suggestion)
    suggestions.sort(key=lambda item: (item["baselineFeatureId"], item["targetFeatureId"]))
    artifact = {
        "schemaVersion": "1.1",
        "baselineDigest": digest(baseline),
        "targetDigest": digest(target),
        "suggestions": suggestions,
    }
    validate_schema(artifact, "feature-identity-suggestions-schema.json")
    return artifact


def reconcile_identity_aliases(baseline, target, artifact):
    validate_manifest(baseline)
    validate_manifest(target)
    validate_identity_mappings(baseline, target, artifact)
    if not artifact["mappings"]:
        raise ArtifactError("At least one approved mapping is required for identity reconciliation")
    if any(mapping["decision"] != "same-capability" for mapping in artifact["mappings"]):
        raise ArtifactError("Identity reconciliation supports only same-capability mappings")

    baseline_features = {item["id"]: item for item in baseline["features"]}
    result = copy.deepcopy(target)
    target_features = {item["id"]: item for item in result["features"]}
    changes = []
    for mapping in artifact["mappings"]:
        historical_labels = []
        historical_keys = set()
        for baseline_id in mapping["baselineFeatureIds"]:
            baseline_feature = baseline_features[baseline_id]
            for label in [baseline_feature["name"], *baseline_feature["aliases"]]:
                normalized = _normalize_label(label)
                if normalized and normalized not in historical_keys:
                    historical_labels.append(label)
                    historical_keys.add(normalized)
        target_changes = []
        for target_id in mapping["targetFeatureIds"]:
            target_feature = target_features[target_id]
            known_labels = {
                _normalize_label(label)
                for label in [target_feature["name"], *target_feature["aliases"]]
                if _normalize_label(label)
            }
            additions = []
            for label in historical_labels:
                normalized = _normalize_label(label)
                if normalized not in known_labels:
                    additions.append(label)
                    known_labels.add(normalized)
            target_feature["aliases"].extend(additions)
            target_changes.append({"targetFeatureId": target_id, "addedAliases": additions})
        changes.append({
            "baselineFeatureIds": mapping["baselineFeatureIds"],
            "targetChanges": target_changes,
            "approvedReference": mapping["approvedReference"],
        })

    validate_manifest(result)
    log = {
        "schemaVersion": "1.0",
        "engineVersion": __version__,
        "baselineDigest": digest(baseline),
        "targetDigest": digest(target),
        "mappingDigest": digest(artifact),
        "outputManifestDigest": digest(result),
        "changes": changes,
        "statistics": {
            "reconciledMappings": len(changes),
            "addedAliases": sum(
                len(target_change["addedAliases"])
                for change in changes
                for target_change in change["targetChanges"]
            ),
        },
        "evidenceVerificationChanged": False,
        "confidenceChanged": False,
        "applicationCodeExecuted": False,
    }
    validate_schema(log, "feature-identity-reconciliation-log-schema.json")
    return {
        "feature-manifest.json": result,
        "review-queue.json": result["reviewQueue"],
        "identity-reconciliation-log.json": log,
    }


def validate_identity_mappings(baseline, target, artifact):
    validate_schema(artifact, "feature-identity-mappings-schema.json")
    if artifact["baselineDigest"] != digest(baseline) or artifact["targetDigest"] != digest(target):
        raise ArtifactError("Identity mappings are stale for these manifests")

    baseline_features = {item["id"]: item for item in baseline["features"]
                         if item["status"] in ACTIVE_STATUSES}
    target_features = {item["id"]: item for item in target["features"]
                       if item["status"] in ACTIVE_STATUSES}
    mapped_baseline = set()
    mapped_target = set()
    decisions = {}
    for mapping in artifact["mappings"]:
        baseline_ids = mapping["baselineFeatureIds"]
        target_ids = mapping["targetFeatureIds"]
        if not set(baseline_ids).issubset(baseline_features) or not set(target_ids).issubset(target_features):
            raise ArtifactError("Identity mapping references an unknown or inactive feature")
        baseline_exact_collisions = set(baseline_ids) & set(target_features)
        target_exact_collisions = set(target_ids) & set(baseline_features)
        if (
            not baseline_exact_collisions.issubset(target_ids)
            or not target_exact_collisions.issubset(baseline_ids)
            or mapping["mappingType"] == "one-to-one" and set(baseline_ids) & set(target_ids)
        ):
            raise ArtifactError("Identity mapping conflicts with exact-ID matching")
        if mapped_baseline & set(baseline_ids) or mapped_target & set(target_ids):
            raise ArtifactError("Identity mapping groups must not overlap")
        mapped_baseline.update(baseline_ids)
        mapped_target.update(target_ids)
        group = {
            "mappingType": mapping["mappingType"],
            "baselineFeatureIds": baseline_ids,
            "targetFeatureIds": target_ids,
            "decision": mapping["decision"],
            "differences": mapping["differences"],
        }
        for baseline_id in baseline_ids:
            decisions[baseline_id] = group
    return decisions