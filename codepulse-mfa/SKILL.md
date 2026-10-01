---
name: codepulse-mfa
description: Performs only the Multi-Factor Authentication portion of the health check. Use this when the user asks whether MFA is implemented, enforced, bypassed, or integrated in the application.
---

# MFA Implementation Health Check

## Input

Use the entire codebase as the context for this skill. Focus on authentication, authorization, identity provider integration, login flows, configuration files, middleware, security policies, and access control code.

## Scope

Perform only step 2 from `healthcheck-full`:

- Check for the implementation of Multi-Factor Authentication (MFA) in the codebase.

Do not perform LOC counting, vulnerability analysis, code quality review, dead code detection, dependency currency checks, or external access analysis unless those findings directly affect MFA.

## Analysis Requirements

Look for evidence of:

- MFA enforcement.
- Conditional access or identity provider integration.
- Authentication middleware.
- Login and sign-in flows.
- Bypass paths or fallback authentication.
- Admin-only MFA requirements versus all-user MFA requirements.
- Hardcoded authentication behavior.
- Configuration-driven MFA settings.

If MFA cannot be confirmed from the codebase, clearly state that MFA was not found or could not be verified from available code.

## Shared References

Before executing this skill, read and apply:

- `../codepulse-shared/references/runtime-contract.md`
- `../codepulse-shared/references/token-efficiency.md`
- `../codepulse-shared/references/grading.md`
- `../codepulse-shared/references/recommendation-priority.md`
- `../codepulse-shared/references/recommendations-library.md`
- `../codepulse-shared/references/report-standard.md`
- `../codepulse-shared/references/assessment-methodology.md`
- `../codepulse-shared/schemas/finding-schema.md`
- `../codepulse-shared/schemas/assessment-result-schema.md`

Use `../codepulse-shared/templates/report-template.html` for the detailed report presentation and preserve authentication/MFA evidence.

## Normalized Result

Emit an assessment result using `../codepulse-shared/schemas/assessment-result-schema.md`. Use stable `MFA-*` finding IDs and the shared finding schema for evidence-backed control gaps, positive observations, and recommendations.

## Output

Create a focused HTML report section for MFA only.
File output path =  codepulse-mfa/reports/

Include:

- Whether MFA appears to be implemented.
- Evidence from files, configuration, or code patterns.
- Gaps, bypass risks, or unclear areas.
- Security implications.
- A letter grade from D to A.
- Actionable recommendations for improving MFA coverage.