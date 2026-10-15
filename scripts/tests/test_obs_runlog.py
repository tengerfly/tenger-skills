import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tsr
from obs import metrics as tsr_metrics
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


class MetricsTests(unittest.TestCase):
    """Synthetic run logs only — real numbers must come from real node executions."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def record(self, node, skill, role="produce", gate="PASS", artifacts=None, round_=None, upstream=None):
        common = ["--project-root", str(self.root), "--execution-id", "EXEC-1", "--node", node, "--skill", skill, "--role", role]
        if round_ is not None:
            common += ["--round", str(round_), "--batch", "1"]
        self.assertEqual(tsr.main(common + ["node-start"]), 0)
        extra = []
        for path in artifacts or []:
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"payload\n")
            extra += ["--artifact", path]
        for ref in upstream or []:
            extra += ["--upstream", ref]
        self.assertEqual(tsr.main(common + ["node-end", "--gate", gate, "--allow-downstream",
                                            "true" if gate == "PASS" else "false", *extra]), 0)

    def test_per_node_totals_come_from_bound_artifacts(self):
        self.record("prd-design", "prd-design", artifacts=[".spec/prd/overview.md", ".spec/prd/M01.md"])
        report = tsr_metrics.summarize(schema.read_events(self.root))
        node = report["nodes"]["prd-design"]
        self.assertEqual((node["artifacts"], node["ends"], node["starts"]), (2, 1, 1))
        self.assertEqual(node["bytes"], 16)
        self.assertGreaterEqual(node["elapsed"], 0)

    def test_rework_rate_counts_review_rounds_above_one(self):
        self.record("prd-review", "prd-review", role="review", round_=1)
        self.record("prd-review", "prd-review", role="review", round_=2)
        report = tsr_metrics.summarize(schema.read_events(self.root))
        self.assertEqual(report["review_rounds"], 2)
        self.assertEqual(report["rework_rate"], 0.5)
        self.assertEqual(report["nodes"]["prd-review"]["max_round"], 2)

    def test_blocked_handoff_is_counted_and_open_node_is_visible(self):
        self.record("tech-review", "tech-review", role="review", round_=1, gate="BLOCKED")
        report = tsr_metrics.summarize(schema.read_events(self.root))
        self.assertEqual(report["blocked_ends"], 1)
        self.assertEqual(report["open_nodes"], [])

    def test_unregistered_node_fails_verification_and_report(self):
        self.record("made-up-node", "made-up-node")
        errors = tsr.verify(self.root)
        self.assertTrue(any("not registered" in e for e in errors), errors)
        self.assertEqual(tsr.main(["--project-root", str(self.root), "--execution-id", "EXEC-1",
                                   "--node", "prd-design", "--skill", "prd-design", "report"]), 1)

    def test_dashboard_states_what_cannot_be_measured(self):
        self.record("prd-design", "prd-design", artifacts=[".spec/prd/overview.md"])
        self.assertEqual(tsr.main(["--project-root", str(self.root), "--execution-id", "EXEC-1",
                                   "--node", "prd-design", "--skill", "prd-design", "report"]), 0)
        board = (self.root / ".spec/观测/看板.md").read_text(encoding="utf-8")
        self.assertIn("N/A", board)
        self.assertIn("prd-design", board)


if __name__ == "__main__":
    unittest.main()
