import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_comparison import approve
from test_requirements_coverage import reviewed_baseline
from test_validation import manifest
from feature_parity.identity import digest
from feature_parity.validation import load_json, validate_manifest, validate_schema


ENGINE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ENGINE_ROOT.parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
FINDER_SKILL = REPOSITORY_ROOT / "codepulse-feature-parity-finder" / "SKILL.md"
PARITY_SKILL = REPOSITORY_ROOT / "codepulse-feature-parity" / "SKILL.md"


def skill_metadata(path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError(f"{path.name} has no YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise AssertionError(f"{path.name} has unterminated YAML frontmatter") from error
    metadata = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = value.strip().strip("'\"")
    return metadata, "\n".join(lines[end + 1:])


class PromptAcceptanceTests(unittest.TestCase):
    def run_cli(self, working_directory, *arguments):
        return subprocess.run(
            [sys.executable, "-B", str(ENGINE_ROOT / "cli.py"), "parity", *arguments],
            cwd=working_directory, capture_output=True, text=True, timeout=30,
        )

    def test_skill_discovery_metadata_routes_supported_prompts(self):
        finder_metadata, finder_body = skill_metadata(FINDER_SKILL)
        parity_metadata, parity_body = skill_metadata(PARITY_SKILL)

        self.assertEqual(finder_metadata["name"], FINDER_SKILL.parent.name)
        self.assertEqual(parity_metadata["name"], PARITY_SKILL.parent.name)
        for phrase in ("discover", "inventory", "application features", "local repository"):
            self.assertIn(phrase, finder_metadata["description"].lower())
        for phrase in ("feature parity", "compare", "reviewed feature manifests", "requirements coverage"):
            self.assertIn(phrase, parity_metadata["description"].lower())

        for phrase in ("parity find", "parity validate", "discovery-log.json", "provisional", "parity report", "by default"):
            self.assertIn(phrase, finder_body.lower())
        for phrase in ("parity compare", "cover-requirements", "approved mappings", "runtime parity", "parity report", "automatically"):
            self.assertIn(phrase, parity_body.lower())
        for phrase in ("semantic enrichment by default", "parity prepare-enrichment", "parity import-enrichment",
                       "inventory-only", "businessrules", "unresolvedquestions", "actual source",
                       "prepared", "latest imported manifest", "observed", "inferred", "not instructions"):
            self.assertIn(phrase, finder_body.lower())
        self.assertIn("partial or unresolved semantic analysis", parity_body.lower())

    def test_finder_prompt_contract_discovers_and_validates_synthetic_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "finder-results"
            completed = self.run_cli(
                root, "find", "--source", str(FIXTURES / "openapi-app"),
                "--output", str(output), "--application-name", "Prompt Acceptance API",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            statistics = json.loads(completed.stdout)
            self.assertEqual(statistics["candidateCount"], 2)
            self.assertEqual(statistics["needsReview"], 2)

            expected_artifacts = {
                "feature-manifest.json", "repository-inventory.json", "evidence-index.json",
                "review-queue.json", "discovery-log.json",
            }
            self.assertEqual({path.name for path in output.iterdir()}, expected_artifacts)
            validate_manifest(load_json(output / "feature-manifest.json"))

            validated = self.run_cli(
                root, "validate", "--manifest", str(output / "feature-manifest.json"),
            )
            self.assertEqual(validated.returncode, 0, validated.stderr)

    def test_parity_prompt_contract_applies_reviewed_mapping_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline = approve(manifest())
            target = manifest()
            target["features"][0]["id"] = "identity.register-user"
            target["features"][0]["name"] = "Register User"
            target = approve(target)
            source_path = root / "reviewed-baseline.json"
            target_path = root / "reviewed-target.json"
            mappings_path = root / "approved-mappings.json"
            source_path.write_text(json.dumps(baseline), encoding="utf-8")
            target_path.write_text(json.dumps(target), encoding="utf-8")
            mappings_path.write_text(json.dumps({
                "schemaVersion": "1.1",
                "baselineDigest": digest(baseline),
                "targetDigest": digest(target),
                "mappings": [{
                    "mappingType": "one-to-one",
                    "baselineFeatureIds": ["identity.create-user"],
                    "targetFeatureIds": ["identity.register-user"],
                    "decision": "same-capability",
                    "rationale": "Synthetic reviewed rename",
                    "differences": [],
                    "approvedReference": "Prompt acceptance review",
                }],
            }), encoding="utf-8")

            output = root / "comparison-results"
            completed = self.run_cli(
                root, "compare", "--source", str(source_path), "--target", str(target_path),
                "--mappings", str(mappings_path), "--output", str(output),
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = load_json(output / "parity-results.json")
            validate_schema(result, "feature-parity-result-schema.json")
            self.assertEqual(result["matches"][0]["matchingStage"], "approved-mapping")
            self.assertEqual(result["matches"][0]["status"], "equivalent")
            self.assertEqual(result["statistics"]["equivalentCount"], 1)

    def test_parity_prompt_contract_covers_reviewed_requirements_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline, reviews = reviewed_baseline()
            paths = {
                "baseline": root / "requirements-baseline.json",
                "reviews": root / "reviewed-requirements.json",
                "target": root / "reviewed-target.json",
            }
            for key, document in (
                ("baseline", baseline), ("reviews", reviews), ("target", approve(manifest())),
            ):
                paths[key].write_text(json.dumps(document), encoding="utf-8")

            output = root / "requirements-results"
            completed = self.run_cli(
                root, "cover-requirements", "--baseline", str(paths["baseline"]),
                "--reviews", str(paths["reviews"]), "--target", str(paths["target"]),
                "--output", str(output),
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = load_json(output / "requirements-coverage.json")
            validate_schema(result, "feature-requirements-coverage-schema.json")
            self.assertEqual(result["statistics"]["coveredCount"], 1)
            self.assertEqual(result["statistics"]["coveragePercent"], 100)


if __name__ == "__main__":
    unittest.main()
