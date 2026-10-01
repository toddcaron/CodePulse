# CodePulse
AI-powered codebase assessment skills for GitHub Copilot that analyze security, code quality, technical debt, dependency lifecycle, and application exposure risks.

CodePulse provides a collection of focused GitHub Copilot skills that can be run independently or together to perform a comprehensive application assessment. Each skill analyzes a specific area of the codebase and generates actionable findings, recommendations, and a letter grade.

## Notes on Token Usage
- Token usage will vary depending on the skill chosen, context and size of codebase.
- CodePulse includes shared token-efficiency guidance and remains fully functional without Caveman.
- CodePulse may operate alongside Caveman or another token-efficiency companion, but does not download or execute external instructions automatically.
- Optional integration, verification, and benchmarking guidance: [Caveman runtime setup](docs/caveman-runtime-setup.md) and [benchmark plan](docs/caveman-benchmark-plan.md).

## CodePulse Skills

| Skill                  | Purpose                                               | Key Areas Reviewed                                                                   | Example Prompt                                                             |
| ---------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| **codepulse-full**     | Complete application assessment across all categories | Security, code quality, dead code, dependencies, exposure, LOC                       | `Run codepulse-full on this repository and generate an executive summary.` |
| **codepulse-loc**      | Measures application size and composition             | Total LOC, language breakdown, large files/modules                                   | `Run codepulse-loc and provide a language breakdown.`                      |
| **codepulse-vuln**     | Performs security and vulnerability analysis          | OWASP risks, dependency vulnerabilities, CVEs, secrets, injection vulnerabilities    | `Run codepulse-vuln and identify any high-risk findings.`                  |
| **codepulse-vuln-verbose** | Performs exhaustive vulnerability analysis with line-level evidence | Every finding instance, source-to-sink evidence, file and line citations, CVEs | `/codepulse-vuln-verbose on this repo.` |
| **codepulse-quality**  | Evaluates maintainability and code quality            | Readability complexity (cyclomatic, cognitive, accidental), code smells, standards compliance, architecture consistency | `Run codepulse-quality and identify refactoring opportunities.`            |
| **codepulse-deadcode** | Identifies cleanup opportunities                      | Unused code, unused variables, obsolete classes, dead endpoints, commented-out code  | `Run codepulse-deadcode and identify code safe for removal.`               |
| **codepulse-plm**      | Reviews technology lifecycle health                   | Outdated frameworks, package versions, deprecated libraries, upgrade risk            | `Run codepulse-plm and identify unsupported technologies.`                 |
| **codepulse-ext**      | Reviews external accessibility and exposure risks     | Public endpoints, APIs, webhooks, CORS, anonymous access, attack surface             | `Run codepulse-ext and analyze the application's external exposure.`       |
| **codepulse-exec**      | Converts a JSON result into an executive-level summary.     | Per provided `*-result.json`. Attempts to answer leadership questions and provide investment and strength analysis.             | `/codepulse-exec <result-json-filepath>`       |

## Common Assessment Scenarios
| Scenario                        | Recommended Skills                                         |
| ------------------------------- | ---------------------------------------------------------- |
| Security Review                 | `codepulse-vuln`, `codepulse-ext`                          |
| Detailed Security Review        | `codepulse-vuln-verbose`                                   |
| Modernization Planning          | `codepulse-plm`, `codepulse-quality`                       |
| Technical Debt Assessment       | `codepulse-quality`, `codepulse-deadcode`                  |
| Architecture Review             | `codepulse-ext`                                             |
| Executive Health Report         | `codepulse-full`                                           |
| Pre-Acquisition Due Diligence   | `codepulse-full`                                           |
| Pre-Production Readiness Review | `codepulse-full`, `codepulse-vuln`                         |
| Legacy System Assessment        | `codepulse-plm`, `codepulse-deadcode`, `codepulse-quality` |

## How CodePulse Measures Complexity

In CodePulse, complexity means **human readability and maintainability**, not the inherent difficulty of the problem being solved. `codepulse-quality` (and the Code Quality area of `codepulse-full`) evaluates three measures defined in [`codepulse-shared/references/complexity-model.md`](codepulse-shared/references/complexity-model.md):

| Measure | What It Answers | Acceptable | Moderate | High | Very High |
|---|---|---|---|---|---|
| Cyclomatic Complexity | How many independent paths must be understood and tested? | 1–10 | 11–20 | 21–50 | > 50 |
| Cognitive Complexity | How hard is the code to read top to bottom? | 0–15 | 16–25 | > 25 | — |
| Accidental Complexity | What complexity exists that the problem does not require? | Qualitative indicators with an inherent-vs-accidental test | | | |

- **Inherent complexity** (essential business rules, regulatory logic, algorithms) is recorded as context but never deducted.
- Complexity contributes 40% of the Code Quality score (Cyclomatic 10, Cognitive 15, Accidental 15); other quality signals contribute 60%.
- Measurement is tool-first. Installing an analyzer such as `lizard`, `radon`, ESLint `complexity` with `eslint-plugin-sonarjs`, PMD, Roslyn metrics, `gocyclo`, or `gocognit` improves accuracy. Without one, values are manually estimated and findings are marked `partially-verified`.
- Complexity findings use `QUAL-CYC-*`, `QUAL-COG-*`, and `QUAL-ACC-*` IDs.

# Installation

CodePulse is distributed as a collection of GitHub Copilot custom skills. Each skill resides in its own folder and contains a `SKILL.md` file that defines when the skill should be invoked and the instructions it should follow.

## Prerequisites
- GitHub Copilot with support for custom skills
- Access to a repository that supports custom Copilot skills
- Read/write access to the repository

## Directory Structure

Each CodePulse skill can be run independently when installed with the sibling `codepulse-shared/` directory. Shared references are authoritative and prevent grading, severity, recommendation, and reporting guidance from drifting between skills. Each skill retains its local `reports/` folder as the default output location.

```text
├── codepulse-full/
│   ├── SKILL.md
│   ├── references/
│   └── reports/
├── codepulse-loc/
│   ├── SKILL.md
│   ├── references/
│   └── reports/
├── codepulse-vuln/
│   ├── SKILL.md
│   ├── references/
│   └── reports/
├── codepulse-vuln-verbose/
│   ├── SKILL.md
│   ├── references/
│   └── reports/
├── codepulse-quality/
│   ├── SKILL.md
│   ├── references/
│   └── reports/
├── codepulse-deadcode/
│   ├── SKILL.md
│   ├── references/
│   └── reports/
├── codepulse-plm/
│   ├── SKILL.md
│   ├── references/
│   └── reports/
├── codepulse-ext/
│   ├── SKILL.md
│   ├── references/
│   └── reports/
├── codepulse-exec/
│   ├── SKILL.md
│   └── reports/
└── codepulse-shared/
        ├── SKILL.md
        ├── references/
        ├── schemas/
        └── renderers/
```

### Shared References

The `codepulse-shared/` directory is the single source of truth for framework-wide behavior.

| File | Purpose |
|--------|----------|
| `references/runtime-contract.md` | Universal evidence, quality, output, and compatibility rules |
| `references/token-efficiency.md` | Targeted scanning and concise-output rules |
| `references/grading.md` | Grading scale, category weights, and scoring guidance |
| `references/severity.md` | Severity and CVE reporting rules |
| `references/recommendation-priority.md` | Recommendation ordering and formatting |
| `references/recommendations-library.md` | Standard remediation guidance |
| `references/report-standard.md` | Detailed and executive report requirements |
| `references/assessment-methodology.md` | Shared assessment workflow and limitations |
| `references/complexity-model.md` | Readability complexity definitions, measurement, thresholds, and scoring |
| `schemas/finding-schema.json` | Normalized evidence-backed finding contract |
| `schemas/assessment-result-schema.json` | Per-capability assessment result contract |
| `schemas/codepulse-report-schema.json` | Complete detailed or executive report contract |
| `renderers/html-template.md` | Detailed HTML rendering instructions and fixed CSS |
| `renderers/markdown-template.md` | Opt-in Markdown rendering instructions |
| `renderers/executive-summary-template.md` | Executive HTML scorecard rendering instructions |

Each `SKILL.md` lists the local references required for that skill. Reports use schema version `2.0` and follow this sequence:

1. Build and validate a JSON report object against the shared schemas.
2. Write `{skill_name}_{currentDate}-result.json` to the `reports/` folder beside the installed skill's `SKILL.md`, not to the analyzed repository's root or current working directory.
3. Render `{skill_name}_{currentDate}-report.html` from that JSON using the appropriate renderer. Render `{skill_name}_{currentDate}-report.md` only when Markdown is explicitly requested.

`codepulse-exec` reads a detailed `-result.json` file and writes its own executive `-result.json` and HTML report. It does not parse HTML reports.

This approach ensures:

- Consistent report formatting
- Consistent grading across skills
- Consistent severity classifications
- Easier maintenance and future enhancements
- Shared behavior can be updated in one location

## Installation Methods

Choose one of the following installation methods.

### Method 1 (Recommended): Install with npx

The easiest way to install CodePulse is with the Skills CLI:

```shell
npx skills add toddcaron/CodePulse
```

This installs the CodePulse skills together with the required `codepulse-shared/` contract and report folders.

This includes:

- codepulse-shared
- codepulse-full
- codepulse-loc
- codepulse-vuln
- codepulse-vuln-verbose
- codepulse-quality
- codepulse-deadcode
- codepulse-plm
- codepulse-ext
- codepulse-exec

### Method 2: Clone the repository

Clone the repository, then copy the CodePulse skill folders into your skills directory:

```shell
git clone https://github.com/Todd-Caron_Taylor/CodePulse.git
```

Common skills directories include:

```text
.agents/skills/
.github/skills/
.claude/skills/
```

Copy all CodePulse skill folders into the skills directory used by your harness.

### Method 3: Install an individual skill

An individual skill can be installed separately when the installation bundle includes that skill, its `reports/` folder, and the sibling `codepulse-shared/` directory. The shared directory is required; local duplicate generic references are not authoritative.

### Minimum Installation Example

```text
.agents/
└── skills/
        ├── codepulse-vuln/
        │   ├── SKILL.md
        │   └── reports/
        └── codepulse-shared/
                ├── SKILL.md
                ├── references/
                ├── schemas/
                └── renderers/
```

### Important

Install the complete skill bundle, including the skill's `reports/` folder and the sibling `codepulse-shared/` directory. Omitting the shared directory may prevent the skill from applying the required contract, grading, or report standards.

# Verify Installation
After installation, open GitHub Copilot and run:

```text
/codepulse-full run on this repository.
```

Or test a focused assessment:

```text
/codepulse-vuln run on this repo
```
If the assessment executes successfully, CodePulse has been installed correctly.

## Reporting Framework

CodePulse separates report data from report presentation. JSON schemas define the data contract; Markdown renderer files define how that data becomes HTML or Markdown. Skills keep report output folders local to each skill.

When generating reports, skills should read the relevant references, JSON schemas, and renderer listed in their `SKILL.md`. Resolve each skill's `reports/` folder beside that installed `SKILL.md`; never resolve it against the analyzed repository's root or current working directory. Findings preserve exact evidence, stable IDs, provenance, limitations, and recommendations in JSON before presentation is rendered.

This ensures that whether an engineer runs:

```text
codepulse-vuln
```

or

```text
codepulse-vuln-verbose
```

or

```text
codepulse-full
```

the output follows the same standards, data schema, rendering rules, visual design, grading methodology, and risk classification system without requiring another skill package.

# Scoring Model

Each assessment category receives a letter grade.

| Grade | Meaning |
|---------|----------|
| **A** | Excellent |
| **B** | Good |
| **C** | Needs Improvement |
| **D** | High Risk / Significant Concerns |
 

The `codepulse-full` assessment calculates an overall grade based on all assessment categories.

The `codepulse-full` skill can generate a complete HTML assessment report suitable for engineering leadership and architecture reviews. The JSON result remains the authoritative machine-readable report; the HTML is a rendered presentation of that result.
---

## Quick Start Prompts
| Goal                  | Example Prompt                                                                 |
| --------------------- | ---------------------------------------------------------------------- |
| Full Assessment       | `/codepulse-full on this repository.`                               |
| Security Audit        | `/codepulse-vuln summarize the top risks.`                      |
| Verbose Security Audit | `/codepulse-vuln-verbose list every vulnerability with file and line references.` |
| Technology Health     | `/codepulse-plm` |
| Technical Debt Review | `Run codepulse-quality and codepulse-deadcode.`                        |
| Exposure Analysis     | `/codepulse-ext review the application's attack surface.`       |
| Application Sizing    | `/codepulse-loc provide a codebase summary.`                    |
