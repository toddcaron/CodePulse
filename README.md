# CodePulse
AI-powered codebase assessment skills for GitHub Copilot that analyze security, code quality, technical debt, dependency lifecycle, authentication, and application exposure risks.

CodePulse provides a collection of focused GitHub Copilot skills that can be run independently or together to perform a comprehensive application assessment. Each skill analyzes a specific area of the codebase and generates actionable findings, recommendations, and a letter grade.

## Notes on Token Usage
- Token usage will vary depending on the skill chosen, context and size of codebase.
- Highly recommended to install and use Caveman along with Codepulse to minimize token usage: https://github.com/juliusbrussee/caveman

## Quick Start
| Goal                  | Example Prompt                                                                 |
| --------------------- | ---------------------------------------------------------------------- |
| Full Assessment       | `/codepulse-full on this repository.`                               |
| Security Audit        | `/codepulse-vuln summarize the top risks.`                      |
| MFA Review            | `/codepulse-mfa identify authentication weaknesses.`            |
| Technology Health     | `/codepulse-plm` |
| Technical Debt Review | `Run codepulse-quality and codepulse-deadcode.`                        |
| Exposure Analysis     | `/codepulse-external review the application's attack surface.`  |
| Application Sizing    | `/codepulse-loc provide a codebase summary.`                    |

## CodePulse Skills

| Skill                  | Purpose                                               | Key Areas Reviewed                                                                   | Example Prompt                                                             |
| ---------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| **codepulse-full**     | Complete application assessment across all categories | Security, MFA, code quality, dead code, dependencies, exposure, LOC                  | `Run codepulse-full on this repository and generate an executive summary.` |
| **codepulse-loc**      | Measures application size and composition             | Total LOC, language breakdown, large files/modules                                   | `Run codepulse-loc and provide a language breakdown.`                      |
| **codepulse-mfa**      | Reviews authentication and MFA implementation         | MFA enforcement, authentication flows, identity provider integration, bypass risks   | `Run codepulse-mfa and determine whether MFA is implemented correctly.`    |
| **codepulse-vuln**     | Performs security and vulnerability analysis          | OWASP risks, dependency vulnerabilities, CVEs, secrets, injection vulnerabilities    | `Run codepulse-vuln and identify any high-risk findings.`                  |
| **codepulse-quality**  | Evaluates maintainability and code quality            | Complexity, code smells, standards compliance, duplication, architecture consistency | `Run codepulse-quality and identify refactoring opportunities.`            |
| **codepulse-deadcode** | Identifies cleanup opportunities                      | Unused code, unused variables, obsolete classes, dead endpoints, commented-out code  | `Run codepulse-deadcode and identify code safe for removal.`               |
| **codepulse-plm**      | Reviews technology lifecycle health                   | Outdated frameworks, package versions, deprecated libraries, upgrade risk            | `Run codepulse-plm and identify unsupported technologies.`                 |
| **codepulse-external** | Reviews external accessibility and exposure risks     | Public endpoints, APIs, webhooks, CORS, anonymous access, attack surface             | `Run codepulse-external and analyze the application's external exposure.`  |

## Common Assessment Scenarios
| Scenario                        | Recommended Skills                                         |
| ------------------------------- | ---------------------------------------------------------- |
| Security Review                 | `codepulse-vuln`, `codepulse-mfa`, `codepulse-external`    |
| Modernization Planning          | `codepulse-plm`, `codepulse-quality`                       |
| Technical Debt Assessment       | `codepulse-quality`, `codepulse-deadcode`                  |
| Architecture Review             | `codepulse-external`, `codepulse-mfa`                      |
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

CodePulse uses a shared reference library to ensure all skills generate reports with a consistent look, feel, grading model, and scoring methodology.

```text
.agents/
└── skills/
    ├── codepulse/
    │   └── references/
    │       ├── report-template.html
    │       ├── grading-model.md
    │       └── severity-ratings.md
    │
    ├── codepulse-full/
    │   └── SKILL.md
    ├── codepulse-loc/
    │   └── SKILL.md
    ├── codepulse-mfa/
    │   └── SKILL.md
    ├── codepulse-vuln/
    │   └── SKILL.md
    ├── codepulse-quality/
    │   └── SKILL.md
    ├── codepulse-deadcode/
    │   └── SKILL.md
    ├── codepulse-plm/
    │   └── SKILL.md
    └── codepulse-external/
        └── SKILL.md
```

### Shared References

The `codepulse/references` folder serves as the central source of truth for all shared assets used across CodePulse skills.

| File | Purpose |
|--------|----------|
| `report-template.html` | Standard HTML layout, styling, executive summary format, and report structure |
| `grading-model.md` | Defines grading criteria and score calculations |
| `severity-ratings.md` | Defines Low, Medium, High, and Critical risk ratings |

All CodePulse skills should reference these files when generating reports and assessments.

This approach ensures:

- Consistent report formatting
- Consistent grading across skills
- Consistent severity classifications
- Easier maintenance and future enhancements
- No duplication of shared assets across skills

## Install the Full Suite

For the best experience, install the entire CodePulse skill collection.

```text
.agents/skills/codepulse
```

***Note*** - If you do not already have a /skill folder created, create one first or copy this repo from the /skills directory level.

This includes:

- codepulse
- codepulse-full
- codepulse-loc
- codepulse-mfa
- codepulse-vuln
- codepulse-quality
- codepulse-deadcode
- codepulse-plm
- codepulse-external

The `codepulse` folder contains shared report templates, grading rules, and severity definitions used by all assessment skills.

Copy the CodePulse folder into your repository:

```text
.agents/skills/
```

Example:

Clone the Repository
```shell
gh repo clone Todd-Caron_Taylor/CodePulse
```

Copy codepulse into your project .agent/skills folder
```bash
cp -R CodePulse/.agents/skills/codepulse ./.agents/skills
```
```shell
Copy-Item -Recurse CodePulse/.agents/skills ./.agents/skills
```

## Install Individual Skills

Individual skills can be installed separately; however, the shared `codepulse` reference library must also be installed.

### Minimum Installation Example

```text
.agents/
└── skills/
    ├── codepulse/
    │   └── references/
    │       ├── report-template.html
    │       ├── grading-model.md
    │       └── severity-ratings.md
    │
    └── codepulse-vuln/
        └── SKILL.md
```

### Important

All CodePulse assessment skills depend on assets located in:

```text
.agents/skills/codepulse/references/
```

Failure to install the shared `codepulse` folder may result in inconsistent report formatting, grading, or assessment outputs.

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

# Shared Reporting Framework

All CodePulse skills use the same reporting framework to ensure a consistent experience across assessments.

When generating reports, skills should reference:

```text
.agents/skills/codepulse/references/report-template.html
```

When assigning grades, skills should reference:

```text
.agents/skills/codepulse/references/grading-model.md
```

When assigning severity levels, skills should reference:

```text
.agents/skills/codepulse/references/severity-ratings.md
```

This ensures that whether an engineer runs:

```text
codepulse-vuln
```

or

```text
codepulse-full
```

the output follows the same standards, visual design, grading methodology, and risk classification system.

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