"""精简建议（三读数齐了才开口）与固定口径的反向对照（排序第 6 项的 ☑ 硬判据）。

钉住的执法：

① 注册表缺 slimAdvice 判据 ⇒ 拒绝执行，不猜三个读数是哪三个、不猜阈值；
② 口径未固定（非全量／slug 不符／时间切点不符）⇒ 命中率读数标「口径未固定」，整轮判「依据不足」不出名单；
③ 任一读数 N/A ⇒ 只报依据不足并写明缺在哪一环；候选卡为 0 时覆盖率不得退化成 100%；
④ 集中度过阈值 ⇒ 打印注册表原文的禁止结论文案、名单清空；把阈值调宽（撤掉报警）名单必须恢复 ⇒
   证明「禁止」是这道闸门在起作用，不是代码写死不给结论；
⑤ 单条命中数为 0 不得判「可删」：低命中只进「观察名单（待验证，不是删除清单）」；
⑥ apply_window 只认带时区的 ISO 切点，naive 直接报错；没有 ts／读不懂 ts 的事件排除并计数
   （证明不了落在窗口内就不算进分子，也不得悄悄少算）。
"""
from __future__ import annotations
import shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from obs import rules, slim

ROOT = Path(__file__).resolve().parents[2]
POL = slim.spec()
CAL = POL["caliber"]
GATE = POL["gate"]
WATCH_THRESHOLD = float(GATE["lowHitShare"])


POL_THRESHOLD = float(yaml.safe_load(slim.SHIPPED_REGISTRY.read_text(encoding="utf-8"))
                      ["attribution"]["concentration"]["maxClauseShare"])


def attribution(with_clauses=12, cards=20, evidence=28, top_evidence=6, threshold=None):
    """造一份归因汇总（结构与 obs.attribution.attribute_all 一致）：测试只验闸门，不复算比例。"""
    total = evidence
    share = top_evidence / total if total else 0.0
    limit = POL_THRESHOLD if threshold is None else float(threshold)
    return {"counts": {"cards": cards, "withClauses": with_clauses, "clauses": evidence,
                       "noSkill": 0, "multiSkillCards": 0, "distinctClauses": 12,
                       "distinctClauseFiles": ["shared/problem-recording.md"]},
            "concentration": {"alarm": bool(cards and total >= 3 and share >= limit),
                              "label": "承接集中度异常", "unusable": "本次证据化命中率不可当质量结论使用",
                              "reason": f"同一条款承担的证据占比 {share:.0%} ≥ 阈值 {limit:.0%}",
                              "belowSample": False, "offSampleNote": "",
                              "share": share, "threshold": limit, "minEvidence": 3,
                              "evidence": total, "cards": cards, "distinctClauses": 12,
                              "top": {"file": "shared/problem-recording.md", "startLine": 18,
                                      "endLine": 40, "heading": "问题记录", "evidence": top_evidence}}}


def hit_report(files=None, value=0.139, **over):
    """一份「已按固定口径跑完」的命中率报告；over 用来注入坏口径（非全量／换 slug／挪切点）。"""
    params = {"sample": int(CAL["sample"]), "slug": str(CAL["projectSlug"]),
              "since": str(CAL["since"]), "until": str(CAL["until"])}
    window = {"since": params["since"], "until": params["until"], "total": 325814,
              "outside": 1200, "unusable": 7, "kept": 324607}
    params.update(over.pop("params", {}))
    window.update(over.pop("window", {}))
    report = {"value": value, "reason": "", "params": params, "window": window,
              "files": files if files is not None else [], "declared": 841, "hits": 117}
    report.update(over)
    return report


def low_files(count=3):
    return [{"file": f"Other/skill-{index}/SKILL.md", "skill": f"skill-{index}", "clauses": 20 + index,
             "readHits": 0, "citeHits": 0, "rate": 0.0} for index in range(count)]


class RegistryGateTests(unittest.TestCase):
    def thin(self, mutate):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        (root / "governance").mkdir(parents=True)
        data = yaml.safe_load(slim.SHIPPED_REGISTRY.read_text(encoding="utf-8"))
        mutate(data)
        (root / "governance/obs-registry.yaml").write_text(
            yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        return root

    def test_missing_section_refuses_to_guess_readings(self):
        root = self.thin(lambda data: data.pop("slimAdvice"))
        with self.assertRaises(ValueError) as caught:
            slim.spec(root)
        self.assertIn("未声明 slimAdvice ⇒ 不猜三读数是哪三个", str(caught.exception))

    def test_missing_threshold_refuses_default_value(self):
        root = self.thin(lambda data: data["slimAdvice"]["gate"].pop("lowHitShare"))
        with self.assertRaises(ValueError) as caught:
            slim.spec(root)
        self.assertIn("slimAdvice.gate 缺判据键 ['lowHitShare']", str(caught.exception))

    def test_undefined_reading_is_not_claimed(self):
        root = self.thin(lambda data: data["slimAdvice"]["requiredReadings"].append("ghostMetric"))
        with self.assertRaises(ValueError) as caught:
            slim.spec(root)
        self.assertIn("未在 readings 定义", str(caught.exception))


class CaliberTests(unittest.TestCase):
    def test_full_caliber_produces_three_readings_and_a_watch_list(self):
        advice = slim.advise(ROOT, hit_report(files=low_files()), attribution(), POL)
        self.assertEqual(advice["missing"], [])
        self.assertTrue(advice["caliberFixed"])
        self.assertEqual(len(advice["watch"]), 3)
        text = slim.render(advice)
        self.assertIn("规则命中率", text)
        self.assertIn("**13.9%**", text)                    # 读数一：规则命中率
        self.assertIn("**60.0%**", text)                    # 读数二：条款证据覆盖率 12/20
        self.assertIn("**21.4%**", text)                    # 读数三：承接集中度 6/28（未过 0.6 阈值）
        self.assertIn("口径已固定", text)
        self.assertIn(GATE["watchListLabel"], text)
        self.assertIn(GATE["zeroHitOnly"], text)

    def test_sampled_run_is_flagged_and_yields_no_list(self):
        advice = slim.advise(ROOT, hit_report(params={"sample": 400}), attribution(), POL)
        reading = advice["readings"]["ruleHitRate"]
        self.assertIn(CAL["unfixedLabel"], reading["reason"])
        self.assertEqual(reading["value"], 0.139, "数照原样印出来，人有权看见它")
        self.assertFalse(reading["usable"], "但口径未固定 ⇒ 不配用来定阈值")
        self.assertEqual(advice["watch"], [], "口径未固定时不得输出任何名单")
        self.assertIn(GATE["missingReading"], advice["blocked"][0])
        self.assertIn(GATE["missingReading"], slim.render(advice))

    def test_missing_slug_and_wrong_cutoffs_are_each_named(self):
        report = hit_report(params={"slug": ""}, window={"since": "2026-01-01T00:00:00+08:00"})
        advice = slim.advise(ROOT, report, attribution(), POL)
        reason = advice["readings"]["ruleHitRate"]["reason"]
        self.assertIn("project-slug", reason)
        self.assertIn("起切点", reason)
        self.assertNotIn("止切点", reason, "只报了实际不符的那几条，不是一句笼统的口径不对")

    def test_naive_hit_value_is_not_replaced_by_a_number(self):
        advice = slim.advise(ROOT, hit_report(value=None, reason="N/A (未授予 TOOL_EVENTS)"),
                             attribution(), POL)
        self.assertEqual(advice["readings"]["ruleHitRate"]["value"], None)
        self.assertIn("未授予 TOOL_EVENTS", advice["readings"]["ruleHitRate"]["reason"])
        self.assertEqual(advice["watch"], [])


class MissingReadingTests(unittest.TestCase):
    def test_no_candidates_means_na_not_hundred_percent(self):
        advice = slim.advise(ROOT, hit_report(files=low_files()), attribution(cards=0, with_clauses=0), POL)
        coverage = advice["readings"]["clauseEvidenceCoverage"]
        self.assertIsNone(coverage["value"])
        self.assertIn("不得退化成 100%", coverage["reason"])
        self.assertIn(GATE["missingReading"], advice["blocked"][0])

    def test_attribution_that_never_ran_is_reported_as_missing(self):
        advice = slim.advise(ROOT, hit_report(files=low_files()), None, POL)
        self.assertIn("归因段本轮没跑成", advice["readings"]["clauseEvidenceCoverage"]["reason"])
        self.assertIn("没有候选卡", advice["readings"]["attributionConcentration"]["reason"])
        self.assertEqual(advice["watch"], [])


class ConcentrationGateTests(unittest.TestCase):
    def test_alarm_blocks_every_verdict_with_registry_text(self):
        # 26/28 ≈ 93% 压在同一条款上 ⇒ 过阈值（0.6），本仓真踩过的那次就是这个形状
        advice = slim.advise(ROOT, hit_report(files=low_files()), attribution(top_evidence=26), POL)
        self.assertTrue(advice["concentrationAlarm"])
        self.assertEqual(advice["watch"], [], "集中度过阈值时不得给出任何名单")
        text = slim.render(advice)
        self.assertIn(GATE["concentrationAlarm"], text)
        self.assertNotIn(GATE["watchListLabel"], text)

    def test_widening_the_threshold_brings_the_list_back(self):
        # 反向对照：报警来自闸门而不是写死——把阈值调到 1.0 撤掉报警，名单必须恢复输出
        loosened = yaml.safe_load(yaml.dump(POL, allow_unicode=True))
        advice = slim.advise(ROOT, hit_report(files=low_files()),
                             attribution(top_evidence=26, threshold=1.0), loosened)
        self.assertFalse(advice["concentrationAlarm"])
        self.assertEqual(len(advice["watch"]), 3)
        self.assertIn(GATE["watchListLabel"], slim.render(advice))


class ZeroHitTests(unittest.TestCase):
    def test_zero_hit_files_are_watch_only_and_never_deletion(self):
        advice = slim.advise(ROOT, hit_report(files=low_files()), attribution(), POL)
        text = slim.render(advice)
        self.assertIn(GATE["watchListLabel"], text)
        self.assertIn(GATE["zeroHitOnly"], text)
        for verdict in ("应当删除", "建议删除", "可直接删除", "予以删除"):
            self.assertNotIn(verdict, text, f"零命中只进观察名单，不许出现「{verdict}」这种判词")
        self.assertIn("命中率 <", text)

    def test_files_above_threshold_stay_out_of_the_list(self):
        files = low_files(2) + [{"file": "PRD/prd-design/SKILL.md", "skill": "prd-design", "clauses": 15,
                                 "readHits": 40, "citeHits": 3, "rate": WATCH_THRESHOLD + 0.05}]
        advice = slim.advise(ROOT, hit_report(files=files), attribution(), POL)
        self.assertEqual([row["file"] for row in advice["watch"]],
                         ["Other/skill-0/SKILL.md", "Other/skill-1/SKILL.md"],
                         "判据宁窄勿宽：高于阈值的文件不得混进观察名单")


class WindowTests(unittest.TestCase):
    def spans(self, stamps):
        return [{"session": "S", "ts": stamp, "kind": "tool.requested"} for stamp in stamps]

    def test_naive_cutoff_is_refused_instead_of_guessed(self):
        for bad in ("2026-09-01 00:00", "not-a-date"):
            with self.assertRaises(ValueError) as caught:
                rules.apply_window(self.spans(["2026-09-02T00:00:00+08:00"]), bad, None)
            self.assertIn("不是带时区的 ISO-8601 时刻", str(caught.exception))

    def test_events_without_readable_ts_are_counted_not_silently_dropped(self):
        window = rules.apply_window(self.spans([
            "2026-08-31T23:59:59+08:00",      # 窗口前
            "2026-09-02T10:00:00+08:00",      # 窗口内
            None,                              # 宿主没写 ts
            "2026-09-02",                      # naive，读不懂 ⇒ 不算进来
        ]), "2026-09-01T00:00:00+08:00", "2026-10-16T23:59:59+08:00")
        self.assertEqual(len(window["spans"]), 1)
        self.assertEqual(window["outside"], 1)
        self.assertEqual(window["unusable"], 2)
        self.assertEqual(window["total"], 4)

    def test_window_shrinks_the_evidence_face_before_capability_check(self):
        # 口径的一致性：能力判定也按窗口后的事件面算，否则窗口外的事件会替窗口内「撑绿」能力
        kept = self.spans(["2026-09-02T10:00:00+08:00"])
        window = rules.apply_window(self.spans(["2025-01-01T10:00:00+08:00"]) + kept,
                                    "2026-09-01T00:00:00+08:00", None)
        self.assertEqual(window["spans"], kept)


class RealRegistryTests(unittest.TestCase):
    def test_shipped_caliber_is_a_real_project_and_a_closed_window(self):
        since, until = CAL["since"], CAL["until"]
        self.assertEqual(int(CAL["sample"]), 0, "固定口径必须是全量")
        self.assertTrue(str(CAL["projectSlug"]).strip(), "固定口径必须限定被观测项目")
        self.assertLess(rules._moment(since), rules._moment(until))
        probe = subprocess.run(["git", "-C", str(ROOT), "check-ignore", str(Path(POL["output"]["file"]))],
                               capture_output=True)
        self.assertEqual(probe.returncode, 0, "精简建议是派生物：不入库，靠复算命令重算")


class EvidenceFloorTests(unittest.TestCase):
    """样本太薄那一格：100% 覆盖率在几张卡上说的是分母小，不是承接得好（同族红线：禁 n=1 标通过）。"""

    def thin(self, mutate):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        (root / "governance").mkdir(parents=True)
        data = yaml.safe_load(slim.SHIPPED_REGISTRY.read_text(encoding="utf-8"))
        mutate(data)
        (root / "governance/obs-registry.yaml").write_text(
            yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        return root

    def test_missing_floor_key_refuses_default(self):
        root = self.thin(lambda data: data["slimAdvice"]["gate"].pop("minEvidenceCards"))
        with self.assertRaises(ValueError) as caught:
            slim.spec(root)
        self.assertIn("slimAdvice.gate 缺判据键", str(caught.exception))
        self.assertIn("minEvidenceCards", str(caught.exception))

    def test_full_coverage_on_thin_sample_is_not_a_percentage_to_act_on(self):
        floor = int(GATE["minEvidenceCards"])
        advice = slim.advise(ROOT, hit_report(files=low_files()),
                             attribution(cards=floor - 1, with_clauses=floor - 1), POL)
        coverage = advice["readings"]["clauseEvidenceCoverage"]
        self.assertEqual(coverage["value"], 1.0, "数字要照实印出来给人看")
        self.assertIs(coverage["usable"], False, "但闸门必须当这一环缺")
        self.assertIn(GATE["tooFewCards"], coverage["reason"])
        concentration = advice["readings"]["attributionConcentration"]
        self.assertIs(concentration["usable"], False)
        self.assertIn(GATE["tooFewCards"], concentration["reason"])
        self.assertEqual(advice["watch"], [], "样本不足不许出观察名单")
        self.assertIn(GATE["missingReading"], advice["blocked"][0])

    def test_lowering_the_floor_makes_the_same_input_produce_a_list(self):
        # 反向对照：同一份输入（9 张卡、全带证据），把阈值调到 1 就必须出名单 ⇒ 挡下来的是闸门不是写死
        floor = int(GATE["minEvidenceCards"])
        loosened = dict(POL, gate=dict(GATE, minEvidenceCards=1))
        advice = slim.advise(ROOT, hit_report(files=low_files()),
                             attribution(cards=floor - 1, with_clauses=floor - 1), loosened)
        self.assertTrue(advice["watch"], "撤掉闸门后同一输入必须真的出名单")
        self.assertEqual(advice["blocked"], [])


if __name__ == "__main__":
    unittest.main()
