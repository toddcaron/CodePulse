---
name: codepulse-vuln
description: Performs only the security vulnerability portion of the health check. Use this when the user asks for vulnerabilities, CVEs, insecure code patterns, dependency vulnerabilities, static security review, or application security risks.
---

# Security Vulnerability Health Check

## Input

Use the entire codebase as the context for this skill. Focus on source code, dependency manifests, package lock files, configuration files, infrastructure files, authentication code, authorization code, API endpoints, data access code, logging, secrets handling, and external integrations.

Exclude `.md` files, `.gitignore` files, generated files, build output, package caches, binaries, images, and other non-code files unless they are directly needed to evaluate security risk.

## Scope

Perform only step 3 from `healthcheck-full`:

- Analyze the code for security vulnerabilities using static code analysis techniques.
- Match identified vulnerabilities with known CVEs where possible.
- Provide a CVE database link for each matched vulnerability.
- Assign a risk level of low, medium, or high for each vulnerability.

Do not perform LOC counting, general MFA review, general code quality review, dead code detection, dependency freshness review, or external access analysis unless those findings directly contribute to a security vulnerability.

## Analysis Requirements

Look for evidence of:

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

For each finding, include:

- Finding title.
- Risk level: low, medium, or high.
- Affected file or area.
- Evidence from the codebase.
- Why it matters.
- Recommended remediation.
- CVE reference when a direct match is found.
- If no CVE match is found, state “No direct CVE match identified from available evidence.”

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

Preserve CVE/NVD evidence and emit stable finding IDs. Use `../codepulse-shared/templates/report-template.html` for the detailed report presentation.

## Normalized Result

Emit an assessment result using `../codepulse-shared/schemas/assessment-result-schema.md`. Every finding must use the shared finding schema with a stable `SEC-*` ID, exact evidence, severity, impact, recommendation, and CVE data when applicable.

## Output

Create a focused HTML security vulnerability report.
File output path =  codepulse-vuln/reports/

Include:

- Executive summary.
- Findings grouped by severity.
- CVE matches where available. If not CVE matches, include a statement indicating no direct CVE match was found.
- Risk rating for each finding.
- Recommended fixes.
- A letter grade from D to A for the vulnerability posture.
- Clear next steps for remediation.

Do not claim that the codebase is secure unless the analysis found no meaningful vulnerabilities and the limitations of static review are clearly stated.