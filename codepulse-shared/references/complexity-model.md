# CodePulse Complexity Model

In CodePulse, **complexity means human readability and maintainability**: how hard code is for a developer to understand, change, and test safely. It does not mean how hard the underlying problem is. Evaluate three measures and deduct only for complexity the code introduces, not complexity the domain requires.

## Definitions

| Measure | Question Answered | Basis |
|---|---|---|
| Cyclomatic Complexity | How many independent paths must be understood and tested? | McCabe: 1 + decision points (`if`, `else if`, `case`, loops, `catch`, `&&`, `\|\|`, `?:`, `??`). |
| Cognitive Complexity | How hard is this code to read top to bottom? | SonarSource model: +1 per break in linear flow (`if`, `else`, `switch`, loops, `catch`, `goto`, labeled `break`/`continue`, recursion, each sequence of mixed boolean operators); +1 extra per nesting level for nested flow breaks. Shorthand that reads easily (null-coalescing, a single `switch`) is not penalized. |
| Accidental Complexity | What complexity exists that the problem does not require? | Complexity introduced by design, tooling, or implementation choices rather than by business rules. |
| Inherent Complexity | What complexity is required by the domain? | Essential business rules, regulatory logic, protocol state machines, algorithms. Record as context; do not deduct. |

## Measurement

Use tool-first measurement with a manual fallback.

1. Use an available analyzer when one exists or can run without modifying the repository:

   | Ecosystem | Cyclomatic | Cognitive |
   |---|---|---|
   | Multi-language | `lizard` | — |
   | Python | `radon cc` | `flake8-cognitive-complexity`, `complexipy` |
   | JavaScript / TypeScript | ESLint `complexity` | `eslint-plugin-sonarjs` `cognitive-complexity` |
   | Java | PMD `CyclomaticComplexity`, Checkstyle | PMD `CognitiveComplexity` |
   | .NET | Roslyn code metrics, `CA1502` | SonarAnalyzer `S3776` |
   | Go | `gocyclo` | `gocognit` |
   | Existing SonarQube / SonarCloud output | Yes | Yes |

2. When no analyzer can run, estimate by reading the source. Count decision points and nesting for the largest, most-branched, and most central functions. Mark resulting findings `partially-verified`, and record "manually estimated" in `evidenceLimitations`.
3. Always record `measurementSource` (tool name and version, or `manual-estimate`) for each measure.
4. Exclude generated code, minified files, vendored or third-party code, migrations, and build output. Report test code separately if it is measured.
5. Discard analyzer pseudo-entries, such as lizard `*global*` rows or top-level statements reported as functions, and note analyzer coverage gaps (for example, lizard reads only `<script>` blocks in `.vue` files).

## Thresholds (per function or method)

| Band | Cyclomatic | Cognitive | Default Severity |
|---|---|---|---|
| Acceptable | 1–10 | 0–15 | None |
| Moderate / Elevated | 11–20 | 16–25 | Low |
| High | 21–50 | > 25 | Medium |
| Very High | > 50 | — | High |

Raise severity one level when a breach sits in a core domain path, an entry point, or frequently changed code. Lower it one level for isolated, stable, well-tested code.

## Accidental Complexity Indicators

- Needless abstraction layers, or interfaces with a single implementation and no seam purpose.
- Pass-through wrappers that add no behavior.
- Speculative generality: unused extension points, options, or generic parameters.
- Excessive configuration or indirection (reflection, DI, events) for simple flows.
- Duplicated logic or repeated business rules.
- Deep inheritance hierarchies where composition would suffice.
- Boolean flag parameters that switch behavior.
- Long parameter lists and primitive obsession.
- Inconsistent patterns solving the same problem in different ways.
- Reinventing framework or standard-library features, or misusing the framework.
- Tight coupling and hidden side effects or temporal coupling.
- Hardcoded values that obscure intent.
- Unclear naming that forces the reader to infer intent.

### Inherent vs. Accidental Test

For each candidate, ask: "Could the same behavior be expressed more simply without losing correctness or required flexibility?" Classify as accidental only when the answer is yes, and state the simpler alternative in the finding. When the answer is no, record the complexity as inherent context and do not deduct. High cyclomatic or cognitive scores caused by inherent rules still warrant readability recommendations (decomposition, naming, tables), but not accidental-complexity findings.

## Aggregation

For each measure, report:

- Measurement source and scope (files and functions measured).
- Median, 90th percentile, and maximum per function.
- Count and percentage of functions in each band.
- Top hotspots by file, function, and line, weighted by centrality (entry points and core domain first), not count alone.

## Scoring

The Code Quality category score (0–100) combines:

| Component | Weight |
|---|---:|
| Cyclomatic Complexity | 10 |
| Cognitive Complexity | 15 |
| Accidental Complexity | 15 |
| Other quality signals (naming, error handling, logging, structure, standards, conventions) | 60 |

Score each complexity component from 0 to 100:

| Component Score | Cyclomatic / Cognitive Condition | Accidental Condition |
|---|---|---|
| 90–100 | ≤ 5% of functions above Acceptable; none High or Very High | No or isolated indicators |
| 80–89 | ≤ 10% above Acceptable; isolated High | A few localized indicators |
| 70–79 | ≤ 20% above Acceptable, or High in core paths | Recurring indicators across modules |
| < 70 | > 20% above Acceptable, or any Very High in core paths | Pervasive indicators that impede change |

Cap the Code Quality grade at C when any Very High cyclomatic function exists in a core domain path or entry point. Record a component as unavailable, rather than substituting a score, when it cannot be measured or estimated.

## Finding IDs

- `QUAL-CYC-*` — Cyclomatic Complexity findings.
- `QUAL-COG-*` — Cognitive Complexity findings.
- `QUAL-ACC-*` — Accidental Complexity findings.
- `QUAL-*` — Other quality findings.

Include the optional `metrics` field from the finding schema on cyclomatic and cognitive findings.

## Limitations

Different analyzers count decision points differently; compare values only within the same source. Manual estimates are approximations. Static measures cannot assess runtime behavior, team familiarity, or change frequency unless version history is reviewed.
