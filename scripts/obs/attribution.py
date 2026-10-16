"""候选问题卡 → 具体 skill 的具体条款（plan v2 §5 闭环后段第一格「归因到具体 skill 的具体条款」）。

上一轮把「检测面 → 候选卡」接上了（`3da6fb4`），卡上有指针但没有归属：谁知道该改哪一条还是靠人回忆。
本模块只做机械反查，全程只读、不改任何正文，也绝不替人判定问题成立。

三条铁律写成代码，不是写在文档里：

1. **每一跳都要能点回原文。** 路径 → 节点/skill 只走注册表反查（`nodes[].paths` glob、卡面 `node`
   字段、issue 池目录段 ↔ `skill-registry` 的 id/legacyAliases 逐字相等），每条命中都带
   `governance/*.yaml:行号` 的出处；条款命中输出 **文件:行区 + 正文原文**，不是标题摘要。
2. **禁止用标题冒充条款，禁止挑「最像的那段」。** needle 必须逐字出现在二级标题段的**正文**里
   （标题行本身命中不算）；不做相似度、不做同义词、不做「大概说的是这段」。
3. **取不到就说取不到。** 没有条款证据就输出「未归因（无条款证据）」并写明哪一跳断了；
   多条命中（多 skill 或多条款）一律「多归属，需人裁决」并**全部列出**，不许自行挑一个当结论。

判据（路由、语料范围、needle、结论口径）全部在 `governance/obs-registry.yaml` 的 `attribution` 节。
"""
from __future__ import annotations
import fnmatch
import re
from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parents[2]
ISSUE_POOL = re.compile(r"^issue/([^/]+)/")


def policy(root: Path | None = None) -> dict:
    """判据只从注册表读；缺节就拒绝开工，不猜一套默认口径出来执法。"""
    from obs import candidates
    path = candidates.registry_path(root)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"归因判据读不动: {path}: {exc}") from exc
    section = data.get("attribution")
    if not isinstance(section, dict):
        raise ValueError(f"{path.as_posix()} 未声明 attribution 判据 ⇒ 不猜口径")
    missing = [key for key in ("routes", "corpus", "kinds", "verdicts", "headingPattern")
               if not section.get(key)]
    if missing:
        raise ValueError(f"{path.as_posix()} 的 attribution 节缺必需键 {missing} ⇒ 拒绝用默认值冒充实装")
    return section


# ── 注册表原文行号：归因要能点回「是哪一行声明让我这么映射的」────────────────────────
def _raw_lines(path: Path) -> list:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def node_declarations(root: Path) -> dict:
    """obs-registry `nodes[]`：id → {skill, paths, line}。line = 该节点声明所在行（出处用）。"""
    from obs import candidates
    path = candidates.registry_path(root)
    rows: dict = {}
    for number, line in enumerate(_raw_lines(path), 1):
        match = re.search(r"^\s*-\s*\{id:\s*(?P<id>[^,]+),\s*skill:\s*(?P<skill>[^,]+),"
                          r"\s*paths:\s*\[(?P<paths>[^\]]*)\]\}", line)
        if not match:
            continue
        paths = [item.strip().strip('"\'') for item in match.group("paths").split(",") if item.strip()]
        rows[match.group("id").strip()] = {"skill": match.group("skill").strip(),
                                           "paths": paths, "file": path.as_posix(), "line": number}
    if not rows:
        # 注册表里 nodes 不是单行 flow 写法时退回 YAML 解析（行号拿不到，出处降级为整节）
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            data = {}
        for node in data.get("nodes") or []:
            if node.get("id"):
                rows[str(node["id"])] = {"skill": str(node.get("skill", "")),
                                         "paths": [str(p) for p in (node.get("paths") or [])],
                                         "file": path.as_posix(), "line": None}
    return rows


def skill_declarations(root: Path) -> dict:
    """skill-registry：可查名（id + legacyAliases，大小写折叠）→ {skill, path, line}。

    只承认「逐字相等（仅折叠大小写）」的别名匹配。目录名差一个字母就不算命中——
    issue 池目录名与本体系 skill 目录名的对应关系由 `shared/problem-recording.md` §2 规定，
    注册表别名是它唯一的机械可核出口，不做前缀/相似度匹配。
    """
    path = (Path(root) / "governance/skill-registry.yaml")
    if not path.is_file():
        path = ROOT_DIR / "governance/skill-registry.yaml"
    names: dict = {}
    current = None
    pending_alias = False
    for number, line in enumerate(_raw_lines(path), 1):
        head = re.match(r"^\s*-\s+id:\s*(?P<id>[^#\s]+)\s*$", line)
        if head:
            current = {"skill": head.group("id").strip(), "path": None,
                       "file": path.as_posix(), "line": number}
            names.setdefault(current["skill"].lower(), current)
            pending_alias = False
            continue
        if current is None:
            continue
        inline = re.match(r"^\s+(?P<key>[A-Za-z]\w*):\s*(?P<value>\S.*)$", line)
        if inline:
            key, value = inline.group("key"), inline.group("value").strip().strip("'\"")
            if key == "path" and current["path"] is None:
                current["path"] = value
            elif key == "legacyAliases":
                for alias in re.findall(r"[A-Za-z0-9_.-]+", value):
                    names.setdefault(alias.lower(), current)
            pending_alias = (key == "legacyAliases")
            continue
        bare = re.match(r"^\s+(?P<key>[A-Za-z]\w*):\s*$", line)
        if bare:
            pending_alias = bare.group("key") == "legacyAliases"
            continue
        if pending_alias:
            item = re.match(r"^\s+-\s+(?P<alias>[^#\s]+)\s*$", line)
            if item:
                names.setdefault(item.group("alias").strip().lower(), current)
                continue
            pending_alias = False
    return {name: row for name, row in names.items() if row.get("path")}


# ── 路由：涉事产物路径 / 卡面 node → skill ────────────────────────────────────────
def _glob_hits_indexed(nodes: dict, relative: str) -> list:
    """nodes[].paths 的 glob 反查。与 metrics.attribute_write 同一 fnmatch 口径，
    但**返回全部命中**：单命中口径是给逐节点指标挑一个落点用的，归因要的是「谁都可能管」。
    """
    portable = str(relative).replace("\\", "/")
    return [(node_id, spec) for node_id, spec in nodes.items()
            if any(fnmatch.fnmatch(portable, pattern) for pattern in spec["paths"])]


def resolve_skills(root: Path, card: dict, pol: dict) -> dict:
    """按注册表声明的路由逐跳反查。返回 {rows, skills, broken}：rows 全部保留，不挑一个。"""
    nodes = node_declarations(root)
    by_skill_id = skill_declarations(root)
    declared = {str(route["id"]): route for route in pol["routes"]}
    rows, broken = [], []

    def add(route_id, skill, node, evidence, detail):
        """skillPath 一律回查 skill-registry 的声明路径；查不到就是不可解析，不猜目录。"""
        declared_path = (by_skill_id.get(str(skill).lower()) or {}).get("path")
        rows.append({"route": route_id, "skill": skill, "skillPath": declared_path,
                     "node": node, "evidence": evidence, "detail": detail})

    if "artifactPathsGlob" in declared:
        route = declared["artifactPathsGlob"]
        hits = 0
        for artifact in card.get("artifacts") or []:
            for node_id, node in sorted(_glob_hits_indexed(nodes, artifact.get("path", "")),
                                         key=lambda row: row[0]):
                hits += 1
                where = f"{node['file']}:{node['line']}" if node["line"] else node["file"]
                add("artifactPathsGlob", node["skill"], node_id,
                    f"{route['source']} @ {where}",
                    f"产物 `{artifact['path']}` 命中该节点声明的 paths glob")
        if not hits:
            broken.append(f"{route['id']}：无命中 —— 涉事产物路径不在任何节点的 paths glob 里"
                          f"（不拿目录名前缀硬凑一个节点）")

    if "runLogNode" in declared:
        route = declared["runLogNode"]
        node = card.get("node")
        if node and node in nodes:
            spec = nodes[node]
            where = f"{spec['file']}:{spec['line']}" if spec["line"] else spec["file"]
            add("runLogNode", spec["skill"], node, f"{route['source']} @ {where}",
                f"卡面 node `{node}`（取自 run-log 事件，不是回忆）反查到该节点声明的 skill")
        elif node:
            broken.append(f"{route['id']}：无命中 —— 卡面 node `{node}` 在 obs-registry 里没有声明")
        else:
            broken.append(f"{route['id']}：无命中 —— 该卡没有 node 字段（见本卡 N/A 说明）")

    if "issuePoolDir" in declared:
        route = declared["issuePoolDir"]
        hits = 0
        for artifact in card.get("artifacts") or []:
            match = ISSUE_POOL.match(str(artifact.get("path", "")).replace("\\", "/"))
            if not match:
                continue
            hits += 1
            directory = match.group(1)
            found = by_skill_id.get(directory.lower())
            if found:
                add("issuePoolDir", found["skill"], None,
                    f"{route['source']} @ {found['file']}:{found['line']}",
                    f"issue 池目录段 `{directory}` 与注册表 id/legacyAliases 逐字相等（折叠大小写）")
            else:
                broken.append(f"{route['id']}：无命中 —— issue 池目录段 `{directory}` "
                              f"在 skill-registry 的 id/legacyAliases 里逐字查不到（不做近似匹配）")
        if not hits:
            broken.append(f"{route['id']}：不适用 —— 涉事产物不是 `issue/<Skill目录名>/…` 的问题池路径")

    skills = []
    for row in rows:
        if row["skill"] not in [item["skill"] for item in skills]:
            skills.append({"skill": row["skill"], "skillPath": row.get("skillPath")})
    return {"rows": rows, "skills": skills, "broken": broken}


# ── 条款：二级标题段的正文逐字命中 ────────────────────────────────────────────────
def _sections_from(lines: list, heading_pattern: str) -> list:
    """把 md 拆成「## 标题 + 到下一个 ## 前的正文」，带行号，便于人点回原文核对。"""
    marks = [(number, line) for number, line in enumerate(lines, 1)
             if re.match(heading_pattern, line)]
    rows = []
    for index, (number, title) in enumerate(marks):
        stop = marks[index + 1][0] if index + 1 < len(marks) else len(lines) + 1
        body = [(line_number, lines[line_number - 1]) for line_number in range(number + 1, stop)]
        rows.append({"heading": title.strip(), "headingLine": number, "endLine": stop - 1,
                     "body": body})
    return rows


def corpus_files(root: Path, skill_path: str, pol: dict) -> list:
    """该 skill 的正文 + 它自己逐字引用到的仓根 shared 契约。窄口径，见注册表注释。"""
    corpus = pol["corpus"]
    files, shared_referenced = [], set()
    skill_dir = (root / str(skill_path)) if skill_path and "${" not in str(skill_path) else None
    if skill_dir is None or not skill_dir.is_dir():
        return []
    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        files.append(skill_md)
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        shared_root = root / "shared"
        for shared in sorted(shared_root.glob("*.md")) if shared_root.is_dir() else []:
            if shared.name in text:                    # 逐字文件名引用才算纳入
                shared_referenced.add(shared)
    for pattern in corpus.get("skillFiles") or []:
        relative = str(pattern).replace("{skillPath}/", "")
        if "*" not in relative:
            continue
        directory, _, leaf = relative.rpartition("/")
        base = (skill_dir / directory) if directory else skill_dir
        files.extend(sorted(base.glob(leaf)))
    files.extend(sorted(shared_referenced))
    unique, seen = [], set()
    for path in files:
        key = path.as_posix()
        if key not in seen and path.is_file():
            seen.add(key)
            unique.append(path)
    return unique


def relative_to(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def expand_needles(pol: dict, kind: str, card: dict) -> tuple:
    """needle 里的 {issueDir} 由卡面指针机械代入；取不到就不带这条 needle（不猜目录名）。"""
    declared = (pol["kinds"].get(kind) or {})
    needles, skipped = [], []
    for needle in declared.get("needles") or []:
        if "{issueDir}" in str(needle):
            directory = None
            for artifact in card.get("artifacts") or []:
                match = ISSUE_POOL.match(str(artifact.get("path", "")).replace("\\", "/"))
                if match:
                    directory = match.group(1)
                    break
            if directory is None:
                skipped.append(f"{needle}（本卡没有 issue 池路径 ⇒ 占位符无可代入值，不拿相近目录冒替）")
                continue
            needles.append(str(needle).replace("{issueDir}", directory))
            continue
        needles.append(str(needle))
    return needles, skipped


def search_clauses(root: Path, skills: list, needles: list, pol: dict) -> list:
    """条款命中 = needle 逐字出现在某二级标题段的**正文**里。标题行命中一律不算。"""
    limit = int(pol.get("maxClauseChars", 900))
    heading_pattern = str(pol["headingPattern"])
    hits, cache = [], {}
    for entry in skills:
        for path in corpus_files(root, entry.get("skillPath"), pol):
            relative = relative_to(root, path)
            if relative not in cache:
                try:
                    cache[relative] = _sections_from(
                        path.read_text(encoding="utf-8", errors="replace").splitlines(),
                        heading_pattern)
                except OSError:
                    cache[relative] = []
            for section in cache[relative]:
                body_text = "\n".join(text for _, text in section["body"])
                for needle in needles:
                    if needle and needle in body_text:
                        hits.append({
                            "skill": entry["skill"], "file": relative,
                            "heading": section["heading"],
                            "startLine": section["headingLine"], "endLine": section["endLine"],
                            "needle": needle,
                            "bodyLines": [f"{relative}:{number}" + "｜" + text
                                          for number, text in section["body"] if text.strip()],
                            "text": body_text.strip()[:limit],
                            "truncated": len(body_text.strip()) > limit,
                        })
                        break                       # 一段只算一条证据，别为多个 needle 重复刷屏
    return hits


def _locate(lines: list, tokens: list):
    """在注册表声明的指针字符串里挑可逐字定位的最具体一段；定位不到就报 N/A，不猜行号。"""
    for token in tokens:
        if not token:
            continue
        for needle in (f"{token}:", f"def {token}", f"- id: {token}", token):
            for index, line in enumerate(lines, 1):
                if needle in line:
                    return index, line
    return None, None


def judge_clause(root: Path, card: dict, pol: dict, cand_pol: dict | None = None) -> list:
    """把判据自己声明的出处（ruleSource / judgeSource）机械解析成 `文件:行号 + 原文`。

    这不是 skill 条款归因（结论桶不因此变绿），它只保证一件事：就算落「未归因」，
    人也有一条能点回原文的路，而不是只剩一句「没找到」。出处字符串来自注册表，不是猜的。
    """
    rows, seen = [], set()
    sources = []
    declared = pol["kinds"].get(card["kind"]) or {}
    if declared.get("ruleSource"):
        sources.append(("注册表声明的判据出处", str(declared["ruleSource"])))
    if cand_pol:
        for surface in card.get("surfaces") or []:
            spec = (cand_pol.get("surfaces") or {}).get(surface) or {}
            for key in ("ruleSource", "judgeSource"):
                if spec.get(key):
                    sources.append((f"检出面 {surface} 的 {key}", str(spec[key])))
    for origin, pointer in sources:
        file_part, _, rest = str(pointer).partition(":")
        pieces = [item for item in rest.replace("\\", "/").split() if item]
        tokens = [piece.rpartition(".")[2].strip("`'\"") for piece in pieces] + pieces + [rest.strip()]
        for candidate in (root / file_part.strip(), ROOT_DIR / file_part.strip()):
            if not candidate.is_file():
                continue
            lines = _raw_lines(candidate)
            number, text = _locate(lines, [token for token in tokens if token])
            key = (relative_to(root, candidate), number, str(pointer))
            if key in seen:
                continue
            seen.add(key)
            rows.append({"origin": origin, "pointer": str(pointer),
                         "file": relative_to(root, candidate), "line": number,
                         "text": (text.strip() if number else
                                  "N/A —— 指针末段在该文件里逐字找不到（不猜行号、不猜原文）")})
            break
    return rows


def attribute_card(root: Path, card: dict, pol: dict | None = None,
                   cand_pol: dict | None = None) -> dict:
    """一张卡 → 归因结论（归因 / 多归属需人裁决 / 未归因）＋可点回原文的证据。"""
    root = Path(root).resolve()
    pol = pol or policy(root)
    verdicts = pol["verdicts"]
    needles, skipped = expand_needles(pol, card["kind"], card)
    resolved = resolve_skills(root, card, pol)
    distinct_skills = [item["skill"] for item in resolved["skills"]]
    clauses = search_clauses(root, resolved["skills"], needles, pol) if needles else []
    distinct_clauses = []
    for clause in clauses:
        key = (clause["file"], clause["startLine"])
        if key not in [(row["file"], row["startLine"]) for row in distinct_clauses]:
            distinct_clauses.append(clause)

    if not needles:
        verdict, why = verdicts["none"], "该 kind 在注册表里没有声明 needle ⇒ 无条款判据可查，不猜"
    elif not resolved["skills"]:
        verdict, why = verdicts["none"], "路径→skill 的每一跳都没命中：" + "；".join(resolved["broken"])
    elif not distinct_clauses:
        verdict, why = verdicts["none"], ("已定位 skill，但 needle 在该 skill 的 SKILL.md/shared 正文里"
                                          "逐字查不到管辖条款 ⇒ 无条款证据（不拿标题或相近段落冒充）")
    elif len(distinct_clauses) > 1 or len(distinct_skills) > 1:
        verdict, why = verdicts["multiple"], (f"条款证据 {len(distinct_clauses)} 处"
                                              f"／归属路由涉及 {len(distinct_skills)} 个 skill ⇒ 全部列出")
    else:
        verdict, why = verdicts["attributed"], "唯一条款证据"
    declared = (pol["kinds"].get(card["kind"]) or {})
    return {"verdict": verdict, "why": why, "needles": needles, "skippedNeedles": skipped,
            "routes": resolved["rows"], "skills": resolved["skills"],
            "brokenRoutes": resolved["broken"], "clauses": distinct_clauses,
            "judgeSources": judge_clause(root, card, pol, cand_pol),
            "corpusFiles": sorted({relative_to(root, path) for entry in resolved["skills"]
                                   for path in corpus_files(root, entry.get("skillPath"), pol)}),
            "basis": str(declared.get("basis", "")),
            "codeEnforcedBy": str(declared.get("codeEnforcedBy", "")),
            "recompute": str(pol["recompute"])}


def attribute_all(root: Path, cards: list, pol: dict | None = None,
                  cand_pol: dict | None = None) -> dict:
    """整批归因 + 三分类计数。只读；不改卡面已有字段之外的东西。"""
    root = Path(root).resolve()
    pol = pol or policy(root)
    buckets = {key: 0 for key in pol["verdicts"].values()}
    counts = {"cards": 0, "noSkill": 0, "clauses": 0, "multiSkillCards": 0}
    distinct: list = []
    for card in cards:
        result = attribute_card(root, card, pol, cand_pol)
        card["attribution"] = result
        buckets[result["verdict"]] = buckets.get(result["verdict"], 0) + 1
        counts["cards"] += 1
        counts["clauses"] += len(result["clauses"])
        for clause in result["clauses"]:
            key = (clause["file"], clause["startLine"])
            if key not in distinct:
                distinct.append(key)
        if not result["skills"]:
            counts["noSkill"] += 1
        if len(result["skills"]) > 1:
            counts["multiSkillCards"] += 1
    counts["distinctClauses"] = len(distinct)
    counts["distinctClauseFiles"] = sorted({name for name, _ in distinct})
    buckets["cards"] = counts["cards"]
    return {"buckets": buckets, "counts": counts, "policy": pol}


# ── 卡面渲染：归因段接在候选卡里，指针能一路点到原文 ──────────────────────────────
def render_block(attribution: dict) -> str:
    lines = ["## 归因（候选·未经确认：这一步只把指针反查到条款，不等于问题成立，也不等于该改这条）", ""]
    lines.append(f"- 结论：**{attribution['verdict']}** ｜ 依据：{attribution['why']}")
    if attribution.get("basis"):
        lines.append(f"- needle 出处（判据原文的 operative 词）：{attribution['basis']}")
    lines.append(f"- 查条款用的 needle（逐字匹配，非相似）：{attribution['needles'] or 'N/A（注册表未声明）'}")
    for item in attribution.get("skippedNeedles") or []:
        lines.append(f"- needle 降级：{item}")
    lines.append("")
    if attribution["routes"]:
        lines += ["### 路径 → 节点/skill 反查（每一跳都能点回注册表）", "",
                  "| 路由 | skill | 节点 | 出处（注册表原文行） | 为什么算命中 |", "|---|---|---|---|---|"]
        for row in attribution["routes"]:
            lines.append(f"| {row['route']} | `{row['skill']}` | {row['node'] or 'N/A'} "
                         f"| `{row['evidence']}` | {row['detail']} |")
        lines.append("")
    for item in attribution.get("brokenRoutes") or []:
        lines.append(f"- 断掉的一跳：{item}")
    if attribution.get("brokenRoutes"):
        lines.append("")
    if attribution["clauses"]:
        lines += ["### 管辖该判据的条款原文（按正文逐字命中，不是标题摘要）", ""]
        for clause in attribution["clauses"]:
            limit = 120
            lines.append(f"- **{clause['file']}:{clause['startLine']}-{clause['endLine']}**"
                         f" ｜ skill `{clause['skill']}` ｜ 命中词 `{clause['needle']}`"
                         f" ｜ 标题行 {clause['heading'][:limit]}（标题本身不算证据，证据见下面正文）")
            lines.append("")
            for row in clause["bodyLines"]:
                lines.append(f"    {row}")
            lines.append("")
        if len(attribution["clauses"]) > 1:
            lines.append("> **多归属，需人裁决**：上面每一处都是逐字命中的候选责任条款，"
                         "工具不替人挑「最像的那个」。")
            lines.append("")
    else:
        lines += ["### 条款证据", "",
                  "无 —— 没有可证据化的条款，所以本卡落「未归因」。"
                  "下面只说明判据实际由谁执法，方便人去核，不构成归因结论。", ""]
    if attribution.get("corpusFiles"):
        lines.append(f"- 查条款用过的正文语料（{len(attribution['corpusFiles'])} 个文件，"
                     f"窄口径：该 skill 的 SKILL.md/shared + 它逐字引用到的仓根 shared）："
                     f"{'、'.join(f'`{name}`' for name in attribution['corpusFiles'])}")
    if attribution.get("judgeSources"):
        lines += ["", "### 判据实际出处（注册表声明，可点回原文；**不是** skill 条款归因）", ""]
        for row in attribution["judgeSources"]:
            where = f"{row['file']}:{row['line']}" if row["line"] else f"{row['file']}（行号 N/A）"
            lines.append(f"- {row['origin']} → `{row['pointer']}` @ `{where}`")
            lines.append(f"    原文｜{row['text'][:300]}")
    if attribution.get("codeEnforcedBy"):
        lines.append(f"- 该判据的执法位置（仅供核对，不是条款归因）：`{attribution['codeEnforcedBy']}`")
    lines.append(f"- 复算归因：`{attribution['recompute']}`")
    return "\n".join(lines) + "\n"
