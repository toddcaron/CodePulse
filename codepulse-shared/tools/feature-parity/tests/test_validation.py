import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from feature_parity.validation import ArtifactError, validate_manifest


def manifest():
    return {
        "schemaVersion": "1.0",
        "application": {"name": "Fixture", "sourceType": "repository", "revision": None},
        "scan": {"coverage": "unknown", "limitations": ["Static evidence only"], "inventoryDigest": "a" * 64},
        "evidence": [{
            "id": "evidence-1", "type": "endpoint", "location": "src/users.cs",
            "lineStart": 1, "lineEnd": 4, "summary": "User creation endpoint",
            "contentHash": "b" * 64, "verification": "verified-original",
        }],
        "features": [{
            "id": "identity.create-user", "name": "Create User", "domain": "Identity",
            "capabilityType": "business", "fingerprint": "c" * 64,
            "status": "discovered", "aliases": [], "actors": ["Administrator"],
            "inputs": ["User profile"], "outputs": ["User account"],
            "preconditions": ["Authorized administrator"],
            "behaviors": [{"id": "create-account", "description": "Creates an account",
                           "mandatory": True, "evidenceRefs": ["evidence-1"]}],
            "evidenceRefs": ["evidence-1"],
            "confidence": {"level": "medium", "score": 0.6, "reasons": ["Endpoint evidence"]},
            "requiresHumanValidation": True,
        }],
        "reviewQueue": [],
    }


class ManifestValidationTests(unittest.TestCase):
    def test_valid_manifest(self):
        validate_manifest(manifest())

    def test_invalid_documents(self):
        mutations = [
            lambda document: document.update(schemaVersion="2.0"),
            lambda document: document["features"][0].update(evidenceRefs=[]),
            lambda document: document["features"][0].update(evidenceRefs=["unknown"]),
            lambda document: document["features"].append(copy.deepcopy(document["features"][0])),
            lambda document: document["evidence"].append(copy.deepcopy(document["evidence"][0])),
            lambda document: document["evidence"][0].update(lineEnd=0),
            lambda document: document["evidence"][0].update(location="../secret"),
            lambda document: document["evidence"][0].update(location="C:/secret"),
            lambda document: document["features"][0].update(requiresHumanValidation=False),
            lambda document: document["features"][0]["behaviors"][0].update(evidenceRefs=["unknown"]),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                document = manifest()
                mutate(document)
                with self.assertRaises(ArtifactError):
                    validate_manifest(document)


if __name__ == "__main__":
    unittest.main()