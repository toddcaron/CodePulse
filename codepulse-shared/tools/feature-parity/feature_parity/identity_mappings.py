"""Digest-bound human decisions for feature identity and lineage mappings."""

from .identity import digest
from .validation import ArtifactError, validate_manifest, validate_schema


ACTIVE_STATUSES = {"confirmed", "discovered", "needs-review"}


def identity_mappings_template(baseline, target):
    validate_manifest(baseline)
    validate_manifest(target)
    return {
        "schemaVersion": "1.1",
        "baselineDigest": digest(baseline),
        "targetDigest": digest(target),
        "mappings": [],
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