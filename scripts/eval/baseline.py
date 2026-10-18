"""Baseline snapshots and diffs — under anchors that refuse to be compared across.

governance/eval-spec.yaml `comparability` binds every eval result to
`skillRevision / casesVersion / engine / model / judgeVersion / scoringVersion` and states
"锚任一项变化即开新基线；禁止跨锚比总分". That sentence had no executor either: there was no
snapshot file, no `save`, no `diff`, so any two runs could be quietly compared and any drift in
the yardstick could be quietly ignored. This file is the executor.

Anchors are *derived from the repo*, not typed by hand — a self-declared anchor is just another
claim to trust. Each one is a mechanical digest of the thing it names:

- `skillRevision`  the bytes of the skill under test (`governance/skill-registry.yaml` resolves
  `skill:` → its directory) plus `shared/`. Deliberately NOT the commit sha: a commit sha changes
  on every docs edit, which would make `diff` refuse almost always and the tool unusable — while
  the day someone edits SKILL.md, the thing measured really did change and a new baseline is due.
- `casesVersion`   the case declarations (everything except `name`) plus the fixture tree bytes.
  Renaming a title is not a new yardstick; changing an expectation, a tamper, an `issueRef` or a
  fixture file is.
- `engine`/`model` declared engines of the behaviour cases ("structure-only"/"engine-default" when
  the set has none) — switching engine or provider is switching anchors, not switching machines.
- `judgeVersion`   bump by hand when run.py's *semantics* change (how red/green/mustContain are
  decided). run.py's bytes are recorded alongside as provenance and a changed digest without a
  bumped version is reported as a warning — the judge implementation moved, so go confirm the
  semantics did not. validate_core.py is deliberately left out of it: the checkers are what the
  structure cases measure, so their movement must show up as a delta, not as a broken anchor.
- `scoringVersion` read from governance/scoring.yaml `version`, so re-weighting invalidates.

`evals/<set>/baseline/result.json` is committed truth; the diff report is derived and lands in
`.spec/obs/` (gitignored) like every other derived artifact.

Exit codes: 0 无回退 ｜ 1 有回退，或基线不干净不能 save ｜ 2 拒绝比较（锚不一致、无基线、集读不动）。
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_core as core

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "tenger.eval-baseline/v1"
JUDGE_VERSION = "eval-judge/2"
ANCHOR_NAMES = ("skillRevision", "casesVersion", "engine", "model", "judgeVersion", "scoringVersion")
# 参与锚定的字段：判据、输入、预算、引用全算；只有 name 不算（改标题不等于换尺子）
CASE_FIELDS = ("id", "layer", "given", "tamper", "expect", "engine", "model",
               "tokenBudget", "timeout", "prompt", "skillFiles", "issueRef", "answerFile")
STATUS_RANK = {"passed": 0, "blocked": 0, "failed": 1, "error": 2}
DERIVED = ROOT / ".spec/obs/eval-baseline-diff.json"
OK, REGRESSED, REFUSED = 0, 1, 2


def _tree(base: Path) -> list:
    """目录或单文件 → 有序 (路径, 字节)；不存在就是空表，由调用方决定怎么报。"""
    base = Path(base)
    if base.is_file():
        return [(_rel(base), base.read_bytes())]
    if not base.is_dir():
        return []
    return [(_rel(path), path.read_bytes()) for path in sorted(base.rglob("*")) if path.is_file()]


def _digest(rows: list) -> str:
    hasher = hashlib.sha256()
    for name, blob in rows:
        hasher.update(name.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(blob)
        hasher.update(b"\0")
    return "sha256:" + hasher.hexdigest()


def skill_sources(skill_id) -> list:
    """被测 skill 的正文目录（注册表解析）+ 跨 skill 契约 shared/。"""
    registry = core.load_yaml(ROOT / "governance/skill-registry.yaml") or {}
    path = next((entry.get("path") for entry in registry.get("skills") or [] if entry.get("id") == skill_id), None)
    if not path:
        raise ValueError(f"skill {skill_id!r} 未在 governance/skill-registry.yaml 登记 ⇒ skillRevision 锚无法核")
    dirs = [ROOT / str(path), ROOT / "shared"]
    rows = [row for directory in dirs for row in _tree(directory)]
    if not rows:
        raise ValueError(f"skill 正文目录为空，无法核出 skillRevision 锚: {dirs}")
    return rows


def anchors_for(eval_path: Path, spec: dict) -> dict:
    cases = sorted(spec.get("cases") or [], key=lambda item: str(item.get("id")))
    projection = [{key: case[key] for key in CASE_FIELDS if key in case} for case in cases]
    rows = [("caseDeclarations", json.dumps(projection, sort_keys=True, ensure_ascii=False).encode("utf-8"))]
    for case in cases:
        given = str(case.get("given") or "").replace("\\", "/")
        if given:
            fixture = ROOT / given
            if not fixture.exists():
                raise ValueError(f"{_rel(eval_path)}/{case.get('id')}: 夹具不存在，无法核出 casesVersion 锚: {given}")
            rows += _tree(fixture)
    behaviour = [case for case in cases if case.get("layer") == "behaviour"]
    engines = sorted({str(case.get("engine") or spec.get("engine")) for case in behaviour if (case.get("engine") or spec.get("engine"))})
    models = sorted({str(case.get("model") or spec.get("model")) for case in behaviour if (case.get("model") or spec.get("model"))})
    scoring = core.load_yaml(ROOT / "governance/scoring.yaml") or {}
    return {"skillRevision": _digest(skill_sources(spec.get("skill"))),
            "casesVersion": _digest(rows),
            "engine": "+".join(engines) or "structure-only",
            "model": "+".join(models) or "engine-default",
            "judgeVersion": JUDGE_VERSION,
            "scoringVersion": str(scoring.get("version"))}


def _rel(path: Path) -> str:
    """仓库相对路径优先；仓库外的探针（单测夹具）退回绝对路径，别让一条路径报错拖垮整次比对。"""
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def baseline_path(eval_path: Path) -> Path:
    return Path(eval_path).resolve().parent / "baseline" / "result.json"


def snapshot(eval_path: Path) -> dict:
    """跑一遍真实执行器取结论（结构层零成本；行为层在未授权时记 blocked，不花 token）。"""
    from eval import run as evaluator
    eval_path = Path(eval_path).resolve()
    spec = evaluator.load_eval(eval_path)
    report = evaluator.run_all(eval_path)
    layers = {case.get("id"): case.get("layer") for case in spec.get("cases") or []}
    return {"schema": SCHEMA, "eval": _rel(eval_path), "skill": spec.get("skill"),
            "savedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
            "anchors": anchors_for(eval_path, spec),
            "provenance": {"runner": _digest(_tree(ROOT / "scripts/eval/run.py")),
                           "python": sys.version.split()[0]},
            "counts": report["counts"],
            "cases": [{"id": item["id"], "layer": layers.get(item["id"], "structure"), "status": item["status"],
                       "outcome": item.get("outcome")} for item in report["results"]]}


def save(eval_path: Path) -> dict:
    snap = snapshot(eval_path)
    counts = snap["counts"]
    if counts["failed"] or counts["error"]:
        raise ValueError(f"{snap['eval']}：这套现在不干净（败 {counts['failed']} ｜ 错 {counts['error']}）。"
                         "基线只能锚在一次通过的快照上（eval-spec comparability.baseline），先修再 save")
    target = baseline_path(eval_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"path": target, "snapshot": snap}


def load(path: Path) -> dict:
    if not Path(path).is_file():
        raise ValueError(f"无基线可比较: {_rel(Path(path))}（先 `baseline.py save`，基线文件要入库）")
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ValueError(f"基线文件不是合法 JSON，不能用它当锚: {path}: {exc}") from exc
    if data.get("schema") != SCHEMA:
        raise ValueError(f"基线 schema 不是 {SCHEMA}: {path}（旧格式一律重新 save）")
    return data


def statement(snap: dict) -> list:
    """口径声明：比的是什么、在什么口径下比、不比什么。缺了它，diff 就是一个可以被任意解读的数。"""
    anchors = snap.get("anchors") or {}
    lines = ["", "口径声明：",
             "- 只有六个锚全一致才可比；任一项不同 ⇒ 开新基线（`save` 后入库），禁止跨锚比总分——"
             "尺子和被测物同时动，差值说明不了任何事（governance/eval-spec.yaml comparability.rule）。",
             f"- 本次锚值：" + "、".join(f"{name}={str(anchors.get(name))[:18]}" for name in ANCHOR_NAMES)
             + "（锚是从仓库字节算出来的，不是手填的）。",
             "- 比的是逐条判定结论（passed/blocked/failed/error）与过/败/错/待引擎计数；"
               "总分用于看趋势，不是放行依据，红线仍由 validate_core 判。",
             "- 行为层用例在零成本快照里一律记 blocked（未设 TSR_ALLOW_ENGINE，本命令不跑引擎、不产生任何 token 花费）；"
               "换引擎或换模型＝换锚，不许拿不同引擎的结果互比。",
             "- 基线文件 evals/<set>/baseline/result.json 是入库真相；本 diff 报告是派生物，写 .spec/obs/（gitignore）。"]
    blocked = sum(1 for case in snap.get("cases", []) if case.get("status") == "blocked")
    if blocked:
        lines.append(f"- 注意：本快照含 {blocked} 条未跑的行为层用例，基线只证明结构层，不证明行为。")
    return lines


def compare(base: dict, cur: dict) -> dict:
    """先验锚，锚不过就一个差值都不给——「顺手比一下」正是历史上把结论跑废的那一步。"""
    mismatch = {}
    for name in ANCHOR_NAMES:
        want, now = (base.get("anchors") or {}).get(name), (cur.get("anchors") or {}).get(name)
        if want is None or now is None or str(want) != str(now):
            mismatch[name] = {"baseline": want, "current": now}
    warned = []
    if str((base.get("provenance") or {}).get("runner")) != str((cur.get("provenance") or {}).get("runner")):
        warned.append("scripts/eval/run.py 的字节变了而 judgeVersion 未升 —— 去确认判据语义是否真没变；"
                      "变了语义必须升 judgeVersion，否则这条基线就是拿新旧两把尺子在比")
    if mismatch:
        return {"eval": cur.get("eval"), "comparable": False, "mismatch": mismatch,
                "deltas": [], "regressions": [], "warnings": warned,
                "statement": statement(cur), "baseline": base, "current": cur}
    before = {case["id"]: case for case in base.get("cases") or []}
    now = {case["id"]: case for case in cur.get("cases") or []}
    deltas = []
    for case_id in sorted(set(before) | set(now)):
        was, is_now = before.get(case_id), now.get(case_id)
        if was is None or is_now is None:
            deltas.append({"id": case_id, "from": (was or {}).get("status", "—"),
                           "to": (is_now or {}).get("status", "—"), "note": "用例集与基线不一致"})
        elif was.get("status") != is_now.get("status"):
            deltas.append({"id": case_id, "from": was.get("status"), "to": is_now.get("status"), "note": ""})
    regressions = [item for item in deltas
                   if STATUS_RANK.get(str(item["to"]), 2) > STATUS_RANK.get(str(item["from"]), 0)]
    counts = {name: {"baseline": (base.get("counts") or {}).get(name), "current": (cur.get("counts") or {}).get(name)}
              for name in ("passed", "failed", "blocked", "error")}
    return {"eval": cur.get("eval"), "comparable": True, "mismatch": {}, "deltas": deltas,
            "regressions": regressions, "counts": counts, "warnings": warned,
            "statement": statement(cur), "baseline": base, "current": cur}


def diff(eval_path: Path) -> dict:
    eval_path = Path(eval_path).resolve()
    return compare(load(baseline_path(eval_path)), snapshot(eval_path))


def render(item: dict) -> str:
    lines = [f"## {item.get('eval') or ''}"]
    base, cur = item.get("baseline") or {}, item.get("current") or {}
    lines.append(f"- 基线快照 {base.get('savedAt', '?')} → 本次 {cur.get('savedAt', '?')}")
    if not item["comparable"]:
        lines.append(f"- ⛔ **拒绝比较**：{len(item['mismatch'])} 个锚不一致，跨锚的差值不是回归结论")
        for name, pair in sorted(item["mismatch"].items()):
            lines.append(f"  - `{name}`：基线 {str(pair['baseline'])[:64]} → 现在 {str(pair['current'])[:64]}")
        lines.append("- 处置：改动是被批准的 ⇒ `baseline.py save` 开新基线并入库；改动是意外 ⇒ 先回退改动。"
                     "两条路都不允许「先比一下看看」。")
    else:
        counts = item["counts"]
        lines.append("- 计数：" + " ｜ ".join(
            f"{name} {value['baseline']}→{value['current']}" + ("（变）" if value['baseline'] != value['current'] else "")
            for name, value in counts.items()))
        if item["deltas"]:
            lines.append(f"- 逐条差异 {len(item['deltas'])} 条（回退 {len(item['regressions'])} 条）：")
            lines += [f"  - {row['id']}：{row['from']} → {row['to']}"
                      + ("⛔ 回退" if row in item["regressions"] else "↗ 好转" if STATUS_RANK.get(str(row['to']), 2)
                         < STATUS_RANK.get(str(row['from']), 0) else "")
                      + (f"（{row['note']}）" if row["note"] else "") for row in item["deltas"]]
        else:
            lines.append("- 逐条差异：无（同一锚下判定结论与基线完全一致）")
    for warning in item.get("warnings") or []:
        lines.append(f"- ⚠ {warning}")
    lines += item["statement"]
    return "\n".join(lines)


def resolve_sets(args: list) -> list:
    if not args:
        return sorted(ROOT.glob("evals/*/eval.yaml"))
    sets = []
    for arg in args:
        candidate = Path(arg)
        if candidate.suffix in {".yaml", ".yml"}:
            resolved = (candidate if candidate.is_absolute() else ROOT / candidate)
        else:
            resolved = ROOT / "evals" / arg / "eval.yaml"
        resolved = resolved.resolve()
        if not resolved.is_file():
            raise ValueError(f"找不到评测集: {arg}（给套名，或给 evals/<set>/eval.yaml 路径）")
        sets.append(resolved)
    return sets


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        # Windows 控制台默认 GBK：口径声明整段是中文，乱码的口径声明等于没有口径声明
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="baseline", description="评测基线：save 存快照，diff 同锚比对")
    parser.add_argument("action", choices=["save", "diff"])
    parser.add_argument("sets", nargs="*", help="评测套名或 eval.yaml 路径；缺省＝全部")
    args = parser.parse_args(argv)
    try:
        targets = resolve_sets(args.sets)
    except ValueError as exc:
        print(f"baseline: {exc}", file=sys.stderr)
        return REFUSED
    reports, code = [], OK
    for target in targets:
        try:
            if args.action == "save":
                result = save(target)
                snap = result["snapshot"]
                print(f"✅ 基线入库 → {_rel(result['path'])}")
                print("   " + "、".join(f"{name}={str(snap['anchors'][name])[:18]}" for name in ANCHOR_NAMES))
                continue
            item = diff(target)
            print(render(item))
            reports.append({"eval": item.get("eval"), "comparable": item["comparable"],
                            "mismatch": item.get("mismatch"), "deltas": item.get("deltas"),
                            "regressions": item.get("regressions"), "statement": item["statement"]})
            if not item["comparable"]:
                code = max(code, REFUSED)
            elif item["regressions"]:
                code = max(code, REGRESSED)
        except ValueError as exc:
            print(f"💥 {target}: {exc}", file=sys.stderr)
            code = max(code, REFUSED)
    if reports:
        DERIVED.parent.mkdir(parents=True, exist_ok=True)
        DERIVED.write_text(json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\n派生报告（不入库）→ {DERIVED.relative_to(ROOT).as_posix()}")
    if args.action == "diff":
        print(f"结论：{'有回退' if code == REGRESSED else ('拒绝比较（锚不一致或无基线）' if code == REFUSED else '同一锚下无回退')}")
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
