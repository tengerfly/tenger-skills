"""Read-only portable Skill checks; Python 3.10+, standard library only.

Checks basic entry metadata, common inline Markdown file links and Python syntax.
Does not execute Skills, fully parse YAML/Markdown, or audit privacy/runtime dependencies.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from pathlib import Path, PureWindowsPath
from urllib.parse import unquote, urlsplit


NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
LINK = re.compile(r"\[[^\]\n]*\]\(([^)\n]+)\)")


def redirected(p: Path) -> bool:
    return p.is_symlink() or bool(
        getattr(p.lstat(), "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def check(root: Path) -> dict:
    requested = root.absolute()
    errors: list[str] = []
    result = {"root": str(requested), "ok": False, "files": 0, "errors": errors,
              "notice": "Static structure only; not behavioral, privacy or installation acceptance."}
    if not requested.is_dir():
        errors.append("Bundle directory does not exist")
        return result
    if redirected(requested):
        errors.append("Bundle root must not be a symlink or reparse point")
        return result
    root = requested.resolve()
    files: list[Path] = []

    def walk_error(exc):
        errors.append(f"Cannot inventory bundle: {exc}")

    for current, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
        for name in list(dirs):
            p = Path(current) / name
            if redirected(p) or not p.resolve().is_relative_to(root):
                errors.append(f"Redirected directory is not portable: {p.relative_to(root)}")
                dirs.remove(name)
            elif name in {".git", "__pycache__"}:
                dirs.remove(name)
        for name in names:
            p = Path(current) / name
            if redirected(p) or not p.resolve().is_relative_to(root):
                errors.append(f"Redirected file is not portable: {p.relative_to(root)}")
            else:
                files.append(p)
    result["files"] = len(files)
    texts = {}
    for p in files:
        if p.suffix not in {".md", ".py"}:
            continue
        try:
            texts[p] = p.read_text(encoding="utf-8")
        except (UnicodeError, OSError) as exc:
            errors.append(f"Cannot read UTF-8 file {p.relative_to(root)}: {exc}")

    entry = root / "SKILL.md"
    text = texts.get(entry)
    if text is None:
        errors.append("Readable SKILL.md is required")
    else:
        header = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
        if not header:
            errors.append("SKILL.md needs UTF-8 YAML frontmatter without BOM")
        else:
            # Deliberately limited to single-line name/description used by this package.
            for key in ("name", "description"):
                values = re.findall(rf"(?m)^{key}:[ \t]*([^\n]*)$", header.group(1))
                if len(values) != 1 or not values[0].strip():
                    errors.append(f"Exactly one nonempty single-line {key} is required")
                    continue
                value = values[0].strip().strip("\"'")
                if key == "name" and (not NAME.fullmatch(value) or len(value) > 64 or value != root.name):
                    errors.append("Skill name must be kebab-case, <=64 characters, and match folder name")
                if key == "description" and (value in {"|", ">"} or not value):
                    errors.append("Use a nonempty single-line description for this basic checker")
        if re.search(r"\{\{[^\n]*?\}\}|(?m:^\s*\[TODO:)", text):
            errors.append("SKILL.md contains unfilled template markers")

    for p, text in texts.items():
        rel = p.relative_to(root)
        if p.suffix == ".py":
            try:
                compile(text, str(rel), "exec")
            except (SyntaxError, ValueError) as exc:
                errors.append(f"Python syntax error in {rel}: {exc}")
            continue
        # Common inline links only, not reference-style links or dynamic runtime paths.
        for match in LINK.finditer(text):
            raw = match.group(1).strip()
            if raw.startswith("<") and raw.endswith(">"):
                raw = raw[1:-1]
            else:
                raw = re.sub(r'\s+"[^"\n]*"$', "", raw)
            if raw.startswith("#"):
                continue
            windows = PureWindowsPath(raw)
            parsed = urlsplit(raw)
            if not windows.drive and parsed.scheme in {"http", "https", "mailto"}:
                continue
            if windows.drive or parsed.scheme or raw.startswith(("/", "\\")):
                errors.append(f"Absolute/external file link in {rel}: {raw}")
                continue
            local = unquote(parsed.path).replace("\\", "/")
            target = (p.parent / local).resolve()
            if not target.is_relative_to(root):
                errors.append(f"Link escapes bundle in {rel}: {raw}")
            elif not target.exists():
                errors.append(f"Missing linked resource in {rel}: {raw}")
    result["ok"] = not errors
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Skill directory containing SKILL.md")
    args = parser.parse_args(argv)
    try:
        result = check(args.root)
    except (OSError, ValueError) as exc:
        result = {"ok": False, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
