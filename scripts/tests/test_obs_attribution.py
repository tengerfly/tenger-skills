"""候选卡归因（条款级）的反向对照（plan v2 §5「归因到具体 skill 的具体条款（读轨迹原文）」）。

这一步最容易造假：机器猜一段「最像的正文」当责任条款，比不归因更坏——它会让人以为已经查过了。
所以每条判据都做双向对照，并**断言具体判据文本与 文件:行号**，不看退出码：

① 唯一逐字命中 ⇒ 归因，输出的必须是**条款正文原文 + 行区**，不是标题摘要；
② needle 只出现在标题行、正文没有，且注册表没声明锚点 ⇒ 必须落「未归因」（needle 口径没被放宽）；
③ 两段正文都命中 ⇒ 「多归属，需人裁决」，两处**全部列出**，不许挑一个当结论；
④ 一个产物被多个节点 glob 覆盖 ⇒ 同样多归属（路径归属本身就是歧义）；
⑤ issue 池目录名近似（多一个字母）⇒ 必须不命中并落未归因（只认逐字相等，不做近似匹配）；
⑥ needle／锚点词表／路由名单都来自注册表：改注册表必须改变结论（证明常量没写死在代码里）；
⑦ 注册表没有 attribution 节 ⇒ 拒绝开工，不猜一套口径；
⑧ 真实语料：本仓 issue 池路径必须能反查到 skill，并点到 shared 条款的行号；
⑨ 章节级同义锚点（`headingAnchors`）：锚点词只在 **## 标题文本**里逐字查，命中即证明「该 skill 正文
   有自己承接的章节」；正文里出现锚点词而标题没有 ⇒ 不算；撤掉 anchors ⇒ 必须退回未归因；
   锚点词短于 `minChars` ⇒ 拒用并写明原因；`match` 值不认识 ⇒ 拒绝按锚点执法（不猜口径）；
   锚点与 needle 同时命中 ⇒ 两处并列全部列出，仍走「多归属，需人裁决」。
⑩ 防刷分闸（`concentration`）：10 张卡全归到同一条条款 ⇒ 必须报「承接集中度异常」并标注命中率
   不可当质量结论使用；同样 10 张卡分散到两条条款 ⇒ 不得报异常；阈值/最小样本改注册表必须改变结论。
"""
from __future__ import annotations
import copy, re, sys, tempfile, unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from obs import attribution

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_FILE = ROOT / "governance/obs-registry.yaml"
REGISTRY = yaml.safe_load(REGISTRY_FILE.read_text(encoding="utf-8"))
POL = REGISTRY["attribution"]
VERDICTS = POL["verdicts"]
KIND = "缺回流用例"

SKILL_MD = """# Probe-Skill

## 无关段落

这一段说的是输入清单，跟回流没关系。

## 记录与回链

收尾时按 `../../shared/problem-recording.md` 建条目，并回链到来源 issue。

## Contract Compatibility Layer

Use the common Gate contract.
"""

SHARED = """# 问题记录、恢复与反哺

## 1. 触发与持久化

记录事实不要求先确认根因。

## 2. 从记录到反哺

先修项目，再复盘。反哺记录包括来源、改动位置、验证证据、适用边界及回退方式。
"""

# 承接章节夹具：正文里**没有**任何 needle 词，只有标题是注册表锚点词的逐字子串。
CARRIER_MD = """# Probe-Skill

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点记录；根因未明不丢事实。此段正文没有判据 operative 词。

## 一、定位与铁律

这一段讲的是输入清单。
"""

# 反面对照夹具：锚点词出现在**正文**里、标题没有 ⇒ 锚点不得算命中（锚点只认标题逐字）。
BODY_ONLY_ANCHOR_MD = """# Probe-Skill

## 一、定位与铁律

这段正文顺嘴提了一句问题记录与恢复，但它的标题里没有这个词。
"""


def card(kind=KIND, path="issue/Probe-Self/2026-01-01/01-x.md", node=None, surfaces=("relay",)):
    """最小候选卡：只用归因需要的字段（真实卡由 obs.candidates 派生，指针同源）。"""
    return {"id": "CAND-TEST", "kind": kind, "evidence": path, "surfaces": list(surfaces),
            "judges": [], "executionId": None, "node": node,
            "window": {"start": None, "end": None, "note": None}, "runLogRefs": [],
            "artifacts": [{"path": path, "recorded": None, "disk": None, "bytes": 1,
                           "ref": "", "note": ""}],
            "na": [], "boundary": "", "attribution": None}


class FixtureMixin(unittest.TestCase):
    """临时仓：skill 正文与注册表都是夹具自己造的，命中与否完全由 needle/锚点决定（不留巧合）。"""

    def make(self, skill_md=SKILL_MD, shared=SHARED, needles=("反哺记录",),
             alias="Probe-Self", second_node=None, anchors=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "governance").mkdir(parents=True)
        (root / "shared").mkdir(parents=True)
        (root / "Probe").mkdir(parents=True)

        nodes = [{"id": "probe", "skill": "probe", "paths": [".spec/prd/**"]}]
        if second_node:
            nodes.append({"id": second_node, "skill": second_node, "paths": [".spec/**"]})
        nodes_block = "\n".join(
            "  - {id: %s, skill: %s, paths: [%s]}" % (
                node["id"], node["skill"], ", ".join('"%s"' % item for item in node["paths"]))
            for node in nodes)
        declared = {"needles": list(needles), "basis": "夹具判据原文",
                    "ruleSource": REGISTRY["attribution"]["kinds"][KIND].get("ruleSource", "")}
        if anchors is not None:
            declared["anchors"] = list(anchors)          # 锚点词表由注册表给；代码里没有一份兜底词表
        kinds = {KIND: declared}
        attribution_section = copy.deepcopy(REGISTRY["attribution"])
        attribution_section["kinds"] = kinds
        registry_text = (
            "version: 1\nnodes:\n" + nodes_block + "\n"
            + yaml.safe_dump({"attribution": attribution_section}, allow_unicode=True, sort_keys=False)
            + yaml.safe_dump({"candidates": REGISTRY["candidates"]}, allow_unicode=True, sort_keys=False))
        (root / "governance/obs-registry.yaml").write_text(registry_text, encoding="utf-8")

        extra = "- id: probe2\n  path: Probe\n  status: active\n" if second_node else ""
        (root / "governance/skill-registry.yaml").write_text(
            "version: 2\nskills:\n"
            "- id: probe\n  path: Probe\n  status: active\n"
            f"  legacyAliases:\n  - {alias}\n" + extra +
            "- id: orphan\n  path: Other\n  status: active\n", encoding="utf-8")
        (root / "Probe/SKILL.md").write_text(skill_md, encoding="utf-8")
        if shared is not None:
            (root / "shared/problem-recording.md").write_text(shared, encoding="utf-8")
        pol = attribution.policy(root)
        return root, pol


class AttributionTests(FixtureMixin):
    def test_unique_body_hit_attributes_with_line_anchor_and_body_text(self):
        root, pol = self.make()
        result = attribution.attribute_card(root, card(), pol)
        self.assertEqual(result["verdict"], VERDICTS["attributed"], result["why"])
        self.assertEqual(len(result["clauses"]), 1)
        clause = result["clauses"][0]
        self.assertEqual(clause["file"], "shared/problem-recording.md")
        self.assertEqual(clause["needle"], "反哺记录")
        self.assertGreaterEqual(clause["startLine"], 1)          # 行号必须给出来，人能点回原文
        self.assertIn("反哺记录包括来源", clause["text"])          # 证据是正文原句
        self.assertNotEqual(clause["text"].strip(), "## 2. 从记录到反哺")  # 不是标题摘要
        self.assertEqual([row["skill"] for row in result["routes"]], ["probe"])
        self.assertIn("skill-registry.yaml:", result["routes"][0]["evidence"])

    def test_heading_only_match_is_not_evidence(self):
        # needle 只在标题行出现、正文没有 ⇒ 禁止把它当条款（这就是「用标题冒充条款」）
        heading_only = "# Probe\n\n## 反哺记录怎么做\n\n这一段只讲输入清单，没有那个词。\n"
        root, pol = self.make(skill_md=heading_only, shared=None)
        result = attribution.attribute_card(root, card(), pol)
        self.assertEqual(result["verdict"], VERDICTS["none"], result["why"])
        self.assertEqual(result["clauses"], [])
        self.assertIn("逐字查不到管辖条款", result["why"])

    def test_multiple_body_hits_are_listed_as_multi_owned(self):
        duplicated = SHARED + "\n## 3. 另一条也提反哺记录\n\n这里正文也逐字出现反哺记录。\n"
        root, pol = self.make(shared=duplicated)
        result = attribution.attribute_card(root, card(), pol)
        self.assertEqual(result["verdict"], VERDICTS["multiple"], result["why"])
        self.assertEqual(len(result["clauses"]), 2)               # 两处都必须列出
        self.assertEqual({clause["heading"] for clause in result["clauses"]},
                         {"## 2. 从记录到反哺", "## 3. 另一条也提反哺记录"})
        self.assertIn("多归属", result["verdict"])

    def test_two_routes_without_clauses_still_says_unattributed(self):
        root, pol = self.make(needles=("这个词正文里根本没有",))
        result = attribution.attribute_card(root, card(), pol)
        self.assertEqual(result["verdict"], VERDICTS["none"])
        self.assertIn("已定位 skill", result["why"])               # 断点要说清断在哪一跳

    def test_path_covered_by_two_node_globs_is_multi_owned(self):
        # 同一产物被两个节点 glob 覆盖，且两个节点声明不同 skill ⇒ 归属本身就是歧义，不许挑一个
        root, pol = self.make(second_node="probe2")
        result = attribution.attribute_card(root, card(path=".spec/prd/overview.md"), pol)
        routes = [row["route"] for row in result["routes"]]
        self.assertIn("artifactPathsGlob", routes)
        self.assertEqual({row["skill"] for row in result["routes"]}, {"probe", "probe2"})
        self.assertEqual(result["verdict"], VERDICTS["multiple"], result["why"])
        self.assertIn("多归属", result["verdict"])
        # 全部列出：两个 skill 都要出现在卡面路由表里，不能只剩一个「最像的」
        rendered = attribution.render_block(result)
        self.assertIn("probe2", rendered)
        self.assertIn("shared/problem-recording.md", rendered)

    def test_near_miss_directory_name_is_not_a_match(self):
        root, pol = self.make(alias="Probe-Self")
        result = attribution.attribute_card(root, card(path="issue/Probe-Selfx/2026-01-01/01.md"), pol)
        self.assertEqual(result["verdict"], VERDICTS["none"])
        self.assertTrue(any("逐字查不到" in item for item in result["brokenRoutes"]), result["brokenRoutes"])

    def test_run_log_node_route_maps_to_declared_skill(self):
        root, pol = self.make(needles=("输入清单",))
        result = attribution.attribute_card(root, card(node="probe"), pol)
        self.assertIn("runLogNode", [row["route"] for row in result["routes"]])
        self.assertEqual(result["skills"], [{"skill": "probe", "skillPath": "Probe"}])

    def test_unregistered_node_is_reported_not_guessed(self):
        root, pol = self.make()
        result = attribution.attribute_card(root, card(node="ghost-node"), pol)
        self.assertTrue(any("ghost-node" in item and "没有声明" in item
                            for item in result["brokenRoutes"]), result["brokenRoutes"])

    def test_shared_contract_enters_corpus_only_when_named_by_the_skill(self):
        # 正向：skill 正文逐字写了 shared 文件名 ⇒ 该契约进入语料
        root, pol = self.make()
        hit = attribution.attribute_card(root, card(), pol)
        self.assertIn("shared/problem-recording.md", hit["corpusFiles"])
        self.assertIn("Probe/SKILL.md", hit["corpusFiles"])
        self.assertEqual(hit["clauses"][0]["file"], "shared/problem-recording.md")

        # 反向：正文没写那个文件名 ⇒ shared 不许被默认塞进语料冒充它的责任条款
        no_ref = "# Probe\n\n## 记录与反哺\n\n反哺记录要回链到来源 issue，但本 skill 不引用问题记录契约。\n"
        root2, pol2 = self.make(skill_md=no_ref)
        result = attribution.attribute_card(root2, card(), pol2)
        self.assertEqual(result["corpusFiles"], ["Probe/SKILL.md"])
        self.assertEqual([clause["file"] for clause in result["clauses"]], ["Probe/SKILL.md"])
        self.assertEqual(result["verdict"], VERDICTS["attributed"], result["why"])

    def test_empty_needle_list_is_explicitly_unattributed(self):
        root, pol = self.make(needles=())
        result = attribution.attribute_card(root, card(), pol)
        self.assertEqual(result["verdict"], VERDICTS["none"])
        self.assertIn("没有声明 needle", result["why"])


class PolicyDrivenTests(FixtureMixin):
    def test_registry_controls_the_needle_set(self):
        # 同一份正文：needle 换成「输入清单」⇒ 命中的是另一段；换成不存在的词 ⇒ 未归因
        root, pol = self.make(needles=("输入清单",))
        result = attribution.attribute_card(root, card(), pol)
        self.assertEqual(result["verdict"], VERDICTS["attributed"])
        self.assertEqual(result["clauses"][0]["needle"], "输入清单")
        self.assertEqual(result["clauses"][0]["heading"], "## 无关段落")

        root2, pol2 = self.make(needles=("反哺记录", "输入清单"))
        both = attribution.attribute_card(root2, card(), pol2)
        self.assertEqual(both["verdict"], VERDICTS["multiple"])
        self.assertEqual(len(both["clauses"]), 2)

    def test_missing_attribution_section_refuses_to_guess(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "governance").mkdir(parents=True)
        (root / "governance/obs-registry.yaml").write_text(
            yaml.safe_dump({key: value for key, value in REGISTRY.items() if key != "attribution"},
                           allow_unicode=True), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            attribution.policy(root)
        self.assertIn("未声明 attribution 判据", str(caught.exception))

    def test_incomplete_attribution_section_refuses_defaults(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "governance").mkdir(parents=True)
        registry = copy.deepcopy(REGISTRY)
        del registry["attribution"]["routes"]
        (root / "governance/obs-registry.yaml").write_text(
            yaml.safe_dump(registry, allow_unicode=True), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            attribution.policy(root)
        self.assertIn("缺必需键", str(caught.exception))

    def test_missing_anchor_or_concentration_policy_refuses_defaults(self):
        """锚点机制与集中度阈值只有注册表里那一份：删掉就拒绝开工，不许代码里藏一套默认词表/阈值。"""
        for key in ("headingAnchors", "concentration"):
            tmp = tempfile.TemporaryDirectory()
            self.addCleanup(tmp.cleanup)
            root = Path(tmp.name)
            (root / "governance").mkdir(parents=True)
            registry = copy.deepcopy(REGISTRY)
            del registry["attribution"][key]
            (root / "governance/obs-registry.yaml").write_text(
                yaml.safe_dump(registry, allow_unicode=True), encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                attribution.policy(root)
            self.assertIn("缺必需键", str(caught.exception))
            self.assertIn(key, str(caught.exception))


class HeadingAnchorTests(FixtureMixin):
    """章节级同义锚点：只修「认不出 skill 自己的承接章节」这一格，不放宽 needle 的正文口径。"""

    def test_anchor_recognises_the_skills_own_carrier_section(self):
        root, pol = self.make(skill_md=CARRIER_MD, shared=None,
                             needles=("反哺记录",), anchors=("问题记录与恢复",))
        result = attribution.attribute_card(root, card(), pol)
        self.assertEqual(result["verdict"], VERDICTS["attributed"], result["why"])
        self.assertEqual(len(result["clauses"]), 1)
        clause = result["clauses"][0]
        self.assertEqual(clause["match"], "heading-anchor")
        self.assertEqual(clause["file"], "Probe/SKILL.md")
        self.assertEqual(clause["heading"], "## 问题记录与恢复（执行必需）")   # 标题逐字，人能点回原文
        self.assertEqual(clause["anchor"], "问题记录与恢复")
        self.assertEqual(clause["needle"], "")                        # 正文没有 needle：证据强度必须分得开
        self.assertNotIn("反哺记录", clause["text"])
        self.assertIn(POL["headingAnchors"]["anchorEvidence"], clause["evidenceClass"])
        rendered = attribution.render_block(result)
        self.assertIn("锚点命中的那段**只**证明该 skill 有自己承接这条义务的章节", rendered)

        # 反向对照：撤掉注册表里的 anchors ⇒ 同一份正文必须退回未归因（锚点没生效＝不是被放宽了）
        root2, pol2 = self.make(skill_md=CARRIER_MD, shared=None,
                                needles=("反哺记录",), anchors=())
        back = attribution.attribute_card(root2, card(), pol2)
        self.assertEqual(back["verdict"], VERDICTS["none"], back["why"])
        self.assertIn("逐字查不到管辖条款", back["why"])
        self.assertEqual(back["clauses"], [])

    def test_anchor_vocabulary_is_taken_from_the_registry_not_from_code(self):
        # 换一组锚点词（正文仍没 needle）⇒ 结论必须跟着变；词表写不死在代码里
        root, pol = self.make(skill_md=CARRIER_MD, shared=None,
                             needles=("反哺记录",), anchors=("运行问题埋点",))
        self.assertEqual(attribution.attribute_card(root, card(), pol)["verdict"], VERDICTS["none"])
        root2, pol2 = self.make(skill_md=CARRIER_MD, shared=None,
                               needles=("反哺记录",), anchors=("定位与铁律",))
        hit = attribution.attribute_card(root2, card(), pol2)
        self.assertEqual(hit["verdict"], VERDICTS["attributed"], hit["why"])
        self.assertEqual(hit["clauses"][0]["heading"], "## 一、定位与铁律")

    def test_anchor_word_in_body_but_not_in_heading_is_not_evidence(self):
        # 「内容看起来相关」不算证据：锚点词只在 ## 标题文本里逐字查
        root, pol = self.make(skill_md=BODY_ONLY_ANCHOR_MD, shared=None,
                             needles=("反哺记录",), anchors=("问题记录与恢复",))
        result = attribution.attribute_card(root, card(), pol)
        self.assertEqual(result["verdict"], VERDICTS["none"], result["why"])
        self.assertEqual(result["clauses"], [])

    def test_anchor_plus_body_needle_lists_both_and_refuses_to_pick(self):
        root, pol = self.make(needles=("反哺记录",), anchors=("记录与回链",))
        result = attribution.attribute_card(root, card(), pol)
        self.assertEqual(result["verdict"], VERDICTS["multiple"], result["why"])
        self.assertEqual(len(result["clauses"]), 2)                    # 两处并列全列，不挑「最像的那个」
        self.assertEqual({row["match"] for row in result["clauses"]}, {"heading-anchor", "needle-body"})
        self.assertEqual(result["clauses"][0]["file"], "Probe/SKILL.md")
        self.assertEqual(result["clauses"][1]["file"], "shared/problem-recording.md")

    def test_anchor_shorter_than_registry_min_chars_is_refused_with_reason(self):
        minimum = int(POL["headingAnchors"]["minChars"])
        short = "记录"
        self.assertLess(len(short), minimum)
        root, pol = self.make(skill_md=CARRIER_MD, shared=None,
                             needles=("反哺记录",), anchors=(short,))
        result = attribution.attribute_card(root, card(), pol)
        self.assertEqual(result["anchors"], [])
        self.assertEqual(result["verdict"], VERDICTS["none"], result["why"])
        expected = (str(POL["headingAnchors"]["shortAnchorReason"])
                    .replace("{anchor}", short).replace("{length}", str(len(short)))
                    .replace("{minChars}", str(minimum)))
        self.assertEqual(result["skippedAnchors"], [expected])          # 拒用要写明为什么，不许静默丢弃
        self.assertIn(f"长度 {len(short)} < headingAnchors.minChars={minimum}", expected)

    def test_unknown_anchor_match_mode_refuses_to_grade_by_anchor(self):
        root, pol = self.make(skill_md=CARRIER_MD, shared=None,
                             needles=("反哺记录",), anchors=("问题记录与恢复",))
        pol["headingAnchors"]["match"] = "semantic-similarity"
        with self.assertRaises(ValueError) as caught:
            attribution.attribute_card(root, card(), pol)
        self.assertIn("heading-verbatim", str(caught.exception))
        self.assertIn("拒绝按锚点执法", str(caught.exception))


class ConcentrationTests(FixtureMixin):
    """防刷分闸：一条条款撑起全部证据＝覆盖面窄，不是覆盖得好 ⇒ 命中率不得当质量结论。"""

    @staticmethod
    def many(n):
        return [card(path=f"issue/Probe-Self/2026-01-01/{index:02d}-x.md") for index in range(1, n + 1)]

    def test_ten_cards_on_one_clause_must_raise_the_alarm(self):
        from obs import candidates
        root, pol = self.make(needles=("反哺记录",))
        summary = attribution.attribute_all(root, self.many(10), pol)
        conc = summary["concentration"]
        self.assertEqual(conc["distinctClauses"], 1)
        self.assertEqual(conc["evidence"], 10)
        self.assertEqual(conc["top"]["file"], "shared/problem-recording.md")
        self.assertEqual(conc["top"]["evidence"], 10)
        self.assertAlmostEqual(conc["share"], 1.0)
        self.assertGreaterEqual(conc["share"], float(POL["concentration"]["maxClauseShare"]))
        self.assertTrue(conc["alarm"], conc)
        self.assertEqual(conc["label"], POL["concentration"]["alarmLabel"])
        self.assertEqual(conc["unusable"], POL["concentration"]["unusableLabel"])
        self.assertIn("100%", conc["reason"])
        text = "\n".join(candidates._attribution_lines(summary))
        self.assertIn("承接集中度异常", text)
        self.assertIn("本次证据化命中率不可当质量结论使用", text)
        self.assertIn("shared/problem-recording.md:", text)             # 报警必须指得出是哪一条

    def test_same_ten_cards_spread_over_clauses_must_not_alarm(self):
        from obs import candidates
        spread = SHARED + "\n## 3. 另一条也提反哺记录\n\n这里正文也逐字出现反哺记录。\n"
        root, pol = self.make(shared=spread, needles=("反哺记录",))
        summary = attribution.attribute_all(root, self.many(10), pol)
        conc = summary["concentration"]
        self.assertEqual(conc["distinctClauses"], 2)
        self.assertEqual(conc["evidence"], 20)
        self.assertAlmostEqual(conc["share"], 0.5)
        self.assertFalse(conc["alarm"], conc)
        text = "\n".join(candidates._attribution_lines(summary))
        self.assertNotIn("承接集中度异常", text)
        self.assertNotIn("不可当质量结论使用", text)

    def test_threshold_and_min_sample_come_from_the_registry(self):
        from obs import candidates
        spread = SHARED + "\n## 3. 另一条也提反哺记录\n\n这里正文也逐字出现反哺记录。\n"
        root, pol = self.make(shared=spread, needles=("反哺记录",))
        summary = attribution.attribute_all(root, self.many(10), pol)
        # 同一份数据、只把阈值改低 ⇒ 必须转成报警（0.6 没有写死在代码里）
        pol["concentration"]["maxClauseShare"] = 0.4
        again = attribution.concentration_report(pol, summary["clauses"], 10)
        self.assertTrue(again["alarm"], again)
        self.assertIn("40%", again["reason"])
        # 样本低于 minEvidence ⇒ 不报警，但必须如实写「未判」，不能读成「分散」
        minimum = int(POL["concentration"]["minEvidence"])
        self.assertGreater(minimum, 2)
        root2, pol2 = self.make(needles=("反哺记录",))
        small = attribution.attribute_all(root2, self.many(2), pol2)
        conc = small["concentration"]
        self.assertEqual(conc["evidence"], 2)
        self.assertFalse(conc["alarm"], conc)
        self.assertTrue(conc["belowSample"], conc)
        text = "\n".join(candidates._attribution_lines(small))
        self.assertIn(f"concentration.minEvidence={minimum}", conc["offSampleNote"])
        self.assertIn("样本太小", text)
        self.assertNotIn("承接集中度异常", text)


class RealCorpusTests(unittest.TestCase):
    """真实语料：本仓 issue 池路径既要能反查到 skill，也要能认出该 skill 自己的承接章节。"""

    # 本轮 24 张「缺回流用例」候选卡涉及的 11 个 skill（issue 池目录段 ↔ skill，取自真实卡面指针）
    AFFECTED = {
        "Backend-Tech-Design": ("backend-tech-design", "DEV/backend-tech-design/SKILL.md"),
        "Fidelity-Review": ("fidelity-review", "UI/fidelity-review/SKILL.md"),
        "Frontend-Dev": ("frontend-dev", "DEV/frontend-dev/SKILL.md"),
        "Frontend-Tech-Design": ("frontend-tech-design", "DEV/frontend-tech-design/SKILL.md"),
        "PRD-Design": ("prd-design", "PRD/prd-design/SKILL.md"),
        "Prototype-Review": ("prototype-review", "UI/prototype-review/SKILL.md"),
        "Skill-Optimizer": ("skill-optimizer", "Other/skill-optimizer/SKILL.md"),
        "Tech-Review": ("tech-review", "DEV/tech-review/SKILL.md"),
        "UI-UX-Design": ("ui-ux-design", "UI/ui-ux-design/SKILL.md"),
        "UI-UX-Review": ("ui-ux-review", "UI/ui-ux-review/SKILL.md"),
        "WorkFlow": ("workflow", "workflow/SKILL.md"),
    }

    def _heading_line(self, root: Path, relative: str, heading: str) -> int:
        """按真实文件算出该标题所在行号：证明卡上的行号指针不是编的。"""
        for number, line in enumerate((root / relative).read_text(
                encoding="utf-8", errors="replace").splitlines(), 1):
            if line.strip() == heading:
                return number
        raise AssertionError(f"{relative} 里没有标题行「{heading}」")

    def test_real_issue_path_lists_both_carrier_section_and_shared_clause(self):
        root = ROOT
        pol = attribution.policy(root)
        result = attribution.attribute_card(
            root, card(path="issue/Backend-Tech-Design/2026-09-07/01-选型澄清一两句即定稿拷问深度未落地.md"),
            pol)
        self.assertEqual([row["skill"] for row in result["routes"]], ["backend-tech-design"])
        self.assertIn("governance/skill-registry.yaml:", result["routes"][0]["evidence"])
        self.assertEqual(result["verdict"], VERDICTS["multiple"], result["why"])
        anchors = [row for row in result["clauses"] if row["match"] == "heading-anchor"]
        bodies = [row for row in result["clauses"] if row["match"] == "needle-body"]
        self.assertTrue(anchors, f"该 skill 的承接章节没被认出来：{result['clauses']}")
        carrier = anchors[0]
        self.assertEqual(carrier["file"], "DEV/backend-tech-design/SKILL.md")
        self.assertEqual(carrier["heading"], "## 问题记录与恢复（执行必需）")
        self.assertEqual(carrier["startLine"],
                         self._heading_line(root, carrier["file"], carrier["heading"]))
        self.assertEqual(carrier["anchor"], "问题记录与恢复")
        self.assertEqual([row["file"] for row in bodies], ["shared/problem-recording.md"])
        self.assertIn("反哺记录包括来源", bodies[0]["text"])
        self.assertGreaterEqual(bodies[0]["startLine"], 1)

    def test_every_affected_skill_has_its_own_carrier_section(self):
        """第 1 步那条「各 skill 正文没有承接条款」的结论必须可机械复核：11/11 有承接章节 ⇒ 量具故障。"""
        root, pol = ROOT, attribution.policy(ROOT)
        rows, missing = [], []
        for directory, (skill, relative) in sorted(self.AFFECTED.items()):
            result = attribution.attribute_card(
                root, card(path=f"issue/{directory}/2026-09-07/01-x.md"), pol)
            self.assertEqual([row["skill"] for row in result["routes"]], [skill],
                             f"{directory} 的目录段反查不到 {skill}（注册表别名变了先查路由，别改判据）")
            owned = [row for row in result["clauses"]
                     if row["match"] == "heading-anchor" and row["file"] == relative]
            if not owned:
                missing.append(skill)
            rows.append(f"{skill:22s} {relative:38s} "
                        + "｜".join(f'{row["heading"]}@{row["startLine"]}' for row in owned))
        self.assertEqual(missing, [], f"这些 skill 的 SKILL.md 确实没有逐字命中的承接章节：{missing}")
        self.assertEqual(len(rows), len(self.AFFECTED))
        for row in rows:
            self.assertIn("## 问题记录与恢复（执行必需）", row, row)

    def test_declared_anchor_words_exist_verbatim_in_real_skill_headings(self):
        """锚点词必须是真实 `## ` 标题里的逐字片段：编一个「看起来像」的锚点就是判据过宽。"""
        import yaml
        pol = attribution.policy(ROOT)
        gate = pol["headingAnchors"]
        registry = yaml.safe_load((ROOT / "governance/skill-registry.yaml").read_text(encoding="utf-8"))
        headings = set()
        for entry in registry["skills"]:
            relative = str(entry.get("path") or "")
            if not relative or "${" in relative:
                continue
            md = ROOT / relative / "SKILL.md"
            if not md.is_file():
                continue
            headings |= {line.strip() for line in
                         md.read_text(encoding="utf-8", errors="replace").splitlines()
                         if re.match(str(pol["headingPattern"]), line)}
        declared = [str(anchor) for spec in pol["kinds"].values() for anchor in (spec.get("anchors") or [])]
        self.assertTrue(declared, "注册表没有 anchors ⇒ 这一格没装，测试应显式失败而不是空过")
        for anchor in declared:
            self.assertGreaterEqual(len(anchor), int(gate["minChars"]), f"锚点「{anchor}」短于 minChars")
            self.assertTrue([heading for heading in headings if anchor in heading],
                            f"锚点词「{anchor}」在真实 ## 标题行里逐字不存在 ⇒ 不是同义锚点，是编的")

    def test_real_skill_clause_route_is_narrow_but_points_back_to_the_judge(self):
        # 该 kind 没声明 anchors（实测 45 份 SKILL.md 的任何 ## 标题里都没有「台账/绑定/未提交」这类词）
        # ⇒ 由脚本执法、正文无承接，必须落未归因，但要把判据原文的行号交出来；锚点不得越界放宽
        from obs import candidates
        root = ROOT
        pol = attribution.policy(root)
        self.assertEqual(pol["kinds"]["产物改了没落台账"].get("anchors") or [], [],
                         "该 kind 若加了 anchors，本条反向对照就得重写")
        probe = card(kind="产物改了没落台账", path="docs/目标进度表.md",
                     node="quality-inspection", surfaces=("verify",))
        result = attribution.attribute_card(root, probe, pol, candidates.policy(root))
        self.assertEqual(result["verdict"], VERDICTS["none"], result["why"])
        self.assertEqual([row["skill"] for row in result["routes"]], ["quality-inspection"])
        self.assertTrue(result["judgeSources"], "未归因也要能点回判据原文")
        located = [row for row in result["judgeSources"] if row["line"]]
        self.assertTrue(located, f"判据出处没定位到行：{result['judgeSources']}")
        self.assertIn("scripts/tsr.py", located[0]["file"])
        self.assertIn("def verify", located[0]["text"])

    def test_registry_needles_are_verbatim_from_the_judge_text(self):
        # 判据自己声明的 ruleSource 必须逐字可在原文里找到，否则 needle 的来路就是编的
        pol = attribution.policy(ROOT)
        rule = str(pol["kinds"][KIND]["ruleSource"])
        file_part, _, key = rule.partition(":")
        text = (ROOT / file_part).read_text(encoding="utf-8")
        self.assertIn(f"{key.rpartition('.')[2]}:", text, f"{rule} 在原文里逐字找不到")


if __name__ == "__main__":
    unittest.main()
