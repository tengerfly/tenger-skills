"""控制文件时点对账（validate_core.control_drift）的正反对照。

为什么要有这组测试：这条检查只看时间戳，最容易写成"永远红"或"永远绿"两种废检查。
所以对照必须同时钉住两头：

① 干净输入 ⇒ 绿（否则这条检查没有可用状态，任何人跑都红 = 噪音）；
② workflow.yaml 落后于产物 ⇒ 红，且报错点名是 workflow 落后（不是别的）；
③ manifest.yaml 自己的 updatedAt 落后于它自己登记的产物 ⇒ 红（"文件写过但没改时间戳"这一种）；
④ 把产物时间改早 ⇒ 立刻转绿 —— 证明判定由比较驱动，不是常量；
⑤ 缺控制文件 ⇒ 明确报"无法对账，不是通过"，不允许静默绿。
"""
from __future__ import annotations
import shutil, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_core as core


class ControlDriftTests(unittest.TestCase):
    def tearDown(self):
        if hasattr(self, "tmp"):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def build(self, workflow_updated: str, manifest_updated: str, produced: str) -> Path:
        self.tmp = Path(tempfile.mkdtemp())
        spec = self.tmp / ".spec"
        spec.mkdir(parents=True, exist_ok=True)
        (spec / "workflow.yaml").write_text(
            "version: 2\nstate: TECH_DESIGN_IN_PROGRESS\ngate: BLOCKED\n"
            f"updatedAt: '{workflow_updated}'\n", encoding="utf-8")
        (spec / "manifest.yaml").write_text(
            "version: 2\nartifacts:\n"
            "  - artifactId: ART-1\n    path: .spec/a.md\n    status: REVIEW\n    gate: BLOCKED\n"
            f"    producedAt: '{produced}'\n"
            f"updatedAt: '{manifest_updated}'\n", encoding="utf-8")
        return self.tmp

    def test_clean_pair_is_green(self):
        root = self.build("2026-10-17T12:00:00+08:00", "2026-10-17T12:00:00+08:00", "2026-10-17T11:00:00+08:00")
        self.assertEqual(core.control_drift(root), [],
                         "两处控制文件都不早于产物时必须绿，否则这条检查就是纯噪音")

    def test_workflow_lagging_is_red_and_named(self):
        root = self.build("2026-10-15T00:09:55+08:00", "2026-10-17T12:00:00+08:00", "2026-10-17T11:07:00+08:00")
        errors = core.control_drift(root)
        self.assertEqual(len(errors), 1, f"只应报 workflow 落后一条：{errors}")
        self.assertIn("workflow.yaml updatedAt", errors[0])
        self.assertIn("ART-1", errors[0], "报错必须点名是哪条产物把它顶住了，否则看不出从哪查")

    def test_manifest_self_stale_is_red(self):
        root = self.build("2026-10-17T12:00:00+08:00", "2026-10-15T00:09:55+08:00", "2026-10-17T11:07:00+08:00")
        errors = core.control_drift(root)
        self.assertEqual(len(errors), 1, f"只应报 manifest 自相矛盾一条：{errors}")
        self.assertIn("manifest.yaml updatedAt", errors[0])

    def test_moving_the_artifact_earlier_turns_it_green(self):
        root = self.build("2026-10-17T12:00:00+08:00", "2026-10-17T12:00:00+08:00", "2026-10-17T13:00:00+08:00")
        self.assertTrue(core.control_drift(root), "产物晚于控制文件时必须红，否则比较没生效")
        manifest = root / ".spec/manifest.yaml"
        manifest.write_text(manifest.read_text(encoding="utf-8").replace("13:00:00", "11:00:00"), encoding="utf-8")
        self.assertEqual(core.control_drift(root), [], "把产物时间改早后必须转绿，证明判定由比较驱动")

    def test_missing_control_file_is_not_a_pass(self):
        self.tmp = Path(tempfile.mkdtemp())
        errors = core.control_drift(self.tmp)
        self.assertTrue(errors, "缺文件不得静默绿")
        self.assertIn("不是通过", errors[0])


if __name__ == "__main__":
    unittest.main()
