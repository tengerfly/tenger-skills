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
                                                    "last_ts": event.get("ts"), "sunk": set(), "actors": set()})
        node["last_ts"] = event.get("ts") or node["last_ts"]
        node["actors"].add(event.get("actor"))
        if event["event"] == "node-start":
            node["starts"] += 1
        if event["event"] == "node-end":
            node["ends"] += 1
            gate = event.get("gate")
            node["gates"][gate] = node["gates"].get(gate, 0) + 1
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


def render(report: dict, node_errors: list, problems: list) -> str:
    lines = ["# 体系观测看板", ""]
    rate = report["rework_rate"]
    lines += [f"- 事件 {report['events']} 条｜执行 {report['executions']} 次｜产物 {report['artifact_bytes']} 字节",
              f"- 评审交接 {report['review_rounds']} 次，返工率 {('N/A (无评审交接)' if rate is None else format(rate, '.0%'))}",
              f"- `BLOCKED` 交接 {report['blocked_ends']} 次｜未收口节点 {len(report['open_nodes'])} 个",
              f"- token/成本：{NO_TOKEN_REASON}", ""]
    if report["sunk_decisions"]:
        lines += [f"- 沉没登记：{', '.join(report['sunk_decisions'])}（口径=作废 DEC 的 lineage 闭包 ∩ 时间切点，非日期窗）", ""]
    lines += ["| 节点 | skill | 耗时(秒) | 最大轮次 | 最大批次 | Gate 分布 | 产物数 | 字节 |",
              "|---|---|---|---|---|---|---|---|"]
    for name in sorted(report["nodes"]):
        node = report["nodes"][name]
        elapsed = "N/A (时间戳不可解析)" if node["elapsed"] is None else f"{node['elapsed']:.0f}"
        gates = ", ".join(f"{k}×{v}" for k, v in sorted(node["gates"].items())) or "—"
        lines.append(f"| {name} | {node['skill']} | {elapsed} | {node['max_round']} | {node['max_batch']} | {gates} | {node['artifacts']} | {node['bytes']} |")
    if node_errors:
        lines += ["", "## 未注册节点（判为缺陷，不作数据点）", *[f"- {error}" for error in node_errors]]
    if problems:
        lines += ["", "## 待处置异常", *[f"- {problem}" for problem in problems]]
    if report["open_nodes"]:
        lines += ["", f"## 进行中/未收口：{', '.join(report['open_nodes'])}"]
    return "\n".join(lines) + "\n"
