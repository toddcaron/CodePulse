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
from feature_parity.enrichment import enrichment_progress, enrichment_template, import_enrichment
from feature_parity.finder import find_repository
from feature_parity.identity import digest
from feature_parity.identity_mappings import identity_mappings_template
from feature_parity.reports import build_report, render_html, render_markdown
from feature_parity.source_context import MAX_CONTEXT_BYTES, prepare_enrichment
from feature_parity.validation import ArtifactError, validate_business_meaning, validate_manifest


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
        "businessMeaning": {
            "purpose": "Control which locations receive a promotion",
            "userGoal": "A promotion manager assigns a campaign to an eligible location",
            "trigger": "A promotion and target location are submitted for assignment",
            "outcome": "An eligible location receives the promotion; inactive locations are rejected",
            "basis": "inferred",
        },
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
        report = build_report(document, inventory_only=True)
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
        report = build_report(document, inventory_only=True)
        self.assertEqual(report["semanticStatus"], "inventory-only")
        document["features"][0]["semanticAnalysis"] = analysis()
        report = build_report(document)
        self.assertEqual(report["semanticStatus"], "complete")
        self.assertIn({"label": "Semantic analysis complete", "value": 1}, report["metrics"])
        for rendered in (render_html(report), render_markdown(report)):
            self.assertIn("Reject the promotion assignment", rendered)
            self.assertIn("observed", rendered)
            self.assertIn("src/users.cs:1-4", rendered)
            self.assertIn("Control which locations receive a promotion", rendered)
        self.assertLess(render_html(report).index("<h2>Capabilities and business context"),
                        render_html(report).index("<h2>Scope"))
        self.assertLess(render_markdown(report).index("## Capabilities and business context"),
                        render_markdown(report).index("## Scope"))
        document["features"][0]["semanticAnalysis"].update(status="partial", unresolvedQuestions=["Missing callee"])
        self.assertEqual(build_report(document)["semanticStatus"], "incomplete")
        document["features"][0]["semanticAnalysis"]["summary"] = '<script>alert("x")</script> | rule'
        report = build_report(document)
        self.assertNotIn("<script>", render_html(report))
        self.assertIn("&lt;script&gt;", render_html(report))
        self.assertIn("\\|", render_markdown(report))

    def test_business_delivery_rejects_missing_context_and_syntax_only_contracts(self):
        changes = [
            lambda feature: feature.pop("semanticAnalysis"),
            lambda feature: feature["semanticAnalysis"].pop("businessMeaning"),
            lambda feature: feature["semanticAnalysis"]["businessMeaning"].update(purpose=" "),
            lambda feature: feature["semanticAnalysis"].update(status="unresolved", unresolvedQuestions=["Unknown intent"]),
            lambda feature: feature.update(name="POST API operation 006fe9d9"),
            lambda feature: feature.update(domain="Unclassified"),
            lambda feature: feature["behaviors"][0].update(description="Declares POST HTTP syntax"),
        ]
        for change in changes:
            document = manifest()
            document["features"][0]["semanticAnalysis"] = analysis()
            change(document["features"][0])
            with self.subTest(change=change), self.assertRaises(ArtifactError):
                validate_business_meaning(document)
        empty = manifest()
        empty["features"] = []
        with self.assertRaises(ArtifactError):
            validate_business_meaning(empty)

    def test_partial_business_meaning_is_deliverable_with_explicit_questions(self):
        document = manifest()
        document["features"][0]["semanticAnalysis"] = analysis()
        document["features"][0]["semanticAnalysis"].update(
            status="partial", unresolvedQuestions=["Confirm the promotion manager role with the product owner"],
        )
        validate_business_meaning(document)
        report = build_report(document)
        self.assertEqual(report["discoveryMode"], "business")
        self.assertEqual(report["semanticStatus"], "incomplete")
        self.assertIn("Confirm the promotion manager role", render_html(report))


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
        self.assertIn("businessMeaning", artifacts["enrichment-proposals.json"]["proposals"][0]["updates"]["semanticAnalysis"])
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

    def test_pending_selection_skips_ready_candidates_after_arbitrary_domain_batch(self):
        source_text = "class Operations {\n" + "\n".join(
            f"[HttpPost]\npublic void Action{index}() {{}}" for index in range(45)
        ) + "\n}"
        (self.source / "PromotionController.cs").write_text(source_text, encoding="utf-8")
        scan = find_repository(self.source)
        document = scan["feature-manifest.json"]
        selected = [feature["id"] for feature in document["features"][10:30]]
        first = prepare_enrichment(document, scan["repository-inventory.json"], self.source, feature_ids=selected)
        self.assertEqual(len(selected), 20)
        latest = self.complete_business_batch(first)
        progress = enrichment_progress(latest)
        self.assertEqual(progress["statistics"]["businessReadyCount"], 20)
        self.assertEqual(progress["statistics"]["pendingCount"], 25)
        self.assertEqual(progress["completionState"], "continue")
        self.assertTrue(set(progress["nextFeatureIds"]).isdisjoint(selected))
        visited = set(selected)
        while progress["completionState"] == "continue":
            prepared = prepare_enrichment(latest, scan["repository-inventory.json"], self.source, pending=True)
            batch_ids = prepared["source-context.json"]["featureIds"]
            self.assertTrue(set(batch_ids).isdisjoint(visited))
            self.assertLessEqual(len(batch_ids), 20)
            visited.update(batch_ids)
            before = {item["id"]: item for item in latest["features"]}
            latest = self.complete_business_batch(prepared)
            for feature in latest["features"]:
                if feature["id"] not in batch_ids:
                    self.assertEqual(feature, before[feature["id"]])
            progress = enrichment_progress(latest)
        self.assertEqual(len(visited), 45)
        self.assertEqual(progress["completionState"], "ready")
        validate_business_meaning(latest)
        self.assertEqual(build_report(latest)["discoveryMode"], "business")
        with self.assertRaisesRegex(ArtifactError, "No pending candidates"):
            prepare_enrichment(latest, scan["repository-inventory.json"], self.source, pending=True)

    def complete_business_batch(self, prepared):
        batch = copy.deepcopy(prepared["enrichment-proposals.json"])
        batch["provenance"] = {"agent": "Fixture", "model": "Synthetic", "version": "1"}
        evidence = {item["id"]: item for item in prepared["feature-manifest.json"]["evidence"]}
        for proposal in batch["proposals"]:
            context_id = next(item["id"] for item in proposal["evidence"]
                              if evidence[item["id"]]["type"] == "source-context")
            proposal["rationale"] = "Synthetic business interpretation for multi-batch workflow verification"
            proposal["updates"] = {
                "name": "Assign promotion to a location", "domain": "Promotions",
                "semanticAnalysis": analysis(context_id),
                "behaviors": [{
                    "id": "assignment", "description": "Assign promotion to an eligible location",
                    "mandatory": True, "evidenceRefs": [context_id],
                }],
            }
        return import_enrichment(prepared["feature-manifest.json"], batch)["feature-manifest.json"]

    def test_pending_cli_resumes_without_offset_and_status_does_not_fail_on_remaining_work(self):
        manifest_path = self.root / "manifest.json"
        manifest_path.write_text(json.dumps(self.document), encoding="utf-8")
        inventory_path = self.root / "inventory.json"
        inventory_path.write_text(json.dumps(self.inventory), encoding="utf-8")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(main(["parity", "enrichment-status", "--manifest", str(manifest_path)]), 0)
        summary = json.loads(stdout.getvalue())
        self.assertEqual(summary["completionState"], "continue")
        self.assertEqual(summary["statistics"]["pendingCount"], 1)
        self.assertEqual(len(summary["nextFeatureIds"]), 1)
        self.assertNotIn("pending", summary)
        arguments = ["parity", "prepare-enrichment", "--manifest", str(manifest_path),
                     "--inventory", str(inventory_path), "--source", str(self.source),
                     "--pending", "--output", str(self.root / "pending-batch")]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(arguments + ["--dry-run"]), 0)
            self.assertFalse((self.root / "pending-batch").exists())
            self.assertEqual(main(arguments), 0)
        persisted = json.loads((self.root / "pending-batch" / "enrichment-progress.json").read_text(encoding="utf-8"))
        self.assertEqual(persisted["completionState"], "continue")
        self.assertEqual(persisted["pending"][0]["featureId"], summary["nextFeatureIds"][0])


class EnrichmentProgressTests(unittest.TestCase):
    def test_actual_size_first_twenty_leaves_548_to_process(self):
        document = manifest()
        base = document["features"][0]
        document["features"] = [dict(copy.deepcopy(base), id=f"feature-{index:04}") for index in range(568)]
        for feature in document["features"][50:70]:
            feature["semanticAnalysis"] = analysis()
        progress = enrichment_progress(document)
        self.assertEqual(progress["statistics"], {
            "activeCount": 568, "businessReadyCount": 20, "pendingCount": 548, "blockedCount": 0,
        })
        self.assertEqual(progress["completionState"], "continue")
        self.assertEqual(progress["nextFeatureIds"], [f"feature-{index:04}" for index in range(20)])
        self.assertEqual(progress, enrichment_progress(copy.deepcopy(document)))
        with self.assertRaisesRegex(ArtifactError, "continue"):
            validate_business_meaning(document)

    def test_blocked_candidate_cannot_starve_unstarted_work(self):
        document = manifest()
        document["features"][0]["semanticAnalysis"] = analysis()
        document["features"][0]["semanticAnalysis"].update(
            status="unresolved", unresolvedQuestions=["Dynamic policy source unavailable"],
        )
        pending = copy.deepcopy(document["features"][0])
        pending["id"] = "other.pending"
        pending.pop("semanticAnalysis")
        inactive = copy.deepcopy(pending)
        inactive.update(id="other.deprecated", status="deprecated")
        document["features"].extend([pending, inactive])
        progress = enrichment_progress(document)
        self.assertEqual(progress["completionState"], "continue")
        self.assertEqual(progress["nextFeatureIds"], ["other.pending"])
        self.assertEqual(progress["statistics"]["blockedCount"], 1)
        self.assertEqual(progress["blocked"][0]["unresolvedQuestions"], ["Dynamic policy source unavailable"])
        pending["semanticAnalysis"] = analysis()
        progress = enrichment_progress(document)
        self.assertEqual(progress["completionState"], "blocked")
        self.assertEqual(progress["nextFeatureIds"], [])
        self.assertEqual(progress["statistics"]["activeCount"], 2)

    def test_legacy_or_naming_only_enrichment_remains_pending_not_blocked(self):
        document = manifest()
        document["features"][0]["semanticAnalysis"] = analysis()
        document["features"][0]["semanticAnalysis"].pop("businessMeaning")
        progress = enrichment_progress(document)
        self.assertEqual(progress["completionState"], "continue")
        self.assertIn("Structured business meaning is missing", progress["pending"][0]["reasons"])
        document["features"] = []
        self.assertEqual(enrichment_progress(document)["completionState"], "empty")
        for limit in (0, 101, -1):
            with self.subTest(limit=limit), self.assertRaises(ArtifactError):
                enrichment_progress(document, limit)
