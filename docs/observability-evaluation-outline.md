# 可观测体系 + 评测体系 完整大纲（WBS / 交付物 / 开发计划）

> 本文是**施工大纲**（做什么、怎么做、交付物、验收）。决策依据与实测证据在同目录
> `observability-evaluation-plan-v2.md`（该文件保留为证据记录，v1 已删除）。

## 0. 四条不变式（任何实现不得违反）

1. **平台无关**：真相来自本仓自记轨 + git；宿主日志只做富化。换 Qoder→zcode→codex 只新增适配器，指标层与评测层代码零改动。
2. **不新增流程节点**：skill 侧运行时负担 = ≤1 条 `tsr` CLI 调用，不产新文档、不填新表格。
3. **能力缺失必须显式降级**：指标声明所需 capability；适配器不提供就显示 `N/A (host lacks X)`，**禁止**用估算冒充实测。
4. **时间戳与摘要由脚本生成**：AI 只填语义字段。同时闭合两个已知问题——台账手写时间戳超前（`knowledge-bases/.spec/问题日志.md:24⑤`）、摘要假绑定。
5. **三分不可混（本体系的核心规则）**：
   - **语义**（`node/role/round/batch/state/gate/reqRefs`）→ **AI 填**，这是它唯一该填的
   - **事实**（`ts/seq/artifacts.sha256/bytes/project`）→ **脚本生成，AI 无法手写**
   - **复算**（gate 与上游是否矛盾、声明产物与磁盘是否一致、自报与宿主是否偏离）→ **独立执行体机械判红，不信任何一方**
   理由：run-log 由 AI 写，失真在设计内；只靠"翻案率"这类自述指标等于让被观测者自己盖章。
6. **适配器零宿主内部知识**：适配器不硬编码任何宿主的日志路径与字段名，改为消费该宿主提供的 **transcript spec（自描述文件）**。换宿主改宿主侧的 spec，**本仓一行代码不改**（否则"只新增一个适配器"不成立）。

---

## 1. 交付物地图（目标目录布局）

```
scripts/
  tsr.py                          A2 自记轨 CLI（唯一运行时入口）
  obs/
    schema.py                     A1 tenger.trace/v1 定义 + 校验 + 版本迁移
    capability.py                 A4 Capability 枚举与协商（缺能力 ⇒ N/A，禁止估算冒充实测）
    gitlog.py                     A3 git 轨读取
    adapters/{base,qoder,zcode,codex,registry}.py   A4 适配器（**不硬编码宿主路径/字段名**）
    adapters/contract_test.py     A4 契约测试：任意 spec 过同一套断言才算合规
    sync_spec.py                  A4b `obs-sync` 规范化映射（spec → run-log）
    snapshot.py                   A5 快照固化（防宿主驱逐/轮转）
    privacy.py                    A5 脱敏白名单
    metrics.py                    A6 指标计算
    report.py                     A6 一页看板
    anomaly.py                    A6 异常 → 候选问题卡
    selfcheck.py                  B5 量具注入反证（复用 scripts/fixtures/）
  evals/harness.py                B4 skill-up 封装 + 引擎选择 + baseline diff
  validate_core.py                B1 在既有 check_* 上加断言（不新增子命令）
<skill>/evals/                    B2 每 skill 一套：eval.yaml / cases/ / fixtures/ / baseline/
observability/                    跨项目聚合数据湖：<project>/<YYYY-MM>.jsonl + 指标快照
.spec/obs/run.jsonl               项目内自记轨（业务项目落这里）
.spec/观测/看板.md                项目内看板
evolution/进化台账.md             C1 新模板（before/after 强制）
governance/obs-registry.yaml      节点↔产物路径↔skill 映射表（节点归属判据的数据源）
```

---

## 2. 数据模型

### 2.1 `tenger.trace/v1` 事件（append-only jsonl）

| 字段 | 类型 | 必填 | **谁填** | 说明 |
|---|---|---|---|---|
| `schema` | str | ✅ | 脚本常量 | `tenger.trace/v1`，缺此字段 ⇒ 整行进 reject 文件 |
| `event` | enum | ✅ | 脚本 | `node-start/node-end/round/artifact/decision/sink/hostlink` |
| `ts` | ISO8601+tz | ✅ | **脚本取机器时钟** | 禁止手填 |
| `seq` | int | ✅ | **脚本自增** | 幂等 + 乱序判定（宿主事件会乱序，见 §2.3） |
| `project` | str | ✅ | 由 `--project-root` 算 | 不用 cwd（子会话 cwd 不受约束，已知坑） |
| `executionId` | str | ✅ | tsr init | **关联主键**，跨会话接续追踪 |
| `node` / `skill` | str | ✅ | AI | node=阶段，skill=执行体；取值受 `governance/skill-registry.yaml` 约束 |
| `role` | enum | ✅ | AI | `produce/fix/review/recheck` |
| `round` / `batch` | int | 评审必填 | AI | **返工率的分母**（上一轮我手数清单时漏过它） |
| `state` | str | 正式流程 | AI | 取值受 `governance/state-registry.yaml` 约束 |
| `gate` | enum | ✅ node-end | AI | `PASS/CONDITIONAL/BLOCKED` |
| `allowDownstream` | bool | ✅ | AI | 与 `gate` 的一致性由**复算**判红，不由自报 |
| `artifacts[]` | {path,sha256,bytes} | ✅ | **脚本算** | 产物指纹，AI 无法伪造摘要 |
| `upstream[]` | {artifact,gate,sha256} | 正式交接 | 脚本读台账 + 算摘要 | 把「闸门核对」从散文变成可判红的数据 |
| `reqRefs[]` | str[] | 建议 | AI | REQ/AC 引用 |
| `sunkOf[]` | str[] | 作废登记 | 脚本按 lineage 算 | 沉没口径见 A2 |
| `origin` | enum | ✅ | **脚本** | `self/adapter/recomputed` ⇒ **冲突仲裁用**（§2.3-①） |
| `actor` | enum | ✅ | **脚本** | `main/subagent/cron/eval-judge` ⇒ **多智能体轨迹隔离用**（§2.3-③） |
| `parentExecution` | str | 子 agent 必填 | 脚本从派发上下文取 | 把子 agent 的轨迹挂回主链，不计入主链耗时分母 |
| `host` | {name,model,sessionId,spanId,traceId} | 可空 | **适配器** | `spanId/traceId` 可选，供跨进程串联；不填不影响核心链路 |

### 2.2 Capability 枚举与三家现状

| Cap | qoder | zcode | codex |
|---|---|---|---|
| `WALL_CLOCK` | ✅ 实测（ts 单调，与机器时钟差 12s） | ✅（`timestamp`） | 待测 |
| `TOOL_EVENTS` | ✅（Bash 10,249 / Edit 4,490 / Read 3,041，共 22,979） | 待测 | 待测 |
| `TOOL_ERRORS` | ✅（`loop.iteration.finished.error_tool_result_count`；⚠️ 426/11,827 条缺该字段，需 guard） | ❌ | 待测 |
| `ARTIFACT_WRITES` | ✅（Write/Edit file_path，KB 命中 2,686/3,289） | 待测 | 待测 |
| `SESSION_ID` | ⚠️ segments 无该键，靠目录名；transcript 覆盖仅 76/566 | 有 `traceId/spanId` | 待测 |
| `MODEL_ID` | ✅ | ✅ | 待测 |
| `LOOP_COUNTS` | ✅ | ❌ | 待测 |
| `TOKENS` | ❌ **实测两源皆 0** | ❌ | 待测 |

→ 三家格式互不相同（qoder `ts/type/data/turn_id` vs zcode `timestamp/event/module/traceId`），且 zcode 有 `eventEvicted=337745` 的驱逐行为 ⇒ 适配器 + 快照不是过度设计，是必需。

### 2.3 三条必须冻结的仲裁与隔离规则（否则协议不成立）

**① 覆盖仲裁（同一事实两个来源冲突时谁为真）**

| 字段类 | 以谁为准 | 理由 |
|---|---|---|
| `ts` / 耗时 / 计数（工具数、错误数、loop） | **适配器** | 机器实测，不可收买 |
| `gate` / `state` / `round` / `reqRefs` / 关联关系 | **自记轨** | 语义只有执行方知道 |
| 产物存在性与摘要 | **复算**（磁盘） | 两边都不信 |
| `executionId` 归属 | **自记轨** | 适配器无权定义业务边界 |

冲突本身要产出指标：`origin` 不一致 ⇒ 记「自报与实测偏离度」，这是量化"AI 自述可信度"的唯一途径，也是后续决定哪些字段可以不再自报的依据。

**② 关联键（宿主不会主动给你它的 session id）**
- 主键永远是本仓 `executionId`；宿主标识只作外键 `host.sessionId/spanId/traceId`（可空）。
- 适配器发现关联的**唯一允许途径**：`obs-sync` 按「时间窗 + 产物写入路径 + node-id」反查匹配，其中 node-id 必须由宿主侧可观测（写进产物文件名、envelope 或环境变量之一）。
- ⛔ 禁止读宿主的私有/未公开路径与内部字段；宿主不提供稳定标识时，判为 `capability` 缺失，指标显示 `N/A`，**不允许靠猜把两件事关联成一件事**。
- 必须容忍多对一：一次 `executionId` 可跨多个宿主会话（换会话续做是常态）。

**③ 多智能体轨迹隔离（上下文超限的解法，也是观测被污染的风险）**
- 子 agent 的轨迹**必须**带 `actor=subagent` + `parentExecution`，否则主链耗时/轮次/错误率会被工具型 agent 的噪声灌满。
- 指标默认口径只算 `actor=main`；子 agent 单独一套指标（它的价值是"隔离了上下文"，代价是"重复加载了 skill 正文"，要分开量）。
- 交接走**文件即消息总线**：子 agent 把全文落盘 + 只回传「产物路径 + 结构化摘要 + gate」，主会话按指针读片段。**禁止**指望子 agent 的返回值承载全文——实测会被截断。

---

## 3. 组件大纲（共 **14** 个：A 6 + B 6 + C 2）

**人日台账（与 §4 阶段表逐项对账，两处必须相等）**
- A：A1 1 + A2 3 + A3 0.5 + A4 2.5 + A5 1 + A6 2.5 = **10.5**
- B：B1 3.5 + B2 1 + B3 1 + B4 3.5~5 + B5 1.5 + B6 1.5 = **12 ~ 13.5**
- C：C1 1.5 + C2 1 = **2.5**
- **合计 25 ~ 26.5 人日**（§4 阶段表相加必须等于此区间）

### A 可观测体系（6 个组件：A1–A6）

**A1｜事件契约与校验器** `scripts/obs/schema.py` · 1 人日
- 做什么：定义 v1 字段、枚举、必填、版本迁移钩子；`verify` 校验「gate 与 allowDownstream 一致」「state 是注册合法值」「产物路径存在且 sha256 与磁盘一致」。
- 怎么做：纯 dataclass + jsonschema-lite 自校验；枚举直接读 `governance/state-registry.yaml`，不另立词表。
- 验收：喂 3 份非法事件（缺 sha / state 非法 / gate=PASS 但 allowDownstream=false）必须 3 红。

**A2｜`tsr` CLI 采集器（唯一运行时入口）** `scripts/tsr.py` · 3 人日
- 子命令：`init` / `node-start` / `node-end` / `artifact` / `link` / `sink` / `host` / `verify` / `report` / `anomaly`
- 关键实现点：
  - `node-end` 自动取机器时钟 + 对声明路径算 sha256/bytes（调用方**无法**手写时间与摘要）
  - `sink --dec DEC-x` 先做 **lineage 传递闭包**（沿 `upstream[]`/`sourceRefs` 反查）再算沉没，输出**区间 + 口径声明**；禁止用日期窗或目录前缀（v1 的 55% 就是这么错的）
  - 全程 append-only；写失败必须非零退出并明确报「未落盘」
- 验收：同 skill 连续两次运行产物可 diff；篡改任一产物正文后 `verify` 必红。

**A3｜git 轨读取（第二真相源）** `scripts/obs/gitlog.py` · 0.5 人日
- 做什么：从提交粒度取耗时/改动范围/回滚点；与 tsr 事件按 ts 窗口对齐，交叉校验自报字段。
- 怎么做：`git log --numstat` 按 node 时间窗聚合；提交信息里的 node/executionId 作 join 键（需在工作流提交规范里加一个 trailer）。
- 验收：tsr 缺失时（未接入的老项目）仅凭 git 仍能出节点耗时区间；两者冲突时看板标「不自洽」。

**A4｜宿主适配器框架 + 三家适配器** `scripts/obs/adapters/*` · 2.5 人日
- 做什么：`discover() / spans() / capabilities`；qoder 先做（数据已探明），zcode 次之，codex 占位。
- 关键实现点：
  - **节点归属主判据 = Write/Edit 的 `file_path` → `governance/obs-registry.yaml` 的节点映射**；`tool_name:"Skill"` 事件（实测仅 114 条）只作旁证，不作主键。
  - qoder 日志必须按 session 目录分组去重（同一 `...p40936.jsonl` 文件名会散现在 20 个目录）。
  - 适配器异常/目录不存在 ⇒ 返回空 span + `capability=[]`，主流程照跑（降级不阻塞）。
- 验收：拔掉全部适配器，指标层只少几列且不报错；接上 qoder 适配器后工具数/错误率/loop 数三列出现真实值。

**A5｜快照固化 + 脱敏** `snapshot.py` / `privacy.py` · 1 人日
- 做什么：每次采集把与本项目相关的 span 落到 `observability/<project>/<YYYY-MM>.jsonl`，宿主日志被驱逐后仓内仍有快照。
- 脱敏纪律：只留 `tool_name` + 路径哈希 + 字节数；命令正文/文件正文默认丢弃，白名单 skill 才留 `args` 摘要；密钥与个人数据模式化拦截。
- 验收：对 `observability/` 跑密钥与 PII 扫描 0 命中；模拟删除宿主日志目录后历史指标不变。

**A6｜指标层 + 看板 + 异常开卡 + 节点映射注册表** `metrics.py` / `report.py` / `anomaly.py` / `governance/obs-registry.yaml` · 2.5 人日
- 指标字典（每项标注真相源与所需 capability）：

| 组 | 指标 | 口径 | 源 / Cap |
|---|---|---|---|
| 效率 | 节点墙钟耗时 | node-start→node-end | tsr / WALL_CLOCK |
| 效率 | 评审轮次·批次 | 按 node 聚合 round/batch | tsr |
| 效率 | loop 迭代数 | `loop.iteration.finished` 计数（缺字段 guard） | qoder / LOOP_COUNTS |
| 效率 | 工具调用分布 | tool_name 分组 | qoder / TOOL_EVENTS |
| 质量 | 工具错误率 | `Σerror_tool_result_count / Σtool_result_count` | qoder / TOOL_ERRORS |
| 质量 | Gate 分布 | PASS/CONDITIONAL/BLOCKED 占比 | tsr |
| 质量 | **摘要不一致数** | 声明 sha ≠ 磁盘 sha | A1 verify（平台无关） |
| 质量 | 沉没投入 | lineage 闭包 ∩ 切点，**区间+口径** | tsr sink |
| 质量 | BLOCKED 成因四分类 | 上游未批/证据缺失/契约非法/授权缺失 | tsr + 问题卡 |
| 质量 | 台账非法条数 | `validate_core gate/artifact` 报错数 | B1 |
| 成本 | 上下文压力**代理** | 读入字节 + 产物字节（标注「代理，非实测」） | tsr + 适配器 |
| 成本 | **重复加载系数** | 同一 skill 正文/shared 契约被重复读入的字节 ÷ 节点数 → **决定是否上多智能体隔离的量化依据** | 适配器 / TOOL_EVENTS |
| 智能 | 同型问题复发率 | 同 `issue/` 指纹滚动 30 天再犯数 | issue + tsr |
| 智能 | 反哺有效率 | 落规则前后同场景错误率差 | tsr + issue |
| 智能 | **规则命中率** | SKILL.md/shared 条款被真实读取引用比例 | 适配器 / TOOL_EVENTS |

- 看板：一页 md（`.spec/观测/看板.md`），依赖缺失项显式 `N/A (原因)`。**不做 HTML**（v1 过度工程已砍）。
- 异常→候选问题卡：阈值触发即开卡，卡内带 `executionId` + ts 窗口 + 产物路径与 sha 指针（证据可回放，不靠 AI 回忆），落 `.spec/问题日志.md` 索引 + 详情文件。
- 验收：用 KB 项目 10-09→10-15 数据回放，看板必须**自动**列出「10-10 DEC-V2 作废 → 沉没区间 + 口径」，而不是任何人手写进去。

### B 评测体系（5 个组件）

**B1｜A 类结构合规断言（先做，最高性价比）** `validate_core.py` 内扩 · 3.5 人日
- 做什么：**不新增子命令**（实测 `main()` 是 `check_*` 函数注册表，L662-665），在既有命令里加断言：
  - `gate` ← 把 `task_preflight.py:145-170` 的 sha256 `subjectDigests`/`contentDigest` 核对逻辑搬进来（当前 `validate_core.py` 里 `digest` 出现 **0 次**）。直接闭合已两次实测的「改 11 个 PRD 正文后 gate/artifact 仍双绿」与 `BLK-GATE-ORDER-01`「闸门有字段无执法者」。
  - `artifact` ← 必需章节齐全率（清单落 `governance/artifact-registry.yaml`：TDD overview 6 章、PRD 模块 9 章等）
  - `refs` ← **先解业务项目无 `governance/` 时不可用**（回退读仓根注册表），否则 A 类在真实项目上是哑的
  - `trace` ← 引用可解析 + 术语**全变体**扫描（`问题日志.md:21` 已沉淀：拆/并 AC 后必须全引点重对齐）
- 验收：注入反证 4 条全红（见 B5）。

**B2｜`evals/` 目录规范与用例分层** · 1 人日
- 结构：`<skill>/evals/{eval.yaml, cases/*.yaml, fixtures/{repos,diffs,scripts}, baseline/result.json}`（对齐 skill-up，不自建格式）
- 分层：L0 每 skill 1 条 smoke（最小输入→必需产物存在且 Gate 合法）· L1 每 skill 3–5 条核心分支 · L2 `issue/` 每个 P0/P1 闭环**强制**回流 1 条 · L3 改 `shared/` 或合并 skill 前全量
- 验收：KB 项目的 `评测集/` 现有 180 份 md 属产品 RAG 语料，**与 skill 评测无关**，不复用不混淆。

**B3｜judge 策略路由与 rubric 规范** · 1 人日
- 纪律：硬约束→`rule_based`（必含章节/必引用某文件/禁用术语）；结构→`script`（调 B1 校验器返回 0/1）；**只有语义判断**（方案是否闭环、还原度、澄清是否问到该问的）→`agent_judge`，且必须附 rubric + 反证样例。
- 理由：agent 评 agent 产物会自我强化错误，`script`/`rule_based` 才是不可收买的守门员。
- 验收：任一 skill 的 case 中 `agent_judge` 占比 ≤30%，超出需说明。

**B4｜引擎适配 + Windows 可行性 + baseline 门禁** `evals/harness.py` · 3.5–5 人日
- 现实：skill-up 的 `qodercli` 引擎**本机不存在**（不在 `~/.qoder-cn/bin`，npm 404）；已装可用为 `claude 2.1.296`、`codex-cli 0.162.1`。官方 install.sh 支持 MINGW/MSYS（CLI 本体可在 Windows 跑），但 Windows full agent evals 文档指向 WSL2，GitHub Action 是 Linux-only；本机 `go` 未安装。
- 怎么做：harness 先做一次**Windows 原生跑通实验**（不通则退到 `script` judge + B1，B 类行为评测延后）；引擎写成配置项而非代码分支 ⇒ 换宿主只改 `eval.yaml`；锁 skill-up tag（官方 Warning 字段/命令会变）。
- 门禁分级：B1 红=阻断提交；L0 红=阻断；L1/L2 红=进 `issue/` 不阻断；L3 红=阻断合并。
- 回归纪律：评测必须由**干净会话**跑，禁止同一会话自改自评。
- 验收：同一套 case 在 `claude_code` 与 `codex` 两引擎各跑一次并出 baseline diff 报告。

**B5｜量具自验（先验再信）** `selfcheck.py` · 1.5 人日
- 注入反证清单（用 `scripts/fixtures/` 做临时副本，跑完即删，防自污染）：
  1. 删必需章节 → B1 `artifact` 红
  2. Gate 字段写非法值 → B1 `gate` 红
  3. 让 skill 跳过某步骤 → B 类对应 case 失败
  4. 改产物正文不动台账 → B1 红（当前不红，靠 B1-① 修好；此条已在 KB 项目实测过，不重做只做回归）
  5. 同一产物连跑两次，ts/sha256 必须一致且等于机器时钟
- 验收：5 条全命中才允许当门禁；产出「检出力报告」写清哪些仍检不出。

**B6｜打分标准与总分模型（用户诉求：一眼看出进步还是退步）** · 1.5 人日
- **两级制，不是单一总分**：红线项**一票否决**（不参与加权、不能被高分抵消）→ 命中即记 `0/BLOCKED`；其余维度加权成 0–100 总分用于看趋势。
- 维度与权重（每条判据必须写成可机械核对或带 rubric）：

| 维度 | 权 | 评法 | 证据来源 |
|---|---|---|---|
| D1 契约合规 | 25 | 脚本 | 产物齐全/schema 合法/**digest 与磁盘一致**/state 走合法边 |
| D2 需求承接 | 20 | 脚本 | traceability 覆盖率：REQ/AC 被承接且未断链的比例 |
| D3 **检出力** | 15 | 脚本 | 在 fixtures 里预埋已知缺陷，被本 skill 抓到的比例 |
| D4 一次通过/返工 | 15 | 脚本 | run-log 的 round/batch、`error_tool_result_count`、重跑次数 |
| D5 语义质量 | 20 | agent_judge | 方案是否闭环、还原度、澄清是否问到该问的（**必须附 rubric**） |
| D6 成本体积 | 5 | 脚本 | 上下文代理字节、产物字节、墙钟耗时（越大越低，标注为代理） |
| ⛔ 红线 | — | 脚本 | gate=PASS 但上游 BLOCKED｜必需章节缺失｜**台账绿而正文被改**｜越权写盘｜伪造验证证据｜judge 占比>30% 或无 rubric |

- **可比性锚定（总分的前提，缺则分数无意义）**：每个分数必须绑定 `{skill 版本 commit, cases 集合版本, engine, model, judge 版本}`；任一变更 ⇒ 开新基线，**禁止跨锚比较**。
- **防 Goodhart（分数最高 ≠ 最好）**：留 10–20% **holdout 用例**不参与优化、只在验收跑；定期换题。总分不降而 holdout 降 ⇒ 判过拟合并报警。
- **体系级不取平均**：取「各 skill 总分中位数 + 红线命中数」，避免一个满分掩盖九个崩盘。
- 报告形态：单 skill = 总分 + 6 维雷达 + 相对基线的**逐维 delta**（只看总分会掩盖"一维崩一维涨"的结构性退步）。
- **调权即换锚**：权重变更（本轮按推荐定 25/20/15/15/20/5，后续依真实评测再调）⇒ 视为基线作废，**历史总分不得与新权重下的分数直接比较**；权重每次变更写进 `governance/obs-capability.yaml` 的 `scoringVersions` 段，分数绑定 `scoringVersion`。
- 验收：同一 skill 改动前后各跑一次，能输出「总分 + 各维 delta + 红线命中」三样；故意做一处"一维崩一维涨"的改动，必须被逐维 delta 暴露出来。

### C 闭环与治理（2 个组件）

**C1｜进化台账 + bad case 回流** · 1.5 人日
- `evolution/进化台账.md` 新模板（当前 3 行 0 条目）：`来源问题ID → 改动 commit → 评测 baseline diff(before/after) → 指标变化 → 结论 → 回滚指针`。**无 before/after 一律标「未验证」，禁止写「已优化」**。
- 回流钩子：`issue/` 条目标「已闭环」时机械检查是否已有对应 L2 case，没有则拒绝闭环。
- `skill-optimizer` / `skill-evolver` 诊断入口从「读摘要」改为「按 obs 指针读轨迹原文」。
- 验收：台账出现一次真实的「未验证」判定即闭环成立。

**C2｜无人值守边界** · 1 人日
- 定时任务**只允许**跑纯脚本（ETL 采集 + A 类校验 + 快照）；⛔ **禁止跑 `agent_judge`** —— 无人值守产生的 agent 轨迹会污染被观测的语料，且要 Full Access。
- 复用 `oss-radar` 已有的定时巡逻形态，不新建调度体系。
- 验收：定时任务产物中 0 条 agent 轨迹（判据：`actor ∈ {cron, eval-judge}` 的事件里不得出现 judge 调用）。

## 4. 开发计划

### 阶段与出口判据

| 阶段 | 内容 | 出口判据（不达标不晋级） | 人日 |
|---|---|---|---|
| **P0 执法先行** | B1-①（digest 搬进 `check_gate` + `check_artifact`）+ B5-④（改正文必须红） | 「改正文台账仍双绿」变必红；KB 现存量重跑不炸 | **2.5 ✅已完成** |
| **P1 真相轨落地** | A1 + A2 + A3 + A5 | 同 skill 两次运行可 diff；ts/sha 由脚本生成；子 agent 轨迹可被 `actor` 排除；模拟删宿主日志后指标不变 | **5.5** |
| **P2 指标可见** | A6（含 obs-registry 节点映射）+ A4（qoder 适配器） | KB 项目回放自动得出沉没区间+口径；拔适配器只降级不报错 | **5** |
| **P3 评测完备** | B1 余下 ③项 + B2 + B3 + B5 全量 + **B6 打分模型** | 注入反证 5 条全中并出「检出力报告」；能输出总分+逐维 delta+红线；A 类可当 pre-commit | **6** |
| **P4 行为评测上引擎** | B4（Windows 可行性 + 双引擎 baseline diff） | 两引擎各跑通一次并出 diff；**在 worktree 内跑完，主工作区 `git status` 零变化**（这是 B4 的验收条件，不另立子系统） | **3.5–5** |
| **P5 闭环接线** | C1 + C2 | 台账有 before/after；回流钩子能拒绝闭环；定时任务 0 条 agent 轨迹 | **2.5** |
| P6 扩面 | 其余 skill 的 L0/L1 用例 | ≥50% 的 L2 case 来自 `issue/` 闭环 | 持续 |

**合计 25–26.5 人日**（P0 2.5 + P1 5.5 + P2 5 + P3 6 + P4 3.5–5 + P5 2.5），与 §3 台账区间一致。
> 记账纪律：人日以 §3 组件数为准，本表只做拆分，两处必须能对上；改任一处必须同轮重算另一处。

### 依赖与并行
- P0 ⊥ P1：P0 只动 `validate_core.py`，P1 只动新文件，可并行。
- A6 依赖 A2 + obs-registry；A4 依赖 A1/A2 完成；B4 依赖 B2/B3。
- **关键路径**：P0 → P1 → P2（这三段做完即「每一步有数据可依」，可开始据此做 skill 精简）。
- 每阶段独立提交、独立可回滚；P0 完成即产生价值，不依赖后续阶段才生效。

### 立即开工的最小集
若想用最小成本先看到数据：**P0（2.5）+ A2 骨架（1）= 3.5 人日**，即可拿到「产物指纹可信 + 节点边界有记录」，其余按阶段推。

---

## 5. 明确不做
- ❌ 不部署 Langfuse/Phoenix/Opik/MLflow：抽象层级不对齐（其 trace=请求，我们节点=跨天阶段）、需 ClickHouse/PG/Redis 自托管、token 拿不到使成本看板价值归零。只借鉴 OTel 的 span 分层与 attribute 命名纪律。
- ❌ 不自建评测格式，对齐 skill-up `eval.yaml`/`cases`。
- ❌ 不做 HTML 交互看板、不做 cron 周报。
- ❌ 不在本阶段做 skill 精简——等 A6 的「规则命中率」有数据后再动。
- ❌ **不在本计划内建"多智能体编排/沙箱"子系统**：那是执行侧架构（属流程精简阶段）。本期只保留两件必要小事：① 契约里的 `actor/parentExecution` 字段（否则子 agent 轨迹会把主链指标污染成不可复原的噪声）；② B 类评测在 worktree 内跑并列进 B4 验收。**是否真得上多智能体隔离，由 A6 新增的「重复加载系数」指标决定，不靠直觉先建。**
- ❌ 不把「翻案率」当守门指标（记账方仍是自述方＝自证），改用 B1-① 的机械复算兜失真。

## 6. 风险登记
1. skill-up 早期不稳定（官方 Warning）→ 锁 tag；评测配置独立目录便于迁移；**A 类不依赖它**。
2. Windows full agent evals 官方指 WSL2 且本机无 Go → P4 第一步就是可行性实验，不通则 B 类降级延后。
3. tsr 的 `gate/round/batch` 仍由执行方填 → 靠 B1-① 机械复算 + A3 git 交叉校验 + 「摘要不一致数」指标盯；不承诺消除自报失真。
4. 宿主日志会被驱逐/轮转（zcode 实测 `eventEvicted=337745`）→ 快照进仓是 P1 硬交付，不是风险注脚。
5. 隐私：适配器 `args` 含命令与路径 → 默认只留 tool_name + 路径哈希 + 字节数。
6. qoder transcript 源覆盖仅 76/566 session → 不得把它当关联主键，关联一律以 tsr 的 `executionId` 为准。
