"""Git-track checks.

The run log records what a node declared; git records what actually landed. They diverge
in exactly the way that matters: work can exist in the working tree with no node-end and no
commit (observed in this repo — three days of finished edits sat uncommitted), and a node
can be closed while its files were never committed. Neither is visible from the other side.
"""
from __future__ import annotations
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise ValueError(f"git {' '.join(args)} failed: {result.stderr.strip()[:200]}")
    return result.stdout


def is_repo(root: Path) -> bool:
    try:
        _git(root, "rev-parse", "--is-inside-work-tree")
        return True
    except ValueError:
        return False


def dirty_entries(root: Path) -> list:
    """Uncommitted paths with their on-disk age, oldest first — the lost-work window."""
    raw = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    entries = []
    now = datetime.now(timezone.utc)
    for line in raw.splitlines():
        if not line.strip():
            continue
        state, relative = line[:2].strip() or "?", line[3:].strip()
        target = root / relative.replace("\\", "/")
        try:
            modified = datetime.fromtimestamp(target.stat().st_mtime, tz=timezone.utc)
        except OSError:
            continue  # deleted or renamed mid-flight: status alone is enough to flag it
        entries.append({"state": state, "path": relative,
                        "ageHours": round((now - modified).total_seconds() / 3600, 1)})
    return sorted(entries, key=lambda item: item["ageHours"], reverse=True)


def commit_window(root: Path, since: str, until: str | None = None) -> dict:
    """Commits inside a node's time window: how much actually landed, and where to roll back.

    `until` is optional on purpose: `git log --until=2100-01-01` silently returns nothing on
    this platform, so an open-ended window must omit the bound rather than use a far-future
    sentinel that looks correct and reports zero landed work.
    """
    arguments = ["log", f"--since={since}", "--format=%H%x09%ad%x09%s", "--date=iso-strict", "--numstat"]
    if until:
        arguments.insert(2, f"--until={until}")
    log = _git(root, *arguments)
    commits, current = [], None
    for line in log.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and len(parts[0]) == 40:
            current = {"sha": parts[0][:12], "at": parts[1], "subject": parts[2], "files": 0, "added": 0, "deleted": 0}
            commits.append(current)
        elif current is not None and line.strip():
            fields = line.split("\t")
            if len(fields) >= 3:
                current["files"] += 1
                if fields[0] != "-":
                    current["added"] += int(fields[0] or 0)
                    current["deleted"] += int(fields[1] or 0)
    return {"count": len(commits), "files": sum(c["files"] for c in commits),
            "added": sum(c["added"] for c in commits), "commits": commits}


def find_gaps(root: Path, unclosed: dict, max_age_hours: float = 4.0) -> list:
    """Declared-but-unclosed nodes, aged uncommitted work, and unpushed delivery, as findings."""
    findings = []
    for (execution, node), started_at in unclosed.items():
        findings.append({"kind": "节点未收口", "node": node, "execution": execution,
                         "detail": f"node-start 于 {started_at} 之后没有 node-end",
                         "evidence": f"{execution}/{node}"})
    if is_repo(root):
        stale = [entry for entry in dirty_entries(root) if entry["ageHours"] >= max_age_hours]
        if stale:
            findings.append({"kind": "改动未提交", "node": None, "execution": None,
                             "detail": f"{len(stale)} 个文件停留在工作树且最久已 {stale[0]['ageHours']} 小时无提交",
                             "evidence": ", ".join(entry["path"] for entry in stale[:8]),
                             "boundary": "只报事实：是否为半成品由人判断，不自动提交、不自动丢弃"})
        findings.extend(delivery_findings(root))
    return findings


DELIVERY_KEYS = ("rule", "kind", "aheadDetail", "notApplicable", "unreadable", "boundary")


def delivery_policy(root: Path) -> dict | None:
    """交付核对只认**被测仓库自己声明**的 delivery 节；没声明就是不适用。

    刻意不回退到随仓发布的注册表：业务项目常把提交留在本地，那是正常状态，
    拿本仓的交付纪律去判红别人的仓库就是把判据绑错对象。
    """
    import yaml
    path = Path(root) / "governance/obs-registry.yaml"
    if not path.is_file():
        return None
    try:
        section = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("delivery")
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"交付判据读不动: {path}: {exc}") from exc
    if section is None:
        return None
    if not isinstance(section, dict):
        raise ValueError(f"{path} 的 delivery 不是表 ⇒ 不猜交付判据长什么样")
    missing = [key for key in DELIVERY_KEYS if not str(section.get(key) or "").strip()]
    if missing:
        raise ValueError(f"delivery 缺必需判据键 {missing} ⇒ 拒绝用默认文案出交付结论")
    return section


def delivery_status(root: Path, pol: dict) -> dict:
    """本地是否领先上游；无上游＝不适用（显式），读不动＝未核（也不当 0）。"""
    try:
        upstream = _git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}").strip()
    except ValueError:
        return {"applicable": False, "count": None, "upstream": None, "reason": pol["notApplicable"]}
    try:
        count = int(_git(root, "rev-list", "--count", "@{u}..HEAD").strip() or "0")
    except (ValueError, TypeError):
        return {"applicable": True, "count": None, "upstream": upstream, "reason": pol["unreadable"]}
    return {"applicable": True, "count": count, "upstream": upstream, "reason": ""}


def delivery_findings(root: Path) -> list:
    pol = delivery_policy(root)
    if pol is None:
        return []
    status = delivery_status(root, pol)
    if not status["applicable"]:
        return []                      # 不适用：显式跳过，不当作「已核对通过」
    if status["count"] is None:
        detail = status["reason"]
    elif status["count"] > 0:
        detail = pol["aheadDetail"].format(count=status["count"], upstream=status["upstream"])
    else:
        return []
    return [{"kind": pol["kind"], "node": None, "execution": None, "cardKind": "unpushed",
             "detail": detail, "evidence": str(status["upstream"] or "N/A"),
             "boundary": pol["boundary"], "rule": pol["rule"]}]
