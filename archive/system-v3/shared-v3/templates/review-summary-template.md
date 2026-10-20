# 评审汇总报告模板（公共结构基线）

> 适用：链上评审 / 周期审计类 skill 的汇总报告（Fidelity-Review、quality-inspection 用单报告模板，无需汇总）。各 skill 的 summary 模板为本模板的领域实例：闭环要素与字段口径以本文件为准，章节组织可按 skill 领域定制。**§0 上游闸门核对与 §0.5 评审上下文隔离为硬性小节。**

## 0. 上游闸门核对与本轮 Gate（硬性前置 · 缺本节不得记 `PASS`）

> 口径：`../gate-policy.md` §6。开工前（评审输入解析时）填一次，出 Gate 时复核一次。领域实例可按本域上游条目改名行，但四字段判据不得改口径。

| 上游 artifact | id | 当时版本 | 文件 mtime | `status` | `gate` | `allowDownstream` | 结论 |
|---|---|---|---|---|---|---|---|
| {{本批所依据的每个上游条目}} | {{ART-…}} | {{v…}} | {{YYYY-MM-DD HH:mm}} | APPROVED / SUPERSEDED | PASS / BLOCKED | true / false | 有效 / 已作废 / 已关闸 |

**时序核查**：上游基线转 `SUPERSEDED`（或方向类 DEC 落盘）的时刻 vs 被审产物 mtime——被审产物晚于作废 ⇒ **基准漂移**，标失效并重判，不得在旧基线上出结论。

**本轮 Gate（限定条件只落字段，不落注释）**：

```yaml
gate: PASS | CONDITIONAL | BLOCKED   # 上游 SUPERSEDED / gate 非 PASS / allowDownstream: false → 只能 BLOCKED
allowDownstream: true | false
blockedBy: []                        # 关闸时必填：owner / requiredInput / clearCondition
reason: <一句话>
```

「判据全闭」是事实记录，不是放行结论；**不得**用注释或正文写「本 `PASS` 仅对旧基线成立」变相放行——下游只读 `gate` / `allowDownstream` 字段，读不到限定语。缺本节 ⇒ Gate 不得写 `PASS`/`CONDITIONAL`：按风险记 `BLOCKED`，并写明缺的是哪一项闸门核对；`gate` 字段只允许 `PASS | CONDITIONAL | BLOCKED` 三值，「未验证」不是合法 Gate 值。

## 0.5 评审上下文隔离记录（硬性 · 缺本节 Gate 只能 BLOCKED）

> 口径：`../review-context-isolation.md` §6。开工前填派发信息，出 Gate 时复核。评审判断必须由隔离上下文作出；产出/修订/自检上下文不得自审。

| 字段 | 值 |
|---|---|
| isolationMode | subagent / new-session |
| reviewerRef | {{全部评审单元的评审者 id（多单元逗号分隔；子代理 id / 新会话 id）}} |
| packageDigest | sha256:{{...}} |
| parentExecution | {{主 executionId；有 run-log 时必填}} |
| producedByContextInvolved | false（必须为 false；true ⇒ BLOCKED） |
| verifiedArtifacts | {{报告与证据文件路径}} |

缺本节、`producedByContextInvolved: true`、或 `reviewerRef`/`packageDigest` 为空 ⇒ Gate 不得 `PASS`/`CONDITIONAL`，只能记 `BLOCKED`（缺评审隔离证据）。

## 1. 元数据

| 字段 | 内容 |
|---|---|
| 任务 ID | {{REVIEW-<评审名缩写>-<序号>}} |
| 评审对象 | {{需求/原型/设计稿/TDD/FTDD/代码 名称与路径}} |
| 日期 | {{YYYY-MM-DD}} |
| 角色/维度文档 | {{各角色（维度）评审文件名}} |

## 2. 角色/维度概览

| 角色/维度 | P0 | P1 | P2 | 小计 |
|---|---|---|---|---|
| {{维度 1..N}} | | | | |

## 3. 去重问题清单

| 编号 | 出处 | 严重度 | 问题 | 成因 | 命中角色/维度 | 建议方向 | 修复判据 |
|---|---|---|---|---|---|---|---|

- 编号格式 `SUM-xx`（按本表行序编）；任务清单沿用或按各 skill 规则重编；
- 同一问题多角色命中 → 合并为一条并标命中角色；标共性问题（多角色同时发现 = 系统性缺陷）。

## 4. 共性问题（系统性缺陷）

| # | 共性问题 | 命中角色/维度 | 问题编号 |
|---|---|---|---|

## 5. 统计与后续

P0/P1/P2 数量及阻塞说明；本 skill 不裁决，供用户决策；任务清单按各 skill 交接修改方。

## 6. 沉淀判定（双向，放行后回填）

| 方向 | 目标 skill | 落点 | 状态 |
|---|---|---|---|
| A · 防复发 | {{产出方 skill}} | 错误表加行 / references 清单 / Gate 预检项 | 待处理 / 已沉淀 / 入池 |
| B · 检出力 | {{发现问题的那一个评审 skill}} | `references/known-issue-patterns.md` 加模式（含检出方法） | 待处理 / 已沉淀 / 入池 |

- **P0 双向必沉**；P1/P2 由模型判是否属「会再犯的一类问题」（规则见 `shared/anti-deadloop.md` §4 Bidirectional learning）；
- 当场改不了的 → 落 `issue/<目标 skill>/<日期>/`（来源=评审闭环，写明双向落点）。
