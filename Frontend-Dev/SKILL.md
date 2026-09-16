---
name: Frontend-Dev
description: 前端代码开发。依据 PRD、原型（结构基线）、设计稿（视觉基准）、TDD、FTDD 把技术方案落地为可运行、高还原、模块化前端工程：测试先行、功能点提交、组件抽离铁律、接口契约双向对齐、浏览器工具硬性预检（全无报错停）。还原度优先，不确定即问给选项。触发：编写/实现/开发前端代码、实现页面、按 FTDD 写前端页面。
compatibility: Claude Code / Agent SDK / OpenCode
---

# 前端代码开发 Skill

> IRON LAW：**设计稿是唯一视觉/交互/文案基准，禁止自创**——设计稿未出现的内容、区块、状态、文字不得擅自添加。
> FTDD 是施工图，照图施工。原则：还原度优先 · 模块化防重 · 测试先行 · 不确定即问 · 功能点即提交。

## 一、定位与铁律

**角色**：前端开发专家。**结构基线** = 低保真原型；**视觉基准** = 设计稿（有则以 `.spec/设计稿/` + `design-system.md` 为视觉唯一应然；无设计稿才从原型基础值收敛并明示降级）；**接口契约源** = 后端 TDD / FTDD（双基准术语见仓库根 `shared/baseline-terms.md`）。

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
| `PROJECT.md` | 续做定位与项目规则 | 无则视为新项目；有代码无文档 → 先按 `shared/dev-common.md` §一沉淀现状基线 |
| `.spec/代码评审/任务清单.md` | 归本 skill 的 `已确认` 任务纳入计划 | 无则跳过 |
| **接收评审纪律** | 先对照代码核实再改；不清楚先澄清（部分理解 = 错误实施）；禁表演性认同；「按规范完整实现」类建议先查真实使用（YAGNI） | 见仓库根 `shared/receiving-review.md` |
| 浏览器工具（**硬依赖**） | 还原校验 | **全无 → 报错停**（策略见 `shared/browser-policy.md`） |

## 三、主流程（10 步）

> 每步做完再进下一步；◉ = 强制暂停等用户确认。

**S1 输入解析与预检**：确认产出位置（目标目录 + git 地址，缺一暂停）；判 monorepo（看 pnpm-workspace / turbo / nx / apps+packages；同仓时确认前端子包、共享类型包、根配置可否动，不确定就问）；读 PROJECT.md 与 `.spec/` 各文档；**输入瘦身（续做页 REQUIRED）**：逐页开发只读本页设计稿 + FTDD 模块 §3~§5 + 本页 shared 契约段，design-system/全局组件/惯例不重读（工程已对账进 variables 与口径表，见 `case-library/static-page-trial-playbook.md` §1）；口径冲突**先查 PROJECT 口径表**（§4.9），表内直接套；纳入评审任务清单；**批判性审视** FTDD 与计划（有疑虑先提，不闷头执行）；判目标端（web / app / 小程序，多套原型按端排期并确认分端或多端一套）；**浏览器工具预检**（任一可用记作还原校验工具）。

**S2 技术栈锁定**：FTDD 存在 → 读 overview 选型**不重选**；缺失 → 补选型（档位必问 + 组件库必问 + 端相关必问，一次性确认后定稿入 PROJECT.md）；`覆盖端 ≠ 目标端` → **⛔ 阻塞**，先让 Frontend-Tech-Design 补对应端方案；**施工框架与 FTDD 选型不一致 → 阻塞对齐**，禁自主切回 React 基线（非 React 框架按 `references/framework-equivalence-guide.md` 等价映射执行）。

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

**S7 逐页面测试先行实现**：`features/<模块>/types.ts` 视图模型先行——契约缺口一律 `XxxExt` 视图扩展补位 + ⚠️ 留痕注释（缺口内容/出处/对接时裁决），**禁静默造字段**；然后先写测试（承接 FTDD 用例标 TC/AC）→ constants/mocks（mock 文案逐字对齐设计稿）→ api → hooks → 组件 → 页面容器 + 样式还原（套路与节奏纪律详见 `case-library/static-page-trial-playbook.md` §3/§6）。**组件抽离在编码当下判定**（模块内 ≥2 处 → `features/<模块>/components/`；跨模块 → `src/components/`，更新全部引用并删旧；禁先复制后重构；props 用 interface 禁 `any`）。每完成一个功能点：勾任务 + 更新 PROJECT.md + eslint/stylelint/commitlint 通过 + git commit（Conventional Commits，禁混入调试/临时/凭据，不擅自 push）。

**S8 契约对齐**：前端 fetch ↔ FTDD ↔ 后端 TDD 双向核对；共享类型只引用不重定义；冲突以 TDD 为准并提醒。

**S9 全局一致性 + 质量验收**：
- 一致性：可运行可测试；模块化合规（无越层、无复制、api 经 hooks）；截图还原比对（**有设计稿时以设计稿为视觉基准**；差异分「可接受（响应式/字体回退/动效实现）」与「必须修正（区块缺失、间距/配色/字号偏差、交互/状态缺失）」→ 必须修正入返工）。
- **性能验收（对预算）**：跑构建产物分析 + Lighthouse / 性能面板，核对 FTDD 的性能预算（Core Web Vitals / 首屏包体）；大列表、图片、字体、按需加载逐项确认——**结论要有实测数据，不是「感觉挺快」**。
- **无障碍验收**：axe-core 扫描无严重问题；键盘可完成主流程（Tab 顺序、焦点可见、Esc 可关弹层）；语义化标签与表单 label 到位；对比度达标（AA）。
- 两项结果写进 PROJECT.md 留痕（取证口径见 `shared/evidence-before-claims.md`）。

**S10 交付 + 回填**：更新 PROJECT.md 进度 + 收尾提交 + README 运行说明；回填 `.spec/代码评审/任务清单.md` 归本 skill 的 `已确认` 任务为 `已修复` + 修改说明；回填后须触发 `Code-Review` 复核（含 `Fidelity-Review` 还原度项），不得自判通过（闭环与上限规则见 `shared/anti-deadloop.md` §一/§二）；是否 push 由用户决定。

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

**4.8 不确定即问**：必问——需求口径不明、原型缺失/互斥、接口契约冲突、技术取舍、组件归属难判、还原差异难断、范围外发现、影响已交付模块、仓库/跨包约定、需改共享类型。提问方式与统一模板见仓库根 `shared/dev-common.md` §二（给选项 + 推荐 + 理由、一次一问、可批量列编号清单逐条确认、结论留痕）；有选项必给选项，无明确选项也说明建议 + 理由；影响 FTDD/PRD 时提醒回写；**纯实现细节不必问**。

**4.9 口径冲突与口径表（2026-09-16 定稿）**：设计稿↔契约↔全局组件冲突（稿面尺寸 vs design-system §5.5 档位、单页状态稿特例 vs 全局组件一致性、不一致稿面文案 vs 契约硬口径等）按 PROJECT.md「口径表」裁定——**表内已有的直接套，不算「不确定即问」；首次裁定的新口径当场落表再继续**（表结构：冲突场景 / 口径 / 首次裁定）；决策模式细则见 `case-library/static-page-trial-playbook.md` §4。同类冲突二次出现仍现场考证或凭感觉裁 = 违规。

## 五、常见错误对照表

> 公共错误行（现状基线 / 零选型 / 拍板 / 传参注释 / 提交粒度 / 门禁 / 进度更新）见仓库根 `shared/dev-common.md` §三；下表为本 skill 端专属与领域行。

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

## 六、资源清单

- `references/architecture-guide.md`、`code-style-guide.md`、`test-guide.md`、`tech-stack-guide.md`、`fidelity-guide.md`、`ui-states-guide.md`、`framework-equivalence-guide.md`、`decision-rules.md`
- `references/case-library/`：组件模式 + 框架写法 + 质量规范 + 同行样本 + **static-page-trial-playbook（静态页试做 SOP，主流程 S1/S7/§4.7/§4.9 引用）**（按需加载）
- `assets/frontend-template-react/`：**React SPA web 端可运行模板**（S3 全新工程起手复制；改造清单 / 换库指南 / 部署配置见其 README）
- `assets/frontend-template-vue3/`：**Vue3 SPA web 端可运行模板**（与 React 版功能点一一对应，新增 Pinia 状态层；S3 起手复制，用法同上）
- `assets/project-structure-template.md`、`module-code-template.md`、`project-status-template.md`
- `shared/baseline-terms.md`、`shared/browser-policy.md`、`shared/dev-common.md`、`shared/receiving-review.md`、`shared/evidence-before-claims.md`、`shared/anti-deadloop.md`（仓库根）：公共约定
- 产出位置：S1 用户给定目录 + git 地址

## 七、运行问题埋点

收尾按 `Skill-Optimizer/references/instrumentation-guide.md` 自查上报 `issue/Frontend-Dev/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `Skill-Optimizer/assets/issue-template.md`）。不确定不记，不打断主流程。
