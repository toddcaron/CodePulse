import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ENGINE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ENGINE_ROOT.parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
SKILL_DIRECTORIES = ("codepulse-feature-parity", "codepulse-feature-parity-finder")


def tree_digest(root):
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            entries.append((path.relative_to(root).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest()))
        else:
            entries.append((path.relative_to(root).as_posix(), "<dir>"))
    return entries


class InstallationSmokeTests(unittest.TestCase):
    """Exercises the skills the way an end user installs them: copied out of this
    repository, invoked from an unrelated working directory."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.root = Path(cls.directory.name)
        cls.installation = cls.root / "installed-skills"
        ignore = shutil.ignore_patterns("__pycache__", "tests", ".gitignore")
        shutil.copytree(ENGINE_ROOT, cls.installation / "codepulse-shared" / "tools" / "feature-parity", ignore=ignore)
        shutil.copytree(REPOSITORY_ROOT / "codepulse-shared" / "schemas", cls.installation / "codepulse-shared" / "schemas")
        for name in SKILL_DIRECTORIES:
            shutil.copytree(REPOSITORY_ROOT / name, cls.installation / name, ignore=ignore)
        cls.cli = cls.installation / "codepulse-shared" / "tools" / "feature-parity" / "cli.py"
        cls.workspace = cls.root / "unrelated-workspace"
        cls.workspace.mkdir()

    def run_installed(self, *arguments):
        return subprocess.run(
            [sys.executable, "-B", str(self.cli), "parity", *arguments],
            cwd=self.workspace, capture_output=True, text=True, timeout=120,
        )

    def test_installed_skills_document_a_resolvable_engine_path(self):
        for name in SKILL_DIRECTORIES:
            skill = self.installation / name / "SKILL.md"
            body = skill.read_text(encoding="utf-8")
            self.assertIn("../codepulse-shared/tools/feature-parity/", body)
            engine = (skill.parent / "../codepulse-shared/tools/feature-parity").resolve()
            self.assertTrue((engine / "cli.py").is_file())
            self.assertTrue((engine / "README.md").is_file())

    def test_installed_engine_resolves_sibling_schemas(self):
        installed_schemas = self.installation / "codepulse-shared" / "schemas"
        self.assertTrue((installed_schemas / "feature-report-schema.json").is_file())
        completed = subprocess.run(
            [sys.executable, "-B", "-c",
             "import sys; sys.path.insert(0, sys.argv[1]); "
             "from feature_parity import validation; print(validation.SCHEMA_ROOT)",
             str(self.cli.parent)],
            cwd=self.workspace, capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(Path(completed.stdout.strip()), installed_schemas)

    def test_installed_discovery_and_report_workflow_leaves_the_source_untouched(self):
        source = self.root / "scanned-application"
        shutil.copytree(FIXTURES / "openapi-app", source)
        before = tree_digest(source)

        discovery = self.workspace / "discovery"
        found = self.run_installed(
            "find", "--source", str(source), "--output", str(discovery),
            "--application-name", "Installation Smoke API",
        )
        self.assertEqual(found.returncode, 0, found.stderr)
        self.assertEqual(json.loads(found.stdout)["candidateCount"], 2)

        validated = self.run_installed("validate", "--manifest", str(discovery / "feature-manifest.json"))
        self.assertEqual(validated.returncode, 0, validated.stderr)

        context = self.workspace / "prepared"
        prepared = self.run_installed(
            "prepare-enrichment", "--manifest", str(discovery / "feature-manifest.json"),
            "--inventory", str(discovery / "repository-inventory.json"), "--source", str(source),
            "--limit", "20", "--output", str(context),
        )
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        proposal_path = context / "enrichment-proposals.json"
        proposals = json.loads(proposal_path.read_text(encoding="utf-8"))
        proposals["provenance"] = {"agent": "Smoke fixture", "model": "Synthetic", "version": "1"}
        for proposal in proposals["proposals"]:
            proposal["rationale"] = "OpenAPI declarations lack implementation bodies"
            proposal["updates"] = {
                "name": "Manage user accounts", "domain": "Identity",
                "behaviors": [{
                    "id": "declared-user-contract", "description": "Documents user account management",
                    "mandatory": False, "evidenceRefs": [item["id"] for item in proposal["evidence"]],
                }],
                "semanticAnalysis": {
                "status": "partial", "summary": "Declared API capability; implementation requires review",
                "businessMeaning": {
                    "purpose": "Provide user account administration",
                    "userGoal": "An account administrator manages application users",
                    "trigger": "The declared user operations are requested",
                    "outcome": "User account management is exposed as a documented API contract",
                    "basis": "inferred",
                },
                "evidenceRefs": [item["id"] for item in proposal["evidence"]],
                "businessRules": [], "unresolvedQuestions": ["Implementation is not present in this fixture"],
            }}
        proposal_path.write_text(json.dumps(proposals), encoding="utf-8")
        enriched = self.workspace / "enriched"
        imported = self.run_installed(
            "import-enrichment", "--manifest", str(context / "feature-manifest.json"),
            "--enrichment", str(proposal_path), "--output", str(enriched),
        )
        self.assertEqual(imported.returncode, 0, imported.stderr)
        report = self.workspace / "discovery-report"
        rendered = self.run_installed(
            "report", "--artifact", str(enriched / "feature-manifest.json"),
            "--output", str(report), "--format", "both",
        )
        self.assertEqual(rendered.returncode, 0, rendered.stderr)
        self.assertEqual(
            sorted(path.name for path in report.iterdir()),
            ["feature-report.html", "feature-report.json", "feature-report.md"],
        )
        document = json.loads((report / "feature-report.json").read_text(encoding="utf-8"))
        self.assertEqual(document["reportType"], "discovery")
        self.assertEqual(document["applications"][0]["name"], "Installation Smoke API")
        self.assertEqual(document["semanticStatus"], "incomplete")
        self.assertEqual(len(document["capabilities"]), 2)
        self.assertTrue((report / "feature-report.html").read_text(encoding="utf-8").startswith("<!doctype html>"))

        self.assertEqual(tree_digest(source), before)

    def test_installed_engine_is_not_written_to_during_a_run(self):
        source = self.root / "isolation-application"
        if not source.exists():
            shutil.copytree(FIXTURES / "openapi-app", source)
        before = tree_digest(self.installation)
        discovery = self.workspace / "isolation-discovery"
        found = self.run_installed("find", "--source", str(source), "--output", str(discovery))
        self.assertEqual(found.returncode, 0, found.stderr)
        rendered = self.run_installed(
            "report", "--artifact", str(discovery / "feature-manifest.json"),
            "--output", str(self.workspace / "isolation-report"), "--inventory-only",
        )
        self.assertEqual(rendered.returncode, 0, rendered.stderr)
        self.assertEqual(tree_digest(self.installation), before)


if __name__ == "__main__":
    unittest.main()
