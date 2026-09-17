"""Behavioral regression tests; all generated skills live in temporary folders."""
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("checker", ROOT / "scripts/check_skill.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.skill = Path(self.temp.name) / "demo"
        self.skill.mkdir()

    def write(self, text, name="SKILL.md"):
        path = self.skill / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def run_check(self, *args):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return checker.main([str(self.skill), *args])

    def header(self, name="demo", description="Valid description"):
        return f"---\nname: {name}\ndescription: {description}\n---\n"

    def test_folded_and_literal_description_limits(self):
        for style in (">", "|"):
            for count, expected in ((20, 0), (1100, 1)):
                with self.subTest(style=style, count=count):
                    self.write(self.header(description=style + "\n  " + "x" * count))
                    self.assertEqual(expected, self.run_check())

    def test_empty_and_non_string_description(self):
        for value in (">", "|", "null", "123", "[]", "true", '\'   \''):
            with self.subTest(value=value):
                self.write(self.header(description=value))
                self.assertEqual(1, self.run_check())

    def test_quoted_name_and_yaml_separator_in_value(self):
        self.write(self.header(name='"demo"', description='"a --- b"'))
        self.assertEqual(0, self.run_check())

    def test_invalid_names_even_when_directory_matches(self):
        for name in ("-demo", "demo-", "demo--bad", "a" * 65):
            checker.errors.clear()
            checker.check_frontmatter({"name": name, "description": "OK"}, Path(name))
            self.assertTrue(checker.errors, name)

    def test_invalid_yaml_and_duplicate_keys(self):
        for text in ("---\nname: [\n---\n", "---\n- demo\n---\n",
                     "---\nname: demo\nname: other\ndescription: OK\n---\n",
                     "---\nname: demo\ndescription: OK\nmetadata:\n  x: one\n  x: two\n---\n"):
            self.write(text)
            self.assertEqual(1, self.run_check())

    def test_missing_name_is_error(self):
        self.write("---\ndescription: OK\n---\n")
        self.assertEqual(1, self.run_check())

    def test_portable_metadata_and_extensions(self):
        self.write("---\nname: demo\ndescription: OK\nmetadata:\n  keywords: [one, two]\n---\n")
        self.assertEqual(1, self.run_check())
        self.write("---\nname: demo\ndescription: OK\ncontext: fork\n---\n")
        self.assertEqual(1, self.run_check())
        self.assertEqual(0, self.run_check("--profile", "claude-code"))

    def test_folded_keyword_stuffing(self):
        self.write(self.header(description='>\n  "a" "b" "c" "d" "e"'))
        self.assertEqual(2, self.run_check())
        self.assertEqual(1, self.run_check("--strict"))

    def test_fences_match_kind_and_length(self):
        for body, expected in (("~~~python\nx=1\n", 1),
                               ("```python\nx=1\n~~~\n", 1),
                               ("````markdown\n```python\nx=1\n```\n````\n", 0),
                               ("~~~python\nx=1\n~~~\n", 0)):
            with self.subTest(body=body):
                self.write(self.header() + body)
                self.assertEqual(expected, self.run_check())

    def test_links_with_anchors_and_spaces(self):
        self.write(self.header() + "[Guide](references/my%20guide.md#section)\n")
        self.assertEqual(1, self.run_check())
        self.write("# Section\n", "references/my guide.md")
        self.assertEqual(0, self.run_check())

    def test_relative_nested_reference_and_broken_link(self):
        self.write(self.header() + "`references/guide.md`\n")
        self.write("[Details](details.md)\n", "references/guide.md")
        self.write("# Details\n", "references/details.md")
        self.assertEqual(2, self.run_check())
        self.write(self.header() + "`references/guide.md` `references/details.md`\n")
        self.assertEqual(0, self.run_check())
        self.write("[Missing](missing.md)\n", "references/guide.md")
        self.assertEqual(1, self.run_check())

    def test_duplicate_basename_does_not_hide_orphan(self):
        self.write(self.header() + "`references/guide.md`\n")
        self.write("# Guide\n", "references/guide.md")
        self.write("# Other\n", "other/guide.md")
        self.assertEqual(2, self.run_check("--allow-dirs=other"))

    def test_missing_parent_relative_link_is_error(self):
        self.write(self.header() + "`references/guide.md`\n")
        self.write("[Missing](../missing.md)\n", "references/guide.md")
        self.assertEqual(1, self.run_check())

    def test_license_and_conventional_directories_are_allowed(self):
        self.write(self.header() + "`agents/reviewer.md`\n")
        self.write("License text", "LICENSE.txt")
        self.write("{}", "evals/evals.json")
        self.write("# Reviewer", "agents/reviewer.md")
        self.write("[Illustration](not-a-real-file.md)", "examples/sample.md")
        self.assertEqual(0, self.run_check("--strict"))

    def test_fenced_example_link_is_not_a_dependency(self):
        self.write(self.header() + "```markdown\n[Example](missing.md)\n```\n")
        self.assertEqual(0, self.run_check())

    def test_unknown_option_and_missing_path_are_usage_errors(self):
        self.write(self.header())
        self.assertEqual(3, self.run_check("--typo"))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(3, checker.main([str(self.skill / "missing")]))


class ScaffoldTests(unittest.TestCase):
    def run_scaffold(self, cwd, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts/scaffold_skill.py"), *args],
                              cwd=cwd, capture_output=True, text=True)

    def test_spaced_and_equals_options_create_requested_resources(self):
        for equals in (False, True):
            with self.subTest(equals=equals), tempfile.TemporaryDirectory() as directory:
                base = Path(directory) / "output with spaces"
                options = ([f"--dir={base}", "--with=references,scripts"] if equals else
                           ["--dir", str(base), "--with", "references,scripts"])
                result = self.run_scaffold(directory, "demo", *options)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertTrue((base / "demo/references/guide.md").is_file())
                self.assertTrue((base / "demo/scripts/run.py").is_file())
                result = subprocess.run([sys.executable, str(base / "demo/scripts/run.py")], capture_output=True)
                self.assertEqual(0, result.returncode, result.stderr)

    def test_unknown_options_and_bad_names_make_no_files(self):
        with tempfile.TemporaryDirectory() as directory:
            for args in (("demo", "--typo"), ("demo--bad",), ("demo", "--with=oops")):
                self.assertEqual(3, self.run_scaffold(directory, *args).returncode)
                self.assertEqual([], list(Path(directory).iterdir()))

    def test_existing_skill_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(0, self.run_scaffold(directory, "demo").returncode)
            path = Path(directory) / "demo/SKILL.md"
            path.write_text("keep me")
            self.assertEqual(3, self.run_scaffold(directory, "demo").returncode)
            self.assertEqual("keep me", path.read_text())

    def test_yaml_scalar_names_remain_strings(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("123", "true", "null", "on"):
                self.assertEqual(0, self.run_scaffold(directory, name).returncode)
                with redirect_stdout(io.StringIO()):
                    result = checker.main([str(Path(directory) / name)])
                self.assertEqual(0, result, name)


if __name__ == "__main__":
    unittest.main()
