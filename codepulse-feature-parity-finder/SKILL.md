---
name: codepulse-feature-parity-finder
description: Runs bounded static discovery of provisional capabilities in a local repository using the CodePulse Feature Parity engine. Use when the user asks to discover or inventory application features and capabilities for later human review.
---

# CodePulse Feature Parity Finder

## Purpose

Run the supported static Finder workflow and summarize its JSON artifacts. Discovery is provisional; it does not establish business completeness, runtime reachability, or feature absence.

## Setup

Before running the engine, read `../codepulse-shared/tools/feature-parity/README.md` for the pinned Python setup, supported syntax, output policy, and limitations. Resolve `../codepulse-shared/tools/feature-parity/cli.py` as a sibling of this installed skill and use its absolute path.

Reuse a verified isolated Python 3.11+ environment with the pinned requirements, or create an isolated environment outside the assessed repository and install only the installed engine's `requirements.lock`, following the README's Setup procedure. A missing temporary environment is not a blocker: provision one and continue. Never install into global Python or modify the assessed repository's environment. Use the isolated environment's absolute Python path for every engine command.

Package installation is allowed only for this engine setup, subject to host permissions and network policy. Do not execute source-repository code, build the application, or contact its services. If the shared engine is missing, Python 3.11+ is unavailable, or setup/verification fails or is denied, stop and report the exact blocker and recovery command; do not claim a completed run. Do not search the assessed repository for another engine copy.

## Inputs

Use a local source directory supplied or clearly identified by the user. Ask only for missing information that blocks a safe run. Optional inputs are application name, scope, include/exclude patterns, confidence threshold, output directory, and dry-run.

The default scope is the engine's configured scope, otherwise all supported scopes. Do not infer that unrecognized files or technologies were fully analyzed.

## Procedure

1. Confirm the source is a local directory and identify the requested scope and policy overrides.
2. Select a fresh output directory outside the scanned source tree. Never pre-create it. If no safe output path is apparent, ask for one. Do not write artifacts into the assessed repository.
3. If dry-run was requested, invoke only the engine's dry-run and state that no scan or artifacts were produced.
4. Run the installed engine with the supplied options:

   ```text
   python <absolute-cli-path> parity find --source <source-directory> --output <fresh-external-directory> [--application-name <name>] [--scope <comma-separated-scopes>] [--include <glob>] [--exclude <glob>] [--confidence-threshold low|medium|high]
   ```

   Repeat `--include` or `--exclude` for each pattern. Add `--dry-run` only when requested. Preserve path quoting for the user's shell.
5. On success, verify the output contains `feature-manifest.json`, `repository-inventory.json`, `evidence-index.json`, `review-queue.json`, and `discovery-log.json`. Validate the manifest by invoking `parity validate --manifest <output>/feature-manifest.json` with the same engine.
6. Read `discovery-log.json` and report its engine-produced statistics, scope/limitations, review-queue size, and exact artifact paths. Do not recompute or invent engine counts. If the command or validation fails, report failure without claiming a completed scan.
7. Tell the user that findings remain provisional and require human review. If comparison is requested, stop here until a reviewed manifest is produced through `review-template` and `reconcile`.

## Reports

Render a discovery report only when the user asks for one. The engine is the only renderer; never hand-author or restyle HTML or Markdown.

```text
python <absolute-cli-path> parity report --artifact <output>/feature-manifest.json --output <fresh-external-directory> [--format html|markdown|both]
```

A discovery report takes no supporting manifests. `feature-report.json` is always written and `feature-report.html` is the default rendering; request Markdown only when the user asks for it. Report only values present in `feature-report.json`, and follow `../codepulse-shared/renderers/feature-report-template.md`. The report restates that candidates are provisional and carries no findings, severities, or grades.

## Safety and Claims

- The engine reads bounded local source and writes only to a fresh external output directory.
- Never run application scripts/tests or claim runtime behavior, complete business scope, or confirmed absence.
- Do not treat a candidate, confidence threshold, or human confirmation as verified evidence or parity approval.
- This workflow produces JSON; HTML and Markdown come only from `parity report`. Do not hand-author a report or assign health grades.

## Completion

State whether discovery completed, the source/scope used, the engine-reported candidate and review counts, material limitations, and artifact paths. Distinguish provisional discovery from human-reviewed comparison. Avoid claiming that any capability is absent.