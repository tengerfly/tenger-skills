# Inspection Report Template

# 项目质量巡检报告

- 项目：
- 巡检日期：YYYY-MM-DD
- 分支 / commit：
- 环境：
- 范围：
- 上次巡检：
- 审计上下文：{{审计子代理 id / 新会话 id}}（必须隔离；产出/修复/发布/自查过被巡检代码的上下文不得自审）
- 评审包摘要：sha256:{{...}}
- Gate：PASS | CONDITIONAL | BLOCKED（分别对应状态 INSPECTION_PASS / INSPECTION_CONDITIONAL / INSPECTION_BLOCKED）

## 0.5 审计上下文隔离记录（硬性 · 缺本节 Gate 只能 BLOCKED）

> 口径：`../../../shared/review-context-isolation.md` §6。

| 字段 | 值 |
|---|---|
| isolationMode | subagent / new-session |
| reviewerRef | {{子代理 id / 新会话 id}} |
| packageDigest | sha256:{{...}} |
| parentExecution | {{主 executionId；有 run-log 时必填}} |
| producedByContextInvolved | false（必须为 false；true ⇒ BLOCKED） |
| verifiedArtifacts | {{报告与证据文件路径}} |

缺本节、`producedByContextInvolved: true`、或 `reviewerRef`/`packageDigest` 为空 ⇒ Gate 不得 `PASS`/`CONDITIONAL`，只能记 `BLOCKED`（缺审计隔离证据）。

## 1. 门禁结果

| 检查 | 命令/来源 | 结果 | 退出码/证据 |
|---|---|---|---|

## 2. 趋势摘要

- 测试健康度：
- 构建/依赖：
- 运行错误/性能：
- 可观测性覆盖：
- 与上次相比：

## 3. 发现项

| ID | 类别 | 级别 | 证据 | 影响 | 路由 | 最小下一步 | 验证方式 |
|---|---|---|---|---|---|---|---|

## 4. 未检查项与例外

| 项目 | 原因 | 风险 | 补证动作 | 责任人 | 截止日期 |
|---|---|---|---|---|---|

## 5. 下一次巡检

- 日期/周期：
- 必查项：
- 需要补齐的基线：
