# Caveman Benchmark Plan

## Objective

Measure whether optional Caveman instructions or Caveman Proxy change analysis cost or assessment outcomes. Accuracy, evidence fidelity, grading integrity, and report completeness are acceptance constraints, not tradeable benchmark metrics. Do not claim savings without comparable measurements.

## Comparison Modes

Run the same assessment in these four modes:

1. **CodePulse only:** no Caveman repo instructions and no proxy.
2. **Repo instructions:** CodePulse with reviewed Caveman repository instructions; no proxy.
3. **Proxy:** CodePulse through a supported Caveman Proxy wrapper; no repo instructions.
4. **Both:** reviewed repository instructions and a supported proxy wrapper.

Record any unavailable mode as not run with a reason. Do not substitute one integration for the other.

For a direct CodePulse context-optimization comparison, also run a baseline and the shared-repository-inventory workflow with the same Caveman mode. Use [the full-context benchmark template](codepulse-full-context-benchmark-template.md) to record both runs. This comparison measures CodePulse workflow reuse; it does not demonstrate Caveman or proxy savings.

## Controls

Keep these consistent where practical and record unavoidable differences:

- Repository, commit, working-tree state, and assessment scope.
- CodePulse version/revision and shared references/schemas.
- Agent/host, agent version, model, reasoning setting, and context limits.
- Build, test, scanner, and repository-inspection commands.
- Prompt, skill set, report schema, and output requirements.
- Network/provider conditions, proxy mode/configuration, and cache state.
- Run order and number of repetitions. Use multiple runs when model variability could change findings; avoid comparing only a favorable single run.

Use an identical baseline repository and discard or isolate generated reports and state between runs. Preserve the original command outputs and report artifacts needed for validation.

## Capture Per Run

Record:

- Run ID, date/time, mode, repository commit, CodePulse version, and active integrations.
- Agent, model, reasoning setting, relevant runtime versions, and proxy/CLI version.
- Direct or wrapped launch command and verifiable runtime evidence that the proxy was active; record unknown when it cannot be verified.
- Duration, credits, input tokens, and output tokens when available, including measurement source and any estimates.
- Required workflows attempted and each workflow status: complete, incomplete, failed, skipped, or unavailable.
- Findings produced, findings verified against originals, findings rejected after validation, and distinct evidence retained after deduplication.
- Report completeness, required sections/scores present, missing evidence, evidence limitations, and assessment failures.
- Original-content recovery success/failure and any secret-redaction issues.

Do not treat proxy-provided compression counts or estimated savings as measured total token savings without an equivalent baseline and comparable measurement source. If token/credit metrics are unavailable or estimates are not comparable, report them as unavailable rather than deriving a savings percentage.

## Review and Comparison

1. Confirm each run covered the same required categories and used the same report schema.
2. Verify every High and Critical finding against the original source or original tool output. Review findings rejected in any mode and material score differences.
3. Compare completeness, verified findings, evidence limitations, failures, and report section/score preservation before considering efficiency.
4. Compare duration and measured token/credit use only when the collection methods and run conditions are comparable. Report spread or variability across repeated runs where available.
5. Document discrepancies, missing metrics, environmental differences, and any proxy bypass or failure. Do not infer that a proxy was active from a command name alone.
6. State conclusions narrowly. No mode is acceptable if it reduces required coverage, loses original evidence, misstates security risk, or weakens report completeness, regardless of cost.

## Result Record

Keep the completed run records and comparison with the assessment artifacts under the team's approved data-retention policy. Do not put credentials, raw secrets, provider keys, session data, or unredacted sensitive source material in benchmark summaries. Preserve exact identifiers and sanitized evidence references needed to reproduce the comparison.

Use [the full-context benchmark template](codepulse-full-context-benchmark-template.md) for every baseline-versus-optimized `codepulse-full` comparison.