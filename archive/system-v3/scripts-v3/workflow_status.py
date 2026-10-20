"""Read-only view of persisted workflow state; never advances or validates a Gate."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validate_core import GATES, LIFECYCLES, load_yaml


TEXT_FIELDS = (
    "workflowId", "projectId", "executionId", "lifecycle", "state",
    "currentSkill", "gate", "nextAction", "revision",
)
REF_FIELDS = ("artifactRefs", "evidenceRefs", "decisionRefs")


def snapshot(project_root: Path) -> dict:
    source = project_root.resolve() / ".spec/workflow.yaml"
    if not source.is_file():
        raise ValueError("没有正式流程状态文件；可能是轻量任务或尚未建档，请读取已有任务摘要，不推断已完成。")
    data = load_yaml(source)
    if not isinstance(data, dict):
        raise ValueError("workflow.yaml 必须是映射；当前状态待核验。")
    for key in TEXT_FIELDS:
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"workflow.yaml 缺失或无效字段：{key}；当前状态待核验。")
    if data["gate"] not in GATES or data["lifecycle"] not in LIFECYCLES:
        raise ValueError("workflow.yaml Gate 或生命周期无效；当前状态待核验。")
    if type(data.get("allowDownstream")) is not bool:
        raise ValueError("allowDownstream 必须为布尔值；当前状态待核验。")
    if data["gate"] == "BLOCKED" and data["allowDownstream"]:
        raise ValueError("BLOCKED 与 allowDownstream=true 冲突；不能视为允许推进。")
    for key in REF_FIELDS:
        refs = data.get(key)
        if not isinstance(refs, list) or any(not isinstance(x, str) or not x.strip() for x in refs):
            raise ValueError(f"{key} 必须为引用 ID 列表；当前状态待核验。")
    result = {key: data[key] for key in (*TEXT_FIELDS, *REF_FIELDS, "allowDownstream")}
    for key in ("updatedAt", "reason", "owner", "requiredInput", "clearanceCondition", "unresolvedRisks"):
        result[key] = data.get(key)
    result["source"] = str(source)
    result["stateChanged"] = False
    result["notice"] = "仅展示已落盘快照；不表示正在运行，不验证证据新鲜度或授予执行/发布权限。"
    return result


def render(data: dict) -> str:
    labels = (
        ("projectId", "项目"), ("workflowId", "流程"), ("executionId", "执行记录"),
        ("lifecycle", "生命周期"), ("state", "正式状态"), ("currentSkill", "当前 Skill"),
        ("gate", "已记录 Gate"), ("allowDownstream", "已记录允许下游"),
        ("updatedAt", "快照更新时间"), ("revision", "版本"),
        ("reason", "原因"), ("owner", "责任方"), ("requiredInput", "待补输入/决定"),
        ("clearanceCondition", "解除条件"), ("nextAction", "下一动作"),
        ("artifactRefs", "产物引用"), ("evidenceRefs", "证据引用"),
        ("decisionRefs", "决策引用"), ("unresolvedRisks", "未决风险"),
    )
    lines = ["流程状态（只读快照）", f"来源：{data['source']}"]
    for key, label in labels:
        value = data.get(key)
        if value is None:
            text = "未记录"
        elif isinstance(value, (dict, list, bool)):
            text = json.dumps(value, ensure_ascii=False, default=str)
        else:
            text = str(value)
        lines.append(f"{label}：{text}")
    lines.append(data["notice"])
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        data = snapshot(args.project_root)
    except (ValueError, OSError) as exc:
        print(f"状态不可确定：{exc}", file=sys.stderr)
        return 2
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str) if args.as_json else render(data))
    return 0


if __name__ == "__main__":
    # Deterministic UTF-8 for Chinese output, including redirected Windows pipes.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
