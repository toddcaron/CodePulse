---
name: codepulse-shared
description: Shared runtime contract, grading standards, severity ratings, recommendations library, report standards, schemas, and templates for all CodePulse assessment skills. Required companion for any CodePulse skill installation.
---

# CodePulse Shared Runtime and Standards

## Purpose

`codepulse-shared` provides the shared runtime contract, grading methodology, severity ratings, recommendations library, report standards, schemas, and templates consumed by all CodePulse assessment skills:

- `codepulse-full`
- `codepulse-loc`
- `codepulse-vuln`
- `codepulse-vuln-verbose`
- `codepulse-quality`
- `codepulse-deadcode`
- `codepulse-plm`
- `codepulse-ext`
- `codepulse-exec`

This shared module must be installed alongside any CodePulse skill in the same parent skills directory.

## Shared Assets

### References

- `references/runtime-contract.md`: Universal requirements, evidence rules, and compatibility expectations.
- `references/token-efficiency.md`: Targeted repository discovery and token-efficiency rules.
- `references/grading.md`: Authoritative grading scale, category weights, and score calculations.
- `references/severity.md`: Standard risk classification (Critical, High, Medium, Low, Informational) and CVE reporting.
- `references/recommendation-priority.md`: Prioritization hierarchy and formatting for remediation recommendations.
- `references/recommendations-library.md`: Standardized remediation guidance for security, quality, lifecycle, and exposure findings.
- `references/report-standard.md`: Standards for detailed and executive reports.
- `references/assessment-methodology.md`: Shared repository analysis workflow and static assessment limitations.

### Schemas

- `schemas/finding-schema.md`: Normalized finding schema with stable ID, category, severity, title, evidence, impact, and recommendation.
- `schemas/assessment-result-schema.md`: Normalized assessment result contract used for intermediate and aggregated results.

### Templates

- `templates/report-template.html`: Standard HTML layout and styling for detailed assessments.
- `templates/executive-report-template.html`: Standard HTML layout and styling for executive health summaries.
- `templates/assessment-output-template.md`: Compact intermediate markdown assessment output template.
