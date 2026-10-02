"""Resolve validated Finder policy without evaluating repository instructions."""

from pathlib import Path, PurePosixPath

from pathspec import PathSpec

from .inventory import InventoryPolicyError, is_link
from .validation import ArtifactError, parse_json, validate_schema


SCOPES = {"business", "ui", "api", "integrations", "reports", "jobs", "authorization", "data-operations"}
DEFAULT_POLICY = {
    "applicationName": "Application", "scopes": sorted(SCOPES),
    "include": [], "exclude": [], "forbiddenPaths": [], "minimumConfidence": "medium",
    "limits": {"maxFileBytes": 1048576, "maxEntries": 20000, "maxDepth": 64},
}


class ConfigurationError(ValueError):
    pass


def _patterns(patterns):
    for pattern in patterns:
        if (
            pattern != pattern.strip() or pattern.startswith(("/", "!", "#"))
            or "\\" in pattern or ":" in pattern or ".." in PurePosixPath(pattern).parts
            or any(ord(character) < 32 for character in pattern)
        ):
            raise ConfigurationError("Patterns must be source-relative forward-slash globs without negation or traversal")
    try:
        return PathSpec.from_lines("gitwildmatch", patterns)
    except ValueError as error:
        raise ConfigurationError("Invalid path pattern") from error


def match_patterns(location, patterns, directory=False):
    return _patterns(patterns).match_file(location + ("/" if directory else ""))


def resolve_policy(source, config_path=None, overrides=None):
    root = Path(source)
    candidate = Path(config_path) if config_path is not None else root / "codepulse.config.json"
    settings = {}
    if config_path is not None or candidate.exists() or candidate.is_symlink():
        if is_link(candidate):
            raise InventoryPolicyError("Configuration links and reparse points are not permitted")
        resolved = candidate.resolve(strict=True)
        if not resolved.is_file():
            raise ConfigurationError("Configuration must be a JSON file")
        with resolved.open("rb") as handle:
            content = handle.read(1048577)
        if len(content) > 1048576:
            raise ConfigurationError("Configuration exceeds the 1 MiB limit")
        try:
            document = parse_json(content.decode("utf-8-sig"))
            validate_schema(document, "feature-parity-config-schema.json")
        except (ArtifactError, UnicodeError) as error:
            raise ConfigurationError("Invalid Feature Parity configuration") from error
        settings = document["featureParity"]
    policy = {
        **DEFAULT_POLICY,
        "limits": {**DEFAULT_POLICY["limits"], **settings.get("limits", {})},
        "applicationName": settings.get("applicationName", "Application"),
        "scopes": settings.get("defaultScope", ["all"]),
        "include": settings.get("include", []), "exclude": settings.get("exclude", []),
        "forbiddenPaths": settings.get("forbiddenPaths", []),
        "minimumConfidence": settings.get("minimumConfidence", "medium"),
    }
    for key, value in (overrides or {}).items():
        if value is not None:
            policy[key] = value
    effective = {key: policy[key] for key in (
        "applicationName", "include", "exclude", "forbiddenPaths", "minimumConfidence", "limits"
    )}
    effective["defaultScope"] = policy["scopes"]
    try:
        validate_schema({"featureParity": effective}, "feature-parity-config-schema.json")
    except ArtifactError as error:
        raise ConfigurationError("Invalid effective Feature Parity configuration") from error
    scopes = policy["scopes"]
    if "all" in scopes:
        if len(scopes) != 1:
            raise ConfigurationError("Scope all cannot be combined with other scopes")
        scopes = sorted(SCOPES)
    if not scopes or not set(scopes).issubset(SCOPES):
        raise ConfigurationError("Unsupported discovery scope")
    policy["scopes"] = sorted(set(scopes))
    if not policy["applicationName"].strip():
        raise ConfigurationError("Application name must not be empty")
    if policy["minimumConfidence"] not in {"low", "medium", "high"}:
        raise ConfigurationError("Unsupported confidence threshold")
    for key in ("include", "exclude", "forbiddenPaths"):
        _patterns(policy[key])
    return policy