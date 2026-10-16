import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eval import run as evaluator

SPEC = Path(__file__).resolve().parents[2] / "evals/gate/eval.yaml"
WF_SPEC = Path(__file__).resolve().parents[2] / "evals/workflow-graph/eval.yaml"


def case(case_id):
    spec = evaluator.load_eval(SPEC)
    return next(item for item in spec["cases"] if item["id"] == case_id)


def wf_case(case_id):
    spec = evaluator.load_eval(WF_SPEC)
    return next(item for item in spec["cases"] if item["id"] == case_id)


class EvalRunnerTests(unittest.TestCase):
    def test_behaviour_cases_stay_blocked_without_engine_authorization(self):
        # 单测绝不允许真跑引擎：跑测试就烧钱、耗分钟、还拿不确定结果当回归结论
        report = evaluator.run_all(SPEC)
        blocked = [item for item in report["results"] if item["status"] == "blocked"]
        bad = [item for item in report["results"] if item["status"] in {"failed", "error"}]
        self.assertEqual(bad, [])
        self.assertGreaterEqual(len(blocked), 1, "行为层用例在未授权时必须显式 blocked")
        self.assertTrue(all("TSR_ALLOW_ENGINE" in item["reason"] for item in blocked))

    def test_wrong_expectation_fails_rather_than_passing_vacuously(self):
        drifted = copy.deepcopy(case("EV-GATE-002"))
        drifted["expect"]["outcome"] = "green"
        self.assertEqual(evaluator.run_case(drifted)["status"], "failed")

    def test_absent_finding_text_cannot_borrow_an_unrelated_failure(self):
        weak = copy.deepcopy(case("EV-GATE-005"))
        weak["expect"]["mustContain"] = "这段判据文本不存在"
        self.assertEqual(evaluator.run_case(weak)["status"], "failed")

    def test_missing_fixture_is_error_not_pass(self):
        broken = copy.deepcopy(case("EV-GATE-001"))
        broken["given"] = "evals/gate/fixtures/does-not-exist"
        self.assertEqual(evaluator.run_case(broken)["status"], "error")

    def test_tamper_target_must_exist_rather_than_silently_green(self):
        broken = copy.deepcopy(case("EV-GATE-002"))
        broken["tamper"]["file"] = ".spec/prd/ghost.md"
        result = evaluator.run_case(broken)
        self.assertEqual(result["status"], "error")
        self.assertIn("tamper target missing", result["reason"])

    def test_non_yaml_markdown_in_eval_set_is_reported_with_the_file_name(self):
        with self.assertRaises(ValueError) as caught:
            evaluator.load_eval(Path(__file__).resolve())
        self.assertIn(str(Path(__file__).name), str(caught.exception))


class SectionScopeTests(unittest.TestCase):
    """禁词判据必须限定在规则所辖的那一节，否则否定句会被误判成违规。"""

    COMPLIANT = ("# 答复\n"
                 "## 已登记为研究问题\n数据形态与来源、向量库选型、语言与框架留到 Tech Design。\n"
                 "## 待你决定（只有你能回答的三件事）\n1. 存什么：你手上主要是什么资料？\n")
    VIOLATION = "## 待你决定\n1. 用什么数据库？\n"

    def test_deferral_language_is_not_a_violation(self):
        body = evaluator._section_body(self.COMPLIANT, "待你决定")
        self.assertNotIn("向量库", body)
        self.assertNotIn("框架", body)

    def test_real_violation_still_matches(self):
        self.assertRegex(evaluator._section_body(self.VIOLATION, "待你决定"), "数据库")

    def test_missing_section_returns_none_so_the_case_cannot_silently_pass(self):
        self.assertIsNone(evaluator._section_body(self.COMPLIANT, "根本不存在的节"))


class StatusCardSectionTests(unittest.TestCase):
    """2026-10-15 真跑 codex 的 GATE 回答用的是状态卡标签行（待你决定：① …），不是 markdown 标题。
    只认标题会让一条合规回答被判成"节缺失"，判据必须认它实际长什么样。"""

    STATUS_CARD = (
        "## 结论先行\n\n"
        "```text\n"
        "状态卡\n"
        "待你决定：① 需求方向是否符合你本意 ② 三个只有你能回答的问题\n"
        "本步产物与证据：intake 草稿见下\n"
        "下一步：确认方向后再决定要不要开一轮调研\n"
        "```\n"
    )

    def test_label_line_section_is_found_without_eating_later_labels(self):
        body = evaluator._section_body(self.STATUS_CARD, "待你决定|需要你回答")
        self.assertIsNotNone(body)
        self.assertIn("需求方向", body)
        self.assertNotIn("本步产物与证据", body)
        self.assertNotIn("向量库", body)

    def test_label_line_section_still_catches_a_real_violation(self):
        text = self.STATUS_CARD.replace("① 需求方向是否符合你本意", "① 数据库选 Postgres 还是向量库")
        self.assertRegex(evaluator._section_body(text, "待你决定"), "Postgres|向量库")


class EngineTranscriptTests(unittest.TestCase):
    """判据只能吃模型自己的回答：transcript 里含注入的 SKILL.md 原文和 GBK 乱码工具回显，
    全文匹配既会误杀技能自己的条款，也会因乱码漏判。"""

    def test_agent_messages_pick_replies_and_drop_tool_echoes(self):
        from eval import engine
        stream = "\n".join([
            '{"type":"item.completed","item":{"type":"agent_message","text":"待你决定：① 方向对不对"}}',
            '{"type":"item.completed","item":{"type":"command_output",'
            '"text":"数据库 技术选型 向量库 —— 这是工具回显，不该进判据"}}',
        ])
        self.assertEqual(["待你决定：① 方向对不对"], engine._agent_messages(stream))

    def test_non_jsonl_stream_yields_no_answers_so_judging_refuses_to_degrade(self):
        from eval import engine
        self.assertEqual([], engine._agent_messages("prose with no jsonl events at all"))


class CostMeteringTests(unittest.TestCase):
    """2026-10-15 实测：codex --json 不再打印 "tokens used"，成本退回 None，
    而 `if budget and tokens and tokens > budget` 会静默跳过预算闸 —— 无计量的"通过"不算数。"""

    def test_usage_tokens_excludes_cached_input(self):
        from eval import engine
        line = ('{"type":"turn.completed","usage":{"input_tokens":1637521,'
                '"cached_input_tokens":1570432,"output_tokens":39236}}')
        self.assertEqual((106325, 1570432), engine.usage_tokens(line))

    def test_missing_usage_reported_as_absent_not_zero(self):
        from eval import engine
        self.assertEqual((None, None), engine.usage_tokens('{"type":"turn.started"}'))


class QuestionScopeJudgingTests(unittest.TestCase):
    """判据范围=问句行。形状取自 2026-10-15 两次真跑的同一条用例（一次状态卡、一次编号清单），
    引擎用 stub 顶掉：单测不许花钱，但判据分支必须真的走一遍。"""

    BANNED = "数据库|用什么框架|技术选型|选 React|Postgres|Elasticsearch|语言是|向量库"
    STATUS_CARD = ("状态卡\n待你决定：① 需求方向是否符合你本意 ② 三个只有你能回答的问题\n"
                   "下一步：确认方向后再定\n"
                   "1. 你打算往里放什么——网页剪藏、PDF，还是随手笔记？\n"
                   "语言、框架、数据库这类技术选型留到 Tech Design 节点，现在我不问。\n")
    NUMBERED = ("先登记需求。下面三件只有你能答：\n"
                "1. 库的边界：只放自己写的笔记，还是也收网页剪藏？\n"
                "2. 「问」的边界：只根据你的资料回答并给出处，还是也接受通用知识兜底？\n"
                "本步不碰技术方案，语言、数据库都不在这一阶段问。\n")

    def _judge(self, output):
        from unittest.mock import patch
        from eval import engine
        case = {"id": "EV-Q", "layer": "behaviour", "engine": "codex",
                "given": "evals/gate/fixtures/ledger-clean", "skillFiles": [],
                "prompt": "p", "tokenBudget": 999999,
                "expect": {"banInQuestions": True, "mustNotContain": self.BANNED}}
        ran = {"ok": True, "exit": 0, "tokens": 1000, "output": output, "transcript": output}
        with patch.object(engine, "available", return_value=["codex"]), patch.object(engine, "run", return_value=ran):
            return evaluator.run_behaviour(case, {})

    def test_both_real_answer_forms_pass_without_misjudging_the_deferral(self):
        for text in (self.STATUS_CARD, self.NUMBERED):
            result = self._judge(text)
            self.assertEqual("passed", result["status"], result["reason"])
            self.assertIn("问句", result["reason"])

    def test_technical_question_asked_to_user_is_a_real_violation(self):
        self.assertEqual("failed", self._judge("1. 数据库用 Postgres 还是向量库？")["status"])

    def test_zero_questions_is_error_not_a_free_pass(self):
        # 一条问句都没有＝规则无从成立，记 error 逼人回看，不给"绿"
        self.assertEqual("error", self._judge("我已经把 intake 落盘了，无需你补充。")["status"])


class WorkflowGraphEvalTests(unittest.TestCase):
    """§4.3 第 3 条「故意让 skill 跳步 → 评测必须失败」的反向对照。

    check_transitions / check_graph 接进 CHECKS 只是把判据入口打开；入口本身也会腐烂——
    夹具被改写、tamper 落不到字、期望值被人调绿，都会让一条"红用例"退化成假通过。
    所以这里先把量具测红一遍，才允许它去测别人。判据来自 validate_core 的真实实现：
    这两个校验器读 <project>/governance/{state,artifact,skill,workflow}-registry.yaml。
    """

    RED_CASES = ("EV-WF-003", "EV-WF-004", "EV-WF-005", "EV-WF-006")

    def test_transition_and_graph_are_wired_into_the_judge(self):
        # 判据入口没接进 CHECKS 时，eval.yaml 里的 validator 会在 findings_for 抛 unknown validator
        self.assertIn("transition", evaluator.CHECKS)
        self.assertIn("graph", evaluator.CHECKS)

    def test_whole_set_is_green_and_costs_no_engine(self):
        report = evaluator.run_all(WF_SPEC)
        self.assertEqual(report["counts"]["failed"], 0)
        self.assertEqual(report["counts"]["error"], 0)
        self.assertEqual(report["counts"]["blocked"], 0, "本套全是结构层，不该出现待引擎用例")
        self.assertTrue(report["green"])

    def test_red_case_flipped_to_green_reports_failed(self):
        # 期望从 red 改成 green 必须报 failed，否则"跳步判据"其实一直没在执法
        for case_id in self.RED_CASES:
            drifted = copy.deepcopy(wf_case(case_id))
            self.assertEqual(drifted["expect"]["outcome"], "red")
            drifted["expect"]["outcome"] = "green"
            result = evaluator.run_case(drifted)
            self.assertEqual(result["status"], "failed", f"{case_id} 的 red 期望可以随便调绿")

    def test_clean_fixture_broken_while_still_expected_green_reports_failed(self):
        # 合规夹具被改坏后仍期望 green，必须报 failed（判绿用例不是"跑不出异常"的另一种写法）
        broken = copy.deepcopy(wf_case("EV-WF-001"))
        broken["tamper"] = copy.deepcopy(wf_case("EV-WF-003")["tamper"])
        result = evaluator.run_case(broken)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["outcome"], "red")

    def test_absent_finding_text_cannot_borrow_an_unrelated_failure(self):
        # 只看红/绿会把"因无关原因失败"当成回归通过：判据文本必须真的命中
        for case_id in self.RED_CASES:
            weak = copy.deepcopy(wf_case(case_id))
            weak["expect"]["mustContain"] = "这段判据文本不存在"
            self.assertEqual(evaluator.run_case(weak)["status"], "failed",
                             f"{case_id} 去掉 mustContain 后仍可借别的错通过")

    def test_missing_fixture_is_error_not_green(self):
        broken = copy.deepcopy(wf_case("EV-WF-002"))
        broken["given"] = "evals/workflow-graph/fixtures/does-not-exist"
        self.assertEqual(evaluator.run_case(broken)["status"], "error")

    def test_missing_tamper_target_is_error_not_silent_red(self):
        broken = copy.deepcopy(wf_case("EV-WF-004"))
        broken["tamper"]["file"] = "governance/ghost-registry.yaml"
        result = evaluator.run_case(broken)
        self.assertEqual(result["status"], "error")
        self.assertIn("tamper target missing", result["reason"])

    def test_tamper_that_no_longer_bites_is_error_not_pass(self):
        # 夹具被重写导致 tamper 找不到原文时，必须炸出来；静默改不动＝红用例悄悄变绿
        drifted = copy.deepcopy(wf_case("EV-WF-005"))
        drifted["tamper"]["replace"]["from"] = "to: A_STATE_NOT_IN_THIS_FILE"
        result = evaluator.run_case(drifted)
        self.assertEqual(result["status"], "error")
        self.assertIn("tamper 'from' not found", result["reason"])


if __name__ == "__main__":
    unittest.main()
