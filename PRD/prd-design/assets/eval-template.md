# PRD 交付三段式验收与 Pass Gate 报告（Eval Template）

> 产出文件名：`验收结果详细说明.md`（归档于 `.spec/PRD/VN/`）。

> 用户终审前自检；报告数量必须为重新清点实测值。

## 1. 元数据
| 字段 | 内容 |
|---|---|
| ID | EVAL-PRD-{{TIMESTAMP}} |
| 需求/版本 | {{}} |
| 模式 | [从0到1]/[存量迭代] |
| 目录 | .spec/PRD/{{VERSION}}/ |
| 裁决 | PASS / CONDITIONAL / BLOCKED |

## 2. 第一段：结果是什么（交付事实）
### 2.1 overview 完备度
- 十一章齐全（成功度量按开关留痕）。
- 泳道图（含异常）；导航与入口结构；模块关联图+双向核对表。
- 模块四要素；全局规范四件套。
- 迭代：差异矩阵+兼容影响；未变更模块页首声明。

### 2.2 模块文档完备度（九章）
- 负向边界 + 用户故事。
- §3 步骤流入口/出口成对。
- §4 图无死路悬空。
- §8 信息清单仅三列。
- §9 Gherkin 单源、编号连续、Then 业务断言。
- 总纲 §4 未开启则无度量章。

### 2.3 实测计数
模块数 / 场景数 / 异常行 / AC 数 / AC 引用占比。

## 3. 第二段：结果缺什么（盲区扫描）
B1 禁词 / B2 模糊未决 / B3 假设漏标 / B4 实现词越界 / B5 断头无头 / B6 状态机 / B7 跨模块断点 / B8 双轨残留 / B9 度量开关违规 / B10 编造；每项结论 [无/风险/致命]。

## 4. 第三段：缺陷清单
P0 一票否决：B4/B5/B6/B7/B8/B10、禁词、模糊、编造。P1：假设漏标/异常缺兜底/覆盖不达标。P2：润色。
| 编号 | 文件 | 等级 | 描述 | 措施 | 状态 |
|---|---|---|---|---|---|
| DEF-01 | | | | | [Fixed] |

## 5. 模块级内联自检
| 模块 | 时间 | 快扫 B2~B5 | P0 | 放行 |
|---|---|---|---|---|
| 01_A | 成文后 | 通过 | 0 | ✅ |

## 6. Pass Gate 裁决
Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.
Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.
