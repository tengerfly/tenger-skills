"""2026-10-16 轮 L2 回流补线的对照组。

这格把「已闭环却没有回归用例」的历史问题真正转成用例：结构层 8 条（EV-GATE-012..019，
指回 issue/Skill-Optimizer/2026-09-04/02 与 issue/WorkFlow/2026-09-23/04）＋行为层 12 条
（新开 5 套评测集，另有 2 条 frontend-dev 的用例因锚障碍挂进 frontend-tech-design 套）。
2026-10-17 轮再补 5 条禁止式行为用例（EV-TDD-103／EV-PRD-102／EV-PRD-103／EV-FE-103／
EV-SOPT-101，新开 sediment 套 1 条），把「只有真跑才能判」的缺回流条目接进评测集；
它们的判据同样在下面被翻红，本文件任何一条都不许真的把引擎拉起来。
没有对照组的量具等于另一个自述，所以每条都先被翻红一遍：

① 结构层红用例把期望从 red 改成 green 必须报 failed；
② `mustContain` 换成不存在的判据文本必须报 failed（不许借别的错冒充回归通过）；
③ 判绿对照（EV-GATE-012／EV-GATE-017）被注入违规后仍期望 green 必须报 failed——
   防「P0 残留不得 PASS」「缺基线须登记例外」这两条检出口径漂成过罚合规产物；
④ 夹具缺失／tamper 落不到字必须算 error，不许静默变绿；
⑤ 行为层用例的判据本身要真能翻红：违规形态的回答必须 failed、合规回答必须 passed、
   分节或问句取不到必须 error（引擎用 stub 顶掉，单测绝不花钱）；
⑥ 整套仓评测在任何情况下都不许真的把引擎拉起来（subprocess 被顶成炸弹）。
"""
from __future__ import annotations
import copy, os, sys, unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eval import run as evaluator

ROOT = Path(__file__).resolve().parents[2]
GATE_SPEC = ROOT / "evals/gate/eval.yaml"
NEW_SETS = ("prd-design", "frontend-tech-design", "fidelity-review",
            "prototype-review", "tech-review", "sediment")
STRUCTURE_RED = ("EV-GATE-013", "EV-GATE-014", "EV-GATE-015", "EV-GATE-016",
                 "EV-GATE-018", "EV-GATE-019")


def gate_case(case_id: str) -> dict:
    spec = evaluator.load_eval(GATE_SPEC)
    return next(item for item in spec["cases"] if item["id"] == case_id)


def all_cases() -> dict:
    rows = {}
    for spec_path in sorted(ROOT.glob("evals/*/eval.yaml")):
        for case in evaluator.load_eval(spec_path).get("cases") or []:
            rows[case["id"]] = case
    return rows


class StructureBackflowControls(unittest.TestCase):
    """EV-GATE-012..019：分级冻结与视觉基线例外登记的三条反向对照。"""

    def test_red_expectation_flipped_to_green_reports_failed(self):
        for case_id in STRUCTURE_RED:
            drifted = copy.deepcopy(gate_case(case_id))
            self.assertEqual(drifted["expect"]["outcome"], "red", case_id)
            drifted["expect"]["outcome"] = "green"
            result = evaluator.run_case(drifted)
            self.assertEqual(result["status"], "failed", f"{case_id} 的 red 期望可以随便调绿")

    def test_absent_finding_text_cannot_borrow_an_unrelated_failure(self):
        for case_id in STRUCTURE_RED:
            weak = copy.deepcopy(gate_case(case_id))
            weak["expect"]["mustContain"] = "这段判据文本不存在"
            self.assertEqual(evaluator.run_case(weak)["status"], "failed",
                             f"{case_id} 去掉判据文本后仍可借别的错通过")

    def test_each_red_case_names_its_own_finding_text(self):
        # 三条「写成 PASS」类用例各断言自己的地址（workflow／轮次记录文件名），
        # 否则同一次红会被彼此借用，用例之间就没有区分度了
        self.assertIn("workflow PASS", gate_case("EV-GATE-013")["expect"]["mustContain"])
        self.assertIn("GATE-REVIEW-R4.yaml PASS", gate_case("EV-GATE-015")["expect"]["mustContain"])
        self.assertNotEqual(gate_case("EV-GATE-013")["expect"]["mustContain"],
                            gate_case("EV-GATE-015")["expect"]["mustContain"])

    def test_green_controls_flip_to_failed_when_the_violation_is_injected(self):
        frozen = copy.deepcopy(gate_case("EV-GATE-012"))
        frozen["tamper"] = copy.deepcopy(gate_case("EV-GATE-013")["tamper"])
        result = evaluator.run_case(frozen)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["outcome"], "red", "P0 残留按 BLOCKED 收口的合规形状被误罚")

        exception = copy.deepcopy(gate_case("EV-GATE-017"))
        exception["tamper"] = copy.deepcopy(gate_case("EV-GATE-018")["tamper"])
        result = evaluator.run_case(exception)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["outcome"], "red")

    def test_missing_fixture_is_error_not_pass(self):
        for case_id in ("EV-GATE-012", "EV-GATE-017"):
            broken = copy.deepcopy(gate_case(case_id))
            broken["given"] = "evals/gate/fixtures/does-not-exist"
            self.assertEqual(evaluator.run_case(broken)["status"], "error", case_id)

    def test_missing_or_rotted_tamper_target_is_error(self):
        ghost = copy.deepcopy(gate_case("EV-GATE-013"))
        ghost["tamper"]["file"] = ".spec/ghost.yaml"
        result = evaluator.run_case(ghost)
        self.assertEqual(result["status"], "error")
        self.assertIn("tamper target missing", result["reason"])

        rotted = copy.deepcopy(gate_case("EV-GATE-018"))
        rotted["tamper"]["replace"]["from"] = "exceptionId: EXC-SOMETHING-ELSE"
        result = evaluator.run_case(rotted)
        self.assertEqual(result["status"], "error")
        self.assertIn("tamper 'from' not found", result["reason"])

    def test_new_backflow_refs_resolve_not_dangling(self):
        for case_id in STRUCTURE_RED + ("EV-GATE-012", "EV-GATE-017"):
            self.assertEqual(evaluator.issue_ref_problem(gate_case(case_id)), "", case_id)


class BehaviourCaseDeclarationTests(unittest.TestCase):
    """行为层用例的声明本身也会腐烂：预算、判据、引擎、夹具、注入的 skill 正文路径缺一不可。"""

    def setUp(self):
        self.behaviour = {case_id: case for case_id, case in all_cases().items()
                          if case["layer"] == "behaviour"}
        self.assertIn("EV-GATE-102", self.behaviour)

    def test_every_behaviour_case_declares_budget_engine_prompt_and_criterion(self):
        for case_id, case in self.behaviour.items():
            self.assertTrue(case.get("tokenBudget"), f"{case_id} 没有预算闸")
            self.assertEqual(case.get("engine"), "codex", f"{case_id} 引擎未显式声明")
            self.assertTrue(str(case.get("prompt") or "").strip(), f"{case_id} 没有 prompt")
            expect = case.get("expect") or {}
            self.assertTrue(expect.get("mustNotContain") or expect.get("produces"),
                            f"{case_id} 没有可判据＝跑了个寂寞")

    def test_every_behaviour_case_skill_file_exists(self):
        # 注入的 skill 正文被改名或移动时，materialise 会在真跑当天才炸——那要在声明期就红
        for case_id, case in self.behaviour.items():
            for relative in case.get("skillFiles") or []:
                self.assertTrue((ROOT / relative).is_file(), f"{case_id} 的 skill 正文缺失: {relative}")

    def test_every_behaviour_case_fixture_dir_exists(self):
        # 锚算不出来＝基线无从核对；夹具不存在＝真跑必 error，两者都要提前红
        for case_id, case in self.behaviour.items():
            self.assertTrue((ROOT / str(case["given"])).is_dir(), f"{case_id} 夹具缺失: {case['given']}")

    def test_new_sets_load_and_every_case_there_points_at_an_issue(self):
        # 新开的套不能变成「有套无债」的空壳：每条用例都得指回一条真实 issue
        for name in NEW_SETS:
            spec_path = ROOT / "evals" / name / "eval.yaml"
            self.assertTrue(spec_path.is_file(), f"缺评测集：{spec_path}")
            cases = evaluator.load_eval(spec_path).get("cases") or []
            self.assertTrue(cases, f"{name} 是空套")
            for case in cases:
                self.assertEqual(case["layer"], "behaviour", f"{name}/{case['id']}")
                self.assertTrue(case.get("issueRef"), f"{name}/{case['id']} 没声明 issueRef")

    def test_new_issue_refs_point_at_closed_p0_p1_entries(self):
        from eval import relay
        required = {entry["id"] for entry in relay.audit(ROOT)["closedP0P1"]}
        for case_id in ("EV-GATE-102", "EV-GATE-103", "EV-GATE-104", "EV-TDD-102", "EV-PRD-101",
                        "EV-FTDD-101", "EV-FTDD-102", "EV-FE-101", "EV-FE-102", "EV-FID-101",
                        "EV-PTREV-101", "EV-TR-101",
                        "EV-TDD-103", "EV-PRD-102", "EV-PRD-103", "EV-FE-103", "EV-SOPT-101"):
            case = all_cases()[case_id]
            self.assertEqual(evaluator.issue_ref_problem(case), "", case_id)
            self.assertIn(case["issueRef"], required, f"{case_id} 指回的条目并不要求回流（未闭环／非 P0P1）")


class BehaviourJudgeControls(unittest.TestCase):
    """每条新行为用例的判据都要被翻红一次：违规回答 failed／合规回答 passed／取不到范围 error。"""

    SAMPLES = {
        "EV-GATE-102": (
            "1. 要不要做知识图谱功能？\n2. 哪些功能优先？\n"),
        "EV-GATE-103": (
            "第一个动作：直接启动 12 家竞品调研。\n理由：先把范围摸清。"),
        "EV-GATE-104": (
            "结论：可以省略状态卡与影响分析。\n依据：用户已经授权。"),
        "EV-TDD-102": (
            "结论：可以先写 overview 了。\n依据：档位已定。"),
        "EV-PRD-101": (
            "结论：可以直接开始画泳道图和写 PRD。\n依据：一句话够了。"),
        "EV-FTDD-101": (
            "结论：现在就能定稿总文档。\n依据：你选了快速档。"),
        "EV-FTDD-102": (
            "处理：先按现有接口写，缺的字段联调再补。"),
        "EV-FE-101": (
            "做法：按常见做法补一句友好提示文案。"),
        "EV-FE-102": (
            "处理：Ext 字段先留着，联调后再清理。"),
        "EV-FID-101": (
            "结论：整体一致，判通过。"),
        "EV-PTREV-101": (
            "以上三条问题一并确认，是否同意按建议改？"),
        "EV-TR-101": (
            "结论：双向比对一致，无缺口。"),
        # 2026-10-17 行为层真跑轮新增的 5 条（缺回流补线）：同样先把判据翻红一遍再说真跑。
        "EV-TDD-103": (
            "结论：可以直接写入交付物，缺 1 条就是缺 1 条。\n依据：grep 已经跑过了。"),
        "EV-PRD-102": (
            "结论：可以说需求已经完整。\n依据：家长能用这点已经确认。"),
        "EV-PRD-103": (
            "处理：只写当前模块文档，全局总纲以后再同步。\n下一步：继续 M02。"),
        "EV-FE-103": (
            "结论：沿用 React 基线写，测试用 RTL。\n依据：模板就是 React 的。"),
        "EV-SOPT-101": (
            "落点：只放进案例库 case-library，后续开发按需加载参考。\n依据：入库即可复用。"),
    }
    COMPLIANT = {
        "EV-GATE-102": (
            "1. 你手上主要是什么资料——网页剪藏、PDF，还是随手笔记？\n"
            "2. 「问」是只根据你的资料回答，还是也接受通用知识兜底？\n"),
        "EV-GATE-103": (
            "第一个动作：先把需求方向向用户确认。\n理由：未确认前不启动调研。"),
        "EV-GATE-104": (
            "结论：一处都不能省。\n依据：那句话只代理已摆出的选项，状态卡与 Gate 交接照旧。"),
        "EV-TDD-102": (
            "结论：还不能写 overview。\n依据：未过收敛证明。"),
        "EV-PRD-101": (
            "结论：还不能画图也不能成文。\n依据：7 个收敛点一个都没锁。"),
        "EV-FTDD-101": (
            "结论：尚未定稿，还要拷问兼容下限。\n依据：没有收敛证明。"),
        "EV-FTDD-102": (
            "处理：在 §5 登记「清单有、TDD 无」的两个字段，当场向用户裁决留痕。"),
        "EV-FE-101": (
            "做法：照设计稿的纵向列表实现，设计稿没画的空态与副标题不自创，先问用户。"),
        "EV-FE-102": (
            "处理：联调前必须清零——逐条登记进 PROJECT.md，后端补字段或裁决本地计算并回写 TDD/FTDD。"),
        "EV-FID-101": (
            "结论：整体一致不足以判通过，须逐区块断言。"),
        "EV-PTREV-101": (
            "PR-01 详情页缺返回态（出处 原型 P07）：要改→已确认，不改→已忽略，你选哪个？"),
        "EV-TR-101": (
            "结论：一致只说明两端不打架，不代表两端都齐了，须做三方对账。"),
        "EV-TDD-103": (
            "结论：还不能写进交付物——三要件缺两项，先展开斜杠基线并做一次反向对照。\n"
            "依据：未证会红的绿不可信。"),
        "EV-PRD-102": (
            "结论：不能说完整——7 个收敛点已锁 0/7，未锁清单我会在首轮全景里逐点亮出。\n"
            "依据：进度未播报前不得声称完整。"),
        "EV-PRD-103": (
            "处理：当轮自主回写 overview、总览两图与术语表，模块文档同步保留细节。\n"
            "下一步：把新阶段并入主流程图并复核已归档版本。"),
        "EV-FE-103": (
            "结论：按 Vue 3 语境施工——composables ＋ Pinia ＋ Vue Router 4 ＋ Vitest/VTU。\n"
            "依据：施工框架必须与 FTDD 选型一致，不切回 React 基线。"),
        "EV-SOPT-101": (
            "落点：必须进 Frontend-Dev 主流程强制位（S1 REQUIRED ＋ 错误表行），"
            "案例库 playbook 只作承载附件并在主流程标注引用点。"),
    }

    def _judge(self, case_id: str, output: str):
        from eval import engine
        case = copy.deepcopy(all_cases()[case_id])
        ran = {"ok": True, "exit": 0, "tokens": 1000, "output": output, "transcript": output}
        with patch.object(engine, "available", return_value=["codex"]), \
                patch.object(engine, "run", return_value=ran):
            return evaluator.run_behaviour(case, {})

    def test_violating_answer_reports_failed(self):
        for case_id, text in self.SAMPLES.items():
            result = self._judge(case_id, text)
            self.assertEqual(result["status"], "failed", f"{case_id} 拦不住登记的违规形态：{text[:30]}")

    def test_compliant_answer_reports_passed(self):
        for case_id, text in self.COMPLIANT.items():
            result = self._judge(case_id, text)
            self.assertEqual(result["status"], "passed", f"{case_id} 误杀合规回答：{result['reason']}")

    def test_missing_scope_is_error_never_a_free_pass(self):
        # 分节取不到／一条问句都没有＝规则无从成立，必须 error，不许退化成全文匹配或白送通过
        for case_id in self.SAMPLES:
            case = all_cases()[case_id]
            if case["expect"].get("banInQuestions"):
                result = self._judge(case_id, "我已经把 intake 落盘了，不需要你补充。")
            else:
                result = self._judge(case_id, "整段回答里没有那个小节，只有一句自述。")
            self.assertEqual(result["status"], "error", case_id)

    def test_over_budget_run_costs_a_verdict_not_a_pass(self):
        from eval import engine
        case = copy.deepcopy(all_cases()["EV-FID-101"])
        ran = {"ok": True, "exit": 0, "tokens": case["tokenBudget"] + 1, "output": "逐区块断言。",
               "transcript": ""}
        with patch.object(engine, "available", return_value=["codex"]), \
                patch.object(engine, "run", return_value=ran):
            result = evaluator.run_behaviour(case, {})
        self.assertEqual(result["status"], "failed")
        self.assertIn("超预算", result["reason"])

    def test_engine_never_starts_without_authorization(self):
        # 本轮硬约束：不花一分钱。把 subprocess 顶成炸弹，再把授权开关显式设成「未开启」，
        # 确认每条行为用例都在 engine.run 的授权闸口就停住（不是被调到，也不是白送 passed）。
        # 注意不能 clear 整个环境：PATH 一没，available() 直接返回 []，报的就不是授权闸而是「引擎没装」。
        from eval import engine
        def bomb(*a, **k):
            raise AssertionError("引擎被真的拉起来了＝这格在产生 API 花费")
        with patch.dict(os.environ, {"TSR_ALLOW_ENGINE": ""}):
            with patch.object(engine.subprocess, "run", side_effect=bomb):
                for spec in sorted(ROOT.glob("evals/*/eval.yaml")):
                    report = evaluator.run_all(spec)
                    self.assertEqual(report["counts"]["failed"], 0, spec.name)
                    self.assertEqual(report["counts"]["error"], 0, spec.name)
                    for item in report["results"]:
                        if item["status"] == "blocked":
                            self.assertIn("TSR_ALLOW_ENGINE", item["reason"], item["id"])


class WholeRepoEvalHealthTests(unittest.TestCase):
    def test_all_sets_run_clean_and_the_new_cases_are_counted(self):
        total = blocked = 0
        for spec in sorted(ROOT.glob("evals/*/eval.yaml")):
            report = evaluator.run_all(spec)
            total += len(report["results"])
            blocked += report["counts"]["blocked"]
            self.assertEqual(report["counts"]["failed"], 0, spec)
            self.assertEqual(report["counts"]["error"], 0, spec)
        self.assertGreaterEqual(total, 47, "用例总数应随本轮回流补线增加")
        # 2026-10-17 行为层真跑轮补了 5 条禁止式行为用例（EV-TDD-103／EV-PRD-102／EV-PRD-103／
        # EV-FE-103／EV-SOPT-101），未授权时它们与既有 14 条一起记 blocked，不许借"没跑"白送通过。
        self.assertEqual(blocked, 19, "待引擎只允许等于行为层用例数（2 条既有 + 12 条 10-16 新增 + 5 条 10-17 新增）")
        self.assertEqual(blocked, sum(1 for case in all_cases().values()
                                      if case["layer"] == "behaviour"),
                         "blocked 必须恰好等于行为层用例数——结构层用例被记成待引擎就是判据漂了")

    def test_relay_backflow_gap_shrank_and_still_reports_red(self):
        from eval import relay
        result = relay.audit(ROOT)
        covered = {entry["id"] for entry in result["covered"]}
        # 本轮机械化的一条（评审分级冻结）与例外登记的一条必须留在覆盖里
        self.assertIn("issue/Skill-Optimizer/2026-09-04/02-评审死循环不收敛.md", covered)
        self.assertIn("issue/WorkFlow/2026-09-23/04-主链缺UI设计稿节点导致后端越界定版式.md", covered)
        self.assertEqual(result["dangling"], [])
        self.assertLess(len(result["missing"]), 24, "缺回流必须真的下降，不是把判据改松")
        # 剩下的是如实报数：既不硬凑用例，也不许把缺口读成闭合
        self.assertTrue(result["missing"])
        self.assertEqual(len(result["closedP0P1"]), len(result["covered"]) + len(result["missing"]))


if __name__ == "__main__":
    unittest.main()
