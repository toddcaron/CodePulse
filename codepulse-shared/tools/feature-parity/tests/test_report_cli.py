import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_comparison import approve
from test_requirements_coverage import reviewed_baseline
from test_validation import manifest
from feature_parity.cli import main
from feature_parity.comparison import compare_manifests
from feature_parity.requirements_coverage import compare_requirements
from feature_parity.validation import load_json, validate_schema


ROOT = Path(__file__).resolve().parents[1]


class ReportCliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.manifest = self.root / "feature-manifest.json"
        self.manifest.write_text(json.dumps(manifest()), encoding="utf-8")
        self.output = self.root / "report"

    def run_cli(self, *arguments):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main(["parity", "report", *arguments])

    def run_manifest_report(self, *extra):
        return self.run_cli("--artifact", str(self.manifest), "--output", str(self.output), *extra)

    def comparison_files(self):
        source = approve(manifest())
        target = json.loads(json.dumps(source))
        result = compare_manifests(source, target)
        paths = (self.root / "source.json", self.root / "target.json", self.root / "parity-results.json")
        for path, document in zip(paths, (source, target, result)):
            path.write_text(json.dumps(document), encoding="utf-8")
        return paths

    def coverage_files(self):
        baseline, reviews = reviewed_baseline()
        target = approve(manifest())
        result = compare_requirements(baseline, reviews, target)
        paths = (self.root / "baseline.json", self.root / "coverage-target.json", self.root / "coverage.json")
        for path, document in zip(paths, (baseline, target, result)):
            path.write_text(json.dumps(document), encoding="utf-8")
        return paths

    def test_default_format_writes_report_object_and_html(self):
        self.assertEqual(self.run_manifest_report(), 0)
        self.assertEqual(
            sorted(path.name for path in self.output.iterdir()),
            ["feature-report.html", "feature-report.json"],
        )
        validate_schema(load_json(self.output / "feature-report.json"), "feature-report-schema.json")
        self.assertTrue((self.output / "feature-report.html").read_text(encoding="utf-8").startswith("<!doctype html>"))

    def test_markdown_is_opt_in(self):
        self.assertEqual(self.run_manifest_report("--format", "markdown"), 0)
        self.assertEqual(
            sorted(path.name for path in self.output.iterdir()),
            ["feature-report.json", "feature-report.md"],
        )

    def test_both_formats_are_supported(self):
        self.assertEqual(self.run_manifest_report("--format", "both"), 0)
        self.assertEqual(
            sorted(path.name for path in self.output.iterdir()),
            ["feature-report.html", "feature-report.json", "feature-report.md"],
        )

    def test_report_does_not_mutate_inputs(self):
        before = self.manifest.read_bytes()
        self.assertEqual(self.run_manifest_report(), 0)
        self.assertEqual(self.manifest.read_bytes(), before)

    def test_dry_run_writes_nothing(self):
        self.assertEqual(self.run_manifest_report("--dry-run"), 0)
        self.assertFalse(self.output.exists())

    def test_existing_output_is_rejected(self):
        self.output.mkdir()
        self.assertEqual(self.run_manifest_report(), 5)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_output_overlapping_an_input_is_rejected(self):
        self.output = self.root
        self.assertEqual(self.run_manifest_report(), 5)

    def test_comparison_report_requires_both_manifests(self):
        source, target, result = self.comparison_files()
        self.assertEqual(self.run_cli("--artifact", str(result), "--output", str(self.output)), 1)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.run_cli(
            "--artifact", str(result), "--source", str(source), "--output", str(self.output),
        ), 1)
        self.assertEqual(self.run_cli(
            "--artifact", str(result), "--source", str(source), "--target", str(target),
            "--output", str(self.output),
        ), 0)
        report = load_json(self.output / "feature-report.json")
        self.assertEqual(report["reportType"], "comparison")

    def test_unaccepted_supporting_input_is_rejected(self):
        source, target, result = self.comparison_files()
        baseline, _, _ = self.coverage_files()
        self.assertEqual(self.run_cli(
            "--artifact", str(result), "--source", str(source), "--target", str(target),
            "--baseline", str(baseline), "--output", str(self.output),
        ), 1)
        self.assertEqual(self.run_cli(
            "--artifact", str(self.manifest), "--target", str(target), "--output", str(self.output),
        ), 1)
        self.assertFalse(self.output.exists())

    def test_stale_supporting_manifest_is_an_artifact_failure(self):
        source, target, result = self.comparison_files()
        stale = load_json(source)
        stale["application"]["name"] = "Renamed baseline"
        source.write_text(json.dumps(stale), encoding="utf-8")
        self.assertEqual(self.run_cli(
            "--artifact", str(result), "--source", str(source), "--target", str(target),
            "--output", str(self.output),
        ), 3)
        self.assertFalse(self.output.exists())

    def test_coverage_report_requires_baseline_and_target(self):
        baseline, target, result = self.coverage_files()
        self.assertEqual(self.run_cli("--artifact", str(result), "--output", str(self.output)), 1)
        self.assertEqual(self.run_cli(
            "--artifact", str(result), "--baseline", str(baseline), "--target", str(target),
            "--output", str(self.output), "--format", "both",
        ), 0)
        report = load_json(self.output / "feature-report.json")
        self.assertEqual(report["reportType"], "requirements-coverage")
        self.assertIn("Requirement coverage", (self.output / "feature-report.md").read_text(encoding="utf-8"))

    def test_unsupported_artifact_is_rejected(self):
        unsupported = self.root / "unsupported.json"
        unsupported.write_text('{"schemaVersion": "1.0"}', encoding="utf-8")
        self.assertEqual(self.run_cli("--artifact", str(unsupported), "--output", str(self.output)), 3)

    def test_missing_artifact_is_an_access_failure(self):
        self.manifest.unlink()
        self.assertEqual(self.run_manifest_report(), 2)

    def test_real_entry_point_from_unrelated_directory(self):
        completed = subprocess.run([
            sys.executable, "-B", str(ROOT / "cli.py"), "parity", "report",
            "--artifact", str(self.manifest), "--output", str(self.output), "--format", "both",
        ], cwd=self.root, capture_output=True, text=True, timeout=60)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["reportType"], "discovery")
        self.assertIn("## Limitations", (self.output / "feature-report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
