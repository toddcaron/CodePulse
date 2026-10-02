import unittest

from test_validation import manifest
from feature_parity.adapters.dotnet import extract_dotnet


class DotnetAdapterTests(unittest.TestCase):
    def test_http_attributes_and_minimal_api(self):
        source = ('[Authorize, HttpPost("/users")]\npublic void CreateUser() {}\n'
                  'app.MapGet("/users", () => Results.Ok());\n')
        hits, issues = extract_dotnet(source)
        self.assertEqual([(item["method"], item["line"]) for item in hits], [("POST", 1), ("GET", 3)])
        self.assertFalse(issues)

    def test_comments_and_strings_are_not_endpoints(self):
        source = ('// [HttpPost]\n/* app.MapGet("/fake", Handler); */\n'
                  'var example = "app.MapPost(\\"/fake\\", Handler)";\n'
                  '[HttpGet]\npublic void Real() {}\n')
        hits, issues = extract_dotnet(source)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["line"], 4)

    def test_verbatim_and_raw_strings_do_not_generate_endpoints(self):
        source = 'var example = @"[HttpGet]";\nvar raw = """app.MapPost("/fake", Handler)""";'
        hits, issues = extract_dotnet(source)
        self.assertEqual(hits, [])

    def test_conditional_compilation_is_deferred(self):
        hits, issues = extract_dotnet('#if false\n[HttpGet]\n#endif')
        self.assertEqual(hits, [])
        self.assertTrue(issues)

    def test_class_names_do_not_invent_business_features(self):
        hits, issues = extract_dotnet('public class CreateUserController {}')
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()