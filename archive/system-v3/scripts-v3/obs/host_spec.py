"""Spec-driven host enrichment.

The adapter engine knows nothing about any host: every path, field name and capability
lives in `governance/host-specs/<host>.yaml`, which the host effectively "declares".
Adding zcode or codex means adding a spec file, not touching this module or the metrics.
A capability is granted only when the fields it requires are actually observed in the
host's own events — declaring it in YAML is not evidence, and a silent zero is worse
than an honest N/A because it reads like a measurement.
"""
from __future__ import annotations
import fnmatch, json, re
from pathlib import Path

import yaml

from obs import metrics

SPECS = Path(__file__).resolve().parents[2] / "governance/host-specs"


def available() -> list:
    return sorted(path.stem for path in SPECS.glob("*.yaml"))


def load(host: str) -> dict:
    path = SPECS / f"{host}.yaml"
    if not path.is_file():
        raise ValueError(f"no host spec for {host!r}; available: {available() or 'none'}")
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    for key in ("discovery", "fields", "kinds", "capabilities"):
        if not spec.get(key):
            raise ValueError(f"host spec {host} is missing '{key}'")
    return spec


def _dig(event: dict, dotted: str):
    cursor = event
    for part in str(dotted).split("."):
        if not isinstance(cursor, dict):
            return None
        cursor = cursor.get(part)
    return cursor


def discover(spec: dict, home: Path, project_slug: str) -> list:
    """Return [(session_id, path)]; the session key comes from the path, not the payload."""
    files = sorted(home.glob(spec["discovery"]["layout"]))
    session_re = re.compile(spec["discovery"]["sessionKey"]["pattern"])
    found = []
    for path in files:
        posix = path.as_posix()
        if project_slug and project_slug not in posix:
            continue
        match = session_re.search(posix)
        if match and "session" in session_re.groupindex:
            session = match.group("session")
        elif match:
            session = match.group(1)
        else:
            session = path.parent.name
        found.append((session, path))
    return found


def read_spans(spec: dict, paths: list) -> list:
    ts_field, kind_field = spec["fields"]["timestamp"], spec["fields"]["kind"]
    tool_field = spec["fields"].get("tool")
    args_field = spec["fields"].get("arguments")
    spans = []
    for session, path in paths:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            spans.append({
                "session": session,
                "ts": event.get(ts_field),
                "kind": event.get(kind_field),
                "tool": _dig(event, tool_field) if tool_field else None,
                "path": _dig(event, args_field + ".file_path") if args_field else None,
                "loop": event.get(spec["fields"].get("loop", "loop_id")),
                "raw": event,
            })
    return spans


def _field_present(spans: list, dotted: str) -> bool:
    for span in spans:
        value = _dig(span["raw"], dotted)
        if value is not None:
            return True
    return False


def verify_capabilities(spec: dict, spans: list) -> dict:
    """Grant a capability only on observed fields; otherwise report the reason, never a zero."""
    report = {}
    for cap in spec.get("capabilities") or []:
        requires = cap.get("requires") or {}
        missing = [field for field in requires.get("fields", []) if not _field_present(spans, field)]
        matching = [span for span in spans
                    if not requires.get("types") or span["kind"] in requires["types"]]
        absent_types = [kind for kind in requires.get("types", [])
                        if not any(span["kind"] == kind for span in spans)]
        if missing or absent_types:
            report[cap["id"]] = {"granted": False,
                                 "reason": f"字段实测缺失: {', '.join(missing + absent_types)}（声明不等于提供）"}
            continue
        reason = cap.get("caveat", "")
        count_field = cap.get("countField")
        if count_field and matching:
            covered = sum(1 for span in matching if _dig(span["raw"], count_field) is not None)
            if covered == 0:
                report[cap["id"]] = {"granted": False,
                                     "reason": f"{count_field} 在 {len(matching)} 条同类事件里一次都没出现"}
                continue
            if covered < len(matching):
                reason = (f"{reason}；{count_field} 覆盖率 {covered}/{len(matching)}，"
                          f"计数口径只能算在带该字段的事件上").strip("；")
        report[cap["id"]] = {"granted": True, "reason": reason}
    for cap in spec.get("absent") or []:
        report[cap["id"]] = {"granted": False, "reason": cap.get("reason", "宿主不提供")}
    return report


def capability(spec: dict, cap_id: str) -> dict:
    """One capability's declaration, field names and all — they live in the spec, never here."""
    for cap in spec.get("capabilities") or []:
        if cap.get("id") == cap_id:
            return cap
    return {}


def _text(value) -> str:
    """Flatten every string an argument tree carries. In-memory only: nothing here is persisted."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "\n".join(_text(item) for item in value.values())
    if isinstance(value, list):
        return "\n".join(_text(item) for item in value)
    return ""


def cap_records(spec: dict, spans: list, cap_id: str) -> list:
    """Project raw spans onto the fields a capability declares, so metrics stay host-free.

    Callers must gate this on verify_capabilities: an ungranted capability means the field was
    never observed, and reading it anyway would turn "not measured" into an empty measurement.
    """
    cap = capability(spec, cap_id)
    if not cap:
        return []
    tools = {str(name) for name in cap.get("toolFilter") or []}
    kinds = {str(kind) for kind in cap.get("eventKinds") or []}
    path_field, args_field = cap.get("pathField"), cap.get("argsField")
    ranges = cap.get("rangeFields") or {}
    records = []
    for span in spans:
        if kinds and span["kind"] not in kinds:
            continue
        if tools and span["tool"] not in tools:
            continue
        raw = span["raw"]
        records.append({
            "session": span["session"], "ts": span["ts"], "tool": span["tool"],
            "path": _dig(raw, path_field) if path_field else None,
            "offset": _dig(raw, ranges["offset"]) if ranges.get("offset") else None,
            "limit": _dig(raw, ranges["limit"]) if ranges.get("limit") else None,
            "text": _text(_dig(raw, args_field)) if args_field else "",
        })
    return records


def attribute(spans: list, project_root: Path) -> dict:
    """Map host write events onto registered nodes by artifact location (primary signal)."""
    registry = metrics.load_registry()
    hits, unattributed = {}, 0
    writes = [span for span in spans if span.get("path") and _is_write(span)]
    for span in writes:
        relative = _relative(span["path"], project_root)
        if relative is None:
            unattributed += 1          # written outside this project: not ours to guess about
            continue
        node = metrics.attribute_write(registry, relative)
        if node is None:
            unattributed += 1
            continue
        hits[node] = hits.get(node, 0) + 1
    return {"writes": len(writes), "byNode": hits, "unattributed": unattributed}


def _is_write(span) -> bool:
    return span.get("tool") in {"Write", "Edit", "write", "edit"}


def _relative(path: str, project_root: Path):
    portable = str(path).replace("\\", "/")
    root = project_root.as_posix().rstrip("/") + "/"
    if portable.lower().startswith(root.lower()):
        return portable[len(root):]
    return None
