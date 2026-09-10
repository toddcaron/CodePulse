---
name: codepulse-full
description: Performs the complete CodePulse application assessment across security, authentication, code quality, dead code, dependency lifecycle health, external exposure, and maintainability metrics. Use when the user requests a full application health review, technical due diligence assessment, modernization readiness review, security posture assessment, portfolio evaluation, or comprehensive codebase analysis.
---

# CodePulse Full Assessment

## Purpose

CodePulse Full Assessment performs a comprehensive evaluation of application health, security posture, maintainability, technical debt, dependency lifecycle health, authentication maturity, and external exposure risk.

This assessment is intended to provide engineering teams, architects, security teams, and technology leaders with an overall understanding of the application's condition and prioritized recommendations for improvement.

The assessment should identify:

- Security risks
- Authentication weaknesses
- Technical debt
- Maintainability concerns
- Obsolete technologies
- External exposure risks
- Modernization opportunities

and provide a unified CodePulse score and grade.

---

## Input

Use the entire codebase as the assessment scope.

Exclude:

- `.md` files
- `.gitignore`
- documentation
- images
- binaries
- generated files
- build output
- package caches
- third-party vendor content

unless these files are required to evaluate:

- dependencies
- authentication
- infrastructure
- external access
- deployment configurations

If dependency manifests, package files, lock files, infrastructure definitions, or configuration files exist, include them in the assessment.

---

## Shared References

Review the following resources before beginning the assessment:

- `references/report-template.html`
- `references/grading-model.md`
- `references/severity-ratings.md`
- `references/recommendations-library.md`

Requirements:

- Use `report-template.html` for report structure and formatting.
- Use `grading-model.md` for all scoring decisions.
- Use `severity-ratings.md` when assigning vulnerability severity levels.
- Use `recommendations-library.md` whenever a matching remediation recommendation exists.

Reuse standardized recommendations whenever possible.

---

## Assessment Areas

### 1. Codebase Size & Maintainability Indicators

Evaluate:

- Total lines of code
- Language distribution
- Solution organization
- Large files or modules
- Maintainability indicators

Assign a grade using the CodePulse grading model.

---

### 2. Authentication & MFA Review

Evaluate:

- MFA implementation
- Authentication flows
- Identity provider integration
- Authentication bypass risks
- Administrative account protections

Assign a grade using the CodePulse grading model.

---

### 3. Security Vulnerability Assessment

Evaluate:

- SQL Injection
- XSS
- Command Injection
- Sensitive data exposure
- Hardcoded credentials
- Weak authentication patterns
- Authorization weaknesses
- Dependency vulnerabilities
- Known CVEs

Requirements:

- Use severity-ratings.md
- Include CVE references when identified
- Include NIST NVD references when applicable
- Classify findings as Critical, High, Medium, Low, or Informational

Assign a grade using the CodePulse grading model.

---

### 4. Code Quality Review

Evaluate:

- Complexity
- Code smells
- Duplication
- Architecture consistency
- Error handling
- Naming conventions
- Maintainability

Assign a grade using the CodePulse grading model.

---

### 5. Dead Code Assessment

Evaluate:

- Unused methods
- Unused classes
- Unused variables
- Obsolete features
- Commented-out code

Clearly distinguish:

- Confirmed dead code
- Potential dead code
- Requires validation

Notes:
- Distinguish between valid comments and commented-out code that may indicate dead code. Mark commented-out code as “Needs confirmation” unless it is clearly obsolete. Make sure to look for comments via the comment syntax appropriate for the language (e.g., `//` for JavaScript, `#` for Python, '///' for XML, `/* */` for block comments).

Assign a grade using the CodePulse grading model.

---

### 6. Dependency & Framework Lifecycle Assessment

Evaluate:

- Outdated dependencies
- Deprecated libraries
- Unsupported frameworks
- Runtime versions
- Modernization risk

Assign a grade using the CodePulse grading model.

---

### 7. External Exposure & Attack Surface Review

Evaluate:

- Public endpoints
- Anonymous access
- API exposure
- Webhooks
- CORS configuration
- External integrations

Assign a grade using the CodePulse grading model.

---

## Report Requirements

Generate a complete HTML report using the CodePulse reporting template.

The report must contain:

1. Executive Summary
2. Assessment Dashboard
3. Overall Grade
4. Assessment Methodology
5. Security Assessment
6. MFA Assessment
7. Code Quality Assessment
8. Dead Code Assessment
9. Dependency & Framework Assessment
10. External Exposure Assessment
11. Codebase Metrics
12. Top Risks
13. Recommendations
14. Modernization Opportunities
15. Conclusion

---

## Scoring Requirements

Every assessment category must receive:

- Numerical score (0-100)
- Letter grade (A-D)

Calculate the overall CodePulse score using the weighting defined in:


references/grading-model.md


The final report must include:

Overall Score
Overall Grade

along with a brief explanation of the overall rating.

---

## Recommendation Requirements

When generating recommendations:

- Prioritize Critical findings first
- Prioritize High findings second
- Use recommendations-library.md whenever possible
- Avoid duplicate recommendations
- Group related recommendations together

Include:

- Finding
- Business Impact
- Recommended Action
- Priority
- Estimated Complexity

---

## Success Criteria

A successful CodePulse assessment should allow stakeholders to answer:

1. Is this application healthy?
2. Is the application secure?
3. What are the highest risks?
4. What should be remediated first?
5. Is modernization required?
6. What investment should be prioritized?

The final assessment should serve as both an engineering review and a portfolio-level application health report.

## Output

Output a single HTML report file containing the complete assessment.
Filename =  {skill_name}_{currentDate}-report.html
File output path =  codepulse-full/reports/