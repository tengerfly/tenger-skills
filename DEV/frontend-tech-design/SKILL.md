---
name: frontend-tech-design
description: "前端技术方案（FTDD）编写。依据 PRD、UI 设计稿（缺失须凭用户批准的例外才可回退低保真原型）与后端 TDD，先苏格拉底式澄清选型（档位、端形态、技术框架——默认 React 但必问可换 Vue3/Taro/uni-app/React Native/Electron，组件库/路由/状态随框架联动；暗黑主题、i18n、浏览器兼容；澄清即定稿），输出总文档（选型+架构图+页面/组件清单+目录+模块边界+请求/逻辑层/CSS 规范）与逐模块方案（页面组件拆分+逻辑层数据流+接口对接+TDD 用例）。默认基线 pnpm+Vite+TS+React hooks+原生 fetch+Sass/Less+Vitest/RTL，框架与生态按清单可换。浏览器工具硬前置，全无报错停。触发：编写前端技术文档/方案/架构设计/FTDD。"
metadata:
  contract-level: legacy-wrapper
  legacy-alias: "Frontend-Tech-Design"
  compatibility: "Claude Code / Agent SDK / OpenCode"
---


> **增量设计入口**：先按 `../../shared/execution-profiles.md` 判断是否需要本 Skill。低风险已有栈局部修改可直接由开发做局部计划，不为了补形式文档强制调用技术设计。确需技术方案时按 `../../shared/requirements-context.md` 固定相关需求/AC 与依赖；已有框架和选型未变化则复用，不重复询问、不重做全套方案。新增架构/关键基础设施/不熟悉依赖仍按 OSS 研究策略核验，专业工具与安全要求不降级。

# 前端技术方案文档（FTDD）编写 Skill

> IRON LAW：**澄清即定稿**——所有选型在方案阶段一次定全，开发期零选型决策。
> FTDD = Frontend Technical Design Document；全程测试驱动：先写测试用例，再写实现方案。

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## 一、定位与铁律

**角色**：前端技术专家 / 架构师。依据定稿 PRD、设计稿/原型与后端 TDD，产出可落地、可评审、可开发的方案包。**第一原则**：先定选型与边界，再逐模块展开；每模块先有测试用例，后有实现方案。

**铁律**：

1. 选型写「待定」即违规；澄清即定稿，开发期零选型决策。
2. **端形态与技术框架每次必问**，用户确认才定稿——禁自主写死 React 或固定栈。
3. 页面清单、组件拆分必须与设计稿/原型对应（结构对原型、视觉对设计稿；布局零改动）。
4. fetch 与后端 TDD 接口清单一一对应，不自造契约；**双向一致 ≠ 完备**——模块 §5 必出页面字段清单作完备性锚点（见 S5）。
5. 先写测试用例，后写实现方案。
6. **无障碍与性能是设计输入，不是事后优化**。
7. 浏览器工具**硬依赖**：全无则报错停，不降级静态对照。
8. 只写本 skill 该写的——不代写 PRD / 原型 / 后端方案。

**适用范围**：适用「已有 PRD（±设计稿/原型 + TDD）写前端技术方案/设计/架构/FTDD」；不适用写评审需求、原型、后端方案、纯运维部署。产物落 `.spec/FTDD/VN/`。

**默认基线**（框架每次必问可换，不可自主定死；端形态×框架清单见 `references/tech-stack-guide.md` §二）：

| 项 | 默认 | 说明 |
|---|---|---|
| 包管理 / 构建 | pnpm / Vite | RN、Electron、uni-app 按生态另定 |
| 语言 | TypeScript（严格模式） | Flutter 为 Dart（备选） |
| 框架 | React 18+，hooks 为主 | **每次必问**：可换 Vue3 / Taro / uni-app / React Native / Electron |
| 请求 | 原生 fetch 封装 | 各端载体随框架（Taro.request / uni.request / wx.request / dio） |
| CSS | Sass/Less + 组件样式隔离（React→CSS Modules / Vue→scoped）+ 全局抽离 | 预处理器不写死 |
| 测试 | Vitest + RTL | 组件测试库随框架联动（RTL / VTU / RNTL） |

## 二、输入与前置

| 输入 | 作用 | 缺失处理 |
|---|---|---|
| `.spec/PRD/VN/`（先读 `PRD速查表.md` 建索引） | 需求基线 | ⛔ 阻塞，先要 |
| `.spec/设计稿/`（**视觉主基准**，含 `design-system.md` token 源）、`.spec/原型/`（**结构基线**） | 页面结构与视觉的输入；页面清单/组件拆分必须与之对应（结构对原型、视觉对设计稿） | 设计稿缺 → **不得自行回退**：须先有用户批准的例外（EXC，规则见 `../../shared/product-workflow-contract.md` §5.1），回退时明示视觉基准降级并引用该 EXC，无 EXC 即停下报 `BLOCKED`（术语见 `../../shared/baseline-terms.md`） |
| `.spec/TDD/VN/` | 请求封装与对接的**唯一依据** | ⛔ 阻塞，先要 |
| `.spec/技术方案评审/任务清单.md` | 归本 skill 的 `已确认` 任务逐条纳入 | 无则跳过 |
| `.spec/开源情报/`（OSS-Radar 同域调研报告） | **写方案前先看同类项目怎么做**：同域开源项目的前端架构/状态方案/组件库选型/测试基建发现（B 泳道三元组）反哺选型候选与组件设计 | 推荐有——缺失时建议先跑 `OSS-Radar`（项目泳道、按 PRD 关键词定向，可复用 ⑧ 轮报告补前端视角）；快速档或用户确认可跳过并留痕 |
| 浏览器工具（**硬依赖**） | 查所选框架/组件库官方文档与版本兼容 | **全无 → 报错要求安装，不跳过**（前端选型依赖官方版本信息；策略见仓库根 `../../shared/browser-policy.md`） |

## 三、主流程（7 步）

> 每步做完再进下一步；◉ = 强制暂停等用户确认。

**S1 解析输入 + 浏览器检测**：读上表输入；抽取页面清单、组件线索、接口清单（来自 TDD）、AC；**读同域开源调研报告（`.spec/开源情报/`，有则 REQUIRED）**——同域项目的前端架构/状态方案/测试基建做法反哺 S2 选型候选与 S5 组件拆分（报告三元组中「建议落点=本方案」的条目逐条纳入并留出处；无报告先建议跑 OSS-Radar，快速档经用户确认跳过并留痕）。

**S1.5 资产检索与选择（AI 知识库门禁）**：检索外部 AI 知识库 `D:\project\agent-project\skills-knowledge\asset-library\`（使用入口与同步协议见仓库根 `../../skill-knowledge/README.md`）——先判项目类型命中 `blueprints/`（可叠加取严）收敛范围，再按 capabilities → patterns/composites → adapters 检索；**命中 → 命中资产直接进方案**（组件清单/选型总览标注资产来源与版本），记录 selected/rejected/unresolved 并锁版本；**命中但不完全适用 → 方案层即做兼容性适配**（扩参数 / 加 adapter / 版本演进既有资产），禁并列冗余资产（防冗余硬条件）；无法适配 → 记缺口并说明与既有资产的差异，交 Dev 走封装七步法（造前 asset-gap）。产物落 `.spec/<feature>/` 的 `asset-needs.yaml`、`asset-selection.yaml`、`composition.yaml`（模板在组件库 `templates/project-side/`）。

**S2 选型澄清（一次定全）**：⛔ 每个决策点过「收敛证明」——结论落到具体页面 / 组件 / 状态归属 + 失败 / 涨 10 倍 / 漏项已拷问 + 用户对定稿复述点头；一两句回答不算定稿（协议见 `references/socratic-grilling.md`，通用核心 `../../shared/socratic-grilling-core.md`）。

- **必问清单（缺一不放行）**：

| 项 | 默认 / 推荐 |
|---|---|
| 档位 | 每次必问，默认企业级生产（明确说 demo/快速/样例才走 demo） |
| 端形态 | **每次必问**：Web PC / H5 / 小程序 / App / 桌面 / 多端一套 |
| 技术框架 | **每次必问**：默认 React 18，可换 Vue3 / Taro / uni-app / React Native / Electron（Flutter 备选点名才选） |
| 组件库 | 每次必问；按所选框架从配套清单联动推荐，用户定用库或自研（自研须补基础组件清单） |
| 状态管理 / 路由 | 随框架联动（React→Zustand 或 RTK / React Router v6；Vue3→Pinia / Vue Router 4；Taro·uni-app 声明式路由；RN→React Navigation） |
| 暗黑模式 / 主题 | 每次必问；需要则 CSS 变量 token + `data-theme` 切换 + 持久化，不需要写 Out-of-Scope（仍用变量组织） |
| 国际化 | 每次必问；需要则 `react-i18next` + 文案抽离 + 语言包，不需要写 Out-of-Scope（仍集中管理文案，禁硬编码） |
| 浏览器兼容 | 每次必问；指定则 plugin-legacy / build.target + 前缀，未指定用 Vite 默认并显式声明 |
| **无障碍目标** | 每次必问：默认 WCAG 2.1 AA（语义化标签、键盘可达与焦点管理、对比度、表单标签） |
| **性能预算** | 每次必问：Core Web Vitals 目标 + 首屏包体上限 + 代码分割与图片/字体策略 |

- 多端必问「一码多端（Taro/uni-app）vs 分端独立」；框架确认后组件库/路由/状态/请求/测试按 `references/tech-stack-guide.md` §三 配套清单联动推荐。
- **做减法**：demo 档不引入 i18n / 主题 / 复杂状态 / 权限路由（除非需求明确）；不为假想复用提前抽组件或 hooks（复用 ≥2 处再抽）；每项选型能答「为什么现在就需要」，否则砍进 Out-of-Scope。
- **引导式澄清**：前置已明确的直接继承不重复问（但本方案新引入的决策——组件拆分、hooks/状态归属、请求封装、边界异常——不得借「继承」跳过拷问）；同一决策点的子维度可按清单逐项过，跨决策点一次一问；每个决策点至少过「什么情况会失败？涨 10 倍还成立吗？漏掉了什么？」一轮；抽象回答（大概/尽量/按需）先落到具体页面、组件、版本或异常再放行。

**S3 生成 overview.md**：按 `assets/overview-template.md` 写满 10 方面——元数据 / 技术选型总览（**含关键决策记录：决策 / 备选项 / 选定理由 / 影响与代价**，只记真有取舍的） / 前端架构图 / 页面清单（路由+职责+模块） / 组件清单 / 工程目录结构 / 模块清单与边界 / 全局规范（fetch / 命名 / 环境变量 / 错误 / 权限 / UI 规范=token+界面状态 / **a11y 规范** / **性能预算**） / 测试策略 / 模块关联图。

**S4 ◉ Scope Gate（强制暂停）**：呈现选型 + 模块应做/不应做 + 页面/组件清单；主动点出风险（50 页后组件拆分是否成立、状态方案是否冲突）邀用户挑战；确认后放行，异议回 S2。**需拍板点逐条编号列清单**一次性呈现，每条带结论、理由与已拷问记录。

**S5 逐模块 NN_xxx.md**：按 `assets/module-template.md` 写满 10 方面——模块概述与边界 / 上下游依赖 / 页面与组件拆分 / hooks 数据流 / fetch 接口对接（引用后端 TDD） / 状态管理 / 关键技术点 / 实现细节与决策 / 异常与边界 / TDD 测试用例。
**一个模块一份文件，10 方面缺一不可**；模块文档与总文档关联图、后端 TDD 接口一致（写法见 `references/doc-structure.md`）。
**页面字段清单（⚠️ REQUIRED，落模块 §5）**：逐页面/区块列全三类字段——**展示字段、交互读取字段、状态判断字段**，每字段标出处（PRD AC 编号 / 原型元素 / 设计稿区块）；清单逐字段对 TDD 出参——「清单有、TDD 无」= 契约完备性缺口，当场裁决（后端补字段→提醒回写 TDD / 前端本地计算）并逐条留痕，未消化缺口带入 ⑩-前 三方对账必查。**双向一致 ≠ 完备**：fetch↔TDD 两端一致查不出「两端都没有」的字段，完备性只认字段清单（评审检出方见 `../tech-review/references/integration-checklist.md` IT-6）。

**S6 全局一致性**：命名统一、hooks/状态一致、接口一一对应、依赖与总文档一致、测试编号连续且可追溯 AC。

**S7 归档 + 回填**：落盘 `.spec/FTDD/VN/`；处理过的评审任务改 `已修复` 并说明。回填后须触发 `Tech-Review` 复核，不得自判通过（闭环与上限规则见仓库根 `../../shared/anti-deadloop.md` §一/§二）。

## 四、关键设计规范

> 正文只留判据；细则按需加载对应 references。

**4.1 页面与组件**：页面 = 路由，语义化命名；页面清单来自 PRD 速查表 + 模块 §3.1 + 设计稿/原型，标注路由/职责/模块/**对应原型文件（结构基线）+ 对应设计稿（视觉基准，有设计稿时）**。页面只编排，逻辑下沉逻辑层。组件分层：基础组件（无业务语义）/ 业务组件（模块内复用）/ 页面容器；**容器/展示黄金法则**——展示组件只接 props + 回调、不发请求、不绑全局状态库，数据由容器组合下传（见 `references/component-design-guide.md` §1.1）。

**4.2 逻辑层优先**：逻辑一律抽独立单元（React hooks `useXxx` / Vue 组合式函数；取数 useFetch·useQuery、表单 useForm、权限 useAuth、主题 useTheme）；通用 `src/hooks/`（Vue 可 `src/composables/`），模块私有 `src/features/<模块>/hooks/`。

**4.3 请求**：Web/RN 统一原生 fetch，**禁 axios**；各端载体随框架（React/Vue→fetch、Taro→Taro.request、uni-app→uni.request、小程序→wx.request、Flutter→dio）；统一入口 `src/api/request.ts`（各端按约定命名），封装原则一致：baseURL、超时（AbortController）、ApiError、token 注入、拦截、取消；接口按业务域拆 `src/api/<模块>.ts` 并与 TDD 一一对应。实例见 `references/fetch-guide.md`。

**4.4 CSS 架构**：预处理器 Sass/Less 二选一（随组件库与团队生态在选型中确定，禁裸 CSS）；组件样式隔离随框架（React→CSS Modules `*.module.scss`；Vue→`scoped` 或 CSS Modules），**全局抽离两种框架都必须**；`src/styles/` 放 variables（token）/ mixins / global（reset）/ theme（可选），扩展名随预处理器；**有设计稿时 token 以 `.spec/设计稿/design-system.md` §7 为唯一来源且登记条数**（开发期 `variables` 须与其逐条对账：条数/值/命名，见 `../../shared/baseline-terms.md` 下游执行口径），无则按 `references/css-guide.md` 基线；命名 BEM 或语义化，颜色只引用变量。

**4.5 无障碍（a11y）**：语义化标签优先于 ARIA 堆砌；键盘可完成主流程（Tab 顺序合理、焦点可见、Esc 可关弹层）；表单控件有 label 与错误提示关联；对比度达 AA。**动效策略**：动效强度档与时长 / 缓动 token 自 `design-system.md` §6/§7 继承，开发期不自造动效值；一切动效尊重 `prefers-reduced-motion`（实现细则见 Frontend-Dev `references/motion-guide.md`）。**落到模块文档「实现细节与决策」的具体页面**。

**4.6 性能预算**：首屏按路由懒加载 + 大依赖按需引入；图片尺寸/格式/懒加载；字体子集化与 `font-display`；大列表虚拟化或分页。**目标值写进总文档全局规范，验收在 Frontend-Dev 阶段对账**。

**4.7 TDD 测试规范**：先写用例后写实现；Vitest + 框架配套库（React→RTL / Vue→Vue Test Utils / RN→RNTL / Flutter→flutter_test）；组件测试 + 逻辑层测试（renderHook / composables）；承接 PRD AC 编号；覆盖渲染 / 交互 / 数据流 / 边界 / 异常。

**4.8 数据流与交互节点**：关键链路（取数 / 提交 / 上传 / 权限 / 弱网 / 大列表）逐节点写清触发、数据来源、loading / 空 / 错误、重复与取消、失败恢复，**禁止只设计正常主链路**；状态覆盖按「10 大 UI 状态」清单逐态核对（通用 8 态 + 涉 AI 加 Streaming / PartialData），写入模块文档 §9。

**4.9 模块边界与关联**：每模块必写应做/不应做（管哪些页面、提供哪些 hooks、消费哪些接口）；前端关联（路由跳转 / 共享组件 / 共享状态 / 接口依赖）须在总文档显式体现，标注类型与传递产物。

## 五、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 选型写待定 | 澄清即定稿（铁律 1） |
| 不问档位 | 每次必问 |
| 自主写死 React/固定栈 | 端形态 + 技术框架每次必问，用户确认才定稿 |
| 生态推荐脱离框架 | 组件库/路由/状态/测试按 tech-stack-guide §三 联动 |
| 默认 Ant | 让用户决定 |
| 漏问暗黑/i18n/兼容/a11y/性能 | 五项必问（含无障碍目标与性能预算） |
| 浏览器不可用继续 | 报错停（硬依赖） |
| 用 axios | 统一 fetch |
| 组件堆逻辑 | 下沉 hooks |
| CSS 混放 | 全局抽离 + 按框架隔离 |
| 页面清单与原型对不上 | 逐页标原型（结构）+ 设计稿（视觉） |
| fetch 与 TDD 脱节 | 一一对应 |
| 双向一致即判完备（无字段锚点） | 模块 §5 页面字段清单（三类字段+出处）逐字段对 TDD 出参（S5） |
| 只测正向渲染 | 补交互/数据流/边界/异常 |
| 测试无 AC | 标 AC 编号 |
| 模块漏维度 | 10 方面补齐 |
| 选型一两句即定稿 | 按拷问协议补问至收敛证明齐 |
| 只问正向，不逼失败/涨 10 倍/漏项 | 每决策点过固定三问 |
| 只问做什么，不问不做/交界 | 补边界拷问（socratic-grilling 领域节） |
| 关键数据流只设计正常主链路 | 逐节点补异常/弱网/重复/失败恢复 |
| 状态只写加载/空/错 | 按 10 大 UI 状态逐态核对（含禁用/403/断网；涉 AI 加流式/增量） |
| 方案层引入与库内既有资产并列的新组件 | S1.5 命中但不适用先兼容性适配（扩参数/加 adapter），禁并列冗余资产（防冗余硬条件） |

## 六、资源清单

- `references/doc-structure.md`、`tech-stack-guide.md`、`component-design-guide.md`、`fetch-guide.md`、`css-guide.md`、`module-design-guide.md`、`test-guide.md`、`socratic-grilling.md`（领域节；通用核心 `../../shared/socratic-grilling-core.md`）、`decision-rules.md`
- `references/case-library/`：架构范式 + 状态管理 + 性能安全 + 同行样本（按需加载）
- `assets/overview-template.md`、`module-template.md`
- `../../shared/baseline-terms.md`、`../../shared/browser-policy.md`、`../../shared/socratic-grilling-core.md`、`../../shared/anti-deadloop.md`、`../../shared/receiving-review.md`（仓库根）：公共约定（末项含接收评审纪律）
- `.spec/FTDD/VN/`：产出目录

## 七、运行问题埋点

收尾按 `../../Other/skill-optimizer/references/instrumentation-guide.md` 自查上报 `../../issue/Frontend-Tech-Design/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `../../Other/skill-optimizer/assets/issue-template.md`）。归因未明先留事实，按共享记录规则处理；不为经验提炼阻塞主流程。

## Contract Compatibility Layer

Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.


> LEGACY BODY BOUNDARY: The preceding body, references, and assets are retained for capability compatibility. When any wording conflicts, the contracts in `../../shared/` and the sections below win.

## Purpose

Preserve the mature capability of `Frontend-Tech-Design` while exposing it through the v2 Skill contract.

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
