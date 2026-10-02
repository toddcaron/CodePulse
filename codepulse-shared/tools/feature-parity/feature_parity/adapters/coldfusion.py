"""Tag-based ColdFusion declarations; CFScript is deliberately not interpreted."""

import re
from html.parser import HTMLParser


def _mask_cf_comments(source):
    characters = list(source)
    position = 0
    depth = 0
    while position < len(source):
        if source.startswith("<!---", position):
            depth += 1
            length = 5
        elif depth and source.startswith("--->", position):
            depth -= 1
            length = 4
            for offset in range(position, position + length):
                characters[offset] = " "
            position += length
            continue
        else:
            length = 1
        if depth:
            for offset in range(position, min(position + length, len(source))):
                if characters[offset] not in "\r\n":
                    characters[offset] = " "
        position += length
    return "".join(characters), depth > 0


class ColdFusionReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ignored_depth = 0
        self.hits = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.ignored_depth += 1
            return
        if self.ignored_depth:
            return
        attributes = dict(attrs)
        spec = None
        if tag == "cffunction" and (attributes.get("access") or "").casefold() == "remote":
            spec = ("api", "endpoint", "remote-function")
        elif tag == "cfform":
            spec = ("ui", "ui", "form")
        elif tag in {"cfhttp", "cfmail", "cfftp"}:
            spec = ("integrations", "integration", tag[2:])
        elif tag == "cfreport":
            spec = ("reports", "report", "report")
        elif tag == "cfschedule":
            spec = ("jobs", "job", "scheduled-task")
        if spec:
            capability, evidence, rule = spec
            self.hits.append({
                "capabilityType": capability, "evidenceType": evidence, "rule": rule,
                "line": self.getpos()[0], "column": self.getpos()[1],
                "label": f"ColdFusion {rule}",
            })

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.ignored_depth = max(0, self.ignored_depth - 1)


def extract_coldfusion(source):
    masked, unclosed = _mask_cf_comments(source)
    if re.search(r"<\s*cfscript\b", masked, re.IGNORECASE):
        return [], ["ColdFusion files containing CFScript were deferred; strings and executable semantics are unresolved"]
    reader = ColdFusionReader()
    reader.feed(masked)
    reader.close()
    issues = []
    if unclosed or reader.ignored_depth:
        issues.append("Unclosed ColdFusion comments or script/style markup limited extraction")
    return reader.hits, issues