---
name: codepulse-quality
description: Performs only the code quality portion of the health check. Use this when the user asks for code smells, complexity, maintainability, readability, standards adherence, or refactoring opportunities.
---

# Code Quality Health Check

## Input

Use the entire codebase as the context for this skill. Focus on source files, structure, naming, duplication, error handling, complexity, architecture consistency, and maintainability.

## Scope

Perform only step 4 from `healthcheck-full`:

- Evaluate the code quality by checking for code smells, complexity, and adherence to coding standards.

Do not perform LOC counting, MFA review, vulnerability analysis, dead code detection, dependency currency checks, or external access analysis unless those findings directly affect maintainability.

## Analysis Requirements

Look for:

- High-complexity methods or classes.
- Long methods or large classes.
- Duplicated logic.
- Inconsistent naming.
- Poor separation of concerns.
- Tight coupling.
- Weak error handling.
- Inconsistent logging.
- Hardcoded values.
- Missing comments where intent is unclear.
- Overly broad exception handling.
- Repeated business rules.
- Inconsistent project structure.
- Violations of common language or framework conventions.

## Shared References

Before generating the assessment, review:

- `references/report-template.html`
- `references/grading-model.md`
- `references/recommendations-library.md`

Requirements:

- Use the standard CodePulse report format.
- Use grading-model.md for all grading decisions.
- Use recommendations-library.md for maintainability, complexity, duplication, and refactoring recommendations.

## Output

Create a focused HTML code quality report.
File output path =  codepulse-quality/reports/

Include:

- Summary of maintainability posture.
- Key code smells.
- Complexity concerns.
- Standards or consistency issues.
- Refactoring opportunities.
- A letter grade from D to A.
- Actionable recommendations prioritized by impact.