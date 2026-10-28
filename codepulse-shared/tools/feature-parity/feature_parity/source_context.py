"""Prepare bounded, hash-checked source evidence for offline model interpretation."""

import copy
import hashlib
from pathlib import PurePosixPath, PureWindowsPath

from .enrichment import enrichment_progress, enrichment_template, select_features
from .identity import digest
from .inventory import EXCLUDED_DIRECTORIES, is_link, is_sensitive, source_root
from .validation import ArtifactError, validate_manifest, validate_schema


MAX_CONTEXT_BYTES = 2 * 1024 * 1024
MAX_CONTEXT_FILES = 100


def prepare_enrichment(manifest, inventory, source, feature_ids=None, offset=0, limit=None, context_files=(), pending=False):
    if pending:
        if feature_ids is not None or offset:
            raise ArtifactError("Pending selection cannot be combined with feature IDs or a nonzero offset")
        progress = enrichment_progress(manifest, 20 if limit is None else limit)
        feature_ids = progress["nextFeatureIds"]
        if not feature_ids:
            raise ArtifactError(
                f"No pending candidates: enrichment is {progress['completionState']}. {progress['nextAction']}"
            )
        limit = None
    selected = select_features(manifest, feature_ids, offset, limit)
    validate_schema(inventory, "feature-repository-inventory-schema.json")
    if digest(inventory) != manifest["scan"]["inventoryDigest"]:
        raise ArtifactError("Source inventory is stale for this manifest")
    root = source_root(source)
    records = {record["path"]: record for record in inventory}
    if len(records) != len(inventory):
        raise ArtifactError("Duplicate inventory path")
    evidence = {item["id"]: item for item in manifest["evidence"]}
    selected_ids = {item["id"] for item in selected}
    locations = {evidence[ref]["location"] for item in selected for ref in item["evidenceRefs"]}
    locations.update(context_files)
    if len(locations) > MAX_CONTEXT_FILES:
        raise ArtifactError("Source context exceeds 100 files; select a smaller batch")
    result = copy.deepcopy(manifest)
    result_evidence = {item["id"]: item for item in result["evidence"]}
    files = []
    total_bytes = 0
    for location in sorted(locations):
        relative = PurePosixPath(location)
        windows = PureWindowsPath(location)
        if (relative.is_absolute() or windows.drive or windows.root or ".." in relative.parts
                or "\\" in location or ":" in location):
            raise ArtifactError("Context files must be source-relative POSIX paths")
        record = records.get(location)
        if record is None or record["exclusionReason"] is not None:
            raise ArtifactError("Context file is absent from the eligible scan inventory")
        path = root.joinpath(*relative.parts)
        if (is_sensitive(path) or any(part.casefold() in EXCLUDED_DIRECTORIES for part in relative.parts)
                or path.name.casefold().endswith((".g.cs", ".g.i.cs", ".designer.cs", ".generated.cs"))):
            raise ArtifactError("Context file violates source exclusion policy")
        current = root
        for part in relative.parts:
            current = current / part
            if is_link(current):
                raise ArtifactError("Linked source context paths are not permitted")
        if not path.resolve(strict=True).is_relative_to(root) or not path.is_file():
            raise ArtifactError("Context file must remain inside the source root")
        with path.open("rb") as handle:
            content = handle.read(MAX_CONTEXT_BYTES + 1)
        total_bytes += len(content)
        if total_bytes > MAX_CONTEXT_BYTES:
            raise ArtifactError("Source context exceeds 2 MiB; select a smaller batch")
        if hashlib.sha256(content).hexdigest() != record["contentHash"]:
            raise ArtifactError("Source context changed since discovery; rerun Finder")
        if any(item["contentHash"] != record["contentHash"]
               for item in evidence.values() if item["location"] == location):
            raise ArtifactError("Source evidence hash disagrees with inventory")
        try:
            text = content.decode("utf-8-sig")
        except UnicodeError as error:
            raise ArtifactError("Source context must be UTF-8") from error
        if "\x00" in text:
            raise ArtifactError("Binary source context is not permitted")
        context = {
            "id": "context-" + digest({"path": location, "contentHash": record["contentHash"]})[:24],
            "type": "source-context", "location": location, "lineStart": 1,
            "lineEnd": max(1, len(text.splitlines())),
            "summary": "Hash-checked source context; business interpretation and runtime behavior unverified",
            "contentHash": record["contentHash"], "verification": "partially-verified",
        }
        existing = result_evidence.get(context["id"])
        if existing is not None and existing != context:
            raise ArtifactError("Conflicting source context evidence")
        result_evidence[context["id"]] = context
        files.append({"evidenceId": context["id"], "location": location, "text": text})
    for feature in result["features"]:
        if feature["id"] not in selected_ids:
            continue
        feature_locations = {evidence[ref]["location"] for ref in feature["evidenceRefs"]} | set(context_files)
        context_refs = [item["evidenceId"] for item in files if item["location"] in feature_locations]
        feature["evidenceRefs"] = sorted(set(feature["evidenceRefs"]) | set(context_refs))
        feature.pop("review", None)
        feature["status"] = "needs-review"
        feature["requiresHumanValidation"] = True
        reason = "Source context prepared; model interpretation and independent human review required"
        if not any(item["featureId"] == feature["id"] and item["reason"] == reason for item in result["reviewQueue"]):
            result["reviewQueue"].append({
                "featureId": feature["id"], "reason": reason, "evidenceRefs": feature["evidenceRefs"],
            })
    result["evidence"] = sorted(result_evidence.values(), key=lambda item: item["id"])
    result["reviewQueue"].sort(key=lambda item: (item["featureId"], item["reason"]))
    validate_manifest(result)
    template = enrichment_template(result, sorted(selected_ids))
    for proposal in template["proposals"]:
        refs = [citation["id"] for citation in proposal["evidence"]]
        proposal["updates"] = {
            "name": "", "domain": "", "behaviors": [],
            "semanticAnalysis": {
                "status": "unresolved", "summary": "",
                "businessMeaning": {"purpose": "", "userGoal": "", "trigger": "", "outcome": "", "basis": "inferred"},
                "evidenceRefs": refs, "businessRules": [], "unresolvedQuestions": [],
            },
        }
    return {
        "feature-manifest.json": result,
        "evidence-index.json": result["evidence"], "review-queue.json": result["reviewQueue"],
        "source-context.json": {
            "baseManifestDigest": digest(result), "inventoryDigest": digest(inventory),
            "featureIds": sorted(selected_ids), "sourceBytes": total_bytes, "files": files,
        },
        "enrichment-proposals.json": template,
        "enrichment-progress.json": enrichment_progress(result),
    }
