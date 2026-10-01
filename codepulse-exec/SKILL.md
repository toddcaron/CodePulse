---
name: codepulse-exec
description: Transforms an existing CodePulse JSON result into a concise executive-level application health summary. Use when the audience is leadership, management, governance teams, architecture review boards, portfolio managers, CIOs, CTOs, VPs, directors, or non-technical stakeholders. Focus on business risk, modernization readiness, security posture, maintainability, operational risk, and investment priorities rather than detailed technical findings.
---

# CodePulse Executive Summary

## Purpose

CodePulse Executive Summary converts a detailed CodePulse result into an executive-ready application health scorecard.

This skill is intended for leadership audiences that need a rapid understanding of:

- Overall application health
- Business risk
- Security posture
- Technical debt
- Modernization readiness
- Operational concerns
- Investment priorities

The executive summary should help leadership answer:

1. Is this application healthy?
2. Is the application secure?
3. How much risk does it present?
4. Does it require investment?
5. What actions should be prioritized?

This skill summarizes findings rather than repeating them.

---

## Input

The only accepted input is a detailed CodePulse result file, `{skill_name}_{currentDate}-result.json`, conforming to `../codepulse-shared/schemas/codepulse-report-schema.json` with `reportType: "detailed"` and `schemaVersion: "2.0"`. The user provides its path; if they don't, prompt for one. Do not parse HTML or Markdown reports. If the file is missing, invalid, or a different schema version, stop and ask the user to rerun the source assessment.

Review all available:

- Executive summaries
- Findings
- Risk ratings
- Grades
- Recommendations
- Metrics
- Vulnerability summaries
- Dependency assessments
- Quality assessments
- Exposure assessments

Do not perform a new code analysis unless explicitly requested.

Assume the detailed result already contains the authoritative findings.

---

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
- `../codepulse-shared/schemas/finding-schema.json`
- `../codepulse-shared/schemas/assessment-result-schema.json`
- `../codepulse-shared/schemas/codepulse-report-schema.json`

Render with `../codepulse-shared/renderers/executive-summary-template.md` after the executive object is final. Do not rerun code analysis unless explicitly requested.

---

## Executive Reporting Principles

### Focus On

Translate technical findings into business outcomes.

Focus on:

- Business risk
- Security posture
- Supportability
- Operational stability
- Technical debt
- Modernization readiness
- Future investment requirements

Summarize trends and patterns rather than individual findings.

---

### Avoid

Do not include:

- File names
- Source code
- Line numbers
- Configuration details
- Individual vulnerability lists
- Detailed implementation findings
- Excessive technical language

Do not repeat every finding from the assessment.

Only include details that materially affect business decisions.

---

## Executive Health Categories

Evaluate and summarize the application using the following categories.

### Security Posture

Assess:

- Overall risk level
- Critical security concerns
- Authentication maturity
- Vulnerability profile

Assign one of:

```text
Strong
Acceptable
Needs Attention
High Risk
```

---

### Technology Health

Assess:

- Framework currency
- Dependency health
- Platform supportability
- Lifecycle concerns

Assign one of:

```text
Modern
Current
Aging
Legacy
```

---

### Maintainability

Assess:

- Technical debt
- Code quality
- Supportability
- Ease of enhancement

Assign one of:

```text
Excellent
Manageable
Challenging
Poor
```

---

### Operational Risk

Assess:

- Application stability
- Support burden
- External exposure
- Security operations concerns

Assign one of:

```text
Low
Moderate
High
Critical
```

---

### Modernization Readiness

Assess:

- Upgrade complexity
- Architectural constraints
- Legacy dependency concerns
- Future scalability

Assign one of:

```text
Ready
Requires Planning
Significant Investment Required
Major Modernization Recommended
```

---

## Executive Dashboard

Create a dashboard section containing:

- Application Name
- Assessment Date
- Overall CodePulse Grade
- Security Posture
- Technology Health
- Maintainability
- Operational Risk
- Modernization Readiness

Use concise visual indicators whenever possible.

Examples:

```text
Security Posture: Needs Attention
Technology Health: Aging
Operational Risk: Moderate
```

---

## Application Snapshot

Provide a concise summary.

Maximum length:

- Two short paragraphs

Describe:

- Overall application condition
- Primary concerns
- General business outlook

The summary should be understandable by non-technical stakeholders.

---

## Top Risks

Identify only the most important risks.

Maximum:

- 3 to 5 items

For each risk provide:

- Risk
- Business Impact
- Priority

Example:

```text
Risk:
Unsupported Framework Components

Business Impact:
Increased security and support risk. Future enhancements may become more costly.

Priority:
High
```

Focus on business impact rather than technical implementation.

---

## Strengths

Identify the most important positive observations.

Maximum:

- 3 to 5 items

Examples:

- Strong authentication controls
- Modern technology stack
- Low security risk profile
- Well-maintained codebase
- Limited technical debt

---

## Investment Priorities

Identify the most valuable areas for future investment.

Examples:

- Security remediation
- MFA expansion
- Dependency upgrades
- Platform modernization
- Technical debt reduction
- Architecture improvements
- Application rationalization

For each priority explain:

- Why it matters
- Expected business benefit

---

## Modernization Outlook

Assess:

- Current modernization readiness
- Major technical blockers
- Future investment needs

Assign complexity:

```text
Low
Medium
High
Very High
```

Provide:

- Complexity assessment
- Key modernization concerns
- Recommended next steps

---

## Executive Recommendation

Conclude with one of the following recommendations:

```text
Continue Current Investment
Monitor Closely
Prioritize Improvements
Modernization Recommended
Immediate Remediation Required
```

Provide a brief rationale.

The recommendation should clearly communicate the level of management attention required.

---

## Normalized Input

Preserve stable finding IDs in `executive.topRisks[].findingIds` when summarizing risks; do not rerun analysis unless explicitly requested.

## Output Format

Build a `codepulse-report-schema.json` object with `reportType: "executive"`, `skillName: "codepulse-exec"`, `sourceReport` set to the input path, and the `executive` block populated from the sections below. When the source result does not contain a complete assessment for a dashboard category (for example, a focused `codepulse-quality` result has no security data), set that rating to `Not Assessed` and record the gap in `limitations`; never infer a rating. Follow the Output Protocol in `../codepulse-shared/references/report-standard.md`: write `{skill_name}_{currentDate}-result.json` and render `{skill_name}_{currentDate}-report.html` with the executive renderer.

File output path =  codepulse-exec/reports/

The report should be suitable for:

- CIO Reviews
- CTO Reviews
- VP Engineering Updates
- Architecture Review Boards
- Governance Committees
- Portfolio Reviews
- Technology Modernization Reviews
- Application Rationalization Programs
- M&A Technology Assessments

Use sections in the following order:

1. Executive Dashboard
2. Application Snapshot
3. Top Risks
4. Strengths
5. Investment Priorities
6. Modernization Outlook
7. Executive Recommendation

---