import contextlib
import hashlib
import io
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


class ArtifactBindingTests(unittest.TestCase):
    """Only the newest node-end binding per artifact path promises anything about today.

    Same 口径 as validate_core.check_digests / subject_bindings: a recorded sha256 is
    "the bytes this node saw when it closed". Once a later node re-binds the path, the older
    snapshot stops matching by definition — that is history, not tampering, so it must not
    join errors (callers grade red/green by len(errors)); it is emitted as an explanation.
    """

    PATH = ".spec/prd/overview.md"

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def base(self, execution):
        return ["--project-root", str(self.root), "--execution-id", execution,
                "--node", "quality-inspection", "--skill", "quality-inspection"]

    def write_body(self, body, path=None):
        target = self.root / (path or self.PATH)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        return body

    def close(self, execution, path, body):
        """Open + close one node through the CLI, letting the tool hash `body` as written."""
        self.write_body(body, path)
        self.assertEqual(0, tsr.main(self.base(execution) + ["node-start"]))
        self.assertEqual(0, tsr.main(self.base(execution) + ["node-end", "--gate", "PASS",
                                                            "--allow-downstream", "true",
                                                            "--artifact", path]))

    def raw_event(self, name, execution, ts, bindings=(), seq=None):
        artifacts = [{"path": path, "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}
                     for path, body in bindings]
        event = {"schema": schema.SCHEMA, "event": name, "project": "probe", "executionId": execution,
                 "node": "quality-inspection", "skill": "quality-inspection", "role": "produce",
                 "actor": "main", "origin": "self", "reqRefs": [], "artifacts": artifacts, "upstream": [],
                 "gate": "PASS", "allowDownstream": False, "ts": ts}
        if seq is not None:
            event["seq"] = seq
        return event

    def append(self, name, execution, ts, bindings=()):
        """Append via the ledger contract so seq stays the machine-assigned write order."""
        schema.append_event(self.root, self.raw_event(name, execution, ts, bindings))

    def binding_errors(self, root):
        return [e for e in tsr.verify(root) if "edited after node-end" in e or "vanished" in e]

    def test_superseded_snapshot_is_explained_not_reported(self):
        """①最新绑定一致 + 有一条被超越的旧快照 ⇒ 不判红（P3 关闭后 P4 续改并重新落账）。"""
        self.close("EXEC-P3", self.PATH, b"# v1 reviewed in P3\n")
        self.assertEqual([], tsr.verify(self.root))
        self.close("EXEC-P4", self.PATH, b"# v2 edited later, re-signed in P4\n")
        notes = []
        errors = tsr.verify(self.root, notes)
        self.assertEqual([], errors)
        self.assertEqual(1, len(notes), notes)
        self.assertIn("1 条更早绑定已被后续节点超越", notes[0])
        self.assertIn("run.jsonl#2", notes[0])

    def test_newest_binding_mismatch_is_red_even_when_an_older_one_matches(self):
        """①的反向对照：只有最新那条对不上才判红，且必须指向最新那条事件。"""
        self.close("EXEC-P3", self.PATH, b"# v1\n")
        self.close("EXEC-P4", self.PATH, b"# v2\n")
        self.write_body(b"# v3 edited behind the ledger\n")
        drift = [e for e in tsr.verify(self.root) if "edited after node-end" in e]
        self.assertEqual(1, len(drift), drift)
        self.assertIn("run.jsonl#4", drift[0])
        self.assertNotIn("#2:", drift[0])

    def test_body_edited_with_no_later_binding_of_that_path_is_red(self):
        """④检出力未削弱：后续节点没绑定这个路径就不能替它作保（本仓 P3/P4 的真实形态）。"""
        self.close("EXEC-P3", self.PATH, b"# v1\n")
        self.write_body(b"# v1 reworded, never re-signed\n")
        self.close("EXEC-P4", "governance/other.yaml", b"version: 1\n")
        notes = []
        errors = tsr.verify(self.root, notes)
        self.assertEqual(1, len([e for e in errors if "edited after node-end" in e]), errors)
        self.assertEqual([], notes, notes)

    def test_deleted_artifact_behind_the_newest_binding_is_still_red(self):
        self.close("EXEC-P3", self.PATH, b"# v1\n")
        (self.root / self.PATH).unlink()
        self.assertTrue(any("artifact vanished" in e for e in tsr.verify(self.root)))

    def test_mixed_timestamp_styles_pick_the_real_newest(self):
        """③'2026-10-12 09:34' 与 '2026-10-12T09:33' 混排：空格排在 T 前，字符串排序选错最新。"""
        current = self.write_body(b"# current bytes signed at 09:34\n")
        self.append("node-start", "EXEC-A", "2026-10-12T09:30:00+08:00")
        self.append("node-end", "EXEC-A", "2026-10-12T09:33:00+08:00", [(self.PATH, b"# older\n")])
        self.append("node-start", "EXEC-B", "2026-10-12 09:34:00+08:00")
        self.append("node-end", "EXEC-B", "2026-10-12 09:34:00+08:00", [(self.PATH, current)])
        self.assertEqual([], self.binding_errors(self.root))
        notes = []
        tsr.verify(self.root, notes)
        self.assertIn("1 条更早绑定已被后续节点超越", notes[0])
        self.assertIn("run.jsonl#2", notes[0])

    def test_mixed_timestamp_styles_reverse_control_newest_is_the_one_that_fails(self):
        """③的反向对照：正文与 09:34 那条不一致时，判红的必须是 09:34（seq 4），不是 09:33。"""
        self.write_body(b"# edited after the 09:34 node-end\n")
        self.append("node-start", "EXEC-A", "2026-10-12T09:30:00+08:00")
        self.append("node-end", "EXEC-A", "2026-10-12T09:33:00+08:00", [(self.PATH, b"# older\n")])
        self.append("node-start", "EXEC-B", "2026-10-12 09:34:00+08:00")
        self.append("node-end", "EXEC-B", "2026-10-12 09:34:00+08:00", [(self.PATH, b"# signed\n")])
        drift = [e for e in tsr.verify(self.root) if "edited after node-end" in e]
        self.assertEqual(1, len(drift), drift)
        self.assertIn("run.jsonl#4", drift[0])

    def test_tie_on_seq_is_broken_by_normalised_time_not_string_order(self):
        """手改台账里 seq 重复时，取最新仍按数字化的时间排，而不是字符串比大小。"""
        current = self.write_body(b"# newest at 09:34\n")
        stale = b"# older at 09:33\n"
        events = [
            self.raw_event("node-start", "EXEC-A", "2026-10-12T09:30:00+08:00", seq=1),
            self.raw_event("node-end", "EXEC-A", "2026-10-12 09:34:00+08:00", [(self.PATH, current)], seq=2),
            self.raw_event("node-start", "EXEC-B", "2026-10-12T09:31:00+08:00", seq=3),
            self.raw_event("node-end", "EXEC-B", "2026-10-12T09:33:00+08:00", [(self.PATH, stale)], seq=2),
        ]
        log = self.root / schema.RUN_LOG
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events), encoding="utf-8")
        self.assertEqual([], self.binding_errors(self.root))
        self.write_body(b"# nobody signed this\n")
        self.assertEqual(1, len([e for e in tsr.verify(self.root) if "edited after node-end" in e]))

    def test_superseded_note_is_printed_and_never_counts_as_an_error(self):
        """说明性输出走 stdout：绿不绿只看 len(errors)，旧快照不得把它染红。"""
        self.close("EXEC-P3", self.PATH, b"# v1\n")
        self.close("EXEC-P4", self.PATH, b"# v2\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = tsr.main(self.base("EXEC-P4") + ["verify"])
        self.assertEqual(0, code)
        self.assertEqual([], tsr.verify(self.root))
        text = out.getvalue()
        self.assertIn("run-log verification passed", text)
        self.assertIn("条更早绑定已被后续节点超越", text)


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
