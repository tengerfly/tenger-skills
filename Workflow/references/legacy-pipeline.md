> LEGACY COMPATIBILITY NOTICE: This file preserves historical material. The active Skill, Gate, state, artifact, and evidence rules are defined by `shared/skill-contract.md`, `shared/gate-policy.md`, `shared/anti-deadloop.md`, `shared/artifact-contract.md`, `governance/`, and `.spec/workflow.yaml`.

﻿---
name: Workflow
description: 全流程开发编排。把 15 个链上专业 Skill 串成链（竞品→PRD→评审→原型→UI→开源调研→方案→开发→代码评审→测试；14 个编号节点 + ⑧⑨ 技术方案前的 OSS-Radar 同域调研步），每个节点都可作起点；默认从 ① 跑 0-1 全流程，已有 PRD 则从 ④ 起跑，只点名某节点则只跑该节点并停下。每个「产物 ⇄ 评审」节点内成门禁闭环：P0/P1 清零才进下一节点（满 3 轮清 P0 后放行）；闭环问题双向沉淀反哺 skill。每完成一节点停下等用户决定（继续/跳过/重做/停）。触发：从零开发、按流程开发、根据 PRD 生成原型/走后续、按方案写代码、评审代码、测试项目、继续、接着做。
compatibility: Claude Code / Agent SDK / OpenCode
---

# 全流程开发编排 Skill

> 只做三件事：记账（PIPELINE.md）、调度（按序启用子 skill）、守门（前置检查 + 门禁闭环判定 + 沉淀记账）。干活的是 15 个**链上**子 skill（14 个编号节点 + ⑧⑨ 前置的 OSS-Radar 同域调研步；链外 `Fidelity-Review` / `Bug-Fix` / `Testing`（备用）按需协同，见 §八）。
> 原则：一条链，任意起点，逐步推进，产物 ⇄ 评审成环，收敛才下行，随时可停。
> 链外修复闭环：`Bug-Fix`（bug 诊断 + 修复委托）不入主链、独立触发；⑭ 测试发现的可运行性问题可转 `Bug-Fix` 走「定位→方案→开发→回归」修复闭环。

## 一、核心模型

**角色**：技术项目经理 / Delivery Lead。**目标**：一句话从任意节点起跑，随时决定继续。**边界**：只调度、记账、守门；交付物由子 skill 产出。

```
① 竞品分析
→ ② PRD 设计 ⇄ ③ PRD 评审
→ ④ 原型设计 ⇄ ⑤ 原型评审
→ ⑥ UI/UX 设计 ⇄ ⑦ UI/UX 评审
→ ⑧ 后端技术方案 ⇄ ⑩-后 技术方案评审（后端）
→ ⑨ 前端技术方案 ⇄ ⑩-前 技术方案评审（前端）
→ ⑪ 后端开发 ⇄ ⑬-后 代码评审（后端）
→ ⑫ 前端开发 ⇄ ⑬-前 代码评审（前端 ∥ 页面还原度）
→ ⑭ 测试
```

- `⇄` = **门禁闭环**：产物 → 评审 → 修复 → 复核，P0/P1 清零才进下行；满 3 轮清 P0 后强制放行（定义见仓库根 `shared/anti-deadloop.md`）。
- `∥` = **并行评审**：⑬-前 由 Code-Review（前端视角）与 Fidelity-Review 并行审，问题合并进同一份任务清单、共用循环与轮次。
- ⑩ 与 ⑬ 按端拆两批执行（写一个审一个）：⑧ 清零才起 ⑨；⑨ 清零才起 ⑪；⑪ 清零才起 ⑫；⑫ 清零才起 ⑭。
- **⑧⑨ 前置调研步（OSS-Radar）**：写技术方案前先跑 `OSS-Radar`（项目泳道，按 PRD 关键词定向同域开源项目，看同类项目怎么做）→ 产出 `.spec/开源情报/` → 再写 TDD/FTDD；⑨ 复用 ⑧ 轮报告或按前端视角补一轮；快速档或用户明确跳过时留痕放行。

| 参数 | 怎么定 | 默认 |
|---|---|---|
| 起点 | 用户点名，或按 `.spec/` 已有产物推断 | ① |
| 终点 | 用户点名；不点名 = 只跑起点 | 起点本身 |
| 跳过 | 用户随时说「跳过 XX」 | 无 |

推进：完成节点（含其门禁闭环收敛）→ 回填 PIPELINE → 交接摘要 → 停下等用户（继续 / 跳过 X / 重做 / 就到这）。用户明确「一路做到测试」才连续跑，中途仍在评审节点停。

## 二、节点速查

前置缺失即阻塞。环境依赖（级别与动作）：⑤⑦⑨⑫ 与 ⑬-前（还原度审查）**硬依赖**（全无报错停），⑭（auto-test）**分层依赖**——L0/L1 确定性门禁与契约冒烟无浏览器可跑，L2 视觉 E2E 硬依赖浏览器；⑧⑩ **软检测**；检测顺序、两级行为与报错文案见仓库根 `shared/browser-policy.md`，此处不重复定义。⑥ UI/UX 设计 = Superdesign 底座**硬依赖**（CLI + 授权 + SOP 可读，缺一阻塞，浏览器仅为截图可选增强）。

| # | 节点 | 调用 | 前置（缺失阻塞） | 产出 |
|---|---|---|---|---|
| ① | 竞品分析 | Competitive-Analysis | 用户想法 | `.spec/<主题>竞品分析/` |
| ② | PRD 设计 | PRD-Design | 用户想法（竞品报告可选） | `.spec/PRD/V1/` |
| ③ | PRD 评审 | PRD-Review ⇄ PRD-Design（闭环） | PRD | `.spec/需求评审/` |
| ④ | 原型设计 | Prototype-Design | PRD（③ 已放行） | `.spec/原型/` |
| ⑤ | 原型评审 | Prototype-Review ⇄ ④/②（闭环） | PRD + 原型 | `.spec/原型评审/` |
| ⑥ | UI/UX 设计 | UI-UX-Design | PRD + 布局清单 + 原型 | `.spec/设计稿/` |
| ⑦ | UI/UX 评审 | UI-UX-Review ⇄ ⑥/④/②（闭环） | PRD + 布局清单 + 设计稿 | `.spec/设计评审/` |
| ⑧ | 后端技术方案 | Backend-Tech-Design | PRD（原型/设计稿可选）+ **同域开源调研（OSS-Radar 项目泳道，快速档/用户确认可跳过留痕）** | `.spec/TDD/V1/` |
| ⑩-后 | 技术方案评审（后端） | Tech-Review（后端视角）⇄ ⑧（闭环） | TDD + PRD | `.spec/技术方案评审/` |
| ⑨ | 前端技术方案 | Frontend-Tech-Design | PRD + TDD + ⑩-后已放行 + 开源调研（复用 ⑧ 轮或补前端轮） | `.spec/FTDD/V1/` |
| ⑩-前 | 技术方案评审（前端） | Tech-Review（前端视角）⇄ ⑨（闭环） | FTDD + PRD | `.spec/技术方案评审/` |
| ⑪ | 后端开发 | Backend-Dev | TDD + ⑩ 已放行 | 代码 + PROJECT.md + PLAN.md |
| ⑬-后 | 代码评审（后端） | Code-Review（后端视角）⇄ ⑪（闭环） | 后端代码 | `.spec/代码评审/` |
| ⑫ | 前端开发 | Frontend-Dev | FTDD + ⑬-后已放行（另需输入：设计稿=**视觉基准**、原型=**结构基线**；设计稿缺少不阻塞，但须明示视觉基准降级） | 代码 + PROJECT.md |
| ⑬-前 | 代码评审（前端 ∥ 还原度） | Code-Review（前端视角）∥ Fidelity-Review ⇄ ⑫（闭环） | 前端代码 + 设计稿（视觉唯一应然；缺失则降级回退原型并明示） | `.spec/代码评审/` |
| ⑭ | 测试 | auto-test | 可运行代码 + PRD + ⑬ 已放行 | `.spec/auto-test/`（L0-L4 分层报告 + 覆盖率门禁 + 修复任务卡与 fresh-agent 回归闭环；有设计稿时 L2 内嵌 `Fidelity-Review` 还原检查；发现可运行性问题 → 转 `Bug-Fix`） |

下表按**执行顺序**排列（⑩/⑬ 分端两批后编号不单调，一律以本表顺序为准）。

**硬串行**：⑧ → ⑩-后 → ⑨ → ⑩-前（FTDD 须读 TDD 接口契约，且 TDD 先过审）；⑪ → ⑬-后 → ⑫ → ⑬-前（前端按后端真实契约对接，且后端代码先过审）。

## 三、起点确定

**用户点名**：从零开发/按流程开发 → ①→⑭；写 PRD → ②（可 +③）；有 PRD 出原型 → ④；评审原型 → ⑤；生成设计稿 → ⑥；评审设计稿 → ⑦；有 PRD 走后续 → ④→⑭；写技术方案 → 先 OSS-Radar 同域调研再 ⑧（含 ⑩-后）；按方案写代码 → ⑪（含 ⑬-后）；评审代码 → ⑬；测试项目/还原度 → ⑭。

**自动推断（需确认）**：无产物 → ①；有 PRD 无原型 → ④；有 PRD+原型未评审 → ⑤；已评审无设计稿 → ⑥；有设计稿未评审 → ⑦；无 TDD → ⑧；有 TDD 未过审 → ⑩-后；有 TDD 无 FTDD → ⑨；有 TDD+FTDD 未过审 → ⑩-前；有 TDD+FTDD 无代码 → ⑪；有后端无前端 → ⑫；代码齐未评审 → ⑬。

推断后必须向用户确认建议起点。设计稿可选：用户说不需要即标 ⑥⑦ `已跳过`，从 ⑧ 起。

## 四、调度规程

**启动**：读项目根 `.spec/PIPELINE.md`——不存在 → 按 `assets/pipeline-template.md` 新建并定起点终点；存在 → 从「当前节点」续跑。启动必问：项目根目录、起点（点名优先，否则推断后确认）、终点（不指定 = 只跑起点）。续跑时必读「遗留问题」段：门禁强制放行残留的 P1 是否需另行处理。

**执行一个节点**：

1. 前置检查：核实产物实际存在，缺失阻塞；门禁节点的前置含「上游门禁已放行」。
2. 播报节点与调用 skill。
3. 读取 `<skill-dir>/SKILL.md` 全文按其流程执行。
4. 产出检查：产物未落盘则阻塞。
5. **门禁节点按 §5 执行闭环**（评审 → 裁决 → 回退 → 复核 → 放行 → 沉淀）。
6. 回填 PIPELINE（进度 + 门禁轮次 + 门禁结果 + 交接记录 + 沉淀痕迹）。
7. 输出交接摘要并停下等用户。

子 skill 目录：优先同级 `../X/SKILL.md`；找不到问用户并记入 PIPELINE。

**交接摘要**：

```
✅ N. 节点已完成
产出物：<路径>
给下一节点的输入：<该读什么>
遗留与待确认：<开放问题>
门禁闭环：轮次 N · 放行结论 · 沉淀 <当场改 {{skill}} D-xx｜入池 issue/...>
PIPELINE：<路径>
—— 回复「继续」/「跳过 X」/「重做」/「就到这」
```

**阻塞格式**：

```
⛔ N. 节点 前置缺失
缺失：<路径/文件>
建议：<先跑 X / 手动指定 / 换起点>
```

## 五、门禁闭环与放行（③⑤⑦⑩⑬）

评审 skill 只审不改、不设门禁；**循环推进与放行判定由本编排负责**，规则定义见仓库根 `shared/anti-deadloop.md`（§一 门禁闭环 / §二 上限 3 / §五 沉淀）。

**闭环模型**：

```
产物完成 → 评审 → 任务清单（待确认）→ 用户逐条裁决
→ P0/P1 有未清 → 回退修改方修复 → 回填「已修复」→ 重跑评审（只验本轮）
→ 清零且复核通过 → 放行 → 进入下一节点
→ 沉淀判定（P0 必沉）→ 当场改产出方 skill / 入 issue 池
```

**守门规则**：

- **放行判据**：P0 全 `已修复` + P1 全 `已修复`（`已忽略` 须有用户确认的理由）+ 复核通过；P2 只记录、留后续，**不阻塞放行**。
- **上限 3**：同批「修复 → 复核」满 3 轮仍未收敛 → 先**强制清零 P0**，再**直接放行**；残留 P1 记入 PIPELINE「遗留问题」，留痕并告知用户。
- **未放行不得起下游**：门禁节点的下游在门禁结果非 `已放行/强制放行` 前一律阻塞。

**门禁点表**：

| 门禁点 | 产物方（修改方） | 评审 skill | 任务清单 |
|---|---|---|---|
| ③ | PRD-Design | PRD-Review | `.spec/需求评审/任务清单.md` |
| ⑤ | Prototype-Design；PRD 冲突 → PRD-Design | Prototype-Review | `.spec/原型评审/任务清单.md` |
| ⑦ | UI-UX-Design；布局 → Prototype-Design；PRD → PRD-Design | UI-UX-Review | `.spec/设计评审/任务清单.md` |
| ⑩-后 | Backend-Tech-Design | Tech-Review（后端视角） | `.spec/技术方案评审/任务清单.md` |
| ⑩-前 | Frontend-Tech-Design | Tech-Review（前端视角） | 同上 |
| ⑬-后 | Backend-Dev | Code-Review（后端视角） | `.spec/代码评审/任务清单.md` |
| ⑬-前 | Frontend-Dev | Code-Review（前端视角）∥ Fidelity-Review | 同上（还原度问题标来源） |

修改方 skill 内含清单检测与回填，编排器只指定入口。门禁点可跳过（用户指令直接跳，PIPELINE 标 `已跳过` + 原因）。

**资产五门禁（对接外部 AI 知识库 asset-library）**：涉及功能实现的任务，在既有门禁外加验五项——① **检索门禁**：候选分析完成（asset-needs/候选记录存在）；② **选择门禁**：selected/rejected/unresolved 三类齐备；③ **实现门禁**：asset-usage 记录实际使用版本（与锁定版本有偏差须有 deviation 说明）；④ **验证门禁**：证据可定位（命令/结果/截图）；⑤ **沉淀门禁**：Case / Pattern Candidate / 更新既有 / 反模式 四出口判断完成，**含查重防冗余（硬性条件）**——库内已有近似资产 → 一律走「更新既有 / 兼容性适配」出口，禁新建并列冗余资产；确需新建须 asset-gap 差异说明并经用户确认。项目侧状态记 `.spec/<feature>/pipeline-state.yaml`（模板在组件库 `templates/project-side/`）；双状态机分开推进：项目任务态（REQUIREMENT→…→USAGE_RECORDED）与资产变更态（DRAFT→…→RETIRED）。组件库位置：`D:\project\agent-project\skills-knowledge\asset-library\`（调度侧引用层与映射表 = 仓库根 `skill-knowledge/`，资产变更时双仓同步更新映射表）。

**分端与并行**：

- ⑩-后 放行 → 才起 ⑨；⑩-前 放行 → 才起 ⑪；⑬-后 放行 → 才起 ⑫；⑬-前 放行 → 才起 ⑭。
- ⑬-前 内：Code-Review（前端视角）与 Fidelity-Review **并行**，两侧问题合并进**同一份** `.spec/代码评审/任务清单.md`（还原度问题标「来源=Fidelity-Review」），共用轮次计数与放行判定；回退方统一为 Frontend-Dev。**还原度判定基准：视觉以设计稿为唯一应然、结构对原型**（双基准见 `shared/baseline-terms.md`）；有设计稿却只与原型比对视觉 = 无效还原结论。
- **并行派发四要素**（同一响应内发多个调用 = 并行）：① 具体范围 ② 明确目标 ③ 约束（不得改范围外） ④ 期望产出。范围过宽、无上下文、无约束、产出含糊 = 派发无效。
- **并行结果必须收口验证**：读每份产出 → 查**冲突**（是否改了同一处 / 结论互斥）→ 跑一次**全量**复核 → **抽查**（并行评审者会犯系统性错误，不能全量采信；结论须主线独立复核，见 `shared/evidence-before-claims.md`）。

**沉淀反哺（双向）**：门禁放行后按 `shared/anti-deadloop.md` §五 判定（**P0 双向必沉**）——**A 防复发**：改产出方 skill 的防复发规则（错误表加行 / references / Gate 预检项），记其 CONTEXT D-xx；**B 检出力**：改发现问题的那一个评审 skill 的 `references/known-issue-patterns.md` 加一条（含「检出方法」）。**当场沉淀优先**（成因明确、改动增量 → 直接改 A/B 两个 skill + 同步部署副本）；改不了的落 `issue/<目标 skill>/<日期>/`（来源=评审闭环，写明双向落点）交 Skill-Optimizer 提炼。PIPELINE 记沉淀痕迹（A 落点 + B 落点 + 入池路径）。

**运行期信号（正向循环第二入口）**：已接入日志/监控基建的项目（server-log 统一日志 / server-monitor 后端监控 / web-monitor 前端监控）在开发与运行中记录的问题，是评审闭环之外的问题来源——回流路径：**日志/监控记录 → `Bug-Fix` 诊断（根因 Gate → 委托方案/开发/回归修复闭环）→ 有预防价值的错误模式沉淀 `bug-patterns/` 池 / skill 方法论问题入 `issue/` 池 → `Skill-Optimizer` 模式③提炼反哺 skill 或对应项目修复**。两类入口（门禁评审 / 运行日志监控）最终汇入同一组池，构成「开发 → 记录 → 修复 → 沉淀 → skill 进化 → 下一项目受益」的正向循环。

**流程裁剪判据**：是否保留某关卡取决于其对冲的模型短板是否仍存在；模型越强流程越轻（可跳过低价值中间环节、保留讨论与最终验收），模型弱或高风险改动时关卡从重。裁剪由用户裁决。

## 六、PIPELINE.md

- 路径：被开发项目根 `.spec/PIPELINE.md`；模板 `assets/pipeline-template.md`；**唯一写入方是本 skill**。
- 作用：跨会话续跑唯一依据。只记本次路径节点，核心四段：本次路径（起点 / 终点 / 序列 / 跳过）、进度（状态 + 门禁轮次 + 门禁结果 + 产物路径）、交接记录（含门禁闭环与沉淀）、遗留问题。

## 七、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 编排器代写业务文档 | 只调度 |
| 凭记忆判断进度 | 先读 PIPELINE |
| 节点完自动往下跑 | 停下等用户 |
| 点名单节点却跑全链 | 终点未定 = 只跑起点 |
| 前置缺失造占位继续 | 阻塞提示 |
| P0/P1 未清放行 | 门禁闭环未收敛不放行 |
| 满 3 轮无限重试 | 强制清 P0 后放行，残留 P1 记遗留 |
| TDD/FTDD 或前后端并行 | 写一个审一个：⑧ 清零起 ⑨、⑪ 清零起 ⑫ |
| ⑩⑬ 合并一次性审 | 分端两批：⑩-后/⑩-前、⑬-后/⑬-前 |
| 前端代码评审漏还原度 | ⑬-前 = Code-Review（前端）∥ Fidelity-Review |
| 有设计稿却按原型判视觉还原 | 视觉唯一应然 = 设计稿；原型只判结构（`shared/baseline-terms.md`） |
| 并行结果直接采信 | 收口验证：查冲突 + 跑全量 + 抽查 |
| 闭环问题不沉淀 | 每闭环做沉淀判定，P0 双向必沉 |
| 未调研同类项目直接写方案 | ⑧ 前先跑 OSS-Radar（快速档/用户确认可跳过须留痕） |
| 组件库已有近似资产仍新建并列组件 | 兼容性适配优先 / 「更新既有」出口；新建须 asset-gap + 用户确认（防冗余硬性条件） |
| 沉淀改结构 / 改被审产物 | 只做增量防复发规则；结构性问题入池 |
| 猜子 skill 路径 | 询问并记入 PIPELINE |
| 起点未确认开跑 | 推断起点必须确认 |
| 擅自加设计变体 / 花钱 | 等用户裁决 |

## 八、资源清单

- `assets/pipeline-template.md`
- 同级子 skill：Competitive-Analysis、PRD-Design、PRD-Review、Prototype-Design、Prototype-Review、UI-UX-Design、UI-UX-Review、OSS-Radar（⑧⑨ 前置同域调研）、Backend-Tech-Design、Frontend-Tech-Design、Tech-Review、Backend-Dev、Frontend-Dev、Code-Review、auto-test（⑭ 测试节点）
- 链外（不入主链编号，独立触发）：`Fidelity-Review`（还原验收；⑭ auto-test L2 内嵌 + ⑬-前 并行）、`Bug-Fix`（修复闭环，承接 ⑭ 发现的可运行性问题与运行期日志/监控信号）、`Testing`（传统项目测试·人工走查备用，源码保留，主链测试节点已由 auto-test 接替）
- 公共约定：`shared/anti-deadloop.md`（门禁闭环 / 上限 3 / 分级 / 沉淀）、`shared/browser-policy.md`（浏览器两级策略 / 检测顺序 / 报错文案）、`shared/baseline-terms.md`（双基准术语）、`shared/evidence-before-claims.md`（取证口径）
- 产物归档：被开发项目 `.spec/`；竞品分析产物 `.spec/<主题>竞品分析/`

## 九、运行问题埋点

收尾按 `Other/Skill-Optimizer/references/instrumentation-guide.md` 自查上报 `issue/WorkFlow/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `Other/Skill-Optimizer/assets/issue-template.md`；调度/守门/PIPELINE 状态侧）。不确定不记，不打断主流程。

