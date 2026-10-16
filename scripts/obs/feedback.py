"""反哺有效率（plan v2 §3「智能化」第三条）：本轮只把读数通路接出来，不造数。

三件事，全部机械化、全部只读：

1. **反哺记录**从 `evolution/进化台账.md` 取（复用 `validate_core.evolution_audit`，不另写一套解析）：
   必须是「声称生效」＋before/after 两侧可核（该条目本身无判据错误）＋落账 commit 经只读 `git cat-file` 验真。
2. **同型错误**从 `obs.recurrence` 的显式复发链取（链节点带日期）。两侧要按 skill 对上才算「可归属」——
   注册表 id 与 legacyAliases 大小写不敏感匹配；对不上就照实说没交集，**不许借别的链凑分母**。
3. 任何一环取不到 ⇒ 整体 N/A 并写明缺在哪一环：反哺记录不足 `minRecords`、可归属链不足 `minChains`、
   观察窗不足 `minObserveDays`（反哺刚生效还没窗）、n=1 ⇒ 一律不出百分比。

判据与禁止项全部在 `governance/obs-registry.yaml` 的 `feedbackRate` 节，代码只执行。
本模块刻意把「量具红点率」（台账 before/after 的检出条数）单列一个读数并明确标注它**不是**反哺有效率——
这条指标最容易的自欺就是拿前者冒充后者（`forbidden` 第一条）。
"""
from __future__ import annotations
import re
from datetime import date, datetime, timedelta
from pathlib import Path
import yaml

ROOT_DIR = Path(__file__).resolve().parents[2]
SHIPPED_REGISTRY = ROOT_DIR / "governance/obs-registry.yaml"
SECTION_KEYS = ("name", "definition", "truthSource", "recompute", "minRecords", "minChains",
                "minObserveDays", "windowDays", "beforeAfterPattern", "detectorRateLabel",
                "naRule", "honestWithoutAfter", "linkRule", "forbidden", "report")
DATE_IN_TITLE = re.compile(r"(?P<ymd>\d{4}-\d{2}-\d{2})")


def registry_path(root: Path | None = None) -> Path:
    if root is not None:
        local = Path(root) / "governance/obs-registry.yaml"
        if local.is_file():
            return local
    return SHIPPED_REGISTRY


def policy(root: Path | None = None) -> dict:
    path = registry_path(root)
    try:
        section = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("feedbackRate")
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"反哺有效率判据读不动: {path}: {exc}") from exc
    if not isinstance(section, dict):
        raise ValueError(f"{path.as_posix()} 未声明 feedbackRate ⇒ 不猜反哺记录与同型错误从哪来")
    missing = [key for key in SECTION_KEYS if key not in section or section[key] in (None, "", [])]
    if missing:
        raise ValueError(f"feedbackRate 缺必需判据键 {missing} ⇒ 拒绝用默认值冒充实装")
    return section


def _day(value):
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _skill_index(root: Path) -> dict:
    """大小写不敏感的 skill 名 → registry id（含 legacyAliases）；issue 池目录名走同一张表。"""
    path = Path(root) / "governance/skill-registry.yaml"
    index: dict = {}
    if not path.is_file():
        return index
    for entry in (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("skills") or []:
        ident = str(entry.get("id") or "").strip()
        if not ident:
            continue
        keys = [ident, *[str(alias) for alias in entry.get("legacyAliases") or []],
                str(entry.get("path") or ""), Path(str(entry.get("path") or "")).name]
        for key in filter(None, keys):
            index.setdefault(key.casefold(), ident)
    return index


def _claim_records(root: Path, pol: dict) -> tuple:
    """进化台账里「声称生效且两侧可核」的反哺记录；返回 (可用记录, 落选原因清单)。"""
    import validate_core as core
    records, dropped = [], []
    try:
        audit = core.evolution_audit(root)
    except (ValueError, OSError) as exc:
        return [], [f"进化台账读不动 ⇒ 没有反哺记录可数：{exc}"]
    pattern = re.compile(str(pol["beforeAfterPattern"]))
    index = _skill_index(root)
    for entry in audit["entries"]:
        title = str(entry.get("title") or "")
        stamp = DATE_IN_TITLE.search(title)
        day = _day(stamp.group("ymd")) if stamp else None
        skills = {index.get(token.casefold()) for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]*", title)}
        skills = sorted(skill for skill in skills if skill)
        if str(entry.get("state")) != "claiming" or entry.get("errors"):
            dropped.append(f"`{title[:48]}`：未声称生效或判据本身有错 ⇒ 不算反哺记录")
            continue
        if day is None:
            dropped.append(f"`{title[:48]}`：标题里取不到生效日 ⇒ 无法划前/后窗")
            continue
        match = pattern.search(str(entry.get("proof") or ""))
        if not match:
            dropped.append(f"`{title[:48]}`：效果证据不是 before→after 形式 ⇒ "
                            f"{pol['honestWithoutAfter']}")
            continue
        if not entry.get("pointersVerified"):
            dropped.append(f"`{title[:48]}`：落账 commit 未通过只读验真 ⇒ 记录不可归属")
            continue
        records.append({"title": title, "date": day.isoformat(), "skills": skills or [None],
                        "before": int(match.group("before")), "after": int(match.group("after")),
                        "commit": str(entry.get("commit") or "").strip().strip("`")})
    return records, dropped


def _chains(root: Path) -> tuple:
    from obs import recurrence
    try:
        report = recurrence.measure(root)
    except (ValueError, OSError) as exc:
        return [], f"复发链读不动 ⇒ 没有同型错误数据可数：{exc}"
    index = _skill_index(root)
    chains = []
    for chain in report.get("chains") or []:
        skill = index.get(str(chain.get("skill") or "").casefold())
        nodes = []
        for node in chain.get("nodes") or []:
            day = _day(node.get("date"))
            if day:
                nodes.append({"rel": str(node.get("rel")), "day": day})
        chains.append({"skillLabel": str(chain.get("skill")), "skill": skill, "nodes": nodes})
    return chains, ""


def _verdict(pol: dict, records: list, chains: list, links: list, dropped: list | None = None,
             chain_error: str = "") -> tuple:
    """出数与拒绝出数的全部判定都关在这个纯函数里：每道闸门各配一条反向对照。"""
    usable = [link for link in links if link["usable"]]
    distinct = sorted({link["skill"] for link in usable})
    if len(records) < int(pol["minRecords"]):
        return None, (f"反哺记录 {len(records)} 条 < minRecords={pol['minRecords']}"
                      f"（另有 {len(dropped or [])} 条台账条目落选，首条原因："
                      f"{(dropped or ['无'])[0]}）⇒ {pol['naRule']}")
    if chain_error:
        return None, f"{chain_error} ⇒ {pol['naRule']}"
    if not links:
        return None, (f"{pol['linkRule']}｜实测：{len(records)} 条反哺记录落在 "
                      f"{sorted({skill for record in records for skill in record['skills']}) or 'N/A'}，"
                      f"{len(chains)} 条复发链落在 "
                      f"{sorted({chain['skill'] or chain['skillLabel'] for chain in chains}) or 'N/A'}"
                      f" ⇒ 两侧没有交集，不借链凑分母，{pol['naRule']}")
    if not usable:
        return None, (f"{len(links)} 条关联全部观察窗不足：{links[0]['unusableReason']} ⇒ {pol['naRule']}")
    if len(distinct) < int(pol["minChains"]):
        return None, (f"可归属且可观察的复发链只有 {len(distinct)} 条 < minChains={pol['minChains']}"
                      f"（{pol['forbidden'][2]}）⇒ {pol['naRule']}")
    effective = [link for link in usable if link["afterCount"] == 0]
    return len(effective) / len(usable), ""


def measure(root: Path | None = None, pol: dict | None = None) -> dict:
    root = Path(root or Path.cwd()).resolve()
    pol = pol or policy(root)
    records, dropped = _claim_records(root, pol)
    chains, chain_error = _chains(root)
    window = timedelta(days=int(pol["windowDays"]))
    least = timedelta(days=int(pol["minObserveDays"]))
    today = datetime.now().astimezone().date()
    links = []
    for record in records:
        for chain in chains:
            if not chain["skill"] or chain["skill"] not in record["skills"]:
                continue
            start = date.fromisoformat(record["date"])
            after_end = min(today, start + window)
            before = [n for n in chain["nodes"] if start - window <= n["day"] < start]
            after = [n for n in chain["nodes"] if start < n["day"] <= after_end]
            observed = (min(today, after_end) - start).days
            links.append({"record": record["title"][:44], "skill": chain["skill"], "chain": chain["skillLabel"],
                          "since": start.isoformat(), "observedDays": observed,
                          "beforeCount": len(before), "afterCount": len(after),
                          "afterNodes": [n["rel"] for n in after],
                          "usable": observed >= least.days,
                          "unusableReason": (f"观察窗只有 {observed} 天 < minObserveDays={pol['minObserveDays']}"
                                             f" ⇒ 反哺刚生效还没有可看的窗")})
    value, reason = _verdict(pol, records, chains, links, dropped, chain_error)
    usable = [link for link in links if link["usable"]]
    report = {"policy": pol, "records": records, "dropped": dropped, "chains": chains,
              "chainError": chain_error, "links": links, "usable": usable, "value": value, "reason": reason}
    if value is not None:
        report["effective"] = [link["record"] for link in usable if link["afterCount"] == 0]
        report["recurred"] = [link["record"] for link in usable if link["afterCount"]]
    return report


def render(report: dict) -> str:
    pol = report["policy"]
    head = ("N/A —— " + report["reason"]) if report["value"] is None else \
        f"**{report['value']:.1%}**（有效 {len(report.get('effective') or [])}／可归属可观察 {len(report['usable'])}）"
    lines = [f"# {pol['name']}（{pol['pillar']}·{pol['id']}）", "",
             f"- 定义：{pol['definition']}",
             f"- 真相源：{pol['truthSource']}",
             f"- **读数：{head}**",
             f"- 口径闸门：反哺记录 ≥{pol['minRecords']} 条｜可归属链 ≥{pol['minChains']} 条"
             f"｜观察窗 ≥{pol['minObserveDays']} 天｜前/后窗各 {pol['windowDays']} 天", ""]
    lines.append(f"## {pol['detectorRateLabel']}")
    if report["records"]:
        lines += ["| 反哺记录 | 生效日 | before → after | 降幅 | 落账 commit |", "|---|---|---|---|---|"]
        for record in report["records"]:
            drop = (record["before"] - record["after"]) / record["before"] if record["before"] else None
            lines.append(f"| `{record['title'][:44]}` | {record['date']} | {record['before']} → {record['after']} | "
                         f"{f'{drop:.0%}' if drop is not None else 'N/A'} | `{record['commit'][:12] or 'N/A'}` |")
    else:
        lines.append("N/A —— 没有一条台账条目通过「声称生效＋两侧可核＋commit 验真」三道门")
    lines.append(f"- ⚠ {pol['forbidden'][0]}")
    if report["dropped"]:
        lines.append(f"- 落选的台账条目（{len(report['dropped'])} 条，逐条给原因）：")
        lines += [f"  - {item}" for item in report["dropped"][:8]]
    lines += ["", f"## 同型错误（显式复发链，不认标题相似）",
              f"- 链 {len(report['chains'])} 条：" +
              ("、".join(f"{chain['skillLabel']}（节点 {len(chain['nodes'])} 个）" for chain in report['chains'])
               or "N/A（没有显式复发指针连出的链）"),
              f"- 反哺记录 ↔ 链 的可归属关联：{len(report['links'])} 条（其中可观察 {len(report['usable'])} 条）"]
    for link in report["links"][:8]:
        lines.append(f"  - `{link['record']}` × {link['chain']}：自 {link['since']} 已观察 {link['observedDays']} 天"
                     f"｜前窗 {link['beforeCount']} 个节点｜后窗 {link['afterCount']} 个节点"
                     f"{'' if link['usable'] else '｜' + link['unusableReason']}")
    lines += ["", "## 禁止的读法（注册表原文，逐条照抄）",
              *[f"- {item}" for item in pol["forbidden"]],
              f"- {pol['naRule']}",
              "", f"复算（1 条 CLI 调用）：`{pol['recompute']}`"]
    return "\n".join(lines) + "\n"


def write(root: Path, report: dict) -> Path:
    target = Path(root) / str(report["policy"]["report"]["outputFile"])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(report), encoding="utf-8")
    return target
