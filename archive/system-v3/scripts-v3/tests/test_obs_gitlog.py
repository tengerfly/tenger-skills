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


class DeliveryTests(unittest.TestCase):
    """交付这一面：本地领先上游就报「交付未推送」；没声明 delivery 的仓库是不适用，不是已通过。"""

    POL = {"rule": "本地提交都要推到上游", "kind": "交付未推送·测试文案",
           "aheadDetail": "{count} 个提交停在本地、未推到上游 {upstream}",
           "notApplicable": "没有上游跟踪分支 ⇒ 交付核对不适用·测试文案",
           "unreadable": "上游或领先数读不动 ⇒ 交付未核·测试文案",
           "boundary": "只报事实：不代推"}

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "repo"
        self.root.mkdir()
        remote = Path(tmp.name) / "remote.git"
        remote.mkdir()                      # git -C 不会替我建目录；不建则裸仓 init 静默失败、上游就配不上
        git(remote, "init", "-q", "--bare")
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "config", "user.email", "probe@example.invalid")
        git(self.root, "config", "user.name", "probe")
        (self.root / "a.md").write_text("# a\n", encoding="utf-8")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "chore: first")
        git(self.root, "remote", "add", "origin", str(remote))
        git(self.root, "push", "-q", "-u", "origin", "main")

    def declare(self, section=None):
        path = self.root / "governance"
        path.mkdir(parents=True, exist_ok=True)
        import yaml
        body = {"version": 1}
        if section is not None:
            body["delivery"] = section
        (path / "obs-registry.yaml").write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")

    def commit_locally(self, count=1):
        for index in range(count):
            (self.root / f"n{index}.md").write_text(f"# {index}\n", encoding="utf-8")
            git(self.root, "add", ".")
            git(self.root, "commit", "-qm", f"chore: local {index}")

    def test_ahead_commits_are_reported(self):
        self.declare(self.POL)
        self.commit_locally(2)
        findings = [f for f in gitlog.find_gaps(self.root, {}, max_age_hours=4.0)
                    if f.get("cardKind") == "unpushed"]
        self.assertEqual(len(findings), 1, findings)
        self.assertEqual(findings[0]["kind"], "交付未推送·测试文案")
        self.assertIn("2 个提交停在本地", findings[0]["detail"])
        self.assertIn("origin/main", findings[0]["detail"] + findings[0]["evidence"])

    def test_pushed_branch_produces_no_finding(self):
        # 反向对照：同一份判据，推完就该没卡——证明红来自领先数，不是这面天生报红
        self.declare(self.POL)
        self.commit_locally(1)
        git(self.root, "push", "-q", "origin", "main")
        self.assertEqual([f for f in gitlog.find_gaps(self.root, {}, max_age_hours=4.0)
                          if f.get("cardKind") == "unpushed"], [])

    def test_repo_without_declaration_is_not_applicable(self):
        self.declare(None)
        self.commit_locally(1)
        self.assertIsNone(gitlog.delivery_policy(self.root))
        self.assertEqual([f for f in gitlog.find_gaps(self.root, {}, max_age_hours=4.0)
                          if f.get("cardKind") == "unpushed"], [],
                         "没声明 delivery 的仓库不能拿本仓的交付纪律去判红")

    def test_no_upstream_is_spelled_out_as_not_applicable(self):
        self.declare(self.POL)
        orphan = self.root.parent / "orphan"
        orphan.mkdir()
        git(orphan, "init", "-q", "-b", "main")
        git(orphan, "config", "user.email", "probe@example.invalid")
        git(orphan, "config", "user.name", "probe")
        (orphan / "governance").mkdir()
        import yaml
        (orphan / "governance/obs-registry.yaml").write_text(
            yaml.safe_dump({"delivery": self.POL}, allow_unicode=True), encoding="utf-8")
        (orphan / "x.md").write_text("# x\n", encoding="utf-8")
        git(orphan, "add", ".")
        git(orphan, "commit", "-qm", "chore: only local")
        status = gitlog.delivery_status(orphan, self.POL)
        self.assertFalse(status["applicable"])
        self.assertEqual(status["reason"], "没有上游跟踪分支 ⇒ 交付核对不适用·测试文案")

    def test_incomplete_section_refuses_default_texts(self):
        import yaml
        broken = dict(self.POL)
        broken.pop("aheadDetail")
        self.declare(broken)
        path = self.root / "governance/obs-registry.yaml"
        (self.root / "governance").mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump({"delivery": broken}, allow_unicode=True), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            gitlog.delivery_policy(self.root)
        self.assertIn("delivery 缺必需判据键", str(caught.exception))
        self.assertIn("aheadDetail", str(caught.exception))

    def test_unpushed_finding_gets_its_own_card_not_the_uncommitted_kind(self):
        # 错标会把「没推送」混进「改动未提交」：同一事实两类卡 ⇒ 台账分家
        from obs import candidates
        self.declare(self.POL)
        self.commit_locally(1)
        findings = gitlog.find_gaps(self.root, {}, max_age_hours=4.0)
        pol = candidates.policy()
        cards = candidates.from_gitlog(pol, self.root, [], findings)
        kinds = [card["kind"] for card in cards]
        self.assertIn("交付未推送·测试文案", kinds)
        self.assertNotIn(pol["kinds"]["uncommitted"], kinds)


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
