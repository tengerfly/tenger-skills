---
name: Frontend-Tech-Design
description: 前端技术方案（FTDD）编写。依据 PRD、低保真原型与后端 TDD，先苏格拉底式澄清选型（档位企业级/demo、组件库、暗黑主题、i18n、浏览器兼容；澄清即定稿），输出总文档（选型+架构图+页面/组件清单+目录+模块边界+fetch/CSS/hooks 规范）与逐模块方案（页面组件拆分+hooks 数据流+fetch 对接+TDD 用例）。固定栈 pnpm+Vite+TS+React hooks+原生 fetch+Sass+Vitest/RTL。浏览器工具硬前置，全无报错停。触发：编写前端技术文档/方案/架构设计/FTDD。
compatibility: Claude Code / Agent SDK / OpenCode
---

# 前端技术方案文档（FTDD）编写 Skill

> FTDD = Frontend Technical Design Document；全程遵循测试驱动开发——先写测试用例，再写代码。

## 一、角色与原则

**角色**：前端技术专家 / 架构师。依据定稿 PRD、原型与后端 TDD，产出可落地、可评审、可 TDD 开发的方案包。

**第一原则**：先定选型与边界，再逐模块展开；每模块先有测试用例，后有实现方案。

- FTDD 承接 PRD + 后端 TDD，写页面、组件、hooks、路由、状态、请求、样式架构。
- 原型是页面结构与交互的直接输入：页面清单、组件拆分必须与原型一一对应。
- 后端 TDD 接口清单是 fetch 封装与对接的唯一依据。

### 固定技术栈（不询问，直接采用）

| 项 | 选型 |
|---|---|
| 包管理器 | pnpm |
| 构建 | Vite |
| 语言 | TypeScript（严格模式） |
| 框架 | React 18+，hooks 为主 |
| 请求 | 原生 fetch |
| CSS | Sass/SCSS + 模块化 + 全局抽离 |
| 测试 | Vitest + React Testing Library |

### 必问选型（见第五节）

| 项 | 默认/推荐 |
|---|---|
| 档位 | 每次必问，默认企业级生产 |
| 组件库 | 每次必问，用户决定（中后台推荐 Ant Design） |
| 暗黑模式/主题 | 每次必问，按需 |
| 国际化 | 每次必问，按需 |
| 浏览器兼容 | 每次必问，未指定用 Vite 默认 |
| 状态管理 | Zustand（轻）/ Redux Toolkit（复杂） |
| 路由 | React Router v6 |

推荐默认项直接采用并定稿，开发期零选型决策。

## 二、适用范围

- 适用：已有 PRD（±原型 + TDD）写前端技术方案/设计/架构/FTDD；接口与需求定稿后、开发前。
- 不适用：写/评审需求、原型、后端方案；纯运维/部署。

## 三、文档维度

### 总文档 overview.md（10 方面）

元数据 / 技术选型总览 / 前端架构图 / 页面清单（路由+职责+模块）/ 组件清单 / 工程目录结构 / 模块清单与边界 / 全局规范（fetch/命名/环境变量/错误/权限）/ 测试策略 / 模块关联图。

### 模块文档 NN_xxx.md（10 方面）

模块概述与边界 / 上下游依赖 / 页面与组件拆分 / hooks 数据流 / fetch 接口对接 / 状态管理 / 关键技术点 / 实现细节与决策 / 异常与边界 / TDD 测试用例。

**铁律**：一个模块一份 NN_xxx.md，10 方面缺一不可；模块文档与总文档关联图、后端 TDD 接口一致；写法见 `references/doc-structure.md`。

## 四、流水线

```
输入 → 解析 + 浏览器检测 → 选型澄清 → overview.md → ◉ Scope Gate → 逐模块 NN_xxx.md → 全局一致性 → 归档
```

1. **输入解析 + 浏览器检测**：优先读 `.spec/PRD/VN/`（先读速查表）、`.spec/原型/`、`.spec/TDD/VN/`（取接口清单）；缺失回退用户路径/粘贴。检查 `.spec/技术方案评审/任务清单.md` 中归本 skill 的 `已确认` 任务逐条纳入。检测浏览器工具（Playwright → browser-use → 其他）：任一可用即查组件库/Vite/React 官方文档与版本兼容；**全无 → 报错要求安装，不跳过**（与 Backend-Tech-Design 不同：前端选型依赖官方版本信息）。
2. **选型澄清**：一次一问、推荐前置；必问项缺一不放行；问完即定稿并写入总文档。
3. **overview.md**：按 `assets/overview-template.md` 写满 10 方面。
4. **Scope Gate（强制暂停）**：呈现选型 + 模块应做/不应做 + 页面/组件清单；主动点风险（50 页后组件拆分是否成立、状态方案是否冲突）邀挑战；确认后放行，异议回步骤 2。
5. **逐模块 NN_xxx.md**：按 `assets/module-template.md` 写满 10 方面，fetch 引用后端 TDD。
6. **全局一致性**：命名统一、hooks/状态一致、接口一一对应、依赖与总文档一致、测试编号连续且可追溯 AC。
7. **归档 + 回填**：落盘 `.spec/FTDD/VN/`；处理过的评审任务改 `已修复` 并说明。

## 五、选型澄清规程

### 档位

| 档位 | 特征 |
|---|---|
| 企业级生产（默认） | 完整测试、错误边界、权限路由、监控、ESLint/Prettier/Husky、CI/CD |
| demo | 最小可用、快速跑通、精简配置 |

明确说 demo/快速/样例才走 demo。

### 必问项

- **组件库**：先按 PRD/原型判形态（表单密集/数据展示/中后台/C 端），让用户定用库或自研；用库参考 Ant（中后台）、Arco、Naive UI。自研须补基础组件清单。
- **暗黑/主题**：需要则补 CSS 变量 token + data-theme 切换 + 持久化；不需要写 Out-of-Scope，仍用 CSS 变量组织。
- **i18n**：需要则 `react-i18next` + 文案抽离 + 语言包；不需要写 Out-of-Scope，仍集中管理文案，禁硬编码。
- **浏览器兼容**：指定则用 plugin-legacy/build.target + 前缀；不指定用 Vite 默认并显式声明。

### 做减法铁律

- demo 档不引入 i18n/主题/复杂状态/权限路由，除非需求明确。
- 不为假想复用提前抽组件/hooks（复用 ≥2 处再抽）。
- 每项选型能答「为什么现在就需要」，否则砍进 Out-of-Scope。

### 引导式澄清与确认清单

- **前置继承**：PRD 已明确规则、TDD 已定契约直接继承，不重复问。
- **引导式提问**：用「问题 + 2~3 选项 + 理由」问透实现决策（如上传：选文件、整传/分片、进度、秒传/取消/重试、大文件）。
- **确认点逐条列清单**：需拍板点编号成清单在 Scope Gate 一次性呈现，确认后逐条写总文档。

## 六、页面与组件设计

- 页面 = 路由，语义化命名；页面清单来自 PRD 速查表 + 模块 §3.1 + 原型，标注路由/职责/模块/原型文件。
- 页面只编排，逻辑下沉 hooks/组件。
- 组件分层：基础组件（无业务语义）/业务组件（模块内复用）/页面容器。原则：单一职责、可复用优先、props 用 TS 约束。
- **hooks 优先**：逻辑一律抽 `useXxx`（数据 useFetch/useQuery、表单 useForm、权限 useAuth、主题 useTheme）；通用 `src/hooks/`，模块私有 `src/features/<模块>/hooks/`。

## 七、fetch 规范

- 统一原生 fetch，禁 axios；统一入口 `src/api/request.ts`。
- 覆盖 baseURL、超时（AbortController）、ApiError、token 注入、拦截、取消。
- 接口按业务域拆 `src/api/<模块>.ts`，与后端 TDD 一一对应。完整实例见 `references/fetch-guide.md`。

## 八、CSS 架构

1. Sass（SCSS），禁裸 CSS；
2. CSS Modules（`*.module.scss`）组件级隔离；
3. `src/styles/`：variables.scss（token）/mixins.scss/global.scss（reset）/theme.scss（可选）；
4. 命名 BEM 或驼峰语义化；颜色只引用变量，禁写死色值。

## 九、TDD 测试规范

- 先写用例后写实现；Vitest + RTL，组件测试 + hooks 测试（renderHook）。
- 承接 PRD AC 编号；覆盖渲染/交互/数据流/边界/异常。

## 十、模块边界与关联

- 每模块必写应做/不应做（管哪些页面、提供哪些 hooks、消费哪些接口）。
- 前端关联（路由跳转/共享组件/共享状态/接口依赖）须在总文档显式体现，标注类型与传递产物。

## 十一、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 选型写待定 | 澄清即定稿 |
| 不问档位 | 每次必问 |
| 默认 Ant | 让用户决定 |
| 漏问暗黑/i18n/兼容 | 三项必问 |
| 浏览器不可用继续 | 报错停 |
| 用 axios | 统一 fetch |
| 组件堆逻辑 | 下沉 hooks |
| CSS 混放 | 全局抽离 + Modules |
| 页面清单与原型对不上 | 逐页标原型 |
| fetch 与 TDD 脱节 | 一一对应 |
| 只测正向渲染 | 补交互/数据流/边界/异常 |
| 测试无 AC | 标 AC 编号 |
| 模块漏维度 | 10 方面补齐 |

## 十二、资源清单

- `references/doc-structure.md`、`tech-stack-guide.md`、`component-design-guide.md`、`fetch-guide.md`、`css-guide.md`、`module-design-guide.md`、`test-guide.md`
- `assets/overview-template.md`、`module-template.md`
- `.spec/FTDD/VN/`：产出目录

## 十三、运行问题埋点

收尾自查，将方法论问题、用户否定/认可信号、可复现产物问题上报告 `issue/<skill>/<日期>/<序号>-<标题>.md`，字段/等级/标签遵循 `Skill-Optimizer/references/instrumentation-guide.md`，模板用 `Skill-Optimizer/assets/issue-template.md`。不确定不记，不打断主流程。