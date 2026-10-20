# 评审包 — {{reviewId}}

> 本文件是隔离评审子代理的输入之一。只写「产物 + 判据 + 输出契约」；**禁止**写入产出会话历史、草稿、自检结论、未确认猜测或「我觉得哪里有问题」的引导。规则见仓库根 `shared/review-context-isolation.md`。

## 1. 评审任务

| 字段 | 值 |
|---|---|
| reviewId | `REV-{{YYYYMMDD}}-{{NN}}` |
| 评审 Skill | {{prd-review / prototype-review / ...}} |
| 评审单元 | {{角色 / 维度 / 批次}} |
| 评审轮次 | {{n}}/3 |
| 隔离模式 | subagent / new-session |
| 评审者 | {{本单元 subagent id / session id；**派发后在报告 §0.5 回填，不改本包字节**；多单元汇总时在报告 §0.5 逗号分隔列出}} |
| 父执行（有 run-log 时） | {{executionId}} |
| 包摘要 | `sha256:{{...}}`（`Get-FileHash` / `sha256sum`） |

## 2. 被审对象（精确版本）

| 项 | 路径 | 版本 / commit | contentDigest |
|---|---|---|---|
| {{产物}} | {{path}} | {{vN / commit}} | {{sha256 或 N/A}} |

## 3. 判据与基线

| 项 | 路径 / 值 | 状态 |
|---|---|---|
| {{PRD / 原型 / 设计稿 / TDD / FTDD / 上游 gate}} | {{path}} | {{APPROVED / gate / allowDownstream}} |

上游闸门核对结论：{{有效 / 已作废 / 已关闸 → BLOCKED}}

## 4. 清单、模板与案例库

- 检查清单：{{本域 references 路径列表}}
- 已知问题模式：{{known-issue-patterns.md 路径}}
- 报告 / 清单模板：{{assets 路径列表}}

## 5. 上轮已确认问题（F1）

| 编号 | 问题 | 修复判据 | 上轮状态 |
|---|---|---|---|
| {{F1-01}} | {{}} | {{}} | {{已修复待复核 / 未修复}} |

> 只放已确认项与修复判据；不放产出方辩解、自查结论或未确认猜测。

## 6. 输出契约

- 报告落点：{{path}}
- 编号 / 分级口径：{{见本域模板与 shared/gate-policy.md §1}}
- 证据要求：{{截图目录 / 命令+退出码 / 文件:行 / 渲染证据}}
- Gate 建议格式：{{P0/P1/P2 计数 + 建议 Gate + 依据}}
- 只审不改：不改被审产物；问题进清单交产出方。
- 报告 §0.5 必须填 `isolationMode` / `reviewerRef` / `packageDigest` / `parentExecution` / `producedByContextInvolved: false` / `verifiedArtifacts`。

## 7. 派发前自检（编排方勾选）

- [ ] 未包含产出过程、草稿、自检结论、未确认猜测
- [ ] 未要求评审者修改被审产物
- [ ] 评审者不读取产出会话记录
- [ ] 被审对象版本与判据版本可定位
- [ ] 已计算包摘要并写入 §1
