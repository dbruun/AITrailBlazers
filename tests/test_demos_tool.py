import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import demos  # noqa: E402


class DemosToolTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        shutil.copytree(REPO_ROOT / "templates", self.root / "templates")
        (self.root / "demos").mkdir()
        shutil.copy(REPO_ROOT / "demos" / "README.md", self.root / "demos" / "README.md")
        demos.update_catalog(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = demos.main(["--root", str(self.root)] + list(argv))
        return code, out.getvalue()

    def test_new_demo_from_template_is_valid(self):
        code, _ = self.run_cli("new", "my-demo", "--title", "My Demo")
        self.assertEqual(code, 0)
        demo = self.root / "demos" / "my-demo"
        self.assertEqual(demos.validate_demo(demo), [])
        meta = json.loads((demo / "demo.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["id"], "my-demo")
        self.assertEqual(meta["title"], "My Demo")
        self.assertIn("My Demo", (demo / "walkthrough" / "index.html").read_text(encoding="utf-8"))
        self.assertIn("[My Demo](my-demo/)", (self.root / "demos" / "README.md").read_text(encoding="utf-8"))
        code, out = self.run_cli("validate")
        self.assertEqual(code, 0, out)

    def test_new_rejects_bad_id_unsafe_title_and_duplicates(self):
        self.assertEqual(self.run_cli("new", "Bad_Name")[0], 1)
        self.assertEqual(self.run_cli("new", "ok-id", "--title", 'Bad "title"')[0], 1)
        self.assertFalse((self.root / "demos" / "ok-id").exists())
        self.assertEqual(self.run_cli("new", "dup")[0], 0)
        self.assertEqual(self.run_cli("new", "dup")[0], 1)

    def test_validate_reports_missing_files_and_bad_metadata(self):
        self.run_cli("new", "broken")
        demo = self.root / "demos" / "broken"
        (demo / "docs" / "EXTENDING.md").unlink()
        meta = json.loads((demo / "demo.json").read_text(encoding="utf-8"))
        meta.update({"id": "other", "status": "unknown", "owners": []})
        meta["deploy"]["guide"] = "../../outside.md"
        (demo / "demo.json").write_text(json.dumps(meta), encoding="utf-8")

        errors = "\n".join(demos.validate_demo(demo))
        self.assertIn("missing required file: docs/EXTENDING.md", errors)
        self.assertIn("must match the folder name", errors)
        self.assertIn("'status' must be one of", errors)
        self.assertIn("'owners' must be a non-empty list", errors)
        self.assertIn("'deploy.guide' file not found", errors)
        self.assertEqual(self.run_cli("validate")[0], 1)

    def test_validate_flags_unreplaced_placeholders(self):
        self.run_cli("new", "placeholder")
        readme = self.root / "demos" / "placeholder" / "README.md"
        readme.write_text("# {{DEMO_TITLE}}\n", encoding="utf-8")
        self.assertIn(
            "unreplaced template placeholder in README.md",
            demos.validate_demo(readme.parent),
        )

    def test_catalog_check_detects_stale_catalog(self):
        self.run_cli("new", "fresh")
        self.assertEqual(self.run_cli("catalog", "--check")[0], 0)
        meta_path = self.root / "demos" / "fresh" / "demo.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["summary"] = "Changed | with pipe"
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
        self.assertEqual(self.run_cli("catalog", "--check")[0], 1)
        self.assertEqual(self.run_cli("catalog")[0], 0)
        self.assertIn("Changed \\| with pipe", (self.root / "demos" / "README.md").read_text(encoding="utf-8"))

    def test_repository_demos_are_valid(self):
        for demo in demos.list_demo_dirs(REPO_ROOT):
            with self.subTest(demo=demo.name):
                self.assertEqual(demos.validate_demo(demo), [])
        self.assertTrue(demos.update_catalog(REPO_ROOT, check=True))


if __name__ == "__main__":
    unittest.main()
