# CodePulse Report Standard

## Detailed Reports

Detailed reports should include, when applicable:

1. Executive Summary
2. Assessment Dashboard
3. Overall Grade
4. Assessment Methodology
5. Category assessments
6. Codebase metrics
7. Top risks
8. Recommendations
9. Modernization opportunities
10. Conclusion

Findings must retain evidence, impact, severity, recommendation, and stable IDs. State assessment limitations and unavailable evidence.

## Executive Reports

Executive reports summarize overall posture, business impact, top risks, modernization readiness, strengths, and prioritized investment actions. Do not repeat detailed source code, file names, line numbers, or every finding unless materially needed for a decision.

## Output Protocol

Data and presentation are separate. `../schemas/codepulse-report-schema.json` defines all report data; `../renderers/*.md` define presentation. Every skill that writes a report:

1. Builds one report object conforming to `../schemas/codepulse-report-schema.json` (`reportType: "detailed"`, or `"executive"` for `codepulse-exec`). Each assessment result conforms to `../schemas/assessment-result-schema.json` and embeds complete finding objects; each finding conforms to `../schemas/finding-schema.json`. Finding IDs may be used only as cross-references outside `assessments[].findings`.
2. Validates the object against the schemas. Fix missing required fields from original evidence, or mark the finding or assessment incomplete with the limitation recorded. Do not invent values to satisfy the schema.
3. Writes the object as `{skill_name}_{currentDate}-result.json` to the skill's `reports/` directory.
4. Renders the object to `{skill_name}_{currentDate}-report.html` in the same directory using `../renderers/html-template.md` (detailed) or `../renderers/executive-summary-template.md` (executive). When the user explicitly requests Markdown, render `{skill_name}_{currentDate}-report.md` using `../renderers/markdown-template.md` instead.

Read the renderer only after the report object is final. Rendered reports contain no data that is absent from the JSON.

## Compatibility

Keep existing user-facing skill names, report directories, and filename conventions. Focused reports continue under their existing `codepulse-*/reports/` directories. Full reports continue under `codepulse-full/reports/` using `{skill_name}_{currentDate}-report.html`.

Schema version is `2.0`. Version `1.0` results (Markdown schemas, optional provenance fields) are not accepted; rerun the assessment to produce a `2.0` result.
