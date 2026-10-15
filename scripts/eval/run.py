"""Structure-layer eval runner: deterministic, zero-cost, no agent, no host.

Two layers exist because only one of them is free. The structure layer feeds a fixture
project through the real validators and asserts which findings fire; it costs seconds and
can therefore run on every change. The behaviour layer must execute a skill inside an agent
engine, which needs an installed engine, provider credentials and spend, so cases declare
`layer: behaviour` and are reported as "not runnable here" instead of silently skipped.

Cases assert on findings, not on exit codes alone, so a checker that fails for an unrelated
reason cannot be mistaken for a passing regression.
"""
from __future__ import annotations
import json, re, shutil, subprocess, sys, tempfile
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_core as core

ROOT = Path(__file__).resolve().parents[2]
CHECKS = {"artifact": core.check_artifact, "gate": core.check_gate, "trace": core.check_trace,
          "registry": core.check_registry, "refs": core.check_refs}


def findings_for(project: Path, validator: str) -> list:
    """Validators return error strings; the section judge returns its own finding list."""
    if validator == "sections":
        from obs import score
        return score.d1_contract(project).get("failures", [])
    if validator not in CHECKS:
        raise ValueError(f"unknown validator: {validator}")
    return CHECKS[validator](project)
    return CHECKS[validator](project)


def load_eval(path: Path) -> dict:
    try:
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: 评测集不是合法 YAML（eval.yaml 是数据文件，不能混入 markdown 块语法）: {exc}") from exc
    if spec.get("schema") != "tenger.eval/v1":
        raise ValueError(f"{path}: unsupported eval schema {spec.get('schema')!r}")
    for case in spec.get("cases") or []:
        if case.get("layer") not in {"structure", "behaviour"}:
            raise ValueError(f"{path}/{case.get('id')}: layer must be structure or behaviour")
        if case.get("layer") == "behaviour":
            if not case.get("prompt"):
                raise ValueError(f"{path}/{case.get('id')}: behaviour 用例必须有 prompt")
            if not case.get("tokenBudget"):
                raise ValueError(f"{path}/{case.get('id')}: behaviour 用例必须声明 tokenBudget（跑一次要知道代价）")
            if not (case.get("expect") or {}).get("mustNotContain") and not (case.get("expect") or {}).get("produces"):
                raise ValueError(f"{path}/{case.get('id')}: behaviour 用例要有可判据（produces 或 mustNotContain），否则只是跑了个寂寞")
    return spec


def _apply_tamper(project: Path, tamper: dict) -> None:
    target = project / str(tamper["file"]).replace("\\", "/")
    if not target.is_file():
        raise ValueError(f"tamper target missing: {tamper['file']}")
    if "append" in tamper:
        with target.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(tamper["append"] if tamper["append"].startswith("\n") else "\n" + tamper["append"])
    elif "replace" in tamper:
        text = target.read_text(encoding="utf-8")
        pair = tamper["replace"]
        if pair["from"] not in text:
            raise ValueError(f"tamper 'from' not found in {tamper['file']}: {pair['from'][:40]}")
        target.write_text(text.replace(pair["from"], pair["to"]), encoding="utf-8")
    else:
        raise ValueError("tamper needs append or replace")


def _section_of(text: str, heading_pattern: str) -> str:
    """Body under the first matching heading, up to the next heading.

    Whole-output ban-word matching yields false positives: an agent that writes
    "技术决策全部留到 Tech Design，现在我不问" is compliant yet contains every banned word.
    Scoping the ban to the section the rule governs is the mechanically sound form.
    """
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if start is None and re.match(rf"^#{{1,6}}\s*.*({heading_pattern})", line.strip(), re.I):
            start = index + 1
        elif start is not None and line.strip().startswith("#"):
            return "\n".join(lines[start:index])
    return "\n".join(lines[start:]) if start is not None else ""


def _section_body(text: str, pattern: str):
    """Return the body under the heading matching `pattern`, or None when the heading is absent.

    A ban-word match over the whole answer is not evidence of a rule violation: a compliant
    agent may write "技术决策留到 Tech Design，现在我不问" and still contain every banned word.
    Scoping to the section the rule governs is the only mechanically sound form.
    """
    lines = text.splitlines()
    heading = re.compile(rf"^\s*(?:#{{1,4}}\s*|\*\*)\s*.*{pattern}", re.I)
    next_heading = re.compile(r"^\s*(?:#{1,4}\s*|\*\*)\s*\S", re.I)
    start = None
    for index, line in enumerate(lines):
        if start is None and heading.search(line):
            start = index + 1
        elif start is not None and index > start and next_heading.search(line) and line.strip() != "":
            return "\n".join(lines[start:index])
    return "\n".join(lines[start:]) if start is not None else None


def run_behaviour(case: dict, spec: dict) -> dict:
    from eval import engine as agent_engine
    chosen = case.get("engine") or spec.get("engine") or "codex"
    if chosen not in agent_engine.available():
        return {"id": case["id"], "status": "blocked",
                "reason": f"引擎 {chosen!r} 本机不可用（可用: {agent_engine.available()}）"}
    fixture = ROOT / str(case["given"]).replace("\\", "/")
    if not fixture.is_dir():
        return {"id": case["id"], "status": "error", "reason": f"夹具不存在: {case['given']}"}
    workspace = Path(tempfile.mkdtemp(prefix="behav-"))
    try:
        project = workspace / "project"
        agent_engine.materialise(fixture, project, case.get("skillFiles") or [], ROOT)
        ran = agent_engine.run(chosen, project, case["prompt"], timeout=case.get("timeout", 240))
        if ran.get("blocked"):
            return {"id": case["id"], "status": "blocked", "reason": ran["reason"]}
        if not ran["ok"]:
            return {"id": case["id"], "status": "failed", "reason": ran["reason"], "tokens": ran.get("tokens")}
        budget = case.get("tokenBudget")
        tokens = ran.get("tokens")
        if budget and tokens and tokens > budget:
            return {"id": case["id"], "status": "failed", "tokens": tokens,
                    "reason": f"超预算：{tokens} > {budget}（行为层必须带预算闸，否则跑一次不知道烧了多少）"}
        for pattern in case.get("expect", {}).get("produces") or []:
            if not list(project.glob(pattern)):
                return {"id": case["id"], "status": "failed", "tokens": tokens,
                        "reason": f"未产出约定文件: {pattern}"}
        judged = ran["output"] + "\n" + "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for pattern in case.get("expect", {}).get("produces") or []
            for path in project.glob(pattern))
        banned = case.get("expect", {}).get("mustNotContain")
        if banned:
            scope_name = case["expect"].get("banInSection")
            scope = _section_body(judged, scope_name) if scope_name else judged
            if scope is None:
                return {"id": case["id"], "status": "error", "tokens": tokens,
                        "reason": f"找不到分节 /{scope_name}/，判据无法成立（不许退化成全文匹配）"}
            hit = re.search(banned, scope, re.S | re.I)
            if hit:
                note = "（已改分节匹配，避免把「留到后面再定」判成违规）" if scope_name else "（全文匹配）"
                return {"id": case["id"], "status": "failed", "tokens": tokens,
                        "reason": f"「{scope_name}」节内出现禁止内容 /{banned}/ {note}",
                        "peek": scope[max(0, hit.start() - 120):hit.end() + 160]}
        return {"id": case["id"], "status": "passed", "tokens": tokens, "reason": f"引擎 {chosen}"}
    except (ValueError, OSError) as exc:
        return {"id": case["id"], "status": "error", "reason": f"{type(exc).__name__}: {exc}"}
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def run_case(case: dict, spec: dict | None = None) -> dict:
    if case["layer"] == "behaviour":
        return run_behaviour(case, spec or {})
    fixture = ROOT / str(case["given"]).replace("\\", "/")
    if not fixture.is_dir():
        return {"id": case["id"], "status": "error", "reason": f"夹具不存在: {case['given']}"}
    workspace = Path(tempfile.mkdtemp(prefix="eval-"))
    try:
        project = workspace / fixture.name
        shutil.copytree(fixture, project)
        if case.get("tamper"):
            _apply_tamper(project, case["tamper"])
        errors = findings_for(project, case["expect"]["validator"])
        expect = case["expect"]
        matched = [error for error in errors if expect["mustContain"] in error] if expect.get("mustContain") else errors
        outcome = "red" if errors else "green"
        passed = outcome == expect["outcome"] and (len(matched) > 0 if expect.get("mustContain") else True)
        return {"id": case["id"], "status": "passed" if passed else "failed", "outcome": outcome,
                "findings": errors[:3],
                "reason": "" if passed else f"期望 {expect['outcome']}{'+' + expect.get('mustContain', '') if expect.get('mustContain') else ''}，实际 {outcome or 'green'}，{len(errors)} 条"}
    except (ValueError, OSError) as exc:
        return {"id": case["id"], "status": "error", "reason": f"{type(exc).__name__}: {exc}"}
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def run_all(eval_path: Path) -> dict:
    eval_path = eval_path.resolve()
    spec = load_eval(eval_path)
    results = [run_case(case, spec) for case in spec.get("cases") or []]
    counts = {status: sum(1 for item in results if item["status"] == status)
              for status in ("passed", "failed", "blocked", "error")}
    return {"skill": spec.get("skill"), "eval": str(eval_path.relative_to(ROOT).as_posix()),
            "ranAt": datetime.now().astimezone().isoformat(timespec="seconds"),
            "counts": counts, "results": results,
            "green": counts["passed"] == len(results)}


def main(argv=None) -> int:
    targets = [Path(item) for item in (argv or [])] or sorted(ROOT.glob("evals/*/eval.yaml"))
    if not targets:
        print("no eval sets found under evals/*/eval.yaml", file=sys.stderr)
        return 1
    reports = []
    load_errors = 0
    for target in targets:
        try:
            report = run_all(target)
        except ValueError as exc:
            print(f"💥 {target}: {exc}", file=sys.stderr)
            load_errors += 1
            continue
        reports.append(report)
        for result in report["results"]:
            mark = {"passed": "✅", "failed": "⛔", "blocked": "⏸", "error": "💥"}[result["status"]]
            cost = f" [token {result['tokens']}]" if result.get("tokens") else ""
            print(f"  {mark} {report['skill']}/{result['id']} {result['status']}{cost} {result['reason']}")
            if result.get("peek"):
                print("     原文摘录:", " ".join(str(result["peek"]).split())[:220])
    out = ROOT / ".spec/obs/eval-report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(len(report["results"]) for report in reports)
    counts = {status: sum(1 for report in reports for item in report["results"] if item["status"] == status)
              for status in ("passed", "failed", "blocked", "error")}
    spent = sum(item.get("tokens") or 0 for report in reports for item in report["results"])
    print(f"评测 {total} 条：过 {counts['passed']} ｜ 败 {counts['failed']} ｜ 错 {counts['error']} ｜ "
          f"待引擎 {counts['blocked']} ｜ 引擎实耗 token {spent}"
          + (f" ｜ 评测集加载失败 {load_errors} 套" if load_errors else ""))
    print(f"报告 → {out.relative_to(ROOT).as_posix()}")
    return 1 if (counts["failed"] or counts["error"] or load_errors) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
