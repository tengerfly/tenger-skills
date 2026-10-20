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

5. 人在环关口：每张卡带**确认协议**（`candidates.confirmation`），三个字段确认人／确认时间／结论
   由人填在 `confirmation.dir`（生成器只读、永不写，且落点检查会拒绝与派生区重叠）；
   闭环率的分子分母都只算「已确认且结论＝`closureConclusion`」的卡，未确认／待定／无效单独报数，
   分母为空一律 N/A。自动执行者当「确认人」判非人确认——夜间自主会话不得自行确认候选卡。

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
    missing = [key for key in ("label", "gradeValue", "naReasons", "surfaces", "kinds", "confirmation")
               if not section.get(key)]
    if missing:
        raise ValueError(f"{path.as_posix()} 的 candidates 节缺必需键 {missing} ⇒ 拒绝用默认值冒充实装")
    return section


def card_id(pol: dict, kind: str, evidence: str) -> str:
    """种子公式与 obs/anomaly.py:finding_id 同构（kind|evidence），两处写手不会各造一套 id。"""
    seed = f"{kind}|{evidence}"
    return str(pol.get("idPrefix", "CAND-")) + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:10].upper()


# ── 闭环中间段：候选卡 → 人的确认（plan v2 §5 的人在环关口）。
# 生成器**只读**确认记录，任何字段都不代填；「无效」与「未确认」分开报——
# 前者是有人声称确认了但机器不认（下一步是修确认记录），后者是还没人看（下一步是找人看）。
CONFIRMATION_KEYS = ("dir", "fileName", "schema", "fieldNames", "unconfirmed", "conclusions",
                     "excludedConclusions", "closureConclusion", "commitPattern", "autoActors",
                     "closureFieldNames", "rules")
CONFIRMATION_RULES = ("protocol", "noSelfConfirm", "unconfirmedNotCounted", "emptyDenominator",
                      "timestamp", "closedNeeds", "shape", "naSection", "splitStorage")
BLANK_VALUES = ("", "-", "n/a", "na", "无", "留空", "待定填")


def confirmation_policy(pol: dict) -> dict:
    """确认协议判据全在注册表；缺键就报错，不退回默认值（同 policy() / attribution.policy() 的先例）。"""
    conf = pol.get("confirmation")
    if not isinstance(conf, dict):
        raise ValueError("governance/obs-registry.yaml 未声明 candidates.confirmation ⇒ 不猜确认协议落点与字段")
    missing = [key for key in CONFIRMATION_KEYS if not conf.get(key)]
    if missing:
        raise ValueError(f"candidates.confirmation 缺必需判据键 {missing} ⇒ 拒绝用默认值冒充实装")
    rules = conf["rules"] if isinstance(conf["rules"], dict) else {}
    missing_rules = [name for name in CONFIRMATION_RULES if not rules.get(name)]
    if missing_rules:
        raise ValueError(f"candidates.confirmation.rules 缺判据文案 {missing_rules} ⇒ 拒绝执行没有凭据的红口")
    for key, roles in (("fieldNames", ("actor", "time", "conclusion")),
                       ("closureFieldNames", ("issue", "commit"))):
        absent = [role for role in roles if not (conf.get(key) or {}).get(role)]
        if absent:
            raise ValueError(f"candidates.confirmation.{key} 缺字段角色 {absent} ⇒ 代码不猜中文字段名")
    return conf


def confirmation_path(root: Path, pol: dict, candidate_id: str) -> Path:
    conf = confirmation_policy(pol)
    return (Path(root) / str(conf["dir"])).resolve() / str(conf["fileName"]).format(id=candidate_id)


def _is_blank(value, conf: dict) -> bool:
    """空值判定：占位文案、`未确认*` 前缀、以及注册表认可的留空写法都算没填（不是没填的声称）。"""
    text = str(value or "").strip()
    return (not text or text == str(conf["unconfirmed"]) or text.startswith("未确认")
            or text.casefold() in BLANK_VALUES)


def _instant(value: str):
    """只认带时区的 ISO-8601 时刻：naive 字符串要猜时区，猜了就等于把别处的确认算进本时区。"""
    try:
        moment = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return moment if moment.tzinfo is not None else None


def read_confirmation(root: Path, pol: dict, candidate_id: str) -> dict:
    """读一张候选卡的人写确认记录 ⇒ {state: 未确认|已确认|无效, conclusion, closed, problems, ...}。"""
    conf = confirmation_policy(pol)
    rules, names = conf["rules"], conf["fieldNames"]
    path = confirmation_path(root, pol, candidate_id)
    try:
        shown = path.relative_to(Path(root).resolve()).as_posix()   # 卡面指针一律仓相对，绝对路径换台机器就失效
    except ValueError:
        shown = path.as_posix()
    info = {"id": candidate_id, "path": shown, "dir": str(conf["dir"]), "state": "未确认",
            "actor": None, "at": None, "conclusion": None, "counts": False, "closed": False,
            "closure": [], "problems": [f"{rules['protocol']}：`{conf['dir']}/` 下没有 `{path.name}`"]}
    if not path.is_file():
        return info
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, yaml.YAMLError) as exc:
        info.update(state="无效", problems=[f"{rules['shape']}：读不动 `{path.as_posix()}`（{exc}）"])
        return info
    if not isinstance(raw, dict):
        info.update(state="无效", problems=[f"{rules['shape']}：`{path.as_posix()}` 不是 YAML 映射"])
        return info
    values = {role: str(raw.get(names[role]) or "").strip() for role in names}
    blank = [names[role] for role in ("actor", "time", "conclusion") if _is_blank(values[role], conf)]
    if blank:
        info["problems"] = [f"{rules['protocol']}：缺 {'、'.join(blank)} ⇒ 计未确认（生成器不得代填）"]
        return info
    # 三字段都齐了才回显文件里写的人/时刻/结论：判「无效」时更要让人看见到底是谁声称确认过
    info.update(actor=values["actor"], at=values["time"], conclusion=values["conclusion"])
    if values["actor"].casefold() in {str(actor).casefold() for actor in conf["autoActors"]}:
        info.update(state="无效", problems=[f"{rules['noSelfConfirm']}（确认人 `{values['actor']}`）"])
        return info
    if values["conclusion"] not in conf["conclusions"]:
        info.update(state="无效",
                    problems=[f"{rules['shape']}：结论 `{values['conclusion']}` 不在注册表枚举 "
                              f"{sorted(conf['conclusions'])} 内 ⇒ 判无效，不当已确认"])
        return info
    moment = _instant(values["time"])
    if moment is None:
        info.update(state="无效", problems=[f"{rules['timestamp']}：确认时间 `{values['time']}` 不合法"])
        return info
    if moment > datetime.now(timezone.utc):
        info.update(state="无效", problems=[f"{rules['timestamp']}：确认时间 `{values['time']}` 晚于本机时钟"])
        return info
    info.update(state="已确认", problems=[])
    excluded = [str(item) for item in conf["excludedConclusions"]]
    if values["conclusion"] in excluded:
        info["problems"] = [f"结论「{values['conclusion']}」与未确认同等待遇：{rules['unconfirmedNotCounted']}"]
    elif values["conclusion"] == str(conf["closureConclusion"]):
        info["counts"] = True
        _fill_closure(root, conf, raw, info)
    return info


def _fill_closure(root: Path, conf: dict, raw: dict, info: dict) -> None:
    """闭环两要件全部机器查：升级后的正式卡文件真实存在＋回归 commit 经 git cat-file 验真。"""
    names, rules = conf["closureFieldNames"], conf["rules"]
    issue_token = str(raw.get(names["issue"]) or "").strip().strip("`'\" ")
    commit_text = str(raw.get(names["commit"]) or "").strip()
    issue_ok = commit_ok = False
    if _is_blank(issue_token, conf):
        info["closure"].append(f"{names['issue']}：N/A —— 没填 ⇒ {rules['closedNeeds']}")
    else:
        target = (Path(root) / issue_token.replace("\\", "/")).resolve()
        if target.is_file() and Path(root).resolve() in target.parents:
            issue_ok = True
            info["closure"].append(f"{names['issue']} ✓ `{issue_token}` 文件真实存在")
        else:
            info["closure"].append(f"{names['issue']} ✗ `{issue_token}` 在仓内查不到该文件"
                                   " ⇒ 写了路径不等于升级 occurred，判未闭环")
    pointers = re.findall(str(conf["commitPattern"]), commit_text)
    if not pointers:
        info["closure"].append(f"{names['commit']}：N/A —— 没有可验真的 commit 指针 ⇒ {rules['closedNeeds']}")
    else:
        import validate_core as core
        state = core.commit_exists(core.git_repos(root), pointers[0])
        if state is True:
            commit_ok = True
            info["closure"].append(f"{names['commit']} ✓ `{pointers[0]}` git cat-file 验真通过")
        elif state is None:
            info["closure"].append(f"{names['commit']} ? `{pointers[0]}` git 查不动（没装 git 或不在仓）"
                                   " ⇒ 判未闭环，不判通过")
        else:
            info["closure"].append(f"{names['commit']} ✗ `{pointers[0]}` 在该仓不存在 ⇒ 判未闭环")
    info["closed"] = bool(issue_ok and commit_ok)


def closure_audit(root: Path, pol: dict, cards: list) -> dict:
    """闭环率：分子分母都只算「已确认且结论=closureConclusion」的卡；未确认/待定/无效单独报数。"""
    conf = confirmation_policy(pol)
    unconfirmed, invalid, confirmed = [], [], {}
    for card in cards:
        info = card.get("confirmation") or read_confirmation(root, pol, card["id"])
        if info["state"] == "未确认":
            unconfirmed.append(info)
        elif info["state"] == "无效":
            invalid.append(info)
        else:
            confirmed.setdefault(info["conclusion"], []).append(info)
    pool = confirmed.get(str(conf["closureConclusion"]), [])
    closed = [info for info in pool if info.get("closed")]
    return {"policy": conf, "cards": len(cards), "unconfirmed": unconfirmed, "invalid": invalid,
            "confirmed": confirmed, "pool": pool, "closed": closed,
            "rate": f"{len(closed) / len(pool):.0%}" if pool else "N/A",
            "excluded": [str(item) for item in conf["excludedConclusions"]]}


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
        if finding.get("cardKind") == "unpushed":
            # 交付面没有 execution 也没有涉事文件：卡面照实留 N/A，绝不能落到「改动未提交」那一类里去
            cards.append(_new_card(
                pol, kind=finding["kind"], evidence=str(finding["evidence"]), surface="gitlog",
                judge=detail, execution=None, node=None, start=None, end=None, artifacts=[],
                na=[f"executionId：N/A —— {na_text['noExecution'].format(surface='git 轨巡检·交付面')}",
                    f"ts 窗口：N/A —— 交付核对看的是分支领先数，不是某次执行的时间窗（不拿提交时刻冒充节点窗口）"],
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
        # 确认段与卡面同批读取：卡是派生物、确认记录属人，二者分开存放所以重算永不覆盖人的判定
        card["confirmation"] = read_confirmation(root, pol, card["id"])
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
    lines += [_confirmation_section(card, pol), ""]
    lines += ["## 下一步（属人的判定）",
              "- 确认这条是否成立：成立才由人升级为正式问题卡并定级（P0/P1）；不成立就删掉本卡。"
              f"确认只写在 `{_confirmation_target(card, pol)}`，卡正文每次重算都会被覆写。",
              f"- 复算命令（1 条 CLI 调用）：`{pol['recompute']}`",
              f"- {pol.get('boundary', '')}"]
    return "\n".join(lines) + "\n"


def _confirmation_target(card: dict, pol: dict) -> str:
    """确认记录路径：优先用已读取的确认段，没读过就按注册表现算（不落盘，只是指路）。"""
    info = card.get("confirmation")
    if info:
        return info["path"]
    try:
        return confirmation_path(Path.cwd(), pol, card["id"]).as_posix()
    except ValueError:
        return f"{pol.get('confirmation', {}).get('dir', 'N/A')}/{card['id']}.yaml"


def _confirmation_section(card: dict, pol: dict) -> str:
    """卡面的确认协议段：摆出三个人在环字段，并如实回显当前确认状态（没确认就写没确认）。"""
    conf = confirmation_policy(pol)
    rules, names = conf["rules"], conf["fieldNames"]
    closure_names = conf["closureFieldNames"]
    placeholder = str(conf["unconfirmed"])
    lines = ["## 确认协议（人在环）", ""]
    info = card.get("confirmation")
    if not info:
        lines.append(rules["naSection"])
    else:
        lines.append(f"- 当前状态：**{info['state']}**")
        lines.append(f"- {names['actor']}：`{info.get('actor') or placeholder}`"
                     f" ｜ {names['time']}：`{info.get('at') or placeholder}`"
                     f" ｜ {names['conclusion']}：`{info.get('conclusion') or placeholder}`")
        lines.append(f"- 确认记录（人手写、生成器永不写这个文件）：`{info['path']}`")
        if info["problems"]:
            lines.append("- 为什么不认：")
            lines += [f"  - {item}" for item in info["problems"]]
        if info["closure"]:
            lines.append(f"- 闭环两要件核对（结论＝{conf['closureConclusion']} 时才有意义）：")
            lines += [f"  - {item}" for item in info["closure"]]
        lines.append(f"- 已闭环：**{'是' if info.get('closed') else '否'}**")
    lines.append(f"- 判据：{rules['protocol']}")
    lines.append(f"- 判据：{rules['unconfirmedNotCounted']}")
    lines.append(f"- 判据：{rules['noSelfConfirm']}")
    lines.append("")
    lines.append(f"填写方式：在 `{conf['dir']}/` 下按候选 ID 建 "
                 f"`{str(conf['fileName']).format(id=card['id'])}`，形如（尖括号是占位，不是已填）：")
    lines += ["```yaml",
              f"schema: {conf['schema']}",
              f"候选: {card['id']}",
              f"{names['actor']}: <真人姓名>",
              f"{names['time']}: \"<ISO-8601 带时区时刻>\"",
              f"{names['conclusion']}: <{' | '.join(sorted(conf['conclusions']))}>",
              f"{closure_names['issue']}: <结论＝{conf['closureConclusion']} 时填：升级后的正式问题卡路径>",
              f"{closure_names['commit']}: <结论＝{conf['closureConclusion']} 时填：修复回归 commit>",
              "```", ""]
    lines.append("结论取值与含义（注册表原文）：")
    lines += [f"- {value}：{meaning}" for value, meaning in sorted(conf["conclusions"].items())]
    return "\n".join(lines)


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
    conf_dir = (root / str(confirmation_policy(pol)["dir"])).resolve()
    if out_dir == conf_dir or conf_dir in out_dir.parents or out_dir in conf_dir.parents:
        raise ValueError(f"生成器不得写确认目录：落点 {out_dir.as_posix()} 与 {conf_dir.as_posix()} 重叠"
                         "（确认记录属人判定；且派生区被 .gitignore 忽略，把确认塞进去等于让判定证据失踪）")
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


def _closure_lines(audit: dict) -> list:
    """闭环率逐数如实报：分母为空就 N/A，绝不把「没人确认」读成「都闭环了」或「0% 通过」。"""
    conf, rules = audit["policy"], audit["policy"]["rules"]
    pool, closed = audit["pool"], audit["closed"]
    distribution = "、".join(f"{value} {len(items)} 张"
                             for value, items in sorted(audit["confirmed"].items())) or "无"
    rate = (f"{audit['rate']}（已闭环 {len(closed)}／已确认「{conf['closureConclusion']}」 {len(pool)} 张）"
            if pool else f"N/A —— {rules['emptyDenominator']}")
    lines = [f"- 确认协议（人在环）：候选 {audit['cards']} 张 ⇒ 未确认 {len(audit['unconfirmed'])} 张"
             f"｜无效确认 {len(audit['invalid'])} 张｜已确认 {sum(len(v) for v in audit['confirmed'].values())} 张"
             f"（结论分布：{distribution}）",
             f"- 闭环率：**{rate}** ｜ 口径：{rules['unconfirmedNotCounted']}",
             f"- 确认记录目录：`{conf['dir']}/` ｜ {rules['splitStorage']}"]
    for info in audit["invalid"][:5]:
        lines.append(f"  - 无效确认 `{info['id']}`：{'；'.join(info['problems']) or rules['shape']}")
    if len(audit["invalid"]) > 5:
        lines.append(f"  - （其余 {len(audit['invalid']) - 5} 条无效确认未列）")
    if not pool:
        lines.append(f"  - 分母为空：本轮没有一张卡经人确认成立 ⇒ 闭环率无从计算"
                     f"（未确认 {len(audit['unconfirmed'])} 张单独报数，不折算成通过率）")
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
    lines += _closure_lines(closure_audit(result["root"], pol, cards))
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
