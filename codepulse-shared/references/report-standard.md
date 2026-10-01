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

## Compatibility

Keep existing user-facing skill names, report directories, and filename conventions. Focused reports continue under their existing `codepulse-*/reports/` directories. Full reports continue under `codepulse-full/reports/` using `{skill_name}_{currentDate}-report.html`.

The shared `../templates/report-template.html` and `../templates/executive-report-template.html` files define structure and presentation. Existing local templates are migration inputs and must not be treated as separate authorities after migration.
