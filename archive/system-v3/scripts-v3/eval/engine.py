"""Agent engine adapters for the behaviour layer.

An engine is a plug, not an identity: cases stay portable and only `engine:` changes when
the host does. Codex is wired first because it runs non-interactively against the user's
existing provider and, unlike the editor host, reports token usage — so behaviour runs
carry a real cost measurement instead of a byte proxy.
"""
from __future__ import annotations
import json, os, re, shutil, signal, subprocess, sys
from pathlib import Path

TIMEOUT_DEFAULT = 240
TOKEN_RE = re.compile(r"tokens used\s*\n?\s*([0123456789,]+)", re.I)


def available() -> list:
    return [name for name in ("codex", "claude") if shutil.which(name) or shutil.which(f"{name}.cmd")]


def _executable(name: str) -> str:
    return shutil.which(name) or shutil.which(f"{name}.cmd") or name


def _kill_tree(proc) -> None:
    """Kill the engine *and everything under it*.

    Windows 上引擎是一条 cmd 包装层 → node → codex.exe 的链；只 kill 直接子进程时，孙进程
    仍持有 stdout/stderr 句柄，communicate() 等 EOF 就永远不返回 —— 420s 超时会被拖成无限等。
    2026-10-18 首次真跑 EV-FE-103 就是这样多卡了 4.5 分钟，靠外部 taskkill 才解开。
    """
    if os.name == "nt":
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                           capture_output=True, timeout=30)
            return
        except (OSError, subprocess.TimeoutExpired):
            pass
    elif hasattr(os, "killpg"):
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            return
        except (OSError, ProcessLookupError):
            pass
    proc.kill()


def _capture(arguments: list, workspace, timeout: int) -> tuple:
    """Run an engine command; on timeout kill the whole tree, then still return the残流.

    返回值 (returncode, stdout, stderr, timedOut)。超时不等于没有产出：已流出的字节必须留下，
    判据是否误杀才可回查；但收集残流绝不能把评测挂死，所以收集本身也带兜底超时。
    """
    popen_args = {"cwd": str(workspace), "stdout": subprocess.PIPE, "stderr": subprocess.PIPE,
                  "text": True, "encoding": "utf-8", "errors": "replace", "stdin": subprocess.DEVNULL}
    if os.name != "nt":
        popen_args["start_new_session"] = True
    proc = subprocess.Popen(arguments, **popen_args)
    try:
        out, err = proc.communicate(timeout=timeout)
        return proc.returncode, out or "", err or "", False
    except subprocess.TimeoutExpired:
        _kill_tree(proc)
        try:
            out, err = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            # 管道仍被异常孙进程占着：宁可交出空残流，也不能为收集残流把评测挂死
            proc.kill()
            out, err = "", ""
        return proc.returncode, out or "", err or "", True


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
        returncode, out, err, timed_out = _capture(arguments, workspace, timeout)
    except OSError as exc:
        return {"ok": False, "reason": f"引擎不可执行: {exc}", "tokens": None, "output": "", "transcript": ""}
    text = out + err
    if timed_out:
        # 超时也照常计量：没有计量的成本会被读成「没花钱」，而超时恰恰是烧了钱没拿到结论。
        tokens, cached = None, None
        if engine == "codex":
            tokens, cached = usage_tokens(text)
        if tokens is None:
            match = TOKEN_RE.search(text)
            tokens = int(match.group(1).replace(",", "")) if match else None
        answers = _agent_messages(text)
        return {"ok": False, "timedOut": True, "tokens": tokens, "cachedTokens": cached,
                "output": "\n\n".join(answers) if answers else text, "transcript": text,
                "reason": f"引擎超时 {timeout}s，已终止进程树（不重试，避免重复计费）；残流 {len(text)} 字"}
    match = TOKEN_RE.search(text)
    tokens = int(match.group(1).replace(",", "")) if match else None
    cached = None
    if engine == "codex":
        measured, cached = usage_tokens(text)
        if measured:
            tokens = measured
    final = text
    if returncode != 0:
        tail = " ".join((err or out or "").split())[-260:]
        return {"ok": False, "tokens": tokens, "output": final, "transcript": text,
                "reason": f"引擎退出码 {returncode}；stderr 尾部：{tail or '(空)'}"}
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
    return {"ok": True, "exit": returncode, "tokens": tokens, "cachedTokens": cached,
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
