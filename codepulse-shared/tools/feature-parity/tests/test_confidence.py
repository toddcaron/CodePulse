import unittest

from test_validation import manifest
from feature_parity.confidence import admitted, confidence_level, declaration_confidence, lexical_endpoint_confidence, syntax_declaration_confidence
from feature_parity.validation import ArtifactError, validate_manifest


class ConfidenceTests(unittest.TestCase):
    def test_boundaries(self):
        for score, level in ((0, "low"), (0.499, "low"), (0.5, "medium"), (0.799, "medium"), (0.8, "high"), (1, "high")):
            with self.subTest(score=score):
                self.assertEqual(confidence_level(score), level)

    def test_provisional_sources_stay_below_medium(self):
        for confidence in (declaration_confidence(), lexical_endpoint_confidence(), syntax_declaration_confidence()):
            self.assertTrue(admitted(confidence, "low"))
            self.assertFalse(admitted(confidence, "medium"))
            self.assertFalse(admitted(confidence, "high"))

    def test_mislabelled_confidence_rejected(self):
        document = manifest()
        document["features"][0]["confidence"]["level"] = "high"
        with self.assertRaises(ArtifactError):
            validate_manifest(document)


if __name__ == "__main__":
    unittest.main()