"""Derived metrics over the portable run log.

Everything here is computed from `tenger.trace/v1` events, so it survives a host change.
Anything the run log cannot know is reported as N/A with the reason rather than being
estimated — an unlabelled estimate would be indistinguishable from a measurement later.
"""
from __future__ import annotations
import fnmatch
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[2] / "governance/obs-registry.yaml"
NO_TOKEN_REASON = "N/A (宿主不输出 token；两源实测均为 0，此处只有字节代理)"


OBJECTIVE_KEYS = ("opsNodes", "opsNodesNote", "completePair", "digestSource", "digestColumn", "verdicts", "naRule")
VERDICT_KEYS = ("satisfied", "noBusinessNode", "missingDigest", "wallClockUnparsable", "opsNodesAreNotProof")


def load_objective_policy() -> dict:
    """①客观数据判据的口径来自注册表；缺节或缺文案就报错，不猜「哪个节点算业务」。"""
    import yaml
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read objectiveData from {REGISTRY.name}: {exc}") from exc
    section = data.get("objectiveData")
    if not isinstance(section, dict):
        raise ValueError(f"{REGISTRY.name} 未声明 objectiveData ⇒ 不猜业务节点从哪来")
    missing = [key for key in OBJECTIVE_KEYS if key not in section or section[key] in (None, "", [])]
    if missing:
        raise ValueError(f"objectiveData 缺必需键 {missing} ⇒ 拒绝用默认值冒充实装")
    verdicts = section["verdicts"]
    absent = [key for key in VERDICT_KEYS if not str(verdicts.get(key) or "").strip()]
    if absent:
        raise ValueError(f"objectiveData.verdicts 缺文案 {absent} ⇒ 判定结果必须逐条有名有姓")
    registered = {str(node.get("id")) for node in (data.get("nodes") or []) if node.get("id")}
    unknown_ops = [str(name) for name in section["opsNodes"] if str(name) not in registered]
    if unknown_ops:
        # 名单里写错一个节点名，就等于把那条运维轨悄悄算成业务节点 ⇒ ①会假绿。宁可不跑也不猜。
        raise ValueError(f"objectiveData.opsNodes 点名了未注册的节点 {unknown_ops} ⇒ "
                         f"拼错的排除名单会把元工作轨读成业务数据，拒绝据此判「满足」")
    return section


def load_registry() -> dict:
    import yaml
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read obs registry: {exc}") from exc
    nodes = {}
    for node in data.get("nodes") or []:
        node_id = str(node.get("id", ""))
        if node_id:
            nodes[node_id] = {"skill": str(node.get("skill", "")), "paths": list(node.get("paths") or [])}
    if not nodes:
        raise ValueError("obs registry declares no nodes")
    return nodes


def attribute_write(node_map: dict, path: str):
    """Map a write event to a node by artifact location — the primary attribution signal."""
    portable = str(path).replace("\\", "/")
    for node_id, spec in node_map.items():
        if any(fnmatch.fnmatch(portable, pattern) for pattern in spec["paths"]):
            return node_id
    return None


def _seconds(first: str, last: str):
    from datetime import datetime
    try:
        return (datetime.fromisoformat(last) - datetime.fromisoformat(first)).total_seconds()
    except (TypeError, ValueError):
        return None


def summarize(events: list) -> dict:
    nodes = {}
    for event in events:
        node = nodes.setdefault(event.get("node"), {"skill": event.get("skill"), "starts": 0, "ends": 0,
                                                    "gates": {}, "rounds": set(), "batches": set(),
                                                    "artifacts": 0, "bytes": 0, "first_ts": event.get("ts"),
                                                    "last_ts": event.get("ts"), "sunk": set(), "actors": set(),
                                                    "last_digests": []})
        node["last_ts"] = event.get("ts") or node["last_ts"]
        node["actors"].add(event.get("actor"))
        if event["event"] == "node-start":
            node["starts"] += 1
        if event["event"] == "node-end":
            node["ends"] += 1
            gate = event.get("gate")
            node["gates"][gate] = node["gates"].get(gate, 0) + 1
            # 只有最后一次 node-end 的绑定才是对当下的承诺（与 tsr verify 同口径），逐次覆盖
            node["last_digests"] = [str(item.get("sha256")) for item in (event.get("artifacts") or [])
                                    if item.get("sha256")]
            for artifact in event.get("artifacts") or []:
                node["artifacts"] += 1
                node["bytes"] += int(artifact.get("bytes") or 0)
        if isinstance(event.get("round"), int):
            node["rounds"].add(event["round"])
        if isinstance(event.get("batch"), int):
            node["batches"].add(event["batch"])
        for decision in event.get("sunkOf") or []:
            node["sunk"].add(decision)

    for node in nodes.values():
        node["elapsed"] = _seconds(node["first_ts"], node["last_ts"])
        node["max_round"] = max(node["rounds"]) if node["rounds"] else 0
        node["max_batch"] = max(node["batches"]) if node["batches"] else 0

    review_ends = [e for e in events if e.get("role") in {"review", "recheck"} and e["event"] == "node-end"]
    rerun = [e for e in review_ends if isinstance(e.get("round"), int) and e["round"] > 1]
    blocked = [e for e in events if e["event"] == "node-end" and e.get("gate") == "BLOCKED"]
    open_nodes = sorted(name for name, node in nodes.items() if node["starts"] > node["ends"])
    subagent = sorted({str(a) for node in nodes.values() for a in node["actors"] if a and a != "main"})
    return {
        "events": len(events),
        "executions": len({e.get("executionId") for e in events}),
        "nodes": nodes,
        "review_rounds": len(review_ends),
        "rework_rate": (len(rerun) / len(review_ends)) if review_ends else None,
        "blocked_ends": len(blocked),
        "open_nodes": open_nodes,
        "non_main_actors": subagent,
        "sunk_decisions": sorted({d for node in nodes.values() for d in node["sunk"]}),
        "artifact_bytes": sum(node["bytes"] for node in nodes.values()),
    }


def objective_status(events: list, policy: dict) -> dict:
    """①客观数据达成没有：按 executionId 找「业务节点的完整 start→end ＋ 产物 sha ＋ 墙钟可解析」。

    运维节点（注册表 opsNodes）不计入——排序表的红线是「不用运维节点冒充业务节点」；
    判据里三格（完整收口／sha／墙钟）任一取不到就整条判未满足并写明缺哪一格。
    """
    ops = {str(name) for name in policy["opsNodes"]}
    runs: dict = {}
    for event in events:
        ident = event.get("executionId")
        run = runs.setdefault(ident, {"executionId": ident, "node": event.get("node"), "starts": 0, "ends": 0,
                                      "first_ts": event.get("ts"), "last_ts": event.get("ts"),
                                      "digests": []})
        run["last_ts"] = event.get("ts") or run["last_ts"]
        if event["event"] == "node-start":
            run["starts"] += 1
        elif event["event"] == "node-end":
            run["ends"] += 1
            run["digests"] = [str(item.get("sha256")) for item in (event.get("artifacts") or [])
                              if item.get("sha256")]
    complete = [run for run in runs.values()
                if run["node"] not in ops and run["starts"] and run["ends"]]
    verdicts = policy["verdicts"]
    if not complete:
        return {"satisfied": False, "reason": verdicts["noBusinessNode"],
                "opsRuns": sorted({str(run["node"]) for run in runs.values() if run["node"] in ops}),
                "businessComplete": []}
    scored = []
    for run in complete:
        seconds = _seconds(run["first_ts"], run["last_ts"])
        scored.append({"node": run["node"], "executionId": run["executionId"], "seconds": seconds,
                       "digests": run["digests"], "first_ts": run["first_ts"], "last_ts": run["last_ts"]})
    passed = [item for item in scored if item["seconds"] is not None and item["digests"]]
    if not passed:
        missing_digest = [item for item in scored if not item["digests"]]
        reason = verdicts["missingDigest"] if missing_digest else verdicts["wallClockUnparsable"]
        return {"satisfied": False, "reason": f"{reason}｜{policy['naRule']}",
                "opsRuns": sorted({str(run["node"]) for run in runs.values() if run["node"] in ops}),
                "businessComplete": scored}
    return {"satisfied": True, "reason": verdicts["satisfied"],
            "opsRuns": sorted({str(run["node"]) for run in runs.values() if run["node"] in ops}),
            "businessComplete": scored, "passed": passed}


def render(report: dict, node_errors: list, problems: list, objective: dict | None = None,
           policy: dict | None = None) -> str:
    lines = ["# 体系观测看板", ""]
    rate = report["rework_rate"]
    lines += [f"- 事件 {report['events']} 条｜执行 {report['executions']} 次｜产物 {report['artifact_bytes']} 字节",
              f"- 评审交接 {report['review_rounds']} 次，返工率 {('N/A (无评审交接)' if rate is None else format(rate, '.0%'))}",
              f"- `BLOCKED` 交接 {report['blocked_ends']} 次｜未收口节点 {len(report['open_nodes'])} 个",
              f"- token/成本：{NO_TOKEN_REASON}"]
    if objective is not None:
        mark = "✅" if objective["satisfied"] else "⛔"
        ops = f"（运维节点 {len(objective['opsRuns'])} 个：{', '.join(objective['opsRuns']) or '无'}，不计入）"
        lines.append(f"- {mark} {objective['reason']}{ops if not objective['satisfied'] else ''}")
        for item in (objective.get("businessComplete") or [])[:6]:
            clock = "N/A (时间戳不可解析)" if item["seconds"] is None else f"{item['seconds']:.0f}s"
            digest = item["digests"][0][:12] if item["digests"] else "N/A (未绑定)"
            lines.append(f"  - `{item['node']}`（{item['executionId']}）墙钟 {clock}｜产物 sha `{digest}`"
                         f"｜绑定 {len(item['digests'])} 个")
    lines.append("")
    if report["sunk_decisions"]:
        lines += [f"- 沉没登记：{', '.join(report['sunk_decisions'])}（口径=作废 DEC 的 lineage 闭包 ∩ 时间切点，非日期窗）", ""]
    width = int((policy or {}).get("digestColumn") or 12)
    lines += ["| 节点 | skill | 耗时(秒) | 最大轮次 | 最大批次 | Gate 分布 | 产物数 | 字节 | 产物 sha（最新绑定） |",
              "|---|---|---|---|---|---|---|---|---|"]
    for name in sorted(report["nodes"]):
        node = report["nodes"][name]
        elapsed = "N/A (时间戳不可解析)" if node["elapsed"] is None else f"{node['elapsed']:.0f}"
        gates = ", ".join(f"{k}×{v}" for k, v in sorted(node["gates"].items())) or "—"
        digests = node.get("last_digests") or []
        shown = (f"{digests[0][:width]}＋{len(digests) - 1} 个" if len(digests) > 1
                 else (digests[0][:width] if digests else "N/A (未绑定)"))
        lines.append(f"| {name} | {node['skill']} | {elapsed} | {node['max_round']} | {node['max_batch']} | {gates} | {node['artifacts']} | {node['bytes']} | {shown} |")
    if node_errors:
        lines += ["", "## 未注册节点（判为缺陷，不作数据点）", *[f"- {error}" for error in node_errors]]
    if problems:
        lines += ["", "## 待处置异常", *[f"- {problem}" for problem in problems]]
    if report["open_nodes"]:
        lines += ["", f"## 进行中/未收口：{', '.join(report['open_nodes'])}"]
    return "\n".join(lines) + "\n"
