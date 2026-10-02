"""Provisional static discovery; implementation and business behavior remain unverified."""

import hashlib

from . import __version__
from .adapters.dotnet import extract_dotnet
from .adapters.frontend import extract_frontend_routes, extract_template
from .adapters.coldfusion import extract_coldfusion
from .config import resolve_policy
from .confidence import admitted, declaration_confidence, lexical_endpoint_confidence, syntax_declaration_confidence
from .identity import digest
from .inventory import inventory_repository, is_link, source_root
from .validation import ArtifactError, parse_json, validate_manifest, validate_schema


HTTP_METHODS = frozenset({"get", "put", "post", "delete", "options", "head", "patch", "trace"})
LIMITATIONS = [
    "Static OpenAPI, C#, Vue/AngularJS and ColdFusion declarations only; reachability and business behavior are unverified",
    "YAML OpenAPI, documentation and tests are inventoried but not extracted yet",
    "Template actions and router registrations may represent fragments of the same feature; no consolidation is claimed",
    "ColdFusion tag extraction does not evaluate CFScript, includes, conditionals, templates or external systems",
    "C# extraction does not resolve framework symbols, registration graphs, authorization, conditional compilation or duplicate representations",
    "No business completeness, runtime correctness or absence claim is made",
    "Sensitive configuration, dependency/generated directories and linked paths are excluded",
    "Source paths are metadata; filenames must not contain secrets or personal data",
    "Git revision is not captured yet; content hashes describe the observed files",
    "Do not scan concurrently modified or hostile filesystems; this scanner is not a sandbox",
]


def _candidate(record, method, identity, evidence_type, summary, description, start, end, confidence, policy,
               capability_type="api"):
    identifier = digest(identity)[:24]
    evidence_id = f"evidence-{identifier}"
    feature_id = f"unclassified.{capability_type}-{identifier}"
    evidence = {
        "id": evidence_id, "type": evidence_type, "location": record["path"],
        "lineStart": start, "lineEnd": end, "summary": summary,
        "contentHash": record["contentHash"], "verification": "partially-verified",
    }
    feature = {
        "id": feature_id, "name": f"{method} {'API operation' if capability_type == 'api' else 'declaration'} {identifier[:8]}",
        "domain": "Unclassified", "capabilityType": capability_type, "fingerprint": digest(identity),
        "status": "needs-review", "aliases": [], "actors": [], "inputs": [],
        "outputs": [], "preconditions": [],
        "behaviors": [{
            "id": "declared-operation", "description": description,
            "mandatory": True, "evidenceRefs": [evidence_id],
        }],
        "evidenceRefs": [evidence_id], "confidence": confidence,
        "requiresHumanValidation": True, "admitted": admitted(confidence, policy["minimumConfidence"]),
    }
    review = {
        "featureId": feature_id,
        "reason": (
            "Confirm business name, contract and reachability; static evidence is insufficient"
            if feature["admitted"] else "Below confidence threshold; retained for review, not admitted to parity"
        ),
        "evidenceRefs": [evidence_id],
    }
    return evidence, feature, review


def find_repository(source, application_name=None, policy=None):
    root = source_root(source)
    policy = policy or resolve_policy(root, overrides={"applicationName": application_name})
    records, issues = inventory_repository(
        root, max_file_bytes=policy["limits"]["maxFileBytes"],
        max_entries=policy["limits"]["maxEntries"], max_depth=policy["limits"]["maxDepth"],
        include_patterns=policy["include"], exclude_patterns=policy["exclude"],
        forbidden_patterns=policy["forbiddenPaths"],
    )
    evidence = []
    features = []
    review = []
    excluded_candidates = 0
    for record in records:
        if record["exclusionReason"] or record["fileType"] not in {".json", ".cs", ".vue", ".html", ".htm", ".js", ".ts", ".cfm", ".cfc"}:
            continue
        path = root / record["path"]
        try:
            if is_link(path) or not path.resolve(strict=True).is_relative_to(root):
                issues.append("A source path changed during discovery")
                continue
            with path.open("rb") as handle:
                content = handle.read(policy["limits"]["maxFileBytes"] + 1)
            if hashlib.sha256(content).hexdigest() != record["contentHash"]:
                issues.append("A source file changed during discovery; rerun required")
                continue
            text = content.decode("utf-8-sig")
            if record["fileType"] in {".vue", ".html", ".htm", ".js", ".ts", ".cfm", ".cfc"}:
                extension = record["fileType"]
                if extension in {".cfm", ".cfc"}:
                    record["adapter"] = "coldfusion-tags"
                    hits, adapter_issues = extract_coldfusion(text)
                elif extension in {".js", ".ts"}:
                    record["adapter"] = "frontend-routes"
                    hits, adapter_issues = extract_frontend_routes(text, typescript=extension == ".ts")
                else:
                    record["adapter"] = "vue-template" if extension == ".vue" else "angularjs-template"
                    hits, adapter_issues = extract_template(text, vue=extension == ".vue")
                issues.extend(adapter_issues)
                for hit in hits:
                    if hit["capabilityType"] not in policy["scopes"]:
                        issues.append("A syntax declaration was not extracted because its capability scope was not selected")
                        excluded_candidates += 1
                        continue
                    item, feature, queue_item = _candidate(
                        record, hit["label"], {"path": record["path"], **hit}, hit["evidenceType"],
                        f"{hit['label']} syntax observed; contract and reachability unresolved",
                        f"Declares {hit['label']} syntax", hit["line"], hit["line"],
                        syntax_declaration_confidence(), policy, capability_type=hit["capabilityType"],
                    )
                    evidence.append(item)
                    features.append(feature)
                    review.append(queue_item)
                continue
            if record["fileType"] == ".cs":
                record["adapter"] = "dotnet-lexical"
                if "api" not in policy["scopes"]:
                    issues.append("C# HTTP syntax was not extracted because API scope was not selected")
                    continue
                hits, adapter_issues = extract_dotnet(text)
                issues.extend(adapter_issues)
                for hit in hits:
                    item, feature, queue_item = _candidate(
                        record, hit["method"], {"path": record["path"], **hit}, "endpoint",
                        f"C# {hit['method']} HTTP syntax found; registration and behavior unverified",
                        f"Declares {hit['method']} HTTP syntax", hit["line"], hit["line"],
                        lexical_endpoint_confidence(), policy,
                    )
                    evidence.append(item)
                    features.append(feature)
                    review.append(queue_item)
                continue
            document = parse_json(text)
        except (ArtifactError, OSError, UnicodeError):
            issues.append("A source file could not be read or parsed for discovery")
            continue
        if not isinstance(document, dict) or not (
            isinstance(document.get("openapi"), str) and document["openapi"].startswith("3.")
            or document.get("swagger") == "2.0"
        ):
            continue
        record["adapter"] = "openapi-json"
        if "api" not in policy["scopes"]:
            issues.append("OpenAPI operations were not extracted because API scope was not selected")
            continue
        paths = document.get("paths")
        if not isinstance(paths, dict):
            issues.append("An OpenAPI paths collection was invalid")
            continue
        line_end = max(1, len(content.splitlines()))
        for route, operations in sorted(paths.items()):
            if not isinstance(route, str) or not route.startswith("/") or not isinstance(operations, dict):
                excluded_candidates += 1
                continue
            for method, operation in sorted(operations.items()):
                if method not in HTTP_METHODS:
                    continue
                if not isinstance(operation, dict) or not isinstance(operation.get("responses"), dict):
                    excluded_candidates += 1
                    issues.append("An OpenAPI operation lacked structured response evidence")
                    continue
                item, feature, queue_item = _candidate(
                    record, method.upper(), {"path": record["path"], "route": route, "method": method},
                    "documentation", f"Structured {method.upper()} operation declaration; implementation unverified",
                    f"Declares a {method.upper()} API operation", 1, line_end,
                    declaration_confidence(), policy,
                )
                evidence.append(item)
                features.append(feature)
                review.append(queue_item)
    manifest = {
        "schemaVersion": "1.0",
        "application": {"name": policy["applicationName"], "sourceType": "repository", "revision": None},
        "scan": {
            "coverage": "incomplete", "limitations": sorted(set(LIMITATIONS + issues)),
            "inventoryDigest": digest(records),
            "configurationDigest": digest(policy),
        },
        "evidence": sorted(evidence, key=lambda item: item["id"]),
        "features": sorted(features, key=lambda item: item["id"]),
        "reviewQueue": sorted(review, key=lambda item: item["featureId"]),
    }
    validate_schema(records, "feature-repository-inventory-schema.json")
    validate_manifest(manifest)
    statistics = {
        "confirmedFeatures": 0, "probableFeatures": 0, "needsReview": len(features),
        "excludedCandidates": excluded_candidates, "inventoryEntries": len(records),
        "excludedEntries": sum(record["exclusionReason"] is not None for record in records),
        "admittedFeatures": sum(feature["admitted"] for feature in features),
        "belowThreshold": sum(not feature["admitted"] for feature in features),
    }
    return {
        "feature-manifest.json": manifest,
        "evidence-index.json": manifest["evidence"],
        "repository-inventory.json": records,
        "review-queue.json": manifest["reviewQueue"],
        "discovery-log.json": {
            "engineVersion": __version__, "statistics": statistics,
            "resolvedConfiguration": policy,
            "limitations": manifest["scan"]["limitations"], "applicationCodeExecuted": False,
        },
    }