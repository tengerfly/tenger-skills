"""D5 must not be able to dress "never measured" up as "no problem".

These are reverse-control tests: each one forges the exact report shape that would fool a
naive scorer (one passing case, an all-blocked run, a missing file, no cost metering) and
asserts the reading stays countable and the N/A reason stays distinguishable. Written against
`score.d5_behaviour`, which only ever reads the derived report — no engine, no spend, and no
TSR_ALLOW_ENGINE anywhere in this file.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from obs import score

REPORT = ".spec/obs/eval-report.json"


def behaviour(case_id, status, **extra):
    """A behaviour-layer record as run.py writes it: no `outcome`, engine fields instead."""
    item = {"id": case_id, "status": status, "reason": extra.pop("reason", "")}
    item.update(extra)
    return item


def structure(case_id, status="passed"):
    """A structure-layer record: run.py always stamps these with outcome green/red."""
    return {"id": case_id, "status": status, "outcome": "red" if status == "failed" else "green",
            "findings": [], "reason": ""}


def report_of(*results):
    return [{"skill": "workflow", "eval": "evals/gate/eval.yaml", "counts": {},
             "results": list(results), "green": False}]


class D5BehaviourTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def write_report(self, *results):
        target = self.root / REPORT
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report_of(*results), ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    # ① 一条行为层 passed ⇒ 不再 N/A，但读数必须如实说"只有 1 条"
    def test_one_passed_behaviour_case_unblocks_d5_without_claiming_quality(self):
        self.write_report(structure("EV-GATE-001"),
                          behaviour("EV-GATE-101", "passed", tokens=32357,
                                    evidence=".spec/obs/behaviour/EV-GATE-101.log"))
        result = score.d5_behaviour(self.root)
        self.assertIsNotNone(result["value"])
        self.assertIn("1/1", result["detail"])
        self.assertIn("过 1｜败 0", result["detail"])
        # n=1 不得被读成"质量合格"：样本不足标注必须在读数里
        self.assertIn("样本 n=1", result["detail"])
        self.assertIn("覆盖率", result["detail"])
        self.assertNotIn("通过，质量", result["detail"])

    def test_structure_results_never_count_as_behaviour_evidence(self):
        self.write_report(structure("EV-GATE-001"), structure("EV-GATE-002", "failed"),
                          behaviour("EV-GATE-101", "passed", tokens=32357))
        result = score.d5_behaviour(self.root)
        self.assertEqual(result["value"], 100.0)
        self.assertIn("1/1 条实跑且通过", result["detail"])

    # ② 报告里全是 blocked ⇒ 仍 N/A，原因必须是"未实跑"
    def test_all_blocked_report_stays_na_and_says_never_ran(self):
        self.write_report(structure("EV-GATE-001"),
                          behaviour("EV-GATE-101", "blocked", reason="引擎未授权（需 TSR_ALLOW_ENGINE=1）"),
                          behaviour("EV-TDD-101", "blocked", reason="引擎未授权（需 TSR_ALLOW_ENGINE=1）"))
        result = score.d5_behaviour(self.root)
        self.assertIsNone(result["value"])
        self.assertIn("全部未实跑", result["detail"])
        self.assertIn("blocked 2", result["detail"])
        self.assertIn("不算通过", result["detail"])
        # 未授权的理由还要能在扣分点里被追责到具体用例
        self.assertTrue(any("EV-GATE-101" in line for line in result["failures"]))

    def test_error_and_blocked_cannot_borrow_a_pass(self):
        """一条 passed + 一条 blocked + 一条 error：error/blocked 进分母、不进分子。"""
        self.write_report(behaviour("EV-GATE-101", "passed", tokens=32357),
                          behaviour("EV-TDD-101", "blocked", reason="引擎本机不可用"),
                          behaviour("EV-Q-101", "error", reason="引擎未回报 token 用量，预算闸无法生效"))
        result = score.d5_behaviour(self.root)
        self.assertEqual(result["value"], 100.0 / 3)
        self.assertIn("1/3", result["detail"])
        self.assertIn("未实跑 2", result["detail"])

    def test_failed_behaviour_run_costs_coverage_not_a_pass(self):
        self.write_report(behaviour("EV-GATE-101", "failed", tokens=58691, reason="超预算"))
        result = score.d5_behaviour(self.root)
        self.assertEqual(result["value"], 0.0)
        self.assertIn("过 0｜败 1", result["detail"])
        self.assertIn("超预算", result["failures"][0])

    def test_report_without_any_behaviour_layer_is_na_as_behaviour_unmeasured(self):
        """有文件但只有结构层 ⇒ N/A，原因要说清是行为层没跑。"""
        self.write_report(structure("EV-GATE-001"), structure("EV-GATE-002"))
        result = score.d5_behaviour(self.root)
        self.assertIsNone(result["value"])
        self.assertIn("没有任何行为层结果", result["detail"])

    # ③ 报告文件不存在 ⇒ N/A，且原因必须与②不同
    def test_missing_report_is_na_for_a_different_reason_than_unrun(self):
        blocked = self.write_report(behaviour("EV-GATE-101", "blocked", reason="引擎未授权"))
        unrun = score.d5_behaviour(self.root)["detail"]
        blocked.unlink()
        missing = score.d5_behaviour(self.root)
        self.assertIsNone(missing["value"])
        self.assertIn("不存在", missing["detail"])
        self.assertNotEqual(missing["detail"], unrun)

    def test_unreadable_report_names_the_failure_instead_of_looking_clean(self):
        target = self.write_report(behaviour("EV-GATE-101", "passed", tokens=1))
        target.write_text("{这不是 JSON", encoding="utf-8")
        result = score.d5_behaviour(self.root)
        self.assertIsNone(result["value"])
        self.assertIn("读不动", result["detail"])

    def test_changed_report_shape_is_announced_not_relabelled_as_unmeasured(self):
        """读不懂 ≠ 没跑：落盘口径变了必须说口径变了。"""
        target = self.write_report(behaviour("EV-GATE-101", "passed", tokens=1))
        target.write_text(json.dumps({"results": []}), encoding="utf-8")
        result = score.d5_behaviour(self.root)
        self.assertIsNone(result["value"])
        self.assertIn("口径已变", result["detail"])

    # ④ 删掉 token 字段 ⇒ 成本读数 N/A，不得显示 0 或估算值
    def test_absent_token_field_makes_cost_na_never_zero_or_estimated(self):
        self.write_report(behaviour("EV-GATE-101", "passed", evidence=".spec/obs/behaviour/x.log",
                                    reason="引擎 codex"))
        result = score.d5_behaviour(self.root)
        self.assertIsNotNone(result["value"])
        self.assertIn("成本 N/A", result["detail"])
        self.assertNotIn("token 合计", result["detail"])
        self.assertNotIn("字节", result["detail"])

    def test_zero_tokens_from_the_host_are_not_a_measurement(self):
        """宿主实测 token 字段全为 0 的先例：0 一律按"未计量"处理，不得冒充成本。"""
        self.write_report(behaviour("EV-GATE-101", "passed", tokens=0))
        self.assertIn("成本 N/A", score.d5_behaviour(self.root)["detail"])

    def test_reported_tokens_are_shown_as_measured_cost(self):
        self.write_report(behaviour("EV-GATE-101", "passed", tokens=32357),
                          behaviour("EV-TDD-101", "passed", tokens=58691))
        detail = score.d5_behaviour(self.root)["detail"]
        self.assertIn("token 合计 91,048", detail)
        self.assertIn("2/2 条有计量", detail)

    def test_d5_is_wired_into_the_board_with_its_reason(self):
        self.write_report(behaviour("EV-GATE-101", "blocked", reason="引擎未授权"))
        result = score.score_project(self.root)
        self.assertEqual(result["dimensions"]["D5"]["value"], None)
        self.assertNotIn("D5", result["scored"])
        row = next(line for line in score.render(result).splitlines() if line.startswith("| D5 |"))
        self.assertIn("全部未实跑", row)
        self.assertIn(" N/A ", row)


if __name__ == "__main__":
    unittest.main()
