"""Template and router syntax only; no component execution or route resolution."""

import re
from html.parser import HTMLParser

from pygments.lexers import JavascriptLexer, TypeScriptLexer

from .lexical import mask_non_code


class TemplateReader(HTMLParser):
    def __init__(self, vue):
        super().__init__(convert_charrefs=True)
        self.vue = vue
        self.template_depth = 0
        self.ignored_depth = 0
        self.hits = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.ignored_depth += 1
            return
        if self.ignored_depth:
            return
        if tag == "template":
            self.template_depth += 1
        if self.vue and not self.template_depth:
            return
        attributes = {name for name, value in attrs}
        rules = []
        if self.vue:
            if tag == "form":
                rules.append("form")
            if any(name.split(".")[0] in {"@click", "@submit", "v-on:click", "v-on:submit"} for name in attributes):
                rules.append("user-action")
            if tag == "router-link" and attributes & {"to", ":to", "v-bind:to"}:
                rules.append("navigation")
        else:
            if tag == "form" and "ng-submit" in attributes:
                rules.append("form")
            if attributes & {"ng-click", "ng-submit"}:
                rules.append("user-action")
            if attributes & {"ui-sref", "ng-href"}:
                rules.append("navigation")
        for rule in rules:
            self.hits.append({
                "capabilityType": "ui", "evidenceType": "ui", "rule": rule,
                "line": self.getpos()[0], "column": self.getpos()[1],
                "label": f"{'Vue' if self.vue else 'AngularJS'} {rule}",
            })

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.ignored_depth = max(0, self.ignored_depth - 1)
        elif tag == "template":
            self.template_depth = max(0, self.template_depth - 1)


def extract_template(source, vue=False):
    reader = TemplateReader(vue)
    reader.feed(source)
    reader.close()
    issues = []
    if reader.template_depth or reader.ignored_depth:
        issues.append("Unclosed template/script/style markup may limit UI extraction")
    return reader.hits, issues


def extract_frontend_routes(source, typescript=False):
    code = mask_non_code(source, TypeScriptLexer() if typescript else JavascriptLexer())
    patterns = (
        (r"\bcreateRouter\s*\(|\bnew\s+VueRouter\s*\(", "Vue router-registration"),
        (r"\$routeProvider\s*\.\s*when\s*\(", "AngularJS route-registration"),
        (r"\$stateProvider\s*\.\s*state\s*\(", "AngularJS state-registration"),
    )
    hits = []
    for pattern, label in patterns:
        for match in re.finditer(pattern, code):
            hits.append({
                "capabilityType": "ui", "evidenceType": "route", "rule": "router-registration",
                "line": source.count("\n", 0, match.start()) + 1,
                "offset": match.start(), "label": label,
            })
    return sorted(hits, key=lambda item: item["offset"]), []