"""Extract explicitly marked prose as unresolved requirement proposals."""

import re

from .identity import digest
from .validation import ArtifactError


MARKER = re.compile(r"^(?:#{1,6} +)?Requirement: +(.+?)\s*$", re.IGNORECASE)


def extract_prose_requirements(text, application_name):
    lines = text.splitlines()
    requirements = []
    ranges = {}
    ignored = 0
    fence = None
    comment = False
    active = None
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        fenced = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence:
            closing = re.fullmatch(r" {0,3}(" + re.escape(fence[0]) + r"{" + str(len(fence)) + r",})[ \t]*", line)
            if closing:
                fence = None
            active = None
            ignored += bool(stripped)
            continue
        if "<!--" in line or comment:
            comment = "-->" not in line
            active = None
            ignored += bool(stripped)
            continue
        if fenced:
            fence = fenced.group(1)
            active = None
            ignored += 1
            continue
        marker = MARKER.fullmatch(line) if not line.startswith((" ", "\t", ">")) else None
        if marker:
            title = marker.group(1)
            if len(title) > 200:
                raise ArtifactError("Prose requirement title exceeds 200 characters")
            identifier = "prose." + digest({"title": title, "line": number})[:24]
            active = {
                "id": identifier, "name": title, "domain": "Unclassified",
                "capabilityType": "business", "actors": [], "inputs": [],
                "outputs": [], "preconditions": [],
                "behaviors": [{"id": "proposal", "description": title, "mandatory": False}],
                "acceptanceCriteria": [],
                "ambiguities": ["Prose proposal is not an approved atomic behavior; mandatory status and contract constraints are unresolved"],
            }
            requirements.append(active)
            ranges[identifier] = [number, number]
        elif not stripped or line.startswith("#"):
            active = None
            ignored += bool(stripped)
        elif active is not None:
            description = active["behaviors"][0]["description"] + "\n" + line
            if len(description) > 4000:
                raise ArtifactError("Prose requirement block exceeds 4000 characters")
            active["behaviors"][0]["description"] = description
            ranges[active["id"]][1] = number
        else:
            ignored += 1
        if len(requirements) > 10000:
            raise ArtifactError("Prose requirement count exceeds limit")
    return {
        "schemaVersion": "1.0", "applicationName": application_name,
        "requirements": requirements,
    }, {"format": "prose", "lineCount": max(1, len(lines)), "ranges": ranges,
        "ignoredNonemptyLines": ignored}