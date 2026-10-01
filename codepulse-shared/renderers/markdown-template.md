# Markdown Renderer (Opt-In)

Use only when the user explicitly asks for Markdown output. Render a `reportType: "detailed"` object conforming to `../schemas/codepulse-report-schema.json` to `{skill_name}_{currentDate}-report.md`. Section order, inclusion rules, assessment titles, and required sections are identical to `html-template.md`; this file defines only the Markdown form.

## Rules

- The JSON is the only data source.
- Wrap paths, commands, versions, CVE/GHSA ids, and finding ids in backticks. Never shorten them.
- Escape `|` inside table cells as `\|`. Do not emit raw HTML from JSON strings.
- Show `unavailable` for `null` scores or grades.

## Forms

```markdown
# {application}

CodePulse / {skillName} / {assessmentDate} · {repository}

## Executive Summary
{executiveSummary paragraphs}

## Assessment Dashboard
| Category | Status | Score | Grade | Summary |
|---|---|---:|:-:|---|

## Overall Grade
**{grade}** · {score} / 100 · {note}

## Assessment Methodology
- Executed checks: `{check}`, …
- Tools: …
- Scope included / excluded: …

## {Assessment Title} — {grade}
{summary}

### Complexity breakdown
| Measure | Source | Functions | Median | P90 | Max | Above threshold | Score |

### Complexity hotspots
| Function | Location | Cyclomatic | Cognitive | Finding | Note |

### Findings
#### `{id}` {severity}: {title}
{impact}
- Evidence: `{path}:{line}` {symbol} — {note}
  ```text
  {snippet|output}
  ```
- CVE: `{id}` {package} {version} → {fixedVersion}
- Recommendation: {recommendation}
- Provenance: {verificationStatus} · {sourceRepresentation} · {evidenceLimitations}

## Codebase Metrics
| Language | Files | Physical | Nonblank |

## Top Risks
1. `{findingId}` {title} — {summary}

## Recommendations
1. **{priority}: {title}** {detail} (`{findingIds}`)

## Modernization Opportunities
- **{title}** {detail}

## Limitations
- …

## Conclusion
{conclusion}
```
