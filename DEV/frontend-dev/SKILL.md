---
name: frontend-dev
description: "前端代码开发。依据 PRD、原型（结构基线）、设计稿（视觉基准）、TDD、FTDD 把技术方案落地为可运行、高还原、模块化前端工程：测试先行、功能点提交、组件抽离铁律、业务组件先检索外部 AI 知识库复用（经仓库根 skill-knowledge 引用层，防冗余沉淀）、接口契约双向对齐、浏览器工具硬性预检（全无报错停）。还原度优先，不确定即问给选项。触发：编写/实现/开发前端代码、实现页面、按 FTDD 写前端页面。"
metadata:
  contract-level: legacy-wrapper
  legacy-alias: "Frontend-Dev"
  compatibility: "Claude Code / Agent SDK / OpenCode"
---

# 前端代码开发 Skill

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## 先判任务强度

先按 `../../shared/execution-profiles.md` 选择强度，按 `../../shared/requirements-context.md` 读取本次需求原文与依赖。低风险独立任务直接走“确认验收点 → 相关代码/接口盘点 → 局部实现 → 针对性验证 → 结果”；缺少完整 TDD/FTDD、PROJECT/PLAN 不单独阻塞，可用同一任务摘要中的局部计划替代。复用现有栈与组件，不强制新模板、外部资产沉淀、完整 Scope Gate 或自动提交；关键业务/接口未知仍须澄清，风险变化则升级。

下文完整开发步骤与产物要求用于标准/完整；轻量仍保留适用的业务约束、范围、实现质量与测试要求，不宣称正式 Gate 通过。无浏览器可交付待视觉验证代码，但不能声称视觉/交互验收通过。


> IRON LAW：**设计稿是唯一视觉/交互/文案基准，禁止自创**——设计稿未出现的内容、区块、状态、文字不得擅自添加。
> FTDD 是施工图，照图施工。原则：还原度优先 · 模块化防重 · 测试先行 · 不确定即问 · 功能点即提交。

## 一、定位与铁律

**角色**：前端开发专家。**结构基线** = 低保真原型；**视觉基准** = 设计稿（有则以 `.spec/设计稿/` + `design-system.md` 为视觉唯一应然；无设计稿才从原型基础值收敛并明示降级）；**接口契约源** = 后端 TDD / FTDD（双基准术语见仓库根 `../../shared/baseline-terms.md`）。

> ⚠️ 低保真原型只有极简中性色 + 单一主色 + 基础字号层级，**不承载视觉基准**。有设计稿却按原型做视觉 = 违规（产出必然「结构与原型一致、视觉与设计稿差一截」）。

**铁律**：

1. 设计稿未出现的内容 / 区块 / 状态 / 文字**不得添加**；加载与错误提示居中；跨 Tab 与来源切换须清除前序状态；空态只允许单一表达。页面状态按 FTDD §9 逐态覆盖（10 大 UI 状态，实现见 `references/ui-states-guide.md`）。
2. 单向依赖：页面容器 → 组件 → hooks → api；页面只编排，逻辑下沉 hooks。
3. 模块内聚：业务代码按 `features/<模块>/`，跨模块复用进 `src/components/`，**禁复制**。
4. 测试先行，编号 `TC-Mxx-nnn ↔ AC-Mxx-nnn`。
5. 共享类型单一来源：前后端同仓时接口 / 枚举 / DTO 放共享包，前端只 `import type`，禁重定义。
6. **浏览器工具硬依赖**：全无 → 报错停，禁跳过、禁降级静态对照；每完成一个页面必须**双开截图比对还原度**（见 §4.7）——有设计稿时设计稿是视觉主基准，必须并排比对，**只对原型比对不算还原完成**。
7. 提交前 eslint + stylelint + commitlint 全过，**禁 `--no-verify`**。
8. 不确定即问，给选项；**禁 TODO 静默跳过**。

**做减法**：复用真出现（≥2 处）才抽；FTDD 明确要的才写。

**适用范围**：适用「有 FTDD（±PRD/原型/TDD）落页面代码」；不适用写评审需求、原型、前后端技术方案、后端代码、纯运维部署。

## 二、输入与前置

| 输入 | 作用 | 缺失处理 |
|---|---|---|
| `.spec/FTDD/VN/` | **施工图** | ⛔ 阻塞（缺失则补选型，见 S2） |
| `.spec/设计稿/`（**视觉主基准**，含 `design-system.md` token 源）、`.spec/原型/`（**结构基线**） | 还原比对的两级基准：结构对原型、视觉对设计稿 | 无设计稿则视觉基准回退原型并**明示降级**（经用户确认） |
| `.spec/TDD/VN/`、`.spec/PRD/VN/`（先读速查表） | 接口契约 + 需求 | 缺则按已有文档推进并标注 |
| **产出位置（必问）** | 目标目录（用给定/自定义名，不套约定）+ git 地址（已有 clone/切分支；空仓 init + remote） | 缺一暂停 |
| `PROJECT.md` | 续做定位与项目规则 | 无则视为新项目；有代码无文档 → 先按 `../../shared/dev-common.md` §一沉淀现状基线 |
| `.spec/代码评审/任务清单.md` | 归本 skill 的 `已确认` 任务纳入计划 | 无则跳过 |
| **接收评审纪律** | 先对照代码核实再改；不清楚先澄清（部分理解 = 错误实施）；禁表演性认同；「按规范完整实现」类建议先查真实使用（YAGNI） | 见仓库根 `../../shared/receiving-review.md` |
| 浏览器工具（**硬依赖**） | 还原校验 | **全无 → 报错停**（策略见 `../../shared/browser-policy.md`） |

## 三、主流程（10 步）

> 每步做完再进下一步；◉ = 强制暂停等用户确认。

**S1 输入解析与预检**：确认产出位置（目标目录 + git 地址，缺一暂停）；判 monorepo（看 pnpm-workspace / turbo / nx / apps+packages；同仓时确认前端子包、共享类型包、根配置可否动，不确定就问）；读 PROJECT.md 与 `.spec/` 各文档；**输入瘦身（续做页 REQUIRED）**：逐页开发只读本页设计稿 + FTDD 模块 §3~§5 + 本页 shared 契约段，design-system/全局组件/惯例不重读（工程已对账进 variables 与口径表，见 `case-library/static-page-trial-playbook.md` §1）；口径冲突**先查 PROJECT 口径表**（§4.9），表内直接套；纳入评审任务清单；**批判性审视** FTDD 与计划（有疑虑先提，不闷头执行）；判目标端（web / app / 小程序，多套原型按端排期并确认分端或多端一套）；**业务组件检索**：涉业务组件/通用 hooks/基建，按 S2 **组件决策链**检索外部 AI 知识库，命中即复用或适配复用，禁重复手写同类业务组件；**浏览器工具预检**（任一可用记作还原校验工具）。

**S2 技术栈锁定**：FTDD 存在 → 读 overview 选型**不重选**；缺失 → 补选型（档位必问 + 组件库必问 + 端相关必问，一次性确认后定稿入 PROJECT.md）；`覆盖端 ≠ 目标端` → **⛔ 阻塞**，先让 Frontend-Tech-Design 补对应端方案；**施工框架与 FTDD 选型不一致 → 阻塞对齐**，禁自主切回 React 基线（非 React 框架按 `references/framework-equivalence-guide.md` 等价映射执行）。

> **组件决策链（调度 AI 知识库，涉新组件/通用 hooks/基建 REQUIRED）**：① 盘点本仓已有基建（已有必须用）→ ② 检索外部 AI 知识库 `D:\project\agent-project\skills-knowledge\asset-library\`（blueprints 判型收敛 → capabilities → patterns/composites → adapters；使用入口与同步协议见仓库根 `../../skill-knowledge/README.md`）→ ③ **命中 → 直接复用并锁版本；命中但不完全适用 → 兼容性适配优先**（扩参数 / 加 adapter / 版本演进既有资产），**禁新建并列冗余组件（硬性条件）**；确实无法适配 → 记 asset-gap 说明与既有资产的差异、经用户确认才新建，或采用其他方案留在项目内不进库 → ④ 交付时做沉淀判断（四出口：Case / Candidate / 更新既有 / 反模式；**沉淀前必查重**，见 S10）；使用记录随 asset-usage / evidence 回写外部库，映射表按双仓同步协议更新。

**S3 工程初始化**：既有工程沿用现状，只补缺失基础设施（根配置改动先问）；全新工程——**web 端 SPA 直接复制可运行模板**（React / Vue3 功能点一一对应）：React → `assets/frontend-template-react/`（Vite + React 18 + AntD 5），Vue3 → `assets/frontend-template-vue3/`（Vite + Vue 3.5 + Element Plus + Pinia）；两版同款底座：TS strict 起手 + 请求层统一解包 / SSE 封装 / 路由守卫 / 错误边界 / 懒加载 + vendor 分包 / 设计 token / ui 组件库隔离出口 / 覆盖率门禁 / CI·Docker 全内置，lint·test·coverage·build 全绿基线，照模板 README「5 分钟改造清单」改品牌 / 主题色 / 代理端口等槽位；组件库或框架与 FTDD 选型不符时按模板 README「换组件库操作指南」在 `components/ui` 出口改造；**非 React/Vue / 非 web 端**仍按 `references/tech-stack-guide.md` + `assets/project-structure-template.md` 起手。monorepo 约定见 §4.2。

**S4 还原基线与 token**：逐页产**还原基线清单**——**结构行对照低保真原型**（区块 / 布局 / 交互 / 流转），**视觉行对照设计稿**（色值 / 字号字重 / 间距 / 圆角阴影 / 图标 / 状态视觉，落 `design-system.md` §7 token）；三态与 FTDD §9 适用状态一并纳入。全部收敛为 `src/styles/variables.{scss|less}`（扩展名随 FTDD 选型）的 CSS 变量，**禁写死**。
- **token 搬运对账（⚠️ REQUIRED，有设计稿时）**：设计稿是 HTML + Tailwind 类、实现是 CSS 变量，**载体不同必须逐条对账**——把 `design-system.md` §7 Token 汇总的 color / typography / spacing / radius / shadow 逐条与实现侧 `variables` 比对**条数 / 值 / 命名**，缺项或值不符即修；对账记录（条数 N↔N + 差异处置）写进 PROJECT.md。**跳过此步 = 允许视觉基线静默降级**。
- 无设计稿时才从原型基础值收敛，并在 PROJECT.md 与还原基线中**明示「视觉基准回退低保真原型」**。
- 静态资源（图标 / 图片）**从设计稿取同套同尺寸资源**（设计稿缺失才用原型），路径复制登记。

**S5 ◉ Scope Gate（强制暂停）**：呈现目标端 + 页面/模块清单 + 技术栈落地方式 + 还原基线摘要（**标明视觉基准 = 设计稿 / 或已降级回退原型**）+ token 对账结果；确认后放行；只做部分以用户指定范围为准。

**S6 开发计划**：按功能点原子拆任务（页面 / 模块 / 复用组件 / hook+测试 / 基础设施；不过大不过碎）；每功能点先写 DoD（测试全绿 + 正常/空/异常边界 + FTDD §9 适用状态齐全 + **还原核对（有设计稿：设计稿并排截图 + token 对账）** + 契约对齐）；按依赖排序落 PROJECT.md + 可勾选任务。
- **粒度判据**：功能点 = **自带测试周期、值得一个新鲜评审者单独把关**的最小单元；脚手架 / 主题配置折进需要它们的那个功能点；只在「评审者可能接受 A 却打回 B」处切分。
- **计划必含**：每功能点写清 `Files`（新建/修改的**精确路径**）+ `Interfaces`（消费谁、产出谁的**精确签名**：组件 props / hook 返回 / api 出入参）。
- **禁占位符**：不得出现 TBD / TODO /「稍后实现」/「加适当校验」/「同功能点 N」。
- **计划自审三查**：① 需求覆盖——每条 AC / 页面能指到具体功能点；② 占位符扫描——按上条清零；③ **命名与类型一致性**——同一组件 / hook / 字段在各处叫法与签名一致。

**S7 逐页面测试先行实现**：`features/<模块>/types.ts` 视图模型先行——契约缺口一律 `XxxExt` 视图扩展补位 + ⚠️ 留痕注释（缺口内容/出处/对接时裁决），**禁静默造字段**；`XxxExt` 是**临时态非终态**——逐条登记 PROJECT.md（缺口/出处/处置状态），**联调前清零**：后端补字段 → 转正式契约并回写 TDD/FTDD，或经 §4.8 裁决前端本地计算 → 删 Ext 改本地推导；Ext 存活到联调后 = 违规；然后先写测试（承接 FTDD 用例标 TC/AC）→ constants/mocks（mock 文案逐字对齐设计稿）→ api → hooks → 组件 → 页面容器 + 样式还原（套路与节奏纪律详见 `case-library/static-page-trial-playbook.md` §3/§6）。**动效实现**：动效值取自 design-system §6/§7 token，不自造；页面含过渡 / 弹层动效时 REQUIRED 加载 `references/motion-guide.md`——无 design-system 降级项目按其默认档收敛并在 PROJECT.md 明示（组件手感 / 性能 / reduced-motion 落地）。**组件抽离在编码当下判定**（模块内 ≥2 处 → `features/<模块>/components/`；跨模块 → `src/components/`，更新全部引用并删旧；禁先复制后重构；props 用 interface 禁 `any`）。每完成一个功能点：勾任务 + 更新 PROJECT.md + eslint/stylelint/commitlint 通过 + git commit（Conventional Commits，禁混入调试/临时/凭据，不擅自 push）。

**S8 契约对齐**：前端 fetch ↔ FTDD ↔ 后端 TDD 双向核对；共享类型只引用不重定义；冲突以 TDD 为准并提醒；核对 `XxxExt` 补位清单——联调前清零或转正式契约（S7），残留即升级 §4.8 提问。

**S9 全局一致性 + 质量验收**：
- 一致性：可运行可测试；模块化合规（无越层、无复制、api 经 hooks）；截图还原比对（**有设计稿时以设计稿为视觉基准**；差异分「可接受（响应式/字体回退/动效实现）」与「必须修正（区块缺失、间距/配色/字号偏差、交互/状态缺失）」→ 必须修正入返工）。
- **性能验收（对预算）**：跑构建产物分析 + Lighthouse / 性能面板，核对 FTDD 的性能预算（Core Web Vitals / 首屏包体）；大列表、图片、字体、按需加载逐项确认——**结论要有实测数据，不是「感觉挺快」**。
- **无障碍验收**：axe-core 扫描无严重问题；键盘可完成主流程（Tab 顺序、焦点可见、Esc 可关弹层）；语义化标签与表单 label 到位；对比度达标（AA）。
- **界面质量与动效验收**：按 `references/web-interface-quality-guide.md`「反模式速查」逐条扫描（表单可访问性 / 图片尺寸 / 焦点与语义 / i18n 格式 / 水合安全）；动效按 `references/motion-guide.md` 自查表核对（transition 属性明确、只动 transform/opacity、reduced-motion 与 hover 门控）。
- 三项结果写进 PROJECT.md 留痕（取证口径见 `../../shared/evidence-before-claims.md`）。

**S10 交付 + 回填**：更新 PROJECT.md 进度 + 收尾提交 + README 运行说明；**业务组件沉淀判定（⚠️ REQUIRED）**：本项目开发的业务组件——项目内已按铁律抽离且跨项目有复用潜力（可剥离项目特有依赖参数化）→ 按「职责边界 / 窄接口 / 最小示例 / 自测证据」四件套沉淀到外部 AI 知识库 `D:\project\agent-project\skills-knowledge\`（asset-library 沉淀闭环：evidence 回写 → 四出口判断，规格见其使用手册）；**沉淀前必查重（硬性条件）**：库内已有近似组件 → 一律走「更新既有 / 兼容适配」出口，禁新建并列冗余组件；确需新建须记 asset-gap 差异说明并经用户确认；判定结果留痕 PROJECT.md；强绑定本项目领域 / 数据结构的项目特有组件**不沉**（防为沉而沉）；回填 `.spec/代码评审/任务清单.md` 归本 skill 的 `已确认` 任务为 `已修复` + 修改说明；回填后须触发 `Code-Review` 复核（含 `Fidelity-Review` 还原度项），不得自判通过（闭环与上限规则见 `../../shared/anti-deadloop.md` §一/§二）；是否 push 由用户决定。

## 四、关键规范

> 正文只留判据；细则按需加载对应 references。

**4.1 端差异适配**：

| 面 | web | app | 小程序 |
|---|---|---|---|
| 工程 | Vite + React SPA | 所选框架 | 原生 / Taro / uni-app |
| 路由 | React Router v6 | 框架路由 | `app.json` / `pages.json` |
| 请求 | fetch 封装 | 框架网络层 | `wx.request` / `uni.request`（对齐同一契约） |
| 样式 | Sass/Less + 隔离（React Modules / Vue scoped） | 框架样式 | rpx / wxss（750 换算） |
| 测试 | Vitest + RTL | 框架方案 | 逻辑单测 |

还原基线跨端一致，**只做语法 / 容器适配，不因端改视觉**；框架级等价映射（Vue3 / Taro / uni-app / RN / Electron / Flutter）见 `references/framework-equivalence-guide.md`。

**4.2 monorepo 与共享类型**：仓库已 monorepo → 按现有约定建/接子包；空仓先单包，后续后端加入再迁（方案先问）；新建时根级配置与后端共用、创建前先确认。**前端只动自己子包**；根配置 / 后端包改动前必问。共享类型（请求 / 响应 / 枚举 / DTO / 分页）只放共享包；前端私有类型（props / UI 状态）放前端 `types.ts`，不污染契约。类型变更影响后端 → 停下问，不擅改；一次提交只含前端文件；跨包改动先确认再同步提交。

**4.3 模块化与组件抽离**：`页面容器（pages/）→ 业务/基础组件 → hooks → api`。组件抽离——模块内 ≥2 处 → `features/<模块>/components/`；跨模块 → `src/components/`；无业务语义可复用 → 组件库或全局组件。**hooks 优先**：逻辑抽 `useXxx`；数据获取统一返回 `{data/list, loading, error, refetch}`（fetch / TanStack Query 按 FTDD）；组件不写业务逻辑。归属变更时同步全部引用、删旧文件。

**4.4 代码规范**：组件/函数短小；命名业务化——组件 PascalCase、class kebab-case、方法 camelCase，禁 `a`/`b`/`data`/`temp`；TS 严格（禁 `any`、禁 `@ts-ignore`）；魔法值抽常量/枚举；注释一句话讲 why、一行内完成、复杂规则拆多条、删废注释；**传参必注**（JSDoc `@param` 逐参写作用/边界/默认，返回非显然用 `@returns`，props 逐字段注释）；共享类型只 import 引用；样式只引 CSS 变量。

**4.5 接口实现**：统一原生 fetch（`src/api/request.ts`：baseURL / 超时 / ApiError / token / 取消），**禁 axios**；按域拆 api 文件；组件经 hooks 调 api，**业务组件不直接 import 业务 api**。

**4.6 测试**：测试先行——先落 FTDD §10 用例再实现（§10 = TDD 测试用例；§9 = 异常与边界/适用状态）；编号沿用 `TC-Mxx-nnn ↔ AC-Mxx-nnn`；覆盖渲染 / 交互 / 数据流 / 边界 / 异常；hooks 用 renderHook + mock api；`pnpm test` 可一键跑通。

**4.7 还原度校验（⚠️ REQUIRED）**：每完成一个页面/功能点，必须先**浏览器双开截图**核验，**存在整体结构、配色、字号层级或适用状态偏离即返工**；只跑通功能不算完成。
- **基准取用（有设计稿时）**：**视觉比对基准 = 设计稿**（`.spec/设计稿/<页面>.html`）——必须先开「设计稿 ↔ 实现页」并排比对；**原型只作结构/存在性对照**，不与实现页做视觉比对、不得以「与原型一致」充当还原结论。无设计稿才回退「原型 ↔ 实现页」并在结论中标注基准降级。
- 逐项对照还原基线维度：结构（原型）/ 布局 / 配色 / 字号字重 / 圆角阴影 / 图标 / 文案 / 三态与适用状态 / 交互细节；**视觉值一致性以 `design-system.md` token 为准判定**（实现页 computed style 与 token 值相符）。
- 1. 本地起 dev server，Playwright 同开**设计稿 + 实现页**（有设计稿时；无设计稿则开原型 + 实现页）并排截图比对；2. Playwright 异常 → browser-use 等兜底；3. 工具全异常 → 停下报错，**禁静默降级静态对照**；4. 差异分类见 S9。
- **脚本化执行（项目配置了验收脚本时 REQUIRED，2026-09-16 定稿）**：先跑项目验收脚本（如 `tools/verify-page.mjs`：设计稿↔实现多档宽度双开整页截图 + 关键交互状态截图 + 顶栏列↔内容列逐像素断言，断言失败=返工）取全部产物，人工只做截图还原度判断与脚本未覆盖状态补验——**禁无头工具手动逐状态交互替代脚本**；无脚本项目按上述手动双开流程并建议参照 playbook §5 建脚本。无头浏览器操作 React 页的可靠路径（受控输入直调 React onChange、文本定位 evaluate 点击等）见 playbook §5。

**4.8 不确定即问**：必问——需求口径不明、原型缺失/互斥、接口契约冲突、技术取舍、组件归属难判、还原差异难断、范围外发现、影响已交付模块、仓库/跨包约定、需改共享类型。提问方式与统一模板见仓库根 `../../shared/dev-common.md` §二（给选项 + 推荐 + 理由、一次一问、可批量列编号清单逐条确认、结论留痕）；有选项必给选项，无明确选项也说明建议 + 理由；影响 FTDD/PRD 时提醒回写；**纯实现细节不必问**。

**4.9 口径冲突与口径表（2026-09-16 定稿）**：设计稿↔契约↔全局组件冲突（稿面尺寸 vs design-system §5.5 档位、单页状态稿特例 vs 全局组件一致性、不一致稿面文案 vs 契约硬口径等）按 PROJECT.md「口径表」裁定——**表内已有的直接套，不算「不确定即问」；首次裁定的新口径当场落表再继续**（表结构：冲突场景 / 口径 / 首次裁定）；决策模式细则见 `case-library/static-page-trial-playbook.md` §4。同类冲突二次出现仍现场考证或凭感觉裁 = 违规。

**4.10 布局还原高危坑（2026-09-17 用户走查复盘沉淀，六连坑）**：
1. **禁用「父级>标签」通配选择器做样式出口**：会命中同层所有同类元素且 specificity (0,1,1) 压过单类 (0,1,0)——案例：`.app-header__brand > span` 的 slogan 灰色规则把 logo 的 span 也盖成灰色。语义元素一律独立 BEM 类。
2. **稿面 `@media` 断点随 token 一起搬**：token 对账只对色值/字号/间距，稿面里的响应式断点（如 `.page-col` ≥1536px 放宽 1440px）漏搬 = 宽屏下内容列/导航系统性偏窄。
3. **组件库派生视觉值必须显式压回稿面**：AntD Avatar 按 size 派生字号（34px→17px，稿面 12px）、Button 两字中文插空格等——组件自算的视觉值逐个与稿面核对（computed style）。
4. **弹框内通栏条禁用负 margin 贴边**：AntD Modal 无 header 下插槽——垂直负 margin 顶进标题行造成遮挡；body 一旦 overflow 限高滚动，水平负 margin 也被裁字。通栏诉求一律改 body 内正常流圆角条。
5. **多面板弹框固定高度**：面板内容高矮不一会让弹框随 tab 切换跳变——Modal content 定高 + header/body flex 分配 + 面板内部滚动（`.ant-modal-body` flex:1 min-height:0 overflow:hidden，Tabs content-holder overflow-y:auto）。
6. **滚动 containment**：应用外壳 `height:100%` flex-col + `main` flex-1 min-height:0 overflow-y:auto——滚动只发生在内容区、顶栏常驻（用户拍板体验口径）；固定工作台页（三栏/画布）在 main 内 `flex:1; min-height:0` 自管滚动，**禁 `calc(100vh - header)` 硬算**（外壳一改全崩）。

## 五、常见错误对照表

> 公共错误行（现状基线 / 零选型 / 拍板 / 传参注释 / 提交粒度 / 门禁 / 进度更新）见仓库根 `../../shared/dev-common.md` §三；下表为本 skill 端专属与领域行。

| 错误 | 纠正 |
|---|---|
| 与 FTDD 不一致 | 读 FTDD |
| 缺失不问档位/组件库 | 补选型必问 |
| 施工框架与 FTDD 选型不一致 | 阻塞对齐，按 framework-equivalence-guide 等价映射 |
| 非 React 框架仍按 React 写法施工 | 读 framework-equivalence-guide §一/二 |
| 覆盖端不符硬写 | 阻塞补方案 |
| 自由发挥样式 | 对照还原基线 + token |
| **有设计稿却按原型做视觉 / 只与原型比对视觉** | 设计稿是视觉唯一应然（铁律 1 附加项、§4.7）；原型只作结构对照 |
| **跳过 token 搬运对账** | S4 必做 §7 token ↔ variables 逐条核对 |
| 复用 ≥2 不抽离 / 复制 | 编码当下抽离（S7） |
| 跨模块组件留私有 | 提升 + 更新引用删旧 |
| 业务组件 import api | 经 hooks → props |
| 组件堆逻辑 | 下沉 hooks |
| 写死色值 | 引用 variables |
| 用 axios | 统一 fetch |
| 后补测试无编号 | 测试先行标 TC/AC |
| 契约不一致 | 双向核对 |
| 浏览器不可用硬跑 | 报错等安装 |
| 同仓重复定义类型 | 共享包单一源 |
| 擅改根配置/后端包 | 先问 |
| 无计划就写 / 粒度异常 | S6 |
| TODO 静默跳过 | 问清或登记 |
| 提交信息随意 | Conventional Commits |
| 混入调试/临时/凭据 | 提交前 diff 自检 |
| 擅自 push | 由用户决定 |
| 组件名小写 / class 驼峰 / 方法大写 | 按 §4.4 命名规范 |
| 只跑通功能就算完成 | 铁律 6 截图比对 |
| 没实测就报性能达标 | S9 出实测数据 |
| 口径冲突逐次现场考证 / 同类反复裁 | 查 PROJECT 口径表直接套；首见新口径裁定后落表（§4.9） |
| 有验收脚本仍手动逐状态截图 / 坐标点击硬怼 | 先跑验收脚本（§4.7）；受控输入等可靠路径见 playbook §5 |
| 契约缺口静默造字段 | `XxxExt` 视图扩展 + 留痕注释（S7） |
| Ext 补位存活到联调后 | 联调前清零：补字段转正式契约或裁决本地算并回写 TDD/FTDD（S7/S8） |
| 父级>标签通配选择器当样式出口 | 语义元素独立 BEM 类（§4.10-1） |
| 稿面 @media 断点不搬 | 断点随 token 对账一起过，双视口比对（§4.10-2） |
| 组件派生视觉值（Avatar 字号等）不核对 | computed style 对稿面，显式覆盖（§4.10-3） |
| 弹框内负 margin 通栏条 | 正常流圆角条（§4.10-4） |
| 多面板弹框高度随 tab 跳变 | Modal 定高 + 面板内滚动（§4.10-5） |
| 整页滚动 / calc(100vh-header) 硬算 | 外壳 flex + 内容区滚动（§4.10-6） |
| `transition: all` / ease-in / `scale(0)` 入场 | 列明属性、确保 ease-out 自定义曲线、从 0.95+opacity 起步（motion-guide §一/§六） |
| 自造动效时长 / 曲线 / 常规 UI 动效超档 | 取 design-system §6/§7 token；按时长档收敛（motion-guide） |
| reduced-motion / hover 门控缺失 | 补 `@media` 分支（motion-guide §三） |
| 图标按钮无 aria-label / 表单无 label | 补可访问名（web-interface-quality-guide §一/§三） |
| `outline: none` 无 focus-visible 替代 | 补可见焦点样式（§二） |
| `<div onClick>` 当按钮 / 链接 | 换 `<button>` / `<a>`（§一） |
| 图片无宽高 / 大列表未虚拟化 | 显式尺寸防 CLS；>50 项虚拟化（§六/§七） |
| 硬编码日期 / 数字格式 / 阻止粘贴 | `Intl.*` 格式化；放开粘贴（§十二/§三） |
| 同类业务组件不检索直接手写 | S1/S2 组件决策链先查外部 AI 知识库，命中复用 |
| 库内已有近似组件仍新建并列组件 | 兼容性适配优先 / 走「更新既有」出口；新建须 asset-gap 差异说明 + 用户确认（硬性条件，S2/S10） |
| 可复用业务组件交付即丢不沉淀 | S10 沉淀判定（⚠️ REQUIRED）：四件套入外部 AI 知识库，项目特有不沉 |

## 六、资源清单

- `references/architecture-guide.md`、`code-style-guide.md`、`test-guide.md`、`tech-stack-guide.md`、`fidelity-guide.md`、`ui-states-guide.md`、`motion-guide.md`（动效实现；S7/S9 用）、`web-interface-quality-guide.md`（界面质量规则集；S9 与评审检出子集引用）、`framework-equivalence-guide.md`、`decision-rules.md`
- `references/case-library/`：组件模式 + 框架写法 + 质量规范 + 同行样本 + **static-page-trial-playbook（静态页试做 SOP，主流程 S1/S7/§4.7/§4.9 引用）**（按需加载）
- `assets/frontend-template-react/`：**React SPA web 端可运行模板**（S3 全新工程起手复制；改造清单 / 换库指南 / 部署配置见其 README）
- `assets/frontend-template-vue3/`：**Vue3 SPA web 端可运行模板**（与 React 版功能点一一对应，新增 Pinia 状态层；S3 起手复制，用法同上）
- `assets/project-structure-template.md`、`module-code-template.md`、`project-status-template.md`
- 仓库根 `../../skill-knowledge/`：**AI 知识库引用层**——外部库 `D:\project\agent-project\skills-knowledge\` 的使用入口 / 映射表 / 防冗余硬规则 / 双仓同步协议（见其 README；S1 检索 / S10 沉淀经此对接）
- `../../shared/baseline-terms.md`、`../../shared/browser-policy.md`、`../../shared/dev-common.md`、`../../shared/receiving-review.md`、`../../shared/evidence-before-claims.md`、`../../shared/anti-deadloop.md`（仓库根）：公共约定
- 产出位置：S1 用户给定目录 + git 地址

## 七、运行问题埋点

收尾按 `../../Other/skill-optimizer/references/instrumentation-guide.md` 自查上报 `../../issue/Frontend-Dev/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `../../Other/skill-optimizer/assets/issue-template.md`）。归因未明先留事实，按共享记录规则处理；不为经验提炼阻塞主流程。

## Contract Compatibility Layer

下方正式状态/manifest/Gate 写入步骤适用于标准/完整交接；轻量独立任务按共享执行强度使用同一任务摘要，不执行正式状态写入、不伪造批准。

Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.


> LEGACY BODY BOUNDARY: The preceding body, references, and assets are retained for capability compatibility. When any wording conflicts, the contracts in `../../shared/` and the sections below win.

## Purpose

Preserve the mature capability of `Frontend-Dev` while exposing it through the v2 Skill contract.

## Trigger

Run when the user explicitly requests this capability or when `WorkFlow/` routes a compatible stage to this wrapper.

## Inputs

- the user's request and confirmed scope;
- current project artifacts, evidence, decisions, and `.spec/workflow.yaml`;
- the retained legacy body, references, assets, and scripts in this directory.

## Preconditions

- read `../../shared/skill-contract.md`, `../../shared/gate-policy.md`, and `../../shared/anti-deadloop.md`;
- read `.spec/manifest.yaml` and `.spec/workflow.yaml` when a project is available;
- verify scope, authorization, repository boundaries, and required upstream artifacts;
- do not overwrite unrelated or uncommitted files.

## Responsibilities

- execute the retained domain capability within its stated scope;
- translate legacy outputs into the current artifact, evidence, decision, and Gate vocabulary;
- record execution, traceability, residual issues, and the next action;
- route work outside this wrapper to the responsible domain Skill.

## Non-goals

- do not silently change product decisions, scope, or acceptance criteria;
- do not invent missing facts, evidence, approvals, or test results;
- do not use legacy Gate values or legacy state files as current truth;
- do not delete retained compatibility material.

## Procedure

1. Read the request, current state, manifest, and upstream handoff.
2. Load only the retained legacy resources needed for this execution.
3. Execute the domain action and keep assumptions separate from evidence.
4. Validate the output against its repair or acceptance criteria.
5. Register artifacts, evidence, decisions, and open items.
6. Write the execution record and `.spec/workflow.yaml`.
7. Emit exactly one Gate and one explicit next action.

## Outputs

- the domain artifact, report, code change, test evidence, or routed task defined by the retained capability;
- `artifactRefs`, `evidenceRefs`, `decisionRefs`, `openItems`, `gate`, and `nextAction`;
- a failure route when the wrapper cannot complete safely.

## Evidence

Use direct source files, command output, test results, screenshots, dated external sources, or explicit user decisions. Label conclusions as `FACT`, `EVIDENCE`, `INFERENCE`, `ASSUMPTION`, `RECOMMENDATION`, `DECISION`, or `OPEN`. A recommendation is not approval.

## Gate

Use only `PASS`, `CONDITIONAL`, or `BLOCKED`. `PASS` requires complete inputs and artifacts with no unresolved P0/P1. Residual P0 is always `BLOCKED`. Residual P1 is never `PASS` and may be `CONDITIONAL` only with `exceptionId`, `risk`, `owner`, `dueAt`, `remediation`, `allowDownstream`, and `approvalRef`. Three review rounds are the maximum; never force-pass or start an automatic fourth round.

## Failure Route

If evidence, authorization, scope, or an upstream Gate is missing, set `BLOCKED`, name the missing item and owner, and route to the responsible upstream Skill. If the issue is outside this wrapper's boundary, stop and route it rather than improvising.

## Downstream Contract

Downstream Skills may consume only manifest entries whose status and Gate allow downstream use. They must read `sourceRefs`, `evidenceRefs`, `decisionRefs`, `openItems`, and `nextAction`; they must not infer approval from chat context or file existence.

## State Changes

Record the old state, new state, actor, timestamp, reason, evidence references, Gate, and next action in `.spec/workflow.yaml`. The exact state names come from `governance/state-registry.yaml`.
