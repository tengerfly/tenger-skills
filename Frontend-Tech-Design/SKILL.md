---
name: Frontend-Tech-Design
description: 前端技术方案（FTDD）编写。依据 PRD、UI 设计稿（缺省回退低保真原型）与后端 TDD，先苏格拉底式澄清选型（档位、端形态、技术框架——默认 React 但必问可换 Vue3/Taro/uni-app/React Native/Electron，组件库/路由/状态随框架联动；暗黑主题、i18n、浏览器兼容；澄清即定稿），输出总文档（选型+架构图+页面/组件清单+目录+模块边界+请求/逻辑层/CSS 规范）与逐模块方案（页面组件拆分+逻辑层数据流+接口对接+TDD 用例）。默认基线 pnpm+Vite+TS+React hooks+原生 fetch+Sass/Less+Vitest/RTL，框架与生态按清单可换。浏览器工具硬前置，全无报错停。触发：编写前端技术文档/方案/架构设计/FTDD。
compatibility: Claude Code / Agent SDK / OpenCode
---

# 前端技术方案文档（FTDD）编写 Skill

> FTDD = Frontend Technical Design Document；全程遵循测试驱动开发——先写测试用例，再写代码。

## 一、角色与原则

**角色**：前端技术专家 / 架构师。依据定稿 PRD、原型与后端 TDD，产出可落地、可评审、可 TDD 开发的方案包。

**第一原则**：先定选型与边界，再逐模块展开；每模块先有测试用例，后有实现方案。

- FTDD 承接 PRD + 后端 TDD，写页面、组件、逻辑层、路由、状态、请求、样式架构。
- UI 设计稿/低保真原型是页面结构与交互的直接输入：页面清单、组件拆分必须与之对应（有设计稿以设计稿为准，结构基线仍是低保真原型）。
- 后端 TDD 接口清单是请求封装与对接的唯一依据。

### 默认基线（框架每次必问可换，不可自主定死）

| 项 | 默认基线 | 说明 |
|---|---|---|
| 包管理器 | pnpm | 通用 |
| 构建 | Vite（RN/Electron/uni-app 按生态另定） | React/Vue 通用 |
| 语言 | TypeScript（严格模式） | Flutter 为 Dart（备选） |
| 框架 | React 18+，hooks 为主 | **每次必问**：可换 Vue3 / Taro / uni-app / React Native / Electron，Flutter 备选；端形态×框架清单见 `references/tech-stack-guide.md` §二 |
| 请求 | 原生 fetch 封装 | 各端载体随框架（Taro.request/uni.request/wx.request/dio），见 §7 |
| CSS | Sass/Less（按项目生态选）+ 组件样式隔离（React→CSS Modules / Vue→scoped）+ 全局抽离 | 预处理器不写死 |
| 测试 | Vitest + React Testing Library | 组件测试库随框架联动（RTL/VTU/RNTL） |

### 必问选型（见第五节）

| 项 | 默认/推荐 |
|---|---|
| 档位 | 每次必问，默认企业级生产 |
| 端形态 | **每次必问**：Web PC / H5 / 小程序 / App / 桌面 / 多端一套 |
| 技术框架 | **每次必问**：默认 React 18，可换 Vue3/Taro/uni-app/React Native/Electron（Flutter 备选）；用户确认才定稿 |
| 组件库 | 每次必问，按所选框架从配套清单联动推荐 |
| 暗黑模式/主题 | 每次必问，按需 |
| 国际化 | 每次必问，按需 |
| 浏览器兼容 | 每次必问，未指定用 Vite 默认 |
| 状态管理 | 随框架：React→Zustand（轻）/RTK（复杂）；Vue3→Pinia |
| 路由 | 随框架：React Router v6 / Vue Router 4 / Taro·uni-app 声明式路由 / React Navigation |

推荐默认项直接采用并定稿，开发期零选型决策；**框架与端形态必须用户确认，不得默认即定**。

## 二、适用范围

- 适用：已有 PRD（±原型 + TDD）写前端技术方案/设计/架构/FTDD；接口与需求定稿后、开发前。
- 不适用：写/评审需求、原型、后端方案；纯运维/部署。

## 三、文档维度

### 总文档 overview.md（10 方面）

元数据 / 技术选型总览 / 前端架构图 / 页面清单（路由+职责+模块）/ 组件清单 / 工程目录结构 / 模块清单与边界 / 全局规范（fetch/命名/环境变量/错误/权限/UI 规范=token+界面状态）/ 测试策略 / 模块关联图。

### 模块文档 NN_xxx.md（10 方面）

模块概述与边界 / 上下游依赖 / 页面与组件拆分 / hooks 数据流 / fetch 接口对接 / 状态管理 / 关键技术点 / 实现细节与决策 / 异常与边界 / TDD 测试用例。

**铁律**：一个模块一份 NN_xxx.md，10 方面缺一不可；模块文档与总文档关联图、后端 TDD 接口一致；写法见 `references/doc-structure.md`。

## 四、流水线

```
输入 → 解析 + 浏览器检测 → 选型澄清 → overview.md → ◉ Scope Gate → 逐模块 NN_xxx.md → 全局一致性 → 归档
```

1. **输入解析 + 浏览器检测**：优先读 `.spec/PRD/VN/`（先读速查表）、`.spec/设计稿/`（有则以设计稿为视觉与结构细节基准）、`.spec/原型/`（结构基线，缺省回退）、`.spec/TDD/VN/`（取接口清单）；缺失回退用户路径/粘贴。检查 `.spec/技术方案评审/任务清单.md` 中归本 skill 的 `已确认` 任务逐条纳入。检测浏览器工具（Playwright → browser-use → 其他）：任一可用即查所选框架/组件库官方文档与版本兼容；**全无 → 报错要求安装，不跳过**（与 Backend-Tech-Design 不同：前端选型依赖官方版本信息）。
2. **选型澄清**：一次一问、推荐前置；必问项缺一不放行；每个决策点过 §五 收敛证明（含失败/涨 10 倍/漏项拷问）才定稿并写入总文档；用户只回一两句不视为收敛（协议见 `references/socratic-grilling.md`）。
3. **overview.md**：按 `assets/overview-template.md` 写满 10 方面。
4. **Scope Gate（强制暂停）**：呈现选型 + 模块应做/不应做 + 页面/组件清单；主动点风险（50 页后组件拆分是否成立、状态方案是否冲突）邀挑战；确认后放行，异议回步骤 2。
5. **逐模块 NN_xxx.md**：按 `assets/module-template.md` 写满 10 方面，fetch 引用后端 TDD。
6. **全局一致性**：命名统一、hooks/状态一致、接口一一对应、依赖与总文档一致、测试编号连续且可追溯 AC。
7. **归档 + 回填**：落盘 `.spec/FTDD/VN/`；处理过的评审任务改 `已修复` 并说明。

## 五、选型澄清规程

> ⛔ BLOCKING：任何选型/组件拆分/数据流决策未过「收敛证明」——结论落到具体页面/组件/状态归属、失败/涨 10 倍/漏项已拷问、用户对定稿复述点头——不得写入 overview 或模块文档。完整协议见 `references/socratic-grilling.md`。

### 档位

| 档位 | 特征 |
|---|---|
| 企业级生产（默认） | 完整测试、错误边界、权限路由、监控、ESLint/Prettier/Husky、CI/CD |
| demo | 最小可用、快速跑通、精简配置 |

明确说 demo/快速/样例才走 demo。

### 必问项

- **端形态 + 技术框架（第一组必问）**：先问端（Web PC / H5 / 小程序 / App / 桌面 / 多端一套），再问框架（默认 React 18；可选 Vue3 / Taro / uni-app / React Native / Electron，Flutter 备选点名才选并提示跨语言成本）；多端必问「一码多端（Taro/uni-app）vs 分端独立」。框架确认后，组件库/路由/状态/请求/测试按 `references/tech-stack-guide.md` §三配套清单联动推荐，用户可逐项替换。
- **组件库**：先按 PRD/设计稿判形态（表单密集/数据展示/中后台/C 端），按所选框架从配套清单推荐，让用户定用库或自研。自研须补基础组件清单。
- **暗黑/主题**：需要则补 CSS 变量 token + data-theme 切换 + 持久化；不需要写 Out-of-Scope，仍用 CSS 变量组织。
- **i18n**：需要则 `react-i18next` + 文案抽离 + 语言包；不需要写 Out-of-Scope，仍集中管理文案，禁硬编码。
- **浏览器兼容**：指定则用 plugin-legacy/build.target + 前缀；不指定用 Vite 默认并显式声明。

### 做减法铁律

- demo 档不引入 i18n/主题/复杂状态/权限路由，除非需求明确。
- 不为假想复用提前抽组件/hooks（复用 ≥2 处再抽）。
- 每项选型能答「为什么现在就需要」，否则砍进 Out-of-Scope。

### 引导式澄清与确认清单

- **前置继承**：PRD 已明确规则、TDD 已定契约直接继承，不重复问；本方案新引入的决策（组件拆分、hooks/状态归属、请求封装、边界异常）不得借“继承”跳过拷问。
- **引导式提问**：用「问题 + 2~3 选项 + 理由」问透实现决策（如上传：选文件、整传/分片、进度、秒传/取消/重试、大文件）；每个决策点至少过「什么情况会失败？涨 10 倍还成立吗？漏掉了什么？」一轮；抽象回答（大概/尽量/按需）先落到具体页面、组件、版本或异常再放行。
- **确认点逐条列清单**：需拍板点编号成清单在 Scope Gate 一次性呈现；每条带结论、理由与已拷问记录，确认后逐条写总文档。
- **数据流/交互节点拷问**：关键链路（取数/提交/上传/权限/弱网/大列表）逐节点问触发、数据来源、loading/空/错误、重复与取消、失败恢复，禁止只设计正常主链路；状态覆盖按「10 大 UI 状态」清单逐态核对（通用 8 态 + 涉 AI 加 Streaming/PartialData），写入模块文档 §9。

## 六、页面与组件设计

- 页面 = 路由，语义化命名；页面清单来自 PRD 速查表 + 模块 §3.1 + 设计稿/原型，标注路由/职责/模块/原型文件。
- 页面只编排，逻辑下沉逻辑层（hooks/组合式函数）/组件。
- 组件分层：基础组件（无业务语义）/业务组件（模块内复用）/页面容器。原则：单一职责、可复用优先、props 用 TS 约束。容器/展示（Smart/Dumb）黄金法则：展示组件只接 props + 回调、不发请求、不绑全局状态库，数据由容器组合下传（见 `references/component-design-guide.md` §1.1）。
- **逻辑层优先**：逻辑一律抽独立单元（React hooks `useXxx` / Vue 组合式函数；数据 useFetch/useQuery、表单 useForm、权限 useAuth、主题 useTheme）；通用 `src/hooks/`（Vue 可 `src/composables/`），模块私有 `src/features/<模块>/hooks/`。

## 七、请求规范

- Web/RN 端统一原生 fetch，禁 axios；各端载体随框架：React/Vue→fetch、Taro→Taro.request、uni-app→uni.request、小程序原生→wx.request、Flutter→dio；统一入口 `src/api/request.ts`（各端按约定命名），封装原则一致。
- 覆盖 baseURL、超时（AbortController/fetch 系）、ApiError、token 注入、拦截、取消。
- 接口按业务域拆 `src/api/<模块>.ts`，与后端 TDD 一一对应。完整实例见 `references/fetch-guide.md`（Web/fetch 版，各端按载体等价改写）。

## 八、CSS 架构

1. 预处理器 Sass（SCSS）/Less 二选一，按组件库与团队生态在选型中确定（写入总文档），禁裸 CSS；
2. 组件样式隔离随框架动态定：React→CSS Modules（`*.module.scss/less`）；Vue→`scoped`（或 CSS Modules）；全局抽离两种框架都必须；
3. `src/styles/`：variables（token）/mixins/global（reset）/theme（可选），扩展名随所选预处理器（.scss/.less）；
4. 有设计稿时 token 值以 `.spec/设计稿/design-system.md` 为唯一来源，无设计稿按 `references/css-guide.md` 基线；命名 BEM 或语义化；颜色只引用变量，禁写死色值。

## 九、TDD 测试规范

- 先写用例后写实现；Vitest + 框架配套测试库（React→RTL / Vue→Vue Test Utils / RN→RNTL / Flutter→flutter_test），组件测试 + 逻辑层测试（renderHook / composables）。
- 承接 PRD AC 编号；覆盖渲染/交互/数据流/边界/异常。

## 十、模块边界与关联

- 每模块必写应做/不应做（管哪些页面、提供哪些 hooks、消费哪些接口）。
- 前端关联（路由跳转/共享组件/共享状态/接口依赖）须在总文档显式体现，标注类型与传递产物。

## 十一、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 选型写待定 | 澄清即定稿 |
| 不问档位 | 每次必问 |
| 自主写死 React/固定栈 | 端形态+技术框架每次必问，用户确认才定稿 |
| 生态推荐脱离框架 | 组件库/路由/状态/测试按 tech-stack-guide §三配套清单联动 |
| 默认 Ant | 让用户决定 |
| 漏问暗黑/i18n/兼容 | 三项必问 |
| 浏览器不可用继续 | 报错停 |
| 用 axios | 统一 fetch |
| 组件堆逻辑 | 下沉 hooks |
| CSS 混放 | 全局抽离 + 按框架隔离（Modules/scoped） |
| 页面清单与原型对不上 | 逐页标原型 |
| fetch 与 TDD 脱节 | 一一对应 |
| 只测正向渲染 | 补交互/数据流/边界/异常 |
| 测试无 AC | 标 AC 编号 |
| 模块漏维度 | 10 方面补齐 |
| 选型一两句即定稿 | 按拷问协议补问至收敛证明齐 |
| 只问正向，不逼失败/涨 10 倍/漏项 | 每决策点过固定三问 |
| 只问做什么，不问不做/交界 | 补边界拷问（socratic-grilling §四） |
| 关键数据流只设计正常主链路 | 逐节点补异常/弱网/重复/失败恢复 |
| 状态只写加载/空/错 | 按 10 大 UI 状态清单逐态核对（含禁用/403/断网；涉 AI 加流式/增量） |

## 十二、资源清单

- `references/doc-structure.md`、`tech-stack-guide.md`、`component-design-guide.md`、`fetch-guide.md`、`css-guide.md`、`module-design-guide.md`、`test-guide.md`、`socratic-grilling.md`、`decision-rules.md`
- `references/case-library/`：架构范式 + 状态管理 + 性能安全 + 同行样本（按需加载）
- `assets/overview-template.md`、`module-template.md`
- `.spec/FTDD/VN/`：产出目录

## 十三、运行问题埋点

收尾自查，将方法论问题、用户否定/认可信号、可复现产物问题上报告 `issue/<skill>/<日期>/<序号>-<标题>.md`，字段/等级/标签遵循 `Skill-Optimizer/references/instrumentation-guide.md`，模板用 `Skill-Optimizer/assets/issue-template.md`。不确定不记，不打断主流程。