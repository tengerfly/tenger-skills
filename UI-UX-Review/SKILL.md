---
name: UI-UX-Review
description: UI/UX 设计稿评审。依据 PRD、布局清单、design-system 对设计稿做四维独立复审：载体与结构零改动（防漏+防加戏）、文案与字段一致、视觉规范一致（token 出处）、视觉呈现与可交付质量（真实渲染 + 结构级可点击性）。UI-UX-Design 内部门禁的第三方独立兜底：只审不改，输出四份维度报告 + 汇总 + 单一事实源任务清单至 `.spec/设计评审/`。浏览器工具硬依赖：任一可用即渲染截图存证，全无则报错停用。防死循环：判据 + P0/P1 冻结 + 复核只验本轮 + 轮次上限 3（超限清 P0 后放行）。触发：评审/走查设计稿、视觉稿核验、对齐 PRD/布局清单、查视觉规范执行。
compatibility: Claude Code / Agent SDK / OpenCode
---

# UI-UX-Review —— UI/UX 设计稿评审

> IRON LAW：**只审不改**——禁改设计稿 HTML、design-system、PRD、布局清单；唯一产物是 `.spec/设计评审/` 下文件。
> 定位：对 UI-UX-Design 产出的设计稿做**独立第三方复审**，兜底其内部门禁自查盲区。只查问题、找成因、给方向。

## 一、定位与铁律

**四个评审维度**：

1. **载体与结构零改动**：对照布局清单，独立页面、弹框、抽屉、区块、元素、跳转逐项一致（防漏）；无出处的区块 / 按钮 / 提示 / 装饰一律不得出现（防加戏）。结构不对 = 视觉阶段越权改布局，打回。
2. **文案与字段一致性**：对照 PRD / 布局清单逐字比对标题、CTA、列名、标签、提示语；不得自行添加多余文案。
3. **视觉规范一致性**：对照 `.spec/设计稿/design-system.md`（**归档副本即交付基准**；`.superdesign/design-system.md` 为 CLI 工作源，仅需追溯原文时对照）——所有视觉值（色值 / 字号 / 字重 / 间距 / 圆角 / 阴影 / 组件 / 图标）必须有 token 出处，无规范外值；反 AI 味 12 条目检（清单见 `references/visual-spec-consistency-checklist.md`）。
4. **视觉呈现与可交付质量**：真实渲染设计稿 HTML——规范是否落地、逐入口做**结构级可点击性**验证（真实 `<a href>` 或等价触发；像按钮却点不动 = 缺陷）、控制台报错 / 死链 / 遮挡 / 资源加载失败、关键缺陷截图。
   - 边界：不验真实业务逻辑 / 数据 / 弹框开合逻辑；可点击性只到「入口存在且可点、href 去向与站点地图一致」。

**铁律**：

1. **只审不改**：唯一产物为 `.spec/设计评审/` 下文件。
2. **成因必写**：每条结合对照源与 HTML 剖析（漏读区块、token 被绕过、直编改坏 href、弹框只做静态视觉）；无法推导标「成因未明」，禁臆造。
3. **方向明确**：设计稿问题 → `UI-UX-Design`；布局清单与 PRD 冲突 / 漏载体 → `Prototype-Design`；PRD 自相矛盾 → `PRD-Design`；口径不一 → `双方协同`。
4. **浏览器工具硬前置**：任一可用即渲染截图 + 点击验证；**全无 → 报错停止，不产出评审文档**（策略见 `shared/browser-policy.md`）。
5. **单一事实源**：全量问题去重后只收口 `任务清单.md`，初始全部 `待确认`。
6. **第三方独立兜底**：不采信 UI-UX-Design 门禁的「✅ 已通过」；只认对照源 + 真实渲染独立复核。

**适用范围**：适用已归档的设计稿复审；不适用评审 PRD / 原型 / 技术方案，也不改设计稿。

## 二、输入与前置

| 项 | 说明 | 缺失处理 |
|---|---|---|
| PRD（有速查表先建索引） | 需求基准 | ⛔ 停下提示 |
| 布局清单（载体级） + **低保真原型 HTML（区块级）** | **结构基准**：布局清单定载体、原型定区块实物（结构真相源见 `shared/baseline-terms.md`） | ⛔ 停下提示 |
| `.spec/设计稿/design-system.md`（**归档副本即交付基准**） | 视觉规范基准（`.superdesign/design-system.md` 为 CLI 工作源，仅追溯时对照） | ⛔ 停下提示 |
| 设计稿工程（HTML + README） | 被审对象 | ⛔ 停下提示 |
| 浏览器工具（**硬依赖**） | 渲染截图 + 点击验证 | 全无 → 报错停止 |

**输出**（`.spec/设计评审/`）：四份维度报告、`设计稿评审汇总报告.md`、`任务清单.md`（`待确认` → `已确认` → `已修复`/`已忽略`）、`screenshots/`（硬性）。

## 三、主流程（8 步）

1. **资产解析与浏览器预检**：读取上表输入，缺失即停；按铁律 4 预检并记录工具。
2. **建立映射基准**：提取 PRD 页面 / 文案 / 跳转、布局清单载体划分、design-system token 速查；产出矩阵 `PRD 功能点 / 布局载体 ↔ 设计稿页面（draftId 版本）`。
3. **渲染走查 + 静态源码审查**：静态服务渲染逐页截图（异常处截入 `screenshots/`）；逐入口点击验证；静态读 HTML 结构 / `<a>` / CSS token / 脚本作证据。两条通道独立完成、最后合并互证；**不参考生成过程，不轻信内部门禁**。
4. **四维对照评审**：按 `references/layout-freeze-checklist.md`、`copywriting-consistency-checklist.md`、`visual-spec-consistency-checklist.md`、`rendered-quality-checklist.md` 逐条过筛（每份含**查漏 + 查多**）；另对照 `references/known-issue-patterns.md`（评审方案例库）过一遍，命中即入相应维度清单。
5. **四份维度报告**：按 `assets/dimension-review-template.md` 落盘四份报告。
6. **汇总**：按 `assets/summary-template.md` 合并去重、归纳跨页面共性问题（如整批 token 偏差）、统计 P0/P1/P2。
7. **任务清单 + 归档**：按 `assets/issue-list-template.md` 生成任务清单——每条自足可读（出处 + 现象 + 成因 + 方向）、附修复判据、状态 `待确认`、标注修改方；P0/P1 阻断、P2 由用户裁决；逐条确认（要改 → `已确认`；不改 → `已忽略` + 理由）；复核只验本轮清单，不无限新增。**问题日志**：归档同时在项目 `.spec/问题日志.md` 台账追加一行索引（日期｜来源｜问题产物｜轮次｜状态｜反哺出口；格式见 skill 源仓库 `shared/templates/problem-log-template.md`）。
8. **双向沉淀判定**：放行后按 `shared/anti-deadloop.md` §五 执行——**A 防复发**：设计稿问题改 `UI-UX-Design`、布局 / 载体问题改 `Prototype-Design`、PRD 口径问题改 `PRD-Design`（记其 CONTEXT D-xx）；**B 检出力**：本 skill `references/known-issue-patterns.md` 按模板加一条（含「检出方法」）。改不了的落 `issue/<目标 skill>/<日期>/`（来源=评审闭环，写明双向落点）。判定结果记入汇总报告「沉淀判定」节。

> 门禁闭环、防评审死循环三招（含轮次上限 3：满 3 轮未收敛 → 强制清 P0 后放行、残留 P1 记遗留）、分级与沉淀的定义见仓库根 `shared/anti-deadloop.md`，本 skill 只保留流程参数，不重复定义。反复不收敛且暴露方法论问题 → 上报 `issue/`，交 Skill-Optimizer。

## 四、评审规范

**4.1 严重度分级（只标注，不设门禁）**——P0/P1/P2 定义与处理口径见 `shared/anti-deadloop.md` §三，下表为本域典型示例：

| 级别 | 定义 | 处理 | 典型 |
|---|---|---|---|
| P0 | 结构错位、主流程入口不可点、视觉严重偏离规范、核心文案大面积冲突 | 阻断；修复并通过复核 | 布局规定的弹框无入口；跳转全死链；整页配色另起炉灶 |
| P1 | 局部结构偏差、文案逐字不符、规范局部未执行、单入口死元素、控制台报错 | 必须进任务清单，原则上全修 | 文案不同字；少一张统计卡；按钮无 href |
| P2 | 非关键润色、次要视觉建议、边缘渲染瑕疵 | 记录，由用户裁决 | 留白可斟酌；提示可精炼 |

**4.2 与内部门禁的关系**：本 skill 是 UI-UX-Design 内部门禁的**第三方兜底**——不采信其自查结论，独立复核；发现的问题照常入清单，按铁律 3 归指派修改方。

## 五、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 评审时改设计稿 / 对照源 | 只记问题，给方向（铁律 1） |
| 采信内部门禁「已通过」 | 独立复核（铁律 6） |
| 问题无成因 / 无方向 | 按铁律 2、3 补齐 |
| 只查漏、不查加戏 | 四维清单每份都查漏 + 查多 |
| 只渲染截图、不读源码 | 双通道互证（步骤 3） |
| 浏览器不可用仍开工 | 报错停止 |
| 把业务逻辑 / 数据当设计问题 | 本 skill 只到结构级可点击性 |
| 任务清单分散 | 单一事实源（铁律 5） |
| 四份报告维度混写 | 一维一份，汇总再合并 |
| 闭环后不沉淀 | 步骤 8 双向沉淀判定，P0 必沉 |

## 六、资源清单

- `references/layout-freeze-checklist.md` / `copywriting-consistency-checklist.md` / `visual-spec-consistency-checklist.md` / `rendered-quality-checklist.md`：四维清单
- `references/browser-inspection-guide.md`：浏览器渲染走查与点击验证细则（步骤 3/4 用）
- `references/known-issue-patterns.md`：评审方案例库（闭环沉淀的已知问题模式 + 检出方法）
- `assets/dimension-review-template.md` / `summary-template.md` / `issue-list-template.md`
- `shared/anti-deadloop.md`、`shared/browser-policy.md`、`shared/baseline-terms.md`（仓库根）：公共约定
- `.spec/设计评审/`：归档目录（含 `screenshots/`）

## 七、运行问题埋点

收尾按 `Skill-Optimizer/references/instrumentation-guide.md` 自查上报 `issue/UI-UX-Review/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `Skill-Optimizer/assets/issue-template.md`；含 Superdesign / UI-UX-Design 侧）。不确定不记，不打断主流程。
