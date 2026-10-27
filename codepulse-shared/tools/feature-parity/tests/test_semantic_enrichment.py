import copy
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_comparison import approve
from test_enrichment import enrichment_batch
from test_validation import manifest
from feature_parity.cli import main
from feature_parity.comparison import compare_manifests
from feature_parity.enrichment import enrichment_template, import_enrichment
from feature_parity.finder import find_repository
from feature_parity.identity import digest
from feature_parity.identity_mappings import identity_mappings_template
from feature_parity.reports import build_report, render_html, render_markdown
from feature_parity.source_context import MAX_CONTEXT_BYTES, prepare_enrichment
from feature_parity.validation import ArtifactError, validate_manifest


SOURCE = """class PromotionController {
    [HttpPost]
    public object Assign(Promotion promotion, Location location) {
        if (!location.Active) return BadRequest("Inactive location");
        return SaveAssignment(promotion, location);
    }
}
"""


def analysis(ref="evidence-1"):
    return {
        "status": "complete",
        "summary": "Assign a promotion to an active location, rejecting inactive locations.",
        "evidenceRefs": [ref],
        "businessRules": [{
            "id": "active-location", "condition": "The selected location is inactive",
            "outcome": "Reject the promotion assignment",
            "basis": "observed", "rationale": "The inactive-location branch returns BadRequest before saving",
            "evidenceRefs": [ref],
        }],
        "unresolvedQuestions": [],
    }


class SemanticContractTests(unittest.TestCase):
    def test_import_persists_readable_business_context_without_approval(self):
        document = approve(manifest())
        batch = enrichment_batch(document)
        batch["proposals"][0]["updates"] = {
            "name": "Assign a promotion to a location", "domain": "Promotion management",
            "semanticAnalysis": analysis(),
        }
        result = import_enrichment(document, batch)["feature-manifest.json"]
        feature = result["features"][0]
        self.assertEqual(feature["semanticAnalysis"]["businessRules"][0]["outcome"], "Reject the promotion assignment")
        self.assertEqual(feature["status"], "needs-review")
        self.assertNotIn("review", feature)
        self.assertEqual(feature["confidence"], document["features"][0]["confidence"])
        self.assertEqual(result["evidence"], document["evidence"])
        self.assertEqual(compare_manifests(result, document)["statistics"]["equivalentCount"], 0)

    def test_invalid_rules_and_incomplete_statuses_fail(self):
        mutations = [
            lambda value: value.update(evidenceRefs=["unknown"]),
            lambda value: value["businessRules"][0].update(evidenceRefs=["unknown"]),
            lambda value: value["businessRules"].append(copy.deepcopy(value["businessRules"][0])),
            lambda value: value["businessRules"][0].update(basis="verified"),
            lambda value: value["businessRules"][0].update(rationale=" "),
            lambda value: value.update(unresolvedQuestions=["Unknown eligibility service"]),
            lambda value: value.update(status="partial"),
            lambda value: value.update(status="partial", unresolvedQuestions=[" "]),
        ]
        for mutation in mutations:
            document = manifest()
            value = analysis()
            mutation(value)
            document["features"][0]["semanticAnalysis"] = value
            with self.subTest(mutation=mutation), self.assertRaises(ArtifactError):
                validate_manifest(document)

    def test_semantic_edits_invalidate_human_approval(self):
        document = manifest()
        document["features"][0]["semanticAnalysis"] = analysis()
        document = approve(document)
        document["features"][0]["semanticAnalysis"]["businessRules"][0]["outcome"] = "Allow the assignment"
        with self.assertRaisesRegex(ArtifactError, "Stale feature approval"):
            validate_manifest(document)

    def test_rule_changes_and_incomplete_analysis_prevent_equivalence(self):
        document = manifest()
        document["features"][0]["semanticAnalysis"] = analysis()
        baseline = approve(document)
        self.assertEqual(compare_manifests(baseline, baseline)["statistics"]["equivalentCount"], 1)
        for status in ("complete", "partial", "unresolved", None):
            target = copy.deepcopy(document)
            if status is None:
                target["features"][0].pop("semanticAnalysis")
            elif status == "complete":
                target["features"][0]["semanticAnalysis"]["businessRules"][0]["outcome"] = "Allow the assignment"
            else:
                target["features"][0]["semanticAnalysis"].update(
                    status=status, unresolvedQuestions=["Eligibility service was not available"],
                )
            target = approve(target)
            with self.subTest(status=status):
                self.assertEqual(compare_manifests(baseline, target)["statistics"]["equivalentCount"], 0)

    def test_large_manifest_template_batches_cover_all_candidates(self):
        document = manifest()
        base = document["features"][0]
        document["features"] = [dict(copy.deepcopy(base), id=f"feature-{index:04}") for index in range(568)]
        identifiers = []
        for offset in range(0, 568, 100):
            template = enrichment_template(document, offset=offset, limit=100)
            identifiers.extend(item["featureId"] for item in template["proposals"])
        self.assertEqual(identifiers, sorted(item["id"] for item in document["features"]))
        report = build_report(document)
        self.assertEqual(len(report["capabilities"]), 500)
        self.assertIn({"label": "Semantic analysis not-started", "value": 568}, report["metrics"])
        self.assertTrue(any("Capability detail is truncated" in item for item in report["limitations"]))
        for options in ({"offset": -1}, {"limit": 101}, {"limit": 0}, {"offset": 568},
                        {"feature_ids": ["unknown"]}, {"feature_ids": ["feature-0000"] * 2},
                        {"feature_ids": ["feature-0000"], "limit": 1}):
            with self.subTest(options=options), self.assertRaises(ArtifactError):
                enrichment_template(document, **options)

    def test_merge_cannot_discard_rules_from_a_mixed_legacy_group(self):
        baseline = manifest()
        second = copy.deepcopy(baseline["features"][0])
        second["id"] = "identity.additional-capability"
        baseline["features"].append(second)
        baseline["features"][0]["semanticAnalysis"] = analysis()
        baseline = approve(baseline)
        target = approve(manifest())
        mappings = identity_mappings_template(baseline, target)
        mappings["mappings"].append({
            "mappingType": "merge",
            "baselineFeatureIds": [item["id"] for item in baseline["features"]],
            "targetFeatureIds": [target["features"][0]["id"]],
            "decision": "same-capability", "rationale": "Synthetic consolidation",
            "differences": [], "approvedReference": "Independent fixture review",
        })
        result = compare_manifests(baseline, target, mappings)
        self.assertEqual(result["statistics"]["equivalentCount"], 0)
        self.assertTrue(all("Business rules differ or semantic analysis is missing" in item["differences"]
                            for item in result["matches"]))

    def test_report_contains_context_rules_citations_and_semantic_counts(self):
        document = manifest()
        report = build_report(document)
        self.assertEqual(report["semanticStatus"], "inventory-only")
        document["features"][0]["semanticAnalysis"] = analysis()
        report = build_report(document)
        self.assertEqual(report["semanticStatus"], "complete")
        self.assertIn({"label": "Semantic analysis complete", "value": 1}, report["metrics"])
        for rendered in (render_html(report), render_markdown(report)):
            self.assertIn("Reject the promotion assignment", rendered)
            self.assertIn("observed", rendered)
            self.assertIn("src/users.cs:1-4", rendered)
        document["features"][0]["semanticAnalysis"].update(status="partial", unresolvedQuestions=["Missing callee"])
        self.assertEqual(build_report(document)["semanticStatus"], "incomplete")
        document["features"][0]["semanticAnalysis"]["summary"] = '<script>alert("x")</script> | rule'
        report = build_report(document)
        self.assertNotIn("<script>", render_html(report))
        self.assertIn("&lt;script&gt;", render_html(report))
        self.assertIn("\\|", render_markdown(report))


class SourcePreparationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "PromotionController.cs").write_text(SOURCE, encoding="utf-8")
        (self.source / "Eligibility.cs").write_text("class Eligibility {}", encoding="utf-8")
        (self.source / "appsettings.json").write_text('{"sensitive": true}', encoding="utf-8")
        self.scan = find_repository(self.source)
        self.document = self.scan["feature-manifest.json"]
        self.inventory = self.scan["repository-inventory.json"]

    def test_preparation_binds_actual_method_bodies_and_related_source(self):
        original = copy.deepcopy(self.document)
        artifacts = prepare_enrichment(
            self.document, self.inventory, self.source, context_files=["Eligibility.cs"],
        )
        self.assertEqual(self.document, original)
        prepared = artifacts["feature-manifest.json"]
        source_text = "\n".join(item["text"] for item in artifacts["source-context.json"]["files"])
        self.assertIn('if (!location.Active) return BadRequest("Inactive location")', source_text)
        self.assertIn("class Eligibility", source_text)
        self.assertEqual(artifacts["source-context.json"]["baseManifestDigest"], digest(prepared))
        self.assertEqual(artifacts["enrichment-proposals.json"]["baseManifestDigest"], digest(prepared))
        refs = prepared["features"][0]["evidenceRefs"]
        contexts = [item for item in prepared["evidence"] if item["type"] == "source-context"]
        self.assertEqual(len(contexts), 2)
        self.assertTrue(all(item["id"] in refs and item["verification"] == "partially-verified" for item in contexts))
        self.assertEqual(artifacts, prepare_enrichment(self.document, self.inventory, self.source, context_files=["Eligibility.cs"]))
        self.assertEqual(prepared["features"][0]["confidence"], original["features"][0]["confidence"])

    def test_stale_excluded_outside_and_oversized_context_fail(self):
        for location in ("appsettings.json", "../outside.cs", "C:/outside.cs", "missing.cs", "folder\\file.cs"):
            with self.subTest(location=location), self.assertRaises(ArtifactError):
                prepare_enrichment(self.document, self.inventory, self.source, context_files=[location])
        changed_inventory = copy.deepcopy(self.inventory)
        changed_inventory[0]["size"] = 42
        with self.assertRaisesRegex(ArtifactError, "inventory is stale"):
            prepare_enrichment(self.document, changed_inventory, self.source)
        (self.source / "PromotionController.cs").write_text(SOURCE + "// changed", encoding="utf-8")
        with self.assertRaisesRegex(ArtifactError, "changed since discovery"):
            prepare_enrichment(self.document, self.inventory, self.source)
        (self.source / "PromotionController.cs").write_bytes(b"x" * (MAX_CONTEXT_BYTES + 1))
        with self.assertRaisesRegex(ArtifactError, "exceeds 2 MiB"):
            prepare_enrichment(self.document, self.inventory, self.source)

    def test_links_and_excess_file_counts_fail_before_export(self):
        with patch("feature_parity.source_context.is_link", return_value=True):
            with self.assertRaisesRegex(ArtifactError, "Linked source context"):
                prepare_enrichment(self.document, self.inventory, self.source)
        with self.assertRaisesRegex(ArtifactError, "exceeds 100 files"):
            prepare_enrichment(self.document, self.inventory, self.source,
                               context_files=[f"source-{index}.cs" for index in range(101)])

    def test_related_context_is_not_attached_to_unselected_features(self):
        (self.source / "OtherController.cs").write_text(
            "class OtherController {\n[HttpGet]\npublic object Get() { return null; }\n}", encoding="utf-8",
        )
        scan = find_repository(self.source)
        document = scan["feature-manifest.json"]
        refs = {item["id"]: item for item in document["evidence"]}
        selected = next(item for item in document["features"]
                        if refs[item["evidenceRefs"][0]]["location"] == "PromotionController.cs")
        artifacts = prepare_enrichment(
            document, scan["repository-inventory.json"], self.source,
            feature_ids=[selected["id"]], context_files=["Eligibility.cs"],
        )
        unselected = next(item for item in document["features"] if item["id"] != selected["id"])
        updated = next(item for item in artifacts["feature-manifest.json"]["features"] if item["id"] == unselected["id"])
        self.assertEqual(updated, unselected)

    def test_cli_prepares_imports_and_reports_a_source_grounded_proposal(self):
        manifest_path = self.root / "manifest.json"
        inventory_path = self.root / "inventory.json"
        manifest_path.write_text(json.dumps(self.document), encoding="utf-8")
        inventory_path.write_text(json.dumps(self.inventory), encoding="utf-8")
        output = self.root / "context"
        args = ["parity", "prepare-enrichment", "--manifest", str(manifest_path),
                "--inventory", str(inventory_path), "--source", str(self.source),
                "--limit", "20", "--output", str(output)]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(args + ["--dry-run"]), 0)
            self.assertFalse(output.exists())
            self.assertEqual(main(args), 0)
            self.assertEqual(main(args), 5)
        batch_path = output / "enrichment-proposals.json"
        batch = json.loads(batch_path.read_text(encoding="utf-8"))
        prepared = json.loads((output / "feature-manifest.json").read_text(encoding="utf-8"))
        context = next(item for item in prepared["evidence"] if item["type"] == "source-context")
        batch["provenance"] = {"agent": "Fixture agent", "model": "Synthetic", "version": "1"}
        proposal = batch["proposals"][0]
        proposal["rationale"] = "Read the inactive-location guard in the controller body"
        proposal["updates"] = {
            "name": "Assign a promotion to a location", "domain": "Promotions",
            "semanticAnalysis": analysis(context["id"]),
            "behaviors": [{
                "id": "reject-inactive-location", "description": "Reject promotion assignment to inactive locations",
                "mandatory": True, "evidenceRefs": [context["id"]],
            }],
        }
        batch_path.write_text(json.dumps(batch), encoding="utf-8")
        imported = self.root / "imported"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["parity", "import-enrichment", "--manifest", str(manifest_path),
                                   "--enrichment", str(batch_path), "--output", str(self.root / "stale")]), 3)
            self.assertFalse((self.root / "stale").exists())
            self.assertEqual(main(["parity", "import-enrichment", "--manifest", str(output / "feature-manifest.json"),
                                   "--enrichment", str(batch_path), "--output", str(imported)]), 0)
            self.assertEqual(main(["parity", "report", "--artifact", str(imported / "feature-manifest.json"),
                                   "--output", str(self.root / "report"), "--format", "both"]), 0)
        result = json.loads((imported / "feature-manifest.json").read_text(encoding="utf-8"))
        validate_manifest(result)
        self.assertEqual(result["features"][0]["semanticAnalysis"]["businessRules"][0]["basis"], "observed")
        self.assertIn("Reject the promotion assignment", (self.root / "report" / "feature-report.html").read_text(encoding="utf-8"))
        bad_output = args[:-1] + [str(self.source / "invalid-output")]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(bad_output), 5)
        self.assertFalse((self.source / "invalid-output").exists())
