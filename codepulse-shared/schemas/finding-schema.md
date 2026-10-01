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

Optional fields: `referenceLinks`, `cveInformation`, `affectedComponent`, `confidence`, `remediationPriority`, `estimatedComplexity`, and `status`.

Do not create findings without evidence. Preserve exact evidence. Use the same ID when the same finding is reused; cross-reference it instead of creating a duplicate. Distinct evidence or remediation may justify separate IDs.
