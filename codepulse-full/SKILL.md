---
name: codepulse-full
description: Performs the complete CodePulse application assessment across security, authentication, code quality, dead code, dependency lifecycle health, external exposure, and maintainability metrics. Use when the user requests a full application health review, technical due diligence assessment, modernization readiness review, security posture assessment, portfolio evaluation, or comprehensive codebase analysis.
---

# CodePulse Full Assessment

## Purpose

Orchestrate the complete CodePulse assessment and produce one unified, evidence-traceable report. Focused skills own category-specific analysis; this skill owns capability selection, result validation, aggregation, deduplication, scoring, and final report assembly.

## Shared References

Before executing this skill, read and apply:

- `../codepulse-shared/references/runtime-contract.md`
- `../codepulse-shared/references/token-efficiency.md`
- `../codepulse-shared/references/grading.md`
- `../codepulse-shared/references/severity.md`
- `../codepulse-shared/references/recommendation-priority.md`
- `../codepulse-shared/references/recommendations-library.md`
- `../codepulse-shared/references/report-standard.md`
- `../codepulse-shared/references/assessment-methodology.md`
- `../codepulse-shared/schemas/finding-schema.md`
- `../codepulse-shared/schemas/assessment-result-schema.md`
- `../codepulse-shared/templates/assessment-output-template.md`

Use `../codepulse-shared/templates/report-template.html` as the detailed report presentation template.

## Input and Scope

Use the entire codebase as context. Exclude documentation, generated files, build output, package caches, binaries, images, vendor content, and `.git/` unless required for dependencies, authentication, infrastructure, external access, or deployment evidence. Preserve exact evidence from included manifests and configuration.

## Required Capabilities

Apply the focused workflow for each category:

| Capability | Skill | Weight |
|---|---|---:|
| Lines of code and maintainability indicators | `codepulse-loc` | 5% |
| Authentication and MFA | `codepulse-mfa` | 5% |
| Security vulnerabilities | `codepulse-vuln` | 30% |
| Code quality | `codepulse-quality` | 25% |
| Dead code | `codepulse-deadcode` | 10% |
| Dependency and framework lifecycle | `codepulse-plm` | 15% |
| External exposure | `codepulse-ext` | 10% |

Use `codepulse-vuln-verbose` only when exhaustive line-level vulnerability analysis is explicitly requested. Do not silently substitute it for the normal security capability.

## Orchestration Procedure

1. Detect repository type, languages, frameworks, boundaries, entry points, manifests, configuration, CI/CD, and infrastructure.
2. Select the seven required capabilities and apply their focused workflows. Reuse repository metadata and evidence between capabilities.
3. Collect one normalized assessment result from each capability. Each result must include `assessmentName`, `repository`, `assessmentDate`, `score`, `status`, `findings`, and `summary`.
4. Validate every finding against the shared finding schema. Reject or mark findings incomplete when required evidence, impact, or recommendation is missing.
5. Preserve exact paths, lines, commands, versions, URLs, CVEs, errors, and configuration values.
6. Merge results by stable finding ID. Cross-reference repeated findings instead of duplicating them.
7. Calculate the weighted overall score using the shared grading standard and assign the overall letter grade.
8. Record every capability as `complete`, `incomplete`, `failed`, or `unavailable`. Include the reason and affected scope for every non-complete result; never silently omit a category.
9. Generate the final detailed HTML report using the existing report structure and shared report standard.

## Required Report Sections

The final report must contain:

1. Executive Summary
2. Assessment Dashboard
3. Overall Grade
4. Assessment Methodology
5. Security Assessment
6. MFA Assessment
7. Code Quality Assessment
8. Dead Code Assessment
9. Dependency & Framework Assessment
10. External Exposure Assessment
11. Codebase Metrics
12. Top Risks
13. Recommendations
14. Modernization Opportunities
15. Conclusion

Include category scores and grades, normalized finding IDs, limitations, incomplete capabilities, and exact evidence where applicable.

## Aggregation Rules

- Critical recommendations precede High, authentication/MFA, lifecycle, exposure, quality, technical debt, dead code, and general best-practice actions.
- Preserve category-specific findings even when a category has no findings; report the evidence and limitation supporting that conclusion.
- Use the shared recommendation priority rules and existing recommendation library where applicable.
- Executive content may summarize detailed findings, but must not remove required report sections or evidence from detailed findings.

## Success Criteria

The assessment answers whether the application is healthy, secure, maintainable, current, externally exposed, and in need of modernization investment. It retains all current category coverage and makes incomplete or failed analysis visible.

## Output

Output one complete HTML report.

Filename: `{skill_name}_{currentDate}-report.html`

Path: `codepulse-full/reports/`
