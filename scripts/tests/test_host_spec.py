import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from obs import host_spec

SESSION = "11111111-2222-3333-4444-555555555555"


def event(**fields):
    return json.dumps(fields, ensure_ascii=False)


class HostSpecTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        self.project = self.home / "work" / "demo-project"
        self.segment = self.home / "logs/sessions/D--demo-project" / SESSION / "segments"
        self.segment.mkdir(parents=True)
        self.spec = host_spec.load("qoder")

    def write_events(self, lines):
        (self.segment / "a.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_discovery_takes_the_session_key_from_the_path(self):
        self.write_events([event(ts="2026-10-15T10:00:00.000+08:00", seq=1, type="tool.requested",
                                 data={"tool_name": "Bash", "args": {"command": "ls"}})])
        found = host_spec.discover(self.spec, self.home, "D--demo-project")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][0], SESSION)

    def test_capability_is_granted_only_on_observed_fields(self):
        self.write_events([
            event(ts="2026-10-15T10:00:00.000+08:00", seq=1, type="tool.requested",
                  data={"tool_name": "Write", "args": {"file_path": str(self.project / ".spec/设计稿/p1.html")}}),
            event(ts="2026-10-15T10:00:01.000+08:00", seq=2, type="loop.iteration.finished",
                  data={"tool_use_count": 1, "error_tool_result_count": 0}),
            event(ts="2026-10-15T10:00:02.000+08:00", seq=3, type="loop.iteration.finished", data={"tool_use_count": 1}),
        ])
        report = host_spec.verify_capabilities(self.spec, host_spec.read_spans(self.spec, host_spec.discover(self.spec, self.home, "")))
        self.assertTrue(report["TOOL_EVENTS"]["granted"])
        self.assertTrue(report["ARTIFACT_WRITES"]["granted"])
        self.assertIn("1/2", report["TOOL_ERRORS"]["reason"])
        self.assertFalse(report["TOKENS"]["granted"])
        self.assertIn("token", report["TOKENS"]["reason"])

    def test_missing_count_field_degrades_instead_of_reporting_zero(self):
        self.write_events([event(ts="2026-10-15T10:00:00.000+08:00", seq=1, type="tool.requested",
                                 data={"tool_name": "Bash", "args": {}})])
        report = host_spec.verify_capabilities(self.spec, host_spec.read_spans(self.spec, host_spec.discover(self.spec, self.home, "")))
        self.assertFalse(report["TOOL_ERRORS"]["granted"])
        self.assertTrue(report["TOOL_EVENTS"]["granted"])

    def test_writes_are_attributed_by_artifact_location(self):
        self.write_events([
            event(ts="2026-10-15T10:00:00.000+08:00", seq=1, type="tool.requested",
                  data={"tool_name": "Write", "args": {"file_path": str(self.project / ".spec/设计稿/p1.html")}}),
            event(ts="2026-10-15T10:00:01.000+08:00", seq=2, type="tool.requested",
                  data={"tool_name": "Edit", "args": {"file_path": str(self.project / ".spec/TDD/overview.md")}}),
            event(ts="2026-10-15T10:00:02.000+08:00", seq=3, type="tool.requested",
                  data={"tool_name": "Write", "args": {"file_path": str(self.home / "elsewhere.md")}}),
        ])
        spans = host_spec.read_spans(self.spec, host_spec.discover(self.spec, self.home, ""))
        result = host_spec.attribute(spans, self.project)
        # 路径归属指向"产物由谁产出"的节点：设计稿归 ui-ux-design，设计评审才归 ui-ux-review
        self.assertEqual(result["byNode"], {"ui-ux-design": 1, "backend-tech-design": 1})
        self.assertEqual(result["unattributed"], 1)

    def test_unknown_host_is_named_with_the_available_options(self):
        with self.assertRaises(ValueError) as caught:
            host_spec.load("nosuchhost")
        self.assertIn("qoder", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
