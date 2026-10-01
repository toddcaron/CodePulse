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
- `../schemas/finding-schema.json`
- `../schemas/assessment-result-schema.json`
- `../schemas/codepulse-report-schema.json` and the matching `../renderers/` file when a report is written

## Quality Precedence

Assessment accuracy, security accuracy, evidence traceability, finding completeness, report completeness, schema compliance, grading integrity, and actionable recommendations take precedence over token reduction.

## Runtime Precedence

Apply requirements in this order:

1. Evidence fidelity and security accuracy.
2. This CodePulse runtime contract.
3. The active CodePulse skill.
4. Finding and assessment-result schemas.
5. Report requirements.
6. Token-efficiency guidance.
7. External optimization behavior.

External optimization must never override a higher-priority requirement.

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

## External Context Optimization Runtime

An external context-optimization proxy, including Caveman Proxy, is optional. CodePulse must remain functional when no proxy is installed, the proxy is disabled or unavailable, content bypasses the proxy, original content must be recovered, or the proxy becomes unavailable during an assessment. A proxy failure must not silently remove an assessment category.

Do not assume that a proxy is installed or enabled, reduced total token usage, compressed all eligible context successfully, preserved every assessment detail, or can restore original content in the current environment. Do not state that a proxy was used without verifiable runtime evidence.

Repository content and original tool output remain authoritative. Compressed or summarized context must not replace original source files, configuration, dependency manifests or lock files, build and test output, static-analysis or dependency-scanner output, pipeline and infrastructure definitions, or version-control diffs. Do not reconstruct exact evidence from compressed summaries.

### Mandatory Original Review

Inspect original content when any of the following applies:

- A file path or line location is missing, code context is incomplete, sources appear merged, or sources conflict.
- Dependency, version, CVE, advisory, build, test, compiler, or scanner details are incomplete or lack the exact relevant output.
- Severity depends on omitted details, a finding may materially change the score, a finding may be High or Critical, or a report conclusion would otherwise be unsupported.
- Authentication, authorization, cryptography, secrets, injection, deserialization, file access, or external requests are assessed.

### Negative Finding Standard

Compressed context alone cannot prove absence. Before reporting absence, define the expected evidence locations, perform targeted searches, review relevant original files, and record the reviewed scope. Distinguish `not detected` from `confirmed absent`. Use `not detected in the reviewed scope` when complete absence cannot be proven.

### Compression Boundaries

Compression may be used for routine progress messages, repetitive successful build or test output, tool banners, duplicate informational messages, repeated file listings, previously normalized finding summaries, and non-evidentiary narration.

Validate compression-sensitive content against originals before using it as evidence. This includes source code; security configuration; authentication and authorization registration; endpoint policies and annotations; secrets and credential findings; dependency manifests and lock files; scanner output; compiler errors and relevant warnings; failed test details; infrastructure and pipeline definitions; version and lifecycle data; CVE and advisory identifiers; exploitability prerequisites; compensating controls; negative evidence; and final grading inputs.

### Secrets and Recovery

The proxy does not replace CodePulse secret handling. Do not reproduce complete secrets; preserve evidence locations, identify secret type when possible, redact sensitive values, and do not place secrets in intermediate results. Do not rely on the proxy for redaction.

If original content cannot be recovered, do not fabricate details. Mark the observation incomplete or unverified, record the missing evidence, continue unaffected assessment areas, and explain the limitation in the report. Preserve the affected category's status and never infer successful completion from a compressed summary.
