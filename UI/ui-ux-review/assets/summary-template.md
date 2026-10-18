# 设计稿评审汇总报告

> 结构基线：仓库根 `../../../shared/templates/review-summary-template.md`（闭环要素[成因/修复判据/状态机]与字段口径以公共版为准；章节组织为本 skill 领域实例）。

> 项目名称：[项目名称]  
> 评审基线：PRD（[路径]）+ 布局清单（[路径]）+ design-system（[路径]） vs 设计稿（[路径]）  
> 评审时间：[YYYY-MM-DD]  
> 浏览器工具状态：[Playwright / browser-use / agent-browser 等任一可用（开工硬性预检通过）]

---

## 〇、上游闸门核对与本轮 Gate（硬性前置 · 缺本节不得记 `PASS`）

> 口径：`../../../shared/gate-policy.md` §6；本节是公共基线 `../../../shared/templates/review-summary-template.md` §0 的领域实例（行按本域上游条目定制，四字段判据口径一致不得改）。本表在**开工前**（SKILL 步骤 1）填一次并核对，出 Gate 时（步骤 6）复核一次；上游关闸或基线作废时，「判据全闭」只作事实记录，放行状态为 `BLOCKED`。

| 上游 artifact | id | 当时版本 | 文件 mtime | `status` | `gate` | `allowDownstream` | 结论 |
|---|---|---|---|---|---|---|---|
| PRD | [PRD-YYYYMMDD-NNN] | [v0.x] | [YYYY-MM-DD HH:mm] | APPROVED / SUPERSEDED | PASS / BLOCKED | true / false | 有效 / 已作废 / 已关闸 |
| 布局清单 + 低保真原型 | […] | […] | […] | […] | […] | […] | […] |
| design-system | […] | […] | […] | […] | […] | […] | […] |

**时序核查**（基线作废时刻 vs 被审产物 mtime，防「在作废基线上收口」）：

| 事件 | 时刻 | 依据 |
|---|---|---|
| 上游基线转 `SUPERSEDED` / 方向类 DEC 落盘 | [时刻] | [manifest / `decisions/` 行 + mtime] |
| 被审设计稿最后一次产出 | [时刻] | [文件 mtime] |
| 判定 | [被审产物早于作废 = 旧周期合法；晚于作废 = 基准漂移，标失效并重判] | [另 grep 本轮判据引用的上游原文是否仍在，消失即判漂移] |

**本轮 Gate（限定只落字段，不落注释）**：

```yaml
gate: PASS | CONDITIONAL | BLOCKED   # 上游 SUPERSEDED / gate 非 PASS / allowDownstream: false → 只能 BLOCKED
allowDownstream: true | false
blockedBy: []                        # 关闸时必填：owner / requiredInput / clearCondition
reason: <一句话>
```

**收口语固定**：基线有效 → 「本周期判据全闭（轮次 n/3），放行 <Gate>」；基线作废或上游关闸 → 「本周期判据全闭（轮次 n/3）；放行状态 `BLOCKED`，缺 <上游批准 + 增量>」。**不得**用注释或正文写「本 `PASS` 仅对旧基线成立」来变相放行——下游只读 `gate` / `allowDownstream` 字段，读不到限定语。

---

## 一、评审概览

### 1.1 总体结论
- **评审状态**：[需修复后复核 / 基本符合预期 / 存在阻塞级缺陷]
- **问题总数**：共 **[N]** 项
  - **P0 致命**：[X] 项（结构错位 / 主流程入口不可点 / 整体脱离规范）
  - **P1 重要**：[Y] 项（局部结构偏差 / 文案逐字不符 / 单入口死元素 / 规范局部未执行 / 渲染报错）
  - **P2 建议**：[Z] 项（非关键文案微调 / 次要视觉建议 / 边缘渲染瑕疵）

### 1.2 维度分布表

| 评审维度 | 报告链接 | P0 | P1 | P2 | 合计 | 主要缺陷特征 |
|---|---|---|---|---|---|---|
| **载体与结构零改动** | [载体与结构零改动评审.md](./载体与结构零改动评审.md) | [ ] | [ ] | [ ] | [ ] | [简述] |
| **文案与字段一致性** | [文案与字段一致性评审.md](./文案与字段一致性评审.md) | [ ] | [ ] | [ ] | [ ] | [简述] |
| **视觉规范一致性** | [视觉规范一致性评审.md](./视觉规范一致性评审.md) | [ ] | [ ] | [ ] | [ ] | [简述] |
| **视觉呈现与可交付质量** | [视觉呈现与可交付质量评审.md](./视觉呈现与可交付质量评审.md) | [ ] | [ ] | [ ] | [ ] | [简述] |

---

## 二、共性与系统性问题归纳

> 多个维度共同涉及或整套设计稿普遍存在的系统性问题：

1. **[共性问题 1 标题]**
   - **涉及页面**：`xxx.html`, `yyy.html`
   - **问题现象**：[描述]
   - **根本成因**：[分析，如某 token 系统性未消费、某区块批量漏译]
   - **证据出处**：[截图路径 / 实测表行 / 命令输出；无证据不得写成已确认问题]
   - **系统级修改建议**：[建议]

> 跨页不变量类（宽度档位、全局组件漂移）按共性问题合并成一条，附「跨页宽度实测表」出处（`../references/rendered-quality-checklist.md` §七）；收敛方案属设计方向决策，须用户裁决后才改。

---

## 三、去重合并问题总表

| 问题编号 | 严重度 | 涉及页面/组件 | 问题摘要 | 根因分类 | 修复判据 | 建议修改方 |
|---|---|---|---|---|---|---|
| SUM-001 | P0 | [页面/弹框] | [简述] | [结构/文案/规范/渲染/布局清单/PRD] | [一句话] | UI-UX-Design / Prototype-Design |
| SUM-002 | P1 | [页面/组件] | [简述] | […] | [一句话] | UI-UX-Design |

> 编号格式 `SUM-xx`（按本表行序编）；任务清单沿用或重编 `ISSUE-xx`，映射关系在清单内标注（维度报告编号 → `SUM-xx` → `ISSUE-xx`）。

---

## 四、后续闭环指引

1. 请用户查阅并裁决 `.spec/设计评审/任务清单.md`：
   - 需修复项标注 `已确认`；无需修改或后续迭代项标注 `已忽略` 并注明理由；
2. 用户确认后，任务清单交回对应 Skill（`UI-UX-Design` 改设计稿 / `Prototype-Design` 改布局清单 / `PRD-Design` 改 PRD）执行定向修复；
3. 修改方修复完毕回填任务清单为 `已修复` 并写明修改说明，触发复核；
4. Gate 口径见 ../../../shared/gate-policy.md：仅 PASS/CONDITIONAL/BLOCKED；残留 P0⇒BLOCKED；残留 P1 不得 PASS，仅完整授权 CONDITIONAL（exceptionId/risk/owner/dueAt/remediation/allowDownstream/approvalRef）；无 force-pass。

## 五、沉淀判定（双向，放行后回填）

| 方向 | 目标 skill | 落点 | 状态 |
|---|---|---|---|
| A · 防复发 | {{UI-UX-Design / Prototype-Design / PRD-Design}} | 错误表加行 / references 清单 / Gate 预检项 | 待处理 / 已沉淀 / 入池 |
| B · 检出力 | `UI-UX-Review` | `../references/known-issue-patterns.md` 加模式（含检出方法） | 待处理 / 已沉淀 / 入池 |

> P0 双向必沉；当场改则记目标 skill `../CONTEXT.md` D-xx，改不了落 `../../../issue/<目标 skill>/<日期>/`（来源=评审闭环）。
