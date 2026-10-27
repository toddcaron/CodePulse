# Feature Report Renderer

Defines the presentation contract for feature-parity reports. The feature-parity engine is the only renderer: `parity report` produces every artifact described here. Skills and agents must not hand-author, re-style, or extend these files.

## Scope

This renderer applies to feature-parity artifacts only. It never renders health findings, severities, grades, scores, or recommendations, and it never reads `../schemas/codepulse-report-schema.json`. The health renderers in this directory never render feature artifacts.

## Data Source

Presentation is separated from data. `../schemas/feature-report-schema.json` (`urn:codepulse:feature-report:1.0`) defines the report object; this file defines its presentation. The rendered HTML and Markdown contain no value that is absent from `feature-report.json`.

`reportType` is one of:

| `reportType` | Input artifact | Required supporting manifests |
|---|---|---|
| `discovery` | `feature-manifest.json` from `parity find` | none |
| `comparison` | `parity-results.json` from `parity compare` | `--source`, `--target` |
| `requirements-coverage` | `requirements-coverage.json` from `parity cover-requirements` | `--baseline`, `--target` |

Supporting manifests are digest-verified against the result. A stale manifest is an artifact failure; the engine refuses to render rather than present mismatched scope.

## Output Protocol

1. `parity report` builds one report object and validates it against `../schemas/feature-report-schema.json`.
2. It always writes `feature-report.json` to the requested output directory.
3. It renders `feature-report.html` by default.
4. Markdown is opt-in: `feature-report.md` is written only for `--format markdown` or `--format both`.
5. The output directory must not exist and must not overlap an input path.

Reports are deterministic: identical inputs produce byte-identical artifacts. No timestamps, host names, paths outside the artifacts, or other volatile telemetry are emitted. Provenance comes from the digests recorded in the artifacts.

## Text Safety

Every string the engine renders originates from scanned repositories or human review text and is treated as untrusted:

- Control characters (C0 and C1) are removed, and all whitespace is collapsed to single spaces, so every rendered value is single-line.
- Values longer than 4000 characters are truncated with a trailing `...`.
- HTML escapes `&`, `<`, `>`, `"`, and `'`. No raw HTML, `<script>`, event handler, `style` attribute, external font, image, stylesheet, or link is ever emitted from artifact content.
- Markdown escapes `\` and `|` so no value can break out of a table cell.
- `unresolvedItems` is capped at 500 records; truncation is disclosed as a limitation rather than silently applied.
- Discovery `capabilities` detail is capped at 500 active features with a disclosed
  limitation; semantic counts always cover all active features. The full manifest
  retains every feature and rule.

## Section Order

Both renderers emit the same sections in the same order.

| # | Section | Source |
|---|---|---|
| 0 | header | `title`, `reportType`, `engineVersion`, `methodology` |
| 0a | Capabilities and business context (discovery only) | `discoveryMode`, `semanticStatus`, `capabilities[]`: readable name and summary, then business purpose, user goal, trigger, outcome, basis, domain, analysis status, questions, citations and identifier; provisional business-rule condition/outcome/basis/rationale/evidence table |
| 1 | Scope | `applications[]`: Role, Application, Source type, Revision, Scan coverage, plus a per-application scope-limitations list when present |
| 2 | Provenance | `digests[]`: Artifact, Digest |
| 3 | Review state | `reviewState[]`: Measure, Count |
| 4 | Results | `metrics[]`: Measure, Count |
| 5 | Formulas | `formulas[]`: Measure, Formula, Value |
| 6 | Unresolved items (`unresolvedCount`) | `unresolvedItems[]`: Identifier, Status, Detail, or an explicit no-records statement |
| 7 | Limitations | `limitations[]` |
| 8 | footer | `engineVersion` plus the static-evidence disclaimer |

Unavailable optional values render as `unavailable`, and digests that were not supplied render as `not supplied`. Standard sections are never omitted, so an empty measure set is visible rather than hidden. The capability section appears only in discovery reports.

## Limitations Disclosure

Every report carries the limitations recorded in its source artifacts plus two standing limitations: that the engine renders only values present in the source JSON artifacts and built or executed nothing, and that static-evidence reports never establish runtime parity or confirmed absence. Limitations are deduplicated.

Conditional limitations are added when a discovery manifest records no confidence admission, when the reviewed-requirements digest is carried from the coverage result rather than re-verified, and when unresolved detail was truncated. Discovery reports additionally state that candidates are provisional and carry no human review, approval, or parity credit.

Empty strings render as `(not recorded)` rather than as blank cells, so missing evidence stays visible.

Discovery reports distinguish inventory-only (no active candidate analyzed), incomplete
(some candidates not-started, partial or unresolved), and complete (all active candidates
analyzed without unresolved questions). An empty inventory is inventory-only, not
vacuously complete. Semantic completion is not approval, runtime correctness or business
completeness. Technical-only manifests never masquerade as analyzed business capabilities.

Normal discovery reports require business meaning before rendering. The engine checks
every active feature, not just the first 500 displayed. Capabilities lead the report:
each has a heading, summary and a readable two-column business-context detail table,
not a wide endpoint inventory. HTML and Markdown preserve the same ordering.

`discoveryMode: business` is the default and requires structured businessMeaning plus
complete/partial candidate analysis and business contracts. Missing/unresolved meaning
fails without publishing a report. `--inventory-only` is an explicit discovery-only
opt-out; the title and mode identify technical inventory output. It is not a fallback
for failed analysis. Business readiness checks cannot establish correctness of intent.
