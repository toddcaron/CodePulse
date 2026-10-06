# Feature Parity Engine (Development Milestone)

Version 0.9.0 implements configurable repository inventory, provisional OpenAPI,
C#, Vue/AngularJS and ColdFusion discovery, manifest validation and conservative
reviewed-contract comparison, digest-bound human review reconciliation and
structured JSON and explicitly marked text/Markdown requirements ingestion, and
separately reviewed static requirements coverage and persisted provisional agent enrichment.
It is not the completed Finder or Parity release,
and no new slash commands are installed yet.
The existing CodePulse health skills are unchanged.

## Setup

Python 3.11+ is required. Provision an isolated environment explicitly before
running the engine. From the CodePulse repository root on Windows:

```powershell
python -m venv "$env:TEMP/codepulse-feature-parity-venv"
& "$env:TEMP/codepulse-feature-parity-venv/Scripts/python.exe" -m pip install -r codepulse-shared/tools/feature-parity/requirements.lock
```

On Linux/macOS:

```sh
python3 -m venv /tmp/codepulse-feature-parity-venv
/tmp/codepulse-feature-parity-venv/bin/python -m pip install -r codepulse-shared/tools/feature-parity/requirements.lock
```

Use the environment's Python for subsequent commands (abbreviated below as
`python`). No runtime command installs packages, calls a model, builds the
application, executes its scripts or tests, or contacts its services.

Keep this directory with the sibling `codepulse-shared/schemas/` assets. Run
`cli.py` by its installed path; `pip install` of an isolated engine directory is
not a supported distribution layout. `pyproject.toml` records runtime metadata;
`requirements.lock` pins the development/runtime dependency set.

## Commands

### Agent Enrichment

Export evidence-bound placeholders and import completed proposals using fresh
output directories:

```sh
python codepulse-shared/tools/feature-parity/cli.py parity enrichment-template --manifest /path/to/feature-manifest.json --output /path/to/new-template
python codepulse-shared/tools/feature-parity/cli.py parity import-enrichment --manifest /path/to/feature-manifest.json --enrichment /path/to/completed-proposals.json --output /path/to/new-enriched-results
```

Both accept `--dry-run`. The template is intentionally incomplete and cannot be
imported unchanged. Supply agent/model/version provenance, a rationale and at least
one permitted update per retained proposal; remove unused proposals. Import accepts
at most 100 proposals, with one proposal per existing active feature. Template export
requires 1-100 active features; larger template selection is not implemented.

Import writes `feature-manifest.json`, `enrichment-proposals.json`,
`review-queue.json` and `enrichment-log.json`. It validates manifest/inventory/contract
digests and exact current/proposed evidence citations with content hashes and record
digests. It creates no evidence or new features. Touched features become `needs-review`
and lose any previous approval, even for name-only edits. Evidence verification,
confidence, admission, identity and fingerprints remain unchanged. No application
code or agent/model is executed by the engine.

Use `review-template` on the imported manifest followed by independent human
`reconcile`. The original manifest and retained proposals stay unchanged. An
unapproved proposal cannot establish equivalence or verified gate credit. Provenance
is declared metadata, not authenticated agent identity; independent human review
remains an external responsibility. See the [enrichment contract](../../references/feature-enrichment.md).

### Command Examples

```sh
python codepulse-shared/tools/feature-parity/cli.py parity find --source codepulse-shared/tools/feature-parity/tests/fixtures/openapi-app --output ../codepulse-finder-results --application-name "Synthetic API"
python codepulse-shared/tools/feature-parity/cli.py parity find --source codepulse-shared/tools/feature-parity/tests/fixtures/dotnet-app --output ../codepulse-dotnet-results --scope api --confidence-threshold low
python codepulse-shared/tools/feature-parity/cli.py parity find --source codepulse-shared/tools/feature-parity/tests/fixtures/ui-legacy-app --output ../codepulse-ui-legacy-results --scope ui,api,integrations,reports,jobs
python codepulse-shared/tools/feature-parity/cli.py parity validate --manifest codepulse-shared/tools/feature-parity/tests/fixtures/baseline.json
python codepulse-shared/tools/feature-parity/cli.py parity ingest-requirements --source codepulse-shared/tools/feature-parity/examples/requirements.json --output ../codepulse-requirements-results
python codepulse-shared/tools/feature-parity/cli.py parity ingest-requirements --source codepulse-shared/tools/feature-parity/examples/requirements.md --application-name "Synthetic Accounts" --output ../codepulse-prose-results
python codepulse-shared/tools/feature-parity/cli.py parity validate --requirements-baseline ../codepulse-requirements-results/requirements-baseline.json
python codepulse-shared/tools/feature-parity/cli.py parity requirements-review-template --baseline ../codepulse-requirements-results/requirements-baseline.json --output ../codepulse-requirements-review-template
python codepulse-shared/tools/feature-parity/cli.py parity cover-requirements --baseline ../codepulse-requirements-results/requirements-baseline.json --reviews ../codepulse-requirements-review-template/requirements-reviews.json --target codepulse-shared/tools/feature-parity/tests/fixtures/baseline.json --output ../codepulse-requirements-coverage --fail-on unverified --dry-run
python codepulse-shared/tools/feature-parity/cli.py parity review-template --manifest codepulse-shared/tools/feature-parity/tests/fixtures/target.json --output ../codepulse-review-template
python codepulse-shared/tools/feature-parity/cli.py parity reconcile --manifest codepulse-shared/tools/feature-parity/tests/fixtures/target.json --reviews ../codepulse-review-template/review-decisions.json --output ../codepulse-reviewed-results --dry-run
python codepulse-shared/tools/feature-parity/cli.py parity compare --source codepulse-shared/tools/feature-parity/tests/fixtures/baseline.json --target codepulse-shared/tools/feature-parity/tests/fixtures/target.json --output /path/to/new-results
```

All samples are synthetic. The manually authored baseline/target fixtures
illustrate the comparison contract; the OpenAPI fixture exercises real extraction
with hashes of the scanned file. None certifies a real application's capabilities.

### Finder

`find` accepts a local directory as an explicitly authorized source. The output
must be a fresh directory outside that source (including resolved ancestor/link
overlaps), so a scan never writes to the scanned repository. Output is JSON only:

- `feature-manifest.json`
- `repository-inventory.json`
- `evidence-index.json`
- `review-queue.json`
- `discovery-log.json`

Finder dry-run checks source/output paths and resolves/validates configuration;
it prints the effective policy but neither inventories nor writes.
Normal runs print engine-derived counts from the discovery log. Zero features is
a successful limited scan, not evidence that the application has no capabilities.

Inventory is sorted and records source-relative paths, language, size, hash,
adapter and exclusion reason. It excludes links and Windows reparse points,
standard dependency/generated directories, common sensitive configuration/key
files, binary/non-UTF-8 files and files over 1 MiB. Traversal is capped at 20,000
entries and 64 directory levels. Unreadable or depth-limited locations are
disclosed. Excluded directories are recorded but not descended into. Configuration
can lower these limits, not raise them. Generated C# suffixes and auto-generated
headers are not promoted to features. Comprehensive secret/metadata redaction
remains planned.

JSON OpenAPI 3.x/Swagger 2.0 operation declarations with structured responses
produce provisional API candidates. Raw route names, summaries, operation IDs,
request/response examples and source excerpts are deliberately not persisted.
Evidence identifies the specification file and full-file line range; per-operation
source offsets are not yet available. Names/IDs use hashed route/method/file
identities; reviewed labels can now change without replacing an existing feature ID.
They are not architecture-independent business IDs. Repeated specs are not yet
consolidated. OpenAPI candidates are low confidence (0.25), require review and cannot
establish equivalent parity. Confidence is limited to documented declarations.

C# extraction uses a pinned Pygments lexer to mask comments and string literals,
then detects HttpGet/Post/Put/Delete/Patch/Head/Options attributes and matching
minimal API Map calls. Evidence points to the syntax line. Scores are 0.40 (low),
and all candidates require review. Conditional compilation is not evaluated;
files with #if are deferred with a limitation. Class names alone are not features.
This is lexical evidence, not Roslyn semantics: framework identity, controller
activation, startup registration, authorization, request/response contracts and
business outcomes are unresolved. Repeated OpenAPI/backend representations are
retained separately pending consolidation. C# identities include syntax offsets,
so edits before a declaration can change provisional IDs. Cross-scan identity
mapping remains deferred. No C# compilation, tests or service execution occurs.

Vue .vue template blocks provide form, click/submit action and router-link
declarations. HTML/HTM files provide AngularJS ng-submit/ng-click/ui-sref/ng-href
declarations; plain HTML does not imply AngularJS features. Python's HTMLParser
ignores HTML comments and script/style bodies. JavaScript/TypeScript router
registration detection uses Pygments masking for comments and literals, then
recognizes createRouter/new VueRouter, explicit $routeProvider.when and
$stateProvider.state calls. Only registration syntax is recorded, not individual
routes, resolved components or business workflows. Embedded .vue script blocks,
aliases, chained provider calls, template expressions, role visibility, include
resolution, dynamic routes and framework identity are not evaluated. Malformed
markup can yield incomplete or misleading syntax evidence; every item needs review.

Tag-based ColdFusion .cfm/.cfc extraction recognizes remote cffunction, cfform,
cfhttp/cfmail/cfftp, cfschedule and cfreport declarations. These map respectively to
API, UI, integrations, jobs and reports. Nested ColdFusion and ordinary HTML
comments are ignored. Files containing CFScript are conservatively deferred with
a limitation instead of treating strings as executable tags. Private/local
functions and database queries/tables alone are not capabilities. Tag presence
does not establish successful execution, active scheduling, public exposure or
reachable UI; conditions and includes are not evaluated.

Frontend/legacy candidates score 0.35 (low) and require review. Multiple declarations
(such as a form and its submit action) may belong to one feature; no consolidation
is claimed. Identity uses file and syntax location, not domain semantics. Raw
handlers, routes, recipient addresses, URLs and attribute values are not copied
into artifacts. The mixed fixture's snapshot expects 15 candidates across five
capability types, not 15 confirmed business features.

### Configuration and Admission

Finder automatically reads source-root `codepulse.config.json` when present, or
accepts an explicit `--config` JSON path. Configuration is bounded to 1 MiB and
links/reparse points are rejected. Only the featureParity section is interpreted;
unrelated sections may coexist. Unknown featureParity options fail explicitly
rather than pretending that deferred options are supported. See
`examples/codepulse.config.json` for the supported subset.

Supported settings: applicationName, defaultScope, include, exclude,
forbiddenPaths, minimumConfidence, and limits (maxFileBytes/maxEntries/maxDepth).
Explicit CLI values replace corresponding configured values; unset values use
configuration, then defaults. Flags: --application-name, --scope (comma-separated),
--include/--exclude (repeatable), --confidence-threshold, and --config. Defaults
are all scopes, no include filter, standard exclusions, medium threshold and the
resource limits above. Every run records resolved configuration and its digest.

Patterns use pathspec gitwildmatch semantics over source-relative POSIX paths,
case-sensitive on every OS. Examples: src/**, **/*.json, private/**. Absolute paths,
backslashes, traversal segments, negation and comments are rejected. Exclude and
forbidden directory matches prune traversal; includes select files but do not
prune unmatched ancestors. Includes cannot bypass standard exclusions, sensitive
files or link policy. Scope filters extraction, not inventory. API, UI, integrations,
reports and jobs can currently produce candidates; business/authorization/data
operation discovery remains unsupported and coverage is always incomplete.

Confidence boundaries: low <0.50, medium [0.50,0.80), high >=0.80. Admission uses
the requested level's lower boundary. Default medium admits none of the current
adapters' candidates; they still appear in the manifest and review queue with
admitted=false and belowThreshold counts. Lowering to low admits candidates but
never confirms them or verifies evidence. Comparison cannot award equivalence to
a non-admitted feature. See the shared feature-confidence-model.md reference.

Git revision remains null. Unknown/other stacks are inventoried using the generic
fallback but do not have extraction yet; coverage is always incomplete. Changed
files between inventory and extraction are skipped and disclosed. This scanner
is not a sandbox against concurrently hostile filesystem mutations: use stable
local sources. File paths and explicit application names are metadata; never put
secret values or personal data in them. No source content values are copied to
artifacts, but comprehensive filename/metadata redaction is not implemented.

### Human Reviews

`review-template` exports `review-decisions.json` for active discovered,
needs-review and confirmed features. Each placeholder has current manifest and
contract digests, `decision=needs-review` and a blank approval reference. This is
deliberately not a valid review batch until a human completes it. An empty active
feature set fails explicitly without producing a template.

Before running the sample reconciliation command, a reviewer must remove untouched
placeholders, select decisions and provide meaningful, safe approval references.
Optional updates cover name, domain, aliases, actors, inputs, outputs, preconditions,
behaviors and references to evidence already in the manifest. Supported decisions
are confirmed, needs-review, rejected and deprecated. IDs and fingerprints remain
unchanged. Creating or verifying evidence and split/merge actions are not supported.

`reconcile` validates the entire batch and resulting manifest in memory before
writing `feature-manifest.json`, `review-queue.json` and `reconciliation-log.json`
to a fresh directory. Original inputs are unchanged. Stale manifest or contract
digests, duplicate decisions, unknown references and disallowed updates fail the
whole batch. The audit log binds input, review and output digests with per-feature
before/after digests. Replaying identical inputs is deterministic; reusing a batch
against an already changed manifest fails as stale. `--dry-run` checks without writes.

Confirmation records a human attestation, not runtime proof. It never changes
evidence verification, confidence or admission. Insufficient verification or
admission remains visible in the review queue and cannot earn equivalent parity.
Aliases are metadata only; the comparer still selects exact IDs. Review text is
persisted verbatim: do not include secrets or personal data. Approval references
are not authenticated identities. See the shared
[review workflow](../../references/feature-review-workflow.md) for the boundary.

### Requirements

`ingest-requirements` accepts one local UTF-8 JSON document conforming to
`feature-requirements-input-schema.json`. See `examples/requirements.json` for
synthetic complete and ambiguous declarations. Required fields explicitly cover
IDs, names, domains, capability types, actors, inputs, outputs, preconditions,
atomic behaviors, acceptance criteria and ambiguities. Unknown contract arrays
may be empty; the importer does not fill them or infer obligations from prose.
Behavior mandatory flags are supplied, never inferred.

Output is a fresh directory containing `requirements-baseline.json`,
`feature-manifest.json`, `review-queue.json` and `requirements-log.json`.
The baseline preserves the original declarations, including order, criteria and
ambiguities. Features and links are sorted deterministically. Input document,
source bytes, baseline and manifest digests are recorded. Evidence paths are
relative to the selected file's parent, use its filename and cover the entire
input file; individual JSON record offsets are not yet available.

Files are limited to 1 MiB. Linked paths/reparse points, sensitive filenames,
non-UTF-8 data, malformed JSON, duplicate keys/IDs and unknown fields fail before
publication. `--dry-run` validates without creating directories or files. Empty
requirements are a successful incomplete import, not evidence of complete scope.
The same staged-publication limitation as comparison applies; require all four
artifacts before consuming a run.

Every imported feature has low confidence (0.25), admitted=false, partially
verified requirement evidence and needs-review status. Human confirmation does
not change those axes. The generated manifest works with review-template and
reconcile, but neither imported nor merely confirmed requirements can earn
equivalent parity under the current comparer. Acceptance criteria and ambiguities
remain in the original baseline; feature review does not rewrite that baseline.
Requirements coverage uses a separate approved-contract file, described below;
it never upgrades these imported feature records. Automated criteria interpretation
remains deferred.

`validate --requirements-baseline` checks the schema, preserved-document digest,
duplicate IDs, safe evidence paths/ranges, source hash consistency and feature
links offline. It checks internal integrity, not original source truth or reviewer
authority. Structured descriptions and metadata are intentionally preserved:
inputs must contain no secrets or personal data. YAML, PDF,
Word documents and collections are not yet supported; convert explicitly to the
structured format without treating an agent conversion as human approval. See
the shared [requirements contract](../../references/feature-requirements-model.md).

Text/Markdown (`.txt`/`.md`) uses a deliberately narrow marker grammar, not general
Markdown or natural-language interpretation. Only unindented `Requirement: Title`
or ATX headings such as `## Requirement: Title` start a proposal. Following nonblank
lines are retained as one unresolved description until a blank, heading, new marker,
comment or code fence. Backtick/tilde fences, HTML comments, quoted markers and
indented markers do not start proposals. Tables, arbitrary bullets and ordinary
"shall" prose are not interpreted. Ignored nonempty lines are counted in sourceMap;
zero extracted proposals does not establish complete requirements coverage.

Prose proposals have Unclassified/business placeholders, empty actor/input/output/
precondition/criteria arrays, one nonmandatory placeholder behavior and an explicit
ambiguity. `mandatory=false` means unresolved here, not an approved optionality
decision. No roles, constraints, acceptance criteria or mandatory flags are inferred
from wording. SourceMap records inclusive line ranges, checked against evidence;
exact source-byte hashes still distinguish CRLF/LF changes. Labels default to the
filename stem or use `--application-name` (JSON declares its own name and rejects
that flag). Titles plus line numbers form provisional IDs, so edits can change IDs.
This is not cross-scan identity reconciliation. Captured descriptions preserve
continuation whitespace but not the entire source document. All imported proposals
remain unapproved and cannot earn parity credit. See `examples/requirements.md`.

### Reviewed Requirements Coverage

`requirements-review-template --baseline FILE --output NEW_DIRECTORY` exports
`requirements-reviews.json`. Each decision contains baseline and declaration
digests, an editable complete contract, blank approvedReference, and empty behavior
mappings for declared criteria. Templates are deliberately unapproved. Before the
sample coverage command, a human must fill references, resolve contract ambiguity
and map every criterion to mandatory behavior IDs. Remove untouched decisions;
omitted requirements remain unresolved, not excluded. Empty baselines/templates
are supported and produce null coverage, never 100%.

`cover-requirements --baseline FILE --reviews FILE --target MANIFEST --output
NEW_DIRECTORY` validates all inputs and writes `requirements-coverage.json`,
`review-queue.json` and `requirements-comparison-log.json`. `--dry-run` validates
without writes. Stale/duplicate/unknown reviews, missing criteria mappings and
invalid contracts reject the run before publication. Input artifacts stay unchanged.
The staged multi-file publication limitation applies here too.

Reviewed contracts must resolve ambiguities, populate actors/inputs/outputs/
preconditions and have at least one explicit mandatory behavior. They retain the
requirement ID, capability type, every originally mandatory behavior's ID and
description, and all original acceptance criteria. Added mandatory behaviors and
criteria are allowed; original obligations cannot be removed, demoted or rewritten.
Intentional changes require a future separate decision workflow. Prose placeholders
may be resolved in this separate contract, leaving the original baseline untouched.

Exact IDs nominate target candidates only. Covered requires an independently
confirmed, admitted repository feature with current approval and verified evidence,
implementation-type evidence for each target behavior, agreeing capability type
and actor/input/output/precondition contracts, and all reviewed mandatory behavior
descriptions present. Extra target behaviors or differing constraints require SME
review. A criterion is covered only when all of its explicitly mapped mandatory
behaviors are covered. Mappings are human interpretations, not engine inference.

Statuses are covered, partial, unable-to-verify and needs-sme-validation. Unknown
targets never become missing. Coverage percentage is covered / all declared
requirements, including unreviewed and unresolved records; partial gets no full
credit. This differs intentionally from manifest parity's verified denominator.
Counts of reviewed, partial and unresolved records remain visible. This evaluates
reviewed static contracts, not runtime acceptance tests or full business scope.

Gates default to `--fail-on never`; `partial` fails on partial coverage and
`unverified` additionally fails on unresolved/SME records. Outputs are persisted
before exit 6. Requirements gates do not offer missing or high-risk policy yet.
Approval references are unauthenticated attestations. Review files must contain
safe text and be retained with the baseline and target for audit. See the shared
[coverage workflow](../../references/feature-requirements-coverage.md).

### Comparison

`compare` requires two distinct manifest files and a fresh output directory.
It writes `parity-results.json`, `review-queue.json` and `comparison-log.json`.
Output is staged before publication, but publishing the three files is not a
transaction; a filesystem failure may leave an incomplete output directory.
The same publication limitation applies to reconciliation.
Do not consume a run without all three artifacts. Full run-state recovery is
planned, not implemented.

Comparison `--dry-run` validates inputs and output policy without writing anything.
Manifest comparison `--fail-on` defaults to `never`. Supported gates:

- `missing`: fails on verified missing records (this engine never asserts missing).
- `partial`: fails on partial or missing records.
- `unverified`: also fails on unable-to-verify and needs-sme-validation records.

Exit codes: 0 completed, 1 invalid invocation/runtime, 2 filesystem access
failure, 3 invalid artifact, 4 engine failure, 5 output/input policy restriction,
6 gate failure. Results are written before a gate failure. Execution failures
are never converted into successful gate results.

## What Equivalence Means Here

Exact IDs nominate candidates only. An equivalent result requires both features
to be reviewed, approvals to match current contracts and evidence, all referenced
evidence to be verified, nonempty actor/input/output/precondition contracts, and
exact agreement on mandatory behavior descriptions and contract constraints.
Additional target behaviors require review. Different descriptions are not
automatically interpreted as synonymous. Partial results identify mandatory
baseline behavior descriptions without corresponding target descriptions; this
is a contract-level gap, not proof that runtime behavior is absent.

Approval digests bind the feature ID, domain, capability type, actors, inputs,
outputs, preconditions, behavior records, referenced evidence metadata/hashes and
admission when present.
Renaming a display label does not revoke the approval or change identity. Changes
to behavior, authorization or evidence revoke the supplied approval. Review
references are attestations, not authenticated identities; approval authority
verification remains future work. Do not generate approval records
from an agent proposal and call them human approval.

Equivalence is limited to reviewed static contracts. The engine cannot establish
business completeness or runtime correctness. An unmatched feature remains
unable-to-verify even when a manifest declares complete scan coverage. A
new-in-target record means no exact-ID baseline match, not proof of a genuinely
new capability; renamed features may remain unresolved.

Coverage is equivalent / (equivalent + partial + missing). Unresolved baseline
records and target-only records are excluded from the denominator and displayed
separately. An empty denominator produces null, never 100%. Consumers must show
unresolved counts next to percentages. Future intentional-decision statuses will
extend this formula explicitly.

## Safety and Limitations

Schemas are draft 2020-12 and resolved using a local registry without remote
retrieval. Schema errors omit source values. Inputs reject duplicate JSON keys,
NaN/Infinity, unknown fields, unsafe evidence paths, dangling references, duplicate
identifiers and stale approvals. Artifact CLI inputs are limited to 16 MiB;
requirements source files have the lower 1 MiB limit. Finder outputs avoid raw
source values; imported manifests, review notes and structured requirements can
retain their supplied text. These inputs must already contain safe content;
comprehensive redaction is
not implemented. Manifest validation checks artifact integrity, not source-file
truth. Finder reads the specification and hashes its actual bytes, but cannot
verify that the described operations have executable implementations.

Version 1.0 schema documents are initial contracts subject to refinement before
the first complete release. The result schema accepts only currently emitted
statuses. Its status-count object reserves all nine planned statuses.

Not yet implemented: deep .NET/frontend/ColdFusion semantics, YAML adapters,
domain mappings/synonyms, comprehensive redaction, general prose requirements
interpretation, advanced requirements mappings and runtime acceptance verification,
review split/merge lineage, alias/semantic mappings, agent enrichment,
intentional decisions, confirmed absence, high-risk gates, incremental scans,
HTML/Markdown rendering, checkpoint recovery and skill orchestration.

## Tests

```sh
python -m unittest discover -s codepulse-shared/tools/feature-parity/tests -v
```

Tests run analysis code and synthetic inputs only, never application code.
The ui-legacy-summary.json snapshot locks candidate/evidence distribution without
volatile timestamps, absolute paths or source hashes.
The existing `validate-codepulse.ps1` remains the separate health-skill validator.