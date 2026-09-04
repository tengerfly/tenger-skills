# CONTEXT.md —— UI-UX-Design Skill 领域术语与决策记录

> 本文件是 `UI-UX-Design` Skill 的**术语对齐源**与**决策日志**。
> SKILL.md / assets / references 中出现的所有概念必须与本文件一致；
> 每敲定一个概念，必须同步更新本文件。

---

## 一、角色定位（Who We Are）

- **Skill 人设**：资深 UI/UX 设计总监 + Superdesign 编排器（Design Director & Orchestrator）；
- **核心目标**：把「PRD + 布局清单 + 低保真原型」变成一套**布局零改动、去 AI 味、风格统一**的设计稿级 HTML 视觉稿；
- **职责边界（Domain Boundary）**：本 skill 管**标准、决策、门禁、归档**（输入契约、风格决策、设计规范沉淀、质量把关、落盘）；**视觉稿的生成本体由 Superdesign 底座执行**（CLI 驱动，画布迭代）。本 skill 不手写设计稿 HTML，不做布局/载体决策（那是 Prototype-Design 的事），不写 PRD、不做评审、不写前端代码。

## 二、术语表（Glossary）

| 术语 | 英文/Key | 权威定义 | 易混淆概念排除 |
|---|---|---|---|
| 布局清单 | Layout Inventory | Prototype-Design（重构版）产出的**载体级**结构交付物：载体划分（页面/弹框/抽屉/表格/卡片/列表/表单…开放枚举）+ 宿主/入口/出口；与**低保真原型 HTML**（页内区块结构实物）共同构成本 skill 的结构真相源（Q1 对齐，D-10） | ❌ 不是 PRD；❌ 不含页内区块级拆解（区块结构由本 skill 从低保真原型提取）；❌ 不是设计任务清单 |
| 布局零改动 | Layout Freeze | 视觉稿的载体划分、页面区块结构、元素集合、跳转关系必须与「布局清单 + 低保真原型」逐项一致，视觉阶段禁止增删移区块 | ❌ 不是「视觉不变」（配色/字体/密度/圆角正是本 skill 的工作对象） |
| 设计稿 | Design Mockup | Superdesign 平台生成的设计稿级 HTML（画布管理，`projectId`/`draftId` 寻址，版本历史），最终导出归档 | ❌ 不是原型（Prototype-Design 产物，结构层）；❌ 不是前端代码（无业务逻辑、无真实数据） |
| 设计规范 | Design System | 每次生成**之前**沉淀的 Design Tokens + 组件规范；单一事实源 = 本 skill 的 `design-system-template.md`，落盘为 `.superdesign/design-system.md` 供 CLI 消费 | ❌ 不是风格提案（提案是选择项，规范是选定后的展开）；❌ 不是 Superdesign 私有格式（格式对齐但源头在本 skill） |
| 风格 DNA | Style DNA | 一套完整的视觉方向描述：配色 / 排版 / 密度 / 圆角阴影 / 交互气质，三套方案必须真实差异化 | ❌ 不是只换主色（那是假差异） |
| 基线复刻 | Replica | 按布局清单 + 低保真原型的区块结构生成的结构正确、灰调无风格 HTML，作为 `create-project --template` 的结构基线（表达布局，不表达风格） | ❌ 不是像素级复刻现有代码 UI（那是 Superdesign 官方 SOP 的代码库场景，本项目场景无既有渲染 UI） |
| 设计任务清单 | Design Task List | 本 skill 消费「布局清单 + 低保真原型」后产出的逐页设计 brief：每页的区块→组件映射（区块结构从低保真原型 HTML 提取，只翻译不改动）、内容要素、交互要求、生成提示词要点 | ❌ 不是布局清单（它是加工后的执行清单） |
| 三件套硬依赖 | Hard Dependency Trio | `superdesign` CLI 已安装 + 账号已授权（`auth status` 有效）+ skill SOP 可读；全无→阻塞并给安装指引 | ❌ 不是软检测（本 skill 无底座无法交付，属硬依赖，同浏览器工具策略的「硬」级） |
| 迭代路由 | Iteration Routing | 用户反馈的三分处理法：`branch`（探索备选）/ `replace`（精选方向上做需要设计判断的修改）/ 直编（确定性修正） | ❌ 不是一律重新生成（浪费 credits） |
| 直编 | Direct Edit | 确定性修正通道：`get-design --output` 导出 → 本地精确修改 HTML → `import-design-draft --into` 回传同 draft（免生成额度，保留版本历史） | ❌ 不是改本地文件了事（必须回传画布保持单一事实源） |
| 保真约束语 | Fidelity Clause | 每次生成调用必附的硬约束语：「只使用设计系统中定义的字体/颜色/间距/组件样式，禁止引入设计系统之外的任何视觉值」 | ❌ 不是可选项（官方判定：缺失它是坏迭代的第一大成因） |
| 生成额度 | Credits | Superdesign 平台按次计费的生成额度，归属用户；每次 branch/replace/flow 生成都在消耗它 | ❌ 不是无限资源——变体数量、生成轮次永远由用户裁决 |
| 归档 | Archive | 定稿导出至 `.spec/设计稿/`（README + HTML + 截图），评审闭环与 Workflow 只认此目录 | ❌ 不是 `.superdesign/`（那是 CLI 硬性工作目录，手段不是交付物） |

## 三、决策日志（Decision Log）

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 2026-09-04 | 职责切分：Prototype-Design 重构后只做**快速原型生成**，产物为「布局清单」；视觉稿全部由本 skill 负责 | 用户指定：原型层管「长什么样、怎么摆」，设计层管「好看、专业、统一」 | ✅ 已确认 |
| D-02 | 2026-09-04 | 布局清单的**输入契约由本 skill 定义**（`assets/layout-inventory-contract.md`），Prototype-Design 重构时对齐此模板产出 | 接口契约由消费方定义；符合「所有产物先出标准模板」的项目习惯 | ✅ 已确认 |
| D-03 | 2026-09-04 | 设计稿生成底座 = **Superdesign**（CLI 驱动 + 官方 SOP 吸收进 references）；本 skill = 设计总监 + 编排器 | 用户指定用 Superdesign 作为底座；skill 不与工具名绑定的语义保留（skill 名用 UI-UX-Design 而非 Superdesign） | ✅ 已确认 |
| D-04 | 2026-09-04 | 产物目录**双目录协作**：`.superdesign/` 为 CLI 硬性工作目录（design-system.md 必须放此），定稿导出归档到 `.spec/设计稿/` | CLI 硬性约定不可违背；评审闭环 / Workflow PIPELINE 只认 `.spec/` | ✅ 已确认 |
| D-05 | 2026-09-04 | 命名 = **UI-UX-Design** | 与仓库命名风格一致（PRD-Design / Prototype-Design / Frontend-Tech-Design） | ✅ 已确认 |
| D-06 | 2026-09-04 | Superdesign 环境即刻安装：CLI v0.14.0 已装 + 账号已授权 + skill 文件落位 `.claude/skills/superdesign/` | 用户选定「现在安装」；三件套硬依赖已就绪 | ✅ 已确认 |
| D-07 | 2026-09-04 | 设计规范**单一事实源**：本 skill `design-system-template.md` 为源 → 用户确认 → 落 `.superdesign/design-system.md`；每次生成调用强制 `--context-file` 携带 + 保真约束语 | 用户要求「生成设计稿前先沉淀设计规范」；官方 DESIGN SYSTEM FIDELITY 规则（缺失为坏迭代第一大成因）双源合一 | ✅ 已确认 |
| D-08 | 2026-09-04 | 风格推荐**双通道**：默认「文字三方案 + 色板小样 HTML」（零额度成本）；用户明确同意后才「出稿对比」（`iterate --mode branch`，花额度），变体数量永远由用户定 | credits 归用户，花钱动作必须用户裁决；与「评审死循环对策」的分级冻结思路一致——P0 花钱动作不默认执行 | ✅ 已确认 |
| D-09 | 2026-09-04 | 本 skill 场景路由 = Superdesign 官方三分路由的 **C 案（无既有渲染 UI）变体**：不做 pixel-perfect 复刻（无实然 UI），以**布局清单为结构真相源**产基线复刻，直接出风格方向稿 | 被开发项目在设计稿阶段通常无前端代码；布局清单即「应然布局」的 ground truth， fabricate 实然复刻反而制造假真相 | ✅ 已确认 |
| D-10 | 2026-09-04 | **Q1 对齐结论：双输入契约**——Prototype-Design 布局清单为**载体级**（其「最快产出」原则下不拆区块级），页内区块结构由**低保真原型 HTML** 实物承载；本 skill 消费「布局清单 + 低保真原型」双输入，区块结构由本 skill 从原型 HTML **提取（只翻译不改动）**，写入设计任务清单；契约模板由「要求生产方含区块级」改为「消费校验 + 提取规则」 | 重构版布局清单已定稿为载体级（`layout-inventory-template.md`），要求其加区块级违背「最快产出」第三原则；低保真原型本身就是区块结构 ground truth，且其「清单↔原型一致」红线保证两输入自洽 | ✅ 已确认（Q1 对齐校验完成） |
| D-11 | 2026-09-04 | 开源设计系统沉淀库（`references/open-source-design-systems.md`）**更新由用户手动发起**（如说「更新开源设计系统库」），skill 不设自动刷新机制 | 用户裁决（Q3）：手动调用，节奏自控 | ✅ 已确认 |
| D-12 | 2026-09-05 | 速查表入口补齐到执行资产层：`assets/layout-inventory-contract.md` 输入表 PRD 行加「若为 PRD-Design 产出，先读 `PRD速查表.md` 建索引」与「逐字级细节按锚点回模块原文」；`references/design-review-gate.md` §四文案保真对照物标「PRD（先读 `PRD速查表.md` 建索引，逐字比对按锚点回原文）」 | SKILL 步骤 2 已声明「若 PRD 为 PRD-Design 产出优先读 PRD速查表.md」，但同流程两份执行文档（消费契约/质量门禁）漏同步，全仓核查补齐，防跨位置失同步 | ✅ 已确认 |

## 四、待决问题清单（Open Questions）

- [x] ~~Q1：布局清单契约与 Prototype-Design 重构版实际产物对齐校验~~ → **已解决（D-10，2026-09-04）**：双输入契约落地，`layout-inventory-contract.md` 已改为「消费校验 + 区块提取规则」。
- [x] ~~Q2：本 skill 是否纳入 Workflow 链节点~~ → **已解决（2026-09-04，Workflow CONTEXT D-09）**：已接入，13 节点链 ⑥ 号位（⑤ 原型评审 → ⑥ UI/UX 设计 → ⑦ 后端技术方案），⑥ 为可选节点。
- [x] ~~Q3：开源设计系统沉淀库的更新节奏~~ → **已解决（D-11，2026-09-04）**：更新由用户手动发起，不自动刷新。
