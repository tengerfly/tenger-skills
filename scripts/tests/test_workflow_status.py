"""Executable status-view tests and active routing invariants, not Agent behavior tests."""
import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import workflow_status as status
import validate_core as core

ROOT = Path(__file__).resolve().parents[2]


class WorkflowStatusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.file = self.root / ".spec/workflow.yaml"
        self.file.parent.mkdir()
        self.data = {
            "workflowId": "WF-1", "projectId": "synthetic", "executionId": "EXEC-1",
            "lifecycle": "CHANGE", "state": "WORKFLOW_BLOCKED", "currentSkill": "feature-decision",
            "gate": "BLOCKED", "allowDownstream": False, "revision": "r1",
            "artifactRefs": ["ART-1"], "evidenceRefs": [], "decisionRefs": [],
            "nextAction": "等待用户确认范围 r1", "requiredInput": "MVP 选择",
        }

    def save(self, data=None):
        self.file.write_text(yaml.safe_dump(self.data if data is None else data, allow_unicode=True), encoding="utf-8")

    def test_json_reports_exact_persisted_block_without_writing(self):
        self.save()
        before = self.file.read_bytes()
        out = io.StringIO()
        with redirect_stdout(out):
            result = status.main(["--project-root", str(self.root), "--json"])
        self.assertEqual(result, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(data["state"], "WORKFLOW_BLOCKED")
        self.assertEqual(data["currentSkill"], "feature-decision")
        self.assertEqual(data["nextAction"], self.data["nextAction"])
        self.assertFalse(data["allowDownstream"])
        self.assertFalse(data["stateChanged"])
        self.assertEqual(before, self.file.read_bytes())
        self.assertEqual(list(self.file.parent.iterdir()), [self.file])

    def test_text_includes_pending_decision_and_next_action(self):
        self.save()
        text = status.render(status.snapshot(self.root))
        self.assertIn(self.data["requiredInput"], text)
        self.assertIn(self.data["nextAction"], text)
        self.assertIn("未记录", text)

    def test_no_formal_file_does_not_create_one_or_invent_state(self):
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(status.main(["--project-root", str(self.root)]), 2)
        self.assertIn("轻量任务", err.getvalue())
        self.assertFalse(self.file.exists())

    def test_invalid_or_conflicting_records_fail_closed(self):
        cases = [[], {**self.data, "allowDownstream": True},
                 {**self.data, "gate": "SUCCESS"}, {**self.data, "lifecycle": "MIGRATE"},
                 {**self.data, "artifactRefs": "ART-1"}, {**self.data, "allowDownstream": "false"}]
        for field in status.TEXT_FIELDS:
            data = copy.deepcopy(self.data)
            del data[field]
            cases.append(data)
        for data in cases:
            with self.subTest(data=data):
                self.save(data)
                with self.assertRaises(ValueError):
                    status.snapshot(self.root)

    def test_cli_emits_utf8_under_non_utf8_environment(self):
        self.save()
        env = dict(os.environ, PYTHONIOENCODING="ascii")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/workflow_status.py"), "--project-root", str(self.root), "--json"],
            capture_output=True, env=env, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout.decode("utf-8"))["nextAction"], self.data["nextAction"])

    def test_duplicate_or_malformed_yaml_is_rejected(self):
        for text in ("state: A\nstate: B\n", "state: ["):
            self.file.write_text(text, encoding="utf-8")
            with self.assertRaises(ValueError):
                status.snapshot(self.root)


class WorkflowRoutingTests(unittest.TestCase):
    def test_only_auto_test_is_discoverable_and_routed_for_testing(self):
        skills, workflows, states = core.read_three(ROOT)
        active = {s["id"]: s for s in skills["skills"] if s["status"] == "active"}
        self.assertNotIn("testing", active)
        discovered = {core.frontmatter(p)[0] for p in core.skill_files(ROOT)}
        self.assertNotIn("testing", discovered)
        self.assertIn("auto-test", discovered)
        self.assertTrue({"testing", "Testing"}.issubset(active["auto-test"]["legacyAliases"]))
        testing = next(w for w in workflows["workflows"] if w["id"] == "testing-workflow")
        self.assertEqual(testing["skills"], ["auto-test"])
        for transition in states["transitions"]:
            self.assertNotEqual(transition["actor"], "testing")
            if transition["to"] == "TEST_PASSED":
                self.assertEqual(transition["actor"], "auto-test")
        self.assertTrue((ROOT / "Test/Testing/ARCHIVED.md").is_file())


if __name__ == "__main__":
    unittest.main()
