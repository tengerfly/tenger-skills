"""检测面 → 候选问题卡：plan v2 §5 闭环中间段的第一格（`a98db84` 只做了开头一小截）。

四件事全部机械化，不靠 AI 回忆：

1. 输入 = **已有检测面**的检出项（`tsr verify` / `tsr report` 看板派生 / `obs.gitlog` 巡检 /
   `eval.relay` L2 回流执法）。本模块不新增判据，只把「哪个量具在说什么对不上」连同指针抄成卡。
2. 每张卡机械带上：触发异常的 `executionId`、ts 窗口（起止）、涉事产物 `path + sha256`
   （台账记录值与磁盘现值并列）、命中的判据文本原文。取不到的维度一律 `N/A` 并写明为什么——
   不拿文件 mtime 冒充节点窗口、不拿相近事件冒替 executionId、不拿巡检时刻冒充收口。
3. 卡只落派生区（`governance/obs-registry.yaml` 的 `candidates.outputDir`），**绝不写 `issue/`**：
   那里是历史证据、只读，而且自动建档等于替人判定问题成立。**等级一律留空**（P0/P1 属人的判定），
   每张卡显式标注「候选·未经确认」。落点由 `forbidWriteInto` 机械兜底，不是口头承诺。
4. 同 `kind + evidence` 只出一张卡（种子公式与 `obs/anomaly.py:finding_id` 一致），重跑不叠卡；
   不再命中的旧卡只报不删——候选卡是镜像，不是真相。

判据文案、落点、N/A 原因全部在 `governance/obs-registry.yaml` 的 `candidates` 节，代码只执行。
"""
from __future__ import annotations
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import re
import yaml

from obs import schema

ROOT_DIR = Path(__file__).resolve().parents[2]
SHIPPED_REGISTRY = ROOT_DIR / "governance/obs-registry.yaml"
# verify 的行格式是 `<run.jsonl>#<seq>: <判据文本>`，seq 由 tsr 落盘时赋值 ⇒ 指针不是猜的
REF = re.compile(r"^(?P<log>\S*run\.jsonl)#(?P<seq>\d+): (?P<msg>.*)$", re.S)
UNREGISTERED = "is not registered in governance/obs-registry.yaml"
NO_LOG = "no run-log events"


def registry_path(root: Path | None = None) -> Path:
    """项目自带的 governance 优先；没有就用本仓发布的判据（换宿主/换项目都不断链）。"""
    if root is not None:
        local = Path(root) / "governance/obs-registry.yaml"
        if local.is_file():
            return local
    return SHIPPED_REGISTRY


def policy(root: Path | None = None) -> dict:
    path = registry_path(root)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"候选判据读不动: {path}: {exc}") from exc
    section = data.get("candidates")
    if not isinstance(section, dict) or not section.get("outputDir"):
        raise ValueError(f"{path.as_posix()} 未声明 candidates.outputDir ⇒ 判据缺失，不猜落点")
    missing = [key for key in ("label", "gradeValue", "naReasons", "surfaces", "kinds")
               if not section.get(key)]
    if missing:
        raise ValueError(f"{path.as_posix()} 的 candidates 节缺必需键 {missing} ⇒ 拒绝用默认值冒充实装")
    return section


def card_id(pol: dict, kind: str, evidence: str) -> str:
    """种子公式与 obs/anomaly.py:finding_id 同构（kind|evidence），两处写手不会各造一套 id。"""
    seed = f"{kind}|{evidence}"
    return str(pol.get("idPrefix", "CAND-")) + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:10].upper()


def _disk(root: Path, relative: str) -> dict:
    target = root / str(relative).replace("\\", "/")
    if not target.is_file():
        return {"sha256": None, "bytes": None}
    data = target.read_bytes()
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def _mtime(root: Path, relative: str):
    """文件系统真实 mtime（不是 ageHours 反推的估计值）。取不到就 None，不编。"""
    try:
        stamp = (root / str(relative).replace("\\", "/")).stat().st_mtime
    except OSError:
        return None
    return datetime.fromtimestamp(stamp, tz=timezone.utc).astimezone().isoformat(timespec="seconds")


def _by_seq(events: list) -> dict:
    return {event.get("seq", index): event for index, event in enumerate(events, 1)}


def node_window(events: list, execution, node) -> tuple:
    """同 executionId + node 的 node-start → node-end ts；缺哪端就是 None，由调用方记 N/A。"""
    start = end = None
    for event in events:
        if event.get("executionId") != execution or event.get("node") != node:
            continue
        if event.get("event") == "node-start" and start is None:
            start = event.get("ts")
        if event.get("event") == "node-end":
            end = event.get("ts")
    return start, end


def unclosed_pairs(events: list) -> dict:
    """{(executionId, node): node-start ts} —— 声明了却没有 node-end 收口的节点。

    `tsr audit` 与本模块共用这一个口径：同 kind+evidence ⇒ 同一事实只出一张候选卡。
    """
    opened, closed = {}, set()
    for event in events:
        key = (event.get("executionId"), event.get("node"))
        if event.get("event") == "node-start":
            opened.setdefault(key, event.get("ts"))
        elif event.get("event") == "node-end":
            closed.add(key)
    return {key: ts for key, ts in opened.items() if key not in closed}


def latest_binding(events: list, relative: str):
    """该路径最新一次 node-end 绑定（复用 tsr.artifact_bindings 的口径，不另起一套）。"""
    import tsr
    rows = tsr.artifact_bindings(events).get(str(relative).replace("\\", "/")) or []
    if not rows:
        return None
    _, where, artifact = rows[-1]
    return {"where": str(where), "seq": int(str(where).rpartition("#")[2]), "artifact": artifact}


def _path_from(msg: str):
    """判据文本末尾带的涉事产物路径（check_bindings 的写法）；拿不到就 None，不乱猜别的字段。"""
    _, sep, tail = msg.rpartition(": ")
    if not sep:
        return None
    candidate = tail.split("（")[0].strip().strip("[]'\" ")
    return candidate if ("/" in candidate or "\\" in candidate) else None


def _new_card(pol: dict, *, kind: str, evidence: str, surface: str, judge: str,
              execution=None, node=None, start=None, end=None, window_note=None,
              run_log_refs=None, artifacts=None, na=None, boundary=None) -> dict:
    return {
        "id": card_id(pol, kind, evidence), "kind": kind, "evidence": evidence,
        "surfaces": [surface], "judges": [judge],
        "executionId": execution, "node": node,
        "window": {"start": start, "end": end, "note": window_note},
        "runLogRefs": list(run_log_refs or []), "artifacts": list(artifacts or []),
        "na": list(na or []), "boundary": boundary or "",
        # 归因由 obs.attribution 在 collect() 末尾统一填入；没有它时渲染段自己会报「没跑」
        "attribution": None,
    }


def _event_artifacts(pol: dict, root: Path, event: dict) -> list:
    rows = []
    for artifact in event.get("artifacts") or []:
        relative = str(artifact.get("path", "")).replace("\\", "/")
        fresh = _disk(root, relative)
        rows.append({"path": relative, "recorded": artifact.get("sha256"), "disk": fresh["sha256"],
                     "bytes": fresh["bytes"], "ref": "本事件绑定",
                     "note": "" if fresh["sha256"] else pol["naReasons"]["fileGone"]})
    return rows


def _subject_artifact(pol: dict, root: Path, events: list, relative: str) -> dict:
    """涉事产物：台账记录值取该路径最新一次绑定（没有就 N/A 并说明），磁盘现值当场重算。"""
    fresh = _disk(root, relative)
    binding = latest_binding(events, relative)
    recorded = binding["artifact"].get("sha256") if binding else None
    notes = [] if fresh["sha256"] else [pol["naReasons"]["fileGone"]]
    if recorded is None:
        notes.append(pol["naReasons"]["noBinding"])
    return {"path": str(relative).replace("\\", "/"), "recorded": recorded, "disk": fresh["sha256"],
            "bytes": fresh["bytes"], "ref": binding["where"] if binding else "N/A（run-log 未绑定此路径）",
            "note": "；".join(notes)}


def _na_fields(pol: dict, card: dict) -> list:
    """把取不到的维度补齐成显式 N/A，绝不留白（留白会被读成「查过且没问题」）。

    某个维度已经有具体原因（哪怕是 `executionId / ts 窗口` 这种合并写法）就不再补泛化文案：
    同一维度两三条 N/A 只会稀释信息、把真正的原因埋掉。
    """
    na = list(card["na"])

    def covered(*tokens: str) -> bool:
        return any(token in str(item) for item in na for token in tokens)

    window = card["window"] or {}
    if not card["executionId"] and not covered("executionId"):
        na.append("executionId：N/A —— 该检出面没有可指向的执行事件（不拿相近事件冒替）")
    if not window.get("start") and not covered("ts 窗口（起）", "ts 窗口："):
        na.append("ts 窗口（起）：N/A —— run-log 里没有该执行的 node-start")
    if not window.get("end") and not covered("ts 窗口（止）", "ts 窗口："):
        na.append(f"ts 窗口（止）：N/A —— {pol['naReasons']['noCloseTs']}")
    if not card["artifacts"] and not covered("涉事产物"):
        na.append(f"涉事产物 path+sha256：N/A —— {pol['naReasons']['noArtifact']}")
    return na


# ── 检出面①：tsr verify（run-log 契约 + 摘要漂移）───────────────────────────────
def from_verify(pol: dict, root: Path, events: list, errors: list) -> list:
    kinds, na_text = pol["kinds"], pol["naReasons"]
    by_seq = _by_seq(events)
    cards = []
    for line in errors:
        match = REF.match(line)
        msg = match.group("msg") if match else line
        seq = int(match.group("seq")) if match else None
        event = by_seq.get(seq) if seq is not None else None
        refs = [f"{match.group('log')}#{seq}"] if match else []
        if UNREGISTERED in msg:
            kind, evidence = kinds["unregisteredNode"], msg.rpartition(": ")[2]
        elif "artifact vanished" in msg:
            kind, evidence = kinds["artifactGone"], line
        elif "edited after node-end" in msg:
            kind, evidence = kinds["bindingDrift"], line
        elif msg.startswith(NO_LOG):
            kind, evidence, event, seq, refs = kinds["noObservability"], schema.RUN_LOG, None, None, []
        else:
            kind, evidence = kinds["contract"], line
        extra = _path_from(msg)
        if extra:
            artifacts = [_subject_artifact(pol, root, events, extra)]
        elif event is not None:
            artifacts = _event_artifacts(pol, root, event)
        else:
            artifacts = []
        execution = event.get("executionId") if event else None
        node = event.get("node") if event else None
        start = end = None
        window_note = None
        notes = []
        if event is not None:
            start, end = node_window(events, execution, node)
            window_note = pol["windowRule"]
        elif match is not None:
            notes.append(f"executionId / ts 窗口：N/A —— 指针 {seq} 在 run-log 里找不到事件（悬空，如实记）")
        else:
            notes.append(f"executionId / ts 窗口：N/A —— {na_text['noLog']}")
        if seq is None and NO_LOG not in line:
            notes.append("run-log 指针：N/A —— 该检出行不带 seq，无法定位事件")
        cards.append(_new_card(pol, kind=kind, evidence=evidence, surface="verify", judge=line,
                               execution=execution, node=node, start=start, end=end,
                               window_note=window_note, run_log_refs=refs, artifacts=artifacts,
                               na=notes, boundary="verify 只报「字节与台账对不上」，不判谁对谁错"))
    return cards


# ── 检出面②：tsr report 看板派生（未注册节点集合 + 未收口节点）───────────────────
def from_report(pol: dict, root: Path, events: list) -> list:
    if not events:
        return []
    from obs import metrics
    kinds, na_text = pol["kinds"], pol["naReasons"]
    registered = metrics.load_registry()
    source = pol["surfaces"]["report"]["judgeSource"]
    cards = []
    for node in sorted({str(event.get("node")) for event in events
                        if event.get("node") not in registered}):
        events_here = [event for event in events if str(event.get("node")) == node]
        first = events_here[0]
        execution = first.get("executionId")
        start, end = node_window(events, execution, node)
        artifacts = _event_artifacts(pol, root, first)
        cards.append(_new_card(
            pol, kind=kinds["unregisteredNode"], evidence=node, surface="report",
            judge=f"unregistered nodes: ['{node}'] —— 看板判据：节点名未注册即缺陷，不是数据点（{source}）",
            execution=execution, node=node, start=start, end=end, window_note=pol["windowRule"],
            run_log_refs=[f"run.jsonl#{event.get('seq')}" for event in events_here],
            artifacts=artifacts,
            na=[] if artifacts else [f"涉事产物：N/A —— {na_text['noArtifact']}"],
            boundary="注册表里没有这个节点名 ⇒ 逐节点指标被静默打散，先确认名字再动判据"))
    for (execution, node), started_at in sorted(unclosed_pairs(events).items()):
        open_events = [event for event in events
                       if event.get("executionId") == execution and event.get("node") == node]
        artifacts = [artifact for event in open_events for artifact in _event_artifacts(pol, root, event)]
        cards.append(_new_card(
            pol, kind=kinds["unclosedNode"], evidence=f"{execution}/{node}", surface="report",
            judge=f"看板「进行中/未收口」命中 {node}：node-start 于 {started_at} 之后没有 node-end"
                  f"（{source}；metrics.summarize.open_nodes）",
            execution=execution, node=node, start=started_at, end=None,
            window_note="起点=node-start ts（run-log 机器时钟）；终点见 N/A 说明",
            run_log_refs=[f"run.jsonl#{event.get('seq')}" for event in open_events],
            artifacts=artifacts,
            na=[f"ts 窗口（止）：N/A —— {na_text['noCloseTs']}"],
            boundary="未收口不等于失败：可能仍在进行，由人确认是半成品还是漏记收口"))
    return cards


# ── 检出面③：git 轨巡检（run-log 结构性看不见的那两类事故）───────────────────────
def from_gitlog(pol: dict, root: Path, events: list, findings: list) -> list:
    kinds, na_text = pol["kinds"], pol["naReasons"]
    cards = []
    for finding in findings:
        detail = f"[{finding['kind']}] {finding['detail']} ｜ 证据 {finding['evidence']}"
        if finding.get("execution") and finding.get("node"):
            execution, node = finding["execution"], finding["node"]
            related = [event for event in events
                       if event.get("executionId") == execution and event.get("node") == node]
            start = next((event.get("ts") for event in related
                          if event.get("event") == "node-start"), None)
            _, end = node_window(events, execution, node)
            artifacts = [artifact for event in related for artifact in _event_artifacts(pol, root, event)]
            cards.append(_new_card(
                pol, kind=kinds["unclosedNode"], evidence=f"{execution}/{node}", surface="gitlog",
                judge=detail, execution=execution, node=node, start=start, end=end,
                window_note="起点=node-start ts（run-log 机器时钟）；终点见 N/A 说明",
                run_log_refs=[f"run.jsonl#{event.get('seq')}" for event in related],
                artifacts=artifacts,
                na=[f"ts 窗口（止）：N/A —— {na_text['noCloseTs']}"] if not end else [],
                boundary=finding.get("boundary", "")))
            continue
        paths = [item.strip() for item in str(finding["evidence"]).split(",") if item.strip()]
        stamps = [stamp for stamp in (_mtime(root, path) for path in paths) if stamp]
        artifacts = []
        for path in paths:
            row = _subject_artifact(pol, root, events, path)
            row["ref"] = _mtime(root, path) or "N/A（mtime 取不到）"
            artifacts.append(row)
        notes = [f"executionId：N/A —— {na_text['noExecution'].format(surface='git 轨巡检')}"]
        if not stamps:
            notes.append(f"ts 窗口：N/A —— {na_text['noWindow']}；工作树项只有文件 mtime，不冒充节点窗口")
        cards.append(_new_card(
            pol, kind=kinds["uncommitted"], evidence=str(finding["evidence"]), surface="gitlog",
            judge=detail, execution=None, node=None,
            start=min(stamps) if stamps else None, end=max(stamps) if stamps else None,
            window_note="窗口=涉事文件 mtime 起止（文件系统真实值，不是节点窗口）" if stamps else None,
            artifacts=artifacts, na=notes, boundary=finding.get("boundary", "")))
    return cards


# ── 检出面④：L2 回流执法（issue 闭环 ↔ 评测用例）────────────────────────────────
def _relay_judge_line(rendered: str, needle: str) -> str:
    for line in rendered.splitlines():
        if needle and needle in line:
            return line.strip()
    return ""


def _l2_rule(root: Path) -> str:
    """判据文本原文取自 governance/eval-spec.yaml `caseTiers.L2`，不在代码里复述一遍。"""
    for candidate in (root / "governance/eval-spec.yaml", ROOT_DIR / "governance/eval-spec.yaml"):
        try:
            data = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            continue
        rule = (data.get("caseTiers") or {}).get("L2")
        if rule:
            return str(rule).strip()
    return "N/A（读不到 governance/eval-spec.yaml 的 caseTiers.L2 ⇒ 判据原文取不到）"


def from_relay(pol: dict, root: Path, events: list) -> list:
    from eval import relay
    kinds, na_text = pol["kinds"], pol["naReasons"]
    if not (root / "issue").is_dir():
        return []
    result = relay.audit(root)
    rendered = relay.render(result)
    rule = _l2_rule(root)
    relay_na = [f"executionId / ts 窗口：N/A —— {na_text['relayGap']}"]
    cards = []
    for entry in result["missing"]:
        line = _relay_judge_line(rendered, entry["id"]) or f"- `{entry['id']}`（{entry['grade']}｜{entry['state']}）"
        artifacts = [_subject_artifact(pol, root, events, entry["id"])]
        binding = latest_binding(events, entry["id"])
        execution = node = start = end = None
        refs = []
        notes = list(relay_na)
        if binding:
            event = _by_seq(events).get(binding["seq"]) or {}
            execution, node = event.get("executionId"), event.get("node")
            start, end = node_window(events, execution, node)
            refs = [binding["where"]]
            notes = []
        cards.append(_new_card(
            pol, kind=kinds["missingBackflow"], evidence=entry["id"], surface="relay",
            judge=f"{line} ｜ 判据原文（{pol['surfaces']['relay']['ruleSource']}）：{rule}",
            execution=execution, node=node, start=start, end=end,
            window_note=pol["windowRule"] if binding else None, run_log_refs=refs,
            artifacts=artifacts, na=notes,
            boundary="缺回流只说明「没有回归」，不说明原判定错了；更不得为了让它绿去改判据"))
    for row in result["dangling"]:
        case = str(row.get("case") or "")
        line = _relay_judge_line(rendered, case)
        evidence = f"{row['eval']}#{case}→{row['ref']}"
        cards.append(_new_card(
            pol, kind=kinds["danglingRef"], evidence=evidence, surface="relay",
            judge=line or "（relay 报告未列出该行，仅结构化字段可用）",
            execution=None, node=None, artifacts=[_subject_artifact(pol, root, events, row["eval"])],
            na=list(relay_na), boundary="用例声明了没核实的关联 ⇒ 覆盖率是虚的"))
    for item in result["loadErrors"]:
        relative = str(item).split(":", 1)[0].strip()
        cards.append(_new_card(
            pol, kind=kinds["unreadableEval"], evidence=relative, surface="relay",
            judge=str(item), execution=None, node=None,
            artifacts=[_subject_artifact(pol, root, events, relative)],
            na=list(relay_na) + [f"判据核对：N/A —— 评测集读不动，这面量具在该内容上是哑的"],
            boundary="读不动不等于通过：回流核对在这一套上没有发生"))
    return cards


def collect(root: Path, max_age_hours: float = 4.0) -> dict:
    """跑四个检出面 → 去重后的候选卡集合。只读，不落盘（落盘由 write() 负责）。"""
    import tsr
    from obs import gitlog, schema
    root = Path(root).resolve()
    pol = policy(root)
    events = schema.read_events(root) if (root / schema.RUN_LOG).is_file() else []
    notes: list = []
    errors = tsr.verify(root, notes)
    surfaces = {name: [] for name in pol["surfaces"]}
    broken: list = []
    batches = [("verify", from_verify(pol, root, events, errors)),
               ("report", from_report(pol, root, events))]
    if gitlog.is_repo(root):
        batches.append(("gitlog", from_gitlog(pol, root, events,
                                              gitlog.find_gaps(root, unclosed_pairs(events),
                                                               max_age_hours=max_age_hours))))
    else:
        broken.append("gitlog 检出面：N/A —— 该根目录不是 git 仓，git 轨无从巡检（不当已通过）")
    if (root / "issue").is_dir():
        try:
            batches.append(("relay", from_relay(pol, root, events)))
        except (ValueError, OSError) as exc:
            broken.append(f"L2 回流检出面：N/A —— relay 读不动（{exc}），这面量具本轮没跑成，不当已通过")
    else:
        broken.append("L2 回流检出面：N/A —— 该项目没有 issue/ 问题池，这面无从检（不当已通过）")
    cards: dict = {}
    for name, batch in batches:
        surfaces[name] = [card["id"] for card in batch]
        for card in batch:
            known = cards.get(card["id"])
            if known is None:
                cards[card["id"]] = card
                continue
            # 同一事实被两处检出面命中 ⇒ 只留一张卡，两处判据都抄进卡
            for field in ("surfaces", "judges", "runLogRefs", "na"):
                for value in card[field]:
                    if value not in known[field]:
                        known[field].append(value)
            for artifact in card["artifacts"]:
                if not any(item["path"] == artifact["path"] for item in known["artifacts"]):
                    known["artifacts"].append(artifact)
            if not known.get("executionId") and card.get("executionId"):
                known["executionId"], known["node"] = card["executionId"], card["node"]
                known["window"] = card["window"]
    for card in cards.values():
        card["na"] = _na_fields(pol, card)
    # 闭环后段：归因到具体条款（plan v2 §5）。注册表没声明判据就如实报「这没跑」，不静默跳过。
    attribution_summary = None
    try:
        from obs import attribution
        attribution_summary = attribution.attribute_all(root, list(cards.values()), None, pol)
    except ValueError as exc:
        attribution_summary = {"error": str(exc)}
        broken.append(f"归因段：N/A —— {exc}（没归因不等于归因通过）")
    return {"root": root, "policy": pol,
            "cards": sorted(cards.values(), key=lambda card: (card["kind"], card["evidence"])),
            "surfaces": surfaces, "broken": broken, "verifyErrors": errors,
            "verifyNotes": notes, "events": len(events), "attribution": attribution_summary}


def render(card: dict, pol: dict) -> str:
    label = str(pol["label"])
    cap = int(pol.get("maxArtifactsPerCard", len(card["artifacts"]) or 12))
    limit = int(pol.get("maxEvidenceChars", 240))
    lines = [f"# 候选问题卡 · {card['kind']}（{label}）", ""]
    lines.append(f"本卡由检测面自动生成：**{label}**。只登记「哪个量具在说什么对不上」＋机器派生指针，"
                 "不判定问题成立、不分级、不写进 `issue/`（历史证据只读；自动建档等于替人判定问题成立）。")
    lines.append("")
    lines.append(f"- 候选 ID：`{card['id']}` ｜ 状态：{pol['statusValue']}")
    lines.append(f"- 等级：**{pol['gradeValue']}**")
    names = "、".join(f"{pol['surfaces'][name]['name']}（{pol['surfaces'][name]['judgeSource']}）"
                      for name in card["surfaces"] if name in pol["surfaces"])
    lines.append(f"- 检出面：{names or 'N/A（检出面未在注册表声明）'}")
    lines.append(f"- 触发执行：executionId `{card['executionId'] or 'N/A'}` ｜ node `{card['node'] or 'N/A'}`"
                 f" ｜ run-log 指针 {'、'.join(card['runLogRefs']) or 'N/A'}")
    window = card["window"] or {}
    note = f"（口径：{window['note']}）" if window.get("note") else ""
    lines.append(f"- ts 窗口：起 `{window.get('start') or 'N/A'}` → 止 `{window.get('end') or 'N/A'}`{note}")
    lines.append("- 涉事产物：path + sha256（台账记录值 ↔ 磁盘现值；两者不等才是异常，N/A 说明取不到的原因）")
    lines.append("")
    if card["artifacts"]:
        lines += ["| path | 台账记录 sha256 | 磁盘现值 sha256 | 字节 | 指针/备注 |", "|---|---|---|---|---|"]
        for item in card["artifacts"][:cap]:
            recorded = f"`{item['recorded']}`" if item.get("recorded") else "N/A"
            disk = f"`{item['disk']}`" if item.get("disk") else "N/A"
            bytes_ = item.get("bytes")
            extra = "；".join(part for part in (item.get("ref") or "", item.get("note") or "") if part)
            lines.append(f"| `{item['path'][:limit]}` | {recorded} | {disk} | "
                         f"{bytes_ if bytes_ is not None else 'N/A'} | {extra or '—'} |")
        if len(card["artifacts"]) > cap:
            lines.append(f"| （其余 {len(card['artifacts']) - cap} 个产物未列，受 candidates.maxArtifactsPerCard 限制） "
                         f"| — | — | — | — |")
        lines.append("")
    lines.append("## 命中的判据文本原文")
    lines.append("")
    for judge in card["judges"]:
        lines += ["```text", str(judge), "```", ""]
    if card["na"]:
        lines += ["## N/A 与原因（取不到就是取不到，禁止用估算/默认值冒充实测）",
                  *[f"- {item}" for item in card["na"]], ""]
    if card.get("boundary"):
        lines += ["## 边界", f"- {card['boundary']}", ""]
    lines += [_attribution_section(card), ""]
    lines += ["## 下一步（属人的判定）",
              "- 确认这条是否成立：成立才由人升级为正式问题卡并定级（P0/P1）；不成立就删掉本卡。",
              f"- 复算命令（1 条 CLI 调用）：`{pol['recompute']}`",
              f"- {pol.get('boundary', '')}"]
    return "\n".join(lines) + "\n"


def _attribution_section(card: dict) -> str:
    """归因段由 obs.attribution 渲染；它没跑成时就如实写「没跑」，绝不留白让人读成「没有归属」。"""
    attribution = card.get("attribution")
    if not attribution:
        return ("## 归因（条款级）\n\n"
                "N/A —— 本轮没有跑归因（注册表未声明 attribution 判据或生成器未被调用）；"
                "「没归因」不等于「没有条款可归」，也不等于「归属已确认」。")
    from obs import attribution as module
    return module.render_block(attribution)


def _assert_allowed(root: Path, out_dir: Path, pol: dict) -> None:
    """落点硬边界机械化：注册表 forbidWriteInto 里的目录（含其父）一律不许当输出。"""
    for name in pol.get("forbidWriteInto") or []:
        blocked = (root / str(name)).resolve()
        if out_dir == blocked or blocked in out_dir.parents or out_dir in blocked.parents:
            raise ValueError(f"候选卡落点被注册表禁止：{out_dir.as_posix()} 与 {blocked.as_posix()} 重叠"
                             f"（issue/ 是历史证据、只读；自动建档等于替人判定问题成立）")


def write(root: Path, cards: list, pol: dict | None = None) -> dict:
    root = Path(root).resolve()
    pol = pol or policy(root)
    out_dir = (root / str(pol["outputDir"])).resolve()
    _assert_allowed(root, out_dir, pol)
    out_dir.mkdir(parents=True, exist_ok=True)
    created, updated, unchanged = [], [], []
    for card in cards:
        target = out_dir / f"{card['id']}.md"
        _assert_allowed(root, target.resolve().parent, pol)
        body = render(card, pol)
        if not target.is_file():
            target.write_text(body, encoding="utf-8")
            created.append(card["id"])
        elif target.read_text(encoding="utf-8") != body:
            target.write_text(body, encoding="utf-8")
            updated.append(card["id"])
        else:
            unchanged.append(card["id"])
    on_disk = {path.stem for path in out_dir.glob("*.md")}
    stale = sorted(on_disk - {card["id"] for card in cards})
    return {"dir": (root / str(pol["outputDir"])).as_posix(), "created": created,
            "updated": updated, "unchanged": unchanged, "stale": stale}


def _attribution_lines(summary) -> list:
    """归因三分类如实报数 + 承接集中度报警。命中率低也照报——把「没归因上」写成「都归好了」才是造假。

    反过来也一样：命中率 100% 但证据全压在同一条款上，是**量具只在那一条上认得出证据**（覆盖面窄），
    不是各 skill 都承接得好。这种情况下本次命中率一律标注为不可当质量结论使用。
    """
    if not summary or summary.get("error"):
        reason = (summary or {}).get("error", "归因段本轮没有被调用")
        return [f"- 归因：**N/A —— {reason}**（没归因不等于没问题，也不等于都已归属）"]
    buckets, counts = summary["buckets"], summary["counts"]
    total = counts["cards"]
    parts = "｜".join(f"{name} {buckets.get(name, 0)} 张" for name in
                      ("归因（唯一条款证据）", "多归属，需人裁决", "未归因（无条款证据）"))
    rate = f"{buckets.get('归因（唯一条款证据）', 0) / total:.0%}" if total else "N/A"
    lines = [f"- 归因（条款级，逐字命中才算证据）：{parts or 'N/A'}"
             f"｜证据化命中率 {rate}（共 {total} 张）"
             f"；带条款证据的卡（含多归属）{counts.get('withClauses', 0)} 张"]
    lines.append(f"- 路径→skill 一跳都没命中的卡 {counts['noSkill']} 张"
                 f"；涉及多个 skill 的卡 {counts['multiSkillCards']} 张"
                 f"；累计条款证据 {counts['clauses']} 处，去重后落在 "
                 f"{counts.get('distinctClauses', 0)} 个不同条款上"
                 f"（{('、'.join(f'`{name}`' for name in counts.get('distinctClauseFiles') or [])) or 'N/A'}）")
    conc = summary.get("concentration") or {}
    top = conc.get("top") or {}
    if conc.get("alarm"):
        lines.append(f"- ⛔ **{conc['label']}**：{conc['reason']}"
                     f"（占比最高的一条 = `{top.get('file')}:{top.get('startLine')}-{top.get('endLine')}`"
                     f"｜{top.get('heading')}｜{top.get('evidence')}/{conc.get('evidence')} 处证据）"
                     f" ⇒ **{conc['unusable']}**（本轮命中率 {rate}）")
    elif conc.get("belowSample"):
        lines.append(f"- 集中度：{conc['offSampleNote']}")
    return lines


def render_report(result: dict) -> str:
    pol, cards = result["policy"], result["cards"]
    lines = [f"# 候选问题卡生成（{pol['label']}）", ""]
    lines.append(f"- run-log 事件 {result['events']} 条｜verify 报红 {len(result['verifyErrors'])} 条"
                 f"｜说明行 {len(result['verifyNotes'])} 条（说明不进 errors，不据此判红）")
    counts = "、".join(f"{pol['surfaces'][name]['name']} {len(ids)} 条"
                       for name, ids in result["surfaces"].items() if name in pol["surfaces"])
    lines.append(f"- 各检出面检出：{counts or 'N/A（没有可跑的检出面）'}")
    if result["broken"]:
        lines.append("- 本轮没跑成的检出面（如实报，不当已通过）：")
        lines += [f"  - {item}" for item in result["broken"]]
    lines.append(f"- 去重后候选：**{len(cards)} 张**（同一事实被两处命中只出一张；等级一律留空）")
    lines += _attribution_lines(result.get("attribution"))
    lines.append(f"- 落点：`{pol['outputDir']}/`（派生区，**不写 `issue/`**）")
    lines.append("")
    if cards:
        lines += ["| 候选 kind | 张数 | 证据（首条） |", "|---|---|---|"]
        grouped: dict = {}
        for card in cards:
            grouped.setdefault(card["kind"], []).append(card)
        limit = int(pol.get("maxEvidenceChars", 240))
        for kind in sorted(grouped):
            lines.append(f"| {kind} | {len(grouped[kind])} | `{grouped[kind][0]['evidence'][:limit]}` |")
        lines.append("")
    else:
        lines.append("四个检出面本轮都没有检出项 ⇒ 没有候选可建（这是「没检出」，不等于「没问题」）。")
        lines.append("")
    lines.append(f"复算：`{pol['recompute']}`")
    return "\n".join(lines) + "\n"
