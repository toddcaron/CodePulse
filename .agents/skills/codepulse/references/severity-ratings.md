# CodePulse Severity Ratings

## Purpose

This document defines the standard risk classification framework used by CodePulse assessments.

All CodePulse security-related skills should use these severity levels consistently.

---

# Severity Levels

| Severity | Description |
|----------|----------|
| Critical | Immediate remediation required. Significant risk of compromise, data loss, unauthorized access, or service disruption. |
| High | Serious security weakness with meaningful business impact or exploitability. |
| Medium | Security concern that should be addressed but does not create immediate business risk. |
| Low | Minor issue, defense-in-depth improvement, or best-practice recommendation. |
| Informational | Observation that does not represent a vulnerability but may be useful context. |

---

# Critical Severity

## Characteristics

One or more of the following:

- Remote code execution
- Authentication bypass
- Authorization bypass resulting in privilege escalation
- Public exposure of secrets or credentials
- Active exploitation evidence
- Significant data exposure
- Known critical CVE affecting deployed components

## Examples

- Hardcoded production credentials
- Privilege escalation vulnerability
- Unauthenticated administrative functionality
- Vulnerable dependency with CVSS score of 9.0+

### Recommendation

Remediate immediately.

---

# High Severity

## Characteristics

One or more of the following:

- SQL Injection
- Command Injection
- Significant authorization weakness
- Sensitive data exposure
- Vulnerable dependencies with known exploits
- Weak authentication controls

## Examples

- Improper access control
- Sensitive data leakage
- High-impact dependency vulnerabilities

### Recommendation

Address as soon as practical.

---

# Medium Severity

## Characteristics

- Security best-practice violations
- Limited exploitability
- Requires additional conditions for exploitation
- Moderate business impact

## Examples

- Missing security headers
- Insufficient input validation
- Overly permissive CORS configuration

### Recommendation

Address during normal development cycles.

---

# Low Severity

## Characteristics

- Limited practical risk
- Defense-in-depth improvements
- Minor security weaknesses

## Examples

- Non-sensitive information disclosure
- Logging configuration concerns
- Missing best-practice controls

### Recommendation

Address when resources permit.

---

# Informational

## Characteristics

- Observations only
- No immediate security risk
- Useful architectural or governance context

## Examples

- MFA implementation detected
- Authentication provider identified
- Security controls observed

---

# CVE Validation Requirements

When a CodePulse skill identifies a dependency, framework, runtime, or component vulnerability that appears to match a known CVE, the skill should attempt to validate the finding against publicly available vulnerability data.

The authoritative source for CVE identification should be:

National Vulnerability Database (NIST NVD)

https://nvd.nist.gov/

Additional reference sources may include:

MITRE CVE Program

https://www.cve.org/

GitHub Security Advisories

https://github.com/advisories

---

# Required CVE Reporting Format

When a CVE is identified, reports should include:

## Vulnerability

Example:

```text
CVE-2025-12345
```

## Source

Example:

```text
https://nvd.nist.gov/vuln/detail/CVE-2025-12345
```

## Severity

Example:

```text
High
```

## Impact Summary

Brief explanation of:

- What the vulnerability is
- Why it matters
- Potential impact to the application

## Remediation Guidance

Include:

- Recommended upgrade version
- Vendor guidance when available
- Alternative mitigations if no patch exists

---

# CVSS Guidance

When available, CodePulse should use the CVSS score published by NIST NVD.

| CVSS Score | Recommended Severity |
|----------|----------|
| 9.0 - 10.0 | Critical |
| 7.0 - 8.9 | High |
| 4.0 - 6.9 | Medium |
| 0.1 - 3.9 | Low |

If no official CVSS score is available, severity should be based on exploitability, business impact, and exposure risk.

---

# Multiple Vulnerability Rule

When multiple vulnerabilities impact the same component:

- Report each CVE individually.
- Identify the highest severity finding.
- Include aggregate remediation recommendations when appropriate.

---

# False Positive Guidance

CodePulse should never claim a vulnerability exists solely because a package name appears in a repository.

A finding should be reported only when:

- A known vulnerable version can be reasonably identified.
- A vulnerable implementation pattern exists.
- A supported CVE mapping is available.

When uncertainty exists, label the finding:

```text
Potential Vulnerability – Requires Validation
```

rather than assigning a confirmed severity rating.

---

# Guiding Principle

CodePulse severity ratings should prioritize:

1. Exploitability
2. Business Impact
3. Exposure Surface
4. Likelihood of Compromise
5. Availability of Mitigations

Severity ratings should reflect practical risk, not simply the existence of a vulnerability.
