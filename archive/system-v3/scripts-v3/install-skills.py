#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""install-skills.py —— 跨平台 skill 安装 / 导出 / 漂移核对入口（Python 3.10+，仅标准库）。

为什么需要它
------------
仓内原有的两份分发脚本都绑定 Windows 场景：sync-skills.sh 依赖 Git Bash + tar，
link-skills.sh 依赖 Windows junction。要「在别的机器 / 别的 AI 宿主 / 别的项目里直接使用」
这套 skill 体系，需要一个不依赖 shell、不依赖第三方包的标准入口。本脚本只用标准库，
Windows / macOS / Linux 行为一致；不要求 PyYAML，frontmatter 只做最小解析（name 行）。

它做什么
--------
1) 发现：从仓库根向下最多扫描两层目录里的 SKILL.md（根级 workflow/SKILL.md 与
   <分类>/<skill>/SKILL.md 都覆盖），skill id 取 frontmatter 的 name:；与目录名不一致时
   打印警告并以 frontmatter 为准。
2) 拷贝安装（默认）：把每个 skill 目录拷到 <target>/<skill-id>/，并把仓库 shared/ 分发到
   三个落点：<target>/shared、<parent(target)>/shared、<target>/<skill-id>/shared。
   三落点是为了让安装副本里任何深度的 shared 相对引用都可解析（判据见 shared/skill-contract.md 1.4）。
3) 链接安装（--link）：不拷贝内容，直接把 <target>/<skill-id> 建为指向源仓 skill 目录的链接
   （Windows 用 junction，macOS/Linux 用符号链接）；<target>/shared 与 <parent(target)>/shared
   也链接到源仓 shared/。适合「本机/同文件系统上让宿主直接引用本仓」，源仓改完即时生效。
   --unlink 只删除确认指向本仓的链接，真实目录/文件与仓外链接一律保留。
4) 核对：--check 只读比对安装副本与源仓。copy 模式比「文件集合 + sha256」，缺失/内容不一致/
   多余都算漂移；--link 模式校验每个落点是否指向源仓，缺失/指向错误/真实目录都算漂移；两者 exit 1。
5) 导出：--export DIR 生成可整包带走的 self-contained 安装包：
   DIR/skills（skills 根） + DIR/shared（容器级 shared） + DIR/MANIFEST.json。
   导出后可直接用 --check --target DIR/skills 自检。链接不可移植，故 --link 与 --export 互斥。

安装布局
--------
    <target>/<skill-id>/SKILL.md         每个 skill 的入口与资源（copy=副本；--link=链接整个 skill 目录）
    <target>/<skill-id>/shared/          该 skill 目录内的 shared 副本（link 模式下由 skill 链接整体承接）
    <target>/shared/                     skills 根级 shared（link 模式=指向源仓 shared/ 的链接）
    <parent(target)>/shared/             宿主容器级 shared（link 模式同上）

    <target> 是宿主的 skills 根，例如 ~/.dsh/skills、~/.qoder-cn/skills、~/.claude/skills。
    copy 模式若发现某 skill 落点已是 junction / 符号链接，会报 linked 跳过、绝不删除链接、
    绝不往链接目标写文件（旧 sync-skills.sh 踩过的坑）。link 模式遇到真实目录/错误指向则报
    conflict 跳过，绝不删除真实内容。

copy 还是 link（选择与风险）
---------------------------
- copy：可分发、可复现、与源仓隔离；换机器/换项目/导出给别人时用。缺省模式，--export 只做 copy。
- link：零拷贝、改源仓即时生效；适合本机开发迭代或同盘宿主引用。代价是「无 commit 隔离」——
  源仓工作区未提交的半成品改动会立刻被宿主读到；源仓被移动/删除、换机器、跨网络盘时链接即失效；
  与 copy 模式混用同一 skills 根会产生 conflict（真实目录不覆盖）。要稳定/可移交就用 copy。

用法
----
    python scripts/install-skills.py --list
    python scripts/install-skills.py --target ~/.dsh/skills --dry-run
    python scripts/install-skills.py --target ~/.dsh/skills
    python scripts/install-skills.py --target ~/.dsh/skills --target ~/.claude/skills
    python scripts/install-skills.py --check --target ~/.dsh/skills
    python scripts/install-skills.py --link --target ~/.dsh/skills --dry-run
    python scripts/install-skills.py --link --target ~/.dsh/skills
    python scripts/install-skills.py --link --check --target ~/.dsh/skills
    python scripts/install-skills.py --unlink --target ~/.dsh/skills
    python scripts/install-skills.py --export /tmp/tenger-skills-pack
    python scripts/install-skills.py --check --target /tmp/tenger-skills-pack/skills

退出码
------
    0  成功（安装已写入 / 链接已建立 / 核对无漂移 / 列出、导出或 unlink 成功）
    1  核对发现漂移或缺失；或运行错误（目标不可写、skill id 冲突、导出目录非空、
       link 遇到真实目录/错误指向的 conflict、unlink 删除失败等）
    2  命令行参数错误（含 --link 与 --export 互斥、--unlink 与 --check 互斥等）

安全边界
--------
- 不删除目标里已有的 skill，也不删除任何「源仓里没有」的文件；这类文件只报 stale 交人工判断。
- 只创建 / 更新文件；已有 skill 目录里除期望文件外的东西一律不动。
- 拒绝把安装/导出写进源仓内部或其父目录（避免污染源仓自我发现结果）。
- 目标 skill 目录若是链接（含 Windows junction），报 linked 跳过；判不出链接类型时，
  若目标 SKILL.md 与源一致就按 unchanged 跳过覆盖，绝不在不确定时瞎写。
- link 模式只建链接：目标已存在真实目录/文件时一律报 conflict 跳过，绝不删除真实内容。
- unlink 只删链接：先用 realpath 确认链接指向落在源仓内；真实目录/文件、仓外链接只报 keep。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
SKILL_ENTRY = "SKILL.md"
SHARED_DIR = "shared"
MANIFEST_NAME = "MANIFEST.json"
GENERATOR = "scripts/install-skills.py"

# 发现阶段的顶层排除目录（与任务口径一致；另有 startswith(".") 兜住 .git/.venv/.spec 等隐藏目录）
EXCLUDED_TOP_DIRS = frozenset({
    ".git", ".venv", "node_modules", "__pycache__", ".spec", "docs", "evals", "issue",
    "chats", "evolution", "bug-patterns", "governance", "scripts", "shared", "skill-knowledge",
    "templates", ".tmp-eval", "dist", "coverage",
})
# 拷贝 / 扫描文件树时排除的派生目录与文件（不随安装副本分发）
EXCLUDED_DIR_NAMES = frozenset({".git", ".venv", "node_modules", "__pycache__", "dist", "coverage"})
EXCLUDED_FILE_NAMES = frozenset({".DS_Store"})
EXCLUDED_FILE_SUFFIXES = (".pyc",)

# 候选宿主 skills 根：--list 时展示（DSH 是当前实际宿主，其余为常见 AI 宿主）
HOST_CANDIDATES = (
    "~/.dsh/skills",
    "~/.qoder-cn/skills",
    "~/.zcode/skills",
    "~/.codebuddy/skills",
    "~/.codex/skills",
    "~/.claude/skills",
)

ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
FRONTMATTER_NAME_PATTERN = re.compile(r"^name:[ \t]*(.*?)[ \t]*$")
GIT_SHA_PATTERN = re.compile(r"^[0-9a-fA-F]{40,64}$")
FILE_ATTRIBUTE_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
DETAIL_LIMIT = 40

USAGE_EPILOG = """安装布局（copy 模式=三落点，与 shared/skill-contract.md 1.4 一致）:
    <target>/<skill-id>/           copy=skill 自身文件副本；--link=junction/symlink（链接整个 skill 目录）
    <target>/<skill-id>/shared/    copy 模式下该 skill 目录内的 shared 副本（link 模式由 skill 链接整体承接）
    <target>/shared/               skills 根级 shared（link 模式=指向源仓 shared/ 的链接）
    <parent(target)>/shared/       宿主容器级 shared（同上）

两种安装模式:
    copy（默认）: 拷贝文件；可分发/可复现/与源仓隔离；--export 只做 copy。
    link（--link）: Windows junction / macOS/Linux 符号链接，零拷贝、源仓改动即时生效；
        无 commit 隔离（未提交改动会立即被宿主读到），源仓移动/换机器/跨网盘即失效。
    --link 与 --export 互斥；同一 skills 根不要混用 copy 与 link（真实目录会报 conflict，不覆盖）。
    --unlink 只删除「确认指向本仓」的链接；真实目录/文件与仓外链接保留并计入 keep。

--check 判据:
    copy 模式: 比对 skill 文件集合 + sha256（含每个 skill 的 shared 副本）以及两个 shared 落点；
        new/updated/stale 任一非零即 drift，drift>0 exit 1（不删除目标里的多余文件）。
    link 模式（--check --link）: 校验每个落点是否为指向源仓的正确链接；缺失/指向错误/真实目录
        都算 drift，exit 1。copy 模式的 --check 遇到链接仍按既有口径报 linked 跳过（不改变）。

示例:
    python scripts/install-skills.py --list
    python scripts/install-skills.py --target ~/.dsh/skills --dry-run
    python scripts/install-skills.py --target ~/.dsh/skills
    python scripts/install-skills.py --check --target ~/.dsh/skills
    python scripts/install-skills.py --link --target ~/.dsh/skills
    python scripts/install-skills.py --link --check --target ~/.dsh/skills
    python scripts/install-skills.py --unlink --target ~/.dsh/skills
    python scripts/install-skills.py --export /tmp/tenger-skills-pack
    python scripts/install-skills.py --check --target /tmp/tenger-skills-pack/skills
"""


class InstallError(RuntimeError):
    """可解释、可修复的运行错误（CLI 捕获后打印为「错误：...」，exit 1）。"""


@dataclass(frozen=True)
class Skill:
    """一个被发现的 skill：id 来自 frontmatter name，source 是源目录。"""

    id: str
    rel_path: str
    source: Path


@dataclass(frozen=True)
class FileEntry:
    """期望安装到目标的一个文件：目标内相对路径 + 源文件 + 源 sha256。"""

    rel: str
    source: Path
    sha256: str


@dataclass
class ScopePlan:
    """一个受管目录（某个 skill 目录 / 某个 shared 落点）的核对计划。"""

    kind: str  # skill | shared | container-shared
    label: str
    dest: Path
    expected: dict[str, FileEntry]
    status: str = "ok"  # ok | absent | linked | unknown | unchanged | nondir
    note: str = ""
    new: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    unchanged: int = 0
    stale: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class TargetPlan:
    """一个 --target 的完整核对计划：46 个 skill 目录 + 两个 shared 落点。"""

    target: Path
    scopes: list[ScopePlan]


@dataclass
class LinkLanding:
    """链接模式的一个落点：某个 skill 目录或一个 shared 落点。"""

    label: str
    dest: Path
    source: Path
    status: str = "unknown"  # ok | created | would-link | missing | wrong-link | real-dir | nondir | conflict | error
    note: str = ""


@dataclass
class SourceIndex:
    """源仓快照：skill 清单、每个 skill 的文件哈希、shared 文件哈希。"""

    root: Path
    skills: list[Skill]
    skill_files: dict[str, dict[str, FileEntry]]
    shared_files: dict[str, FileEntry]
    warnings: list[str]


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------

def repo_root() -> Path:
    """本脚本所在仓库的根目录（由脚本位置决定，不依赖当前工作目录）。"""
    return Path(__file__).resolve().parents[1]


def normalize_path(value: str) -> Path:
    """展开 ~ 并转绝对路径（不解析链接，保留调用者语义）。"""
    return Path(os.path.abspath(os.path.expanduser(value)))


def resolve_targets(values: Sequence[str]) -> list[Path]:
    """规范化 --target 列表：去重后按路径排序，保证输出确定性。"""
    unique: dict[str, Path] = {}
    for value in values:
        path = normalize_path(value)
        unique.setdefault(os.path.normcase(str(path)), path)
    return sorted(unique.values(), key=lambda path: os.path.normcase(str(path)))


def _is_within(child: Path, parent: Path) -> bool:
    """child 是否在 parent 之内（Windows 下大小写不敏感）。"""
    try:
        Path(os.path.normcase(str(child))).relative_to(Path(os.path.normcase(str(parent))))
        return True
    except ValueError:
        return False


def _assert_outside_repo(path: Path, root: Path, purpose: str) -> None:
    if _is_within(path, root) or _is_within(root, path):
        raise InstallError(
            "{}不能是源仓内部目录或其父目录：{}（源仓：{}）；请指向仓库外的宿主 skills 根，"
            "例如 ~/.dsh/skills、~/.claude/skills".format(purpose, path, root)
        )


def assert_target_safe(target: Path, root: Path) -> None:
    """安装/核对前的目标安全检查：不写进源仓，不顺着指向源仓的链接写。"""
    _assert_outside_repo(target, root, "目标目录")
    if not os.path.lexists(target):
        return
    state, note = detect_link(target, None)
    if state == "link":
        real = Path(os.path.realpath(target))
        if _is_within(real, root):
            raise InstallError(
                "目标 {} 是链接（{}），真实路径在源仓内：{}；安装会写进源仓。"
                "请传入宿主真实目录，或改用 --target 指向仓库外路径".format(target, note, real)
            )


def iter_files(base: Path) -> Iterator[tuple[str, Path]]:
    """按确定性顺序遍历 base 下的受管文件，返回 (posix 相对路径, 绝对路径)。

    排除目录：node_modules/__pycache__/.venv/dist/coverage/.git；
    排除文件：*.pyc、.DS_Store。符号链接目录不展开（避免跨出源目录）。
    """
    if not base.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(name for name in dirnames if name not in EXCLUDED_DIR_NAMES)
        for name in sorted(filenames):
            if name in EXCLUDED_FILE_NAMES or name.endswith(EXCLUDED_FILE_SUFFIXES):
                continue
            full = Path(dirpath) / name
            yield full.relative_to(base).as_posix(), full


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_revision(root: Path) -> str | None:
    """git rev-parse HEAD（git 不可用 / 非 git 工作树时返回 None，不报错）。"""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    revision = proc.stdout.strip()
    return revision if GIT_SHA_PATTERN.fullmatch(revision) else None


def detect_link(path: Path, reference: Path | None) -> tuple[str, str]:
    """判断路径是否链接。返回 (状态, 说明)。

    状态：absent（不存在）/ link / dir / nondir / unknown（判不出，交给上层兜底）。
    Windows junction 不是符号链接（Path.is_symlink() 为 False），但 lstat 带
    FILE_ATTRIBUTE_REPARSE_POINT；再退一步用 samefile 与源目录比对，作为跨平台兜底。
    """
    if not os.path.lexists(path):
        return "absent", ""
    try:
        if path.is_symlink():
            return "link", "符号链接"
    except OSError:
        pass
    try:
        lst = os.lstat(path)
    except OSError as exc:
        return "unknown", "无法读取路径属性：{}".format(exc)
    if getattr(lst, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT:
        return "link", "Windows 重解析点（junction）"
    if reference is not None and os.path.exists(reference):
        try:
            if os.path.samefile(path, reference):
                return "link", "与源目录指向同一实体（链接）"
        except OSError:
            pass
    if path.is_dir():
        return "dir", ""
    return "nondir", ""


# ---------------------------------------------------------------------------
# 发现：扫描仓库根下深度 <= 2 的 SKILL.md
# ---------------------------------------------------------------------------

def read_frontmatter_name(skill_md: Path) -> str | None:
    """只解析 frontmatter 的顶层 name: 行（不依赖 PyYAML）。解析失败返回 None。"""
    try:
        with open(skill_md, encoding="utf-8-sig", errors="replace") as handle:
            first = handle.readline().strip()
            if first != "---":
                return None
            for line in handle:
                stripped = line.rstrip("\r\n")
                if stripped.strip() == "---":
                    return None
                match = FRONTMATTER_NAME_PATTERN.match(stripped)
                if match:
                    value = match.group(1).strip()
                    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                        value = value[1:-1].strip()
                    return value or None
    except OSError:
        return None
    return None


def _skip_source_dir(name: str) -> bool:
    return name in EXCLUDED_TOP_DIRS or name.startswith(".")


def discover_skills(root: Path) -> tuple[list[Skill], list[str]]:
    """发现仓内 skill：深度 <= 2 的 */SKILL.md，id 取 frontmatter name。

    返回 (按 id 排序的 skills, 警告列表)。id 冲突、id 不安全属于硬错误（抛 InstallError）。
    """
    root = Path(root)
    if not root.is_dir():
        raise InstallError("仓库根不存在或不是目录：{}；请在 git clone 后的仓库根运行".format(root))
    warnings: list[str] = []
    found: list[Skill] = []

    def _consider(directory: Path) -> bool:
        entry = directory / SKILL_ENTRY
        if not entry.is_file():
            return False
        try:
            rel_path = directory.relative_to(root).as_posix()
        except ValueError:
            return False
        dir_name = directory.name
        declared = read_frontmatter_name(entry)
        if declared is None:
            warnings.append(
                "{} 缺少 frontmatter name:，退回目录名 {}".format(rel_path, dir_name)
            )
            skill_id = dir_name
        elif declared != dir_name:
            warnings.append(
                "{} 的 frontmatter name={} 与目录名 {} 不一致；以 frontmatter 为准".format(
                    rel_path, declared, dir_name
                )
            )
            skill_id = declared
        else:
            skill_id = declared
        if not ID_PATTERN.fullmatch(skill_id) or skill_id in {".", ".."}:
            raise InstallError(
                "skill id 不安全：{!r}（来自 {}）；name 只能是以字母或数字开头的 [A-Za-z0-9._-]".format(
                    skill_id, rel_path
                )
            )
        found.append(Skill(id=skill_id, rel_path=rel_path, source=directory))
        return True

    try:
        tops = sorted(root.iterdir(), key=lambda path: path.name.casefold())
    except OSError as exc:
        raise InstallError("无法读取仓库根 {}：{}；请检查目录权限".format(root, exc)) from exc
    for top in tops:
        if not top.is_dir() or _skip_source_dir(top.name):
            continue
        if _consider(top):
            continue
        try:
            subs = sorted(top.iterdir(), key=lambda path: path.name.casefold())
        except OSError as exc:
            warnings.append("无法读取目录 {}：{}（已跳过）".format(top, exc))
            continue
        for sub in subs:
            if not sub.is_dir() or _skip_source_dir(sub.name):
                continue
            _consider(sub)

    by_id: dict[str, Skill] = {}
    for skill in found:
        previous = by_id.get(skill.id)
        if previous is not None:
            raise InstallError(
                "skill id 冲突：{} 同时出现在 {} 与 {}；请修改其中一个 SKILL.md 的 frontmatter name".format(
                    skill.id, previous.rel_path, skill.rel_path
                )
            )
        by_id[skill.id] = skill
    return sorted(found, key=lambda skill: skill.id), sorted(warnings)


def build_source_index(root: Path | None = None) -> SourceIndex:
    """建立源仓快照（哈希每份源文件一次，多个 target 复用）。"""
    root = repo_root() if root is None else Path(root)
    skills, warnings = discover_skills(root)
    if not skills:
        raise InstallError(
            "未在 {} 下发现任何 skill（期望 <skill>/SKILL.md 或 <分类>/<skill>/SKILL.md）；"
            "请确认在完整的仓库克隆里运行".format(root)
        )
    shared_root = root / SHARED_DIR
    if not shared_root.is_dir():
        raise InstallError(
            "缺少 {}；shared/ 是安装布局的一部分（三落点都从它分发），请确认仓库完整".format(shared_root)
        )
    shared_files = {
        rel: FileEntry(rel=rel, source=path, sha256=sha256_file(path))
        for rel, path in iter_files(shared_root)
    }
    if not shared_files:
        raise InstallError("{} 为空；请确认仓库完整（shared/ 至少应含契约文件）".format(shared_root))
    skill_files: dict[str, dict[str, FileEntry]] = {}
    for skill in skills:
        entries = {
            rel: FileEntry(rel=rel, source=path, sha256=sha256_file(path))
            for rel, path in iter_files(skill.source)
        }
        if SKILL_ENTRY not in entries:
            raise InstallError("{} 在扫描后丢失 {}；请检查文件系统状态".format(skill.source, SKILL_ENTRY))
        skill_files[skill.id] = entries
    return SourceIndex(root=root, skills=skills, skill_files=skill_files,
                       shared_files=shared_files, warnings=warnings)


def build_link_index(root: Path | None = None) -> SourceIndex:
    """链接/解链只需要发现结果与 shared 目录，不哈希文件（比 build_source_index 快）。"""
    root = repo_root() if root is None else Path(root)
    skills, warnings = discover_skills(root)
    if not skills:
        raise InstallError(
            "未在 {} 下发现任何 skill（期望 <skill>/SKILL.md 或 <分类>/<skill>/SKILL.md）；"
            "请确认在完整的仓库克隆里运行".format(root)
        )
    if not (root / SHARED_DIR).is_dir():
        raise InstallError(
            "缺少 {}；link 模式需要把宿主 shared 落点链接到源仓 shared/，请确认仓库完整".format(
                root / SHARED_DIR)
        )
    return SourceIndex(root=root, skills=skills, skill_files={}, shared_files={},
                       warnings=warnings)


# ---------------------------------------------------------------------------
# 核对 / 安装
# ---------------------------------------------------------------------------

def _build_skill_expected(index: SourceIndex, skill: Skill) -> dict[str, FileEntry]:
    expected = dict(index.skill_files[skill.id])
    for rel, entry in index.shared_files.items():
        shared_rel = "{}/{}".format(SHARED_DIR, rel)
        expected[shared_rel] = FileEntry(rel=shared_rel, source=entry.source, sha256=entry.sha256)
    return expected


def _compare_scope(*, kind: str, label: str, dest: Path, expected: dict[str, FileEntry],
                   reference: Path | None) -> ScopePlan:
    plan = ScopePlan(kind=kind, label=label, dest=dest, expected=expected)
    if os.path.lexists(dest):
        state, note = detect_link(dest, reference)
        if state == "link":
            plan.status = "linked"
            plan.note = note
            return plan
        if state == "unknown":
            plan.status = "unknown"
            plan.note = note
            # 判不出链接类型时的兜底：SKILL.md 与源一致就按 unchanged 跳过覆盖，绝不瞎写。
            if reference is not None:
                source_md = reference / SKILL_ENTRY
                dest_md = dest / SKILL_ENTRY
                try:
                    if (source_md.is_file() and dest_md.is_file()
                            and sha256_file(dest_md) == sha256_file(source_md)):
                        plan.status = "unchanged"
                        plan.unchanged = len(expected)
                        plan.note = "{}；但 {} 与源一致，按 unchanged 跳过覆盖".format(note, SKILL_ENTRY)
                except OSError:
                    pass
            return plan
        if state == "nondir":
            plan.status = "nondir"
            plan.errors.append(
                "路径已存在但不是目录（{}）；请改名或删除后重试".format(dest)
            )
            return plan
    if not dest.is_dir():
        plan.status = "absent"
        plan.new = sorted(expected)
        return plan

    plan.status = "ok"
    for rel in sorted(expected):
        entry = expected[rel]
        path = dest.joinpath(*rel.split("/"))
        try:
            actual = sha256_file(path)
        except FileNotFoundError:
            plan.new.append(rel)
            continue
        except OSError as exc:
            plan.errors.append("读取失败 {}：{}；请检查权限后重试".format(path, exc))
            continue
        if actual == entry.sha256:
            plan.unchanged += 1
        else:
            plan.updated.append(rel)
    for rel, _full in iter_files(dest):
        if rel not in expected:
            plan.stale.append(rel)
    return plan


def plan_target(index: SourceIndex, target: Path) -> TargetPlan:
    """生成一个 target 的只读核对计划（不写任何文件）。"""
    target = Path(target)
    if os.path.lexists(target) and not target.is_dir():
        raise InstallError(
            "目标不是目录：{}；请换一个目录（例如 ~/.dsh/skills），或先把它改名".format(target)
        )
    scopes: list[ScopePlan] = []
    for skill in index.skills:
        scopes.append(_compare_scope(
            kind="skill",
            label=skill.id,
            dest=target / skill.id,
            expected=_build_skill_expected(index, skill),
            reference=skill.source,
        ))
    shared_expected = dict(index.shared_files)
    scopes.append(_compare_scope(
        kind="shared",
        label=SHARED_DIR,
        dest=target / SHARED_DIR,
        expected=shared_expected,
        reference=index.root / SHARED_DIR,
    ))
    container_shared = target.parent / SHARED_DIR
    scopes.append(_compare_scope(
        kind="container-shared",
        label=str(container_shared),
        dest=container_shared,
        expected=shared_expected,
        reference=index.root / SHARED_DIR,
    ))
    return TargetPlan(target=target, scopes=scopes)


def _copy_content(source: Path, destination: Path) -> None:
    """按内容复制文件（sha256 是安装/核对唯一判据；skill 资产无执行位，不保留 mtime/mode 省系统调用）。"""
    with open(source, "rb") as source_handle, open(destination, "wb") as destination_handle:
        shutil.copyfileobj(source_handle, destination_handle, 1024 * 1024)


def _apply_scope(scope: ScopePlan) -> int:
    written = 0
    updated = set(scope.updated)
    ensured_dirs: set[str] = set()
    for rel in scope.new + scope.updated:
        entry = scope.expected[rel]
        dest_path = scope.dest.joinpath(*rel.split("/"))
        try:
            # 只有被覆盖的已有文件才可能是符号链接；新建文件不存在，无需多一次 lstat
            if rel in updated and dest_path.is_symlink():
                scope.errors.append(
                    "目标是符号链接文件，拒绝写入：{}；请人工确认后换成普通文件".format(dest_path)
                )
                continue
            parent = dest_path.parent
            parent_key = os.path.normcase(str(parent))
            if parent_key not in ensured_dirs:
                parent.mkdir(parents=True, exist_ok=True)
                ensured_dirs.add(parent_key)
            _copy_content(entry.source, dest_path)
        except OSError as exc:
            scope.errors.append(
                "写入失败 {}：{}；请检查目标权限/磁盘，或先用 --dry-run 查看计划".format(dest_path, exc)
            )
            continue
        written += 1
    return written


def install_targets(index: SourceIndex, targets: Sequence[Path], *,
                    dry_run: bool = False) -> list[TargetPlan]:
    """安装到多个 target，返回安装前的核对计划（含写入后的错误信息）。"""
    plans: list[TargetPlan] = []
    for target in targets:
        plan = plan_target(index, target)
        plans.append(plan)
        if dry_run:
            continue
        Path(target).mkdir(parents=True, exist_ok=True)
        for scope in plan.scopes:
            if scope.status in {"ok", "absent"}:
                _apply_scope(scope)
    return plans


def target_counts(plans: Sequence[TargetPlan]) -> dict[str, int]:
    """汇总计数：new/updated/unchanged/stale/drift/linked/errors（文件数，drift=new+updated+stale）。"""
    counts = {"new": 0, "updated": 0, "unchanged": 0, "stale": 0,
              "drift": 0, "linked": 0, "errors": 0}
    for plan in plans:
        for scope in plan.scopes:
            counts["new"] += len(scope.new)
            counts["updated"] += len(scope.updated)
            counts["unchanged"] += scope.unchanged
            counts["stale"] += len(scope.stale)
            counts["errors"] += len(scope.errors)
            if scope.status == "linked":
                counts["linked"] += 1
    counts["drift"] = counts["new"] + counts["updated"] + counts["stale"]
    return counts


def format_counts(counts: dict[str, int]) -> str:
    return ("new={new} updated={updated} unchanged={unchanged} stale={stale} "
            "drift={drift} linked={linked} errors={errors}").format(**counts)


# ---------------------------------------------------------------------------
# 链接模式（--link / --link --check / --unlink）
# ---------------------------------------------------------------------------

def _same_path(left: Path, right: Path) -> bool:
    """两路径是否指向同一实体（会解析符号链接与 Windows junction）。"""
    try:
        return os.path.samefile(left, right)
    except OSError:
        return os.path.normcase(os.path.realpath(left)) == os.path.normcase(os.path.realpath(right))


def _points_into_repo(path: Path, root: Path) -> bool:
    """路径（解析链接后）是否落在源仓内。"""
    return _is_within(Path(os.path.realpath(path)), root)


def _remove_dir_link(path: Path) -> None:
    """只删除已确认是链接的目录落点：POSIX 符号链接用 unlink，Windows junction 用 rmdir。"""
    try:
        os.unlink(path)
        return
    except OSError:
        pass
    os.rmdir(path)


def _create_dir_link(link_path: Path, source: Path) -> str:
    """创建指向 source 的目录链接，返回链接方式说明。

    Windows 用 junction（cmd /c mklink /J，普通用户可用、无需开发者模式）；
    其他平台用符号链接。创建后立即回读校验，不可读/指向不符则回滚并报错。
    """
    link_path.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link_path), str(source)],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise InstallError(
                "创建 junction 失败：{} -> {}：{}；请检查目标目录权限或路径是否可用".format(
                    link_path, source, detail)
            )
        mode = "junction"
    else:
        try:
            os.symlink(str(source), str(link_path), target_is_directory=True)
        except OSError as exc:
            raise InstallError(
                "创建符号链接失败：{} -> {}：{}；请检查目标目录权限（Windows 需开发者模式/管理员）".format(
                    link_path, source, exc)
            ) from exc
        mode = "symlink"
    if not os.path.isdir(link_path) or not _same_path(link_path, source):
        try:
            _remove_dir_link(link_path)
        except OSError:
            pass
        raise InstallError(
            "链接已创建但不可读或指向不符：{} -> {}；已尝试回滚".format(link_path, source)
        )
    return mode


def link_landings(index: SourceIndex, target: Path) -> list[LinkLanding]:
    """链接模式的全部落点：每个 skill 目录 + skills 根级 shared + 宿主容器级 shared。"""
    shared_source = index.root / SHARED_DIR
    landings = [
        LinkLanding(label=skill.id, dest=target / skill.id, source=skill.source)
        for skill in index.skills
    ]
    landings.append(LinkLanding(label=SHARED_DIR, dest=target / SHARED_DIR, source=shared_source))
    container_shared = target.parent / SHARED_DIR
    landings.append(LinkLanding(label=str(container_shared), dest=container_shared,
                                source=shared_source))
    return landings


def inspect_link_landing(landing: LinkLanding) -> LinkLanding:
    """只读检查一个链接落点的当前状态（不写盘）。"""
    dest, source = landing.dest, landing.source
    if not os.path.lexists(dest):
        landing.status = "missing"
        landing.note = "缺失（应链接到 {}）".format(source)
        return landing
    state, note = detect_link(dest, source)
    if state == "link":
        if _same_path(dest, source):
            landing.status = "ok"
            landing.note = "已正确链接到源仓"
        else:
            landing.status = "wrong-link"
            landing.note = "链接指向 {}，期望 {}".format(os.path.realpath(dest), source)
        return landing
    if state == "dir":
        landing.status = "real-dir"
        landing.note = "目标是真实目录（不是链接，不删除）"
        return landing
    if state == "unknown":
        landing.status = "unknown"
        landing.note = note or "无法确认链接类型"
        return landing
    landing.status = "nondir"
    landing.note = "目标存在但不是目录"
    return landing


def apply_link_landing(landing: LinkLanding, dry_run: bool) -> LinkLanding:
    """建立一个链接落点；已存在的东西一律不覆盖，只报 ok / conflict。"""
    if os.path.lexists(landing.dest):
        inspect_link_landing(landing)
        if landing.status == "ok":
            return landing
        if landing.status == "wrong-link":
            landing.status = "conflict"
            landing.note = landing.note + "；不覆盖（请人工处理后重试）"
            return landing
        if landing.status == "real-dir":
            landing.status = "conflict"
            landing.note = landing.note + "；为不删除真实内容已跳过，请人工确认"
            return landing
        landing.status = "conflict"
        landing.note = "{}；不覆盖（请人工处理后重试）".format(landing.note or "已存在非链接对象")
        return landing
    if dry_run:
        landing.status = "would-link"
        landing.note = "将创建链接"
        return landing
    try:
        mode = _create_dir_link(landing.dest, landing.source)
    except (InstallError, OSError) as exc:
        landing.status = "error"
        landing.note = str(exc)
        return landing
    landing.status = "created"
    landing.note = "已创建 {} 链接".format(mode)
    return landing


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------

def print_warnings(index: SourceIndex) -> None:
    for warning in index.warnings:
        print("警告：{}".format(warning), file=sys.stderr)


def print_header(index: SourceIndex) -> None:
    print("源仓库：{}".format(index.root))
    revision = git_revision(index.root)
    print("源修订：{}".format(revision or "未知（非 git 工作树或未安装 git）"))
    if index.shared_files:
        print("发现 skill：{} 个；shared 文件：{} 个".format(
            len(index.skills), len(index.shared_files)))
    else:
        print("发现 skill：{} 个；shared 目录：{}".format(
            len(index.skills), index.root / SHARED_DIR))


def print_targets(targets: Sequence[Path], dry_run: bool = False) -> None:
    print("目标（{} 个）{}：".format(len(targets), "，dry-run 不写入" if dry_run else ""))
    for target in targets:
        print("  - {}".format(target))


def _print_scope_install(scope: ScopePlan) -> None:
    if scope.status == "linked":
        print("   [linked]    {}（{}；已跳过，不写入）".format(scope.label, scope.note))
        return
    if scope.status == "unknown":
        print("   [skip]      {}（{}；无法确认是否为链接，已跳过）".format(scope.label, scope.note))
        return
    if scope.status == "unchanged" and scope.note:
        print("   [same]      {}（{}）".format(scope.label, scope.note))
        return
    if scope.status == "nondir":
        print("   [error]     {}：路径已存在但不是目录（{}）".format(scope.label, scope.dest))
    if scope.new:
        print("   [new]       {}（{} 个文件）".format(scope.label, len(scope.new)))
    elif scope.updated:
        print("   [update]    {}（{}/{} 个文件有差异）".format(
            scope.label, len(scope.updated), len(scope.expected)))
    if scope.stale:
        shown = ", ".join(scope.stale[:3])
        remaining = "" if len(scope.stale) <= 3 else " 等 {} 个".format(len(scope.stale))
        print("   [stale]     {}：源中不存在的文件 {}{}（保留，不删除）".format(
            scope.label, shown, remaining))
    for message in scope.errors:
        print("   [error]     {}：{}".format(scope.label, message))


def print_install_plan(plan: TargetPlan, dry_run: bool) -> None:
    print("== {}{}".format(plan.target, "  (dry-run，不写入)" if dry_run else ""))
    for scope in plan.scopes:
        _print_scope_install(scope)


def print_check_plan(plan: TargetPlan, verbose: bool) -> None:
    print("== {}".format(plan.target))
    rows: list[tuple[str, ScopePlan, str]] = []
    for scope in plan.scopes:
        if scope.status == "linked":
            continue
        if scope.status == "unknown":
            print("   [skip]      {}（{}；无法核对，未计入 drift）".format(scope.label, scope.note))
            continue
        if scope.status == "unchanged" and scope.note:
            print("   [same]      {}（{}）".format(scope.label, scope.note))
            continue
        for rel in scope.new:
            rows.append(("new", scope, rel))
        for rel in scope.updated:
            rows.append(("updated", scope, rel))
        for rel in scope.stale:
            rows.append(("stale", scope, rel))
        for message in scope.errors:
            print("   [error]     {}：{}".format(scope.label, message))
    limit = None if verbose else DETAIL_LIMIT
    shown_rows = rows if limit is None else rows[:limit]
    for action, scope, rel in shown_rows:
        path = scope.dest.joinpath(*rel.split("/"))
        suffix = "（源中不存在，未删除）" if action == "stale" else ""
        print("   [{}] {}{}".format(action, path, suffix))
    if limit is not None and len(rows) > limit:
        print("   ... 其余 {} 条差异未列出（加 --verbose 查看全部）".format(len(rows) - limit))
    counts = target_counts([plan])
    print("   核对：{}".format(format_counts(counts)))
    if counts["linked"]:
        print("   链接跳过：{} 个落点（junction/符号链接，不核对、不写入）".format(counts["linked"]))
    if counts["drift"] or counts["errors"]:
        print("   RESULT: DRIFT({}) ERRORS({})；修复：python scripts/install-skills.py --target {}".format(
            counts["drift"], counts["errors"], plan.target))
    else:
        print("   RESULT: PASS")


def print_link_install_landing(landing: LinkLanding) -> None:
    if landing.status == "created":
        print("   [linked]     {} -> {}".format(landing.label, landing.source))
    elif landing.status == "would-link":
        print("   [would-link] {} -> {}".format(landing.label, landing.source))
    elif landing.status != "ok":
        print("   [{}] {}：{}".format(landing.status, landing.label, landing.note))


def print_link_check_landing(landing: LinkLanding) -> None:
    print("   [drift]      {}：{}".format(landing.label, landing.note))


# ---------------------------------------------------------------------------
# 子命令实现
# ---------------------------------------------------------------------------

def _load_index() -> SourceIndex:
    index = build_source_index(repo_root())
    print_warnings(index)
    return index


def _load_link_index() -> SourceIndex:
    index = build_link_index(repo_root())
    print_warnings(index)
    return index


def cmd_list(args: argparse.Namespace) -> int:
    index = _load_index()
    print("源仓库：{}".format(index.root))
    revision = git_revision(index.root)
    print("源修订：{}".format(revision or "未知（非 git 工作树或未安装 git）"))
    print("发现 skill：{} 个（深度 <= 2 的 SKILL.md，已排除归档/评测/工具目录）".format(len(index.skills)))
    width = max((len(skill.id) for skill in index.skills), default=8) + 2
    for skill in index.skills:
        print("  {}{}".format(skill.id.ljust(width), skill.rel_path))
    print("shared 文件：{} 个".format(len(index.shared_files)))
    print("")
    print("候选宿主 skills 根（用 --target <目录> 安装；\"存在\"= 磁盘上已有该目录）：")
    for shown in HOST_CANDIDATES:
        candidate = Path(os.path.expanduser(shown))
        print("  [{}] {}".format("存在" if candidate.is_dir() else "缺失", shown))
    if args.target:
        print("命令行 --target 指定的目录：")
        for target in resolve_targets(args.target):
            state, _note = detect_link(target, None)
            label = "存在" if os.path.isdir(target) else "缺失"
            if state == "link":
                label = "链接"
            print("  [{}] {}".format(label, target))
    print("")
    print("下一步：")
    print("  copy 安装：python scripts/install-skills.py --target <目录> --dry-run   # 先看计划")
    print("  link 引用：python scripts/install-skills.py --link --target <目录> --dry-run")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    index = _load_index()
    targets = resolve_targets(args.target)
    print_header(index)
    print_targets(targets, dry_run=args.dry_run)
    failed = False
    plans: list[TargetPlan] = []
    for target in targets:
        print("")
        try:
            assert_target_safe(target, index.root)
            plan = plan_target(index, target)
        except (InstallError, OSError) as exc:
            print("   [error]     {}：{}".format(target, exc), file=sys.stderr)
            failed = True
            continue
        print_install_plan(plan, dry_run=args.dry_run)
        if not args.dry_run:
            try:
                target.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                print("   [error]     无法创建目标目录 {}：{}；请检查权限".format(target, exc),
                      file=sys.stderr)
                failed = True
                continue
            written = 0
            for scope in plan.scopes:
                if scope.status in {"ok", "absent"}:
                    written += _apply_scope(scope)
            counts = target_counts([plan])
            print("   写入：{} 个文件".format(written))
            print("   小结：{}（安装前基线，跑 --check 可确认现在无漂移）".format(format_counts(counts)))
            if counts["errors"]:
                failed = True
        else:
            print("   小结：{}（dry-run，未写入）".format(format_counts(target_counts([plan]))))
        plans.append(plan)
    counts = target_counts(plans)
    print("")
    print("合计：{}".format(format_counts(counts)))
    if args.dry_run:
        print("dry-run：未写入任何文件。去掉 --dry-run 才会真正安装。")
    if failed or counts["errors"]:
        print("RESULT: FAIL（见上方 [error]；修正后重跑）", file=sys.stderr)
        return 1
    if args.dry_run:
        print("RESULT: OK（dry-run）")
    else:
        print("RESULT: OK（已安装；--check 可复核）")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    index = _load_index()
    targets = resolve_targets(args.target)
    print_header(index)
    print_targets(targets)
    failed = False
    plans: list[TargetPlan] = []
    for target in targets:
        print("")
        try:
            assert_target_safe(target, index.root)
            plan = plan_target(index, target)
        except (InstallError, OSError) as exc:
            print("   [error]     {}：{}".format(target, exc), file=sys.stderr)
            failed = True
            continue
        print_check_plan(plan, verbose=args.verbose)
        plans.append(plan)
    counts = target_counts(plans)
    print("")
    print("合计：{}".format(format_counts(counts)))
    if failed or counts["drift"] or counts["errors"]:
        print("RESULT: DRIFT({}) ERRORS({})；用 --target 安装修复，或先 --dry-run 看变更".format(
            counts["drift"], counts["errors"]))
        return 1
    print("RESULT: PASS（安装副本与源仓一致）")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    index = _load_index()
    root = index.root
    destination = normalize_path(args.export)
    _assert_outside_repo(destination, root, "导出目录")
    if os.path.lexists(destination):
        if not destination.is_dir():
            raise InstallError("导出目录存在但不是目录：{}；请换一个目录".format(destination))
        try:
            non_empty = next(destination.iterdir(), None) is not None
        except OSError as exc:
            raise InstallError("无法读取导出目录 {}：{}；请检查权限".format(destination, exc)) from exc
        if non_empty:
            raise InstallError(
                "导出目录非空：{}；为避免混入旧文件，请换一个不存在或空目录".format(destination)
            )
    print_header(index)
    print("导出目录：{}".format(destination))
    destination.mkdir(parents=True, exist_ok=True)
    skills_root = destination / "skills"
    plan = plan_target(index, skills_root)
    written = 0
    for scope in plan.scopes:
        written += _apply_scope(scope)
    errors = [message for scope in plan.scopes for message in scope.errors]
    if errors:
        raise InstallError("导出写入失败：{}".format("；".join(errors[:3])))
    revision = git_revision(root)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "generator": GENERATOR,
        "generatedAt": generated_at,
        "sourceRevision": revision,
        "skills": [skill.id for skill in index.skills],
    }
    manifest_path = destination / MANIFEST_NAME
    try:
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise InstallError("写 MANIFEST 失败 {}：{}".format(manifest_path, exc)) from exc
    verify_counts = target_counts([plan_target(index, skills_root)])
    if verify_counts["drift"] or verify_counts["errors"]:
        raise InstallError(
            "导出后自检失败（{}）；这是脚本缺陷，请附本输出报告".format(format_counts(verify_counts))
        )
    print("")
    print("导出完成：{}".format(destination))
    print("  skills 根：{}".format(skills_root))
    print("  容器级 shared：{}".format(destination / SHARED_DIR))
    print("  MANIFEST：{}".format(manifest_path))
    print("  写入 {} 个文件；自检 PASS（--check 口径 drift=0）".format(written))
    print("  核对命令：python scripts/install-skills.py --check --target \"{}\"".format(skills_root))
    print("  用法：把 {} 整个目录拷到别的机器，或把其中的 skills 拷进宿主 skills 根".format(
        destination.name or destination))
    return 0


def cmd_link_install(args: argparse.Namespace) -> int:
    index = _load_link_index()
    targets = resolve_targets(args.target)
    print_header(index)
    print("模式：link（junction / 符号链接引用源仓；源仓工作区改动即时生效，无 commit 隔离）")
    print_targets(targets, dry_run=args.dry_run)
    failed = False
    total = {"linked": 0, "ok": 0, "conflict": 0, "error": 0}
    for target in targets:
        print("")
        print("== {}".format(target))
        try:
            assert_target_safe(target, index.root)
            if not args.dry_run:
                target.mkdir(parents=True, exist_ok=True)
        except (InstallError, OSError) as exc:
            print("   [error]     {}：{}".format(target, exc), file=sys.stderr)
            failed = True
            continue
        counts = {"linked": 0, "ok": 0, "conflict": 0, "error": 0}
        for landing in link_landings(index, target):
            apply_link_landing(landing, dry_run=args.dry_run)
            print_link_install_landing(landing)
            if landing.status in {"created", "would-link"}:
                counts["linked"] += 1
            elif landing.status == "ok":
                counts["ok"] += 1
            elif landing.status == "conflict":
                counts["conflict"] += 1
            else:
                counts["error"] += 1
        print("   小结：linked={linked} ok={ok} conflict={conflict} error={error}".format(**counts))
        if counts["conflict"] or counts["error"]:
            failed = True
            print("   RESULT: CONFLICT（真实目录/错误指向不会被覆盖；请换新 --target 或人工处理后重试）")
        elif args.dry_run:
            print("   RESULT: OK（dry-run，未创建任何链接）")
        else:
            print("   RESULT: OK（已建立链接；用 --link --check 复核）")
        for key in total:
            total[key] += counts[key]
    print("")
    print("合计：linked={linked} ok={ok} conflict={conflict} error={error}".format(**total))
    if args.dry_run:
        print("dry-run：未创建任何链接。")
    if failed:
        print("RESULT: FAIL（有 conflict/error，见上方明细）", file=sys.stderr)
        return 1
    print("RESULT: OK（link 模式；源仓改动即时生效）")
    return 0


def cmd_link_check(args: argparse.Namespace) -> int:
    index = _load_link_index()
    targets = resolve_targets(args.target)
    print_header(index)
    print("模式：link --check（只读；校验每个落点是否是指向源仓的正确链接）")
    print_targets(targets)
    failed = False
    total = {"ok": 0, "drift": 0}
    for target in targets:
        print("")
        print("== {}".format(target))
        try:
            assert_target_safe(target, index.root)
        except (InstallError, OSError) as exc:
            print("   [error]     {}：{}".format(target, exc), file=sys.stderr)
            failed = True
            continue
        counts = {"ok": 0, "drift": 0}
        drift_landings: list[LinkLanding] = []
        for landing in link_landings(index, target):
            inspect_link_landing(landing)
            if landing.status == "ok":
                counts["ok"] += 1
            else:
                counts["drift"] += 1
                drift_landings.append(landing)
        limit = None if args.verbose else DETAIL_LIMIT
        for landing in (drift_landings if limit is None else drift_landings[:limit]):
            print_link_check_landing(landing)
        if limit is not None and len(drift_landings) > limit:
            print("   ... 其余 {} 条差异未列出（加 --verbose 查看全部）".format(
                len(drift_landings) - limit))
        print("   核对：ok={ok} drift={drift}".format(**counts))
        if counts["drift"]:
            failed = True
            print("   RESULT: DRIFT({})；修复：python scripts/install-skills.py --link --target {}".format(
                counts["drift"], target))
        else:
            print("   RESULT: PASS（所有落点均指向源仓）")
        for key in total:
            total[key] += counts[key]
    print("")
    print("合计：ok={ok} drift={drift}".format(**total))
    if failed or total["drift"]:
        print("RESULT: DRIFT({})；link 模式核对未通过".format(total["drift"]))
        return 1
    print("RESULT: PASS（link 模式全部指向源仓）")
    return 0


def cmd_unlink(args: argparse.Namespace) -> int:
    index = _load_link_index()
    targets = resolve_targets(args.target)
    print_header(index)
    print("模式：unlink（只删除确认指向本仓的链接；真实目录/文件、仓外链接一律保留）")
    print_targets(targets, dry_run=args.dry_run)
    failed = False
    total = {"unlink": 0, "keep": 0}
    for target in targets:
        print("")
        print("== {}".format(target))
        if not os.path.lexists(target):
            print("   [skip]      目标不存在，无需 unlink")
            continue
        try:
            assert_target_safe(target, index.root)
        except (InstallError, OSError) as exc:
            print("   [error]     {}：{}".format(target, exc), file=sys.stderr)
            failed = True
            continue
        counts = {"unlink": 0, "keep": 0}
        for landing in link_landings(index, target):
            if not os.path.lexists(landing.dest):
                continue
            state, _note = detect_link(landing.dest, None)
            if state != "link":
                counts["keep"] += 1
                print("   [keep]       {}：真实目录/文件，保留（不是链接）".format(landing.label))
                continue
            resolved = os.path.realpath(landing.dest)
            if not _points_into_repo(landing.dest, index.root):
                counts["keep"] += 1
                print("   [keep]       {}：链接指向仓外（{}），保留".format(landing.label, resolved))
                continue
            if args.dry_run:
                counts["unlink"] += 1
                print("   [would-unlink] {} -> {}".format(landing.label, resolved))
                continue
            try:
                _remove_dir_link(landing.dest)
            except OSError as exc:
                failed = True
                print("   [error]      {}：删除链接失败：{}；请检查权限".format(landing.label, exc))
                continue
            counts["unlink"] += 1
            print("   [unlink]     {} -> {}".format(landing.label, resolved))
        print("   小结：unlink={unlink} keep={keep}".format(**counts))
        for key in total:
            total[key] += counts[key]
    print("")
    print("合计：unlink={unlink} keep={keep}".format(**total))
    if args.dry_run:
        print("dry-run：未删除任何链接。")
    if failed:
        print("RESULT: FAIL（见上方 [error]）", file=sys.stderr)
        return 1
    print("RESULT: OK（dry-run）" if args.dry_run else "RESULT: OK（链接已清理，真实目录/文件未动）")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="install-skills.py",
        description="跨平台安装 / 链接 / 导出 / 核对 tenger-skills 体系（Python 标准库；Windows/macOS/Linux 通用）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=USAGE_EPILOG,
    )
    parser.add_argument(
        "--target", action="append", default=[], metavar="DIR",
        help="宿主 skills 根，可重复（如 ~/.dsh/skills）；安装/链接布局见下方说明",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="只打印计划，不写入/不创建（copy 安装、--link、--unlink 均支持）",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="只读核对：默认 copy 模式比文件集合 + sha256；与 --link 同用时校验链接指向是否正确",
    )
    parser.add_argument(
        "--link", action="store_true",
        help="链接模式安装：skill 与 shared 落点建为指向源仓的链接（Windows junction / Unix 符号链接），"
             "源仓改动即时生效；与 --check 同用时校验链接指向",
    )
    parser.add_argument(
        "--unlink", action="store_true",
        help="只删除确认指向本仓的链接（skill 与 shared 落点）；真实目录/文件与仓外链接保留并计入 keep",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="列出发现的 skill 与候选宿主 skills 根",
    )
    parser.add_argument(
        "--export", metavar="DIR",
        help="导出 self-contained 安装包到 DIR（DIR/skills + DIR/shared + MANIFEST.json）；不可与 --link 同用",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="核对时列出全部差异路径（默认每个 target 最多列 %d 条）" % DETAIL_LIMIT,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        # Windows 控制台默认 GBK：中文口径打出去会成乱码，读输出的人只能猜
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = build_parser()
    args = parser.parse_args(argv)
    modes = [bool(args.check), bool(args.list), args.export is not None, bool(args.unlink)]
    if sum(modes) > 1:
        parser.error("--check / --list / --export / --unlink 只能选一个")
    if args.link and args.export is not None:
        parser.error("--link 不能与 --export 同用：导出是可移植的 self-contained 拷贝包，链接不可移植")
    if args.link and args.list:
        parser.error("--link 不能与 --list 同用（--list 只读清单，不安装）")
    if args.link and args.unlink:
        parser.error("--link 与 --unlink 互斥，只能选一个")
    try:
        if args.export is not None:
            if args.target:
                parser.error("--export 不能与 --target 同用（导出=生成 self-contained 包）")
            if args.dry_run:
                parser.error("--export 不支持 --dry-run（导出目录必须为空，失败可整目录删掉重试）")
            return cmd_export(args)
        if args.list:
            if args.dry_run:
                parser.error("--list 本身只读，不需要 --dry-run")
            return cmd_list(args)
        if args.unlink:
            if not args.target:
                parser.error("--unlink 需要至少一个 --target DIR，例如 --target ~/.dsh/skills")
            return cmd_unlink(args)
        if args.check:
            if args.dry_run:
                parser.error("--check 本身只读，不需要 --dry-run")
            if not args.target:
                parser.error("--check 需要至少一个 --target DIR，例如 --target ~/.dsh/skills")
            return cmd_link_check(args) if args.link else cmd_check(args)
        if args.link:
            if not args.target:
                parser.error("--link 需要至少一个 --target DIR，例如 --target ~/.dsh/skills")
            return cmd_link_install(args)
        if not args.target:
            parser.print_help()
            print("")
            print("提示：未指定动作。copy 安装用 --target，link 引用用 --link --target，"
                  "核对用 --check，导出用 --export；先加 --dry-run 看计划。")
            return 0
        return cmd_install(args)
    except InstallError as exc:
        print("错误：{}".format(exc), file=sys.stderr)
        return 1
    except OSError as exc:
        print("错误：文件系统操作失败：{}；请检查目标目录权限后重试".format(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
