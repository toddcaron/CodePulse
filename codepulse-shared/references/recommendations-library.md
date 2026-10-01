# CodePulse Recommendations Library

This document provides standardized remediation guidance used by all CodePulse skills. Reuse these recommendations whenever applicable.

---

# Security Recommendations

## Hardcoded Credentials

### Finding

Credentials, API keys, connection strings, tokens, secrets, or certificates are stored directly in source code.

### Recommendation

- Remove hardcoded secrets from source code immediately.
- Store secrets in a secure secret management solution.
- Rotate all exposed credentials.
- Review commit history to ensure secrets are not accessible in version control history.
- Implement automated secret scanning during the CI/CD process.

### Priority

Critical

---

## SQL Injection

### Finding

Database queries are constructed through string concatenation or unvalidated user input.

### Recommendation

- Replace dynamic SQL with parameterized queries.
- Utilize ORM framework protections where available.
- Validate and sanitize all user input.
- Perform security testing against data access layers.
- Add automated SAST rules to detect unsafe query patterns.

### Priority

High

---

## Cross-Site Scripting (XSS)

### Finding

User-supplied content may be rendered without proper encoding.

### Recommendation

- Apply context-aware output encoding.
- Sanitize user-generated content before rendering.
- Implement Content Security Policy (CSP) headers.
- Validate all client-side and server-side inputs.
- Use framework-specific XSS protections.

### Priority

High

---

## Authorization Weaknesses

### Finding

Users may access resources outside their intended permissions.

### Recommendation

- Enforce authorization checks at the server layer.
- Implement least-privilege access controls.
- Validate ownership of resources before access.
- Centralize authorization policy enforcement.
- Add automated tests covering privilege escalation scenarios.

### Priority

High

---

## Sensitive Data Exposure

### Finding

Sensitive information is exposed through responses, logs, or storage mechanisms.

### Recommendation

- Encrypt data at rest and in transit.
- Remove confidential information from logs.
- Mask sensitive fields before display.
- Review API responses for excessive data disclosure.
- Implement data classification standards.

### Priority

High

---

## Vulnerable Dependencies

### Finding

A dependency contains a known CVE or unsupported version.

### Recommendation

- Upgrade to a patched version immediately.
- Review release notes for breaking changes.
- Remove unused dependencies.
- Enable automated dependency scanning.
- Establish dependency review procedures.

### Priority

Based on CVSS Score

---

# Authentication & MFA Recommendations

## MFA Not Implemented

### Finding

Multi-factor authentication was not detected.

### Recommendation

- Implement MFA for all interactive users.
- Require MFA for privileged accounts.
- Integrate with a supported identity provider.
- Enforce MFA through centralized policies.
- Disable legacy authentication methods.

### Priority

High

---

## Partial MFA Coverage

### Finding

MFA exists but is inconsistently applied.

### Recommendation

- Expand MFA enforcement to all users.
- Eliminate MFA exceptions where possible.
- Review service account authentication methods.
- Implement conditional access policies.

### Priority

Medium

---

## Weak Authentication Flows

### Finding

Authentication flows contain weaknesses or bypass opportunities.

### Recommendation

- Strengthen authentication policies.
- Validate token handling logic.
- Review session management controls.
- Enforce secure password policies.
- Conduct authentication-focused penetration testing.

### Priority

High

---

# Code Quality Recommendations

## High Cyclomatic Complexity

### Finding

Functions exceed cyclomatic complexity thresholds, creating many independent paths to understand and test.

### Recommendation

- Add characterization tests before refactoring.
- Extract cohesive branches into well-named methods.
- Replace conditional chains with lookup tables, strategy objects, or polymorphism.
- Separate validation, orchestration, and business rules.

### Priority

Medium

---

## High Cognitive Complexity

### Finding

Functions are difficult to read due to deep nesting, broken linear flow, or mixed boolean logic.

### Recommendation

- Use guard clauses and early returns to flatten nesting.
- Name intermediate boolean expressions to reveal intent.
- Extract nested loops and blocks into named functions.
- Avoid mixing `&&` and `||` in a single expression without grouping.

### Priority

Medium

---

## Accidental Complexity

### Finding

The implementation contains complexity the problem does not require, such as needless abstraction, indirection, duplication, or reinvented framework features.

### Recommendation

- Remove pass-through layers and single-implementation abstractions without a seam purpose.
- Replace custom infrastructure with framework or standard-library features.
- Consolidate inconsistent patterns that solve the same problem.
- Remove speculative extension points and unused options.
- Document the simpler alternative and refactor incrementally behind tests.

### Priority

Medium

---

## Code Duplication

### Finding

Business logic is duplicated across multiple locations.

### Recommendation

- Consolidate duplicated logic.
- Introduce shared services or libraries.
- Standardize implementation patterns.
- Add regression tests before refactoring.

### Priority

Medium

---

## Inconsistent Coding Standards

### Finding

Coding conventions vary throughout the application.

### Recommendation

- Adopt coding standards.
- Implement automated linting.
- Introduce formatting checks within CI/CD pipelines.
- Enforce code review standards.

### Priority

Low

---

# Dead Code Recommendations

## Unused Methods or Classes

### Finding

Methods or classes appear unused.

### Recommendation

- Confirm no usage exists through code search and telemetry.
- Remove obsolete code.
- Archive deprecated functionality when required.
- Update related documentation.

### Priority

Low

---

## Commented-Out Code

### Finding

Large blocks of commented code exist.

### Recommendation

- Remove obsolete commented code.
- Preserve history through source control instead of comments.
- Document rationale separately if needed.

### Priority

Low

---

## Obsolete Features

### Finding

Components appear to support retired functionality.

### Recommendation

- Validate business ownership.
- Remove unused feature paths.
- Simplify application architecture.
- Reduce maintenance burden.

### Priority

Medium

---

# Dependency & Framework Recommendations

## Outdated Dependencies

### Finding

Dependencies are behind current supported versions.

### Recommendation

- Upgrade dependencies on a regular cadence.
- Review vendor release notes.
- Establish dependency health dashboards.
- Include dependency review in release processes.

### Priority

Medium

---

## Unsupported Frameworks

### Finding

Frameworks have reached end-of-support status.

### Recommendation

- Prioritize upgrade planning.
- Identify upgrade blockers.
- Develop phased modernization plans.
- Reduce reliance on unsupported technologies.

### Priority

High

---

## Legacy Runtime Versions

### Finding

Applications rely on outdated platform runtimes.

### Recommendation

- Migrate to supported runtime versions.
- Validate compatibility through automated testing.
- Schedule runtime upgrades as part of modernization efforts.

### Priority

High

---

# External Exposure Recommendations

## Publicly Accessible Endpoints

### Finding

Endpoints appear accessible without sufficient controls.

### Recommendation

- Require authentication where appropriate.
- Review authorization rules.
- Restrict unnecessary public access.
- Implement API gateway protections.
- Monitor exposed endpoints.

### Priority

High

---

## Overly Permissive CORS

### Finding

CORS configuration allows broader access than required.

### Recommendation

- Restrict allowed origins.
- Limit supported methods.
- Remove wildcard configurations.
- Review API consumer requirements regularly.

### Priority

Medium

---

## Excessive Attack Surface

### Finding

The application exposes unnecessary services or functionality.

### Recommendation

- Disable unused endpoints.
- Remove deprecated APIs.
- Minimize externally accessible components.
- Apply defense-in-depth controls.

### Priority

High

---

# Modernization Recommendations

## Technical Debt

### Finding

The application contains significant technical debt.

### Recommendation

- Prioritize high-risk debt items.
- Include remediation work in sprint planning.
- Track debt using backlog items.
- Measure debt reduction over time.

### Priority

Medium

---

## Architecture Modernization

### Finding

Application architecture limits maintainability or scalability.

### Recommendation

- Evaluate service decomposition opportunities.
- Improve separation of concerns.
- Standardize architectural patterns.
- Reduce tight coupling between components.

### Priority

Medium

---

## Cloud Readiness

### Finding

The application may be difficult to deploy or scale in modern environments.

### Recommendation

- Evaluate containerization opportunities.
- Externalize configuration.
- Improve observability and logging.
- Automate deployment pipelines.

### Priority

Medium

---

# Executive Summary Recommendation Prioritization

Reports should prioritize recommendations in this order:

1. Critical Security Risks
2. High-Risk Security Findings
3. Authentication & MFA Gaps
4. Unsupported Frameworks & Dependencies
5. External Exposure Risks
6. Major Code Quality Issues
7. Technical Debt Reduction Opportunities
8. Dead Code Cleanup Activities
9. General Best Practice Improvements

---

# Recommendation Formatting Standard

Each recommendation should contain:

## Finding

Short description of the issue.

## Business Impact

Describe the potential impact on security, maintainability, reliability, compliance, or modernization goals.

## Recommended Action

Clear remediation guidance.

## Priority

One of:

- Critical
- High
- Medium
- Low

## Estimated Complexity

One of:

- Small
- Medium
- Large

## Expected Benefit

Describe the expected improvement after remediation.

---

# Guiding Principle

CodePulse recommendations should be actionable, specific, evidence-based, prioritized by risk, and understandable by both technical and leadership audiences. Recommendations should focus on reducing risk while improving maintainability, security posture, and modernization readiness.
