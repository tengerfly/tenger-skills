"""tsr — the only runtime entry point the skills touch for observability.

Contract: the caller passes semantics (node, skill, role, gate, round, refs) and this
tool stamps time, assigns the sequence number and hashes artifacts. A hand-written
timestamp or digest is therefore not expressible through this CLI, which is the point —
ledger fields must be falsifiable against the machine and the disk.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from obs import metrics, schema


def _project(args) -> Path:
    return Path(args.project_root).resolve()


def _bool(value: str) -> bool:
    lowered = str(value).strip().lower()
    if lowered not in {"true", "false"}:
        raise argparse.ArgumentTypeError("allow-downstream must be true or false")
    return lowered == "true"


def _event(args, name: str) -> dict:
    return {
        "schema": schema.SCHEMA, "event": name,
        "project": args.project_id or _project(args).name,
        "executionId": args.execution_id, "node": args.node, "skill": args.skill,
        "role": args.role, "actor": args.actor, "origin": "self",
        "parentExecution": args.parent_execution,
        "round": args.round, "batch": args.batch, "state": args.state,
        "reqRefs": args.req or [], "artifacts": [], "upstream": [],
    }


def cmd_start(args) -> int:
    event = _event(args, "node-start")
    schema.append_event(_project(args), event)
    print(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
    return 0


def cmd_end(args) -> int:
    root = _project(args)
    event = _event(args, "node-end")
    event["gate"] = args.gate
    event["allowDownstream"] = args.allow_downstream
    for raw in args.artifact or []:
        path = (root / raw.replace("\\", "/")).resolve()
        if not path.is_relative_to(root):
            print(f"artifact escapes project root: {raw}", file=sys.stderr)
            return 1
        if not path.is_file():
            print(f"declared artifact does not exist: {raw}", file=sys.stderr)
            return 1
        bound = schema.digest(path)  # hash the resolved absolute path; record the portable form
        bound["path"] = raw.replace("\\", "/")
        event["artifacts"].append(bound)
    for raw in args.upstream or []:
        artifact, _, gate = raw.partition(":")
        event["upstream"].append({"artifact": artifact, "gate": gate or "PASS"})
    if args.sunk_of:
        event["sunkOf"] = args.sunk_of
    schema.append_event(root, event)
    print(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
    return 0


def _bind_key(event: dict, index: int):
    """Sort key that reflects real precedence, never raw string luck.

    The ledger mixes '2026-10-12 09:34' with '2026-10-12T09:33' and a space sorts before
    'T', so comparing timestamps as strings crowns the older snapshot as the current
    promise. Write order leads (seq is assigned by this tool at append time and is the
    replay order); the digit-only timestamp only breaks ties when a hand-authored line
    repeats or omits seq.
    """
    seq = event.get("seq")
    digits = re.sub(r"\D", "", str(event.get("ts", "")))[:14].ljust(14, "0")
    return (seq if isinstance(seq, int) and not isinstance(seq, bool) else index, digits)


def artifact_bindings(events: list) -> dict:
    """path -> node-end bindings, oldest first: [(key, where, artifact)].

    The newest binding per path is the only one making a claim about today's bytes;
    everything before it is a photograph of the moment that node closed.
    """
    bindings: dict = {}
    for index, event in enumerate(events, 1):
        if event.get("event") != "node-end":
            continue
        where = f"{schema.RUN_LOG}#{event.get('seq', index)}"
        for artifact in event.get("artifacts") or []:
            path = str(artifact.get("path", "")).replace("\\", "/")
            bindings.setdefault(path, []).append((_bind_key(event, index), where, artifact))
    return {path: sorted(rows, key=lambda row: row[0]) for path, rows in bindings.items()}


def check_bindings(root: Path, events: list, errors: list, notes: list) -> None:
    """Re-derive today's bytes against the newest binding per path; older snapshots are history.

    Same 口径 as validate_core.check_digests / subject_bindings: a recorded sha256 means
    "these are the bytes this node saw when it closed", so a superseded snapshot necessarily
    stops matching once the artifact legitimately evolves in a later node. Grading every
    historical snapshot as drift is what buries real findings in noise (13 findings against
    153 lines over there, and the same shape here).

    Detection power is unchanged for the failure this exists to catch: edit the body and let
    no later node-end re-bind that path, and the stale record is still the newest binding for
    the path, so it still fails below.
    """
    superseded = []
    for path, rows in sorted(artifact_bindings(events).items()):
        target = root / path
        fresh = schema.digest(target)["sha256"] if target.is_file() else None
        _, latest_where, latest = rows[-1]
        if fresh is None:
            errors.append(f"{latest_where}: artifact vanished: {path}")
        elif fresh != latest.get("sha256"):
            errors.append(f"{latest_where}: artifact edited after node-end: {path}"
                          "（该路径最新一次绑定，此后没有节点重新绑定它 ⇒ 改了正文没落台账）")
        for _, where, artifact in rows[:-1]:
            if fresh is None:
                superseded.append(f"{where}→{path}（文件已不在磁盘）")
            elif fresh != artifact.get("sha256"):
                superseded.append(f"{where}→{path}")
    if superseded:
        notes.append(f"{len(superseded)} 条更早绑定已被后续节点超越，不算违规"
                     f"（快照只承诺当时字节）：{'、'.join(superseded)}")


def verify(root: Path, notes: list | None = None) -> list:
    """Re-derive facts from disk and the log itself; trust nothing the caller asserted.

    `notes` is an optional accumulator for honest explanatory output. Superseded snapshots
    deliberately stay out of the returned errors: callers grade red/green by len(errors),
    and an older snapshot is a fact about history, not a violation.
    """
    errors = []
    explained = notes if notes is not None else []
    events = schema.read_events(root)
    if not events:
        return ["no run-log events: observability is not wired for this project"]
    registered = metrics.load_registry()
    last_seq, last_ts = 0, ""
    opened = set()
    for index, event in enumerate(events, 1):
        where = f"{schema.RUN_LOG}#{event.get('seq', index)}"
        errors.extend(f"{where}: {error}" for error in schema.validate(event))
        if event.get("node") not in registered:
            errors.append(f"{where}: node is not registered in governance/obs-registry.yaml: {event.get('node')}")
        seq = event.get("seq")
        if not isinstance(seq, int) or seq <= last_seq:
            errors.append(f"{where}: seq must increase strictly (out-of-order writes break replay)")
        last_seq = seq if isinstance(seq, int) else last_seq
        ts = str(event.get("ts", ""))
        if ts < last_ts:
            errors.append(f"{where}: ts goes backwards ({last_ts} -> {ts})")
        last_ts = max(last_ts, ts)
        key = (event.get("executionId"), event.get("node"), event.get("actor"))
        if event["event"] == "node-start":
            opened.add(key)
        elif event["event"] == "node-end":
            if key not in opened:
                errors.append(f"{where}: node-end without matching node-start for {key[0]}/{key[1]}")
            if event.get("gate") == "PASS" and event.get("allowDownstream"):
                closed = [u["artifact"] for u in event.get("upstream") or [] if u.get("gate") != "PASS"]
                if closed:
                    errors.append(f"{where}: PASS with allowDownstream while upstream is closed: {closed}")
    check_bindings(root, events, errors, explained)
    return errors


def cmd_verify(args) -> int:
    notes: list = []
    errors = verify(_project(args), notes)
    for error in errors:
        print(error, file=sys.stderr)
    for note in notes:
        # 说明性输出走 stdout，绝不混进 errors：调用方按 len(errors) 判红绿
        print(f"说明：{note}")
    if errors:
        print(f"run-log verification failed: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("run-log verification passed")
    return 0


def cmd_report(args) -> int:
    root = _project(args)
    notes: list = []
    problems = verify(root, notes)
    for note in notes:
        print(f"说明：{note}")
    events = schema.read_events(root)
    registered = metrics.load_registry()
    node_errors = sorted({str(event.get("node")) for event in events
                          if event.get("node") not in registered})
    policy = metrics.load_objective_policy()
    objective = metrics.objective_status(events, policy)
    text = metrics.render(metrics.summarize(events), node_errors, problems, objective, policy)
    target = root / ".spec/观测/看板.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print(f"看板 → {target.relative_to(root).as_posix()}")
    if node_errors:
        print(f"unregistered nodes: {node_errors}", file=sys.stderr)
        return 1
    return 0


def cmd_host(args) -> int:
    """Read-only host probe: what can this host actually prove, and where does it stop."""
    from obs import host_spec
    home = Path(args.home).expanduser().resolve()
    if not home.is_dir():
        print(f"tsr: host home not found: {home}", file=sys.stderr)
        return 1
    spec = host_spec.load(args.host)
    found = host_spec.discover(spec, home, args.project_slug or "")
    if not found:
        print(f"tsr: no {args.host} trace files matched for {args.project_slug or '(any project)'}", file=sys.stderr)
        return 1
    spans = host_spec.read_spans(spec, found[:args.sample])
    report = host_spec.verify_capabilities(spec, spans)
    print(f"host={args.host} files={len(found)} sampled={len(spans)}")
    for name in sorted(report):
        info = report[name]
        print(f"  {'GRANTED' if info['granted'] else 'denied '} {name}" + (f" — {info['reason']}" if info["reason"] else ""))
    attribution = host_spec.attribute(spans, _project(args))
    print(f"  writes={attribution['writes']} attributed={attribution['byNode']} unattributed={attribution['unattributed']}")
    print("  note: 宿主数据只富化，真相是 .spec/obs/run.jsonl；unattributed 不靠猜补")
    return 0


def cmd_rules(args) -> int:
    """规则命中率（plan v2 §3 智能化）：只读宿主日志算指标，不跑引擎、不新增流程节点。

    宿主无关：字段名与工具名来自 governance/host-specs/<host>.yaml，口径来自
    governance/obs-registry.yaml；取不到的维度由 rules.measure 降级成 N/A。
    """
    from obs import host_spec, rules
    root = _project(args)
    home = Path(args.home).expanduser().resolve()
    if not home.is_dir():
        print(f"tsr: host home not found: {home}", file=sys.stderr)
        return 1
    spec = host_spec.load(args.host)
    found = host_spec.discover(spec, home, args.project_slug or "")
    if not found:
        print(f"tsr: no {args.host} trace files matched for {args.project_slug or '(any project)'}", file=sys.stderr)
        return 1
    spans = host_spec.read_spans(spec, found[:args.sample] if args.sample else found)
    window = rules.apply_window(spans, args.since, args.until) if (args.since or args.until) else None
    report = rules.measure(root, spec, spans, skills=args.skill, window=window,
                           params={"sample": args.sample, "slug": args.project_slug,
                                   "since": args.since, "until": args.until})
    text = rules.render(report)
    print(text)
    if args.write:
        target = root / ".spec/观测/规则命中率.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        print(f"规则命中率 → {target.relative_to(root).as_posix()}")
    # N/A 是诚实降级，不是命令失败：拔掉适配器只让指标少一维，不该把观测链路判红
    return 0


def cmd_slim(args) -> int:
    """精简建议（plan v2 §0 的目标收益）：三读数齐了才允许开口，集中度过阈值机械禁止给删减结论。

    默认就跑注册表钉死的固定口径（全量＋slug＋时间切点）；任一参数被改写 ⇒ slim 自己把该读数
    标成「口径未固定」并拒绝出名单。退出码恒为 0：依据不足是如实降级，不是命令失败。
    """
    from obs import candidates, host_spec, rules, slim
    root = _project(args)
    pol = slim.spec(root)
    cal = pol["caliber"]
    sample = args.sample if args.sample is not None else int(cal["sample"])
    slug = args.project_slug if args.project_slug is not None else str(cal["projectSlug"])
    since = args.since or str(cal["since"])
    until = args.until or str(cal["until"])
    home = Path(args.home).expanduser().resolve()
    if not home.is_dir():
        print(f"tsr: host home not found: {home}", file=sys.stderr)
        return 1
    spec = host_spec.load(args.host)
    found = host_spec.discover(spec, home, slug)
    if not found:
        print(f"tsr: no {args.host} trace files matched for {slug or '(any project)'}", file=sys.stderr)
        return 1
    spans = host_spec.read_spans(spec, found[:sample] if sample else found)
    window = rules.apply_window(spans, since, until)
    hit = rules.measure(root, spec, spans, window=window,
                        params={"sample": sample, "slug": slug, "since": since, "until": until})
    collected = candidates.collect(root, max_age_hours=args.max_age_hours)
    advice = slim.advise(root, hit, collected.get("attribution"), pol)
    print(slim.render(advice))
    print(f"- 本轮候选 {len(collected['cards'])} 张｜命中率读数 {hit.get('value') if hit.get('value') is not None else 'N/A'}"
          f"｜blocked 由闸门判：{len(advice['blocked'])} 条")
    if args.write:
        target = root / str(pol["output"]["file"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(slim.render(advice), encoding="utf-8")
        print(f"精简建议 → {target.relative_to(root).as_posix()}")
    return 0


def cmd_score(args) -> int:
    from obs import score
    root = _project(args)
    result = score.score_project(root)
    text = score.render(result)
    target = root / ".spec/观测/打分.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print(text)
    return 1 if result["redLines"] else 0


def cmd_audit(args) -> int:
    """Cross-check declared work against what actually landed; report, never auto-fix."""
    from obs import anomaly, candidates, gitlog
    root = _project(args)
    events = schema.read_events(root)
    # 未收口口径与候选卡生成器同一个函数：同一事实两处各算一套，卡就会分家
    unclosed = candidates.unclosed_pairs(events)
    findings = gitlog.find_gaps(root, unclosed, max_age_hours=args.max_age_hours)
    if not findings:
        print("audit: 无未收口节点，无超时未提交改动")
        return 0
    for finding in findings:
        print(f"  [{finding['kind']}] {finding['detail']} ｜ 证据 {finding['evidence']}")
    if args.write:
        result = anomaly.upsert(root, findings)
        print(f"问题卡 → 新增 {len(result['created'])} 条，已存在 {len(result['unchanged'])} 条（不重复建条目）")
    else:
        print("  （只报告不落盘；要建档加 --write）")
    return 0


def cmd_candidates(args) -> int:
    """检测面 → 候选问题卡（plan v2 §5 中间段第一格）。只派生指针，不判定、不分级、不进 issue/。

    退出码恒为 0：候选卡是「未经确认的检出项」，红绿由各检出面自己判（verify/relay 才是执法者）。
    把它当门禁会让「有候选」被误读成「有问题成立」。
    """
    from obs import candidates
    root = _project(args)
    result = candidates.collect(root, max_age_hours=args.max_age_hours)
    print(candidates.render_report(result))
    for card in result["cards"][:args.preview]:
        attribution = card.get("attribution") or {}
        where = ""
        if attribution.get("clauses"):
            clause = attribution["clauses"][0]
            where = f" ｜ 条款 {clause['file']}:{clause['startLine']}"
        print(f"  [{card['kind']}] {card['id']} ｜ executionId {card['executionId'] or 'N/A'}"
              f" ｜ 窗口 {card['window'].get('start') or 'N/A'} → {card['window'].get('end') or 'N/A'}"
              f" ｜ 涉事产物 {len(card['artifacts'])} 个"
              f" ｜ 归因 {attribution.get('verdict', 'N/A（归因段没跑成）')}{where}")
    if len(result["cards"]) > args.preview:
        print(f"  （其余 {len(result['cards']) - args.preview} 张未预览；--preview 调大）")
    if args.write:
        written = candidates.write(root, result["cards"])
        print(f"候选卡 → 新增 {len(written['created'])} 张｜更新 {len(written['updated'])} 张｜"
              f"未变 {len(written['unchanged'])} 张 ｜ 落点 {written['dir']}")
        if written["stale"]:
            print(f"  不再命中的旧候选卡 {len(written['stale'])} 张（只报不删，由人处置）："
                  f"{'、'.join(written['stale'][:10])}")
    else:
        print("  （只报告不落盘；要建候选卡加 --write）")
    return 0


def cmd_feedback(args) -> int:
    """反哺有效率（plan v2 §3 智能化第三条）：只读台账与显式复发链，取不到就 N/A，绝不造数。

    退出码恒为 0：N/A 是诚实降级（缺记录／缺链／窗不够），不是命令失败。把它当门禁就会有人为了变绿去凑分母。
    """
    from obs import feedback
    root = _project(args)
    report = feedback.measure(root)
    print(feedback.render(report))
    if args.write:
        print(f"反哺有效率 → {feedback.write(root, report).relative_to(root).as_posix()}")
    else:
        print("  （只报告不落盘；要落派生报告加 --write）")
    return 0


def cmd_recurrence(args) -> int:
    """同型问题复发率（plan v2 §3「智能化」第二条）：只读 issue/ 卡片正文里的显式复发指针。

    口径与文案全部在 governance/obs-registry.yaml 的 recurrence 节（语料 glob、窗口天数、
    指针正则、成链条件、N/A 规则）；键缺失或取值不认识 ⇒ 直接报错退出，不退回默认值。
    不做任何标题相似度配对（上一版那么干同时产出假阳性和假阴性，已作废）。
    退出码恒为 0：这条指标是事实陈述，红绿仍由 issue/ 池与 L2 回流执法；把它当门禁就等于
    「复发率高 ⇒ 判工作流有问题」，那是把量具读数冒成判定。
    """
    from obs import recurrence
    root = _project(args)
    pol = recurrence.policy(root)
    report = recurrence.measure(root, pol)
    print(recurrence.render(report))
    if args.write:
        target = recurrence.write(root, report)
        print(f"复发率报告 → {target.relative_to(root).as_posix()}（只新增派生报告，不改任何卡片）")
    else:
        # 落点也取自注册表（recurrence.report.outputFile）：命令行文案里不另写一套路径
        print(f"  （只报告不落盘；要落 {report['outputFile']} 加 --write）")
    return 0


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        # Windows 控制台默认 GBK：中文口径与 N/A 原因打出去会成乱码，读报告的人只能猜
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="tsr", description="tenger.trace/v1 run log")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--project-id")
    parser.add_argument("--execution-id")
    parser.add_argument("--node")
    parser.add_argument("--skill")
    parser.add_argument("--role", default="produce", choices=sorted(schema.ROLES))
    parser.add_argument("--actor", default="main", choices=sorted(schema.ACTORS))
    parser.add_argument("--parent-execution")
    parser.add_argument("--round", type=int, dest="round", default=None)
    parser.add_argument("--batch", type=int, default=None)
    parser.add_argument("--state")
    parser.add_argument("--req", action="append")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("node-start").set_defaults(handler=cmd_start)

    end = sub.add_parser("node-end")
    end.add_argument("--gate", required=True, choices=sorted(schema.GATES))
    end.add_argument("--allow-downstream", required=True, type=_bool)
    end.add_argument("--artifact", action="append", help="project-relative path; hashed by this tool")
    end.add_argument("--upstream", action="append", help="artifactId:gate of an upstream baseline")
    end.add_argument("--sunk-of", action="append", help="decision id that retired the baseline this work sank")
    end.set_defaults(handler=cmd_end)

    sub.add_parser("verify").set_defaults(handler=cmd_verify)
    sub.add_parser("report").set_defaults(handler=cmd_report)

    host = sub.add_parser("host")
    host.add_argument("--host", required=True)
    host.add_argument("--home", required=True)
    host.add_argument("--project-slug", default="")
    host.add_argument("--sample", type=int, default=20)
    host.set_defaults(handler=cmd_host)

    sub.add_parser("score").set_defaults(handler=cmd_score)

    rules = sub.add_parser("rules")
    rules.add_argument("--host", required=True)
    rules.add_argument("--home", required=True)
    rules.add_argument("--project-slug", default="")
    rules.add_argument("--sample", type=int, default=0, help="只采前 N 个段文件；0=全部（宿主日志会被驱逐，够用就好）")
    rules.add_argument("--skill", action="append", help="把 SKILL.md 语料收窄到某个 skill（可重复；shared 仍整体计入分母）")
    rules.add_argument("--since", default="", help="ISO-8601 带时区起始切点；不填＝不设窗口（口径未固定）")
    rules.add_argument("--until", default="", help="ISO-8601 带时区截止切点；不填＝不设窗口（口径未固定）")
    rules.add_argument("--write", action="store_true", help="落 .spec/观测/规则命中率.md（默认只打印）")
    rules.set_defaults(handler=cmd_rules)

    slim = sub.add_parser("slim", help="精简建议（三读数齐了才开口；默认按注册表的固定口径跑）")
    slim.add_argument("--host", default="qoder")
    slim.add_argument("--home", default="~/.qoder-cn", help="宿主日志根目录")
    slim.add_argument("--project-slug", default=None, help="缺省＝注册表 caliber.projectSlug")
    slim.add_argument("--sample", type=int, default=None, help="缺省＝注册表 caliber.sample（0=全量）")
    slim.add_argument("--since", default="", help="缺省＝注册表 caliber.since")
    slim.add_argument("--until", default="", help="缺省＝注册表 caliber.until")
    slim.add_argument("--max-age-hours", type=float, default=4.0, help="候选卡巡检里「改动未提交」的阈值")
    slim.add_argument("--write", action="store_true",
                      help=f"落 slimAdvice.output.file（默认只打印；派生物，不入库）")
    slim.set_defaults(handler=cmd_slim)

    audit = sub.add_parser("audit")
    audit.add_argument("--write", action="store_true", help="persist findings as problem cards")
    audit.add_argument("--max-age-hours", type=float, default=4.0)
    audit.set_defaults(handler=cmd_audit)

    cand = sub.add_parser("candidates")
    cand.add_argument("--write", action="store_true",
                      help="落候选卡到注册表声明的派生区（candidates.outputDir）；绝不写 issue/")
    cand.add_argument("--max-age-hours", type=float, default=4.0, help="git 轨「改动未提交」的超龄阈值")
    cand.add_argument("--preview", type=int, default=10, help="打印前 N 张候选卡的指针摘要")
    cand.set_defaults(handler=cmd_candidates)

    rec = sub.add_parser("recurrence")
    rec.add_argument("--write", action="store_true",
                     help="落派生报告到注册表声明的 report.outputFile（默认只打印；不写 issue/、不建卡）")
    rec.set_defaults(handler=cmd_recurrence)

    feed = sub.add_parser("feedback",
                          help="反哺有效率（智能化第三条）：反哺记录×显式复发链，取不到一律 N/A，不造数")
    feed.add_argument("--write", action="store_true",
                      help="落派生报告到 feedbackRate.report.outputFile（默认只打印）")
    feed.set_defaults(handler=cmd_feedback)

    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (ValueError, OSError) as exc:
        # never claim a write happened when it did not
        print(f"tsr: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
