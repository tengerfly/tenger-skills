# 评审 D 组报告：Test/auto-test + Other 19 + Skill/skill-lifecycle

> 审计员：audit-test-other（任务 task-7）｜日期：2026-10-18｜性质：**只审不改**（本轮未修改任何 skill/文档/脚本，未写 issue 池，未 commit）
> 范围：21 个 skill 入口（Test 1 + Other 19 + Skill 1）按 self-audit-checklist 七维 + 可移植性逐项审；判据来源 = `Other/skill-optimizer/assets/self-audit-checklist.md`、`Other/skill-optimizer/assets/skill-writing-standard.md`、`shared/skill-contract.md`、`governance/skill-registry.yaml`、`shared/gate-policy.md`、`shared/artifact-contract.md`、`governance/artifact-registry.yaml`、`governance/state-registry.yaml`。
> 机械面三命令全部 PASS（见第四节）。**本次未发现 P0**（无危险指令、无硬编码凭据、SKILL.md 无阻断性错误）。P1 共 10 条，P2 共 19 条。
> 与 lead-mechanical 报告的交叉：F-M1（Testing 旧口径）、F-M3（legacy-adapter 缺 contract-level）、F-M4（历史机器路径）、F-M5（auto-test legacy-wrapper）已由 Lead 机械报告覆盖，本报告只在其**未覆盖的位置**补充证据（D-01/D-12/D-21），不重复列同一条。

## 一、范围（覆盖的 skill 清单）

| # | skill id | 路径 | registry contractLevel | 本轮读取文件 |
|---|---|---|---|---|
| 1 | auto-test | Test/auto-test | legacy-wrapper | SKILL/README/CONTEXT + 5 references + 3 assets + project/ 4 文件 |
| 2 | bug-fix | Other/bug-fix | legacy-wrapper | SKILL/README/CONTEXT + 2 references + case-library 4 + 3 assets |
| 3 | defect-triage | Other/defect-triage | v1 | SKILL/CONTEXT/README + agents/openai.yaml |
| 4 | deployment-execution | Other/deployment-execution | v1 | 同上 |
| 5 | essence-distill | Other/essence-distill | legacy-adapter | SKILL/README/CONTEXT + 2 references/assets |
| 6 | fact-check | Other/fact-check | legacy-adapter | SKILL/README/CONTEXT |
| 7 | incident-response | Other/incident-response | v1 | SKILL/CONTEXT/README + agents/openai.yaml |
| 8 | optimization-planning | Other/optimization-planning | v1 | 同上 |
| 9 | oss-radar | Other/oss-radar | legacy-wrapper | SKILL/README/CONTEXT + 2 assets + 1 reference |
| 10 | post-release-review | Other/post-release-review | v1 | SKILL/CONTEXT/README + agents/openai.yaml |
| 11 | project-onboarding | Other/project-onboarding | v1 | SKILL + 1 asset + 1 reference（无 README/CONTEXT） |
| 12 | quality-inspection | Other/quality-inspection | v1 | SKILL + 1 asset + 1 reference（无 README/CONTEXT） |
| 13 | refactor-planning | Other/refactor-planning | v1 | SKILL/CONTEXT/README + agents/openai.yaml |
| 14 | release-planning | Other/release-planning | v1 | 同上 |
| 15 | release-verification | Other/release-verification | v1 | 同上 |
| 16 | signal-collection | Other/signal-collection | v1 | 同上 |
| 17 | signal-triage | Other/signal-triage | v1 | 同上 |
| 18 | skill-evolver | Other/skill-evolver | legacy-wrapper | SKILL/CONTEXT + 2 assets（无 README） |
| 19 | skill-optimizer | Other/skill-optimizer | legacy-wrapper | SKILL/README/CONTEXT + 5 assets + 1 reference |
| 20 | source-reading | Other/source-reading | legacy-adapter | SKILL/README/CONTEXT + 2 references + 2 assets |
| 21 | skill-lifecycle | Skill/skill-lifecycle | v1 | SKILL + 4 references + 6 assets + scripts/tests 全部 |

汇总：21 个入口（占全仓 45 个的 46.7%）；registry 交叉项 46 = 45 active + 1 external（skill-knowledge），contractLevel 分布 v1 28 / legacy-wrapper 12 / legacy-adapter 5。

## 二、做得好（引用文件:行）

1. **auto-test 与 project/ 资料的边界写清楚了，且三层文件口径一致**：README.md:12 明确 "project/ 只作研究参考，不参与执行，执行入口仍是本目录 SKILL.md"；CONTEXT.md:20 同口径；project/README.md:18-22 进一步声明"本目录不承载任何执行步骤、门禁或产物格式；两者冲突时以 SKILL.md 和 shared 契约为准"，并给出迁移对照与可追溯 commit `b0b78b6`。null 占位修复落点正确：SKILL.md:162 已是 `Preserve the mature capability of auto-test ...`，全文再无"capability of null"。
2. **auto-test 的"声明-流程一致"在本组最完整**：三条 Iron Law（证据先于声明 / 分层短路 / 真实优先 mock 兜底，SKILL.md:15-17）在细则里都有对应可执行动作——fix-loop-guide.md:32-52 轮次状态机（3 轮上限）、coverage-gate.md:9-11 覆盖率阈值 + ratchet、case-authoring-guide.md:42-57 mock 边界铁律、SKILL.md:73-76 fresh-agent 回归纪律。声明"引擎模式"也给了会话模式完整降级（SKILL.md:44-49，产物格式一致）。
3. **skill-optimizer 与 skill-evolver 的分工边界是全组最干净的双向声明**：skill-optimizer/SKILL.md:14 与 skill-evolver/SKILL.md:14 互相指认调度方/执行方；skill-evolver/SKILL.md:123-132 用表格逐项划分（偏好库/issue 池/八维与七维/bug-patterns/外部情报）；evolution/README.md:21-27 再用三池判据（持久偏好→evolution、方法论→issue、代码坑→bug-patterns）兜底。无职责重叠、无互相改写。
4. **"数据池写路径"的可移植降级已在 3/4 个入口闭环**：bug-fix/SKILL.md:18,113（安装副本写用户指定目录/项目本地，待反馈回写）、skill-optimizer/SKILL.md:59,152（同上 + 授权边界）、oss-radar/assets/watchlist-template.md:11（不写死个人绝对路径），并由 shared/problem-recording.md:22 给出通用口径"不把当前目录、安装缓存或两层 ../ 默认当源仓；未授权只留本地待反馈"。
5. **Skill/skill-lifecycle 独立包自包含与只读安全经实测**：全包 grep 无 shared/、governance/、issue/、bug-patterns/、evolution/、WorkFlow 引用（0 命中）；check_bundle.py:22-27 拒绝 symlink/reparse、:104-110 只编译不执行被测脚本；本轮实跑 `python Skill/skill-lifecycle/tests/test_bundle.py -q` → **Ran 12 tests, OK (skipped=1)**；behavior-cases.md:3 明确"尚未运行，不是通过记录"，未把结构检查冒充行为证据。
6. **本组 10 个 v1 skill 的 State Changes 全部使用已注册状态**：逐条比对 governance/state-registry.yaml，defect-triage / release-planning / deployment-execution / release-verification / signal-collection / signal-triage / incident-response / optimization-planning / post-release-review / refactor-planning 引用的状态名 0 个未注册（含 WORKFLOW_BLOCKED / OBSERVABILITY_GAP / RELEASE_PAUSED 等边界态）。auto-test "testing-workflow 仅是领域注册 ID"（SKILL.md:25）与 governance/workflow-registry.yaml:80-92 事实一致，不是悬空引用。
7. **fact-check 的"查不到≠可以编"红线落地为可执行判据**：SKILL.md:10-11（IRON LAW + 禁止编造核验）、:66-88（四值判定 + ⚠️ 必标边界 + ❓ 必写原因与下一步）、:53-57（反证搜索必做、独立源才叫交叉、"再问 AI 不算证据"），是"声明了能力 → 有对应动作"的正面样本。

## 三、问题清单

> 等级口径按 self-audit-checklist.md:86：P0 = 阻断性/明显错误（引用断裂、术语冲突影响执行）；P1 = 不一致但不阻塞；P2 = 轻微（文句/建议）。"证据原文"为文件内逐字摘录，可 grep 复核。

### P1（不一致，需修）

| ID | skill | 文件:行 | 等级 | 维度 | 现象 | 证据原文 | 判据 | 修复方向 |
|---|---|---|---|---|---|---|---|---|
| D-01 | bug-fix / fact-check | bug-fix/README.md:12,19,43；bug-fix/CONTEXT.md:9,58；bug-fix/assets/fix-task-list-template.md:29,32,40；bug-fix/assets/locate-report-template.md:10；fact-check/README.md:38；fact-check/CONTEXT.md:30 | P1 | 跨位置同步 | 回归委托仍写"按需 Testing"，而 SKILL 正文已按 D-19 改为 auto-test、Test/README.md:8 明确 Testing 已归档不再作备用入口 → 模型按 README/模板执行会路由到已归档技能 | `回归 → 开发自测 + 按需 Testing`（README:12）；`回归由开发自测 + 按需 Testing`（CONTEXT:58）；`已写代码的验收 → Testing / auto-test`（fact-check/README:38）；对照 SKILL.md:102 `调 auto-test（L0-L4 分层全量回归）`、CONTEXT.md:53 D-19 | 活跃文件中"按需 Testing"清零（D-xx 历史决策记录除外） | 上述 11 处统一改"auto-test（L0-L4 分层回归）"；bug-fix CONTEXT Q2（:58）改为 auto-test 与 D-19 自洽；fact-check README/CONTEXT 同步。F-M1 只覆盖 auto-test/shared 侧，本条是其未覆盖的 bug-fix/fact-check 侧 |
| D-02 | 12 个 legacy-wrapper（本组 auto-test/bug-fix/oss-radar/skill-evolver/skill-optimizer） | auto-test/SKILL.md:229；bug-fix/SKILL.md:258；oss-radar/SKILL.md:199；skill-evolver/SKILL.md:250；skill-optimizer/SKILL.md:276（其余 7 个同款） | P1 | 可移植性 / 声明-流程 | State Changes 声明"状态名来自 governance/state-registry.yaml"，但安装器不分发 governance（`scripts/install-skills.py:104-108` EXCLUDED_TOP_DIRS 含 governance），copy/link 安装副本中该引用悬空；shared/templates/workflow.yaml 未提供状态枚举 | `The exact state names come from `governance/state-registry.yaml`.`（各 wrapper State Changes 末行）；install-skills.py:104-108 排除列表含 "governance" | copy/link 安装后 12 个入口的"状态名来源"可达，或显式声明安装副本降级口径 | 二选一：① 把状态枚举做成 shared 可分发契约（需同步治理单源决策）；② 改文"正式状态名以源仓 registry 为准；安装副本以 shared/templates/workflow.yaml + 项目 .spec/workflow.yaml 现状为准，未授权不写正式状态" |
| D-03 | deployment-execution / release-verification / signal-collection | deployment-execution/SKILL.md:30；release-verification/SKILL.md:49；signal-collection/SKILL.md:37 | P1 | 逻辑闭环 | 跨 skill 路由把两个 skill id 用 "/" 拼成一条路径（形如 `../a/b`），作为路径解析指向不存在的目录；shared/skill-contract.md:33-38 规定路由只写 skill id；机械门禁 check-installed-refs.py:38-39 的 REF 正则只匹配带扩展名的引用，漏检此形态（本轮 checked=539 全绿但未覆盖） | `将异常路由给 ../release-verification/incident-response`；`信号异常转 ../signal-triage/incident-response`；`交给 ../signal-triage/product-analytics` | 非法路由写法全仓清零；checker 增加 "`../` + skill-id + `/` + skill-id" 扫描规则 | 改为 `release-verification` / `incident-response`（canonical id，按 §1.4 只写 id）；checker 补扫描规则后回归 |
| D-04 | quality-inspection / signal-collection / signal-triage / project-onboarding | quality-inspection/SKILL.md:145；signal-collection/SKILL.md:49；signal-triage/SKILL.md:49；project-onboarding/SKILL.md:185（另 PRD/product-analytics/SKILL.md:49 同类） | P1 | 逻辑闭环 | Failure Route 指向的 `Observability-Design`、`Technical-Discovery` 不在 skill-registry（46 项无此 id）、仓内无对应 SKILL.md，仅存在于 docs 旧方案；异常路径断头 | `转 `Observability-Design`，不宣称运行健康`；`转 `Technical-Discovery`，不编造结果`；docs/个人工程体系-可执行实施方案-v1.md:460 才出现过 Observability-Design | Failure Route 只指向 registry 已注册 id，或显式标注"能力未落地"并给降级目标 | 改指已注册 skill（如 `project-onboarding` / `defect-triage` / `tech-review`）或加"（未落地，暂降级到 X）"；若确需该能力需先注册 skill，不在本轮擅自新增 |
| D-05 | defect-triage / optimization-planning / refactor-planning（v1 族） | defect-triage/SKILL.md:44,53；optimization-planning/SKILL.md:41；refactor-planning/SKILL.md:53；governance/artifact-registry.yaml:4-470；scripts/validate_core.py:310 | P1 | 声明-流程 / 产物契约 | 三个 v1 skill 的主产物目录在 artifact-registry 无对应 type（全文无 defect/optimization/refactor 类型），validate_core 对未知 type 直接报错 → 正式执行产物无法登记 manifest（artifact-contract.md:23 "Every material artifact has a stable manifest entry"）；13 个 v1 中仅 release-planning:54 与 refactor-planning:56 写 manifest 更新，其余未声明登记义务 | `为信号生成 `DEF-*`……写入 `.spec/defects/<id>.md``；`.spec/optimization/<id>.md`；`.spec/refactor/<id>.md`；`unknown artifact type: {aid} -> {typ}`（validate_core.py:310） | 三类产物有注册 type 或明确映射，且各 skill Outputs 声明 manifest type | registry 增 `defect`/`optimization`/`refactor` 三型（推荐），或在相应 skill Outputs 写明 "manifest type: triage/decision"；未写 manifest 的 v1 skill 补一行登记义务 |
| D-06 | defect-triage / incident-response / release-planning（+ 全 wrapper 的 execution record） | shared/templates/defect-triage.md:3；shared/templates/incident-report.yaml:2；shared/templates/release-plan.yaml:2；shared/templates/execution-record.yaml:3 | P1 | 声明-承接（双向断头） | 4 个 shared 模板全仓 grep **0 引用**（本轮逐名搜索确认），对应 skill 均未引用任何模板；且模板与 skill 的 ID/格式口径冲突：skill 写 `DEF-*`、模板写 `TRIAGE-YYYYMMDD-001`；release-planning 产 .md 而模板是 .yaml；incident ID 前缀 `INC-` 在 skill 中未声明 | `- Triage ID: `TRIAGE-YYYYMMDD-001``；`releaseId: REL-YYYYMMDD-001`；`incidentId: INC-YYYYMMDD-001`；skill 侧 `DEF-*`（defect-triage:44）、`release-plan.md`（release-planning:51） | 模板与 skill 双向可追溯、ID 前缀唯一 | 二选一：① 接线——三个 skill 的 Outputs/Procedure 引用对应模板并统一 ID 前缀（推荐 TRIAGE→DEF 或反之，全文一次改）；② 以 skill 为唯一口径，删除 4 个 orphan 模板（execution-record 内容已被 skill-contract.md §5 覆盖，可删） |
| D-07 | skill-evolver | skill-evolver/SKILL.md:38；evolution/README.md:3；scripts/install-skills.py:104-108 | P1 | 可移植性 | 数据池 `../../evolution/` 声明"不外发部署"（installer 也确实排除 evolution），但 SKILL 未给安装副本运行时的落点/降级；首次运行会向外层目录建池，与本组其它三池（bug-fix/skill-optimizer/oss-radar）已有降级不一致 | `../../evolution/`（仓库根相对写法，可移植）——……**不外发部署**（:38）；`集中一处、不外发部署（部署副本只含 skill 文件，不含数据池）`（evolution/README:3） | 安装副本/其它项目运行时，偏好库/信号/台账有明确落点或"待反馈"口径 | SKILL §二/⓪ 补一句（与 bug-fix:18 同款）："安装副本/其它项目运行时写用户指定维护目录或项目本地，不写源仓，待反馈后统一回写本池"；evolution/README 同步 |
| D-08 | auto-test / oss-radar | auto-test/SKILL.md:51,55-62；oss-radar/SKILL.md:20,31；oss-radar/README.md:7 | P1 | 枚举一致 | auto-test 标题"主流程（7 步）"但正文列 1-8 共 8 步（第 8 步"汇总与门禁"被漏计）；oss-radar 标题"双泳道 × 双模式 × 五步"与正文"**五步**：⓪…⑤"（6 项）、README:7 括号内 6 个动作均不一致 | `## 三、主流程（7 步）`（:51）+"8. **汇总与门禁**……"（:62）；`双泳道 × 双模式 × 五步`（:20）+"**五步**：⓪ 装载 watchlist → ① 发现 → ② 采集 → ③ 提炼 → ④ 反哺产出 → ⑤ 台账回写"（:31） | 标题数字 = 枚举项数（全仓同族计数 grep 复核） | auto-test 改"8 步"；oss-radar 改"六步"（或把 ⓪ 装载并入 ①），README:7 同步；修复后回查"步"关键词 |
| D-09 | quality-inspection | quality-inspection/SKILL.md:136-138；quality-inspection/assets/inspection-report-template.md:11 | P1 | 声明-流程 / 契约冲突 | Gate 节自造 Gate 值 `INSPECTION_PASS/CONDITIONAL/BLOCKED`，违反 shared/skill-contract.md:98 §6 与 shared/gate-policy.md:76"禁自造 Gate 值"；这三个名字在 state-registry.yaml:141-167 是 **state** 而非 Gate | `- `INSPECTION_PASS`：确定性检查结果可复核……`（:136-138）；`Gate：INSPECTION_PASS \| INSPECTION_CONDITIONAL \| INSPECTION_BLOCKED`（模板:11） | Gate 节只出现 PASS/CONDITIONAL/BLOCKED；INSPECTION_* 仅出现在 State Changes | Gate 改三值；INSPECTION_* 保留在 State Changes（已是注册状态）；模板:11 同步 |
| D-10 | auto-test | Test/auto-test/project/README.md:20 | P1 | 逻辑闭环（引用断裂） | "仓库根 `../../shared/`"从 project/ 解析到 `Test/shared/`（不存在）；从 project/ 到仓根是三层，同文件 `../SKILL.md` 却正确，属迁移笔误 | `两者冲突时以 SKILL.md 和仓库根 `../../shared/` 契约为准`（:20）；实测 Test/auto-test/project/../../shared → Test/shared（MISSING），../../../shared 存在 | 该路径解析可达 | 改 `../../../shared/`；同类迁移文件用脚本复核一遍（本轮其它 in-scope 文件未发现） |

### P2（轻微/建议）

| ID | skill | 文件:行 | 等级 | 维度 | 现象 | 证据原文 | 判据 | 修复方向 |
|---|---|---|---|---|---|---|---|---|
| D-11 | auto-test | SKILL.md（全文未提 project/） | P2 | 声明-流程 | README:12/CONTEXT:20/project/README:18-22 已声明 project/ 只读研究资料，但 SKILL.md（触发后唯一必加载文件）无一句声明；project/ 内含"要做企业级 Auto-Test 平台"的项目计划全文，执行 agent 可能误当本 skill 的需求/路线图 | project/项目计划-企业级AI自动化测试.md:1 "# 项目计划：企业级 AI 自动化测试系统（Auto-Test）"；对照 SKILL.md 全文无 "project/" | SKILL.md 目录/边界段有一句 project/ 定位 | §一 定位或 §五 产物约定加："本目录 project/ = 旧独立项目只读研究资料，不参与测试执行，执行入口仅 SKILL.md（详见 project/README.md）" |
| D-12 | auto-test | CONTEXT.md:26,27；project/README.md:4 | P2 | 可移植性 | 随 skill 分发的文件中残留机器绝对路径；其中 CONTEXT D-02（2026-10-18）与 project/README 是本轮 Phase 0 新增内容（非历史证据），F-M4 的"历史只读保留"口径未覆盖 | `生效副本 C:\Users\15136\.zcode\skills\auto-test`（:26）；`旧独立项目 D:\project\agent-project\auto-test`（:27）；`来源：2026-09-18 的独立仓库 D:\project\agent-project\auto-test`（:4） | 分发包内无本机绝对路径 | 改写为"当时生效副本（本机路径已不保留）"与"原独立 git 仓库（远端 https://github.com/tengerfly/auto-test）"，保留 commit b0b78b6 追溯 |
| D-13 | auto-test | SKILL.md:5-6 | P2 | 术语/跨位置同步 | frontmatter `legacy-alias: null`，但 registry legacyAliases 为 `Testing/testing`（skill-registry.yaml:388-395）；contract §2 要求历史名进 metadata.legacy-alias；用户本轮刚因 null 占位投诉，宿主若展示 frontmatter 仍可能显示 null | `legacy-alias: null`（:6）；registry:388-395 `legacyAliases: - Testing - testing`；CONTEXT:27 "frontmatter 的 legacy-alias: null 是契约允许的 YAML null，保留不动" | frontmatter legacy-alias = registry aliases（或删键并在 registry 注明无 alias） | 设为 `legacy-alias: "Testing"`（与 registry 对齐），CONTEXT D-02 补一句修订结论；或删键并改 registry 说明 |
| D-14 | auto-test | SKILL.md:7 | P2 | 可移植性 | compatibility 声明"需要 Bash"，与"跨平台直接可用"目标及仓内 PowerShell 工具链矛盾；正文命令模板均为 npm/pnpm，无 Bash 必需证据 | `compatibility: "ZCode / Claude Code 等 coding agent。需要 Bash；…"` | 平台声明与正文命令/依赖一致 | 改"需要 shell（Bash/PowerShell 任一）"或删该子句 |
| D-15 | 多个（本组 6 处） | skill-optimizer/CONTEXT.md:1,SKILL.md:142,assets/self-audit-checklist.md:11,assets/vibe-principles-mapping.md:16,20,references/known-issue-patterns.md:4；project-onboarding/SKILL.md:124-129；12 wrapper 兼容层同一句 | P2 | 术语/可移植性 | 实际目录是 `workflow/`（root README:61），多处写 `WorkFlow/`；Windows 大小写不敏感可解析，Linux/macOS 直接断。另 legacy alias 大写与 canonical id 混用（PRD-Workflow/DEV-Workflow/Release-Workflow 与 workflow-registry 的 prd-workflow/dev-workflow/release-workflow） | `Run when ... `WorkFlow/` routes a compatible stage`（wrapper 兼容层）；`根 README/WorkFlow/其他 skill/issue`（:142）；`../../WorkFlow/自动化环节`（vibe:16）；实际 workflow\SKILL.md 存在、WorkFlow 不存在 | 目录/技能引用与 git 实际大小写一致（Linux 可解析） | wrapper 兼容层与 assets 内统一改 `workflow`；技能引用统一 canonical id（小写），legacy alias 仅出现在 registry/显式历史段 |
| D-16 | source-reading | README.md:15-19；SKILL.md:95-104 | P2 | 跨位置同步 | README 产出清单只列 00-总览/01-*/章节规划，SKILL.md 已含 `导读.md`（小仓/批量单文档）与 `大纲.md`（④ 大纲先行留档）→ README 未同步 2026-09-19 升级 | `- `章节规划.md` —— 大仓的拆章方案留档`（README:19）；SKILL.md:101 `\| `导读.md` \| 单文档多章节形态……`；:103 `\| `大纲.md` \| ④ 大纲先行留档……` | README 产出清单 = SKILL.md 产物落盘表 | README 补两行并注明"大纲先行/对纲复核" |
| D-17 | project-onboarding | SKILL.md:170,180,203 | P2 | 声明-流程 | Gate 节用状态名 `ONBOARDING_BASELINE_READY`/`BASELINE_INCOMPLETE` 表述通过/不通过，未落 `PASS/CONDITIONAL/BLOCKED`；State Changes 写"建议状态"弱化契约 | `只有同时满足以下条件才能通过 `ONBOARDING_BASELINE_READY``；`否则输出 `BASELINE_INCOMPLETE``；`建议状态：` | Gate 节按 gate-policy 三值表述；状态名只出现在 State Changes | Gate 改"PASS 条件：…；未满足 → BLOCKED"，State Changes 保留状态名并删"建议"（已注册即有效） |
| D-18 | quality-inspection | SKILL.md:118-124；assets/inspection-report-template.md；缺 README/CONTEXT | P2 | 声明-承接/一致性 | Outputs 声明 5 个文件，模板只承接 1 份报告（gate-results.yaml/findings.md/trend.md/evidence-index.md 无骨架）；且缺 README/CONTEXT（19 个兄弟 skill 均有） | `└── evidence-index.md`（:123）；模板全文只有"项目质量巡检报告"一份 | 声明产出的每个文件有模板/骨架或写明派生关系 | 模板补四文件骨架，或 Outputs 注"后四件由报告派生、格式见报告对应节"；补 3 行 README + CONTEXT（术语/决策） |
| D-19 | skill-optimizer | README.md:22；skill-evolver/SKILL.md:120 | P2 | 跨位置同步 | 宿主同步口径过期：README 仍写"同步 CodeBuddy 副本"，Phase 0 后宿主收口为 install-skills.py 四目标（root README:46-50，.codebuddy 已停用）；skill-evolver:120 把 `scripts/sync-skills.sh` 与安装器并列，而 root README:48 已标其仅 Git Bash 遗留场景 | `落点=先源仓库再同步 CodeBuddy 副本`（README:22）；`（或 `scripts/sync-skills.sh`）`（skill-evolver:120） | 活跃文档只写当前同步口径；legacy 脚本加"仅 Git Bash 遗留"标注 | README 改"源仓 → python scripts/install-skills.py --target <宿主 skills 根> → --check 全绿"；sync-skills.sh 出现处加 legacy 标注 |
| D-20 | skill-optimizer | SKILL.md:190,27,40 | P2 | 逻辑闭环/文句 | 资源清单 6 项中 5 项缺 `assets/` 前缀（实际都在 assets/），仅 issue-template 给了 shared 绝对路径；issue 结构两种写法不一致 | `- `../../shared/templates/issue-template.md`、`signal-checklist.md`、`skill-writing-standard.md`、…`（:190）；:27 `<序号>.md` vs :40 `<序号>-<标题>.md` | 资源清单路径全部可解析；同一结构只写一种形式 | 补 `assets/` 前缀；两处 issue 结构统一为 `<序号>-<标题>.md` |
| D-21 | skill-optimizer | CONTEXT.md:1,5 | P2 | 跨位置同步/口径 | 顶部 LEGACY COMPATIBILITY NOTICE 自称"preserves historical material"，与同文件 :5"术语对齐源 + 决策日志"角色冲突（skill-writing-standard 维度七要求"对照 CONTEXT.md"）；该 notice 只注入 10 个文件（技术评审/代码评审/UI 评审/PRD 评审 CONTEXT + 2 legacy refs + 3 其它），同族 wrapper 的 bug-fix/oss-radar/skill-evolver CONTEXT 没有 → 子集不一致 | :1 `This file preserves historical material. The active ... rules are defined by `shared/...``；:5 `术语对齐源 + 决策日志` | CONTEXT 的权威角色与 legacy notice 不矛盾；同族注入规则一致 | 删 notice，或改"决策历史记录；现行规则以 shared/ 为准"；若保留则全仓按同一规则统一 |
| D-22 | essence-distill / skill-optimizer | essence-distill/SKILL.md:41；essence-distill/references/extract-playbook.md:26；skill-optimizer/SKILL.md:58,193 | P2 | 逻辑闭环/可移植 | 用同层兄弟 `../source-reading/...`、`../bug-fix/assets/pattern-card-template.md` 引用技能私有资产：双视图实测可达（checker PASS），但违反 shared/skill-contract.md:36 §1.4 形式 2"逻辑引用 `<skill-id>/内部路径`（不带 ../）"；且 pattern-card 被 bug-fix+skill-optimizer 两个 skill 需要，按 §1.4 应"提升进 shared/" | 克隆策略复用 `../source-reading/references/clone-playbook.md`；模板见 `../bug-fix/assets/pattern-card-template.md` | 跨 skill 引用只用 §1.4 两种形式；被 ≥2 skill 需要的资产在 shared/ | 改逻辑引用（`source-reading/references/clone-playbook.md`）；把 pattern-card-template 提升 `shared/templates/pattern-card-template.md` 后两处引用 |
| D-23 | auto-test / source-reading / skill-lifecycle | auto-test/references/specialty-testing-guide.md:3；source-reading/references/clone-playbook.md:48；Skill/skill-lifecycle/assets/issue-template.md:12 | P2 | 文句质量 | 中英混杂、列表项重复、繁体字混用 | `本层回答「扛不扛得住、安不安全、 everyone 能不能用」`；`docs/ examples/ examples/ benchmarks/`；`复現条件与脱敏证据` | 无混入英文/重复项/繁体字（全仓 grep） | 分别改"所有人能不能用"、去重一个 examples/、"复現"→"复现" |
| D-24 | source-reading | references/clone-playbook.md:3 | P2 | 逻辑闭环/文句 | 铁律"克隆到工作区**外**的临时目录"与括注示例 `<工作区>/.spec/源码学习/_clones/`（在工作区内）自相矛盾；SKILL.md:30 同句"工作区外" | `克隆到工作区**外**的临时目录（如 `<工作区>/.spec/源码学习/_clones/<owner>__<repo>` 或系统临时目录）` | 同一句口径自洽（"在研项目之外"或"工作区内 _clones"二选一） | 改"在研项目工作区之外；本 skill 自身工作区可用 .spec/源码学习/_clones/" |
| D-25 | essence-distill | assets/essence-template.md:12；SKILL.md:35 | P2 | 跨位置同步 | 模板固定"八条精华"，SKILL 声明速览档"5~8 条精华" | `## 八条精华`；`一页纸：定位 3 句 + 5~8 条精华 + 深读建议` | 模板与正文档位口径一致 | 改"## 精华（5~8 条）" |
| D-26 | essence-distill | references/extract-playbook.md:19,26 | P2 | 声明-流程 | 取源依赖 pdftotext/pypdf/ebooklib/whisper 等外部工具/库，未给"检测→降级→停"步骤（仅 OCR 缺失有说明；对比 oss-radar/source-reading 的降级链） | `优先 `pdftotext -layout`（poppler）或 python `pypdf` 抽取` | 外部依赖声明处有检测与缺失处理 | 补"优先 X→不可用 Y→都不可用则停并说明文本可得性结论"；extract-playbook 文件头注明依赖 |
| D-27 | auto-test（project/ 历史资料） | project/旧项目问题日志.md:13；project/项目计划-企业级AI自动化测试.md:97；project/README.md:27 | P2 | 跨位置同步/时效 | 迁移后历史快照存在与现状冲突的表述：问题日志"当前 .spec 下没有…"在本仓语境失真（本仓 .spec 有 auto-test 产物）；项目计划仍写"人盯着的深度验收继续用 Testing Skill"（快照早于 2026-09-22 Testing 归档）；project/README 已声明"研究快照、不得覆盖 SKILL.md"但未点名 Testing 时间线 | `暂无问题记录：当前 .spec 下没有评审/测试/Bug 类产物目录。`（:13）；`人盯着的深度验收继续用 Testing Skill`（项目计划:97） | 历史快照不被读成现状的操作说明齐备 | project/README 加一行"快照早于 2026-09-22 Testing 归档，Testing 相关表述已被 auto-test 取代，仅作历史"；问题日志加"该句指旧独立项目 .spec" |
| D-28 | 13 个 v1/Other skill | 各 agents/openai.yaml:4 | P2 | 简洁/一致性 | 13 个入口的 default_prompt 两种模板并存（6 个"严格按 SKILL.md 执行，保存证据和状态，不越权执行生产动作。"、7 个"按 SKILL.md 执行，先标记事实与未知项，再产出可验证交付物。"），generic 且未体现风险档 | 见上两串原文 | 同族入口的默认提示一致（或按风险分档有依据） | 统一为一种；若按风险分档，在模板注释写明分档依据 |
| D-29 | 机械面（scripts） | scripts/check-installed-refs.py:178；对比 Skill/skill-lifecycle/scripts/check_bundle.py:140-142 | P2 | 可移植性/可复核性 | 脚本中文统计行在 Windows 捕获/重定向时乱码（本轮实测 checked=539 后接乱码），未像 check_bundle.py 那样 reconfigure stdout；其它应用解析该输出时会看到坏字节 | check-installed-refs.py:178 直接 print 中文；check_bundle.py:140-142 有 stream.reconfigure(encoding="utf-8") | 脚本输出在任意平台/编码环境下可读 | main() 前对 stdout/stderr reconfigure utf-8（与 check_bundle.py 同款）；同时把 D-03 的漏检规则补进 REF/新增 pattern |

## 四、机械扫描结果

### 4.1 指定三命令（全部 PASS）

```text
python scripts/validate_core.py skill-contract --project-root .   → skill-contract validation passed (exit 0)
python scripts/validate_core.py registry --project-root .         → registry validation passed (exit 0)
python scripts/check-installed-refs.py --project-root . --quiet   → checked=539  分类层写法=0  源仓不可达=0  副本不可达=0  RESULT: PASS (exit 0)
```
（第三行在 PowerShell 捕获时中文乱码，见 D-29；英文 RESULT 可解析。）

### 4.2 本组补充机械核对

| 检查 | 结果 | 证据/方法 |
|---|---|---|
| registry ↔ 目录 ↔ frontmatter name | 21/21 一致（全仓 45/45，与 lead 一致） | 脚本解析 frontmatter + registry；0 mismatch |
| 全仓 skill 计数 | 46 条 = 45 active + 1 external（skill-knowledge）；contractLevel：v1 28 / legacy-wrapper 12 / legacy-adapter 5 | registry 解析；与 README.md:6 "45 个本地 Skill"、docs/当前项目介绍:56 一致 |
| 21 个 SKILL.md 相对 markdown 链接 | 0 死链 | 逐文件解析本地链接并 os.path.exists |
| 反引号相对路径（含目录） | 1 处真实断链：Test/auto-test/project/README.md:20（D-10）；其余解析可达 | 逐文件解析并 resolve |
| 机器绝对路径 | 本组 3 处（均 auto-test，D-12）；全仓历史证据另有若干（F-M4 已知） | grep `[A-Za-z]:[/\\]`、C:/Users、D:/project |
| 危险指令 / 凭据 / 外联 | 0（仅 self-audit-checklist.md:74 自身条款举例 rm -rf / curl 管道等） | grep 危险模式 + sk-/ghp_/AKIA/password= |
| 占位符残留 | 模板文件中的 `{{…}}` 均为有意占位；SKILL.md 本体 0 个未替换占位符 | grep <Skill-Name>/{{…}}/TODO/FIXME |
| null / auto-test-legacy 残留 | SKILL 正文 null 已修（:162）；auto-test-legacy 只出现在计划/issue/project README 的历史说明（描述"已删除"），无活跃命名；frontmatter legacy-alias: null 仍在（D-13） | grep 全组 |
| Testing 残留 | 本组 27 处；其中执行性口径 13 处（D-01），其历史/决策记录/ARCHIVED 语境可保留 | grep "Testing" in scope |
| 状态名 vs state-registry | 10 个 v1 skill 引用的状态名 0 个未注册 | 抽取 State Changes 反引号片段逐个比对 |
| State Changes 之外的自造 Gate 值 | 2 个 skill：quality-inspection（D-09 列 Gate 值）、project-onboarding（D-17 用状态名表述 Gate） | grep Gate 节 |
| 步数/枚举计数 | 2 处错：auto-test 7 vs 8、oss-radar 五步 vs 6（D-08）；其余（bug-fix 10 步、source-reading 八步、fact-check 四步、essence-distill 七步、skill-evolver 8 铁律/5 护栏、skill-optimizer 4 模式/8 维）均自洽 | 逐 skill 数标题/步骤 |
| shared/templates 被引用情况 | 4 个 orphan：defect-triage.md / incident-report.yaml / release-plan.yaml / execution-record.yaml（全仓 grep 0） | D-06 |
| install-skills.py 分发集合 | 仅 skills + shared；排除 governance/issue/evolution/bug-patterns/chats/scripts/docs/evals | install-skills.py:104-108 |
| skill-lifecycle 独立包 | 无 shared/governance/issue/evolution 引用；tests 12 OK (skipped=1)；check_bundle ok（files=15, errors=[]） | grep + 实跑 |
| skill-lifecycle 代码安全 | 只读；拒 symlink/reparse；不执行被测脚本；subprocess 用 -I -S -B -X utf8；无网络/上传 | 读 scripts/check_bundle.py、tests/test_bundle.py |

### 4.3 非阻塞观察（范围外，供 lead 取舍）

- `README.md:130` 写 installer "18 unit tests"，`docs/体系修复与评审执行计划-20261018.md:17` 写"19 tests"，而 `scripts/tests/test_install_skills.py` 实际有 23 个 `def test_` → 三处口径不一致（与 F-M2 同类，属历史校验数字过期）。
- `shared/skill-contract.md:49` frontmatter 示例写 `contract-level: v2 | legacy-wrapper`，而 registry 实际值集合为 `v1 | legacy-wrapper | legacy-adapter`（validate_core.py:267-278 支持三值）→ 契约文档示例枚举与实现/注册表不一致（shared/ 文件不在本组范围，交 lead 定）。
- 本组 3 个 legacy-adapter skill（essence-distill/fact-check/source-reading）无 `metadata.contract-level` 且无 v2 必备章节——已由 lead F-M3 覆盖（契约允许、风格不一致），本报告不重复。
- auto-test 仍为 legacy-wrapper 并含 LEGACY BODY BOUNDARY（lead F-M5）——按"契约机制非能力降级"理解，未重复。

## 五、未覆盖 / 不确定项

1. **行为层未验证**：未跑付费/行为级 eval（按执行计划"行为层付费评测不跑（如实标 blocked）"）；本报告结论均来自文本 + 机械扫描，不含真实模型执行效果。
2. **安装/链接 e2e 未由本组验证**：copy/link 两模式端到端由 portable-installer 负责，本报告 D-02/D-07 只基于"分发集合"静态推断。
3. **全量 validate.ps1 未跑**（按任务约束不跑）；三命令 PASS 只覆盖 skill-contract/registry/跨视图引用，不等价于全量校验。
4. **project/ 竞品数据时效**：project/ 内 2026-09-18 的 Star/市场/定价数据已过时，project/README:27 已声明快照性质，本报告未复核外部事实（属研究资料，不阻塞）。
5. **skill-evolver/SKILL.md:34 引用的 `.spec/开源情报/2026-09-18-skill进化器调研.md`** 仅源仓存在、安装副本不可达；作为"灵感出处"provenance 可接受，未列缺陷，建议换机场景注明"源仓资料"。
6. **auto-test "引擎模式"真实可用性**：本机无 auto-test CLI/MCP，无法验证引擎分支，仅确认会话模式降级路径完整。
7. **跨组重复风险**：D-09/D-17（Gate 值）、D-15（WorkFlow 大小写）可能与其他组报告重叠，lead 去重时以证据合并即可。
8. 本组未审 `workflow/`、`shared/`、`scripts/` 正文（只在核对时引用），其问题不在本组结论内。

## 六、优先建议（Top 5）

1. **清 Testing 残留（D-01 + lead F-M1 合并一次修）**：bug-fix/fact-check 共 11 处"按需 Testing"是当前最可能误导执行的路由断头（Testing 已归档不可发现）；一次性改为 auto-test，并 grep 全仓"按需 Testing"清零。
2. **补 artifact 契约闭环（D-05/D-06）**：先定 `defect/optimization/refactor` 三型的归属（registry 增型 or 映射到 triage/decision），再决定 4 个 orphan 模板"接线还是删除"，同步统一 ID 前缀（DEF/TRIAGE、REL、INC）。这是"其他应用正式使用"的交接底座，且改动面小、可机械复核。
3. **修悬空/畸形路由并补机械门禁（D-03/D-04）**：3 处 `../a/b` + 5 处未注册技能路由；同时给 check-installed-refs.py 补两条规则（无扩展名的 skill 路由、`../skill/skill` 形态），防复发。
4. **可移植闭环（D-07/D-02/D-12）**：skill-evolver 安装副本数据池落点必须写清（对应用户"换机/软链接直接可用"目标）；12 wrapper 的 governance 状态引用给降级口径；auto-test 两处 Phase 0 新增机器路径改相对/URL。
5. **低风险确定性小修（D-08/D-09/D-10/D-17/D-19/D-23）**：步数 2 处、Gate 值 1 个 skill、project/README 路径 1 处、文档过期 2 处、错别字 3 处——每处 1 行，改完可在全仓 grep 复核清零。

---

**报告自检**：覆盖 21/21 个指定 skill；每条问题都有文件:行 + 原文 + 判据 + 修复方向；"做得好"引用具体行；机械命令与补充扫描均给出可复核命令/方法；未写 issue 池、未改任何 skill/文档/脚本、未 commit。

## 七、修复执行记录（2026-10-18 夜，task-12 修复阶段）

> 性质：按本报告 P1/P2 在 **Test/、Other/、Skill/ 写域**内修复；未触碰 Lead 保留项（D-02/D-05/D-06 模板文件本身、shared/、docs/、根 README）。`evolution/README.md` 为 Lead 明确指派同步（写域外唯一例外）。每批改动后均跑三命令，最终结果见下。

| 报告条目 | 修复摘要 | 涉及文件 |
|---|---|---|
| D-01 | Testing 残留全部改 auto-test：「按需 Testing」统一替换为 auto-test（L0-L4 分层回归）；历史 D-06/D-08/D-14/D-19 行加「Testing 已于 2026-09-22 归档」注记（不抹历史）；fact-check description 内相对路径改 `auto-test`；skill-optimizer 心法映射表 Testing→auto-test、归档路径改指 auto-test 指南 | bug-fix README/CONTEXT/2 模板/SKILL、fact-check README/CONTEXT/SKILL、Test/auto-test README/CONTEXT、skill-optimizer assets/vibe-principles-mapping |
| D-03 | 3 处畸形路由 `../a/b` 改「canonical id / canonical id」 | deployment-execution:30、release-verification:49、signal-collection:37 |
| D-04 | 悬空路由清零：Observability-Design→`signal-collection`（补采集/埋点并登记 OBSERVABILITY_GAP；signal-collection 自指改为交 `quality-inspection` 补埋点）；Technical-Discovery→`workflow` 重新路由 | quality-inspection、signal-collection、signal-triage、project-onboarding |
| D-06（skill 侧） | 三个 v1 skill 接线 shared/templates 并统一 ID 前缀：defect-triage→`DEF-*`+defect-triage.md；incident-response→`INC-*`+incident-report.yaml；release-planning→`REL-*`+release-plan.yaml | 三个 SKILL.md（模板文件本身交 Lead） |
| D-07 | skill-evolver 补「安装副本/其它项目不写源仓 evolution/，改用用户指定目录或项目本地，待反馈回写」；evolution/README 同步同口径 | skill-evolver/SKILL.md、evolution/README.md |
| D-08 | auto-test「主流程（7 步）」→8 步；oss-radar 标题/正文/README「五步」→六步 | auto-test/SKILL.md、oss-radar/SKILL.md+README |
| D-09 | quality-inspection Gate 改 `PASS/CONDITIONAL/BLOCKED`（INSPECTION_* 保留为对应状态）；报告模板 Gate 行同步 | quality-inspection/SKILL.md + assets 模板 |
| D-10 | project/README `../../shared/`→`../../../shared/` | Test/auto-test/project/README.md |
| D-11 | SKILL.md 增 project/ 只读边界声明（执行入口仅 SKILL.md） | auto-test/SKILL.md |
| D-12 | 机器绝对路径清零：CONTEXT D-01/D-02 与 project/README 改「当时本机生效副本/原仓库远端」表述 | auto-test/CONTEXT.md、project/README.md |
| D-13 | frontmatter `legacy-alias: null`→`"Testing"`（与 registry legacyAliases 对齐）；CONTEXT 新增 D-03 记录，D-02 行标注已被 D-03 修订 | auto-test/SKILL.md、CONTEXT.md |
| D-14 | compatibility「需要 Bash」→「需要 shell（Bash/PowerShell 任一）」 | auto-test/SKILL.md |
| D-15 | `WorkFlow/`→`workflow`（5 个 wrapper 兼容层、skill-optimizer 3 处 assets/references、Other/README）；project-onboarding 路由/下游改 canonical kebab（prd-workflow、dev-workflow、release-workflow、operations-workflow、impact-analysis、defect-triage、refactor-planning、incident-response、product-analytics、optimization-planning）；Other/README 清单改 canonical id | 多文件 |
| D-16 | source-reading README 产出清单补 `导读.md`、`大纲.md` | source-reading/README.md |
| D-17 | project-onboarding Gate 改「全部条件满足→PASS（状态 ONBOARDING_BASELINE_READY）/否则 BLOCKED（状态 BASELINE_INCOMPLETE）」；State Changes 删「建议」 | project-onboarding/SKILL.md |
| D-18 | quality-inspection Outputs 补四个派生件与模板节映射；补 README + CONTEXT | quality-inspection/SKILL.md、新增 README/CONTEXT |
| D-19 | skill-optimizer README 宿主同步口径改 install-skills.py + --check；skill-evolver 的 sync-skills.sh 标注「遗留，仅 Git Bash」 | skill-optimizer/README.md、skill-evolver/SKILL.md |
| D-20 | skill-optimizer 资源清单补 `assets/` 前缀；issue 结构统一 `<序号>-<标题>.md` | skill-optimizer/SKILL.md |
| D-21 | skill-optimizer CONTEXT 顶部 notice 改为「决策与术语历史记录，不作现行规则源」 | skill-optimizer/CONTEXT.md |
| D-22 | 同层兄弟引用改逻辑引用：`source-reading/references/clone-playbook.md`、`bug-fix/assets/pattern-card-template.md`（pattern-card 提升 shared/ 待 Lead） | essence-distill SKILL/references、skill-optimizer/SKILL.md |
| D-23 | 3 处文句：everyone→所有人、examples/ 去重、复現→复现 | auto-test guides、source-reading clone-playbook、skill-lifecycle asset |
| D-24 | 克隆目录口径统一为「在研项目工作区之外；本 skill 工作区可用 .spec/源码学习/_clones/」 | source-reading SKILL + clone-playbook |
| D-25 | essence 模板「八条精华」→「精华（5~8 条）」 | essence-distill/assets/essence-template.md |
| D-26 | 取源工具/库缺失补「声明缺失→用户提供文本→仍不可得停在第⓪步」降级 | essence-distill/references/extract-playbook.md |
| D-27 | project/README 增 Testing 归档时间线；旧项目问题日志「当前 .spec」改指旧项目并给本仓指引 | project 两文件 |
| D-28 | 12 个 in-scope `agents/openai.yaml` 的 default_prompt 统一为同一模板 | 12 个 yaml |
| anti-deadloop §号 / force-pass | bug-fix 超限口径改按 §3 三值处理；skill-optimizer §五→§4；severity 引用改 gate-policy §1；skill-optimizer CONTEXT D-27 行加「已撤销」注记并新增 D-45 订正记录 | bug-fix SKILL、skill-optimizer SKILL/assets/CONTEXT |
| **C-27**（Lead 追加） | skill-writing-standard §七 不采纳表「严重度加 P3 级」行改为「评审类 skill 只标 P0/P1/P2（P3 仅用于记录/backlog）；严重度定义见 shared/gate-policy.md §1」 | skill-optimizer/assets/skill-writing-standard.md |
| **C-12**（Lead 追加） | 删除 bug-fix/README 误插的英文 Gate 段，恢复 README 结构（流程代码块 → 三、目录与产出） | bug-fix/README.md |

**修复后校验（最终）**：
```text
python scripts/validate_core.py skill-contract --project-root .  → passed (exit 0)
python scripts/validate_core.py registry --project-root .        → passed (exit 0)
python scripts/check-installed-refs.py --project-root . --quiet  → checked=574  分类层=0 源仓不可达=0 副本不可达=0  RESULT: PASS (exit 0)
```
未跑全量 validate.ps1、未重锚 eval 基线、未 git commit（按指令）。修复阶段未做行为级验证。

**新增文件（5）**：Other/project-onboarding/{README,CONTEXT}.md、Other/quality-inspection/{README,CONTEXT}.md、Other/skill-evolver/README.md（与同族 skill 文档口径一致）。

**交 Lead / 未覆盖**：① D-02（12 wrapper 的 governance 状态来源口径）；② D-05（artifact-registry 增 defect/optimization/refactor 三型）；③ D-06 模板文件本身：defect-triage.md 的 `TRIAGE-` 需改为 `DEF-`（incident INC-/release REL- 已对齐），统一前缀 **DEF-/INC-/REL-**；④ D-22 pattern-card-template 提升 `shared/templates/`（当前已改逻辑引用）；⑤ D-29 scripts 双修（check-installed-refs.py stdout UTF-8 + 无扩展名路由扫描规则）；⑥ PRD 组 3 个 `agents/openai.yaml` 未统一（写域外）；⑦ legacy alias 散文（如 Bug-Fix/Code-Review 等称呼）仅在路由/架构路径处转 canonical，未做全量批量替换。