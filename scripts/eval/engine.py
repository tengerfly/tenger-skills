"""Agent engine adapters for the behaviour layer.

An engine is a plug, not an identity: cases stay portable and only `engine:` changes when
the host does. Codex is wired first because it runs non-interactively against the user's
existing provider and, unlike the editor host, reports token usage — so behaviour runs
carry a real cost measurement instead of a byte proxy.
"""
from __future__ import annotations
import json, os, re, shutil, subprocess, sys
from pathlib import Path

TIMEOUT_DEFAULT = 240
TOKEN_RE = re.compile(r"tokens used\s*\n?\s*([0123456789,]+)", re.I)


def available() -> list:
    return [name for name in ("codex", "claude") if shutil.which(name) or shutil.which(f"{name}.cmd")]


def _executable(name: str) -> str:
    return shutil.which(name) or shutil.which(f"{name}.cmd") or name


def _agent_messages(text: str) -> list:
    """Pull the model's own replies out of codex's JSONL event stream.

    Judging the raw transcript is wrong twice over: the injected SKILL.md context and every
    tool echo (Chinese file content arrives GBK-mangled on this host) sit in it, so a ban-word
    scan either hits the skill's own instructions or misses violations hidden in mojibake.
    """
    answers = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        for node in (event, event.get("item"), event.get("message")):
            if not isinstance(node, dict):
                continue
            kind = str(node.get("type") or "")
            role = str(node.get("role") or "")
            if "agent_message" not in kind and not (kind in {"response_output", "message"} and role in {"", "assistant"}):
                continue
            value = node.get("text") or node.get("content") or node.get("message")
            if isinstance(value, str) and value.strip():
                answers.append(value.strip())
    return answers


def usage_tokens(text: str):
    """Sum codex `turn.completed` usage into the billable figure: non-cached input + output.

    Cost must come from the engine, not from our guess: the editor host reports 0 for every
    token field. Cached input is excluded (it is billed at a fraction) but reported alongside,
    so a reader can tell "cheap because cached" from "actually small".
    """
    total = 0
    cached = 0
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{") or "turn.completed" not in line:
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        use = event.get("usage") if isinstance(event.get("usage"), dict) else None
        if not use:
            continue
        total += int(use.get("input_tokens") or 0) + int(use.get("output_tokens") or 0)
        cached += int(use.get("cached_input_tokens") or 0)
    if not total:
        return None, None
    return total - cached, cached


def run(engine: str, workspace: Path, prompt: str, timeout: int = TIMEOUT_DEFAULT,
        model: str | None = None) -> dict:
    if os.environ.get("TSR_ALLOW_ENGINE") != "1":
        # 真跑引擎 = 花钱 + 分钟级 + 不确定；单测与常规回归里必须默认禁止
        return {"ok": False, "blocked": True, "tokens": None, "output": "", "transcript": "",
                "reason": "引擎未授权（需 TSR_ALLOW_ENGINE=1 显式开启，防止跑测试就在烧钱）"}
    if engine == "codex":
        # 0.162 的 exec 没有 --ask-for-approval 长选项，且 prompt 必须走位置参数（放在 -- 后会被当子命令）
        arguments = [_executable("codex"), "exec", "--json", "--skip-git-repo-check", "--cd", str(workspace),
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
    except subprocess.TimeoutExpired as exc:
        # 超时不等于没有产出：capture_output 会把已流的字节挂在异常上。丢掉它就等于
        # 「跑失败了但连原文都没有」，判据是否误杀再也无法回查。
        partial = " ".join(filter(None, [str(exc.stdout or ""), str(exc.stderr or "")]))
        match = TOKEN_RE.search(partial)
        answers = _agent_messages(partial)
        return {"ok": False, "timedOut": True, "tokens": int(match.group(1).replace(",", "")) if match else None,
                "output": "\n\n".join(answers) if answers else partial, "transcript": partial,
                "reason": f"引擎超时 {timeout}s，已终止（不重试，避免重复计费）；残流 {len(partial)} 字"}
    except OSError as exc:
        return {"ok": False, "reason": f"引擎不可执行: {exc}", "tokens": None, "output": "", "transcript": ""}
    text = (proc.stdout or "") + (proc.stderr or "")
    match = TOKEN_RE.search(text)
    tokens = int(match.group(1).replace(",", "")) if match else None
    cached = None
    if engine == "codex":
        measured, cached = usage_tokens(text)
        if measured:
            tokens = measured
    final = text
    if proc.returncode != 0:
        tail = " ".join((proc.stderr or proc.stdout or "").split())[-260:]
        return {"ok": False, "tokens": tokens, "output": final, "transcript": text,
                "reason": f"引擎退出码 {proc.returncode}；stderr 尾部：{tail or '(空)'}"}
    if engine == "codex":
        answers = _agent_messages(text)
        if not answers:
            # 提取不到最终回答就报错，不许退回拿整条 transcript 当判据输入：
            # 那里面含被注入的 SKILL.md 原文，全文匹配必然误杀
            return {"ok": False, "tokens": tokens, "cachedTokens": cached, "output": "", "transcript": text,
                    "reason": "codex --json 流里没取到 agent_message，判据无法成立（不退化为全文匹配）"}
        final = "\n\n".join(answers)
    if engine == "claude":
        start = text.find("{")
        if start >= 0:
            try:
                data = json.loads(text[start:])
                tokens = (data.get("usage") or {}).get("input_tokens", 0) + (data.get("usage") or {}).get("output_tokens", 0) or None
                final = str(data.get("result") or text)
            except ValueError:
                pass
    return {"ok": True, "exit": proc.returncode, "tokens": tokens, "cachedTokens": cached,
            "output": final, "transcript": text, "reason": ""}


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
