# Structured Requirements Contract

Version 0.8 supports one explicitly selected local JSON or marked text/Markdown document.
This is an ingestion contract, not completed requirements coverage analysis or
proof of business completeness. No application code, scripts, tests or services
run, and the engine does not call a model or interpret document text as instructions.

## Input and Provenance

The strict version 1.0 input contains applicationName and requirements. Each
requirement supplies id, name, domain, capabilityType, actors, inputs, outputs,
preconditions, behaviors, acceptanceCriteria and ambiguities. Each behavior has
an id, description and explicit mandatory boolean. Missing contract knowledge
uses empty arrays, not invented roles or conditions. At least one declared
behavior is required per requirement. IDs must be unique within the document;
behavior IDs must be unique within their requirement.

The example under tools/feature-parity/examples/requirements.json is synthetic.
Input strings are preserved verbatim and must contain no secrets or personal
data. Unknown properties, approval fields, engine confidence and totals are not
accepted. JSON is UTF-8 with optional BOM; duplicate keys and non-finite numbers
fail. Source files are bounded to 1 MiB; linked/reparse paths and sensitive names
are excluded. Use stable local filesystems, not concurrently hostile sources.

The importer hashes the exact bytes it parses. Evidence paths are relative to
the selected document's parent and use its filename. JSON has full-file ranges;
marked prose has block-level inclusive source ranges recorded in sourceMap.
JSON record offsets and multi-document path roots are deferred. A requirements
baseline retains original declarations and their canonical digest, the source
byte digest, evidence and explicit requirement-to-feature links. Generated feature
IDs match declared requirement IDs; fingerprints depend on that ID, not labels.
Evidence hashes change with source edits. IDs across applications still need an
explicit identity policy; matching IDs alone never establishes parity.

## Review and Comparison Boundary

All imported features are needs-review, admitted=false, confidence 0.25, with
partially-verified requirement evidence. Every declaration enters the queue;
explicit ambiguity gets a distinct fixed reason. Empty imports keep incomplete
coverage. Declared criteria and ambiguity text remain in the baseline and are
not silently transformed into atomic behaviors or discarded.

Review-template/reconcile can review the generated manifest but cannot upgrade
evidence verification, confidence or admission. The baseline retains the original
requirements even when the generated feature contract is edited. Current
manifest comparison cannot award equivalent credit for these imported features.
Requirements-to-target coverage now uses a separate digest-bound human review
file with resolved contracts and explicit criterion mappings. It does not mutate
the baseline or upgrade its evidence. See feature-requirements-coverage.md.
Advanced target mappings, document contradiction analysis and automated
acceptance-criteria interpretation remain deferred.

## Validation and Publication

`parity validate --requirements-baseline FILE` checks local schemas, preserved
input digest, unique requirement/behavior/evidence IDs, safe paths and line ranges,
source hash consistency and exact requirement/feature/evidence links. Digests
check internal consistency, not authenticated origin, original-file truth or
human approval. A fully rewritten artifact with recomputed hashes is not detected
as an unauthorized revision without an external trusted digest or authority.

Ingestion emits baseline, feature manifest, queue and schema-validated log into a
fresh directory. Original files stay unchanged; invalid batches fail before writes.
Dry-run validates all data/output policy without writes. Staged publication is not
a multi-file transaction; a write failure can leave an incomplete directory.
Consume only runs with all four artifacts. Logs use fixed summaries and engine
counts; source declarations are retained in data artifacts, not printed to stdout.

## Marked Prose

Text/Markdown supports only unindented `Requirement: Title` or ATX headings such
as `## Requirement: Title`. A block captures following nonblank lines until a blank,
heading, new marker, comment or fenced example. Comments, backtick/tilde fences,
quoted and indented markers cannot start proposals. This is an explicit marker
reader, not full Markdown parsing. Tables, arbitrary prose and bullet lists are
not independently interpreted; continuation text remains one unresolved proposal.

Roles, inputs, outputs, preconditions and criteria stay empty. Domain/capability
are Unclassified/business placeholders. Every proposal has an explicit ambiguity
and one behavior with mandatory=false as an unresolved placeholder, not an approved
optional obligation. Offline validation rejects resolved contract claims in prose
baselines, map/evidence disagreement, malformed and overlapping ranges. Human review
may edit the generated feature separately, without rewriting the original baseline.

Provisional IDs hash title and starting line, so source edits can change identity;
cross-scan reconciliation is deferred. The application label defaults to file stem
or explicit --application-name; JSON uses its declared label. Titles are stripped
of trailing whitespace; continuation whitespace is preserved. Source-byte hashes
are exact, while extracted text normalizes line endings. Ignored nonempty lines
are counted, not reproduced. SourceMap and evidence ranges are integrity checks,
not proof of correct interpretation or authenticated source truth.

YAML, PDF, Word documents and collections remain unsupported. General natural-
language requirements interpretation remains deferred; reviewed static baseline
coverage uses the separate approval workflow.
Convert unsupported formats explicitly to structured JSON; conversions remain
unapproved proposals, never invented authoritative obligations.