# CONTEXT.md —— Workflow 术语与决策记录

> Workflow 术语对齐源 + 决策日志。

## 一、角色与边界

- 人设：技术项目经理 / Delivery Lead。
- 目标：一句话从任意节点起跑，随时决定继续。
- 边界：只调度、记账、守门；交付物由子 skill 产出。

## 二、术语表

| 术语 | 定义 |
|---|---|
| 节点/链 | 节点=一 skill；链=默认顺序，节点可任意起点 |
| 起点/终点/路径 | 起点可推断；终点不指定=只跑起点；路径扣除跳过 |
| 跳过 | 用户决定不做某节点，标记已跳过 |
| 前置 | 产物缺失即阻塞；门禁节点的前置含「上游门禁已放行」 |
| 交接记录 | PIPELINE 追加：产物/下游输入/遗留/用户决定 |
| 门禁闭环 | 「产物 ⇄ 评审」配对：产物→评审→修复→复核，收敛才进下行（③⑤⑦⑩⑬，分端两批 ⑩-后/⑩-前、⑬-后/⑬-前） |
| 放行判据 | P0 全已修复 + P1 全已修复（已忽略须用户确认理由）+ 复核通过；P2 记遗留不阻塞 |
| 上限 3 | 同批修复→复核满 3 轮不收敛：强制清 P0 后直接放行，残留 P1 记遗留 |
| 并行评审 | ⑬-前 内 Code-Review（前端视角）∥ Fidelity-Review，问题合并同一清单、共用轮次 |
| 沉淀判定 | 门禁放行后对问题判定是否反哺 skill：**P0 双向必沉**，P1/P2 由模型判「会再犯的一类问题」 |
| 双向沉淀 | 方向 A 产出方 skill（防复发）+ 方向 B 评审方 skill 案例库（检出力，`references/known-issue-patterns.md`） |
| 当场沉淀 / 入池 | 成因明确且改动增量 → 直接改 A/B 两个 skill（记 D-xx）；否则落 issue/（写明双向落点）交 Skill-Optimizer 提炼 |
| 子 skill | 可独立调用，不因编排改变行为 |

## 三、决策日志

| # | 日期 | 决策 |
|---|---|---|
| D-01~07 | 09-03 | 一条链任意起点/终点只跑起点/评审可跳/术语弃流水线/不设依赖分级/PIPELINE 只记本次/两处串行 |
| D-08~10 | 09-04~05 | 增 ⑤ 原型评审 → 13 节点；增 ⑥ UI/UX → 14 节点；增 ⑦ UI/UX 评审 |
| D-11 | 09-05 | Fidelity-Review 不入链，作为 ⑭ 测试内嵌 |
| D-12 | 09-05 | README 评审回退表同步 14 节点 |
| D-13 | 09-05 | 流程裁剪判据（模型越强流程越轻） |
| D-14 | 09-07 | Bug-Fix（第 16 专业）不入主链，作为链外修复闭环：承接 ⑭ 测试发现的可运行性问题，修复沉淀入源仓库 bug-patterns/ 集中池反哺方案/开发 skill（与 Fidelity-Review 同不入链惯例） |
| D-15 | 09-08 | 全仓体检修复：SKILL 补「十、运行问题埋点」节（此前 18 skill 中唯一缺失，调度/守门/PIPELINE 问题入 issue/WorkFlow/）——Skill-Optimizer 模式④全仓体检，✅ |
| D-16 | 09-09 | 体检修复 2 项：CONTEXT 决策日志 D-14/D-15 行列数修正；埋点统一格式（全仓冗余专项体检（用户裁决全量修复 + R9 评审模板参数化），✅） |
| D-17 | 09-09 | 终检修复 1 项：pipeline-template 项目信息表拆 5 列规范格式（全仓终检（冗余专项体检修复后复审，用户裁决全修），✅） |
| D-18 | 09-10 | 门禁闭环改造（用户裁决）：①每个「产物 ⇄ 评审」节点内成循环，P0 清零；P1 需修复，超限只能授权 CONDITIONAL 才能下行；②⑩/⑬ 分端两批执行（⑧清零起⑨、⑪清零起⑫）——写一个审一个；③满 3 轮不收敛 → 强制清 P0 后**直接放行**，残留 P1 记遗留（原「停下交用户」废弃）；④⑬-前 前端代码评审 ∥ Fidelity-Review 并行，问题合并同一清单、共用轮次；⑤新增门禁闭环沉淀判定（P0 必沉；优先当场改产出方 skill 防复发规则，改不了入 `issue/` 池交 Skill-Optimizer 提炼）；⑥PIPELINE 加门禁轮次/门禁结果/遗留问题段。定义权威落仓库根 `shared/anti-deadloop.md`（扩为门禁闭环口径）| 用户要求「评审-修改-再评审直到问题清零才进下一节点」+ 问题沉淀反哺 skill 正向循环 | ✅ |
| D-19 | 09-10 | 沉淀双向化（用户补充）：同一问题同时反哺两端——方向 A 产出方 skill（防复发：错误表/references/Gate 预检项）+ 方向 B **发现问题的那一个评审 skill**（检出力：`references/known-issue-patterns.md` 评审方案例库，每条含「检出方法」可执行判据）。P0 双向必沉；当场改优先（A/B 各记 D-xx、同步部署副本），改不了入池并写明双向落点。6 个评审 skill 各建案例库骨架；模板 `shared/templates/known-issue-patterns-template.md` | 用户：开发 skill 的 P0 问题应同时沉淀到开发 skill（防下次出现）与代码评审 skill（案例库，下次能查出） | ✅ |
| D-20 | 09-10 | **结构重构（统一骨架）**：章节 10 → 8——§一 核心模型（角色/目标/边界 + 流向图 + 参数表）；§二 节点速查（大表 + 硬串行）；§三 起点确定；§四 调度规程（启动 / 执行一个节点 / 交接摘要 / 阻塞格式）；§五 **门禁闭环与放行**（闭环模型 + 守门规则 + 门禁点表 + 分端与并行 + 沉淀反哺 + 裁剪判据）；§六 PIPELINE.md；§七 错误表（原「铁律」并入错误表与流程约束，消除与 §五 的重复）；§八 资源清单；§九 埋点。old-vs-new 审计：原 10 章内容全部有归属（原 §七 铁律 9 条已按职责分流到 §一 角色边界 / §四 调度 / §五 守门），无功能丢失 | 用户要求：整理成顺畅流程（Skill-Optimizer 全量体检） | ✅ |
| D-21 | 09-15 | 视觉基准口径纠偏：§二节点表 ⑫ 补「另需输入：设计稿=视觉基准、原型=结构基线；设计稿缺少不阻塞但须明示降级」（保持在「前置」列的可选语义，不与 ⑥⑦ 可选节点冲突）、⑬-前 标注「设计稿视觉唯一应然」；§五 分端与并行补「还原度判定基准：视觉以设计稿为应然、结构对原型；有设计稿却只与原型比对 = 无效还原结论」；§七 错误表加「有设计稿却按原型判视觉还原」行 | 用户反馈设计稿 OK 但实现页差别大；编排层须把基准口径写进节点契约与守门规则，避免子 skill 口径漂移 | ✅ |

| D-22 | 2026-09-19 | 主链四处改造：① ⑭ 测试节点 Testing → auto-test（产物 `.spec/auto-test/`，分层依赖口径：L0/L1 无浏览器可跑、L2 硬依赖；有设计稿时 L2 内嵌 Fidelity-Review）；Testing 源码不动，降级链外人工走查备用。② ⑧⑨ 前新增 OSS-Radar 同域开源调研步（产出 `.spec/开源情报/`，快速档/用户确认可跳过留痕；⑨ 复用 ⑧ 轮报告）——写技术方案前先看同类项目怎么做；链上子 skill 14→15。③ 资产五门禁措辞统一外部 AI 知识库（引用层+映射表在仓库根 skill-knowledge/，双仓同步），沉淀门禁增查重防冗余硬条件。④ 沉淀反哺段新增「运行期信号」：日志/监控（server-log/server-monitor/web-monitor）问题 → Bug-Fix → bug-patterns/issue 池 → Skill-Optimizer 提炼，构成正向循环第二入口；错误表 +2 行 | 用户拍板：auto-test 替换 Testing、技术方案前先 OSS-Radar、AI 组件统一外部仓+防冗余硬性条件、日志监控问题回流优化 skill/项目 | ✅ |
| D-23 | 2026-10-09 | **入口触发判据由封闭名词枚举改为类别判据**（同根因第三次复发的修复）：① frontmatter `description` 首句改为「判据按类别不按名词——用户描述『期望存在的软件能力』（要一个还不存在的东西，而非改已有代码）即入口」，形态名词（应用/产品/网站/工具/系统/平台/服务/后台/小程序/Agent/智能体/知识库/RAG/图谱/MVP/原型/Demo）显式标注为**示例而非白名单、未列举同判**，并补「模糊正是入口，不是拒绝理由」；② 正文 `Trigger` 同步加同一类别判据，防 L1/L2 口径漂移把白名单读回来。**不改判据只加名词 = 无效修复**（09-23 的修复方式即为本次复发根因）。验收口径升格：形态名词是变量，须逐个形态各起独立会话试跑（`docs/task-scope-regression.md`「2026-10-08 入口触发网形态变体」节，含轻量对照防误伤），n=1 通过不得标 ✅；三项试跑全绿前 `issue/WorkFlow/2026-10-08/01` 保持「待处理」 **试跑样本量口径**：每形态 ≥2 次独立会话，单形态 n=1 通过不得写 ✅；关闭条件相应改为「每形态 ≥2 次全命中 + 轻量对照仍走轻量档」 | 用户拍板：记问题并修改对应 skill（同根因第 3 次） | ✅ 规则已改｜◐ 首轮试跑 5/6（2026-10-09）：判据可达成立、Agent 形态随机漏检 1 次 → 新根因 R4，修法 A（瘦身前置）／B（宿主全局兜底）／C（命中率长期跟踪）待裁决，本条不关闭 |
| D-24 | 2026-10-10 | **闸门执法落到主流程（开工前闸门核对 REQUIRED）**：§4 守门与交接加两步——① 〔REQUIRED · 开工前闸门核对〕调度任一专业 Skill 前，先读其上游 artifact 的 `status`／`version`／`gate`／`allowDownstream`／`blockedBy`；任一 `SUPERSEDED`／非 `PASS`／`false` ⇒ 不启动该节点、`currentState` 与 `nextAction` 不得指向关闸上游的下游、状态停在阻塞点用**已注册** `WORKFLOW_BLOCKED`（不为此刻意新增 `*_WAITING_UPSTREAM`，避免改状态注册表 + 全部转移边而收益重叠）、`workflow.yaml.blockedItems` 记 `BLK-*`（含 `owner`／`requiredInput`／`clearCondition`）、`nextAction` 指回 owner；明禁以「下游先往前赶、上游慢慢补」「并行不空等」「先把能做的做了」为由越过未清阻塞。② 〔REQUIRED · 基线作废即清点沉没产出〕方向／基线类 DEC 把已批准基线转 `SUPERSEDED` 的同一轮，必须输出「引用该基线的下游产物清单 + 逐项处置（回炉重写／增量更新／作废）」，清单靠 `sourceRefs` 反查。另：`Responsibilities` 补「调度前执行上游闸门核对」，`Non-goals` 补「不在上游关闸或基线作废未清点时把下游节点排进 `nextAction`」。契约同步落 `shared/gate-policy.md` 新增 §6 Gate enforcement（规则 1–5）与 `shared/artifact-contract.md` §2 基线绑定。③ **机械检出补上（本轮自纠一处不实断言）**：原以为 `scripts/validate_core.py:386` 既有的「非 `BLOCKED` 的 Gate 引用 `DRAFT`/`SUPERSEDED` 记录即报错」足以覆盖 `sourceRefs`，实测该判据**只作用于 Gate 记录的 `evidenceRefs`/`decisionRefs`，不查产物 `sourceRefs`**——故在 `check_artifact` 补一条：产物 `status != SUPERSEDED`、`sourceRefs` 指向 `SUPERSEDED` 上游、且未在 `supersedes` 声明取代关系 ⇒ 报 `is built on a superseded baseline`；单测 `test_sourceRefs_binding_rejects_superseded_baseline` 带对照组（当前产物命中，自身已作废者与合法取代者不命中）。字段仍零新增，但契约那句「量具已有牙齿」的断言自此才成立 | `issue/WorkFlow/2026-10-10/01`（P0：13:57 登记 `allowDownstream: false`，14:52 编排仍排 FTDD；10:53 作废 v0.2 基线，当日 OSS 调研与 TDD V1 无人回头清点）＋ `issue/UI-UX-Review/2026-10-10/01`；B 方向落 `Skill-Optimizer` D-40 · 案例库模式 5 | ✅ 规则已改 + 量具已补｜◐ 未经真实「上游关闸」场景 fresh 会话复跑验证｜量具证据：`validate_core.py system` 61 tests OK（含本轮新增 1 条）、`check-installed-refs.py` 441 处引用双视图可达 RESULT: PASS、`skill-contract` / `registry` 校验通过 |

| D-25 | 2026-10-10 | **建档结构与量具可达入主流程**（`issue/WorkFlow/2026-10-10/02` 规则层）：§1「标准/完整」步加〔REQUIRED · 建档结构与量具可达〕——`.spec/workflow.yaml`、`.spec/manifest.yaml` 的根结构与字段名以 `../shared/templates/workflow.yaml`、`../shared/templates/project-manifest.yaml` 为准，取值以 `governance/` 注册表与 `../shared/artifact-contract.md` §2 为准；首次建档或改动后跑 `python scripts/validate_core.py gate --project-root <项目>` 与 `artifact --project-root <项目>`，**解析失败或字段非法即停 `WORKFLOW_BLOCKED` 并如实报告，不得在「校验器读不通」的状态下继续正式交接**（校验器不通 ⇒ §6 全部闸门规则只剩执行方自觉）。**本轮自纠一处**：初稿写的是 `system`，实测对业务项目会因项目内缺 `governance/state-registry.yaml`、`.spec/traceability.yaml`、`shared/templates/task-envelope.yaml` 报 10 条无关红——`system` 只适用于本仓自检，业务项目改用 `gate` + `artifact` 两条（fixture 实测：漂移样本报 `cannot parse YAML ... duplicate YAML key` + `workflow has invalid gate: None`，合规样本报通过）。`shared/artifact-contract.md` §2 同步加「Status vocabulary」映射：`REGISTERED`→`DRAFT`、`READY`→`REVIEW`（有批准 DEC 才 `APPROVED`）、`APPROVED_SUPERSEDED`→`SUPERSEDED`（批准历史走 `decisionRefs`、取代关系走 `supersedes`），轮次 `round: n/3` 属 Gate 记录不属 `status` | `issue/WorkFlow/2026-10-10/02`（实测 `validate_core.py gate` 对 knowledge-bases 报 `cannot parse YAML ... duplicate YAML key: 'sourceRefs'` + `workflow has invalid gate: None`；`artifactId` 出现 0 次、`- id:` 24 条、枚举外状态 13 条）；**项目侧 8 步迁移仍未执行**（业务项目改动需单独授权） | ✅ 规则已改｜◐ 迁移与真实复跑待授权 |

## 四、待决问题

Q1 纯前端形态、Q2 一路做到测试时评审停不停、Q3 起点推断误判处理，均为开放问题。
Q4 当场沉淀（自动改产出方 skill）是否需逐条用户确认——D-18 定为不逐条请示（用户已授权），但须留痕 D-xx + 收尾汇总告知；观察若干项目后复盘是否需加确认闸。
