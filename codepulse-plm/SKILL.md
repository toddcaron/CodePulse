---
name: codepulse-plm
description: Performs only the outdated framework, library, and dependency lifecycle portion of the health check. Use this when the user asks for PLM issues, outdated dependencies, unsupported frameworks, package currency, runtime versions, or library upgrade risks.
---

# Framework and Dependency Lifecycle Health Check

## Input

Use the entire codebase as the context for this skill. Focus on dependency manifest files, lock files, project files, package references, runtime configuration, framework versions, container files, build files, and deployment configuration.

## Scope

Perform only step 6 from `healthcheck-full`:

- Check for outdated frameworks and libraries to ensure the codebase is using up-to-date dependencies.

Do not perform LOC counting, MFA review, vulnerability analysis, code quality review, dead code detection, or external access analysis unless those findings directly relate to dependency lifecycle risk.

## Analysis Requirements

Look for:

- Outdated frameworks.
- Unsupported runtime versions.
- Old package versions.
- Deprecated libraries.
- Package versions with known upgrade pressure.
- Unpinned or floating dependency versions.
- Inconsistent package versions across projects.
- Legacy framework usage.
- Build or deployment dependencies that may be out of support.

When possible, categorize each item as:

- Current.
- Update recommended.
- Upgrade required.
- Potentially unsupported.
- Needs verification.

## Shared References

Before generating the assessment, review:

- `references/report-template.html`
- `references/grading-model.md`
- `references/severity-ratings.md`
- `references/recommendations-library.md`

Requirements:

- Use report-template.html for formatting.
- Use severity-ratings.md when evaluating framework, runtime, or dependency risks.
- Use recommendations-library.md for upgrade guidance.
- Use grading-model.md for scoring.

## Output

Create a focused HTML dependency lifecycle report.
File output path =  codepulse-plm/reports/

Include:

- Summary of framework and library health.
- Outdated or potentially unsupported components.
- Upgrade risk.
- Recommended upgrade path.
- A letter grade from D to A.
- Prioritized remediation recommendations.