#!/bin/bash
# 回填各项目 .spec/问题日志.md（台账索引，一事一源：详情留在各评审产物内）
# 用法: bash gen-problem-logs.sh <项目根目录> ...
BASE="$(cd "$(dirname "$0")" && pwd)"
DIRS="需求评审 原型评审 技术方案评审 代码评审 设计评审 页面还原评审 页面还原核验 测试 auto-test bug修复"
for proj in "$@"; do
  spec="$proj/.spec"
  [ -d "$spec" ] || { echo "跳过(无 .spec): $proj"; continue; }
  rows=""
  for d in $DIRS; do
    dd="$spec/$d"
    [ -d "$dd" ] || continue
    mtime=$(find "$dd" -name "*.md" -not -path "*screenshots*" -printf "%TY-%Tm-%Td\n" 2>/dev/null | sort | tail -1)
    [ -z "$mtime" ] && mtime=$(date -r "$dd" "+%Y-%m-%d" 2>/dev/null)
    rounds=$(ls "$dd" 2>/dev/null | grep -v -i "screenshot" | head -4 | tr '\n' ' ')
    rel=".spec/$d"
    rows="${rows}| $mtime | $d | \`$rel/\` | $rounds | 回填 | 待综合分析 |
"
  done
  if [ -z "$rows" ]; then
    note="暂无问题记录：当前 .spec 下没有评审/测试/Bug 类产物目录。"
  else
    note=""
  fi
  cat > "$spec/问题日志.md" <<EOF
# 问题日志（$(basename "$proj")）

> 定位：本项目所有评审 / 测试 / Bug-Fix 产生问题的**台账索引**——只记一行索引，问题详情留在各评审产物内（一事一源，不复制内容）。
> 写入规则：评审 / 测试 / Bug-Fix 收尾归档时**追加一行**；修复闭环状态在对应评审任务清单内维护，本文件只记状态与反哺出口。
> 综合分析：定期读本文件 + tenger-skills \`issue/\` + \`evolution/信号/\`，按 \`issue/README.md\` §问题数据流总览的出口分工反哺（对 Skill-Optimizer 说「综合分析问题日志」触发）。
> 本文件由 2026-09-19 收敛整理回填生成（状态列「回填」= 既有产物补记，日期取产物最近修改时间）。

## 台账

| 日期 | 来源 | 问题产物 | 轮次/范围 | 状态 | 反哺出口 |
|---|---|---|---|---|---|
EOF
  [ -n "$rows" ] && printf "%s" "$rows" >> "$spec/问题日志.md"
  if [ -n "$note" ]; then echo "" >> "$spec/问题日志.md"; echo "$note" >> "$spec/问题日志.md"; fi
  echo "已生成: $spec/问题日志.md ($(printf "%s" "$rows" | grep -c "^|" 2>/dev/null) 行)"
done
