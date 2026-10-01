# Finding Schema

Every finding is a normalized record with these required fields:

| Field | Requirement |
|---|---|
| `id` | Stable unique identifier, scoped by assessment/category, such as `SEC-004`. |
| `category` | Assessment category. |
| `severity` | `Critical`, `High`, `Medium`, `Low`, or `Informational`, when applicable. |
| `title` | Short descriptive title. |
| `evidence` | Exact repository evidence, including paths and lines where available. |
| `impact` | Security, business, operational, quality, or modernization impact. |
| `recommendation` | Actionable remediation or explicitly stated follow-up. |
| `verificationStatus` | Evidence verification state from the allowed values below. Required for new normalized findings. |
| `sourceRepresentation` | Representation on which the finding was reviewed: original, normalized, compressed, or summarized. Required for new normalized findings. |
| `evidenceRecoveryRequired` | Boolean indicating whether original evidence still must be retrieved or checked. Required for new normalized findings. |
| `evidenceLimitations` | Array of evidence gaps or verification limitations; use an empty array when none apply. Required for new normalized findings. |

Allowed `verificationStatus` values: `verified-original`, `verified-tool-output`, `partially-verified`, `unverified`, and `unavailable`.

Allowed `sourceRepresentation` values: `original`, `normalized`, `compressed`, and `summarized`.

For backward compatibility, consumers may accept legacy records without the four provenance fields. New normalized findings must include them. A confirmed High or Critical finding must not rely only on compressed or summarized content; verify against original content or leave it partially verified, unverified, or unavailable.

Optional fields: `referenceLinks`, `cveInformation`, `affectedComponent`, `confidence`, `remediationPriority`, `estimatedComplexity`, and `status`.

Do not create findings without evidence. Preserve exact evidence. Use the same ID when the same finding is reused; cross-reference it instead of creating a duplicate. Distinct evidence or remediation may justify separate IDs.
