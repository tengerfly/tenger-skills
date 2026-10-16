"""tsr — the only runtime entry point the skills touch for observability.

Contract: the caller passes semantics (node, skill, role, gate, round, refs) and this
tool stamps time, assigns the sequence number and hashes artifacts. A hand-written
timestamp or digest is therefore not expressible through this CLI, which is the point —
ledger fields must be falsifiable against the machine and the disk.
"""
from __future__ import annotations
import argparse, json, sys
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


def verify(root: Path) -> list:
    """Re-derive facts from disk and the log itself; trust nothing the caller asserted."""
    errors = []
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
            for artifact in event.get("artifacts") or []:
                path = root / str(artifact.get("path", "")).replace("\\", "/")
                if not path.is_file():
                    errors.append(f"{where}: artifact vanished: {artifact.get('path')}")
                    continue
                fresh = schema.digest(path)
                if fresh["sha256"] != artifact.get("sha256"):
                    errors.append(f"{where}: artifact edited after node-end: {artifact.get('path')}")
            if event.get("gate") == "PASS" and event.get("allowDownstream"):
                closed = [u["artifact"] for u in event.get("upstream") or [] if u.get("gate") != "PASS"]
                if closed:
                    errors.append(f"{where}: PASS with allowDownstream while upstream is closed: {closed}")
    return errors


def cmd_verify(args) -> int:
    errors = verify(_project(args))
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"run-log verification failed: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("run-log verification passed")
    return 0


def cmd_report(args) -> int:
    root = _project(args)
    problems = verify(root)
    events = schema.read_events(root)
    registered = metrics.load_registry()
    node_errors = sorted({str(event.get("node")) for event in events
                          if event.get("node") not in registered})
    text = metrics.render(metrics.summarize(events), node_errors, problems)
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
    report = rules.measure(root, spec, spans, skills=args.skill)
    text = rules.render(report)
    print(text)
    if args.write:
        target = root / ".spec/观测/规则命中率.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        print(f"规则命中率 → {target.relative_to(root).as_posix()}")
    # N/A 是诚实降级，不是命令失败：拔掉适配器只让指标少一维，不该把观测链路判红
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
    from obs import anomaly, gitlog
    root = _project(args)
    events = schema.read_events(root)
    opened, closed = {}, set()
    for event in events:
        key = (event.get("executionId"), event.get("node"))
        if event["event"] == "node-start":
            opened[key] = event.get("ts")
        elif event["event"] == "node-end":
            closed.add(key)
    unclosed = {key: ts for key, ts in opened.items() if key not in closed}
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
    rules.add_argument("--write", action="store_true", help="落 .spec/观测/规则命中率.md（默认只打印）")
    rules.set_defaults(handler=cmd_rules)

    audit = sub.add_parser("audit")
    audit.add_argument("--write", action="store_true", help="persist findings as problem cards")
    audit.add_argument("--max-age-hours", type=float, default=4.0)
    audit.set_defaults(handler=cmd_audit)

    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (ValueError, OSError) as exc:
        # never claim a write happened when it did not
        print(f"tsr: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
