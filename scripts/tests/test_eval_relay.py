"""L2 回流执法的对照组。

`governance/eval-spec.yaml` 的 caseTiers.L2（「issue/ 每个 P0/P1 闭环后必须回流成 1 条；未回流不得标闭环」）
原本只是纸面纪律。这里给它的每一条判据都配反向对照——本仓的血泪教训是「量具会腐烂，得让它在测试里先红」，
没有对照组的检查等于没检查：
① 闭环却没有回流用例 ⇒ 必须报缺；② 用例的 `issueRef` 指向不存在的条目 ⇒ 必须 error 而不是绿；
再加两条防误伤/防装死的对照：已忽略或未闭环的条目不得被要求回流，状态词落在状态机枚举外时
必须显式报「判不了」，既不默认它是闭环、也不默认它没事。
"""
from __future__ import annotations
import copy, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eval import relay
from eval import run as evaluator

ROOT = Path(__file__).resolve().parents[2]
GATE_SPEC = ROOT / "evals/gate/eval.yaml"

TABLE = """# 一条问题

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | {grade} |
| 标签 | `流程缺陷` |
| 优化状态 | {state} |
"""

# issue/ 池里真实存在的第二种写法：front-matter 用「状态」而不是「优化状态」
FRONT_MATTER = """---
标题: 老格式条目
归属技能: Probe
等级: {grade}
状态: {state}
---

## 现象
"""

EVAL_YAML = """schema: tenger.eval/v1
skill: workflow
cases:
  - id: EV-P-001
    name: 合规夹具判绿
    layer: structure
    given: evals/gate/fixtures/ledger-clean
    expect: {validator: artifact, outcome: green}
"""

WITH_REF = EVAL_YAML.replace("outcome: green}", "outcome: green}\n    issueRef: issue/Probe/2026-01-01/01-x.md")
WITH_GHOST_REF = EVAL_YAML.replace("outcome: green}", "outcome: green}\n    issueRef: issue/Probe/2026-01-01/09-ghost.md")


class ProbeRepoMixin(unittest.TestCase):
    def build(self, issues: dict, eval_yaml: str) -> Path:
        """临时目录里搭一个最小仓库：几条 issue + 一套评测集；绝不碰仓内真实 issue。"""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for relative, body in issues.items():
            path = root.joinpath(*relative.split("/"))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        spec = root / "evals" / "probe" / "eval.yaml"
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_text(eval_yaml, encoding="utf-8")
        return root


class RelayClosedLoopTests(ProbeRepoMixin):
    def test_closed_p0_without_a_case_is_reported_as_missing(self):
        # ① 已闭环但无回流用例 → 必须报缺
        root = self.build({"issue/Probe/2026-01-01/01-x.md": TABLE.format(grade="P0", state="已沉淀")}, EVAL_YAML)
        result = relay.audit(root)
        self.assertEqual([entry["id"] for entry in result["closedP0P1"]], ["issue/Probe/2026-01-01/01-x.md"])
        self.assertEqual(result["covered"], [])
        self.assertEqual([entry["id"] for entry in result["missing"]], ["issue/Probe/2026-01-01/01-x.md"])
        self.assertIn("缺回流", relay.render(result))

    def test_a_single_backflow_case_closes_the_debt(self):
        # 同一条 issue 只要有一条用例指回来就不再报缺（执法的是「有没有」，不是「够不够多」）
        root = self.build({"issue/Probe/2026-01-01/01-x.md": TABLE.format(grade="P0", state="已沉淀")}, WITH_REF)
        result = relay.audit(root)
        self.assertEqual(result["missing"], [])
        self.assertEqual([entry["id"] for entry in result["covered"]], ["issue/Probe/2026-01-01/01-x.md"])
        self.assertEqual(result["dangling"], [])

    def test_ignored_issue_is_not_demanded_to_have_a_case(self):
        root = self.build({"issue/Probe/2026-01-01/01-x.md": TABLE.format(grade="P0", state="已忽略（本仓不适用）")},
                          EVAL_YAML)
        result = relay.audit(root)
        self.assertEqual(result["closedP0P1"], [])
        self.assertEqual(result["missing"], [])
        self.assertEqual([entry["id"] for entry in result["ignored"]], ["issue/Probe/2026-01-01/01-x.md"])

    def test_open_p1_is_not_demanded_yet(self):
        root = self.build({"issue/Probe/2026-01-01/01-x.md": TABLE.format(grade="P1", state="处理中")}, EVAL_YAML)
        self.assertEqual(relay.audit(root)["missing"], [])

    def test_p2_is_out_of_l2_scope(self):
        root = self.build({"issue/Probe/2026-01-01/01-x.md": TABLE.format(grade="P2", state="已沉淀")}, EVAL_YAML)
        self.assertEqual(relay.audit(root)["closedP0P1"], [])

    def test_status_word_outside_the_state_machine_is_reported_not_silently_passed(self):
        # 「复发重开」「已修规则」不在 issue/README.md 状态机枚举里：既不默认它是闭环，也不默认它没事
        root = self.build({"issue/Probe/2026-01-01/01-x.md": TABLE.format(grade="P0", state="**复发重开**（第 3 次）")},
                          EVAL_YAML)
        result = relay.audit(root)
        self.assertEqual(result["missing"], [])
        self.assertEqual([entry["id"] for entry in result["unknownState"]], ["issue/Probe/2026-01-01/01-x.md"])
        self.assertIn("判不了", relay.render(result))

    def test_front_matter_dialect_status_field_is_read_too(self):
        # 池里真有这种写法（Fidelity-Review / Frontend-Dev 2026-09-07）：只读「优化状态」会把它当成没问题
        root = self.build({"issue/Probe/2026-01-01/01-x.md": FRONT_MATTER.format(grade="P0", state="已沉淀")},
                          EVAL_YAML)
        self.assertEqual([entry["id"] for entry in relay.audit(root)["missing"]], ["issue/Probe/2026-01-01/01-x.md"])


class DanglingReferenceTests(ProbeRepoMixin):
    def test_audit_collects_a_reference_that_points_nowhere(self):
        root = self.build({"issue/Probe/2026-01-01/01-x.md": TABLE.format(grade="P1", state="待处理")},
                          WITH_GHOST_REF)
        result = relay.audit(root)
        self.assertEqual([row["case"] for row in result["dangling"]], ["EV-P-001"])
        self.assertIn("条目不存在", result["dangling"][0]["reason"])
        self.assertIn("悬空引用", relay.render(result))

    def test_run_case_reports_error_for_a_missing_issue_entry(self):
        # ② 用例的 issueRef 指向不存在的条目 → 必须 error，不许绿
        drifted = copy.deepcopy(evaluator.load_eval(GATE_SPEC)["cases"][0])
        drifted["issueRef"] = "issue/Nope/2026-01-01/01-does-not-exist.md"
        result = evaluator.run_case(drifted)
        self.assertEqual(result["status"], "error")
        self.assertIn("issueRef", result["reason"])
        self.assertIn("条目不存在", result["reason"])

    def test_a_ref_outside_the_issue_pool_is_error_not_a_guess(self):
        drifted = copy.deepcopy(evaluator.load_eval(GATE_SPEC)["cases"][0])
        drifted["issueRef"] = "evals/gate/fixtures/ledger-clean"
        self.assertEqual(evaluator.run_case(drifted)["status"], "error")
        drifted["issueRef"] = "../issue/outside.md"
        self.assertEqual(evaluator.run_case(drifted)["status"], "error")

    def test_behaviour_case_with_a_bad_ref_errors_before_any_engine_runs(self):
        # 引用核对在分派之前：解析不到就 error，绝不能先把引擎拉起来花钱。
        # 按 layer 取而不是按下标取最后一条：用例集尾部随时会新增结构层用例（2026-10-17 加了 resign 两条），
        # 下标取法会静默变成「拿一条结构层用例测行为层前置」——测试还在绿，判据已经没在测。
        cases = evaluator.load_eval(GATE_SPEC)["cases"]
        drifted = copy.deepcopy(next(case for case in reversed(cases) if case["layer"] == "behaviour"))
        self.assertEqual(drifted["layer"], "behaviour")
        drifted["issueRef"] = ["issue/Nope/2026-01-01/01-ghost.md"]
        result = evaluator.run_case(drifted)
        self.assertEqual(result["status"], "error")
        self.assertNotIn("tokens", result)

    def test_declared_case_without_ref_still_runs_normally(self):
        # 对照组另一侧：不写 issueRef（可选字段）不得影响判定
        result = evaluator.run_case(evaluator.load_eval(GATE_SPEC)["cases"][0])
        self.assertEqual(result["status"], "passed")

    def test_short_form_ref_resolves_and_ambiguity_is_refused(self):
        root = self.build({"issue/Probe/2026-01-01/01-a.md": TABLE.format(grade="P0", state="已沉淀"),
                           "issue/Probe/2026-01-01/02-b.md": TABLE.format(grade="P0", state="已沉淀")}, EVAL_YAML)
        self.assertEqual(relay.resolve_ref("issue/Probe/2026-01-01/02", root)[0], "issue/Probe/2026-01-01/02-b.md")
        (root / "issue" / "Probe" / "2026-01-01" / "02-c.md").write_text(TABLE.format(grade="P1", state="已沉淀"),
                                                                        encoding="utf-8")
        resolved, reason = relay.resolve_ref("issue/Probe/2026-01-01/02", root)
        self.assertIsNone(resolved)
        self.assertIn("无法确定唯一", reason)


class BackflowLayerTests(ProbeRepoMixin):
    """「已回流」必须分结构层／仅行为层两列：行为层用例夜间一律 blocked。

    2026-10-17 并发会话把 5 条接成行为层用例（EV-FE-103／EV-PRD-102／EV-PRD-103／EV-SOPT-101／EV-TDD-103），
    混在「已回流 26 条」里会被读成「这些规则现在都能拦住」——只登记了用例，拦截力没有增加。
    """

    BEHAVIOUR_REF = """schema: tenger.eval/v1
skill: workflow
cases:
  - id: EV-P-101
    layer: behaviour
    given: evals/gate/fixtures/ledger-clean
    prompt: "跑一遍"
    tokenBudget: 1000
    expect: {mustNotContain: "X"}
    issueRef: issue/Probe/2026-01-01/01-x.md
"""

    MIXED_REF = """schema: tenger.eval/v1
skill: workflow
cases:
  - id: EV-P-001
    layer: structure
    given: evals/gate/fixtures/ledger-clean
    expect: {validator: artifact, outcome: green}
    issueRef: issue/Probe/2026-01-01/01-x.md
  - id: EV-P-101
    layer: behaviour
    given: evals/gate/fixtures/ledger-clean
    prompt: "跑一遍"
    tokenBudget: 1000
    expect: {mustNotContain: "X"}
    issueRef: issue/Probe/2026-01-01/01-x.md
"""

    ISSUE = "issue/Probe/2026-01-01/01-x.md"

    def test_behaviour_only_backflow_is_split_out_and_points_at_the_behaviour_ledger(self):
        root = self.build({self.ISSUE: TABLE.format(grade="P0", state="已沉淀")}, self.BEHAVIOUR_REF)
        result = relay.audit(root)
        self.assertEqual([entry["id"] for entry in result["covered"]], [self.ISSUE])
        self.assertEqual(result["coveredStructure"], [])
        self.assertEqual([entry["id"] for entry in result["coveredBehaviourOnly"]], [self.ISSUE])
        self.assertEqual(result["coveredCases"][self.ISSUE], ["EV-P-101"])
        text = relay.render(result)
        self.assertIn("仅行为层回流", text)
        self.assertIn("行为层台账", text, "横幅必须把读的人引到真跑台账，不许拿「待授权」冒充没跑")
        self.assertIn("EV-P-101", text, "只报条数看不出是哪条用例在顶")

    def test_structure_backflow_counts_as_blocking_coverage(self):
        root = self.build({self.ISSUE: TABLE.format(grade="P0", state="已沉淀")}, WITH_REF)
        result = relay.audit(root)
        self.assertEqual([entry["id"] for entry in result["coveredStructure"]], [self.ISSUE])
        self.assertEqual(result["coveredBehaviourOnly"], [])
        self.assertNotIn("仅行为层回流", relay.render(result), "结构层能当场判，就不该挂仅行为层横幅")

    def test_mixed_layers_count_as_structure_and_list_every_case(self):
        root = self.build({self.ISSUE: TABLE.format(grade="P0", state="已沉淀")}, self.MIXED_REF)
        result = relay.audit(root)
        self.assertEqual([entry["id"] for entry in result["coveredStructure"]], [self.ISSUE])
        self.assertEqual(result["coveredBehaviourOnly"], [])
        self.assertEqual(sorted(result["coveredCases"][self.ISSUE]), ["EV-P-001", "EV-P-101"])

    def test_real_pool_covered_entries_expose_layer_and_cases(self):
        result = relay.audit(ROOT)
        covered = {entry["id"] for entry in result["covered"]}
        structure = {entry["id"] for entry in result["coveredStructure"]}
        behaviour = {entry["id"] for entry in result["coveredBehaviourOnly"]}
        self.assertEqual(covered, structure | behaviour)
        self.assertEqual(structure & behaviour, set())
        for ident in covered:
            self.assertTrue(result["coveredCases"].get(ident), f"{ident} 说已回流却没有可报的用例 id")


class TriageTests(ProbeRepoMixin):
    """分诊核对：缺回流要么接成用例、要么写明不可机械化的结论——新增缺口没分诊就报红。

    方向要摆对：名单里已不再缺的条目（用例接上了）只报「过期」不报红，否则就是把判据调反、
    惩罚进展。尺子本身读不动（缺 l2Triage 或 declared 为空）也不许当成「没有未分诊」。
    """

    def spec(self, root: Path, declared) -> None:
        import yaml
        path = root / "governance" / "eval-spec.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        section = {"l2Triage": {"rule": "每条 missing 都要在 declared 里", "declared": declared,
                                "texts": {"undeclared": "UNDECLARED-判据文本", "stale": "STALE-判据文本",
                                          "clean": "CLEAN-判据文本", "missingPolicy": "MISSINGPOLICY-判据文本"}}}
        if declared == "drop-section":
            section = {"version": 1}
        path.write_text(yaml.safe_dump(section, allow_unicode=True), encoding="utf-8")

    def second_gap(self, root: Path) -> None:
        path = root / "issue" / "Probe" / "2026-01-02" / "01-y.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(TABLE.format(grade="P1", state="已沉淀"), encoding="utf-8")

    def test_undocumented_gap_is_undeclared(self):
        root = self.build({"issue/Probe/2026-01-01/01-x.md": TABLE.format(grade="P0", state="已沉淀")}, EVAL_YAML)
        self.second_gap(root)
        self.spec(root, [{"issue": "issue/Probe/2026-01-01/01-x.md", "verdict": "需 agent_judge",
                          "reason": "语义判断，结构层无等价尺子"}])
        result = relay.audit(root)
        self.assertEqual(result["triage"]["covered"], ["issue/Probe/2026-01-01/01-x.md"])
        self.assertEqual(result["triage"]["undeclared"], ["issue/Probe/2026-01-02/01-y.md"],
                         "新增缺口没进名单就必须点名，不能只报「还差两条」")
        self.assertEqual(result["triage"]["stale"], [])
        text = relay.render(result)
        self.assertIn("UNDECLARED-判据文本", text)
        self.assertIn("issue/Probe/2026-01-02/01-y.md", text)

    def test_triaged_gap_reads_clean_and_shows_the_verdict(self):
        root = self.build({"issue/Probe/2026-01-01/01-x.md": TABLE.format(grade="P0", state="已沉淀")}, EVAL_YAML)
        self.spec(root, [{"issue": "issue/Probe/2026-01-01/01-x.md", "verdict": "证据双侧交集为空",
                          "reason": "真实文档侧 0 命中（附扫描计数）"}])
        result = relay.audit(root)
        self.assertEqual(result["triage"]["undeclared"], [])
        text = relay.render(result)
        self.assertIn("CLEAN-判据文本", text)
        self.assertIn("证据双侧交集为空", text, "分诊结论要能看见，不能只报一个条数")

    def test_wired_entry_makes_the_list_stale_but_not_undeclared(self):
        # 反向对照：把回流用例接上 ⇒ 缺口消失，名单里这一条变「过期」；过期不许冒充未分诊
        root = self.build({"issue/Probe/2026-01-01/01-x.md": TABLE.format(grade="P0", state="已沉淀")}, WITH_REF)
        self.spec(root, [{"issue": "issue/Probe/2026-01-01/01-x.md", "verdict": "证据双侧交集为空",
                          "reason": "旧结论，现已接上"}])
        result = relay.audit(root)
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["triage"]["stale"], ["issue/Probe/2026-01-01/01-x.md"])
        self.assertEqual(result["triage"]["undeclared"], [])
        text = relay.render(result)
        self.assertIn("STALE-判据文本", text)
        self.assertNotIn("UNDECLARED-判据文本", text)

    def test_empty_declared_uses_the_registry_text(self):
        root = self.build({"issue/Probe/2026-01-01/01-x.md": TABLE.format(grade="P0", state="已沉淀")}, EVAL_YAML)
        self.spec(root, [])
        result = relay.audit(root)
        self.assertEqual(result["triage"]["error"], "MISSINGPOLICY-判据文本")
        self.assertIn("MISSINGPOLICY-判据文本", relay.render(result))

    def test_absent_section_is_red_not_skipped(self):
        root = self.build({"issue/Probe/2026-01-01/01-x.md": TABLE.format(grade="P0", state="已沉淀")}, EVAL_YAML)
        self.spec(root, "drop-section")
        result = relay.audit(root)
        self.assertIn("未声明 l2Triage", result["triage"]["error"])

    def test_unreadable_spec_says_could_not_check(self):
        root = self.build({"issue/Probe/2026-01-01/01-x.md": TABLE.format(grade="P0", state="已沉淀")}, EVAL_YAML)
        result = relay.audit(root)   # 临时仓里没有 governance/eval-spec.yaml
        self.assertTrue(result["triage"]["error"].startswith("分诊核对读不动"),
                        "文件不在也要如实说「没能核」，不能悄悄当通过")


class RealPoolTriageTests(unittest.TestCase):
    def test_real_gaps_are_triaged_one_to_one(self):
        result = relay.audit(ROOT)
        triage = result["triage"]
        self.assertEqual(triage["error"], "")
        self.assertEqual(triage["undeclared"], [], "现仓缺回流必须逐条有分诊结论")
        self.assertEqual(len(triage["covered"]), len(result["missing"]))
        self.assertEqual(sorted(triage["declared"]), sorted(set(triage["covered"]) | set(triage["stale"])),
                         "名单里每一条要么还压着缺口（已分诊），要么已被用例接上（过期）——不许有第三种默默失踪")
        # 「过期」只允许一种成因：回流用例真的接上了（条目仍是 P0/P1 已闭环，且有 issueRef 指回）。
        # 条目被删、状态被改回待处理／已忽略 都等于把缺口读没，必须红。
        # 2026-10-17 行为层轮把 5 条接成用例 ⇒ 这 5 条按本判据判为正当过期；
        # governance/eval-spec.yaml 的名单修剪由用户做（本轮对 governance/* 无写权），这里不代笔。
        closed = {entry["id"] for entry in result["closedP0P1"]}
        wired = {entry["id"] for entry in result["covered"]}
        missing_ids = {entry["id"] for entry in result["missing"]}
        for ident in triage["stale"]:
            self.assertNotIn(ident, missing_ids, f"{ident} 既过期又缺回流，自相矛盾")
            self.assertIn(ident, closed, f"{ident} 的过期不是「用例接上了」，而是条目不再要求回流（被删／改状态）")
            self.assertIn(ident, wired, f"{ident} 说过期，却没有回流的用例指回")
        for ident, item in triage["declared"].items():
            self.assertTrue(item["verdict"] and item["reason"], f"{ident} 的分诊结论不能空着")


class RealPoolWiringTests(unittest.TestCase):
    """执法器必须真的对着本仓现状工作——只在临时夹具里绿，等于没接上。"""

    def test_every_entry_in_the_pool_is_parsed_none_is_silently_skipped(self):
        files = [path for path in (ROOT / "issue").rglob("*.md") if path.name != "README.md"]
        self.assertEqual(len(relay.issue_entries(ROOT)), len(files))

    def test_real_pool_has_closed_p0_p1_entries_and_the_parser_sees_them(self):
        # 判据字段名或写法一旦漂移，解析会静默返回空 → 这条先红，才说明执法还活着
        self.assertGreaterEqual(len(relay.audit(ROOT)["closedP0P1"]), 1)

    def test_declared_issue_refs_in_the_repo_all_resolve(self):
        self.assertEqual(relay.audit(ROOT)["dangling"], [])

    def test_at_least_one_closed_issue_now_has_a_backflow_case(self):
        # 反向对照：接线本身不能退化成「字段有人写、没人读」
        self.assertGreaterEqual(len(relay.audit(ROOT)["covered"]), 1)

    def test_workflow_2026_10_10_closed_entries_have_backflow_cases(self):
        # 2026-10-15 补线的两条 WorkFlow P0 必须保持在覆盖里：用例被删、issueRef 被漂改，这里先红
        covered = {entry["id"] for entry in relay.audit(ROOT)["covered"]}
        self.assertIn("issue/WorkFlow/2026-10-10/01-上游Gate关闭后下游仍排队缺开工前闸门校验.md", covered)
        self.assertIn("issue/WorkFlow/2026-10-10/02-业务项目控制文件偏离v2契约致Gate从未被机械校验.md", covered)

    def test_required_count_always_equals_covered_plus_missing(self):
        result = relay.audit(ROOT)
        self.assertEqual(len(result["closedP0P1"]), len(result["covered"]) + len(result["missing"]))
        self.assertEqual({entry["id"] for entry in result["missing"]} & {entry["id"] for entry in result["covered"]}, set())


if __name__ == "__main__":
    unittest.main()
