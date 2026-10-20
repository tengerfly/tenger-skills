"""一次性回填：把 `.spec/obs/behaviour/*.log` 证据日志头部的历史真跑结果导入追加台账。

背景：行为层真跑结果原先只活在 `.spec/obs/eval-report.json` 里，而那份报告每次评测被整份
覆写——2026-10-15 三次真跑的真实成本（tokens 32357/58691/70554）连同 pass/fail 就曾被一次
未授权跑抹干净。证据日志是当时落盘的原始记录，头部格式固定，可以机械解析。

解析规则（显式、可复核；解析不出的一律跳过并报告原因，绝不编造）：
1. 头部第 1 行必须整行匹配固定格式
   `# 行为层证据 <caseId> ｜ 引擎 <name> ｜ ok=<True|False> ｜ exit=<值> ｜ tokens=<值|null> ｜ timedOut=<True|False>`，
   且要有 `# 记录时间` 行与 `--- OUTPUT ---` 段；任一缺失 ⇒ 跳过（记原因）。
2. caseId 必须能在 `evals/*/eval.yaml` 里被声明为 `layer: behaviour` 的用例；
   否则跳过——本仓实测有大量 `EV-Q` 日志来自单测桩（固定 tokens=1000、prompt='p'），
   它们不是真实评测运行，回填进去就是拿假成本污染真相台账。
2b. 引擎为 codex 且头部 tokens 有值时，该数字必须能在证据 transcript 原文里机械复算出来
   （新版 turn.completed.usage 计量行，或旧版 "tokens used" 页脚——两者正是当时引擎的取数源）；
   复算不出或复算不一致 ⇒ 跳过——测试桩日志的 tokens 是手填常量、造不出源文本里的计量行，
   这条是「真实运行」的机械指纹，防假成本污染真相台账。
   （实测本仓的桩测试会往 .spec/obs/behaviour/ 写 EV-FE/EV-FID/EV-FTDD 等假日志，
   仅靠规则 2 拦不住已被同事补进 eval.yaml 声明的用例 id，故必须加本指纹闸。）
3. 状态按 run.py 自身的判定树机械推导（只依据头部与证据原文，不凭记忆）：
   - timedOut=True 或 ok=False 或 exit≠0 ⇒ failed（引擎层失败，reason 取头部判定行）；
   - ok=True、exit=0、tokens=None ⇒ error（run.py：预算闸无法生效就是 error，不洗成通过）；
   - ok=True、exit=0、tokens>0 ⇒ 对证据里的引擎原回复重放现行判据：
     codex 用 engine._agent_messages 从 transcript 精确还原当时的判据输入
     （与 run_behaviour 同源，不退化全文匹配），随后逐字走 run.py 的
     预算闸→produces→禁词范围（问句/分节/全文）分支。声明了 produces 的用例无法从
     证据重建临时工作区 ⇒ 跳过（不编造判定）；非 codex 引擎同理跳过。
4. tokens 未计量显式 null，禁止填 0；cachedTokens 从同一 transcript 的
   turn.completed.usage 机械提取，取不到则 null。
5. 幂等：evidence 路径已在台账里的记录跳过，脚本可安全重跑。

用法：`./.venv/Scripts/python.exe scripts/eval/backfill_behaviour_runs.py [--apply]`
（缺省 dry-run 只报数；--apply 才追加）。不调用任何引擎、不产生任何花费。
"""
from __future__ import annotations
import argparse, json, re, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eval import run as evaluator

ROOT = Path(__file__).resolve().parents[2]
HEADER_RE = re.compile(
    r"^# 行为层证据 (?P<caseId>\S+) ｜ 引擎 (?P<engine>\S+) ｜ ok=(?P<ok>True|False) "
    r"｜ exit=(?P<exit>\S+) ｜ tokens=(?P<tokens>\S+) ｜ timedOut=(?P<timedOut>True|False)$")
OUTPUT_MARK = "\n--- OUTPUT ---\n"


def declared_behaviour_cases() -> dict:
    """caseId → (skill, spec, case)，只收 evals/*/eval.yaml 里声明的 layer: behaviour 用例。"""
    table = {}
    for path in sorted(ROOT.glob("evals/*/eval.yaml")):
        try:
            spec = evaluator.load_eval(path)
        except (ValueError, OSError) as exc:
            print(f"跳过评测集 {path.name}: {exc}", file=sys.stderr)
            continue
        for case in spec.get("cases") or []:
            if case.get("layer") == "behaviour":
                table[str(case.get("id"))] = (str(spec.get("skill")), spec, case)
    return table


def parse_header(text: str):
    lines = text.splitlines()
    if not lines:
        return None, "空文件"
    match = HEADER_RE.match(lines[0])
    if not match:
        return None, "头部格式不匹配"
    stamp = next((line[len("# 记录时间 "):].strip() for line in lines[:6] if line.startswith("# 记录时间 ")), "")
    verdict = next((line[len("# 判定: "):].strip() for line in lines[:6] if line.startswith("# 判定: ")), "")
    if not stamp:
        return None, "缺记录时间行"
    if OUTPUT_MARK not in text:
        return None, "缺 OUTPUT 段"
    fields = match.groupdict()
    tokens = None if fields["tokens"] == "None" else (int(fields["tokens"]) if fields["tokens"].isdigit() else fields["tokens"])
    if not isinstance(tokens, (int, type(None))):
        return None, f"tokens 值无法解析: {fields['tokens']!r}"
    exit_code = fields["exit"]
    fields.update(ok=fields["ok"] == "True", timedOut=fields["timedOut"] == "True",
                  tokens=tokens, exit=exit_code, ranAt=stamp, verdict=verdict,
                  output=text.split(OUTPUT_MARK, 1)[1])
    return fields, ""


def replay_status(fields: dict, spec: dict, case: dict):
    """按 run.py 判定树机械推导状态；返回 (status, reason) 或 (None, 跳过原因)。"""
    if fields["timedOut"] or not fields["ok"] or fields["exit"] != "0":
        return "failed", f"回填（引擎层失败）：{fields['verdict']}"
    if fields["tokens"] is None:
        return "error", ("回填：引擎未回报 token 用量，预算闸无法生效"
                         f"（声明预算 {case.get('tokenBudget')}；状态取自 run.py 判定树，非推测）")
    if fields["engine"] != "codex":
        return None, f"非 codex 引擎（{fields['engine']}）无法机械还原判据输入，不编造判定"
    expect = case.get("expect") or {}
    if expect.get("produces"):
        return None, "用例声明 produces，临时工作区已销毁，无法从证据重建产出判定"
    answers = None
    from eval import engine as agent_engine
    answers = agent_engine._agent_messages(fields["output"])
    if not answers:
        # 当时的判据输入＝引擎自己回的 agent 消息；取不到就说明这份证据是旧版纯文本流
        # （含注入 SKILL.md 原文与 GBK 乱码工具回显），在它上面重放禁词判据只会因乱码漏判——
        # 状态无法忠实重建 ⇒ 不编造，宁可不回填（成本再真也不把猜出来的 pass/fail 写进真相）。
        return None, ("证据非 codex JSONL 流（取不到 agent 消息），判据输入无法忠实重建；"
                      "不重放判定、不编造状态（该次运行成本真实，但 pass/fail 已不可考）")
    output = "\n\n".join(answers)
    budget = case.get("tokenBudget")
    if budget and fields["tokens"] > budget:
        return "failed", f"回填：超预算 {fields['tokens']} > {budget}（预算取现行声明）"
    banned = expect.get("mustNotContain")
    if not banned:
        return None, "现行声明里没有可重放的禁词判据，不编造判定"
    if expect.get("banInQuestions"):
        lines = evaluator._question_lines(output)
        if not lines:
            return "error", "回填：证据原文里没有任何问句，判据无法成立（run.py 同款规则，记 error 不当通过）"
        scope, label = "\n".join(lines), f"{len(lines)} 条问句"
    elif expect.get("banInSection"):
        scope = evaluator._section_body(output, expect["banInSection"])
        label = f"「{expect['banInSection']}」节"
        if scope is None:
            return "error", "回填：证据原文里找不到分节，判据无法成立（不退化全文匹配）"
    else:
        scope, label = output, "全文"
    hit = re.search(banned, scope, re.S | re.I)
    if hit:
        return "failed", f"回填：{label}内出现禁止内容 /{banned}/"
    return "passed", f"回填：对证据内引擎原回复重放现行判据（范围 {label}）；当时引擎判定: {fields['verdict']}"


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = argparse.ArgumentParser(prog="backfill_behaviour_runs")
    args.add_argument("--apply", action="store_true", help="真正追加台账（缺省 dry-run）")
    args = args.parse_args(argv)
    cases = declared_behaviour_cases()
    ledger = ROOT / evaluator.BEHAVIOUR_LEDGER
    known_evidence = set()
    if ledger.is_file():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            try:
                known_evidence.add(str(json.loads(line).get("evidence")))
            except ValueError:
                pass
    records, skipped = [], []
    for path in sorted((ROOT / ".spec/obs/behaviour").glob("*.log")):
        evidence = path.relative_to(ROOT).as_posix()
        if evidence in known_evidence:
            skipped.append((evidence, "已在台账（幂等跳过）"))
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            skipped.append((evidence, f"读取失败 {exc}"))
            continue
        fields, why = parse_header(text)
        if fields is None:
            skipped.append((evidence, why))
            continue
        declared = cases.get(fields["caseId"])
        if declared is None:
            skipped.append((evidence, f"caseId {fields['caseId']} 未在任何 evals/*/eval.yaml 声明为 behaviour 用例"
                                      "（测试桩/探针产物，非真实评测运行）"))
            continue
        skill, spec, case = declared
        from eval import engine as agent_engine
        from eval.engine import usage_tokens
        measured, cached = usage_tokens(fields["output"])
        fingerprint = None
        if measured:
            fingerprint = ("turn.completed 计量", measured)
        else:
            footer = agent_engine.TOKEN_RE.search(fields["output"])
            if footer:
                fingerprint = ("tokens used 页脚（旧版 codex 文本流）",
                               int(footer.group(1).replace(",", "")))
        if fields["engine"] == "codex" and fields["tokens"] is not None:
            # 真实性指纹：头部 tokens 必须能在 transcript 原文里机械复算出来（新版
            # turn.completed.usage 或旧版 "tokens used" 页脚，二者都正是当时引擎读的源）。
            # 测试桩只手填常量、造不出源文本里的计量行 ⇒ 拦下，防假成本污染真相台账。
            if fingerprint is None:
                skipped.append((evidence, "codex 真跑必须在 transcript 里留计量行（turn.completed 或 "
                                          "'tokens used' 页脚）：无指纹，疑似测试桩伪造，拒绝回填"))
                continue
            if fingerprint[1] != fields["tokens"]:
                skipped.append((evidence, f"头部 tokens={fields['tokens']} 与 transcript 复算 "
                                          f"{fingerprint[0]}={fingerprint[1]} 不一致，不采信，不编造"))
                continue
            if fingerprint[0] != "turn.completed 计量":
                cached = None
        status, reason = replay_status(fields, spec, case)
        if status is None:
            skipped.append((evidence, reason))
            continue
        records.append({"caseId": fields["caseId"], "skill": skill, "engine": fields["engine"],
                        "status": status, "tokens": fields["tokens"],
                        "cachedTokens": cached if cached else None,
                        "ranAt": fields["ranAt"], "evidence": evidence, "reason": reason,
                        "backfilledAt": datetime.now().astimezone().isoformat(timespec="seconds")})
    by_status = {}
    for row in records:
        by_status[row["status"]] = by_status.get(row["status"], 0) + 1
    print(f"候选证据日志 {len(list((ROOT / '.spec/obs/behaviour').glob('*.log')))} 份 ｜ "
          f"可回填 {len(records)} 条（{'、'.join(f'{k} {v}' for k, v in sorted(by_status.items())) or '无'}）｜ "
          f"跳过 {len(skipped)} 条")
    skip_reasons = {}
    for _e, why in skipped:
        key = why.split("（")[0][:60]
        skip_reasons[key] = skip_reasons.get(key, 0) + 1
    for key, count in sorted(skip_reasons.items()):
        print(f"  跳过 {count} 条：{key}")
    for row in records:
        print(f"  + {row['caseId']} {row['status']} tokens={row['tokens']} cached={row['cachedTokens']} "
              f"ranAt={row['ranAt']} evidence={row['evidence']}")
    if not args.apply:
        print("dry-run：未写台账（--apply 才追加）")
        return 0
    appended = evaluator.append_behaviour_ledger(ROOT, records)
    print(f"已追加 {appended} 条 → {evaluator.BEHAVIOUR_LEDGER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
