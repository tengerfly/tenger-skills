"""目标台账执法（governance/goal-plan.yaml）的反向对照。

这条执法防的是流程自身失效，不是产品缺陷——本仓真的发生过：正文注记说某项 ☐→◐、表格行还写 ☐、
计数行却按 ◐5 记（三处互斥），面板也漂过 doing vs ☑。每条负向对照都断言**具体判据文本**，
且夹具基线必须先全绿，红点才能归因到被改坏的那一处：

① done 没挂依据／依据回查失败（假 commit、不存在的路径、行号超出文件、没写行号）⇒ 红；
   没标 done 的条目依据坏了也照样报（别攒到收口才炸）；
② 状态出三态枚举／statuses 节自己长出新态 ⇒ 红（政策上就写死「部分完成不算完成」）；
③ ◐/☐ 没写 blockedBy／条目缺必需字段 ⇒ 红；
④ 与台账行内状态／计数行／行数不一致 ⇒ 红；找不到计数行、台账读不动也算红；
⑤ next 指针缺失、指向不存在的 id、指向已 done 的条目 ⇒ 红；
⑥ 面板状态漂移 ⇒ 红；面板不在本机只报「未核」，既不计红也不计绿（硬约束 A：执法不绑宿主路径）；
⑦ 真仓自证：本仓此刻 0 错，且 goal-plan.yaml 必须存在（否则「删文件即免检」又回来了）。
"""
from __future__ import annotations
import copy, sys, tempfile, unittest
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_core as core

ROOT = Path(__file__).resolve().parents[2]
REAL = yaml.safe_load((ROOT / "governance/goal-plan.yaml").read_text(encoding="utf-8"))
PROOF, POINTER = REAL["proofRules"], REAL["nextRules"]
MARK = {"done": "☑ 完成", "doing": "◐ 进行中", "todo": "☐ 未完成"}
FALLBACK_COMMIT = "4c46167"          # 本仓真实存在的 commit：只给夹具当依据，真依据由 RealRepoTests 直核
GHOST_COMMIT = "deadbee"             # 七位十六进制，形状合法但不存在——形状合法才会被弱检查放过


def entry_of(data, goal_id):
    return next(item for item in data["goals"] if item["id"] == goal_id)


def ledger_text(data):
    """按 yaml 生成台账表格与计数行：基线夹具两头一致，之后逐条只改坏一处。"""
    rows = ["| # | 层 | 目标项 | 状态 | 依据 |", "| --- | --- | --- | --- | --- |"]
    for entry in data["goals"]:
        rows.append(f"| {entry['ledgerRow']} | {entry['layer']} | {entry['label']} "
                    f"| {MARK.get(str(entry['status']), '◑ 出枚举')} | 夹具依据 |")
    counts = Counter(str(entry["status"]) for entry in data["goals"])
    rows += ["", f"**计数**：☑ 完成 {counts['done']} ｜ ◐ 进行中 {counts['doing']} "
                 f"｜ ☐ 未完成 {counts['todo']}（共 {len(data['goals'])}）",
             "", "## 下一格（唯一指针 · 每轮必须改写后再提交）",
             f"- **当前下一格**：{data['next']['task']}"]
    return "\n".join(rows) + "\n"


def panel_text(data, overrides=()):
    blocks = []
    for entry in data["goals"]:
        status = dict(overrides).get(entry["panelId"], entry["status"])
        blocks.append(f"  {{\n    id: '{entry['panelId']}',\n    status: '{status}',\n  }},")
    return "const GOALS = [\n" + "\n".join(blocks) + "\n];\n"


class Fixture(unittest.TestCase):
    def build(self, mutate=None, with_panel=True, panel_overrides=()):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        data = copy.deepcopy(REAL)
        for entry in data["goals"]:
            commits = list((entry.get("basis") or {}).get("commits") or [])
            entry["basis"] = {"commits": commits or ([FALLBACK_COMMIT] if entry["status"] == "done" else []),
                              "files": []}
        data["sources"]["panel"] = "panel.canvas.tsx"       # 夹具里面板是仓内相对路径
        ledger = None
        if mutate:
            ledger = mutate(data)
        (root / "governance").mkdir(parents=True)
        (root / "governance/goal-plan.yaml").write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        ledger_path = root / data["sources"]["ledger"]
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger_path.write_text(ledger if ledger is not None else ledger_text(data), encoding="utf-8")
        if with_panel:
            (root / "panel.canvas.tsx").write_text(self.panel_of(data, panel_overrides), encoding="utf-8")
        self.root, self.data = root, data
        return root, data

    @staticmethod
    def panel_of(data, overrides=()):
        return panel_text(data, overrides)

    def errors(self, root=None):
        return "\n".join(core.goalplan_audit(root or self.root)["errors"])


class BaselineTests(Fixture):
    def test_consistent_fixture_is_clean(self):
        root, _ = self.build()
        result = core.goalplan_audit(root)
        self.assertTrue(result["applies"])
        self.assertEqual(result["errors"], [], f"基线夹具本该全绿：{result['errors']}")
        self.assertGreater(result["counts"]["verified"], 0)


class ProofTests(Fixture):
    def test_done_without_any_basis_is_red(self):
        self.build(lambda data: entry_of(data, "loop-sink").update({"basis": {"commits": [], "files": []}}))
        text = self.errors()
        self.assertIn("标 ☑(done) 却没挂可回查依据", text)
        self.assertIn(PROOF["naIsNotProof"], text)

    def test_ghost_commit_pointer_is_red(self):
        self.build(lambda data: entry_of(data, "loop-sink").update({"basis": {"commits": [GHOST_COMMIT]}}))
        text = self.errors()
        self.assertIn("在该仓不存在", text)
        self.assertIn(PROOF["doneNeeds"], text)

    def test_missing_file_in_basis_is_red(self):
        self.build(lambda data: entry_of(data, "loop-sink").update(
            {"basis": {"commits": [], "files": ["scripts/obs/no_such_module.py:12"]}}))
        text = self.errors()
        self.assertIn("指的文件不存在", text)
        self.assertIn("回查落点失效", text)

    def test_line_number_beyond_file_end_is_red(self):
        def mutate(data):
            entry_of(data, "loop-sink").update({"basis": {"commits": [], "files": ["tiny.md:9"]}})
            return None
        root, _ = self.build(mutate)
        (root / "tiny.md").write_text("只有一行\n", encoding="utf-8")
        self.assertIn("行号超出文件实际 1 行", self.errors(root))

    def test_basis_without_line_number_is_red(self):
        self.build(lambda data: entry_of(data, "loop-sink").update(
            {"basis": {"commits": [], "files": ["scripts/tsr.py"]}}))
        self.assertIn("不是 path:行号 的写法", self.errors())

    def test_broken_basis_on_doing_entry_is_still_reported(self):
        # ◐ 条目依据坏了不判「缺依据」（它还没声称完成），但必须如实报——别攒到收口才炸
        self.build(lambda data: entry_of(data, "loop-l2").update({"basis": {"commits": [GHOST_COMMIT]}}))
        text = self.errors()
        self.assertIn("的依据有 1 条回查失败", text)
        self.assertIn("别攒到收口才炸", text)


class StatusTests(Fixture):
    def test_status_outside_three_states_is_red(self):
        def mutate(data):
            entry_of(data, "loop-sink")["status"] = "partial"
            entry_of(data, "loop-sink")["blockedBy"] = "出枚举的条目也要有说明才不撞两条判据"
        self.build(mutate, with_panel=False)
        text = self.errors()
        self.assertIn("不在三态枚举内", text)
        self.assertIn("不允许「部分完成算完成」", text)

    def test_registry_growing_a_new_state_refuses_to_run(self):
        root, _ = self.build(lambda data: data["statuses"].update({"partial": "差不多完成"}))
        self.assertIn("出现三态之外的值", core.check_goalplan(root)[0])

    def test_doing_without_blocked_reason_is_red(self):
        self.build(lambda data: entry_of(data, "loop-l2").update({"blockedBy": ""}))
        text = self.errors()
        self.assertIn("却没写 blockedBy", text)
        self.assertIn("没写原因的「进行中」等于没人认领", text)

    def test_entry_missing_required_field_is_red(self):
        def mutate(data):
            entry_of(data, "loop-l2").pop("criteria")
            return ledger_text(data)
        self.build(mutate)
        text = self.errors()
        self.assertIn("缺必需字段 ['criteria']", text)
        self.assertIn("硬判据缺失就没法判 ☑", text)


class LedgerDriftTests(Fixture):
    def test_duplicate_ledger_row_number_is_red(self):
        # 并行编辑把整行弄丢后再「恢复」就会留下重复行；按行号读的执法器（dict 覆盖）看不见它
        root, data = self.build()
        body = ledger_text(data).splitlines()
        first = next(index for index, line in enumerate(body) if line.startswith("| 1 |"))
        body.insert(first + 1, body[first])
        (root / data["sources"]["ledger"]).write_text("\n".join(body) + "\n", encoding="utf-8")
        text = "\n".join(core.goalplan_audit(root)["errors"])
        self.assertIn("行号 1 出现两次", text)
        self.assertIn(data["countRules"]["uniqueLedgerRows"], text)

    def test_ledger_row_split_over_lines_is_red(self):
        root, data = self.build()
        body = ledger_text(data).splitlines()
        first = next(index for index, line in enumerate(body) if line.startswith("| 1 |"))
        row = body[first]
        head, tail = row[: len(row) // 2], row[len(row) // 2:]
        body[first:first + 1] = [head, tail]
        (root / data["sources"]["ledger"]).write_text("\n".join(body) + "\n", encoding="utf-8")
        text = "\n".join(core.goalplan_audit(root)["errors"])
        self.assertIn("被拆成", text)
        self.assertIn(data["countRules"]["oneRowPerLine"], text)

    def test_clean_table_does_not_complain(self):
        # 阳性对照的另一半：结构判据不许天生报红（真仓的台账由 RealRepoTests 那条一起核）
        root, _ = self.build()
        text = "\n".join(core.goalplan_audit(root)["errors"])
        self.assertNotIn("行号 1 出现两次", text)
        self.assertNotIn("被拆成", text)

    def test_row_status_drift_is_red(self):
        root, data = self.build()
        drifted = ledger_text(data).replace(f"| {MARK['done']} | 夹具依据 |", f"| {MARK['doing']} | 夹具依据 |", 1)
        self.assertNotEqual(drifted, ledger_text(data))
        (root / data["sources"]["ledger"]).write_text(drifted, encoding="utf-8")
        text = "\n".join(core.goalplan_audit(root)["errors"])
        self.assertIn("与台账第", text)
        self.assertIn("不一致", text)
        self.assertIn("历史快照当承诺的同族漂移", text)

    def test_count_line_drift_is_red(self):
        root, data = self.build()
        body = ledger_text(data).replace("**计数**：☑ 完成 8", "**计数**：☑ 完成 9", 1)
        self.assertNotEqual(body, ledger_text(data))
        (root / data["sources"]["ledger"]).write_text(body, encoding="utf-8")
        text = "\n".join(core.goalplan_audit(root)["errors"])
        self.assertIn("≠ 逐条实算", text)
        self.assertIn("计数行是抄的、行是源", text)

    def test_missing_count_line_is_red(self):
        root, data = self.build()
        body = "\n".join(line for line in ledger_text(data).splitlines() if not line.startswith("**计数**"))
        (root / data["sources"]["ledger"]).write_text(body + "\n", encoding="utf-8")
        self.assertIn("找不到「计数」行", "\n".join(core.goalplan_audit(root)["errors"]))

    def test_entry_count_mismatch_is_red(self):
        root, data = self.build()
        full = ledger_text(data)
        trimmed = copy.deepcopy(data)
        trimmed["goals"] = trimmed["goals"][:10]
        (root / "governance/goal-plan.yaml").write_text(
            yaml.safe_dump(trimmed, allow_unicode=True, sort_keys=False), encoding="utf-8")
        text = "\n".join(core.goalplan_audit(root)["errors"])
        self.assertIn("条目 10 条 ≠ 台账目标级表格 11 行", text)

    def test_ledger_file_absent_refuses_to_claim_green(self):
        root, data = self.build()
        (root / data["sources"]["ledger"]).unlink()
        self.assertIn("台账读不动", "\n".join(core.check_goalplan(root)))


class PointerTests(Fixture):
    def test_missing_next_task_is_red(self):
        self.build(lambda data: data["next"].update({"task": ""}))
        text = self.errors()
        self.assertIn("next 指针缺失或为空", text)
        self.assertIn(POINTER["required"], text)

    def test_cell_not_in_ids_is_red(self):
        self.build(lambda data: data["next"].update({"cell": "loop-whatever"}))
        text = self.errors()
        self.assertIn("不是 goals[].id 之一", text)
        self.assertIn(POINTER["cellMustExist"], text)

    def test_pointing_at_a_done_entry_is_red(self):
        self.build(lambda data: data["next"].update({"cell": "loop-sink"}))
        text = self.errors()
        self.assertIn("指向已 done 的条目", text)
        self.assertIn(POINTER["doneCellIsRed"], text)

    def test_stale_copy_of_the_pointer_in_the_ledger_is_red(self):
        # yaml 的 task 改了、台账还留着旧抄本 ⇒ 必须红：两份抄本一定会漂，以 yaml 为源
        def mutate(data):
            stale = ledger_text(data)
            data["next"]["task"] = str(data["next"]["task"]) + "（本轮改写：换了个说法）"
            return stale
        self.build(mutate)
        text = self.errors()
        self.assertIn("没逐字抄 next.task 原文", text)
        self.assertIn(POINTER["ledgerMustQuoteTask"], text)


class PanelTests(Fixture):
    def test_panel_status_drift_is_red(self):
        self.build(panel_overrides={"loop-sink": "doing"})
        text = self.errors()
        self.assertIn("面板 `loop-sink` 状态 doing ≠ goal-plan done", text)
        self.assertIn("面板与台账必须同批改", text)

    def test_panel_missing_only_reports_unverified(self):
        def mutate(data):
            data["sources"]["panel"] = "no-such-dir/absent.canvas.tsx"
            return ledger_text(data)
        root, _ = self.build(mutate, with_panel=False)
        result = core.goalplan_audit(root)
        self.assertEqual(result["panel"], "面板不在本机 ⇒ 未核状态一致性（不判红也不判绿）")
        self.assertEqual(result["errors"], [])


class MachineProofTests(Fixture):
    """声明了 machineProof 的条目：标 ☑ 必须检出面当前判满足；尺子取不到也判红，不默认通过。"""

    def business_run(self, root):
        import json
        log = root / ".spec/obs/run.jsonl"
        log.parent.mkdir(parents=True, exist_ok=True)
        events = [{"schema": "tenger.trace/v1", "event": "node-start", "project": "p",
                   "executionId": "EXEC-BIZ-1", "node": "prd-design", "skill": "prd-design",
                   "role": "produce", "actor": "main", "origin": "self",
                   "ts": "2026-10-17T09:00:00+08:00", "artifacts": [], "upstream": []},
                  {"schema": "tenger.trace/v1", "event": "node-end", "project": "p",
                   "executionId": "EXEC-BIZ-1", "node": "prd-design", "skill": "prd-design",
                   "role": "produce", "actor": "main", "origin": "self",
                   "ts": "2026-10-17T09:40:00+08:00", "gate": "PASS", "allowDownstream": True,
                   "artifacts": [{"path": ".spec/prd/overview.md", "sha256": "b" * 64, "bytes": 20}],
                   "upstream": []}]
        log.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in events) + "\n", encoding="utf-8")

    def claim_done(self, data):
        entry = entry_of(data, "loop-data")
        entry["status"] = "done"
        entry.setdefault("basis", {})["commits"] = [FALLBACK_COMMIT]
        entry.pop("blockedBy", None)

    def test_unsatisfied_detector_blocks_a_claimed_checkmark(self):
        root, data = self.build(self.claim_done, with_panel=False)
        text = self.errors()
        self.assertIn("标 ☑(done) 而检出面判未满足", text)
        self.assertIn("①客观数据判据：未满足", text, "要说清是哪一格没过，不能只说「☑ 不成立」")
        self.assertIn(data["proofRules"]["machineProofRule"], text)

    def test_satisfied_detector_allows_the_claim(self):
        # 阳性对照（本轮记过的规矩）：断言「不报错」之前必须证明同一把尺子真的会亮
        root, data = self.build(self.claim_done, with_panel=False)
        self.assertIn("标 ☑(done) 而检出面判未满足", self.errors())
        self.business_run(root)
        self.assertNotIn("而检出面判未满足", self.errors())

    def test_unknown_source_refuses_to_guess_the_yardstick(self):
        def mutate(data):
            self.claim_done(data)
            entry_of(data, "loop-data")["machineProof"] = "ghostCheck"
        root, _ = self.build(mutate, with_panel=False)
        text = self.errors()
        self.assertIn("未在 proofRules.machineProofs 声明", text)
        self.assertIn("ghostCheck", text)

    def test_unsupported_source_is_red_not_skipped(self):
        # 名字声明了、执法器却没实现 ⇒ 不能当成「这条不用核」
        def mutate(data):
            self.claim_done(data)
            data["proofRules"]["machineProofs"]["somedayCheck"] = "将来才会实现的检出面"
            entry_of(data, "loop-data")["machineProof"] = "somedayCheck"
        root, _ = self.build(mutate, with_panel=False)
        self.assertIn("已声明但执法器没实现它 ⇒ 拒绝当作已通过", self.errors())

    def test_doing_entry_is_never_nagged_by_this_gate(self):
        self.build()
        text = self.errors()
        self.assertNotIn("machineProof", text)
        self.assertNotIn("而检出面判未满足", text)

    def test_delivery_proof_is_na_when_the_repo_does_not_declare_it(self):
        # 交付面只认被测仓自己声明的 delivery 节：没声明就是不适用（不判红也不判绿），业务仓不该被本仓纪律绑住
        root, _ = self.build()
        result = core.goalplan_audit(root)
        self.assertNotIn("delivery", "\n".join(result["errors"]))
        self.assertTrue(any("delivery" in note for note in result["machineNotes"]), result["machineNotes"])

    def test_declared_delivery_but_not_a_git_repo_is_red(self):
        import yaml
        root, _ = self.build()
        shipped = yaml.safe_load((ROOT / "governance/obs-registry.yaml").read_text(encoding="utf-8"))
        (root / "governance/obs-registry.yaml").write_text(
            yaml.safe_dump({"delivery": shipped["delivery"]}, allow_unicode=True, sort_keys=False), encoding="utf-8")
        errors = "\n".join(core.goalplan_audit(root)["errors"])
        self.assertIn("声明了 delivery 判据但这里不是 git 仓", errors)
        self.assertIn("不当已通过", errors)

    def test_real_repo_delivery_proof_actually_passes(self):
        # 阳性对照：真仓此刻不领先上游 ⇒ 必须真判 pass，而不是因为哪里读不到而蒙过去
        state, text = core.goalproof_machine(ROOT, "delivery", REAL["proofRules"])
        self.assertEqual(state, "pass", text)
        self.assertIn("已推齐", text)


class RealRepoTests(unittest.TestCase):
    def test_this_repo_must_keep_the_plan_file(self):
        # 「删掉文件就能免检」正是本执法要防的漏洞，所以先钉住文件在不在
        self.assertTrue((ROOT / core.GOALPLAN_FILE).is_file(),
                        f"本仓必须有 {core.GOALPLAN_FILE}，否则 goalplan 执法会静默变成「不适用」")

    def test_shipped_ledger_panel_and_plan_are_consistent(self):
        result = core.goalplan_audit(ROOT)
        self.assertTrue(result["applies"])
        self.assertEqual(result["errors"], [], f"真实台账此刻必须全绿：{result['errors']}")
        self.assertEqual(result["counts"]["goals"], 11)
        self.assertEqual(result["panel"], "", "面板不在本机就说明 sources.panel 或 panelId 写错了")

    def test_every_done_entry_carries_verified_basis(self):
        for entry in core.goalplan_audit(ROOT)["entries"]:
            if entry["mark"] == "☑":
                self.assertGreaterEqual(entry["verified"], 1, f"{entry['id']} 标 ☑ 却没一条依据能回查")

    def test_blocked_entries_name_their_hard_blocker(self):
        for entry in REAL["goals"]:
            if entry["status"] != "done":
                self.assertTrue(str(entry.get("blockedBy") or "").strip(),
                                f"{entry['id']} 进行中却没写阻塞原因")

    def test_next_pointer_cell_is_still_open(self):
        aimed = entry_of(REAL, REAL["next"]["cell"])
        self.assertNotEqual(aimed["status"], "done", "指针必须改写后再提交")


if __name__ == "__main__":
    unittest.main()
