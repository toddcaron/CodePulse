"""Deterministic, presentation-independent feature reports and safe renderers."""

import html
import re
from collections import Counter

from . import __version__
from .identity import digest
from .validation import ArtifactError, validate_manifest, validate_schema


TEXT_LIMIT = 4000
UNRESOLVED_LIMIT = 500
FEATURE_STATUSES = ("discovered", "needs-review", "confirmed", "deprecated", "rejected", "merged", "split")
MATCH_STATUSES = (
    ("equivalent", "Equivalent"), ("partial", "Partial"),
    ("changed-intentionally", "Changed intentionally"), ("replaced", "Replaced"),
    ("missing", "Missing"), ("new-in-target", "New in target"),
    ("not-applicable", "Not applicable"), ("unable-to-verify", "Unable to verify"),
    ("needs-sme-validation", "Needs SME validation"),
)
CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
STANDING_LIMITATIONS = (
    "The engine renders only values present in the source JSON artifacts; no application was built or executed",
    "Reports are generated from static evidence and never establish runtime parity or confirmed absence",
)


def _text(value):
    collapsed = CONTROL_CHARACTERS.sub(" ", str(value))
    collapsed = " ".join(collapsed.split())
    if not collapsed:
        return "(not recorded)"
    if len(collapsed) > TEXT_LIMIT:
        return collapsed[: TEXT_LIMIT - 3] + "..."
    return collapsed


def _texts(values):
    seen = []
    for value in values:
        item = _text(value)
        if item not in seen:
            seen.append(item)
    return seen[:100]


def _application(manifest, role):
    return {
        "role": role,
        "name": _text(manifest["application"]["name"]),
        "sourceType": manifest["application"]["sourceType"],
        "revision": _text(manifest["application"]["revision"]) if manifest["application"]["revision"] else None,
        "coverage": manifest["scan"]["coverage"],
        "limitations": _texts(manifest["scan"]["limitations"]),
    }


def _measures(pairs):
    return [{"label": _text(label), "value": int(value)} for label, value in pairs]


def _percent(numerator, denominator):
    return 100 * numerator / denominator if denominator else None


def _unresolved(records):
    return records[:UNRESOLVED_LIMIT], len(records) > UNRESOLVED_LIMIT


def report_kind(artifact):
    if isinstance(artifact, dict):
        if "features" in artifact and "scan" in artifact:
            return "discovery"
        if "mappingDigest" in artifact:
            return "comparison"
        if "reviewsDigest" in artifact:
            return "requirements-coverage"
    raise ArtifactError(
        "Unsupported report artifact; supply a feature manifest, parity results or requirements coverage"
    )


def _discovery_report(manifest):
    validate_manifest(manifest)
    statuses = Counter(feature["status"] for feature in manifest["features"])
    features = manifest["features"]
    active = [feature for feature in features if feature["status"] in {"discovered", "confirmed", "needs-review"}]
    semantic_counts = Counter(feature.get("semanticAnalysis", {}).get("status", "not-started") for feature in active)
    semantic_status = ("inventory-only" if semantic_counts["not-started"] == len(active)
                       else "complete" if semantic_counts["complete"] == len(active) else "incomplete")
    evidence = {item["id"]: item for item in manifest["evidence"]}
    capabilities = []
    for feature in active[:UNRESOLVED_LIMIT]:
        analysis = feature.get("semanticAnalysis", {})
        capabilities.append({
            "identifier": _text(feature["id"]), "name": _text(feature["name"]), "domain": _text(feature["domain"]),
            "status": analysis.get("status", "not-started"),
            "summary": _text(analysis.get("summary", "Technical candidate only; business meaning has not been analyzed")),
            "unresolvedQuestions": _texts(analysis.get("unresolvedQuestions", [])),
            "businessRules": [{
                "condition": _text(rule["condition"]), "outcome": _text(rule["outcome"]),
                "basis": rule["basis"], "rationale": _text(rule["rationale"]),
                "evidence": [_text(f"{evidence[ref]['location']}:{evidence[ref]['lineStart']}-{evidence[ref]['lineEnd']} ({ref})")
                             for ref in rule["evidenceRefs"]],
            } for rule in analysis.get("businessRules", [])],
        })
    admission_recorded = any("admitted" in feature for feature in features)
    metrics = [("Candidate features", len(features)), ("Evidence records", len(manifest["evidence"]))]
    metrics.extend((f"Semantic analysis {status}", semantic_counts[status])
                   for status in ("complete", "partial", "unresolved", "not-started"))
    if admission_recorded:
        admitted = sum(bool(feature.get("admitted")) for feature in features)
        metrics.extend([("Admitted candidates", admitted), ("Below confidence threshold", len(features) - admitted)])
    metrics.append(("Review queue items", len(manifest["reviewQueue"])))
    formulas = [{
        "label": "Human review share", "value": _percent(len(manifest["reviewQueue"]), len(features)),
        "expression": "100 x review queue items / candidate features",
    }]
    if admission_recorded:
        formulas.insert(0, {
            "label": "Admitted share",
            "value": _percent(sum(bool(feature.get("admitted")) for feature in features), len(features)),
            "expression": "100 x admitted candidates / candidate features",
        })
    items, truncated = _unresolved([{
        "identifier": _text(item["featureId"]), "status": "needs-review", "detail": _text(item["reason"]),
    } for item in manifest["reviewQueue"]])
    limitations = list(manifest["scan"]["limitations"]) + [
        "Discovered candidates are provisional and carry no human review, approval or parity credit",
        f"Semantic enrichment status: {semantic_status}; analysis completion is not business completeness or approval",
    ]
    if len(active) > UNRESOLVED_LIMIT:
        limitations.append(f"Capability detail is truncated to the first {UNRESOLVED_LIMIT} active features; the manifest remains complete")
    if not admission_recorded:
        limitations.append("This manifest does not record confidence admission; admitted counts are not reported")
    if truncated:
        limitations.append(f"Unresolved detail is truncated to the first {UNRESOLVED_LIMIT} records; the JSON artifacts remain complete")
    return {
        "reportType": "discovery",
        "title": f"Provisional capability discovery: {_text(manifest['application']['name'])}",
        "methodology": "Bounded static discovery of provisional capabilities; no application build or execution",
        "semanticStatus": semantic_status, "capabilities": capabilities,
        "applications": [_application(manifest, "scanned")],
        "digests": [
            {"label": "Repository inventory", "value": manifest["scan"]["inventoryDigest"]},
            {"label": "Resolved configuration", "value": manifest["scan"].get("configurationDigest")},
            {"label": "Feature manifest", "value": digest(manifest)},
        ],
        "reviewState": _measures(
            (status.replace("-", " ").capitalize() + " features", statuses[status]) for status in FEATURE_STATUSES
        ),
        "metrics": _measures(metrics),
        "formulas": formulas,
        "unresolvedCount": len(manifest["reviewQueue"]),
        "unresolvedItems": items,
        "limitations": limitations,
    }


def _comparison_report(artifact, source, target):
    validate_schema(artifact, "feature-parity-result-schema.json")
    validate_manifest(source)
    validate_manifest(target)
    if artifact["baselineDigest"] != digest(source) or artifact["targetDigest"] != digest(target):
        raise ArtifactError("Supplied manifests are stale for this comparison result")
    matches = artifact["matches"]
    statistics = artifact["statistics"]
    unresolved_records = [record for record in matches if record["requiresHumanValidation"]]
    items, truncated = _unresolved([{
        "identifier": _text(record["baselineFeatureId"] or (record["targetFeatureIds"] or ["(unmatched)"])[0]),
        "status": _text(record["status"]),
        "detail": _text("; ".join(record["rationale"] + record["differences"])),
    } for record in unresolved_records])
    limitations = list(artifact["limitations"])
    if truncated:
        limitations.append(f"Unresolved detail is truncated to the first {UNRESOLVED_LIMIT} records; the JSON artifacts remain complete")
    return {
        "reportType": "comparison",
        "title": (
            f"Reviewed feature comparison: {_text(source['application']['name'])}"
            f" to {_text(target['application']['name'])}"
        ),
        "methodology": _text(artifact["methodology"]),
        "applications": [_application(source, "baseline"), _application(target, "target")],
        "digests": [
            {"label": "Baseline manifest", "value": artifact["baselineDigest"]},
            {"label": "Target manifest", "value": artifact["targetDigest"]},
            {"label": "Approved identity mappings", "value": artifact["mappingDigest"]},
        ],
        "reviewState": _measures([
            ("Confirmed baseline features", sum(item["status"] == "confirmed" for item in source["features"])),
            ("Confirmed target features", sum(item["status"] == "confirmed" for item in target["features"])),
            ("Approved mapping matches", sum(item["matchingStage"] == "approved-mapping" for item in matches)),
            ("Approved intentional differences", statistics["byStatus"]["changed-intentionally"]),
            ("Matches requiring human validation", len(unresolved_records)),
        ]),
        "metrics": _measures(
            [(label, statistics["byStatus"][status]) for status, label in MATCH_STATUSES]
            + [("Verified denominator", statistics["verifiedDenominator"])]
        ),
        "formulas": [
            {
                "label": "Equivalent coverage", "value": statistics["coveragePercent"],
                "expression": "100 x equivalent / (equivalent + partial + changed-intentionally + missing)",
            },
            {
                "label": "Unresolved matches", "value": statistics["unresolvedCount"],
                "expression": "unable-to-verify + needs-SME-validation",
            },
        ],
        "unresolvedCount": statistics["unresolvedCount"],
        "unresolvedItems": items,
        "limitations": limitations,
    }


def _coverage_report(artifact, baseline, target):
    validate_schema(artifact, "feature-requirements-coverage-schema.json")
    validate_schema(baseline, "feature-requirements-baseline-schema.json")
    validate_manifest(target)
    if artifact["baselineDigest"] != digest(baseline) or artifact["targetDigest"] != digest(target):
        raise ArtifactError("Supplied baseline or target is stale for this coverage result")
    statistics = artifact["statistics"]
    unresolved_records = [record for record in artifact["matches"] if record["requiresHumanValidation"]]
    items, truncated = _unresolved([{
        "identifier": _text(record["requirementId"]),
        "status": _text(record["status"]),
        "detail": _text("; ".join(record["rationale"] + record["unresolvedCriteria"])),
    } for record in unresolved_records])
    limitations = list(artifact["limitations"]) + [
        "The reviewed-requirements digest is carried from the coverage result; review decisions are not re-read by the report",
    ]
    if truncated:
        limitations.append(f"Unresolved detail is truncated to the first {UNRESOLVED_LIMIT} records; the JSON artifacts remain complete")
    requirements = {
        "role": "requirements", "name": _text(baseline["document"]["applicationName"]),
        "sourceType": "requirements", "revision": None,
        "coverage": baseline["coverage"], "limitations": [],
    }
    return {
        "reportType": "requirements-coverage",
        "title": (
            f"Reviewed requirements coverage: {_text(baseline['document']['applicationName'])}"
            f" to {_text(target['application']['name'])}"
        ),
        "methodology": _text(artifact["methodology"]),
        "applications": [requirements, _application(target, "target")],
        "digests": [
            {"label": "Requirements baseline", "value": artifact["baselineDigest"]},
            {"label": "Reviewed requirements decisions", "value": artifact["reviewsDigest"]},
            {"label": "Target manifest", "value": artifact["targetDigest"]},
        ],
        "reviewState": _measures([
            ("Declared requirements", statistics["requirementCount"]),
            ("Reviewed requirements", statistics["reviewedCount"]),
            ("Requirements awaiting review", statistics["requirementCount"] - statistics["reviewedCount"]),
            ("Matches requiring human validation", len(unresolved_records)),
        ]),
        "metrics": _measures([
            ("Covered requirements", statistics["coveredCount"]),
            ("Partial requirements", statistics["partialCount"]),
            ("Unresolved requirements", statistics["unresolvedCount"]),
        ]),
        "formulas": [{
            "label": "Requirement coverage", "value": statistics["coveragePercent"],
            "expression": "100 x covered requirements / declared requirements",
        }],
        "unresolvedCount": statistics["unresolvedCount"],
        "unresolvedItems": items,
        "limitations": limitations,
    }


def build_report(artifact, source=None, target=None, baseline=None):
    kind = report_kind(artifact)
    if kind == "discovery":
        report = _discovery_report(artifact)
    elif kind == "comparison":
        report = _comparison_report(artifact, source, target)
    else:
        report = _coverage_report(artifact, baseline, target)
    report = {
        "schemaVersion": "1.0", "engineVersion": __version__, **report,
        "limitations": _texts(list(report["limitations"]) + list(STANDING_LIMITATIONS)),
    }
    validate_schema(report, "feature-report-schema.json")
    return report


def _measure_value(value):
    if value is None:
        return "unavailable"
    if isinstance(value, bool) or isinstance(value, int):
        return str(value)
    return f"{value:.1f}"


def _escape(value):
    return html.escape(str(value), quote=True)


CSS = (
    ":root{--ink:#19211d;--muted:#5d6962;--line:#d9dfd8;--green:#176b4d}"
    "*{box-sizing:border-box}body{margin:0;background:#f5f7f2;color:var(--ink);font:16px/1.55 Georgia,serif}"
    "main{max-width:1120px;margin:0 auto;padding:40px 16px 64px}"
    "header{border-top:8px solid var(--ink);padding:20px 0}"
    "h1{font-size:clamp(1.6rem,4vw,2.8rem);line-height:1.1;margin:8px 0;font-weight:500}h2{margin:0 0 12px}"
    "h2,th,.eyebrow,.meta{font-family:\"Trebuchet MS\",Verdana,sans-serif}"
    ".eyebrow{color:var(--green);font-size:.78rem;font-weight:700;text-transform:uppercase}"
    ".meta{color:var(--muted);font-size:.85rem}"
    "section{background:#fff;border:1px solid var(--line);border-radius:8px;padding:20px;margin-top:18px}"
    "table{width:100%;border-collapse:collapse}"
    "th,td{padding:8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}"
    "th{color:var(--muted);font-size:.78rem;text-transform:uppercase}"
    "code{background:#eef1ed;padding:1px 4px;border-radius:3px;overflow-wrap:anywhere}ul{padding-left:22px}"
    "footer{margin-top:28px;border-top:1px solid var(--line);padding-top:14px;color:var(--muted);font-size:.85rem}"
    "@media print{body{background:#fff}section{break-inside:avoid}}"
)


def _html_table(headers, rows):
    head = "".join(f"<th>{_escape(header)}</th>" for header in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def _capability_rows(report):
    return [[item["name"], item["domain"], item["status"], item["summary"],
             "; ".join(item["unresolvedQuestions"]) or "(none recorded)", item["identifier"]]
            for item in report.get("capabilities", [])]


def _rule_rows(report):
    return [[item["name"], rule["basis"], rule["condition"], rule["outcome"], rule["rationale"],
             "; ".join(rule["evidence"])]
            for item in report.get("capabilities", []) for rule in item["businessRules"]]


def render_html(report):
    validate_schema(report, "feature-report-schema.json")
    scope_limitations = "".join(
        f"<h3>{_escape(application['role'])} scope limitations</h3><ul>"
        + "".join(f"<li>{_escape(item)}</li>" for item in application["limitations"])
        + "</ul>"
        for application in report["applications"] if application["limitations"]
    )
    sections = [
        "<section><h2>Scope</h2>" + _html_table(
            ["Role", "Application", "Source type", "Revision", "Scan coverage"],
            [[
                _escape(application["role"]), _escape(application["name"]),
                _escape(application["sourceType"] or "unavailable"),
                f"<code>{_escape(application['revision'])}</code>" if application["revision"] else "unavailable",
                _escape(application["coverage"]),
            ] for application in report["applications"]],
        ) + scope_limitations + "</section>",
        "<section><h2>Provenance</h2>" + _html_table(
            ["Artifact", "Digest"],
            [[_escape(item["label"]), f"<code>{_escape(item['value'])}</code>" if item["value"] else "not supplied"]
             for item in report["digests"]],
        ) + "</section>",
        "<section><h2>Review state</h2>" + _html_table(
            ["Measure", "Count"],
            [[_escape(item["label"]), _escape(item["value"])] for item in report["reviewState"]],
        ) + "</section>",
        "<section><h2>Results</h2>" + _html_table(
            ["Measure", "Count"],
            [[_escape(item["label"]), _escape(item["value"])] for item in report["metrics"]],
        ) + "</section>",
        "<section><h2>Formulas</h2>" + _html_table(
            ["Measure", "Formula", "Value"],
            [[_escape(item["label"]), f"<code>{_escape(item['expression'])}</code>",
              _escape(_measure_value(item["value"]))] for item in report["formulas"]],
        ) + "</section>",
        f"<section><h2>Unresolved items ({_escape(report['unresolvedCount'])})</h2>" + (
            _html_table(
                ["Identifier", "Status", "Detail"],
                [[f"<code>{_escape(item['identifier'])}</code>", _escape(item["status"]), _escape(item["detail"])]
                 for item in report["unresolvedItems"]],
            ) if report["unresolvedItems"] else "<p>No records require human validation in this result.</p>"
        ) + "</section>",
        "<section><h2>Limitations</h2><ul>" + "".join(
            f"<li>{_escape(item)}</li>" for item in report["limitations"]
        ) + "</ul></section>",
    ]
    if "capabilities" in report:
        sections.insert(4, "<section><h2>Capabilities and business context</h2>"
                        f"<p>Semantic enrichment: {_escape(report['semanticStatus'])}</p>"
                        + _html_table(
                            ["Capability", "Domain", "Analysis", "Purpose and outcome", "Unresolved questions", "Identifier"],
                            [[_escape(cell) for cell in row] for row in _capability_rows(report)],
                        ) + "<h3>Business rules (provisional)</h3>" + _html_table(
                            ["Capability", "Basis", "When", "Then", "Rationale", "Evidence"],
                            [[_escape(cell) for cell in row] for row in _rule_rows(report)],
                        ) + "</section>")
    return (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{_escape(report['title'])}</title><style>{CSS}</style></head>"
        "<body><main>"
        f'<header><div class="eyebrow">CodePulse Feature Parity / {_escape(report["reportType"])}</div>'
        f'<h1>{_escape(report["title"])}</h1>'
        f'<p class="meta">{_escape(report["methodology"])}</p></header>'
        + "".join(sections)
        + f'<footer>Rendered by the CodePulse feature-parity engine {_escape(report["engineVersion"])} '
        "from reviewed JSON artifacts. This is a static evidence report, not a runtime parity certification."
        "</footer></main></body></html>\n"
    )


def _cell(value):
    return str(value).replace("\\", "\\\\").replace("|", "\\|")


def _markdown_table(headers, rows):
    lines = ["| " + " | ".join(_cell(header) for header in headers) + " |",
             "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(_cell(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def render_markdown(report):
    validate_schema(report, "feature-report-schema.json")
    blocks = [
        f"# {_cell(report['title'])}",
        f"CodePulse Feature Parity report type `{report['reportType']}`, engine `{report['engineVersion']}`.",
        f"{_cell(report['methodology'])}",
        "## Scope",
        _markdown_table(
            ["Role", "Application", "Source type", "Revision", "Scan coverage"],
            [[
                application["role"], application["name"], application["sourceType"] or "unavailable",
                f"`{application['revision']}`" if application["revision"] else "unavailable",
                application["coverage"],
            ] for application in report["applications"]],
        ),
        *[
            f"### {_cell(application['role'])} scope limitations\n\n"
            + "\n".join(f"- {_cell(item)}" for item in application["limitations"])
            for application in report["applications"] if application["limitations"]
        ],
        "## Provenance",
        _markdown_table(
            ["Artifact", "Digest"],
            [[item["label"], f"`{item['value']}`" if item["value"] else "not supplied"]
             for item in report["digests"]],
        ),
        "## Review state",
        _markdown_table(["Measure", "Count"], [[item["label"], item["value"]] for item in report["reviewState"]]),
        "## Results",
        _markdown_table(["Measure", "Count"], [[item["label"], item["value"]] for item in report["metrics"]]),
        "## Formulas",
        _markdown_table(
            ["Measure", "Formula", "Value"],
            [[item["label"], f"`{item['expression']}`", _measure_value(item["value"])]
             for item in report["formulas"]],
        ),
        f"## Unresolved items ({report['unresolvedCount']})",
        _markdown_table(
            ["Identifier", "Status", "Detail"],
            [[f"`{item['identifier']}`", item["status"], item["detail"]] for item in report["unresolvedItems"]],
        ) if report["unresolvedItems"] else "No records require human validation in this result.",
        "## Limitations",
        "\n".join(f"- {_cell(item)}" for item in report["limitations"]),
    ]
    if "capabilities" in report:
        position = blocks.index("## Formulas")
        blocks[position:position] = [
            "## Capabilities and business context",
            f"Semantic enrichment: {report['semanticStatus']}",
            _markdown_table(
                ["Capability", "Domain", "Analysis", "Purpose and outcome", "Unresolved questions", "Identifier"],
                _capability_rows(report),
            ),
            "### Business rules (provisional)",
            _markdown_table(["Capability", "Basis", "When", "Then", "Rationale", "Evidence"], _rule_rows(report)),
        ]
    return "\n\n".join(blocks) + "\n"


def report_artifacts(artifact, source=None, target=None, baseline=None, formats=("html",)):
    report = build_report(artifact, source=source, target=target, baseline=baseline)
    artifacts = {"feature-report.json": report}
    if "html" in formats:
        artifacts["feature-report.html"] = render_html(report)
    if "markdown" in formats:
        artifacts["feature-report.md"] = render_markdown(report)
    return artifacts
