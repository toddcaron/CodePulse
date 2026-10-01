# CodePulse Full Context Benchmark Record

Use this record to compare a baseline `codepulse-full` run with the shared-repository-inventory workflow. Complete one record per comparable pair. Do not claim a saving when the measurement source, repository state, or required coverage differs.

## Controls

| Field | Value |
|---|---|
| Repository and commit | |
| Working-tree state | |
| CodePulse revision | |
| Assessment prompt | |
| Agent, model, and reasoning setting | |
| Context limit | |
| Caveman mode or no integration | |
| Network and cache conditions | |
| Repetitions and run order | |

## Baseline

| Measure | Value | Measurement source or limitation |
|---|---|---|
| Run ID and date/time | | |
| Duration | | |
| Input tokens or credits | | |
| Output tokens or credits | | |
| Repository inventory reused | No | |
| Capability statuses | | |
| Findings produced / verified / rejected / deduplicated | | |
| High/Critical findings verified against originals | | |
| Original-evidence recovery | | |
| Schema validation | | |
| Required report sections and scores | | |
| Limitations or failures | | |

## Optimized

| Measure | Value | Measurement source or limitation |
|---|---|---|
| Run ID and date/time | | |
| Duration | | |
| Input tokens or credits | | |
| Output tokens or credits | | |
| Repository inventory reused | Yes | |
| Capability statuses | | |
| Findings produced / verified / rejected / deduplicated | | |
| High/Critical findings verified against originals | | |
| Original-evidence recovery | | |
| Schema validation | | |
| Required report sections and scores | | |
| Limitations or failures | | |

## Comparison

| Check | Result | Notes |
|---|---|---|
| Same repository, revision, prompt, and scope | Pass / Fail | |
| All six capability statuses equivalent | Pass / Fail | |
| Verified High/Critical findings preserved | Pass / Fail | |
| Required report sections and scores preserved | Pass / Fail | |
| Report schema validation preserved | Pass / Fail | |
| Evidence limitations or recovery regressions | None / Describe | |
| Token or credit measurement comparable | Yes / No | |
| Duration measurement comparable | Yes / No | |

## Parity Verdict

State `accepted`, `rejected`, or `inconclusive`.

- Accept only when required coverage, evidence fidelity, verified High/Critical findings, schema validation, and report completeness are equivalent.
- Reject when any required category, evidence, schema field, score, or report section regresses.
- Use `inconclusive` when token, credit, or duration telemetry is unavailable or not comparable. Do not estimate savings.