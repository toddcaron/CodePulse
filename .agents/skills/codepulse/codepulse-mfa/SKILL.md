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

Before performing the assessment, review:

- `.agents/skills/codepulse/references/report-template.html`
- `.agents/skills/codepulse/references/grading-model.md`
- `.agents/skills/codepulse/references/recommendations-library.md`

Requirements:

- Use report-template.html for the final HTML output.
- Use grading-model.md when calculating grades.
- Use MFA recommendations from recommendations-library.md when implementation gaps are identified.

## Output

Create a focused HTML report section for MFA only.

Include:

- Whether MFA appears to be implemented.
- Evidence from files, configuration, or code patterns.
- Gaps, bypass risks, or unclear areas.
- Security implications.
- A letter grade from D to A.
- Actionable recommendations for improving MFA coverage.