# CodePulse Recommendation Priority

Prioritize recommendations in this order:

1. Critical security risks
2. High-risk security findings
3. Authentication and MFA gaps
4. Unsupported frameworks and dependencies
5. External exposure risks
6. Major code-quality issues
7. Technical-debt reduction
8. Dead-code cleanup
9. General best-practice improvements

Each recommendation should include the finding, business impact, recommended action, priority, estimated complexity (`Small`, `Medium`, or `Large`), and expected benefit. Recommendations must be actionable, specific, evidence-based, and deduplicated.

Reuse the existing recommendations library when a matching recommendation exists. Group related actions and reference stable finding IDs rather than repeating full findings.
