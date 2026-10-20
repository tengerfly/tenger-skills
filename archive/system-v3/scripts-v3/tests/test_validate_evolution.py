"""进化台账 before/after + commit/回滚指针执法的反向对照（plan v2 §3 台账规则 / §5 闭环后两段）。

判据原文：每条进化必须挂 before/after，无指标一律标「未验证」，禁止写「已优化」；
本轮再钉住 §5 的后两格——**落账 commit 指针**与**回滚指针**必须机械验真。

本文件对每条判据都做反向对照：合规输入必绿、改坏必红，并且**断言注册表里的判据文本原文**
（只看退出码会把「因无关原因失败」读成回归通过，这是本仓已经付过学费的地方）。

覆盖面：
① 必需字段行（效果证据／判定／落账 commit／回滚方式）缺任一条必红；
② before/after 缺一侧、或只有文字没数值 ⇒ 必红；N/A 必须是「N/A（原因）」，写「待补」不算；
③ 出处必须是注册表允许的可复算量具；
④ **commit 指针写成一个 git 里不存在的 sha ⇒ 必红**（本仓最常见的造假就是留个漂亮字符串）；
⑤ 回滚指针必须是可执行目标（`git revert`／`git checkout`）且指向可验真的 commit；
⑥ 「未验证」是合法态（数值取不到就 N/A + 原因），裸「已优化」是非法态；
⑦ 判定=未验证 却声称生效 ⇒ 矛盾必红；判定值枚举外 ⇒ 判不了不算通过；
⑧ 台账不存在／判据缺失／git 查不了 ⇒ 报红，不静默绿（不得把「查不了」读成「过了」）；
⑨ 模板代码围栏里的示例不得被当成条目；⑩ 判据改自注册表必须随之改变。
"""
from __future__ import annotations
import re, shutil, subprocess, sys, tempfile, unittest
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
FIELDS = POLICY["fields"]
LEDGER_REL = str(POLICY["path"])


def _head_sha():
    """取一个真实存在、可被只读 git 查询验真的 commit 当合规夹具（写死 sha 会随历史腐烂）。"""
    git = shutil.which("git")
    if not git:
        return None
    try:
        probe = subprocess.run([git, "-C", str(ROOT), "rev-parse", "HEAD"],
                               capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return (probe.stdout or "").strip() or None


REAL_SHA = _head_sha()
# 40 位十六进制：格式完全合规，但 git 对象库里不存在——正是「漂亮字符串过关」那种造假
FAKE_SHA = "deadbeef" + "0123456789abcdef" * 2

LEDGER = """# 进化台账

> 条目格式见 Other/skill-evolver/assets/evolution-log-entry-template.md。只增不改。

"""


def entry(sha: str = REAL_SHA or "0" * 40) -> str:
    """合规条目模板：四项必需字段齐、before/after 都是数值、出处是允许量具。"""
    return f"""### E-001 2026-10-16 ui-ux-review（档位：标准）
- 触发信号：issue/UI-UX-Review/2026-10-10/01
- 诊断结论：批次报告的 P0 残留没有回查上游 PRD 版本
- 效果证据：`tsr score` → 总分 before 61.4 → after 78.2
- 判定：已验证
- 回归用例：EV-DR-004
- 落账 commit：`{sha}`
- 回滚方式：`git revert {sha}`
"""


GOOD = entry()

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
            "- 落账 commit：`<sha>`\n"
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

    def require_git(self) -> None:
        if not REAL_SHA:
            self.skipTest("本机没有可用 git ⇒ 无法构造「真实存在的 commit」正向对照（不假装验过）")


class ReverseComparisonTests(LedgerMixin):
    def test_compliant_entry_is_green(self):
        self.require_git()
        root, _ = self.repo(LEDGER + GOOD)
        result = core.evolution_audit(root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["counts"]["entries"], 1)
        self.assertEqual(result["counts"]["withProof"], 1)
        self.assertEqual(result["counts"]["pointersVerified"], 1)

    def test_deleting_the_after_metric_is_red(self):
        # 反向对照①：把 after 侧数值删掉 ⇒ 必须红，并断言判据原文
        broken = GOOD.replace("before 61.4 → after 78.2", "before 61.4 → after")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noAfter"], errors[0])
        self.assertIn(f"{LEDGER_REL}:{line_of(LEDGER + broken, '效果证据')}: ", errors[0])

    def test_deleting_the_before_metric_is_red(self):
        broken = GOOD.replace("before 61.4 → after 78.2", "before → after 78.2")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noBefore"], errors[0])

    def test_prose_only_after_value_is_red(self):
        broken = GOOD.replace("before 61.4 → after 78.2", "before 61.4 → after 肉眼好多了")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noAfter"], errors[0])

    def test_prose_only_evidence_is_red_as_no_number(self):
        broken = GOOD.replace("before 61.4 → after 78.2", "明显好用了不少")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noNumber"], errors[0])
        self.assertIn("明显好用了不少", errors[0])       # 报的是本行原文，不是空泛指控

    def test_placeholder_todo_is_red_not_honest_na(self):
        # 「待补（还没跑基线）」是留白，不是显式 N/A + 原因；合法诚实态必须写 N/A（原因）
        broken = GOOD.replace("before 61.4", "before 待补（还没跑基线）")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noBefore"], errors[0])
        self.assertIn("待补", errors[0])

    def test_unreproducible_source_is_red(self):
        broken = GOOD.replace("`tsr score`", "`我的记忆`")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noSource"], errors[0])

    def test_missing_evidence_line_is_red_at_entry_heading(self):
        broken = GOOD.replace("- 效果证据：`tsr score` → 总分 before 61.4 → after 78.2\n", "")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noProofField"], errors[0])
        self.assertIn(f"{LEDGER_REL}:{line_of(LEDGER + broken, '### E-001')}: ", errors[0])

    def test_missing_commit_field_is_red(self):
        # 反向对照②：删掉「落账 commit」整行 ⇒ 缺必需字段红
        broken = GOOD.replace(f"- 落账 commit：`{REAL_SHA}`\n", "")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(str(REASONS["missingField"]).replace("{field}", FIELDS["commit"]), errors[0])
        self.assertIn(f"{LEDGER_REL}:{line_of(LEDGER + broken, '### E-001')}: ", errors[0])

    def test_missing_rollback_field_is_red(self):
        broken = GOOD.replace(f"- 回滚方式：`git revert {REAL_SHA}`\n", "")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(str(REASONS["missingField"]).replace("{field}", FIELDS["rollback"]), errors[0])

    def test_fake_commit_pointer_is_red(self):
        # 反向对照③（本仓最常见的造假）：sha 格式完全合规，但 git 对象库里没有它
        self.require_git()
        broken = GOOD.replace(REAL_SHA, FAKE_SHA)
        self.assertIn(FAKE_SHA, broken)                  # 夹具自己先要成立，否则是假对照
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertTrue(errors, "引用不存在的 commit 必须判红，不许留个漂亮字符串过关")
        self.assertTrue(all(REASONS["commitNotFound"] in error for error in errors), errors)
        self.assertEqual(len(errors), 2)                 # 落账 commit 与回滚指针各一处
        self.assertIn(FAKE_SHA, errors[0])               # 报的是那条查无此物的指针本身
        self.assertIn(POLICY["git"]["verifyCommand"], errors[0])   # 还写清是按哪条命令验的

    def test_commit_pointer_without_sha_is_red(self):
        broken = GOOD.replace(f"- 落账 commit：`{REAL_SHA}`",
                              "- 落账 commit：今天那个提交（详见聊天记录）")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noCommitPointer"], errors[0])

    def test_rollback_must_be_an_executable_target(self):
        # 有 commit 指针但没有可执行回滚动作（只说手工改回去）⇒ 按「无回滚目标」判红
        broken = GOOD.replace(f"- 回滚方式：`git revert {REAL_SHA}`",
                              f"- 回滚方式：手工把措辞改回去，指针 `{REAL_SHA}`")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["noRollbackTarget"], errors[0])

    def test_honest_unverified_with_na_and_reason_is_green(self):
        # ⑤「未验证」是合法态：数值取不到就写 N/A + 原因，不逼人造数
        self.require_git()
        honest = GOOD.replace("before 61.4 → after 78.2",
                              "before N/A（该量具当时还没落地，无历史命令可复算） → after 78.2")
        honest = honest.replace("判定：已验证", "判定：未验证")
        root, _ = self.repo(LEDGER + honest)
        result = core.evolution_audit(root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["counts"]["honest"], 1)

    def test_na_without_reason_is_red(self):
        broken = GOOD.replace("before 61.4", "before N/A").replace("判定：已验证", "判定：未验证")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["badNaWithoutReason"], errors[0])

    def test_na_side_cannot_claim_verified(self):
        # 声称「已验证」却有一侧是 N/A ⇒ 没有实测数值就不许标已验证
        broken = GOOD.replace("before 61.4", "before N/A（取不到，原因见诊断结论）")
        root, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["naWithClaimed"], errors[0])

    def test_forbidden_claim_optimized_is_red_even_with_numbers(self):
        # 反向对照④：plan §3「禁止写已优化」是硬规则，挂了 before/after 也不许写
        offender = GOOD.replace("判定：已验证", "判定：已优化")
        root, _ = self.repo(LEDGER + offender)
        errors = core.check_evolution(root)
        self.assertIn(REASONS["forbiddenWord"], errors[0])
        self.assertIn(f"{LEDGER_REL}:{line_of(LEDGER + offender, '判定')}: ", errors[0])

    def test_unverified_verdict_but_claiming_body_is_red_as_contradiction(self):
        self.require_git()
        conflict = GOOD.replace("判定：已验证", "判定：未验证").replace(
            "- 回归用例：EV-DR-004", f"- 回归用例：规则已生效，只是没补用例")
        root, _ = self.repo(LEDGER + conflict)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["contradiction"], errors[0])

    def test_verdict_outside_the_enum_is_red_not_passed(self):
        dodgy = GOOD.replace("判定：已验证", "判定：基本没问题")
        root, _ = self.repo(LEDGER + dodgy)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["badVerdict"], errors[0])

    def test_claim_in_body_without_evidence_line_is_red(self):
        body = ("### E-002 2026-10-16 backend-dev（档位：保守）\n"
                "- 触发信号：用户点名\n"
                "- 改动清单：SKILL.md:12-18 补一段\n"
                "- 判定：未验证（本次已生效，效果不错）\n"
                "- 落账 commit：`0000000000000000000000000000000000000000`\n"
                "- 回滚方式：`git revert 0000000000000000000000000000000000000000`\n")
        root, _ = self.repo(LEDGER + body)
        errors = core.check_evolution(root)
        self.assertTrue(any(REASONS["contradiction"] in error for error in errors), errors)
        self.assertTrue(any(REASONS["noProofField"] in error for error in errors), errors)

    def test_two_entries_only_the_offender_is_reported(self):
        self.require_git()
        other = entry().replace("E-001", "E-002")
        broken = other.replace("before 61.4 → after 78.2", "before 61.4 → after 待补")
        text = LEDGER + GOOD + "\n" + broken
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
        note = GOOD + "- 备注：台账规则见 plan §3，不得写「已优化」\n"
        root, _ = self.repo(LEDGER + note)
        self.assertEqual(core.check_evolution(root), [])


class FalsePositiveGuardTests(LedgerMixin):
    def test_template_code_fence_is_not_read_as_an_entry(self):
        root, _ = self.repo(LEDGER + template_fence() + GOOD)
        result = core.evolution_audit(root)
        self.assertEqual(result["counts"]["entries"], 1, "模板示例不能被当成条目判红")

    def test_real_repo_ledger_entries_pass_the_same_judge(self):
        # 真实台账不是空集：同一套判据必须在真条目上跑绿，且每条指针都可验真
        text = (ROOT / LEDGER_REL).read_text(encoding="utf-8")
        root, _ = self.repo(text)
        result = core.evolution_audit(root)
        self.assertGreaterEqual(result["counts"]["entries"], 1,
                                "台账仍是 0 条 ⇒ 执法只是空集通过，没达标")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["counts"]["pointersVerified"], result["counts"]["entries"])

    def test_real_repo_ledger_is_not_an_empty_set(self):
        result = core.evolution_audit(ROOT)
        self.assertGreaterEqual(result["counts"]["entries"], 1)
        self.assertGreaterEqual(result["counts"]["pointersVerified"], 1)


class GitVerificationTests(LedgerMixin):
    """commit 指针验真本身的对照：只读、三态、查不了不判绿。"""

    def test_readonly_only_helpers_are_used(self):
        source = (ROOT / "scripts/validate_core.py").read_text(encoding="utf-8")
        for banned in ("git add", "git commit", "git push", "git stash",
                       "git reset", "git checkout ", "git rm", 'git", "checkout"'):
            self.assertNotIn(banned, source, f"执法器里不许出现写操作型 git 命令：{banned}")
        self.assertIn("cat-file", source)                 # 只读查询必须在

    def test_existing_commit_verifies_true(self):
        self.require_git()
        self.assertIs(core.commit_exists(core.git_repos(ROOT), REAL_SHA), True)

    def test_short_sha_of_existing_commit_verifies_true(self):
        self.require_git()
        self.assertIs(core.commit_exists(core.git_repos(ROOT), REAL_SHA[:7]), True)

    def test_fabricated_commit_verifies_false(self):
        self.assertIs(core.commit_exists(core.git_repos(ROOT), FAKE_SHA), False)

    def test_unreachable_repo_is_none_not_true(self):
        # 查不了 ⇒ None（既不算存在也不算不存在）；审计层据此判红，绝不判绿
        self.assertIsNone(core.commit_exists([], REAL_SHA or "abc1234"))

    def test_object_that_is_not_a_commit_is_rejected(self):
        self.require_git()
        blob = subprocess.run([shutil.which("git"), "-C", str(ROOT), "rev-parse",
                               f"{REAL_SHA}^{{tree}}"], capture_output=True, text=True)
        tree = (blob.stdout or "").strip()
        if not tree:
            self.skipTest("取不到 tree 对象 ⇒ 这一条对照做不了（不假装验过）")
        self.assertIs(core.commit_exists(core.git_repos(ROOT), tree), False,
                      "非 commit 对象（tree/blob）不许当 commit 指针过关")


class PolicyDrivenTests(LedgerMixin):
    def test_missing_ledger_is_red_not_silently_green(self):
        root, _ = self.repo(None)
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn(REASONS["missingLedger"], errors[0])

    def test_ledger_path_outside_project_is_refused(self):
        root, _ = self.repo(LEDGER + GOOD)
        errors = core.check_evolution(root, ledger="../somewhere/进化台账.md")
        self.assertEqual(len(errors), 1)
        self.assertIn("台账路径非法", errors[0])

    def test_absent_policy_section_refuses_to_guess(self):
        root, _ = self.repo(LEDGER + GOOD,
                            policy_patch=lambda registry: registry.pop("evolutionLedger"))
        errors = core.check_evolution(root)
        self.assertEqual(len(errors), 1)
        self.assertIn("未声明 evolutionLedger 判据", errors[0])

    def test_incomplete_policy_refuses_default_values(self):
        def thin(registry):
            del registry["evolutionLedger"]["acceptedSources"]
        root, _ = self.repo(LEDGER + GOOD, policy_patch=thin)
        self.assertIn("缺必需判据键", core.check_evolution(root)[0])

    def test_new_required_keys_are_enforced(self):
        # 新增的执法位同样不许用默认值冒充实装
        for key in ("requiredFields", "commitPointerPattern", "rollbackTargetPattern", "git"):
            def thin(registry, target=key):
                del registry["evolutionLedger"][target]
            root, _ = self.repo(LEDGER + GOOD, policy_patch=thin)
            self.assertIn("缺必需判据键", core.check_evolution(root)[0], f"{key} 没被钉住")

    def test_loosening_the_registry_loosens_the_verdict(self):
        # 判据常量来自注册表：把「我的记忆」加进允许量具 ⇒ 同一条台账由红变绿
        broken = GOOD.replace("`tsr score`", "`我的记忆`")
        strict, _ = self.repo(LEDGER + broken)
        self.assertIn(REASONS["noSource"], core.check_evolution(strict)[0])

        def loosen(registry):
            registry["evolutionLedger"]["acceptedSources"].append("我的记忆")
        relaxed, _ = self.repo(LEDGER + broken, policy_patch=loosen)
        self.assertEqual(core.check_evolution(relaxed), [])

    def test_registry_controls_which_field_names_are_required(self):
        # 反向：把必需字段改成只要求判定 ⇒ 「落账 commit」缺失不再报红（证明名单没写死在代码里）
        missing_commit = str(REASONS["missingField"]).replace("{field}", FIELDS["commit"])
        broken = GOOD.replace(f"- 落账 commit：`{REAL_SHA}`\n", "")
        strict, _ = self.repo(LEDGER + broken)
        errors = core.check_evolution(strict)
        self.assertEqual(len(errors), 1)
        self.assertIn(missing_commit, errors[0])

        def rename(registry):
            registry["evolutionLedger"]["requiredFields"] = ["判定"]
        loose, _ = self.repo(LEDGER + broken, policy_patch=rename)
        self.assertNotIn(missing_commit, " ".join(core.check_evolution(loose)))

    def test_tightening_the_registry_tightens_the_verdict(self):
        # 把「顺手」加进 claimWords ⇒ 原本不声称生效的条目立刻被要求指标
        quiet = GOOD.replace("判定：已验证", "判定：未验证").replace(
            "before 61.4 → after 78.2",
            "before N/A（还没跑基线，不拿估算冒充实测） → after N/A（同上原因，本轮未实测）")
        base, _ = self.repo(LEDGER + quiet)
        self.assertEqual(core.check_evolution(base), [])

        def tighten(registry):
            registry["evolutionLedger"]["claimWords"].append("顺手")
        body = quiet.replace("issue/UI-UX-Review/2026-10-10/01", "顺手改了措辞（没有 issue 来源）")
        self.assertIn("顺手", body)
        strict, _ = self.repo(LEDGER + body, policy_patch=tighten)
        errors = core.check_evolution(strict)
        self.assertTrue(any(REASONS["contradiction"] in error for error in errors), errors)


class CliTests(LedgerMixin):
    def run_cli(self, root) -> tuple:
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = core.main(["evolution", "--project-root", str(root)])
        return code, out.getvalue(), err.getvalue()

    def test_cli_reports_real_entries_and_exits_green(self):
        code, out, _ = self.run_cli(ROOT)
        self.assertEqual(code, 0)
        self.assertIn("evolution validation passed", out)
        audit = core.evolution_audit(ROOT)
        self.assertIn(f"台账条目 **{audit['counts']['entries']}** 条", out)
        self.assertIn(f"指针验真 {audit['counts']['pointersVerified']} 条", out)

    def test_cli_zero_entry_pass_is_labelled_as_empty_set(self):
        # 空集通过不许和达标混读：退出行自己要把「空集」写出来
        empty, _ = self.repo(LEDGER)
        code, out, _ = self.run_cli(empty)
        self.assertEqual(code, 0)
        self.assertIn("空集通过", out)
        self.assertIn("没有条目可判", out)

    def test_cli_red_output_names_the_entry_line_and_the_missing_side(self):
        broken = GOOD.replace("before 61.4 → after 78.2", "before 61.4 → after 待补")
        text = LEDGER + broken
        root, _ = self.repo(text)
        code, out, err = self.run_cli(root)
        self.assertEqual(code, 1)
        self.assertIn(REASONS["noAfter"], err)
        self.assertIn(f"{LEDGER_REL}:{line_of(text, '效果证据')}: ", err)
        self.assertIn("evolution validation failed: 1 error(s)", out)

    def test_cli_reports_fabricated_pointer_as_red(self):
        self.require_git()
        text = LEDGER + GOOD.replace(REAL_SHA, FAKE_SHA)
        root, _ = self.repo(text)
        code, out, err = self.run_cli(root)
        self.assertEqual(code, 1)
        self.assertIn(REASONS["commitNotFound"], err)
        self.assertIn("evolution validation failed", out)


class GateWiringTests(LedgerMixin):
    def test_evolution_check_runs_inside_the_system_gate(self):
        # 「可进门禁」必须可验：把台账改坏，system 必须带出 evolution 的红
        broken = GOOD.replace("before 61.4 → after 78.2", "before 61.4 → after 待补")
        root, _ = self.repo(LEDGER + broken)
        (root / ".spec").mkdir()
        with redirect_stderr(StringIO()):
            errors = core.check_system(root, skip_fixtures=True, skip_knowledge=True)
        self.assertTrue([error for error in errors
                         if error.startswith("evolution:") and REASONS["noAfter"] in error], errors)

    def test_fabricated_pointer_also_fails_the_system_gate(self):
        self.require_git()
        root, _ = self.repo(LEDGER + GOOD.replace(REAL_SHA, FAKE_SHA))
        (root / ".spec").mkdir()
        with redirect_stderr(StringIO()):
            errors = core.check_system(root, skip_fixtures=True, skip_knowledge=True)
        self.assertTrue([error for error in errors
                         if error.startswith("evolution:")
                         and REASONS["commitNotFound"] in error], errors)


if __name__ == "__main__":
    unittest.main()
