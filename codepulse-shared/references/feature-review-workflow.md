# Feature Review Workflow

This development contract is separate from CodePulse health assessments. Human
feature confirmation does not verify evidence, raise confidence, admit candidates
or prove runtime equivalence. No assessed application code runs in this workflow.

## Review Sequence

1. Validate the manifest and export `parity review-template --manifest INPUT --output NEW_DIRECTORY`.
2. A human reviews the existing evidence and contracts. Remove untouched
   placeholders, choose confirmed/needs-review/rejected/deprecated and fill each
   approval reference. Never substitute an agent proposal for human approval.
3. Optionally edit allowed name/domain/aliases/actors/inputs/outputs/preconditions,
   behaviors and evidence references. References must resolve to existing evidence;
   behavior references must belong to the feature's selected evidence.
4. Run `parity reconcile --manifest INPUT --reviews REVIEW_JSON --output NEW_DIRECTORY --dry-run`.
5. Run again without dry-run to publish a new manifest, queue and audit log.
   Retain the original manifest and review batch for reproducibility.

Exported templates are intentionally invalid as approvals: references are blank.
The batch must have at least one decision. Empty active feature sets have no CLI
template. Template defaults do not change status unless explicitly submitted by
a human with an approval reference. Rejected/deprecated features can be reopened
through a manually authored digest-bound batch, but are omitted from templates.

## Integrity and Limits

Manifest and per-feature contract digests bind the batch to its original input.
Duplicates, unknown features, stale digests, unsupported actions, invalid updates
or dangling references reject the whole logical batch before publication. Input
objects and files are not mutated. Same original inputs produce identical output;
applying an old batch to a modified manifest deliberately fails.

IDs and fingerprints are retained for existing features, including display-label
renames. This does not reconcile identities after rescanning changed source code.
Aliases do not yet drive comparison. Creating evidence, upgrading verification,
confidence changes, exclusion actions and split/merge lineage remain deferred.

Confirmed records receive a newly computed contract approval digest. Reopened,
rejected and deprecated records lose prior approval. Reviewed records with
insufficient admission or evidence verification retain a follow-up queue item.
Confirmation can still have incomplete contracts; comparison independently
requires supported evidence and populated mandatory contracts before equivalence.

Approval references are attestations, not authenticated identities or signatures.
Notes and references are persisted verbatim and must contain no secrets or personal
data. Comprehensive redaction and approval-authority verification are not implemented.
The audit schema records before/after feature and input/review/output digests but
does not independently authenticate a reviewer or validate source-file truth.

Artifact publication is staged but not a multi-file filesystem transaction.
On a write failure, do not consume an incomplete directory. Recovery is deferred.
All artifact inputs are limited to 16 MiB and JSON schemas resolve locally.