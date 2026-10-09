# 用户说「我想做一个企业级 RAG 知识库 Agent 项目」仍未触发 WorkFlow，需求域第三次被跳过

> 归属 skill：`WorkFlow` ｜ 日期：2026-10-08 ｜ 来源：用户

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P0 |
| 标签 | `触发识别` / `流程缺陷` / `规则空转` |
| 优化状态 | 规则已修（2026-10-09，R1/R2/R3 三处落点均已改并同步生效副本）；**未关闭**——关闭条件为三形态 fresh-agent 试跑全绿，见「修复方向 · 回归判据」与 `docs/task-scope-regression.md`「2026-10-08 入口触发网形态变体」节 |
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
- 复核证据 / 未验证项：**已验证**（2026-10-09）——① `workflow/SKILL.md:3` 换形候选词逐个 `grep -c`：Agent／智能体／知识库／RAG／系统／平台／服务／后台／小程序／图谱 修复前均为 0，修复后均为 1，且 description 内显式写明「本列表只是示例不是白名单」；② YAML frontmatter 可正常解析（`yaml.safe_load` 通过，`name: workflow` 未变，无 ASCII `: ` 破坏标量）；③ `docs/task-scope-regression.md` 原 n=1 行已加注「仅覆盖『应用』一词」，新增形态变体节含轻量对照行；④ 门禁全绿：`validate_core registry/refs/skill-contract/system` 均 pass、`scripts/tests` 60 tests OK（skipped=1）、`check-installed-refs.py` PASS（checked=426，分类层写法/源仓不可达/副本不可达均为 0）。**未验证项**：模型的真实触发行为——静态改对 description 只证明判据可达，不证明 fresh 会话命中，必须按回归判据跑三形态
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
| 未闭环项 | 回归判据（三形态 fresh-agent 各起独立会话，首个动作均为 `Skill(workflow)` 且首轮不问技术选型；轻量对照仍走轻量档）**尚未试跑**，本条保持未关闭；试跑结果回填 `docs/task-scope-regression.md` 该节「本轮结果」列后再改本表 |
