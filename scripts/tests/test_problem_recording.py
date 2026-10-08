"""Static wiring regressions; these do not execute an Agent or prove runtime logging."""
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "shared/problem-recording.md"


class ProblemRecordingContractTests(unittest.TestCase):
    def test_every_registered_entry_loads_recording_policy(self):
        registry = yaml.safe_load((ROOT / "governance/skill-registry.yaml").read_text(encoding="utf-8"))
        self.assertTrue(registry["skills"])
        for skill in registry["skills"]:
            if skill.get("status") != "active":
                continue
            entry = ROOT / skill["path"] / "SKILL.md"
            with self.subTest(skill=skill["id"]):
                text = entry.read_text(encoding="utf-8")
                section = text.split("## 问题记录与恢复（执行必需）", 1)[1].split("\n## ", 1)[0]
                refs = re.findall(r"`([^`]*\.md)`", section)
                self.assertEqual(len(refs), 1)
                # Portable packages declare their self-contained recording policy;
                # all engineering entries retain the shared repository default.
                policy = ROOT / skill.get("recordingPolicy", "shared/problem-recording.md")
                self.assertTrue(policy.is_file())
                self.assertEqual((entry.parent / refs[0]).resolve(), policy.resolve())
                if "recordingPolicy" in skill:
                    self.assertTrue(policy.resolve().is_relative_to(entry.parent.resolve()))
                for obligation in ("下一安全节点", "根因未明", "恢复/交付前", "唯一索引"):
                    self.assertIn(obligation, section)

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
        detail = (ROOT / "Other/skill-optimizer/assets/issue-template.md").read_text(encoding="utf-8")
        for field in ("原问题 ID", "脱敏证据", "责任方", "下一动作", "修复判据", "复核证据", "回退方式"):
            self.assertIn(field, detail)

    def test_authoritative_policy_keeps_failure_and_authority_boundaries(self):
        policy = POLICY.read_text(encoding="utf-8")
        for boundary in ("下一安全节点", "未落盘", "根因", "恢复及最终交付前",
                         "不新建重复条目", "跨仓", "已修复", "已验证", "强制终止", "不是自动日志服务"):
            self.assertIn(boundary, policy)
        guide = (ROOT / "Other/skill-optimizer/references/instrumentation-guide.md").read_text(encoding="utf-8")
        self.assertNotIn("不确定算不算问题 → 不记", guide)
        self.assertNotIn("不是执行中动作", guide)
        refs = re.findall(r"`([^`]*problem-recording\.md)`", guide)
        self.assertTrue(any((ROOT / "Other/skill-optimizer/references" / ref).resolve() == POLICY.resolve()
                            for ref in refs))
        profile = (ROOT / "shared/execution-profiles.md").read_text(encoding="utf-8")
        self.assertIn("problem-recording.md", profile)
        self.assertIn("不等收尾", profile)


if __name__ == "__main__":
    unittest.main()
