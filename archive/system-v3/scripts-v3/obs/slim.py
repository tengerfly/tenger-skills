"""精简建议（目标收益）：三读数齐了才允许开口，集中度过阈值就机械禁止给删减结论。

plan v2 §0 把「skill 正文该不该精简」列为这套体系要回答的第一个收益问题。此前只有一把尺子：
`tsr rules` 报规则命中率并按命中率排文件——**单读数就会骗人**：

- 命中率是下界（宿主把正文注入上下文时不留日志），低命中只说明「轨迹里没有证据」；
- 条款证据覆盖率与承接集中度会告诉我们另一件事：证据是不是全压在同一条款上。
  本仓踩过——24 处证据全落 `shared/problem-recording.md` 那次，正确读法是**量具覆盖面窄**，
  不是各 skill 都承接得好；反过来拿它当依据去删正文，就是把量具故障读成产品结论。

所以这里只做三件事，判据全部来自 `governance/obs-registry.yaml` 的 `slimAdvice` 节：

1. 把三个读数摆到同一张纸上：规则命中率（含口径是否固定）＋条款证据覆盖率＋承接集中度；
2. 任一读数取不到 ⇒ 只报「依据不足」并写明缺在哪一环，**不出任何名单**（N/A 不是 0，也不等于没问题）；
3. 集中度过阈值 ⇒ 打印注册表原文的禁止结论文案并**不生成删减/观察名单**；
   即便三读数齐备，输出的也只是「观察名单（待验证，不是删除清单）」——删正文属人。

固定口径＝全量（`--sample 0`）＋`--project-slug` 限定被观测项目＋ISO 时间切点，三者缺一即标「口径未固定」，
该读数不得据以定删减阈值。
"""
from __future__ import annotations
from pathlib import Path
import yaml

ROOT_DIR = Path(__file__).resolve().parents[2]
SHIPPED_REGISTRY = ROOT_DIR / "governance/obs-registry.yaml"
SECTION_KEYS = ("label", "readings", "requiredReadings", "caliber", "gate", "output", "boundary")
CALIBER_KEYS = ("sample", "projectSlug", "since", "until", "rule", "unfixedLabel")
GATE_KEYS = ("missingReading", "concentrationAlarm", "zeroHitOnly", "watchListLabel", "lowHitShare",
             "minEvidenceCards", "tooFewCards")


def registry_path(root: Path | None = None) -> Path:
    if root is not None:
        local = Path(root) / "governance/obs-registry.yaml"
        if local.is_file():
            return local
    return SHIPPED_REGISTRY


def spec(root: Path | None = None) -> dict:
    """读 slimAdvice 节；缺键直接报错，不用默认值凑一份看起来完整的建议。"""
    path = registry_path(root)
    try:
        section = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("slimAdvice")
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"精简建议判据读不动: {path}: {exc}") from exc
    if not isinstance(section, dict):
        raise ValueError(f"{path.as_posix()} 未声明 slimAdvice ⇒ 不猜三读数是哪三个，也不猜阈值")
    missing = [key for key in SECTION_KEYS if not section.get(key)]
    if missing:
        raise ValueError(f"slimAdvice 缺必需判据键 {missing} ⇒ 拒绝用默认值冒充实装")
    for sub, keys in (("caliber", CALIBER_KEYS), ("gate", GATE_KEYS)):
        absent = [key for key in keys if section[sub].get(key) in (None, "")]
        if absent:
            raise ValueError(f"slimAdvice.{sub} 缺判据键 {absent} ⇒ 拒绝执行没有凭据的红口")
    named = [key for key in section["requiredReadings"] if not section["readings"].get(key)]
    if named:
        raise ValueError(f"slimAdvice.requiredReadings 里有读数未在 readings 定义：{named} ⇒ 不许口头宣称有这一读数")
    return section


def caliber_check(report: dict, cal: dict) -> tuple:
    """本次跑法是否等于注册表钉死的固定口径；不等就把差在哪一条条写出来。"""
    params = report.get("params") or {}
    window = report.get("window") or {}
    gaps = []
    if int(params.get("sample", -1) or 0) != int(cal["sample"]):
        gaps.append(f"--sample {params.get('sample', '未传')} ≠ 全量 {cal['sample']}")
    if str(params.get("slug") or "") != str(cal["projectSlug"]):
        gaps.append(f"--project-slug `{params.get('slug') or '未传'}` ≠ {cal['projectSlug']}")
    for key, label in (("since", "起切点"), ("until", "止切点")):
        if str(window.get(key) or "") != str(cal[key]):
            gaps.append(f"{label} `{window.get(key) or '未设'}` ≠ {cal[key]}")
    return (not gaps, gaps)


def readings(rules_report: dict, attribution, cal: dict, gate: dict | None = None) -> dict:
    """三读数各自成条：取不到就是 N/A ＋原因，绝不拿相近数字顶替。"""
    out: dict = {}
    floor = int((gate or {}).get("minEvidenceCards") or 0)
    value = rules_report.get("value")
    fixed, gaps = caliber_check(rules_report, cal)
    if value is None:
        out["ruleHitRate"] = {"label": "规则命中率", "value": None, "usable": False,
                              "reason": rules_report.get("reason") or "rules.measure 没给出数"}
    elif not fixed:
        # 数还是照原样印出来（人有权看见它），但 usable=False ⇒ 闸门当它是缺的：口径没固定就不配定阈值
        out["ruleHitRate"] = {"label": "规则命中率", "value": value, "usable": False,
                              "reason": f"{cal['unfixedLabel']}（{'；'.join(gaps)}）⇒ {cal['rule']}"}
    else:
        out["ruleHitRate"] = {"label": "规则命中率", "value": value, "usable": True, "reason": "",
                              "detail": f"口径已固定：全量＋slug＋切点 {cal['since']}→{cal['until']}"}
    counts = (attribution or {}).get("counts") or {}
    cards = int(counts.get("cards", 0))
    if attribution is None:
        out["clauseEvidenceCoverage"] = {"label": "条款证据覆盖率", "value": None,
                                         "reason": "归因段本轮没跑成（注册表未声明 attribution 判据或候选卡为空）"}
    elif cards == 0:
        out["clauseEvidenceCoverage"] = {"label": "条款证据覆盖率", "value": None,
                                         "reason": "本轮没有候选卡 ⇒ 没有可归因的对象，比例无从计算（不得退化成 100%）"}
    elif floor and cards < floor:
        # 数照样印出来给人看，但 usable=False ⇒ 闸门当这一环缺：分母太小的 100% 不是「覆盖得好」
        out["clauseEvidenceCoverage"] = {
            "label": "条款证据覆盖率", "value": int(counts.get("withClauses", 0)) / cards, "usable": False,
            "detail": f"带逐字条款证据的卡 {counts.get('withClauses', 0)}/{cards} 张",
            "reason": f"候选卡 {cards} 张 < minEvidenceCards={floor} ⇒ {gate['tooFewCards']}"}
    else:
        out["clauseEvidenceCoverage"] = {"label": "条款证据覆盖率",
                                         "value": int(counts.get("withClauses", 0)) / cards,
                                         "detail": f"带逐字条款证据的卡 {counts.get('withClauses', 0)}/{cards} 张"}
    conc = (attribution or {}).get("concentration") or {}
    if not conc or cards == 0:
        out["attributionConcentration"] = {"label": "承接集中度", "value": None,
                                           "reason": "没有条款证据可统计占比 ⇒ 集中度无从计算"
                                           if cards else "本轮没有候选卡 ⇒ 集中度无从计算"}
    elif attribution is not None and floor and cards < floor:
        out["attributionConcentration"] = {
            "label": "承接集中度", "value": float(conc.get("share", 0.0)), "usable": False,
            "threshold": float(conc.get("threshold", 0.0)),
            "reason": f"候选卡 {cards} 张 < minEvidenceCards={floor} ⇒ {gate['tooFewCards']}"}
    else:
        out["attributionConcentration"] = {
            "label": "承接集中度", "value": float(conc.get("share", 0.0)),
            "alarm": bool(conc.get("alarm")), "threshold": float(conc.get("threshold", 0.0)),
            "detail": (f"占比最高的一条 = `{(conc.get('top') or {}).get('file')}:"
                       f"{(conc.get('top') or {}).get('startLine')}`"
                       f"｜{(conc.get('evidence'))} 处证据／去重 {conc.get('distinctClauses')} 条"),
            "offSample": str(conc.get("offSampleNote") or "")}
    return out


def advise(root: Path, rules_report: dict, attribution, advice_spec: dict | None = None) -> dict:
    """把三读数摆齐＋按闸门出结论。返回 {readings, blocked, reasons, watch, forbidden}。"""
    pol = advice_spec or spec(root)
    names = [str(name) for name in pol["requiredReadings"]]
    got = readings(rules_report, attribution, pol["caliber"], pol["gate"])
    result = {"policy": pol, "readings": got, "missing": [], "blocked": [], "watch": [],
              "concentrationAlarm": False, "caliberFixed": False}
    def unusable(item: dict) -> bool:
        """取不到数（value None）或取到了但不配用（口径未固定 ⇒ usable False）都算「缺这一环」。"""
        return item.get("value") is None or item.get("usable") is False

    missing = [name for name in names if unusable(got.get(name) or {})]
    result["missing"] = [{"name": name, "reason": got.get(name, {}).get("reason", "读数没实现")}
                         for name in missing]
    if missing:
        result["blocked"].append(pol["gate"]["missingReading"])
        return result
    result["caliberFixed"] = True
    conc = got["attributionConcentration"]
    if conc.get("alarm"):
        result["concentrationAlarm"] = True
        result["blocked"].append(f"{pol['gate']['concentrationAlarm']}"
                                 f"（{conc.get('detail', '')}，阈值 {conc['threshold']:.0%}）")
        return result
    threshold = float(pol["gate"]["lowHitShare"])
    result["watch"] = [entry for entry in (rules_report.get("files") or [])
                       if entry.get("rate", 1.0) < threshold]
    return result


def render(advice: dict) -> str:
    """建议正文：读数、闸门、名单（或拒判原因）逐条落字，指针能点回注册表与复算命令。"""
    pol = advice["policy"]
    lines = [f"# {pol['label']}（三读数齐了才允许开口）", ""]
    lines.append(f"- 判定依据：`governance/obs-registry.yaml` 的 slimAdvice 节（阈值 {pol['gate']['lowHitShare']}"
                 f"｜观察名单阈值以下仍不是删除清单）")
    lines.append("- 三个读数：")
    for name in [str(item) for item in pol["requiredReadings"]]:
        item = advice["readings"].get(name) or {}
        value = item.get("value")
        shown = "N/A" if value is None else (f"{value:.1%}" if isinstance(value, float) else str(value))
        tail = f" ｜ {item['reason']}" if item.get("reason") else ""
        detail = f" ｜ {item['detail']}" if item.get("detail") else ""
        alarm = " ｜ ⛔ 过阈值报警" if item.get("alarm") else ""
        lines.append(f"  - {pol['readings'].get(name, name)}：**{shown}**{detail}{alarm}{tail}")
        if item.get("offSample"):
            lines.append(f"    - {item['offSample']}")
    lines.append("")
    if advice["missing"]:
        lines += [f"## 依据不足：{pol['gate']['missingReading']}", ""]
        lines += [f"- 缺的读数：{item['name']} —— {item['reason']}" for item in advice["missing"]]
    elif advice["concentrationAlarm"]:
        lines += [f"## 禁止给删减结论：{pol['gate']['concentrationAlarm']}", ""]
        lines += [f"- {reason}" for reason in advice["blocked"]]
    else:
        threshold = float(pol["gate"]["lowHitShare"])
        lines.append(f"## {pol['gate']['watchListLabel']}（命中率 < {threshold:.0%} 的 {len(advice['watch'])} 个文件）")
        lines.append(f"- 仍然禁止的读法：{pol['gate']['zeroHitOnly']}")
        if not advice["watch"]:
            lines.append("- 本轮没有文件低于该阈值 ⇒ 没有观察对象（这也不等于「都别删」，只是没证据指向谁）")
        else:
            lines += ["", "| 文件 | skill | 条款 | 读取 | 引用 | 命中率 |", "|---|---|---|---|---|---|"]
            for entry in advice["watch"]:
                lines.append(f"| `{entry['file']}` | {entry['skill']} | {entry['clauses']} | {entry['readHits']} "
                             f"| {entry['citeHits']} | {entry['rate']:.0%} |")
    lines += ["", f"- 边界：{pol['boundary']}",
              f"- 复算（1 条 CLI 调用）：`{pol['output']['recompute']}`"]
    return "\n".join(lines) + "\n"
