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
- `../codepulse-shared/schemas/finding-schema.md`
- `../codepulse-shared/schemas/assessment-result-schema.md`

Use `../codepulse-shared/templates/report-template.html` for the detailed report presentation.

## Normalized Result

Emit an assessment result using `../codepulse-shared/schemas/assessment-result-schema.md`. Use stable `LOC-*` finding IDs for evidence-backed maintainability observations and include the score, grade, status, summary, and limitations.

## Output

Create a focused HTML report section for lines of code only.
File output path =  codepulse-loc/reports/

Include:

- Total lines of code.
- Breakdown by language or file type.
- Notable concentrations of code.
- Any assumptions or exclusions.
- A letter grade from D to A based on codebase size manageability and clarity of organization.
- Actionable recommendations if the codebase appears overly large, disorganized, or difficult to maintain.