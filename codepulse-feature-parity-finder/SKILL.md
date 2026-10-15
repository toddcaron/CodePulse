---
name: codepulse-feature-parity-finder
description: Runs bounded static discovery of provisional capabilities in a local repository using the CodePulse Feature Parity engine. Use when the user asks to inventory or discover application capabilities for a later human review.
---

# CodePulse Feature Parity Finder

## Purpose

Run the supported static Finder workflow and summarize its JSON artifacts. Discovery is provisional; it does not establish business completeness, runtime reachability, or feature absence.

## Setup

Before running the engine, read `../codepulse-shared/tools/feature-parity/README.md` for the pinned Python setup, supported syntax, output policy, and limitations. Resolve `../codepulse-shared/tools/feature-parity/cli.py` as a sibling of this installed skill and use its absolute path. Use an already provisioned Python 3.11+ environment with the pinned requirements. Do not install packages, execute source-repository code, build the application, or contact its services.

If the shared engine or a working pinned Python environment is unavailable, stop and report the documented setup requirement. Do not search the assessed repository for another engine copy.

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

## Safety and Claims

- The engine reads bounded local source and writes only to a fresh external output directory.
- Never run application scripts/tests or claim runtime behavior, complete business scope, or confirmed absence.
- Do not treat a candidate, confidence threshold, or human confirmation as verified evidence or parity approval.
- This workflow produces JSON only. Do not invent HTML/Markdown reports or health grades.

## Completion

State whether discovery completed, the source/scope used, the engine-reported candidate and review counts, material limitations, and artifact paths. Distinguish provisional discovery from human-reviewed comparison. Avoid claiming that any capability is absent.