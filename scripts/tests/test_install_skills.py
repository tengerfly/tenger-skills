"""scripts/install-skills.py 的跨平台安装器回归测试（unittest；真实临时目录，setUp/tearDown 清理）。

覆盖任务验收的六条：
1) 发现 >=40 个 skill，含 auto-test 与 workflow，不含 evals/ 夹具与 docs/ 归档伪 skill；
2) 安装到 <host>/skills 后，skill 落点与 shared 三落点齐全；
3) 二次安装幂等（全部 unchanged，写入 0 个文件），且 --check exit 0；
4) 篡改一个安装文件后 --check exit 1 且报出该文件，恢复后 exit 0；
5) 链接目标（符号链接 / Windows junction）被跳过；Windows 无符号链接权限时 skipTest；
6) 派生目录/文件（__pycache__ / node_modules / dist / coverage / .venv / *.pyc / .DS_Store）不被拷贝。

补充覆盖链接引用模式（--link / --link --check / --unlink）：
7) --link 后 skill 与 shared 落点为指向源仓的链接（Windows junction 实测 / POSIX 符号链接），
   --link --check PASS；源仓文件改动通过链接即时可见（无 commit 隔离）；
8) --link --check 把指向错误/缺失/真实目录都判 drift，exit 1；--link 安装遇到真实目录只报
   conflict、不覆盖不删除；
9) --unlink 只删「确认指向本仓」的链接；真实目录/文件、仓外链接保留并计入 keep。

测试策略（控制运行时间）：
- 真实仓：只读发现 + 一次全量 copy 安装（45 个 skill / 2000+ 文件，临时目录 IO 较慢，单次约 10-20s）；
  copy 模式全量检查与全量 link/check/unlink 由下方合成仓用例 + 交付时的手动验收命令覆盖
  （Windows 每个 junction 要起一次 cmd 进程，全量 47 个落点约 20s，不适合放进每轮单测）。
- 合成仓：把真实 auto-test / workflow skill 目录与真实 shared 契约文件复制进临时仓，再把
  install-skills.py 复制到 <合成仓>/scripts/ 下按路径加载并调用 main()。这样走同一份 CLI 逻辑，
  但只拷贝几十个文件，幂等 / 漂移 / 链接 / 导出用例可以在秒级完成。
- 所有写入都在临时目录；除只读扫描源仓外不修改仓库。
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "scripts" / "install-skills.py"
COUNT_PATTERN = re.compile(r"new=(\d+) updated=(\d+) unchanged=(\d+) stale=(\d+) drift=(\d+)")


def load_module(name: str, path: Path):
    """按路径加载模块（scripts/install-skills.py 文件名带连字符，不能直接 import）。"""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # dataclass 需要能从 sys.modules 反查模块；按路径加载时须先手动登记再 exec_module。
    sys.modules[spec.name] = module
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


installer = load_module("install_skills_under_test", INSTALLER)


def run_cli(module, *argv: str) -> tuple[int, str, str]:
    """在进程内跑 CLI，返回 (exit code, stdout, stderr)；不落子进程、不污染测试输出。"""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = module.main(list(argv))
    return code, out.getvalue(), err.getvalue()


def parse_counts(output: str) -> dict[str, int]:
    match = COUNT_PATTERN.search(output)
    if not match:
        raise AssertionError("输出里找不到 new/updated/unchanged/stale/drift 计数：\n" + output)
    keys = ("new", "updated", "unchanged", "stale", "drift")
    return {key: int(value) for key, value in zip(keys, match.groups())}


class TempDirTestCase(unittest.TestCase):
    """每个测试一个真实临时目录，tearDown 递归清理。"""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="install-skills-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)


def build_synthetic_repo(tmp: Path) -> tuple[Path, Path]:
    """构造合成仓：真实 auto-test / workflow skill + 真实 shared 契约 + 派生垃圾。

    返回 (仓库根, 仓内安装器脚本路径)；脚本放 <repo>/scripts/ 下，加载后 repo_root() 即合成仓。
    """
    repo = tmp / "synthetic-repo"
    (repo / "scripts").mkdir(parents=True)
    script = repo / "scripts" / "install-skills.py"
    shutil.copy2(INSTALLER, script)
    skills, _warnings = installer.discover_skills(ROOT)
    by_id = {skill.id: skill for skill in skills}
    for skill_id, dest_rel in (("auto-test", "Test/auto-test"), ("workflow", "workflow")):
        shutil.copytree(by_id[skill_id].source, repo / dest_rel)
    # 只放最小 shared 契约（真实文件），够验证三落点即可；全量 40 文件由真实仓用例覆盖。
    shared = repo / "shared"
    shared.mkdir()
    shutil.copy2(ROOT / "shared" / "skill-contract.md", shared / "skill-contract.md")
    (shared / "templates").mkdir()
    (shared / "templates" / "demo.md").write_text("# demo template\n", encoding="utf-8")
    # 派生项：安装时不得被拷贝
    junk_cases = (
        repo / "Test" / "auto-test" / "__pycache__",
        repo / "Test" / "auto-test" / "node_modules" / "pkg",
        repo / "workflow" / "dist",
    )
    for junk_dir in junk_cases:
        junk_dir.mkdir(parents=True)
        (junk_dir / "junk.txt").write_text("junk\n", encoding="utf-8")
    (repo / "Test" / "auto-test" / "compiled.pyc").write_text("junk", encoding="utf-8")
    (repo / "Test" / "auto-test" / ".DS_Store").write_text("junk", encoding="utf-8")
    return repo, script


# ---------------------------------------------------------------------------
# 1) 发现：真实仓 + 合成仓；CLI 入口
# ---------------------------------------------------------------------------

class DiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skills, cls.warnings = installer.discover_skills(ROOT)

    def test_discovers_at_least_forty_skills_with_key_entries(self):
        ids = [skill.id for skill in self.skills]
        self.assertGreaterEqual(len(ids), 40, "仓库 skill 数突然变少，先确认发现逻辑是否被改坏")
        self.assertIn("auto-test", ids)
        self.assertIn("workflow", ids)
        self.assertEqual(ids.count("auto-test"), 1, "docs/ 归档里的旧 auto-test 不得被重复发现")
        self.assertEqual(ids, sorted(ids), "skills 必须按 id 确定性排序")
        self.assertEqual(len(ids), len(set(ids)), "skill id 不得重复")

    def test_sources_cover_root_level_and_category_layout(self):
        by_id = {skill.id: skill for skill in self.skills}
        self.assertEqual(by_id["workflow"].rel_path, "workflow", "根级 workflow/SKILL.md 必须被发现")
        self.assertRegex(by_id["auto-test"].rel_path, r"^[^/]+/auto-test$",
                         "分类目录下的 <分类>/<skill>/SKILL.md 必须被发现")
        for skill in self.skills:
            self.assertTrue((skill.source / "SKILL.md").is_file())
            depth = len(skill.rel_path.split("/"))
            self.assertIn(depth, (1, 2), "发现范围只能是深度 <= 2 的 skill 目录：{}".format(skill.rel_path))

    def test_excluded_archives_and_fixtures_are_not_skills(self):
        rels = {skill.rel_path for skill in self.skills}
        excluded_prefixes = (
            "evals/", "docs/", "issue/", "chats/", "governance/", "scripts/", "shared/",
            ".spec/", ".tmp-eval/", "templates/", "skill-knowledge/", "evolution/", "bug-patterns/",
        )
        offenders = sorted(rel for rel in rels if rel.startswith(excluded_prefixes))
        self.assertEqual(offenders, [], "归档/评测/工具目录里的伪 skill 不得被发现")
        ids = {skill.id for skill in self.skills}
        for fixture_id in ("probe-skill", "probe-legacy", "probe-portable"):
            self.assertNotIn(fixture_id, ids, "evals/ 夹具被当成 skill 发现了")
        self.assertEqual(self.warnings, [], "真实仓库 discovery 不应有 frontmatter 警告")


class CliEntryPointTests(unittest.TestCase):
    """真实入口冒烟：用子进程跑「用户会敲的那条命令」。"""

    @staticmethod
    def run_script(*argv: str) -> tuple[int, str, str]:
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            [sys.executable, str(INSTALLER), *argv],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(ROOT), env=env, check=False,
        )
        return result.returncode, result.stdout, result.stderr

    def test_list(self):
        code, out, err = run_cli(installer, "--list")
        self.assertEqual(code, 0, out + err)
        self.assertIn("auto-test", out)
        self.assertIn("workflow", out)
        self.assertIn("候选宿主 skills 根", out)
        self.assertIn("~/.dsh/skills", out)
        self.assertIn("--link", out, "--list 的下一步提示应同时给出 copy 与 link 两种用法")

    def test_help_via_subprocess(self):
        code, out, err = self.run_script("--help")
        self.assertEqual(code, 0, out + err)
        for option in ("--target", "--dry-run", "--check", "--list", "--export", "--link", "--unlink"):
            self.assertIn(option, out)
        self.assertIn("commit", out, "--help 应说明 link 模式无 commit 隔离的风险")

    def test_link_export_conflict_exits_2(self):
        # 参数互斥：--link 与 --export 同用必须 exit 2（不是运行期错误）
        code, _out, err = self.run_script(
            "--link", "--export", str(Path(tempfile.gettempdir()) / "install-skills-never-created"))
        self.assertEqual(code, 2)
        self.assertIn("--link", err)


class SyntheticDiscoveryTests(TempDirTestCase):
    @staticmethod
    def write_skill(root: Path, rel: str, name: str) -> None:
        directory = root / rel
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "SKILL.md").write_text(
            "---\nname: {}\ndescription: fixture\n---\n\n# {}\n".format(name, name), encoding="utf-8")

    def test_frontmatter_name_wins_and_mismatch_warns(self):
        root = self.tmp / "repo"
        self.write_skill(root, "PRD/dir-name", "front-name")
        skills, warnings = installer.discover_skills(root)
        self.assertEqual([skill.id for skill in skills], ["front-name"],
                         "skill id 必须取 frontmatter name，而不是目录名")
        self.assertEqual(skills[0].rel_path, "PRD/dir-name")
        self.assertTrue(any("dir-name" in warning and "front-name" in warning for warning in warnings),
                        "目录名与 frontmatter 不一致必须告警：{}".format(warnings))

    def test_top_level_exclusions_are_not_scanned(self):
        root = self.tmp / "repo"
        for rel, name in (
            ("PRD/real-skill", "real-skill"),
            ("workflow", "workflow"),
            ("evals/set/fixtures/fake", "fake-eval"),
            ("docs/archived-skill", "archived-skill"),
            ("scripts/tool-skill", "tool-skill"),
            ("shared/template", "template-skill"),
        ):
            self.write_skill(root, rel, name)
        skills, _warnings = installer.discover_skills(root)
        self.assertEqual([skill.id for skill in skills], ["real-skill", "workflow"])

    def test_duplicate_ids_are_reported_as_error(self):
        root = self.tmp / "repo"
        self.write_skill(root, "PRD/one", "dup")
        self.write_skill(root, "DEV/two", "dup")
        with self.assertRaises(installer.InstallError) as caught:
            installer.discover_skills(root)
        message = str(caught.exception)
        self.assertIn("dup", message)
        self.assertIn("PRD/one", message)
        self.assertIn("DEV/two", message)


# ---------------------------------------------------------------------------
# 2-6) 合成仓 CLI：布局 / 幂等 / 漂移 / 排除项 / 链接 / 导出
# ---------------------------------------------------------------------------

class SyntheticCliTests(TempDirTestCase):
    def setUp(self):
        super().setUp()
        self.repo, self.script = build_synthetic_repo(self.tmp)
        self.module = load_module("install_skills_synthetic_repo", self.script)
        self.host = self.tmp / "host"
        self.target = self.host / "skills"

    def cli(self, *argv: str):
        return run_cli(self.module, *argv)

    def install(self, *extra: str):
        return self.cli("--target", str(self.target), *extra)

    def check(self):
        return self.cli("--check", "--target", str(self.target))

    def test_install_writes_skill_and_shared_three_landings(self):
        code, out, err = self.install()
        self.assertEqual(code, 0, out + err)
        self.assertTrue((self.target / "auto-test" / "SKILL.md").is_file())
        self.assertTrue((self.target / "shared" / "skill-contract.md").is_file())
        self.assertTrue((self.target / "auto-test" / "shared" / "skill-contract.md").is_file())
        self.assertTrue((self.host / "shared" / "skill-contract.md").is_file())
        self.assertTrue((self.host / "shared" / "templates" / "demo.md").is_file(),
                        "shared 子目录必须随三落点一起分发")
        self.assertEqual((self.target / "auto-test" / "SKILL.md").read_bytes(),
                         (self.repo / "Test" / "auto-test" / "SKILL.md").read_bytes(),
                         "安装副本内容必须与源仓一致")
        installed = {path.name for path in self.target.iterdir() if (path / "SKILL.md").is_file()}
        self.assertEqual(installed, {"auto-test", "workflow"})

        banned = {"__pycache__", "node_modules", "dist", "coverage", ".venv", ".git"}
        self.assertFalse(any(path.name in banned for path in self.target.rglob("*")),
                         "安装副本不得包含派生目录")
        self.assertFalse(any(path.suffix == ".pyc" for path in self.target.rglob("*")),
                         "安装副本不得包含 *.pyc")
        self.assertFalse(any(path.name == ".DS_Store" for path in self.target.rglob("*")),
                         "安装副本不得包含 .DS_Store")

    def test_second_install_is_idempotent_and_check_passes(self):
        first_code, first_out, first_err = self.install()
        self.assertEqual(first_code, 0, first_out + first_err)
        second_code, second_out, second_err = self.install()
        self.assertEqual(second_code, 0, second_out + second_err)
        counts = parse_counts(second_out)
        self.assertEqual((counts["new"], counts["updated"]), (0, 0),
                         "二次安装必须全部 unchanged：\n" + second_out)
        self.assertGreater(counts["unchanged"], 0)
        self.assertIn("写入：0 个文件", second_out, "幂等安装不应写任何文件")
        code, out, err = self.check()
        self.assertEqual(code, 0, out + err)
        self.assertIn("RESULT: PASS", out)
        check_counts = parse_counts(out)
        self.assertEqual(check_counts["drift"], 0)
        self.assertGreater(check_counts["unchanged"], 0)
        self.assertIn("linked=0", out)

    def test_check_detects_tampering_and_recovers(self):
        self.assertEqual(self.install()[0], 0)
        target_file = self.target / "auto-test" / "SKILL.md"
        original = target_file.read_bytes()
        try:
            target_file.write_bytes(original + b"\n<!-- tampered by test -->\n")
            code, out, err = self.check()
            self.assertEqual(code, 1, out + err)
            self.assertIn("[updated]", out)
            self.assertIn("auto-test", out)
            self.assertIn("SKILL.md", out)
            self.assertIn("updated=1", out)
            self.assertIn("RESULT: DRIFT", out)
        finally:
            target_file.write_bytes(original)
        code, out, err = self.check()
        self.assertEqual(code, 0, out + err)
        self.assertIn("RESULT: PASS", out)

        # <target>/shared 落点也在核对口径内
        target_shared = self.target / "shared" / "skill-contract.md"
        shared_original = target_shared.read_bytes()
        try:
            target_shared.write_bytes(shared_original + b"\n<!-- drift -->\n")
            code, out, err = self.check()
            self.assertEqual(code, 1, out + err)
            self.assertIn("skill-contract.md", out)
        finally:
            target_shared.write_bytes(shared_original)
        self.assertEqual(self.check()[0], 0)

        # 目标多出源中不存在的文件：报 stale（不自动删除），也算漂移
        leftover = self.target / "auto-test" / "leftover.md"
        leftover.write_text("old\n", encoding="utf-8")
        try:
            code, out, err = self.check()
            self.assertEqual(code, 1, out + err)
            self.assertIn("[stale]", out)
            self.assertIn("leftover.md", out)
            self.assertTrue(leftover.is_file(), "--check 不得删除目标里的多余文件")
        finally:
            leftover.unlink()
        self.assertEqual(self.check()[0], 0)

    def test_dry_run_writes_nothing(self):
        code, out, err = self.install("--dry-run")
        self.assertEqual(code, 0, out + err)
        self.assertFalse(self.target.exists(), "dry-run 不得创建目标目录")
        self.assertIn("dry-run", out)

    def test_check_on_missing_target_reports_drift_without_writing(self):
        code, out, err = self.check()
        self.assertEqual(code, 1, out + err)
        self.assertIn("RESULT: DRIFT", out)
        self.assertFalse(self.target.exists(), "--check 必须只读，不得创建任何目录")

    def test_install_does_not_touch_foreign_skills_or_container_files(self):
        foreign = self.target / "third-party-skill"
        foreign.mkdir(parents=True)
        (foreign / "SKILL.md").write_text("---\nname: third-party-skill\n---\n", encoding="utf-8")
        sentinel = self.host / "keep-me.txt"
        sentinel.write_text("keep\n", encoding="utf-8")
        self.assertEqual(self.install()[0], 0)
        self.assertTrue((foreign / "SKILL.md").is_file(), "目标里额外的 skill 绝不能被删除")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")
        self.assertEqual(self.install()[0], 0)
        self.assertTrue((foreign / "SKILL.md").is_file(), "二次安装也不得动额外 skill")

    def test_export_is_self_contained_and_check_passes(self):
        export_dir = self.tmp / "tenger-skills-pack"
        code, out, err = self.cli("--export", str(export_dir))
        self.assertEqual(code, 0, out + err)
        self.assertTrue((export_dir / "skills" / "auto-test" / "SKILL.md").is_file())
        self.assertTrue((export_dir / "shared" / "skill-contract.md").is_file())
        self.assertTrue((export_dir / "skills" / "auto-test" / "shared" / "skill-contract.md").is_file())
        manifest_path = export_dir / "MANIFEST.json"
        self.assertTrue(manifest_path.is_file(), "--export 必须写 MANIFEST.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for key in ("skills", "sourceRevision", "generatedAt"):
            self.assertIn(key, manifest)
        self.assertEqual(manifest["skills"], ["auto-test", "workflow"])
        self.assertRegex(manifest["generatedAt"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertIsNone(manifest["sourceRevision"], "合成仓不是 git 工作树，sourceRevision 应为 null")
        code, out, err = self.cli("--check", "--target", str(export_dir / "skills"))
        self.assertEqual(code, 0, out + err)
        self.assertIn("RESULT: PASS", out)

    def test_export_refuses_non_empty_directory(self):
        export_dir = self.tmp / "not-empty"
        export_dir.mkdir()
        (export_dir / "old.txt").write_text("old\n", encoding="utf-8")
        code, _out, err = self.cli("--export", str(export_dir))
        self.assertEqual(code, 1, "非空导出目录必须拒绝，避免混入旧文件")
        self.assertIn("非空", err)

    def test_symbolic_link_target_is_skipped(self):
        linked_source = shutil.copytree(self.repo / "Test" / "auto-test", self.tmp / "linked-source")
        self.target.mkdir(parents=True)
        link = self.target / "auto-test"
        try:
            os.symlink(linked_source, link, target_is_directory=True)
        except (OSError, NotImplementedError, AttributeError) as exc:
            self.skipTest("当前环境无法创建符号链接（Windows 需开发者模式/管理员）：{}".format(exc))
        try:
            code, out, err = self.install()
            self.assertEqual(code, 0, out + err)
            linked_lines = [line for line in out.splitlines() if "auto-test" in line]
            self.assertTrue(any("[linked]" in line for line in linked_lines),
                            "符号链接目标必须报 linked：{}".format(out))
            self.assertTrue(link.is_symlink(), "链接本身不得被删除/替换")
            self.assertFalse((linked_source / "shared").exists(),
                             "跳过链接时不得往链接目标里写内嵌 shared")
            self.assertTrue((self.target / "workflow" / "SKILL.md").is_file(),
                            "链接之外的 skill 仍应正常安装")
            code, out, err = self.check()
            self.assertEqual(code, 0, out + err)
            self.assertIn("linked=1", out)
        finally:
            try:
                os.unlink(link)
            except OSError:
                try:
                    os.rmdir(link)
                except OSError:
                    pass

    @unittest.skipUnless(os.name == "nt", "Windows junction 专项")
    def test_windows_junction_target_is_skipped(self):
        linked_source = shutil.copytree(self.repo / "Test" / "auto-test", self.tmp / "linked-source")
        self.target.mkdir(parents=True)
        junction = self.target / "auto-test"
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(junction), str(linked_source)],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            self.skipTest("当前环境无法创建 junction：{}".format((result.stderr or result.stdout).strip()))
        try:
            # junction 不是符号链接：Path.is_symlink() 为 False，installer 必须靠重解析点识别
            self.assertTrue(junction.is_dir())
            self.assertEqual(installer.detect_link(junction, linked_source)[0], "link",
                             "junction 必须被识别为链接")
            code, out, err = self.install()
            self.assertEqual(code, 0, out + err)
            self.assertIn("[linked]", out)
            self.assertFalse((linked_source / "shared").exists(),
                             "跳过 junction 时不得往源目录写内嵌 shared")
            self.assertTrue((self.target / "workflow" / "SKILL.md").is_file())
        finally:
            try:
                os.rmdir(junction)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# 7-9) 链接引用模式：--link / --link --check / --unlink
# ---------------------------------------------------------------------------

class LinkModeTests(TempDirTestCase):
    def setUp(self):
        super().setUp()
        self.repo, self.script = build_synthetic_repo(self.tmp)
        self.module = load_module("install_skills_link_mode", self.script)
        self.host = self.tmp / "host"
        self.target = self.host / "skills"
        self.skill_sources = {
            "auto-test": self.repo / "Test" / "auto-test",
            "workflow": self.repo / "workflow",
        }
        self.repo_shared = self.repo / "shared"

    def cli(self, *argv: str):
        return run_cli(self.module, *argv)

    def link_install(self, *extra: str):
        return self.cli("--link", "--target", str(self.target), *extra)

    def link_check(self):
        return self.cli("--link", "--check", "--target", str(self.target))

    def unlink(self, *extra: str):
        return self.cli("--unlink", "--target", str(self.target), *extra)

    def skip_if_link_unsupported(self, code: int, out: str, err: str) -> None:
        combined = (out or "") + (err or "")
        if code != 0 and ("创建 junction 失败" in combined or "创建符号链接失败" in combined):
            self.skipTest("当前环境无法创建目录链接：{}".format(combined.strip()[:300]))

    def _remove_link_or_skip(self, path: Path) -> None:
        try:
            self.module._remove_dir_link(path)
        except OSError as exc:
            self.skipTest("当前环境无法移除目录链接：{}".format(exc))

    def test_link_install_check_and_live_view(self):
        """链接安装 + --link --check + 源仓改动即时可见（Windows junction 实测在其中）。"""
        code, out, err = self.link_install()
        self.skip_if_link_unsupported(code, out, err)
        self.assertEqual(code, 0, out + err)
        for skill_id, source in self.skill_sources.items():
            landing = self.target / skill_id
            self.assertTrue(landing.is_dir(), skill_id)
            self.assertEqual(self.module.detect_link(landing, source)[0], "link",
                             "link 落点必须是链接：{}".format(skill_id))
            self.assertTrue(self.module._same_path(landing, source), skill_id)
        self.assertEqual(self.module.detect_link(self.target / "shared", self.repo_shared)[0], "link")
        self.assertEqual(self.module.detect_link(self.host / "shared", self.repo_shared)[0], "link")
        self.assertEqual((self.target / "auto-test" / "SKILL.md").read_bytes(),
                         (self.skill_sources["auto-test"] / "SKILL.md").read_bytes())
        expected_landings = len(self.skill_sources) + 2
        self.assertIn("linked={}".format(expected_landings), out)
        # link 模式不生成每 skill 内嵌 shared（由两个 shared 落点承接）
        self.assertFalse((self.target / "auto-test" / "shared").exists())
        if os.name == "nt":
            # Windows 应使用 junction：Path.is_symlink() 为 False，但仍能被识别为链接
            self.assertFalse((self.target / "auto-test").is_symlink(),
                             "Windows 应使用 junction 而非符号链接")
        code, out, err = self.link_check()
        self.assertEqual(code, 0, out + err)
        self.assertIn("RESULT: PASS", out)
        self.assertIn("drift=0", out)
        # 幂等：再装一次应全部 ok，不重建
        code, out, err = self.link_install()
        self.assertEqual(code, 0, out + err)
        self.assertIn("linked=0 ok={}".format(expected_landings), out)
        # 源仓工作区改动通过链接即时可见（无 commit 隔离）
        source_file = self.skill_sources["auto-test"] / "SKILL.md"
        original = source_file.read_bytes()
        try:
            source_file.write_bytes(original + b"\n<!-- changed in repo working tree -->\n")
            self.assertIn(b"changed in repo working tree",
                          (self.target / "auto-test" / "SKILL.md").read_bytes(),
                          "link 模式应即时看到源仓工作区改动")
        finally:
            source_file.write_bytes(original)
        self.assertEqual(self.link_check()[0], 0, "恢复源文件后链接核对仍应 PASS")

    def test_link_check_drift_conflict_and_unlink_safety(self):
        """指向错误/真实目录判 drift；安装不覆盖；unlink 只删本仓链接。"""
        code, out, err = self.link_install()
        self.skip_if_link_unsupported(code, out, err)
        self.assertEqual(code, 0, out + err)
        # 一个落点换成真实目录（模拟 copy 模式混用），另一个换成仓外链接
        auto_link = self.target / "auto-test"
        self._remove_link_or_skip(auto_link)
        auto_link.mkdir()
        (auto_link / "SKILL.md").write_text("real dir content", encoding="utf-8")
        workflow_link = self.target / "workflow"
        self._remove_link_or_skip(workflow_link)
        external = self.tmp / "external-dir"
        external.mkdir()
        (external / "SKILL.md").write_text("external", encoding="utf-8")
        try:
            self.module._create_dir_link(workflow_link, external)
        except self.module.InstallError as exc:
            self.skipTest("当前环境无法创建目录链接：{}".format(exc))
        code, out, err = self.link_check()
        self.assertEqual(code, 1, out + err)
        self.assertIn("drift=2", out)
        self.assertIn("RESULT: DRIFT", out)
        self.assertIn("auto-test", out)
        self.assertIn("workflow", out)
        # --link 安装遇到真实目录/错误指向只报 conflict，不覆盖不删除
        code, out, err = self.link_install()
        self.assertEqual(code, 1, out + err)
        self.assertIn("conflict", out)
        self.assertTrue((auto_link / "SKILL.md").is_file(), "真实目录内容不得被删除")
        self.assertTrue(self.module._same_path(workflow_link, external),
                        "错误指向的链接不得被覆盖")
        # --unlink 只删两个指向本仓的 shared 链接；真实目录与仓外链接保留
        code, out, err = self.unlink()
        self.assertEqual(code, 0, out + err)
        self.assertIn("unlink=2 keep=2", out)
        self.assertFalse(os.path.lexists(self.target / "shared"), "skills 根级 shared 链接应被删除")
        self.assertFalse(os.path.lexists(self.host / "shared"), "容器级 shared 链接应被删除")
        self.assertTrue((auto_link / "SKILL.md").is_file(), "真实目录必须保留")
        self.assertTrue(os.path.lexists(workflow_link), "仓外链接必须保留")
        self.assertTrue(self.module._same_path(workflow_link, external))

    def test_link_dry_run_and_missing_target_are_read_only(self):
        code, out, err = self.link_install("--dry-run")
        self.assertEqual(code, 0, out + err)
        self.assertFalse(self.target.exists(), "--link --dry-run 不得创建目标目录或链接")
        self.assertIn("dry-run", out)
        code, out, err = self.link_check()
        self.assertEqual(code, 1, out + err)
        self.assertIn("RESULT: DRIFT", out)
        self.assertFalse(self.target.exists(), "--link --check 必须只读")



# ---------------------------------------------------------------------------
# 真实仓全量安装（45 个 skill / 2000+ 文件一条端到端证据）
# ---------------------------------------------------------------------------

class RealRepoInstallTests(TempDirTestCase):
    def test_full_repo_install(self):
        index = installer.build_source_index(ROOT)
        host = self.tmp / "host"
        target = host / "skills"
        code, out, err = run_cli(installer, "--target", str(target))
        self.assertEqual(code, 0, out + err)
        self.assertTrue((target / "auto-test" / "SKILL.md").is_file())
        self.assertTrue((target / "shared" / "skill-contract.md").is_file())
        self.assertTrue((target / "auto-test" / "shared" / "skill-contract.md").is_file())
        self.assertTrue((host / "shared" / "skill-contract.md").is_file())
        self.assertTrue((target / "shared" / "gate-policy.md").is_file(),
                        "真实 shared 全量（40 个文件）必须落到 skills 根级 shared")
        self.assertEqual((target / "auto-test" / "SKILL.md").read_bytes(),
                         (next(skill.source for skill in index.skills if skill.id == "auto-test")
                          / "SKILL.md").read_bytes())
        installed = {path.name for path in target.iterdir() if (path / "SKILL.md").is_file()}
        self.assertEqual(installed, {skill.id for skill in index.skills},
                         "所有发现的 skill 都应安装（且不得混入外来 skill）")
        self.assertFalse(any(path.name == "__pycache__" for path in target.rglob("*")),
                         "全量安装也不得拷贝 __pycache__")

if __name__ == "__main__":
    unittest.main()
