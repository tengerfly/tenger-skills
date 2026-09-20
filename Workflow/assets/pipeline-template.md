> LEGACY COMPATIBILITY NOTICE: This template is retained for old numbered-pipeline compatibility. The active state source is `.spec/workflow.yaml`; this file must not be treated as the current state database.

# {{项目名称}} · 开发流程状态（PIPELINE）

> Workflow 唯一状态源，其他 skill 只读不写。续跑先读本文件从「当前节点」继续；只记录本次路径节点。

## 一、项目信息
| 项目名称 | 根目录 | 目标端 | 创建 | 更新 |
|---|---|---|---|---|
| {{}} | {{}} | {{}} | {{}} | {{}} |

## 二、本次路径
| 起点 | 终点 | 计划节点序列 | 跳过节点 | 当前节点 |
|---|---|---|---|---|

## 三、进度
| # | 节点 | 调用 Skill | 状态 | 门禁轮次 | 门禁结果 | 产物路径 | 更新时间 |
|---|---|---|---|---|---|---|---|

状态：未开始 / 进行中 / 已完成 / 已跳过（写原因）/ 已阻塞（写原因）。
门禁轮次：该节点的「修复 → 复核」已跑轮次（非门禁节点填 `-`）。
Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 requires an authorized CONDITIONAL exception record. Never force-pass.

## 四、交接记录
每完成一个节点追加一条（下游开工前读最近一条）。
### {{N}}. {{节点名}}（{{时间}}）
- 执行 Skill / 产出物 / 给下游输入 / 遗留待确认 / 用户决定
- 门禁闭环：轮次 N · 放行结论 · 沉淀（当场改：{{skill}} D-xx｜入池：`issue/{{skill}}/{{日期}}/NN-xxx.md`）

## 五、遗留问题
门禁未清即放行（授权 CONDITIONAL）或 P2 留后续的问题逐条列出：编号 / 问题 / 等级 / 出处 / 后续处理。

## 六、流程结论
结束时填：完成节点、跳过节点、遗留问题汇总。
