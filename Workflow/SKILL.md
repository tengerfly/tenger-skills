---
name: Workflow
description: 全流程开发编排。把 14 个专业 Skill 串成链（竞品→PRD→评审→原型→UI→方案→开发→代码评审→测试），每个节点都可作起点；默认从 ① 跑 0-1 全流程，已有 PRD 则从 ④ 起跑，只点名某节点则只跑该节点并停下。每完成一节点停下等用户决定（继续/跳过/重做/停）。触发：从零开发、按流程开发、根据 PRD 生成原型/走后续、按方案写代码、评审代码、测试项目、继续、接着做。
compatibility: Claude Code / Agent SDK / OpenCode
---

# 全流程开发编排 Skill

> 只做三件事：记账（PIPELINE.md）、调度（按序启用子 skill）、守门（前置检查与评审回退）。干活的是 14 个子 skill。
> 原则：一条链，任意起点，逐步推进，随时可停。

## 一、核心模型

```
① 竞品分析 → ② PRD 设计 → ③ PRD 评审 → ④ 原型设计 → ⑤ 原型评审 → ⑥ UI/UX 设计 → ⑦ UI/UX 评审
→ ⑧ 后端技术方案 → ⑨ 前端技术方案 → ⑩ 技术方案评审 → ⑪ 后端开发 → ⑫ 前端开发 → ⑬ 代码评审 → ⑭ 测试
```

| 参数 | 怎么定 | 默认 |
|---|---|---|
| 起点 | 用户点名，或按 `.spec/` 已有产物推断 | ① |
| 终点 | 用户点名；不点名 = 只跑起点 | 起点本身 |
| 跳过 | 用户随时说「跳过 XX」 | 无 |

推进：完成节点 → 回填 PIPELINE → 交接摘要 → 停下等用户（继续 / 跳过 X / 重做 / 就到这）。用户明确「一路做到测试」才连续跑，中途仅在评审节点停。

## 二、节点速查表

前置缺失即阻塞。环境依赖：
- 浏览器工具（Playwright → browser-use → 其他）：⑤⑦⑨⑫⑭ 硬依赖（全无报错停），⑧⑩ 软检测（全无跳过辅助步骤）。
- ⑥ UI/UX 设计 = Superdesign 底座硬依赖（CLI + 授权 + SOP 可读，缺一阻塞）；浏览器仅为截图可选增强。

| # | 节点 | 调用 | 前置（缺失阻塞） | 产出 |
|---|---|---|---|---|
| ① | 竞品分析 | Competitive-Analysis | 用户想法 | `.spec/<主题>竞品分析/` |
| ② | PRD 设计 | PRD-Design | 用户想法（竞品报告可选） | `.spec/PRD/V1/` |
| ③ | PRD 评审 | PRD-Review ⇄ PRD-Design | PRD | `.spec/需求评审/` |
| ④ | 原型设计 | Prototype-Design | PRD | `.spec/原型/` |
| ⑤ | 原型评审 | Prototype-Review ⇄ ④/② | PRD + 原型 | `.spec/原型评审/` |
| ⑥ | UI/UX 设计 | UI-UX-Design | PRD + 布局清单 + 原型 | `.spec/设计稿/` |
| ⑦ | UI/UX 评审 | UI-UX-Review ⇄ ⑥/④/② | PRD + 布局清单 + 设计稿 | `.spec/设计评审/` |
| ⑧ | 后端技术方案 | Backend-Tech-Design | PRD（原型/设计稿可选） | `.spec/TDD/V1/` |
| ⑨ | 前端技术方案 | Frontend-Tech-Design | PRD + TDD（设计稿可选） | `.spec/FTDD/V1/` |
| ⑩ | 技术方案评审 | Tech-Review ⇄ ⑧/⑨ | TDD 或 FTDD + PRD | `.spec/技术方案评审/` |
| ⑪ | 后端开发 | Backend-Dev | TDD（FTDD 可选） | 代码 + PROJECT.md + PLAN.md |
| ⑫ | 前端开发 | Frontend-Dev | FTDD（TDD/设计稿可选） | 代码 + PROJECT.md |
| ⑬ | 代码评审 | Code-Review ⇄ ⑪/⑫ | 任一端代码 | `.spec/代码评审/` |
| ⑭ | 测试 | Testing | 可运行代码 + PRD | `.spec/测试/`（有设计稿时内嵌 Fidelity-Review） |

**硬串行**：⑧ TDD → ⑨ FTDD（FTDD 须读 TDD 接口契约）；⑪ 后端 → ⑫ 前端（按真实契约对接）。

## 三、起点确定

### 用户点名

从零开发/按流程开发 → ①→⑭；写 PRD → ②（可 +③）；有 PRD 出原型 → ④；评审原型 → ⑤；生成设计稿 → ⑥；评审设计稿 → ⑦；有 PRD 走后续 → ④→⑭；写技术方案 → ⑧（可到⑩）；按方案写代码 → ⑪→⑫；评审代码 → ⑬；测试项目/还原度 → ⑭（还原度内嵌 Fidelity-Review）。

### 自动推断（需确认）

无产物 → ①；有 PRD 无原型 → ④；有 PRD+原型未评审 → ⑤；已评审无设计稿 → ⑥；有设计稿未评审 → ⑦；无 TDD → ⑧；有 TDD 无 FTDD → ⑨；有 TDD+FTDD 无代码 → ⑪；有后端无前端 → ⑫；代码齐 → ⑬。

推断后必须向用户确认建议起点。设计稿可选：用户说不需要即标 ⑥⑦ `已跳过`，从 ⑧ 起。

## 四、调度规程

### 启动
读项目根 `.spec/PIPELINE.md`：不存在 → 按 `assets/pipeline-template.md` 新建并定起点终点；存在 → 从「当前节点」续跑。启动必问：项目根目录、起点（点名优先，否则推断后确认）、终点（不指定 = 只跑起点）。

### 执行一个节点
1. 前置检查：读目录核实产物实际存在，缺失阻塞。
2. 播报节点与调用 skill。
3. 读取 `<skill-dir>/SKILL.md` 全文按其流程执行。
4. 产出检查：产物未落盘则阻塞。
5. 评审节点按第五节判定。
6. 回填 PIPELINE（已完成 + 产物路径 + 交接记录）。
7. 输出交接摘要并停下等用户。

子 skill 目录：优先同级 `../X/SKILL.md`；找不到问用户并记入 PIPELINE。

### 交接摘要

```
✅ N. 节点已完成
产出物：<路径>
给下一节点的输入：<该读什么>
遗留与待确认：<开放问题>
PIPELINE：<路径>
—— 回复「继续」/「跳过 X」/「重做」/「就到这」
```

### 阻塞格式

```
⛔ N. 节点 前置缺失
缺失：<路径/文件>
建议：<先跑 X / 手动指定 / 换起点>
```

## 五、评审节点与回退（③⑤⑦⑩⑬）

评审 skill 只审不改、不设门禁；放行由本编排判定：

```
评审完成 → 任务清单（待确认）→ 用户逐条裁决
已确认=0 → 放行；已确认>0 → 回修改方修复（轮次+1）→ 重跑评审
轮次>3 → 停，交用户：接受现状 / 忽略 / 转人工
```

| 节点 | 清单 | 修改方 |
|---|---|---|
| ③ | `.spec/需求评审/任务清单.md` | PRD-Design |
| ⑤ | `.spec/原型评审/任务清单.md` | 原型 → Prototype-Design；PRD 冲突 → PRD-Design |
| ⑦ | `.spec/设计评审/任务清单.md` | 设计稿 → UI-UX-Design；布局 → Prototype-Design；PRD → PRD-Design |
| ⑩ | `.spec/技术方案评审/任务清单.md` | 后端 → Backend-Tech-Design；前端 → Frontend-Tech-Design；双方先后端再前端 |
| ⑬ | `.spec/代码评审/任务清单.md` | 后端 → Backend-Dev；前端 → Frontend-Dev；双方先后端再前端 |

修改方 skill 内含清单检测与回填，编排器只指定入口。评审节点可跳过（用户指令直接跳）。

**流程裁剪判据**：是否保留某关卡取决于其对冲的模型短板是否仍存在；模型越强流程越轻（可跳过低价值中间环节、保留讨论与最终验收），模型弱或高风险改动时关卡从重。裁剪由用户裁决。

## 六、PIPELINE.md

- 路径：被开发项目根 `.spec/PIPELINE.md`；模板 `assets/pipeline-template.md`；唯一写入方是本 skill。
- 作用：跨会话续跑唯一依据。只记本次路径节点，核心三段：本次路径（起点/终点/序列/跳过）、进度（状态 + 产物路径）、交接记录。

## 七、铁律

1. 编排器不产业务文档，只写 PIPELINE.md。
2. 进度只读 PIPELINE.md，不靠对话记忆；完成即时回填。
3. 每节点完成停等用户（除非用户明确一路做到 X）。
4. 前置缺失就阻塞，不硬推。
5. 评审未清零不放行；回退超 3 轮交回用户。
6. 硬串行处不并行。
7. 子 skill 内部 Gate、必问项、成本红线（含 Superdesign 花钱动作）照常执行，编排器不越权代答。
8. 子 skill 永远可独立调用。

## 八、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 编排器代写业务文档 | 只调度 |
| 凭记忆判断进度 | 先读 PIPELINE |
| 节点完自动往下跑 | 停下等用户 |
| 点名单节点却跑全链 | 终点未定 = 只跑起点 |
| 前置缺失造占位继续 | 阻塞提示 |
| TDD/FTDD 或前后端并行 | 硬串行 |
| P0 未清放行 | 未清零不放行；坚持则标已忽略+理由 |
| 无限回退 | 轮次上限 3 |
| 猜子 skill 路径 | 询问并记入 PIPELINE |
| 起点未确认开跑 | 推断起点必须确认 |
| 擅自加设计变体/花钱 | 等用户裁决 |

## 九、资源清单

- `assets/pipeline-template.md`
- 同级子 skill：Competitive-Analysis、PRD-Design、PRD-Review、Prototype-Design、Prototype-Review、UI-UX-Design、UI-UX-Review、Backend-Tech-Design、Frontend-Tech-Design、Tech-Review、Backend-Dev、Frontend-Dev、Code-Review、Testing
- 产物归档：被开发项目 `.spec/`；竞品分析产物 `.spec/<主题>竞品分析/`