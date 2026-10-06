import copy
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from test_validation import manifest
from test_comparison import approve
from test_reviews import review_batch
from feature_parity.comparison import compare_manifests, gate_failed
from feature_parity.cli import main
from feature_parity.enrichment import enrichment_template, import_enrichment
from feature_parity.identity import contract_digest, digest
from feature_parity.reviews import reconcile_manifest, review_template
from feature_parity.validation import ArtifactError


def enrichment_batch(document):
    feature = document["features"][0]
    return {
        "schemaVersion": "1.0", "baseManifestDigest": digest(document),
        "inventoryDigest": document["scan"]["inventoryDigest"],
        "provenance": {"agent": "Synthetic proposal agent", "model": "Synthetic model", "version": "fixture-1"},
        "proposals": [{"id": "proposal-1", "featureId": feature["id"],
                       "expectedContractDigest": contract_digest(feature, document["evidence"]),
                       "evidence": [{"id": item["id"], "contentHash": item["contentHash"], "recordDigest": digest(item)}
                                    for item in document["evidence"] if item["id"] in feature["evidenceRefs"]],
                       "updates": {"name": "Provision User"}, "rationale": "Synthetic evidence-linked naming proposal"}],
    }


class EnrichmentTests(unittest.TestCase):
    def test_template_is_deterministic_and_not_importable_until_completed(self):
        document = manifest()
        template = enrichment_template(document)
        self.assertEqual(template, enrichment_template(document))
        with self.assertRaises(ArtifactError):
            import_enrichment(document, template)
        template["provenance"] = enrichment_batch(document)["provenance"]
        template["proposals"][0]["updates"] = {"name": "Proposed"}
        template["proposals"][0]["rationale"] = "Synthetic rationale"
        self.assertEqual(import_enrichment(document, template)["feature-manifest.json"]["features"][0]["status"], "needs-review")

    def test_cli_persists_proposals_audit_and_reviewable_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document = approve(manifest())
            source = root / "manifest.json"
            source.write_text(json.dumps(document), encoding="utf-8")
            template_dir = root / "template"
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["parity", "enrichment-template", "--manifest", str(source), "--output", str(template_dir)]), 0)
                proposal_file = template_dir / "enrichment-proposals.json"
                self.assertEqual(main(["parity", "import-enrichment", "--manifest", str(source), "--enrichment", str(proposal_file), "--output", str(root / "invalid")]), 3)
                self.assertFalse((root / "invalid").exists())
                proposal_file.write_text(json.dumps(enrichment_batch(document)), encoding="utf-8")
                arguments = ["parity", "import-enrichment", "--manifest", str(source), "--enrichment", str(proposal_file), "--output", str(root / "imported")]
                self.assertEqual(main(arguments + ["--dry-run"]), 0)
                self.assertFalse((root / "imported").exists())
                self.assertEqual(main(arguments), 0)
                self.assertEqual(main(arguments), 5)
            artifacts = {item.name: json.loads(item.read_text(encoding="utf-8")) for item in (root / "imported").iterdir()}
            self.assertEqual(set(artifacts), {"feature-manifest.json", "enrichment-proposals.json", "enrichment-log.json", "review-queue.json"})
            self.assertEqual(artifacts["enrichment-proposals.json"], enrichment_batch(document))
            self.assertEqual(artifacts["feature-manifest.json"]["features"][0]["status"], "needs-review")
            self.assertEqual(json.loads(source.read_text(encoding="utf-8")), document)

    def test_import_preserves_identity_evidence_confidence_and_original(self):
        document = approve(manifest())
        batch = enrichment_batch(document)
        original = copy.deepcopy((document, batch))
        artifacts = import_enrichment(document, batch)
        result = artifacts["feature-manifest.json"]
        feature = result["features"][0]
        self.assertEqual(feature["name"], "Provision User")
        self.assertEqual(feature["id"], document["features"][0]["id"])
        self.assertEqual(feature["fingerprint"], document["features"][0]["fingerprint"])
        self.assertEqual(feature["confidence"], document["features"][0]["confidence"])
        self.assertEqual(result["evidence"], document["evidence"])
        self.assertNotIn("review", feature)
        self.assertEqual(feature["status"], "needs-review")
        self.assertEqual(artifacts["enrichment-log.json"]["statistics"]["approvalsWithdrawn"], 1)
        self.assertEqual((document, batch), original)

    def test_unapproved_enrichment_cannot_earn_gate_credit(self):
        document = approve(manifest())
        result = import_enrichment(document, enrichment_batch(document))["feature-manifest.json"]
        comparison = compare_manifests(result, document)
        self.assertEqual(comparison["statistics"]["equivalentCount"], 0)
        self.assertTrue(gate_failed(comparison, "unverified"))
        template = review_template(result)
        self.assertEqual(template["decisions"][0]["approvedReference"], "")

    def test_agent_cannot_set_approvals_status_identity_confidence_or_totals(self):
        document = manifest()
        for field, value in (("review", {}), ("status", "confirmed"), ("admitted", True), ("confidence", {}),
                             ("id", "new.id"), ("requiresHumanValidation", False), ("statistics", {})):
            batch = enrichment_batch(document)
            batch["proposals"][0]["updates"][field] = value
            with self.subTest(field=field), self.assertRaises(ArtifactError):
                import_enrichment(document, batch)

    def test_stale_digests_and_evidence_metadata_are_rejected(self):
        document = manifest()
        mutations = [
            lambda batch: batch.update(baseManifestDigest="0" * 64),
            lambda batch: batch.update(inventoryDigest="0" * 64),
            lambda batch: batch["proposals"][0].update(expectedContractDigest="0" * 64),
            lambda batch: batch["proposals"][0]["evidence"][0].update(contentHash="0" * 64),
            lambda batch: batch["proposals"][0]["evidence"][0].update(recordDigest="0" * 64),
            lambda batch: batch["proposals"][0].update(featureId="unknown"),
            lambda batch: batch["proposals"].append(copy.deepcopy(batch["proposals"][0])),
            lambda batch: batch["proposals"][0].update(updates={}),
        ]
        for mutation in mutations:
            batch = enrichment_batch(document)
            mutation(batch)
            with self.subTest(mutation=mutation), self.assertRaises(ArtifactError):
                import_enrichment(document, batch)

    def test_invalid_behavior_refs_fail_without_mutating_original(self):
        document = manifest()
        original = copy.deepcopy(document)
        batch = enrichment_batch(document)
        batch["proposals"][0]["updates"]["behaviors"] = [{"id": "proposal", "description": "Unapproved behavior",
                                                        "mandatory": True, "evidenceRefs": ["unknown"]}]
        with self.assertRaises(ArtifactError):
            import_enrichment(document, batch)
        self.assertEqual(document, original)

    def test_human_review_is_separate_and_never_upgrades_evidence(self):
        document = manifest()
        document["features"][0]["admitted"] = False
        document["evidence"][0]["verification"] = "partially-verified"
        imported = import_enrichment(document, enrichment_batch(document))["feature-manifest.json"]
        reviewed = reconcile_manifest(imported, review_batch(imported))["feature-manifest.json"]
        self.assertFalse(reviewed["features"][0]["admitted"])
        self.assertEqual(reviewed["evidence"], document["evidence"])
        self.assertEqual(compare_manifests(reviewed, reviewed)["statistics"]["equivalentCount"], 0)

    def test_replay_is_deterministic_and_old_batch_is_stale_after_import(self):
        document = manifest()
        batch = enrichment_batch(document)
        first = import_enrichment(document, batch)
        self.assertEqual(first, import_enrichment(document, batch))
        with self.assertRaises(ArtifactError):
            import_enrichment(first["feature-manifest.json"], batch)