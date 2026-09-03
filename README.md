# CodePulse
AI-powered codebase assessment skills for GitHub Copilot that analyze security, code quality, technical debt, dependency lifecycle, authentication, and application exposure risks.

CodePulse provides a collection of focused GitHub Copilot skills that can be run independently or together to perform a comprehensive application assessment. Each skill analyzes a specific area of the codebase and generates actionable findings, recommendations, and a letter grade.

## Notes on Token Usage
- Token usage will vary depending on the skill chosen, context and size of codebase.
- Highly recommended to install and use Caveman along with Codepulse to minimize token usage: https://github.com/juliusbrussee/caveman

## CodePulse Skills

| Skill                  | Purpose                                               | Key Areas Reviewed                                                                   | Example Prompt                                                             |
| ---------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| **codepulse-full**     | Complete application assessment across all categories | Security, MFA, code quality, dead code, dependencies, exposure, LOC                  | `Run codepulse-full on this repository and generate an executive summary.` |
| **codepulse-loc**      | Measures application size and composition             | Total LOC, language breakdown, large files/modules                                   | `Run codepulse-loc and provide a language breakdown.`                      |
| **codepulse-mfa**      | Reviews authentication and MFA implementation         | MFA enforcement, authentication flows, identity provider integration, bypass risks   | `Run codepulse-mfa and determine whether MFA is implemented correctly.`    |
| **codepulse-vuln**     | Performs security and vulnerability analysis          | OWASP risks, dependency vulnerabilities, CVEs, secrets, injection vulnerabilities    | `Run codepulse-vuln and identify any high-risk findings.`                  |
| **codepulse-vuln-verbose** | Performs exhaustive vulnerability analysis with line-level evidence | Every finding instance, source-to-sink evidence, file and line citations, CVEs | `/codepulse-vuln-verbose on this repo.` |
| **codepulse-quality**  | Evaluates maintainability and code quality            | Complexity, code smells, standards compliance, duplication, architecture consistency | `Run codepulse-quality and identify refactoring opportunities.`            |
| **codepulse-deadcode** | Identifies cleanup opportunities                      | Unused code, unused variables, obsolete classes, dead endpoints, commented-out code  | `Run codepulse-deadcode and identify code safe for removal.`               |
| **codepulse-plm**      | Reviews technology lifecycle health                   | Outdated frameworks, package versions, deprecated libraries, upgrade risk            | `Run codepulse-plm and identify unsupported technologies.`                 |
| **codepulse-ext**      | Reviews external accessibility and exposure risks     | Public endpoints, APIs, webhooks, CORS, anonymous access, attack surface             | `Run codepulse-ext and analyze the application's external exposure.`       |
| **codepulse-exec**      | Converts a report into an executive-level summary.     | Per provided report. Attempts to answer leadership questions and provide investment and strength analysis.             | `/codepulse-exec <report-filepath>`       |

## Common Assessment Scenarios
| Scenario                        | Recommended Skills                                         |
| ------------------------------- | ---------------------------------------------------------- |
| Security Review                 | `codepulse-vuln`, `codepulse-mfa`, `codepulse-ext`         |
| Detailed Security Review        | `codepulse-vuln-verbose`                                   |
| Modernization Planning          | `codepulse-plm`, `codepulse-quality`                       |
| Technical Debt Assessment       | `codepulse-quality`, `codepulse-deadcode`                  |
| Architecture Review             | `codepulse-ext`, `codepulse-mfa`                           |
| Executive Health Report         | `codepulse-full`                                           |
| Pre-Acquisition Due Diligence   | `codepulse-full`                                           |
| Pre-Production Readiness Review | `codepulse-full`, `codepulse-vuln`                         |
| Legacy System Assessment        | `codepulse-plm`, `codepulse-deadcode`, `codepulse-quality` |

# Installation

CodePulse is distributed as a collection of GitHub Copilot custom skills. Each skill resides in its own folder and contains a `SKILL.md` file that defines when the skill should be invoked and the instructions it should follow.

## Prerequisites
- GitHub Copilot with support for custom skills
- Access to a repository that supports custom Copilot skills
- Read/write access to the repository

## Directory Structure

Each CodePulse skill is self-contained so it can be installed and run independently. Its local `references/` folder contains the templates and guidance needed by that skill, and its local `reports/` folder is the default output location.

```text
├── codepulse-full/
│   ├── SKILL.md
│   ├── references/
│   └── reports/
├── codepulse-loc/
│   ├── SKILL.md
│   ├── references/
│   └── reports/
├── codepulse-mfa/
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
└── codepulse-exec/
        ├── SKILL.md
        ├── references/
        └── reports/
```

### Local References

Every skill owns the assets it needs in its local `references/` folder.

| File | Purpose |
|--------|----------|
| `report-template.html` | Standard HTML layout, styling, executive summary format, and report structure |
| `grading-model.md` | Defines grading criteria and score calculations |
| `severity-ratings.md` | Defines Low, Medium, High, and Critical risk ratings where the skill evaluates risk |
| `recommendations-library.md` | Standard remediation guidance where the skill produces recommendations |
| `executive-scorecard-template.html` | Executive report layout used by `codepulse-exec` |

Each `SKILL.md` lists the local references required for that skill. Skills use their local `reports/` folder for generated output.

This approach ensures:

- Consistent report formatting
- Consistent grading across skills
- Consistent severity classifications
- Easier maintenance and future enhancements
- Skills can be installed without a separate shared package

## Installation Methods

Choose one of the following installation methods.

### Method 1 (Recommended): Install with npx

The easiest way to install CodePulse is with the Skills CLI:

```shell
npx skills add toddcaron/CodePulse
```

This installs the self-contained CodePulse skills with their local references and report folders.

This includes:

- codepulse-full
- codepulse-loc
- codepulse-mfa
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

Every skill can be installed separately because its references and report output folder are included in the skill directory.

### Minimum Installation Example

```text
.agents/
└── skills/
    └── codepulse-vuln/
        ├── SKILL.md
        ├── references/
        │   ├── report-template.html
        │   ├── grading-model.md
        │   ├── severity-ratings.md
        │   └── recommendations-library.md
        └── reports/
```

### Important

Install the complete skill folder, including its `references/` and `reports/` subfolders. Omitting the local references may prevent the skill from generating a correctly formatted or graded report.

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

# Reporting Framework

CodePulse skills use the same reporting conventions while keeping their required assets locally available.

When generating reports, skills should reference:

```text
references/report-template.html
```

When assigning grades, skills should reference:

```text
references/grading-model.md
```

When assigning severity levels, skills should reference:

```text
references/severity-ratings.md
```

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

the output follows the same standards, visual design, grading methodology, and risk classification system without requiring another skill package.

# Scoring Model

Each assessment category receives a letter grade.

| Grade | Meaning |
|---------|----------|
| **A** | Excellent |
| **B** | Good |
| **C** | Needs Improvement |
| **D** | High Risk / Significant Concerns |
 

The `codepulse-full` assessment calculates an overall grade based on all assessment categories.

The `codepulse-full` skill can generate a complete HTML assessment report suitable for engineering leadership and architecture reviews.
---

## Quick Start Promps
| Goal                  | Example Prompt                                                                 |
| --------------------- | ---------------------------------------------------------------------- |
| Full Assessment       | `/codepulse-full on this repository.`                               |
| Security Audit        | `/codepulse-vuln summarize the top risks.`                      |
| Verbose Security Audit | `/codepulse-vuln-verbose list every vulnerability with file and line references.` |
| MFA Review            | `/codepulse-mfa identify authentication weaknesses.`            |
| Technology Health     | `/codepulse-plm` |
| Technical Debt Review | `Run codepulse-quality and codepulse-deadcode.`                        |
| Exposure Analysis     | `/codepulse-ext review the application's attack surface.`       |
| Application Sizing    | `/codepulse-loc provide a codebase summary.`                    |
