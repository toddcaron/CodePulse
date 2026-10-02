# Feature Confidence Model (Development 0.4)

Confidence measures the strength of observed evidence, not product approval or
business completeness. The engine computes it. Agent proposals cannot set scores,
change evidence verification, or approve themselves.

## Current Factors

- Structured JSON OpenAPI declaration: 0.25. The declaration was observed, but
  the implementation and executable registration are unverified.
- Comment-aware C# HTTP syntax: 0.40. Source syntax was observed, but framework
  symbols, runtime registration, authorization and behavior are unresolved.
- Vue/AngularJS templates/router syntax and ColdFusion supported tags: 0.35.
  Forms, actions, navigation, remote functions, integrations, scheduled tasks and
  reports are declarations only; business contracts and execution are unresolved.

All current sources are `partially-verified`, not confirmed implementations. Scores are
not summed across duplicate representations. Cross-adapter consolidation and
independent-evidence bonuses are not implemented yet.

## Levels and Admission

- Low: score below 0.50.
- Medium: score at least 0.50 and below 0.80.
- High: score at least 0.80.

The score must be within [0, 1]; the manifest validator rejects a level that does
not agree with the score. Admission uses the corresponding lower boundary:
`low` 0.00, `medium` 0.50, `high` 0.80. Default threshold is medium.

Finder emits all qualifying evidence-backed candidates. Below-threshold candidates
have `admitted: false` and remain in the manifest and review queue, with counts
in the discovery log. An admitted candidate still requires human review and
verified behavior evidence before parity equivalence. Admission is bound into
review digests when present. Older manually authored fixtures without an admission
field remain compatible and default to admitted for comparison only.

## Deferred Factors

Reachability, independent evidence types, executable tests, contradictory evidence
and approved behavior mappings need explicit contracts and fixtures before scoring
them. No current scan claims complete reachability or business completeness.