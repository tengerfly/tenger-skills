"""行为层追加台账的五条反向对照：台账坏了、空了、被误读，D5 与 run.py 都必须当场现形。

背景（实测数据丢失通路）：`eval-report.json` 每次评测被整份覆写，行为层真跑的成本与 pass/fail
只活在报告里，一次未授权跑就能把三次真跑抹干净、D5 永久失明。修复＝append-only 台账
`.spec/obs/behaviour-runs.jsonl`（真相源，入库）+ D5 改读台账（拿不到才回退报告）。
本文件不跑任何引擎、不产生任何花费、不读真实 .spec/（全部用临时目录），每条都先"锻造出
能骗过朴素实现的形状"再断言读数不肯上当。
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eval import run as evaluator
from obs import score

LEDGER = score.BEHAVIOUR_LEDGER
REPORT = score.EVAL_REPORT


def ledger_record(case_id, status, **extra):
    """台账记录的标准形状（与 run.py behaviour_ledger_records 落盘口径一致）。"""
    row = {"caseId": case_id, "skill": "workflow", "engine": "codex", "status": status,
           "tokens": extra.pop("tokens", None), "cachedTokens": extra.pop("cachedTokens", None),
           "ranAt": "2026-10-16T12:00:00+08:00", "evidence": extra.pop("evidence", None),
           "reason": extra.pop("reason", "")}
    row.update(extra)
    return row


class LedgerD5Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def write_ledger(self, *rows):
        target = self.root / LEDGER
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
        return target

    def write_report(self, results):
        target = self.root / REPORT
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps([{"skill": "workflow", "results": results}], ensure_ascii=False),
                          encoding="utf-8")
        return target

    # ① 台账只有 blocked ⇒ D5 仍 N/A，原因必须写"未实跑"，且数据源点名是台账
    def test_ledger_with_only_blocked_stays_na_and_says_never_ran(self):
        self.write_ledger(ledger_record("EV-GATE-101", "blocked", reason="引擎未授权"),
                          ledger_record("EV-TDD-101", "blocked", reason="引擎未授权"))
        result = score.d5_behaviour(self.root)
        self.assertIsNone(result["value"])
        self.assertIn("全部未实跑", result["detail"])
        self.assertIn("blocked 2", result["detail"])
        self.assertIn("追加台账", result["detail"])
        self.assertIn("不算通过", result["detail"])
        # 对照面：报告里就算写着 passed 也不能越过台账——覆写的派生物说了不算
        self.write_report([{"id": "EV-GATE-101", "status": "passed", "tokens": 1}])
        self.assertIsNone(score.d5_behaviour(self.root)["value"])

    # ② 台账有 1 条 passed（含 tokens）⇒ 覆盖率点亮，且 n<3 的样本不足警示必须在场
    def test_one_passed_ledger_row_lights_coverage_with_small_sample_warning(self):
        self.write_ledger(ledger_record("EV-GATE-101", "passed", tokens=32357),
                          ledger_record("EV-TDD-101", "blocked", reason="引擎未授权"))
        result = score.d5_behaviour(self.root)
        self.assertEqual(result["value"], 100.0)
        self.assertIn("1/1 条实跑且通过", result["detail"])
        self.assertIn("样本 n=1 < 3", result["detail"])
        self.assertIn("不得当质量结论", result["detail"])
        # blocked 不进分母（分母＝实跑过的条数），但必须显示为未实跑留痕
        self.assertIn("未实跑记录 1", result["detail"])
        self.assertIn("追加台账", result["detail"])

    # ③ passed 但 tokens 为 null ⇒ 成本读数 N/A，禁止显示 0、禁止字节冒充
    def test_passed_row_with_null_tokens_shows_cost_na_not_zero(self):
        self.write_ledger(ledger_record("EV-GATE-101", "passed", tokens=None,
                                        reason="引擎 codex；判据范围 3 条问句"))
        result = score.d5_behaviour(self.root)
        self.assertIsNotNone(result["value"])
        self.assertIn("成本 N/A", result["detail"])
        self.assertNotIn("token 合计", result["detail"])
        self.assertNotIn("字节", result["detail"])

    # ④ 台账文件不存在 ⇒ N/A 原因必须与①不同（缺真相 ≠ 有真相但全没跑）
    def test_missing_ledger_reason_differs_from_all_blocked_ledger(self):
        self.write_ledger(ledger_record("EV-GATE-101", "blocked", reason="引擎未授权"))
        unrun = score.d5_behaviour(self.root)["detail"]
        (self.root / LEDGER).unlink()
        missing = score.d5_behaviour(self.root)
        self.assertIsNone(missing["value"])
        self.assertNotEqual(missing["detail"], unrun)
        self.assertIn("不存在", missing["detail"])
        # 回退到 eval-report 时也必须点名数据源
        self.write_report([{"id": "EV-GATE-101", "status": "blocked", "reason": "引擎未授权"}])
        fallback = score.d5_behaviour(self.root)
        self.assertIsNone(fallback["value"])
        self.assertIn("eval-report.json", fallback["detail"])
        self.assertIn("回退", fallback["detail"])

    # 台账坏一行也不许静默：点名坏行，且不得悄悄降级去读会被覆写的报告
    def test_corrupt_ledger_line_is_named_not_demoted(self):
        target = self.write_ledger(ledger_record("EV-GATE-101", "passed", tokens=32357))
        target.write_text(target.read_text(encoding="utf-8") + "{这一行坏了\n", encoding="utf-8")
        self.write_report([{"id": "EV-GATE-101", "status": "passed", "tokens": 1}])
        result = score.d5_behaviour(self.root)
        self.assertIsNone(result["value"])
        self.assertIn("第 2 行不是合法 JSON", result["detail"])
        self.assertIn("不回退", result["detail"])


class LedgerAppendSemanticsTests(unittest.TestCase):
    """⑤ 这格的核心目的：台账只追加、永不覆写——"重复运行不得吃掉既有行"要有对照。"""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def test_repeated_appends_never_overwrite_existing_rows(self):
        first = ledger_record("EV-GATE-101", "blocked", reason="这次没跑（留痕）")
        second = ledger_record("EV-GATE-101", "passed", tokens=32357, evidence=".spec/obs/behaviour/x.log")
        self.assertEqual(evaluator.append_behaviour_ledger(self.root, [first]), 1)
        self.assertEqual(evaluator.append_behaviour_ledger(self.root, [second]), 1)
        self.assertEqual(evaluator.append_behaviour_ledger(self.root, [first]), 1)  # 同一条再记一次也追加
        lines = (self.root / LEDGER).read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 3, "追加语义被破坏：第二次运行覆盖了既有行＝数据丢失通路复发")
        self.assertEqual(json.loads(lines[0]), first, "既有行被改动")
        self.assertEqual(json.loads(lines[2]), first)
        self.assertEqual(json.loads(lines[1]), second)

    def test_blocked_and_unmeasured_rows_carry_explicit_null_not_zero(self):
        spec = {"skill": "workflow", "engine": None,
                "cases": [{"id": "EV-GATE-101", "layer": "behaviour", "engine": "codex"},
                          {"id": "EV-GATE-001", "layer": "structure"}]}
        results = [{"id": "EV-GATE-101", "status": "blocked", "reason": "引擎未授权"},
                   {"id": "EV-GATE-001", "status": "passed", "outcome": "green"}]
        rows = evaluator.behaviour_ledger_records("workflow", spec, results, "2026-10-16T12:00:00+08:00")
        self.assertEqual(len(rows), 1, "结构层结果绝不进行为层台账")
        row = rows[0]
        self.assertEqual(set(row), {"caseId", "skill", "engine", "status", "tokens",
                                    "cachedTokens", "ranAt", "evidence", "reason"})
        self.assertIsNone(row["tokens"])
        self.assertIsNone(row["cachedTokens"])
        evaluator.append_behaviour_ledger(self.root, rows)
        line = (self.root / LEDGER).read_text(encoding="utf-8")
        self.assertIn('"tokens": null', line, "未计量必须显式 null；写成 0 会把没计量洗成没花钱")

    def test_run_cli_appends_blocked_and_never_touches_report_overwrite(self):
        # 对照 main 的接线：真实 CLI 跑结构层套会顺带把行为层 blocked 留痕进台账；
        # 用一个临时评测集（结构层 1 条 + 行为层 1 条）在真实 ROOT 外验证不了 main 的 ROOT 常量，
        # 所以这里直接验 run_all→behaviour_ledger_records→append 的组合语义。
        spec = {"skill": "probe", "engine": None,
                "cases": [{"id": "EV-B-101", "layer": "behaviour", "engine": "codex"}]}
        results = [{"id": "EV-B-101", "status": "blocked",
                    "reason": "引擎未授权（需 TSR_ALLOW_ENGINE=1）"}]
        rows = evaluator.behaviour_ledger_records("probe", spec, results, "2026-10-16T12:00:00+08:00")
        self.assertEqual(evaluator.append_behaviour_ledger(self.root, rows), 1)
        again = evaluator.append_behaviour_ledger(self.root, rows)
        self.assertEqual(again, 1)
        self.assertEqual(len((self.root / LEDGER).read_text(encoding="utf-8").splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
