# CodePulse Grading Model

## Purpose

This document defines the standard grading methodology used by all CodePulse skills.

All CodePulse assessments should use these guidelines when assigning grades and calculating overall application health scores.

---

# Grading Scale

| Grade | Score Range | Meaning |
|---------|---------|---------|
| A | 90-100 | Excellent |
| B | 80-89 | Good |
| C | 70-79 | Needs Improvement |
| D | Below 70 | High Risk / Significant Concerns |

---

# Assessment Categories

The CodePulse Full Assessment evaluates the following categories:

| Category | Weight |
|----------|----------|
| Security Vulnerabilities | 32% |
| Code Quality | 26% |
| Dead Code | 11% |
| Dependency & Framework Health | 16% |
| External Exposure | 10% |
| Lines of Code & Maintainability Indicators | 5% |

Total Weight = 100%

---

# Category Grading Guidance

## Security Vulnerabilities

### Grade A

- No critical vulnerabilities identified
- No high-risk vulnerabilities identified
- Few or no medium findings
- Secure coding practices consistently observed

### Grade B

- No critical findings
- Limited high-risk findings
- Medium findings documented with reasonable mitigations

### Grade C

- Multiple medium-risk findings
- One or more unresolved high-risk findings
- Inconsistent security practices

### Grade D

- Critical vulnerabilities identified
- Multiple high-risk vulnerabilities
- Sensitive data exposure
- Authentication or authorization weaknesses

---

## Code Quality

Complexity means human readability and maintainability. Score Cyclomatic (10), Cognitive (15), and Accidental (15) Complexity, plus other quality signals (60), using `complexity-model.md`. Do not deduct for inherent domain complexity. Cap the grade at C when any Very High cyclomatic function exists in a core domain path or entry point.

### Grade A

- Functions are predominantly within acceptable cyclomatic and cognitive thresholds
- Little or no accidental complexity
- Consistent architecture
- Minimal duplication
- Strong maintainability

### Grade B

- Isolated cyclomatic or cognitive threshold breaches
- Localized accidental complexity
- Minor code smells
- Some refactoring opportunities

### Grade C

- High cyclomatic or cognitive complexity in core paths
- Recurring accidental complexity across modules
- Architectural inconsistencies
- Maintainability concerns

### Grade D

- Widespread high or very high complexity
- Pervasive accidental complexity that impedes change
- Excessive technical debt
- Poor maintainability
- Widespread code quality issues

---

## Dead Code

### Grade A

- Little or no dead code observed

### Grade B

- Small amount of obsolete or unused code

### Grade C

- Moderate cleanup opportunities exist

### Grade D

- Significant dead code throughout application

---

## Dependency & Framework Health

### Grade A

- Frameworks and dependencies are current and supported

### Grade B

- Minor updates recommended

### Grade C

- Multiple outdated components
- Some upgrade planning required

### Grade D

- Unsupported technologies detected
- Significant modernization risk

---

## External Exposure

### Grade A

- External access tightly controlled
- Strong authentication and authorization

### Grade B

- Minor exposure risks identified

### Grade C

- Multiple externally accessible endpoints requiring review

### Grade D

- Excessive exposure
- Weak access controls
- Significant attack surface

---

## Lines of Code & Maintainability Indicators

### Grade A

- Clear organization
- Appropriate solution size
- Good separation of concerns

### Grade B

- Minor organizational concerns

### Grade C

- Large or difficult-to-maintain areas identified

### Grade D

- Excessive size and complexity impacting maintainability

---

# Overall Application Grade

The overall application grade should be calculated using the weighted score from all assessed categories.

The category weights above are authoritative. Legacy examples that use different weights are illustrative history and must not override the declared 30%, 5%, 25%, 10%, 15%, 10%, and 5% model.

Every category included in the aggregate must have a numeric score from 0 to 100 or an explicitly recorded incomplete/unavailable status. Do not silently substitute a score for missing evidence.

---

# Executive Summary Guidance

Every report should include:

- Overall Grade
- Top Risks
- Recommended Remediation Priorities
- Positive Findings
- Key Technical Debt Indicators
- Modernization Opportunities

Reports should prioritize actionable recommendations over raw findings whenever possible.

---

# Guiding Principle

CodePulse grades should reflect actual risk and maintainability concerns rather than issue counts alone.

Ten minor issues should not outweigh one critical vulnerability.

Risk severity, exploitability, business impact, and modernization concerns should always influence the final assessment.
