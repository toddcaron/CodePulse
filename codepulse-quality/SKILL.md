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

- **Cyclomatic Complexity**: independent paths per function. For supported source types, first use the bundled `../codepulse-shared/tools/lizard/lizard.py` according to the shared complexity model. Run it with an available Python 3.8+ interpreter, verify its version, request CSV output, and process function records after excluding `*global*` pseudo-functions. Record `lizard 1.24.0`, exact command, source roots, exclusions, function count, and coverage gaps in `metrics.complexity`. Use an ecosystem-specific analyzer, then a manual estimate marked `partially-verified`, only when the bundled analyzer cannot supply the measure.
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
- `../codepulse-shared/tools/lizard/README.md`
- `../codepulse-shared/schemas/finding-schema.json`
- `../codepulse-shared/schemas/assessment-result-schema.json`
- `../codepulse-shared/schemas/codepulse-report-schema.json`

Render with `../codepulse-shared/renderers/html-template.md` after the report object is final and emit stable quality finding IDs.

## Normalized Result

Emit an assessment result using `../codepulse-shared/schemas/assessment-result-schema.json`. Use stable `QUAL-CYC-*`, `QUAL-COG-*`, and `QUAL-ACC-*` IDs for complexity findings and `QUAL-*` for other evidence-backed quality observations. Include score, grade, status, summary, limitations, and `metrics.complexity` (component scores, measurement sources, hotspots).

## Output

Follow the Output Protocol in `../codepulse-shared/references/report-standard.md`: write `{skill_name}_{currentDate}-result.json` and render `{skill_name}_{currentDate}-report.html`.
File output path = the `reports/` directory beside this `SKILL.md` in the installed `codepulse-quality` skill. Resolve it relative to the skill directory, never relative to the analyzed repository or current working directory.

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