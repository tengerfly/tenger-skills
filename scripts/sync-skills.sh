#!/usr/bin/env bash
# sync-skills.sh —— 把本仓 skill 源同步到各宿主的个人 skills 目录（安装副本）
#
# 背景：宿主只读个人目录下的已安装副本，本仓改动不会自动生效。历史上靠手工 cp，
# 结果出现「仓库已修、生效副本还是旧版」的漂移（见 issue/WorkFlow/2026-09-23 系列，
# 以及 .spec/auto-test/报告/run-2026-09-23-workflow-p0-trial.md 记载的同步约定）。
#
# 同步内容（按 git 追踪文件导出，不带 node_modules / __pycache__ / .venv）：
#   1) 每个 skill 目录 → <目标>/<skill-name>/
#      源仓目录名已统一到 registry id（小写 kebab，见 shared/skill-contract.md §1.4）；
#      下面的 basename|tr 只是防御历史混合大小写写法，正常情况下不再改变目录名。
#   2) 仓库 shared/ 分发到三个层级，覆盖 skill 内出现的各种相对引用深度（已实测四端全解析）：
#        <容器>/shared、<目标>/shared、<目标>/<skill>/shared
#      这些是资源目录（无 SKILL.md），不会被宿主当成 skill 加载。
#
# 不做的事：不删除目标里的额外 skill、不用镜像删除覆盖安装目录（沿用使用手册口径）。
# 目标里存在而源里没有的**文件**只报告为 stale，交人工判断，脚本不自动删；
# 只有「源已移除的空目录」会被清理（空目录不承载内容，留着会让同步失去幂等性）。
#
# 用法：
#   bash scripts/sync-skills.sh                  # 同步到全部默认宿主
#   bash scripts/sync-skills.sh --dry-run        # 只报告差异，不写入
#   bash scripts/sync-skills.sh --target <目录>   # 自定义目标（可重复）
#   bash scripts/sync-skills.sh --ref <git-ref>  # 指定源版本，默认 HEAD
#   bash scripts/sync-skills.sh --list-targets   # 只打印默认目标
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REF="HEAD"
DRY_RUN=0
LIST_ONLY=0
TARGETS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --list-targets) LIST_ONLY=1; shift ;;
    --ref) REF="${2:-}"; shift 2 ;;
    --target) TARGETS+=("${2:-}"); shift 2 ;;
    -h|--help) sed -n '2,22p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "未知参数：$1" >&2; exit 1 ;;
  esac
done

if [ "${#TARGETS[@]}" -eq 0 ]; then
  TARGETS=(
    "$HOME/.zcode/skills"
    "$HOME/.codebuddy/skills"
    "$HOME/.qoder-cn/skills"
    "$HOME/.codex/skills"
  )
fi

if [ "$LIST_ONLY" -eq 1 ]; then
  for t in "${TARGETS[@]}"; do echo "$t"; done
  exit 0
fi

# ---- 1) 一次性导出源（staging）：skill 目录 + shared/ ----
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

# 以 git 追踪路径为准（注意：索引里编排器目录是 workflow/，磁盘上显示 WorkFlow/）；
# skill 目录既可能位于分类目录下（PRD/idea-intake），也可能是根级单目录（Workflow）。
skill_rels=()
while IFS= read -r p; do
  d="${p%/SKILL.md}"
  case "$d" in
    */*/*) continue ;;           # 排除 skill 内部嵌套的 SKILL.md（如 assets 里的模板）
  esac
  skill_rels+=("$d")
done < <(git -C "$ROOT" ls-files -- '*/SKILL.md' | sort)

if [ "${#skill_rels[@]}" -eq 0 ]; then
  echo "未在仓库中找到任何 skill 源目录" >&2
  exit 1
fi

git -C "$ROOT" archive "$REF" -- "${skill_rels[@]}" shared | tar -x -C "$STAGE"

echo "源仓库：$ROOT  (ref=$REF)"
echo "skill 数：${#skill_rels[@]}"
echo "目标："
for t in "${TARGETS[@]}"; do echo "  - $t"; done
[ "$DRY_RUN" -eq 1 ] && echo "模式：dry-run（不写入）"
echo

# ---- 2) 逐目标分发 ----
total_new=0; total_upd=0; total_same=0; total_stale=0

# 把 staging 里的 shared 刷到指定位置；$1=目标路径 $2=缺失时是否创建
sync_shared_to() {
  local dest="$1" create_if_missing="${2:-0}"
  if [ ! -d "$dest" ]; then
    [ "$create_if_missing" -eq 0 ] && return 0
    if [ "$DRY_RUN" -eq 1 ]; then echo "   [new]    shared → $dest"; return 0; fi
    mkdir -p "$dest"; cp -r "$STAGE/shared/." "$dest/"
    echo "   [new]    shared → $dest"; return 0
  fi
  if diff -rq "$STAGE/shared" "$dest" >/dev/null 2>&1; then return 0; fi
  if [ "$DRY_RUN" -eq 1 ]; then echo "   [update] shared → $dest"; return 0; fi
  cp -r "$STAGE/shared/." "$dest/"
  echo "   [update] shared → $dest"
}

for target in "${TARGETS[@]}"; do
  echo "== $target"
  if [ ! -d "$target" ]; then
    if [ "$DRY_RUN" -eq 1 ]; then
      echo "   [skip] 目录不存在（dry-run 不创建）"; echo; continue
    fi
    mkdir -p "$target"
  fi

  new_n=0; upd_n=0; same_n=0; stale_n=0; add_n=0
  stale_report=""
  add_report=""

  for rel in "${skill_rels[@]}"; do
    name="$(basename "$rel" | tr 'A-Z' 'a-z')"
    dest="$target/$name"
    src="$STAGE/$rel"

    if [ ! -d "$dest" ]; then
      if [ "$DRY_RUN" -eq 0 ]; then
        mkdir -p "$dest"
        cp -r "$src/." "$dest/"
        cp -r "$STAGE/shared" "$dest/shared"
      fi
      echo "   [new]    $name"
      new_n=$((new_n + 1))
      continue
    fi

    # 先把本 skill 需要的内容拼成一个期望态（skill 自身 + shared），再与现状比较
    expect="$(mktemp -d)"
    cp -r "$src/." "$expect/"
    cp -r "$STAGE/shared" "$expect/shared"

    diffout="$(diff -rq "$expect" "$dest" 2>/dev/null || true)"
    if [ -z "$diffout" ]; then
      same_n=$((same_n + 1))
    else
      if [ "$DRY_RUN" -eq 0 ]; then
        cp -r "$expect/." "$dest/"
      fi
      upd_lines=$(printf '%s\n' "$diffout" | grep -c . || true)
      echo "   [update] $name  ($upd_lines 处文件差异)"
      upd_n=$((upd_n + 1))
    fi

    # 区分单向差异：只有源有 = 目标缺失（已由上面的 cp 补齐）；只有目标有 = 源已移除。
    # 注意 diff 报的是「条目所在目录」，可能是目标目录本身，也可能是其子目录。
    only_src="$(printf '%s\n' "$diffout" | sed -n "s|^Only in \($expect[^:]*\): \(.*\)\$|\1/\2|p" | sed "s|^$expect/||" || true)"
    only_dst="$(printf '%s\n' "$diffout" | sed -n "s|^Only in \($dest[^:]*\): \(.*\)\$|\1/\2|p" | sed "s|^$dest/||" || true)"
    if [ -n "$only_src" ]; then
      add_n=$((add_n + 1))
      add_report="$add_report
     - $name: $(printf '%s\n' "$only_src" | head -3 | tr '\n' ' ')"
    fi
    if [ -n "$only_dst" ]; then
      remaining=""
      while IFS= read -r item; do
        [ -z "$item" ] && continue
        if [ -d "$dest/$item" ] && [ -z "$(ls -A "$dest/$item" 2>/dev/null)" ]; then
          # 空目录不承载任何内容，源里已无则直接清掉，保证同步幂等
          if [ "$DRY_RUN" -eq 0 ]; then
            rmdir "$dest/$item" 2>/dev/null && echo "   [prune-empty] $name: $item"
          else
            echo "   [prune-empty] $name: $item (dry-run)"
          fi
        else
          remaining="$remaining$item "
        fi
      done <<< "$only_dst"
      if [ -n "$remaining" ]; then
        stale_n=$((stale_n + 1))
        stale_report="$stale_report
     - $name: $remaining"
      fi
    fi
    rm -rf "$expect"
  done

  echo "   小结：new=$new_n update=$upd_n unchanged=$same_n 待补齐=$add_n stale=$stale_n"
  if [ -n "$add_report" ]; then
    echo "   目标缺失、本次$([ "$DRY_RUN" -eq 1 ] && echo 将补齐 || echo 已补齐):$add_report"
  fi
  if [ -n "$stale_report" ]; then
    echo "   stale（源里没有、目标仍保留，请人工确认）:$stale_report"
  fi

  # shared 的三个落点（已实测：四端 298 处相对引用据此全部可解析）
  #   <container>/shared      ← 技能根 `../../shared/` 与嵌套 `../../../shared/`：
  #                             宿主比源仓多一层 skills/，所有 ../.. 形式都上溯到这里
  #   <目标>/shared            ← 裸 `shared/xxx`（从 skills 根起算）
  #   <目标>/<skill>/shared    ← 已在上面的循环里逐技能写入
  sync_shared_to "$(dirname "$target")/shared" 1 || true
  sync_shared_to "$target/shared" 1 || true
  echo
  total_new=$((total_new + new_n)); total_upd=$((total_upd + upd_n))
  total_same=$((total_same + same_n)); total_stale=$((total_stale + stale_n))
done

echo "合计：new=$total_new update=$total_upd unchanged=$total_same stale=$total_stale"
echo "完成。若刚同步的是当前宿主，skill 列表刷新后生效。"
