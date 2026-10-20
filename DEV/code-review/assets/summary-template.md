# 代码评审汇总报告

> 结构基线：仓库根 `../../../shared/templates/review-summary-template.md`（闭环要素[成因/修复判据/状态机]与字段口径以公共版为准；章节组织为本 skill 领域实例）。**公共 §0「上游闸门核对与本轮 Gate」为本报告硬性小节**（四字段判据口径同 `../../../shared/gate-policy.md` §6，不得改口径）：缺该节则本轮结论只能记「未验证」，交回 Workflow 判停，不得 `PASS`。**公共 §0.5「评审上下文隔离记录」同为硬性小节**：缺该节或隔离证据不符 ⇒ Gate 只能 `BLOCKED`。

> 合并后端/前端两份清单：去重 + 共性 + 统计。需求：{{}}；日期：{{}}。

## 0.5 评审上下文隔离记录（硬性 · 缺本节 Gate 只能 BLOCKED）

> 口径：`../../../shared/review-context-isolation.md` §6。评审判断必须由隔离评审者作出；产出/修复被审代码的上下文（含编排会话）不得自审。

| 字段 | 值 |
|---|---|
| isolationMode | subagent / new-session |
| reviewerRef | {{⑬-后：批次评审子代理 id；⑬-前：前端批次评审子代理 id + Fidelity-Review 评审子代理 id + 汇总子代理 id}} |
| packageDigest | sha256:{{各单元评审包摘要（多个以逗号分隔）}} |
| parentExecution | {{主 executionId；有 run-log 时必填}} |
| producedByContextInvolved | false（必须为 false；true ⇒ BLOCKED） |
| verifiedArtifacts | {{角色文档 / Fidelity-Review 报告 / 汇总报告 / 任务清单与证据路径}} |

缺本节、`producedByContextInvolved: true`、或 `reviewerRef`/`packageDigest` 为空 ⇒ Gate 不得 `PASS`/`CONDITIONAL`，只能记 `BLOCKED`（缺评审隔离证据）。

## 一、评审范围
被审代码、文档基线、静态验证摘要。

## 二、前后端契约错误（核心共性）
| 编号 | 接口 | 问题 | 成因 | 归因 | 严重度 |
|---|---|---|---|---|---|
| C-01 | | | | 后端/前端/双方 | P0 |

## 三、合并去重清单
同一处多视角命中合并，标命中视角。

## 四、严重度统计
后端 / 前端 / 契约 / 去重合计，按 P0/P1/P2。

## 五、结论与建议
- 是否可联调：契约专项全绿且无 P0 才可。
- 顺序：P0 契约 → P1 架构/异常 → P2 质量。
- 职责：契约交 Backend/Frontend-Dev；业务正确性交测试。

## 六、备注
只审不改；P0 补丁见角色文档第四节。

## 七、沉淀判定（双向，放行后回填）

| 方向 | 目标 skill | 落点 | 状态 |
|---|---|---|---|
| A · 防复发 | `Backend-Dev` / `Frontend-Dev` | 错误表加行 / references 清单 / Gate 预检项 | 待处理 / 已沉淀 / 入池 |
| B · 检出力 | `Code-Review` | `references/known-issue-patterns.md` 加模式（含检出方法） | 待处理 / 已沉淀 / 入池 |

> P0 双向必沉；当场改则记目标 skill `CONTEXT.md` D-xx，改不了落 `../../../issue/<目标 skill>/<日期>/`（来源=评审闭环）。⑬-前 还原度问题由 `Fidelity-Review` 出、交本 skill 统一执行沉淀判定（含其 `known-issue-patterns.md`）。