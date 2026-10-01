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

Distinguish between valid comments and commented-out code that may indicate dead code. Mark commented-out code as “Needs confirmation” unless it is clearly obsolete. Make sure to look for comments via the comment syntax appropriate for the language (e.g., `//` for JavaScript, `#` for Python, '///' for XML, `/* */` for block comments).

## Shared References

Before executing this skill, read and apply:

- `../codepulse-shared/references/runtime-contract.md`
- `../codepulse-shared/references/token-efficiency.md`
- `../codepulse-shared/references/grading.md`
- `../codepulse-shared/references/recommendation-priority.md`
- `../codepulse-shared/references/recommendations-library.md`
- `../codepulse-shared/references/report-standard.md`
- `../codepulse-shared/references/assessment-methodology.md`
- `../codepulse-shared/schemas/finding-schema.json`
- `../codepulse-shared/schemas/assessment-result-schema.json`
- `../codepulse-shared/schemas/codepulse-report-schema.json`

Render with `../codepulse-shared/renderers/html-template.md` after the report object is final. Preserve confirmed versus suspected dead-code distinctions and stable finding IDs.

## Normalized Result

Emit an assessment result using `../codepulse-shared/schemas/assessment-result-schema.json`. Use stable `DEAD-*` finding IDs and mark each observation as confirmed, potential, or requiring confirmation without overstating static evidence.

## Output

Follow the Output Protocol in `../codepulse-shared/references/report-standard.md`: write `{skill_name}_{currentDate}-result.json` and render `{skill_name}_{currentDate}-report.html`.
File output path =  codepulse-deadcode/reports/

Include:

- Confirmed unused items.
- Suspected unused items.
- Evidence or reference basis.
- Cleanup recommendations.
- Areas requiring manual validation.
- A letter grade from D to A.
- Suggested safe-removal strategy.

