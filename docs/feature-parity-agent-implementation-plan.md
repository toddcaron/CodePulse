# Feature Parity Agent Implementation

## Current State

Last updated: **2026-10-02**. Engine version: **0.8.0**.

**Latest completed milestone:** reviewed static requirements coverage.
**Release status:** development engine only; the first complete release is not finished.
**Active implementation:** none currently in progress. The next recommended slice
is persisted agent enrichment, followed by approved identity mappings.

The engine can discover provisional capabilities, reconcile human feature reviews,
ingest requirements, compare reviewed feature manifests and assess separately
reviewed requirements against supported target manifests. It does not build or run
assessed applications and does not prove runtime parity or complete business scope.

Latest completed validation: **177 tests run, 176 passed, 1 skipped** for Windows
symlink permissions. Existing CodePulse health validation passed. Editor diagnostics
and tracked whitespace checks passed. These results describe the 0.8 milestone,
not acceptance of the unfinished release.

### Available Commands

All commands use `python codepulse-shared/tools/feature-parity/cli.py parity`:

- `find`: bounded inventory and provisional repository discovery.
- `validate`: feature manifest or requirements-baseline integrity checks.
- `review-template` and `reconcile`: human feature-review workflow.
- `ingest-requirements`: structured JSON or explicitly marked text/Markdown proposals.
- `requirements-review-template` and `cover-requirements`: separate human-approved
  requirement contracts, criterion mappings and static coverage.
- `compare`: reviewed manifest-to-manifest comparison; repository inputs are not supported.

See the [engine guide](../codepulse-shared/tools/feature-parity/README.md) for setup,
command arguments, output artifacts, gates and supported syntax.

### Completed Milestones

- **0.1:** schemas, offline validation, reviewed exact-ID comparison and basic CLI gates.
- **0.2:** secure bounded inventory and provisional JSON OpenAPI discovery.
- **0.3:** configuration, confidence admission and lexical C# HTTP discovery.
- **0.4:** initial Vue/AngularJS and tag-based ColdFusion adapters.
- **0.5:** digest-bound human feature-review reconciliation and audited outputs.
- **0.6:** structured JSON requirements ingestion and baseline integrity validation.
- **0.7:** marked text/Markdown proposals with source-line evidence and ambiguity.
- **0.8:** separate reviewed requirements contracts, explicit criterion mappings,
  conservative target coverage, audited results and persisted opt-in gates.

### What Is Not Available Yet

- Finder and Parity slash-command skills, HTML/Markdown reports and installation integration.
- Persisted agent-enrichment proposals and their review/import workflow.
- Approved alias/identity mappings, cross-scan identity reconciliation and split/merge lineage.
- Intentional-change decisions, confirmed absence, all final parity statuses and high-risk gates.
- Incremental scans, cache invalidation, checkpoint recovery and Windows/Linux CI.
- Full framework semantics, duplicate consolidation, comprehensive redaction and broader document adapters.

Human confirmation never upgrades evidence verification, confidence or admission.
Current discovery stays provisional. Reviewed requirements coverage is a separate
workflow, not a promotion of imported requirement evidence into implementation proof.

### Next Delivery Order

1. **Persisted enrichment:** add evidence-linked proposal/provenance contracts,
  stale-input checks and import into reviewable proposals only. Agents cannot set
  approvals, confidence or totals. Verify unapproved proposals receive no gate credit.
2. **Approved mappings and decisions:** add digest-bound identity mappings, rename
  reconciliation and intentional differences, then split/merge coverage without double counting.
3. **Finder completeness:** improve supported adapters, consolidate evidence and
  extend safe supporting-document extraction and redaction.
4. **Incremental and recovery:** implement dependency-aware invalidation and validated
  checkpoints; compare full, incremental and resumed results.
5. **Release integration:** add reports, skills, installation checks and CI while
  preserving existing health-skill contracts; finish remaining status/high-risk policies.

This is the recommended backlog order, not a claim that these tasks are underway.
Detailed work packages and final release acceptance checks follow below.

## Approved Decisions

- Python 3.11+ engine with pinned dependencies and explicit environment setup.
- Skills own conversations; the engine owns extraction, validation, confidence,
  comparison, statistics, gates and rendering.
- Persist agent enrichment as a versioned, evidence-linked input. It remains
  provisional until reviewed; agents cannot approve their own proposals.
- First release includes requirements coverage, incremental scans and CI gates.
- Static extraction with documented reachability limits. No application builds,
  repository script/test execution, live service calls or engine LLM calls.
- Root-level distributable skill directories and sibling shared resources.
- Exact IDs currently select candidates; aliases and approved mappings are planned.
  Candidate matching alone never establishes behavioral parity.

The source proposal remains unchanged. This document records the clarified
implementation direction and delivery status, not a claim that all features
below have been implemented.

## Implemented Detail Through 0.8

The following capabilities are implemented within the documented limits. This
section is cumulative; the status summary above is the current delivery snapshot.

- Initial manifest/result schemas with offline draft 2020-12 validation.
- Canonical evidence IDs and reference-integrity validation.
- Review digest checks binding approvals to behavior and evidence.
- Deterministic, exact-ID candidate comparison of reviewed static contracts.
- Conservative equivalent/partial/unverified/review/target-only classifications.
- JSON outputs with evidence references and engine-derived statistics.
- `validate` and manifest-only `compare` commands; basic opt-in gates and dry-run.
- Synthetic fixtures and focused unit/CLI tests.
- Bounded read-only repository inventory, standard/sensitive exclusions,
  link/reparse-point policy and inventory schema validation.
- `find` command producing five JSON artifacts and engine-derived counts.
- Provisional JSON OpenAPI operations; no invented business contracts or runtime
  reachability. Unknown technologies are inventoried with explicit limitations.
- Fresh external output policy, source-change checks, read-only dry-run and
  Finder-to-comparison CLI tests from an unrelated working directory.
- Schema-validated source-root/explicit configuration, CLI precedence, scopes,
  include/exclude/forbidden globs and lowerable resource limits.
- Policy digest, confidence boundaries and explicit admission: below-threshold
  candidates remain reviewable but cannot establish equivalence.
- Comment-aware C# HTTP attributes/minimal API syntax with line-level evidence;
  generated and conditional sources stay unpromoted. Pinned Pygments is used for
  lexical masking, not full framework resolution.
- Initial Vue/AngularJS form/action/navigation and router declarations, with
  template/comment/script handling and lexical JS/TS masking.
- ColdFusion remote functions, forms, integrations, scheduled tasks and reports
  from supported tags; nested comments are ignored and CFScript files deferred.
- Capability-aware candidates and scope filters, mixed-stack fixture and summary
  snapshot. Syntax values are not copied to evidence; all items remain provisional.

- Digest-bound human review batches and schema-validated reconciliation audit logs.
- Unapproved `review-template` export and fail-closed `reconcile` commands, with
  fresh outputs, bounded input reads and no-write dry-run.
- Confirm/reopen/reject/deprecate decisions and controlled contract/metadata edits;
  naming changes preserve existing IDs and fingerprints. Evidence references may
  attach only existing records; evidence verification/confidence/admission are unchanged.
- Atomic logical batch validation, stale/conflicting decision rejection, untouched
  feature preservation and real review CLI tests from unrelated working directories.

- Strict structured requirements input/baseline/log contracts and the
  `ingest-requirements` command with bounded, hash-bound reads and no-write dry-run.
- Preserved declared IDs, atomic behaviors, mandatory flags, acceptance criteria
  and ambiguities; source-relative full-file evidence and deterministic links.
- Provisional requirements-derived manifests compatible with review workflows;
  import and confirmation cannot upgrade evidence/admission or earn parity credit.
- Offline baseline validation of digests, IDs, evidence provenance and references,
  synthetic examples and real CLI ingestion/review-export integration tests.

- Explicitly marked text/Markdown proposals with block-level source evidence,
  ignored-line disclosure, fenced-example/comment exclusion and unresolved contracts.
- Source-map schema and integrity validation; application labels, malformed/binary
  input rejection, synthetic Markdown example and real ingestion/validation CLI tests.

- Separate digest-bound human-reviewed requirements contracts and explicit
  acceptance-criterion-to-mandatory-behavior mappings, preserving original obligations.
- Requirements-review-template and cover-requirements commands with dry-run,
  supported repository targets, no baseline/evidence promotion and exact-ID matching.
- Covered/partial/unresolved/SME outcomes, all-declared-requirement denominator,
  persisted opt-in gates, audited JSON outputs and real subprocess integration tests.

This is version 0.8.0, not a completed MVP. The first schema contracts will be
extended before release. No new slash-command skill is registered yet.

## Remaining Work Packages

### 1. Complete Contracts (Partial)

Define invocation, candidates, enrichment,
review actions, approved parity decisions, cache and run-state schemas. Extend
configuration and confidence models beyond their implemented initial subsets.
Specify independent-evidence weights, review lineage, approved mappings,
criticality, all nine statuses and final coverage/gate policies. Add invalid and
positive fixtures before implementing consumers. Feature contracts are separate
from health schema 2.0, health finding IDs and letter grades.

### 2. Secure Inventory and Finder (Partial)

Inventory policy, JSON OpenAPI and initial C#/frontend/ColdFusion extraction are implemented.
Extend them with metadata redaction, Git revision tracking, duplicate consolidation,
domain mappings/synonyms, business normalization and
operation-level evidence offsets. Harden resource limits and filesystem access
against changing sources; current scans require stable local filesystems and are
not a sandbox. Extend framework semantics and add documentation/tests,
YAML OpenAPI and SQL supporting evidence. Vue embedded script/route resolution and
ColdFusion CFScript are not implemented. Dead/commented/generated-only evidence
must remain provisional; never execute source repositories.

### 3. Reviews, Requirements and Enrichment (Partial)

Feature reviews, requirements ingestion and reviewed static coverage are implemented.
Enrichment is not started.

Basic review import/reconciliation and within-manifest rename preservation are
implemented. Add cross-scan identity mapping, split/merge lineage, new evidence
creation/verification and authenticated approval authority. Structured JSON
and explicitly marked text/Markdown ingestion are implemented; add broader prose
interpretation and document collections. Resolved contracts and explicit criterion
mappings now live in separate requirements reviews without rewriting original inputs.
Unsupported binary formats
require conversion. Ambiguity enters review, never invented requirements. Validate
enrichment provenance, inventory/evidence hashes and references; proposals cannot
set engine totals/confidence or human approval. Approved intentional differences
retain underlying evidence and differences.

### 4. Full Comparison (Partial)

Add aliases, explicit mappings, deterministic behavior candidates and approved
enrichment. Every stage still checks outcomes, mandatory behaviors, actors,
inputs/outputs, authorization and preconditions. One-to-many and many-to-one
mappings retain per-baseline coverage. Missing requires adequate reviewed scope;
incomplete scans stay unverified. Exact-ID reviewed requirements coverage is
implemented; add advanced mappings and automated acceptance-criteria interpretation.
Implement remaining modes, intentional decisions,
all statuses, business-configured high-risk gates and internal repository
discovery. Persist results before gate failure; fatal engine failures remain fatal.

### 5. Incremental and Recovery (Not Started)

Cache evidence/dependency hashes and versioned configuration, adapter, schema,
requirements, review, decision and enrichment inputs. Dirty-worktree content is
authoritative, not Git revision alone. Invalidate transitive dependencies; use
full scans when unknown. Retain approvals only while their evidence remains valid.
Track removed evidence/orphans. Validate checkpoints before resuming and preserve
safe run-status output on partial failure.

### 6. Skills, Reports and Integration (Not Started)

Add Finder and Parity SKILL.md files with slot precedence, context inference,
minimal questions, engine invocation and truthful completion summaries. Write
JSON-driven HTML/Markdown reports with scope, revisions, review state, formulas,
unresolved counts and limitations. Add explicit feature profiles to shared runtime
and report guidance and to validate-codepulse.ps1, preserving every existing
health assertion. Add installation smoke tests and Windows/Linux CI. Feature
results do not become inputs to codepulse-exec or codepulse-full in this release.

## Agent Ownership

The contracts/runtime lead owns shared schemas and interfaces. Once stable,
adapter owners can work independently on .NET, frontend and legacy/documentation
fixtures. Review/requirements and report work can proceed against those contracts.
Comparison and incremental owners follow the approved behavior/dependency model.
The integration/test owner controls shared guidance, the validator and skills.
Do not parallel-edit shared contracts without coordinating with their owner.

Each handoff includes implementation paths, supported syntax/limits, fixtures,
focused validation commands and remaining gaps. No agent makes a commit or
executes source code without explicit authorization.

## Final Release Acceptance Checks

These are release requirements, not a list of checks already completed. Current
milestone validation is recorded at the top. Split/merge, incremental/resumed runs,
comprehensive redaction, HTML and installation/CI acceptance remain pending.

- Schema validation plus duplicate/dangling reference checks for every artifact.
- Same-ID behavior/authorization differences cannot silently pass equivalence.
- Unapproved enrichment and stale reviews cannot supply verified gate credit.
- Unknown/failed extraction does not become a confirmed absence claim.
- Fixtures cover mixed frameworks, duplicates, dead/comment/generated candidates,
  requirements ambiguity, renamed/split/merged capabilities and approved changes.
- Full, incremental and resumed runs produce identical canonical semantic results
  after edits/deletions/configuration/review changes; exclude volatile telemetry.
- Synthetic secrets/PII never appear in persisted artifacts, logs or cache.
- Gates, safe error categories, no-write dry-run, safe HTML and installation from
  an unrelated working directory are covered by executable tests.
- Existing health validation passes unchanged; no application code executes.