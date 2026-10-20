"""候选卡确认协议（人在环）＋「未确认不计入闭环率」的反向对照（排序第 5 项的 ☑ 硬判据）。

钉住的执法，一条不落：

① 卡面必须摆出确认人／确认时间／结论三个字段，未确认时逐字显示注册表占位文案；
② 注册表缺 confirmation 判据 ⇒ 拒绝执行（不猜落点、不用默认字段名、红口无凭不执行）；
③ 只填一部分＝未确认（不是已确认），占位文案本身也算未确认；
④ 自动执行者当「确认人」判**非人确认**（夜间自主会话不得自行确认候选卡，这条是机械兜底不是口头承诺）；
⑤ 结论不在注册表枚举／确认时间不带时区／未来时刻 ⇒ 判「无效」，与「没确认」分开报；
⑥ 「待定」与未确认同等待遇；「成立」缺 `升级为`＋`回归` 任一要件 ⇒ 计未闭环（0%），
   两要件齐且机器查得到 ⇒ 100%；写了不存在的路径／查不到的 sha 都必须掉回未闭环；
⑦ 闭环率的分子分母只算「已确认且结论=成立」：未确认既不分摊也不稀释；分母为空一律 N/A；
⑧ 生成器永不写确认目录：重算候选卡不覆盖人写的判定；把确认目录嵌进派生区必须被拒
   （派生区被 .gitignore 忽略，判定证据塞进去就等于失踪）。
"""
from __future__ import annotations
import hashlib, shutil, subprocess, sys, tempfile, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tsr
from obs import candidates

ROOT = Path(__file__).resolve().parents[2]
POLICY = candidates.policy()
CONF = candidates.confirmation_policy(POLICY)
RULES, NAMES = CONF["rules"], CONF["fieldNames"]
CLOSURE = CONF["closureFieldNames"]
PLACEHOLDER = CONF["unconfirmed"]
ACTOR, AT, CONCLUSION = NAMES["actor"], NAMES["time"], NAMES["conclusion"]


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def card_of(result, kind):
    return [card for card in result["cards"] if card["kind"] == kind]


class Harness(unittest.TestCase):
    """临时仓里造一张真实的 bindingDrift 候选卡：事件与 sha 都由 tsr 落盘，不是手写的。"""

    def make(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = self.root = Path(tmp.name)
        (root / ".spec/prd").mkdir(parents=True)
        self.doc = root / ".spec/prd/overview.md"
        self.doc.write_text("# v1\n", encoding="utf-8")
        git(root, "init", "-q")
        git(root, "config", "user.email", "probe@example.invalid")
        git(root, "config", "user.name", "probe")
        git(root, "add", ".")
        git(root, "commit", "-qm", "chore: fixture")
        self.head = git(root, "rev-parse", "HEAD").stdout.strip()
        flags = ["--project-root", str(root), "--execution-id", "EXEC-CONF-1",
                 "--node", "prd-design", "--skill", "prd-design"]
        self.assertEqual(0, tsr.main(flags + ["--state", "PRD_IN_PROGRESS", "node-start"]))
        self.assertEqual(0, tsr.main(flags + ["--state", "PRD_APPROVED", "node-end", "--gate", "PASS",
                                              "--allow-downstream", "true",
                                              "--artifact", ".spec/prd/overview.md"]))
        self.doc.write_text("# v1\n# 改了正文没落台账\n", encoding="utf-8")
        self.card = card_of(candidates.collect(root), POLICY["kinds"]["bindingDrift"])[0]
        self.id = self.card["id"]
        return root

    def confirm(self, **fields):
        """人写确认记录（模拟人手，不是生成器）。"""
        directory = self.root / CONF["dir"]
        directory.mkdir(parents=True, exist_ok=True)
        body = {**{"schema": CONF["schema"], "候选": self.id}, **fields}
        target = directory / str(CONF["fileName"]).format(id=self.id)
        target.write_text(yaml.safe_dump(body, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return target

    def human(self, **over):
        """一份格式齐备的确认：默认结论「成立」，坏味道由 over 注入。"""
        return self.confirm(**{ACTOR: "张三", AT: self.stamp(), CONCLUSION: "成立", **over})

    def reread(self):
        return candidates.read_confirmation(self.root, POLICY, self.id)

    def audit(self, extra=()):
        card = dict(self.card)
        card["confirmation"] = self.reread()
        return candidates.closure_audit(self.root, POLICY, [card, *extra])

    def issue(self, relative=".spec/issues/Probe/2026-10-17/01-real.md", body="# 正式问题卡\n"):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if body is not None:
            target.write_text(body, encoding="utf-8")
        return relative

    def stamp(self, minutes=-5):
        return (datetime.now(timezone.utc).astimezone() + timedelta(minutes=minutes)).isoformat(
            timespec="seconds")


class RegistryTests(Harness):
    def thin(self, mutate):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        (root / "governance").mkdir(parents=True)
        data = yaml.safe_load(candidates.SHIPPED_REGISTRY.read_text(encoding="utf-8"))
        mutate(data["candidates"])
        (root / "governance/obs-registry.yaml").write_text(
            yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        return root

    def test_card_shows_the_three_human_fields_as_unconfirmed(self):
        self.make()
        text = candidates.render(self.card, POLICY)
        self.assertIn("## 确认协议（人在环）", text)
        for name in (ACTOR, AT, CONCLUSION):
            self.assertIn(f"{name}：`{PLACEHOLDER}`", text)
        self.assertIn(self.card["confirmation"]["path"], text)
        self.assertIn(RULES["unconfirmedNotCounted"], text)
        self.assertIn(RULES["protocol"], text)
        self.assertIn(RULES["noSelfConfirm"], text)
        self.assertIn("当前状态：**未确认**", text)
        for conclusion, meaning in CONF["conclusions"].items():
            self.assertIn(f"- {conclusion}：{meaning}", text)

    def test_confirmation_section_absent_reads_as_na_not_as_confirmed(self):
        # 反向对照：collect 没附确认段时必须显式 N/A——留白会被读成「都确认过了」
        self.make()
        card = dict(self.card)
        card.pop("confirmation")
        text = candidates.render(card, POLICY)
        self.assertIn(RULES["naSection"], text)
        self.assertNotIn("当前状态：**已确认**", text)

    def test_missing_confirmation_section_refuses_to_guess_fields(self):
        root = self.thin(lambda section: section.pop("confirmation"))
        with self.assertRaises(ValueError) as caught:
            candidates.policy(root)
        self.assertIn("confirmation", str(caught.exception))
        self.assertIn("拒绝用默认值冒充实装", str(caught.exception))

    def test_missing_closure_role_refuses_to_invent_names(self):
        root = self.thin(lambda section: section["confirmation"].pop("closureFieldNames"))
        with self.assertRaises(ValueError) as caught:
            candidates.confirmation_policy(candidates.policy(root))
        self.assertIn("closureFieldNames", str(caught.exception))
        self.assertIn("缺必需判据键", str(caught.exception))

    def test_missing_rule_text_refuses_unbacked_verdicts(self):
        root = self.thin(lambda section: section["confirmation"]["rules"].pop("closedNeeds"))
        with self.assertRaises(ValueError) as caught:
            candidates.confirmation_policy(candidates.policy(root))
        self.assertIn("candidates.confirmation.rules 缺判据文案", str(caught.exception))
        self.assertIn("closedNeeds", str(caught.exception))


class UnconfirmedTests(Harness):
    def test_partial_confirmation_stays_unconfirmed(self):
        self.make()
        self.confirm(**{ACTOR: "张三", AT: self.stamp()})
        info = self.reread()
        self.assertEqual(info["state"], "未确认")
        self.assertIn(f"缺 {CONCLUSION}", info["problems"][0])
        self.assertEqual(self.audit()["pool"], [], "没结论的卡不得进闭环率分母")

    def test_placeholder_values_are_not_read_as_confirmation(self):
        self.make()
        self.confirm(**{name: PLACEHOLDER for name in (ACTOR, AT, CONCLUSION)})
        info = self.reread()
        self.assertEqual(info["state"], "未确认")
        self.assertIn(RULES["protocol"], info["problems"][0])

    def test_empty_denominator_is_na_not_zero_percent(self):
        self.make()
        audit = self.audit()
        self.assertEqual(audit["rate"], "N/A")
        self.assertEqual(audit["pool"], [])
        lines = "\n".join(candidates._closure_lines(audit))
        self.assertIn(f"闭环率：**N/A —— {RULES['emptyDenominator']}**", lines)
        self.assertIn(RULES["unconfirmedNotCounted"], lines)
        self.assertIn("分母为空", lines)


class InvalidTests(Harness):
    def check(self, expect, **over):
        self.make()
        self.human(**over)
        info = self.reread()
        self.assertEqual(info["state"], "无效", f"{over} 不该被当成人的确认")
        self.assertIn(expect, "；".join(info["problems"]))
        return info

    def test_autonomous_actor_is_not_a_human_confirmation(self):
        for actor in ("autonomous-night", "agent", "main", "TSR"):
            info = self.check(RULES["noSelfConfirm"], **{ACTOR: actor})
            self.assertEqual(self.audit()["pool"], [], "非人确认不得进闭环率分母")
            self.assertEqual(info["actor"], actor)

    def test_conclusion_outside_the_enum_is_invalid(self):
        info = self.check("不在注册表枚举", **{CONCLUSION: "大概是问题吧"})
        for conclusion in CONF["conclusions"]:
            self.assertIn(conclusion, info["problems"][0], "得把人该填哪些值说清楚")

    def test_naive_timestamp_is_invalid(self):
        self.assertIn("不合法", self.check(RULES["timestamp"], **{AT: "2026-10-16 21:00"})["problems"][0])

    def test_future_timestamp_is_invalid(self):
        self.assertIn("晚于本机时钟", self.check(RULES["timestamp"], **{AT: self.stamp(minutes=60)})["problems"][0])

    def test_unparseable_sidecar_is_invalid_not_unconfirmed(self):
        self.make()
        directory = self.root / CONF["dir"]
        directory.mkdir(parents=True, exist_ok=True)
        (directory / str(CONF["fileName"]).format(id=self.id)).write_text("只有一句话\n", encoding="utf-8")
        info = self.reread()
        self.assertEqual(info["state"], "无效")
        self.assertIn(RULES["shape"], info["problems"][0])

    def test_pending_conclusion_is_excluded_from_the_rate(self):
        self.make()
        self.human(**{CONCLUSION: "待定"})
        info = self.reread()
        self.assertEqual(info["state"], "已确认")
        self.assertFalse(info["counts"])
        self.assertIn(RULES["unconfirmedNotCounted"], info["problems"][0])
        audit = self.audit()
        self.assertEqual(audit["pool"], [])
        self.assertEqual(audit["rate"], "N/A")


class ClosureTests(Harness):
    def test_confirmed_without_evidence_is_zero_percent(self):
        self.make()
        self.human()
        info = self.reread()
        self.assertTrue(info["counts"])
        self.assertFalse(info["closed"])
        self.assertEqual(self.audit()["rate"], "0%")
        self.assertIn("没有可验真的 commit 指针", "；".join(info["closure"]))
        self.assertIn(RULES["closedNeeds"], "；".join(info["closure"]))

    def test_ghost_path_and_unverifiable_commit_both_fail_closed(self):
        self.make()
        self.human(**{CLOSURE["issue"]: ".spec/issues/Probe/2026-10-17/01-ghost.md",
                      CLOSURE["commit"]: hashlib.sha1(b"not-a-commit").hexdigest()[:12]})
        info = self.reread()
        self.assertFalse(info["closed"])
        joined = "；".join(info["closure"])
        self.assertIn("查不到该文件", joined)
        self.assertIn("在该仓不存在", joined)
        self.assertEqual(self.audit()["rate"], "0%")

    def test_existing_issue_outside_the_repo_does_not_close(self):
        # 反向对照：仓外的真文件不算升级（路径逃逸会把别人的目录当本仓证据）
        self.make()
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(outside, ignore_errors=True))
        (outside / "01-outside.md").write_text("# 别的目录里的文件\n", encoding="utf-8")
        self.human(**{CLOSURE["issue"]: (outside / "01-outside.md").as_posix(),
                      CLOSURE["commit"]: self.head})
        info = self.reread()
        self.assertFalse(info["closed"], "仓外文件不得算「已升级为正式问题卡」")
        self.assertIn("查不到该文件", "；".join(info["closure"]))

    def test_real_issue_file_and_verifiable_commit_close_the_card(self):
        self.make()
        relative = self.issue()
        self.human(**{CLOSURE["issue"]: relative, CLOSURE["commit"]: self.head})
        info = self.reread()
        self.assertTrue(info["closed"], "两要件机器都查得到 ⇒ 这才叫闭环")
        audit = self.audit()
        self.assertEqual(audit["rate"], "100%")
        joined = "；".join(info["closure"])
        self.assertIn("git cat-file 验真通过", joined)
        self.assertIn("文件真实存在", joined)
        self.assertIn("闭环率：**100%（已闭环 1／已确认「成立」 1 张）**",
                      "\n".join(candidates._closure_lines(audit)))

    def test_unconfirmed_cards_neither_dilute_nor_inflate_the_rate(self):
        # 本文件唯一的比例判据：1 张闭环 + 1 张未确认 ⇒ 仍 100%，未确认不进分子分母
        self.make()
        relative = self.issue()
        self.human(**{CLOSURE["issue"]: relative, CLOSURE["commit"]: self.head})
        audit = self.audit(extra=[{"id": "CAND-OTHER00001", "state": "未确认",
                                   "actor": None, "at": None, "conclusion": None,
                                   "counts": False, "closed": False, "closure": [], "problems": []}])
        self.assertEqual(audit["cards"], 2)
        self.assertEqual(len(audit["unconfirmed"]), 1)
        self.assertEqual(len(audit["pool"]), 1)
        self.assertEqual(audit["rate"], "100%")
        self.assertIn("未确认 1 张", "\n".join(candidates._closure_lines(audit)))


class WriteGuardTests(Harness):
    def test_write_never_creates_or_touches_the_confirmation_dir(self):
        self.make()
        candidates.write(self.root, [self.card])
        self.assertFalse((self.root / CONF["dir"]).exists(),
                         "生成器不得创建确认目录——建了就可能填，填了就是替人判定问题成立")
        self.human(**{CONCLUSION: "不成立"})
        target = self.root / CONF["dir"] / f"{self.id}.yaml"
        before = target.read_text(encoding="utf-8")
        candidates.write(self.root, candidates.collect(self.root)["cards"])
        self.assertEqual(target.read_text(encoding="utf-8"), before,
                         "重算候选卡覆盖确认记录 ⇒ 人的判定丢了")

    def test_confirmation_dir_nested_in_derived_area_is_refused(self):
        # 反向对照：派生区被 .gitignore 忽略，把确认目录塞进去＝判定证据不入库，必须拒写
        tampered = yaml.safe_load(candidates.SHIPPED_REGISTRY.read_text(encoding="utf-8"))
        tampered["candidates"]["confirmation"]["dir"] = ".spec/obs/candidates/confirmations"
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        (root / "governance").mkdir(parents=True)
        (root / "governance/obs-registry.yaml").write_text(
            yaml.safe_dump(tampered, allow_unicode=True), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            candidates.write(root, [])
        self.assertIn("生成器不得写确认目录", str(caught.exception))

    def test_confirmation_dir_is_tracked_so_verdicts_are_auditable(self):
        probe = git(ROOT, "check-ignore", str(Path(CONF["dir"]) / "CAND-X.yaml"))
        self.assertNotEqual(probe.returncode, 0,
                            f"确认记录被 gitignore ⇒ 人的判定不可回查：{probe.stdout}")
        derived = git(ROOT, "check-ignore", str(Path(POLICY["outputDir"]) / "CAND-X.md"))
        self.assertEqual(derived.returncode, 0, "派生区应当是可重算的忽略产物，两处口径不能混")


class RealRepoTests(unittest.TestCase):
    def test_real_candidates_are_all_reported_with_a_confirmation_state(self):
        result = candidates.collect(ROOT)
        self.assertTrue(result["cards"], "本仓当前确有未收口的检出项，别把它读成「没问题」")
        audit = candidates.closure_audit(ROOT, POLICY, result["cards"])
        self.assertEqual(len(audit["unconfirmed"]) + len(audit["invalid"])
                         + sum(len(v) for v in audit["confirmed"].values()), len(result["cards"]))
        for card in result["cards"]:
            self.assertIn(card["confirmation"]["state"], ("未确认", "已确认", "无效"))
        if not audit["pool"]:
            self.assertEqual(audit["rate"], "N/A", "分母为空不得给出任何百分比")


if __name__ == "__main__":
    unittest.main()
