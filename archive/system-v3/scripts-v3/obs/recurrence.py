"""同型问题复发率 — plan v2 §3「智能化」第二条（§5 闭环里那条「应随反哺下降」）。

口径只有一条：**显式复发指针**。卡片正文里逐字存在的两类写法才算——
①「第 N 次复发」（含「第3次复发」「第三次复发」这类变体）；②「issue/<Skill>/<日期>/<NN>」指回旧卡。

上一版一次性脚本按「标题去掉日期数字后的主干词」聚指纹，实测两头都错，所以这里一条相似度都不做：
`issue/Frontend-Dev/2026-09-16/01`、`02` 是**两个不同问题**，它们的首行是 `# ../../issue/...` 这种自指路径
（没有真正的 `# ` 标题），旧脚本回退用路径当标题，于是把两张并成「同型复发组」（假阳性，跨度还是 0 天）；
而真写了「第 3 次复发」的卡一条没检出（假阴性）。本模块改成：配对只用指针；指针解析不到就如实记
「未解析／歧义／跨 skill／指向更晚／同行无复发记号」，读不动与非日期目录的卡单列计数——
**绝不把「没扫到」写成「没复发」**。反过来，正文出现「复发」二字但没有显式指针的一律不计入，只单列交人裁决。
口径这么窄，报出来的 0 只能读成「卡片里没写显式指针」，报告必须自己把这句话讲清。

判据（语料 glob、窗口天数、指针正则、成链条件、N/A 规则与全部文案）在
`governance/obs-registry.yaml` 的 `recurrence` 节：代码零硬编码常量，键缺失或取值不认识 ⇒ 拒绝开工并报错，
不退回默认值（同 `candidates.policy` / `attribution.policy` 的先例）。语料是历史证据、只读：
本模块不改写任何卡、不新建卡、不要求任何 skill 新产出文档，也不调任何引擎。
"""
from __future__ import annotations
import re
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parents[2]
SHIPPED_REGISTRY = ROOT_DIR / "governance/obs-registry.yaml"
POLICY_KEY = "recurrence"
EDGE = "recurrenceEdge"          # refs[].status 里唯一「计入复发」的那一格，其余都是排除项

# 必需键：少任何一个都拒绝开工（取数口径不完整就是没口径，不猜一套、也不退回实现内的默认值）。
REQUIRED = (
    "id", "name", "pillar", "definition", "truthSource", "recompute", "use", "forbidden",
    "corpus.glob", "corpus.layout", "corpus.skillFrom", "corpus.dateFrom", "corpus.datePattern",
    "corpus.cardPattern", "corpus.excludeFileNames", "corpus.encoding",
    "recognized", "badValueReason",
    "window.days", "window.inclusiveStart", "window.badDaysReason", "window.cutoffPolicy",
    "window.cutoffReason",
    "pointers.ordinal.pattern", "pointers.ordinal.label", "pointers.ordinal.numeralGroup",
    "pointers.ordinal.direction", "pointers.issueRef.pattern", "pointers.issueRef.label",
    "pointers.issueRef.groups", "pointers.issueRef.direction", "pointers.numerals",
    "pointers.missingGroupReason",
    "chain.scope", "chain.order", "chain.requireCue", "chain.cueWords", "chain.snippetField",
    "chain.locationField",
    "rate.label", "rate.numerator", "rate.denominator", "rate.dedupe",
    "report.outputFile", "report.naToken", "report.maxSnippetChars", "report.snippetEllipsis",
    "report.maxListItems",
    "naRule", "reasons", "caveats",
)
# reasons 的每一格都会被写进报告（缺一格就是有一格口径没落纸），caveats 同理
REASON_KEYS = (
    "noCorpus", "noCutoff", "unreadable", "nonDateDir", "irregularName", "excluded", EDGE,
    "unresolved", "ambiguous", "forwardRef", "selfRef", "crossSkill", "cueless",
    "unparsedOrdinal", "ordinalWithoutChain", "zero",
)
CAVEAT_KEYS = ("narrowScope", "notAbsence", "denominatorNote")


def registry_path(root: Path | None = None) -> Path:
    """项目自带的 governance 优先，否则用本仓发布的判据（与 candidates/attribution 同一套取法）。"""
    if root is not None:
        local = Path(root) / "governance/obs-registry.yaml"
        if local.is_file():
            return local
    return SHIPPED_REGISTRY


def _dig(section, dotted: str):
    cursor = section
    for part in str(dotted).split("."):
        if not isinstance(cursor, dict):
            return None
        cursor = cursor.get(part)
    return cursor


def _is_empty(value) -> bool:
    """False 与 0 都是「声明了的值」；只有 None 和空容器才算缺键（`requireCue: false` 是合法口径）。"""
    return value is None or (isinstance(value, (str, list, dict, tuple)) and len(value) == 0)


def policy(root: Path | None = None) -> dict:
    path = registry_path(root)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"复发判据读不动: {path}: {exc}") from exc
    section = data.get(POLICY_KEY)
    if not isinstance(section, dict):
        raise ValueError(f"{path.as_posix()} 未声明 {POLICY_KEY} 判据 ⇒ 不猜口径")
    missing = [key for key in REQUIRED if _is_empty(_dig(section, key))]
    missing += [f"reasons.{key}" for key in REASON_KEYS
                if _is_empty((section.get("reasons") or {}).get(key))]
    missing += [f"caveats.{key}" for key in CAVEAT_KEYS
                if _is_empty((section.get("caveats") or {}).get(key))]
    if missing:
        raise ValueError(f"{path.as_posix()} 的 {POLICY_KEY} 节缺必需键 {missing} ⇒ 拒绝用默认值冒充实装")
    unbound, wrong = [], []
    for key, expect in (section.get("recognized") or {}).items():
        declared = _dig(section, str(key))
        if _is_empty(declared):
            unbound.append(str(key))
        elif str(declared) != str(expect):
            wrong.append(str(section["badValueReason"]).replace("{key}", str(key))
                         .replace("{value}", str(declared)).replace("{expect}", str(expect)))
    if unbound:
        raise ValueError(f"{path.as_posix()} 的 recognized 指向了没声明的键 {unbound} ⇒ 取值闸门自己也不完整")
    if wrong:
        raise ValueError("；".join(wrong))
    raw_days = _dig(section, "window.days")
    try:
        days = int(str(raw_days))
    except (TypeError, ValueError):
        days = 0
    if days <= 0:
        raise ValueError(str(section["window"]["badDaysReason"]).replace("{value}", str(raw_days)))
    section["window"]["days"] = days
    return section


def compile_patterns(pol: dict) -> dict:
    """正则全部来自注册表：编译不过、或声明的命名组不存在 ⇒ 报错，不退回代码自备的一套模式。"""
    patterns = {"date": "corpus.datePattern", "card": "corpus.cardPattern",
                "ordinal": "pointers.ordinal.pattern", "ref": "pointers.issueRef.pattern"}
    out = {}
    for name, key in patterns.items():
        declared = str(_dig(pol, key))
        try:
            out[name] = re.compile(declared)
        except re.error as exc:
            raise ValueError(f"{key} 的正则编译不过：{declared}（{exc}）") from exc
    wanted = {"ref": [str(group) for group in pol["pointers"]["issueRef"]["groups"]],
              "ordinal": [str(pol["pointers"]["ordinal"]["numeralGroup"])]}
    for name, groups in wanted.items():
        for group in groups:
            if group not in out[name].groupindex:
                raise ValueError(str(pol["pointers"]["missingGroupReason"]).replace("{group}", group))
    return out


def _relative(root: Path, path: Path) -> str:
    base = Path(root).resolve()
    try:
        return path.resolve().relative_to(base).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def enumerate_cards(root: Path, pol: dict, rx: dict) -> dict:
    """按 corpus.glob 枚举卡片：日期只取父目录名、skill 只取祖父目录名（都不从正文猜）。"""
    excluded_names = {str(name) for name in pol["corpus"]["excludeFileNames"]}
    cards, unreadable, odd_dirs, odd_names, skipped = [], [], [], [], []
    for path in sorted(Path(root).glob(str(pol["corpus"]["glob"]))):
        if not path.is_file():
            continue
        relative = _relative(root, path)
        if str(path.name) in excluded_names:
            skipped.append(relative)
            continue
        try:
            # 严格解码：坏字节卡片进「读不动」单列，而不是带替换符硬扫——替换符会把指针吃掉，
            # 那种「扫过了」是假绿（注册表 reasons.unreadable：既不计复发也不计未复发）
            text = path.read_text(encoding=str(pol["corpus"]["encoding"]))
        except (OSError, UnicodeError) as exc:
            unreadable.append({"file": relative, "error": str(exc)})
            continue
        day_dir = path.parent.name
        if not rx["date"].fullmatch(day_dir):
            odd_dirs.append({"file": relative, "directory": day_dir})
            continue
        try:
            day = date.fromisoformat(day_dir)
        except ValueError:
            odd_dirs.append({"file": relative, "directory": day_dir})
            continue
        number = rx["card"].match(path.name)
        if not number:
            odd_names.append({"file": relative, "name": path.name})
            continue
        cards.append({"rel": relative, "skill": path.parent.parent.name, "date": day,
                      "card": number.group(1), "lines": text.splitlines()})
    return {"cards": cards, "unreadable": unreadable, "oddDirs": odd_dirs, "oddNames": odd_names,
            "excluded": skipped}


def _snippet(line: str, pol: dict) -> str:
    """指针原文片段：折行折空格、竖线转义（卡片里大量是表格行），超长截断并留省略号。"""
    text = re.sub(r"\s+", " ", str(line)).strip().replace("|", "\\|")
    limit = int(pol["report"]["maxSnippetChars"])
    if len(text) > limit:
        text = text[:limit].rstrip() + str(pol["report"]["snippetEllipsis"])
    return text


def _ordinal_value(numeral: str, pol: dict):
    """只按注册表 pointers.numerals 逐字查表；查不到就返回 None（不猜一个数，也不做算术外推）。"""
    token = str(numeral)
    if token.isdigit():
        return int(token)
    found = (pol["pointers"]["numerals"] or {}).get(token)
    return int(found) if found is not None else None


def _where(rel: str, line: int) -> str:
    return f"{rel}:{line}"


def _classify(card: dict, target: dict, resolved: list, pol: dict, has_cue: bool) -> tuple:
    """一条旧卡引用的判据：解析→非自指→同 skill→严格更早→同行有复发记号，缺一格就不成边。

    返回 (判据格, 解析到的卡片)；每一格的文案都在注册表 reasons 里，代码不现编说法。
    """
    key = (target["skill"].casefold(), target["date"], target["card"])
    if not resolved:
        return "unresolved", None
    if len(resolved) > 1:
        return "ambiguous", None
    if resolved[0] == card["rel"]:
        return "selfRef", resolved[0]
    if key[0] != card["skill"].casefold():
        return "crossSkill", resolved[0]
    # target["date"] 一定是已入基数卡片用过的目录名（enumerate_cards 那边解析过一次），此处直接比先后
    target_day = date.fromisoformat(target["date"])
    if (target_day, target["card"]) >= (card["date"], card["card"]):
        return "forwardRef", resolved[0]
    if bool(pol["chain"]["requireCue"]) and not has_cue:
        return "cueless", resolved[0]
    return EDGE, resolved[0]


def scan_cards(cards: list, pol: dict, rx: dict) -> dict:
    """逐行扫显式指针：序数复发进 claims，旧卡引用进 refs，满足成链判据的同时进 edges。"""
    cues = [str(word) for word in pol["chain"]["cueWords"]]
    ref_groups = [str(group) for group in pol["pointers"]["issueRef"]["groups"]]
    numeral_group = str(pol["pointers"]["ordinal"]["numeralGroup"])
    index: dict = {}
    for card in cards:
        index.setdefault((card["skill"].casefold(), card["date"].isoformat(), card["card"]), []).append(card["rel"])
    edges, claims, refs = [], [], []
    for card in cards:
        for number, line in enumerate(card["lines"], 1):
            on_this_line = []
            for match in rx["ordinal"].finditer(line):
                numeral = match.group(numeral_group)
                claim = {"file": card["rel"], "skill": card["skill"], "position": card["card"],
                         "date": card["date"].isoformat(), "line": number,
                         "where": _where(card["rel"], number), "snippet": _snippet(line, pol),
                         "verbatim": str(match.group(0)), "numeral": numeral,
                         "value": _ordinal_value(numeral, pol), "onPointerLine": False}
                claims.append(claim)
                on_this_line.append(claim)
            has_cue = any(word in line for word in cues)
            for match in rx["ref"].finditer(line):
                target = {group: str(match.group(group)) for group in ref_groups}
                resolved = index.get((target["skill"].casefold(), target["date"], target["card"])) or []
                status, hit = _classify(card, target, resolved, pol, has_cue)
                refs.append({"file": card["rel"], "line": number, "where": _where(card["rel"], number),
                             "snippet": _snippet(line, pol), "targetSkill": target["skill"],
                             "targetDate": target["date"], "targetCard": target["card"], "target": hit,
                             "status": status, "reason": str(pol["reasons"][status])})
                if status == EDGE:
                    edges.append({"source": card["rel"], "target": hit, "line": number,
                                  "where": refs[-1]["where"], "snippet": refs[-1]["snippet"],
                                  "skill": card["skill"]})
                    # 序数只有落在「指针行」上才参与链位核对：旧卡事后补写的「第 3 次复发，见 <更晚的卡>」
                    # 说的是后面那张卡，拿它报链位不符就是误报（真语料里 09-23/01 就是这一形）
                    for claim in on_this_line:
                        claim["onPointerLine"] = True
    return {"edges": edges, "claims": claims, "refs": refs}


def build_chains(edges: list, cards: list) -> list:
    """同一 skill 内被边连起来的卡片成一个连通分量，按 chain.order 升序排成 A→B→C；≥2 张才算一条链。"""
    by_rel = {card["rel"]: card for card in cards}
    parent = {rel: rel for rel in by_rel}

    def find(item: str) -> str:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    nodes = set()
    for edge in edges:
        nodes.update((edge["source"], edge["target"]))
        head, tail = find(edge["source"]), find(edge["target"])
        if head != tail:
            parent[tail] = head
    components: dict = {}
    for rel in nodes:
        components.setdefault(find(rel), set()).add(rel)
    sources = {edge["source"] for edge in edges}
    chains = []
    for members in components.values():
        ordered = sorted((by_rel[rel] for rel in members),
                         key=lambda item: (item["date"], item["card"], item["rel"]))
        chains.append({"skill": ordered[0]["skill"], "hops": len(ordered) - 1,
                       "nodes": [dict(rel=card["rel"], date=card["date"].isoformat(), card_no=card["card"],
                                      recurs=card["rel"] in sources,
                                      pointers=[edge for edge in edges if edge["source"] == card["rel"]])
                                 for card in ordered]})
    for chain in chains:
        for position, node in enumerate(chain["nodes"], 1):
            node["position"] = position
    return chains


def measure(root: Path, pol: dict | None = None) -> dict:
    """跑完整判据：基数 → 扫指针 → 成链 → 窗口 → 复发率。取不到的维度一律 N/A 并写明为什么。"""
    pol = pol or policy(root)
    rx = compile_patterns(pol)
    reasons, report_pol = pol["reasons"], pol["report"]
    na = str(report_pol["naToken"])
    report = {"metric": str(pol["id"]), "name": str(pol["name"]), "pillar": str(pol["pillar"]),
              "definition": str(pol["definition"]).strip(), "truthSource": str(pol["truthSource"]).strip(),
              "recompute": str(pol["recompute"]).strip(), "use": str(pol["use"]).strip(),
              "layout": str(pol["corpus"]["layout"]), "glob": str(pol["corpus"]["glob"]),
              "rateLabel": str(pol["rate"]["label"]), "naToken": na, "value": None, "reason": "",
              "cutoff": None, "windowStart": None, "windowDays": int(pol["window"]["days"]),
              "inclusiveStart": bool(pol["window"]["inclusiveStart"]),
              "cutoffReason": str(pol["window"]["cutoffReason"]),
              "ordinalLabel": str(pol["pointers"]["ordinal"]["label"]),
              "refLabel": str(pol["pointers"]["issueRef"]["label"]),
              "snippetField": str(pol["chain"]["snippetField"]), "locationField": str(pol["chain"]["locationField"]),
              "maxListItems": int(report_pol["maxListItems"]), "outputFile": str(report_pol["outputFile"]),
              "cueWords": [str(word) for word in pol["chain"]["cueWords"]],
              "cards": [], "cardsTotal": 0, "cardsInWindow": 0, "unreadable": [], "oddDirs": [],
              "oddNames": [], "excluded": [], "edges": [], "chains": [], "claims": [], "refs": [],
              "recurrences": [], "recurrencesInWindow": [], "unsupportedClaims": [], "mentions": [],
              "cueCards": 0, "longestHops": 0, "longestNodes": 0, "chainSkillsLabel": "无",
              "allTimeRate": None, "caveats": [], "naRule": str(pol["naRule"]).strip(),
              "forbidden": [str(item) for item in pol["forbidden"]]}
    corpus = enumerate_cards(root, pol, rx)
    cards = corpus["cards"]
    report.update({"cardsTotal": len(cards), "unreadable": corpus["unreadable"],
                   "oddDirs": corpus["oddDirs"], "oddNames": corpus["oddNames"],
                   "excluded": corpus["excluded"], "cards": cards})
    if not cards:
        # 没语料 ≠ 0% 复发：基数都没有还报 0，就是把量具空转的读数当成结论
        report["reason"] = (f"{na}（{reasons['noCorpus']}；另有非日期目录 {len(corpus['oddDirs'])} 个、"
                            f"文件名不合 {len(corpus['oddNames'])} 个、读不动 {len(corpus['unreadable'])} 个）")
        report["caveats"] = [str(pol["caveats"][key]) for key in CAVEAT_KEYS]
        return report

    scanned = scan_cards(cards, pol, rx)
    chains = build_chains(scanned["edges"], cards)
    sources = {edge["source"] for edge in scanned["edges"]}
    chain_nodes = {node["rel"] for chain in chains for node in chain["nodes"]}
    dates = [card["date"] for card in cards]
    cutoff = max(dates)
    start = cutoff - timedelta(days=report["windowDays"] - (1 if report["inclusiveStart"] else 0))
    in_window = [card for card in cards if start <= card["date"] <= cutoff]
    report.update({"edges": scanned["edges"], "chains": chains, "claims": scanned["claims"],
                   "refs": scanned["refs"], "cutoff": cutoff.isoformat(), "windowStart": start.isoformat(),
                   "cardsInWindow": len(in_window),
                   "recurrences": sorted(sources),
                   "recurrencesInWindow": sorted(card["rel"] for card in in_window if card["rel"] in sources)})

    # 次序核对：只有落在「指针行」上的序数才参与链位判定；不在指针行上的序数只作旁证（旧卡常常
    # 事后补写「第 3 次复发，见 <更晚的卡>」，那种序数说的是后面那张卡，拿它报「链位不符」就是误报）
    for claim in scanned["claims"]:
        node = next((item for chain in chains for item in chain["nodes"] if item["rel"] == claim["file"]), None)
        claim["chainPosition"] = node["position"] if node else None
        if claim["onPointerLine"] and node:
            claim["orderCheck"] = ("一致" if claim["value"] == node["position"] else
                                   f"不符：卡内自报第 {claim['value']} 次 ≠ 链位第 {node['position']} 次（不改判，交人核）")
        else:
            claim["orderCheck"] = ""
        if claim["file"] not in chain_nodes:
            entry = dict(claim)
            entry["reason"] = str(reasons["ordinalWithoutChain"])
            report["unsupportedClaims"].append(entry)

    # 「复发」二字出现在正文、但没成边的卡：单列，不计入复发率
    cue_card_set = {card["rel"] for card in cards
                    if any(word in "\n".join(card["lines"]) for word in report["cueWords"])}
    report["cueCards"] = len(cue_card_set)
    for card in cards:
        if card["rel"] in sources or card["rel"] not in cue_card_set:
            continue
        number = next((index for index, line in enumerate(card["lines"], 1)
                       if any(word in line for word in report["cueWords"])), 1)
        report["mentions"].append({"file": card["rel"], "line": number, "where": _where(card["rel"], number),
                                   "snippet": _snippet(card["lines"][number - 1], pol),
                                   "hasClaim": any(claim["file"] == card["rel"] for claim in scanned["claims"])})

    report["longestHops"] = max((chain["hops"] for chain in chains), default=0)
    report["longestNodes"] = max((len(chain["nodes"]) for chain in chains), default=0)
    skills = sorted({chain["skill"] for chain in chains})
    report["chainSkillsLabel"] = "、".join(skills) if skills else f"无（{reasons['zero']}）"
    if report["cardsInWindow"]:
        report["value"] = len(report["recurrencesInWindow"]) / report["cardsInWindow"]
    if report["cardsTotal"]:
        report["allTimeRate"] = len(report["recurrences"]) / report["cardsTotal"]
    if not report["recurrencesInWindow"]:
        report["reason"] = str(reasons["zero"]) if not report["recurrences"] else (
            f"{na}（窗口内 0 张复发卡，但全时窗外有 {len(report['recurrences'])} 张 ⇒ "
            f"复发卡都早于窗口起点 {report['windowStart']}，不是没有复发）")
    report["caveats"] = [str(pol["caveats"][key]) for key in CAVEAT_KEYS]
    if report["unreadable"]:
        report["caveats"].append(f"{len(report['unreadable'])} 张卡读不动 ⇒ {reasons['unreadable']}")
    if report["oddDirs"]:
        report["caveats"].append(f"{len(report['oddDirs'])} 张卡的父目录名不合 datePattern ⇒ {reasons['nonDateDir']}")
    if report["oddNames"]:
        report["caveats"].append(f"{len(report['oddNames'])} 张卡的文件名不合 cardPattern ⇒ {reasons['irregularName']}")
    return report


def _capped(items: list, limit: int) -> tuple:
    return items[:limit], max(len(items) - limit, 0)


def _bucket_lines(report: dict) -> list:
    """没入基数的卡一律单列：读的人要能看出「这里少了什么」，而不是把缺的当成「没复发」。"""
    buckets = []
    if report["excluded"]:
        buckets.append(f"按 excludeFileNames 排除：{', '.join(report['excluded'])}")
    if report["oddDirs"]:
        buckets.append(f"非日期目录：{', '.join(item['file'] for item in report['oddDirs'])}")
    if report["oddNames"]:
        buckets.append(f"文件名不合 cardPattern：{', '.join(item['file'] for item in report['oddNames'])}")
    if report["unreadable"]:
        buckets.append(f"读不动：{', '.join(item['file'] + '（' + item['error'] + '）' for item in report['unreadable'])}")
    if not buckets:
        return []
    return ["", "## 不入基数的卡片（单列，不折进 0、也不折进「没复发」）", *[f"- {item}" for item in buckets]]


def render(report: dict) -> str:
    """一页可核报告：每张判为复发的卡都带「指针原文片段 + 文件:行号」，读数的人能逐条点回去。"""
    na = report["naToken"]
    limit = report["maxListItems"]
    if report["value"] is None:
        head = f"**{report['rateLabel']}：{na}**"
    else:
        head = (f"**{report['rateLabel']}：{report['value']:.1%}**（窗口内 "
                f"{len(report['recurrencesInWindow'])} 张复发卡 / {report['cardsInWindow']} 张卡片）")
    lines = [f"# {report['name']}（{report['metric']}）", "", f"- {head}",
             f"- 定义：{report['definition']}", f"- 用途：{report['use']}",
             f"- 真相源：{report['truthSource']}", f"- 复算：`{report['recompute']}`"]
    if report.get("reason"):
        lines.append(f"- 判定：{report['reason']}")
    if report["cutoff"] is None:
        lines += _bucket_lines(report)
        lines += ["", "## 口径声明", f"- {report['naRule']}",
                  *[f"- {caveat}" for caveat in report["caveats"]],
                  "", "## 配对禁区（注册表 forbidden，代码不实现其中任何一种）",
                  *[f"- {item}" for item in report["forbidden"]]]
        return "\n".join(lines) + "\n"
    lines += [f"- 切点：{report['cutoff']}（{report['cutoffReason']}）",
              f"- 窗口：{report['windowStart']} .. {report['cutoff']}"
              f"（滚动 {report['windowDays']} 天，{'含首尾' if report['inclusiveStart'] else '不含切点当天'}）",
              f"- 语料：{report['cardsTotal']} 张卡（`{report['glob']}`，布局 {report['layout']}，日期取父目录名）"
              f"｜窗口内 {report['cardsInWindow']} 张｜按名单排除 {len(report['excluded'])}｜"
              f"非日期目录 {len(report['oddDirs'])}｜文件名不合 {len(report['oddNames'])}｜"
              f"读不动 {len(report['unreadable'])}",
              f"- 显式复发链：{len(report['chains'])} 条｜最长 {report['longestHops']} 跳"
              f"（最长链 {report['longestNodes']} 张卡）｜涉及 skill：{report['chainSkillsLabel']}",
              f"- 带显式指针、判为复发的卡：窗口内 {len(report['recurrencesInWindow'])} 张｜全时 "
              f"{len(report['recurrences'])} 张（全时占比 {report['allTimeRate']:.1%}）",
              f"- 「{report['ordinalLabel']}」声称未串进链的：{len(report['unsupportedClaims'])} 条（不计入复发率）",
              f"- 正文出现「{'、'.join(report['cueWords'])}」字样的卡：{report['cueCards']} 张｜其中判为复发 "
              f"{len(report['recurrences'])} 张｜其余 {report['cueCards'] - len(report['recurrences'])} 张"
              f"没有显式指针 ⇒ 一律不计入"]
    if report["chains"]:
        lines += ["", "## 复发链（每一跳带指针位置与原文片段）"]
        for order, chain in enumerate(report["chains"], 1):
            lines.append(f"### 链 {order} ｜ {chain['skill']} ｜ {len(chain['nodes'])} 张卡 / {chain['hops']} 跳")
            for node in chain["nodes"]:
                tag = "复发（本卡带指回旧卡的指针）" if node["recurs"] else "链头（本卡没有指回旧卡的指针）"
                lines.append(f"- 第 {node['position']} 次｜{node['date']}｜`{node['rel']}`｜{tag}")
                for edge in node["pointers"]:
                    lines.append(f"  - {report['locationField']} `{edge['where']}` → 指回 `{edge['target']}`")
                    lines.append(f"  - {report['snippetField']} `{edge['snippet']}`")
        checks = [claim for claim in report["claims"] if claim["orderCheck"] and claim["chainPosition"]]
        if checks:
            lines += ["", "## 链位与卡内自报次序的核对（逐字取序数，不符只报不判）",
                      *[f"- `{item['where']}`｜链位第 {item['chainPosition']} 次｜{item['orderCheck']}"
                        for item in checks]]
    if report["unsupportedClaims"]:
        shown, hidden = _capped(report["unsupportedClaims"], limit)
        lines += ["", f"## 未成链的{report['ordinalLabel']}声称（如实报，不计入复发率，交人裁决）",
                  *[f"- `{item['where']}`｜原文「{item['verbatim']}」"
                    f"{'' if item['value'] is not None else '｜' + item['reason']}"
                    f"｜{item['snippet']}" for item in shown]]
        if hidden:
            lines.append(f"- （其余 {hidden} 条未列）")
    others = [ref for ref in report["refs"] if ref["status"] != EDGE]
    if others:
        shown, hidden = _capped(others, limit)
        lines += ["", f"## {report['refLabel']}（不构成复发：逐条写明缺哪一格）",
                  *[f"- `{item['where']}` → `{item['targetSkill']}/{item['targetDate']}/{item['targetCard']}`"
                    f"｜{item['reason']}｜{item['snippet']}" for item in shown]]
        if hidden:
            lines.append(f"- （其余 {hidden} 条未列）")
    if report["mentions"]:
        shown, hidden = _capped(report["mentions"], limit)
        lines += ["", f"## 只有「{'、'.join(report['cueWords'])}」字样、没有显式指针的卡片（不计入复发）",
                  *[f"- `{item['where']}`｜{'卡内另有序数声称' if item['hasClaim'] else '行文提及'}"
                    f"｜{item['snippet']}" for item in shown]]
        if hidden:
            lines.append(f"- （其余 {hidden} 张未列）")
    buckets = _bucket_lines(report)
    lines += buckets
    lines += ["", "## 口径声明", f"- {report['naRule']}",
              *[f"- {caveat}" for caveat in report["caveats"]],
              "", "## 配对禁区（注册表 forbidden，代码不实现其中任何一种）",
              *[f"- {item}" for item in report["forbidden"]]]
    return "\n".join(lines) + "\n"


def write(root: Path, report: dict) -> Path:
    """报告落盘是可选动作（默认只打到 stdout）：指标不改历史证据，也不替人建卡。"""
    target = Path(root) / report["outputFile"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(report), encoding="utf-8")
    return target
