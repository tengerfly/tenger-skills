"""反哺有效率读数（obs.feedback）的闸门对照（排序第 4 格：只补通路，不造数）。

这个指标唯一的价值就在于「拿不到数时老实说拿不到」，所以对照全部围绕「什么时候必须 N/A、
为什么是这道闸门在起作用而不是写死」，每条都断言注册表里的具体判据文本：

① 注册表缺 feedbackRate 或缺判据键 ⇒ 拒绝执行，不用默认值凑一份读数；
② 反哺记录不足 minRecords ⇒ N/A，并给出落选条目数与首条原因；
③ 记录与复发链按 skill 对不上 ⇒ N/A，明写「两侧没有交集，不借链凑分母」；
④ 可归属链只剩 1 条 ⇒ N/A 并引 n=1 禁令；把 minChains 降到 1 ⇒ 同一个输入必须出数
   （证明禁止来自闸门，不是代码写死不给结论）；
⑤ 观察窗不足 ⇒ N/A 并给出实际天数与阈值；
⑥ 两侧齐备才出百分比；⑦ 量具红点率（86%／92%）永远单列，不许爬到读数行上；
⑧ **落点层次**：反哺记录的落账 commit 改的是 skill 正文还是工具层——全在工具层时 N/A 必须说
   「落点问题、再补链也没用」，读不动时只能记「未核」，不许把 git 失败默认成「未触达」（假阴性）。
"""
from __future__ import annotations
import shutil, sys, tempfile, unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from obs import feedback

ROOT = Path(__file__).resolve().parents[2]
POL = feedback.policy()
NA, LINK_RULE = POL["naRule"], POL["linkRule"]
NO_N1 = POL["forbidden"][2]


def record(skill="workflow", day="2026-08-01", title=None, before=10, after=4):
    return {"title": title or f"### E-x {day} {skill}（档位：标准）", "date": day,
            "skills": [skill], "before": before, "after": after, "commit": "0123456789ab"}


def link(skill="workflow", after_count=0, usable=True, label="WorkFlow", since="2026-08-01"):
    return {"record": f"E-x {skill}", "skill": skill, "chain": label, "since": since,
            "observedDays": 40, "beforeCount": 2, "afterCount": after_count, "afterNodes": [],
            "usable": usable, "unusableReason": f"观察窗只有 3 天 < minObserveDays={POL['minObserveDays']}"}


def chain(skill="workflow", label="WorkFlow", nodes=()):
    return {"skill": skill, "skillLabel": label, "nodes": list(nodes)}


class RegistryGateTests(unittest.TestCase):
    def stripped(self, mutate):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        (root / "governance").mkdir(parents=True)
        data = yaml.safe_load(feedback.SHIPPED_REGISTRY.read_text(encoding="utf-8"))
        mutate(data)
        (root / "governance/obs-registry.yaml").write_text(
            yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        return root

    def test_missing_section_refuses_to_guess_sources(self):
        root = self.stripped(lambda data: data.pop("feedbackRate"))
        with self.assertRaises(ValueError) as caught:
            feedback.policy(root)
        self.assertIn("未声明 feedbackRate ⇒ 不猜反哺记录与同型错误从哪来", str(caught.exception))

    def test_missing_key_refuses_default_values(self):
        root = self.stripped(lambda data: data["feedbackRate"].pop("minObserveDays"))
        with self.assertRaises(ValueError) as caught:
            feedback.policy(root)
        self.assertIn("缺必需判据键", str(caught.exception))
        self.assertIn("minObserveDays", str(caught.exception))

    def test_missing_landing_section_refuses_default(self):
        root = self.stripped(lambda data: data["feedbackRate"].pop("landing"))
        with self.assertRaises(ValueError) as caught:
            feedback.policy(root)
        self.assertIn("缺必需判据键", str(caught.exception))
        self.assertIn("landing", str(caught.exception))

    def test_missing_landing_text_refuses_default(self):
        # 落点文案也必须写在注册表里：代码里留一句"我觉得"的文案，下轮就没人能核对它出自哪条判据
        root = self.stripped(lambda data: data["feedbackRate"]["landing"].pop("noneTouched"))
        with self.assertRaises(ValueError) as caught:
            feedback.policy(root)
        self.assertIn("feedbackRate.landing 缺文案键", str(caught.exception))
        self.assertIn("noneTouched", str(caught.exception))


class GateTests(unittest.TestCase):
    def verdict(self, records, links, chains=None, dropped=None, pol=None, landing=None):
        return feedback._verdict(pol or POL, records, chains if chains is not None else [],
                                 links, dropped or [], "", landing)

    def test_records_below_floor_is_na_with_dropped_reason(self):
        value, reason = self.verdict([record()], [], dropped=["`E-003`：未声称生效或判据本身有错"])
        self.assertIsNone(value)
        self.assertIn(f"minRecords={POL['minRecords']}", reason)
        self.assertIn("未声称生效或判据本身有错", reason)
        self.assertIn(NA, reason)

    def test_no_overlap_refuses_to_borrow_other_chains(self):
        chains = [chain(skill="workflow")]
        records = [record(skill="quality-inspection"), record(skill="quality-inspection", day="2026-08-02")]
        value, reason = self.verdict(records, [], chains)
        self.assertIsNone(value)
        self.assertIn("两侧没有交集，不借链凑分母", reason)
        self.assertIn(LINK_RULE, reason)
        self.assertIn("quality-inspection", reason)
        self.assertIn("workflow", reason, "要说清链落在哪个 skill，别只报「对不上」")

    def test_landing_tool_only_names_the_layer_as_the_reason(self):
        # 反向对照：落点全在工具层时，N/A 必须说「落点问题」而不是「差几条链」
        landing = {"records": 2, "touched": 0, "unreadable": 0, "detail": []}
        value, reason = self.verdict([record(skill="quality-inspection"),
                                      record(skill="quality-inspection", day="2026-08-02")], [],
                                     [chain(skill="workflow")], landing=landing)
        self.assertIsNone(value)
        self.assertIn(POL["landing"]["noneTouched"], reason)
        self.assertNotIn(POL["landing"]["someTouched"], reason)

    def test_landing_on_skill_text_switches_the_diagnosis(self):
        landing = {"records": 2, "touched": 1, "unreadable": 0,
                   "detail": [{"title": "E-1", "commit": "a" * 40, "files": 1, "skills": ["workflow"]},
                              {"title": "E-2", "commit": "b" * 40, "files": 3, "skills": []}]}
        value, reason = self.verdict([record(skill="quality-inspection"),
                                      record(skill="quality-inspection", day="2026-08-02")], [],
                                     [chain(skill="workflow")], landing=landing)
        self.assertIsNone(value)
        self.assertIn(POL["landing"]["someTouched"], reason)
        self.assertNotIn("没有一条反哺记录的落账 commit 触达 skill 正文", reason,
                         "已经有一条改到正文了还说「没有一条」＝假阴性")
        self.assertIn("workflow", reason)

    def test_unreadable_landing_is_never_counted_as_tool_only(self):
        # 读不动 ≠ 未触达：把 git 失败默认成「工具层」就会造出一条不存在的落点结论
        landing = {"records": 2, "touched": 0, "unreadable": 1, "detail": []}
        value, reason = self.verdict([record(skill="quality-inspection"),
                                      record(skill="quality-inspection", day="2026-08-02")], [],
                                     [chain(skill="workflow")], landing=landing)
        self.assertIsNone(value)
        self.assertIn(POL["landing"]["unreadable"], reason)
        self.assertNotIn(POL["landing"]["noneTouched"], reason)

    def test_single_chain_triggers_the_n1_ban(self):
        links = [link(skill="workflow"), link(skill="workflow", after_count=1)]
        value, reason = self.verdict([record(), record(skill="workflow", day="2026-08-02")], links,
                                     [chain(skill="workflow")])
        self.assertIsNone(value)
        self.assertIn(f"minChains={POL['minChains']}", reason)
        self.assertIn(NO_N1, reason)

    def test_lowering_the_threshold_makes_the_same_input_produce_a_number(self):
        # 反向对照：证明④的 N/A 是闸门在起作用，不是代码写死不给结论
        links = [link(skill="workflow"), link(skill="workflow", after_count=1)]
        loosened = dict(POL, minChains=1)
        value, reason = self.verdict([record(), record(day="2026-08-02")], links,
                                     [chain(skill="workflow")], pol=loosened)
        self.assertEqual(value, 0.5, "1 条挡住／2 条可观察 ⇒ 50%，且必须真的能算出来")
        self.assertEqual(reason, "")

    def test_short_observe_window_is_not_counted(self):
        links = [link(skill="workflow", usable=False), link(skill="code-review", usable=False)]
        value, reason = self.verdict([record(), record(skill="code-review", day="2026-10-15")], links,
                                     [chain(skill="workflow"), chain(skill="code-review", label="Code-Review")])
        self.assertIsNone(value)
        self.assertIn(f"minObserveDays={POL['minObserveDays']}", reason)
        self.assertIn("观察窗不足", reason)

    def test_two_observable_chains_produce_the_rate(self):
        links = [link(skill="workflow"), link(skill="code-review", label="Code-Review", after_count=1)]
        value, reason = self.verdict([record(), record(skill="code-review", day="2026-08-03")], links,
                                     [chain(skill="workflow"), chain(skill="code-review", label="Code-Review")])
        self.assertEqual(value, 0.5)
        self.assertEqual(reason, "")


class LandingTests(unittest.TestCase):
    """落点判定的三件事：目录前缀取自注册表、git 读不动要如实未核、真 commit 分类要对得上。"""

    def test_prefixes_come_from_skill_registry_not_hardcoded_dirs(self):
        prefixes = dict(feedback._skill_prefixes(ROOT))
        self.assertIn("ui/ui-ux-review", prefixes)
        self.assertEqual(prefixes["ui/ui-ux-review"], "ui-ux-review")

    def test_non_sha_and_head_are_refused_not_guessed(self):
        for bad in ("", "HEAD", "not-a-sha", "abc"):
            self.assertIsNone(feedback.changed_files(bad, ROOT),
                              f"`{bad}` 不是落账 commit 该长的样子，不能拿去猜落点")

    def test_real_records_split_by_layer(self):
        def last_commit(rel):
            import subprocess
            proc = subprocess.run(["git", "log", "-1", "--format=%H", "--", rel], cwd=str(ROOT),
                                  capture_output=True, text=True, encoding="utf-8", errors="replace")
            return proc.stdout.strip()

        skill_commit = last_commit("UI/ui-ux-review/SKILL.md")
        tool_commit = "27d66573faaaa9c706c47f0c5e6c23383dff4324"  # E-001 落账 commit（只改 tsr.py 与其单测）
        self.assertTrue(skill_commit, "本仓历史里应有改到 skill 正文的 commit")
        summary = feedback.landing_summary(ROOT, [
            {"title": "E-skill", "date": "2026-10-01", "skills": ["ui-ux-review"],
             "before": 3, "after": 1, "commit": skill_commit},
            {"title": "E-tool", "date": "2026-10-02", "skills": ["quality-inspection"],
             "before": 3, "after": 1, "commit": tool_commit}])
        self.assertEqual(summary["records"], 2)
        self.assertEqual(summary["touched"], 1, "改到 UI/ui-ux-review/SKILL.md 的那条必须判「触达 skill 正文」")
        first, second = (item["skills"] for item in summary["detail"])
        self.assertIn("ui-ux-review", first, "落点要点名到 registry id，不能只报「改过文件」")
        self.assertTrue(first, "批处理 commit 会改到多个 skill，落点要全列出来而不是只取第一个")
        self.assertEqual(second, [], "只改 scripts/tsr.py 与其单测 ⇒ 工具层，永远对不上 issue 池的链")

    def test_missing_registry_lands_on_empty_prefixes(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        (root / "governance").mkdir(parents=True)
        self.assertEqual(feedback._skill_prefixes(root), [])


class RenderTests(unittest.TestCase):
    def test_detector_rate_stays_off_the_reading_line(self):
        report = {"policy": POL, "records": [record(skill="quality-inspection", before=14, after=2),
                                              record(skill="quality-inspection", day="2026-08-02",
                                                     before=153, after=13)],
                  "dropped": [], "chains": [chain(skill="workflow")], "chainError": "",
                  "links": [link(skill="workflow"), link(skill="workflow", after_count=1)],
                  "usable": [link(skill="workflow"), link(skill="workflow", after_count=1)],
                  "value": 0.5, "reason": "", "effective": ["E-x workflow"], "recurred": ["E-x workflow"]}
        text = feedback.render(report)
        reading = [line for line in text.splitlines() if line.startswith("- **读数：")][0]
        self.assertIn("50.0%", reading)
        self.assertNotIn("86%", reading, "量具红点率爬到读数行就是本指标要防的冒充")
        self.assertIn(POL["detectorRateLabel"], text)
        self.assertIn("86%", text)
        self.assertIn(POL["forbidden"][0], text)
        self.assertIn(NO_N1, text)

    def test_na_reading_keeps_the_reason_inline(self):
        report = {"policy": POL, "records": [record()], "dropped": ["`E-004`：未声称生效或判据本身有错"],
                  "chains": [], "chainError": "", "links": [], "usable": [], "value": None,
                  "reason": "反哺记录 1 条 < minRecords=2 ⇒ " + NA}
        text = feedback.render(report)
        self.assertIn("N/A —— 反哺记录 1 条 < minRecords=2", text)
        self.assertIn("不得读成 0% 或 100%", text)


class RealRepoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = feedback.measure(ROOT)

    def test_real_repo_today_reports_na_because_the_two_sides_do_not_intersect(self):
        self.assertIsNone(self.report["value"],
                          f"今晚不该出数：{self.report['reason']}")
        self.assertIn("两侧没有交集", self.report["reason"])
        self.assertGreaterEqual(len(self.report["records"]), 1)
        self.assertTrue(self.report["dropped"], "落选原因必须逐条摆出来，不能静默少算")

    def test_real_records_carry_verifiable_commits_and_pair_numbers(self):
        for item in self.report["records"]:
            self.assertRegex(item["commit"], r"^[0-9a-f]{7,40}$")
            self.assertIsInstance(item["before"], int)
            self.assertIsInstance(item["after"], int)
            self.assertTrue(item["skills"], "记录要点名反哺到哪个 skill，否则永远对不上链")

    def test_render_is_reproducible_from_the_real_report(self):
        text = feedback.render(self.report)
        self.assertIn(POL["name"], text)
        self.assertIn(POL["recompute"], text)
        self.assertIn("WorkFlow", text, "复发链要如实列出（1 条），不能因为没交集就不报")

    def test_real_report_prints_where_each_record_landed(self):
        # 现值：4 条反哺记录全部落在工具层 ⇒ 报告必须把「落点」这格算出来给人看，而不是只说对不上
        landing = self.report["landing"]
        self.assertLessEqual(landing["touched"] + landing["unreadable"], landing["records"])
        text = feedback.render(self.report)
        self.assertIn(POL["landing"]["rule"], text)
        for item in landing["detail"]:
            self.assertIn(item["title"], text, "每条记录的落点要逐条可核，不能只给一个合计")
        if landing["touched"] == 0 and not landing["unreadable"]:
            self.assertIn(POL["landing"]["noneTouched"], self.report["reason"])


if __name__ == "__main__":
    unittest.main()
