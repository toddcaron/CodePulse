---
name: codepulse-vuln-verbose
description: Performs an exhaustive security vulnerability review and reports every vulnerability instance with direct repository-relative file and line references. Use when the user requests a verbose, comprehensive, or line-by-line vulnerability report.
---

# Verbose Security Vulnerability Health Check

## Purpose

Perform the security vulnerability portion of the CodePulse health check with exhaustive evidence. Report every distinct security vulnerability identified in the codebase and every affected occurrence, including direct references to the repository-relative file path and line number.

This is a verbose variant of `codepulse-vuln`. It must favor completeness and traceability over brevity while preserving the same security-only scope, severity framework, CVE validation, report template, and grading model.

## Input

Use the entire codebase as the context for this skill. Focus on source code, dependency manifests, package lock files, configuration files, infrastructure files, authentication code, authorization code, API endpoints, data access code, logging, secrets handling, and external integrations.

Exclude `.md` files, `.gitignore` files, generated files, build output, package caches, binaries, images, and other non-code files unless they are directly needed to evaluate security risk.

## Scope

Perform only step 3 from `healthcheck-full`:

- Analyze the code for security vulnerabilities using static code analysis techniques.
- Match identified vulnerabilities with known CVEs where possible.
- Provide a CVE database link for each matched vulnerability.
- Assign a risk level using the shared severity framework.

Do not perform LOC counting, general MFA review, general code quality review, dead code detection, dependency freshness review, or external access analysis unless those findings directly contribute to a security vulnerability.

## Exhaustive Analysis Requirements

Search the complete in-scope codebase for evidence of:

- SQL injection.
- Cross-site scripting.
- Command injection.
- Path traversal.
- Insecure deserialization.
- Authentication bypass.
- Authorization flaws.
- Insecure direct object references.
- Hardcoded secrets, keys, passwords, tokens, or connection strings.
- Weak cryptography.
- Sensitive data exposure.
- Insecure logging of secrets or PII.
- Missing input validation.
- Unsafe file upload handling.
- Overly permissive CORS.
- Insecure dependency versions with known CVEs.
- Unsafe external calls or unvalidated redirects.
- Any other vulnerability supported by concrete codebase evidence.

For each vulnerability:

1. Report every distinct vulnerability rather than grouping unrelated issues under one finding.
2. Report every affected occurrence when the same vulnerability pattern appears in multiple files or locations. A shared root cause may be summarized, but no affected location may be omitted.
3. Trace data flow where practical from the untrusted source through transformations to the security-sensitive sink or decision.
4. Distinguish confirmed vulnerabilities from plausible risks, assumptions, and informational observations.
5. Do not infer a vulnerability solely from a filename, framework, or dependency name without supporting evidence.
6. Record the exact repository-relative path and 1-based line number for each relevant source, sink, configuration, dependency declaration, or authorization decision.
7. Include a short quoted code excerpt for each citation when possible. Keep excerpts limited to the lines needed to establish the evidence.
8. Re-check line numbers against the current files immediately before generating the report.
9. Where a vulnerability spans multiple locations, list each location separately in an Evidence Locations table.
10. State the scan coverage and limitations, including areas that could not be evaluated statically.

## Required Finding Format

Every finding in the HTML report must include:

- A unique finding identifier such as `VULN-001`.
- Finding title.
- Risk level: Critical, High, Medium, Low, or Informational, following `../codepulse-shared/references/severity.md`.
- Affected component or area.
- A complete Evidence Locations table with columns for `File`, `Line`, `Code`, and `Role in Vulnerability`.
- Evidence from the codebase and the relevant source-to-sink or control-flow explanation.
- Why it matters and likely impact.
- Exploitability conditions and assumptions.
- Recommended remediation, using `../codepulse-shared/references/recommendations-library.md` where applicable.
- CVE reference and NVD link when a direct match is found.
- The exact statement `No direct CVE match identified from available evidence.` when no direct CVE match is found.
- Verification steps for confirming the remediation.

Use file citations in this form:

```text
path/to/file.ext:123
```

Use repository-relative paths with forward slashes and 1-based line numbers. Do not cite only a directory, class, method, or filename without a line number. If a generated or minified file is excluded, say so in the limitations instead of citing it as source evidence.

## Completeness Controls

Before finalizing the report:

- Scan all in-scope source, configuration, infrastructure, manifest, and lock files.
- Search each vulnerability category above and investigate both direct matches and relevant sinks.
- Check for repeated instances across the codebase and ensure each has a citation.
- Ensure finding identifiers are unique and citations point to existing files and valid current line numbers.
- Ensure findings are not silently omitted because they share a root cause, component, or severity.
- Include a coverage appendix listing the categories reviewed and the result for each: findings, no evidence found, or unable to assess.
- If no vulnerabilities are found, include the searches and coverage performed to support that conclusion. Do not claim the codebase is secure; state the limits of static analysis.

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

Preserve exhaustive line-level evidence, CVE/NVD references, and stable finding IDs. Render with `../codepulse-shared/renderers/html-template.md` after the report object is final.

## Normalized Result

Emit an assessment result using `../codepulse-shared/schemas/assessment-result-schema.json`. Every line-level finding must use the shared finding schema with a stable `SEC-*` ID and preserve exhaustive path, line, source-to-sink, severity, impact, recommendation, and CVE evidence.

## Output

Follow the Output Protocol in `../codepulse-shared/references/report-standard.md`: write `{skill_name}_{currentDate}-result.json` and render `{skill_name}_{currentDate}-report.html` in:

```text
codepulse-vuln-verbose/reports/
```

The report must include:

- Executive summary with total findings and total affected evidence locations.
- Findings grouped by severity.
- A complete finding-by-finding inventory with direct file and line citations.
- CVE matches and source links where available.
- Risk rating for each finding.
- Recommended fixes and remediation verification steps.
- Coverage appendix and static-analysis limitations.
- A letter grade from D to A for the vulnerability posture.
- Clear next steps for remediation.

Do not claim that the codebase is secure unless the analysis found no meaningful vulnerabilities and the limitations of static review are clearly stated.
