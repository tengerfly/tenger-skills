"""①客观数据的达成判据（obs.metrics.objective_status）对照。

排序第 1 格的 ☑ 判据原文是「run-log 里除运维节点外至少 1 个业务节点完整 start→end，且 report 能算出
该节点的墙钟与产物 sha」。在此之前这句话只能靠人读看板判断：看板对「元工作轨」和「业务轨」长得一模一样，
`summarize` 连 sha 都不取（只有字节数）。本文件钉住四件事：

① 口径来自注册表 `objectiveData`，缺节／缺键／缺文案 ⇒ 报错，不猜「哪个节点算业务」；
② 三格（完整收口／产物 sha／墙钟可解析）任一取不到 ⇒ 整条判未满足，并写明缺哪一格；
③ **运维节点不得冒充业务节点**，反向对照是把 `opsNodes` 清空后同一输入必须判「满足」——
   证明挡下来的是闸门而不是代码写死（本仓每条闸门都要配这一条）；
④ 看板要真的把 sha 印出来（判据点名要的东西不能只在台账里存在、不在读数里出现）。
"""
from __future__ import annotations
import copy, shutil, sys, tempfile, unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from obs import metrics

ROOT = Path(__file__).resolve().parents[2]
POLICY = metrics.load_objective_policy()
V = POLICY["verdicts"]


def event(node, ident, kind, ts, artifacts=()):
    item = {"schema": "tenger.trace/v1", "event": kind, "project": "probe", "executionId": ident,
            "node": node, "skill": node, "role": "produce", "actor": "main", "origin": "self",
            "ts": ts, "artifacts": [], "upstream": []}
    if kind == "node-end":
        item["gate"] = "PASS"
        item["allowDownstream"] = True
        item["artifacts"] = [{"path": path, "sha256": sha, "bytes": 20} for path, sha in artifacts]
    return item


def pair(node, ident, start="2026-10-17T09:00:00+08:00", end="2026-10-17T09:42:10+08:00", artifacts=((".spec/prd/overview.md", "b" * 64),)):
    return [event(node, ident, "node-start", start), event(node, ident, "node-end", end, artifacts)]


OPS = pair("quality-inspection", "EXEC-OPS-1", artifacts=(("governance/x.yaml", "a" * 64),))
BIZ = pair("prd-design", "EXEC-BIZ-1")


class PolicyGateTests(unittest.TestCase):
    """口径只能在注册表里：缺了就报错，不许退回代码内默认值。"""

    def with_registry(self, mutate):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
        (tmp / "governance").mkdir(parents=True)
        data = yaml.safe_load(metrics.REGISTRY.read_text(encoding="utf-8"))
        mutate(data)
        target = tmp / "governance/obs-registry.yaml"
        target.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        return target

    def test_absent_section_refuses_to_guess_business_nodes(self):
        original = metrics.REGISTRY
        metrics.REGISTRY = self.with_registry(lambda data: data.pop("objectiveData"))
        self.addCleanup(setattr, metrics, "REGISTRY", original)
        with self.assertRaises(ValueError) as caught:
            metrics.load_objective_policy()
        self.assertIn("未声明 objectiveData ⇒ 不猜业务节点从哪来", str(caught.exception))

    def test_missing_key_refuses_defaults(self):
        original = metrics.REGISTRY
        metrics.REGISTRY = self.with_registry(lambda data: data["objectiveData"].pop("digestColumn"))
        self.addCleanup(setattr, metrics, "REGISTRY", original)
        with self.assertRaises(ValueError) as caught:
            metrics.load_objective_policy()
        self.assertIn("objectiveData 缺必需键", str(caught.exception))
        self.assertIn("digestColumn", str(caught.exception))

    def test_missing_verdict_text_refuses_defaults(self):
        original = metrics.REGISTRY
        metrics.REGISTRY = self.with_registry(
            lambda data: data["objectiveData"]["verdicts"].pop("missingDigest"))
        self.addCleanup(setattr, metrics, "REGISTRY", original)
        with self.assertRaises(ValueError) as caught:
            metrics.load_objective_policy()
        self.assertIn("objectiveData.verdicts 缺文案", str(caught.exception))
        self.assertIn("missingDigest", str(caught.exception))


    def test_typo_in_ops_nodes_refuses_instead_of_faking_green(self):
        # 名单里一个字母写错，那条运维轨就会被当业务节点 ⇒ ①假绿；这种错必须拒绝开工
        original = metrics.REGISTRY
        metrics.REGISTRY = self.with_registry(
            lambda data: data["objectiveData"]["opsNodes"].append("quality-inspections"))
        self.addCleanup(setattr, metrics, "REGISTRY", original)
        with self.assertRaises(ValueError) as caught:
            metrics.load_objective_policy()
        self.assertIn("点名了未注册的节点", str(caught.exception))
        self.assertIn("quality-inspections", str(caught.exception))


class VerdictTests(unittest.TestCase):
    def test_business_node_with_clock_and_digest_satisfies(self):
        status = metrics.objective_status(BIZ + OPS, POLICY)
        self.assertTrue(status["satisfied"], status["reason"])
        self.assertEqual(V["satisfied"], status["reason"])
        item = [run for run in status["businessComplete"] if run["node"] == "prd-design"][0]
        self.assertEqual(2530.0, item["seconds"])
        self.assertEqual(["b" * 64], item["digests"])

    def test_ops_only_track_is_not_proof(self):
        status = metrics.objective_status(OPS, POLICY)
        self.assertFalse(status["satisfied"])
        self.assertEqual(V["noBusinessNode"], status["reason"])
        self.assertEqual(["quality-inspection"], status["opsRuns"], "要能看出挡路的是运维轨，不是说没数据")

    def test_business_node_without_bound_digest_is_half_done(self):
        status = metrics.objective_status(pair("prd-design", "EXEC-B", artifacts=()), POLICY)
        self.assertFalse(status["satisfied"])
        self.assertIn(V["missingDigest"], status["reason"])
        self.assertIn(POLICY["naRule"], status["reason"], "未满足要写明缺哪一格，不能只说「不行」")

    def test_unparsable_timestamp_is_never_estimated_as_zero(self):
        status = metrics.objective_status(
            pair("prd-design", "EXEC-C", start="昨天", end="前天"), POLICY)
        self.assertFalse(status["satisfied"])
        self.assertIn(V["wallClockUnparsable"], status["reason"])
        self.assertIsNone(status["businessComplete"][0]["seconds"])

    def test_start_without_end_is_not_a_complete_run(self):
        status = metrics.objective_status([event("prd-design", "EXEC-D", "node-start",
                                                 "2026-10-17T09:00:00+08:00")], POLICY)
        self.assertFalse(status["satisfied"])
        self.assertEqual(V["noBusinessNode"], status["reason"], POLICY["completePair"])

    def test_latest_binding_is_the_promise_not_the_first_one(self):
        # 同族教训：只有最后一次 node-end 才是对当下的承诺（与 tsr verify 同口径）
        events = (pair("prd-design", "EXEC-E", artifacts=((".spec/prd/overview.md", "1" * 64),))
                  + [event("prd-design", "EXEC-E", "node-end", "2026-10-17T10:00:00+08:00",
                           ((".spec/prd/overview.md", "2" * 64),))])
        status = metrics.objective_status(events, POLICY)
        self.assertEqual(["2" * 64], status["businessComplete"][0]["digests"])

    def test_emptying_ops_nodes_proves_the_gate_not_hardcoding(self):
        # 反向对照：同一份「只有运维轨」的输入，撤掉 opsNodes 就必须判满足 ⇒ 说明上一条的红来自闸门
        status = metrics.objective_status(OPS, dict(POLICY, opsNodes=[]))
        self.assertTrue(status["satisfied"], V["opsNodesAreNotProof"])


class BoardTests(unittest.TestCase):
    def test_board_prints_the_digest_the_criterion_asks_for(self):
        text = metrics.render(metrics.summarize(BIZ + OPS), [], [],
                              metrics.objective_status(BIZ + OPS, POLICY), POLICY)
        self.assertIn("产物 sha（最新绑定）", text)
        self.assertIn("b" * POLICY["digestColumn"], text)
        self.assertIn("✅", text)
        self.assertIn("墙钟 2530s", text)

    def test_board_marks_missing_binding_as_na_not_blank(self):
        events = pair("prd-design", "EXEC-F", artifacts=())
        text = metrics.render(metrics.summarize(events), [], [],
                              metrics.objective_status(events, POLICY), POLICY)
        self.assertIn("N/A (未绑定)", text)
        self.assertIn("⛔", text)

    def test_legacy_callers_still_render(self):
        # render 的第三方参数是可选的：老调用（三参）不许因为加了判据行而炸
        text = metrics.render(metrics.summarize(BIZ), [], [])
        self.assertIn("耗时(秒)", text)
        self.assertNotIn("①客观数据判据", text)


class RealRepoTests(unittest.TestCase):
    def test_current_track_is_meta_work_and_says_so(self):
        from obs import schema
        events = schema.read_events(ROOT)
        status = metrics.objective_status(events, POLICY)
        self.assertIn(status["reason"], [V[key] for key in
                                         ("noBusinessNode", "missingDigest", "wallClockUnparsable", "satisfied")])
        if not status["satisfied"]:
            self.assertTrue(status["opsRuns"], "报「未满足」时必须指出轨上到底有什么，不能空口")


if __name__ == "__main__":
    unittest.main()
