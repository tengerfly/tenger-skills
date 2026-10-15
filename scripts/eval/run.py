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
import json, shutil, subprocess, sys, tempfile
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


def run_case(case: dict) -> dict:
    if case["layer"] == "behaviour":
        return {"id": case["id"], "status": "blocked",
                "reason": "行为层需要 agent 引擎与 provider 授权，本机当前不可跑（不静默跳过，显式标记）"}
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
    spec = load_eval(eval_path)
    results = [run_case(case) for case in spec.get("cases") or []]
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
    bad = 0
    for target in targets:
        try:
            report = run_all(target)
        except ValueError as exc:
            print(f"💥 {target}: {exc}", file=sys.stderr)
            bad += 1
            continue
        reports.append(report)
        for result in report["results"]:
            mark = {"passed": "✅", "failed": "⛔", "blocked": "⏸", "error": "💥"}[result["status"]]
            print(f"  {mark} {report['skill']}/{result['id']} {result['status']} {result['reason']}")
    out = ROOT / ".spec/obs/eval-report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(len(report["results"]) for report in reports)
    failed_cases = sum(1 for report in reports for item in report["results"] if item["status"] in {"failed", "error"})
    blocked = sum(1 for report in reports for item in report["results"] if item["status"] == "blocked")
    bad = failed_cases + bad  # `bad` already counts eval sets that would not load at all
    print(f"评测 {total} 条：过 {total - bad - blocked} ｜ 败/错 {bad} ｜ 行为层待授权 {blocked} → "
          f"{out.relative_to(ROOT).as_posix()}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
