# Assessment Result

- Schema version: `1.0`
- Assessment: `{assessmentName}`
- Repository: `{repository}`
- Date: `{assessmentDate}`
- Status: `{complete|incomplete|failed|unavailable}`
- Score: `{0-100 or unavailable}`
- Grade: `{A-D or unavailable}`

## Summary

{summary}

## Findings

Each normalized finding includes the following provenance fields in addition to the finding fields defined by `finding-schema.md`:

```json
{
	"findingId": "{stable finding id}",
	"category": "{category}",
	"severity": "{severity}",
	"title": "{title}",
	"evidence": [],
	"impact": "{impact}",
	"recommendation": "{recommendation}",
	"verificationStatus": "{verified-original|verified-tool-output|partially-verified|unverified|unavailable}",
	"sourceRepresentation": "{original|normalized|compressed|summarized}",
	"evidenceRecoveryRequired": false,
	"evidenceLimitations": []
}
```

`findingId` maps to the stable `id` in the finding schema. Preserve exact evidence references and include concrete limitations; do not use a compressed summary as a substitute for evidence.

## Limitations

{limitations or None reported}
