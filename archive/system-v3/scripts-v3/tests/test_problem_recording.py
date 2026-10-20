"""Static wiring regressions; these do not execute an Agent or prove runtime logging."""
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_core as core

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "shared/problem-recording.md"


class ProblemRecordingContractTests(unittest.TestCase):
    def test_every_registered_entry_loads_recording_policy(self):
        # 口径只有一份：validate_core.check_recording（评测集 evals/recording 调的是同一个实现）。
        # 这里不再用 subTest 逐条重写一遍判据——两处各写一套就会出现「单测绿、评测红」的分裂口径。
        self.assertEqual(core.check_recording(ROOT), [],
                         "active skill 的承接节／义务词／规范指针必须逐条过校验器")

    def test_tampered_copy_reports_the_exact_verdict(self):
        # 反向对照：把承接节删掉必须报出那句判据，而不是报个别的错就算红
        root, victim, entry = self.sandbox()
        original = entry.read_text(encoding="utf-8")
        self.assertIn(core.RECORDING_HEADING, original)
        entry.write_text(original.replace(core.RECORDING_HEADING, "## 别的章节", 1), encoding="utf-8")
        findings = core.check_recording(root)
        self.assertEqual(findings, [f"skill {victim} SKILL.md missing recording section: {core.RECORDING_HEADING}"],
                         f"只动一处就该只报一条：{findings}")

    def test_obligation_keyword_loss_is_named_not_blurred(self):
        root, victim, entry = self.sandbox()
        original = entry.read_text(encoding="utf-8")
        self.assertIn("唯一索引", core.recording_section(original))
        entry.write_text(original.replace("唯一索引", "索引", 1), encoding="utf-8")
        self.assertEqual(core.check_recording(root),
                         [f"skill {victim} recording section missing obligation keyword: 唯一索引"])

    def test_pointer_to_a_missing_policy_does_not_resolve(self):
        root, victim, entry = self.sandbox()
        original = entry.read_text(encoding="utf-8")
        entry.write_text(original.replace("problem-recording.md", "no-such-policy.md", 1), encoding="utf-8")
        findings = "；".join(core.check_recording(root))
        self.assertIn("does not resolve", findings)

    def test_legacy_entries_are_not_punished(self):
        # 判据宁窄勿宽：没登记的 legacy 条目缺承接节不得报红，否则执法会去罚不适用对象
        root, _victim, entry = self.sandbox(legacy_without_section=True)
        self.assertEqual(core.check_recording(root), [])

    def sandbox(self, legacy_without_section=False):
        """临时小仓：1 个 active skill（真正文）＋可选 1 个 legacy（无承接节），判据只对 active 生效。"""
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
        registry = yaml.safe_load((ROOT / "governance/skill-registry.yaml").read_text(encoding="utf-8"))
        # 选一个用仓根默认规范的 active 条目：带 recordingPolicy 覆盖的是自带规范的便携包，
        # 拿它做夹具会把对照测成「指针本来就指向包内文件」，报不出这句判据。
        active = next(skill for skill in registry["skills"]
                      if skill.get("status") == "active" and not skill.get("recordingPolicy"))
        skills = [dict(active)]
        if legacy_without_section:
            legacy = dict(active)
            legacy.update({"id": "probe-legacy", "status": "legacy", "path": "Other/probe-legacy"})
            skills.append(legacy)
        (tmp / "governance").mkdir(parents=True)
        (tmp / "governance/skill-registry.yaml").write_text(
            yaml.safe_dump({"skills": skills}, allow_unicode=True), encoding="utf-8")
        policy = tmp / "shared/problem-recording.md"
        policy.parent.mkdir(parents=True)
        shutil.copyfile(POLICY, policy)
        entry = tmp / active["path"] / "SKILL.md"
        entry.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / active["path"] / "SKILL.md", entry)
        if legacy_without_section:
            bare = tmp / "Other/probe-legacy/SKILL.md"
            bare.parent.mkdir(parents=True, exist_ok=True)
            bare.write_text("# 一个没有承接节的 legacy 条目\n", encoding="utf-8")
        return tmp, active["id"], entry

    def test_reporting_consumers_bind_to_project_index(self):
        for name in ("Test/auto-test/SKILL.md", "DEV/code-review/SKILL.md",
                     "Other/defect-triage/SKILL.md", "UI/fidelity-review/SKILL.md"):
            with self.subTest(entry=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                self.assertIn(".spec/问题日志.md", text)
                self.assertIn("problem-recording.md", text)
        review = (ROOT / "DEV/code-review/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("唯一索引", review)
        self.assertIn("待合并", review)
        triage = (ROOT / "Other/defect-triage/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("分诊完成不等于缺陷修复闭环", triage)

    def test_index_and_detail_templates_keep_tracking_fields(self):
        index = (ROOT / "shared/templates/problem-log-template.md").read_text(encoding="utf-8")
        for field in ("问题 ID/范围", "问题产物", "状态", "反哺出口", "下一安全节点",
                      "不重复追加", "恢复/交付前", "待授权反馈", "已修复不等于已复核"):
            self.assertIn(field, index)
        detail = (ROOT / "shared/templates/issue-template.md").read_text(encoding="utf-8")
        for field in ("原问题 ID", "脱敏证据", "责任方", "下一动作", "修复判据", "复核证据", "回退方式"):
            self.assertIn(field, detail)

    def test_authoritative_policy_keeps_failure_and_authority_boundaries(self):
        policy = POLICY.read_text(encoding="utf-8")
        for boundary in ("下一安全节点", "未落盘", "根因", "恢复及最终交付前",
                         "不新建重复条目", "跨仓", "已修复", "已验证", "强制终止", "不是自动日志服务"):
            self.assertIn(boundary, policy)
        guide = (ROOT / "shared/instrumentation-guide.md").read_text(encoding="utf-8")
        self.assertNotIn("不确定算不算问题 → 不记", guide)
        self.assertNotIn("不是执行中动作", guide)
        refs = re.findall(r"`([^`]*problem-recording\.md)`", guide)
        self.assertTrue(any((ROOT / ref).resolve() == POLICY.resolve()
                            for ref in refs))
        profile = (ROOT / "shared/execution-profiles.md").read_text(encoding="utf-8")
        self.assertIn("problem-recording.md", profile)
        self.assertIn("不等收尾", profile)


if __name__ == "__main__":
    unittest.main()
