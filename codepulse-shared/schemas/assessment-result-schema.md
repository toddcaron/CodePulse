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
  "summary": ""
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

## Handling Gaps

Use `incomplete` when analysis started but evidence or execution was insufficient. Use `failed` when the workflow could not complete because of an execution error. Use `unavailable` when the capability or required evidence does not exist. Include the reason and affected scope in `summary` or an optional `limitations` field. Never silently omit a category.

## Optional Fields

`grade`, `category`, `limitations`, `metrics`, `recommendations`, `startedAt`, `completedAt`, and `sourceReport` may be included.

## Compatibility

Consumers must accept additive optional fields and preserve unknown fields when forwarding results. Breaking changes require a new major schema version and an explicit compatibility mapping. Finding references must resolve to stable IDs and must not duplicate the same finding during aggregation.
