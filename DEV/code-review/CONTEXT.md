> LEGACY COMPATIBILITY NOTICE: This file preserves historical material. The active Skill, Gate, state, artifact, and evidence rules are defined by `shared/skill-contract.md`, `shared/gate-policy.md`, `shared/anti-deadloop.md`, `shared/artifact-contract.md`, `governance/`, and `.spec/workflow.yaml`.

# CONTEXT.md —— Code-Review 术语与决策记录

> Code-Review 的术语对齐源与决策日志。references/assets 概念必须与此一致；敲定概念即更新本文件。

## 一、角色与边界

- 人设：Staff 级软件开发专家，沉淀代码评审方法论。
- 目标：评审 ../backend-dev/Frontend-Dev 代码的契约、可运行、架构、质量、安全与闭环结构。
- 边界：只审不改；业务逻辑正确性不评（交测试流程）。

## 二、术语表

| 术语 | Key | 定义 | 排除 |
|---|---|---|---|
| 代码评审 | Code Review | 后端/前端代码的结构性评审 | 不是 Tech-Review（审文档）、不是业务逻辑测试 |
| 接口契约一致性 | Contract Consistency | 路径/方法/入参/出参/错误码/分页/枚举三方一致，共享类型单一源 | 不是接口风格问题 |
| 静态验证 | Static Verification | install→tsc（或 build）→test→lint 取证 | 不是端到端联调 |
| 建议补丁 | Suggested Patch | P0 修复方向以代码块进报告，不落盘 | 不是直接改代码 |
| 六大闭环 | Six Closed-Loops | 需求/流程/状态/数据/异常/测试的代码层闭环 | 与 Tech-Review 文档层闭环同名不同义 |
| 业务逻辑正确性 | Business Logic Correctness | 规则算得对不对 | Out-of-Scope |
| 字段术语一致性 | Field Term Consistency | 名称/大小写/风格/词义一致，以 TDD+共享类型为权威 | A vs a、驼峰 vs 下划线、userId vs uid 均不一致 |
| 审查方法学 | Review Methods | case-library/review-methods.md：审查优先级/自动化/轻量/评论约定/反馈文化/反模式/AI 边界 | 不是评审清单（那是 backend/frontend-checklist） |
| 案例库 | Case Library | case-library/：review-methods + 同行样本 | 借鉴不照搬，本 Skill 双视角+契约专项优先 |

## 三、决策日志

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 2026-09-02 | 只审不改，P0 附建议补丁（代码块） | 保持独立立场，修复由用户裁决 | ✅ 已确认 |
| D-02 | 2026-09-02 | 可运行性走静态验证 B 档 | 契约错误可静态证伪；业务正确性由测试承接 | ✅ 已确认 |
| D-03 | 2026-09-02 | 核心目标 = 接口契约一致性 | 用户主要目的是防契约对不上 | ✅ 已确认 |
| D-04 | 2026-09-03 | 字段术语一致性（大小写/风格/同义词）列 P0 | 用户补充防 A/a 错误 | ✅ 已确认 |
| D-05 | 2026-09-05 | 防死循环补轮次上限 3；description 输入基线同步 | 体检逻辑闭环 P0 + 术语一致 P1 | ✅ 已确认 |
| D-06 | 2026-09-05 | 注入 review 独立性：独立上下文、不参考生成过程、可换模型交叉 | Vibe Coding 心法 4；评审类适用 | ✅ 已确认 |
| D-07 | 2026-09-08 | 新增 case-library（review-methods 审查方法学 + agent-skill-samples 同行样本） | 用户提供代码审核案例库资源清单，要求系统增强 | ✅ 已确认 |
| D-08 | 09-09 | 体检修复 6 项：原型布局清单术语；输入基线补设计稿视觉基准（双基准）；验证跑不了弯引号；role-template 补 F1-xx 前端编号；README 产物目录移出目录树；验证链 tsc/build 二选一（CONTEXT）+三招收口 shared + issue-list 薄壳化（R9） | 全仓冗余专项体检（用户裁决全量修复 + R9 评审模板参数化） | ✅ |
| D-09 | 09-10 | 门禁闭环改造 + 双向沉淀：①支持分端单批（⑬-后 只审后端 / ⑬-前 前端视角 ∥ Fidelity-Review 并行，问题合并同一清单、共用轮次）；②新增步骤 9「双向沉淀判定」（方向 A 改 ../backend-dev/Frontend-Dev 防复发；方向 B 本 skill `references/known-issue-patterns.md` 加模式含检出方法）；③超限动作由「停下交用户」改「强制清 P0 后放行，残留 P1 记遗留」；④新增 `references/known-issue-patterns.md` 案例库并在步骤 3 对照；⑤资源清单/README/错误表/description 同步 | 用户要求评审-修复-再评审循环到清零才进下一节点 + 前端代码评审固定带还原度 + 问题双向沉淀反哺 skill | ✅ |
| D-10 | 09-10 | 吸收 sanyuan-skills（code-review-expert）精华：①双视角清单扩为 A~M 组——后端新增 F5~F9（TOCTOU/乐观锁/分布式锁/计数原子/缓存一致性）、H5~H10（SSRF/路径穿越/越权IDOR/原型污染/加密凭据/资源耗尽）、K 性能与缓存、L 边界条件、M 删除候选；前端新增 K 性能与渲染、L 边界与长内容、M 删除候选，并扩充 H4~H5（越权前置收敛/危险注入面）；②每组加「提问式引导 Ask」+ 大文件 TOC；③新增 `references/removal-plan-template.md`（安全删 vs 延后删 + 删除前检查清单）；④流水线新增步骤 4「删除候选与清理计划」（只给计划不代删）；⑤新增「零问题也必须说明覆盖边界」（铁律 5 + 步骤 7）；⑥新增「大批量分批」策略（>500 行先按模块汇总再分批）；⑦严重度典型示例补安全/竞态/N+1；⑧description 补触发词「清理死代码」；⑨顶部加 IRON LAW | 用户要求吸收三元 skill 精华反哺本仓库（来源：sanyuan-skills / code-review-expert，MIT） | ✅ |
| D-11 | 09-10 | **结构重构（统一骨架）**：章节 10 → 7——§一 定位与铁律（IRON LAW + 铁律瘦身 8 条 + **两条强制收尾口径**：零问题也要说明覆盖边界 / 未运行验证不得声明通过）；§二 输入与前置（输入表 + 批次裁剪 + 大批量分批 + **视角分工表**）；§三 主流程 9 步；§四 评审规范 4.1~4.4（六大闭环 / 六项正确性 / 严重度分级 / 静态验证规程，把原先分散在 §二·§三·§五·§六 的规范归并）；§五 错误表 / §六 资源 / §七 埋点。old-vs-new 审计：原 10 章内容全部有归属，无功能丢失 | 用户要求：整理成顺畅流程（Skill-Optimizer 全量体检） | ✅ |
| D-12 | 09-15 | 视觉基准口径纠偏：§二输入表「原型 HTML」由「还原基线」改「**结构基线**（不作视觉基准）」、「设计稿（可选）」改「**视觉主基准**（含 token 对账；缺失则明示降级）」；`frontend-checklist.md` D 节标题「原型还原」→「**还原（结构对原型 / 视觉对设计稿）**」、D2 改对设计稿、D3 补 token 对账、新增 D5（证据须为设计稿并排截图）；`role-review-template.md` 评审基线与维度分组同步 | 用户反馈设计稿 OK 但实现页差别大；Code-Review 前端批次固定并行 Fidelity-Review，自身检查项须同口径（配合 Frontend-Dev D-16 / Fidelity-Review D-22） | ✅ |
| D-13 | 09-15 | 全仓一致性纠偏：README 流程改分端单批 9 步并补删除候选/闭环复核与沉淀判定；summary-template 补沉淀判定节（SKILL 承诺未落地）+ ⑬-前 沉淀归口说明；role-review-template 补修复判据列 + 覆盖 A~M（原漏 K/L/M）；known-issue-patterns 补表头、编号归位 1/2、步骤号纠正、去占位注释 | 四代理并行七维体检 | ✅ |
| D-14 | 09-17 | 吸收外部精华：`frontend-checklist.md` 新增「N. 界面质量（a11y / 表单 / i18n / 水合 / 动效）」8 项可静态检出项（aria-label / label / focus-visible / 图片宽高 / transition:all / Intl / 水合 / 反模式扫描）+ 目录行 + Ask 提问，覆盖 A~M 之外的界面质量域 | 用户要求吸收外部前端设计 skill 精华（vercel web-design-guidelines 等）；规则全集见 Frontend-Dev `references/web-interface-quality-guide.md`，本组只取可静态检出面 | ✅ |
| D-15 | 09-17 | 体检修复（本次吸收后自检）：SKILL 两处「A~M 组」→「A~N 组」（步骤 3 / 资源清单），与 frontend-checklist 新增 N 节同步 | Skill-Optimizer 模式④体检（判据=全文件「A~M」清零） | ✅ |

| D-16 | 2026-09-19 | §4.1.0「M6 资产与契约检查」→「外部 AI 知识库」：新增第⑥项「零冗余并列」（未检索/未适配即新建与库内既有资产并列重复的组件，防冗余硬性条件），冗余并列升 P0；补调度侧引用层与映射表指针（仓库根 ../../skill-knowledge/） | 用户拍板：AI 组件统一外部仓 skills-knowledge，防冗余为硬性条件 | ✅ |
## 四、待决问题

无。
