"""Import declared requirements without inventing obligations or approvals."""

import copy
import hashlib
from pathlib import Path

from . import __version__
from .confidence import declaration_confidence
from .identity import digest
from .inventory import InventoryPolicyError, is_link, is_sensitive
from .prose_requirements import extract_prose_requirements
from .validation import ArtifactError, parse_json, validate_evidence_records, validate_manifest, validate_schema


def load_requirements_source(path, application_name=None):
    source = Path(path).absolute()
    if source.suffix.casefold() not in {".json", ".md", ".txt"}:
        raise ArtifactError("Unsupported requirements source format")
    if any(is_link(item) for item in (source, *source.parents)):
        raise InventoryPolicyError("Requirements source cannot use linked paths")
    resolved = source.resolve(strict=True)
    if not resolved.is_file():
        raise InventoryPolicyError("Requirements source must be a local file")
    if is_sensitive(resolved):
        raise InventoryPolicyError("Requirements source is excluded by sensitive-file policy")
    with resolved.open("rb") as handle:
        content = handle.read(1024 * 1024 + 1)
    if len(content) > 1024 * 1024:
        raise InventoryPolicyError("Requirements source exceeds the 1 MiB limit")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeError as error:
        raise ArtifactError("Requirements source must contain UTF-8 text") from error
    if "\x00" in text:
        raise ArtifactError("Binary requirements source is unsupported")
    source_map = None
    if resolved.suffix.casefold() == ".json":
        document = parse_json(text)
    else:
        document, source_map = extract_prose_requirements(text, application_name or resolved.stem)
    return resolved, document, hashlib.sha256(content).hexdigest(), max(1, len(text.splitlines())), source_map


def validate_requirements_input(document):
    validate_schema(document, "feature-requirements-input-schema.json")
    identifiers = [item["id"] for item in document["requirements"]]
    if len(identifiers) != len(set(identifiers)):
        raise ArtifactError("Duplicate requirement ID")
    for requirement in document["requirements"]:
        behavior_ids = [item["id"] for item in requirement["behaviors"]]
        if len(behavior_ids) != len(set(behavior_ids)):
            raise ArtifactError("Duplicate requirement behavior ID")
    return document


def validate_requirements_baseline(baseline):
    validate_schema(baseline, "feature-requirements-baseline-schema.json")
    document = validate_requirements_input(baseline["document"])
    if baseline["inputDigest"] != digest(document):
        raise ArtifactError("Requirements input digest does not match preserved declarations")
    evidence_ids = validate_evidence_records(baseline["evidence"])
    expected = {item["id"]: "requirement." + digest(item["id"])[:24] for item in document["requirements"]}
    source_map = baseline.get("sourceMap")
    if source_map is not None:
        if set(source_map["ranges"]) != set(expected):
            raise ArtifactError("Prose source map does not match requirements")
        if source_map["ignoredNonemptyLines"] > source_map["lineCount"]:
            raise ArtifactError("Invalid prose ignored-line count")
        for start, end in source_map["ranges"].values():
            if end < start or end > source_map["lineCount"]:
                raise ArtifactError("Invalid prose source range")
        ordered_ranges = sorted(source_map["ranges"].values())
        if any(previous[1] >= current[0] for previous, current in zip(ordered_ranges, ordered_ranges[1:])):
            raise ArtifactError("Overlapping prose source ranges")
        for requirement in document["requirements"]:
            if (not requirement["ambiguities"] or any(requirement[key] for key in (
                    "actors", "inputs", "outputs", "preconditions", "acceptanceCriteria"))
                    or len(requirement["behaviors"]) != 1 or requirement["behaviors"][0]["mandatory"]):
                raise ArtifactError("Prose proposals cannot claim resolved contracts or mandatory obligations")
    ranges_by_evidence = {expected[identifier]: bounds for identifier, bounds in source_map["ranges"].items()} if source_map else {}
    if evidence_ids != set(expected.values()):
        raise ArtifactError("Requirements evidence IDs do not match declarations")
    for evidence in baseline["evidence"]:
        if (evidence["type"] != "requirement" or evidence["verification"] != "partially-verified"
                or evidence["contentHash"] != baseline["sourceDigest"]
                or (source_map is None and evidence["lineStart"] != 1)):
            raise ArtifactError("Requirements evidence provenance is inconsistent")
        if source_map and [evidence["lineStart"], evidence["lineEnd"]] != ranges_by_evidence[evidence["id"]]:
            raise ArtifactError("Prose evidence differs from source map")
    locations = {(item["location"], None if source_map else item["lineEnd"]) for item in baseline["evidence"]}
    if len(locations) > 1:
        raise ArtifactError("Structured requirements must reference one full-file source")
    linked = set()
    for link in baseline["featureLinks"]:
        identifier = link["requirementId"]
        if (identifier not in expected or identifier in linked or link["featureId"] != identifier
                or link["evidenceRefs"] != [expected[identifier]]):
            raise ArtifactError("Duplicate, dangling or inconsistent requirement feature link")
        linked.add(identifier)
    if linked != set(expected):
        raise ArtifactError("Requirements baseline lacks feature links")
    return baseline


def ingest_requirements(document, location, content_hash, line_count, source_map=None):
    validate_requirements_input(document)
    if source_map is not None:
        validate_schema(source_map, "feature-prose-source-map-schema.json")
        if set(source_map["ranges"]) != {item["id"] for item in document["requirements"]}:
            raise ArtifactError("Prose source map does not match requirements")
    source_evidence = {
        "id": "requirement.source", "type": "requirement", "location": location,
        "lineStart": 1, "lineEnd": line_count,
        "summary": "Declared requirement; implementation and business completeness are unverified",
        "contentHash": content_hash, "verification": "partially-verified",
    }
    validate_evidence_records([source_evidence])
    requirements = copy.deepcopy(document)
    evidence = []
    features = []
    queue = []
    links = []
    for requirement in sorted(requirements["requirements"], key=lambda item: item["id"]):
        evidence_id = "requirement." + digest(requirement["id"])[:24]
        bounds = source_map["ranges"][requirement["id"]] if source_map else [1, line_count]
        evidence.append(dict(source_evidence, id=evidence_id, lineStart=bounds[0], lineEnd=bounds[1]))
        feature = {key: copy.deepcopy(requirement[key]) for key in (
            "id", "name", "domain", "capabilityType", "actors", "inputs", "outputs", "preconditions"
        )}
        feature.update({
            "fingerprint": digest({"requirementId": requirement["id"]}),
            "status": "needs-review", "aliases": [], "admitted": False,
            "evidenceRefs": [evidence_id], "requiresHumanValidation": True,
            "confidence": declaration_confidence(),
            "behaviors": [dict(behavior, evidenceRefs=[evidence_id])
                          for behavior in sorted(requirement["behaviors"], key=lambda item: item["id"])],
        })
        features.append(feature)
        reason = "Requirement declaration requires human validation and implementation evidence"
        if requirement["ambiguities"]:
            reason = "Declared requirement ambiguity requires human resolution"
        queue.append({"featureId": feature["id"], "reason": reason, "evidenceRefs": [evidence_id]})
        links.append({"requirementId": requirement["id"], "featureId": feature["id"], "evidenceRefs": [evidence_id]})
    manifest = {
        "schemaVersion": "1.0",
        "application": {"name": document["applicationName"], "sourceType": "requirements", "revision": None},
        "scan": {"coverage": "incomplete", "inventoryDigest": content_hash, "limitations": [
            "Declared requirements are not implementation evidence or proof of business completeness",
            "Acceptance criteria and ambiguities are preserved in the baseline, not interpreted as atomic behaviors",
            "JSON evidence ranges cover the full input file; per-record offsets are not available",
        ]},
        "evidence": evidence, "features": features, "reviewQueue": queue,
    }
    validate_manifest(manifest)
    baseline = {
        "schemaVersion": "1.0", "document": requirements, "inputDigest": digest(document),
        "sourceDigest": content_hash, "evidence": copy.deepcopy(evidence), "featureLinks": links,
        "coverage": "incomplete", "requiresHumanValidation": True,
    }
    if source_map is not None:
        baseline["sourceMap"] = copy.deepcopy(source_map)
        manifest["scan"]["limitations"][-1] = "Only explicitly marked prose blocks are proposals; unmarked content is not interpreted"
        manifest["scan"]["limitations"].append("Prose mandatory flags are unresolved placeholders, not optionality decisions")
        if source_map["lineCount"] != line_count:
            raise ArtifactError("Prose source line count differs from input")
    validate_requirements_baseline(baseline)
    artifacts = {
        "requirements-baseline.json": baseline, "feature-manifest.json": manifest,
        "review-queue.json": queue,
        "requirements-log.json": {
            "schemaVersion": "1.0", "engineVersion": __version__,
            "inputDigest": digest(document), "sourceDigest": content_hash,
            "baselineDigest": digest(baseline), "manifestDigest": digest(manifest),
            "statistics": {"requirements": len(features), "ambiguousRequirements": sum(
                bool(item["ambiguities"]) for item in requirements["requirements"]
            ), "confirmedFeatures": 0, "admittedFeatures": 0, "reviewQueueItems": len(queue)},
            "applicationCodeExecuted": False,
        },
    }
    validate_schema(artifacts["requirements-log.json"], "feature-requirements-log-schema.json")
    return artifacts