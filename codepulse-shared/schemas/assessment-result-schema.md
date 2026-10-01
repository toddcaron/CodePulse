# Assessment Result Schema

Each assessment should emit a versioned result compatible with:

```json
{
  "schemaVersion": "1.0",
  "assessmentName": "",
  "repository": "",
  "assessmentDate": "",
  "score": null,
  "status": "complete",
  "findings": [],
  "summary": "",
  "verificationStatus": "verified-original",
  "sourceRepresentation": "original",
  "evidenceRecoveryRequired": false,
  "evidenceLimitations": []
}
```

## Required Fields

- `schemaVersion`: compatibility version.
- `assessmentName`: stable skill/capability name.
- `repository`: repository or path assessed.
- `assessmentDate`: ISO date or date-time.
- `score`: numeric 0-100 when scoring is possible; `null` when unavailable.
- `status`: one of `complete`, `incomplete`, `failed`, or `unavailable`.
- `findings`: array of finding IDs or normalized finding records.
- `summary`: concise result summary.

## Evidence Provenance

Every new normalized finding includes its own `verificationStatus`, `sourceRepresentation`, `evidenceRecoveryRequired`, and `evidenceLimitations`, as defined in `finding-schema.md`. Assessment results may include the same fields to summarize evidence provenance across the result; the summary must not imply that all evidence is verified when it is mixed.

- `verificationStatus`: one of `verified-original`, `verified-tool-output`, `partially-verified`, `unverified`, or `unavailable`.
- `sourceRepresentation`: one of `original`, `normalized`, `compressed`, or `summarized`.
- `evidenceRecoveryRequired`: boolean; true when original evidence still needs retrieval or review.
- `evidenceLimitations`: array of specific missing evidence or verification limitations; empty when none apply.

Workflow `status` describes assessment completion and remains one of `complete`, `incomplete`, `failed`, or `unavailable`; it is not an evidence-verification status. A confirmed High or Critical finding must not rely only on compressed or summarized content. If original evidence cannot be verified, preserve the limitation and do not claim confirmation.

## Handling Gaps

Use `incomplete` when analysis started but evidence or execution was insufficient. If a workflow was intentionally skipped, use `incomplete` and include `skipReason` plus the affected scope in `summary` or `limitations`, so the skip is explicit without expanding the status enum. Use `failed` when the workflow could not complete because of an execution error. Use `unavailable` when the capability or required evidence does not exist. Never silently omit a category. Do not calculate a complete overall assessment when a required workflow was skipped or otherwise non-complete.

## Optional Fields

`grade`, `category`, `limitations`, `metrics`, `recommendations`, `startedAt`, `completedAt`, `sourceReport`, `skipReason`, `verificationStatus`, `sourceRepresentation`, `evidenceRecoveryRequired`, and `evidenceLimitations` may be included.

## Compatibility

Consumers must accept additive optional fields and preserve unknown fields when forwarding results. Breaking changes require a new major schema version and an explicit compatibility mapping. Finding references must resolve to stable IDs and must not duplicate the same finding during aggregation.
