> LEGACY COMPATIBILITY NOTICE: This file preserves historical material. The active Skill, Gate, state, artifact, and evidence rules are defined by `shared/skill-contract.md`, `shared/gate-policy.md`, `shared/anti-deadloop.md`, `shared/artifact-contract.md`, `governance/`, and `.spec/workflow.yaml`.

# CONTEXT.md —— Skill-Optimizer 术语与决策记录

> Skill-Optimizer 术语对齐源 + 决策日志。

## 一、角色与边界

- 人设：Skill 运维 + 迭代器。
- 目标：把运行问题沉淀为 skill 改进。
- 边界：不参与业务交付；只优化 skill 本身。

## 二、术语表（节选）

- 问题池：`../../issue/` 唯一事实源；问题=优化点（非交付物缺陷）；埋点=主通道，兜底记录=补记。
- 评审闭环沉淀：门禁闭环放行后的沉淀判定产出；issue 来源字段可填「评审闭环」，必填**双向落点**——A 产出方 skill（防复发）/ B 评审 skill（检出力，`references/known-issue-patterns.md` 案例库）。
- 错误模式池：`../../bug-patterns/`（09-07 新增，位置经 D-11/D-12 两轮修正后**终定源仓库根集中池**）记录各项目真实 bug 的可类别化错误模式 + 防复发规则，区别于 ../../issue/；写入方 Bug-Fix（任意被修项目直接写入本池），提炼方模式③-附加（本仓库一处读取）。
- 挖掘/信号：从聊天提取四类信号聚合为问题。
- 沉淀：../../issue/案例卡状态已沉淀/已提炼，强制填目标+位置；标准=五份强约束；全方位优化=八维；编写规范=skill-writing-standard。
- 简洁不落俗 vs 省：省管结构体积，简洁管行文。
- 自我指涉=先己后人；自洽体检=七维只出清单不改；沉淀约定=一类问题 + 先源仓后 CodeBuddy。
- 触发词 eval：量化触发准确率——生成触发样本（正/负/边界）→盲测→假阳假阴→≤5 轮迭代调 description。
- 安全审计：体检第七维——危险指令/硬编码凭据/依赖/外联风险，带脚本的 skill 重点查。
- L1~L4 四级加载：L1 元数据/L2 指令/L3 引用/L4 脚本，渐进式披露省 Token。
- old-vs-new 能力审计：优化收尾对比改动前后能力清单，防丢功能/引入未声明行为。

## 三、决策日志（节选）

| # | 日期 | 决策 |
|---|---|---|
| D-01~13 | 09-04~05 | 边界/池/埋点/自我指涉/状态机/等级/标签/挖掘输入/四维优化/标准先行/死循环对策/自洽体检/自身体检修复 |
| D-14~15 | 09-05 | 优化四维→八维 + 编写规范 + 心法映射表 |
| D-16 | 09-05 | 心法 7 类→13 类 |
| D-17 | 09-05 | 沉淀约定（一类问题 + 先源仓库再同步 CodeBuddy） |
| D-18 | 09-05 | 全仓通用：确认点逐条列清单 + 引导式提问 |
| D-19 | 09-07 | 双问题池：新增 ../../bug-patterns/（真实 bug 错误模式，区别于 ../../issue/ skill 自身问题）；写入方 Bug-Fix、提炼方模式③ |
| D-20 | 09-07 | 模式③-附加提炼：错误表加行→references 防复发清单→Gate 预检项逐层升级 |
| D-21 | 09-07 | 池位置一度误改「随被修项目走」（各项目根 + 跨项目拉取），后经用户澄清推翻（用户澄清：集中一处处理而非各项目拉取；⚠️ 已被 D-22 取代） |
| D-22 | 09-07 | 池位置终定：../../bug-patterns/ 集中池在 skill 源仓库根，各被修项目修复时统一写入本池，用户在本仓库一处定期提炼 | 用户最终拍板「直接写入 tenger-skills，我只需在这里定期处理」 | ✅ |
| D-23 | 09-08 | 模式③ 触发精准加量化 eval（生成样本→盲测→假阳假阴→≤5轮）+ 流程加 old-vs-new 能力审计；模式④ 体检六维→七维（加安全审计）；skill-writing-standard §二 显式 L1~L4 四级加载 | 用户提供 Skill 优化元技能参考（skill-creator 2026/ima 触发词实战/skills-security-check/daymade fork/浙大论文）；增量补强不推翻四模式/八维框架 | ✅ |
| D-24 | 09-09 | 体检修复 2 项：CONTEXT Q1 埋点落地关闭；instrumentation-guide 过时括注删除；根 README 六维→七维同步（2 处）+ ../../shared/ 公共约定目录落地（anti-deadloop/browser-policy/socratic-grilling-core/baseline-terms/dev-common/templates×3） | 全仓冗余专项体检（用户裁决全量修复 + R9 评审模板参数化） | ✅ |
| D-25 | 09-09 | 终检修复 1 项：instrumentation-guide「skill 侧只留一行引用」→「保留统一句式引用节」（与实物一致）；根 README 终检同步（.spec 树补 bug修复/与接口性能清单、原型评审四维注释、TDD/FTDD 补「方案」、技术方案评审补任务清单） | 全仓终检（冗余专项体检修复后复审，用户裁决全修） | ✅ |
| D-26 | 09-10 | 评审闭环沉淀接入：issue 来源新增「评审闭环」（门禁闭环当场改不了的项）；模板加「双向落点」段（A 产出方 / B 评审方）；模式③-附加扩为双来源（../../bug-patterns/ + 评审闭环沉淀项），来源二按双向落点分别落 A 产出方防复发规则与 B 评审方案例库 `known-issue-patterns.md`；沉淀约定加「双向」；错误表加 2 行；资源清单加 `../../shared/templates/known-issue-patterns-template.md` | Workflow 门禁闭环改造配套（用户要求评审问题沉淀反哺 skill） | ✅ |
| D-27 | 09-10 | 模式③ 优化「门禁闭环改造」涉及的 15 个 skill（八维核验）：核出并全修 6 条——P1：UI-UX-Review 步骤 7 单条约 400 字混装（拆为「任务清单 + 归档」与「双向沉淀判定」两步，流程 7→8 步）；P2：7 个产物 skill 复核句措辞不统一（统一为「回填后须触发 X-Review 复核，不得自判通过（规则见 shared §一/§二）」）、3 个评审 skill description 缺「超限清 P0 后放行」表述（补齐）、6 个评审 skill 沉淀段字段表述不一（统一薄壳 + 指向案例库模板）、Workflow description「循环门禁」改「门禁闭环」、Workflow 节点速查表补「按执行顺序」说明。issue 池无待处理项；全部 SKILL ≤127 行（红线 500）| 用户要求用优化 skill 优化刚落地的门禁闭环改造 | ✅ |
| D-28 | 09-10 | 吸收外部精华（用户指定 sanyuan-skills，MIT）：①标准层——`assets/skill-writing-standard.md` 加目录 + 关键词轰炸四维（§一）+ references 组织四条（按领域/一层/标注何时加载/>100 行加 TOC）+ 信息单一归属（§二）+ Iron Law 置顶写法（§3.1，附 5 领域示例）+ Red Flags 撤退机制（§3.2）+ 懒惰默认值挖掘法（§3.4）+ 自由度匹配脆弱度（§3.5）+ 确认门四类触发 + Pre-Delivery 可验证判据（§四）+ 新增 §七「外部做法的采纳与不采纳」；②元技能层——`optimize-checklist` 维度二~六按新判据补全，`self-audit-checklist` 加输入三方式 + 输出「先列 ≥2 条优点」+ 新增「元反模式」5 条，SKILL.md 模式④流程同步 + §七 加「外部参考吸收留痕」+ 顶部加 IRON LAW；③具体 skill 层——Code-Review 见其 D-10。不采纳项记入 §七（禁 README / 加 P3 级 / 强制参数体系），防重复讨论 | 用户提供 sanyuan-skills 要求吸收精华反哺本仓库 | ✅ |
| D-29 | 09-10 | **防凌乱机制「归位原则」**（用户要求把结构凌乱的根因计入优化 skill）：根因 = 每轮吸收都把新内容**追加到最近的地方**（末尾补一节 / 加「附」/ 塞进某步末行）而非归位。① `assets/skill-writing-standard.md` **新增 §八**——四条规则（先问归属再落笔：主流程某步 / 规范 §4.x / 铁律 / references，找不到归属 = 结构缺一类先补结构；禁止 `三·附`、`-附加` 等补丁式章节名；三份清单分工（铁律 = 红线 ≤8 / 错误表 = 易犯错 + 纠正 / §4.x = 判据）；被连续追加 ≥3 次的小节要拆分或下沉）+ **归位自查三问**；② `optimize-checklist` 维度六加「归位检查」判据 | 用户：skill 是吸收各方优点汇总易凌乱，需防后续沉淀再凌乱 | ✅ |
| D-30 | 09-10 | **全仓 16 个 skill 结构重构收口 + 体检**（用户裁决：全量铺开 + 接受重排 + 铁律瘦身 ≤8）：统一 7 章骨架，总行数 **2419 → 1528（-37%）**，每个 skill 均做 old-vs-new 能力审计（无功能丢失）；过程中补上 `Prototype-Review` / `UI-UX-Review` 原本缺失的「错误表」「资源清单」。**体检发现并修复 4 处跨位置失同步**：① `prd-design/README.md` 决策编号 D-24→D-30；② `prototype-design/README.md` D-16→D-18；③ `ui-ux-design/README.md` D-21→D-25 且「9 步 3 Gate」→「9 步 4 Gate」；④ 根 README 的 `../../shared/` 清单补 `evidence-before-claims` / `receiving-review`。核验：各 SKILL.md 内部 §X 交叉引用全部指向存在章节、铁律条号引用 8 处全对、`../../shared/` 11 文件齐全（`references/assets` 报告的 missing 均为跨 skill 引用的正则截断误报） | 用户要求：体检 → 无问题则提交并同步 CodeBuddy / Codex | ✅ |
| D-31 | 09-15 | 体检清单增强（防复犯）：维度二补「声明-承接」检查项（SKILL 声明有、assets 模板未承接 = 断头）与「中央约定不重复」检查项（../../shared/*.md 已声明唯一权威者，各 skill 只引用不复制）；维度五最常失同步处补「轮次超限口径、设计稿/原型基准归属」；沉淀落点改为「生效客户端副本」表述 | 本次全仓审计暴露两类系统性漏检：跨文件承诺未落地、中央约定被下游重复定义 | ✅ |
| D-32 | 09-16 | 沉淀约定新增 §七-6「**落点分层**」：用户要「沉淀成标准流程/后续都按此执行/提高质量」→ 必须落目标 skill 主流程强制位（SKILL.md 步骤内 REQUIRED/Gate/错误表行），案例库/references 只作正文附件并标注主流程引用点；仅落案例库=未完成；判据=「下次不读这篇参考是否就会照旧做错」 | 用户澄清正面案例沉淀本意是标准 SOP 而非案例入库，暴露沉淀约定无落点分层判据（../../issue/Skill-Optimizer/2026-09-16/01；配套 Frontend-Dev 主流程 SOP 化见其 CONTEXT D-18） | ✅ |
| D-33 | 09-16 | 体检修复：落点分层规则引用编号全仓纠偏——规则实际落「七、沉淀约定」第 6 条，5 处引用误写「§七-8」或「第 8 条」（Frontend-Dev CONTEXT D-18、本 CONTEXT D-32、../../issue/Skill-Optimizer/2026-09-16/01 两处、../../issue/Frontend-Dev/2026-09-16/02 两处），统一改为「§七-6」 | Skill-Optimizer 模式④体检，用户裁决全修；判据 = 全仓「七-8」grep 清零 | ✅ |
| D-34 | 09-17 | 吸收外部精华（第二批 · 前端设计类 7 来源，用户确认全量执行）：①标准层——`assets/skill-writing-standard.md` §七 追加来源二（anthropics frontend-design / impeccable / taste-skill / emil-design-eng / vercel agent-skills / ui-ux-pro-max / awesome-design-md）与已采纳点（动效设计工程、动效实现技法、Web 界面质量规则集、设计读声明、AI Slop Test、动效强度档入风格决策）+ 不采纳表 6 行（taste 版式重排类 / 三 Dials 整搬 / ui-ux-pro-max 脚本数据库 / impeccable 30 场景整搬 / 54 品牌入库 / emil 进阶技法整搬）；②具体 skill 层——UI-UX-Design D-28、Frontend-Dev D-20、Fidelity-Review D-23、Code-Review D-14、Frontend-Tech-Design D-19 | 用户提供 7 个外部前端设计 skill 要求吸收精华沉淀到对应 skill（本地插件市场 4 个 + GitHub 镜像克隆 3 个：emilkowalski/skills、Leonxlnx/taste-skill、vercel-labs/agent-skills） | ✅ |
| D-35 | 09-17 | 体检判据升格（当天体检实战教训，用户确认）：①维度五新增「**范围引用同步**」——扩展清单 / 枚举后全仓 grep「范围引用」（「A~M 组」「12 条」「六查」类）同步；②维度五新增「**同批吸收后跨文件口径比对**」——多文件批量改动后对同类数值 / 口径跨文件 grep（防「<300ms」与「200-500ms」张力类）；③元反模式新增「过程已发现的问题未全部进清单」 | 来源：前端设计精华吸收 + 当天体检（UI-UX-Design D-29 / Frontend-Dev D-21 / Fidelity-Review D-24 / Code-Review D-15 / UI-UX-Review D-17）暴露的三类失同步 | ✅ |
| D-36 | 09-18 | **进化引擎接入**：新建 Skill-Evolver（链外，全功能闭环：信号采集→偏好库→触发→诊断→方案→确认后执行，仓库根 `../../evolution/` 集中池）；本 skill三处改动——定位行声明「模式②遇偏好类信号、模式③执行优化时内部调用」；模式②加第 4 步**分流**（偏好/行为习惯类信号 REQUIRED SUB-SKILL 交 Skill-Evolver，判据「这是用户的稳定偏好吗」）；模式③加进化管线接入说明（依据含偏好信号或需读轨迹定因时走其 ④⑤⑥，双留痕）；资源清单补 `../../evolution/` 池与关联 skill | OSS-Radar 首轮定向调研（深读 6 repo：hermes-self-evolution/GenericAgent/OpenViking/GEPA/claude-mem/evolver，报告 `.spec/开源情报/2026-09-18-skill进化器调研.md`）+ 用户拍板「全功能 skill + Skill-Optimizer 内部调用 + 默认档位确认后改」 | ✅ |

| D-37 | 2026-09-19 | 模式②挖掘输入源补第三通道：运行期日志/监控问题记录（server-log / server-monitor / web-monitor 导出），标注为正向循环第二入口——与门禁评审闭环并列的问题来源 | 用户拍板：日志/监控记录的问题回流优化 skill 或对应项目 | ✅ |
| D-38 | 10-08 | 两份共享约定提升出本 skill：`references/instrumentation-guide.md` → 仓库根 `shared/instrumentation-guide.md`、`assets/issue-template.md` → `shared/templates/issue-template.md`（二者被 16 个 skill 的埋点章节共用，留在私有目录时安装副本扁平布局下 `../` 解析必断）；SKILL.md「标准先行 / 沉淀约定 / 资源清单 / 埋点」四处引用同步改指 shared，README 目录说明更新；写法归一落 `shared/skill-contract.md` §1.4（只允许 shared 相对路径与 `<skill-id>/…` 逻辑引用，禁带分类层），门禁落 `scripts/check-installed-refs.py`（已接入 `validate-reference-integrity.ps1`）；`Skill/skill-lifecycle` 自带的同名 `assets/issue-template.md` 属其便携包私有，保持不动 | `issue/Skill-Optimizer/2026-10-08/01`（跨 skill 引用两视图互不成立；用户裁决统一到小写 id + 共享资产进 shared） | ✅ |
| D-39 | 10-09 | **模式 3 补可执行检出方法（触发网脆弱专项）**：`references/known-issue-patterns.md` 模式 3 典型现象增第二种载体「description 用封闭名词枚举，用户换未列举形态名词即失配」；检出方法由 ① 扩为 ①②③——② 取各 skill `description`，对换形候选词（Agent／智能体／知识库／RAG／系统／平台／服务／后台／小程序／图谱）逐个 `grep -c`，判「穷举白名单」vs「类别判据 + 开放示例」，判据 = **命中与否是否取决于用户说出被列举的那个名词**，穷举即报「入口触发网脆弱」并关联 `issue/WorkFlow/2026-10-08/01`；③ 核对 `docs/task-scope-regression.md` 回归场景是否只锚定单一形态名词（只跑一种说法就标 ✅ = 假绿）；修复方向恒为改类别判据，**禁止用「再补几个名词」收口**；同日试跑后补 ④ **失败分型**——漏触发先取同句重跑 ≥2 次定性：重跑有命中且命中样本引用了判据即**随机漏检**（判据可达、裁决抖动），改 description 无效，兜底须落在「选中 skill 之前」就生效的宿主全局指令层；重跑也不命中才回到 ② 判不可达改写法。试跑口径升格为**每形态 ≥2 次独立会话**，单形态 n=1 不得标 ✅ | 09-23 的修复方式（往 description 里穷举形态名词）本身即 10-08 第三次复发的根因；本条为 B 方向（检出力）落点，A 方向落 `WorkFlow` D-23 | ✅ |

| D-40 | 2026-10-10 | **编排层案例库 +模式 5「闸门失守 / 基线作废未清点」**（`references/known-issue-patterns.md`）：与模式 4 划界（4 = 上游产物**不存在**被写成中性说明；5 = 上游产物**存在且曾批准**，被关闸或作废后无人执法）。检出方法四条——① 指针 vs 闸门比对（`manifest.yaml` 中 `gate != PASS`／`allowDownstream: false` 条目 与 `currentState`／`nextAction` 所指阶段）；② 基准版本比对（下游产物声明所依据的上游版本 vs 上游当前 `version`／`status`）；③ mtime 时序（DEC／PRD 版本行 mtime vs 下游产物 mtime，作废早于产出而产物未标废即命中）；④ **量具可达性核查**（对项目实跑 `python scripts/validate_core.py gate --project-root <项目>`，解析失败即判「Gate 从未被机械校验」，按成因升级并另登 issue）。同批 A 方向落 `WorkFlow` D-24、`UI-UX-Review` D-19、`UI-UX-Design` D-37，两条 issue 状态回填「已沉淀」；并新登记 `issue/WorkFlow/2026-10-10/02`（P0：业务项目 `.spec/` 控制文件偏离 v2 契约模板——`manifest:` 包裹、`id` 非 `artifactId`、`status` 用 `REGISTERED`／`READY`／`APPROVED_SUPERSEDED` 等枚举外值、缺 `lifecycle`／`owner`／`producedAt`、重复 key `sourceRefs`、`workflow.yaml` 无顶层 `gate`，致校验器直接解析失败；含 8 步项目侧迁移动作清单，待单独授权） | `issue/WorkFlow/2026-10-10/01` 双向落点 B（编排器无上游评审方，按 `issue/README.md` 出口②收敛到本 skill 案例库）；方法④ 由本轮落地时的真实项目实测暴露 | ✅ |

| D-41 | 2026-10-10 | **评审节点承接位对称补齐**（收掉 D-40 之后我自己在 issue 台账声明的「未覆盖边界」）：`shared/templates/review-summary-template.md` 新增 **§0 上游闸门核对与本轮 Gate**（四字段核对表 + 时序核查 + Gate 字段块 + 「判据全闭 ≠ 放行」「不得用注释承载限定」）——编号取 §0 前置，不重排原 §1~§6，防跨文件引用断头；`tech-review` D-10／`code-review` D-17／`prd-review` D-12／`prototype-review` D-09 各自主流程输入步（或 Preconditions）加**同一条**〔REQUIRED · 开工前闸门核对〕，4 份 `assets/summary-template.md` 结构基线行加 §0 硬性小节指针；`ui-ux-review` 的 §〇 标注为公共 §0 的领域实例（行按本域定制、四字段判据同口径）。`code-review` 保持铁律 5「不设门禁」——只报关闸事实交回 Workflow 判停，不自判放行 | 判据按 §七-6 落点分层：「下次不读这篇参考是否就会照旧做错」= 必须进主流程 + 模板承接位，只落 shared 文字判据属规则空转（本轮 5 个评审节点中仅 1 个有核对表，正是该落差）；用户裁决「先要解决这些问题」 | ✅ |

| D-42 | 2026-10-10 | **试跑量具自污染入案例库（模式 6）+ 入口兜底扩到「续做类」请求**：① `references/known-issue-patterns.md` 加模式 6「试跑量具自污染」，四种载体（cwd 未锁 / 答案泄漏 / 信号未隔离 / 入口未命中却计入结论）+ 起会话前的四问 + 跑后 hash 比对判副本污染；② 行为验证轮实测出真因：Qoder 侧入口兜底存在（auto-memory `reference-entry-routing-guard`）但索引 description 只写「期望存在的软件能力」，**「把 TDD 补齐、按现状推进」这类续做请求匹配不上 → 记忆不会被打开 → `workflow` 未被选中 → §6 闸门规则一行都读不到**。修法是扩类而非加词：判据从「要不要新东西」改成「这一步会不会跨阶段」，并明确「只做流程判断/只登记状态」不构成轻量豁免；同步改 `~/.zcode/AGENTS.md` 同一处（宿主级兜底，仓外）；③ 隔离样本 `s3-drifted-c`（schema 漂移但 `gate: PASS/true`）专测「量具跑不通即停」，与闸门信号解耦 | `issue/WorkFlow/2026-10-10/01` 行为验证轮（3 会话 2 个未加载 `workflow`、1 个改扫真实项目并引用本轮刚写的 issue 文件 = 开卷）；`issue/WorkFlow/2026-10-08/01` R4 随机漏检的同族证据（n=2，且给出「记忆索引 description 决定记忆是否被打开」这一具体机制） | ✅ |
| D-43 | 2026-10-18 | **挖掘输入源排序（承接 `issue/Skill-Optimizer/2026-09-15/01`）**：模式②第 1 步改为「项目 `.spec/` 评审/测试问题文档 + git log（全量已蒸馏）→ rollout jsonl（仅近段证据/错误签名）→ chats 手工导出」并加「滚动记录不能当全量问题史」；第 3 步要求每条标注证据来源类型；`chats/README.md` 补两 caveats（轮转丢历史、跨项目混存）＋导出须标项目名 | 实测 103 条 user 消息里首条任务书已不存在，同目录混存其他项目 | ✅ 规则已改｜◐ 真实挖掘复跑未做 |

## 四、待决问题

Q1 已完成（埋点已落地全部 skill，2026-09-09 体检确认）；Q2 已定（500 行红线）。


## 2026-09-21 问题记录修复（D-RECORDING-20260921）

- 依据：`issue/Skill-Optimizer/2026-09-21/01-试跑前问题记录入口与聚合台账接线不完整.md` 与 `02-收尾式埋点缺少已观察异常的及时持久化规则.md`；用户指令「修复问题」。
- 决定：共享记录规则统一下一安全节点落盘、一事一源、最小索引、恢复与复核；所有注册 Skill 入口显式接入，重点补 auto-test / Code-Review + Fidelity-Review / defect-triage。
- 不做：新增后台服务、默认跨仓写入、同步安装目录、解除正式 Gate、变更 Superdesign 设计流程。
- 复核：静态接线测试见 `scripts/tests/test_problem_recording.py`；实际 Agent 行为与中断恢复仍按 `docs/task-scope-regression.md` 试跑，不能用静态通过代替。
- 回退：只撤销本次记录入口段、共享记录规则及配套模板/消费者修订；保留问题事实及此前用户修改，不执行整文件 Git 回退。
