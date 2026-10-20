"""Structure-layer eval runner: deterministic, zero-cost, no agent, no host.

Two layers exist because only one of them is free. The structure layer feeds a fixture
project through the real validators and asserts which findings fire; it costs seconds and
can therefore run on every change. The behaviour layer must execute a skill inside an agent
engine, which needs an installed engine, provider credentials and spend, so cases declare
`layer: behaviour` and are reported as "not runnable here" instead of silently skipped.

Cases assert on findings, not on exit codes alone, so a checker that fails for an unrelated
reason cannot be mistaken for a passing regression.

Cases may declare `issueRef` — the repo-relative path of the `issue/` entry the case was
distilled from (`governance/eval-spec.yaml` caseTiers L2). A reference that does not resolve
is an `error`, never a pass: coverage numbers must not be paid for with guessed links.
"""
from __future__ import annotations
import json, os, re, shutil, sys, tempfile, time
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_core as core

ROOT = Path(__file__).resolve().parents[2]
# 行为层追加台账：append-only 真相源，与 eval-report.json（每次整份覆写的派生物）分轨。
# 实测教训：2026-10-15 三次真跑的成本与 pass/fail 只活在报告里，被一次未授权跑覆写抹干净，
# D5 因此永久失明。台账只追加、永不覆写，且入库（见 .gitignore 的反向豁免注释）。
BEHAVIOUR_LEDGER = ".spec/obs/behaviour-runs.jsonl"
CHECKS = {"artifact": core.check_artifact, "gate": core.check_gate, "trace": core.check_trace,
          "registry": core.check_registry, "refs": core.check_refs,
          "transition": core.check_transitions, "graph": core.check_graph,
          "recording": core.check_recording, "crossrefs": core.check_crossrefs,
          "resign": core.resign_findings}


def findings_for(project: Path, validator: str) -> list:
    """Validators return error strings; the section judge returns its own finding list."""
    if validator == "sections":
        from obs import score
        return score.d1_contract(project).get("failures", [])
    if validator not in CHECKS:
        raise ValueError(f"unknown validator: {validator}")
    return CHECKS[validator](project)


def load_eval(path: Path) -> dict:
    try:
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: 评测集不是合法 YAML（eval.yaml 是数据文件，不能混入 markdown 块语法）: {exc}") from exc
    if spec.get("schema") != "tenger.eval/v1":
        raise ValueError(f"{path}: unsupported eval schema {spec.get('schema')!r}")
    seen = {}
    for case in spec.get("cases") or []:
        case_id = case.get("id")
        if not case_id:
            raise ValueError(f"{path}: 用例缺 id（基线按 id 对账，无名用例无法追踪）")
        if case_id in seen:
            # 同一 id 出现两次时，基线对账按 id 建字典会互相覆盖，计数却看着更"全"
            # ——2026-10-17 新增 resign 用例时就这样撞了既有的 EV-GATE-008/009。
            raise ValueError(f"{path}: 用例 id 重复：{case_id}（同 id 两条用例会让基线对账互相覆盖）")
        seen[case_id] = True
        if case.get("layer") not in {"structure", "behaviour"}:
            raise ValueError(f"{path}/{case.get('id')}: layer must be structure or behaviour")
        if case.get("layer") == "behaviour":
            if not case.get("prompt"):
                raise ValueError(f"{path}/{case.get('id')}: behaviour 用例必须有 prompt")
            if not case.get("tokenBudget"):
                raise ValueError(f"{path}/{case.get('id')}: behaviour 用例必须声明 tokenBudget（跑一次要知道代价）")
            if not (case.get("expect") or {}).get("mustNotContain") and not (case.get("expect") or {}).get("produces"):
                raise ValueError(f"{path}/{case.get('id')}: behaviour 用例要有可判据（produces 或 mustNotContain），否则只是跑了个寂寞")
            answer_file = str(case.get("answerFile") or "").replace("\\", "/")
            if answer_file:
                # 答卷必须落在工作区内：越界路径会让「读答案」变成读宿主任意文件
                if Path(answer_file).is_absolute() or ".." in Path(answer_file).parts:
                    raise ValueError(f"{path}/{case.get('id')}: answerFile 必须是项目内相对路径: {answer_file}")
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


def _section_body(text: str, pattern: str):
    """Return the body of the section named `pattern`, or None when that section is absent.

    Two forms occur in real answers: a markdown heading, and a status-card label line
    (`待你决定：① …`, often inside a fenced block). Accepting only headings made a compliant
    answer fail as "节标题找不到". The section ends at the next heading, the next label line,
    or a blank line — never at the end of the document, so a ban stays scoped to one section.
    """
    lines = text.splitlines()
    label = re.compile(rf"^\s*(?:[-*]\s*)?(?:\d+[.、)]\s*)?\*{{0,2}}\s*({pattern})\s*\*{{0,2}}\s*[:：]\s*(.*)$", re.I)
    heading = re.compile(rf"^\s*#{{1,4}}\s*.*{pattern}", re.I)
    boundary = re.compile(r"^\s*(?:#{1,4}\s*|(?:[-*]\s*)?\*{0,2}\s*[^\s:：*|]{1,24}\s*\*{0,2}\s*[:：])", re.I)
    for index, line in enumerate(lines):
        hit = label.match(line)
        is_heading = hit is None and bool(heading.match(line))
        if not hit and not is_heading:
            continue
        body = [hit.group(2)] if hit else []
        for follow in lines[index + 1:]:
            if not follow.strip():
                break
            if body and boundary.match(follow):
                break
            body.append(follow)
        return "\n".join(body).strip()
    return None


def _write_evidence(case_id: str, engine_name: str, ran: dict, prompt: str) -> str:
    """Persist the raw engine transcript so a verdict can be re-read, not re-guessed.

    Behaviour runs are non-deterministic and cost real tokens; without the原文, a failed
    predicate can only be argued about. Derived output, so it stays out of git.
    """
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    folder = ROOT / ".spec/obs/behaviour"
    folder.mkdir(parents=True, exist_ok=True)
    header = (f"# 行为层证据 {case_id} ｜ 引擎 {engine_name} ｜ ok={ran.get('ok')} "
              f"｜ exit={ran.get('exit')} ｜ tokens={ran.get('tokens')} ｜ timedOut={ran.get('timedOut', False)}\n"
              f"# 记录时间 {datetime.now().astimezone().isoformat(timespec='seconds')}\n"
              f"# 判定: {ran.get('reason') or '(exit 0)'}\n\n--- PROMPT ---\n{prompt}\n\n--- OUTPUT ---\n")
    path = folder / f"{case_id}-{stamp}.log"
    path.write_text(header + str(ran.get("transcript") or ran.get("output") or "(引擎无输出)"), encoding="utf-8")
    return path.relative_to(ROOT).as_posix()


def _workdir(case_id: str) -> Path:
    """Scratch project for a behaviour run, kept inside the repo.

    %TEMP% paths got `Access is denied` from the codex sandbox on this host, so the agent ran
    the whole case read-only and could not produce any artifact — a false failure of the skill
    rather than of the harness.
    """
    path = ROOT / ".tmp-eval" / f"{case_id}-{os.getpid()}-{int(time.time())}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _question_lines(text: str) -> list:
    """Lines the agent actually puts to the user (ends with a question mark).

    Two real codex runs of the same case produced a 状态卡 with `待你决定：` and a numbered
    question list, so anchoring this rule on a section title was guaranteed to flap. The rule
    governs *what gets asked*, and a question line is the form-independent unit: the deferral
    sentence ("数据库留到 Tech Design 再定") is not a question, so it can no longer be misjudged.
    """
    return [line.strip() for line in text.splitlines() if re.search(r"[?？]\s*$", line.strip())]


def _chosen_engine(case: dict, spec: dict) -> str:
    """行为层用哪个引擎：用例指定 > 评测集默认 > codex（与 run_behaviour 的选择规则同源）。"""
    return str(case.get("engine") or spec.get("engine") or "codex")


def behaviour_ledger_records(skill: str, spec: dict, results: list, ran_at: str) -> list:
    """为行为层判定构造台账记录（纯函数，不落盘；结构层结果一律不产记录）。

    未计量的成本必须显式 null——填 0 会把「没计量」洗成「没花钱」，这正是本仓被
    编辑器宿主 token=0 骗过的那类错误。blocked 也产记录：「这次没跑」同样是需要留痕的事实。
    """
    declared = {str(case.get("id")): case for case in (spec.get("cases") or [])
                if case.get("layer") == "behaviour"}
    records = []
    for item in results:
        case = declared.get(str(item.get("id")))
        if case is None:
            continue
        records.append({"caseId": str(item["id"]), "skill": skill, "engine": _chosen_engine(case, spec),
                        "status": str(item.get("status") or "?"),
                        "tokens": item.get("tokens"), "cachedTokens": item.get("cachedTokens"),
                        "ranAt": ran_at, "evidence": item.get("evidence"),
                        "reason": str(item.get("reason") or "")})
    return records


def append_behaviour_ledger(root: Path, records: list) -> int:
    """把行为层判定逐条追加进台账；只 open("a")，任何路径都不得覆写既有行。"""
    if not records:
        return 0
    path = Path(root) / BEHAVIOUR_LEDGER
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return len(records)


def run_behaviour(case: dict, spec: dict) -> dict:
    from eval import engine as agent_engine
    chosen = _chosen_engine(case, spec)
    if chosen not in agent_engine.available():
        return {"id": case["id"], "status": "blocked",
                "reason": f"引擎 {chosen!r} 本机不可用（可用: {agent_engine.available()}）"}
    fixture = ROOT / str(case["given"]).replace("\\", "/")
    if not fixture.is_dir():
        return {"id": case["id"], "status": "error", "reason": f"夹具不存在: {case['given']}"}
    workspace = _workdir(case["id"])
    try:
        project = workspace / "project"
        agent_engine.materialise(fixture, project, case.get("skillFiles") or [], ROOT)
        ran = agent_engine.run(chosen, project, case["prompt"], timeout=case.get("timeout", 240))
        if ran.get("blocked"):
            return {"id": case["id"], "status": "blocked", "reason": ran["reason"]}
        evidence = _write_evidence(case["id"], chosen, ran, case["prompt"])
        if not ran["ok"]:
            return {"id": case["id"], "status": "failed", "reason": ran["reason"],
                    "tokens": ran.get("tokens"), "cachedTokens": ran.get("cachedTokens"),
                    "evidence": evidence}
        budget = case.get("tokenBudget")
        tokens = ran.get("tokens")
        if tokens is None:
            # 没有计量就无法证明没超预算；把"取不到成本"判成 error，比静默跳过预算闸诚实
            return {"id": case["id"], "status": "error", "evidence": evidence,
                    "cachedTokens": ran.get("cachedTokens"),
                    "reason": f"引擎未回报 token 用量，预算闸无法生效（声明预算 {budget}）"}
        if budget and tokens > budget:
            return {"id": case["id"], "status": "failed", "tokens": tokens,
                    "cachedTokens": ran.get("cachedTokens"), "evidence": evidence,
                    "reason": f"超预算：{tokens} > {budget}（行为层必须带预算闸，否则跑一次不知道烧了多少）"}
        # 答卷文件（answerFile）：判据只吃模型自己写下的答案，但「没交卷」不是违规也不是通过。
        # 2026-10-18 真跑实测：要求「首行结论」的回答有 10/20 条根本没这个首行（模型改成小节/表格作答），
        # 判据只能记 error；让用例把答案落成文件后，判据锚在小节名上就不再依赖模型的聊天排版。
        answer_file = case.get("answerFile")
        answer_text = ""
        if answer_file:
            target = (project / str(answer_file).replace("\\", "/")).resolve()
            if not target.is_relative_to(project.resolve()) or not target.is_file():
                return {"id": case["id"], "status": "error", "tokens": tokens,
                        "cachedTokens": ran.get("cachedTokens"), "evidence": evidence,
                        "reason": f"答案文件未产出：{answer_file}（判据无法成立；不记通过，也不把「没交答卷」算成违规）"}
            answer_text = target.read_text(encoding="utf-8", errors="replace")
        for pattern in case.get("expect", {}).get("produces") or []:
            if not list(project.glob(pattern)):
                return {"id": case["id"], "status": "failed", "tokens": tokens,
                        "cachedTokens": ran.get("cachedTokens"), "evidence": evidence,
                        "reason": f"未产出约定文件: {pattern}"}
        produced_text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for pattern in case.get("expect", {}).get("produces") or []
            for path in project.glob(pattern))
        judged = "\n".join(part for part in (answer_text, ran["output"], produced_text) if part)
        banned = case.get("expect", {}).get("mustNotContain")
        cached = ran.get("cachedTokens")
        if banned:
            scope_name = case["expect"].get("banInSection")
            if case["expect"].get("banInQuestions"):
                lines = _question_lines(judged)
                if not lines:
                    return {"id": case["id"], "status": "error", "tokens": tokens, "cachedTokens": cached,
                            "evidence": evidence,
                            "reason": "回答里没有任何问句，这条规则无法判（记 error，不许当通过）"}
                scope, label = "\n".join(lines), f"{len(lines)} 条问句"
            elif scope_name:
                scope, label = _section_body(judged, scope_name), f"「{scope_name}」节"
                if scope is None:
                    return {"id": case["id"], "status": "error", "tokens": tokens, "cachedTokens": cached,
                            "evidence": evidence,
                            "reason": f"找不到分节 /{scope_name}/，判据无法成立（不许退化成全文匹配）"}
            else:
                scope, label = judged, "全文"
            hit = re.search(banned, scope, re.S | re.I)
            if hit:
                return {"id": case["id"], "status": "failed", "tokens": tokens, "cachedTokens": cached,
                        "evidence": evidence,
                        "reason": f"{label}内出现禁止内容 /{banned}/",
                        "peek": scope[max(0, hit.start() - 120):hit.end() + 160]}
            return {"id": case["id"], "status": "passed", "tokens": tokens, "cachedTokens": cached,
                    "evidence": evidence,
                    "reason": f"引擎 {chosen}；判据范围 {label}"}
    except (ValueError, OSError) as exc:
        return {"id": case["id"], "status": "error", "reason": f"{type(exc).__name__}: {exc}"}
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def issue_ref_problem(case: dict) -> str:
    """用例声明的 `issueRef` 必须解析到真实条目，解析不到就是 error。

    覆盖率是量具换来的，不能靠猜的关联凑：一句编造的引用会让一条闭环 issue 看起来「已回流」，
    而实际上没有任何回归在守它——这正是 L2 要闭合的洞，所以这里宁可乐一条也不放空一条。
    """
    declared = case.get("issueRef")
    if not declared:
        return ""
    from eval import relay
    problems = []
    for ref in (declared if isinstance(declared, list) else [declared]):
        resolved, reason = relay.resolve_ref(ref, ROOT)
        if not resolved:
            problems.append(f"issueRef `{ref}`：{reason}")
    return "；".join(problems)


def run_case(case: dict, spec: dict | None = None) -> dict:
    problem = issue_ref_problem(case)
    if problem:
        return {"id": case["id"], "status": "error", "reason": problem}
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


def _label(path: Path) -> str:
    """仓内给仓库相对路径，仓外（临时探针评测集）给绝对路径。

    写死 `relative_to(ROOT)` 会让"仓库外的一套 eval.yaml 根本跑不起来"——那是把量具钉死在
    这个目录布局上，对照组也就没地方放了。
    """
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def run_all(eval_path: Path) -> dict:
    eval_path = eval_path.resolve()
    spec = load_eval(eval_path)
    results = [run_case(case, spec) for case in spec.get("cases") or []]
    counts = {status: sum(1 for item in results if item["status"] == status)
              for status in ("passed", "failed", "blocked", "error")}
    return {"skill": spec.get("skill"), "eval": _label(eval_path),
            "ranAt": datetime.now().astimezone().isoformat(timespec="seconds"),
            "counts": counts, "results": results,
            "green": counts["passed"] == len(results)}


def _print_relay_status() -> None:
    """把 L2 回流缺口的真实数字打在每次评测输出里，但不改上面用例计数。

    缺回流的红由 `scripts/eval/relay.py` 自己的退出码承担（「未回流不得标闭环」）。把「issue 闭环了
    却没有用例」混进本套用例的通过/失败里，等于让评测集为一个它并没有判过的东西负责——数字看着严，
    实际是把两条判据搅在一起。这里只把缺口如实显示出来，让人无法假装没看见。
    """
    try:
        from eval import relay
        result = relay.audit(ROOT)
    except (ValueError, OSError) as exc:
        print(f"L2 回流执法未能核：{exc}", file=sys.stderr)
        return
    undecidable = len(result["unknownState"]) + len(result["missingStateField"])
    triage = result.get("triage") or {}
    print(f"L2 回流执法：P0/P1 已闭环 {len(result['closedP0P1'])} 条 ｜ 已回流 {len(result['covered'])} 条"
          f"（结构层 {len(result.get('coveredStructure') or [])}｜仅行为层 "
          f"{len(result.get('coveredBehaviourOnly') or [])}，结论见行为层台账）"
          f" ｜ 缺回流 {len(result['missing'])} 条 ｜ 悬空引用 {len(result['dangling'])} 条 ｜ 判不了 {undecidable} 条"
          f"（详单 `python scripts/eval/relay.py`；缺回流即红，不影响上面的用例计数）")
    if triage.get("error"):
        print(f"L2 分诊核对未能核：{triage['error']}（缺尺子按红处理，不默认通过）", file=sys.stderr)
    else:
        print(f"L2 分诊核对：缺回流中已分诊 {len(triage.get('covered') or [])} 条 ｜ "
              f"未分诊 {len(triage.get('undeclared') or [])} 条（未分诊即红）｜ "
              f"名单过期 {len(triage.get('stale') or [])} 条（过期只报数，不惩罚进展）")


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        # Windows 控制台默认 GBK，报告里的 ✅/⛔ 会直接抛 UnicodeEncodeError 把评测搞成"没跑"
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    targets = [Path(item) for item in (argv or [])] or sorted(ROOT.glob("evals/*/eval.yaml"))
    if not targets:
        print("no eval sets found under evals/*/eval.yaml", file=sys.stderr)
        return 1
    reports = []
    load_errors = 0
    appended = 0
    for target in targets:
        try:
            report = run_all(target)
        except ValueError as exc:
            print(f"💥 {target}: {exc}", file=sys.stderr)
            load_errors += 1
            continue
        reports.append(report)
        # 台账追加只挂在 CLI 入口：run_all 是被单测/基线快照当库调用的，判定归判定、留痕归留痕；
        # 而每一次真实评测运行的行为层判定（含 blocked）都必须逐条落进不可覆写的真相里。
        appended += append_behaviour_ledger(ROOT, behaviour_ledger_records(
            report["skill"], load_eval(target), report["results"], report["ranAt"]))
        for result in report["results"]:
            mark = {"passed": "✅", "failed": "⛔", "blocked": "⏸", "error": "💥"}[result["status"]]
            cost = f" [token {result['tokens']}]" if result.get("tokens") else ""
            print(f"  {mark} {report['skill']}/{result['id']} {result['status']}{cost} {result['reason']}")
            if result.get("peek"):
                print("     原文摘录:", " ".join(str(result["peek"]).split())[:220])
            if result.get("evidence"):
                print(f"     证据 → {result['evidence']}")
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
    _print_relay_status()
    print(f"报告 → {out.relative_to(ROOT).as_posix()}")
    if appended:
        print(f"行为层台账追加 {appended} 条 → {BEHAVIOUR_LEDGER}（append-only 真相，入库；报告覆写抹不掉它）")
    return 1 if (counts["failed"] or counts["error"] or load_errors) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
