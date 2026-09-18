# GitHub API Playbook（采集通道手册）

> 步骤①发现 / ②采集 执行时加载。技术型内容讲判据不写死流程；限流数字是硬约束，记牢防封。

## 目录

- [一、通道与限流](#一通道与限流)
- [二、常用端点](#二常用端点)
- [三、搜索查询语法](#三搜索查询语法)
- [四、增量与去重](#四增量与去重)
- [五、限流应对](#五限流应对)

## 一、通道与限流

| 通道 | 配额 | 适用 |
|---|---|---|
| `gh api`（本机 gh CLI 已认证） | 5000 次/h | **首选**；配额宽、可带 `--jq` 直接出结构化结果 |
| `api.github.com` 免认证 | 核心 60 次/h；**search 10 次/分** | gh 不可用时；省着用，一次 search 值十次 core |
| `raw.githubusercontent.com` | 宽松，不计 core 配额 | 拉单文件原文（README/SKILL.md）优先走这 |
| WebSearch / web_reader | 各自限制 | 前两类全 403 时的兜底；也用于「GitHub Trending」无官方 API 的替代 |

限流响应头：`X-RateLimit-Remaining`（剩余）、`X-RateLimit-Reset`（重置时刻的 epoch 秒）——437 前先看 Remaining 决定收敛。

## 二、常用端点

```bash
# 1. 搜仓库（发现步主力）
gh api "search/repositories?q=topic:claude-skills+pushed:>2026-09-01&sort=stars&order=desc&per_page=10" \
  --jq '.items[] | {full_name, stargazers_count, pushed_at, description}'

# 免认证等价：
curl -s "https://api.github.com/search/repositories?q=topic:agent-skills&per_page=10"

# 2. 仓库元信息（分诊用：星数/license/活跃度/默认分支）
gh api repos/<owner>/<repo> --jq '{stars: .stargazers_count, license: .license.spdx_id, pushed_at, default_branch}'

# 3. README 原文
gh api repos/<owner>/<repo>/readme -H "Accept: application/vnd.github.raw+json"

# 4. 目录树（一次拿全 repo 文件清单，免逐层 contents）
gh api "repos/<owner>/<repo>/git/trees/<default_branch>?recursive=1" --jq '.tree[].path'

# 5. 单文件原文（raw 通道，省配额）
curl -s "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>"
```

## 三、搜索查询语法

qualifier 组合（与/或、排除均支持）：

| qualifier | 作用 | 例 |
|---|---|---|
| `topic:` | 按 topic 精确匹配 | `topic:claude-skills` |
| `language:` | 主语言 | `language:typescript` |
| `pushed:` / `created:` | 增量窗口 | `pushed:>2026-09-01` |
| `stars:` | 星数门槛（分诊降噪） | `stars:>50` |
| `in:name,description,readme` | 关键词命中范围 | `skill in:name,description` |
| NOT（大写）/ `-` 前缀 | 排除 | `NOT tutorial`、`topic:ai-agent language:vue` |

skill 泳道常用 topics：`claude-skills`、`agent-skills`、`claude-code`、`mcp`、`awesome-claude`；项目泳道关键词按 watchlist 技术栈填（如 `nestjs`、`vue3`、`monorepo`、`ai-agent`）。

## 四、增量与去重

1. 时间窗：所有 search 拼上 `pushed:><last_run>`（watchlist 台账取值），只看动过的仓。
2. 已扫排除：候选出来后对照台账「已扫 repo」清单手工剔除（search 的排除 qualifier 不覆盖全场景，台账是唯一事实源）。
3. 深读去重：情报库已有同 repo 条目时，本轮只补「新增量」，不重写旧发现。

## 五、限流应对

| 症状 | 动作 |
|---|---|
| search 返回 403/429 | 看 `X-RateLimit-Reset`；等不够划算就直接降级通道（免认证→WebSearch） |
| core 60/h 用尽 | 余下采集全走 `raw.githubusercontent.com` + gh（若可用） |
| 全通道不可用 | 本轮唯一合法停机点：报告写明通道全灭 + 建议 tomorrow 再跑，台账不动 |
