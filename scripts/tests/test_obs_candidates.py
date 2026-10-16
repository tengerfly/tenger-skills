"""候选问题卡生成器的反向对照（plan v2 §5 闭环中间段第一格）。

每条执法都配「合规必绿／改坏必红」对照，且**断言具体判据文本**而不是只看有没有产出——
本仓的血泪教训是「因无关原因失败」会被当成回归通过。逐面钉住：

① verify（产物改了没落台账）：字节一致必须没卡；改了正文必须出卡，并带上台账记录值与磁盘现值两个 sha256；
② report / gitlog（节点未收口）：同一事实被两面上报 ⇒ 只出一张卡、两处判据都抄进卡，重跑不叠卡；
③ gitlog（改动未提交）：阈值调宽必须没卡，超龄必须出卡并带 mtime 窗口与文件 sha256；
④ relay（缺回流用例）：补一条 issueRef 必须没卡；闭环无回流必须出卡并带上 L2 判据原文；
   P2／未闭环不得被误伤（判据宁窄勿宽）；
⑤ 硬边界：卡面显式「候选·未经确认」、等级留空（不代填 P0/P1）、落点被注册表禁止时机械拒绝写
   `issue/`；取不到的维度必须写明 N/A 原因，不许留白。
"""
from __future__ import annotations
import hashlib, os, subprocess, sys, tempfile, time, unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tsr
from obs import candidates, schema

ROOT = Path(__file__).resolve().parents[2]
POLICY = candidates.policy()
KINDS = POLICY["kinds"]
L2_RULE = "未回流不得标闭环"

ISSUE_TABLE = """# 一条问题

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | {grade} |
| 标签 | `流程缺陷` |
| 优化状态 | {state} |
"""

EVAL_NO_REF = """schema: tenger.eval/v1
skill: workflow
cases:
  - id: EV-P-001
    name: 合规夹具判绿
    layer: structure
    given: evals/gate/fixtures/ledger-clean
    expect: {validator: artifact, outcome: green}
"""
EVAL_WITH_REF = EVAL_NO_REF.replace(
    "outcome: green}", "outcome: green}\n    issueRef: issue/Probe/2026-01-01/01-x.md")
EVAL_GHOST_REF = EVAL_NO_REF.replace(
    "outcome: green}", "outcome: green}\n    issueRef: issue/Probe/2026-01-01/09-ghost.md")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def card_of(result, kind):
    return [card for card in result["cards"] if card["kind"] == kind]


class RepoMixin(unittest.TestCase):
    """临时仓：run-log 由 tsr 自己落盘，ts 与 sha256 都是机器生成的，不是手写的。"""

    def make(self, commit=False):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / ".spec/prd").mkdir(parents=True)
        self.doc = root / ".spec/prd/overview.md"
        self.doc.write_text("# v1\n", encoding="utf-8")
        if commit:
            git(root, "init", "-q")
            git(root, "config", "user.email", "probe@example.invalid")
            git(root, "config", "user.name", "probe")
            git(root, "add", ".")
            git(root, "commit", "-qm", "chore: fixture")
        return root

    def closed_node(self, root, execution="EXEC-PROBE-1", node="prd-design"):
        flags = ["--project-root", str(root), "--execution-id", execution, "--node", node,
                 "--skill", node]
        self.assertEqual(0, tsr.main(flags + ["--state", "PRD_IN_PROGRESS", "node-start"]))
        self.assertEqual(0, tsr.main(flags + ["--state", "PRD_APPROVED", "node-end",
                                              "--gate", "PASS", "--allow-downstream", "true",
                                              "--artifact", ".spec/prd/overview.md"]))

    def open_node(self, root, execution="EXEC-OPEN-1", node="prd-design"):
        self.assertEqual(0, tsr.main(["--project-root", str(root), "--execution-id", execution,
                                      "--node", node, "--skill", node,
                                      "--state", "PRD_IN_PROGRESS", "node-start"]))


class VerifySurfaceTests(RepoMixin):
    def test_compliant_binding_produces_no_drift_card(self):
        root = self.make()
        self.closed_node(root)
        self.assertEqual(card_of(candidates.collect(root), KINDS["bindingDrift"]), [])

    def test_edited_artifact_produces_card_with_machine_pointers(self):
        root = self.make()
        self.closed_node(root)
        recorded = sha(self.doc)
        self.doc.write_text("# v1\n# 改了正文没落台账\n", encoding="utf-8")
        disk = sha(self.doc)
        events = schema.read_events(root)
        ended = [event for event in events if event["event"] == "node-end"][0]
        cards = card_of(candidates.collect(root), KINDS["bindingDrift"])
        self.assertEqual(len(cards), 1)
        card = cards[0]
        self.assertEqual(card["executionId"], "EXEC-PROBE-1")
        self.assertEqual(card["node"], "prd-design")
        start, end = candidates.node_window(events, "EXEC-PROBE-1", "prd-design")
        self.assertEqual((card["window"]["start"], card["window"]["end"]), (start, end))
        self.assertTrue(start and end)
        self.assertEqual([item["path"] for item in card["artifacts"]], [".spec/prd/overview.md"])
        self.assertEqual(card["artifacts"][0]["recorded"], recorded)
        self.assertEqual(card["artifacts"][0]["disk"], disk)
        self.assertEqual(card["runLogRefs"], [f"{schema.RUN_LOG}#{ended['seq']}"])
        text = candidates.render(card, POLICY)
        # 断言具体判据文本，而不是只看有没有卡
        self.assertIn("artifact edited after node-end", text)
        self.assertIn("改了正文没落台账", text)
        self.assertIn(recorded, text)
        self.assertIn(disk, text)
        self.assertIn("候选·未经确认", text)

    def test_vanished_artifact_is_carded_with_explicit_na_reason(self):
        root = self.make()
        self.closed_node(root)
        self.doc.unlink()
        cards = card_of(candidates.collect(root), KINDS["artifactGone"])
        self.assertEqual(len(cards), 1)
        self.assertIsNone(cards[0]["artifacts"][0]["disk"])
        text = candidates.render(cards[0], POLICY)
        self.assertIn("artifact vanished", text)
        self.assertIn("磁盘上已无此文件", text)

    def test_card_never_assigns_a_grade(self):
        root = self.make()
        self.closed_node(root)
        self.doc.write_text("# touched\n", encoding="utf-8")
        card = card_of(candidates.collect(root), KINDS["bindingDrift"])[0]
        grade_lines = [line for line in candidates.render(card, POLICY).splitlines()
                       if line.startswith("- 等级：")]
        self.assertEqual(grade_lines, [f"- 等级：**{POLICY['gradeValue']}**"])


class DedupeTests(RepoMixin):
    def test_same_fact_from_two_surfaces_yields_one_card(self):
        # node-start 没有 node-end：看板派生面与 git 轨巡检面都命中 ⇒ 一张卡、两处判据
        root = self.make(commit=True)
        self.open_node(root)
        result = candidates.collect(root, max_age_hours=0.0)
        cards = card_of(result, KINDS["unclosedNode"])
        self.assertEqual(len(cards), 1)
        self.assertEqual(sorted(cards[0]["surfaces"]), ["gitlog", "report"])
        self.assertEqual(len(cards[0]["judges"]), 2)
        self.assertIn("进行中/未收口", cards[0]["judges"][0])
        self.assertIn("没有 node-end", cards[0]["judges"][1])
        written = candidates.write(root, cards)
        self.assertEqual(len(written["created"]), 1)
        again = candidates.write(root, card_of(candidates.collect(root, max_age_hours=0.0),
                                               KINDS["unclosedNode"]))
        self.assertEqual(again["created"], [])
        self.assertEqual(len(again["unchanged"]), 1)
        self.assertEqual(len(list((root / POLICY["outputDir"]).glob("*.md"))), 1)

    def test_unclosed_window_has_no_end_and_says_why(self):
        root = self.make()
        self.open_node(root, execution="EXEC-OPEN-2")
        card = card_of(candidates.collect(root), KINDS["unclosedNode"])[0]
        self.assertIsNone(card["window"]["end"])
        self.assertTrue(card["window"]["start"])
        text = candidates.render(card, POLICY)
        self.assertIn("止 `N/A`", text)
        self.assertIn("不拿巡检时刻冒充收口", text)


class GitlogSurfaceTests(RepoMixin):
    def test_fresh_edits_under_threshold_produce_no_card(self):
        root = self.make(commit=True)
        self.doc.write_text("# mid-flight, just saved\n", encoding="utf-8")
        self.assertEqual(card_of(candidates.collect(root, max_age_hours=24.0),
                                 KINDS["uncommitted"]), [])

    def test_aged_uncommitted_work_is_carded_with_digest_and_mtime_window(self):
        root = self.make(commit=True)
        self.doc.write_text("# mid-flight\n# 三天了没人提交\n", encoding="utf-8")
        stamp = time.time() - 72 * 3600
        os.utime(self.doc, (stamp, stamp))
        cards = card_of(candidates.collect(root, max_age_hours=4.0), KINDS["uncommitted"])
        self.assertEqual(len(cards), 1)
        card = cards[0]
        self.assertIsNone(card["executionId"])   # git 轨的工作树项在 run-log 里没有事件
        self.assertEqual([item["path"] for item in card["artifacts"]], [".spec/prd/overview.md"])
        self.assertEqual(card["artifacts"][0]["disk"], sha(self.doc))
        self.assertIsNone(card["artifacts"][0]["recorded"])
        self.assertTrue(card["window"]["start"] and card["window"]["end"])
        text = candidates.render(card, POLICY)
        self.assertIn("改动未提交", text)
        self.assertIn("无 executionId 可指", text)
        self.assertIn(sha(self.doc), text)
        self.assertIn("没有被任何 node-end 绑定过", text)


class RelaySurfaceTests(RepoMixin):
    def build(self, issue_body, eval_yaml):
        root = self.make()
        entry = root / "issue/Probe/2026-01-01/01-x.md"
        entry.parent.mkdir(parents=True, exist_ok=True)
        entry.write_text(issue_body, encoding="utf-8")
        spec = root / "evals/probe/eval.yaml"
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_text(eval_yaml, encoding="utf-8")
        return root, entry

    def test_closed_p0_without_case_is_carded_with_rule_verbatim(self):
        root, entry = self.build(ISSUE_TABLE.format(grade="P0", state="已沉淀"), EVAL_NO_REF)
        cards = card_of(candidates.collect(root), KINDS["missingBackflow"])
        self.assertEqual(len(cards), 1)
        card = cards[0]
        self.assertEqual(card["evidence"], "issue/Probe/2026-01-01/01-x.md")
        self.assertEqual(card["artifacts"][0]["disk"], sha(entry))
        self.assertIsNone(card["executionId"])
        text = candidates.render(card, POLICY)
        self.assertIn(L2_RULE, text)                 # 命中的判据文本原文
        self.assertIn(sha(entry), text)
        # N/A 原因取自注册表，测试也不复述一遍（复述就等于又造了第二套口径）
        self.assertIn(POLICY["naReasons"]["relayGap"], text)

    def test_a_backflow_case_removes_the_candidate(self):
        root, _ = self.build(ISSUE_TABLE.format(grade="P0", state="已沉淀"), EVAL_WITH_REF)
        self.assertEqual(card_of(candidates.collect(root), KINDS["missingBackflow"]), [])

    def test_open_or_p2_entries_are_not_carded(self):
        # 判据宁窄勿宽：只有 P0/P1 且已闭环才要回流；未闭环与 P2 不该被误伤
        for grade, state in (("P0", "处理中"), ("P2", "已沉淀")):
            root, _ = self.build(ISSUE_TABLE.format(grade=grade, state=state), EVAL_NO_REF)
            self.assertEqual(card_of(candidates.collect(root), KINDS["missingBackflow"]), [],
                             f"{grade}/{state} 不该要求回流")

    def test_dangling_issue_ref_is_carded(self):
        root, _ = self.build(ISSUE_TABLE.format(grade="P1", state="已沉淀"), EVAL_GHOST_REF)
        cards = card_of(candidates.collect(root), KINDS["danglingRef"])
        self.assertEqual(len(cards), 1)
        text = candidates.render(cards[0], POLICY)
        self.assertIn("悬空", text)
        self.assertIn("09-ghost.md", text)

    def test_unreadable_eval_set_is_carded_not_treated_as_clean(self):
        root, _ = self.build(ISSUE_TABLE.format(grade="P0", state="已沉淀"), "schema: broken\n")
        cards = card_of(candidates.collect(root), KINDS["unreadableEval"])
        self.assertEqual(len(cards), 1)
        self.assertIn("读不动", candidates.render(cards[0], POLICY))


class BoundaryTests(RepoMixin):
    def test_registry_forbids_writing_into_issue_pool(self):
        # 落点硬边界是机械兜底，不是口头承诺：改注册表把落点挪进 issue/ 必须被拒
        root = self.make()
        (root / "governance").mkdir(parents=True)
        tampered = yaml.safe_load(candidates.SHIPPED_REGISTRY.read_text(encoding="utf-8"))
        tampered["candidates"]["outputDir"] = "issue/candidates"
        (root / "governance/obs-registry.yaml").write_text(
            yaml.safe_dump(tampered, allow_unicode=True), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            candidates.write(root, [])
        self.assertIn("候选卡落点被注册表禁止", str(caught.exception))
        self.assertFalse((root / "issue").exists())

    def test_missing_policy_section_refuses_to_guess_landing_spot(self):
        root = self.make()
        (root / "governance").mkdir(parents=True)
        (root / "governance/obs-registry.yaml").write_text("version: 1\n", encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            candidates.policy(root)
        self.assertIn("未声明 candidates.outputDir", str(caught.exception))

    def test_incomplete_policy_refuses_default_values(self):
        root = self.make()
        (root / "governance").mkdir(parents=True)
        thinned = yaml.safe_load(candidates.SHIPPED_REGISTRY.read_text(encoding="utf-8"))
        del thinned["candidates"]["naReasons"]
        (root / "governance/obs-registry.yaml").write_text(
            yaml.safe_dump(thinned, allow_unicode=True), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            candidates.policy(root)
        self.assertIn("缺必需键", str(caught.exception))

    def test_cards_carry_the_unconfirmed_label_and_recompute_line(self):
        root = self.make()
        self.closed_node(root)
        self.doc.write_text("# drifted\n", encoding="utf-8")
        card = candidates.collect(root)["cards"][0]
        text = candidates.render(card, POLICY)
        self.assertIn(f"# 候选问题卡 · {card['kind']}（候选·未经确认）", text)
        self.assertIn(POLICY["recompute"], text)
        self.assertIn("不写进 `issue/`", text)
        self.assertIn("候选卡是镜像不是真相", text)


class RealRepoTests(unittest.TestCase):
    """真数据：拿本仓现有检测面跑出一份非空候选，数量与检出面自证一致。"""

    @classmethod
    def setUpClass(cls):
        cls.result = candidates.collect(ROOT)

    def test_real_repo_produces_non_empty_candidates_matching_detector_counts(self):
        from eval import relay
        expected = len(relay.audit(ROOT)["missing"])
        self.assertGreaterEqual(expected, 1, "本仓 L2 缺口应如实存在，别当它没了")
        cards = card_of(self.result, KINDS["missingBackflow"])
        self.assertEqual(len(cards), expected)
        self.assertTrue(len(self.result["cards"]) > 0)
        for card in self.result["cards"]:
            self.assertIn(card["kind"], set(KINDS.values()), "不得发明 kind")
            self.assertTrue(card["judges"], "每张卡必须抄到判据文本原文")
            self.assertTrue(card["evidence"])

    def test_every_real_card_has_pointers_or_written_na_reasons(self):
        for card in self.result["cards"]:
            text = candidates.render(card, POLICY)
            self.assertIn("候选·未经确认", text)
            self.assertIn(POLICY["gradeValue"], text)
            if not card["executionId"]:
                self.assertTrue(any("executionId" in line and "N/A" in line
                                    for line in text.splitlines()),
                                f"{card['kind']}：取不到 executionId 必须显式 N/A 并写明原因")
            if not card["window"].get("end"):
                self.assertTrue(any("ts 窗口" in line and "N/A" in line for line in text.splitlines()),
                                f"{card['kind']}：窗口缺端必须显式 N/A，不许留白")

    def test_declared_landing_spot_is_not_inside_the_issue_pool(self):
        out = (ROOT / POLICY["outputDir"]).resolve()
        pool = (ROOT / "issue").resolve()
        self.assertFalse(str(out).startswith(str(pool)))
        self.assertEqual(POLICY["forbidWriteInto"], ["issue"])


if __name__ == "__main__":
    unittest.main()
