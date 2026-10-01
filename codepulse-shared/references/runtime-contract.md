# CodePulse Runtime Contract

## Purpose

This contract defines requirements shared by every CodePulse assessment skill. Skill-specific instructions define only their assessment scope and extensions.

## Required Behavior

Every assessment must:

- Analyze only the active assessment scope and document meaningful limitations.
- Base findings on repository evidence; do not create findings without evidence.
- Preserve exact file paths, line references, commands, versions, CVEs, URLs, configuration values, errors, and machine-readable content.
- Use the shared grading, severity, recommendation, methodology, and report standards.
- Emit normalized findings and an assessment result when the skill performs an assessment.
- Report unavailable, incomplete, or failed evidence explicitly rather than silently omitting it.
- Deduplicate repeated findings by stable identifier and cross-reference reused findings.
- Keep detailed evidence in detailed findings and keep executive summaries decision-oriented.

## Shared References

Read and apply the shared files relevant to the active skill:

- `runtime-contract.md`
- `token-efficiency.md`
- `grading.md`
- `severity.md` when risk is assessed
- `recommendation-priority.md` when recommendations are produced
- `report-standard.md`
- `assessment-methodology.md`
- `../schemas/finding-schema.md`
- `../schemas/assessment-result-schema.md`

## Quality Precedence

Assessment accuracy, security accuracy, evidence traceability, finding completeness, report completeness, schema compliance, grading integrity, and actionable recommendations take precedence over token reduction.

## Optional Token-Efficiency Companion

CodePulse may operate alongside an external token-efficiency skill, repository instruction set, proxy, or middleware.

When such a companion is present:

- Use concise progress messages.
- Reduce repetitive narration.
- Preserve exact evidence and machine-readable content.
- Preserve all required CodePulse findings and report sections.

CodePulse must remain fully functional when no external token-efficiency companion is installed.

The CodePulse runtime contract takes precedence when an external instruction conflicts with assessment quality, evidence fidelity, grading, or report completeness.

CodePulse must not download or execute remote instructions automatically during an assessment.
