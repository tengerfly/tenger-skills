"""同型问题复发率的反向对照（plan v2 §3「智能化」第二条）。

这个量具的上一版就是靠「标题去掉日期数字后的主干词」凑组，**两头都错过**，所以这里的重点不是
「能不能数出复发」，而是「能不能不数错」：

① 造一条有「第 2 次复发」＋「见 issue/…」的卡 ⇒ 必须判成复发链（指针原文＋文件:行号都能点回去）；
② 同一目录两张无指针的卡（我们踩过的 `issue/Frontend-Dev/2026-09-16/01`、`02` 情形）⇒ **必须判 0 组复发**，
   不许因为标题相近、路径同目录、或首行那条 `# ../../issue/<自己>` 的自指占位路径就配对；
③ 把注册表里的窗口天数或语料键删掉 ⇒ 必须报错拒绝开工，不许静默退回默认值；
④ 正文出现「复发」二字但没有任何显式指针 ⇒ 不计入复发，只单列成交人裁决的旁证。

另钉基数纪律：没有语料 ⇒ N/A 而不是 0%；读不动／非日期目录／文件名不合的卡单列，不折进 0；
窗口天数改成 3 天窗口起点必须跟着动（证明 30 不是硬编码）。
全程只读临时目录里的合成卡片（真仓那份只做结构不变量核验），不碰任何卡片内容、不调引擎、不花钱。
"""
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from obs import recurrence

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_TEXT = (ROOT / "governance/obs-registry.yaml").read_text(encoding="utf-8")
SHIPPED = recurrence.policy(ROOT)      # 仓里发布的那份判据能跑起来，本身就是第一条断言
PROBE = "Probe"


def card(day: str, name: str, body: str, skill: str = PROBE) -> tuple:
    return (f"issue/{skill}/{day}/{name}", body)


HEAD = "# 入口没触发（第 1 次）\n\n- 现象：用户说「我想做一个应用」，助手直接问技术选型。\n"
SECOND = ("# 入口又没触发（第 2 次）\n\n"
          "| 优化状态 | 规则已改 |\n"
          "|---|---|\n"
          "| 等级 | P0 |\n\n"
          "**复发性**：同根因第 2 次复发，见 `issue/Probe/2026-09-01/01-head.md`。\n")
THIRD = ("# 入口第三次没触发\n\n"
         "> 归属 skill：`Probe` ｜ 日期：2026-01-99（正文里的日期是坏的，取数只认目录名）\n\n"
         "| 复发关联 | `issue/Probe/2026-09-01/01-head.md`、`issue/Probe/2026-09-10/02-second.md`"
         "（同根因第三次复发） |\n")
UNRELATED = "# 另一条问题\n\n没有指回任何旧卡。\n"


class RepoMixin(unittest.TestCase):
    """临时仓：注册表从发布版复制一份再按需改坏；卡片按 issue/<Skill>/<日期>/<NN>-<标题>.md 铺。"""

    def _close_previous(self) -> None:
        """一个用例里连做两次临时仓（改注册表前后对照）时先回收上一个，别留到 GC 报 ResourceWarning。"""
        previous = getattr(self, "_tmp", None)
        if previous is not None:
            try:
                previous.cleanup()
            except OSError:
                pass
            self._tmp = None

    def make(self, cards=(), tamper=None, registry=None) -> Path:
        self._close_previous()
        tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self._tmp = tmp
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "repo"
        (root / "governance").mkdir(parents=True)
        if registry is None:
            data = yaml.safe_load(REGISTRY_TEXT)
            if tamper:
                tamper(data)
            registry = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
        (root / "governance/obs-registry.yaml").write_text(registry, encoding="utf-8")
        for relative, body in cards:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")
        self.root = root
        return root

    def measure(self, root=None) -> dict:
        return recurrence.measure(root or self.root)

    def assertNoChain(self, report) -> None:
        self.assertEqual(report["chains"], [], "凑出链了——判据不许靠标题/路径相近")
        self.assertEqual(report["recurrences"], [])
        self.assertEqual(report["recurrencesInWindow"], [])
        self.assertEqual(report["edges"], [])


class PositiveControls(RepoMixin):
    def test_explicit_ordinal_and_pointer_form_a_chain(self):
        """①「第 2 次复发」＋「见 issue/…」⇒ 判成链：链头无指针、链尾带指针，最长 1 跳。"""
        self.make([card("2026-09-01", "01-head.md", HEAD), card("2026-09-10", "02-second.md", SECOND)])
        report = self.measure()
        self.assertEqual(len(report["chains"]), 1)
        chain = report["chains"][0]
        self.assertEqual(chain["skill"], PROBE)
        self.assertEqual(chain["hops"], 1)
        self.assertEqual([node["rel"].split("/")[-1] for node in chain["nodes"]], ["01-head.md", "02-second.md"])
        self.assertEqual([node["recurs"] for node in chain["nodes"]], [False, True])
        self.assertEqual(report["recurrences"], [f"issue/{PROBE}/2026-09-10/02-second.md"])
        self.assertEqual(report["longestHops"], 1)
        self.assertEqual(report["chainSkillsLabel"], PROBE)

    def test_three_cards_chain_by_two_hops_and_order_check(self):
        """A→B→C 串成 3 张卡 / 2 跳；次序按父目录名（正文里那句「日期：2026-01-99」是诱饵，不参与取数）。"""
        self.make([card("2026-09-01", "01-head.md", HEAD), card("2026-09-10", "02-second.md", SECOND),
                   card("2026-09-20", "03-third.md", THIRD)])
        report = self.measure()
        chain = report["chains"][0]
        self.assertEqual((len(chain["nodes"]), chain["hops"]), (3, 2))
        self.assertEqual([node["position"] for node in chain["nodes"]], [1, 2, 3])
        self.assertEqual([node["date"] for node in chain["nodes"]],
                         ["2026-09-01", "2026-09-10", "2026-09-20"])
        self.assertEqual(report["cutoff"], "2026-09-20")
        # 一张卡指两张旧卡 ⇒ 两条边，但复发只算一次（rate.dedupe=byCard）
        self.assertEqual(len(chain["nodes"][2]["pointers"]), 2)
        self.assertEqual(len(report["recurrences"]), 2)
        claims = {claim["file"]: claim for claim in report["claims"]}
        third = claims[f"issue/{PROBE}/2026-09-20/03-third.md"]
        self.assertEqual((third["value"], third["chainPosition"], third["orderCheck"]), (3, 3, "一致"))

    def test_pointer_evidence_carries_snippet_and_file_line(self):
        """交付要求：每张判为复发的卡都要带「指针原文片段 + 文件:行号」，读数的人能点回去核对。"""
        self.make([card("2026-09-01", "01-head.md", HEAD), card("2026-09-10", "02-second.md", SECOND)])
        report = self.measure()
        edge = report["chains"][0]["nodes"][1]["pointers"][0]
        self.assertEqual(edge["where"], f"issue/{PROBE}/2026-09-10/02-second.md:7")
        self.assertIn(f"issue/{PROBE}/2026-09-01/01-head.md", edge["snippet"])
        self.assertIn("同根因第 2 次复发", edge["snippet"])
        rendered = recurrence.render(report)
        self.assertIn(f"`issue/{PROBE}/2026-09-10/02-second.md:7`", rendered)
        self.assertIn("指针原文片段", rendered)

    def test_chinese_and_spaced_ordinals_all_link(self):
        """「第 3 次复发」「第3次复发」「第三次复发」这类变体都要认（口径就是注册表里那一条正则）。"""
        for numeral in ("第 3 次复发", "第三次复发", "第3次复发"):
            root = self.make([card("2026-09-01", "01-head.md", HEAD),
                              card("2026-09-10", "02-second.md",
                                   f"**复发性**：同根因{numeral}，见 `issue/Probe/2026-09-01/01-head.md`。\n")])
            self.assertEqual(len(self.measure(root)["chains"]), 1, numeral)

    def test_window_rate_uses_window_cards_as_denominator(self):
        """复发率 = 窗口内复发卡 / 窗口内卡片；切点取语料最新日期并写进报告。"""
        self.make([card("2026-09-01", "01-head.md", HEAD), card("2026-09-10", "02-second.md", SECOND),
                   card("2026-09-20", "03-other.md", UNRELATED)])
        report = self.measure()
        self.assertEqual((report["cardsTotal"], report["cardsInWindow"]), (3, 3))
        self.assertAlmostEqual(report["value"], 1 / 3, places=6)
        self.assertEqual(report["windowDays"], SHIPPED["window"]["days"])
        self.assertIn("2026-09-20", recurrence.render(report))


class FalsePositiveGuards(RepoMixin):
    def test_two_pointerless_cards_in_one_directory_are_zero_groups(self):
        """②我们踩过的 01/02 情形：同目录两张不同问题的卡 ⇒ 必须 0 组复发，不许凑。"""
        self.make([card("2026-09-16", "01-正面案例-静态页试做流程.md",
                        "# 静态页试做流程\n\n- 先出结构再补样式。\n", skill="Frontend-Dev"),
                   card("2026-09-16", "02-案例升级为主流程标准SOP.md",
                        "# 案例升级为主流程标准 SOP\n\n- 把案例升级成 SOP。\n", skill="Frontend-Dev")])
        report = self.measure()
        self.assertNoChain(report)
        self.assertEqual(report["value"], 0.0)                 # 0 是实测，不是「没得算」
        self.assertIn(SHIPPED["reasons"]["zero"], report["reason"])

    def test_identical_titles_on_different_days_are_not_a_recurrence(self):
        """标题逐字相同也不配对——上一版就是这么把假阳性做出来的。"""
        same = "# 选型澄清一两句即定稿拷问深度未落地\n\n- 现象：澄清两句就定稿。\n"
        self.make([card("2026-09-07", "01-same.md", same, skill="Backend-Tech-Design"),
                   card("2026-09-23", "01-same.md", same, skill="Backend-Tech-Design")])
        self.assertNoChain(self.measure())

    def test_self_path_placeholder_heading_is_not_a_pointer(self):
        """`# ../../issue/<自己>` 这类自指占位行必须判成自指，不能拉同目录另一张卡凑组。"""
        self.make([card("2026-09-16", "01-head.md", f"# ../../issue/{PROBE}/2026-09-16/01\n\n正文。\n"),
                   card("2026-09-16", "02-second.md",
                        f"# ../../issue/{PROBE}/2026-09-16/02\n\n正文。\n")])
        report = self.measure()
        self.assertNoChain(report)
        self.assertEqual({ref["status"] for ref in report["refs"]}, {"selfRef"})
        self.assertIn(SHIPPED["reasons"]["selfRef"], report["refs"][0]["reason"])

    def test_mention_without_pointer_is_not_counted(self):
        """④只有「复发」二字、没有任何显式指针 ⇒ 不计入，但必须单列出来（不静默当成没复发）。"""
        mention = ("# 状态双写漂移\n\n> 定级理由：极易复发（任何一次换编辑器都会再犯）。\n\n"
                   "| 沉淀目标 | A · 防复发：`WorkFlow` |\n")
        self.make([card("2026-10-09", "01-double-write.md", mention, skill="WorkFlow")])
        report = self.measure()
        self.assertNoChain(report)
        self.assertEqual(report["claims"], [])
        self.assertEqual([item["file"] for item in report["mentions"]],
                         ["issue/WorkFlow/2026-10-09/01-double-write.md"])
        self.assertEqual(report["cueCards"], 1)
        self.assertEqual(report["value"], 0.0)
        self.assertIn("只有「复发」字样", recurrence.render(report))

    def test_forward_pointer_to_a_later_card_does_not_link(self):
        """旧卡事后补写「第 3 次复发，见 <更晚的卡>」⇒ 不是「指回旧卡」，不成边；序数声称单列。"""
        self.make([card("2026-09-01", "01-old.md",
                        "| 优化状态 | 第 2 次复发，见 `issue/Probe/2026-10-08/01-new.md` |\n"),
                   card("2026-10-08", "01-new.md", "# 新卡\n\n没有指回旧卡的指针。\n")])
        report = self.measure()
        self.assertNoChain(report)
        self.assertEqual({ref["status"] for ref in report["refs"]}, {"forwardRef"})
        self.assertEqual(len(report["unsupportedClaims"]), 1)
        self.assertIn(SHIPPED["reasons"]["ordinalWithoutChain"], report["unsupportedClaims"][0]["reason"])
        self.assertIn("第 2 次复发", report["unsupportedClaims"][0]["verbatim"])

    def test_pointer_that_resolves_to_nothing_is_reported_not_guessed(self):
        """解析不到卡片的路径 ⇒ unresolved（不许拿相近标题冒替），并且如实 0 组。"""
        self.make([card("2026-09-10", "02-second.md",
                        "**复发性**：第 2 次复发，见 `issue/Probe/2026-01-01/09-ghost.md`。\n")])
        report = self.measure()
        self.assertNoChain(report)
        self.assertEqual({ref["status"] for ref in report["refs"]}, {"unresolved"})
        self.assertIn(SHIPPED["reasons"]["unresolved"], report["refs"][0]["reason"])

    def test_cross_skill_pointer_is_side_evidence_only(self):
        """链按「同一 skill 下 A→B→C」计（chain.scope=sameSkill）：跨 skill 的旧卡引用只作旁证。"""
        self.make([card("2026-09-16", "02-sop.md", "同根问题复发，见 `issue/Skill-Optimizer/2026-09-16/01-x.md`。\n"),
                   card("2026-09-16", "01-x.md", "# 落点分层\n\n正文。\n", skill="Skill-Optimizer")])
        report = self.measure()
        self.assertNoChain(report)
        self.assertEqual({ref["status"] for ref in report["refs"]}, {"crossSkill"})

    def test_bare_pointer_without_cue_is_not_counted(self):
        """成链第④格（同一行要有复发记号）：只「关联」旧卡 ⇒ 算待裁决的交叉引用，不算复发。"""
        self.make([card("2026-09-01", "01-head.md", HEAD),
                   card("2026-09-10", "02-second.md", f"- 关联 `issue/{PROBE}/2026-09-01/01-head.md`（同批另一条）\n")])
        report = self.measure()
        self.assertNoChain(report)
        self.assertEqual({ref["status"] for ref in report["refs"]}, {"cueless"})

    def test_require_cue_flag_is_registry_driven(self):
        """把 chain.requireCue 改成 false ⇒ 裸指针就成边：证明这格口径是注册表在执法，不是代码写死。"""
        cards = [card("2026-09-01", "01-head.md", HEAD),
                 card("2026-09-10", "02-second.md",
                      f"- 关联 `issue/{PROBE}/2026-09-01/01-head.md`（同批另一条）\n")]
        self.make(cards)
        self.assertNoChain(self.measure())
        self.make(cards, tamper=lambda data: data["recurrence"]["chain"].update(requireCue=False))
        self.assertEqual(len(self.measure()["chains"]), 1)


class RegistryDiscipline(RepoMixin):
    def test_missing_window_days_refuses_instead_of_defaulting(self):
        """③删掉窗口键 ⇒ 报错拒绝开工（尤其不许默默用代码里的 30 天）。"""
        self.make([card("2026-09-01", "01-head.md", HEAD)],
                  tamper=lambda data: data["recurrence"]["window"].pop("days"))
        with self.assertRaises(ValueError) as caught:
            recurrence.policy(self.root)
        self.assertIn("window.days", str(caught.exception))
        self.assertIn("拒绝用默认值", str(caught.exception))

    def test_missing_corpus_glob_refuses_instead_of_guessing_a_path(self):
        """③删掉语料键 ⇒ 报错；尤其不许退回写死的 issue/**。"""
        self.make([card("2026-09-01", "01-head.md", HEAD)],
                  tamper=lambda data: data["recurrence"]["corpus"].pop("glob"))
        with self.assertRaises(ValueError) as caught:
            recurrence.policy(self.root)
        self.assertIn("corpus.glob", str(caught.exception))

    def test_missing_reason_key_refuses(self):
        """每一格排除口径都要有落纸的原因文案，少一格就拒绝开工（不许现编一句糊过去）。"""
        self.make([card("2026-09-01", "01-head.md", HEAD)],
                  tamper=lambda data: data["recurrence"]["reasons"].pop("cueless"))
        with self.assertRaises(ValueError) as caught:
            recurrence.policy(self.root)
        self.assertIn("reasons.cueless", str(caught.exception))

    def test_missing_whole_section_refuses(self):
        self.make([card("2026-09-01", "01-head.md", HEAD)], registry="version: 1\nnodes: []\n")
        with self.assertRaises(ValueError) as caught:
            recurrence.policy(self.root)
        self.assertIn("未声明 recurrence 判据", str(caught.exception))

    def test_unrecognized_policy_value_refuses(self):
        """取值闸门：把日期取法改成「从正文猜」⇒ 报错，不悄悄按另一套取法跑。"""
        self.make([card("2026-09-01", "01-head.md", HEAD)],
                  tamper=lambda data: data["recurrence"]["corpus"].update(dateFrom="bodyText"))
        with self.assertRaises(ValueError) as caught:
            recurrence.policy(self.root)
        self.assertIn("corpus.dateFrom", str(caught.exception))
        self.assertIn("拒绝开工", str(caught.exception))

    def test_non_positive_window_days_refuses(self):
        self.make([card("2026-09-01", "01-head.md", HEAD)],
                  tamper=lambda data: data["recurrence"]["window"].update(days=0))
        with self.assertRaises(ValueError) as caught:
            recurrence.policy(self.root)
        self.assertIn(SHIPPED["window"]["badDaysReason"].replace("{value}", "0"), str(caught.exception))

    def test_broken_pointer_group_refuses(self):
        """注册表正则里没有声明的命名组 ⇒ 报错，不退回代码自备的模式。"""
        self.make([card("2026-09-01", "01-head.md", HEAD)],
                  tamper=lambda data: data["recurrence"]["pointers"]["issueRef"].update(
                      pattern="issue/(?P<skill>[^/]+)/(?P<date>\\d{4}-\\d{2}-\\d{2})"))
        with self.assertRaises(ValueError) as caught:
            recurrence.compile_patterns(recurrence.policy(self.root))
        self.assertIn(SHIPPED["pointers"]["missingGroupReason"].replace("{group}", "card"),
                      str(caught.exception))

    def test_window_days_actually_moves_the_window(self):
        """窗口天数改成 3 天 ⇒ 起点跟着动，复发卡落到窗外时报 0 并说明「不是没有复发」。"""
        cards = [card("2026-05-01", "01-head.md", HEAD.replace("2026-09-01", "2026-05-01")),
                 card("2026-05-20", "02-second.md",
                      "**复发性**：同根因第 2 次复发，见 `issue/Probe/2026-05-01/01-head.md`。\n"),
                 card("2026-05-25", "03-other.md", UNRELATED)]
        wide = self.measure(self.make(cards))
        self.assertEqual(wide["windowDays"], SHIPPED["window"]["days"])
        self.assertEqual((wide["cardsInWindow"], wide["value"]), (3, 1 / 3))
        self.assertEqual(wide["recurrencesInWindow"], [f"issue/{PROBE}/2026-05-20/02-second.md"])
        narrow = self.measure(self.make(cards, tamper=lambda data: data["recurrence"]["window"].update(days=3)))
        self.assertGreater(narrow["windowStart"], wide["windowStart"])   # 窗口越短，起点越靠近切点
        self.assertEqual(narrow["cardsInWindow"], 1)
        self.assertEqual(narrow["value"], 0.0)
        self.assertEqual(len(narrow["recurrences"]), 1)                 # 全时仍承认那张复发卡
        self.assertIn("不是没有复发", narrow["reason"])                 # 窗外有货 ⇒ 不许读成没复发


class BaseDiscipline(RepoMixin):
    def test_empty_corpus_is_na_not_zero_percent(self):
        root = self.make([])
        report = self.measure(root)
        self.assertIsNone(report["value"])
        self.assertIn("N/A", report["reason"])
        self.assertIn(SHIPPED["reasons"]["noCorpus"], report["reason"])
        self.assertNotIn("0.0%", recurrence.render(report))

    def test_non_date_directory_and_readme_are_listed_not_folded_into_zero(self):
        """禁止把「没扫到」写成「没复发」：非日期目录、按名单排除的文件都要单列。"""
        self.make([card("latest", "01-head.md", "# 无日期目录下的卡\n\n极易复发但没有指针。\n")])
        (self.root / "issue/Probe/2026-09-01").mkdir(parents=True)
        (self.root / "issue/Probe/2026-09-01/README.md").write_text("# 说明\n", encoding="utf-8")
        report = self.measure()
        self.assertEqual(report["cardsTotal"], 0)
        self.assertEqual([item["directory"] for item in report["oddDirs"]], ["latest"])
        self.assertEqual(report["excluded"], [f"issue/{PROBE}/2026-09-01/README.md"])
        self.assertIsNone(report["value"])                              # 基数 0 ⇒ N/A，不是 0%
        rendered = recurrence.render(report)
        self.assertIn("非日期目录", rendered)
        self.assertIn("不入基数的卡片", rendered)

    def test_card_excluded_from_base_makes_pointer_unresolved(self):
        """文件名不合 cardPattern 的卡不入基数；指向它的那条指针因此 unresolved，如实报而不是硬凑。"""
        self.make([card("2026-09-01", "head.md", "# 文件名没有序号\n\n正文。\n"),
                   card("2026-09-10", "02-second.md",
                        "**复发性**：第 2 次复发，见 `issue/Probe/2026-09-01/01-head.md`。\n")])
        report = self.measure()
        self.assertEqual([item["file"] for item in report["oddNames"]], [f"issue/{PROBE}/2026-09-01/head.md"])
        self.assertEqual(report["cardsTotal"], 1)
        self.assertNoChain(report)
        self.assertEqual({ref["status"] for ref in report["refs"]}, {"unresolved"})

    def test_undecodable_card_is_listed_as_unreadable_not_as_clean_bill(self):
        """读不动的卡既不计复发也不计未复发：单列 + 进口径声明（严格解码，不拿替换符硬扫成「扫过了」）。"""
        root = self.make([card("2026-09-01", "01-head.md", HEAD)])
        (root / f"issue/{PROBE}/2026-09-02").mkdir(parents=True)
        (root / f"issue/{PROBE}/2026-09-02/02-broken.md").write_bytes("# 极易复发\n".encode("utf-8") + b"\xff\xfe")
        report = self.measure(root)
        self.assertEqual([item["file"] for item in report["unreadable"]], [f"issue/{PROBE}/2026-09-02/02-broken.md"])
        self.assertEqual(report["cardsTotal"], 1)
        self.assertTrue(any("读不动" in caveat for caveat in report["caveats"]))
        self.assertIn("读不动", recurrence.render(report))

    def test_report_keeps_forbidden_grouping_and_na_rules_visible(self):
        """报告要把「不许用标题相似凑组」的禁区与 N/A 口径印出来，读数的人才知道这数怎么来的。"""
        self.make([card("2026-09-01", "01-head.md", HEAD)])
        rendered = recurrence.render(self.measure())
        for item in SHIPPED["forbidden"]:
            self.assertIn(item, rendered)
        self.assertIn(SHIPPED["naRule"], rendered)
        for key in ("narrowScope", "notAbsence", "denominatorNote"):
            self.assertIn(SHIPPED["caveats"][key], rendered)


class RealCorpusInvariants(RepoMixin):
    """真仓 issue/ 只读跑一遍：钉住「每条判定都能点回去」这条硬要求，不钉具体读数（读数会变）。"""

    def test_real_corpus_verdicts_are_all_point_verifiable(self):
        report = recurrence.measure(ROOT)
        self.assertGreaterEqual(report["cardsTotal"], 1)
        self.assertIsNotNone(report["value"])
        for edge in report["edges"]:
            relative, _, number = edge["where"].rpartition(":")
            lines = (ROOT / relative).read_text(encoding="utf-8").splitlines()
            self.assertTrue(0 < int(number) <= len(lines), edge["where"])
            body = " ".join(lines[int(number) - 1].split())
            self.assertIn(edge["snippet"].rstrip(SHIPPED["report"]["snippetEllipsis"]).replace("\\|", "|"), body)
        for chain in report["chains"]:
            self.assertEqual(len({node["rel"].split("/")[1] for node in chain["nodes"]}), 1,
                             "同一条链必须同 skill（chain.scope=sameSkill）")
            self.assertEqual([node["date"] for node in chain["nodes"]], sorted(node["date"] for node in chain["nodes"]))
        self.assertEqual(report["recurrences"], sorted({edge["source"] for edge in report["edges"]}))
        # 提到复发字的卡里，只有带显式指针的才计入（其余必须能在旁证区找到）
        self.assertEqual(report["cueCards"],
                         len(report["recurrences"]) + len(report["mentions"]))


if __name__ == "__main__":
    unittest.main()
