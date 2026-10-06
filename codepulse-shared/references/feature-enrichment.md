# Persisted Agent Enrichment

Enrichment is an optional, offline, provisional input, not implementation evidence
or an approval. The engine does not call a model. Schema version 1.0 records the
original manifest and inventory digests, declared agent/model/version provenance,
and up to 100 uniquely identified proposals for distinct existing active features.

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

The four persisted artifacts are the new manifest, original proposal batch,
review queue and schema-validated import log. The log binds input, proposal and output
digests, before/after feature digests and engine-derived counts. Outputs use the
existing fresh-directory, staged-publication policy; multi-file transactional recovery
is not provided. Canonical results are deterministic for the same input pair.

Manifest/evidence checks are against stored scan artifacts, not a fresh live-source
rescan. Rerun discovery when repository content changes; imports never claim current
runtime behavior. Provenance is declared and not cryptographically authenticated.
Comprehensive content redaction remains deferred, so do not include secrets in free
text. New-feature proposals, evidence extraction, cross-scan reconciliation and
large-manifest template selection remain future work.