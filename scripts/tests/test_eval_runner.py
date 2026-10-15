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
    def test_all_declared_cases_pass(self):
        report = evaluator.run_all(SPEC)
        blocked = [item for item in report["results"] if item["status"] == "blocked"]
        bad = [item for item in report["results"] if item["status"] in {"failed", "error"}]
        self.assertEqual(bad, [])
        self.assertEqual(len(blocked), 1, "行为层用例必须显式 blocked，不允许静默跳过")

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


if __name__ == "__main__":
    unittest.main()
