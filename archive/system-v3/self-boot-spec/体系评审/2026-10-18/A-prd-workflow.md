# 体系评审报告 A 组：PRD 12 Skill + workflow（只审不改）

> 评审人：audit-prd-workflow（task-4） ｜ 日期：2026-10-18 ｜ 范围：PRD/ 下 12 个 skill + 根级 workflow/
> 依据：docs/体系修复与评审执行计划-20261018.md；Other/skill-optimizer/assets/self-audit-checklist.md（七维）；Other/skill-optimizer/assets/skill-writing-standard.md；shared/skill-contract.md、product-workflow-contract.md、gate-policy.md、anti-deadloop.md、artifact-contract.md、requirements-context.md；governance/skill-registry.yaml、workflow-registry.yaml、state-registry.yaml、artifact-registry.yaml、schemas/；README.md
> 纪律：只审不改（未改任何 skill/文档/脚本，未写 issue 池，未 commit）；按任务约定未跑全量 scripts/validate.ps1。

## 一、范围

### 1.1 覆盖 skill（13 个入口，全部实际通读）

| 目录 | skill id | SKILL.md 行数 | registry 状态 | 备注 |
|---|---|---|---|---|
| workflow | workflow | 214 | active / contractLevel v1 | 根编排器 |
| PRD/prd-workflow | prd-workflow | 75 | active / v1 | 产品域编排 |
| PRD/idea-intake | idea-intake | 80 | active / v1 | 原子 |
| PRD/product-discovery | product-discovery | 79 | active / v1 | 原子 |
| PRD/competitive-analysis | competitive-analysis | 62 | active / v1，legacyAlias Competitive-Analysis | 兼容入口转 v2 |
| PRD/product-definition | product-definition | 77 | active / v1 | 原子 |
| PRD/application-blueprint | application-blueprint | 78 | active / v1 | 原子 |
| PRD/feature-decision | feature-decision | 81 | active / v1 | 原子 |
| PRD/prd-design | prd-design | 63 | active / v1，legacyAlias PRD-Design | 兼容入口转 v2 |
| PRD/prd-review | prd-review | 60 | active / v1，legacyAlias PRD-Review | 兼容入口转 v2 |
| PRD/change-intake | change-intake | 72 | active / v1 | 跨域入口 |
| PRD/impact-analysis | impact-analysis | 73 | active / v1 | 跨域入口 |
| PRD/product-analytics | product-analytics | 55 | active / v1 | OPERATIONS 域产品分析 |

registry 共 46 项 = 45 个本地 active Skill + 1 个外部引用（skill-knowledge，status: external），13 个入口 id 与目录名、frontmatter name 全部一致（机检 0 差异）。

### 1.2 覆盖文件与深度

- **逐字通读**：13 个 SKILL.md；workflow/README.md、workflow/CONTEXT.md、workflow/assets/pipeline-template.md、workflow/references/legacy-pipeline.md；PRD/{competitive-analysis,prd-design,prd-review} 的 README.md 与 CONTEXT.md；PRD/prd-review/assets/{summary,issue-list}-template.md；PRD/prd-design/assets/eval-template.md；PRD/competitive-analysis/assets/report-template.md 与 references/legacy-skill.md 片段；本组涉及的全部 shared/ 契约与 governance/ 注册表、schema。
- **机械扫描（脚本化，只读）**：PRD/ + workflow/ 共 80 个 md/yaml 文件——重复行、空章节、占位符、U+FFFD 乱码、机器绝对路径、凭据、危险指令、跨 skill 引用形态；state-registry 126 条转移与 13 个 SKILL 的 State Changes 逐边比对；frontmatter name/13 个强制节/registry id 三方比对；registry 计数统计。
- **未逐字通读**：competitive-analysis / prd-design / prd-review 的 references、case-library、其余 assets（约 60 个二级文件）——仅做机械扫描与抽样核对，见第五节。

### 1.3 本组重点问题的回答位置

- 产品阶段交接契约（shared/product-workflow-contract.md、requirements-context.md）与各 skill 是否闭环 → A-01、A-07、A-08；
- prd-workflow 与根 workflow 的边界 → A-09（另有 A-16 交接下游未指名）；
- trigger 描述是否覆盖 what+when → A-10（13 个里 10 个缺「何时用」）。

## 二、做得好（先列有效资产，防后续修改改坏）

1. **入口标识三方一致，强制节齐全**：13/13 SKILL.md 的 `name` = 目录名 = registry id（例 PRD/prd-workflow/SKILL.md:2 `name: prd-workflow` ↔ skill-registry.yaml:189-190）；13/13 含 skill-contract §3 的 13 个强制节（Purpose/Trigger/…/State Changes），`validate_core.py skill-contract` 与 `registry` 均 exit 0。
2. **12 个原子 skill 的状态链与唯一状态源逐边一致**：对 state-registry 全部 126 条转移做机检，idea-intake:80、product-discovery:79、competitive-analysis:62、product-definition:77、application-blueprint:78、feature-decision:81、prd-design:63、prd-review:60、change-intake:72、impact-analysis:73、product-analytics:55 的 State Changes **全部合法**（对应 TR-093~TR-126）；只有 prd-workflow 一处失配（A-02），说明「照注册表写 State Changes」这条纪律在原子层已被执行。
3. **contract §2.2 的前两条硬门禁已落成可执行步骤**：workflow/SKILL.md:101-109（资源投入门禁：确认先于投入、提问合法性、研究未回传冻结下游题目）与 PRD/idea-intake/SKILL.md:36-39 把「只问只有用户能回答的题」「答案依赖研究的问题不得提问」写成了可判定条件，且 workflow:109 以引用指向 contract §2.2 未复述——符合「信息单一归属」（skill-writing-standard.md:66）。
4. **workflow/SKILL 引用的脚本与治理文件全部真实存在、子命令可执行**：workflow/SKILL.md:71 的 `validate_core.py gate/artifact/controldrift`、:123 的 `resign --apply --decision` 均存在于 scripts/validate_core.py:1759-1764；:119 的 scripts/tsr.py、:214 的 scripts/task_preflight.py、:71 的 shared/templates/workflow.yaml 与 project-manifest.yaml、:14-15 的 governance/eval-spec.yaml（caseTiers:36、issueRef:42 存在）与 scripts/eval/relay.py 全部存在。这是「声明-流程一致」的正面样本，其他 skill 可对照。
5. **PRD 活跃面干净的可移植性与安全性**：PRD/ 全部文件机器绝对路径 grep = 0；无 scripts/、无硬编码凭据、无 rm -rf / curl pipe bash / 外联上传类指令（安全维度 0 命中）；外部依赖均有降级路径——competitive-analysis:50（无联网/授权 → 明确标注的未验证草案 + 补证路径）、product-analytics:24（无数据 → OPEN）、shared/requirements-context.md:43（Wiki/搜索可选，不要求部署知识库）。
6. **数量口径跨位置一致**：registry 46 项 = 45 active + 1 external（skill-registry.yaml）；README.md:6 与 docs/当前项目介绍与目标对齐说明书.md:56,160 均写「45 个本地 Skill」；产品域十阶段在 workflow-registry.yaml:30-48、PRD/prd-workflow/README.md:3、docs/当前项目介绍…:180 三处一致（A-02 只错在「阶段间状态」而非阶段数）。
7. **prd-review 的「开工前闸门核对」是全产品域唯一在 Procedure 内显式落地的 Gate 前置检查**，且字段齐全：PRD/prd-review/SKILL.md:38 逐条读 `status/version/gate/allowDownstream`，并规定「缺公共 §0 节则本轮 Gate 只能记未验证」（assets/summary-template.md:3）。它就是 A-08 建议的修复模板。

## 三、问题清单（每条可复核：现象来自实际文件内容，判据来自列明文档）

> 等级口径：P0=阻断/会误导执行；P1=不一致但不阻塞；P2=轻微。维度编号：1 术语·命名 / 2 逻辑闭环 / 3 文句质量 / 4 声明-流程一致 / 5 跨位置同步 / 6 简洁 / 7 安全 / 8 可移植性。

| ID | skill | 文件:行 | 等级 | 维度 | 现象 | 证据原文（可复核） | 判据 | 修复方向 |
|---|---|---|---|---|---|---|---|---|
| A-01 | 产品交接契约（全产品域） | shared/product-workflow-contract.md:87-101 | **P0** | 4/5 | §4「Product artifact contract」的字段名/枚举与产物注册表、量具冲突；按 §4 写 manifest 必被校验器拒绝 | §4 写 `kind: intake / discovery-brief / research / …`，且只列 artifactId/kind/projectId/lifecycle/status/sourceRefs/evidenceRefs/decisionRefs/openItems/gate/allowDownstream；而 shared/artifact-contract.md:29 用 `type: prd`、:33-39 要求 producedBy/producedAt；governance/schemas/artifact-manifest.schema.yaml:3 `requiredArtifactFields: [artifactId, type, path, lifecycle, owner, status, producedBy, producedAt]`；§4 的 kind 枚举缺 journey-map、scope-decision（artifact-registry.yaml:337、373 已登记；application-blueprint/SKILL.md:54 与 feature-decision/SKILL.md:57 实际产出） | 契约字段名/必填项须能通过机械校验；skill 产物类型必须在契约枚举内（artifact-contract §2 + schema） | ①§4 字段名改 `type`，补 producedBy/producedAt；②kind 枚举与 artifact-registry 对齐（或删枚举改「以 artifact-registry 为准」）；③gate/allowDownstream 移出产物契约，指向 workflow/gates 记录；④同步 docs/PRD-Workflow-v2.md:34-46 产物类型清单 |
| A-02 | prd-workflow | PRD/prd-workflow/SKILL.md:75 | **P0** | 2/5 | State Changes 声称的 13 段状态链有 6 条转移在 state-registry 中不存在（跳过全部 *_READY 状态） | 声明链：`INTAKE_READY → IDEA_INTAKE_IN_PROGRESS → DISCOVERY_IN_PROGRESS → COMPETITIVE_RESEARCH_IN_PROGRESS → PRODUCT_DEFINITION_IN_PROGRESS → APPLICATION_BLUEPRINT_IN_PROGRESS → FEATURE_DECISION_IN_PROGRESS → PRD_IN_PROGRESS → PRD_REVIEW_IN_PROGRESS → PRD_APPROVED → PROTOTYPE_IN_PROGRESS → PROTOTYPE_REVIEW_IN_PROGRESS → PROTOTYPE_APPROVED`；registry 只允许 `IDEA_INTAKE_IN_PROGRESS→IDEA_INTAKE_READY`（TR-094）、`IDEA_INTAKE_READY→DISCOVERY_IN_PROGRESS`（TR-096）、`DISCOVERY_READY→COMPETITIVE_RESEARCH_IN_PROGRESS`（TR-099）、`COMPETITIVE_RESEARCH_READY→PRODUCT_DEFINITION_IN_PROGRESS`（TR-102）、`PRODUCT_DEFINITION_READY→APPLICATION_BLUEPRINT_IN_PROGRESS`（TR-105）、`APPLICATION_BLUEPRINT_READY→FEATURE_DECISION_IN_PROGRESS`（TR-108）、`FEATURE_DECISION_READY→PRD_IN_PROGRESS`（TR-111）；机检 126 条边中这 6 条非法（其余 12 个原子 skill 全部合法） | state-registry 是唯一状态源（skill-contract §6、artifact-contract §5）；SKILL 声明的转换必须可在注册图找到 | ①把 6 个 *_READY 补进链内；或②改成「阶段图」并写「实际转换以 governance/state-registry.yaml 为准」；③同时补 CHANGE/OPTIMIZE 的链（当前只画了 CREATE） |
| A-03 | workflow | workflow/CONTEXT.md:22（另 :3、:15-16、:19、:21、:33-48） | P1 | 1/4/5 | 自称「Workflow 术语对齐源」的文件保留被共享契约明令禁止的强制放行口径、以 PIPELINE 为交接状态源，且未加 LEGACY 声明 | CONTEXT:3 自称「术语对齐源 + 决策日志」；:22「上限 3：同批「修复→复核」满 3 轮仍未收敛 → …强制清 P0 后直接放行，残留 P1 记遗留」；shared/anti-deadloop.md:35「never use “force pass”, “clear P0 then pass”, or “leave P1 as legacy” as a Gate rule」；workflow/SKILL.md:148 与 README.md:95 均为「residual P1 never PASS，仅授权 CONDITIONAL」；CONTEXT:19「交接记录：PIPELINE 追加」vs artifact-contract.md:19「.spec/PIPELINE.md 是只读 legacy 输入」；CONTEXT:16「终点不指定=只跑起点」vs SKILL.md:68「默认完成用户要求的可验收结果，不每完成一小步都等待继续」；README.md:119 要求历史文件加 legacy notice，本文件没有 | 同一规则在 shared/SKILL/README/CONTEXT 四处表述必须一致；被契约点名的禁用 Gate 措辞不得出现在活跃文件；未标 legacy 的旧口径文件视为活跃 | 重写 CONTEXT 术语表为 v2 口径（Gate 三值、workflow.yaml 唯一状态源、连续执行语义）；若保留历史决策日志，则在文件头加 LEGACY COMPATIBILITY NOTICE 并删掉被当作现行规则的措辞；补 D-27+ 记录 |
| A-04 | change-intake、impact-analysis | PRD/change-intake/SKILL.md:14-17；PRD/impact-analysis/SKILL.md:14-17 | P1 | 3/4 | 两处 `## Purpose` 之下被误插入英文 Gate 契约段，Purpose 首句变成 Gate 规则；同段在 21 个文件批量出现（部分落在合法兼容层） | 结构均为：:14「## Purpose」→ :15「Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL…There is no force-pass rule.」→ :17 才是真正的 Purpose 中文句；对照合法落点 DEV/backend-dev/SKILL.md:175-179 位于 Contract Compatibility Layer | Purpose 节应以能力陈述开头；同一 Gate 段只应出现一次且在 Gate/兼容层（信息不重复，skill-writing-standard.md:66,206） | 删除两处 :15 段（Gate 节已有正确中文口径）；同时全仓 grep「Use the common Gate contract」复核注入位置（DEV/UI 部分文件被插进 Markdown 表格中间，属 C/D 组范围） |
| A-05 | competitive-analysis | PRD/competitive-analysis/README.md:8,23 | P1 | 4/5 | README 声明的「11 模块报告」与「数据红线 8 条见 SKILL.md」在 active SKILL.md 中均不存在 | README:8「`.spec/<主题>竞品分析/`：报告（11 模块）+ 验收结果详细说明」；README:23「数据红线 8 条见 SKILL.md」；SKILL.md:46-47 Outputs 仅为「research artifact：研究范围、竞品选择、带来源的功能全景/对比矩阵、限制和未知项」；数据红线实际只在 references/legacy-skill.md:33-44（8 条）；SKILL.md:56 又写「旧 references/legacy-skill.md 只作研究方法参考，冲突规则以本入口为准」 | 声明指向本文件的内容必须存在；核心交付须由 SKILL Procedure/Outputs 承接（self-audit-checklist 维度二「声明-承接」） | README 改为「active 交付=research + 功能清单；11 模块报告与数据红线属 legacy：references/legacy-skill.md」；或把数据红线提升进 active SKILL（更利于其他应用直接使用） |
| A-06 | competitive-analysis | PRD/competitive-analysis/CONTEXT.md:16（另 :1） | P1 | 1/7 | 术语表自造 Gate 值 `FAIL`，与「Gate 只有三值」唯一事实源冲突；文件未标 LEGACY | CONTEXT:16「Pass Gate：…CONDITIONAL=P0=0 但 P1(Open)≥1（就地补齐再验）；FAIL=命中 P0」；shared/gate-policy.md:3「Every Skill and Workflow uses the same three outcomes: PASS / CONDITIONAL / BLOCKED」、:76「Do not invent FAIL…only as historical text in a legacy reference」；同批 PRD/prd-review/CONTEXT.md:1 已有 LEGACY COMPATIBILITY NOTICE，本文件没有 | Gate 值只允许三种（skill-contract §6）；含旧 Gate 口径的文件必须标 legacy（README.md:119） | FAIL 改为 BLOCKED（并说明「阻断输出并回炉」语义）；文件头补 legacy notice 或按 v2 重写 |
| A-07 | competitive-analysis（契约承接层） | shared/product-workflow-contract.md:69 vs PRD/competitive-analysis/SKILL.md:26-27,38-44,46-47 | P1 | 2/4 | contract §2.2 第 3 条硬门禁「研究裁剪依据必须声明来自哪条用户确认」在产品原子 skill 中没有对应字段与核对步骤 | contract:69「全景与功能清单的裁剪依据必须声明来自哪一条用户确认（需求方向、指定竞品、限定形态或明示授权），否则不得自行划定研究范围并投入资源」；competitive-analysis Preconditions（:26-27）、Procedure（:38-44）、Outputs（:46-47）均无 scopeBasis/裁剪依据字段；第 1、2 条已在 idea-intake:36-39 与 workflow:101-109 落地，第 3 条无承接 | contract 明示「三条硬门禁（可执行判据，非叙述性要求）」→ 必须落到某执行文件的检测/产字段 | competitive-analysis Preconditions 增核对（本次研究范围来自哪条用户确认），Outputs 增「裁剪依据/用户确认引用」字段；或在 research artifact 模板固定该槽位 |
| A-08 | prd-workflow（及产品原子 skill） | PRD/prd-workflow/SKILL.md:47-55；workflow/SKILL.md:121；PRD/prd-review/SKILL.md:38 | P1 | 2/4 | 产品域「开工前闸门核对」未落地：根 workflow 只对自己直接调度的节点执行，产品域实际调度者是 prd-workflow，而它的 Procedure 没有读上游 manifest 四位字段的步骤 | workflow/SKILL.md:121「〔REQUIRED，先于任何节点调度与状态前移〕…读该节点所依赖的上游 artifact…`status`、`version`、`gate`、`allowDownstream`、`blockedBy`」；prd-review:38 有完整实现；prd-workflow Procedure 8 步（:48-55）无此动作；Responsibilities:38 只有「校验证据、产物、决策和回退路径」；其余原子 skill 仅 prd-design:32 有笼统「正式 Gate 允许交接」 | gate-policy §6「closed means closed」要求每个下游开工前读上游字段；A-09 若把产品域交给 prd-workflow，则它必须承接该 REQUIRED | prd-workflow Procedure 步骤 1 增 REQUIRED 上游闸门核对（字段/阻塞格式/blockedItems 写法照 prd-review:38 与 gate-policy §6）；或在每个原子 skill Preconditions 增同一段并引用 gate-policy §6（二选一，别两处各写一套） |
| A-09 | workflow、prd-workflow | workflow/SKILL.md:75,87（全文无 prd-workflow）；governance/workflow-registry.yaml:21-22,30-48；PRD/prd-workflow/SKILL.md:22；README.md:85 | P1 | 2/5 | 产品域编排双头：根 workflow 明确「进入需求域（idea-intake）」且全文从不提 prd-workflow；注册表却把 prd-workflow 登记为其子 Workflow；README 又声明 prd-workflow 拥有产品域序列 | workflow:75「⇒ 归 CREATE 并进入需求域（`idea-intake`）」；workflow:87「CREATE -> PRD -> Prototype -> UI Design -> …」（领域名直连）；workflow-registry:21-22 `childWorkflows:` 含 `prd-workflow`，:30-48 `prd-workflow.skills` 列 10 个原子；prd-workflow:22「CREATE、CHANGE、OPTIMIZE 进入产品域…时触发」；README:85「`prd-workflow` owns only the product-domain sequence」 | 同一职责不得双头调度（contract §2.1：prd-workflow 唯一主责=选阶段/调度/状态展示与 Gate 交接）；父 Workflow 与子 Workflow 之间须有明确交接点 | 二选一并全仓统一：①workflow:75/87 改为「进入产品域 → prd-workflow」，删除直连 idea-intake 的表述（建议，docs/当前项目介绍:60 已称 prd-workflow 是产品域实际编排）；②删除 workflow-registry 的 prd-workflow 子流程定位并在 prd-workflow/README 声明仅独立进入 |
| A-10 | 10 个入口 description | 各 SKILL.md:3（prd-workflow、idea-intake、product-discovery、product-definition、application-blueprint、feature-decision、prd-review、change-intake、impact-analysis、product-analytics） | P1 | 1/4 | 10/13 入口 description 只说「做什么」不说「何时用」，未达编写规范 §一；与同仓 17 个带「触发：」清单的 skill 不一致 | 例：change-intake:3「把模糊请求登记为可追踪的生命周期任务并完成初步分类。」26 字；impact-analysis:3 36 字；product-analytics:3 30 字；prd-workflow:3 无用户口语触发词。规范要求「须同时说清 1 做什么 2 何时用」（Other/skill-optimizer/assets/skill-writing-standard.md:18-32），并给出「触发：」示例；全仓 grep「触发：」命中 17 个 SKILL.md，本组 12 个 PRD skill 均无 | description 是宿主唯一判定入口（标准 §一「L1 元数据」）；「何时使用只能放 description，不许放正文」（标准 :36） | 为 10 个 description 补「触发：」用户原话（写 PRD/做产品规划/梳理业务蓝图/功能取舍/评审需求/登记需求/评估改动影响/看产品数据/帮我 analyze 竞品），保留现有边界句；目标是用户最可能的 3~5 种说法都能命中 |
| A-11 | idea-intake | PRD/idea-intake/SKILL.md:70 | P1 | 2/8 | Failure Route 写 `../change-intake/impact-analysis`：源仓视图不存在，且属 contract §1.4 禁止的跨 skill 相对路径形态；机械门禁未报 | :70「语义冲突回用户确认；上下文缺失回 project-onboarding；变化交 ../change-intake/impact-analysis；故障交 defect-triage」；shared/skill-contract.md:36-38「指向其他 skill 的私有资产——写逻辑引用 <skill-id>/内部路径（不带 ../、不带分类层）」「禁止写法：…跨分类的 ../<兄弟skill>/」；源仓路径 PRD/idea-intake/../change-intake/impact-analysis 不存在；check-installed-refs.py:38-40 的 REF 正则要求以扩展名结尾，裸 skill 路由不被扫描 → `--quiet` 仍 exit 0 | 跨 skill 引用只允许两种写法（§1.4）；Failure Route 目标必须可解析、可路由 | 改为「变化交 change-intake 与 impact-analysis（两个独立 skill）」；并把「裸 skill-id 相对路径」纳入 check-installed-refs 扫描（否则同类问题继续漏检） |
| A-12 | product-analytics | PRD/product-analytics/SKILL.md:49 | P1 | 2/4 | Failure Route 指向未注册 skill `Observability-Design`：路由目标不存在，失败路线断头 | :49「埋点/关联缺失转 Observability-Design；行为偏差转 defect-triage；…」；skill-registry.yaml 46 项中无 Observability-Design（grep 0 命中）；同一目标还被 Other/signal-triage/SKILL.md:49、Other/signal-collection/SKILL.md:49、Other/quality-inspection/SKILL.md:145 引用（系统性问题，交 C/D 组） | Failure Route 必须指向可调用的 owner（gate-policy §4「The Failure Route must name the next owner」）；skill-contract §1.4「只是路由或称呼时直接写 skill id」隐含目标已注册 | 改为可执行路线：「转 signal-collection 补埋点并登记 OBSERVABILITY_GAP」；若确要保留 Observability-Design，先补该 skill 的 SKILL.md 与注册项（当前无） |
| A-13 | prd-design、prd-review | PRD/prd-design/README.md:1-4,14,25-28；PRD/prd-design/CONTEXT.md:65；PRD/prd-review/README.md:6-16,21-24 | P1 | 5/4 | 两份 README/CONTEXT 仍以「定稿」口吻描述被 v2 SKILL 替换前的流程，且未加 LEGACY 声明；外部应用读者会把 README 当现行流程 | prd-design README:14「两段式流水线：总览期收敛 7 点…」、:25-28 流程 S1~S7/范围 Gate/终审；active SKILL.md:40-45 只有 5 步 Procedure，无 7 点、无范围 Gate；prd-review README:6-16「一审三角色…产品专家总审」、:21「三角色独立上下文并行评审」，active SKILL.md:32-42 无三角色/并行/总审调度步骤（仅按审查对象加载 4 份 checklist）；同期 PRD/prd-review/CONTEXT.md:1 已有 LEGACY notice，而 prd-design README/CONTEXT 与 prd-review README 没有；README.md:119「Historical files are marked with a legacy notice where their old wording could be misleading」 | SKILL/README/CONTEXT 对同一能力描述一致（维度五）；旧口径文件须按 README:119 标 legacy | 二选一：①三份文件加 LEGACY COMPATIBILITY NOTICE 并改写成「旧流程见 references/legacy-skill.md；现行边界见 SKILL.md」；②把仍需保留的能力（三角色评审、7 点澄清）升进 active SKILL Procedure（属行为变更，需用户裁决） |
| A-14 | change-intake、product-discovery、workflow | PRD/change-intake/SKILL.md:72；PRD/product-discovery/SKILL.md:79；workflow/SKILL.md:192-194；state-registry TR-002/005/096/097 | P2 | 1/2 | 同一个状态 `DISCOVERY_IN_PROGRESS` 在一个 CREATE 生命周期内承担两种语义（项目基线发现 vs 产品发现），workflow.yaml 无法区分 | change-intake:72 `INTAKE_REQUESTED → DISCOVERY_IN_PROGRESS → INTAKE_READY`（registry TR-002/TR-005）；product-discovery:79 `IDEA_INTAKE_READY → DISCOVERY_IN_PROGRESS → DISCOVERY_READY`（TR-096/TR-097）；workflow:192-194 概览链两处都出现 | currentState 是唯一进度源（artifact-contract §5）；同一状态 id 不宜在一个生命周期内有两种业务含义 | 建议 registry 增 BASELINE_DISCOVERY_IN_PROGRESS（或 change-intake 改用 ONBOARDING_*），同步三处 State Changes；属治理层改动，需 Lead 派单给 registry owner |
| A-15 | workflow | workflow/SKILL.md:189-194、:50 | P2 | 2/5 | 概览状态链含非法边 PRD_IN_PROGRESS→PRD_APPROVED（缺 PRD_REVIEW_IN_PROGRESS）；「15 节点」口径与 legacy 文件不一致 | SKILL:194「-> PRD_IN_PROGRESS -> PRD_APPROVED -> UI_IN_PROGRESS」；registry TR-112（PRD_IN_PROGRESS→PRD_REVIEW_IN_PROGRESS）与 TR-113（→PRD_APPROVED）；:189 有缓解语「实际转换以注册图与预检为准」；:50「保留旧 PIPELINE.md/线性 15 节点链路」vs references/legacy-pipeline.md:5,11「15 个链上专业 Skill（14 个编号节点 + ⑧⑨ 前置 OSS-Radar 调研步）」 | 状态链须与注册表一致（有缓解语时降为 P2）；数量口径应精确 | 链中补 PRD_REVIEW_IN_PROGRESS；:50 改「15 个链上 Skill / 14 个编号节点」 |
| A-16 | prd-workflow | PRD/prd-workflow/SKILL.md:55,71-72 | P2 | 2 | 未指名下一 Workflow/下游 owner，只写「下一 Workflow」，UI 阶段交接靠外部推断 | :55「输出 execution summary、manifest、decision、traceability 和下一 Workflow」；:71-72 Downstream Contract 只列「UI/DEV/auto-test 只消费 manifest 中 APPROVED 的产品 artifact」；registry TR-120 `PROTOTYPE_APPROVED→UI_IN_PROGRESS`（ui-workflow）；contract §1 称 UI 阶段是产品序列「必经后置」 | 交接须点名下游 owner 与合法边（gate-policy §4；README:85） | :55 明确「下一 Workflow = ui-workflow（PROTOTYPE_APPROVED → UI_IN_PROGRESS）」，或在 Downstream Contract 补一行 |
| A-17 | prd-workflow | PRD/prd-workflow/SKILL.md:37,69 | P2 | 1 | 同一文件内 skill 名称四套写法混用：kebab、CamelCase legacyAlias、空格大写、中文 | :37「顺序调度 `idea-intake`、`product-discovery`、`Competitive-Analysis`、`product-definition`、…`PRD-Design`、`PRD-Review`、`Prototype-Design`、`Prototype-Review`」；:69「回 Product Discovery/Competitive Analysis/Product Definition/Application Blueprint/Feature Decision/PRD-Design/Prototype-Design」 | skill-contract §1.4「只是路由或称呼时直接写 skill id」；registry canonicalId=lowercase-kebab（skill-registry:23） | 全文统一 canonical kebab id；legacyAlias 只留在 registry 与 frontmatter metadata |
| A-18 | feature-decision | PRD/feature-decision/SKILL.md:17 vs :37,:49,:52；contract:69 | P2 | 1 | 功能决策枚举三套并存 | :17「转成可追踪的 Adopt/Adapt/Reject/Defer 与 Must/Should/Could/Won't 决策」；:37/:49/:52「MVP/Later/Reject/Defer」；shared/product-workflow-contract.md:69 只写「MVP/Later/Reject/Defer」 | 枚举前后一致、与产品交接契约一致（维度一/五） | Purpose 只保留 MVP/Later/Reject/Defer；若 Adopt/Adapt、MoSCoW 是输入框架，注明并给到 MVP/Later 的映射表，否则删除 |
| A-19 | root README、workflow README | README.md:55,85；workflow/README.md:3 | P2 | 5/8 | ①README 布局把 prototype 归入 PRD/，与 registry 及 docs 说明矛盾；②活跃文档把目录写成 `WorkFlow/`，与实际 Git 路径 `workflow/` 及 docs 的命名要求矛盾（大小写敏感 FS/他机拷贝后不可达） | README:55「PRD/ product discovery, decisions, PRD, and prototype workflow」；skill-registry.yaml:276-295 prototype-design/review 的 path=UI/…；docs/当前项目介绍与目标对齐说明书.md:194「（prototype-design）虽放在 UI 目录，属于产品域主流程」；README:85「`WorkFlow/` routes work」；workflow/README.md:3「`WorkFlow/` is the root-level orchestrator」；docs/当前项目介绍…:77 与 docs/工程体系使用手册.md:95 均写「Git 路径是 `workflow/`，跨平台引用应按 Git 路径」 | 目录归属以 registry path 为准（skill-contract §1.4）；活跃文档只用 Git 路径 | README:55 删 prototype（或注明原型 Skill 位于 UI/）；README:85 与 workflow/README:3 改 `workflow/`，需要时可括注旧拼写 |
| A-20 | workflow | workflow/references/legacy-pipeline.md:148,202（:1 已标 legacy） | P2 | 8/3 | 会随 skill 分发的文件内保留本机绝对路径与损坏文本 | :148「组件库位置：`D:\project\agent-project\skills-knowledge\asset-library\`」；:202「模板 `../../shared/templates/issue-template.md`mplates/issue-template.md`」（重复残片）；顶部 :1 已声明 LEGACY | Phase 0 目标含「去机器硬编码」（执行计划:18）；文本无截断/重复残片；legacy notice 不豁免可移植性 | :148 改 `$env:SKILLS_KNOWLEDGE_ROOT/asset-library/` 或仓库相对路径；修复 :202 截断串 |
| A-21 | root README | README.md:130 | P2 | 5 | 安装器单测数量失同步 | README:130「The regression suite also runs the cross-platform installer's 18 unit tests (scripts/tests/test_install_skills.py…)」；实际 scripts/tests/test_install_skills.py 现有 29 个 `def test_`（含 Phase 0 新增 link/unlink 用例，:501-:661）；执行计划:17 又记 19 tests | 计数类事实以当前文件为准（维度五范围引用同步） | 改为「29 项（含 link/unlink 端到端）」或删具体数字改「完整单测套件」 |
| A-22 | competitive-analysis、prd-design | PRD/competitive-analysis/README.md:19-20；PRD/prd-design/assets/eval-template.md:49-50 | P2 | 3/6 | 同一 English Gate 段连续重复两行（批量注入残留） | 两文件均为同一句「Use the common Gate contract: …There is no force-pass rule.」连续出现在相邻两行；正常落点见 DEV/backend-dev/SKILL.md:175-179（Contract Compatibility Layer） | 同一句话出现两次以上即冗余（skill-writing-standard.md:206） | 各删一行；并按 A-04 做全仓注入位置复核（DEV/UI 中插入表格中间的问题属 C/D 组） |
| A-23 | 13 个入口 + registry | 各 SKILL.md 第 4-6 行；governance/skill-registry.yaml | P2 | 1/5 | frontmatter 的 contract-level 元数据与注册表值域两处不一致；3 个 skill 的 short-description 与 description 完全同文 | skill-contract.md:44-54 定义 metadata 为 `contract-level: v2 / legacy-wrapper` + `legacy-alias`；13 个 in-scope SKILL.md 均无 contract-level 字段（对照：12 个活跃 skill 写 `contract-level: legacy-wrapper` 且无 short-description）；registry 给这 13 项标 `contractLevel: v1`，全表值域 v1=28/legacy-wrapper=12/legacy-adapter=5/external-reference=1，其中 v1/legacy-adapter/external-reference 不在 contract 枚举内；PRD/change-intake/SKILL.md:3 与 :5、impact-analysis:3 与 :5、product-analytics:3 与 :5 文本完全相同；competitive-analysis/prd-design/prd-review 还用了 contract 未定义的 `migration-target` 键 | frontmatter/registry 元数据须与 skill-contract §2 一致；元数据不得承载重复信息 | Lead 统一裁决枚举（建议 contract 增加 legacy-adapter/external-reference 或把 v1 映射为 v2 系）；13 个 skill 补 `contract-level: v2`；short-description 去重或删除 |
| A-24 | prd-review | PRD/prd-review/assets/summary-template.md:36-39；PRD/prd-review/assets/issue-list-template.md:6,10 | P2 | 1/5 | 活跃模板用旧名 PRD-Design/PRD-Review 作修改方/落点，与 active SKILL 的 kebab id 不一致 | summary-template:36「A · 防复发：`PRD-Design`」、:39「改不了落 `../../../issue/PRD-Design/<日期>/`」；issue-list-template:6「修改方枚举：`PRD-Design`」、:10「本 skill 修改方固定为 PRD-Design」；PRD/prd-review/SKILL.md:38 用 prd-design/prd-review | 历史名只入 metadata.legacy-alias（skill-contract:54）；产物路由按 registry id | 模板统一改 prd-design/prd-review；issue 目录新条目用 canonical id（历史目录保留） |
| A-25 | docs 手册 | docs/当前项目介绍与目标对齐说明书.md:187-188 | P2 | 5 | 手册对两个产品的描述与 active SKILL 不符 | :187「prd-design：将前置批准内容写成可开发、可验收的 PRD；兼容旧入口」——registry 实际 contractLevel v1/active，prd-design SKILL 是 v2 原子（docs/PRD-Workflow-v2.md:32 才把旧名当兼容入口，两处口径不同）；:188「prd-review：多角色检查完整性与一致性」——active SKILL.md:19-32 为单评审者只读评审，无多角色 | 手册事实须与 SKILL 当前能力一致（维度五） | :187 改「v2 产品规格原子 skill（旧名 PRD-Design 为别名）」；:188 改「独立只读评审，按审查对象加载四份 checklist」 |
| A-26 | workflow | workflow/references/legacy-pipeline.md:31,131,178（legacy 文件）；workflow/SKILL.md:205 | P2 | 1 | legacy 文件保留 force-pass 规则（已标 legacy 可保留），但现行 SKILL 指示「兼容规则见 references/legacy-pipeline.md」，读者会被引到禁用口径 | legacy:31「满 3 轮清 P0 后强制放行」、:131「强制清零 P0，再直接放行；残留 P1 记入 PIPELINE」、:178 错误表「强制清 P0 后放行」；anti-deadloop.md:35 明令禁止；SKILL.md:205「详细旧版节点与脚本兼容规则见 references/legacy-pipeline.md」 | legacy 内容可保留但不得被现行入口当作规则源（gate-policy:76 只允许历史文本出现在 legacy reference） | SKILL:205 改为「仅兼容读取旧节点编号与脚本名；Gate/放行口径以 shared/gate-policy.md 与 shared/anti-deadloop.md 为准」；legacy 三处 force-pass 行加显式「已废止」标注 |

## 四、机械扫描结果（只读；本组实际执行）

### 4.1 任务指定命令

| 命令 | 退出码 | 结果摘要 |
|---|---|---|
| `python scripts/validate_core.py skill-contract --project-root .` | 0 | `skill-contract validation passed` |
| `python scripts/validate_core.py registry --project-root .` | 0 | `registry validation passed` |
| `python scripts/check-installed-refs.py --project-root . --quiet` | 0 | `checked=539`，禁用写法/源仓不可达/副本不可达均为 0，`RESULT: PASS`（中文标签在 GBK 控制台显示为乱码，不影响判定） |

### 4.2 本组自建扫描（脚本化，只读）

| 检查 | 覆盖 | 结果 |
|---|---|---|
| State Changes ↔ state-registry 逐边比对 | 13 个 SKILL，126 条注册转移 | 12 个原子 skill 全部合法；**prd-workflow 6 条非法**（A-02）；workflow 1 条非法（有缓解语，A-15） |
| frontmatter name / 强制节 / registry id | 13 个 SKILL | name=目录=registry id 13/13；13 强制节 13/13 |
| registry 计数 | 46 项 | 45 active + 1 external；13 个 in-scope id 全部在册 |
| 机器绝对路径 | PRD/ 与 workflow/ 全部 md/yaml | PRD 0 命中；workflow 1 命中（A-20，legacy 文件） |
| 凭据（api key/token/password/私钥） | PRD/、workflow/ | 0 命中（命中的 token/upload 均为产品业务示例文本，非凭据/外联） |
| 危险指令（rm -rf、curl pipe bash、格式化、robocopy /MIR 等） | PRD/、workflow/ | 0 命中 |
| 重复非平凡行 | PRD/ + workflow/ 80 文件 | 2 处（A-22）；另发现同一 Gate 段在 21 个文件出现（部分为合法兼容层，交 C/D） |
| U+FFFD 乱码字符 / 未替换占位符 | 同上 | 0 乱码；占位符仅模板变量（`{{MODULE_INDEX}}` 等），无未替换残留 |
| 安装器单测计数 | scripts/tests/test_install_skills.py | 29 个 test 方法（README 写 18，A-21） |
| 跨 skill 相对引用形态 | PRD/ | 发现 1 处 contract §1.4 禁用形态（A-11），且现有门禁扫描不到裸 skill 路由 |

### 4.3 量具盲区（比单条问题更重要）

- `check-installed-refs.py:38-40` 的引用正则要求路径以文件扩展名结尾，**裸 skill-id 相对路径（如 `../change-intake/impact-analysis`）不进入扫描** → 本次 A-11 在 `--quiet` 绿的情况下仍然存在。建议把「`../<known-skill-id>` 形式」加入禁用写法扫描，否则「机械全绿」不能证明跨 skill 路由可移植。
- `validate_core.py skill-contract` 只校验强制节与 frontmatter 基本形态，**不校验 State Changes 与 state-registry 的一致性、description 触发词、README/CONTEXT 同步、legacy notice**——本报告 P0/P1 全部在它绿的情况下存在。结论：机械绿只说明「结构齐」，不说明「内容对」；内容面必须继续靠人工/机检脚本互补。

## 五、未覆盖 / 不确定项

1. **references/case-library 未逐字通读**：competitive-analysis / prd-design / prd-review 的约 60 个二级文件只做机械扫描与抽样（competitive-analysis/assets/report-template.md 全文、references/legacy-skill.md 片段、prd-review 两份模板全文已读）。这些文件内部的计数/术语一致性（如「11 模块」「五层框架」「9 章」）未逐条核完，可能仍有 legacy 口径残留。
2. **行为层未验证**：未跑 fresh-agent 场景、未跑 12 套 eval、未跑全量 `scripts/validate.ps1`/`run-tests.ps1`（任务约定）。本报告全部结论为静态口径，不代表触发/执行行为已达标。
3. **A-13 的处置方向依赖用户/Lead 裁决**：「旧 README/CONTEXT 是保留为历史并加 notice，还是把旧流程升进 active SKILL」属产品域行为决策，我只能指出冲突，不能判定哪一侧是应然。
4. **A-14 可能是有意设计**：`DISCOVERY_IN_PROGRESS` 的两种语义在 registry 既有转移里是合法的，若治理层本意就是复用同一状态，则 A-14 降为记录项；建议 Lead 找 registry owner 确认。
5. **A-23 的枚举裁决属治理层**：contract-level 的值域（v1/legacy-adapter/external-reference）是补齐 contract 还是改 registry，需与 registry/契约 owner 统一，本组只报不一致。
6. **docs/工程体系使用手册.md、docs/当前项目介绍… 其余章节未逐字**：仅 grep 核了 PRD 相关段落（45 个 Skill、十阶段、WorkFlow 大小写提示、两处产品描述），其他事实未核。
7. **prd-workflow/README.md 与 CONTEXT.md 只有 3 行**：按新骨架可能是刻意精简；但自洽检查清单要求 CONTEXT 有术语对齐源，无法据此完成术语比对，列为不确定项而非缺陷。
8. **本轮新发现可能已被 issue 池覆盖**：未读 `issue/` 池做去重（不在本组授权写入范围），汇总时请 Lead 按路径/现象去重。
9. `check-installed-refs.py` 的中文输出在本机 GBK 控制台显示为乱码（工具侧问题，scripts/ 不在本组范围）；若「其他应用直接使用」依赖控制台可读性，建议 C/D 组顺手修。

## 六、优先建议（Top 5）

1. **先修 A-01（P0，契约字段）**：把 shared/product-workflow-contract.md §4 的 `kind` 改为 `type`、补 producedBy/producedAt、枚举对齐 artifact-registry；这是产品域正式交接的第一道门，不修则所有按契约写 manifest 的下游都会踩。
2. **再修 A-02（P0，状态链）**：prd-workflow State Changes 补 6 个 *_READY（或声明以注册图为准 + 补 CHANGE/OPTIMIZE 链），与 governance/state-registry.yaml 对齐；同时用同一方法全仓复核其余 State Changes（本组 12 个原子已核合法，DEV/UI 等未核）。
3. **裁决 A-09 边界，并顺手落 A-08**：明确「根 workflow → prd-workflow → 产品原子」的单一调度链，把「开工前闸门核对」写进 prd-workflow Procedure（模板用 prd-review:38）。这两条决定产品阶段交接是否真正闭环，优先级高于文句类修复。
4. **清 A-03/A-06/A-13 的旧口径冲突**：workflow/CONTEXT 的 force-pass、competitive-analysis/CONTEXT 的 FAIL、prd-design/prd-review 的旧流程 README——统一按 README:119 加 LEGACY notice 或改写成 v2 口径。这批文件是「其他应用直接拷贝使用」时最容易被误读的部分，且改动成本低。
5. **批量修误插/悬空类（A-04、A-05、A-11、A-12、A-22）**：删除 change-intake/impact-analysis Purpose 下的英文 Gate 段、修 competitive-analysis README 的「见 SKILL.md」错指、修 idea-intake Failure Route 与 product-analytics 的未注册路由、去重复行。都是一处几行的确定性修复，可一并处理并加两条机械扫描（裸 skill 路由、重复 Gate 段）防复发。

> 附：本报告仅为 A 组结论；B/C/D 组的同类问题（尤其 A-04 的批量注入、A-12 的 Observability-Design 系统引用、A-01 的契约字段影响面）需在汇总时合并去重，避免同一根因重复派单。
