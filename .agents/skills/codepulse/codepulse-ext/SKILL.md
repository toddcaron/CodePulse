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

Before generating the assessment, review:

- `.agents/skills/codepulse/references/report-template.html`
- `.agents/skills/codepulse/references/grading-model.md`
- `.agents/skills/codepulse/references/severity-ratings.md`
- `.agents/skills/codepulse/references/recommendations-library.md`

Requirements:

- Use report-template.html for formatting.
- Use severity-ratings.md when determining exposure severity.
- Use recommendations-library.md for remediation guidance.
- Use grading-model.md for scoring.

## Output

Create a focused HTML external access report.

Include:

- External access classification.
- Evidence from code or configuration.
- Security implications.
- Risk level.
- Recommended controls.
- A letter grade from D to A.
- Follow-up validation steps for infrastructure or deployment owners.