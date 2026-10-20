# PRD 评审汇总报告 — {{需求名称}}

> 结构基线：仓库根 `../../../shared/templates/review-summary-template.md`（闭环要素[成因/修复判据/状态机]与字段口径以公共版为准；章节组织为本 skill 领域实例）。**公共 §0「上游闸门核对与本轮 Gate」为本报告硬性小节**（四字段判据口径同 `../../../shared/gate-policy.md` §6，不得改口径）：缺该节则本轮 Gate 只能记 `BLOCKED`（缺上游闸门核对证据），不得 `PASS` / `CONDITIONAL`。**§0.5「评审上下文隔离记录」同为硬性小节**：缺本节，或 `reviewerRef` / `packageDigest` 缺失、`producedByContextInvolved` 非 false ⇒ 本轮 Gate 只能记 `BLOCKED`（缺评审隔离证据），不得 `PASS` / `CONDITIONAL`。

> 汇总前端 / 后端 / 测试三角色 + 产品专家总审结果，去重合并并标共性问题；产品专家调度归并的已有问题标原编号 + 命中角色，不重复编号。

## 0.5 评审上下文隔离记录（硬性 · 缺本节 Gate 只能 BLOCKED）

> 口径：`../../../shared/review-context-isolation.md` §6 与公共基线 §0.5（`../../../shared/templates/review-summary-template.md`）。评审判断必须由隔离上下文作出；产出 / 修订 / 自检该 PRD 的上下文不得自审。开工前填派发信息（默认 1 个 fresh 评审子代理；按角色拆分时前端 / 后端 / 测试各 1 个子代理 + 产品专家总审子代理），出 Gate 时复核。

| 字段 | 值 |
|---|---|
| isolationMode | subagent / new-session |
| reviewerRef | {{各评审单元子代理 id / 新会话 id（角色拆分时：前端/后端/测试 + 产品总审，多单元逗号分隔）}} |
| packageDigest | sha256:{{...}} |
| parentExecution | {{主 executionId；有 run-log 时必填}} |
| producedByContextInvolved | false（必须为 false；true ⇒ BLOCKED） |
| verifiedArtifacts | {{报告与证据文件路径}} |

缺本节、`producedByContextInvolved: true`、或 `reviewerRef` / `packageDigest` 为空 ⇒ Gate 不得 `PASS` / `CONDITIONAL`，只能记 `BLOCKED`（缺评审隔离证据）。

## 1. 元数据
| 任务 ID | 需求名称 | 日期 | 角色文档 |
|---|---|---|---|
| REVIEW-SUM-{{}} | | | 前端/后端/测试/产品评审.md |

## 2. 角色概览
| 角色 | P0 | P1 | P2 | 小计 |
|---|---|---|---|---|

## 3. 去重问题清单
| 编号 | 出处 | 严重度 | 问题 | 成因 | 命中角色 | 建议方向 | 修复判据 |
|---|---|---|---|---|---|---|---|

- 编号格式 `SUM-xx`（按本表行序编）；任务清单沿用此编号或重编 REQ-xx（评审任务编号，与 PRD 需求编号 REQ-Mxx-nnn 无关）。
- 逐条直接列出；「建议方向」= 修改方向必填（改哪个概念 / 哪句话、往哪改）。

## 4. 共性问题与结论冲突（系统性缺陷）
| # | 共性问题 | 命中角色 | 问题编号 |
|---|---|---|---|

- 三角色结论冲突以产品专家调度裁决为准，记入本表并附裁决建议方向；定级以调度校准后为准。

## 5. 统计
P0/P1/P2 数量及阻塞说明。本 skill 不裁决，供用户决策。

## 6. 沉淀判定（双向，放行后回填）

| 方向 | 目标 skill | 落点 | 状态 |
|---|---|---|---|
| A · 防复发 | `prd-design` | 错误表加行 / references 清单 / Gate 预检项 | 待处理 / 已沉淀 / 入池 |
| B · 检出力 | `prd-review` | `references/known-issue-patterns.md` 加模式（含检出方法） | 待处理 / 已沉淀 / 入池 |

> P0 双向必沉；当场改则记目标 skill `CONTEXT.md` D-xx，改不了落 `../../../issue/PRD-Design/<日期>/`（来源=评审闭环；问题池沿用既有叶目录名 PRD-Design，skill id 用 prd-design）。