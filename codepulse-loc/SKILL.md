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

Before generating the assessment, review:

- `references/report-template.html`
- `references/grading-model.md`

Requirements:

- Use report-template.html for formatting.
- Use grading-model.md when assigning maintainability grades related to codebase size and organization.

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