import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tsr
from obs import anomaly, gitlog, schema


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


class GitTrackTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / ".spec/prd").mkdir(parents=True)
        self.doc = self.root / ".spec/prd/overview.md"
        self.doc.write_text("# committed\n", encoding="utf-8")
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "probe@example.invalid")
        git(self.root, "config", "user.name", "probe")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "chore: fixture")

    def age(self, hours):
        stamp = time.time() - hours * 3600
        os.utime(self.doc, (stamp, stamp))

    def test_aged_uncommitted_work_is_found(self):
        self.doc.write_text("# committed\n# three days of finished edits, never committed\n", encoding="utf-8")
        self.age(72)
        findings = gitlog.find_gaps(self.root, {}, max_age_hours=4.0)
        self.assertEqual([f["kind"] for f in findings], ["改动未提交"])
        self.assertIn(".spec/prd/overview.md", findings[0]["evidence"])
        self.assertIn("不自动提交", findings[0]["boundary"])

    def test_fresh_edits_are_not_reported_as_stalled(self):
        self.doc.write_text("# mid-flight\n", encoding="utf-8")
        self.assertEqual(gitlog.find_gaps(self.root, {}, max_age_hours=4.0), [])

    def test_committed_clean_tree_produces_no_findings(self):
        self.assertEqual(gitlog.find_gaps(self.root, {}, max_age_hours=4.0), [])

    def test_node_started_but_never_closed_is_reported(self):
        unclosed = {("EXEC-1", "prd-design"): "2026-10-15T09:00:00+08:00"}
        findings = gitlog.find_gaps(self.root, unclosed, max_age_hours=4.0)
        self.assertEqual(findings[0]["kind"], "节点未收口")

    def test_commit_window_counts_landed_work(self):
        window = gitlog.commit_window(self.root, "2000-01-01")
        self.assertEqual(window["count"], 1)
        self.assertEqual(window["files"], 1)
        self.assertEqual(window["added"], 1)

    def test_far_future_until_is_refused_rather_than_reporting_zero(self):
        # this platform returns no commits for --until=2100-01-01; an open window must omit it
        self.assertEqual(gitlog.commit_window(self.root, "2000-01-01", until="2100-01-01")["count"], 0)


class AnomalyCardTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def test_same_evidence_updates_one_card_not_two(self):
        finding = {"kind": "改动未提交", "detail": "3 个文件停留工作树", "evidence": ".spec/a.md",
                   "node": None, "execution": None}
        first = anomaly.upsert(self.root, [finding])
        second = anomaly.upsert(self.root, [finding])
        self.assertEqual(len(first["created"]), 1)
        self.assertEqual(second["created"], [])
        self.assertEqual(second["unchanged"], [anomaly.finding_id(finding)])
        index = (self.root / anomaly.INDEX).read_text(encoding="utf-8")
        self.assertEqual(index.count(anomaly.finding_id(finding)), 1)

    def test_card_carries_reproducible_pointers_not_narrative(self):
        finding = {"kind": "节点未收口", "detail": "node-start 后无 node-end", "evidence": "EXEC-1/prd-design",
                   "node": "prd-design", "execution": "EXEC-1"}
        anomaly.upsert(self.root, [finding])
        card = next((self.root / anomaly.DETAIL_DIR).glob("*.md")).read_text(encoding="utf-8")
        for field in ("问题 ID", "证据", "影响与严重度", "责任方/下一动作/修复判据", "反哺"):
            self.assertIn(field, card)
        self.assertIn("EXEC-1/prd-design", card)
        self.assertIn("待确认", card)


if __name__ == "__main__":
    unittest.main()
