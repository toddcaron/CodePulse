import copy
import unittest

from test_comparison import approve
from test_requirements_coverage import reviewed_baseline
from test_validation import manifest
from feature_parity.comparison import compare_manifests
from feature_parity.reports import (
    UNRESOLVED_LIMIT, build_report, render_html, render_markdown, report_artifacts,
)
from feature_parity.requirements_coverage import compare_requirements
from feature_parity.validation import ArtifactError, validate_schema


HOSTILE = '<script>alert("x")</script> | injected'


def comparison_inputs():
    source = approve(manifest())
    target = copy.deepcopy(source)
    return source, target, compare_manifests(source, target)


def coverage_inputs():
    baseline, reviews = reviewed_baseline()
    target = approve(manifest())
    return baseline, target, compare_requirements(baseline, reviews, target)


class DiscoveryReportTests(unittest.TestCase):
    def test_discovery_report_records_scope_review_state_and_limitations(self):
        document = manifest()
        document["features"][0]["admitted"] = False
        document["reviewQueue"] = [{
            "featureId": "identity.create-user", "reason": "Below confidence threshold",
            "evidenceRefs": ["evidence-1"],
        }]
        report = build_report(document)

        self.assertEqual(report["reportType"], "discovery")
        self.assertEqual(report["applications"][0]["role"], "scanned")
        self.assertEqual(report["applications"][0]["coverage"], "unknown")
        self.assertIn("Static evidence only", report["applications"][0]["limitations"])
        self.assertIn({"label": "Needs review features", "value": 0}, report["reviewState"])
        self.assertIn({"label": "Below confidence threshold", "value": 1}, report["metrics"])
        self.assertEqual(report["unresolvedCount"], 1)
        self.assertEqual(report["unresolvedItems"][0]["detail"], "Below confidence threshold")

    def test_manifest_without_admission_omits_admitted_counts(self):
        report = build_report(manifest())
        labels = [item["label"] for item in report["metrics"]]
        self.assertNotIn("Admitted candidates", labels)
        self.assertIn(
            "This manifest does not record confidence admission; admitted counts are not reported",
            report["limitations"],
        )

    def test_unresolved_detail_is_bounded_and_disclosed(self):
        document = manifest()
        base = document["features"][0]
        document["features"] = []
        document["reviewQueue"] = []
        for index in range(UNRESOLVED_LIMIT + 1):
            feature = copy.deepcopy(base)
            feature["id"] = f"identity.feature-{index}"
            document["features"].append(feature)
            document["reviewQueue"].append({
                "featureId": feature["id"], "reason": "Synthetic review", "evidenceRefs": ["evidence-1"],
            })
        report = build_report(document)

        self.assertEqual(report["unresolvedCount"], UNRESOLVED_LIMIT + 1)
        self.assertEqual(len(report["unresolvedItems"]), UNRESOLVED_LIMIT)
        self.assertIn(
            f"Unresolved detail is truncated to the first {UNRESOLVED_LIMIT} records; the JSON artifacts remain complete",
            report["limitations"],
        )


class ComparisonReportTests(unittest.TestCase):
    def test_comparison_report_carries_statuses_and_formulas(self):
        source, target, result = comparison_inputs()
        report = build_report(result, source=source, target=target)

        self.assertEqual(report["reportType"], "comparison")
        self.assertEqual([item["role"] for item in report["applications"]], ["baseline", "target"])
        self.assertIn({"label": "Equivalent", "value": 1}, report["metrics"])
        self.assertIn({"label": "Confirmed baseline features", "value": 1}, report["reviewState"])
        coverage = next(item for item in report["formulas"] if item["label"] == "Equivalent coverage")
        self.assertEqual(coverage["value"], 100)
        self.assertEqual(
            coverage["expression"],
            "100 x equivalent / (equivalent + partial + changed-intentionally + missing)",
        )
        self.assertEqual(report["unresolvedCount"], 0)
        self.assertEqual(report["unresolvedItems"], [])

    def test_stale_supporting_manifests_are_rejected(self):
        source, target, result = comparison_inputs()
        for mutation in (
            lambda: source["application"].update(name="Renamed baseline"),
            lambda: target["application"].update(name="Renamed target"),
        ):
            mutation()
            with self.subTest(mutation=mutation), self.assertRaises(ArtifactError):
                build_report(result, source=source, target=target)

    def test_mapping_digest_is_reported_when_absent(self):
        source, target, result = comparison_inputs()
        report = build_report(result, source=source, target=target)
        mappings = next(item for item in report["digests"] if item["label"] == "Approved identity mappings")
        self.assertIsNone(mappings["value"])


class CoverageReportTests(unittest.TestCase):
    def test_coverage_report_records_review_state_and_formula(self):
        baseline, target, result = coverage_inputs()
        report = build_report(result, baseline=baseline, target=target)

        self.assertEqual(report["reportType"], "requirements-coverage")
        self.assertEqual([item["role"] for item in report["applications"]], ["requirements", "target"])
        self.assertIn({"label": "Declared requirements", "value": 1}, report["reviewState"])
        self.assertIn({"label": "Requirements awaiting review", "value": 0}, report["reviewState"])
        self.assertEqual(report["formulas"][0]["value"], 100)
        self.assertIn(
            "The reviewed-requirements digest is carried from the coverage result; review decisions are not re-read by the report",
            report["limitations"],
        )

    def test_stale_baseline_is_rejected(self):
        baseline, target, result = coverage_inputs()
        baseline["document"]["applicationName"] = "Renamed requirements"
        with self.assertRaises(ArtifactError):
            build_report(result, baseline=baseline, target=target)


class RendererSafetyTests(unittest.TestCase):
    def hostile_report(self):
        document = manifest()
        document["application"]["name"] = HOSTILE
        document["scan"]["limitations"] = [HOSTILE]
        document["reviewQueue"] = [{
            "featureId": "identity.create-user", "reason": HOSTILE, "evidenceRefs": ["evidence-1"],
        }]
        return build_report(document)

    def test_html_escapes_artifact_values_and_embeds_no_scripts(self):
        rendered = render_html(self.hostile_report())
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("javascript:", rendered)
        self.assertNotIn("http://", rendered)
        self.assertNotIn("onerror", rendered)
        self.assertTrue(rendered.startswith("<!doctype html>"))

    def test_markdown_escapes_table_delimiters(self):
        rendered = render_markdown(self.hostile_report())
        self.assertIn("\\|", rendered)
        self.assertNotIn(f"| {HOSTILE} |", rendered)
        self.assertIn("## Limitations", rendered)

    def test_control_characters_are_removed_from_rendered_values(self):
        document = manifest()
        document["application"]["name"] = "Injected\u0000\u001b[31mName"
        report = build_report(document)
        self.assertEqual(report["applications"][0]["name"], "Injected [31mName")
        self.assertNotIn("\u0000", render_html(report))
        self.assertNotIn("\u001b", render_markdown(report))

    def test_renderers_are_deterministic_and_schema_valid(self):
        source, target, result = comparison_inputs()
        report = build_report(result, source=source, target=target)
        validate_schema(report, "feature-report-schema.json")
        self.assertEqual(render_html(report), render_html(copy.deepcopy(report)))
        self.assertEqual(render_markdown(report), render_markdown(copy.deepcopy(report)))


class ReportArtifactTests(unittest.TestCase):
    def test_requested_formats_control_rendered_artifacts(self):
        document = manifest()
        self.assertEqual(sorted(report_artifacts(document)), ["feature-report.html", "feature-report.json"])
        self.assertEqual(
            sorted(report_artifacts(document, formats=("markdown",))),
            ["feature-report.json", "feature-report.md"],
        )
        self.assertEqual(
            sorted(report_artifacts(document, formats=("html", "markdown"))),
            ["feature-report.html", "feature-report.json", "feature-report.md"],
        )

    def test_unsupported_artifact_is_rejected(self):
        for artifact in ({"schemaVersion": "1.0"}, [], "manifest"):
            with self.subTest(artifact=artifact), self.assertRaises(ArtifactError):
                build_report(artifact)


if __name__ == "__main__":
    unittest.main()
