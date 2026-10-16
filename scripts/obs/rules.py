"""规则命中率 — 智能化指标：SKILL.md / shared 条款被真实读取或引用的比例。

plan v2 §3 里唯一没落地的智能化指标。用途是把「哪些 skill 正文该精简」从拍脑袋变成可复算
的数字：命中证据只来自**被采到的 session**，而宿主把 skill 正文注入上下文时不留日志，
所以报出来的一定是**下界**——低命中只说明「轨迹里没有证据」，不证明条款没用，报告必须写清。

宿主无关是继承来的，不是在本模块重复实现：这里只见 `host_spec.cap_records()` 投影出的
`{path, offset, limit, text}`，字段名与工具名留在 `governance/host-specs/<host>.yaml`；
口径（所需 capability、语料基数、N/A 规则）留在 `governance/obs-registry.yaml` 的 metrics 节。
取不到的维度一律 N/A 并写明原因，禁止用估算或默认值冒充实测。
"""
from __future__ import annotations
import re
from datetime import datetime
from pathlib import Path

import yaml

from obs import host_spec

REGISTRY = Path(__file__).resolve().parents[2] / "governance/obs-registry.yaml"
HEADING = re.compile(r"^##(?!#)\s+(.+?)\s*$")
EOF = 10 ** 9


def _yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def metric_spec(metric_id: str = "rule_hit_rate") -> dict:
    """The registry is the single source for the metric's scope; a missing entry is an error.

    Falling back to hard-coded defaults here would let the code and the registry drift, and
    the board would then report a number whose口径 nobody registered.
    """
    for entry in (_yaml(REGISTRY).get("metrics") or []):
        if str(entry.get("id")) == metric_id:
            return entry
    raise ValueError(f"{metric_id!r} is not registered in governance/obs-registry.yaml (metrics)")


def _normalise(text) -> str:
    """Fold a heading to a citation needle: drop list numbering, punctuation, case and spacing."""
    text = re.sub(r"^\s*[0-9]+(?:\.[0-9]+)*[.、)：:]?\s*", "", str(text))
    text = text.strip("`*—－-:： 　\t")
    return re.sub(r"\s+", " ", text).casefold()


def enumerate_clauses(relative: str, text: str, min_cite_chars: int = 4) -> list:
    """Split a document into its `##` sections; frontmatter and fenced blocks declare no clause.

    A `## ` line inside a code fence is example content, not a rule — SKILL.md templates are
    full of them, so counting those would inflate the denominator with clauses nobody wrote.
    `min_cite_chars` is 4 because these bodies are Chinese: 4 chars is a normal heading length,
    and the narrowing comes from requiring the file pointer in the same argument, not from length.
    """
    lines = text.splitlines()
    clauses, headings, fence, front = [], [], False, bool(lines and lines[0].strip() == "---")
    for index, line in enumerate(lines, 1):
        if front:
            if index > 1 and line.strip() == "---":
                front = False
            continue
        if line.strip().startswith("```") or line.strip().startswith("~~~"):
            fence = not fence
            continue
        if fence:
            continue
        match = HEADING.match(line)
        if match:
            headings.append((index, match.group(1).strip()))
    for position, (start, title) in enumerate(headings):
        end = headings[position + 1][0] - 1 if position + 1 < len(headings) else len(lines)
        needle = _normalise(title)
        clauses.append({"id": f"{relative} § {title}", "file": relative, "heading": title,
                        "norm": needle, "start": start, "end": end,
                        "citable": len(needle) >= min_cite_chars})
    return clauses


def _skill_dir(relative: str) -> str:
    parts = [part for part in relative.split("/") if part]
    return parts[-2] if len(parts) >= 2 else ""


def build_corpus(root: Path, metric: dict, skills=None) -> dict:
    """Enumerate the clause base from the declared corpus sources — never from a guess."""
    clauses, missing, sources = [], [], []
    min_chars = int(metric.get("minCiteChars") or 4)
    wanted_files = {str(s) for s in (skills or [])}
    for source in metric.get("corpus") or []:
        if source.get("from") == "skill-registry":
            ledger = root / "governance/skill-registry.yaml"
            if not ledger.is_file():
                missing.append(f"语料源不可枚举：{ledger.relative_to(root).as_posix()} 不存在")
                continue
            status = str(source.get("status") or "")
            for entry in _yaml(ledger).get("skills") or []:
                ident = str(entry.get("id", ""))
                if status and str(entry.get("status")) != status:
                    continue
                if wanted_files and ident not in wanted_files and _skill_dir(str(entry.get("path", ""))) not in wanted_files:
                    continue
                relative = f"{str(entry.get('path', '')).strip('/')}/{str(source.get('file', 'SKILL.md'))}"
                _absorb(root, relative, clauses, missing, min_chars)
            sources.append(f"skill-registry[{status or 'any'}] 的 {source.get('file')}")
        elif source.get("glob"):
            for path in sorted(root.glob(str(source["glob"]))):
                _absorb(root, path.relative_to(root).as_posix(), clauses, missing, min_chars)
            sources.append(f"glob {source['glob']}")
    files = {}
    for clause in clauses:
        files.setdefault(clause["file"], {"clauses": []})["clauses"].append(clause)
    for relative, entry in files.items():
        is_skill = relative.casefold().endswith("skill.md")
        entry["skill"] = _skill_dir(relative) if is_skill else "shared"
        entry["isSkill"] = is_skill
        # 读取按尾路径匹配（安装副本比仓内少一层分类目录）；引用必须「文件指针 + 标题原文」同现于一条参数。
        # SKILL.md 的指针带目录段：否则 "workflow"+"skill.md"+"Outputs" 三个通用词就能伪造一次引用。
        entry["matchKeys"] = ["/".join(relative.split("/")[-2:])] if is_skill else [relative]
        entry["citeKeys"] = [_normalise(key) for key in entry["matchKeys"]]
    return {"clauses": clauses, "files": files, "missing": missing, "sources": sources}


def _absorb(root: Path, relative: str, clauses: list, missing: list, min_chars: int) -> None:
    target = root / relative
    if not target.is_file():
        missing.append(f"语料文件不可读：{relative}")
        return
    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        missing.append(f"语料文件不可读：{relative}（{exc}）")
        return
    clauses.extend(enumerate_clauses(relative, text, min_chars))


def match_file(observed, files: dict):
    """Resolve a host-side path to a corpus file across both layouts (repo has a category layer)."""
    portable = str(observed or "").replace("\\", "/").casefold().rstrip("/")
    if not portable:
        return None
    for relative, entry in files.items():
        for key in entry["matchKeys"]:
            needle = key.casefold()
            if portable.endswith("/" + needle) or portable == needle:
                return relative
    return None


def _line_range(record: dict):
    """(start, end) of an observed read; None ⇒ the host logged no range, so the whole file."""
    offset, limit = _int(record.get("offset")), _int(record.get("limit"))
    if offset is None and limit is None:
        return None, None
    start = offset if offset is not None else 1
    return start, (start + limit - 1) if limit else EOF


def _int(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def read_hits(records: list, corpus: dict) -> tuple:
    """Clause-level read evidence: a ranged read only credits the clauses it actually covered."""
    hits, files_read = {}, {}
    for record in records:
        relative = match_file(record.get("path"), corpus["files"])
        if relative is None:
            continue
        files_read[relative] = files_read.get(relative, 0) + 1
        start, end = _line_range(record)
        for clause in corpus["files"][relative]["clauses"]:
            if start is not None and not (clause["start"] <= end and clause["end"] >= start):
                continue
            hits.setdefault(clause["id"], 0)
            hits[clause["id"]] += 1
    return hits, files_read


def cite_hits(records: list, corpus: dict) -> tuple:
    """Clause-level cite evidence: heading text co-occurring with its file pointer in one argument."""
    hits, text_events = {}, 0
    for record in records:
        text = _normalise(record.get("text") or "")
        if not text:
            continue
        text_events += 1
        for relative, entry in corpus["files"].items():
            if not all(key in text for key in entry["citeKeys"]):
                continue
            for clause in entry["clauses"]:
                if clause["citable"] and clause["norm"] in text:
                    hits.setdefault(clause["id"], 0)
                    hits[clause["id"]] += 1
    return hits, text_events


def _moment(value):
    """只认带时区的 ISO-8601 时刻：naive 字符串要猜时区，猜了就把别处的事件算进本窗口。"""
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def apply_window(spans: list, since=None, until=None) -> dict:
    """按时间切点收窄证据面（固定口径的第三条腿：全量＋slug＋切点）。

    没有 ts 或 ts 读不懂的事件一律排除并单独计数：无法证明它落在窗口内，就不能把它算进分子。
    """
    if since and _moment(since) is None:
        raise ValueError(f"--since `{since}` 不是带时区的 ISO-8601 时刻 ⇒ 不猜时区，窗口拒绝生效")
    if until and _moment(until) is None:
        raise ValueError(f"--until `{until}` 不是带时区的 ISO-8601 时刻 ⇒ 不猜时区，窗口拒绝生效")
    low, high = _moment(since), _moment(until)
    kept, outside, unusable = [], 0, 0
    for span in spans:
        moment = _moment(span.get("ts"))
        if moment is None:
            unusable += 1
            continue
        if (low is not None and moment < low) or (high is not None and moment > high):
            outside += 1
            continue
        kept.append(span)
    return {"spans": kept, "since": str(since or ""), "until": str(until or ""),
            "total": len(spans), "outside": outside, "unusable": unusable}


def measure(root: Path, spec: dict, spans: list, skills=None, capabilities: dict = None,
            metric_id: str = "rule_hit_rate", window: dict = None, params: dict = None) -> dict:
    """Compute the hit rate for one host's spans, degrading to N/A whenever a field is missing."""
    metric = metric_spec(metric_id)
    if window:
        spans = window["spans"]
    caps = capabilities if capabilities is not None else host_spec.verify_capabilities(spec, spans)
    report = {"metric": metric_id, "name": str(metric.get("name", metric_id)),
              "definition": str(metric.get("definition", "")).strip(),
              "use": str(metric.get("use", "")).strip(), "value": None, "reason": "",
              "declared": 0, "hits": 0, "readHits": 0, "citeHits": 0,
              "files": [], "misses": [], "channels": {}, "evidence": {}, "caveats": [],
              "capabilities": caps, "scope": {"skills": sorted(skills) if skills else "全部注册 skill"},
              "window": ({key: value for key, value in window.items() if key != "spans"}
                         | {"kept": len(spans)} if window else None),
              "params": dict(params or {})}
    for cap in (metric.get("capabilities") or {}).get("required") or []:
        info = caps.get(cap) or {}
        if not info.get("granted"):
            report["reason"] = (f"N/A (未授予 {cap}：{info.get('reason') or '宿主 spec 未声明该能力'}。"
                                f"若本次带了 --sample，先分清是抽样窗口内没出现该字段，还是宿主真不提供——"
                                f"用 --sample 0 复算再下结论)")
            return report
    corpus = build_corpus(root, metric, skills)
    report["caveats"] = [str(metric.get("bias", "")).strip()]
    report["sources"] = corpus["sources"]
    report["missing"] = corpus["missing"]
    if skills:
        report["caveats"].append("--skill 只收窄 SKILL.md 语料源；shared/*.md 为全部 skill 共用，仍整体计入分母")
    if not corpus["clauses"]:
        report["reason"] = "N/A (条款基数为 0：" + ("; ".join(corpus["missing"]) or "未枚举到任何 ## 条款") + ")"
        return report
    if corpus["missing"]:
        report["caveats"].append("分母不完整（读取失败的语料文件已排除，不补估）：" + "; ".join(corpus["missing"]))

    declared = metric.get("capabilities") or {}
    read_cap = str(declared.get("readChannel") or "")
    if not read_cap:
        report["reason"] = "N/A (obs-registry 未声明读取通道用哪个 capability)"
        return report
    records = host_spec.cap_records(spec, spans, read_cap)
    reads, files_read = read_hits(records, corpus)
    report["evidence"] = {"sessions": len({span.get("session") for span in spans}), "spans": len(spans),
                          "readEvents": len(records), "matchedReads": sum(files_read.values())}

    channels = {}
    cites, text_events = {}, 0
    for name in [str(item) for item in (declared.get("citeChannels") or [])]:
        info = caps.get(name) or {}
        if info.get("granted"):
            found, events = cite_hits(host_spec.cap_records(spec, spans, name), corpus)
            cites.update(found)
            text_events += events
            channels[name] = {"granted": True, "reason": str(info.get("reason") or "")}
        else:
            channels[name] = {"granted": False,
                              "reason": f"N/A ({info.get('reason') or '适配器未授予该能力'})；引用通道未参与"}
            report["caveats"].append(f"{name} 取不到 ⇒ 本数字是「仅读取通道」口径，不得当两通道命中率引用")
    report["channels"] = channels
    report["evidence"]["textEvents"] = text_events

    hit_ids = set(reads) | set(cites)
    clauses = corpus["clauses"]
    report.update({"declared": len(clauses), "hits": len(hit_ids),
                   "readHits": len(reads), "citeHits": len(cites),
                   "value": len(hit_ids) / len(clauses)})
    files = []
    for relative, entry in sorted(corpus["files"].items()):
        own = entry["clauses"]
        hit = [clause for clause in own if clause["id"] in hit_ids]
        files.append({"file": relative, "skill": entry["skill"], "clauses": len(own),
                      "readHits": sum(1 for c in own if c["id"] in reads),
                      "citeHits": sum(1 for c in own if c["id"] in cites),
                      "hits": len(hit), "rate": len(hit) / len(own), "readEvents": files_read.get(relative, 0)})
    report["files"] = files
    report["misses"] = [{"id": clause["id"], "file": clause["file"], "heading": clause["heading"],
                         "citable": clause["citable"]} for clause in clauses if clause["id"] not in hit_ids]
    # 零命中留空原因并给 0.0：那是实测结果，写成 N/A 就把「没人读」伪装成「没数据」，
    # 精简永远拿不到依据；反过来，取不到的维度在上面已经 return 成 N/A 了。
    return report


def render(report: dict, top: int = 12) -> str:
    lines = [f"# {report['name']}（{report['metric']}）", ""]
    value = report.get("value")
    head = f"N/A（{report['reason']}）" if value is None else f"{value:.1%}"
    lines += [f"- **命中率：{head}**",
              f"- 定义：{report['definition']}",
              f"- 用途：{report['use']}"]
    if value is None:
        # N/A 也要写清差在哪一环：只留一个 N/A，读数的人分不清是没数据还是零命中，就会去猜
        lines += [f"- 判定见适配器 capability 报告：{'、'.join(sorted(report.get('capabilities') or {})) or '无'}"]
        return "\n".join(lines) + "\n"
    lines.append(f"- 条款基数 {report['declared']} 条｜命中 {report['hits']} 条"
                 f"（读取 {report['readHits']}、引用 {report['citeHits']}，并集去重）")
    evidence = report.get("evidence") or {}
    if evidence:
        lines.append("- 证据面：" + "，".join(f"{key} {count}" for key, count in sorted(evidence.items())))
    window = report.get("window")
    if window:
        lines.append(f"- 时间切点：`{window['since'] or 'N/A（未设）'}` → `{window['until'] or 'N/A（未设）'}`"
                     f"｜窗口内 {window['kept']} / 共 {window['total']} 条事件"
                     f"（窗口外排除 {window['outside']}，无 ts 或读不懂 ts 而排除 {window['unusable']}——"
                     f"证明不了落在窗口内就不算进分子）")
    if report.get("sources"):
        lines.append("- 语料来源：" + "；".join(report["sources"]))
    channels = report.get("channels") or {}
    if channels:
        lines.append("- 通道：" + "；".join(
            f"{name} {'参与' if info['granted'] else info['reason']}" for name, info in channels.items()))
    lines.append("- ⚠ 下界口径：只统计被采到的 session，未采到的语料按未命中计；禁止当上界引用。")
    lines += ["", "## 命中率最低的文件（单读数观察名单，不构成删减依据）",
              "",
              "本表只有一个读数＝规则命中率。删减结论必须由 `tsr slim` 同时给出三个读数"
              "（规则命中率＋条款证据覆盖率＋承接集中度）才允许开口，且集中度过阈值时它会机械拒绝。",
              "", "| 文件 | skill | 条款 | 读取 | 引用 | 命中率 |", "|---|---|---|---|---|---|"]
    ranked = sorted(report.get("files") or [], key=lambda item: (item["rate"], -item["clauses"]))
    for entry in ranked[:top]:
        lines.append(f"| {entry['file']} | {entry['skill']} | {entry['clauses']} | {entry['readHits']} "
                     f"| {entry['citeHits']} | {entry['rate']:.0%} |")
    misses = report.get("misses") or []
    if misses:
        lines += ["", f"## 未命中的条款（共 {len(misses)} 条，示例 20 条）",
                  *[f"- {item['id']}" for item in misses[:20]]]
    if report.get("caveats"):
        lines += ["", "## 口径声明", *[f"- {caveat}" for caveat in report["caveats"] if caveat]]
    if report.get("missing"):
        lines += ["", "## 分母缺口", *[f"- {item}" for item in report["missing"]]]
    return "\n".join(lines) + "\n"
