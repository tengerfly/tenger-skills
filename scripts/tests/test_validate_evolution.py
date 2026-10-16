"""进化台账 before/after 执法的反向对照（plan v2 §3 台账规则 / §5 闭环「记 before→after」那一段）。

规则原文：每条进化必须挂 before/after，无指标一律标「未验证」，禁止写「已优化」。
本文件给它的每一条判据都配对照：合规输入必绿、改坏必红，并且**断言注册表里的判据文本原文**
（只看退出码会把「因无关原因失败」读成回归通过，这是本仓已经付过学费的地方）。

覆盖面：① before/after 两侧数值缺一不可；② 只有文字描述（没数值）必红；③ 出处必须是注册表允许的
可复算量具；④ 缺「效果证据」行必红并指到条目行号；⑤ 写「未验证」是诚实态，放行；⑥ 出现「已优化」
必红；⑦ 判定=未验证 却声称生效 ⇒ 矛盾必红；⑧ 判定值在枚举外 ⇒ 判不了不算通过；⑨ 台账不存在／
判据缺失 ⇒ 报红而不是静默绿；⑩ 模板代码围栏里的示例不得被当成条目（防误伤）；⑪ 判据改自注册表
必须随之改变（证明常量没写死在代码里）。
"""
from __future__ import annotations
import sys, tempfile, unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_core as core

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "governance/obs-registry.yaml"
POLICY = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))["evolutionLedger"]
REASONS = POLICY["reasons"]
LEDGER_REL = str(POLICY["path"])

LEDGER = """# 进化台账

> 条目格式见 Other/skill-evolver/assets/evolution-log-entry-template.md。只增不改。

"""

GOOD_ENTRY = """### E-001 2026-10-16 ui-ux-review（档位：标准）
- 触发信号：issue/UI-UX-Review/2026-10-10/01
- 诊断结论：批次报告的 P0 残留没有回查上游 PRD 版本
- 效果证据：`tsr score` → 总分 before 61.4 → after 78.2
- 判定：已验证
- 回归用例：EV-DR-004
"""


def line_of(text: str, needle: str) -> int:
    """把「指到具体行」的期望也算出来，不写死行号（前缀行数一变写死的号就假绿/假红）。"""
    for number, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return number
    raise AssertionError(f"夹具里没有这一行：{needle}")


def template_fence() -> str:
    """模板原文（含「不得写「已优化」」这类教学措辞与未填占位）——不能被读成条目。"""
    return ("```markdown\n"
            "### E-<序号> <日期> <目标 skill>（档位：<保守|标准|激进>）\n"
            "- 效果证据：`<命令>` → <指标> before <值> → after <值>\n"
            "- 判定：<已验证 | 未验证>——**缺 before/after 只能写「未验证」，不得写「已优化」**\n"
            "```\n\n")


class LedgerMixin(unittest.TestCase):
    def repo(self, body: str | None = None, policy_patch=None) -> tuple:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "governance").mkdir(parents=True)
        registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        if policy_patch:
            policy_patch(registry)
        (root / "governance/obs-registry.yaml").write_text(
            yaml.safe_dump(registry, allow_unicode=True), encoding="utf-8")
        ledger = root / LEDGER_REL
        ledger.parent.mkdir(parents=True, exist_ok=True)
        if body is not None:
            ledger.write_text(body, encoding="utf-8")
        return root, ledger


class ReverseComparisonTests(LedgerMixin):
    def test_compliant_entry_with_before_and_after_is_green(self):
        root, _ = self.repo(LEDGER + GOOD_ENTRY)
        result = core.evolution_audit(root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["counts"]["entries"], 1)
        self.assertEqual(result["counts"]["withProof"], 1)

    def test_missing_after_value_is_red_with_declared_judge_text(self):
        broken = GOOD_ENTRY.replace("before 61.4 → after 78.2", "before 61.4 → after 肉眼好多了")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noAfter"], errors[0])
        self.assertIn(f"{LEDGER_REL}:{line_of(LEDGER + broken, '效果证据')}: ", errors[0])

    def test_missing_before_value_is_red(self):
        broken = GOOD_ENTRY.replace("before 61.4 → after 78.2", "before 说不清 → after 78.2")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noBefore"], errors[0])

    def test_prose_only_evidence_is_red_as_no_number(self):
        broken = GOOD_ENTRY.replace("before 61.4 → after 78.2", "明显好用了不少")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noNumber"], errors[0])
        self.assertIn("明显好用了不少", errors[0])       # 报的是本行原文，不是空泛指控

    def test_unreproducible_source_is_red(self):
        broken = GOOD_ENTRY.replace("`tsr score`", "`我的记忆`")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noSource"], errors[0])

    def test_missing_evidence_line_is_red_at_entry_heading(self):
        broken = GOOD_ENTRY.replace("- 效果证据：`tsr score` → 总分 before 61.4 → after 78.2\n", "")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noProofField"], errors[0])
        self.assertIn(f"{LEDGER_REL}:{line_of(LEDGER + broken, '### E-001')}: ", errors[0])

    def test_honest_unverified_without_metrics_is_green(self):
        # 写「未验证」是诚实态：允许通过，不逼人造数
        honest = GOOD_ENTRY.replace("- 效果证据：`tsr score` → 总分 before 61.4 → after 78.2",
                                    "- 效果证据：待补（还没跑基线）").replace("判定：已验证", "判定：未验证")
        root, _ = self.repo(LEDGER + honest)
        result = core.evolution_audit(root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["counts"]["honest"], 1)

    def test_forbidden_claim_optimized_is_red_even_with_numbers(self):
        # plan §3「禁止写已优化」是硬规则：挂了 before/after 也不许写「已优化」
        offender = GOOD_ENTRY.replace("判定：已验证", "判定：已优化")
        root, _ = self.repo(LEDGER + offender)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["forbiddenWord"], errors[0])
        self.assertIn(f"{LEDGER_REL}:{line_of(LEDGER + offender, '判定')}: ", errors[0])

    def test_unverified_verdict_but_claiming_body_is_red_as_contradiction(self):
        conflict = GOOD_ENTRY.replace("判定：已验证", "判定：未验证").replace(
            "- 回归用例：EV-DR-004", "- 回归用例：规则已生效，只是没补用例")
        root, _ = self.repo(LEDGER + conflict)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["contradiction"], errors[0])

    def test_verdict_outside_the_enum_is_red_not_passed(self):
        dodgy = GOOD_ENTRY.replace("判定：已验证", "判定：基本没问题")
        root, _ = self.repo(LEDGER + dodgy)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["badVerdict"], errors[0])

    def test_claim_in_body_without_evidence_line_is_red(self):
        # 没写判定行也没效果证据行，但正文声称「已生效」⇒ 仍按「声称生效」要求指标
        body = ("### E-002 2026-10-16 backend-dev（档位：保守）\n"
                "- 触发信号：用户点名\n"
                "- 改动清单：SKILL.md:12-18 补一段\n"
                "- 判定：未验证（本次已生效，效果不错）\n")
        root, _ = self.repo(LEDGER + body)
        errors = core.check_evolution(root)
        self.assertTrue(any(REASONS["contradiction"] in error for error in errors), errors)
        self.assertTrue(any(REASONS["noProofField"] in error for error in errors), errors)

    def test_two_entries_only_the_offender_is_reported(self):
        other = GOOD_ENTRY.replace("E-001", "E-002")
        broken = other.replace("before 61.4 → after 78.2", "before 61.4 → after 待补")
        text = LEDGER + GOOD_ENTRY + "\n" + broken
        root, _ = self.repo(text)
        result = core.evolution_audit(root)
        self.assertEqual(result["counts"]["entries"], 2)
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn(REASONS["noAfter"], result["errors"][0])
        # 红必须落在 E-002 的那一行上，不是把合规的 E-001 一起打了
        self.assertEqual([entry["line"] for entry in result["entries"] if entry["errors"]],
                         [line_of(text, "### E-002")])
        self.assertEqual(int(result["errors"][0].split(":")[1]), line_of(text, "after 待补"))

    def test_quoted_instruction_is_not_read_as_a_claim(self):
        # 「不得写「已优化」」这类教学引文不得把整条判成违规（防误伤说明文字）
        note = GOOD_ENTRY + "- 备注：台账规则见 plan §3，不得写「已优化」\n"
        root, _ = self.repo(LEDGER + note)
        self.assertEqual(core.check_evolution(root), [])


class FalsePositiveGuardTests(LedgerMixin):
    def test_template_code_fence_is_not_read_as_an_entry(self):
        root, _ = self.repo(LEDGER + template_fence() + GOOD_ENTRY)
        result = core.evolution_audit(root)
        self.assertEqual(result["counts"]["entries"], 1, "模板示例不能被当成条目判红")
        self.assertEqual(result["errors"], [])

    def test_repo_ledger_current_state_has_nothing_to_judge_yet(self):
        root, _ = self.repo((ROOT / LEDGER_REL).read_text(encoding="utf-8"))
        result = core.evolution_audit(root)
        self.assertEqual(result["counts"]["entries"], 0)
        self.assertEqual(result["errors"], [])
        self.assertIn("没有可判对象", core.render_evolution(result))


class PolicyDrivenTests(LedgerMixin):
    def test_missing_ledger_is_red_not_silently_green(self):
        root, _ = self.repo(None)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["missingLedger"], errors[0])

    def test_ledger_path_outside_project_is_refused(self):
        root, _ = self.repo(LEDGER + GOOD_ENTRY)
        errors = core.check_evolution(root, ledger="../somewhere/进化台账.md")
        self.assertEqual(len(errors), 1)
        self.assertIn("台账路径非法", errors[0])

    def test_absent_policy_section_refuses_to_guess(self):
        root, _ = self.repo(LEDGER + GOOD_ENTRY,
                            policy_patch=lambda registry: registry.pop("evolutionLedger"))
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn("未声明 evolutionLedger 判据", errors[0])

    def test_incomplete_policy_refuses_default_values(self):
        def thin(registry):
            del registry["evolutionLedger"]["acceptedSources"]
        root, _ = self.repo(LEDGER + GOOD_ENTRY, policy_patch=thin)
        self.assertIn("缺必需判据键", core.check_evolution(root)[0])

    def test_loosening_the_registry_loosens_the_verdict(self):
        # 判据常量来自注册表：把「我的记忆」加进允许量具 ⇒ 同一条台账由红变绿
        broken = GOOD_ENTRY.replace("`tsr score`", "`我的记忆`")
        strict, _ = self.repo(LEDGER + broken)
        self.assertIn(REASONS["noSource"], core.check_evolution(strict)[0])

        def loosen(registry):
            registry["evolutionLedger"]["acceptedSources"].append("我的记忆")
        relaxed, _ = self.repo(LEDGER + broken, policy_patch=loosen)
        self.assertEqual(core.check_evolution(relaxed), [])

    def test_tightening_the_registry_tightens_the_verdict(self):
        # 反向：把「顺手」加进 claimWords ⇒ 原本不声称生效的条目立刻被要求指标
        quiet = GOOD_ENTRY.replace("判定：已验证", "判定：未验证").replace(
            "- 效果证据：`tsr score` → 总分 before 61.4 → after 78.2", "- 效果证据：待补")
        base, _ = self.repo(LEDGER + quiet)
        self.assertEqual(core.check_evolution(base), [])

        def tighten(registry):
            registry["evolutionLedger"]["claimWords"].append("顺手")
        body = quiet.replace("issue/UI-UX-Review/2026-10-10/01", "顺手改了措辞（没有 issue 来源）")
        self.assertIn("顺手", body)                    # 夹具自己先要成立，否则是假对照
        strict, _ = self.repo(LEDGER + body, policy_patch=tighten)
        errors = core.check_evolution(strict)
        self.assertTrue(any(REASONS["noProofField"] in error or REASONS["noNumber"] in error
                            for error in errors), errors)


class CliTests(LedgerMixin):
    def run_cli(self, root) -> tuple:
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = core.main(["evolution", "--project-root", str(root)])
        return code, out.getvalue(), err.getvalue()

    def test_cli_reports_this_repo_ledger_as_zero_entries_and_exits_green(self):
        code, out, _ = self.run_cli(ROOT)
        self.assertEqual(code, 0)
        self.assertIn("台账条目 0 条", out)
        self.assertIn("evolution validation passed", out)

    def test_cli_red_output_names_the_entry_line_and_the_missing_side(self):
        broken = GOOD_ENTRY.replace("before 61.4 → after 78.2", "before 61.4 → after 待补")
        text = LEDGER + broken
        root, _ = self.repo(text)
        code, out, err = self.run_cli(root)
        self.assertEqual(code, 1)
        self.assertIn(REASONS["noAfter"], err)
        self.assertIn(f"{LEDGER_REL}:{line_of(text, '效果证据')}: ", err)
        self.assertIn("evolution validation failed: 1 error(s)", out)


class GateWiringTests(LedgerMixin):
    def test_evolution_check_runs_inside_the_system_gate(self):
        # 「可进门禁」必须可验：把台账改坏，system 必须带出 evolution 的红
        broken = GOOD_ENTRY.replace("before 61.4 → after 78.2", "before 61.4 → after 待补")
        root, _ = self.repo(LEDGER + broken)
        (root / ".spec").mkdir()
        with redirect_stderr(StringIO()):
            errors = core.check_system(root, skip_fixtures=True, skip_knowledge=True)
        self.assertTrue([error for error in errors
                         if error.startswith("evolution:") and REASONS["noAfter"] in error], errors)


if __name__ == "__main__":
    unittest.main()
