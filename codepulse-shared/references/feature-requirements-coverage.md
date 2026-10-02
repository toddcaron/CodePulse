# Reviewed Requirements Coverage

This contract evaluates reviewed obligations against reviewed static target
contracts. It does not build applications, execute tests/services, verify runtime
acceptance or authenticate reviewer authority. Requirements evidence remains
partially-verified and imported features remain non-admitted. No baseline records
are promoted into verified implementation evidence.

## Workflow

1. Ingest JSON or marked prose to obtain requirements-baseline.json.
2. Export `parity requirements-review-template --baseline BASELINE --output NEW_DIRECTORY`.
3. A human completes each approvedReference, resolves the copied contract, and
   maps every criterion to one or more mandatory behavior IDs. Remove untouched
   decisions. Blank references and empty mapping placeholders cannot approve.
4. Validate through `parity cover-requirements --baseline BASELINE --reviews REVIEWS --target TARGET_MANIFEST --output NEW_DIRECTORY --dry-run`.
5. Publish without dry-run, retaining the original baseline, reviews and target.
   Optional fail-on values are never, partial and unverified.

Reviews bind the complete original baseline digest and each declaration digest.
Changing evidence/source/declarations makes old reviews stale. Duplicate or unknown
IDs reject the entire batch. The reviewed contract must keep identity/capability,
all original mandatory IDs/descriptions and all declared criteria. Mandatory
behaviors cannot be demoted or rewritten. Intentional removal/change is deferred.
Contracts must have nonempty actor/input/output/precondition arrays, no ambiguity,
and at least one mandatory behavior. Added obligations are allowed. Prose placeholders
can be replaced by explicit reviewed behaviors and constraints without changing the
original baseline; their false mandatory flag was an unresolved placeholder.

Criterion mappings must cover exactly the reviewed criterion set, once per
criterion, using existing mandatory IDs. Human interpretation owns this mapping.
The engine checks integrity, not whether the mapping captures the criterion's
business meaning. Empty reviews are valid: every unreviewed obligation remains
unable-to-verify. Agent proposals cannot act as human approval.

## Coverage Rules

Targets are selected by exact ID only. Covered needs a current confirmed/admitted
repository target with verified evidence, populated constraints, a mandatory
behavior and at least one implementation-type evidence record per behavior.
Supported types include endpoint, route, UI, service, handler, test, authorization,
integration, data-operation, report and job. Documentation/requirements alone
cannot supply implementation support. These evidence classifications and reviews
are supplied attestations, not independently authenticated source truth.

Capability and actor/input/output/precondition sets must agree. Additional target
behavior descriptions or differing constraints enter SME review and receive no
coverage credit. Every mandatory reviewed description must match a supported target
description. Some matched descriptions with outstanding mandatory obligations yield
partial; none yield needs-sme-validation. A criterion is covered only when every
mapped mandatory behavior is covered. Unmatched targets remain unable-to-verify,
never confirmed missing. Target-only features do not affect requirement totals.

Full coverage = covered / all declared requirements. Partial, unreviewed and
unresolved requirements stay in the denominator and receive no full credit.
An empty baseline yields null. Report requirementCount, reviewedCount, coveredCount,
partialCount and unresolvedCount alongside the percentage. This is deliberately
not the manifest parity verified-denominator formula or proof of complete scope.

## Publication and Safety

Three artifacts are required: requirements-coverage.json, review-queue.json and
requirements-comparison-log.json. Result digests bind baseline, reviews and target;
the log binds the result. Original artifacts stay unchanged. Schema and reference
validation precede writes. Staging is not an atomic multi-file transaction; do not
consume incomplete outputs. Dry-run writes nothing and does not evaluate gate exit.
Gate failure occurs only after persistence: partial rejects partial records;
unverified also rejects unable-to-verify and needs-sme-validation. Fatal errors
remain errors, independent of never policy. High-risk gates are deferred.

Review references are not authenticated signatures. Input text can be retained in
contracts and criterion lists and must contain no secrets or personal data. Claims
of runtime acceptance, business completeness or authenticated approval are prohibited.
Alias/split/merge target mappings, explicit intentional changes, automated criteria
interpretation and broader requirements extraction remain future work.