import unittest
from pathlib import Path

import test_validation
from feature_parity.prose_requirements import extract_prose_requirements
from feature_parity.requirements import ingest_requirements, validate_requirements_baseline
from feature_parity.validation import ArtifactError


class ProseRequirementsTests(unittest.TestCase):
    def extract(self, text):
        return extract_prose_requirements(text, "Synthetic Requirements")

    def test_explicit_markers_preserve_lines_without_inference(self):
        text = "# Notes\n\n## Requirement: Create user\nThe administrator shall create an account.\n\nRequirement: Disable user\nDisable an account.\n"
        document, source_map = self.extract(text)
        self.assertEqual(list(source_map["ranges"].values()), [[3, 4], [6, 7]])
        self.assertEqual(document["requirements"][0]["actors"], [])
        self.assertFalse(document["requirements"][0]["behaviors"][0]["mandatory"])
        self.assertIn("shall", document["requirements"][0]["behaviors"][0]["description"])
        artifacts = ingest_requirements(document, "requirements.md", "a" * 64, 7, source_map)
        validate_requirements_baseline(artifacts["requirements-baseline.json"])
        self.assertEqual(artifacts["feature-manifest.json"]["features"][0]["status"], "needs-review")

    def test_examples_comments_quotes_and_unmarked_prose_are_not_obligations(self):
        text = "```text\nRequirement: Code example\n```\n<!--\nRequirement: Comment\n-->\n> Requirement: Quoted text\n    Requirement: Indented code\nThe system shall create accounts.\n"
        document, source_map = self.extract(text)
        self.assertEqual(document["requirements"], [])
        self.assertGreater(source_map["ignoredNonemptyLines"], 0)

    def test_duplicate_titles_have_distinct_provisional_ids(self):
        document, source_map = self.extract("Requirement: Same\n\nRequirement: Same\n")
        self.assertEqual(len(source_map["ranges"]), 2)
        self.assertNotEqual(document["requirements"][0]["id"], document["requirements"][1]["id"])

    def test_invalid_ranges_and_map_links_fail(self):
        for bounds in ([3, 2], [1, 99]):
            document, source_map = self.extract("Requirement: Create user\n")
            source_map["ranges"][document["requirements"][0]["id"]] = bounds
            with self.assertRaises(ArtifactError):
                ingest_requirements(document, "requirements.txt", "a" * 64, 1, source_map)

    def test_replay_and_line_endings(self):
        self.assertEqual(self.extract("Requirement: Test\r\nDescription\r\n"), self.extract("Requirement: Test\nDescription\n"))

    def test_oversized_proposal_fails(self):
        with self.assertRaises(ArtifactError):
            self.extract("Requirement: " + "x" * 201)
        with self.assertRaises(ArtifactError):
            self.extract("Requirement: Test\n" + "x" * 4001)

    def test_fence_with_trailing_info_cannot_close_code_example(self):
        document, source_map = self.extract("```\n<!-- literal comment\n```python\nRequirement: Example\n```\nRequirement: Real\n")
        self.assertEqual([item["name"] for item in document["requirements"]], ["Real"])
        self.assertEqual(list(source_map["ranges"].values()), [[6, 6]])

    def test_missing_or_malformed_source_maps_fail_as_artifacts(self):
        document, source_map = self.extract("Requirement: Test\n")
        source_map["ranges"].clear()
        with self.assertRaises(ArtifactError):
            ingest_requirements(document, "requirements.md", "a" * 64, 1, source_map)
        with self.assertRaises(ArtifactError):
            ingest_requirements(document, "requirements.md", "a" * 64, 1, {})

    def test_continuation_whitespace_is_preserved(self):
        document, _ = self.extract("Requirement: Test\n  An explicit indented description.  \n")
        self.assertEqual(document["requirements"][0]["behaviors"][0]["description"], "Test\n  An explicit indented description.  ")

    def test_checked_in_markdown_example(self):
        text = (Path(__file__).resolve().parents[1] / "examples" / "requirements.md").read_text(encoding="utf-8")
        document, source_map = self.extract(text)
        self.assertEqual([item["name"] for item in document["requirements"]], ["Create User", "Disable User"])
        self.assertEqual(list(source_map["ranges"].values()), [[5, 7], [9, 11]])