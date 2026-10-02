# Executive Summary Renderer

Render a `reportType: "executive"` object conforming to `../schemas/codepulse-report-schema.json` into one self-contained HTML file. Data comes only from `executive`, `application`, `assessmentDate`, `sourceReport`, and `limitations`.

## Rules

- Apply the escaping, link, and no-script rules from `html-template.md`.
- Use the CSS block from `html-template.md` verbatim, plus this line:
  ```css
  .card{border-top:4px solid var(--blue);padding-top:8px}.card strong{display:block;font:700 1.1rem "Trebuchet MS",sans-serif}.Strong,.Modern,.Excellent,.Ready,.LowRisk{border-top-color:var(--green)}.NeedsAttention,.Aging,.Challenging,.Moderate,.RequiresPlanning{border-top-color:var(--amber)}.HighRisk,.Legacy,.Poor,.HighOp,.CriticalOp,.SignificantInvestmentRequired,.MajorModernizationRecommended{border-top-color:var(--red)}.NotAssessed{border-top-color:var(--line)}
  ```
- Card class = rating value with spaces removed. For `operationalRisk`, use `LowRisk`, `Moderate`, `HighOp`, or `CriticalOp`. `Not Assessed` uses class `NotAssessed` and renders the value in `meta` style.
- Do not render file names, line numbers, source code, configuration details, or individual vulnerability lists. `findingIds` may appear only as a small `meta` trace line.
- Use the skeleton and footer from `html-template.md`; title is `{application} – Executive Summary – {assessmentDate}`.

## Section Order

| # | Title | Source | Markup |
|---|---|---|---|
| 0 | header | `application`, `assessmentDate` | `<header><div class="eyebrow">CodePulse Executive Summary / {assessmentDate}</div><h1>{application}</h1></header>` |
| 1 | Executive Dashboard | `executive.dashboard` | `<div class="grid">` of six cards: `<div class="card {class}"><span class="meta">{label}</span><strong>{value}</strong></div>`. The overall grade card uses `G(overallGrade)` from `html-template.md`. Labels: Overall CodePulse Grade, Security Posture, Technology Health, Maintainability, Operational Risk, Modernization Readiness. |
| 2 | Application Snapshot | `executive.snapshot[]` | up to 2 `<p>` |
| 3 | Top Risks | `executive.topRisks[]` | `<div class="grid">` of `<div class="f {priority}"><p><strong>{risk}</strong></p><p>{businessImpact}</p><p class="meta">Priority: {priority}</p></div>` |
| 4 | Strengths | `executive.strengths[]` | `<ul>` |
| 5 | Investment Priorities | `executive.investmentPriorities[]` | table: Area, Why it matters, Business benefit, Priority |
| 6 | Modernization Outlook | `executive.modernizationOutlook` | `<p><strong>Complexity: {complexity}</strong></p><p>{summary}</p>`, then Concerns and Next steps lists |
| 7 | Executive Recommendation | `executive.recommendation` | `<p><strong>{decision}</strong></p><p>{rationale}</p>` |
| 8 | Limitations | `limitations[]`, `sourceReport` | `<ul>` plus `<p class="meta">Source: <code>{sourceReport}</code></p>` |
