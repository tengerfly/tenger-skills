"""基线快照与 diff 的对照组：锚不一致必须拒绝比较、量具腐烂必须报回退。

`governance/eval-spec.yaml` comparability 要求把结果钉在 `skillRevision / casesVersion / engine /
model / judgeVersion / scoringVersion` 上，「锚任一项变化即开新基线，禁止跨锚比总分」——历史上跨锚
比过一次，结论当场作废。这条纪律此前同样只是纸面：没有快照文件、没有 save、没有 diff。
这里每条都要先红一遍：③ 锚不一致必须拒绝比较（不许静默给 diff）；④ 期望从 red 改成 green 必须报
failed，而且判据腐烂（红用例悄悄变绿）必须被 diff 报成回退，不能报成「与基线一致」。
"""
from __future__ import annotations
import copy, io, json, sys, tempfile, unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eval import baseline
from eval import run as evaluator

ROOT = Path(__file__).resolve().parents[2]

PROBE_YAML = """schema: tenger.eval/v1
skill: workflow
cases:
  - id: EV-P-001
    name: 合规状态机判绿
    layer: structure
    given: evals/workflow-graph/fixtures/graph-clean
    expect: {validator: transition, outcome: green}
  - id: EV-P-002
    name: 技术方案未评审就进开发必须判红
    layer: structure
    given: evals/workflow-graph/fixtures/graph-clean
    tamper:
      file: governance/state-registry.yaml
      replace: {from: "requiredArtifacts: [tech-design]", to: "requiredArtifacts: []"}
    expect: {validator: transition, outcome: red, mustContain: entering DEV_IN_PROGRESS must require tech-design}
"""


def rotted_checker(project):
    """模拟"量具腐烂"：判据实现再也不报任何东西，红用例于是悄悄变绿。"""
    return []


class ProbeSetMixin(unittest.TestCase):
    def probe(self, body: str = PROBE_YAML):
        """把探针评测集放在临时目录：基线文件也落在这里，测试绝不写 evals/ 真目录。"""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        spec = Path(tmp.name) / "evals" / "probe" / "eval.yaml"
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_text(body, encoding="utf-8")
        return spec


class AnchorTests(ProbeSetMixin):
    def test_anchors_are_exactly_the_names_governance_binds(self):
        # 锚清单由 governance 定；代码里少一个名字或多一个名字都必须当场红
        bound = yaml.safe_load((ROOT / "governance/eval-spec.yaml").read_text(encoding="utf-8"))["comparability"]["bind"]
        scoring = yaml.safe_load((ROOT / "governance/scoring.yaml").read_text(encoding="utf-8"))["comparability"]["bind"]
        self.assertEqual(list(baseline.ANCHOR_NAMES), bound)
        self.assertEqual(list(baseline.ANCHOR_NAMES), scoring)

    def test_snapshot_carries_every_anchor_and_never_runs_the_engine(self):
        snap = baseline.snapshot(self.probe())
        self.assertEqual(sorted(snap["anchors"]), sorted(baseline.ANCHOR_NAMES))
        self.assertTrue(all(str(value) for value in snap["anchors"].values()), snap["anchors"])
        self.assertEqual(snap["counts"]["error"], 0)
        self.assertEqual(snap["counts"]["blocked"], 0, "探针套全是结构层，出现待引擎用例＝引擎被拉起来了")
        self.assertEqual(snap["counts"]["passed"], 2)

    def test_case_name_edit_does_not_move_the_anchor_but_a_declared_ref_does(self):
        base = baseline.snapshot(self.probe())
        renamed = PROBE_YAML.replace("name: 合规状态机判绿", "name: 改个说法而已")
        self.assertEqual(baseline.snapshot(self.probe(renamed))["anchors"]["casesVersion"],
                         base["anchors"]["casesVersion"], "改标题不等于换尺子")
        wired = PROBE_YAML.replace("outcome: green}", "outcome: green}\n    issueRef: issue/WorkFlow/2026-10-10/02")
        self.assertNotEqual(baseline.snapshot(self.probe(wired))["anchors"]["casesVersion"],
                            base["anchors"]["casesVersion"], "L2 接线进了用例声明就必须开新基线")

    def test_statement_declares_the_caliber_it_compares_under(self):
        text = "\n".join(baseline.statement(baseline.snapshot(self.probe())))
        for marker in ("口径声明", "禁止跨锚比总分", "TSR_ALLOW_ENGINE", ".spec/obs/"):
            self.assertIn(marker, text)


class DiffControlTests(ProbeSetMixin):
    def test_flipping_the_red_expectation_to_green_fails_the_case(self):
        # ④ 期望从 red 改成 green 必须报 failed（基线机制建立在"这条红是被真判出来的"之上）
        drifted = copy.deepcopy(evaluator.load_eval(self.probe())["cases"][1])
        drifted["expect"]["outcome"] = "green"
        self.assertEqual(evaluator.run_case(drifted)["status"], "failed")

    def test_rotted_judge_is_reported_as_a_regression_not_as_a_clean_diff(self):
        spec = self.probe()
        base = baseline.snapshot(spec)
        with patch.dict(evaluator.CHECKS, {"transition": rotted_checker}):
            rotted = baseline.snapshot(spec)
        result = baseline.compare(base, rotted)
        self.assertTrue(result["comparable"], result["mismatch"])
        self.assertEqual([row["id"] for row in result["deltas"]], ["EV-P-002"])
        self.assertEqual([row["id"] for row in result["regressions"]], ["EV-P-002"])
        self.assertEqual(result["current"]["counts"]["failed"], 1)
        baseline.save(spec)
        with patch.dict(evaluator.CHECKS, {"transition": rotted_checker}):
            code = _run_main(["diff", str(spec)])
        self.assertEqual(code, baseline.REGRESSED, "判据腐烂必须让 diff 退出码变红，不能报\"与基线一致\"")

    def test_anchor_mismatch_refuses_comparison_and_shows_no_deltas(self):
        # ③ 锚不一致 → 拒绝比较并报错，一个差值都不给（静默 diff 正是把结论跑废的那一步）
        spec = self.probe()
        base = baseline.snapshot(spec)
        for name in baseline.ANCHOR_NAMES:
            drifted = copy.deepcopy(base)
            drifted["anchors"][name] = "different"
            result = baseline.compare(base, drifted)
            self.assertFalse(result["comparable"], f"{name} 变了居然还敢比")
            self.assertEqual(result["deltas"], [], f"{name} 锚不一致却给了 diff")
            self.assertIn(name, result["mismatch"])
            self.assertIn("拒绝比较", baseline.render(result))

    def test_cli_refuses_cross_anchor_comparison_with_exit_code_two(self):
        spec = self.probe()
        baseline.save(spec)
        stored = json.loads(baseline.baseline_path(spec).read_text(encoding="utf-8"))
        stored["anchors"]["judgeVersion"] = "eval-judge/999"
        baseline.baseline_path(spec).write_text(json.dumps(stored, ensure_ascii=False), encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out):
            code = baseline.main(["diff", str(spec)])
        text = out.getvalue()
        self.assertEqual(code, baseline.REFUSED)
        self.assertIn("拒绝比较", text)
        self.assertIn("judgeVersion", text)
        self.assertNotIn("逐条差异", text)

    def test_missing_baseline_is_refused_not_reported_as_equal(self):
        code, err = _run_main(["diff", str(self.probe())], capture_stderr=True)
        self.assertEqual(code, baseline.REFUSED)
        self.assertIn("无基线", err)

    def test_save_refuses_a_suite_that_is_not_clean(self):
        spec = self.probe()
        with patch.dict(evaluator.CHECKS, {"transition": rotted_checker}):
            with self.assertRaises(ValueError) as caught:
                baseline.save(spec)
        self.assertIn("不干净", str(caught.exception))
        self.assertFalse(baseline.baseline_path(spec).exists(), "不干净的快照绝不能落进基线文件")

    def test_round_trip_of_untouched_suite_reports_no_drift(self):
        spec = self.probe()
        baseline.save(spec)
        stored = baseline.load(baseline.baseline_path(spec))
        result = baseline.compare(stored, baseline.snapshot(spec))
        self.assertTrue(result["comparable"])
        self.assertEqual(result["deltas"], [])
        self.assertEqual(result["warnings"], [], "同一批字节不该报执行器漂移")


class TruthVsDerivedTests(ProbeSetMixin):
    def test_baseline_files_are_committed_truth_and_diff_report_is_derived(self):
        ignores = [line.strip() for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
                   if line.strip() and not line.strip().startswith("#")]
        self.assertIn(baseline.DERIVED.relative_to(ROOT).as_posix(), ignores, "派生报告必须被 gitignore")
        self.assertFalse([line for line in ignores if "baseline" in line and "evals" in line],
                         "evals/<set>/baseline 是入库真相，不能被忽略")
        for spec in sorted(ROOT.glob("evals/*/eval.yaml")):
            self.assertTrue(baseline.baseline_path(spec).is_file(), f"缺基线文件：{spec}")

    def test_saved_baselines_match_the_committed_anchors(self):
        # 入库的基线必须是"当下判得出来"的那一份：锚漂了却没重新 save，说明真相文件腐烂了
        for spec in sorted(ROOT.glob("evals/*/eval.yaml")):
            stored = baseline.load(baseline.baseline_path(spec))
            result = baseline.compare(stored, baseline.snapshot(spec))
            self.assertTrue(result["comparable"], f"{spec}：{result['mismatch']}")
            self.assertEqual(result["regressions"], [], f"{spec}：{result['deltas']}")


def _run_main(argv, capture_stderr: bool = False):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = baseline.main(argv)
    if capture_stderr:
        return code, err.getvalue()
    return code


if __name__ == "__main__":
    unittest.main()
