"""跨 skill 引用两视图判据的接线与范围对照（validate_core.check_crossrefs）。

这面尺子（`scripts/check-installed-refs.py`，判据源 `shared/skill-contract.md` §1.4）本来就在仓里，
但只挂在 ps1 脚本上：既不在 `validate_core system`，也不在评测器 CHECKS ⇒ 无人值守链路从不检它。
本轮接线，同时钉住四件事：

① 真仓此刻三项归零（接线当场抓出一条 2026-10-12 起就存在的真断链并改掉）；
② 适配器真有检出力：合规夹具判绿之外，三种破坏必须各报出**具体判据文本**——
   本仓曾经因为「尺子取的是被测目录里的路径」而让夹具红用例静默变绿（夹具不带 scripts/），
   所以这条对照专门走 `core.check_crossrefs` 而不是直接调脚本；
③ 新增的 `evals` 豁免只豁免测试数据：同样的违规文本放在 `evals/**` 不报、放在真实 skill 路径必须报；
④ 没有 skill-registry.yaml 的项目判「不适用」，不判「已通过」。
"""
from __future__ import annotations
import shutil, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_core as core

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "evals/crossrefs/fixtures/crossrefs-clean"
ENTRY = "PRD/probe-a/SKILL.md"
LAYER_REF = "错误写法示例：判据源 `../../UI/probe-b/references/x.md`。"
DEEP_REF = "../../../shared/problem-recording.md"
SHARED_REF = "错误写法示例：入口见 `../PRD/probe-a/SKILL.md`。"


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))
        self.project = self.tmp / "crossrefs-clean"
        shutil.copytree(FIXTURE, self.project)

    def findings(self):
        return core.check_crossrefs(self.project)

    def test_real_repo_is_clean_now(self):
        # ①：接线后的真实仓必须三项归零（有红点就是真缺陷，别当噪音）
        self.assertEqual(core.check_crossrefs(ROOT), [],
                         "真仓跨 skill 引用三项必须归零，否则本条判据长期带红")

    def test_compliant_fixture_produces_no_finding(self):
        # ②的前提：合规现场不报，红用例的红才归因到被改坏的那一处
        self.assertEqual(self.findings(), [], f"合规夹具不该报：{self.findings()}")

    def test_layer_prefix_is_reported_through_the_adapter(self):
        entry = self.project / ENTRY
        entry.write_text(entry.read_text(encoding="utf-8") + "\n" + LAYER_REF + "\n", encoding="utf-8")
        hits = [item for item in self.findings() if item.startswith("禁用写法（带分类层的跨 skill 相对路径）")]
        self.assertEqual(len(hits), 1, f"分类层写法必须被点名：{self.findings()}")
        # LAYER 判据抓到「分类层/技能目录」这一段就定性（后面的文件名不是判据的一部分）
        self.assertIn("../../UI/probe-b/", hits[0])

    def test_wrong_uplevel_count_is_reported_as_repo_unreachable(self):
        entry = self.project / ENTRY
        text = entry.read_text(encoding="utf-8").replace("../../shared/problem-recording.md", DEEP_REF)
        self.assertNotEqual(text, entry.read_text(encoding="utf-8"), "篡改没生效，本条对照就失去意义")
        entry.write_text(text, encoding="utf-8")
        hits = [item for item in self.findings() if item.startswith("源仓不可达")]
        self.assertEqual(len(hits), 1, f"层数写错必须报源仓视图：{self.findings()}")

    def test_source_reachable_but_copy_lands_on_category_dir(self):
        notes = self.project / "shared/probe-notes.md"
        notes.write_text(notes.read_text(encoding="utf-8") + "\n" + SHARED_REF + "\n", encoding="utf-8")
        hits = [item for item in self.findings() if "不是 skill id" in item]
        self.assertEqual(len(hits), 1,
                         f"副本视图（按 registry 模拟扁平布局）必须抓出这一类：{self.findings()}")
        self.assertIn("PRD", hits[0])

    def test_missing_registry_is_not_applicable_not_passed(self):
        bare = self.tmp / "no-registry"
        bare.mkdir()
        self.assertEqual(core.check_crossrefs(bare), [],
                         "项目没有 skill-registry.yaml ⇒ 不适用（调用方须如实标注，不得读成已通过）")


class FixtureExemptionScopeTests(unittest.TestCase):
    """`evals` 豁免只能豁免测试数据，不能顺手把真实 skill 正文也免掉。"""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))
        registry = self.tmp / "governance/skill-registry.yaml"
        registry.parent.mkdir(parents=True)
        registry.write_text("skills:\n  - id: probe-a\n    path: PRD/probe-a\n    status: active\n",
                            encoding="utf-8")

    def write(self, relative, body):
        target = self.tmp / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")

    def test_evals_dir_is_exempt_but_real_skill_dir_is_not(self):
        self.write("evals/probe/eval.yaml", "# 夹具说明\n" + LAYER_REF + "\n")
        self.assertEqual(core.check_crossrefs(self.tmp), [], "evals 里是被测数据，不该当真引用扫")
        self.write("PRD/probe-a/SKILL.md", "# Probe\n" + LAYER_REF + "\n")
        hits = [item for item in core.check_crossrefs(self.tmp) if item.startswith("禁用写法")]
        self.assertEqual(len(hits), 1, f"同一句放在真实 skill 路径必须报：{core.check_crossrefs(self.tmp)}")
        self.assertIn("../../UI/probe-b/", hits[0])


if __name__ == "__main__":
    unittest.main()
