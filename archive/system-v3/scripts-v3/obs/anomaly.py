"""Findings to problem cards, following the one-event-one-source rule.

Cards carry machine pointers (execution id, log offset, artifact digest) instead of a
narrative recollection, so the next session can re-derive the same facts rather than trust
a summary. Re-running on the same evidence updates the existing card instead of stacking a
duplicate — the index is a mirror, the detail file is the source.
"""
from __future__ import annotations
import hashlib, re
from datetime import datetime
from pathlib import Path

INDEX = ".spec/问题日志.md"
DETAIL_DIR = ".spec/issues"
FIELDS = ("问题 ID", "发现时间", "当前状态", "任务/Skill/步骤", "期望与实际", "证据",
          "影响与严重度", "责任方/下一动作/修复判据", "处理与复核", "反哺")


def finding_id(finding: dict) -> str:
    seed = f"{finding.get('kind')}|{finding.get('evidence')}"
    return "OBS-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:10].upper()


def _fingerprint(text: str) -> str:
    return text.replace("\\", "/").strip()


def render(finding: dict, project: Path) -> str:
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    lines = [f"# {finding['kind']}：{finding['detail'][:60]}", ""]
    lines.append(f"- 问题 ID：{finding_id(finding)} ｜ 发现时间：{now} ｜ 当前状态：待分诊")
    lines.append(f"- 任务/Skill/步骤：execution `{finding.get('execution') or '—'}` / node `{finding.get('node') or '—'}`")
    lines.append(f"- 期望与实际：期望该节点有收口记录或改动已落提交；实际为「{finding['detail']}」")
    lines.append(f"- 证据：{finding.get('evidence')}（可由 tsr audit / git status 复算，不依赖叙述）")
    lines.append("- 影响与严重度：待确认（未判定是否半成品，不擅自升级为缺陷）")
    lines.append("- 责任方/下一动作/修复判据：待分诊；动作=人确认为半成品还是遗漏收口，判据=工作树干净且节点有 node-end")
    lines.append("- 处理与复核：未处理")
    lines.append("- 反哺：待分析（若同类反复出现，考虑接进 gate 判据而非只做事后巡检）")
    return "\n".join(lines) + "\n"


def index_row(finding: dict, project: Path) -> str:
    ident = finding_id(finding)
    date = datetime.now().astimezone().date().isoformat()
    detail = f"{DETAIL_DIR}/{ident}.md"
    return (f"| {date} | 自动巡检 · {finding['kind']} | `{detail}` | — | 待分诊 "
            f"| {finding['detail'][:80]}（证据：{finding.get('evidence', '')[:60]}） |")


def upsert(project: Path, findings: list) -> dict:
    """Write cards for new findings, update status lines for known ones; never duplicate."""
    detail_dir = project / DETAIL_DIR
    detail_dir.mkdir(parents=True, exist_ok=True)
    index = project / INDEX
    existing = index.read_text(encoding="utf-8") if index.is_file() else ""
    created, unchanged = [], []
    header = "" if existing.strip() else ("# 问题日志\n\n"
                "| 日期 | 来源 | 详情 | 轮次 | 状态 | 事实与反哺 |\n"
                "|---|---|---|---|---|---|\n")
    for finding in findings:
        ident = finding_id(finding)
        if re.search(rf"\b{ident}\b", existing):
            unchanged.append(ident)
            continue
        (detail_dir / f"{ident}.md").write_text(render(finding, project), encoding="utf-8")
        existing = (existing.rstrip() + "\n" if existing.strip() else header.rstrip() + "\n") + index_row(finding, project) + "\n"
        created.append(ident)
    if created:
        index.write_text(existing, encoding="utf-8")
    return {"created": created, "unchanged": unchanged, "index": INDEX}
