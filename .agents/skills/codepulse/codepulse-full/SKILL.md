---
name: codepulse-full
description: Performs the complete 7-part codebase health check, including lines of code, MFA, security vulnerabilities, code quality, dead code, outdated frameworks/libraries, and external access risk. Use this when the user asks for a full health check, complete codebase review, application health report, or overall application risk assessment.
---

# Full Codebase Health Check

## Input

Use the entire codebase as the context for this skill. Exclude `.md` files, `.gitignore` files, generated files, build output, package caches, binaries, images, and other non-code files from the analysis unless they are directly needed to evaluate dependencies, authentication, or external access.

## Steps

1. Count the total number of lines of code in the codebase.
2. Check for the implementation of Multi-Factor Authentication (MFA) in the codebase.
3. Analyze the code for security vulnerabilities using static code analysis techniques. Match identified vulnerabilities with known CVEs where possible, provide a CVE database link for each matched vulnerability, and assign a risk level of low, medium, or high.
4. Evaluate code quality by checking for code smells, complexity, maintainability issues, and adherence to coding standards.
5. Identify potential dead code and unused variables in the codebase.
6. Check for outdated frameworks and libraries to determine whether dependencies are current and supportable.
7. Determine whether the codebase allows external access and evaluate the security implications.

## Shared References

Use the following shared CodePulse resources when generating the assessment:

- `.agents/skills/codepulse/references/report-template.html`
- `.agents/skills/codepulse/references/grading-model.md`
- `.agents/skills/codepulse/references/severity-ratings.md`
- `.agents/skills/codepulse/references/recommendations-library.md`

Review these files before generating the final report.

Use:

- `report-template.html` for report layout and visual structure.
- `grading-model.md` to assign section grades and calculate the overall CodePulse score.
- `severity-ratings.md` to classify vulnerabilities and security findings.
- `recommendations-library.md` when generating remediation guidance.

If a finding matches a recommendation in the recommendations library, reuse the standardized recommendation rather than generating new wording.

## Output

Create a comprehensive health check report with one section for each step above. Include actionable findings, recommendations, evidence from the codebase, and suggested best practices.

The report should be an HTML document with a structure, look, and feel that follows this example:

`.agents/skills/healthcheck-full/healthcheck-report-example.html`

Provide a letter grade from D to A for each section, where A is excellent and D is poor. The final overall grade should be the average of the individual section grades.