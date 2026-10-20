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
EVAL_REPORT = ".spec/obs/eval-report.json"
# 行为层追加台账（append-only 真相源，入库）：eval-report.json 每次评测被整份覆写，
# 历史实跑的成本与 pass/fail 只有台账保得住。D5 优先读台账，台账拿不到才回退报告。
BEHAVIOUR_LEDGER = ".spec/obs/behaviour-runs.jsonl"
# 台账里"发生了实跑"的状态集：blocked/error 一律不算通过；blocked 连实跑都不算，
# 但它必须出现在未实跑计数里——"这次没跑"同样是需要留痕的事实。
RUN_STATUSES = {"passed", "failed", "error"}
# 本仓规矩：单条通过只能说"该条通过"。低于此实跑数时读数照给，但必须自带"样本不足"标注。
MIN_SAMPLE = 3
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


def _behaviour_records(report: list) -> list:
    """Pick behaviour-layer results out of an eval report, and justify the identification test.

    `run.py` stamps every structure-layer verdict with `outcome` (green/red); behaviour records
    are the ones that carry no outcome. Keying on `outcome` rather than on the engine-only
    fields (`tokens`/`evidence`) is the one-sided error we want: a structure record that errored
    before setting an outcome gets counted as an unmeasured behaviour entry, which can only push
    coverage down. The opposite test would drop a missing behaviour run out of the denominator
    altogether and show full coverage for a suite that never ran.
    """
    records = []
    for entry in report if isinstance(report, list) else []:
        skill = str(entry.get("skill") or "?") if isinstance(entry, dict) else "?"
        for item in (entry.get("results") or []) if isinstance(entry, dict) else []:
            if isinstance(item, dict) and "outcome" not in item:
                records.append((skill, item))
    return records


def _cost_readout(records: list) -> str:
    """Engine token cost, or N/A.

    Two precedents set this rule: the editor host was measured to report token 0 for every
    event, and `run.py` already escalates a missing meter to `error`. So only a positive token
    count is a measurement — 0 and absent both mean "not metered", and bytes may never stand in.
    """
    metered = []
    for _skill, item in records:
        tokens = item.get("tokens")
        if isinstance(tokens, (int, float)) and not isinstance(tokens, bool) and tokens > 0:
            metered.append(int(tokens))
    if not metered:
        return "成本 N/A (报告未记录 token)"
    return (f"成本 token 合计 {sum(metered):,}（{len(metered)}/{len(records)} 条有计量，"
            f"均值 {sum(metered) // len(metered):,}）")


def d5_behaviour(root: Path) -> dict:
    """Behaviour layer as a *countable coverage* reading, never as a manufactured quality score.

    Data source priority: the append-only ledger `.spec/obs/behaviour-runs.jsonl` (committed
    truth; a real run's verdict and cost survive forever), falling back to the derived
    `eval-report.json` only when no ledger exists yet — and the detail always names which
    source produced the reading, because "the report says X" and "the ledger says X" are not
    the same claim (the report is overwritten wholesale on every run; that is the very data
    loss this ledger was built to end).
    Repo discipline: one passing case only proves that case passed. So this dimension reports
    how many behaviour records actually ran and how many of them passed, and keeps blocked
    (unauthorized) and error (no cost metering / predicate could not hold) entries out of the
    numerator — never a pass. Nothing here may convert "never measured" into "no problem":
    an all-unmeasured ledger is N/A, and the reason distinguishes a missing ledger from a
    ledger whose behaviour layer never ran.
    """
    if (root / BEHAVIOUR_LEDGER).is_file():
        return _d5_from_ledger(root)
    return _d5_from_report(root)


def _ledger_rows(root: Path):
    """Parse the JSONL ledger; returns (rows, error-detail) — a broken truth file is never
    silently demoted to the fallback report, because that would let ledger corruption
    masquerade as "no data" instead of "fix me". """
    path = root / BEHAVIOUR_LEDGER
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return None, f"N/A (追加台账 {BEHAVIOUR_LEDGER} 读不动：{type(exc).__name__}；不回退 eval-report，先修台账)"
    rows = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            return None, (f"N/A (追加台账 {BEHAVIOUR_LEDGER} 第 {number} 行不是合法 JSON；追加式真相坏了一行也必须"
                          f"点名，不回退 eval-report、不静默丢弃)")
        if not isinstance(row, dict):
            return None, f"N/A (追加台账 {BEHAVIOUR_LEDGER} 第 {number} 行不是记录对象；台账口径已变)"
        rows.append(row)
    return rows, None


def _d5_from_ledger(root: Path) -> dict:
    ledger_source = f"｜数据源=追加台账 {BEHAVIOUR_LEDGER}"
    rows, error = _ledger_rows(root)
    if error:
        return {"value": None, "detail": error}
    if not rows:
        return {"value": None,
                "detail": f"N/A (追加台账存在但还没有任何行为层判定被记入：评测未跑或台账刚建档)" + ledger_source}
    runs = [row for row in rows if str(row.get("status")) in RUN_STATUSES]
    passed = [row for row in runs if str(row.get("status")) == "passed"]
    unrun = {}
    for row in rows:
        if str(row.get("status")) not in RUN_STATUSES:
            unrun[str(row.get("status"))] = unrun.get(str(row.get("status")), 0) + 1
    failures = [f"{row.get('skill', '?')}/{row.get('caseId', '?')}: {row.get('status')} {row.get('reason', '')}"
                for row in rows if str(row.get("status")) != "passed"]
    if not runs:
        breakdown = "／".join(f"{status} {count}" for status, count in sorted(unrun.items()))
        return {"value": None,
                "detail": f"N/A (行为层 {len(rows)} 条全部未实跑：{breakdown}；"
                          f"blocked=未授权、error=成本或判据无法成立，两者一律不算通过)" + ledger_source,
                "failures": failures}
    note = ("" if len(runs) >= MIN_SAMPLE
            else f"（样本 n={len(runs)} < {MIN_SAMPLE}：单条通过只说明该条通过，不得当质量结论）")
    return {"value": 100.0 * len(passed) / len(runs),
            "detail": f"行为层 {len(passed)}/{len(runs)} 条实跑且通过"
                      f"（实跑 {len(runs)}：过 {len(passed)}｜败/错 {len(runs) - len(passed)}；"
                      f"未实跑记录 {sum(unrun.values())}）｜读数为覆盖率、非质量分{note}｜"
                      f"{_cost_readout([('', row) for row in runs])}｜"
                      f"覆盖率分母＝实跑过的条数（台账是事件史：blocked 留痕条数随未授权重跑增长，"
                      f"放进分母会让同一个『没跑』被计很多次而没有任何新事实）" + ledger_source,
            "failures": failures}


def _d5_from_report(root: Path) -> dict:
    fallback_source = f"｜数据源=eval-report.json（回退：追加台账 {BEHAVIOUR_LEDGER} 不存在）"
    path = root / EVAL_REPORT
    if not path.is_file():
        return {"value": None, "detail": f"N/A ({EVAL_REPORT} 不存在，评测未跑)" + fallback_source}
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        # a corrupt derived file is not "unmeasured by choice": name the failure so it cannot
        # be mistaken for a clean N/A next run
        return {"value": None, "detail": f"N/A ({EVAL_REPORT} 读不动：{type(exc).__name__})" + fallback_source}
    if not isinstance(report, list):
        # 口径变了就要说出来，不能把"读不懂"降级成"行为层没跑"
        return {"value": None, "detail": f"N/A ({EVAL_REPORT} 顶层不是评测集列表，run.py 落盘口径已变)" + fallback_source}
    records = _behaviour_records(report)
    if not records:
        return {"value": None, "detail": f"N/A (报告里没有任何行为层结果，只有结构层：行为层未跑)" + fallback_source}
    rows = [(skill, str(item.get("id")), str(item.get("status") or "?"), item) for skill, item in records]
    ran = [row for row in rows if row[2] in {"passed", "failed"}]
    if not ran:
        unrun = {}
        for _skill, _cid, status, _item in rows:
            unrun[status] = unrun.get(status, 0) + 1
        breakdown = "／".join(f"{status} {count}" for status, count in sorted(unrun.items()))
        return {"value": None,
                "detail": f"N/A (行为层 {len(rows)} 条全部未实跑：{breakdown}；"
                          f"blocked=未授权、error=成本或判据无法成立，两者一律不算通过)" + fallback_source,
                "failures": [f"{skill}/{cid}: {status} {item.get('reason', '')}"
                             for skill, cid, status, item in rows]}
    passed = [row for row in rows if row[2] == "passed"]
    failures = [f"{skill}/{cid}: {status} {item.get('reason', '')}"
                for skill, cid, status, item in rows if status != "passed"]
    note = ("" if len(ran) >= MIN_SAMPLE
            else f"（样本 n={len(ran)} < {MIN_SAMPLE}：单条通过只说明该条通过，不得当质量结论）")
    return {"value": 100.0 * len(passed) / len(rows),
            "detail": f"行为层 {len(passed)}/{len(rows)} 条实跑且通过"
                      f"（实跑 {len(ran)}：过 {len(passed)}｜败 {len(ran) - len(passed)}；"
                      f"未实跑 {len(rows) - len(ran)}）｜读数为覆盖率、非质量分{note}｜{_cost_readout(records)}"
                      + fallback_source,
            "failures": failures}


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
            "D4": d4_rework(root, summary), "D5": d5_behaviour(root),
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
