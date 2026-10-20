"""规则命中率的量具自验：先证明它会掉，再信它报的高。

plan v2 §4.3 的纪律在指标层同样成立：一个「无论有没有证据都报高命中率」的量具是空转。
这里用合成日志夹具钉住正反两组对照——读 3 条 + 引用 1 条必须得确定值，把证据删掉必须
变成 0 或 N/A；并且顺带钉住「换宿主只新增 spec、不改代码」这条硬约束。
单测只读临时目录里的合成日志，绝不碰引擎、不产生任何 API 花费。
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml
from obs import host_spec, rules

SESSION = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
WORKFLOW_SKILL = ("# Workflow\n说明行\n## 需求冻结前不问选型\n正文一\n## 批次编排\n正文二\n")
PRD_SKILL = "# PRD\n## 验收标准\n每条功能点给可测验收\n"
GATE_POLICY = ("# Gate Policy v2\n说明行\n## Gate 判定映射\nP0 一律 BLOCKED\n## 例外审批\n"
               "残留 P1 需授权\n## 尾节\n无内容\n")


def event(**fields):
    return json.dumps(fields, ensure_ascii=False)


def read_event(path, offset=None, limit=None, seq=1):
    args = {"file_path": path}
    if offset is not None:
        args["offset"] = offset
    if limit is not None:
        args["limit"] = limit
    return event(ts="2026-10-15T10:00:00.000+08:00", seq=seq, type="tool.requested",
                 data={"tool_name": "Read", "args": args})


class RuleHitRateTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.root = base / "repo"
        self.home = base / "host"
        self.segment = self.home / "logs/sessions/D--demo" / SESSION / "segments"
        self.segment.mkdir(parents=True)
        (self.root / "governance").mkdir(parents=True)
        (self.root / "governance/skill-registry.yaml").write_text(yaml.safe_dump(
            {"version": 2, "skills": [
                {"id": "workflow", "path": "workflow", "status": "active"},
                {"id": "prd-design", "path": "prd-design", "status": "active"},
                {"id": "archived-skill", "path": "archived", "status": "legacy"}]},
            allow_unicode=True), encoding="utf-8")
        for relative, text in (("workflow/SKILL.md", WORKFLOW_SKILL), ("prd-design/SKILL.md", PRD_SKILL),
                               ("shared/gate-policy.md", GATE_POLICY)):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        self.spec = host_spec.load("qoder")

    def trace(self, lines):
        (self.segment / "a.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
        found = host_spec.discover(self.spec, self.home, "")
        return host_spec.read_spans(self.spec, found)

    def measure(self, spans, skills=None):
        return rules.measure(self.root, self.spec, spans, skills=skills)

    def test_corpus_counts_sections_not_fences_or_frontmatter(self):
        # 基数=已注册 active skill 的 SKILL.md + shared/*.md 的二级标题；代码块与 legacy skill 不算条款
        corpus = rules.build_corpus(self.root, rules.metric_spec())
        self.assertEqual([clause["id"] for clause in corpus["clauses"]][:2],
                         ["workflow/SKILL.md § 需求冻结前不问选型", "workflow/SKILL.md § 批次编排"])
        self.assertEqual(len(corpus["clauses"]), 6)
        self.assertNotIn("archived/SKILL.md", {clause["file"] for clause in corpus["clauses"]})

    def test_read_three_plus_cite_one_gives_an_exact_rate(self):
        """正向：读 3 条（含区间读取与安装副本路径）+ 引用 1 条 → 命中率 = 4/6 = 66.7%。"""
        spans = self.trace([
            read_event(str(self.root / "workflow/SKILL.md"), offset=3, limit=1),
            read_event("C:/Users/me/.qoder-cn/skills/prd-design/SKILL.md", seq=2),
            read_event(str(self.root / "shared/gate-policy.md"), offset=3, limit=1, seq=3),
            event(ts="2026-10-15T10:00:04.000+08:00", seq=4, type="tool.requested",
                  data={"tool_name": "Bash",
                        "args": {"command": "grep -n 例外审批 shared/gate-policy.md"}}),
        ])
        report = self.measure(spans)
        self.assertEqual(report["declared"], 6)
        self.assertEqual((report["readHits"], report["citeHits"], report["hits"]), (3, 1, 4))
        self.assertAlmostEqual(report["value"], 4 / 6, places=6)
        # 区间读取只算覆盖到的条款：同文件的另一条必须是未命中
        misses = {item["id"] for item in report["misses"]}
        self.assertIn("workflow/SKILL.md § 批次编排", misses)
        self.assertIn("shared/gate-policy.md § 尾节", misses)

    def test_removing_the_citation_record_drops_the_rate(self):
        """反证一：引用记录是承重的——删掉它命中率必须掉下来，引用通道记 0 而不是留在数里。"""
        with_cite = self.measure(self.trace([
            read_event(str(self.root / "workflow/SKILL.md"), offset=3, limit=1),
            read_event(str(self.root / "shared/gate-policy.md"), offset=3, limit=1, seq=2),
            event(ts="2026-10-15T10:00:03.000+08:00", seq=3, type="tool.requested",
                  data={"tool_name": "Bash", "args": {"command": "cat 例外审批 shared/gate-policy.md"}}),
        ]))
        without = self.measure(self.trace([
            read_event(str(self.root / "workflow/SKILL.md"), offset=3, limit=1),
            read_event(str(self.root / "shared/gate-policy.md"), offset=3, limit=1, seq=2),
        ]))
        self.assertEqual((with_cite["hits"], without["hits"]), (3, 2))
        self.assertEqual((with_cite["citeHits"], without["citeHits"]), (1, 0))
        self.assertLess(without["value"], with_cite["value"])

    def test_stripping_the_evidence_records_gives_zero_not_a_high_rate(self):
        """反证二（空转检验）：证据记录换成与语料无关的读取 ⇒ 0.0，禁止默认成高分。

        这里故意保留一条合法的 Read（file_path 指向 .spec 产物），让 CLAUSE_READS 仍然授予：
        于是 0.0 只能来自「语料一条都没被读到」，而不是「没测」——量具若把没测当命中基线，
        这一条就会红。
        """
        stripped = self.trace([read_event(str(self.root / ".spec/prd/overview.md"))])
        report = self.measure(stripped)
        self.assertEqual(report["value"], 0.0)
        self.assertEqual((report["hits"], report["readHits"], report["citeHits"]), (0, 0, 0))
        self.assertEqual(report["declared"], 6)
        rendered = rules.render(report)
        self.assertIn("命中率：0.0%", rendered)
        self.assertNotIn("100", rendered.splitlines()[2])
        # 连一条工具事件都不剩 ⇒ 只能记 N/A（没测），不得记成 0 之后的「没问题」
        empty = self.measure(self.trace([event(ts="2026-10-15T10:00:00.000+08:00", seq=1,
                                               type="session.phase.finished", data={"phase": "start"})]))
        self.assertIsNone(empty["value"])
        self.assertIn("N/A", empty["reason"])

    def test_missing_capability_is_na_with_the_missing_field_named(self):
        """反证三：宿主有工具事件但读不到 file_path ⇒ N/A 并写明缺哪个字段，不许记 0 也不许记「没问题」。"""
        spans = self.trace([
            event(ts="2026-10-15T10:00:00.000+08:00", seq=1, type="tool.requested",
                  data={"tool_name": "Bash", "args": {}}),
            event(ts="2026-10-15T10:00:01.000+08:00", seq=2, type="loop.iteration.finished",
                  data={"tool_use_count": 3}),
        ])
        report = self.measure(spans)
        self.assertIsNone(report["value"])
        self.assertIn("N/A", report["reason"])
        self.assertIn("CLAUSE_READS", report["reason"])
        self.assertIn("data.args.file_path", report["reason"])

    def test_empty_clause_base_is_na_not_100_percent(self):
        empty_root = self.root.parent / "empty"
        (empty_root / "governance").mkdir(parents=True)
        (empty_root / "governance/skill-registry.yaml").write_text(
            yaml.safe_dump({"version": 2, "skills": []}), encoding="utf-8")
        report = rules.measure(empty_root, self.spec, self.trace([read_event("C:/elsewhere/x.md")]))
        self.assertIsNone(report["value"])
        self.assertIn("条款基数为 0", report["reason"])

    def test_cite_channel_degrades_when_host_carries_no_text(self):
        """硬约束①：核心逻辑不认宿主。第二家宿主字段名全不一样，只加 spec、不改 rules.py。

        它的 params 里没有可匹配的正文（EVIDENCE_TEXT 实测取不到）⇒ 引用通道记 N/A，
        命中率降级成「仅读取通道」并写进口径声明，不能冒充两通道。
        """
        other = {"discovery": {"layout": "trace/*.jsonl",
                               "sessionKey": {"from": "path", "pattern": "trace/(?P<session>[0-9a-f-]{36})/"}},
                 "fields": {"timestamp": "@when", "kind": "evt", "tool": "call.tool",
                            "arguments": "call.params", "loop": "call.turn"},
                 "kinds": {"toolCall": "call.started"},
                 "capabilities": [
                     {"id": "TOOL_EVENTS", "requires": {"fields": ["call.tool"]}},
                     {"id": "CLAUSE_READS", "requires": {"fields": ["call.tool", "call.params.fp"]},
                      "eventKinds": ["call.started"], "toolFilter": ["readFile"],
                      "pathField": "call.params.fp",
                      "rangeFields": {"offset": "call.params.from", "limit": "call.params.take"}},
                     {"id": "EVIDENCE_TEXT", "requires": {"fields": ["call.body"]},
                      "eventKinds": ["call.started"], "argsField": "call.body"}]}
        trace = self.home / "trace" / SESSION
        trace.mkdir(parents=True)
        (trace / "1.jsonl").write_text("\n".join([
            json.dumps({"@when": "2026-10-15T10:00:00Z", "evt": "call.started",
                        "call": {"tool": "readFile", "params": {"fp": str(self.root / "shared/gate-policy.md"),
                                                                "from": 3, "take": 1}}}),
            json.dumps({"@when": "2026-10-15T10:00:01Z", "evt": "call.started",
                        "call": {"tool": "run", "params": {"cmd": "grep 例外审批 shared/gate-policy.md"}}}),
        ]) + "\n", encoding="utf-8")
        spans = host_spec.read_spans(other, [(SESSION, trace / "1.jsonl")])
        report = rules.measure(self.root, other, spans)
        self.assertEqual(report["readHits"], 1)
        self.assertEqual(report["citeHits"], 0)
        self.assertFalse(report["channels"]["EVIDENCE_TEXT"]["granted"])
        self.assertIn("仅读取通道", " ".join(report["caveats"]))
        self.assertAlmostEqual(report["value"], 1 / 6, places=6)

    def test_loose_generic_words_cannot_fake_a_citation(self):
        """防自欺：指针必须是 <skill 目录>/SKILL.md 这一串，通用词拼不出一次引用。

        「workflow 的 SKILL.md」+「批次编排」这种松散同现若算命中，命中率就会因为
        Outputs / Evidence 这类通用标题虚高，精简决策会反过来被量具骗。
        """
        loose = self.trace([event(ts="2026-10-15T10:00:00.000+08:00", seq=1, type="tool.requested",
                                  data={"tool_name": "Write",
                                        "args": {"file_path": str(self.root / ".spec/x.md"),
                                                 "content": "参考 workflow 的 SKILL.md，注意 批次编排 与 尾节"}})])
        self.assertEqual(self.measure(loose)["citeHits"], 0)
        exact = self.trace([event(ts="2026-10-15T10:00:00.000+08:00", seq=1, type="tool.requested",
                                  data={"tool_name": "Write",
                                        "args": {"file_path": str(self.root / ".spec/x.md"),
                                                 "content": "按 workflow/SKILL.md 的「批次编排」执行"}})])
        self.assertEqual(self.measure(exact)["citeHits"], 1)

    def test_skill_scoped_corpus_keeps_shared_contracts_in_the_base(self):
        spans = self.trace([read_event(str(self.root / "workflow/SKILL.md"))])
        report = self.measure(spans, skills=["workflow"])
        self.assertEqual(report["declared"], 5)          # workflow 2 条 + shared 3 条
        self.assertEqual(report["hits"], 2)
        self.assertIn("--skill 只收窄", " ".join(report["caveats"]))

    def test_report_never_carries_host_body_text(self):
        """隐私白名单：正文只做内存内匹配，报告里只能有条款 id 与计数。"""
        spans = self.trace([event(ts="2026-10-15T10:00:00.000+08:00", seq=1, type="tool.requested",
                                  data={"tool_name": "Write",
                                        "args": {"file_path": str(self.root / ".spec/prd/x.md"),
                                                 "content": "依据 shared/gate-policy.md 的 例外审批 规则，SECRET-BODY-不要外泄"}})])
        report = self.measure(spans)
        self.assertEqual(report["citeHits"], 1)
        self.assertNotIn("SECRET-BODY", rules.render(report))

    def test_unregistered_metric_id_is_an_error_not_a_silent_default(self):
        with self.assertRaises(ValueError):
            rules.metric_spec("made_up_metric")


if __name__ == "__main__":
    unittest.main()
