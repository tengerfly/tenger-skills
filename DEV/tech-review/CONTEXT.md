> LEGACY COMPATIBILITY NOTICE: This file preserves historical material. The active Skill, Gate, state, artifact, and evidence rules are defined by `shared/skill-contract.md`, `shared/gate-policy.md`, `shared/anti-deadloop.md`, `shared/artifact-contract.md`, `governance/`, and `.spec/workflow.yaml`.

# CONTEXT.md —— Tech-Review 术语与决策记录

> Tech-Review 的术语对齐源与决策日志。

## 一、角色与边界

- 人设：软件开发专家（后端/前端双视角）。
- 目标：审技术方案的闭环 + 关联。
- 边界：只审不改；无 Pass/Fail；浏览器软检测。

## 二、术语表

| 术语 | 定义 |
|---|---|
| 闭环 | 需求/流程/状态/数据四类文档层闭环 |
| 关联关系错误 | 模块/接口/页面—原型的一致性断裂 |
| 双视角隔离 | 独立评审、汇总才合并 |
| 关联一致性专项 | FTDD 页面字段清单 ⇄ fetch ↔ TDD 出参三方对账（双向一致 ≠ 完备，字段清单为完备性锚） |
| 任务清单/修复判据/冻结/复核/上限 | 与仓库评审类一致 |
| 浏览器软检测 | 全无跳过不阻塞 |

## 三、决策日志

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 09-05 | 低保真术语修正 + 轮次上限 3 + 新建 CONTEXT | 体检术语/逻辑闭环 P0 + 三件套 | ✅ |
| D-02 | 09-05 | checklist 补 PRD 速查表入口 | 独立加载失同步 P1×2 | ✅ |
| D-03 | 09-05 | 双视角独立上下文 + 可换模型交叉 | 心法4 | ✅ |
| D-04 | 09-09 | 体检修复 6 项：术语统一「技术方案文档」；7 步与流程图对齐；汇总报告文件名一致；README 摘要补判据；「无缝」改可判定表述；三招/分级收口 shared + issue-list 薄壳化（R9） | 全仓冗余专项体检（用户裁决全量修复 + R9 评审模板参数化） | ✅ |
| D-05 | 09-10 | 门禁闭环改造 + 双向沉淀：①支持分端单批（⑩-后 只审 TDD；⑩-前 审 FTDD 并收口 FTDD↔TDD 完整接口一致性）；②步骤 8 改「闭环复核与双向沉淀判定」（A 改 Backend/Frontend-Tech-Design 防复发；B 本 skill `references/known-issue-patterns.md` 加模式含检出方法）；③超限动作由「停下交用户」改「清 P0 后放行」（已撤销：按 shared/anti-deadloop.md §3，残留 P0⇒BLOCKED、P1⇒仅授权 CONDITIONAL）；④新增案例库并在步骤 3 对照；⑤资源清单/README/错误表/description 同步 | 用户要求写一个审一个 + 问题双向沉淀反哺 skill | ✅ |
| D-06 | 09-10 | **结构重构（统一骨架）**：章节 10 → 7——§一 定位与铁律（铁律 7 条 + 适用范围）；§二 输入与前置（输入表 + 批次裁剪 + **视角分工表**，把原 §二·§四 合并）；§三 主流程 8 步；§四 评审规范 4.1 找没闭环 + 4.2 找关联错误 + 4.3 严重度（原 §三·§六 归并）；§五 错误表 / §六 资源 / §七 埋点。old-vs-new 审计：原条目全部有归属，无功能丢失 | 用户要求：整理成顺畅流程（Skill-Optimizer 全量体检） | ✅ |
| D-07 | 09-15 | 视觉基准口径纠偏：§二输入表新增「设计稿（有则）= 评审基线（视觉）」行、⑩-前 批次裁剪纳入设计稿；步骤 1 输入解析补读设计稿；§4.2 关联错误表新增「页面—设计稿」行；`frontend-checklist.md` 标准与 FE-T1 补设计稿逐页对应、新增 FE-T8「视觉基准承接」（§8.6 token 来源/条数未登记 = 问题）；`role-review-template.md` 输入基线加设计稿 | 用户反馈设计稿 OK 但实现页差别大；FTDD 未承接视觉基准是链条首端断点，须在 ⑩-前 拦住（配合 Frontend-Tech-Design D-17） | ✅ |
| D-08 | 09-15 | 全仓一致性纠偏：视角分工「标准」列补设计稿（视觉）；README 关联补「页面—设计稿」、流程改分端单批 8 步并补闭环复核与沉淀判定；role-review-template 补修复判据列；known-issue-patterns 补表头并修错别字「叠床架屋」 | 四代理并行七维体检 | ✅ |
| D-09 | 09-17 | ⑩-前 关联专项升级三方对账：「FTDD 页面字段清单 ⇄ fetch ↔ TDD 出参」——双向一致查不出两端同时缺失；清单有 TDD 无 = 完备性缺口，FTDD 无清单 = 方案缺失；§二批次裁剪、§4.2 关联表、错误表、integration-checklist IT-6、known-issue-patterns #3、术语表同步 | 用户痛点：开发期才发现后端接口少字段（../../issue/Tech-Review/2026-09-17/01；联动 Frontend-Tech-Design D-20 / Frontend-Dev D-22） | ✅ |

| D-10 | 2026-10-10 | 步骤 1「输入解析」加〔REQUIRED · 开工前闸门核对〕：逐条读上游（PRD／原型／设计稿／对面方案）的 `status`、`version`、`gate`、`allowDownstream`，任一 `SUPERSEDED`／非 `PASS`／`false` ⇒ 不在作废基线上出结论、本批只能 `BLOCKED`（命名缺失输入 + owner + 清除条件），「判据全闭」只作事实、限定条件只能落字段不得写注释；`assets/summary-template.md` 结构基线行加公共 §0「上游闸门核对与本轮 Gate」硬性小节指针（缺节则 Gate 只能记「未验证」，不得 `PASS`）。口径统一指 `../../shared/gate-policy.md` §6 | `issue/WorkFlow/2026-10-10/01`＋`issue/UI-UX-Review/2026-10-10/01` 的**对称补齐**：原仅 ⑦ UI-UX-Review 有核对表承接位，其余评审节点只继承 §6 文字判据 = 声明有、模板没承接的断头落差；用户裁决「先要解决这些问题」 | ✅ 规则已改｜◐ 未经真实场景 fresh 复跑验证 |

| D-11 | 2026-10-18 | 评审修复（audit C 组）：C-06 anti-deadloop 节号校正（严重度定义改指 gate-policy §1）；C-07 known-issue-patterns #6 限定作用域（⑩-后 FTDD 未产出不算缺 EXC）；C-13 撤销 D-05 ③「清 P0 后放行」旧口径（按 anti-deadloop §3：残留 P0⇒BLOCKED、P1⇒仅授权 CONDITIONAL）；C-18 补全「三招」截断句；C-19 流程图改「任务清单 + P0 确认」。 | 来源 `.spec/体系评审/2026-10-18/C-dev.md`；用户要求体系可直接被他机/宿主使用 | ✅ 已确认 |
| D-12 | 2026-10-19 | **评审上下文隔离硬性化**：新增「评审上下文隔离（执行必需）」节 + 主流程步骤 0；单批 1 个 fresh 批次评审子代理并由其直接出汇总，双批 2 个独立批次评审子代理 + 1 个独立汇总子代理（不得一个子代理混做两批）；铁律 4 改「视角隔离 + 独立子代理上下文」；步骤 3/4 标注批次评审者执行、步骤 6 标注汇总归属、步骤 8 复核隔离；错误表 / 资源清单 / 汇总模板 §0.5 / role 模板元数据（评审上下文 + 评审包摘要）/ README 同步 | 用户 2026-10-19 要求评审判断必须发生在隔离上下文，不得在产出/修订同一会话自审（`shared/review-context-isolation.md` + `issue/Skill-Optimizer/2026-10-19/01`） | ✅ 规则已改｜◐ 行为验证待跑 |

## 四、待决问题

无。