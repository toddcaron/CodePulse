---
name: codepulse-shared
description: Shared runtime contract, grading standards, severity ratings, recommendations library, report standards, JSON schemas, and report renderers for all CodePulse assessment skills. Required companion for any CodePulse skill installation.
---

# CodePulse Shared Runtime and Standards

## Purpose

`codepulse-shared` provides the shared runtime contract, grading methodology, severity ratings, recommendations library, report standards, JSON schemas, and renderers consumed by all CodePulse assessment skills:

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

### Schemas (JSON Schema 2020-12, sole data authority)

- `schemas/finding-schema.json`: Normalized finding with stable ID, category, severity, title, evidence, impact, recommendation, and provenance.
- `schemas/assessment-result-schema.json`: Normalized per-capability assessment result, including complexity and LOC metrics.
- `schemas/codepulse-report-schema.json`: Report object persisted as `{skill_name}_{currentDate}-result.json` and consumed by renderers and `codepulse-exec`.

### Renderers

- `renderers/html-template.md`: Detailed HTML report rendering rules and fixed CSS.
- `renderers/markdown-template.md`: Opt-in Markdown report rendering rules.
- `renderers/executive-summary-template.md`: Executive HTML scorecard rendering rules.

The output protocol is defined in `references/report-standard.md`.
