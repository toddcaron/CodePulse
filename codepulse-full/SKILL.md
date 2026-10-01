---
name: codepulse-full
description: Performs the complete CodePulse application assessment across security, code quality, dead code, dependency lifecycle health, external exposure, and maintainability metrics. Use when the user requests a full application health review, technical due diligence assessment, modernization readiness review, security posture assessment, portfolio evaluation, or comprehensive codebase analysis.
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
- `../codepulse-shared/references/complexity-model.md`
- `../codepulse-shared/schemas/finding-schema.json`
- `../codepulse-shared/schemas/assessment-result-schema.json`
- `../codepulse-shared/schemas/codepulse-report-schema.json`

Render with `../codepulse-shared/renderers/html-template.md` after the report object is final.

## Input and Scope

Use the entire codebase as context. Exclude documentation, generated files, build output, package caches, binaries, images, vendor content, and `.git/` unless required for dependencies, authentication, infrastructure, external access, or deployment evidence. Preserve exact evidence from included manifests and configuration.

## Required Capabilities

Apply the focused workflow for each category:

| Capability | Skill | Weight |
|---|---|---:|
| Lines of code and maintainability indicators | `codepulse-loc` | 5% |
| Security vulnerabilities | `codepulse-vuln` | 32% |
| Code quality | `codepulse-quality` | 26% |
| Dead code | `codepulse-deadcode` | 11% |
| Dependency and framework lifecycle | `codepulse-plm` | 16% |
| External exposure | `codepulse-ext` | 10% |

Use `codepulse-vuln-verbose` only when exhaustive line-level vulnerability analysis is explicitly requested. Do not silently substitute it for the normal security capability.

## Shared Repository Inventory

Run this assessment as one inline orchestration workflow. Do not assume focused skills can invoke one another or suppress their standalone output contracts.

Before category analysis, build one repository inventory containing metadata and exact evidence references for:

- Repository type, languages, frameworks, boundaries, and source roots.
- Entry points, manifests, lock files, configuration, CI/CD, and infrastructure.
- Authentication, authorization, routes/endpoints, data access, and external integrations.
- Available analyzers and exclusions.

Keep the inventory to paths, classifications, versions, commands, and concise metadata. Do not copy complete source files, raw logs, or summarized findings into it. Each capability consumes only its relevant projection and retrieves original content when the inventory is insufficient:

| Capability | Inventory projection |
|---|---|
| `codepulse-loc` | Source roots, file classifications, exclusions |
| `codepulse-vuln` | Authentication, authorization, routes, data access, integrations, manifests, configuration |
| `codepulse-quality` | Source roots, entry points, core paths, analyzer commands and versions |
| `codepulse-deadcode` | Source roots, imports, routes, configuration and project references |
| `codepulse-plm` | Manifests, lock files, runtimes, containers, build and deployment configuration |
| `codepulse-ext` | Routes, authentication, CORS, ingress, host/port configuration, external integrations |

Inventory reuse reduces duplicate discovery only. It never proves a negative finding, replaces mandatory original review, or replaces exact evidence in normalized findings.

## Orchestration Procedure

1. Build the shared repository inventory.
2. Run the six capability workflows inline, using the relevant inventory projection, targeted searches, and original-content reads only where required by the active capability or evidence rule. For `codepulse-quality`, execute an available complexity analyzer without modifying the analyzed repository before manually estimating complexity. Use `lizard` for multi-language Cyclomatic Complexity when it is available and suitable for the detected source types; otherwise use the ecosystem-specific analyzer defined by `complexity-model.md`. Record the analyzer name and version, command, scope, exclusions, and coverage gaps in `metrics.complexity`. Use a manual estimate only when no suitable analyzer can run, mark affected findings `partially-verified`, and record `manual-estimate` with the reason in the result limitations.
3. Collect one normalized assessment result from each capability. Each result must include `assessmentName`, `repository`, `assessmentDate`, `score`, `status`, `findings`, and `summary`. Record `complete`, `incomplete`, `failed`, or `unavailable` for every capability. Represent an intentionally skipped capability as `incomplete` with an explicit `skipReason` and affected scope. Never infer successful completion from a compressed summary.
4. Normalize every finding with stable `id`, category, severity where applicable, title, exact evidence, impact, recommendation, `verificationStatus`, `sourceRepresentation`, `evidenceRecoveryRequired`, and `evidenceLimitations`. Embed each complete normalized finding object in its assessment result; never emit only a finding ID in `findings`.
5. Validate every result and finding against the shared schemas. Validate evidence references against available original repository content or original tool output. Reject or mark findings incomplete when required evidence, impact, recommendation, or provenance is missing. Inspect original content whenever required by the runtime contract; do not reconstruct exact evidence from summaries.
6. Preserve exact paths, lines, commands, versions, URLs, CVEs, errors, and configuration values. Confirmed High and Critical findings must be verified against original content and must not rely only on compressed or summarized context. If originals cannot be recovered, retain the observation as unverified or incomplete and record the limitation rather than claiming confirmation.
7. Merge results by stable finding ID only after validation. Deduplicate repeated findings without deleting distinct evidence; cross-reference reused findings. Reopen original evidence to resolve conflicting findings or sources.
8. Calculate the weighted overall score and assign the overall letter grade only after evidence and finding validation. Select recommendations after deduplication, using stable IDs to reference complete findings rather than repeating evidence. Do not present the overall assessment as complete when a required capability is incomplete, failed, intentionally skipped, or unavailable; explain the effect on score and coverage.
9. Assemble one `codepulse-report-schema.json` object (`reportType: "detailed"`) only from validated normalized results, set `overall.complete` to false when any capability is not `complete`, and render the final detailed HTML report once the report object is final. Preserve each capability status, evidence limitations, and required report sections.

## Required Report Sections

The final report must contain:

1. Executive Summary
2. Assessment Dashboard
3. Overall Grade
4. Assessment Methodology
5. Security Assessment
6. Code Quality Assessment
7. Dead Code Assessment
8. Dependency & Framework Assessment
9. External Exposure Assessment
10. Codebase Metrics
11. Top Risks
12. Recommendations
13. Modernization Opportunities
14. Conclusion

Include category scores and grades, normalized finding IDs, limitations, incomplete capabilities, and exact evidence where applicable. The Code Quality Assessment must include the Cyclomatic, Cognitive, and Accidental Complexity breakdown defined in the shared complexity model.

## Aggregation Rules

- Critical recommendations precede High, lifecycle, exposure, quality, technical debt, dead code, and general best-practice actions.
- Preserve category-specific findings even when a category has no findings; report the evidence and limitation supporting that conclusion.
- A no-finding result must document reviewed evidence scope and targeted original-content searches; compressed context alone cannot support a claim of absence.
- A proxy's presence, use, successful compression, token savings, or ability to restore originals must be supported by verifiable runtime evidence. Otherwise record the state as unknown and proceed without relying on the proxy.
- Use the shared recommendation priority rules and existing recommendation library where applicable.
- Executive content may summarize detailed findings, but must not remove required report sections or evidence from detailed findings.

## Success Criteria

The assessment answers whether the application is healthy, secure, maintainable, current, externally exposed, and in need of modernization investment. It retains all six defined category areas and makes incomplete or failed analysis visible.

## Output

Follow the Output Protocol in `../codepulse-shared/references/report-standard.md`: write `{skill_name}_{currentDate}-result.json` and render one complete `{skill_name}_{currentDate}-report.html`.

Path: the `reports/` directory beside this `SKILL.md` in the installed `codepulse-full` skill. Resolve it relative to the skill directory, never relative to the analyzed repository or current working directory.
