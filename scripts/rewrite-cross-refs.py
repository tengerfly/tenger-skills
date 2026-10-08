#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rewrite-cross-refs.py —— 跨 skill 引用的布局规范化（单一权威：governance/skill-registry.yaml）

背景：源仓是「<分类>/<Skill-Name>/」两层，安装副本是「<skills 根>/<skill-id>/」一层且目录名小写。
同一条相对路径字符串不可能在两种布局下都精确可达（层数天然差一、大小写不同）。实测 58 处跨
skill 引用中，源仓可达而副本不可达 25 处、两视图都不可达 20 处、仅大小写不符 13 处、两视图
大小写精确可达 0 处。

两种布局共用同一套解析（registry 权威 + 目标文件存在性校验 + tail 唯一名修正）：
  --layout repo        就地修源仓里写错的回退层数与 tail（真 bug，人类可读路径不变形）
  --layout installed   分发时把源仓写法重算成副本布局写法（由 sync-skills.sh 对 staging 调用）

只处理指向「其他 skill 目录」的相对引用（首段命中 registry 的分类名 / Skill-Name / id）。
`shared/`、`issue/`、`chats/`、`bug-patterns/` 等仓库根池引用一律跳过：副本侧由 shared 三落点
冗余承接，池引用本就不该由 skill 目录相对路径解析。
"""
import argparse
import os
import posixpath
import re
import sys

import yaml

REF = re.compile(
    r'(?<![\w./-])((?:\.\./)+(?:[A-Za-z0-9_.+-]+/)*?[A-Za-z0-9_.+-]+\.'
    r'(?:md|markdown|py|mjs|cjs|js|ts|json|ya?ml|ps1|sh|html|txt))'
)
TEXT_EXT = ('.md', '.markdown', '.py', '.mjs', '.cjs', '.js', '.ts', '.json',
            '.yaml', '.yml', '.ps1', '.sh', '.html', '.txt')


def load_entries(root):
    reg = yaml.safe_load(open(os.path.join(root, 'governance', 'skill-registry.yaml'), encoding='utf-8'))
    out = []

    def walk(o):
        if isinstance(o, dict):
            i, p = o.get('id'), o.get('path')
            if isinstance(i, str) and isinstance(p, str) and p.strip():
                p = p.strip().rstrip('/')
                # 外部知识库（registry 里是 ${...} 占位、status: external）不参与仓内路径规范化
                if not ('${' in p or p.startswith('$')):
                    out.append((i.strip(), p))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(reg)
    return out


class Index:
    def __init__(self, entries):
        self.by_path = {p: i for i, p in entries}
        self.by_name = {}
        self.by_id = {}
        self.cats = set()
        for i, p in entries:
            segs = p.split('/')
            self.by_name.setdefault(segs[-1], (i, p))
            self.by_id[i] = (i, p)
            if len(segs) > 1:
                self.cats.add(segs[0])

    def lookup(self, seg):
        if seg in self.by_name:
            return self.by_name[seg]
        if seg in self.by_id:
            return self.by_id[seg]
        return None


def skill_of(rel, index):
    """返回该文件所属 skill 的 (path, 内部相对目录)；不在任何 skill 内返回 None"""
    parts = rel.split('/')
    for depth in range(len(parts) - 1, 0, -1):
        cand = '/'.join(parts[:depth])
        if cand in index.by_path:
            inner = parts[depth:-1]
            return cand, ('/'.join(inner))
    return None


def fix_tail(tree_root, target_path, tail, log, rel_src, raw):
    """目标文件存在性校验；不存在则按文件名在目标 skill 内唯一匹配修正"""
    cand = posixpath.normpath(f'{target_path}/{tail}')
    if os.path.isfile(os.path.join(tree_root, cand.replace('/', os.sep))):
        return cand, False
    base = os.path.basename(tail)
    hits = []
    walk_root = os.path.join(tree_root, target_path.replace('/', os.sep))
    if os.path.isdir(walk_root):
        for dirpath, dirnames, filenames in os.walk(walk_root):
            dirnames[:] = [d for d in dirnames if d not in ('node_modules', '.git', 'dist', 'coverage', '__pycache__')]
            if base in filenames:
                rel = os.path.relpath(os.path.join(dirpath, base), walk_root).replace(os.sep, '/')
                hits.append(f'{target_path}/{rel}')
    if len(hits) == 1:
        log['tail_fixed'].append((rel_src, raw, hits[0]))
        return hits[0], True
    log['unresolved'].append((rel_src, raw, f'target={target_path} tail={tail} hits={len(hits)}'))
    return None, False


def run(args):
    index = Index(load_entries(args.repo_root))
    log = {'rewritten': [], 'tail_fixed': [], 'unchanged': 0,
           'skipped_pool': 0, 'skipped_inner': 0, 'unresolved': [], 'files': 0}
    apply = args.apply

    for dirpath, dirnames, filenames in os.walk(args.repo_root):
        dirnames[:] = [d for d in dirnames
                       if d not in ('.git', 'node_modules', '.qoder-cn', '.spec', 'dist', 'coverage',
                                    '__pycache__', '.venv', 'issue', 'chats', 'evolution',
                                    'bug-patterns', '.codebuddy', '.messages', '.zcode', '.codex')]
        for fn in filenames:
            if not fn.lower().endswith(TEXT_EXT):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, args.repo_root).replace(os.sep, '/')
            own = skill_of(rel, index)
            if not own:
                continue
            log['files'] += 1
            skill_path, inner_dir = own
            text = open(full, encoding='utf-8', errors='ignore').read()

            def repl(m):
                raw = m.group(1)
                parts = raw.split('/')
                ups = 0
                k = 0
                while parts[k] == '..':
                    ups += 1
                    k += 1
                segs = parts[k:]
                if not segs:
                    return raw
                if segs[0] in index.cats and len(segs) >= 2:
                    tgt = index.lookup(segs[1])
                    tail = '/'.join(segs[2:])
                else:
                    tgt = index.lookup(segs[0])
                    tail = '/'.join(segs[1:])
                if tgt is None:
                    if segs[0] in ('shared', 'issue', 'chats', 'bug-patterns', 'evolution',
                                  'docs', 'governance', 'templates', 'references', 'assets', 'scripts'):
                        log['skipped_pool'] += 1
                    else:
                        log['skipped_inner'] += 1
                    return raw
                if not tail:
                    log['skipped_inner'] += 1
                    return raw
                target_path, fixed = fix_tail(args.repo_root, tgt[1], tail, log, rel, raw)
                if target_path is None:
                    return raw
                tail_in_target = posixpath.relpath(target_path, tgt[1])
                if args.layout == 'installed':
                    cur_dir = posixpath.join(args.root_label, index.by_path[skill_path], inner_dir) if inner_dir \
                        else posixpath.join(args.root_label, index.by_path[skill_path])
                    tgt_full = posixpath.join(args.root_label, tgt[0], tail_in_target)
                else:
                    cur_dir = posixpath.join(skill_path, inner_dir) if inner_dir else skill_path
                    tgt_full = target_path
                new = posixpath.relpath(tgt_full, cur_dir)
                if new == raw:
                    log['unchanged'] += 1
                    return raw
                log['rewritten'].append((rel, raw, new, fixed))
                return new

            new_text = REF.sub(repl, text)
            if new_text != text and apply:
                with open(full, 'w', encoding='utf-8', newline='') as f:
                    f.write(new_text)

    print('layout=%s apply=%s files_scanned=%d' % (args.layout, apply, log['files']))
    print('rewritten=%d  tail_fixed=%d  unchanged=%d  skipped(池/内部)=%d  unresolved=%d'
          % (len(log['rewritten']), len(log['tail_fixed']), log['unchanged'],
             log['skipped_pool'] + log['skipped_inner'], len(log['unresolved'])))
    print('\n--- 修正了 tail 的（原路径在目标 skill 内不存在，按唯一文件名改写）---')
    for rel, raw, hit in log['tail_fixed'][:args.limit]:
        print('  %s\n      %s  ->  %s' % (rel, raw, hit))
    print('\n--- 改写清单（前 %d 条）---' % args.limit)
    for rel, raw, new, fixed in log['rewritten'][:args.limit]:
        print('  %s\n      %s\n   -> %s%s' % (rel, raw, new, '   [tail 已修正]' if fixed else ''))
    print('\n--- 未解决（需人工定夺）---')
    for rel, raw, why in log['unresolved'][:args.limit]:
        print('  %s\n      %s   (%s)' % (rel, raw, why))
    return 0 if not log['unresolved'] else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default=os.getcwd())
    ap.add_argument('--layout', choices=['repo', 'installed'], required=True)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--root-label', default='skills', help='installed 布局下技能目录的父目录名（虚拟，宿主无关）')
    ap.add_argument('--limit', type=int, default=40)
    args = ap.parse_args()
    if args.repo_root == os.getcwd():
        args.repo_root = os.path.abspath(args.repo_root)
    return run(args)


if __name__ == '__main__':
    sys.exit(main())
