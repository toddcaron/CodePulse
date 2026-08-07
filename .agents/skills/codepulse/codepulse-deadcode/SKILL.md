---
name: codepulse-deadcode
description: Performs only the dead code and unused variable portion of the health check. Use this when the user asks for unused code, dead code, obsolete methods, unused variables, unused imports, or cleanup opportunities.
---

# Dead Code Health Check

## Input

Use the entire codebase as the context for this skill. Focus on source files, imports, variables, methods, classes, routes, components, configuration references, and project references.

## Scope

Perform only step 5 from `healthcheck-full`:

- Identify potential dead code and unused variables in the codebase.

Do not perform LOC counting, MFA review, vulnerability analysis, broad code quality review, dependency currency checks, or external access analysis unless those findings directly support dead code identification.

## Analysis Requirements

Look for:

- Unused variables.
- Unused imports.
- Unused methods.
- Unused classes.
- Unreferenced components.
- Dead routes or endpoints.
- Commented-out code blocks.
- Obsolete feature flags.
- Unused configuration keys.
- Project references that appear unused.
- Duplicate implementations where one appears abandoned.

Distinguish between confirmed dead code and suspected dead code. If usage cannot be verified statically, mark it as “Needs confirmation.”

## Shared References

Before generating the assessment, review:

- `.agents/skills/codepulse/references/report-template.html`
- `.agents/skills/codepulse/references/grading-model.md`
- `.agents/skills/codepulse/references/recommendations-library.md`

Requirements:

- Use report-template.html for output formatting.
- Use grading-model.md for scoring.
- Use dead code cleanup recommendations from recommendations-library.md.
`

## Output

Create a focused HTML dead code report.
Filename =  {skill_name}_{currentDate}-report.html
File output path =  .agents/skills/codepulse/reports/

Include:

- Confirmed unused items.
- Suspected unused items.
- Evidence or reference basis.
- Cleanup recommendations.
- Areas requiring manual validation.
- A letter grade from D to A.
- Suggested safe-removal strategy.

