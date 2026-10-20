#!/usr/bin/env bash
# link-skills.sh —— 用 Windows junction 把仓内 skill 直接挂进宿主 skills 目录，
# 改完即生效，免掉每轮 sync-skills.sh 的比对与拷贝。
#
# 用法：
#   bash scripts/link-skills.sh --dry-run          # 只报告将做什么
#   bash scripts/link-skills.sh                    # 挂到默认宿主（zcode + qoder-cn）
#   bash scripts/link-skills.sh --target <目录>     # 指定宿主（可重复）
#   bash scripts/link-skills.sh --unlink           # 撤掉 junction（只删链接，不动仓库）
#   bash scripts/link-skills.sh --list-targets
#
# 语义与边界：
#   - 只对「仓内 skill」建链接，宿主里的外来 skill 一律不动；
#   - 已存在的**拷贝目录**会先删再换成链接（删前确认它不是链接，绝不对链接用 rm -rf）；
#   - `shared/` 的两个落点（`<host>/shared`、`<host>/skills/shared`）同样换成链接，
#     这样 `../shared/`、`../../shared/`、`../../../shared/` 三种深度都指向仓库真身；
#   - EXCLUDE 里的 skill 保持拷贝（内含 node_modules，链接会让宿主扫到几千个文件）；
#   - 挂上链接后**不要再对该宿主跑 sync-skills.sh**：它会试图往 skill 目录里补
#     内嵌 shared 副本，而链接指向仓库 ⇒ 等于往仓库里写文件。sync 已加 [linked] 跳过守卫。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRY_RUN=0
UNLINK=0
LIST_ONLY=0
TARGETS=()
EXCLUDE=(frontend-dev)

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --unlink) UNLINK=1; shift ;;
    --list-targets) LIST_ONLY=1; shift ;;
    --target) TARGETS+=("${2:-}"); shift 2 ;;
    -h|--help) sed -n '2,25p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "未知参数：$1" >&2; exit 1 ;;
  esac
done

if [ "${#TARGETS[@]}" -eq 0 ]; then
  TARGETS=(
    "$HOME/.zcode/skills"
    "$HOME/.qoder-cn/skills"
  )
fi

if [ "$LIST_ONLY" -eq 1 ]; then
  printf '%s\n' "${TARGETS[@]}"; exit 0
fi

is_excluded() {
  local id="$1" x
  for x in "${EXCLUDE[@]}"; do [ "$x" = "$id" ] && return 0; done
  return 1
}

win() { cygpath -w "$1"; }

# 链接一个目录：$1=链接位置 $2=仓库内真身
# 安全顺序：已存在的拷贝先改名 → 建链接 → 校验可读 → 才删旧拷贝；任一步失败即回滚改名。
link_dir() {
  local dest="$1" src="$2" bak="$1.old-$$"
  if [ -L "$dest" ]; then
    if [ "$(readlink "$dest")" = "$src" ]; then
      echo "   [ok]      $(basename "$dest")"; return 0
    fi
    echo "   [relink]  $(basename "$dest")  (现指向 $(readlink "$dest"))"
    [ "$DRY_RUN" -eq 1 ] && return 0
    cmd //c rmdir "$(win "$dest")" >/dev/null
  elif [ -e "$dest" ]; then
    echo "   [replace] $(basename "$dest")  (拷贝目录 → 链接)"
    [ "$DRY_RUN" -eq 1 ] && return 0
    mv -- "$dest" "$bak"
  else
    echo "   [new]     $(basename "$dest")"
    [ "$DRY_RUN" -eq 1 ] && return 0
  fi
  if ! cmd //c mklink //J "$(win "$dest")" "$(win "$src")" >/dev/null 2>&1; then
    echo "   [FAIL]    $(basename "$dest")：mklink 失败" >&2
    [ -e "$bak" ] && mv -- "$bak" "$dest"
    return 1
  fi
  if [ ! -d "$dest" ]; then
    echo "   [FAIL]    $(basename "$dest")：链接建出但不可读" >&2
    cmd //c rmdir "$(win "$dest")" >/dev/null 2>&1 || true
    [ -e "$bak" ] && mv -- "$bak" "$dest"
    return 1
  fi
  [ -e "$bak" ] && rm -rf -- "$bak"
  return 0
}

unlink_dir() {
  local dest="$1"
  if [ -L "$dest" ]; then
    echo "   [unlink]  $(basename "$dest")"
    [ "$DRY_RUN" -eq 1 ] && return 0
    cmd //c rmdir "$(win "$dest")" >/dev/null
  fi
}

# 仓内 skill 清单：id（frontmatter name）| 相对目录
mapfile -t PAIRS < <(
  git -C "$ROOT" ls-files -z '*SKILL.md' | tr '\0' '\n' | while IFS= read -r f; do
    [ -n "$f" ] || continue
    id="$(sed -n 's/^name:[[:space:]]*//p' "$ROOT/$f" | head -1 | tr -d '\r')"
    [ -n "$id" ] && printf '%s|%s\n' "$id" "$(dirname "$f")"
  done | sort -u
)

echo "源仓库：$ROOT"
echo "skill 数：${#PAIRS[@]}（EXCLUDE 保持拷贝：${EXCLUDE[*]}）"
[ "$DRY_RUN" -eq 1 ] && echo "模式：dry-run（不写入）"
[ "$UNLINK" -eq 1 ] && echo "模式：unlink（只撤链接）"
echo

for target in "${TARGETS[@]}"; do
  echo "== $target"
  if [ ! -d "$target" ]; then echo "   [skip] 目录不存在"; echo; continue; fi
  n_link=0; n_skip=0
  for pair in "${PAIRS[@]}"; do
    id="${pair%%|*}"; rel="${pair#*|}"
    if is_excluded "$id"; then echo "   [copy]    $id（EXCLUDE，保持拷贝）"; n_skip=$((n_skip+1)); continue; fi
    if [ "$UNLINK" -eq 1 ]; then unlink_dir "$target/$id"; else link_dir "$target/$id" "$ROOT/$rel"; fi
    n_link=$((n_link+1))
  done
  # shared 两个落点
  if [ "$UNLINK" -eq 1 ]; then
    unlink_dir "$target/shared"
    unlink_dir "$(dirname "$target")/shared"
  else
    link_dir "$target/shared" "$ROOT/shared"
    link_dir "$(dirname "$target")/shared" "$ROOT/shared"
  fi
  echo "   小结：处理 $n_link 个 skill，EXCLUDE 保留拷贝 $n_skip 个"
  echo
done
