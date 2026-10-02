# Optional Caveman Runtime Setup

CodePulse works without Caveman repository instructions and without Caveman Proxy. Neither is a CodePulse dependency, and neither changes CodePulse's evidence, grading, schema, or report requirements. This document describes installation and validation; it is not organizational security, legal, or licensing approval.

## Two Separate Integrations

**Caveman repository instructions** are static instruction files written into a repository for an agent to read. They influence response style, but do not install the host runtime or prove that a proxy is active. The upstream Copilot `--with-init` path documents `.github/copilot-instructions.md` and `AGENTS.md` as outputs. The instructions reviewed for release `v3.0.0` ask for terse language while preserving technical substance and call for clarity on security warnings and irreversible actions. CodePulse requirements in `codepulse-shared/references/runtime-contract.md` take precedence.

**Caveman Proxy** is a host-level CLI/runtime installed on the developer or assessment machine. It is separate from repository files, and does not provide a repository-local installation in the reviewed upstream documentation. Launch only an agent that the installed CLI explicitly supports. Do not assume GitHub Copilot in the IDE is a supported wrapper; its repository-instruction integration is separate.

## Repository Instructions

Review the upstream installer source, generated rule text, release provenance, and license before running it. The command requested for this repository is:

```bash
npx -y github:JuliusBrussee/caveman -- --only copilot --with-init
```

Run it from the CodePulse repository root. The command is not pinned to a commit; resolve and record the exact release/tag and commit used before adopting generated instructions. The reviewed upstream release documentation identifies version `v3.0.0`; its installer writes repo-wide rule files, with the Copilot output at `.github/copilot-instructions.md` and `AGENTS.md` also listed for initialization. The installer may append to existing files. Review the full diff and preserve unrelated existing content.

The installer was run from the repository root on 2026-09-30. The cached installer package reports version `3.0.0` and Apache-2.0. The `--with-init` step added these six files: `.cursor/rules/caveman.mdc`, `.windsurf/rules/caveman.md`, `.clinerules/caveman.md`, `.github/copilot-instructions.md`, `.opencode/AGENTS.md`, and `AGENTS.md`. Each was reviewed and given a CodePulse precedence clause. OpenClaw initialization was skipped because its workspace was not present. The six generated files were subsequently removed at the user's request; no repo-wide Caveman instruction files are currently retained.

The installer's separate GitHub Copilot skill step ran `npx skills add JuliusBrussee/caveman --skill * -a github-copilot --yes -g` and reported failure. Thus the repository rule files were installed, but this does not establish that a user-scoped Copilot skill was installed. These capabilities are separate and optional. The npm Git-package restriction that blocked an earlier dry-run was later resolved; do not use that earlier error as the current installation result. The command resolves a GitHub package rather than pinning a commit, so version `3.0.0` is recorded here but an immutable source commit was not captured.

Do not report the optional skill-install step as complete. Review the full diff and preserve all unrelated existing content before committing the generated files.

After installation:

1. Review every created and modified instruction file. Remove or resolve wording that conflicts with CodePulse evidence fidelity, security accuracy, required coverage, schemas, grading, or reports.
2. Record the exact Caveman source revision and the date reviewed in the repository change or deployment record. Do not treat the moving GitHub default branch as a stable version.
3. Confirm CodePulse still works when generated Caveman instructions are absent. Do not duplicate Caveman's complete policy into every CodePulse `SKILL.md`.
4. Do not commit credentials, provider keys, caches, backups, session data, or local configuration that may contain secrets.

## Host Proxy Installation

The current upstream CLI documentation requires Node.js 22.13 or newer. Confirm the selected CLI release's requirements before installing or upgrading.

```bash
npm install -g @caveman-ai/cli
caveman setup --install
```

Inspect what is installed and available:

```bash
caveman setup
caveman status
caveman --help
```

The current upstream agent-wrapping documentation lists `aider`, `claude`, `codex`, `gemini`, `hermes`, `kilo`, `openclaw`, `opencode`, `pi`, and `qwen`. This list can change; use the installed CLI's setup/help output and current upstream agent documentation to confirm support for the exact host and version. Installation of the agent itself may be separate.

Launch examples documented upstream include:

```bash
caveman claude
caveman codex
caveman gemini
```

The `caveman <agent>` shortcut may enable a persistent native integration. For a one-session wrapper where supported, use:

```bash
caveman wrap claude
```

Use the same pattern only for agent IDs the installed CLI confirms. Do not infer that an IDE extension is routed just because its related CLI is supported.

## Setup Verification

Record the CLI version, agent and version, setup/status output, launch method, and available runtime evidence. To distinguish a direct run from a proxy run, record an explicit CLI status, runtime/process state, proxy receipt, or other verifiable signal. A wrapped command alone is not proof that requests traversed the proxy or were compressed. Do not claim token savings without comparable input/output or credit measurements.

For evidence-sensitive CodePulse work, keep originals accessible independently of proxy summaries. Validate source code, configuration, manifests and lock files, exact failed test/build output, scanner output, and other compression-sensitive evidence against originals as required by the runtime contract. If original content cannot be recovered, report the observation as incomplete or unverified and continue unaffected categories. High and Critical findings require original-content verification.

## Upgrade

Review release notes, source provenance, package/runtime licenses, security advisories, data flow, and changed setup behavior before upgrading. Pin an approved CLI version where the package supports it, preserve the previous version and host configuration as required by local policy, and record the new version. Use the package manager's pinned install form only after confirming the approved version, then run `caveman setup`, `caveman status`, and the supported agent's doctor/status command if available. Re-run the installation validation checklist below.

For repository instructions, review the selected release's installer before repeating the repository command. Inspect resulting changes; do not force-overwrite user-authored files without review.

## Disable or Uninstall

Disable native host integrations before removing the CLI, so the runtime can restore its managed routing/configuration:

```bash
caveman disable --all
npm uninstall -g @caveman-ai/cli
```

Confirm the exact disable syntax against the installed CLI (`caveman --help`) before use. Upstream documents repository rule files as separate artifacts that its host uninstall does not remove; review and remove only the Caveman-owned blocks/files if desired, preserving unrelated content. Disabling the proxy does not remove or change CodePulse.

To disable repo instructions only, remove the Caveman-owned generated content after reviewing its boundaries. If instructions were appended to a shared file, remove only the identified Caveman text and retain all other content.

## Security, Licensing, and Governance

Before team adoption:

- Review upstream source, release provenance, package lifecycle scripts, and runtime binaries; pin approved versions where practical.
- Review the applicable license for the CLI, proxy binaries, generated instructions, and transitive packages. Upstream identifies Caveman's instructions/CLI/runtime as Apache-2.0; verify this against the precise release and package artifacts being approved.
- Review request data flow, provider routing, local storage and recovery behavior, telemetry, logs, backups, and deletion controls. Do not assume that content remains local or that originals can always be recovered.
- Review credential handling, including environment variables and any provider or gateway credentials. Never commit or print secrets; CodePulse redaction rules remain in force.
- Review generated instructions and validate their precedence against CodePulse's runtime contract.
- Validate compatibility with organizational AI, source-code, privacy, and data-retention policies.
- Assign an owner for upgrades, support, vulnerability monitoring, and removal.

These checks are required review topics, not a security, legal, licensing, or organizational approval.

## Troubleshooting

- **Git fetch blocked by npm policy:** use an approved environment or approved internal mirror after policy review. Do not bypass the restriction by executing an unreviewed downloaded installer. The repository instructions can remain absent; CodePulse remains usable without them.
- **`caveman` not found after npm install:** verify Node/npm global bin directory is on `PATH`, open a new shell, then check `caveman --help` and `caveman setup`.
- **Setup reports missing runtime components:** follow the exact repair instructions from the installed CLI, then re-run `caveman setup` and `caveman status`.
- **Agent does not launch or route:** verify the installed agent and version, confirm its ID is supported by the installed CLI, inspect the CLI's doctor/status output, and try the documented direct launch to isolate host problems. Do not assume Copilot IDE support.
- **Proxy unavailable during an assessment:** continue with direct repository/tool access where possible, record the affected evidence and workflow status, and do not infer that a category completed. Recover and inspect originals when required.
- **Unexpected repository instruction conflict:** remove or revise only the Caveman-owned instruction text after reviewing the full diff; CodePulse precedence remains authoritative.

## Installation Validation Checklist

1. If repo-wide Caveman instructions are enabled, their source version is recorded and each file defers to CodePulse; otherwise, confirm their absence. Record any separate optional Copilot skill-install outcome.
2. Runtime precedence remains intact; CodePulse requirements override external optimization instructions.
3. CodePulse runs without Caveman instructions or proxy.
4. CodePulse runs with repo-wide Caveman instructions and retains required detail and report structure.
5. The selected agent can be launched through a wrapper documented for the installed CLI version.
6. Proxy-enabled and direct runs can be distinguished using verifiable runtime evidence; unknown states are labeled unknown.
7. Original evidence remains retrievable when required; failed recovery is reported as a limitation.
8. High and Critical findings are verified against original content.
9. Secrets remain redacted in findings, intermediate results, logs, and reports.
10. All required assessment categories, statuses, report sections, and scores remain intact; incomplete, failed, skipped, and unavailable states are visible.