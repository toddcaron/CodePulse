# CodePulse Token-Efficiency Rules

Reduce avoidable context and narration without reducing evidence fidelity or assessment quality.

## General Rules

- Use concise, direct language.
- Do not narrate routine actions or announce the next routine step.
- Prefer structured output, bullets, and tables where they reduce repetition.
- Do not repeat instructions or findings already established by the active contract.

## Repository Analysis

Before scanning, detect repository type, languages/frameworks, project boundaries, entry points, manifests, configuration, CI/CD, and infrastructure. Build a targeted plan for the active assessment.

Do not exhaustively scan when targeted evidence is sufficient. Reuse metadata and findings collected during the current assessment. Expand scope only when evidence is insufficient.

Prioritize manifests and entry points such as `package.json`, `*.csproj`, `*.sln`, `Directory.Packages.props`, `appsettings*.json`, `Program.cs`, `Startup.cs`, `web.config`, lock files, authentication configuration, pipeline definitions, and infrastructure files.

Skip unless required:

```text
node_modules/ bin/ obj/ dist/ build/ coverage/ logs/ vendor/ packages/ .git/
```

Also skip generated code, minified assets, binaries, caches, copied artifacts, and duplicate vendored source.

## Output Compression

Replace workflow narration with direct findings. Summarize successful builds, tests, repetitive warnings, and tool banners. Preserve errors, failed tests, relevant warnings, security findings, and exact evidence needed for traceability.

Use finding identifiers when a full finding already exists, for example `See Finding SEC-004.`

Executive sections should contain overall posture, top risks, business impact, modernization opportunities, and prioritized actions. Move implementation detail into findings.

## Protected Content

Never shorten, rewrite, or omit source code, file paths, commands, CVE identifiers, dependency names or versions, error messages, URLs, API endpoints, line numbers, configuration evidence, security evidence, machine-readable output, or required report sections.

## Tool Usage

Reuse existing results. Avoid duplicate enumeration, searches, dependency analysis, equivalent tools, and report generation. Batch related operations when supported.
