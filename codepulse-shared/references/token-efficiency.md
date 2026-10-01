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

## Shared Repository Inventory

For `codepulse-full`, discover repository metadata once and reuse it across its inline capability workflows. The inventory may contain repository type, languages/frameworks, boundaries and source roots, entry points, manifests and lock files, configuration, authentication and authorization locations, routes/endpoints, data access and external integrations, CI/CD and infrastructure, available analyzers, exclusions, and exact evidence references.

Keep inventory entries compact: paths, classifications, versions, commands, and concise metadata. Do not store complete source files, raw logs, complete findings, or reconstructed evidence in the inventory.

Project only the inventory evidence each capability needs:

- LOC: source roots, file classifications, and exclusions.
- Vulnerability: authentication, authorization, routes, data access, integrations, manifests, and configuration.
- Quality: source roots, entry points, core paths, and available analyzers.
- Dead code: source roots, imports, routes, configuration, and project references.
- PLM: manifests, lock files, runtimes, containers, build, and deployment configuration.
- External exposure: routes, authentication, CORS, ingress, host/port configuration, and external integrations.

Inventory reuse avoids repeated discovery; it does not prove absence, replace targeted searches, or replace original-content review. Retrieve original content whenever required by the runtime contract, especially for sensitive evidence, High or Critical findings, conflicts, missing context, and negative findings.

## Output Compression

Replace workflow narration with direct findings. Summarize successful builds, tests, repetitive warnings, and tool banners. Preserve errors, failed tests, relevant warnings, security findings, and exact evidence needed for traceability.

Use finding identifiers when a full finding already exists, for example `See Finding SEC-004.`

Executive sections should contain overall posture, top risks, business impact, modernization opportunities, and prioritized actions. Move implementation detail into findings.

## Protected Content

Never shorten, rewrite, or omit source code, file paths, commands, CVE identifiers, dependency names or versions, error messages, URLs, API endpoints, line numbers, configuration evidence, security evidence, machine-readable output, or required report sections.

## Tool Usage

Reuse existing results. Avoid duplicate enumeration, searches, dependency analysis, equivalent tools, and report generation. Batch related operations when supported.

For `codepulse-full`, defer routine reference expansion until its active phase: inventory and capability analysis first; schema validation and original-evidence recovery after normalization; scoring and recommendation selection after validation; rendering after the report object is final. This sequencing never removes a required reference, schema field, evidence item, or report section.

## External Proxy Coordination

When an external context-optimization proxy is active:

- Continue using targeted repository searches.
- Reuse verified normalized findings.
- Do not assume compression guarantees lower token usage.
- Validate compression-sensitive evidence against original content.
- Request original content only when required for evidence fidelity.
- Do not repeatedly expand content already verified.
- Do not place complete source files or raw logs in intermediate results.
- Preserve exact paths, versions, identifiers, errors, and evidence.
- Treat the CodePulse runtime contract as authoritative when external optimization conflicts with assessment requirements.
