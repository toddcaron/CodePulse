import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from . import __version__
from .comparison import compare_manifests, gate_failed
from .config import ConfigurationError, resolve_policy
from .enrichment import enrichment_progress, enrichment_template, import_enrichment
from .identity import digest
from .identity_mappings import identity_mappings_template, identity_suggestions, reconcile_identity_aliases
from .finder import find_repository
from .source_context import prepare_enrichment
from .inventory import InventoryPolicyError, source_root
from .reviews import reconcile_manifest, review_template
from .reports import report_artifacts, report_kind
from .requirements import ingest_requirements, load_requirements_source, validate_requirements_baseline
from .requirements_coverage import compare_requirements, coverage_gate_failed, requirements_review_template
from .validation import ArtifactError, parse_json, validate_business_meaning, validate_manifest, validate_schema


class InvocationError(ValueError):
    pass


class PolicyError(ValueError):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise InvocationError("Invalid arguments; use parity --help for supported commands")


def parser():
    root = Parser(prog="codepulse", description="Static reviewed-contract comparison; no source code execution")
    groups = root.add_subparsers(dest="group", required=True)
    parity = groups.add_parser("parity")
    commands = parity.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="Validate a feature manifest or requirements baseline offline")
    validation_input = validate.add_mutually_exclusive_group(required=True)
    validation_input.add_argument("--manifest")
    validation_input.add_argument("--requirements-baseline")
    validate.add_argument("--require-business-meaning", action="store_true",
                          help="Require business-ready discovery analysis before delivery")
    requirements = commands.add_parser("ingest-requirements", help="Import JSON or explicitly marked text/Markdown requirement proposals")
    requirements.add_argument("--source", required=True)
    requirements.add_argument("--output", required=True)
    requirements.add_argument("--application-name", help="Application label for text/Markdown inputs; JSON uses its declared name")
    requirements.add_argument("--dry-run", action="store_true")
    requirements_template = commands.add_parser("requirements-review-template", help="Export unapproved requirements contract and criterion mappings")
    requirements_template.add_argument("--baseline", required=True)
    requirements_template.add_argument("--output", required=True)
    requirements_template.add_argument("--dry-run", action="store_true")
    coverage = commands.add_parser("cover-requirements", help="Compare reviewed requirement contracts with a supported target manifest")
    coverage.add_argument("--baseline", required=True)
    coverage.add_argument("--reviews", required=True)
    coverage.add_argument("--target", required=True)
    coverage.add_argument("--output", required=True)
    coverage.add_argument("--fail-on", choices=("never", "partial", "unverified"), default="never")
    coverage.add_argument("--dry-run", action="store_true")
    template = commands.add_parser("review-template", help="Export unapproved review placeholders with current digests")
    template.add_argument("--manifest", required=True)
    template.add_argument("--output", required=True)
    template.add_argument("--dry-run", action="store_true")
    reconcile = commands.add_parser("reconcile", help="Apply explicit human reviews to a new manifest")
    reconcile.add_argument("--manifest", required=True)
    reconcile.add_argument("--reviews", required=True)
    reconcile.add_argument("--output", required=True)
    reconcile.add_argument("--dry-run", action="store_true")
    enrichment_export = commands.add_parser("enrichment-template", help="Export evidence-bound unapproved agent proposal placeholders")
    enrichment_export.add_argument("--manifest", required=True)
    enrichment_export.add_argument("--output", required=True)
    enrichment_export.add_argument("--dry-run", action="store_true")
    progress = commands.add_parser("enrichment-status", help="Show business readiness and the next pending batch; unfinished work is not a command failure")
    progress.add_argument("--manifest", required=True)
    progress.add_argument("--limit", type=int, default=20, help="Maximum next batch size, 1-100")
    prepare = commands.add_parser("prepare-enrichment", help="Prepare hash-checked source context and model proposal placeholders")
    prepare.add_argument("--manifest", required=True)
    prepare.add_argument("--inventory", required=True)
    prepare.add_argument("--source", required=True)
    prepare.add_argument("--context-file", action="append", default=[], help="Additional eligible source-relative POSIX path")
    prepare.add_argument("--output", required=True)
    prepare.add_argument("--dry-run", action="store_true")
    prepare.add_argument("--pending", action="store_true", help="Select the next business-incomplete candidates, skipping already ready and explicitly unresolved features")
    for selection in (enrichment_export, prepare):
        selection.add_argument("--feature-id", action="append", help="Repeat for each active feature in the batch")
        selection.add_argument("--offset", type=int, default=0, help="Offset in active features sorted by ID")
        selection.add_argument("--limit", type=int, help="Explicit batch size, 1-100")
    enrichment_import = commands.add_parser("import-enrichment", help="Import agent proposals into a new needs-review manifest")
    enrichment_import.add_argument("--manifest", required=True)
    enrichment_import.add_argument("--enrichment", required=True)
    enrichment_import.add_argument("--output", required=True)
    enrichment_import.add_argument("--dry-run", action="store_true")
    find = commands.add_parser("find", help="Discover provisional OpenAPI, C#, Vue/AngularJS and ColdFusion declarations")
    find.add_argument("--source", required=True)
    find.add_argument("--output", required=True)
    find.add_argument("--application-name")
    find.add_argument("--config")
    find.add_argument("--scope", help="Comma-separated scopes; default from configuration or all")
    find.add_argument("--include", action="append", help="Repeat for each source-relative glob")
    find.add_argument("--exclude", action="append", help="Repeat for each source-relative glob")
    find.add_argument("--confidence-threshold", choices=("low", "medium", "high"))
    find.add_argument("--dry-run", action="store_true")
    compare = commands.add_parser("compare", help="Compare two feature manifests; repository discovery is not yet available")
    compare.add_argument("--source", required=True)
    compare.add_argument("--target", required=True)
    compare.add_argument("--output", required=True)
    compare.add_argument("--mappings", help="Approved digest-bound one-to-one, split or merge identity mappings")
    compare.add_argument("--fail-on", choices=("never", "partial", "unverified"), default="never")
    compare.add_argument("--dry-run", action="store_true")
    mapping_template = commands.add_parser("identity-mappings-template", help="Export a digest-bound template for reviewed identity mappings")
    mapping_template.add_argument("--source", required=True)
    mapping_template.add_argument("--target", required=True)
    mapping_template.add_argument("--output", required=True)
    mapping_template.add_argument("--dry-run", action="store_true")
    report = commands.add_parser("report", help="Render safe HTML or Markdown reports from engine JSON artifacts")
    report.add_argument("--artifact", required=True, help="Feature manifest, parity results or requirements coverage JSON")
    report.add_argument("--output", required=True)
    report.add_argument("--source", help="Baseline manifest required by a comparison result")
    report.add_argument("--target", help="Target manifest required by comparison and coverage results")
    report.add_argument("--baseline", help="Requirements baseline required by a coverage result")
    report.add_argument("--format", choices=("html", "markdown", "both"), default="html")
    report.add_argument("--inventory-only", action="store_true",
                        help="Explicitly render a technical discovery inventory without business readiness")
    report.add_argument("--dry-run", action="store_true")
    identity_reconcile = commands.add_parser("reconcile-identities", help="Carry approved prior names and aliases into a new manifest")
    identity_reconcile.add_argument("--source", required=True)
    identity_reconcile.add_argument("--target", required=True)
    identity_reconcile.add_argument("--mappings", required=True)
    identity_reconcile.add_argument("--output", required=True)
    identity_reconcile.add_argument("--dry-run", action="store_true")
    return root


def _json_input(path):
    resolved = Path(path).resolve(strict=True)
    if not resolved.is_file():
        raise InvocationError("An artifact input must be a local JSON file")
    with resolved.open("rb") as handle:
        content = handle.read(16 * 1024 * 1024 + 1)
    if len(content) > 16 * 1024 * 1024:
        raise PolicyError("Artifact exceeds the 16 MiB input limit")
    try:
        document = parse_json(content.decode("utf-8-sig"))
    except UnicodeError as error:
        raise ArtifactError("Invalid UTF-8 JSON document") from error
    return resolved, document


def _input(path):
    resolved, document = _json_input(path)
    validate_manifest(document)
    return resolved, document


def _progress_summary(progress):
    return {key: value for key, value in progress.items() if key not in {"pending", "blocked"}}


def _output(path, inputs):
    output = Path(path).resolve()
    if output.exists():
        raise PolicyError("Output already exists; choose a fresh directory")
    if any(output == source or output in source.parents for source in inputs):
        raise PolicyError("Output overlaps an input")
    return output


def _write_results(output, result):
    artifacts = {
        "parity-results.json": result,
        "review-queue.json": [record for record in result["matches"] if record["requiresHumanValidation"]],
        "comparison-log.json": {
            "engineVersion": __version__, "completedStages": ["validation", "contract-comparison"],
            "resultDigest": digest(result), "applicationCodeExecuted": False,
        },
    }
    _write_artifacts(output, artifacts)


def _write_artifacts(output, artifacts):
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".codepulse-parity-", dir=output.parent))
    try:
        for name, document in artifacts.items():
            content = document if isinstance(document, str) else json.dumps(document, indent=2, ensure_ascii=True) + "\n"
            (staging / name).write_text(content, encoding="utf-8")
        output.mkdir()
        for artifact in staging.iterdir():
            os.rename(artifact, output / artifact.name)
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main(argv=None):
    try:
        arguments = parser().parse_args(argv)
        if arguments.command == "validate":
            if arguments.requirements_baseline:
                if arguments.require_business_meaning:
                    raise InvocationError("--require-business-meaning requires --manifest")
                _, baseline = _json_input(arguments.requirements_baseline)
                validate_requirements_baseline(baseline)
                print("Requirements baseline is valid (schema, digests and reference integrity)")
            else:
                _, document = _input(arguments.manifest)
                if arguments.require_business_meaning:
                    validate_business_meaning(document)
                print("Feature manifest has business meaning (provisional; human review required)"
                      if arguments.require_business_meaning else "Feature manifest is valid (schema and reference integrity)")
            return 0
        if arguments.command in {"requirements-review-template", "cover-requirements"}:
            baseline_path, baseline = _json_input(arguments.baseline)
            inputs = [baseline_path]
            if arguments.command == "requirements-review-template":
                artifacts = {"requirements-reviews.json": requirements_review_template(baseline)}
            else:
                reviews_path, reviews = _json_input(arguments.reviews)
                target_path, target = _input(arguments.target)
                inputs.extend([reviews_path, target_path])
                result = compare_requirements(baseline, reviews, target)
                log = {"schemaVersion": "1.0", "engineVersion": __version__,
                       "resultDigest": digest(result), "applicationCodeExecuted": False}
                validate_schema(log, "feature-requirements-comparison-log-schema.json")
                artifacts = {"requirements-coverage.json": result,
                             "review-queue.json": [item for item in result["matches"] if item["requiresHumanValidation"]],
                             "requirements-comparison-log.json": log}
            output = _output(arguments.output, inputs)
            if arguments.dry_run:
                print("Requirements operation validated; no artifacts written")
                return 0
            _write_artifacts(output, artifacts)
            if arguments.command == "requirements-review-template":
                print("Unapproved requirements template exported; human contract and criterion review required")
                return 0
            print(json.dumps(result["statistics"], sort_keys=True))
            return 6 if coverage_gate_failed(result, arguments.fail_on) else 0
        if arguments.command == "ingest-requirements":
            if Path(arguments.source).suffix.casefold() not in {".json", ".md", ".txt"}:
                raise InvocationError("Only JSON, text and Markdown requirements are supported; convert other formats explicitly")
            if Path(arguments.source).suffix.casefold() == ".json" and arguments.application_name is not None:
                raise InvocationError("Structured JSON declares its application name; --application-name is for prose inputs")
            source, document, content_hash, line_count, source_map = load_requirements_source(arguments.source, arguments.application_name)
            output = _output(arguments.output, [source])
            artifacts = ingest_requirements(document, source.name, content_hash, line_count, source_map)
            if arguments.dry_run:
                print("Requirements validated; no artifacts written")
                return 0
            _write_artifacts(output, artifacts)
            print(json.dumps(artifacts["requirements-log.json"]["statistics"], sort_keys=True))
            return 0
        if arguments.command == "enrichment-status":
            _, manifest = _input(arguments.manifest)
            print(json.dumps(_progress_summary(enrichment_progress(manifest, arguments.limit)), sort_keys=True))
            return 0
        if arguments.command in {"enrichment-template", "prepare-enrichment", "import-enrichment"}:
            manifest_path, manifest = _input(arguments.manifest)
            inputs = [manifest_path]
            if arguments.command == "import-enrichment":
                enrichment_path, enrichment = _json_input(arguments.enrichment)
                inputs.append(enrichment_path)
                artifacts = import_enrichment(manifest, enrichment)
            elif arguments.command == "prepare-enrichment":
                inventory_path, inventory = _json_input(arguments.inventory)
                source = source_root(arguments.source)
                inputs.extend([inventory_path, source])
                output_path = Path(arguments.output).resolve()
                if output_path.is_relative_to(source):
                    raise PolicyError("Enrichment output must be outside the assessed source")
                artifacts = prepare_enrichment(
                    manifest, inventory, source, arguments.feature_id, arguments.offset, arguments.limit,
                    arguments.context_file, pending=arguments.pending,
                )
            else:
                artifacts = {"enrichment-proposals.json": enrichment_template(
                    manifest, arguments.feature_id, arguments.offset, arguments.limit,
                )}
            output = _output(arguments.output, inputs)
            if arguments.dry_run:
                print("Enrichment operation validated; no artifacts written")
                return 0
            _write_artifacts(output, artifacts)
            if arguments.command == "import-enrichment":
                print(json.dumps({
                    **artifacts["enrichment-log.json"]["statistics"],
                    "businessAnalysis": _progress_summary(artifacts["enrichment-progress.json"]),
                }, sort_keys=True))
            elif arguments.command == "prepare-enrichment":
                print(json.dumps(_progress_summary(artifacts["enrichment-progress.json"]), sort_keys=True))
            else:
                print("Unapproved enrichment placeholders exported; complete provenance, rationale and proposed updates")
            return 0
        if arguments.command == "report":
            artifact_path, artifact = _json_input(arguments.artifact)
            kind = report_kind(artifact)
            if arguments.inventory_only and kind != "discovery":
                raise InvocationError("--inventory-only is accepted only for discovery reports")
            required = {"discovery": (), "comparison": ("source", "target"),
                        "requirements-coverage": ("baseline", "target")}[kind]
            supporting = {}
            inputs = [artifact_path]
            for option in ("source", "target", "baseline"):
                supplied = getattr(arguments, option)
                if supplied is None:
                    if option in required:
                        raise InvocationError(
                            f"A {kind} report requires --{' and --'.join(required)}"
                        )
                    continue
                if option not in required:
                    raise InvocationError(f"--{option} is not accepted for a {kind} report")
                path, document = _json_input(supplied)
                supporting[option] = document
                inputs.append(path)
            formats = ("html", "markdown") if arguments.format == "both" else (arguments.format,)
            output = _output(arguments.output, inputs)
            artifacts = report_artifacts(artifact, formats=formats, inventory_only=arguments.inventory_only, **supporting)
            if arguments.dry_run:
                print("Report inputs and output policy are valid; no artifacts written")
                return 0
            _write_artifacts(output, artifacts)
            print(json.dumps({"reportType": kind, "artifacts": sorted(artifacts)}, sort_keys=True))
            return 0
        if arguments.command == "identity-mappings-template":
            source_path, source = _input(arguments.source)
            target_path, target = _input(arguments.target)
            if source_path == target_path or os.path.samefile(source_path, target_path):
                raise InvocationError("Source and target must be different manifests")
            output = _output(arguments.output, [source_path, target_path])
            artifact = identity_mappings_template(source, target)
            suggestions = identity_suggestions(source, target)
            if arguments.dry_run:
                print("Identity-mapping template validated; no artifacts written")
                return 0
            _write_artifacts(output, {
                "identity-mappings.json": artifact,
                "identity-suggestions.json": suggestions,
            })
            print("Unapproved identity template and advisory suggestions exported; mappings require explicit human approval")
            return 0
        if arguments.command == "reconcile-identities":
            source_path, source = _input(arguments.source)
            target_path, target = _input(arguments.target)
            mappings_path, mappings = _json_input(arguments.mappings)
            if source_path == target_path or os.path.samefile(source_path, target_path):
                raise InvocationError("Source and target must be different manifests")
            output = _output(arguments.output, [source_path, target_path, mappings_path])
            artifacts = reconcile_identity_aliases(source, target, mappings)
            if arguments.dry_run:
                print("Identity reconciliation validated; no artifacts written")
                return 0
            _write_artifacts(output, artifacts)
            print(json.dumps(artifacts["identity-reconciliation-log.json"]["statistics"], sort_keys=True))
            return 0
        if arguments.command in {"review-template", "reconcile"}:
            manifest_path, manifest = _input(arguments.manifest)
            inputs = [manifest_path]
            if arguments.command == "reconcile":
                review_path, reviews = _json_input(arguments.reviews)
                inputs.append(review_path)
                artifacts = reconcile_manifest(manifest, reviews)
            else:
                template = review_template(manifest)
                if not template["decisions"]:
                    raise InvocationError("No active features are available for a review template")
                artifacts = {"review-decisions.json": template}
            output = _output(arguments.output, inputs)
            if arguments.dry_run:
                print("Review operation validated; no artifacts written")
                return 0
            _write_artifacts(output, artifacts)
            if arguments.command == "reconcile":
                print(json.dumps(artifacts["reconciliation-log.json"]["statistics"], sort_keys=True))
            else:
                print("Unapproved template exported; approval references require human completion")
            return 0
        if arguments.command == "find":
            root = source_root(arguments.source)
            inputs = (root, Path(arguments.config).resolve()) if arguments.config else (root,)
            output = _output(arguments.output, inputs)
            if output.is_relative_to(root):
                raise PolicyError("Finder output must be outside the scanned source directory")
            policy = resolve_policy(root, arguments.config, {
                "applicationName": arguments.application_name,
                "scopes": [item.strip() for item in arguments.scope.split(",")] if arguments.scope is not None else None,
                "include": arguments.include, "exclude": arguments.exclude,
                "minimumConfidence": arguments.confidence_threshold,
            })
            if arguments.dry_run:
                print("Finder source and output policy are valid; no scan or writes performed")
                print(json.dumps(policy, sort_keys=True))
                return 0
            artifacts = find_repository(root, policy=policy)
            _write_artifacts(output, artifacts)
            print(json.dumps(artifacts["discovery-log.json"]["statistics"], sort_keys=True))
            return 0
        source_path, source = _input(arguments.source)
        target_path, target = _input(arguments.target)
        if source_path == target_path or os.path.samefile(source_path, target_path):
            raise InvocationError("Source and target must be different manifests")
        inputs = [source_path, target_path]
        mappings = None
        if arguments.mappings:
            mapping_path, mappings = _json_input(arguments.mappings)
            inputs.append(mapping_path)
        output = _output(arguments.output, inputs)
        result = compare_manifests(source, target, mappings)
        validate_schema(result, "feature-parity-result-schema.json")
        if arguments.dry_run:
            print("Inputs and output policy are valid; no artifacts written")
            return 0
        _write_results(output, result)
        print(json.dumps(result["statistics"], sort_keys=True))
        return 6 if gate_failed(result, arguments.fail_on) else 0
    except (InvocationError, ConfigurationError) as error:
        print(str(error), file=sys.stderr)
        return 1
    except ArtifactError as error:
        print(str(error), file=sys.stderr)
        return 3
    except (PolicyError, InventoryPolicyError) as error:
        print(str(error), file=sys.stderr)
        return 5
    except OSError:
        print("Unable to access an input or output path", file=sys.stderr)
        return 2
    except Exception:
        print("Feature parity engine failed; no successful result is claimed", file=sys.stderr)
        return 4