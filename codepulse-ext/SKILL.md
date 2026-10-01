---
name: codepulse-ext
description: Performs only the external access and exposure portion of the health check. Use this when the user asks whether the application allows external access, exposes public endpoints, has internet-facing APIs, or has external security implications.
---

# External Access Health Check

## Input

Use the entire codebase as the context for this skill. Focus on API endpoints, routing, authentication, authorization, CORS, firewall-related configuration, deployment files, environment configuration, network settings, infrastructure files, ingress configuration, and external integrations.

## Scope

Perform only step 7 from `healthcheck-full`:

- Determine if the codebase allows external access and evaluate the security implications.

Do not perform LOC counting, MFA review, general vulnerability analysis, code quality review, dead code detection, or dependency currency checks unless those findings directly affect external exposure risk.

## Analysis Requirements

Look for:

- Public or unauthenticated endpoints.
- Internet-facing routes.
- API controllers or route definitions.
- CORS policy configuration.
- Anonymous access.
- External callbacks or webhooks.
- External service integrations.
- Ingress, reverse proxy, or gateway configuration.
- Public hostnames or exposed ports.
- Weak authorization around externally reachable functionality.
- Environment-specific exposure differences.

Classify exposure as:

- No external access found.
- Internal-only access appears likely.
- External access appears possible.
- External access confirmed.
- Unable to determine from available code.

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

Use `../codepulse-shared/templates/report-template.html` for the detailed report presentation and preserve exact exposure evidence.

## Normalized Result

Emit an assessment result using `../codepulse-shared/schemas/assessment-result-schema.md`. Use stable `EXT-*` finding IDs for evidence-backed exposure observations and include status, score, limitations, impact, and remediation.

## Output

Create a focused HTML external access report.
Filename =  {skill_name}_{currentDate}-report.html
File output path =  codepulse-ext/reports/

Include:

- External access classification.
- Evidence from code or configuration.
- Security implications.
- Risk level.
- Recommended controls.
- A letter grade from D to A.
- Follow-up validation steps for infrastructure or deployment owners.