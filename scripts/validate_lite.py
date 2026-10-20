#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_lite.py —— v4 骨架轻量校验（纯标准库，Python 3.10+，目标 <5 秒）。

查 6 类（口径唯一来源：.tmp-v4/BRIEF.md §3 文件清单 + §4 统一约定；PLAN.md §7）：
① 技能结构 + 根目录骨架：根目录必需项、可见项 ≤10；核心 10 个 skills/<id>/SKILL.md；
   frontmatter 仅 name/description、name=目录名、description ≤60 字；固定五节逐字且顺序固定
   （厚收 auto-test/review/acceptance 可在五节后追加 ≤2 节）；行数预算；shared 4 份；
   issue 模板、bug-patterns、根 README/WORKFLOW 行数。
② 引用可达：仓内 Markdown 的相对链接（跳过代码块与占位符，排除 archive/）目标必须存在，
   且不得写绝对路径、不得越出仓库。
③ 问题卡字段：issue/NNN-slug.md 的 frontmatter 必填字段/枚举/日期 + 正文固定四节。
④ loop-log 表头：11 列逐字 + 表头分隔行。
⑤ 报告模板必需字段：review-report / acceptance-report 的标题、结论三值、sha256、签收。
⑥ installer core 清单：CORE_PROFILE 恰为核心 10 个 id、--profile core|all 默认 core、
   发现排除 archive/；--list --profile core 与 --dry-run 冒烟（只读，不写仓）。

输出：逐项 PASS / FAIL，FAIL 带文件:行号级原因；有 FAIL 时 exit 1，全部 PASS exit 0。
用法：python scripts/validate_lite.py
"""

from __future__ import annotations

import contextlib
import datetime as dt
import importlib.util
import io
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path
from types import ModuleType
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
BT = chr(96)  # 反引号：用来拼代码块/行内代码的 Markdown 语法，避免源码难读

# ---------------------------------------------------------------------------
# 口径常量（与 BRIEF §3/§4 一一对应；改口径先改 BRIEF）
# ---------------------------------------------------------------------------

# skills/<id>/SKILL.md 行数上限（含 frontmatter 与空行，BRIEF §2 铁律 7）
SKILL_BUDGETS: dict[str, int] = {
    "workflow": 120,
    "onboarding": 100,
    "requirements": 100,
    "tech-design": 100,
    "backend-dev": 100,
    "frontend-dev": 100,
    "auto-test": 150,
    "review": 180,
    "acceptance": 150,
    "bug-fix": 100,
}
THICK_SKILLS = ("auto-test", "review", "acceptance")
FIVE_SECTIONS = ("何时用", "交付物", "验收判据", "停等点", "证据要求")

ROOT_REQUIRED = (
    "README.md", "WORKFLOW.md", "PLAN.md", "loop-log.md",
    "skills", "shared", "issue", "bug-patterns", "scripts", "archive",
)
ROOT_DOC_BUDGETS = {"README.md": 150, "WORKFLOW.md": 100}
SHARED_REQUIRED = (
    "skill-authoring.md", "review-contract.md", "acceptance-contract.md", "issue-loop.md",
)

ISSUE_FIELDS = ("id", "type", "skill", "severity", "status", "found", "verifiedBy")
ISSUE_TYPES = {"skill", "project", "env", "process"}
ISSUE_SEVERITIES = {"P0", "P1", "P2"}
ISSUE_STATUSES = {"open", "fixed", "verified", "closed"}
ISSUE_SECTIONS = ("现象", "证据", "影响", "建议改动")
ISSUE_NAME_PATTERN = re.compile(r"^\d{3}-[a-z0-9][a-z0-9-]*\.md$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

LOOP_LOG_HEADER = (
    "| 日期 | 任务 | 时长 | 返工 | 介入 | 评审发现数 | 一次通过 | 新增问题 | 已修复 | 复发 | Skill 改动 |"
)

REVIEW_REPORT = "skills/review/templates/review-report.md"
REVIEW_REPORT_HEADINGS = (
    "0. 隔离信息", "1. 评审包与判据", "2. 证据核对",
    "3. AC 逐条核对", "4. 问题清单", "5. 结论",
)
REVIEW_REPORT_RULES = {
    "5. 结论": (("ACCEPT", "放行"), ("FIX", "可修后复验"), ("REJECT", "阻塞")),
}
ACCEPTANCE_REPORT = "skills/acceptance/templates/acceptance-report.md"
ACCEPTANCE_REPORT_HEADINGS = (
    "0. 任务与范围", "1. DoD 核对", "2. 证据核验", "3. 遗留风险与豁免", "4. 结论",
)
ACCEPTANCE_REPORT_RULES = {
    "2. 证据核验": (("sha256", "文件指纹"),),
    "4. 结论": (("ACCEPT", "放行"), ("FIX", "可修后复验"), ("REJECT", "阻塞"), ("签收", "owner 签收")),
}

INSTALLER = "scripts/install-skills.py"
EXPECTED_CORE = sorted(SKILL_BUDGETS.keys())

LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\s*\)")
INLINE_CODE_PATTERN = re.compile(BT + r"[^" + BT + r"\n]*" + BT)
HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->")
FENCE_PATTERN = re.compile(r"^(" + BT + r"{3,}|~{3,})")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
ABSOLUTE_WIN_PATTERN = re.compile(r"^[A-Za-z]:[\\/]")
LIST_ID_PATTERN = re.compile(r"^\s{2}(\S+)\s+skills/", re.MULTILINE)
DETAIL_LIMIT = 30


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------

def rel_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def loc(path: Path, lineno: int | None = None) -> str:
    text = rel_path(path)
    return "{}:{}".format(text, lineno) if lineno else text


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig", errors="replace").splitlines()


def count_lines(path: Path) -> int:
    return len(read_lines(path))


def strip_quotes(value: str) -> str:
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1].strip()
    return text


class Reporter:
    """逐项打印 PASS / FAIL；FAIL 带文件:行号级原因。"""

    def __init__(self) -> None:
        self.total = 0
        self.failed = 0

    def group(self, title: str) -> None:
        print("\n" + title)

    def item(self, label: str, issues: list[str]) -> None:
        self.total += 1
        if not issues:
            print("  PASS {}".format(label))
            return
        self.failed += 1
        print("  FAIL {}".format(label))
        shown = issues if len(issues) <= DETAIL_LIMIT else issues[:DETAIL_LIMIT]
        for issue in shown:
            print("       - {}".format(issue))
        if len(issues) > DETAIL_LIMIT:
            print("       - ……其余 {} 条已省略".format(len(issues) - DETAIL_LIMIT))


def parse_frontmatter_lines(
    path: Path, lines: list[str]
) -> tuple[dict[str, tuple[str, int]], int, list[str]]:
    """最小解析 frontmatter：返回 (字段 -> (值, 行号), 正文起始下标, 问题列表)。

    只认顶层 key: value 单行；闭合并忽略注释行与空行；不依赖 PyYAML。
    """
    problems: list[str] = []
    if not lines or lines[0].strip() != "---":
        return {}, 0, ["{} frontmatter 缺失：第 1 行必须是 ---".format(loc(path, 1))]
    fields: dict[str, tuple[str, int]] = {}
    for index in range(1, len(lines)):
        raw = lines[index]
        if raw.strip() == "---":
            return fields, index + 1, problems
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            problems.append("{} frontmatter 行不是 key: value：{!r}".format(
                loc(path, index + 1), raw.strip()))
            continue
        key, _, value = raw.partition(":")
        fields[key.strip()] = (value.strip(), index + 1)
    problems.append("{} frontmatter 没有闭合的 ---".format(loc(path, 1)))
    return {}, 0, problems


def scan_headings(lines: list[str], start: int = 0) -> list[tuple[int, int, str]]:
    """扫描 Markdown 标题，跳过代码块，返回 (1-based 行号, 级别, 标题文本)。"""
    headings: list[tuple[int, int, str]] = []
    fence = None
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        fence_match = FENCE_PATTERN.match(stripped)
        if fence_match:
            marker = fence_match.group(1)[0]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is not None:
            continue
        heading = HEADING_PATTERN.match(stripped)
        if heading:
            headings.append((index + 1, len(heading.group(1)), heading.group(2).strip()))
    return headings


# ---------------------------------------------------------------------------
# ① 技能结构与根目录骨架
# ---------------------------------------------------------------------------

def check_skill(rep: Reporter, skill_id: str, budget: int) -> None:
    path = ROOT / "skills" / skill_id / "SKILL.md"
    if not path.is_file():
        return
    lines = read_lines(path)
    rel = "skills/{}/SKILL.md".format(skill_id)

    # frontmatter：仅两键 name/description；name=目录名；description ≤60 字
    fields, body_start, problems = parse_frontmatter_lines(path, lines)
    issues = list(problems)
    if fields:
        for key in sorted(set(fields) - {"name", "description"}):
            issues.append("{} frontmatter 只允许 name/description，多出字段 {}（BRIEF §4.1）".format(
                loc(path, fields[key][1]), key))
        if "name" not in fields:
            issues.append("{} frontmatter 缺少 name".format(loc(path, 1)))
        else:
            value = strip_quotes(fields["name"][0])
            if value != skill_id:
                issues.append("{} name={!r} 与目录名 {} 不一致".format(
                    loc(path, fields["name"][1]), value, skill_id))
        if "description" not in fields:
            issues.append("{} frontmatter 缺少 description".format(loc(path, 1)))
        else:
            value = strip_quotes(fields["description"][0])
            lineno = fields["description"][1]
            if not value:
                issues.append("{} description 为空（写清何时用）".format(loc(path, lineno)))
            elif len(value) > 60:
                issues.append("{} description {} 字 > 60 字上限".format(loc(path, lineno), len(value)))
    rep.item("{} frontmatter（name=目录名 / description ≤60 字）".format(rel), issues)

    # 固定五节：标题逐字、顺序固定；厚收三件套才可追加 ≤2 节
    headings = [(lineno, text) for lineno, level, text in scan_headings(lines, body_start) if level == 2]
    issues = []
    for index, expected in enumerate(FIVE_SECTIONS):
        if index >= len(headings):
            issues.append("{} 缺少第 {} 节 ## {}（五节必须齐全，BRIEF §4.1）".format(
                loc(path, len(lines)), index + 1, expected))
            continue
        if headings[index][1] != expected:
            issues.append("{} 第 {} 个 ## 小节应为 ## {}，实际 ## {}（顺序固定）".format(
                loc(path, headings[index][0]), index + 1, expected, headings[index][1]))
    extra = headings[len(FIVE_SECTIONS):]
    for heading in extra:
        if heading[1] in FIVE_SECTIONS:
            issues.append("{} 五节标题重复出现：## {}".format(loc(path, heading[0]), heading[1]))
        elif skill_id not in THICK_SKILLS:
            issues.append("{} 五节之外不允许追加 ## {}（只有 auto-test/review/acceptance 可追加 ≤2 节）".format(
                loc(path, heading[0]), heading[1]))
    if skill_id in THICK_SKILLS and len(extra) > 2:
        for heading in extra[2:]:
            issues.append("{} 厚收最多追加 2 节，多出 ## {}".format(loc(path, heading[0]), heading[1]))
    rep.item("{} 固定五节（逐字且顺序固定）".format(rel), issues)

    # 行数预算
    total = len(lines)
    issues = [] if total <= budget else [
        "{} 行数 {} > 预算 {}（超一行也不通过：先删再交，BRIEF §2 铁律 7）".format(rel, total, budget)
    ]
    rep.item("{} 行数 {}/{}（≤{}）".format(rel, total, budget, budget), issues)


def check_skeleton(rep: Reporter) -> None:
    rep.group("① 技能结构与根目录骨架")

    issues = []
    for name in ROOT_REQUIRED:
        path = ROOT / name
        if name.endswith(".md"):
            if not path.is_file():
                issues.append("{}:1 缺少文件".format(name))
        elif not path.is_dir():
            issues.append("{}:1 缺少目录".format(name))
    rep.item("根目录骨架（README/WORKFLOW/PLAN/loop-log + skills/shared/issue/bug-patterns/scripts/archive）", issues)

    try:
        visible = sorted(item.name for item in ROOT.iterdir() if not item.name.startswith("."))
    except OSError as exc:
        visible = []
        rep.item("根目录可见项 ≤10", ["根目录不可读：{}".format(exc)])
    if visible:
        issues = []
        if len(visible) > 10:
            issues.append("根目录可见项 {} 个 > 10：{}（BRIEF §1：删/移多余项）".format(
                len(visible), "、".join(visible)))
        rep.item("根目录可见项 ≤10（当前 {} 个）".format(len(visible)), issues)

    for name, budget in ROOT_DOC_BUDGETS.items():
        path = ROOT / name
        if not path.is_file():
            continue
        total = count_lines(path)
        issues = [] if total <= budget else [
            "{} 行数 {} > 预算 {}（先删再交，BRIEF §3）".format(name, total, budget)
        ]
        rep.item("{} 行数 {}/{}（≤{}）".format(name, total, budget, budget), issues)

    issues = []
    for name in SHARED_REQUIRED:
        if not (ROOT / "shared" / name).is_file():
            issues.append("shared/{}:1 缺少契约文件".format(name))
    rep.item("shared/ 4 份契约齐全", issues)

    issues = []
    if not (ROOT / "issue" / "README.md").is_file():
        issues.append("issue/README.md:1 缺少文件")
    if not (ROOT / "issue" / "000-template.md").is_file():
        issues.append("issue/000-template.md:1 缺少文件")
    rep.item("issue/README.md + 000-template.md", issues)

    if (ROOT / "bug-patterns" / "README.md").is_file():
        rep.item("bug-patterns/README.md", [])
    else:
        rep.item("bug-patterns/README.md", ["bug-patterns/README.md:1 缺少文件"])

    skills_dir = ROOT / "skills"
    issues = []
    if not skills_dir.is_dir():
        issues.append("skills/:1 缺少目录")
    else:
        for skill_id in EXPECTED_CORE:
            if not (skills_dir / skill_id / "SKILL.md").is_file():
                issues.append("skills/{}/SKILL.md:1 缺少文件（核心 10 个必须齐全）".format(skill_id))
        for child in sorted(skills_dir.iterdir()):
            if child.is_dir() and (child / "SKILL.md").is_file() and child.name not in SKILL_BUDGETS:
                issues.append("skills/{}/SKILL.md:1 不在核心 10 名单内（v4 P1 只有 10 个 skill）".format(
                    child.name))
    rep.item("skills/ 核心 10 个目录", issues)

    for skill_id in EXPECTED_CORE:
        check_skill(rep, skill_id, SKILL_BUDGETS[skill_id])


# ---------------------------------------------------------------------------
# ② 引用可达
# ---------------------------------------------------------------------------

def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for name in ("README.md", "WORKFLOW.md", "PLAN.md", "loop-log.md"):
        path = ROOT / name
        if path.is_file():
            files.append(path)
    for dirname in ("skills", "shared", "issue", "bug-patterns"):
        base = ROOT / dirname
        if not base.is_dir():
            continue
        for path in base.rglob("*.md"):
            if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
                continue
            files.append(path)
    return sorted(set(files), key=rel_path)


def resolve_link_issue(source: Path, lineno: int, raw_target: str) -> str | None:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if not target:
        return None
    lowered = target.lower()
    if lowered.startswith(("http://", "https://", "mailto:", "tel:", "data:")) or "://" in target:
        return None
    if target.startswith("#"):
        return None
    if any(char in target for char in "<>{}"):
        return None  # 模板占位符，不是真实链接
    target = target.split("#", 1)[0]
    if not target:
        return None
    if ABSOLUTE_WIN_PATTERN.match(target) or target.startswith("/"):
        return "{} 链接用了绝对路径：{}（铁律：路径相对化，不写本机路径）".format(
            loc(source, lineno), raw_target)
    target = unquote(target)
    candidate = source.parent / target
    try:
        resolved = candidate.resolve()
    except OSError:
        resolved = Path(candidate.absolute())
    if not resolved.exists():
        return "{} 链接目标不存在：{}（解析为 {}）".format(
            loc(source, lineno), raw_target, rel_path(resolved))
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        return "{} 链接越出仓库：{}（解析为 {}）".format(
            loc(source, lineno), raw_target, resolved)
    return None


def check_links(rep: Reporter) -> None:
    rep.group("② 引用可达（Markdown 相对链接目标必须存在）")
    files = iter_markdown_files()
    issues: list[str] = []
    link_total = 0
    for path in files:
        lines = read_lines(path)
        fence = None
        for lineno, line in enumerate(lines, 1):
            fence_match = FENCE_PATTERN.match(line.lstrip())
            if fence_match:
                marker = fence_match.group(1)[0]
                if fence is None:
                    fence = marker
                elif fence == marker:
                    fence = None
                continue
            if fence is not None:
                continue
            cleaned = INLINE_CODE_PATTERN.sub("", line)
            cleaned = HTML_COMMENT_PATTERN.sub("", cleaned)
            for match in LINK_PATTERN.finditer(cleaned):
                link_total += 1
                issue = resolve_link_issue(path, lineno, match.group(1))
                if issue:
                    issues.append(issue)
    rep.item("相对链接可达（{} 个 Markdown / {} 条链接；排除 archive/ 与代码块）".format(
        len(files), link_total), issues)


# ---------------------------------------------------------------------------
# ③ 问题卡字段
# ---------------------------------------------------------------------------

def is_placeholder(value: str, is_template: bool) -> bool:
    if not is_template:
        return False
    text = value.strip()
    if not text:
        return True
    return any(token in text for token in ("<", ">", "...", "NNN", "YYYY-MM-DD"))


def check_issue_card(rep: Reporter, card: Path) -> None:
    lines = read_lines(card)
    fields, body_start, problems = parse_frontmatter_lines(card, lines)
    issues = list(problems)
    if not ISSUE_NAME_PATTERN.fullmatch(card.name):
        issues.append("{}:1 文件名不符合 NNN-slug.md（例如 001-review-slow.md）".format(loc(card)))
    is_template = card.name.startswith("000-")

    for key in ISSUE_FIELDS:
        if key not in fields:
            issues.append("{} frontmatter 缺少字段 {}（BRIEF §4.6）".format(loc(card, 1), key))
    for key in sorted(set(fields) - set(ISSUE_FIELDS)):
        issues.append("{} frontmatter 非约定字段 {}（只允许 7 个，不发明字段）".format(
            loc(card, fields[key][1]), key))

    def value_of(key: str) -> tuple[str, int] | None:
        if key not in fields:
            return None
        return strip_quotes(fields[key][0]), fields[key][1]

    checks = (
        ("type", ISSUE_TYPES, "只允许 skill/project/env/process"),
        ("severity", ISSUE_SEVERITIES, "只允许 P0/P1/P2"),
        ("status", ISSUE_STATUSES, "只允许 open/fixed/verified/closed"),
    )
    for key, allowed, hint in checks:
        entry = value_of(key)
        if entry is None:
            continue
        value, lineno = entry
        if is_placeholder(value, is_template):
            continue
        if value not in allowed:
            issues.append("{} {}={!r} 非法（{}）".format(loc(card, lineno), key, value, hint))

    entry = value_of("id")
    if entry is not None and not is_placeholder(entry[0], is_template) and not entry[0]:
        issues.append("{} id 不能为空".format(loc(card, entry[1])))

    entry = value_of("skill")
    if entry is not None and not is_placeholder(entry[0], is_template) and not entry[0]:
        issues.append("{} skill 不能为空（无归属填 none）".format(loc(card, entry[1])))

    entry = value_of("found")
    if entry is not None and not is_placeholder(entry[0], is_template):
        value, lineno = entry
        if not DATE_PATTERN.fullmatch(value):
            issues.append("{} found={!r} 不是 YYYY-MM-DD".format(loc(card, lineno), value))
        else:
            try:
                dt.datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                issues.append("{} found={!r} 不是合法日期".format(loc(card, lineno), value))

    headings = [(lineno, text) for lineno, level, text in scan_headings(lines, body_start) if level == 2]
    for index, expected in enumerate(ISSUE_SECTIONS):
        if index >= len(headings):
            issues.append("{} 缺少第 {} 节 ## {}（正文固定四节）".format(
                loc(card, len(lines)), index + 1, expected))
            continue
        if headings[index][1] != expected:
            issues.append("{} 第 {} 个 ## 小节应为 ## {}，实际 ## {}（四节顺序固定）".format(
                loc(card, headings[index][0]), index + 1, expected, headings[index][1]))
    for heading in headings[len(ISSUE_SECTIONS):]:
        issues.append("{} 正文多出小节 ## {}（只有现象/证据/影响/建议改动四节）".format(
            loc(card, heading[0]), heading[1]))
    rep.item(rel_path(card), issues)


def check_issues(rep: Reporter) -> None:
    rep.group("③ 问题卡字段与正文结构（issue/NNN-slug.md）")
    issue_dir = ROOT / "issue"
    if not issue_dir.is_dir():
        rep.item("issue/ 问题卡", ["issue/:1 缺少目录"])
        return
    cards = sorted(
        (path for path in issue_dir.glob("*.md") if path.name.lower() != "readme.md"),
        key=lambda path: path.name,
    )
    if not cards:
        rep.item("issue/ 问题卡", ["issue/:1 没有问题卡（至少应有 000-template.md）"])
        return
    for card in cards:
        check_issue_card(rep, card)


# ---------------------------------------------------------------------------
# ④ loop-log 表头
# ---------------------------------------------------------------------------

def check_loop_log(rep: Reporter) -> None:
    rep.group("④ loop-log 表头（11 列逐字）")
    path = ROOT / "loop-log.md"
    if not path.is_file():
        rep.item("loop-log.md 11 列表头", ["loop-log.md:1 缺少文件"])
        return
    lines = read_lines(path)
    issues: list[str] = []
    header_line = None
    for lineno, line in enumerate(lines, 1):
        if line.strip() == LOOP_LOG_HEADER:
            header_line = lineno
            break
    if header_line is None:
        first_table = next(((lineno, line) for lineno, line in enumerate(lines, 1)
                            if line.strip().startswith("|")), None)
        if first_table is None:
            issues.append("loop-log.md:1 未找到表格表头（应含 11 列，逐字见 BRIEF §4.7）")
        else:
            issues.append("loop-log.md:{} 表头不是约定 11 列：{}".format(
                first_table[0], first_table[1].strip()))
    else:
        separator = lines[header_line] if header_line < len(lines) else ""
        cells = [cell.strip() for cell in separator.strip().strip("|").split("|")]
        if (not separator.strip().startswith("|") or len(cells) != 11
                or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)):
            issues.append("loop-log.md:{} 表头下一行应为 11 列分隔行（|---|…）".format(header_line + 1))
    rep.item("loop-log.md 11 列表头逐字", issues)


# ---------------------------------------------------------------------------
# ⑤ 报告模板必需字段
# ---------------------------------------------------------------------------

def check_template(rep: Reporter, rel: str, required: tuple[str, ...],
                   rules: dict[str, tuple[tuple[str, str], ...]]) -> None:
    path = ROOT / rel
    if not path.is_file():
        rep.item(rel, ["{}:1 缺少模板文件".format(rel)])
        return
    lines = read_lines(path)
    headings = [(lineno, text) for lineno, level, text in scan_headings(lines) if level == 2]
    issues: list[str] = []
    positions: dict[str, tuple[int, int]] = {}
    cursor = 0
    for expected in required:
        found = None
        for index in range(cursor, len(headings)):
            if headings[index][1] == expected:
                found = index
                break
        if found is None:
            issues.append("{} 缺少必需标题 ## {}（BRIEF §4.8）".format(rel, expected))
            break
        positions[expected] = (found, headings[found][0])
        cursor = found + 1
    for heading, checks in rules.items():
        if heading not in positions:
            continue
        index, heading_line = positions[heading]
        start = heading_line  # 标题下一行的 0-based 下标
        end = headings[index + 1][0] - 1 if index + 1 < len(headings) else len(lines)
        content = "\n".join(lines[start:end])
        lowered = content.lower()
        for token, description in checks:
            matched = token in (lowered if token.lower() == "sha256" else content)
            if not matched:
                issues.append("{}:{} ## {} 段内缺少 {}（{}）".format(
                    rel, heading_line, heading, token, description))
    rep.item(rel, issues)


def check_templates(rep: Reporter) -> None:
    rep.group("⑤ 评审 / 验收报告模板必需字段（BRIEF §4.8）")
    check_template(rep, REVIEW_REPORT, REVIEW_REPORT_HEADINGS, REVIEW_REPORT_RULES)
    check_template(rep, ACCEPTANCE_REPORT, ACCEPTANCE_REPORT_HEADINGS, ACCEPTANCE_REPORT_RULES)
    for rel in ("skills/review/templates/review-package.md",
                "skills/acceptance/templates/acceptance-checklist.md"):
        if (ROOT / rel).is_file():
            rep.item(rel, [])
        else:
            rep.item(rel, ["{}:1 缺少模板文件".format(rel)])


# ---------------------------------------------------------------------------
# ⑥ installer core 清单
# ---------------------------------------------------------------------------

def load_installer(script: Path) -> ModuleType | None:
    """按文件路径导入 installer（只读，用于核对常量与 CLI）。

    注意：dataclass 装饰器要求模块已登记进 sys.modules，否则 exec_module 会抛
    AttributeError；导入成功/失败后都从 sys.modules 摘掉，避免污染本进程。
    """
    module_name = "install_skills_under_validate"
    try:
        spec = importlib.util.spec_from_file_location(module_name, script)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(module_name, None)
        return module
    except Exception:  # 导入错误一律归为可解释 FAIL
        return None


def run_installer_main(module: ModuleType, arguments: list[str]) -> tuple[int, str]:
    """在进程内调用 installer.main(argv)，返回 (exit code, 捕获输出)。

    为什么不起子进程：本机解释器启动 + git 版本查询合计约 3 秒，两次子进程会撑破
    5 秒预算；这里打桩 git_revision（版本号不是校验对象），CLI 解析/发现/profile
    过滤/计划生成仍是真实执行。真实命令冒烟由 CI 单独两步覆盖。
    """
    original = getattr(module, "git_revision", None)
    buffer = io.StringIO()
    try:
        if original is not None:
            module.git_revision = lambda root: "validate-lite"  # type: ignore[assignment]
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            code = module.main(arguments)
    finally:
        if original is not None:
            module.git_revision = original  # type: ignore[assignment]
    return code, buffer.getvalue()


def tail(text: str, limit: int = 500) -> str:
    compact = " / ".join(part.strip() for part in text.splitlines() if part.strip())
    return compact[-limit:]


def check_installer(rep: Reporter) -> None:
    rep.group("⑥ installer core 清单（--profile core 默认）")
    script = ROOT / INSTALLER
    if not script.is_file():
        rep.item(INSTALLER, ["{}:1 缺少文件".format(INSTALLER)])
        return
    module = load_installer(script)
    if module is None:
        rep.item("{} 可导入".format(INSTALLER),
                 ["{}:1 导入失败（语法/运行时错误），先修脚本".format(INSTALLER)])
        return
    rep.item("{} 可导入".format(INSTALLER), [])

    issues: list[str] = []
    core = getattr(module, "CORE_PROFILE", None)
    try:
        core_ids = sorted(core) if core is not None else []
    except TypeError:
        core_ids = []
    if core_ids != EXPECTED_CORE:
        missing = sorted(set(EXPECTED_CORE) - set(core_ids))
        extra = sorted(set(core_ids) - set(EXPECTED_CORE))
        detail = []
        if missing:
            detail.append("缺 " + "、".join(missing))
        if extra:
            detail.append("多 " + "、".join(extra))
        issues.append("{}:1 CORE_PROFILE 应为核心 10 个 id（{}）".format(
            INSTALLER, "；".join(detail) or "当前为空"))
    rep.item("CORE_PROFILE = 核心 10 个 id", issues)

    issues = []
    try:
        parser = module.build_parser()
        default_profile = parser.parse_args([]).profile
        core_profile = parser.parse_args(["--profile", "core"]).profile
        all_profile = parser.parse_args(["--profile", "all"]).profile
        if default_profile != "core" or core_profile != "core" or all_profile != "all":
            issues.append("{}:1 --profile 不应答（默认/core/all，实际 {!r}/{!r}/{!r}）".format(
                INSTALLER, default_profile, core_profile, all_profile))
    except (AttributeError, SystemExit, TypeError) as exc:
        issues.append("{}:1 --profile core|all 未实现：{}".format(INSTALLER, exc))
    rep.item("--profile core|all（默认 core）", issues)

    issues = []
    excluded = getattr(module, "EXCLUDED_TOP_DIRS", frozenset())
    if "archive" not in excluded:
        issues.append("{}:1 发现阶段未排除 archive/（冻结区不应被安装）".format(INSTALLER))
    rep.item("发现阶段排除 archive/", issues)

    expected_set = set(EXPECTED_CORE)
    code, output = run_installer_main(module, ["--list", "--profile", "core"])
    issues = []
    if code != 0:
        issues.append("--list --profile core exit {}：{}".format(code, tail(output)))
    else:
        listed = set(LIST_ID_PATTERN.findall(output))
        if listed != expected_set:
            issues.append("--list --profile core 清单不符：缺 {}；多 {}".format(
                "、".join(sorted(expected_set - listed)) or "无",
                "、".join(sorted(listed - expected_set)) or "无"))
        if "profile：core" not in output:
            issues.append("--list --profile core 输出缺少「profile：core」行")
    rep.item("--list --profile core 清单 = 10 个", issues)

    probe = Path(tempfile.mkdtemp(prefix="validate-lite-"))
    try:
        target = probe / "skills"
        code, output = run_installer_main(
            module, ["--target", str(target), "--profile", "core", "--dry-run"])
        issues = []
        if code != 0:
            issues.append("--dry-run --profile core exit {}：{}".format(code, tail(output)))
        elif "profile：core" not in output:
            issues.append("--dry-run 输出缺少「profile：core」（profile 未生效）")
        elif "dry-run" not in output.lower():
            issues.append("--dry-run 输出未标注 dry-run")
        if target.exists():
            issues.append("--dry-run 不应创建目标目录：{}".format(target))
        rep.item("--dry-run --profile core 冒烟（不写盘）", issues)
    finally:
        shutil.rmtree(probe, ignore_errors=True)


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    started = time.perf_counter()
    print("validate_lite.py · v4 骨架轻量校验")
    print("口径：.tmp-v4/BRIEF.md §3（文件清单）+ §4（统一约定）；PLAN.md §7")
    print("根目录：{}".format(ROOT))

    rep = Reporter()
    check_skeleton(rep)
    check_links(rep)
    check_issues(rep)
    check_loop_log(rep)
    check_templates(rep)
    check_installer(rep)

    elapsed = time.perf_counter() - started
    issues = [] if elapsed < 5.0 else [
        "总耗时 {:.2f}s > 5 秒上限（先减少扫描/子进程，别加检查层）".format(elapsed)
    ]
    rep.item("总耗时 {:.2f}s（上限 5 秒）".format(elapsed), issues)

    print("\n" + "─" * 60)
    if rep.failed:
        print("结果：FAIL · {} 项失败 / 共 {} 项 · 用时 {:.2f}s".format(rep.failed, rep.total, elapsed))
        print("修法：按 BRIEF §4 补齐缺失文件/字段/链接；validate_lite 只查机械口径，不替代评审。")
        return 1
    print("结果：PASS · 全部 {} 项通过 · 用时 {:.2f}s".format(rep.total, elapsed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
