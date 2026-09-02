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
| Security Vulnerabilities | 30% |
| MFA Implementation | 5% |
| Code Quality | 25% |
| Dead Code | 10% |
| Dependency & Framework Health | 15% |
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

## MFA Implementation

### Grade A

- MFA enforced for all users
- Authentication flows properly secured
- No obvious bypass paths detected

### Grade B

- MFA implemented but coverage gaps exist
- Administrative users protected

### Grade C

- Partial MFA implementation
- Inconsistent enforcement

### Grade D

- MFA not detected
- Authentication controls appear weak
- Obvious bypass scenarios identified

---

## Code Quality

### Grade A

- Low complexity
- Consistent architecture
- Minimal duplication
- Strong maintainability

### Grade B

- Minor code smells
- Some refactoring opportunities

### Grade C

- Significant complexity
- Architectural inconsistencies
- Maintainability concerns

### Grade D

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

Example:

| Category | Grade | Score |
|----------|----------|----------|
| Security | B | 85 |
| MFA | A | 95 |
| Code Quality | B | 82 |
| Dead Code | C | 72 |
| Dependencies | B | 84 |
| Exposure | A | 95 |
| LOC | B | 86 |

Weighted Overall Score:

```text
(85 × 0.25)
+ (95 × 0.15)
+ (82 × 0.20)
+ (72 × 0.10)
+ (84 × 0.15)
+ (95 × 0.10)
+ (86 × 0.05)
```

Result:

```text
85.55 = Grade B
```

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