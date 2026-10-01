---
name: codepulse-exec
description: Transforms an existing CodePulse assessment report into a concise executive-level application health summary. Use when the audience is leadership, management, governance teams, architecture review boards, portfolio managers, CIOs, CTOs, VPs, directors, or non-technical stakeholders. Focus on business risk, modernization readiness, security posture, maintainability, operational risk, and investment priorities rather than detailed technical findings.
---

# CodePulse Executive Summary

## Purpose

CodePulse Executive Summary converts a detailed CodePulse assessment report into an executive-ready application health scorecard.

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

Use an existing CodePulse HTML report as the primary source. The user needs to provide the full report file path. If they don't provide a path, you will prompt for one.

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

Assume the detailed report already contains the authoritative findings.

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
- `../codepulse-shared/schemas/finding-schema.md`
- `../codepulse-shared/schemas/assessment-result-schema.md`
- `../codepulse-shared/templates/report-template.html`
- `../codepulse-shared/templates/executive-report-template.html`
- `references/executive-scorecard-template.html`

Use the shared contract for interpretation and preserve the local scorecard as the executive presentation extension. Do not rerun code analysis unless explicitly requested.

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

Prefer a normalized assessment result or a detailed CodePulse report conforming to `../codepulse-shared/schemas/assessment-result-schema.md`. Preserve stable finding IDs when summarizing risks and recommendations; do not rerun analysis unless explicitly requested.

## Output Format

Generate a concise executive HTML report that matches the CodePulse executive scorecard template:
references/executive-scorecard-template.html

Filename =  {skill_name}_{currentDate}-report.html
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