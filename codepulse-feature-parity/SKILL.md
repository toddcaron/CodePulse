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
6. Once the comparison artifacts are verified, choose a second fresh report output directory that does not overlap the inputs or comparison output, then run `parity report` with `parity-results.json` as `--artifact`, and the same baseline and target manifests as `--source` and `--target`. Omit `--format` by default to render HTML. Use `--format markdown` or `--format both` only if the user requests that format. This also applies when the compare command returns gate exit code 6 because the result artifacts still exist.
7. Verify `feature-report.json` and `feature-report.html` (and `feature-report.md` when requested). If report generation fails, state separately whether the comparison completed and that the report failed.

## Requirements Coverage

If only raw requirements text/JSON is supplied, use `ingest-requirements` and
`requirements-review-template` to prepare provisional inputs, then pause for a human
to review the requirement contracts and criterion mappings. Do not claim coverage or
render a report until that separate review is complete and `cover-requirements` has
produced a result.

1. Validate the requirements baseline with `parity validate --requirements-baseline <baseline.json>` and confirm the separate reviewed requirements artifact is available.
2. Validate the target with `parity validate --manifest <target-manifest.json>`.
3. Choose a fresh output directory and run:

   ```text
   python <absolute-cli-path> parity cover-requirements --baseline <baseline.json> --reviews <reviewed-requirements.json> --target <target-manifest.json> --output <fresh-output-directory> [--fail-on never|partial|unverified]
   ```

   The default gate is `never`; use another supported gate only when requested. `missing` and high-risk gates are not supported.
4. Verify `requirements-coverage.json`, `review-queue.json`, and `requirements-comparison-log.json`. Summarize engine-produced counts, unresolved criteria, and scope limitations.
5. After the coverage result is verified, choose a second fresh report output directory that does not overlap the inputs or coverage output, then run `parity report` with `requirements-coverage.json` as `--artifact`, the same requirements baseline as `--baseline`, and the same target manifest as `--target`. Omit `--format` by default to render HTML. Use `--format markdown` or `--format both` only if the user requests that format.
6. Verify `feature-report.json` and `feature-report.html` (and `feature-report.md` when requested). If report generation fails, state separately whether coverage completed and that the report failed.
## Reports

Render a report automatically after every successful completed comparison or requirements-coverage run, including a comparison whose requested gate fails after writing its result artifacts. Do not render reports for dry-runs, failed runs without result artifacts, or preparation-only commands such as validation, ingestion, template export, or identity reconciliation. Use a separate fresh output directory that does not overlap the inputs or the workflow's JSON output. The engine is the only renderer; never hand-author or restyle HTML or Markdown.

```text
python <absolute-cli-path> parity report --artifact <parity-results.json> --source <baseline-manifest> --target <target-manifest> --output <fresh-output-directory> [--format html|markdown|both]
```

For requirements coverage, supply `--artifact <requirements-coverage.json> --baseline <baseline.json> --target <target-manifest.json>` instead. The supporting manifests are digest-verified against the result; exit code 3 means they are stale for that result, so rerun the workflow rather than editing artifacts.

Omit `--format` for the default HTML report; request Markdown or both formats only when the user asks. `feature-report.json` is always written. Verify the report files before claiming report generation succeeded. Report only values present in `feature-report.json`, and follow `../codepulse-shared/renderers/feature-report-template.md`. Feature reports carry no findings, severities, grades, scores, or recommendations.

## Review Boundaries

- Discovery candidates and identity suggestions do not establish equivalence.
- Approved mappings nominate candidates; independent contract/evidence checks still determine comparison status.
- Unmatched features remain unverified. Complete scan scope does not prove absence.
- Requirements coverage is a separate workflow and does not promote requirements evidence into implementation proof.
- Do not claim runtime parity, complete business scope, or confirmed absence. Do not assign health grades.
- The comparison and coverage commands emit JSON; the skill then runs `parity report` by default to create HTML. HTML and optional Markdown come only from the engine. Do not hand-author a report.

## Completion

State the workflow and inputs used, engine-produced counts and statuses, gate outcome, unresolved review items, limitations, and paths to both workflow and report artifacts. Distinguish candidate selection, human review, and contract equivalence. If report generation fails, report that separately from workflow completion. Never claim stronger evidence than the result records support.