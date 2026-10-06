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
from .enrichment import enrichment_template, import_enrichment
from .identity import digest
from .finder import find_repository
from .inventory import InventoryPolicyError, source_root
from .reviews import reconcile_manifest, review_template
from .requirements import ingest_requirements, load_requirements_source, validate_requirements_baseline
from .requirements_coverage import compare_requirements, coverage_gate_failed, requirements_review_template
from .validation import ArtifactError, parse_json, validate_manifest, validate_schema


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
    compare.add_argument("--fail-on", choices=("never", "missing", "partial", "unverified"), default="never")
    compare.add_argument("--dry-run", action="store_true")
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
            (staging / name).write_text(json.dumps(document, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
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
                _, baseline = _json_input(arguments.requirements_baseline)
                validate_requirements_baseline(baseline)
                print("Requirements baseline is valid (schema, digests and reference integrity)")
            else:
                _input(arguments.manifest)
                print("Feature manifest is valid (schema and reference integrity)")
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
        if arguments.command in {"enrichment-template", "import-enrichment"}:
            manifest_path, manifest = _input(arguments.manifest)
            inputs = [manifest_path]
            if arguments.command == "import-enrichment":
                enrichment_path, enrichment = _json_input(arguments.enrichment)
                inputs.append(enrichment_path)
                artifacts = import_enrichment(manifest, enrichment)
            else:
                artifacts = {"enrichment-proposals.json": enrichment_template(manifest)}
            output = _output(arguments.output, inputs)
            if arguments.dry_run:
                print("Enrichment operation validated; no artifacts written")
                return 0
            _write_artifacts(output, artifacts)
            if arguments.command == "import-enrichment":
                print(json.dumps(artifacts["enrichment-log.json"]["statistics"], sort_keys=True))
            else:
                print("Unapproved enrichment placeholders exported; complete provenance, rationale and proposed updates")
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
        output = _output(arguments.output, (source_path, target_path))
        result = compare_manifests(source, target)
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