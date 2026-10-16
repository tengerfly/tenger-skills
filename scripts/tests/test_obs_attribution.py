"""候选卡归因（条款级）的反向对照（plan v2 §5「归因到具体 skill 的具体条款（读轨迹原文）」）。

这一步最容易造假：机器猜一段「最像的正文」当责任条款，比不归因更坏——它会让人以为已经查过了。
所以每条判据都做双向对照，并**断言具体判据文本与 文件:行号**，不看退出码：

① 唯一逐字命中 ⇒ 归因，输出的必须是**条款正文原文 + 行区**，不是标题摘要；
② needle 只出现在标题行、正文没有 ⇒ 必须落「未归因」（禁止用标题冒充条款）；
③ 两段正文都命中 ⇒ 「多归属，需人裁决」，两处**全部列出**，不许挑一个当结论；
④ 一个产物被多个节点 glob 覆盖 ⇒ 同样多归属（路径归属本身就是歧义）；
⑤ issue 池目录名近似（多一个字母）⇒ 必须不命中并落未归因（只认逐字相等，不做近似匹配）；
⑥ needle／路由名单都来自注册表：改注册表必须改变结论（证明常量没写死在代码里）；
⑦ 注册表没有 attribution 节 ⇒ 拒绝开工，不猜一套口径；
⑧ 真实语料：本仓 issue 池路径必须能反查到 skill，并点到 shared 条款的行号。
"""
from __future__ import annotations
import copy, sys, tempfile, unittest
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


def card(kind=KIND, path="issue/Probe-Self/2026-01-01/01-x.md", node=None, surfaces=("relay",)):
    """最小候选卡：只用归因需要的字段（真实卡由 obs.candidates 派生，指针同源）。"""
    return {"id": "CAND-TEST", "kind": kind, "evidence": path, "surfaces": list(surfaces),
            "judges": [], "executionId": None, "node": node,
            "window": {"start": None, "end": None, "note": None}, "runLogRefs": [],
            "artifacts": [{"path": path, "recorded": None, "disk": None, "bytes": 1,
                           "ref": "", "note": ""}],
            "na": [], "boundary": "", "attribution": None}


class FixtureMixin(unittest.TestCase):
    """临时仓：skill 正文与注册表都是夹具自己造的，命中与否完全由 needle 决定（不留巧合）。"""

    def make(self, skill_md=SKILL_MD, shared=SHARED, needles=("反哺记录",),
             alias="Probe-Self", second_node=None):
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
        kinds = {KIND: {"needles": list(needles), "basis": "夹具判据原文",
                        "ruleSource": REGISTRY["attribution"]["kinds"][KIND].get("ruleSource", "")}}
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


class RealCorpusTests(unittest.TestCase):
    """真实语料：本仓 issue 池的一条路径必须能反查到 skill 并点到 shared 条款行号。"""

    def test_real_issue_path_attributes_to_a_shared_clause(self):
        root = ROOT
        pol = attribution.policy(root)
        result = attribution.attribute_card(
            root, card(path="issue/Backend-Tech-Design/2026-09-07/01-选型澄清一两句即定稿拷问深度未落地.md"),
            pol)
        self.assertEqual([row["skill"] for row in result["routes"]], ["backend-tech-design"])
        self.assertIn("governance/skill-registry.yaml:", result["routes"][0]["evidence"])
        self.assertEqual(result["verdict"], VERDICTS["attributed"], result["why"])
        clause = result["clauses"][0]
        self.assertEqual(clause["file"], "shared/problem-recording.md")
        self.assertIn("反哺记录包括来源", clause["text"])
        self.assertGreaterEqual(clause["startLine"], 1)

    def test_real_skill_clause_route_is_narrow_but_points_back_to_the_judge(self):
        # 由脚本执法、skill 正文没有承接条款 ⇒ 必须落未归因，但要把判据原文的行号交出来
        from obs import candidates
        root = ROOT
        pol = attribution.policy(root)
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
