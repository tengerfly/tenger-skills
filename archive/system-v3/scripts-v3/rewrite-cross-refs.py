#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rewrite-cross-refs.py —— 按 registry 权威修复源仓视图的跨 skill 引用

用途：跨 skill 引用常见的三种写错——回退层数不对、分类层写错、tail 漏了 `references/` 段。
本脚本以 `governance/skill-registry.yaml` 为唯一权威：解析每条 `../` 引用真正指向的 skill，
校验目标文件在源仓是否真实存在（不存在则按唯一文件名修正 tail），再按当前文件位置重算相对路径。

只修**源仓布局**（`<分类>/<skill-id>/`）。安装副本视图（扁平 `<skills 根>/<skill-id>/`）的正确性
由 `scripts/check-installed-refs.py` 门禁把关，规则见 `shared/skill-contract.md` §1.4：
跨 skill 引用不允许写带分类层的相对路径，也不靠分发时改写。

先不带 --apply 看报告，确认后 --apply。
"""
import argparse
import os
import posixpath
import re
import sys

import yaml

REF = re.compile(r'(?<![\w./-])((?:\.\./)+(?:[A-Za-z0-9_.+-]+/)*?[A-Za-z0-9_.+-]+\.'
                 r'(?:md|markdown|py|mjs|cjs|js|ts|json|ya?ml|ps1|sh|html|txt))')
TEXT_EXT = ('.md', '.markdown', '.py', '.mjs', '.cjs', '.js', '.ts', '.json',
            '.yaml', '.yml', '.ps1', '.sh', '.html', '.txt')
EXCL = ('.git', 'node_modules', '.qoder-cn', '.spec', 'dist', 'coverage', '__pycache__',
        '.venv', 'issue', 'chats', 'evolution', 'bug-patterns', '.codebuddy', '.messages',
        '.zcode', '.codex')


def load_entries(root):
    reg = yaml.safe_load(open(os.path.join(root, 'governance', 'skill-registry.yaml'), encoding='utf-8'))
    out = []

    def walk(o):
        if isinstance(o, dict):
            i, p = o.get('id'), o.get('path')
            if isinstance(i, str) and isinstance(p, str) and p.strip():
                p = p.strip().rstrip('/')
                if '${' not in p and not p.startswith('$'):
                    out.append((i, p))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(reg)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=os.getcwd())
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--limit', type=int, default=30)
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    entries = load_entries(root)
    by_path = {p: i for i, p in entries}
    index = {}
    cats = set()
    for i, p in entries:
        segs = p.split('/')
        index.setdefault(segs[-1], (i, p))
        index.setdefault(i, (i, p))
        if len(segs) > 1:
            cats.add(segs[0])

    def skill_of(rel):
        parts = rel.split('/')
        for depth in range(len(parts) - 1, 0, -1):
            cand = '/'.join(parts[:depth])
            if cand in by_path:
                return cand, '/'.join(parts[depth:-1])
        return None, None

    def fix_tail(target_path, tail, rel, raw, log):
        cand = posixpath.normpath(f'{target_path}/{tail}')
        if os.path.isfile(os.path.join(root, cand.replace('/', os.sep))):
            return cand, False
        base = os.path.basename(tail)
        hits = []
        walk_root = os.path.join(root, target_path.replace('/', os.sep))
        if os.path.isdir(walk_root):
            for dirpath, dirnames, filenames in os.walk(walk_root):
                dirnames[:] = [d for d in dirnames if d not in ('node_modules', '.git', 'dist',
                                                               'coverage', '__pycache__')]
                if base in filenames:
                    r = os.path.relpath(os.path.join(dirpath, base), walk_root).replace(os.sep, '/')
                    hits.append(f'{target_path}/{r}')
        if len(hits) == 1:
            log['tail_fixed'].append((rel, raw, hits[0]))
            return hits[0], True
        log['unresolved'].append((rel, raw, f'target={target_path} tail={tail} hits={len(hits)}'))
        return None, False

    log = {'rewritten': [], 'tail_fixed': [], 'unresolved': [], 'unchanged': 0, 'skipped': 0, 'files': 0}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCL]
        for fn in filenames:
            if not fn.lower().endswith(TEXT_EXT):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, '/')
            skill_path, inner_dir = skill_of(rel)
            if not skill_path:
                continue
            log['files'] += 1
            cur_dir = posixpath.join(skill_path, inner_dir) if inner_dir else skill_path
            text = open(full, encoding='utf-8', errors='ignore').read()

            def repl(m):
                raw = m.group(1)
                parts = raw.split('/')
                k = 0
                while parts[k] == '..':
                    k += 1
                segs = parts[k:]
                if not segs:
                    return raw
                if segs[0] in cats and len(segs) >= 2:
                    tgt = index.get(segs[1])
                    tail = '/'.join(segs[2:])
                else:
                    tgt = index.get(segs[0])
                    tail = '/'.join(segs[1:])
                if tgt is None or not tail:
                    log['skipped'] += 1
                    return raw
                target_path, fixed = fix_tail(tgt[1], tail, rel, raw, log)
                if target_path is None:
                    return raw
                new = posixpath.relpath(target_path, cur_dir)
                if new == raw:
                    log['unchanged'] += 1
                    return raw
                log['rewritten'].append((rel, raw, new, fixed))
                return new

            new_text = REF.sub(repl, text)
            if new_text != text and args.apply:
                with open(full, 'w', encoding='utf-8', newline='') as f:
                    f.write(new_text)

    print('apply=%s files_scanned=%d rewritten=%d tail_fixed=%d unchanged=%d skipped=%d unresolved=%d'
          % (args.apply, log['files'], len(log['rewritten']), len(log['tail_fixed']),
             log['unchanged'], log['skipped'], len(log['unresolved'])))
    if log['rewritten']:
        print('\n--- 改写 ---')
        for rel, raw, new, fixed in log['rewritten'][:args.limit]:
            print('  %s\n      %s\n   -> %s%s' % (rel, raw, new, '   [tail 已修正]' if fixed else ''))
    if log['unresolved']:
        print('\n--- 未解决（目标文件不存在，需人工定夺）---')
        for rel, raw, why in log['unresolved'][:args.limit]:
            print('  %s\n      %s   (%s)' % (rel, raw, why))
    return 0


if __name__ == '__main__':
    sys.exit(main())
