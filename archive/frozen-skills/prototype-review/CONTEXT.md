> LEGACY COMPATIBILITY NOTICE: This file preserves historical material. The active Skill, Gate, state, artifact, and evidence rules are defined by `shared/skill-contract.md`, `shared/gate-policy.md`, `shared/anti-deadloop.md`, `shared/artifact-contract.md`, `governance/`, and `.spec/workflow.yaml`.

# CONTEXT.md —— Prototype-Review 术语与决策记录

> Prototype-Review 的术语对齐源与决策日志；概念须与 SKILL/assets/references 一致。

## 一、角色与边界

- 人设：资深产品与交互体验专家。
- 目标：逻辑闭环、文案一致、防漏、防加戏。
- 边界：只审不改；产出 `.spec/原型评审/`；浏览器工具硬前置。

## 二、术语表

| 术语 | 定义 | 排除 |
|---|---|---|
| 四维评审 | 完整性/文案一致/流程闭环/实现质量 | 第 4 维不查视觉精修 |
| 防漏防加戏 | 每维双向：该有没有、不该有的有没有 | 不单向 |
| 截图走查 | 浏览器局部截图存证 | 不替代静态审查，双通道互证 |
| 要素映射基准 | PRD 功能点 ↔ 原型页面/载体矩阵 | 不是评审报告 |
| 任务清单 | 全量问题收口、待确认→裁决→回填 | 不是汇总附件 |
| 修复判据 | 修到什么表现算完成 | 不是修改建议 |
| 分级冻结 | P0/P1 阻断、P2 用户裁决 | 不是标注本身 |
| 复核只验本轮 | 不无限新增同级问题 | 不是每轮全量重扫 |
| 轮次上限 3 | 满 3 轮不收敛：残留 P0 ⇒ `BLOCKED`；残留 P1 不得 `PASS`，仅可完整授权 `CONDITIONAL`；不自动第 4 轮（口径 `../../shared/anti-deadloop.md` §3） | 不是硬跑 3 次、不是停下交用户，也不得强制放行 |
| 成因必写 | 结合代码剖析；推不出标成因未明 | 不是现象复述 |
| 建议修改方 | 原型→Prototype-Design；PRD→PRD-Design；双方→协同 | 不是自己修 |

## 三、决策日志

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 09-05 | 补轮次上限 3 + compatibility + CONTEXT | 体检逻辑闭环 P0 + 同步 P1×2 | ✅ |
| D-02 | 09-05 | 文案清单头部补 PRD 速查表对照物声明 | 独立执行文档缺对照物来源 | ✅ |
| D-03 | 09-05 | 六大索引枚举与 PRD-Design 对齐 | 简写语义偏窄 | ✅ |
| D-04 | 09-05 | 双通道独立互证显式化 | Vibe Coding 心法 4（评审独立性） | ✅ |
| D-05 | 09-09 | 体检修复 3 项：README「不防加戏」语义反转修正；速查表索引更名连锁；浏览器策略/三招/埋点收口 shared 引用 + issue-list 薄壳化（R9） | 全仓冗余专项体检（用户裁决全量修复 + R9 评审模板参数化） | ✅ |
| D-06 | 09-10 | 门禁闭环改造 + 双向沉淀：①步骤 7 末补「双向沉淀判定」（A 改 prototype-design / prd-design 防复发；B 本 skill `references/known-issue-patterns.md` 加模式含检出方法）；②超限动作由「停下交用户」改「强制清 P0 后放行，残留 P1 记遗留」；③步骤 4 补案例库对照；④新增案例库 + README/术语表同步 | 用户要求评审循环门禁 + 问题双向沉淀反哺 skill | ✅（已撤销：按 shared/anti-deadloop.md §3，残留 P0⇒BLOCKED、P1⇒仅授权 CONDITIONAL） |
| D-07 | 09-10 | **结构重构（统一骨架）**：章节 6 → 7——§一 定位与铁律（四维评审范围 + 铁律 5 条）；§二 输入与前置（输入表含缺失处理 + 输出目录清单）；§三 主流程 7 步 → **6 步**（「产出四份维度报告」并入「四维对照评审」，报告落盘不再是独立步骤）；§四 评审规范（严重度分级）；**§五 错误表（新增，此前缺失）**；**§六 资源清单（新增，此前缺失）**；§七 埋点。old-vs-new 审计：原条目全部有归属，且补上了缺失的两节 | 用户要求：整理成顺畅流程（Skill-Optimizer 全量体检） | ✅ |
| D-08 | 09-15 | 全仓一致性纠偏：summary-template 补沉淀判定节（SKILL 承诺未落地）、维度模板与汇总表补修复判据列；cases 步骤编号纠正（步骤 3~5/6 → 随步骤 4 同步、汇总步骤 5 前）；README 流程补双向沉淀判定；dimension/summary 编号对齐公共模板 SUM-xx；browser-inspection-guide 标题错别字「审批」→「走查」 | 四代理并行七维体检 | ✅ |

| D-09 | 2026-10-10 | Preconditions 新增「上游输入的**批准状态现行有效**」一条：逐条读 `.spec/manifest.yaml` 上游条目的 `status`、`version`、`gate`、`allowDownstream`，任一 `SUPERSEDED`／非 `PASS`／`false` ⇒ 本轮只能 `BLOCKED`（判据全闭只作事实；限定条件只能落字段，`../../shared/gate-policy.md` §6），汇总报告须含公共 §0 核对表；`assets/summary-template.md` 结构基线行加该硬性小节指针 | `issue/WorkFlow/2026-10-10/01`＋`issue/UI-UX-Review/2026-10-10/01` 对称补齐（评审节点承接位落差）；用户裁决「先要解决这些问题」 | ✅ 规则已改｜◐ 未经真实场景 fresh 复跑验证 |
| D-10 | 2026-10-19 | **评审上下文隔离硬性化（用户要求）**：新增「评审上下文隔离（执行必需）」节——四维各 1 个独立 fresh 评审子代理（互不可见）+ 1 个独立汇总子代理（只读四份维度报告 + 模板），编排形态只做基线核对 / 建包 / 派发 / 收产物 / 落 Gate；无子代理写包 + dispatch-prompt 交新会话，仍无 ⇒ `BLOCKED`；Procedure 加步骤 0「隔离派发（REQUIRED）」并标注步骤 4/5/6 形态；Preconditions / Outputs / Evidence 增补隔离前置、评审包与隔离记录；summary 模板加 §0.5、dimension 模板加元数据「评审上下文 / 评审包摘要」；README 补隔离规则（legacy 四维流程仅限隔离评审子代理执行） | 用户 2026-10-19 要求评审类 Skill 不得在产出同一上下文评审（`issue/Skill-Optimizer/2026-10-19/01`）；依据 review 独立性、公共契约 `../../shared/review-context-isolation.md` | ✅ 规则已改｜◐ 待 fresh-agent 行为验证 |

## 四、待决问题

无。