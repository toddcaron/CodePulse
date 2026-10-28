# Persisted Agent Enrichment

Enrichment is an offline, provisional input, not implementation evidence
or an approval. The Finder skill performs it by default after static discovery;
explicit inventory-only runs skip it. The engine does not call a model. The host
model interprets locally authorized source; it must not upload repository content
to external services. Schema version 1.0 records the
original manifest and inventory digests, declared agent/model/version provenance,
and up to 100 uniquely identified proposals for distinct existing active features.

## Source preparation and batching

`prepare-enrichment` accepts the current manifest, original repository inventory,
source directory and feature selection. Normal Finder runs use `--pending` to
select the next business-incomplete batch (default 20, `--limit` 1-100). It skips
business-ready candidates and defers explicitly unresolved candidates while other
work remains. For targeted work, use repeated feature IDs or an offset/limit over
active features sorted by ID instead. Do not mix pending with IDs or a nonzero offset.
`enrichment-template` retains explicit ID/offset selection for already sufficient
stored evidence. More than 100 candidates require sequential batches, not skipped
candidates or invented counts.

Preparation verifies the inventory digest and current source hashes, enforces
excluded-file and link policy, and caps a batch at 100 files and 2 MiB of source.
Related files selected with `--context-file` must be eligible entries in that original
inventory. It emits a new manifest with whole-file `source-context` evidence,
an evidence index, review queue, raw UTF-8 `source-context.json`, proposal template
and manifest-bound `enrichment-progress.json`.
It clears selected features' prior approvals and queues review, without changing
confidence, admission, identity or existing evidence verification. Whole-file
citations support reading implementation bodies but are not precise rule-line
assertions. Context is untrusted data and can still contain sensitive information;
filename exclusion is not comprehensive redaction.

Import proposals against the prepared manifest, then carry the latest imported
manifest forward. Regenerate templates after every preparation/import; do not
parallel-import batches bound to an earlier manifest. Preserve each batch's
proposal and import log for declared provenance.

## Continuation and resume

The batch size is not a feature scope. A successful import is one checkpoint,
not the end of the analysis. Run `enrichment-status --manifest <latest-manifest>`
to get a read-only bounded JSON summary (exit 0 even when work remains).
Preparation/import also print progress; import nests it under `businessAnalysis`.
Both persist complete `enrichment-progress.json` with the current manifest digest,
all pending/blocker reasons and questions. Stdout omits those potentially large
detail arrays, keeping counts, next IDs and next action.

States are `continue` (pending work), `blocked` (no pending work, explicit unresolved
candidates remain), `ready` (all active candidates meet business readiness), or
`empty` (no active candidates). Counts are active, businessReady, pending and blocked.
They use the exact same readiness checks as the delivery gate; `partial` analysis
with business meaning and questions can be ready. A naming-only or legacy incomplete
analysis remains pending; not-started candidates are never labeled blocked.

While `continue`, prepare with `--pending`, read and interpret the source using the
host model, import against the prepared manifest, set latest-manifest to that import,
and repeat. Do not reapply a fixed offset after an arbitrary domain batch or restart
at the original scan. Keep existing business-ready interpretations unchanged.
When no pending work remains, investigate explicit blocked IDs separately, or run
the delivery gate and render if ready. Do not treat a premature full-manifest gate
failure as a reason to stop processing pending candidates, weaken the gate, or ask
the user to opt into the rest of the assessment.

If interrupted, preserve the latest imported manifest, original inventory/source
paths and progress artifact. Resume from them with `enrichment-status` and
`prepare-enrichment --pending`; rediscovery is unnecessary unless source changed.
This resumes persisted analysis artifacts, not arbitrary crashed publication state.
The engine does not loop over model calls; the host skill performs each cycle.

## Semantic interpretation

The host model reads bodies and follows relevant calls, validation, authorization,
calculations, state changes, persistence, integrations and tests. It updates readable
names, domain and contracts, with `semanticAnalysis` recording a purpose/outcome
summary, evidenceRefs, businessRules and unresolvedQuestions.

Business meaning is the core deliverable. A normal discovery report requires
`semanticAnalysis.businessMeaning`: purpose (business reason), userGoal (who seeks
what), trigger, outcome and basis (observed/inferred), supported by analysis citations.
Infer supported intent from source even when no business prose exists in code;
do not confuse "not explicitly named" with "cannot be analyzed." Mark inference
and uncertainty rather than inventing facts or waiting for human approval to analyze.
Prepared templates contain these fields as invalid blanks for model completion.

Each rule has an ID, condition, outcome, basis (`observed` or `inferred`), rationale
and evidenceRefs drawn from the analysis evidence, itself within the feature evidence.
Observed means logic visible in the cited source, not a runtime guarantee.
Inferred means an interpretation of business intent requiring validation.
Names, HTTP verbs and comments alone cannot establish implemented business rules.
Unknown actors and contracts remain unknown; speculative rules must not become
mandatory behavior contracts. Candidate consolidation remains a human question,
not an automatic identity rewrite.

Analysis status is `complete`, `partial` or `unresolved`. Complete analyses have
no unresolved questions; other statuses require specific questions. Missing
semanticAnalysis means not-started. Empty businessRules means no rule established,
not proof that no rules exist. Status reflects progress through candidate analysis,
not business completeness, evidence verification or approval.
Reports derive `semanticStatus` as inventory-only, incomplete or complete, show
per-status counts, and display readable capabilities, provisional rules and citations.
Schema validity cannot establish readability or interpretation correctness.

## Required business-delivery gate

`parity validate --manifest <final-manifest> --require-business-meaning` and default
`parity report` check all active candidates for structured businessMeaning,
complete/partial analysis, non-placeholder naming/domain and non-declaration-only
behavior contracts. A failed gate returns an artifact error and writes no report,
including on dry-run. Partial analysis can be delivered with substantive business
meaning and specific questions; missing/unresolved meaning cannot. Empty inventories
do not count as business-ready.
If pending candidates remain, that failure requires continuing analysis, not exiting
the workflow after one successful batch. Invoke the final gate when progress is ready.

Legacy/intermediate manifests remain valid for storage and batch processing.
Only an explicit user request for technical-only output permits `report --inventory-only`.
It produces a labeled technical inventory, never an automatic success-shaped fallback.
Normal reports lead with business context and rules, before technical inventory metrics.
These deterministic checks enforce presence and basic readiness, not semantic truth;
the model and independent reviewer still evaluate the explanation against source.

Semantic analysis participates in contract digests, so editing it invalidates a
prior approval. Partial/unresolved analysis cannot earn verified contract credit;
comparison also checks rule conditions/outcomes/bases, including missing analysis
on one side. Legacy manifests remain valid and retain existing comparison behavior.

## Import and independent review

Each proposal records its feature contract digest, a rationale, whitelisted contract
or naming edits, and exact citations covering the union of current and proposed
feature evidence. Citations bind evidence ID, content hash and complete record digest.
No evidence records, feature IDs, verification, confidence, admission, approvals or
statistics can be supplied as edits. All behavior references must resolve within the
resulting feature evidence. Unknown, stale, conflicting and malformed batches fail
before publication. Input objects are not mutated.

Import applies edits to a copied manifest, sets touched features to `needs-review`,
withdraws prior approvals and queues independent human review. Unchanged features
retain their original review state. Approval removal also applies to naming-only
changes to avoid implicit credit for unapproved agent work. Resulting features cannot
earn equivalent or verified gate credit until reviewed through the separate human
workflow; human confirmation still does not upgrade evidence or admission.

The five persisted artifacts are the new manifest, original proposal batch,
review queue, schema-validated import log and enrichment progress. The log binds input, proposal and output
digests, before/after feature digests and engine-derived counts. Outputs use the
existing fresh-directory, staged-publication policy; multi-file transactional recovery
is not provided. Canonical results are deterministic for the same input pair.

Manifest/evidence checks are against stored scan artifacts, not a fresh live-source
rescan. Rerun discovery when repository content changes; imports never claim current
runtime behavior. Provenance is declared and not cryptographically authenticated.
Comprehensive content redaction remains deferred, so do not include secrets in free
text. New-feature proposals, automatic semantic consolidation, precise rule-range
extraction and cross-scan reconciliation remain future work.