---
name: codepulse-loc
description: Performs only the lines-of-code portion of the health check. Use this when the user asks for codebase size, total lines of code, LOC count, file counts, or language breakdown.
---

# Lines of Code Health Check

## Input

Use the entire codebase as the context for this skill. Exclude `.md` files, `.gitignore` files, generated files, build output, package caches, binaries, images, and other non-code files.

## Scope

Perform only step 1 from `healthcheck-full`:

- Count the total number of lines of code in the codebase.

Do not perform MFA review, vulnerability analysis, code quality review, dead code detection, dependency currency checks, or external access analysis.

## Analysis Requirements

- Count total lines of code.
- Break down lines of code by language or file type when possible.
- Identify large files or unusually large areas of the codebase.
- Distinguish source code from generated or vendor-managed code when possible.
- State any exclusions used during the count.

## Shared References

Before executing this skill, read and apply:

- `../codepulse-shared/references/runtime-contract.md`
- `../codepulse-shared/references/token-efficiency.md`
- `../codepulse-shared/references/grading.md`
- `../codepulse-shared/references/recommendations-library.md`
- `../codepulse-shared/references/report-standard.md`
- `../codepulse-shared/references/assessment-methodology.md`
- `../codepulse-shared/schemas/finding-schema.json`
- `../codepulse-shared/schemas/assessment-result-schema.json`
- `../codepulse-shared/schemas/codepulse-report-schema.json`

Render with `../codepulse-shared/renderers/html-template.md` after the report object is final.

## Normalized Result

Emit an assessment result using `../codepulse-shared/schemas/assessment-result-schema.json`. Use stable `LOC-*` finding IDs for evidence-backed maintainability observations and include the score, grade, status, summary, limitations, and `metrics.loc`.

## Output

Follow the Output Protocol in `../codepulse-shared/references/report-standard.md`: write `{skill_name}_{currentDate}-result.json` and render `{skill_name}_{currentDate}-report.html`.
File output path = the `reports/` directory beside this `SKILL.md` in the installed `codepulse-loc` skill. Resolve it relative to the skill directory, never relative to the analyzed repository or current working directory.

Include:

- Total lines of code.
- Breakdown by language or file type.
- Notable concentrations of code.
- Any assumptions or exclusions.
- A letter grade from D to A based on codebase size manageability and clarity of organization.
- Actionable recommendations if the codebase appears overly large, disorganized, or difficult to maintain.