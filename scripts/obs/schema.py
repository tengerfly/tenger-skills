"""tenger.trace/v1 — portable run-log contract for the skill system.

The run log, not any host's telemetry, is the source of truth: hosts rotate their
logs, differ in field naming, and cannot be relied on to outlive a session. Everything
factual (timestamp, sequence number, artifact digests) is generated here by the script,
so a drifting hand-written ledger cannot masquerade as evidence; the caller only supplies
semantics (which node, which gate, which round).
"""
from __future__ import annotations
import hashlib, json, os, re
from datetime import datetime
from pathlib import Path

SCHEMA = "tenger.trace/v1"
RUN_LOG = ".spec/obs/run.jsonl"
EVENTS = {"node-start", "node-end", "decision", "sink", "verify"}
ROLES = {"produce", "fix", "review", "recheck"}
GATES = {"PASS", "CONDITIONAL", "BLOCKED"}
ACTORS = {"main", "subagent", "cron", "eval-judge"}
REVIEW_ROLES = {"review", "recheck"}
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")


def now() -> str:
    """Machine clock, local timezone, millisecond precision — never hand-authored."""
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def digest(path: Path) -> dict:
    data = path.read_bytes()
    return {"path": path.as_posix(), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def run_log(root: Path) -> Path:
    return root / RUN_LOG


def read_events(root: Path) -> list:
    log = run_log(root)
    if not log.is_file():
        return []
    events = []
    for line_no, line in enumerate(log.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{RUN_LOG}:{line_no} is not valid JSON: {exc}") from exc
    return events


def append_event(root: Path, event: dict) -> dict:
    """Validate then durably append one event; a rejected event leaves the log untouched."""
    errors = validate(event)
    if errors:
        raise ValueError("event rejected: " + "; ".join(errors))
    log = run_log(root)
    log.parent.mkdir(parents=True, exist_ok=True)
    event = dict(event)
    event["seq"] = len(read_events(root)) + 1
    event.setdefault("ts", now())
    event.setdefault("schema", SCHEMA)
    with log.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return event


def validate(event: dict) -> list:
    errors = []
    if event.get("schema") not in (None, SCHEMA):
        errors.append(f"unsupported schema: {event.get('schema')}")
    if event.get("event") not in EVENTS:
        errors.append(f"unknown event type: {event.get('event')}")
    for field in ("project", "executionId", "node", "skill"):
        value = event.get(field)
        if not isinstance(value, str) or not ID.match(value):
            errors.append(f"{field} must be a non-empty identifier, got {value!r}")
    if event.get("role") not in ROLES:
        errors.append(f"role must be one of {sorted(ROLES)}")
    if event.get("actor") not in ACTORS:
        errors.append(f"actor must be one of {sorted(ACTORS)}")
    if event.get("origin") not in {"self", "adapter", "recomputed"}:
        errors.append("origin must be self/adapter/recomputed")
    if event.get("actor") == "subagent" and not event.get("parentExecution"):
        errors.append("subagent events must carry parentExecution or they pollute the main-chain metrics")
    if event["event"] == "node-end":
        if event.get("gate") not in GATES:
            errors.append(f"node-end gate must be one of {sorted(GATES)}")
        if not isinstance(event.get("allowDownstream"), bool):
            errors.append("node-end allowDownstream must be boolean")
    if event.get("role") in REVIEW_ROLES:
        for field in ("round", "batch"):
            if not isinstance(event.get(field), int) or event[field] < 1:
                errors.append(f"{event.get('role')} events require positive int {field} (rework rate depends on it)")
    if event.get("state") is not None and not re.match(r"^[A-Z][A-Z0-9_]*$", str(event["state"])):
        errors.append(f"state must be a registered UPPER_SNAKE value: {event.get('state')}")
    for artifact in event.get("artifacts") or []:
        if not all(key in artifact for key in ("path", "sha256", "bytes")):
            errors.append(f"artifact binding incomplete: {artifact}")
    for upstream in event.get("upstream") or []:
        if upstream.get("gate") not in GATES or not upstream.get("artifact"):
            errors.append(f"upstream entry needs artifact and a legal gate: {upstream}")
    return errors
