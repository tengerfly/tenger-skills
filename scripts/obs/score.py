"""Weighted scoring over what can be measured mechanically.

A dimension with no evidence reports N/A and its weight is removed from the denominator,
so a total can never silently treat "unmeasured" as "clean". Red lines are not weighted:
they zero the score, because a compliant-looking-but-drifted baseline must not be able to
earn its way past a broken gate.
"""
from __future__ import annotations
import json, re, fnmatch
from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parents[2]
SCORING = ROOT_DIR / "governance/scoring.yaml"
REGISTRY = ROOT_DIR / "governance/artifact-registry.yaml"
BASELINE = ".spec/obs/score-baseline.json"
REDLINE_PATTERNS = (
    ("上游关闸却放行", "upstream is closed"),
    ("摘要与磁盘不一致", "contentDigest mismatch"),
    ("摘要与磁盘不一致", "subjectDigests mismatch"),
    ("批准后正文被改", "edited after node-end"),
    ("节点名未注册", "not registered"),
)


def _yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def weights() -> dict:
    dims = _yaml(SCORING).get("dimensions") or {}
    return {key: int(spec["weight"]) for key, spec in dims.items()}


def section_rules() -> dict:
    """Path-scoped section requirements; a type with no verified rule is simply not judged."""
    registry = _yaml(REGISTRY)
    rules = {}
    for item in registry.get("artifacts") or []:
        declared = item.get("documentSections")
        if not declared:
            continue
        normalised = []
        for entry in declared:
            if isinstance(entry, dict) and entry.get("sections"):
                normalised.append({"match": str(entry["match"]), "sections": [str(s) for s in entry["sections"]]})
            elif isinstance(entry, str):
                normalised.append({"match": "*", "sections": [entry]})
        if normalised:
            rules[str(item.get("type"))] = normalised
    return rules


def _missing_sections(text: str, keywords: list) -> list:
    """Match keywords inside heading lines only: real docs write "1. 元数据与变更记录", so exact
    template titles would penalise compliant work."""
    headings = "\n".join(line for line in text.splitlines() if line.lstrip().startswith("#"))
    return [keyword for keyword in keywords if keyword not in headings]


def _sections_for(rules: list, relative: str) -> list:
    sections = []
    for rule in rules:
        pattern = rule["match"]
        if fnmatch.fnmatch(relative, pattern) or fnmatch.fnmatch("/" + relative, pattern):
            sections += rule["sections"]
    return sections


def _ledger(root: Path):
    """Read the manifest ledger when a project has one; scoring must degrade, not crash."""
    import validate_core as core
    if not (root / ".spec/manifest.yaml").is_file():
        return {}, []
    try:
        _, by_id, errors = core.artifact_context(root)
        return by_id, errors
    except ValueError:
        return {}, []


def d1_contract(root: Path) -> dict:
    import validate_core as core
    by_id, _ = _ledger(root)
    if not by_id:
        return {"value": None, "detail": "N/A (无 manifest.yaml，无法判契约)"}
    specs = section_rules()
    judged = passed = skipped = 0
    failures = []
    for aid, item in by_id.items():
        rules = specs.get(str(item.get("type")))
        relative = str(item.get("path") or "").replace("\\", "/")
        required = _sections_for(rules or [], relative)
        if not required or item.get("status") not in {"APPROVED", "REVIEW"}:
            skipped += 1
            continue
        target, path_error = core.project_path(root, item.get("path"))
        if path_error or not target or not target.is_file():
            failures.append(f"{aid}: 正文不可读，无法判章节")
            judged += 1
            continue
        judged += 1
        missing = _missing_sections(target.read_text(encoding="utf-8", errors="replace"), required)
        if missing:
            failures.append(f"{aid}: 缺章节关键词 {missing}")
        else:
            passed += 1
    coverage = judged / max(1, judged + skipped)
    return {"value": 100.0 * passed / judged if judged else None, "coverage": coverage,
            "detail": f"{passed}/{judged} 产物章节齐全（判据覆盖 {coverage:.1%}，其余类型未声明 documentSections ⇒ 不判）",
            "failures": failures}


def d2_traceability(root: Path) -> dict:
    import validate_core as core
    by_id, _ = _ledger(root)
    path = root / ".spec/traceability.yaml"
    if not path.is_file():
        return {"value": None, "detail": "N/A (无 traceability.yaml)"}
    record = _yaml(path)
    links = core.items(record.get("links"))
    if not links:
        # the file exists but carries no consumable links: that is a broken chain, not an
        # unmeasured dimension, so it must cost points rather than disappear as N/A
        return {"value": 0.0, "detail": "traceability.yaml 存在但读不到 links 列表（链路不可消费）",
                "failures": ["traceability.links 缺失或为空，检查是否被包在多余的顶层键下"]}
    resolvable = 0
    broken = []
    for link in links:
        endpoints = [link.get("from"), link.get("to")] + list(core.items(link.get("evidenceRefs")))
        bad = [str(x) for x in endpoints
               if x and str(x) not in by_id and not core.EXTERNAL_REF.match(str(x))]
        if bad:
            broken.append(f"{link.get('linkId')}: 断链 {bad}")
        else:
            resolvable += 1
    return {"value": 100.0 * resolvable / len(links),
            "detail": f"{resolvable}/{len(links)} 条链路引用可解析", "failures": broken}


def d3_detection(root: Path) -> dict:
    path = root / ".spec/obs/detection.json"
    if not path.is_file():
        return {"value": None, "detail": "N/A (尚未跑 selfcheck 注入反证)"}
    record = json.loads(path.read_text(encoding="utf-8"))
    fired = int(record.get("fired", 0))
    total = int(record.get("total", 0))
    return {"value": 100.0 * fired / total if total else None,
            "detail": f"注入反证 {fired}/{total} 条被检出", "failures": record.get("missed", [])}


def d4_rework(root: Path, summary: dict) -> dict:
    rate = summary.get("rework_rate")
    if rate is None:
        return {"value": None, "detail": "N/A (run-log 里没有评审交接)"}
    return {"value": 100.0 * (1 - rate),
            "detail": f"评审交接 {summary['review_rounds']} 次，返工率 {rate:.0%}"}


def d6_cost(root: Path, summary: dict) -> dict:
    baseline_path = root / BASELINE
    if not baseline_path.is_file():
        return {"value": None, "detail": "N/A (无字节基线，无法判膨胀)"}
    baseline = json.loads(baseline_path.read_text(encoding="utf-8")).get("artifactBytes")
    if not baseline:
        return {"value": None, "detail": "N/A (基线未记录字节)"}
    growth = summary["artifact_bytes"] / baseline - 1
    if growth <= 0:
        return {"value": 100.0, "detail": f"产物字节相对基线 {growth:+.0%}"}
    return {"value": max(0.0, 100.0 - min(100.0, growth * 200)),
            "detail": f"产物字节相对基线膨胀 {growth:+.0%}（每 +1% 扣 2 分）",
            "failures": [f"字节膨胀 {growth:+.0%}"]}


def red_lines(root: Path, problems: list) -> list:
    hits = []
    for label, pattern in REDLINE_PATTERNS:
        matched = [p for p in problems if pattern in p]
        if matched:
            hits.append(f"{label}（{len(matched)} 条，例：{matched[0]}）")
    return hits


def score_project(root: Path) -> dict:
    from obs import metrics, schema
    import tsr
    import validate_core as core
    events = schema.read_events(root)
    summary = metrics.summarize(events) if events else {"rework_rate": None, "review_rounds": 0,
                                                        "artifact_bytes": 0, "nodes": {}}
    problems = []
    if (root / ".spec/manifest.yaml").is_file():
        problems.extend(core.check_artifact(root))
    if events:
        problems.extend(tsr.verify(root))
    dims = {"D1": d1_contract(root), "D2": d2_traceability(root), "D3": d3_detection(root),
            "D4": d4_rework(root, summary), "D5": {"value": None, "detail": "N/A (B 类评测未接)"},
            "D6": d6_cost(root, summary)}
    table = weights()
    scored = {key: dim["value"] for key, dim in dims.items() if dim.get("value") is not None}
    hits = red_lines(root, problems)
    used_weight = sum(table[key] for key in scored)
    # a red line is scored as 0, not omitted: "0" is comparable across runs, None is not
    total = 0.0 if hits else (sum(table[key] * scored[key] for key in scored) / used_weight if used_weight else None)
    return {"total": total, "dimensions": dims, "scored": sorted(scored),
            "weightUsed": used_weight, "redLines": hits, "problems": problems,
            "anchor": {"scoringVersion": 1, "skillRevision": _revision(root)}}


def _revision(root: Path) -> str:
    head = root / ".git" / "HEAD"
    try:
        git_dir = root / ".git"
        ref = head.read_text(encoding="utf-8").strip()
        if ref.startswith("ref: "):
            return (git_dir / ref[5:]).read_text(encoding="utf-8").strip()[:12]
        return ref[:12]
    except OSError:
        return "unknown"


def render(result: dict) -> str:
    table = weights()
    lines = ["# 评测打分", ""]
    total = result["total"]
    lines.append(f"- **总分：{'红线命中，判 0' if result['redLines'] else ('N/A (无任何可测维度)' if total is None else format(total, '.1f'))}**")
    lines.append(f"- 有效维度权重 {result['weightUsed']}/100；N/A 维度的权重已从分母剔除")
    lines.append(f"- 锚：scoring v{result['anchor']['scoringVersion']} @ {result['anchor']['skillRevision']}")
    if result["redLines"]:
        lines += ["", "## ⛔ 红线（不可被高分抵消）", *[f"- {hit}" for hit in result["redLines"]]]
    lines += ["", "| 维度 | 权重 | 得分 | 依据 |", "|---|---|---|---|"]
    for key in sorted(result["dimensions"]):
        dim = result["dimensions"][key]
        value = "N/A" if dim.get("value") is None else format(dim["value"], ".1f")
        lines.append(f"| {key} | {table[key]} | {value} | {dim.get('detail', '')} |")
    misses = [f"- {key}: {failure}" for key, dim in result["dimensions"].items()
              for failure in dim.get("failures", [])[:5]]
    if misses:
        lines += ["", "## 扣分点（每维度最多列 5 条）", *misses]
    lines += ["", "> 总分只用于看趋势。逐维 delta 必须与总分同看：一维崩一维涨会伪装成持平。"]
    return "\n".join(lines) + "\n"
