# CONTEXT.md —— Frontend-Tech-Design 术语与决策记录

> Frontend-Tech-Design 术语对齐源 + 决策日志。

## 一、角色与边界

- 人设：前端技术专家/架构师。
- 目标：依据 PRD + 原型 + TDD 产出可落地、可评审、可 TDD 开发的方案包。
- 边界：前端承接方；后端归 Backend-Tech-Design；开发期零选型。

## 二、术语表

| 术语 | 定义 | 排除 |
|---|---|---|
| FTDD | overview + NN_xxx，落 `.spec/FTDD/VN/` | 与 TDD 同缩写不同义 |
| 默认基线 | React 基线为默认；端形态+技术框架每次必问，组件库/路由/状态/测试随框架联动（tech-stack-guide §三） | 框架不可自主定死 |
| 档位 | 企业级/demo，前端叫 demo | 与后端快速实现语义同级 |
| 内容维度 | 总文档 10 方面 + 模块 10 方面固定骨架 | 不自由发挥 |
| UI 设计稿 | 输入基准：有设计稿以设计稿为准（缺省回退低保真原型），页面/组件拆分与之对应 | 结构基线仍是原型 |
| 接口契约单源 | fetch 对接唯一依据是 TDD 接口清单 | 不自造接口 |
| 浏览器硬检测 | 全无报错停 | 不是软检测 |
| hooks 数据流 | 逻辑进 hooks，组件只渲染 | 不是 class 数据流 |
| 选型澄清即定稿 | 澄清完写入总文档，Frontend-Dev 零决策 | 不留待定 |
| 苏格拉底拷问协议 | FTDD 澄清执行规范：决策树单步提问 + 边界/节点拷问 + 收敛证明 | 不是泛泛聊天；未过门槛不定稿 |
| 收敛证明 | 决策可定稿的四条件：结论落到具体范围 + 方案/理由/备选 + 失败/涨 10 倍/漏项已拷问 + 用户认可 | 缺一即 P0，退回补问 |
| 节点拷问 | 关键数据流/交互链路逐节点问触发/数据来源/异常/失败恢复 | 禁止只设计正常主链路 |
| 方案决策规则 | decision-rules.md：架构范式/微前端/状态管理/性能硬规则/构建工具/渲染策略/安全的选型与量化阈值（Decision Rules） | 与 Frontend-Dev 分工：本份管方案层，那份管编码层 |
| 案例库 | case-library/：architecture-patterns + state-management + performance-security + 同行样本（Case Library） | 借鉴不照搬，选型仍须收敛证明 |

## 三、决策日志

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 09-05 | 新建 CONTEXT；高保真→低保真；README 关系图 14 节点 | 体检术语 P0 + 同步 P1 | ✅ |
| D-02 | 09-05 | 做减法 + Scope Gate 邀抬杠 | 心法 2/3 | ✅ |
| D-03 | 09-05 | 选型澄清即定稿 | 开发期零决策 | ✅ |
| D-04 | 09-05 | 模块文档 10 方面；§5.8 前置继承/引导提问/确认清单 | 方案深到可直接编码 | ✅ |
| D-05 | 09-07 | 恢复 grill-me 式单步拷问并升为强制协议：收敛证明 + 数据流/交互节点拷问 | 澄清一两句即定稿，深度未落地（issue Frontend-Tech-Design/2026-09-07/01） | ✅ |
| D-06 | 09-08 | 沉淀容器/展示组件黄金法则（框架无关，React/Vue 写法注记）+ overview §8.6 UI 规范（token+界面状态）+ 模块文档 §9 扩为 10 大 UI 状态逐态核对 | 外部方法论 ui-ux-design.md；规范先行：UI 规范确认后开发照规范执行 | ✅ |
| D-07 | 09-08 | 选型机制重构：废「固定技术栈不询问」→ 默认基线（React）+ 端形态/技术框架每次必问可换（Vue3/Taro/uni-app/RN/Electron，Flutter 备选点名才选）；tech-stack-guide 重构为端形态×框架清单 + 8 框架配套生态 + 通用决策；输入描述 PRD+低保真原型 → PRD+UI 设计稿（缺省回退原型） | 用户裁决：技术方案针对整个前端版图不能定死 React；原生小程序仅简单场景，复杂场景用跨端框架 | ✅ |
| D-08 | 09-08 | 预处理器与隔离方案动态化：Sass/Less 按项目生态选型、组件样式隔离 React→CSS Modules / Vue→scoped，全链（SKILL/overview/css-guide/README）清写死；css-guide 示例以 SCSS 表述 + Less 等价映射 + 补 Vue scoped 对照；§八补「有设计稿时 token 值以 design-system.md 为唯一来源」强化规范先行链路 | 用户裁决：不写死 SCSS 与 CSS Modules，随框架动态处理 | ✅ |
| D-09 | 09-08 | 体检修复：术语统一「默认技术基线」→「默认基线」（与 CONTEXT 术语表/README 一致）；module-template §9 补跨 skill 寻址注记（../Frontend-Dev/references/） | Skill-Optimizer 模式④体检（六维机械核验） | ✅ |
| D-10 | 09-08 | 新增 decision-rules（架构范式/状态/性能/构建/渲染/安全选型+量化阈值）+ case-library（架构范式/状态管理/性能安全/同行样本 4 文件） | 用户提供前端技术方案案例库资源清单，要求系统增强；借鉴 peterhdd engineering-frontend-developer | ✅ |
| D-11 | 09-09 | 体检修复 10 项：设计稿=视觉基准/结构基线=原型统一（3 处）；适用输入补设计稿；引导式提问口径统一；CONTEXT 术语表 2 行列数修正；doc-structure §9 十态口径；module-template 9.x→10.x+§4→§5；module-design-guide §四→§五+10.1；socratic-grilling 拆领域节（R5）；fetch-guide token 改内存+HttpOnly Cookie（C1）；埋点统一 | 全仓冗余专项体检（用户裁决全量修复 + R9 评审模板参数化） | ✅ |

## 四、待决问题

无。