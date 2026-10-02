import unittest

from test_validation import manifest
from feature_parity.adapters.frontend import extract_frontend_routes, extract_template
from feature_parity.adapters.coldfusion import extract_coldfusion


class FrontendAdapterTests(unittest.TestCase):
    def test_vue_template_forms_actions_navigation(self):
        source = '<template>\n<form @submit.prevent="save"><button @click="save">Save</button></form>\n<router-link to="/users">Users</router-link>\n</template>'
        hits, issues = extract_template(source, vue=True)
        self.assertEqual([item["rule"] for item in hits], ["form", "user-action", "user-action", "navigation"])
        self.assertEqual({item["line"] for item in hits}, {2, 3})

    def test_vue_comments_script_strings_and_style_ignored(self):
        source = '<template><!-- <form @submit="fake"> --><p>Hello</p></template>\n<script>const fake = "<form @submit=\'fake\'>";</script>\n<style>content: "<form>";</style>'
        hits, issues = extract_template(source, vue=True)
        self.assertEqual(hits, [])

    def test_angular_html(self):
        hits, issues = extract_template('<form ng-submit="save()"><button ng-click="save()">Save</button></form><a ui-sref="users">Users</a>')
        self.assertEqual(len(hits), 4)
        self.assertTrue(all(item["label"].startswith("AngularJS") for item in hits))

    def test_generic_html_does_not_invent_angular(self):
        hits, issues = extract_template('<form><button>Save</button></form>')
        self.assertEqual(hits, [])

    def test_router_registration_comments_strings_ignored(self):
        source = '// createRouter({});\nconst fake = "$routeProvider.when(\'/fake\')";\nconst router = createRouter({ routes });\n$routeProvider.when("/users", {});\n$stateProvider.state("users", {});'
        hits, issues = extract_frontend_routes(source)
        self.assertEqual([item["line"] for item in hits], [3, 4, 5])

    def test_typescript_router(self):
        hits, issues = extract_frontend_routes('const router: Router = createRouter({routes});', typescript=True)
        self.assertEqual(len(hits), 1)

    def test_router_names_alone_are_not_declarations(self):
        hits, issues = extract_frontend_routes('const createRouterExample = {}; function state() {}')
        self.assertEqual(hits, [])

    def test_unclosed_template_is_disclosed(self):
        hits, issues = extract_template('<template><button @click="save">Save</button>', vue=True)
        self.assertEqual(len(hits), 1)
        self.assertTrue(issues)


class ColdFusionAdapterTests(unittest.TestCase):
    def test_remote_and_scheduled_integration_report_form(self):
        source = '<cffunction name="create" access="remote">\n<cfhttp url="https://example.invalid">\n<cfmail to="test@example.invalid">\n<cfschedule action="update">\n<cfreport template="report.cfr">\n<cfform></cfform></cffunction>'
        hits, issues = extract_coldfusion(source)
        self.assertEqual([item["capabilityType"] for item in hits], ["api", "integrations", "integrations", "jobs", "reports", "ui"])

    def test_nested_comments_and_ordinary_comments_ignored(self):
        source = '<!--- outer <!--- <cfhttp> ---> <cfmail> --->\n<!-- <cfschedule> -->\n<cfform></cfform>'
        hits, issues = extract_coldfusion(source)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["line"], 3)

    def test_local_functions_and_tables_are_not_features(self):
        hits, issues = extract_coldfusion('<cffunction access="private"></cffunction><cfquery>select * from Users</cfquery>')
        self.assertEqual(hits, [])

    def test_script_string_examples_are_deferred(self):
        hits, issues = extract_coldfusion('<cfscript>var fake = "<cfhttp>";</cfscript>')
        self.assertEqual(hits, [])
        self.assertTrue(issues)

    def test_unclosed_cf_comment_is_disclosed(self):
        hits, issues = extract_coldfusion('<!--- <cfhttp>')
        self.assertEqual(hits, [])
        self.assertTrue(issues)

    def test_script_tags_are_ignored(self):
        hits, issues = extract_coldfusion('<script>const example = "<cfform>";</script>')
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()