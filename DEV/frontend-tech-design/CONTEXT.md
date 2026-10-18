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
| UI 设计稿 | 输入基准：有设计稿以设计稿为准（缺失须凭用户批准的例外 EXC 才回退低保真原型，见 `../../shared/product-workflow-contract.md` §5.1），页面/组件拆分与之对应 | 结构基线仍是原型 |
| 接口契约单源 | fetch 对接唯一依据是 TDD 接口清单 | 不自造接口 |
| 页面字段清单 | 模块 §5 REQUIRED：逐页面/区块列展示 / 交互读取 / 状态判断三类字段并标出处，逐字段对 TDD 出参对账完备性 | 双向一致 ≠ 完备 |
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
| D-05 | 09-07 | 恢复 grill-me 式单步拷问并升为强制协议：收敛证明 + 数据流/交互节点拷问 | 澄清一两句即定稿，深度未落地（issue ../frontend-tech-design/2026-09-07/01） | ✅ |
| D-06 | 09-08 | 沉淀容器/展示组件黄金法则（框架无关，React/Vue 写法注记）+ overview §8.6 UI 规范（token+界面状态）+ 模块文档 §9 扩为 10 大 UI 状态逐态核对 | 外部方法论 ui-ux-design.md；规范先行：UI 规范确认后开发照规范执行 | ✅ |
| D-07 | 09-08 | 选型机制重构：废「固定技术栈不询问」→ 默认基线（React）+ 端形态/技术框架每次必问可换（Vue3/Taro/uni-app/RN/Electron，Flutter 备选点名才选）；tech-stack-guide 重构为端形态×框架清单 + 8 框架配套生态 + 通用决策；输入描述 PRD+低保真原型 → PRD+UI 设计稿（缺省回退原型） | 用户裁决：技术方案针对整个前端版图不能定死 React；原生小程序仅简单场景，复杂场景用跨端框架 | ✅ |
| D-08 | 09-08 | 预处理器与隔离方案动态化：Sass/Less 按项目生态选型、组件样式隔离 React→CSS Modules / Vue→scoped，全链（SKILL/overview/css-guide/README）清写死；css-guide 示例以 SCSS 表述 + Less 等价映射 + 补 Vue scoped 对照；§八补「有设计稿时 token 值以 design-system.md 为唯一来源」强化规范先行链路 | 用户裁决：不写死 SCSS 与 CSS Modules，随框架动态处理 | ✅ |
| D-09 | 09-08 | 体检修复：术语统一「默认技术基线」→「默认基线」（与 CONTEXT 术语表/README 一致）；module-template §9 补跨 skill 寻址注记（../frontend-dev/references/） | Skill-Optimizer 模式④体检（六维机械核验） | ✅ |
| D-10 | 09-08 | 新增 decision-rules（架构范式/状态/性能/构建/渲染/安全选型+量化阈值）+ case-library（架构范式/状态管理/性能安全/同行样本 4 文件） | 用户提供前端技术方案案例库资源清单，要求系统增强；借鉴 peterhdd engineering-frontend-developer | ✅ |
| D-11 | 09-09 | 体检修复 10 项：设计稿=视觉基准/结构基线=原型统一（3 处）；适用输入补设计稿；引导式提问口径统一；CONTEXT 术语表 2 行列数修正；doc-structure §9 十态口径；module-template 9.x→10.x+§4→§5；module-design-guide §四→§五+10.1；socratic-grilling 拆领域节（R5）；fetch-guide token 改内存+HttpOnly Cookie（C1）；埋点统一 | 全仓冗余专项体检（用户裁决全量修复 + R9 评审模板参数化） | ✅ |
| D-12 | 09-09 | 终检修复 1 项：module-template 头部摘要链补「上下游依赖」（§2） | 全仓终检（冗余专项体检修复后复审，用户裁决全修） | ✅ |
| D-13 | 09-10 | 门禁闭环配套：步骤 7 回填评审任务清单后须重跑 `Tech-Review` 复核（不得自判通过）；满 3 轮按仓库根 `../../shared/anti-deadloop.md` §二 处理 | Workflow 门禁闭环改造配套（用户要求写一个审一个） | ✅ |
| D-14 | 09-10 | 吸收外部精华：总文档「全局规范」项补**无障碍 a11y 规范**与**性能预算**，并明确「**无障碍与性能是设计输入，不是事后优化**」——a11y 目标默认 WCAG 2.1 AA（语义化/键盘可达与焦点管理/对比度/表单标签）+ axe-core 自动化检查；性能预算 = Core Web Vitals 目标 + 首屏包体上限 + 代码分割与图片/字体策略；二者在模块文档「实现细节与决策」落到具体页面 | 来源：`inskillflow/claude-code-skills` 的 `frontend-developer`（Core Web Vitals / WCAG 2.1-2.2 AA / axe-core / 设计阶段即考虑无障碍） | ✅ |
| D-15 | 09-10 | 补吸收（用户「确认做」）：「技术选型总览」补**关键决策记录**（决策 / 备选项 / 选定理由 / 影响与代价；只记真有取舍的——状态管理、组件分层、构建与路由方案），与 Backend-Tech-Design 的 ADR 对齐 | 来源：`backend-architect`（ADR 记录决策与权衡） | ✅ |
| D-16 | 09-10 | **结构重构（与 Backend-Tech-Design 同骨架）**：章节 13 → 7——§一 定位与铁律（Iron Law + 铁律瘦身 8 条：选型写待定/端与框架必问/布局零改动/fetch 一一对应/测试先行/a11y 与性能是设计输入/浏览器硬依赖/只写本分）；§二 输入与前置（表格化，含 a11y 与性能目标的必问清单）；§三 主流程 7 步（**必问清单表整体内联进 S2**，含新增的无障碍目标与性能预算）；§四 关键设计规范 4.1~4.9（归并原 §五~§十 与文档维度）；§五 错误表 / §六 资源 / §七 埋点。old-vs-new 审计：原表格（默认基线 / 必问项 / 档位）与新规范全部有归属，无功能丢失 | 用户要求：吸收汇总易凌乱，整理成顺畅流程（Skill-Optimizer 全量体检） | ✅ |
| D-17 | 09-15 | 视觉基准口径纠偏：§二输入表改「设计稿=视觉主基准（含 design-system token 源），原型=结构基线；设计稿缺则明示视觉基准降级」；§4.4 补「token 以 design-system §7 为唯一来源并登记条数、开发期 variables 逐条对账」；§8.6 模板新增「token 搬运对账（登记 §7 条数）+ 还原基准分工（结构对原型、视觉对设计稿）」两行；§3.1 页面清单表加「对应设计稿（视觉基准）」列（module-template + module-design-guide + doc-structure 同步）；doc-structure 自检加 token 条数基线项；错误表「页面清单与原型对不上」补设计稿 | 用户反馈设计稿 OK 但实现页差别大；FTDD 是下游取视觉基准的交接点，须登记设计稿稿源与 token 对账基线（配合 Frontend-Dev D-16） | ✅ |
| D-18 | 09-15 | 全仓一致性纠偏：overview-template §2 补关键决策记录表 + 无障碍/性能预算选型行、§4 页面清单补「对应设计稿」列、新增 §8.7 无障碍规范与 §8.8 性能预算（D-14 声明未落模板）；doc-structure §二.2/§二.8 同步；README 必问项补 a11y 与性能预算、产出一节补全；SKILL §4.1 页面清单标注补设计稿 | 全仓七维体检（四代理并行审计）发现「SKILL 声明有、模板未承接」类断头 | ✅ |
| D-19 | 09-17 | 吸收外部精华：§4.5 无障碍补「动效策略」——动效强度档与时长 / 缓动 token 自 `design-system.md` §6/§7 继承，开发期不自造动效值；一切动效尊重 `prefers-reduced-motion`（实现细则指 Frontend-Dev `references/motion-guide.md`） | 用户要求吸收外部前端设计 skill 精华（emil-design-eng + taste-skill 动效强度档）；属「澄清即定稿」延伸——防动效在开发期才临时决策 | ✅ |
| D-20 | 09-17 | 契约完备性锚点：S5 新增「页面字段清单（REQUIRED，落模块 §5）」——逐页面/区块列展示 / 交互读取 / 状态判断三类字段并标出处，逐字段对 TDD 出参，「清单有、TDD 无」= 缺口当场裁决留痕；铁律 4 补「双向一致 ≠ 完备」；错误表 +1 行；module-template §5 加清单表与示例行 | 用户痛点：开发期才发现后端接口少字段，双向比对查不出两端同时缺失，须需求侧锚点（../../issue/Frontend-Tech-Design/2026-09-17/01；联动 Tech-Review D-09 / Frontend-Dev D-22） | ✅ |

| D-21 | 2026-09-19 | ① 输入表+S1 增 OSS-Radar 同域开源调研报告（`.spec/开源情报/`，有则 REQUIRED，缺失建议先跑、可复用 ⑧ 轮报告补前端视角）——写方案前先看同类项目怎么做；② S1.5 由「M6 资产门禁」改「AI 知识库门禁」：措辞统一外部库（经仓库根 skill-knowledge 引用层），命中资产直接进方案并标来源版本，命中但不适用→方案层即兼容性适配（防冗余硬条件），无法适配→记差异交 Dev 七步法；错误表 +1 行 | 用户拍板：技术方案前先 OSS-Radar 调研 GitHub 同类项目；AI 组件统一外部仓 skills-knowledge，防冗余为硬性条件 | ✅ |
| D-22 | 2026-10-18 | **S1.5 AI 知识库门禁路径可移植化**：外部库检索路径由本机绝对路径改为 `$env:SKILLS_KNOWLEDGE_ROOT/asset-library/`，并补未配置时的降级口径（按 `../../skill-knowledge/README.md` 的降级规则跳过检索并登记，不伪造命中） | 用户 2026-10-18 要求可移植 / 换机可用 | ✅ 已确认 |
## 四、待决问题

无。
