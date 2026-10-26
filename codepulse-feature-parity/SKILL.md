---
name: codepulse-feature-parity
description: Compares reviewed feature manifests or separately reviewed requirements against a supported target manifest. Use when the user asks for static feature parity, to compare reviewed feature manifests, or for reviewed requirements coverage.
---

# CodePulse Feature Parity

## Purpose

Run the supported manifest comparison or reviewed-requirements coverage workflow and summarize the engine's JSON results. This is static contract comparison, not application execution or runtime parity proof.

## Setup

Before running the engine, read `../codepulse-shared/tools/feature-parity/README.md` for pinned Python setup, command contracts, output policy, gates, and limitations. Resolve `../codepulse-shared/tools/feature-parity/cli.py` as a sibling of this installed skill and use its absolute path.

Reuse a verified isolated Python 3.11+ environment with the pinned requirements, or create an isolated environment outside the assessed repository and install only the installed engine's `requirements.lock`, following the README's Setup procedure. A missing temporary environment is not a blocker: provision one and continue. Never install into global Python or modify the assessed repository's environment. Use the isolated environment's absolute Python path for every engine command.

Package installation is allowed only for this engine setup, subject to host permissions and network policy. Do not execute application code, build repositories, or contact application services. If the shared engine is missing, Python 3.11+ is unavailable, or setup/verification fails or is denied, stop and report the exact blocker and recovery command; do not claim a completed run. Do not search an assessed repository for another engine copy.

## Supported Workflows

Choose one workflow based on the supplied inputs:

- **Feature comparison:** two feature manifest JSON files, optionally with a human-completed digest-bound identity-mapping file.
- **Requirements coverage:** a validated requirements baseline, its separately reviewed requirements contracts/criterion mappings, and a target feature manifest.
- **Repository discovery:** use `codepulse-feature-parity-finder` first. Discovery outputs are provisional; do not compare them as reviewed manifests until a human has reviewed and reconciled them.

The `compare` command accepts manifests, not repository paths. If inputs are ambiguous, ask one concise question to select the workflow.

## Feature Comparison

1. Validate both manifests with `parity validate --manifest <path>`. Ensure source and target are distinct files.
2. Select a fresh output directory that does not exist and does not overlap an input. Preserve the input manifests and mappings unchanged.
3. If renamed candidates need review and no mapping file was supplied, offer `identity-mappings-template` for these exact manifests. Its `identity-mappings.json` requires human decisions; `identity-suggestions.json` is advisory. Do not fill or approve mappings on the user's behalf. `reconcile-identities` may carry historical aliases only from already approved same-capability mappings.
4. Run:

   ```text
   python <absolute-cli-path> parity compare --source <baseline-manifest> --target <target-manifest> --output <fresh-output-directory> [--mappings <approved-mappings.json>] [--fail-on never|partial|unverified]
   ```

   Default to `--fail-on never` unless the user requested a supported gate. The `missing` gate is unsupported. Add `--dry-run` only when requested.
5. Verify `parity-results.json`, `review-queue.json`, and `comparison-log.json` exist. Report results from the engine's `parity-results.json` statistics and match records. A gate exit code 6 means artifacts were written and the requested gate failed; inspect and report those artifacts rather than calling the comparison itself an engine failure.

## Requirements Coverage

1. Validate the requirements baseline with `parity validate --requirements-baseline <baseline.json>` and confirm the separate reviewed requirements artifact is available.
2. Validate the target with `parity validate --manifest <target-manifest.json>`.
3. Choose a fresh output directory and run:

   ```text
   python <absolute-cli-path> parity cover-requirements --baseline <baseline.json> --reviews <reviewed-requirements.json> --target <target-manifest.json> --output <fresh-output-directory> [--fail-on never|partial|unverified]
   ```

   The default gate is `never`; use another supported gate only when requested. `missing` and high-risk gates are not supported.
4. Verify `requirements-coverage.json`, `review-queue.json`, and `requirements-comparison-log.json`. Summarize engine-produced counts, unresolved criteria, and scope limitations.
5. If only raw requirements text/JSON is supplied, use `ingest-requirements` and `requirements-review-template` to prepare provisional inputs, then pause for a human to review the requirement contracts and criterion mappings. Do not claim coverage until that separate review is complete.

## Reports

Render a report only when the user asks for one. The engine is the only renderer; never hand-author or restyle HTML or Markdown.

```text
python <absolute-cli-path> parity report --artifact <parity-results.json> --source <baseline-manifest> --target <target-manifest> --output <fresh-output-directory> [--format html|markdown|both]
```

For requirements coverage, supply `--artifact <requirements-coverage.json> --baseline <baseline.json> --target <target-manifest.json>` instead. The supporting manifests are digest-verified against the result; exit code 3 means they are stale for that result, so rerun the workflow rather than editing artifacts.

`feature-report.json` is always written and `feature-report.html` is the default rendering; request Markdown only when the user asks for it. Report only values present in `feature-report.json`, and follow `../codepulse-shared/renderers/feature-report-template.md`. Feature reports carry no findings, severities, grades, scores, or recommendations.

## Review Boundaries

- Discovery candidates and identity suggestions do not establish equivalence.
- Approved mappings nominate candidates; independent contract/evidence checks still determine comparison status.
- Unmatched features remain unverified. Complete scan scope does not prove absence.
- Requirements coverage is a separate workflow and does not promote requirements evidence into implementation proof.
- Do not claim runtime parity, complete business scope, or confirmed absence. Do not assign health grades.
- This workflow emits JSON artifacts; HTML and Markdown come only from `parity report`. Do not hand-author a report.

## Completion

State the workflow and inputs used, engine-produced counts and statuses, gate outcome, unresolved review items, limitations, and artifact paths. Distinguish candidate selection, human review, and contract equivalence. Never claim stronger evidence than the result records support.