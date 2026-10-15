import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tsr
from obs import schema

BASE = ["--project-root", "", "--execution-id", "EXEC-1", "--node", "prd-design", "--skill", "prd-design"]
def args(*extra):
    return ["--execution-id", "EXEC-1", "--node", "prd-design", "--skill", "prd-design", "--role", "produce", *extra]


class RunLogTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        tsr.main(["--project-root", str(self.root), *args(), "node-start"])

    def finish(self, gate="PASS", allow="true", upstream=None, artifacts=(".spec/prd/overview.md",)):
        extra = []
        for path in artifacts:
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.is_file():
                target.write_bytes(b"# approved baseline\n")
            extra += ["--artifact", path]
        for ref in upstream or []:
            extra += ["--upstream", ref]
        code = tsr.main(["--project-root", str(self.root), *args(), "node-end",
                         "--gate", gate, "--allow-downstream", allow, *extra])
        self.assertEqual(code, 0)

    def test_bound_artifact_verifies_clean(self):
        self.finish()
        self.assertEqual(tsr.main(["--project-root", str(self.root), *args(), "verify"]), 0)

    def test_body_edited_after_node_end_is_detected(self):
        self.finish()
        (self.root / ".spec/prd/overview.md").write_bytes(b"# approved baseline\n# drifted quietly\n")
        errors = tsr.verify(self.root)
        self.assertTrue(any("edited after node-end" in e for e in errors), errors)

    def test_pass_downstream_over_closed_upstream_is_refused(self):
        self.finish(gate="PASS", allow="true", upstream=["PRD-V3:BLOCKED"])
        errors = tsr.verify(self.root)
        self.assertTrue(any("upstream is closed" in e for e in errors), errors)

    def test_review_without_round_is_rejected_at_write_time(self):
        code = tsr.main(["--project-root", str(self.root), "--execution-id", "EXEC-1",
                         "--node", "prd-review", "--skill", "prd-review", "--role", "review", "node-end",
                         "--gate", "PASS", "--allow-downstream", "true"])
        self.assertEqual(code, 1)

    def test_round_and_batch_are_recorded_for_rework_rate(self):
        code = tsr.main(["--project-root", str(self.root), "--execution-id", "EXEC-1",
                         "--node", "prd-review", "--skill", "prd-review", "--role", "review",
                         "--round", "2", "--batch", "3", "node-end",
                         "--gate", "CONDITIONAL", "--allow-downstream", "false"])
        self.assertEqual(code, 0)
        last = schema.read_events(self.root)[-1]
        self.assertEqual((last["round"], last["batch"], last["gate"]), (2, 3, "CONDITIONAL"))

    def test_subagent_without_parent_is_rejected(self):
        code = tsr.main(["--project-root", str(self.root), "--execution-id", "SUB-1",
                         "--node", "prd-design", "--skill", "prd-design", "--actor", "subagent", "node-start"])
        self.assertEqual(code, 1)

    def test_caller_cannot_author_timestamp_or_sequence(self):
        self.finish()
        events = schema.read_events(self.root)
        self.assertEqual([e["seq"] for e in events], list(range(1, len(events) + 1)))
        for event in events:
            self.assertRegex(event["ts"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{2}:?\d{2}$")

    def test_node_end_without_start_is_flagged(self):
        self.finish()
        code = tsr.main(["--project-root", str(self.root), "--execution-id", "EXEC-7",
                         "--node", "never-started", "--skill", "prd-design", "node-end",
                         "--gate", "PASS", "--allow-downstream", "true"])
        self.assertEqual(code, 0)
        errors = tsr.verify(self.root)
        self.assertTrue(any("node-end without matching node-start" in e for e in errors), errors)

    def test_run_log_is_plain_json_readable_by_any_host(self):
        self.finish()
        lines = (self.root / schema.RUN_LOG).read_text(encoding="utf-8").splitlines()
        self.assertTrue(all(json.loads(line)["schema"] == schema.SCHEMA for line in lines))


if __name__ == "__main__":
    unittest.main()
