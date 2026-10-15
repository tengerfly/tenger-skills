"""Agent engine adapters for the behaviour layer.

An engine is a plug, not an identity: cases stay portable and only `engine:` changes when
the host does. Codex is wired first because it runs non-interactively against the user's
existing provider and, unlike the editor host, reports token usage — so behaviour runs
carry a real cost measurement instead of a byte proxy.
"""
from __future__ import annotations
import os, re, shutil, subprocess, sys
from pathlib import Path

TIMEOUT_DEFAULT = 240
TOKEN_RE = re.compile(r"tokens used\s*\n?\s*([0123456789,]+)", re.I)


def available() -> list:
    return [name for name in ("codex", "claude") if shutil.which(name) or shutil.which(f"{name}.cmd")]


def _executable(name: str) -> str:
    return shutil.which(name) or shutil.which(f"{name}.cmd") or name


def run(engine: str, workspace: Path, prompt: str, timeout: int = TIMEOUT_DEFAULT,
        model: str | None = None) -> dict:
    if os.environ.get("TSR_ALLOW_ENGINE") != "1":
        # 真跑引擎 = 花钱 + 分钟级 + 不确定；单测与常规回归里必须默认禁止
        return {"ok": False, "blocked": True, "tokens": None, "output": "",
                "reason": "引擎未授权（需 TSR_ALLOW_ENGINE=1 显式开启，防止跑测试就在烧钱）"}
    if engine == "codex":
        # 0.162 的 exec 没有 --ask-for-approval 长选项，且 prompt 必须走位置参数（放在 -- 后会被当子命令）
        arguments = [_executable("codex"), "exec", "--skip-git-repo-check", "--cd", str(workspace),
                     "--sandbox", "workspace-write"]
        if model:
            arguments += ["--model", model]
        arguments += [prompt]
    elif engine == "claude":
        arguments = [_executable("claude"), "-p", prompt, "--output-format", "json"]
    else:
        return {"ok": False, "reason": f"未接入的引擎: {engine}（可用: {available()}）"}
    try:
        proc = subprocess.run(arguments, cwd=str(workspace), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return {"ok": False, "reason": f"引擎超时 {timeout}s，已终止（不重试，避免重复计费）", "tokens": None}
    except OSError as exc:
        return {"ok": False, "reason": f"引擎不可执行: {exc}", "tokens": None}
    text = (proc.stdout or "") + (proc.stderr or "")
    match = TOKEN_RE.search(text)
    tokens = int(match.group(1).replace(",", "")) if match else None
    if proc.returncode != 0:
        tail = " ".join((proc.stderr or proc.stdout or "").split())[-260:]
        return {"ok": False, "tokens": tokens, "output": text,
                "reason": f"引擎退出码 {proc.returncode}；stderr 尾部：{tail or '(空)'}"}
    if engine == "claude":
        import json
        start = text.find("{")
        if start >= 0:
            try:
                data = json.loads(text[start:])
                tokens = (data.get("usage") or {}).get("input_tokens", 0) + (data.get("usage") or {}).get("output_tokens", 0) or None
                text = str(data.get("result") or text)
            except ValueError:
                pass
    return {"ok": proc.returncode == 0, "exit": proc.returncode, "tokens": tokens,
            "output": text, "reason": "" if proc.returncode == 0 else f"引擎退出码 {proc.returncode}"}


def materialise(fixture: Path, workspace: Path, skill_files: list, repo_root: Path) -> None:
    """Copy a fixture project in, then drop the skill under test in as AGENTS.md context."""
    shutil.copytree(fixture, workspace)
    parts = []
    for relative in skill_files:
        source = (repo_root / relative).resolve()
        if not source.is_relative_to(repo_root.resolve()):
            raise ValueError(f"skill context escapes repo: {relative}")
        if source.is_file():
            parts.append(f"<!-- {relative} -->\n{source.read_text(encoding='utf-8', errors='replace')}")
        else:
            raise ValueError(f"skill context missing: {relative}")
    (workspace / "AGENTS.md").write_text("\n\n---\n\n".join(parts), encoding="utf-8")
