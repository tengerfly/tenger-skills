#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-installed-refs.py —— 跨 skill / shared 引用的两视图可达性门禁

判据来自仓库根 `shared/skill-contract.md` §1.4。源仓是「<分类>/<skill-id>/」两层，
安装副本是「<skills 根>/<skill-id>/」一层，所以一条 `../` 路径要在两边都成立才算正确。

检查三件事：
  1) 禁用写法：带分类层的跨 skill 相对路径（副本扁平布局下必断）；
  2) 源仓视图：解析后目标文件必须存在；
  3) 副本视图：站在宿主容器（skills 的父目录）视角解析同一条引用，落点必须是
     已知 skill id、shared 三落点之一，且对应资产在源仓里真实存在（分发即随之可达）。

历史池（issue/ bug-patterns/ evolution/ chats/）、测试夹具目录（*/tests/）与占位路径
（含 < > 或 xxx/X）不检查：前者是当时事实，后者不是真引用。
exit code：0=通过，1=有违规。
"""
import argparse
import os
import posixpath
import re
import sys

import yaml

EXCL = ('.git', '.spec', '.codebuddy', '.zcode', '.codex', '.messages', 'node_modules', '.venv',
        'dist', 'coverage', '__pycache__', '.qoder-cn', 'qoder-knowledge',
        'issue', 'chats', 'evolution', 'bug-patterns',
        # 评测夹具与用例正文是被测数据，不是宿主会加载的 skill 正文：
        # 红用例必须故意写坏路径（例如指一个不存在的规范文件），把它们当真引用扫就等于自己抓自己。
        # 与既有豁免 `*/tests/`、`scripts/tests/` 同一类；代价是 evals/ 里的真断链不会被这面量具抓到。
        'evals',
        # .tmp-eval/ 是 .gitignore 里的临时探针区（一次会话的脚手架脚本），不是会被宿主加载的 skill 正文；
        # 探针常故意用两级回退去指不存在的文件（探测解析行为），把它们当真引用扫会让整条 system 门禁红在垃圾上。
        # 真要藏一个真 skill 到这里，registry 侧「path is not a Skill directory」仍会兜（与 fixtures 同一类风险）。
        '.tmp-eval')
TEXT_EXT = ('.md', '.markdown', '.py', '.ps1', '.sh', '.yaml', '.yml', '.txt')
REF = re.compile(r'(?<![\w./-])((?:\.\./)+(?:[A-Za-z0-9_.-]+/)*?[A-Za-z0-9_.-]+\.'
                 r'(?:md|markdown|py|mjs|cjs|js|ts|json|ya?ml|ps1|sh|html|txt))')
LAYER = re.compile(r'(?:\.\./)+(?:DEV|UI|PRD|Other|Test|Skill)/[A-Za-z0-9_.-]+/')
PLACEHOLDER_SEGS = {'xxx', 'X', 'x', 'YYYY', 'Skill-Name', 'private'}
# 仓根工作区池：只在源仓存在，不随 skill 分发。源仓视图仍检查可达性，副本视图豁免（见 §1.4 边界）
POOLS = ('issue', 'chats', 'evolution', 'bug-patterns', 'docs', 'governance', 'scripts',
         'skill-knowledge', 'templates')


def load_entries(root):
    with open(os.path.join(root, 'governance', 'skill-registry.yaml'), encoding='utf-8') as handle:
        reg = yaml.safe_load(handle)
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


def exists(root, rel):
    return bool(rel) and os.path.exists(os.path.join(root, rel.replace('/', os.sep)))


def is_placeholder(ref):
    if '<' in ref or '>' in ref or '{' in ref or '$' in ref:
        return True
    return any(seg in PLACEHOLDER_SEGS for seg in ref.split('/')[:-1] + [ref.split('/')[-1].split('.')[0]])


def audit(root: str) -> dict:
    """跑 §1.4 的三件事，只返回结构化结果：不打印、不退出。

    ps1 门禁、`validate_core` 校验器与评测层都消费这一份，判据不另写第二套。
    """
    entries = load_entries(root)
    by_path = {p: i for i, p in entries}
    id2path = {i: p for i, p in entries}
    ids = set(id2path)

    def locate(rel):
        parts = rel.split('/')
        for depth in range(len(parts) - 1, 0, -1):
            cand = '/'.join(parts[:depth])
            if cand in by_path:
                return cand, '/'.join(parts[depth:-1])
        return None, None

    def copy_base(rel):
        """当前文件在安装副本里的位置（相对宿主容器：skills 的父目录）"""
        spath, inner = locate(rel)
        if spath:
            return posixpath.normpath(posixpath.join('skills', by_path[spath], inner))
        if rel == 'shared' or rel.startswith('shared/'):
            return posixpath.normpath(posixpath.join('skills', posixpath.dirname(rel)))
        return None

    def copy_check(base, ref):
        target = posixpath.normpath(posixpath.join(base, ref))
        segs = [s for s in target.split('/') if s]
        if segs and segs[0] == '..':
            return False, target, '跳出宿主容器'
        if segs[0] == 'shared':
            return exists(root, target), target, '容器级 shared 落点'
        if segs[0] == 'skills' and len(segs) >= 2:
            second, tail = segs[1], '/'.join(segs[2:])
            if second == 'shared':
                return exists(root, posixpath.join('shared', tail)), target, 'skills 根 shared 落点'
            if second in ids:
                return exists(root, posixpath.join(id2path[second], tail)), target, 'skill %s' % second
            return False, target, '二级目录 %s 不是 skill id（分类层残留或路径写错）' % second
        return False, target, '落点 %s 不在 skills/shared 体系内' % target

    bad_layer, bad_repo, bad_copy, checked, pool_refs = [], [], [], 0, 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCL]
        for fn in filenames:
            if not fn.lower().endswith(TEXT_EXT):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, '/')
            if '/tests/' in '/%s/' % rel or rel.startswith('scripts/tests/'):
                continue
            with open(full, encoding='utf-8', errors='ignore') as handle:
                text = handle.read()
            for m in LAYER.findall(text):
                bad_layer.append((rel, m))
            base = copy_base(rel)
            for ref in REF.findall(text):
                if is_placeholder(ref):
                    continue
                checked += 1
                repo_target = posixpath.normpath(posixpath.join(posixpath.dirname(rel), ref))
                if not exists(root, repo_target):
                    bad_repo.append((rel, ref, repo_target))
                    continue
                if not base:
                    continue
                if repo_target.split('/')[0] in POOLS:
                    pool_refs += 1
                    continue
                ok, tgt, why = copy_check(base, ref)
                if not ok:
                    bad_copy.append((rel, ref, '%s  [%s]' % (tgt, why)))

    return {"root": root, "layer": bad_layer, "repo": bad_repo, "copy": bad_copy,
            "counts": {"checked": checked, "layer": len(bad_layer), "repo": len(bad_repo),
                       "copy": len(bad_copy), "pool": pool_refs, "skills": len(entries)}}


def findings(result: dict, limit: int = 0) -> list:
    """把三视口的违规点成一句句可断言的判据文本；limit=0＝全量（校验器不许截断藏红点）。"""
    def take(rows):
        return rows if not limit else rows[:limit]
    out = ["禁用写法（带分类层的跨 skill 相对路径）: %s -> %s" % (rel, ref)
           for rel, ref in take(result["layer"])]
    out += ["源仓不可达: %s -> %s   -> %s" % (rel, ref, target)
            for rel, ref, target in take(result["repo"])]
    out += ["副本不可达: %s -> %s   [%s]" % (rel, ref, why)
            for rel, ref, why in take(result["copy"])]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project-root', default=os.getcwd())
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()
    result = audit(os.path.abspath(args.project_root))
    counts = result["counts"]
    print('checked=%d  分类层写法=%d  源仓不可达=%d  副本不可达=%d'
          % (counts["checked"], counts["layer"], counts["repo"], counts["copy"]))
    if not args.quiet:
        for title, lst in (('分类层', result["layer"]), ('源仓', result["repo"]), ('副本', result["copy"])):
            for row in lst[:20]:
                print('  [%s] %s\n        %s%s' % (title, row[0], row[1], ('   -> ' + row[2]) if len(row) > 2 else ''))
    bad = counts["layer"] + counts["repo"] + counts["copy"]
    print('RESULT: %s' % ('PASS' if bad == 0 else 'FAIL(%d)' % bad))
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
