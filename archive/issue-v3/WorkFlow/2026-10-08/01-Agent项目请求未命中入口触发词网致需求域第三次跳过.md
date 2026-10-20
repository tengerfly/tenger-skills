# 用户说「我想做一个企业级 RAG 知识库 Agent 项目」仍未触发 WorkFlow，需求域第三次被跳过

> 归属 skill：`WorkFlow` ｜ 日期：2026-10-08 ｜ 来源：用户

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P0 |
| 标签 | `触发识别` / `流程缺陷` / `规则空转` |
| 优化状态 | 规则已改 + **首轮 fresh-agent 试跑已跑（2026-10-09）：未通过**。命中率 5/6，Agent 形态同句重跑 3 次中漏 1 次（判据可达但**随机漏检**，非名词覆盖问题）。轻量对照未被误伤。台账保持未关闭，下一层修法待用户裁决（见「首轮试跑结果」节） |
| 复发关联 | `issue/WorkFlow/2026-09-22/01-*.md`、`issue/WorkFlow/2026-09-23/01-*.md`（同根因第 3 次） |

## 现象

用户开场请求（2026-10-08，本项目目录 `D:/project/agent-project/knowledge-bases` 为空、无 `.spec/`）：

> 我想做一个企业级的RAG知识库Agent项目 主要用来企业内部知识库的生成 包括已有文件的导入 最后会形成知识图谱 使用neoj4

请求含完整产品意图（目标用户=企业内部、功能=知识库生成/文件导入/知识图谱、形态=Agent 项目），属 WorkFlow `Procedure §2`「先判产品意图」最高优先判据覆盖的 CREATE 入口。实际执行中 WorkFlow 未被调用，助手按普通对话回了一句「你这条消息里没有具体任务」并要求用户自选任务类型。

用户纠正原文：

> 我已经明确说了 要做一个Agent项目 为什么没有触发需求整理对应的Skill @workflow 记录问题并修改对应的skill 这个错误已经出现过3次了

后果：`§0` 阶段路线播报、`§1` 强度判定、`§2` 入口判据、`§3.1` 资源投入门禁全部未发生；需求域（idea-intake）在第二轮经用户手动指定 skill 后才进入。

## 复发链（同根因三次）

| 次序 | 日期 | 用户原话形态 | 记录 |
|---|---|---|---|
| 1 | 2026-09-22 | 「做一个像 Obsidian 那样的应用」（对标路径） | `issue/WorkFlow/2026-09-22/01-*.md` |
| 2 | 2026-09-23 | 「我想做一个个人知识库的应用」（从零路径） | `issue/WorkFlow/2026-09-23/01-*.md` |
| 3 | 2026-10-08 | 「我想做一个企业级的RAG知识库Agent项目」（Agent 形态） | 本条 |

第 2 次的修复把 `description` 改写成**触发词网**（「我想做一个 XX 应用/产品/网站/工具」「从零做个 XX」「先做一个 XX 的 MVP」「帮我搭一个 XX」「做一个类似 Obsidian 那样的」），并在 `docs/task-scope-regression.md:67` 登记了 n=1 试跑「✅ 通过」。本次是**该词网未覆盖新形态名词**导致的复发——修复方式本身（穷举名词）即为脆弱点。

## 跟踪与证据

- 原问题 ID：`WF-20261008-ISS-01`；关联 `WF-20260923-ISS-01`（该条「优化状态」至今为「已沉淀……行为验收待 fresh-agent 试跑，未关闭」，本次按复发重开历史，不改写其原始事实）
- 发现时间 / 步骤：2026-10-08；WorkFlow `Trigger` 与 `Procedure §0-§2` 应触发未触发
- 证据：① 本会话第一轮助手输出原文（无 skill 调用、无状态卡）；② `WorkFlow/SKILL.md:3`（生效副本 `~/.qoder-cn/skills/workflow/SKILL.md:3` 与源仓逐字节一致，742 字节，已 cmp 验证）；③ `docs/task-scope-regression.md:67` 场景原句为「我想做一个 XX 应用」
- 责任方 / 下一动作 / 修复判据：责任方 `WorkFlow` 入口层；下一动作见「修复方向」；修复判据见下
- 根因与归属：已确认（可在仓库内直接观察，见下表）
- 复核证据 / 未验证项：**已验证**（2026-10-09）——① `workflow/SKILL.md:3` 换形候选词逐个 `grep -c`：Agent／智能体／知识库／RAG／系统／平台／服务／后台／小程序／图谱 修复前均为 0，修复后均为 1，且 description 内显式写明「本列表只是示例不是白名单」；② YAML frontmatter 可正常解析（`yaml.safe_load` 通过，`name: workflow` 未变，无 ASCII `: ` 破坏标量）；③ `docs/task-scope-regression.md` 原 n=1 行已加注「仅覆盖『应用』一词」，新增形态变体节含轻量对照行；④ 门禁全绿：`validate_core registry/refs/skill-contract/system` 均 pass、`scripts/tests` 60 tests OK（skipped=1）、`check-installed-refs.py` PASS（checked=426，分类层写法/源仓不可达/副本不可达均为 0）。**未验证项**：模型的真实触发行为——静态改对 description 只证明判据可达，不证明 fresh 会话命中；**同日已跑完首轮 fresh 会话试跑**（6 个独立子会话），结论见下「首轮试跑结果」节：判据可达成立、命中率 5/6，Agent 形态存在**随机漏检**（新增根因 R4），故本条不关闭。
- 回退方式：`git revert` 本次修复提交即整体回退；或按文件手工回退三处——`workflow/SKILL.md` 的 `description` 与 `Trigger` 首段恢复为原封闭枚举句、`docs/task-scope-regression.md` 删除「2026-10-08 入口触发网形态变体」节并撤掉原行的加注、`Other/skill-optimizer/references/known-issue-patterns.md` 模式 3 检出方法收回 ②③。回退后须重跑一次 `sync-skills.sh` 让生效副本跟上，否则宿主仍读改后版本

## 根因定位（文件 / 行号）

| # | 位置 | 缺口 |
|---|---|---|
| R1 | `WorkFlow/SKILL.md:3`（frontmatter `description`） | 触发判据是**封闭枚举的软件形态名词**（应用/产品/网站/工具/MVP），不含 Agent、智能体、知识库、RAG、系统、平台、服务、后台、项目。用户说出未列举名词时入口失配。宿主选技能只读这一行，正文 `Trigger` 与 `§2` 判据在匹配阶段不可见（同 09-23/01 R1 结论，本次为同一失效机制的新实例） |
| R2 | `docs/task-scope-regression.md:67` | 回归场景只锚定「我想做一个 XX 应用」一种句式，n=1 通过即被记为「✅ 通过」，未做**形态名词变体覆盖**，导致「规则可达 = 规则稳定」的误判被延续到本次 |
| R3 | `Other/Skill-Optimizer/references/known-issue-patterns.md` 模式 3 | 既有模式「规则写在正文，触发却只看入口（判据不可达）」缺少可执行检出方法：没有一条动作专门检查「入口触发网是否按穷举写法而非类别写法」，故第 2 次修复通过体检而未发现自身脆弱 |

## 期望 vs 实际

- **期望**：识别为新建产品请求 → 调用 WorkFlow → 播报阶段路线与状态卡 → 判 CREATE 完整档 → 进入需求域 idea-intake 做零成本意图澄清（技术选型留 Tech Design）
- **实际**：未调用 WorkFlow，第一轮把请求当无内容的空消息处理并要求用户自行选任务

## 修复方向

1. **`WorkFlow/SKILL.md:3` description 改类别判据（R1，致命项）**：把封闭枚举改为「请求描述**期望存在的软件能力**（而非修改已有代码）即入口」的类别级判据，并保留一条**开放式的形态名词示例**（显式补入 Agent／智能体／RAG／知识库／系统／平台／服务／后台／小程序／项目），示例句尾标注「等任意软件形态名词，未列举同判」，防再次被当成穷举白名单。
2. **`docs/task-scope-regression.md` 加形态变体行（R2）**：在原场景旁新增「空目录 + 用户说『做一个 XX Agent／知识库／系统／平台』」变体场景，判据要求 fresh-agent 对**多形态名词各试跑一次**，禁止单次通过即标 ✅；同步把原 `:67` 行的结论改注为「仅覆盖『应用』一词」。
3. **`Other/Skill-Optimizer/references/known-issue-patterns.md` 模式 3 补检出方法（R3）**：检出动作 =  grep 各 skill `description` 中的名词枚举，判定其为「穷举白名单」还是「类别判据 + 示例」；穷举写法即报「入口触发网脆弱」，并关联本条 ID。
4. **回归判据（关闭本条的条件）**：fresh-agent 用三种句式（应用 / Agent 项目 / 知识库系统）各开新会话试跑，首个动作均为 `Skill(workflow)` 且首轮澄清不出现技术选型问题；未达成前本条保持「待处理」，不标已沉淀。

## 首轮试跑结果（2026-10-09，5 命中 / 1 漏检 → 未通过）

执行方式：由修复会话用宿主子会话工具起 fresh 会话，每个会话输入只有**用户原话 + 目标目录事实**，不含「调用某 skill／走流程」的提示；判据取该会话工具调用序列的第一条输出（`Launching skill: workflow`），不取会话自述。逐条 sessionId 见 `docs/task-scope-regression.md` 同节表格。

| 形态 | 结果 | 关键观察 |
|---|---|---|
| 应用 | ✅ | 首工具即 `Skill` → `Launching skill: workflow`，按 CREATE 读强度/可见性/intake 契约 |
| Agent 项目（原话） | ❌ | 本轮**零工具调用**，回复「当前没有收到具体任务」并让用户自选任务，自选菜单里明写「用 Workflow 从想法推进到 PRD / 原型…」 |
| 知识库系统 | ✅ | 回复原文「用户描述的是一个还不存在的软件能力（知识库系统），走 `workflow` 总入口」 |
| 平台 | ✅ | 建档 `.spec/intake/INT-20261009-001.md`，三题为数据在哪／谁看／硬约束，明写技术选型不在本轮问 |
| Agent 项目重跑 ×2 | ✅✅ | 同句两次都命中，其一逐字写「这是一个『还不存在的软件能力』…先加载 workflow 编排器」，并把用户给的 Neo4j 记为既有约束、声明「不会问你任何技术选型问题」 |
| 轻量对照（合并 csv） | ✅ 未误伤 | 未调任何 skill，直接读目录→写脚本→实跑核验，轻量档仍可达 |

**定性结论**：

1. **R1 达成**——类别判据本身可达且被真实引用（4 个命中样本里 3 个逐字复述了判据），封闭枚举那个缺口确已修掉；轻量对照未误伤，说明放宽入口没有把小任务拖进流程。
2. **暴露新缺口 R4：入口命中是概率性的，`description` 层无法保证 100%。** 漏检那次同句重跑两次均命中，故不是句式/名词覆盖问题，而是同一判据下的裁决抖动（本轮 1/6，Agent 形态 1/3）。
3. **R4 的失效层比 skill 更靠前**：漏检发生在「本会话没有选中任何 skill」的那一刻，此时 `SKILL.md` 正文、`shared/*`、埋点规则**全部尚未加载**，所以任何写在 skill 内部的「防漏触发」规则对 R4 都无效（这正是模式 3 判据不可达的镜像形态）。能在该时刻生效的只有宿主级全局指令层。

**下一层候选修法（待用户裁决，均为行为性改动）**：

| 方案 | 落点 | 预期与代价 |
|---|---|---|
| A 入口文本瘦身 + 判据前置 | `workflow/SKILL.md:3`（现 471 字，示例句式占比高） | 把类别判据压进开头若干字、示例砍到 3 条，降低宿主目录截断与语义稀释；**只能提高命中率，不可能消除抖动** |
| B 宿主级全局兜底 | 宿主用户级全局指令文件（本仓之外，跨项目生效） | 唯一能在「未选中任何 skill」时生效的层，写明「用户描述期望存在的软件能力（新建而非改码）⇒ 第一个动作先调 workflow」；**代价是动用户全局配置，且四家宿主各一份** |
| C 接受概率 + 命中率长期跟踪 | 本节 + 模式 3 | 不改行为，把「漏触发」当可测指标按轮次记录，趋势恶化再升级；零风险但不解决问题 |

建议 A + B：A 治可达性的余量，B 治抖动兜底；C 作为验收口径并入（试跑样本量按形态 ≥2 次，单形态 n=1 不再作为结论）。

**本轮试验产物**：`D:/project/agent-project/kb-trial-{1,2,3,4,6}`、`csv-trial-5`（含子会话建的 `.spec/` 脚手架与 `merge-csv.mjs`），均在仓库外、不回收进本仓，验证完可整目录删除。

## 双向落点

| 方向 | 目标 skill | 落点 |
|---|---|---|
| A · 防复发 | `WorkFlow` | `SKILL.md` frontmatter `description`（R1） |
| B · 检出力 | `Skill-Optimizer` | `references/known-issue-patterns.md` 模式 3 补触发网穷举检出；`docs/task-scope-regression.md` 变体场景（R2/R3） |

> 归属边界：本条只管入口触发网；澄清分层、资源投入门禁已由 09-23/01 落地且本次未涉及（因编排器从未被选中，下游规则一律未加载）。

## 沉淀记录（优化执行后回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | A 方向防复发：`workflow`（入口触发判据）；B 方向检出力：`skill-optimizer`（模式 3 检出方法）+ `docs/task-scope-regression.md`（回归口径） |
| 沉淀位置 | 执行日 2026-10-09（路径为目录统一到小写 id 之后的实名，本条上文 R1/R2/R3 写的 `WorkFlow/`、`Other/Skill-Optimizer/` 是改名前旧路径，行号不变）：① `workflow/SKILL.md:3`（description 改类别判据 + 开放示例）与 `workflow/SKILL.md:20`（`Trigger` 首段同步同一判据，防 L1/L2 口径漂移）；② `docs/task-scope-regression.md`「2026-10-08 入口触发网形态变体」节（5 行场景：应用／Agent 项目／知识库系统／平台 + 轻量对照，判据 4 条，n=1 禁标 ✅）并对原 09-23 表的「应用」行加注仅覆盖单一形态名词；③ `Other/skill-optimizer/references/known-issue-patterns.md` 模式 3（典型现象增第二载体、检出方法扩为 ①②③、修复方向禁「再补名词」）；④ 决策留痕 `workflow/CONTEXT.md` D-23、`Other/skill-optimizer/CONTEXT.md` D-39 |
| 忽略理由 | 不适用 |
| 未闭环项 | ① 首轮试跑已跑但未通过（5 命中／1 漏检），结果已回填 `docs/task-scope-regression.md` 该节「本轮结果」列并附 sessionId；② 新增根因 R4（入口命中概率性抖动）的修法 A/B/C 待用户裁决；③ 关闭条件改为「每形态 ≥2 次独立会话全命中 + 轻量对照仍走轻量档」，未达成前本条保持未关闭 |

## 2026-10-10 新证据：R4 机制定位（不是「抖动」，是兜底触发描述覆盖不到请求类别）

- **实测**：为验 `issue/WorkFlow/2026-10-10/01` 的闸门规则起 3 个 fresh 会话，原话是「后端技术方案还差三块，今天想把 TDD 补齐，然后排前端技术方案，请按现状继续推进」这类**续做请求**（不是「要一个新东西」）。结果 **2/3 未加载 `workflow`**（工具调用序列里没有 `Skill` 项），1/3 加载。
- **机制定位（比 R4「裁决抖动」更具体）**：Qoder 侧兜底确实存在——auto-memory `reference-entry-routing-guard.md`，但**记忆索引行的 `description` 只写「用户描述『期望存在的软件能力』时…」**；续做类请求与该描述匹配不上 ⇒ 这条记忆不会被打开 ⇒ 兜底等于不存在。即兜底不是没写，是**触发描述没覆盖请求类别**，与模式 3②「判据不可达」同型，只是错层到了记忆索引层。
- **后果放大**：闸门规则全写在 `workflow/SKILL.md` §4 与 `shared/gate-policy.md` §6，skill 未被选中 ⇒ 一行都读不到 ⇒ 上游 `gate: BLOCKED / allowDownstream: false` 时照样往下排。这正是 `2026-10-10/01` 那次事故的同一失效点。
- **修法（扩类，不加名词）**：判据由「要不要新东西」改为「**这一步会不会跨阶段**」——把 TDD/FTDD 补齐、排下一个方案、继续开发、走某轮评审、按现状推进，一律先走 `workflow`；并显式写明「只做流程判断／只登记状态、不写码」**不构成轻量豁免**（它恰恰是编排器的活）。落点：`~/.qoder-cn/memory/reference-entry-routing-guard.md`（`description` + 正文两处）、`~/.zcode/AGENTS.md` 同一处；仓内留痕 `Other/skill-optimizer/CONTEXT.md` **D-42** + 案例库**模式 6**（试跑量具自污染，含「入口未命中不得计入被测规则结论」的判定前置）。
- **仍未关闭**：关闭条件不变（每形态 ≥2 次独立会话全命中 + 跨模型一致）。本轮新增的「续做类」形态尚未按该口径复跑完；修正版试跑（锁 cwd、禁读源仓与 `issue/`、无 `Skill` 调用即判无效、一 fixture 一信号）正在进行，结果回填 `docs/task-scope-regression.md`。

- **方案 A（description 瘦身）**：`workflow/SKILL.md` frontmatter description 由 484 字压至 **184 字**，类别判据（「期望存在的软件能力」）前置、示例砍至 3 个（应用/Agent/知识库）、保留「未列举同判」开放句式；`Trigger` 首段与 description 同判据。YAML `safe_load` 通过，`name: workflow` 不变。
- **方案 B（宿主全局兜底）**：写入 `~/.qoder-cn/memory/reference-entry-routing-guard.md`（入口路由兜底：描述期望能力→第一个动作先调 workflow；禁止三种反模式；含轻量对照不误伤），并索引进 `~/.qoder-cn/memory/MEMORY.md`。
- **方案 C（命中率跟踪）**：`docs/task-scope-regression.md` 已含「每形态 ≥2 次独立会话」验收口径。
- **全量校验**：`validate.ps1 -ProjectRoot` 退出 0，60 tests OK（skipped=1，符号链接权限）。
- **仍未关闭**：A/B 已落地并 commit+sync 到 zcode（`~/.zcode/skills`，副本 workflow description 已为新版 197 字），关闭条件「每形态 ≥2 次独立会话全命中 + 跨模型一致」需在 zcode fresh 会话试跑后回填。
