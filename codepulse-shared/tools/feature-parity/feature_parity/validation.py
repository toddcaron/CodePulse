"""Offline schema validation and evidence reference integrity."""

import json
from pathlib import Path, PurePosixPath, PureWindowsPath

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from .identity import contract_digest
from .confidence import confidence_level


SCHEMA_ROOT = Path(__file__).resolve().parents[3] / "schemas"


class ArtifactError(ValueError):
    """An artifact violates its schema or semantic contract."""


def load_json(path):
    try:
        return parse_json(Path(path).read_text(encoding="utf-8-sig"))
    except UnicodeError as error:
        raise ArtifactError("Invalid UTF-8 JSON document") from error


def parse_json(text):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ArtifactError("Duplicate JSON property")
            result[key] = value
        return result

    def reject_constant(value):
        raise ArtifactError("Non-finite JSON number")

    try:
        return json.loads(
            text,
            object_pairs_hook=unique_keys,
            parse_constant=reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ArtifactError("Invalid UTF-8 JSON document") from error


def validate_schema(document, schema_name="feature-manifest-schema.json"):
    resources = []
    schemas = {}
    for path in sorted(SCHEMA_ROOT.glob("feature-*-schema.json")):
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)
        schemas[path.name] = schema
        resources.append((schema["$id"], Resource.from_contents(schema)))
    validator = Draft202012Validator(
        schemas[schema_name], registry=Registry().with_resources(resources)
    )
    errors = sorted(validator.iter_errors(document), key=lambda error: str(list(error.path)))
    if errors:
        error = errors[0]
        location = "/".join(str(part) for part in error.absolute_path) or "root"
        raise ArtifactError(f"Schema violation at {location}: {error.validator}")


def _unique_records(records, label):
    identifiers = [record["id"] for record in records]
    if len(identifiers) != len(set(identifiers)):
        raise ArtifactError(f"Duplicate {label} ID")
    return set(identifiers)


def _check_refs(references, identifiers):
    if not set(references).issubset(identifiers):
        raise ArtifactError("Dangling evidence reference")


def validate_evidence_records(records):
    validate_schema(records, "feature-evidence-index-schema.json")
    evidence_ids = _unique_records(records, "evidence")
    for evidence in records:
        location = evidence["location"]
        posix = PurePosixPath(location)
        windows = PureWindowsPath(location)
        if (
            posix.is_absolute() or windows.drive or windows.root
            or ".." in posix.parts or "\\" in location or ":" in location
        ):
            raise ArtifactError("Evidence location must be a source-relative POSIX path")
        if evidence["lineEnd"] < evidence["lineStart"]:
            raise ArtifactError("Reversed evidence line range")
    return evidence_ids


def validate_manifest(document):
    validate_schema(document)
    evidence_ids = validate_evidence_records(document["evidence"])
    feature_ids = _unique_records(document["features"], "feature")
    for feature in document["features"]:
        if feature["confidence"]["level"] != confidence_level(feature["confidence"]["score"]):
            raise ArtifactError("Confidence level disagrees with score")
        _check_refs(feature["evidenceRefs"], evidence_ids)
        _unique_records(feature["behaviors"], "behavior")
        for behavior in feature["behaviors"]:
            _check_refs(behavior["evidenceRefs"], set(feature["evidenceRefs"]))
        if feature["status"] != "confirmed" and not feature["requiresHumanValidation"]:
            raise ArtifactError("Unconfirmed feature must require human validation")
        if feature["status"] == "confirmed":
            if feature["review"]["contractDigest"] != contract_digest(feature, document["evidence"]):
                raise ArtifactError("Stale feature approval")
            if feature["requiresHumanValidation"]:
                raise ArtifactError("Confirmed feature cannot require human validation")
    for item in document["reviewQueue"]:
        if item["featureId"] not in feature_ids:
            raise ArtifactError("Dangling review feature reference")
        _check_refs(item["evidenceRefs"], evidence_ids)
    return document