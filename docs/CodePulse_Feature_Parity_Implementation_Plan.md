# CodePulse Feature Parity Implementation Plan

This plan separates the conversational skill experience from the deterministic finder and comparison engines. That preserves CodePulse’s existing slash-command model while making parity analysis repeatable, testable, reviewable, and economical for large repositories.

CodePulse is currently positioned as a set of focused, repeatable application-health skills, with individual slash commands available from Copilot Chat. The proposed parity capabilities should follow that delivery pattern but introduce structured intermediate artifacts instead of relying exclusively on model-generated narrative.

---

# 1. Implementation Objective

Build two new CodePulse capabilities:

## Feature Parity Finder

Discovers user-observable and system-level capabilities in one repository and produces a reviewable feature manifest.

```text
/codepulse-feature-parity-finder
```

## Feature Parity

Compares two feature manifests, repositories, or a repository against requirements and produces an evidence-backed parity report.

```text
/codepulse-feature-parity
```

## Shared engine

Both skills use a common engine responsible for:

- Source validation
- Repository traversal
- Evidence extraction
- Capability normalization
- Stable feature identification
- Manifest validation
- Feature matching
- Confidence calculation
- Report generation

---

# 2. Design Principles

The developer should implement the following principles as requirements, not suggestions.

## 2.1 Skills are orchestration layers

The skill files should:

- Determine the user’s intent.
- Parse arguments or prompt for missing values.
- Validate the requested operation.
- Invoke the appropriate engine command.
- Explain unresolved questions.
- Summarize the generated artifacts.

The skill must not attempt to perform the full discovery or comparison through prompt reasoning alone.

## 2.2 Evidence is mandatory

No discovered capability should be included without at least one evidence item.

Valid evidence includes:

- Route
- UI page or component
- Controller or endpoint
- Application service
- Command or query handler
- Scheduled job
- Integration
- Authorization policy
- Database operation
- Automated test
- Requirement
- Documentation
- Feature flag
- Report definition
- Configuration entry

## 2.3 Results require human validation

Feature discovery is an assessment, not an authoritative requirements source.

The engine must distinguish:

- Confirmed by multiple evidence types
- Strongly inferred
- Weakly inferred
- Unable to verify
- Requires subject-matter-expert review

## 2.4 Domain-specific context is extensible

The engine must support application-specific references, naming rules, architecture conventions, and exclusion rules. Domain-specific material should supplement generic skill guidance.

## 2.5 Feature parity is not code parity

Two systems may implement the same business capability using completely different:

- Frameworks
- UI structures
- APIs
- Database schemas
- Integration patterns
- Architectural boundaries

The engine must compare observable behavior and business capability, not filenames or classes alone.

---

# 3. Proposed Repository Structure

```text
.agents/
  skills/
    codepulse-feature-parity-finder/
      SKILL.md

    codepulse-feature-parity/
      SKILL.md

    codepulse/
      references/
        feature-manifest-schema.json
        feature-parity-config-schema.json
        feature-classification.md
        feature-evidence-model.md
        feature-confidence-model.md
        feature-matching-rules.md
        feature-parity-report-template.html
        feature-inventory-report-template.html

  tools/
    feature-parity/
      README.md
      finder.*
      comparer.*
      validate.*
      render.*
      adapters/
        generic.*
        dotnet.*
        vue.*
        angularjs.*
        coldfusion.*
      tests/
        fixtures/
        unit/
        integration/
        snapshots/

codepulse.config.json
```

If CodePulse already has a standard location for executable scripts, use that location instead of introducing `.agents/tools`. The logical separation should remain the same.

---

# 4. Command Syntax

The user should be able to use either a guided prompt or explicit arguments.

The first release should use a simple `key: value` syntax because it is readable in chat, easy for the skill to parse, and does not require assuming that the slash command itself supports formal CLI flags.

## 4.1 Finder: minimal command

```text
/codepulse-feature-parity-finder
```

Expected behavior:

1. Check whether a current workspace or repository is available.
2. If found, propose it as the source.
3. Ask only for information that cannot be inferred.
4. Display a run summary before beginning if material ambiguity remains.

## 4.2 Finder: natural-language command

```text
/codepulse-feature-parity-finder
Analyze the current repository and discover all business features.
```

```text
/codepulse-feature-parity-finder
Build a feature inventory for PMK Legacy.
```

The skill should extract what it can but still convert the request into a normalized invocation model.

## 4.3 Finder: structured command

```text
/codepulse-feature-parity-finder

source: .
scope: all
output: ./codepulse-results/pmk-legacy
application-name: PMK Legacy
```

Extended example:

```text
/codepulse-feature-parity-finder

source: ../PMK-Legacy
application-name: PMK Legacy
scope: business, ui, api, integrations, reports, jobs
include: src, database, docs, tests
exclude: bin, obj, node_modules, vendor, generated
requirements: ./docs/requirements
config: ./codepulse.config.json
output: ./codepulse-results/pmk-legacy
confidence-threshold: medium
```

## 4.4 Finder command fields

### Required after inference

- `source`

### Optional

- `application-name`
- `scope`
- `include`
- `exclude`
- `requirements`
- `documentation`
- `config`
- `output`
- `confidence-threshold`
- `incremental`
- `format`
- `dry-run`

### Allowed `scope` values

```text
all
business
ui
api
integrations
reports
jobs
authorization
data-operations
```

Multiple values should be comma-separated.

### Allowed `confidence-threshold` values

```text
low
medium
high
```

Default:

```text
medium
```

### Allowed `format` values

```text
json
html
markdown
all
```

Default:

```text
all
```

## 4.5 Parity: minimal command

```text
/codepulse-feature-parity
```

The skill should determine whether the current workspace contains:

- Two manifests
- A manifest and a repository
- Two repository paths
- A repository and requirements
- Previously generated CodePulse artifacts

If the comparison inputs cannot be inferred, prompt the user to select the comparison mode.

## 4.6 Parity: manifest comparison

```text
/codepulse-feature-parity

source: ./codepulse-results/pmk-legacy/feature-manifest.json
target: ./codepulse-results/pmk-rewrite/feature-manifest.json
output: ./codepulse-results/pmk-parity
```

## 4.7 Parity: repository comparison

```text
/codepulse-feature-parity

source: ../PMK-Legacy
target: ../PMK-Rewrite
discover: true
output: ./codepulse-results/pmk-parity
```

When `discover: true`, the parity skill should invoke Finder for each repository and then pass the generated manifests to the comparison engine.

## 4.8 Parity: requirements coverage

```text
/codepulse-feature-parity

baseline: ./docs/PMK-MVP-Requirements
target: ../PMK-Rewrite
mode: requirements-coverage
output: ./codepulse-results/pmk-mvp-coverage
```

## 4.9 Parity command fields

### Required after inference

One of:

```text
source + target
baseline + target
```

### Optional

- `mode`
- `discover`
- `requirements`
- `config`
- `output`
- `minimum-confidence`
- `include`
- `exclude`
- `format`
- `fail-on`
- `dry-run`

### Allowed `mode` values

```text
manifest-to-manifest
repo-to-repo
requirements-coverage
baseline-to-target
```

### Allowed `fail-on` values

```text
never
missing
partial
unverified
high-risk-gap
```

Default:

```text
never
```

For the initial interactive release, parity findings should not cause execution failure unless the user explicitly requests gating behavior.

---

# 5. Prompt Flow Requirements

The skills should implement slot-filling behavior. They should gather required values, infer reasonable defaults, and avoid asking about information that can be discovered safely.

## 5.1 Finder prompt flow

### Step 1: Detect repository context

If a repository is available:

```text
I found the current workspace repository:

Source: /workspace/PMK-Rewrite

Would you like me to use this repository?
1. Use the current repository
2. Provide another local path
3. Provide an existing feature manifest
```

If no repository is available:

```text
I need a source to analyze.

Provide one of the following:
1. A local repository path
2. A workspace-relative repository path
3. An existing feature manifest

Example:
source: ../PMK-Legacy
```

A remote Git URL should only be accepted if the runtime is explicitly capable of cloning or reading it. Otherwise, the skill must instruct the user to clone or open the repository locally rather than pretending it can inspect the URL.

### Step 2: Determine discovery scope

Default behavior should favor a complete scan:

```text
What should I include in the feature inventory?

1. All capabilities
2. Business and user-facing features only
3. API and integration capabilities
4. Custom scope

Recommended: All capabilities
```

If the user chooses custom scope:

```text
Select one or more:
- UI
- API
- Integrations
- Reports
- Scheduled jobs
- Authorization
- Data operations
```

### Step 3: Offer supporting sources

```text
Do you have supporting material that should be used as evidence?

Examples:
- Requirements
- User stories
- Architecture documentation
- Existing feature lists
- Test cases

Enter paths separated by commas, or enter "none."
```

This question should be optional. The scan must be able to proceed without supporting documentation.

### Step 4: Confirm exclusions

The engine should auto-detect standard exclusions and display them:

```text
The following directories will be excluded:

- .git
- bin
- obj
- node_modules
- packages
- dist
- build
- generated
- vendor

Provide additional exclusions, or enter "continue."
```

Do not require the user to approve standard exclusions unless an exclusion might remove application-owned source.

### Step 5: Execution summary

```text
Feature discovery configuration

Application: PMK Legacy
Source: ../PMK-Legacy
Scope: All capabilities
Supporting material: ./docs/requirements
Confidence threshold: Medium
Output: ./codepulse-results/pmk-legacy

I have enough information to begin.
```

If the execution environment requires action confirmation, this is the confirmation boundary. Otherwise, the skill should proceed immediately once required inputs are resolved.

### Step 6: Completion response

```text
Feature discovery completed.

Artifacts:
- feature-manifest.json
- feature-inventory.html
- review-queue.json
- discovery-log.json

Summary:
- Confirmed features: [engine value]
- Probable features: [engine value]
- Needs review: [engine value]
- Excluded candidates: [engine value]

Review the items in review-queue.json before treating the manifest as an approved baseline.
```

Counts must come from engine output. The skill must never calculate or invent them independently.

## 5.2 Parity prompt flow

### Step 1: Determine comparison mode

```text
What would you like to compare?

1. Feature manifest to feature manifest
2. Repository to repository
3. Requirements to repository
4. Baseline manifest to repository
```

### Step 2: Collect baseline

```text
Provide the baseline source.

Example:
source: ./manifests/PMK-Legacy.feature-manifest.json
```

### Step 3: Collect target

```text
Provide the target implementation.

Example:
target: ../PMK-Rewrite
```

### Step 4: Handle missing manifests

If either source is a repository:

```text
The target is a repository rather than a feature manifest.

I can run Feature Parity Finder first and use the generated manifest for this comparison.
```

The skill then invokes Finder as an internal prerequisite. It should not ask the user to manually invoke the second skill.

### Step 5: Ask about intentional changes

```text
Do you have an approved-decision file identifying intentionally removed, replaced, or changed features?

Example:
decisions: ./docs/parity-decisions.json

Enter a path or "none."
```

This is optional but important because an intentional redesign must not automatically be reported as an unexplained gap.

### Step 6: Display comparison summary

```text
Parity comparison configuration

Baseline: PMK Legacy manifest
Target: PMK Rewrite repository
Mode: Baseline to target
Target discovery: Required
Approved decisions: ./docs/parity-decisions.json
Output: ./codepulse-results/pmk-parity
```

### Step 7: Completion response

```text
Feature parity analysis completed.

Artifacts:
- parity-report.html
- parity-results.json
- unmatched-features.json
- review-queue.json
- comparison-log.json

Important:
This result identifies evidence-backed matches and potential gaps. Items marked "Needs SME validation" require product or operational review.
```

---

# 6. Input Resolution Rules

The skill needs a deterministic precedence order.

## 6.1 Precedence

Use input values in this order:

1. Explicit structured arguments
2. Explicit natural-language instruction
3. Current workspace context
4. Repository-level CodePulse configuration
5. Skill defaults
6. Ask the user

## 6.2 Do not ask when

The skill must not ask for a value when:

- A valid source is explicitly provided.
- The current repository is available and the user says “this repo.”
- An output path can safely use the default.
- The default scope is `all`.
- Standard exclusions can be auto-detected.
- A previous step in the same invocation already supplied the value.

## 6.3 Ask when

The skill must ask when:

- Multiple repositories could reasonably be the intended source.
- A path does not exist.
- A path resolves outside the permitted workspace.
- The source and target resolve to the same repository or manifest.
- The comparison direction is ambiguous.
- A required source cannot be accessed.
- Multiple candidate manifests are found with no clear newest or approved version.
- A remote repository URL is supplied but remote access is unavailable.

---

# 7. Feature Manifest Requirements

The Finder engine’s primary output is a versioned JSON document.

## 7.1 Manifest envelope

```json
{
  "schemaVersion": "1.0",
  "generator": {
    "name": "CodePulse Feature Parity Finder",
    "version": "1.0.0"
  },
  "application": {
    "name": "PMK Legacy",
    "sourceType": "repository",
    "sourceLocation": "../PMK-Legacy",
    "revision": "git-commit-or-null"
  },
  "scan": {
    "scopes": [
      "business",
      "ui",
      "api",
      "integrations",
      "reports",
      "jobs",
      "authorization",
      "data-operations"
    ],
    "includes": [],
    "excludes": [],
    "startedAt": "ISO-8601",
    "completedAt": "ISO-8601"
  },
  "features": [],
  "reviewQueue": [],
  "statistics": {}
}
```

## 7.2 Feature record

```json
{
  "id": "user-management.create-user",
  "name": "Create User",
  "description": "Allows an authorized administrator to create a user account.",
  "domain": "User Management",
  "capabilityType": "business",
  "actors": [
    "Administrator"
  ],
  "inputs": [
    "User profile"
  ],
  "outputs": [
    "User account"
  ],
  "preconditions": [
    "Actor has user-management permission"
  ],
  "behaviors": [
    "Validates required profile data",
    "Creates the user account",
    "Assigns initial access"
  ],
  "evidence": [],
  "confidence": {
    "level": "high",
    "score": 0.91,
    "reasons": []
  },
  "status": "discovered",
  "requiresHumanValidation": false,
  "tags": [
    "administration",
    "security"
  ]
}
```

## 7.3 Evidence record

```json
{
  "type": "route",
  "location": "src/Admin/Users/CreateUser.vue",
  "symbol": "CreateUser",
  "lineStart": 1,
  "lineEnd": 180,
  "summary": "Administrative page for creating users.",
  "strength": "strong",
  "contentHash": "optional-hash"
}
```

## 7.4 Review queue record

```json
{
  "candidateId": "candidate-0042",
  "proposedName": "Bulk Customer Import",
  "reason": "UI and database evidence found, but no reachable route was identified.",
  "evidenceRefs": [
    "evidence-21",
    "evidence-22"
  ],
  "recommendedAction": "Confirm whether the import is active or obsolete."
}
```

---

# 8. Finder Engine Functional Requirements

## 8.1 Source validation

The engine must:

- Verify the source exists.
- Verify it is readable.
- Detect whether it is a repository, directory, manifest, or document collection.
- Resolve canonical paths.
- Prevent unintended path traversal outside configured boundaries.
- Record the Git revision when available.
- Refuse to log secrets or credentials.

## 8.2 Repository inventory

The engine must produce an inventory containing:

- File path
- File type
- File size
- Language
- Generated/vendor classification
- Content hash
- Last-known source revision, when available
- Adapter assignment
- Exclusion reason, when excluded

## 8.3 Technology detection

The engine must detect likely technology stacks from project markers.

Initial target adapters should support:

- .NET Framework
- ASP.NET Core
- Vue
- AngularJS
- ColdFusion
- SQL Server scripts
- Generic REST/OpenAPI
- Generic documentation and tests

Unknown technologies must fall back to a generic adapter rather than terminating the scan.

## 8.4 Evidence extractors

The engine must support pluggable extractors.

### UI extractor

Detect:

- Routes
- Pages
- Views
- Forms
- Navigation items
- User actions
- Validation rules
- Conditional visibility
- Role restrictions

### API extractor

Detect:

- Endpoints
- HTTP methods
- Request and response models
- Authorization requirements
- External versus internal exposure
- Versioning
- Documented behavior

### Business-logic extractor

Detect:

- Application services
- Use cases
- Commands
- Queries
- Handlers
- Domain services
- Workflow/state changes
- Validation and decision rules

### Integration extractor

Detect:

- External APIs
- Message queues
- Events
- Webhooks
- File transfer
- Email notifications
- Scheduled synchronization
- SSIS-style or batch integration references

### Report extractor

Detect:

- Named reports
- Exports
- Print outputs
- Search results
- Dashboards
- Scheduled report delivery

### Background-work extractor

Detect:

- Scheduled jobs
- Hosted services
- Queue consumers
- Batch processes
- Retry processing
- Cleanup jobs

### Security extractor

Detect:

- Roles
- Claims
- Permissions
- Policies
- Anonymous access
- Administrative-only capabilities
- Tenant boundaries

### Data-operation extractor

Detect user-meaningful operations such as:

- Import
- Export
- Archive
- Restore
- Approve
- Publish
- Activate
- Clone
- Search
- Bulk edit

Database tables alone must not be promoted to features without behavioral evidence.

### Test and documentation extractor

Detect:

- Test names
- Acceptance criteria
- Gherkin scenarios
- User stories
- Requirements
- README descriptions
- ADRs
- Architecture descriptions

Documentation should supplement code evidence. It must not silently override conflicting implementation evidence.

## 8.5 Candidate generation

The engine must generate raw capability candidates from extracted evidence.

A candidate should include:

- Proposed name
- Proposed domain
- Capability type
- Evidence references
- Source adapter
- Discovery rule
- Preliminary confidence
- Candidate fingerprint

## 8.6 Candidate normalization

Normalization must:

- Convert names into verb-object format where practical.
- Remove purely technical suffixes such as `Controller`, `Service`, and `Component`.
- Normalize common synonyms through a configurable dictionary.
- Preserve meaningful domain terminology.
- Split compound candidates when they represent multiple user outcomes.
- Merge duplicate evidence for the same likely capability.
- Avoid merging features solely because they share a noun.

Examples:

```text
UserCreateController
CreateUser.vue
POST /api/users
CreateUserCommand
```

should be candidates for:

```text
Create User
```

However:

```text
View User
Edit User
Disable User
```

must remain separate capabilities unless configuration explicitly groups them.

## 8.7 Domain classification

The engine should classify each feature into a domain using this precedence:

1. Explicit repository mapping
2. Requirements or documentation mapping
3. Namespace/module mapping
4. Route grouping
5. Model-assisted classification
6. `Unclassified`

The engine must never discard a feature because its domain is unknown.

## 8.8 Stable feature IDs

Feature IDs should use normalized domain and capability names:

```text
user-management.create-user
orders.route-order-to-vendor
reporting.export-customer-summary
```

If collisions occur, add a stable qualifier derived from behavior, not a sequential number wherever possible.

Poor:

```text
orders.search-2
```

Preferred:

```text
orders.search-by-customer
orders.search-by-order-number
```

## 8.9 Confidence scoring

Confidence should be calculated from explicit evidence factors.

Recommended initial model:

- Strong executable entry point: positive weight
- UI plus backend evidence: positive weight
- Test or acceptance criteria: positive weight
- Multiple independent evidence types: positive weight
- Reachability from route/menu/API: positive weight
- Documentation only: limited weight
- Commented code only: negative weight
- Dead or unreachable code indicator: negative weight
- Conflicting evidence: negative weight
- Generated-code-only evidence: negative weight

Store both:

```json
{
  "level": "medium",
  "score": 0.67,
  "reasons": [
    "UI route found",
    "Backend handler found",
    "No test or documentation evidence found"
  ]
}
```

Thresholds must be configurable.

## 8.10 Reachability analysis

Where practical, the Finder should determine whether a candidate can be reached from:

- An application route
- A menu
- An API route
- A scheduled job registration
- An event subscription
- A command handler
- A referenced integration

Unreachable code should appear in the review queue rather than automatically becoming a confirmed feature.

## 8.11 Secret and sensitive-data handling

The Finder must:

- Never include secret values in evidence excerpts.
- Redact connection strings, tokens, passwords, certificates, and keys.
- Avoid copying customer data or personally identifiable records.
- Store file locations and safe summaries rather than unrestricted source excerpts.
- Support configurable forbidden paths and file patterns.
- Mark redaction events in the discovery log.

## 8.12 Incremental scanning

The engine should support:

```text
incremental: true
```

Incremental mode should:

- Load the previous manifest.
- Compare Git revision and file hashes.
- Rescan changed files.
- Re-evaluate candidates affected by changed dependencies.
- Preserve reviewed feature metadata when evidence remains valid.
- Mark removed evidence.
- Identify newly orphaned features.
- Avoid regenerating unchanged evidence summaries.

---

# 9. Human Review Workflow

The Finder must treat the manifest as draft until reviewed.

## 9.1 Feature statuses

```text
discovered
confirmed
rejected
merged
split
deprecated
needs-review
```

## 9.2 Review decisions

A reviewer must be able to:

- Confirm a feature.
- Edit its name.
- Assign or change its domain.
- Reject it as technical implementation detail.
- Mark it obsolete.
- Merge it with another feature.
- Split it into multiple features.
- Add missing evidence.
- Mark the feature intentionally excluded from parity.
- Add product-owner notes.

## 9.3 Review artifact

The first release may use JSON or YAML:

```json
{
  "featureId": "user-management.create-user",
  "decision": "confirmed",
  "reviewerNote": "Active administrative workflow.",
  "aliases": [
    "Add User",
    "User Registration by Admin"
  ]
}
```

The engine should apply review decisions on future runs and avoid overwriting them without reporting a conflict.

---

# 10. Parity Comparison Requirements

Although Finder is the first dependency, the implementation should define comparison contracts early so the manifest supports them.

## 10.1 Comparison statuses

```text
equivalent
partial
changed-intentionally
replaced
missing
new-in-target
not-applicable
unable-to-verify
needs-sme-validation
```

## 10.2 Matching stages

Use a staged approach:

### Stage 1: Exact stable ID

```text
user-management.create-user
```

### Stage 2: Alias match

Match approved aliases and historical names.

### Stage 3: Domain and behavior match

Compare:

- Domain
- Actors
- Inputs
- Outputs
- Preconditions
- Behaviors

### Stage 4: Evidence-semantic match

Use model-assisted reasoning only after deterministic matching cannot resolve the feature.

### Stage 5: Human review

Low-confidence or one-to-many matches enter the review queue.

## 10.3 Match record

```json
{
  "baselineFeatureId": "user-management.create-user",
  "targetFeatureIds": [
    "identity.admin-provision-user"
  ],
  "status": "equivalent",
  "confidence": {
    "level": "high",
    "score": 0.89
  },
  "rationale": [
    "Same administrator actor",
    "Equivalent user creation outcome",
    "Equivalent validation behavior"
  ],
  "baselineEvidence": [],
  "targetEvidence": [],
  "differences": [],
  "requiresHumanValidation": false
}
```

## 10.4 Partial parity

A feature is `partial` when the target implements only part of the outcome or behavior.

Example:

```text
Baseline customer search supports:
- Customer number
- Company name
- Contact email

Target supports:
- Customer number
- Company name

Result: Partial

Potential gap:
- Contact-email search
```

## 10.5 Intentional differences

Support a decision file:

```json
{
  "baselineFeatureId": "users.reset-password-question",
  "decision": "replaced",
  "targetFeatureId": "identity.self-service-password-reset",
  "reason": "Legacy security-question workflow replaced by the approved identity-provider workflow.",
  "approvedReference": "ADR-014"
}
```

Approved decisions should affect status but must not erase the underlying difference.

---

# 11. Reports and Output Artifacts

## 11.1 Finder outputs

Required:

```text
feature-manifest.json
feature-inventory.html
review-queue.json
discovery-log.json
```

Optional:

```text
feature-inventory.md
evidence-index.json
repository-inventory.json
```

## 11.2 Parity outputs

Required:

```text
parity-results.json
parity-report.html
review-queue.json
comparison-log.json
```

Optional:

```text
parity-summary.md
missing-features.json
partial-features.json
new-target-features.json
```

## 11.3 Finder report sections

- Executive summary
- Discovery scope
- Repository and revision
- Methodology
- Features by domain
- Features by capability type
- Confidence distribution
- Evidence coverage
- Items needing review
- Excluded candidates
- Scan limitations
- Artifact references

## 11.4 Parity report sections

- Executive summary
- Comparison scope
- Baseline and target revisions
- Overall parity coverage
- Equivalent capabilities
- Partial capabilities
- Missing capabilities
- Intentionally changed capabilities
- Replaced capabilities
- New target capabilities
- Unable-to-verify items
- High-risk gaps
- Review queue
- Methodology and limitations

A percentage may be included, but it must not obscure unresolved items. The report should show how the percentage was calculated and exclude `unable-to-verify` from the denominator unless configuration says otherwise.

---

# 12. Configuration Requirements

Add a repository-level configuration file.

```json
{
  "featureParity": {
    "applicationName": "PMK",
    "defaultScope": [
      "business",
      "ui",
      "api",
      "integrations",
      "reports",
      "jobs",
      "authorization"
    ],
    "include": [
      "src/**",
      "database/**",
      "docs/**",
      "tests/**"
    ],
    "exclude": [
      "**/bin/**",
      "**/obj/**",
      "**/node_modules/**",
      "**/generated/**"
    ],
    "domainMappings": [
      {
        "pattern": "src/UserManagement/**",
        "domain": "User Management"
      }
    ],
    "synonyms": {
      "customer": [
        "client",
        "account"
      ],
      "disable-user": [
        "deactivate-user",
        "inactivate-user"
      ]
    },
    "minimumConfidence": "medium",
    "redactPatterns": [
      "**/appsettings.*.json",
      "**/*.pfx",
      "**/*.key"
    ]
  }
}
```

Project-specific configuration must augment rather than modify the generic CodePulse skill.

---

# 13. Suggested Engine Interface

The engine should expose a CLI-style contract even when invoked by a skill. This makes it independently testable and usable in CI later.

## Finder

```text
codepulse parity find \
  --source ../PMK-Legacy \
  --config ./codepulse.config.json \
  --scope all \
  --output ./codepulse-results/pmk-legacy \
  --format all
```

## Compare

```text
codepulse parity compare \
  --source ./manifests/pmk-legacy.json \
  --target ./manifests/pmk-rewrite.json \
  --decisions ./docs/parity-decisions.json \
  --output ./codepulse-results/pmk-parity \
  --format all
```

## Validate manifest

```text
codepulse parity validate \
  --manifest ./manifests/pmk-legacy.json
```

## Reapply review decisions

```text
codepulse parity reconcile \
  --manifest ./manifests/pmk-legacy.json \
  --reviews ./reviews/pmk-legacy-reviews.json
```

Exit codes should distinguish:

```text
0 = completed successfully
1 = invalid arguments or configuration
2 = inaccessible source
3 = invalid manifest
4 = engine failure
5 = policy or security restriction
6 = parity gate failed
```

---

# 14. Skill Requirements

## 14.1 Finder `SKILL.md`

The Finder skill should contain:

- Purpose
- Trigger conditions
- Explicit non-goals
- Supported input styles
- Slot definitions
- Input precedence rules
- Prompt flow
- Validation rules
- Engine invocation contract
- Output requirements
- Failure handling
- Security requirements
- References to shared schemas and templates

Suggested description:

```yaml
name: codepulse-feature-parity-finder
description: Discovers business, user-facing, API, integration, reporting, scheduled, authorization, and data-operation capabilities in an application repository and produces an evidence-backed feature manifest for review or later parity comparison. Use when the user asks to identify application features, build a capability inventory, prepare a rewrite baseline, or generate input for a feature parity assessment.
```

## 14.2 Parity `SKILL.md`

Suggested description:

```yaml
name: codepulse-feature-parity
description: Compares two application capability manifests, repositories, or a requirements baseline against a target implementation. Produces an evidence-backed feature parity report identifying equivalent, partial, missing, replaced, intentionally changed, new, and unverified capabilities.
```

## 14.3 Skill guardrails

Both skills must state:

- Do not claim business completeness based solely on static code.
- Do not equate file or class similarity with feature equivalence.
- Do not treat dead or unreachable code as a confirmed feature.
- Do not expose secret values.
- Do not silently omit low-confidence candidates.
- Do not invent requirements.
- Do not declare intentional removal without an approved decision artifact.
- Do not overwrite reviewed manifests without reconciliation.
- Do not calculate counts independently of engine output.

---

# 15. Error and Recovery Flows

## Invalid repository path

```text
I could not access the specified source:

../PMK-Legacy

Provide an existing local or workspace-relative repository path.
```

## Remote URL cannot be accessed

```text
The repository URL identifies the source, but this runtime cannot inspect remote repository contents directly.

Clone or open the repository in the current workspace, then provide its local path.
```

## No features found

```text
The scan completed, but no qualifying features met the current evidence threshold.

Possible causes:
- The selected scope excluded the application’s primary capability type.
- The repository uses an unsupported structure.
- Most capabilities are defined outside the scanned paths.
- The confidence threshold is too restrictive.

Review discovery-log.json and repository-inventory.json before rerunning.
```

## Conflicting manifests

```text
Multiple feature manifests were found, and I cannot determine which one is the approved baseline.

Provide the path to the manifest that should be used.
```

## Partial engine failure

The engine should preserve valid intermediate output and write:

```text
run-status.json
```

It should include:

- Completed stages
- Failed stage
- Error category
- Safe error message
- Whether the run can resume
- Intermediate artifact locations

---

# 16. Testing Requirements

This feature should have both conventional software tests and skill behavior tests.

## 16.1 Unit tests

Test:

- Path validation
- Configuration loading
- Exclusion matching
- Technology detection
- Candidate normalization
- Stable ID generation
- Alias matching
- Confidence calculation
- Manifest validation
- Decision-file application
- Parity status assignment
- Secret redaction

## 16.2 Adapter fixture tests

Create small representative applications containing:

- .NET controller and Vue page implementing one capability
- API-only capability
- Scheduled job
- Integration
- Report
- Role-restricted feature
- Dead route
- Commented-out implementation
- Generated source
- Duplicate UI and backend representations
- Renamed target feature
- Split target feature
- Consolidated target feature

Expected manifests should be stored as snapshots.

## 16.3 End-to-end scenarios

### Scenario A: Finder on a single application

Expected:

- Manifest validates.
- Duplicates are consolidated.
- Dead code is not confirmed.
- Evidence paths resolve.
- Review queue is generated.

### Scenario B: Equivalent rewrite

Expected:

- Equivalent capabilities match despite different architecture and names.

### Scenario C: Partial rewrite

Expected:

- Missing sub-behavior results in `partial`, not `equivalent`.

### Scenario D: Intentional replacement

Expected:

- Approved decision produces `replaced`.
- Original difference remains visible in the report.

### Scenario E: Unsupported technology

Expected:

- Generic adapter executes.
- Limitations are documented.
- Scan does not fail solely because no dedicated adapter exists.

### Scenario F: Secret redaction

Expected:

- No credential values appear in any artifact or log.

## 16.4 Prompt-flow tests

Test the skill with:

```text
/codepulse-feature-parity-finder
```

```text
/codepulse-feature-parity-finder
Run on this repo.
```

```text
/codepulse-feature-parity-finder
source: ../PMK-Legacy
scope: ui, api
```

```text
/codepulse-feature-parity
Compare this repo to ../PMK-Legacy.
```

```text
/codepulse-feature-parity
source: legacy.json
target: rewrite.json
```

Verify:

- No unnecessary question is asked.
- Missing required input is requested.
- Defaults are disclosed.
- Invalid paths are rejected.
- Engine output is summarized accurately.
- The model does not invent engine statistics.

---

# 17. Acceptance Criteria

## Finder MVP

The MVP is complete when:

- The Finder skill accepts guided and structured input.
- It can analyze a local repository.
- It supports generic, .NET, Vue, AngularJS, ColdFusion, and documentation extraction at the agreed initial depth.
- It produces a schema-valid manifest.
- Every feature has evidence.
- Low-confidence findings enter the review queue.
- Standard generated and dependency folders are excluded.
- Sensitive values are redacted.
- Repeated evidence is consolidated.
- Output includes JSON and HTML.
- Unit and fixture tests pass.
- The skill never declares the manifest authoritative without human review.

## Parity MVP

The MVP is complete when:

- The Parity skill accepts manifest-to-manifest comparison.
- It can invoke Finder when a repository is supplied.
- It uses deterministic exact and alias matching before semantic matching.
- It supports all defined comparison statuses.
- It produces evidence-backed match records.
- It supports approved decision files.
- It generates JSON and HTML reports.
- Unresolved matches enter the review queue.
- Report totals come directly from comparison results.
- The comparison is reproducible for unchanged inputs and configuration.

---

# 18. Delivery Sequence

## Phase 1: Contracts and schemas

Build:

- Manifest schema
- Configuration schema
- Review-decision schema
- Parity-result schema
- Evidence model
- Confidence model
- Command contracts
- Sample fixtures

Do this before writing prompt-heavy skill files.

## Phase 2: Finder core

Build:

- Source validator
- Repository inventory
- Exclusion engine
- Technology detector
- Generic extractor interface
- Candidate store
- Normalization
- Stable IDs
- Confidence scoring
- JSON output

## Phase 3: Initial adapters

Implement:

- .NET
- Vue
- AngularJS
- ColdFusion
- Documentation/tests
- Generic API/OpenAPI
- SQL supporting evidence

## Phase 4: Finder skill and guided interaction

Build:

- `SKILL.md`
- Argument parsing guidance
- Prompt state machine
- Context inference
- Error flows
- Completion summary

## Phase 5: Review workflow

Build:

- Review queue
- Decision import
- Manifest reconciliation
- Reviewed metadata preservation
- Conflict reporting

## Phase 6: Comparison engine

Build:

- Exact matching
- Alias matching
- Behavioral matching
- Semantic candidate matching
- Intentional-decision handling
- Parity classifications
- Comparison JSON

## Phase 7: Parity skill and report

Build:

- `SKILL.md`
- Finder orchestration
- Comparison prompt flow
- HTML output
- Leadership summary
- Engineering detail
- Review queue

## Phase 8: Incremental mode and pipeline readiness

Build:

- Hash-based incremental scans
- Git revision tracking
- Parity gates
- Machine-readable exit codes
- CI examples
- Snapshot regression testing

---

# 19. Recommended MVP Boundary

To avoid making the first release too broad, the initial version should support:

1. Local repository or existing manifest inputs
2. .NET, Vue, AngularJS, ColdFusion, tests, and documentation
3. JSON and HTML outputs
4. All-capability and custom-scope scans
5. Manifest review decisions
6. Manifest-to-manifest comparison
7. Repository-to-repository comparison through automatic Finder execution
8. Evidence and confidence on every finding
9. Manual decision file for intentional differences

Defer these until after the core contracts are stable:

- Direct remote-repository cloning
- Browser or runtime crawling
- Database introspection against live systems
- Azure DevOps work-item synchronization
- Automatic product-usage analytics
- CI failure gates
- Graph database storage
- Interactive report editing
- Cross-portfolio feature mining

The architecture should leave room for those capabilities without making them MVP dependencies.

---

# 20. Developer Definition of Done

The developer should not consider the work complete merely because both slash commands generate plausible reports. Completion requires:

- Versioned schemas
- Repeatable engine execution
- Evidence traceability
- Explicit confidence rationale
- Human-review support
- Secret redaction
- Stable IDs
- Test fixtures
- Prompt-flow tests
- Adapter tests
- Snapshot comparisons
- Failure recovery
- Documentation
- Sample commands
- Sample output
- Clear limitations

The most important architectural boundary is this:

> **The skill owns the conversation. The engine owns discovery and comparison. The manifest is the contract between them.**

That boundary will let CodePulse preserve its simple `/codepulse-*` experience while making Feature Parity Finder reliable enough to support PMK and other modernization efforts.
