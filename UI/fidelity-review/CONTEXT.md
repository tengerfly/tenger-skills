# CONTEXT.md —— Fidelity-Review 术语与决策记录

> Fidelity-Review 术语对齐源 + 决策日志。

## 一、角色与边界

- 人设：资深前端 UI 验收专家。
- 目标：实现页 vs 设计稿逐页还原度评审（视觉/交互/长文案）。
- 边界：只审不改；不评业务逻辑（auto-test）、契约/架构（Code-Review）、设计稿本身（UI-UX-Review）。

## 二、术语表

| 术语 | 定义 | 排除 |
|---|---|---|
| 页面还原度评审 | 实现页 vs 设计稿的分级问题清单 | 不是设计稿评审/代码评审 |
| 还原度 | 实现页对设计稿的忠实程度 | 不是开发期还原基线 |
| UI 设计稿 | A：`.spec/设计稿/`（**视觉唯一应然**）；B：外部稿；C：无设计稿**且已登记用户批准例外 EXC** 才回退原型（降级，结论须标 EXC 出处） | 不是原型/实现页 |
| 基准通道 | A 优先（token 可机械比）；B 目测并标注；C 原型兜底（**视觉质量降级，不得据此判视觉达标**） | 不是任选其一；**原型不当视觉基准** |
| token 搬运对账 | design-system §7 ↔ 实现 `styles/variables` 逐条核对（条数/值/命名）+ computed style 断言 | 不是只看截图目测 |
| 视觉/交互还原 | 视觉一致 / 可点+反馈+方式一致 | 交互不含业务正确性 |
| 超长文案专项 | 长文案下样式是否崩 | 不是文案一致性 |
| 截图必证 | 样式/视觉/溢出必配截图 | 硬性产出 |
| 任务清单/轻量清单 | 独立模式任务闭环；auto-test 场景就地 mini-issue | 轻量清单无状态机 |
| 边界造条件 | 长文案/暗色/窄屏主动触发 | 不只 Happy Path |
| 读结构驱动交互 | snapshot 元素树驱动点击 | 不替代截图 |
| 精确判定工具 | axe-core 算对比度等 | 不替代 AI 观感 |
| 决策规则 | decision-rules.md：像素容忍度分级/断点/diff阈值/attempts/token绑定/交互量化（Decision Rules）；补「量化」维度 | 不重复六大铁律 |
| 案例库 | case-library/：pixel-methods + 同行样本（Case Library）；借鉴不照搬 | 双通道+截图存证优先 |

## 三、决策日志

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 09-05 | 命名 Fidelity-Review，产物 `.spec/页面还原评审/` | 与 UI-UX-Review 区分 | ✅ |
| D-02 | 09-05 | 双通道设计稿基准 | 既要接流水线也可独立用外部稿 | ✅ |
| D-03 | 09-05 | 独立专项 + Testing 内嵌 | Code-Review 只管代码层 | ✅（Testing 已归档，现为 auto-test 场景） |
| D-04 | 09-05 | 视觉 + 交互（全量+普适项） | 用户补交互问题 | ✅ |
| D-05 | 09-05 | 超长文案专项 | 用户点名典型场景 | ✅ |
| D-06 | 09-05 | 双模式交付 | 独立闭环 + Testing 内嵌 | ✅（Testing 已归档，现为 auto-test 场景） |
| D-07 | 09-05 | 浏览器硬依赖 | 视觉/交互必须真实渲染点击 | ✅ |
| D-08 | 09-05 | 只审不改 + 防死循环三招，沿用家族模板 | 统一评审类 | ✅ |
| D-09 | 09-05 | 承接 UI-UX-Review Q1：独立成 skill | 阶段/对象不同，独立最清晰 | ✅ |
| D-10 | 09-05 | PRD 回溯统一走速查表入口并同步四处 | 全仓约定补齐 | ✅ |
| D-11 | 09-05 | axe-core 精确判定 + 暗色/窄屏 + 读结构驱动 | 秘籍 UI 测试增强 | ✅ |
| D-12 | 09-05 | README D 编号同步 D-01~D-11 | 跨位置失同步 | ✅ |
| D-13 | 09-05 | 补独立走查纪律（不参考实现过程） | 全仓评审独立性对齐 | ✅ |
| D-14 | 09-07 | 页面级截图外增加逐区块断言（字号/空态/方向/居中/状态重置/文案/icon） | 学径复检漏检：用户逐条发现区块级偏离 | ✅ |
| D-15 | 09-08 | 状态检查扩为 10 大 UI 状态双向对照（design-system §5.10 状态稿逐态还原一致；实现页多出的状态表达=加戏）；字号阶梯出处入检 | 外部方法论 ui-ux-design.md；与 UI-UX-Design 状态规范对齐 | ✅ |
| D-16 | 09-08 | 体检修复：SKILL §一视觉还原面与 §四 P1 严重度「三态」→「状态（含 10 大 UI 状态）/状态缺失」，与 visual-checklist §六 十态口径统一 | Skill-Optimizer 模式④体检（六维机械核验） | ✅ |
| D-17 | 09-08 | 全仓体检修复：SKILL §二通道 A「高保真 HTML」→「设计稿 HTML」（全仓废弃术语「高保真」业务残留清零） | Skill-Optimizer 模式④全仓体检 | ✅ |
| D-18 | 09-08 | 新增 decision-rules（像素容忍度/断点/diff阈值/5-attempts/token绑定/交互量化）+ case-library（像素方法学/同行样本） | 用户提供样式还原度审查案例库资源清单，要求系统增强；借鉴 lobehub visual-pixel-perfect | ✅ |
| D-19 | 09-09 | 体检修复 5 项：README 三态→10 大 UI 状态（D-16 落地补全）；mini-issue §四、report §四/§七节号修正；overflow Scope Gate 表述修正；decision-rules 六大铁律括号修正；三招/浏览器策略/双基准收口 shared 引用 + issue-list 薄壳化（R9） | 全仓冗余专项体检（用户裁决全量修复 + R9 评审模板参数化） | ✅ |
| D-20 | 09-10 | 门禁闭环改造 + 双向沉淀：①新增模式三「代码评审场景」——⑬-前 与 Code-Review 前端批次**并行**，报告落 `.spec/代码评审/前端页面还原度评审.md`、问题交 Code-Review 合并进同一任务清单（标来源=Fidelity-Review），不单独确认/计轮次，双向沉淀交 Code-Review 统一执行；②超限动作由「交用户」改「清 P0 后放行」；③独立模式补双向沉淀判定；④步骤 4 补案例库对照；⑤新增 `references/known-issue-patterns.md` + README/错误表同步 | 用户要求前端代码评审固定并行还原度审查、并纳入同一循环门禁 | ✅（已撤销：按 shared/anti-deadloop.md §3，残留 P0⇒BLOCKED、P1⇒仅授权 CONDITIONAL） |
| D-21 | 09-10 | **结构重构（统一骨架）**：章节 11 → 7——§一 定位与铁律（三评审面 + **与相邻 skill 边界表**（原 §八 上下游并入）+ 铁律 6 条）；§二 输入与前置（双通道基准 + 输入 + 三模式输出）；§三 主流程 7 步（**逐区块断言从步骤 4 抽出**）；§四 评审规范 4.1 严重度 + 4.2 逐区块断言 + 4.3 防死循环差异；§五 错误表 / §六 资源 / §七 埋点。old-vs-new 审计：原条目全部有归属，无功能丢失 | 用户要求：整理成顺畅流程（Skill-Optimizer 全量体检） | ✅ |
| D-22 | 09-15 | **视觉基准口径纠偏（P0）**：①§一新增 IRON LAW「设计稿是视觉唯一应然」——原型只作结构/存在性对照，不得用「与原型一致」判还原达标；②§一视觉还原面、步骤 1/2/3 明确基准侧截图=设计稿；③通道扩为 A/B/**C（无设计稿回退原型=降级，不得据此判视觉达标）**；④新增 §4.2.1 **token 搬运对账断言**（design-system §7 ↔ 实现 variables 逐条 + computed style，未做不得判通道 A 视觉达标）；⑤错误表加「拿原型当视觉基准判达标」「有设计稿却只与原型比对」两行；⑥`visual-checklist.md`（基准口径 + §七 token 对账）、`design-source-guide.md`（通道 C + 应然铁律）、`review-report-template.md`（视觉基准应然位 + token 对账行 + VIS-02 示例）、README 同步；⑦`known-issue-patterns.md` 由空表首填 2 条（视觉基准错用原型 P0 / token 未搬运对账 P1，含检出方法） | 用户反馈：设计稿 OK 但实现页差别大；本 skill 是唯一以设计稿为应然的第三方验收，须显式化并把「原型当视觉基准」列为 P0 模式（配合 Frontend-Dev D-16） | ✅ |
| D-23 | 09-17 | 吸收外部精华：`interaction-checklist.md` 新增「六、动效还原」（时长/缓动对 token、可打断、origin、reduced-motion、hover 门控、transition:all）与「七、界面质量可见项」（焦点可见、label、省略号规范、图片尺寸、遮挡）两节，原「六、输出」顺延为「八」；`visual-checklist.md` §一 补「固定/悬浮元素不遮挡内容与焦点」、§五 补「图片显式尺寸不引起布局跳变」 | 用户要求吸收外部前端设计 skill 精华（emil-design-eng / vercel web-design-guidelines）；实现规则全集见 `frontend-dev/references/motion-guide.md` + `frontend-dev/references/web-interface-quality-guide.md` | ✅ |
| D-24 | 09-17 | 体检修复（本次吸收后自检，用户裁决全量修）3 项：①interaction-checklist §六 时长口径统一（常规 UI <300ms、弹层 / 抽屉类据档）；②SKILL 步骤 4 括注补「动效还原 / 界面质量可见项」新节引用点；③去重：interaction-checklist §七 删图片尺寸行（归 visual-checklist §五）、visual-checklist §一 遮挡表述收窄为「不遮挡内容」（焦点归 interaction §七） | Skill-Optimizer 模式④体检 | ✅ |

| D-25 | 2026-09-19 | 调用方切换：三模式中「Testing 场景」→「auto-test 场景」（⑭ 测试节点已由 auto-test 接替，L2 视觉 E2E 内嵌本 skill；链外 Testing 备用时同理）；description/边界表/铁律/模式二/收尾/错误表同步措辞 | 用户拍板：auto-test 入仓替换 Testing（Testing 源码不动） | ✅ |
| D-26 | 2026-10-19 | **评审上下文隔离硬性化（用户要求）**：①新增「评审上下文隔离（执行必需）」节——单评审单元也必须隔离执行；被 Code-Review / auto-test 调用时由调用方派发独立评审子代理并传评审包；当前上下文参与过实现页开发/修复/自检必须派发、不得自审；无隔离能力 ⇒ `BLOCKED`。②三模式同步：模式三改「由 Code-Review 派发的独立评审子代理与 Code-Review 批次评审者并行」（description 头部与边界表同步）；主流程步骤 1 增确认隔离形态、步骤 3 删「任务重可开独立会话」改「必须隔离；无隔离能力按契约处理」。③`assets/review-report-template.md` 头部/元数据加评审上下文 + 评审包摘要与 §0.5 表；④资源清单补 `shared/review-context-isolation.md` / `shared/templates/review-package.md`；README + 错误表同步 | `issue/Skill-Optimizer/2026-10-19/01`（评审类 skill 未强制隔离评审上下文）；规则 `../../shared/review-context-isolation.md` | ✅ 规则已改｜◐ 待真实项目 fresh 派发复跑验证 |
## 四、待决问题

Q1 已解决：不设独立 Workflow 节点，auto-test 内嵌调用（Testing 已归档）；Q2 已解决：有设计稿时还原走查交本 skill，midscenejs 负责三态+基础视觉断言。
