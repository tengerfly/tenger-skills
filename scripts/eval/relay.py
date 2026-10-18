"""L2 回流执法：`issue/` 条目想标闭环，就得有一条评测用例指回来。

governance/eval-spec.yaml `caseTiers.L2` 写的是「issue/ 每个 P0/P1 闭环后必须回流成 1 条；未回流不得标闭环」，
docs/observability-evaluation-outline.md C1 把同一个东西叫「回流钩子：条目标已闭环时机械检查是否已有对应
L2 case，没有则拒绝闭环」。在这之前这句话没有任何执行者——一条 P0 改完正文、状态填上「已沉淀」，
全仓没有任何机械核对问过它有没有对应回归。本文件就是那个核对者，两个方向都查：

1. 闭环却没有用例指回来 ⇒ 报缺回流（退出码 1）；
2. 用例写了 `issueRef` 却指向不存在的条目 ⇒ 算 error（run.py 逐条判 error，这里汇总报出）；
3. 缺回流的每一条都要有**分诊结论**（`governance/eval-spec.yaml` 的 `l2Triage`）：新增缺口没分诊 ⇒ 报红；
   名单里已不再缺的 ⇒ 报「名单过期」但**不判红**——那说明用例接上了，惩罚进展等于把判据调反。
   分诊名单本身读不动 ⇒ 也报红（尺子取不到不许默认通过）。

口径全部抄仓库现状，不发明字段：
- 条目 id ＝ 仓库相对路径（`issue/README.md` 的写入约定与 `shared/templates/issue-template.md`
  「跟踪与证据」都写明「本仓直接建 issue 可用仓库相对路径作为稳定标识」；正文里
  `稳定标识 = issue/WorkFlow/2026-10-10/02` 这种「目录/NN」短写也支持，但必须唯一命中）；
- 状态字段实名 ＝ 表行「优化状态」（模板口径），池内早期条目用 front-matter／行内的「状态」，两种都读；
  等级字段实名 ＝「等级」；
- 闭环 ＝ 状态以「已沉淀」开头（`issue/README.md` 状态机：待处理 → 处理中 → 已沉淀 / 已忽略）。
  「已忽略」＝决定不修，没有需要回归的规则，不要求用例；状态词落在枚举外（「复发重开」「已修规则」
  「规则已改+试跑未通过」）的单列成「无法判定」，既不默认它是闭环、也不默认它不是——
  静默放过正是量具腐烂的方式。
- 只有 P0/P1 触发回流要求（L2 原文口径），P2 与「等级字段缺失」的老格式条目进「无法判定」桶如实报数。

退出码：0 ＝ 无缺口；1 ＝ 有缺回流／悬空引用／评测集读不动；2 ＝ 用法或路径错误。
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ROOT = Path(__file__).resolve().parents[2]
ISSUE_ROOT = "issue"
L2_GRADES = ("P0", "P1")
CLOSED = "已沉淀"
IGNORED = "已忽略"
OPEN_STATES = ("待处理", "处理中")
# 注册表没声明时的兜底文案：只有行为层用例指回时，必须标「待授权」而不是并进「能拦住」。
BEHAVIOUR_ONLY_TEXT = (
    "这些条目的 issueRef 用例全是 behaviour 层，未授权时一律 blocked ⇒ 只证明「用例已登记」，"
    "不证明「规则现在能拦住」；标「待授权」，不得并进「已拦住」的读数")

# 表行（模板口径）与行内/front-matter（池内老口径）两种写法都要认；键名按出现的实名列，
# 长名在前，避免「优化状态」被「状态」抢先匹配。
_ROW = re.compile(r"^\|\s*\*{0,2}(优化状态|等级|状态)\*{0,2}\s*\|\s*([^|\n]*?)\s*\|\s*$", re.M)
_INLINE = re.compile(r"(?<![^\s|｜*：:;；-])(优化状态|等级|状态)\s*[:：]\s*([^\n|｜]*)")
_GRADE = re.compile(r"\bP([012])\b")


def _norm(value: str) -> str:
    """去掉 markdown 强调与反引号，让 `**已沉淀**` 与「已沉淀」判成同一个词。"""
    return re.sub(r"[*`]", "", str(value or "")).strip()


def classify(state: str) -> str:
    """把状态词映射到 issue/README.md 的状态机；认不出来就是 unknown，不猜。"""
    text = _norm(state)
    if not text:
        return "missing"
    if text.startswith(CLOSED):
        return "closed"
    if text.startswith(IGNORED):
        return "ignored"
    if text.startswith(OPEN_STATES):
        return "open"
    return "unknown"


def parse_issue(path: Path, root: Path = ROOT) -> dict:
    """读一条 issue 的等级与优化状态；读不到就如实标 missing，不当成「不需要回流」。"""
    text = path.read_text(encoding="utf-8", errors="replace")
    fields: dict = {}
    for pattern in (_ROW, _INLINE):
        for match in pattern.finditer(text):
            fields.setdefault(match.group(1), match.group(2))
    grade_match = _GRADE.search(_norm(fields.get("等级", "")))
    state = _norm(fields.get("优化状态", "")) or _norm(fields.get("状态", ""))
    return {"id": path.relative_to(root).as_posix(),
            "skill": path.relative_to(root).parts[1] if len(path.relative_to(root).parts) > 2 else "",
            "grade": f"P{grade_match.group(1)}" if grade_match else "",
            "state": state[:120], "classification": classify(state)}


def issue_entries(root: Path = ROOT) -> list:
    base = root / ISSUE_ROOT
    if not base.is_dir():
        return []
    entries = [parse_issue(path, root) for path in sorted(base.rglob("*.md")) if path.name != "README.md"]
    for entry in entries:
        entry["required"] = entry["grade"] in L2_GRADES and entry["classification"] == "closed"
    return entries


def resolve_ref(ref: str, root: Path = ROOT):
    """把 `issueRef` 解析成条目 id；解析不到就返回原因，绝不"挑一个最像的"凑覆盖率。"""
    text = str(ref).strip().replace("\\", "/").removeprefix("./")
    if not text.startswith(f"{ISSUE_ROOT}/"):
        return None, "issueRef 必须以 issue/ 开头的仓库相对路径（本仓条目稳定标识）"
    target = (root / text)
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError:
        return None, f"issueRef 跑出仓库: {text}"
    if target.is_file():
        if target.name == "README.md":
            return None, f"issueRef 指向目录说明而非问题条目: {text}"
        return text, ""
    if text.endswith(".md"):
        return None, f"条目不存在: {text}"
    if target.parent.is_dir():
        # 没写扩展名才允许按 `<NN>` 短引用去匹配；写了文件名就不该再猜
        hits = sorted((child.relative_to(root)).as_posix() for child in target.parent.glob(f"{target.name}-*.md"))
        if len(hits) == 1:
            return hits[0], ""
        return None, f"短引用 {text} 命中 {len(hits)} 个条目，无法确定唯一（写全文件名）"
    return None, f"条目不存在: {text}"


def refs_by_case(root: Path = ROOT) -> tuple:
    """扫全部评测集声明的 issueRef；返回 ([(用例引用位置, ref, 解析结果)], [读不动的评测集])。"""
    from eval import run as evaluator
    rows, load_errors = [], []
    for spec_path in sorted((root / "evals").glob("*/eval.yaml")):
        try:
            spec = evaluator.load_eval(spec_path)
        except (ValueError, OSError) as exc:
            load_errors.append(f"{spec_path.relative_to(root).as_posix()}: {exc}")
            continue
        for case in spec.get("cases") or []:
            declared = case.get("issueRef")
            if declared in (None, "", []):
                continue
            refs = declared if isinstance(declared, list) else [declared]
            for ref in refs:
                resolved, reason = resolve_ref(ref, root)
                rows.append({"eval": spec_path.relative_to(root).as_posix(), "case": case.get("id"),
                             "layer": case.get("layer"), "ref": str(ref),
                             "resolved": resolved, "reason": reason})
    return rows, load_errors


def triage_policy(root: Path = ROOT) -> dict:
    """读 governance/eval-spec.yaml 的 l2Triage；读不动／缺节／declared 为空都返回带 error 的空表。

    这里刻意不「缺了就当没有缺口」：尺子取不到时默认通过，就是把漏分诊洗成绿（本仓犯过的那族）。
    """
    path = Path(root) / "governance/eval-spec.yaml"
    try:
        import yaml
        section = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("l2Triage")
    except (OSError, ValueError) as exc:
        return {"error": f"分诊核对读不动：{path.name}: {exc}", "declared": {}, "texts": {}}
    if not isinstance(section, dict) or not section.get("declared"):
        missing = (section or {}).get("texts", {}).get("missingPolicy") if isinstance(section, dict) else None
        return {"error": missing or "governance/eval-spec.yaml 未声明 l2Triage.declared ⇒ 缺口无法核对是否已分诊",
                "declared": {}, "texts": (section or {}).get("texts", {}) if isinstance(section, dict) else {}}
    declared = {}
    for item in section["declared"]:
        ident = str(item.get("issue") or "").strip()
        if ident:
            declared[ident] = {"verdict": str(item.get("verdict") or "").strip(),
                               "reason": str(item.get("reason") or "").strip()}
    return {"error": "", "declared": declared, "texts": section.get("texts") or {}, "rule": section.get("rule")}


def triage_check(result: dict, root: Path = ROOT) -> dict:
    """缺回流的每一条都必须有分诊结论；名单里已不再缺的如实报「过期」，但不算红。"""
    policy = triage_policy(root)
    missing_ids = [entry["id"] for entry in result["missing"]]
    declared = policy["declared"]
    undeclared = [ident for ident in missing_ids if ident not in declared]
    stale = [ident for ident in declared if ident not in set(missing_ids)]
    return {"error": policy["error"], "texts": policy["texts"], "declared": declared,
            "undeclared": undeclared, "stale": stale,
            "covered": [ident for ident in missing_ids if ident in declared]}


def audit(root: Path = ROOT) -> dict:
    entries = issue_entries(root)
    rows, load_errors = refs_by_case(root)
    linked = {row["resolved"] for row in rows if row["resolved"]}
    rows_by_ref = {}
    for row in rows:
        if row["resolved"]:
            rows_by_ref.setdefault(row["resolved"], []).append(row)
    covered = [entry for entry in entries if entry["required"] and entry["id"] in linked]
    # 「已回流」必须分两层报：结构层用例当场就能判，行为层用例未授权时一律 blocked
    # （2026-10-17 并发会话把 5 条接成行为层用例，混进「已回流 26 条」会被读成「这些规则现在能拦住」）。
    structure_ids = {entry["id"] for entry in covered
                     if any(row.get("layer") == "structure" for row in rows_by_ref.get(entry["id"], []))}
    by_id = {entry["id"]: entry for entry in entries}
    missing = [entry for entry in entries if entry["required"] and entry["id"] not in linked]
    dangling = [row for row in rows if not row["resolved"]]
    result = {"root": str(root), "entries": entries,
              "closedP0P1": [entry for entry in entries if entry["required"]],
              "covered": covered,
              "coveredStructure": [entry for entry in covered if entry["id"] in structure_ids],
              "coveredBehaviourOnly": [entry for entry in covered if entry["id"] not in structure_ids],
              "coveredCases": {entry["id"]: [row["case"] for row in rows_by_ref.get(entry["id"], [])]
                               for entry in covered},
              "missing": missing, "dangling": dangling, "loadErrors": load_errors,
              "unknownState": [entry for entry in entries if entry["classification"] == "unknown"],
              "missingStateField": [entry for entry in entries if entry["classification"] == "missing"],
              "ignored": [entry for entry in entries if entry["classification"] == "ignored"],
              "openGraded": [entry for entry in entries if entry["grade"] in L2_GRADES
                             and entry["classification"] in ("open", "unknown", "missing")],
              "linkedNotRequired": [row for row in rows if row["resolved"]
                                    and by_id.get(row["resolved"], {}).get("required") is False]}
    result["triage"] = triage_check(result, root)
    return result


def render(result: dict) -> str:
    entries = result["entries"]
    lines = ["# L2 回流执法（issue 闭环 ↔ 评测用例双向核对）", ""]
    lines.append(f"- issue 条目：{len(entries)} 条；其中 P0/P1 已闭环（状态以「{CLOSED}」开头）"
                 f"**{len(result['closedP0P1'])} 条**")
    lines.append(f"- 有 `issueRef` 指回的：**{len(result['covered'])} 条**"
                 f"（结构层可判 {len(result.get('coveredStructure') or [])} 条"
                 f"｜仅行为层 {len(result.get('coveredBehaviourOnly') or [])} 条）"
                 f"｜缺回流：**{len(result['missing'])} 条**")
    lines.append(f"- 悬空 `issueRef`（指向不存在条目）：{len(result['dangling'])} 条"
                 f"｜读不动的评测集：{len(result['loadErrors'])} 套")
    lines.append(f"- 只作溯源的引用（指向未闭环或不需回流的条目，如复发重开／试跑未通过）："
                 f"{len(result['linkedNotRequired'])} 条——不给它们计回流覆盖")
    lines.append(f"- 无法判定闭环与否（状态词在状态机枚举外／缺字段／缺等级）："
                 f"{len(result['unknownState']) + len(result['missingStateField'])} 条"
                 f"｜已忽略（不要求用例）：{len(result['ignored'])} 条")
    lines.append("")
    if result["missing"]:
        lines.append(f"## ⛔ 缺回流（{len(result['missing'])} 条）——按 L2「未回流不得标闭环」，这些条目现在不算闭合")
        lines += [f"- `{entry['id']}`（{entry['grade']}｜{entry['state']}）" for entry in result["missing"]]
        lines.append("")
    behaviour_only = result.get("coveredBehaviourOnly") or []
    if behaviour_only:
        lines.append(f"## ⚠ 仅行为层回流（{len(behaviour_only)} 条）——用例已登记，但未授权未跑，"
                     f"不得读成「现在能拦住」")
        lines.append("- " + (((result.get("triage") or {}).get("texts") or {}).get("behaviourOnly")
                             or BEHAVIOUR_ONLY_TEXT))
        for entry in behaviour_only:
            cases = "、".join(result.get("coveredCases", {}).get(entry["id"]) or [])
            lines.append(f"- `{entry['id']}`（{entry['grade']}）← {cases}")
        lines.append("")
    triage = result.get("triage") or {}
    lines.append("## 分诊核对（缺口要么接成用例，要么写明不可机械化的结论）")
    if triage.get("error"):
        lines.append(f"- ⛔ {triage['error']}")
    else:
        lines.append(f"- 名单内已分诊：{len(triage.get('covered') or [])} 条｜未分诊：{len(triage.get('undeclared') or [])} 条"
                     f"｜名单过期（已不再缺回流）：{len(triage.get('stale') or [])} 条")
        if triage.get("undeclared"):
            lines.append(f"- ⛔ {triage['texts'].get('undeclared', '')}")
            lines += [f"  - `{ident}`：不在 governance/eval-spec.yaml 的 l2Triage.declared 里"
                      for ident in triage["undeclared"]]
        if triage.get("stale"):
            lines.append(f"- ⚠ {triage['texts'].get('stale', '')}")
            lines += [f"  - `{ident}`（结论曾是「{(triage['declared'].get(ident) or {}).get('verdict', 'N/A')}」）"
                      for ident in triage["stale"]]
        if not triage.get("undeclared") and not triage.get("stale") and triage.get("covered"):
            lines.append(f"- {triage['texts'].get('clean', '')}")
    if triage.get("declared"):
        for ident, item in triage["declared"].items():
            lines.append(f"  - `{ident}` ⇒ {item['verdict']}｜{item['reason']}")
    lines.append("")
    if result["dangling"]:
        lines.append(f"## ⛔ 悬空引用（{len(result['dangling'])} 条）——用例声明了没核实的关联")
        lines += [f"- {row['eval']} / {row['case']} → `{row['ref']}`：{row['reason']}" for row in result["dangling"]]
        lines.append("")
    if result["loadErrors"]:
        lines.append("## ⛔ 评测集读不动（回流无法核对）")
        lines += [f"- {item}" for item in result["loadErrors"]]
        lines.append("")
    if result["covered"]:
        lines.append(f"## 已接线（{len(result['covered'])} 条）")
        behaviour_ids = {entry["id"] for entry in behaviour_only}
        lines += [f"- `{entry['id']}`（{entry['grade']}）"
                  + ("｜仅行为层（待授权）" if entry["id"] in behaviour_ids else "")
                  for entry in result["covered"]]
        lines.append("")
    noise = result["unknownState"] + result["missingStateField"]
    if noise:
        lines.append(f"## 判不了（{len(noise)} 条）——状态词不在 issue/README.md 状态机枚举内，或根本没有状态字段")
        lines += [f"- `{entry['id']}`（等级 {entry['grade'] or '未标'}｜状态 {entry['state'] or '缺字段'}）"
                  for entry in noise]
        lines.append("")
    lines.append(f"口径：闭环＝「{CLOSED}」；要求回流＝等级 ∈ {L2_GRADES} 且闭环；"
                 f"已忽略不要求用例；判不了的一律如实报数，不当成已通过。")
    return "\n".join(lines)


def blocking(result: dict) -> bool:
    """relay 判红的口径：缺回流／悬空引用／评测集读不动／未分诊／分诊尺子读不动。"""
    triage = result.get("triage") or {}
    return bool(result["missing"] or result["dangling"] or result["loadErrors"]
                or triage.get("undeclared") or triage.get("error"))


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        # Windows 控制台默认 GBK：中文与 ⛔ 打出去要么炸要么成乱码，读的人只能猜
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="relay", description="L2 回流执法：闭环 issue ↔ 评测用例")
    parser.add_argument("--json", action="store_true", help="输出机器可读的审计结果")
    args = parser.parse_args(argv)
    if not (ROOT / ISSUE_ROOT).is_dir():
        print(f"relay: 找不到问题池 {ROOT / ISSUE_ROOT}", file=sys.stderr)
        return 2
    result = audit(ROOT)
    if args.json:
        print(json.dumps({key: value for key, value in result.items() if key != "entries"},
                         ensure_ascii=False, indent=2))
    else:
        print(render(result))
    red = blocking(result)
    print(f"\n结论：{'缺回流、悬空引用或缺口未分诊，红' if red else '闭环 issue 全部有回流用例且逐条分诊'}")
    return 1 if red else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
