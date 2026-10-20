"""resign 子命令：漂移检测与授权写盘的反向对照。

判据（每条都要有反例）：
1. 绑定与磁盘一致 → 0 条待重签，退出 0；
2. 字节改过未重签 → 报 1 条待重签，dry-run 退出 1；
3. 不给 --decision 写盘 → 报错拒绝（重签＝批准行为）；
4. 给 --decision 写盘 → 台账更新，再查为 0 条。
"""
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "validate_core.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _project(tmp: Path, digest: str) -> Path:
    spec = tmp / ".spec"
    spec.mkdir(parents=True)
    (spec / "目标.md").write_text("v1", encoding="utf-8")
    (spec / "manifest.yaml").write_text(
        "artifacts:\n"
        "  - artifactId: SUBJ-1\n"
        "    type: decision\n"
        "    path: .spec/目标.md\n"
        "    status: APPROVED\n"
        "  - artifactId: EVID-1\n"
        "    type: validation-report\n"
        "    path: .spec/目标.md\n"
        "    status: REVIEW\n"
        "    subjectDigests:\n"
        f"      SUBJ-1: {digest}\n",
        encoding="utf-8",
    )
    return tmp


def _run(project: Path, *args: str):
    return subprocess.run([sys.executable, str(SCRIPT), "resign", "--project-root", str(project), *args],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


class ResignTest(unittest.TestCase):
    def test_clean_when_digest_matches(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _project(tmp, "0" * 64)
            sha = _sha(tmp / ".spec" / "目标.md")
            manifest = tmp / ".spec" / "manifest.yaml"
            manifest.write_text(manifest.read_text(encoding="utf-8").replace("0" * 64, sha), encoding="utf-8")
            r = _run(tmp)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("无需重签", r.stdout)

    def test_detects_drift_and_dry_run_fails(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _project(tmp, "0" * 64)  # 台账记的是错的值
            r = _run(tmp)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("1 条 binding 与磁盘不符", r.stdout)
            self.assertIn("dry-run", r.stdout)

    def test_apply_without_decision_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _project(tmp, "0" * 64)
            r = _run(tmp, "--apply")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("必须给 --decision", r.stdout + r.stderr)

    def test_apply_with_decision_writes_and_clears(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _project(tmp, "0" * 64)
            r = _run(tmp, "--apply", "--decision", "DEC-TEST-1")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("已写盘 1 条", r.stdout)
            r2 = _run(tmp)
            self.assertIn("无需重签", r2.stdout)

    def test_subject_absent_from_manifest_is_reported_not_skipped(self):
        # 「查不到」不等于「一致」：subject 不在台账里时无法重签，必须报出来；
        # 静默跳过会让这类 binding 永远留在「无需重签」里。
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _project(tmp, "0" * 64)
            manifest = tmp / ".spec" / "manifest.yaml"
            manifest.write_text(manifest.read_text(encoding="utf-8")
                                .replace("SUBJ-1: " + "0" * 64, "GHOST-1: " + "0" * 64),
                                encoding="utf-8")
            r = _run(tmp)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("无法核", r.stdout)
            r2 = _run(tmp, "--apply", "--decision", "DEC-TEST-1")
            self.assertNotEqual(r2.returncode, 0)
            self.assertIn("先清理台账", r2.stdout + r2.stderr)
            self.assertIn("GHOST-1", manifest.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
