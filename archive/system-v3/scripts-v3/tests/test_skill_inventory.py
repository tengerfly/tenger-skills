"""Skill 清单扫描的范围对照（validate_core.skill_files / check_registry）。

`check_registry` 会全仓清点 `SKILL.md`：没 frontmatter、名字与注册表不一致、没登记，一律判红。
评测夹具（`evals/**/fixtures/**/SKILL.md`）是被测数据不是本仓的 skill——它们自带一份迷你
`governance/skill-registry.yaml` 并在临时复制的项目根里跑。把夹具当 skill 清点，只有两种坏结果：
往真注册表里塞假条目（污染 skill 名录），或者门禁永远红。所以夹具目录被跳过，与既有的
`assets`（便携包自带 SKILL.md 副本）同一类。

对照组必须同时钉住两头，否则这个跳过就是给自己开后门：

① 同一个临时根里，**不在** fixtures 下的 SKILL.md 仍要被抓进清单（跳过范围只到 fixtures 一层）；
② 真实夹具文件确实存在且确实不再进清单（不然是空跑，证明不了跳过在起作用）；
③ 门禁层面：`check_registry(仓根)` 不得再拿夹具路径报「invalid frontmatter」。
"""
from __future__ import annotations
import shutil, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_core as core

ROOT = Path(__file__).resolve().parents[2]
NO_FRONTMATTER = "# 一个没有 frontmatter 的 SKILL.md\n\n正文。\n"


class SkillInventoryScopeTests(unittest.TestCase):
    def tearDown(self):
        if hasattr(self, "tmp"):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def test_only_fixture_directories_are_skipped(self):
        self.tmp = Path(tempfile.mkdtemp())
        for relative in ("PRD/real-skill/SKILL.md", "PRD/fixtures/probe/SKILL.md",
                         "evals/recording/fixtures/clean/PRD/probe/SKILL.md",
                         "Test/other-skill/SKILL.md"):
            target = self.tmp / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(NO_FRONTMATTER, encoding="utf-8")
        found = [path.relative_to(self.tmp).as_posix() for path in core.skill_files(self.tmp)]
        self.assertEqual(found, ["PRD/real-skill/SKILL.md", "Test/other-skill/SKILL.md"],
                         "跳过只能跳过 fixtures 目录，同仓其它位置的 SKILL.md 必须照常进清单")

    def test_repo_fixtures_exist_but_are_not_inventoried(self):
        # ②：夹具文件真存在（否则本条是空跑），且整个仓的清单里一条夹具都不该出现
        shipped = ["evals/recording/fixtures/recording-clean/PRD/probe-skill/SKILL.md",
                   "evals/recording/fixtures/recording-clean/Other/probe-legacy/SKILL.md",
                   "evals/recording/fixtures/recording-portable/PRD/probe-portable/SKILL.md"]
        for relative in shipped:
            self.assertTrue((ROOT / relative).is_file(), f"夹具文件不在了，本条对照就失去意义：{relative}")
            findings = core.frontmatter(ROOT / relative)
            self.assertFalse(findings[0], f"夹具本来就没 frontmatter ⇒ 没跳过就一定会报红：{relative}")
        hit = [path.relative_to(ROOT).as_posix() for path in core.skill_files(ROOT)
               if "fixtures" in path.parts]
        self.assertEqual(hit, [], f"夹具路径被当成 skill 清点了：{hit}")

    def test_registry_gate_does_not_blame_the_fixtures(self):
        # ③：门禁层面的后果——加跳过前，这三条正是 system 报的红
        errors = [error for error in core.check_registry(ROOT) if "fixtures" in error]
        self.assertEqual(errors, [], f"夹具路径被当成 skill 清点了：{errors}")


if __name__ == "__main__":
    unittest.main()
