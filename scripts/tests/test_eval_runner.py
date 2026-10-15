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


if __name__ == "__main__":
    unittest.main()
