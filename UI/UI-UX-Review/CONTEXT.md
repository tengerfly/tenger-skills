> LEGACY COMPATIBILITY NOTICE: This file preserves historical material. The active Skill, Gate, state, artifact, and evidence rules are defined by `shared/skill-contract.md`, `shared/gate-policy.md`, `shared/anti-deadloop.md`, `shared/artifact-contract.md`, `governance/`, and `.spec/workflow.yaml`.

# CONTEXT.md —— UI-UX-Review 术语与决策记录

> UI-UX-Review 的术语对齐源与决策日志。

## 一、角色与边界

- 人设：资深 UI/UX 评审专家。
- 目标：独立复审设计稿（结构越权/文案不符/规范绕过/渲染不过关），兜底生成方门禁。
- 边界：只审不改；不生成视觉、不写 PRD/前端代码、不跑业务测试；被审对象是视觉稿不是可运行产品。

## 二、术语表

| 术语 | 定义 | 排除 |
|---|---|---|
| 设计稿评审 | 四维独立复审设计稿 | 不是原型评审/内部门禁 |
| 独立复审 | 三源对照 + 真实渲染证据 | 不只做一致性比对 |
| 布局零改动 | 与布局清单逐项一致 | 评审独立执行同源检查 |
| 设计规范 | `.superdesign/design-system.md` 权威、归档副本作对照 | 规范外视觉值即缺陷 |
| 结构级可点击 | 逐入口验 `<a href>`，死元素缺陷 | 不是业务交互测试 |
| 死元素 | 长得像可点但点击无反应 | 静态 chip 不算 |
| 修复判据 | 修到什么表现算过 | 不是修改方向 |
| 防死循环三招 | 判据+冻结+轮次上限 3 | 缺一即可能死循环 |
| 任务清单 | `.spec/设计评审/任务清单.md` 单一源 | 不是维度报告 |

## 三、决策日志

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 09-05 | 全面独立复审（三源+渲染） | 门禁自查有盲区；渲染是差异价值 | ✅ |
| D-02 | 09-05 | 四维切分 + 家族产出范式 | 对齐 Prototype-Review | ✅ |
| D-03 | 09-05 | 只做结构级可点击，不做业务交互 | 视觉稿不是可运行产品 | ✅ |
| D-04 | 09-05 | 命名 UI-UX-Review；产物 `.spec/设计评审/` | 命名一致；接修复闭环零改动 | ✅ |
| D-05 | 09-05 | 浏览器硬依赖 | 不渲染丢核心价值 | ✅ |
| D-06 | 09-05 | 内建埋点 | 全仓一致 | ✅ |
| D-07 | 09-05 | 接入 Workflow 第⑦节点 | 用户整体愿景 | ✅ |
| D-08 | 09-05 | 六大索引枚举对齐 PRD-Design | 术语/同步 P2 | ✅ |
| D-09 | 09-05 | 双通道独立互证；README D 编号同步 | 心法4 评审独立性 | ✅ |
| D-10 | 09-05 | rendered-quality 加 Nielsen 十项体验核对 | 补主观体验参照系 | ✅ |
| D-11 | 09-09 | 体检修复 2 项：反 AI 味 12 条维度归属统一第 3 维；三招/浏览器策略收口 shared 引用（SKILL 铁律 4 + browser-inspection-guide 收口重写）/埋点统一 + issue-list 薄壳化（R9） | 全仓冗余专项体检（用户裁决全量修复 + R9 评审模板参数化） | ✅ |
| D-12 | 09-09 | 终检修复 1 项：§六防死循环差异句删 ../../shared/anti-deadloop.md 复述部分 | 全仓终检（冗余专项体检修复后复审，用户裁决全修） | ✅ |
| D-13 | 09-10 | 门禁闭环改造 + 双向沉淀：①步骤 7 改「任务清单 + 双向沉淀判定 + 归档」（A 改 ../UI-UX-Design/Prototype-Design/PRD-Design 防复发；B 本 skill `references/known-issue-patterns.md` 加模式含检出方法）；②超限动作由「停下交用户」改「强制清 P0 后放行，残留 P1 记遗留」；③步骤 4 补案例库对照；④新增案例库 + README/description 同步 | 用户要求评审循环门禁 + 问题双向沉淀反哺 skill | ✅ |
| D-14 | 09-10 | 模式③ 优化：步骤 7 原约 400 字单条混装「任务清单 + 门槛 + 确认 + 沉淀」→ 拆为步骤 7「任务清单 + 归档」与步骤 8「双向沉淀判定」，流程 7→8 步；沉淀段压缩为薄壳（A/B 落点 + 指向 `../../shared/templates/known-issue-patterns-template.md`）；description 补「超限清 P0 后放行」| 自检发现单条过长、与 shared 公共定义重复 | ✅ |
| D-15 | 09-10 | **结构重构（统一骨架）**：章节 7 → 7（内部重整）——§一 定位与铁律（四维目标 + 铁律 6 条）；§二 输入与前置（输入表含缺失处理 + 输出清单）；§三 主流程 8 步；§四 评审规范（4.1 严重度 + **4.2 与内部门禁的关系**，原 §六「防死循环」并入主流程注释）；**§五 错误表（新增，此前缺失）**；**§六 资源清单（新增，此前缺失）**；§七 埋点。old-vs-new 审计：原条目全部有归属，且补上缺失两节 | 用户要求：整理成顺畅流程（Skill-Optimizer 全量体检） | ✅ |
| D-16 | 09-15 | 全仓一致性纠偏：输入表补低保真原型 HTML（区块级结构基准，设计任务清单仅作索引不作独立基准）；design-system 基准改「归档副本即交付基准」；summary-template 补沉淀判定节 + 编号改 SUM-xx；轮次口径改「强制清 P0 后放行」；资源清单补 browser-inspection-guide | 四代理并行七维体检；与 ../../shared/baseline-terms.md 对齐 | ✅ |
| D-17 | 09-17 | 检出力补强：visual-spec-consistency-checklist「组件与资源」加「动效合规」检项（时长对 §6 档、曲线取 §7 token、无 ease-in、常规 UI <300ms、弹层 / 抽屉类按档、无答不出目的的动画；口径同设计门禁 §二）——补齐「设计门禁查动效、评审方不查」的检出力落差 | Skill-Optimizer 模式④体检发现（配合 UI-UX-Design D-28/D-29） | ✅ |
| D-18 | 10-08 | 跨页宽度不变量落**主流程强制位 + 承接位**（承接 3c1030c 的规则补录）：①步骤 3 加 REQUIRED 逐页三值实测、步骤 4 加「无实测表只能标未验证」判据、步骤 7 加证据回勾自检、§二 输出加「跨页宽度实测表」、§五 错误表 +1 行（规则空转）；②§七 量测产物固定表头，删除全仓不存在的 `tools/width-parity-probe.mjs` 引用改「按需现写」；③模式 3 出处 ⑨→⑦（权威表 `Workflow/references/legacy-pipeline.md`：⑦=设计稿评审、⑨=前端技术方案）；④二次窄列三类豁免统一为全站唯一枚举，跨 skill 引用补 `../../UI-UX-Design/references/self-write-sop.md` 全路径；⑤模式 5 标注已落主流程、出处「三条」改「§七 5 条规则」；⑥dimension-review / summary 两模板加实测表与证据出处节；⑦README 第四维描述补跨页实测 | `issue/UI-UX-Review/2026-10-08/01`＋`issue/UI-UX-Design/2026-10-08/01`（Skill-Optimizer 模式④七维体检 13 项）；判据=主流程有动作 · 模板有承接位 · 两端门禁同一判据 | ✅ |

## 四、待决问题

Q1（页面还原度归属）已解决：独立成 Fidelity-Review（开发后 vs 设计稿），与本 skill 阶段不同、边界不重叠。