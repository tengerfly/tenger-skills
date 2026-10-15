import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eval import run as evaluator

SPEC = Path(__file__).resolve().parents[2] / "evals/gate/eval.yaml"


def case(case_id):
    spec = evaluator.load_eval(SPEC)
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


if __name__ == "__main__":
    unittest.main()
