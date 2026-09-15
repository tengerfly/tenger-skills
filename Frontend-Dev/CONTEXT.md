# CONTEXT.md —— Frontend-Dev 术语与决策记录

> Frontend-Dev 的术语对齐源与决策日志。

## 一、角色与边界

- 人设：前端开发专家。
- 目标：依据 FTDD 落地高还原、模块化、可运行、可维护的前端工程。
- 边界：照图施工；不重新设计/改需求/换选型；后端归 Backend-Dev。

## 二、术语表

| 术语 | 定义 | 排除 |
|---|---|---|
| 还原双基准 | 结构=低保真原型；视觉=设计稿（**设计稿为视觉唯一应然，含 token 搬运对账**；无设计稿才回退原型并明示降级） | 不是只对原型还原；**有设计稿却按原型做视觉 = 违规** |
| 功能点 | 可独立验收/提交的单元 | 不是一行代码 |
| 组件抽离铁律 | 模块内 ≥2 次 → features/<模块>/components/；跨模块 → src/components/ | 编码当下抽离，禁先复制后重构 |
| hooks 优先 | 逻辑抽 hooks，组件只渲染；数据返回 `{data/list, loading, error, refetch}` | 业务组件不直接 import api |
| 共享类型单一来源 | 接口/枚举/DTO 放共享包，前端 import type | 不另建一套 |
| 三道提交门禁 | eslint + stylelint + commitlint | 禁 --no-verify |
| 浏览器硬性预检 | Playwright → browser-use → 其他；全无报错停 | 不是软检测 |
| 页面还原度校验 | 基准与实现页截图并排，差异分可接受/必须修正 | 不是业务测试 |
| 不确定即问 | 影响正确性/契约/还原/选型/范围就问 | 纯实现细节不问 |
| 断点续做 | PROJECT.md 是唯一恢复入口 | 不靠记忆 |
| 契约双向核对 | fetch ↔ FTDD ↔ TDD 一致 | 不是单向参照 |
| 项目现状基线 | 既有工程先盘点沉淀 PROJECT.md，按现状开发 | 现状优先于模板 |
| 编码层决策规则 | Decision Rules | decision-rules.md：组件模式/状态管理/样式/数据表单/测试/工程化规范的量化硬规则 | 与 FTDD 分工：那份管方案层，本份管编码层 |
| 案例库 | Case Library | case-library/：component-patterns + framework-patterns + quality-conventions + 同行样本 | 借鉴不照搬，FTDD 选型与多框架等价映射优先 |
| 口径表 | PROJECT.md 内冲突裁定表（冲突场景 / 口径 / 首次裁定）：表内直接套、首见落表、同类二次现场考证 = 违规（§4.9） | 不是每次冲突都现场考证 |
| 输入瘦身 | 续做页只读本页设计稿 + FTDD 模块 §3~§5 + 本页 shared 契约段（S1 REQUIRED） | 不是每页重读全局文档 |
| 视图扩展 `XxxExt` | 契约缺口在 `features/<模块>/types.ts` 以 `XxxExt` 补位 + ⚠️ 留痕注释（S7） | 禁静默造字段 |

## 三、决策日志

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 09-05 | 还原双基准落地 + 新建 CONTEXT | 体检术语 P1 + 跨位置 P1×3 | ✅ |
| D-02 | 09-05 | 注入做减法 | Vibe Coding 心法 2 | ✅ |
| D-03 | 09-05 | 功能点 DoD 前置 | 学习笔记 3.1 | ✅ |
| D-04 | 09-05 | 既有工程盘点 + 开发期零选型决策 | 用户要求同后端口径 | ✅ |
| D-05 | 09-07 | 还原失败模式沉淀：每页功能点提交前必须浏览器双开截图，禁止「先功能后视觉/默认样式顶替/未样式提交」 | 学径前端整站还原 P0 复盘（页面还原评审报告 G/H/P/L/K） | ✅ |
| D-06 | 09-07 | 设计稿唯一基准与状态自洽：禁自创文案/区块/空态，字号 token 统一、弹框方向照稿、Loading 居中、Tab 切换清状态、文件选择防抖、待确认 icon 位 | 用户逐条反馈（自创稿/竖版弹框/重复空态/加载/错误残留/闪烁） | ✅ |
| D-07 | 09-08 | 沉淀 10 大 UI 状态实现指南（ui-states-guide.md，框架无关 + React/Vue 注记）；铁律/步骤 4/6/13 与 FTDD §9 适用状态挂钩，状态缺失=功能点未完成 | 外部方法论 ui-ux-design.md：状态稳健不只 Success 态；规范先行链路 | ✅ |
| D-08 | 09-08 | 体检修复：删根目录遗留重复副本 fidelity-guide.md（正主 references/ 版）；fidelity-guide 状态口径与 SKILL 同步（三态/适用状态，挂钩 FTDD §9 + ui-states-guide 指针）；补跨 skill 寻址注记；FTDD 多框架施工缺口记 issue/Frontend-Dev/2026-09-08/01（P1 待处理） | Skill-Optimizer 模式④体检（六维机械核验） | ✅ |
| D-09 | 09-08 | 多框架施工适配（修 issue 01）：新增 references/framework-equivalence-guide.md（7 框架核心概念等价映射总表 + 6 条施工切换规则 + 切换自查清单）；SKILL §六补「施工框架与 FTDD 选型不一致 → 阻塞对齐」+ 非 React 框架等价映射路由；错误对照表加 2 行 | Skill-Optimizer 模式③优化（issue 01 P1） | ✅ |
| D-10 | 09-08 | 新增 decision-rules（组件模式/状态/样式/数据表单/测试/工程化规范硬规则）+ case-library（组件模式/框架写法/质量规范/同行样本 4 文件） | 用户提供前端开发案例库资源清单，要求系统增强；借鉴 lobehub/qumge 范本 | ✅ |
| D-11 | 09-09 | 体检修复 9 项：孤立代码围栏删除；FTDD §9/§10 一词两义 5 处归位；双开对象表述统一；Flutter 补枚举；api 收敛 src/api/ 口径；commitlint Test 小写；tech-stack-guide token 内存化+悬空编号修正；CONTEXT hooks 补 list 别名；README VN/设计稿+下游 Code-Review；现状基线/澄清协议/错误表收口 shared/dev-common.md（R7）+双基准引用（R6）+埋点统一 | 全仓冗余专项体检（用户裁决全量修复 + R9 评审模板参数化） | ✅ |
| D-12 | 09-09 | 终检修复 2 项：tech-stack-guide RN 请求列 axios 口径收敛（FTDD 选 axios 时经统一契约层接入）；CONTEXT/fidelity-guide 弯引号统一「」 | 全仓终检（冗余专项体检修复后复审，用户裁决全修） | ✅ |
| D-13 | 09-10 | 门禁闭环配套：步骤 11 交付补「回填 `.spec/代码评审/任务清单.md` 归本 skill 的已确认项 → 重跑 `Code-Review` 复核（含 Fidelity-Review 还原度项），不得自判通过」；满 3 轮按仓库根 `shared/anti-deadloop.md` §二 处理 | Workflow 门禁闭环改造配套（用户要求前端代码评审固定带还原度 + 循环到清零） | ✅ |
| D-14 | 09-10 | 吸收外部精华：步骤 10「全局一致性」扩为「**全局一致性 + 质量验收**」——①**性能验收对预算**（构建产物分析 + Lighthouse/性能面板核对 Core Web Vitals 与首屏包体，大列表/图片/字体/按需加载逐项确认，**结论要有实测数据**）；②**无障碍验收**（axe-core 无严重问题、键盘可完成主流程含 Tab 顺序与焦点可见、语义化与表单 label、对比度 AA）；③两项结果写进 PROJECT.md 留痕（对接 `shared/evidence-before-claims.md`）。另同日早前已落计划规范与接收评审（步骤 6/1） | 来源：`inskillflow/claude-code-skills` 的 `frontend-developer`（Core Web Vitals / WCAG AA / axe-core / 审计驱动验证） | ✅ |
| D-15 | 09-10 | **结构重构（统一骨架）**：章节 15 → 7——§一 定位与铁律（Iron Law「设计稿是唯一基准，禁止自创」+ 铁律瘦身 8 条）；§二 输入与前置（表格化，含产出位置必问 / 评审清单与接收评审纪律 / 浏览器硬依赖）；§三 主流程 10 步（**组件抽离落地检查并入 S7 编码当下**；S9 = 一致性 + 性能验收 + 无障碍验收）；§四 关键规范 4.1~4.8（端差异适配 / monorepo 与共享类型 / 模块化与组件抽离 / 代码规范 / 接口实现 / 测试 / 还原度校验 / 不确定即问）；§五 错误表 / §六 资源 / §七 埋点。old-vs-new 审计：原 15 章内容全部有归属，无功能丢失 | 用户要求：整理成顺畅流程（Skill-Optimizer 全量体检） | ✅ |
| D-16 | 09-15 | **视觉基准口径纠偏（P0）**：①铁律 6、§一角色、§二输入表、S4、§4.7 全部改为「**设计稿是视觉唯一应然**，原型只作结构对照」，删除「基准=原型，有设计稿时加开」的降级语气；②§4.7 明确必须并排「设计稿 ↔ 实现页」，只对原型比对不算还原完成；③S4 新增 **token 搬运对账（REQUIRED）**——design-system §7 ↔ `styles/variables` 逐条核对条数/值/命名，记录进 PROJECT.md；④S6 DoD 与 S5 Scope Gate 补还原证据与基准标注；⑤错误表加「有设计稿却按原型做视觉」「跳过 token 对账」两行；⑥`references/fidelity-guide.md` 重写（基准口径表按维度标注对照基准、脚本模板加 `DESIGN_BASE`、结论表加视觉基准行、失败模式加第 6/7 条）；⑦templates/skills 同步（module-code / project-status / project-structure / tech-stack-guide / code-style-guide / README） | 用户反馈：设计稿 OK 但前端画出来差别大；根因 = `fidelity-guide` 与 §4.7 主述以低保真原型为视觉基准（原型仅中性色+单一主色+基础字号），比对必过而视觉必然走样；中央口径 `shared/baseline-terms.md` 同批补「还原度定义 + 下游执行口径 + token 对账」 | ✅ |
| D-17 | 09-16 | 正面案例沉淀：新增 `case-library/static-page-trial-playbook.md`（静态页试做六节流程：输入瘦身/复用清单/编码套路/口径决策模式/验收脚本化/节奏纪律）+ 案例库索引行；配套验收脚本与口径表落消费方项目仓库 | 用户点名首页/资产库两页为正面案例要求沉淀；节奏复盘 41min/页拆解显示验收手动截图与口径现场考证为可固化成本（issue/Frontend-Dev/2026-09-16/01，标签=正面参考） | ✅ |
| D-18 | 09-16 | **案例升级为主流程标准 SOP**：S1 输入瘦身（REQUIRED）+ 口径表查表；S7 视图模型先行（XxxExt 扩展+留痕，禁静默造字段）；§4.7 新增脚本化执行（项目有验收脚本则 REQUIRED 先跑，禁手动逐状态替代）；新增 §4.9 口径冲突与口径表（表内直接套、首见落表、二次考证=违规）；错误表 +3 行；§六标注 playbook=SOP；playbook 头部标注 SOP 状态 | 用户澄清「本意是沉淀成标准 SOP，后续开发都按这个流程来，能提高质量」——案例库被动落点无法保证执行，必须进主流程 Gate（issue/Frontend-Dev/2026-09-16/02；元教训落 Skill-Optimizer §七-6） | ✅ |
| D-19 | 09-16 | 体检修复 5 项：①S7 引用扩为「套路与节奏纪律详见 playbook §3/§6」，承接 playbook 头部 §6 硬性纪律声明；②§4.9 补「决策模式细则见 playbook §4」+「§5.5」注明 design-system；③playbook 头部引用点标注对应节号（S1§1 / S7§3·§6 / §4.7§5 / §4.9§4）；④playbook hooks 契约字段对齐术语表 `{data/list, loading, error, refetch}`；⑤术语表 +3 行（口径表 / 输入瘦身 / 视图扩展 XxxExt）。另 D-18 引用编号 §七-8 纠偏为 §七-6（纠错记录归 Skill-Optimizer D-33） | Skill-Optimizer 模式④体检，用户裁决全修 | ✅ |

## 四、待决问题

无。
