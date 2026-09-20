---
name: Prototype-Review
description: 原型评审：对照 PRD 核查页面/载体完整性（防漏 + 防加戏）、文案逐字一致、交互与状态闭环、原型自身实现质量（不查视觉）。浏览器工具为硬前置：任一可用即用于截图存证，全无则报错停用。只审不改，产出四份维度报告 + 汇总 + 单一事实源任务清单；防评审死循环（判据 + P0/P1 冻结 + 复核只验本轮 + 轮次上限 3，超限清 P0 后放行）。触发：评审/走查原型、对齐文案、查页面遗漏、核查闭环。
compatibility: Claude Code / Agent SDK / OpenCode
---

> LEGACY COMPATIBILITY NOTICE: This file preserves historical material. The active Skill, Gate, state, artifact, and evidence rules are defined by `shared/skill-contract.md`, `shared/gate-policy.md`, `shared/anti-deadloop.md`, `shared/artifact-contract.md`, `governance/`, and `.spec/workflow.yaml`.

# Prototype-Review —— 原型评审

> IRON LAW：**只审不改**——严禁改原型 HTML/CSS/JS 与 PRD，唯一产出是 `.spec/原型评审/` 下的报告与清单。
> 定位：以 PRD 为基准审查已生成原型（结构基线），不查视觉精修。

## 一、定位与铁律

**四个评审维度**：

1. **页面与载体完整性**：PRD 规定的页面、弹框、抽屉、页内区块必须落地；PRD 未要求的按钮、提示、区块、装饰元素不得出现（防漏 + 防加戏）。
2. **文案与字段一致性**：页面标题、CTA、提示文案、表格列名、表单标签与 PRD 逐字吻合；不得有多余提示 / 引导文案。
3. **交互与流程闭环**：页面出入口、正向/逆向分支、弹框打开与关闭、空/载/错/满多状态必须通畅闭环。
4. **原型自身实现质量（闭环验证前提）**：查控制台报错、样式穿透 / 错位、层级遮挡、死链、点击无响应——原型坏了，前三项无法验证。**不查**视觉精修、配色、AI 模板感。

**铁律**：

1. **只审不改**：不改原型与 PRD；唯一产出为 `.spec/原型评审/` 下报告与清单。
2. **成因必写**：每条问题结合 PRD 与原型代码给成因（漏读章节、同名歧义、事件未监听、overflow 遮挡）；无法推导标「成因未明」，禁臆造。
3. **方向明确**：每条给修改方向与建议修改方——原型问题 → `Prototype-Design`；PRD 自相矛盾 → `PRD-Design`；双方口径不一 → `双方协同`。
4. **浏览器工具硬前置**：任一可用即用于截图存证（细则见 `references/browser-inspection-guide.md`）；**全部不可用 → 报错停止，不产出任何评审文档**（策略见 `../../shared/browser-policy.md`）。
5. **单一事实源**：全量问题去重后只收口到 `.spec/原型评审/任务清单.md`，初始状态均为 `待确认`。

**适用范围**：适用已生成的低保真原型对照 PRD 走查；不适用评审需求、设计稿、技术方案，也不查视觉精修。

## 二、输入与前置

| 项 | 说明 | 缺失处理 |
|---|---|---|
| PRD 目录（默认 `.spec/PRD/`） | 评审基准 | ⛔ 停下提示 |
| 原型工程（默认 `.spec/原型/`） | HTML + `布局清单.md` + `README.md` | ⛔ 停下提示 |
| 浏览器工具（**硬前置**） | 截图存证 + 点击验证 | 全不可用 → 报错停止 |

有 `PRD速查表.md` 时先读建六大索引，逐字比对按锚点回原文。

**输出**（`.spec/原型评审/`）：`页面与载体完整性评审.md` / `文案与字段一致性评审.md` / `交互与流程闭环评审.md` / `原型自身质量评审.md` / `原型评审汇总报告.md` / `任务清单.md` / `screenshots/`（硬性产出）。

## 三、主流程（6 步）

**1. 资产解析与浏览器预检**：读 PRD（速查表 / overview / NN_xxx）与原型（HTML / 布局清单 / README），缺失即停；按铁律 4 预检浏览器工具并记录走查工具。

**2. 建立映射基准**：从速查表页面功能区块索引与各模块 §3.1 提取页面、交互路径、关键文案；读 `布局清单.md`；产出矩阵 `PRD 功能点 ↔ 原型页面/载体（文件 / Modal ID）`。

**3. 截图走查 + 静态源码审查（双通道互证）**：
- **截图走查（硬性）**：逐页打开原型，对异常 / 缺失 / 不一致处局部截屏存入 `screenshots/`；
- **静态源码审查（并行）**：读 HTML 结构、CSS、JS 交互，以代码行与 DOM 路径为证据；
- 两通道独立完成、互不参考，最后合并比对；只认原型成品与 PRD 原文，不参考生成过程。

**4. 四维对照评审 + 产出四份报告**：按 `references/page-completeness-checklist.md`、`copywriting-consistency-checklist.md`、`interaction-closure-checklist.md`、`prototype-quality-checklist.md` 逐项过筛（每份同时**查漏 + 查多**）；另对照 `references/known-issue-patterns.md`（评审方案例库）过一遍，命中即入相应维度清单。随后按 `assets/dimension-review-template.md` 落盘四份维度报告。

**5. 汇总**：按 `assets/summary-template.md` 聚合四份报告——合并同类、消除重复、归纳跨页面系统性问题、统计 P0/P1/P2。

**6. 任务清单 + 双向沉淀判定 + 归档**：按 `assets/issue-list-template.md` 生成 `任务清单.md`——
- 每条自足可读（出处 + 现象 + 成因 + 修改方向，不依赖原文）、附**修复判据**、标注建议修改方；初始 `待确认`；
- 逐条向用户确认裁决（要改 → `已确认`；不改 → `已忽略` + 理由；不理解即展开说明）；P0/P1 阻断、P2 由用户裁决；
- 复核只验本轮已确认清单，不无限新增同级问题（新发现降 P2 留后续或经同意进下一轮）；
- **双向沉淀判定**：放行后按 `../../shared/anti-deadloop.md` §五 判定（P0 双向必沉）——**A 防复发**：原型问题改 `Prototype-Design`、PRD 口径问题改 `PRD-Design`（记其 CONTEXT D-xx）；**B 检出力**：本 skill `references/known-issue-patterns.md` 按模板加一条（含「检出方法」）。改不了的落 `../../issue/<目标 skill>/<日期>/`（来源=评审闭环，写明双向落点）。判定结果记入汇总报告「沉淀判定」节；
- 交付总结明确剩余待裁决项。
- **问题日志**：归档同时在项目 `.spec/问题日志.md` 台账追加一行索引（日期｜来源｜问题产物｜轮次｜状态｜反哺出口；格式见 skill 源仓库 `../../shared/templates/problem-log-template.md`）。

> 门禁闭环、防评审死循环三招（含轮次上限 3：满 3 轮未收敛 → 强制清 P0 后放行、残留 P1 记遗留）、分级与沉淀的定义见仓库根 `../../shared/anti-deadloop.md`，本 skill 只保留流程参数，不重复定义。

## 四、评审规范

**4.1 严重度分级（只标注，不设门禁）**——P0/P1/P2 定义与处理口径见 `../../shared/anti-deadloop.md` §三，下表为本域典型示例：

| 级别 | 定义 | 处理 | 典型 |
|---|---|---|---|
| P0 致命 | 流程断头、核心页面 / 模态缺失、严重阻碍开发与演示 | 阻塞；修复并通过复核 | 核心审核弹框无入口也无代码；主流程死胡同 |
| P1 重要 | 字段 / 文案严重不符、关键状态缺失、弹框无法关闭 | 必须进任务清单，原则上全修 | 按钮文案写反；必填星号缺失；空 / 异常状态未设计 |
| P2 建议 | 非关键文案润色、次要体验优化 | 记录，由用户裁决 | 提示可精炼；次要入口可优化 |

## 五、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 评审时改原型或 PRD | 只记问题，给方向（铁律 1） |
| 问题无成因 | 结合 PRD 与原型代码剖析（铁律 2） |
| 问题无修改方向 / 修改方 | 按铁律 3 标注 |
| 浏览器不可用仍开工 | 报错停止，不产出文档（铁律 4） |
| 只看异常、不查「多出的内容」 | 四维清单每份都查漏 + 查多 |
| 只走截图、不读源码 | 双通道互证（步骤 3） |
| 四份报告维度混写 | 一维一份，汇总再合并 |
| 把视觉精修当问题 | 本 skill 不查视觉，交 UI-UX-Review |
| 任务清单分散多份 | 单一事实源（铁律 5） |
| 闭环后不沉淀 | 步骤 6 双向沉淀判定，P0 必沉 |

## 六、资源清单

- `references/page-completeness-checklist.md` / `copywriting-consistency-checklist.md` / `interaction-closure-checklist.md` / `prototype-quality-checklist.md`：四维清单（各含查漏 + 查多）
- `references/known-issue-patterns.md`：评审方案例库（闭环沉淀的已知问题模式 + 检出方法）
- `references/browser-inspection-guide.md`：浏览器走查与截图细则
- `assets/dimension-review-template.md` / `summary-template.md` / `issue-list-template.md`
- `../../shared/anti-deadloop.md`、`../../shared/browser-policy.md`（仓库根）：公共约定
- `.spec/原型评审/`：归档目录（含 `screenshots/`）

## 七、运行问题埋点

收尾按 `../../Other/Skill-Optimizer/references/instrumentation-guide.md` 自查上报 `../../issue/Prototype-Review/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `../../Other/Skill-Optimizer/assets/issue-template.md`）。不确定不记，不打断主流程。
