"""Portable regression tests; may run after copying this Skill out of its source repo."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("portable_bundle_checker", BUNDLE / "scripts/check_bundle.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class PortableBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.bundle = self.work / "skill-lifecycle"
        shutil.copytree(BUNDLE, self.bundle, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    def add(self, name, text):
        p = self.bundle / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def check_bad(self, message):
        result = checker.check(self.bundle)
        self.assertFalse(result["ok"], result)
        self.assertTrue(any(message in e for e in result["errors"]), result)

    def test_copied_package_runs_offline_without_site_packages_or_source_repo(self):
        before = hashes(self.bundle)
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-B", "-X", "utf8", str(self.bundle / "scripts/check_bundle.py"), str(self.bundle)],
            cwd=self.work, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
        self.assertTrue(json.loads(result.stdout.decode("utf-8"))["ok"])
        self.assertEqual(hashes(self.bundle), before)
        self.assertEqual(set(self.work.iterdir()), {self.bundle})

    def test_missing_referenced_template_fails(self):
        (self.bundle / "assets/issue-template.md").unlink()
        self.check_bad("Missing linked resource")

    def test_reference_can_use_parent_inside_bundle(self):
        self.add("references/extra.md", "[Template](../assets/issue-template.md)\n")
        self.assertTrue(checker.check(self.bundle)["ok"])

    def test_escape_to_existing_external_file_fails(self):
        external = self.work / "private.md"
        external.write_text("private", encoding="utf-8")
        for link in ("../private.md", "%2e%2e/private.md"):
            with self.subTest(link=link):
                self.add("escape.md", f"[Private]({link})\n")
                self.check_bad("Link escapes bundle")
        self.assertEqual(external.read_text(encoding="utf-8"), "private")

    def test_absolute_local_links_fail(self):
        for link in ("C:/private/secret.md", "/private/secret.md", "file:///private/secret.md", "//host/share/a.md"):
            with self.subTest(link=link):
                self.add("absolute.md", f"[Bad]({link})\n")
                self.check_bad("Absolute/external file link")

    def test_redirected_directory_is_not_traversed(self):
        external = self.work / "external"
        external.mkdir()
        (external / "secret.md").write_bytes(b"secret")
        try:
            (self.bundle / "outside").symlink_to(external, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"Symlink creation unavailable: {exc}")
        self.check_bad("Redirected directory")
        self.assertEqual(list(external.iterdir()), [external / "secret.md"])

    def test_metadata_missing_duplicate_and_name_mismatch_fail(self):
        original = (self.bundle / "SKILL.md").read_text(encoding="utf-8")
        cases = [original.replace("name: skill-lifecycle", "name: other"),
                 original.replace("name: skill-lifecycle", "name: skill-lifecycle\nname: other"),
                 original.replace("name: skill-lifecycle\n", ""), "# No metadata\n"]
        for text in cases:
            with self.subTest(text=text[:90]):
                self.add("SKILL.md", text)
                self.assertFalse(checker.check(self.bundle)["ok"])

    def test_unfilled_entry_template_is_not_a_finished_skill(self):
        text = (self.bundle / "SKILL.md").read_text(encoding="utf-8")
        self.add("SKILL.md", text + "\n{{unfilled}}\n")
        self.check_bad("unfilled template")

    def test_python_is_compiled_but_not_executed(self):
        sentinel = self.work / "must-not-exist"
        self.add("scripts/no-execution.py", f"from pathlib import Path\nPath({str(sentinel)!r}).touch()\n")
        before = hashes(self.bundle)
        self.assertTrue(checker.check(self.bundle)["ok"])
        self.assertFalse(sentinel.exists())
        self.assertEqual(hashes(self.bundle), before)

    def test_bad_python_syntax_fails(self):
        self.add("scripts/invalid.py", "def invalid(:\n")
        self.check_bad("Python syntax error")

    def test_invalid_utf8_fails(self):
        (self.bundle / "invalid.md").write_bytes(b"\xff\xfe")
        self.check_bad("Cannot read UTF-8")

    def test_completed_target_template_stands_alone_without_maintainer(self):
        target = self.work / "meeting-notes"
        target.mkdir()
        text = (self.bundle / "assets/skill-template.md").read_text(encoding="utf-8")
        import re
        text = text.replace("{{skill-name}}", "meeting-notes")
        text = re.sub(r"\{\{.*?\}\}", "Meeting notes with explicit decisions only.", text)
        (target / "SKILL.md").write_text(text, encoding="utf-8")
        # Structural smoke only: not an actual model execution or acceptance trial.
        result = checker.check(target)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["files"], 1)


if __name__ == "__main__":
    unittest.main()
