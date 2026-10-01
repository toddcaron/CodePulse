---
name: codepulse-quality
description: Performs only the code quality portion of the health check. Use this when the user asks for code smells, readability complexity (cyclomatic, cognitive, accidental), maintainability, readability, standards adherence, or refactoring opportunities.
---

# Code Quality Health Check

## Input

Use the entire codebase as the context for this skill. Focus on source files, structure, naming, duplication, error handling, complexity, architecture consistency, and maintainability.

## Scope

Perform only the Code Quality capability of `codepulse-full`:

- Evaluate the code quality by checking for code smells, readability complexity, and adherence to coding standards.

In this skill, **complexity means human readability and maintainability**, not the inherent difficulty of the problem. Apply `../codepulse-shared/references/complexity-model.md` for definitions, measurement, thresholds, and scoring.

Do not perform LOC counting, MFA review, vulnerability analysis, dead code detection, dependency currency checks, or external access analysis unless those findings directly affect maintainability.

## Analysis Requirements

### Readability Complexity

Evaluate each measure using the shared complexity model:

- **Cyclomatic Complexity**: independent paths per function. Measure with an available analyzer; otherwise estimate manually and mark findings `partially-verified`.
- **Cognitive Complexity**: how hard a function is to read, driven by nesting, breaks in linear flow, and mixed boolean logic.
- **Accidental Complexity**: complexity the problem does not require. Apply the inherent-vs-accidental test and state the simpler alternative for every accidental finding. Do not deduct for inherent domain complexity.

Record the measurement source, distribution (median, 90th percentile, max), threshold breaches, and centrality-weighted hotspots for each measure.

### Other Quality Signals

- Long methods or large classes.
- Inconsistent naming.
- Poor separation of concerns.
- Weak error handling.
- Inconsistent logging.
- Missing comments where intent is unclear.
- Overly broad exception handling.
- Inconsistent project structure.
- Violations of common language or framework conventions.

Score duplication, repeated business rules, tight coupling, and hardcoded values as Accidental Complexity indicators; do not count them twice.

## Shared References

Before executing this skill, read and apply:

- `../codepulse-shared/references/runtime-contract.md`
- `../codepulse-shared/references/token-efficiency.md`
- `../codepulse-shared/references/grading.md`
- `../codepulse-shared/references/recommendation-priority.md`
- `../codepulse-shared/references/recommendations-library.md`
- `../codepulse-shared/references/report-standard.md`
- `../codepulse-shared/references/assessment-methodology.md`
- `../codepulse-shared/references/complexity-model.md`
- `../codepulse-shared/schemas/finding-schema.md`
- `../codepulse-shared/schemas/assessment-result-schema.md`

Use `../codepulse-shared/templates/report-template.html` for the detailed report presentation and emit stable quality finding IDs.

## Normalized Result

Emit an assessment result using `../codepulse-shared/schemas/assessment-result-schema.md`. Use stable `QUAL-CYC-*`, `QUAL-COG-*`, and `QUAL-ACC-*` IDs for complexity findings and `QUAL-*` for other evidence-backed quality observations. Include score, grade, status, summary, complexity component scores, measurement sources, and limitations.

## Output

Create a focused HTML code quality report.
File output path =  codepulse-quality/reports/

Include:

- Summary of maintainability posture.
- Key code smells.
- Complexity breakdown: a table per measure (Cyclomatic, Cognitive, Accidental) with measurement source, median, 90th percentile, max, threshold breaches, and component score.
- Top complexity hotspots with file, function, and line.
- Accidental complexity findings, each with its inherent-vs-accidental rationale and simpler alternative.
- Standards or consistency issues.
- Refactoring opportunities.
- A letter grade from D to A.
- Actionable recommendations prioritized by impact.