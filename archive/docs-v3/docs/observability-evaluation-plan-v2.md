# 可观测体系 + 评测体系 执行计划 v2（专家评审后定稿）

> v1 已被敌意评审推翻两处承重前提，并按「不依赖宿主编辑器」这一新硬约束重做架构。
> 评审与复核证据见 §1。

## 0. 目标与两条硬约束

**目标**：体系具备「客观数据 → 问题定位 → 改动 → 评测验证 → 沉淀/回滚」的正向循环；后续每一步（含 skill 精简）都有数据可依。

**硬约束 A｜平台无关**：观测与评测的核心**不得绑定 Qoder**。换 zcode / codex 时只新增一个适配器，指标层与评测层代码不动。
**硬约束 B｜不新增流程节点**：观测层不得要求 skill 产出新文档。运行时负担 ≤1 条 CLI 调用。

---

## 1. 复核后确认的事实（推翻 v1 的部分已标注）

### 1.1 Qoder 宿主日志（`~/.qoder-cn/logs/sessions/<proj>/<uuid>/segments/*.jsonl`）

| 项 | v1 说法 | 实测 | 结论 |
|---|---|---|---|
| `tool_name:"Skill"` 调用数 | 342 | **114** | ❌ v1 错，grep 命中数不是事件数 |
| 第一主信号 | Read 36,328 | **Bash 10,249 / Edit 4,490 / Read 3,041**（`tool.requested` 共 22,979） | ❌ 主信号认反 |
| 事件顶层键 | — | `ts,seq,level,type,data,turn_id,tool_call_id,loop_id,request_id` → **无 session_id** | ⚠️ 需靠目录名 join |
| session 覆盖 | — | segments 侧 **566** 个 session 目录；`projects/*.jsonl` transcript 仅 **78**，可 join **76** | ⚠️ 富化源覆盖 13% |
| token | 全为 0 | transcript 侧 `"input_tokens"` 等出现 **0 次** | ❌ 两个源都没有，成本类只能代理 |
| 节点归属 | 靠 Skill 事件 | **Write/Edit 的 file_path → `.spec/` 子目录** 映射：KB 项目 3,289 次写盘中 **2,686 次命中**（设计稿 876 / TDD 353 / 原型 324 / prd 260 / 设计评审 129 / 技术方案评审 84） | ✅ 改用它作主判据 |
| 时钟 | 怀疑脏 | 宿主 ts 单调、最大 ts 与机器时钟相差 12 秒 | ✅ 宿主 ts 可信；**台账手写 ts 不可信**（`knowledge-bases/.spec/问题日志.md:24⑤` 记「本机 12:39，台账写 13:0x 超前 30 分钟」） |

### 1.2 zcode 宿主日志（`~/.zcode/cli/log/zcode-YYYY-MM-DD.jsonl`）

字段风格完全不同：`timestamp`(ISO Z) / `level` / `event` / `module` / `message` / **`traceId` / `spanId`** / `context{...}`，且 context 里带 `counters.eventEvicted=337745`（**存在事件驱逐/保留上限**）。

→ **这直接证明「读宿主日志」不能当主心骨**：格式两家不一样，且日志会被驱逐。适配器只能是富化层，不能是真相源。

### 1.3 引擎可用性（评测执行侧）

- 已装可用：`claude --version` = 2.1.296、`codex-cli` = 0.162.1
- **qodercli 不存在**：不在 `~/.qoder-cn/bin`、npm registry 404 → skill-up 的 `qodercli` 引擎本机跑不了
- skill-up 官方 install.sh 检 MINGW/MSYS/CYGWIN（CLI 本体 Windows 可跑），但文档对 Windows 的 full agent evals 指向 WSL2；GitHub Action 明写 Linux only
- 本机 `go` 未安装

### 1.4 仓内已有算力（避免重复造）

- `scripts/validate_core.py` 已有 `gate / artifact / refs / trace / registry / transition / graph / system` 等子命令 → **v1 新增 4 个子命令是重复建设**
- `validate_core.py` 里 `digest` 出现 **0 次**；而 `scripts/task_preflight.py:145-170` 已用 sha256 机械核对 `subjectDigests` / `contentDigest`
- `knowledge-bases/.spec/问题日志.md:24④ / 31①` 已两次实测「改 11 个 PRD 正文后 gate/artifact 仍双绿」→ **摘要核对缺失已被独立证实两次**
- `validate_core.py` 的 `refs` 依赖项目根存在 `governance/` → **业务项目跑不了**（Workflow SKILL.md:67 已记此坑）

---

## 2. 架构：真相来自本仓自记轨，宿主日志只做富化

```
                 ┌──────────────────────────────────────────┐
真相源(平台无关)  │ L1 自记轨  tsr CLI → .spec/obs/run.jsonl   │  ← 唯一契约，换宿主不变
                 │    · 脚本自己取机器时钟（禁止 AI 手写 ts）   │
                 │    · 脚本自己算产物 sha256                 │
                 │    · 节点边界 + gate + round + REQ 引用     │
                 ├──────────────────────────────────────────┤
                 │ L1b git 轨  每节点一提交（已有习惯）        │  ← 第二真相源，天然平台无关
                 └───────────────┬──────────────────────────┘
                                 │ join by (project, ts 窗口, 产物路径)
                 ┌───────────────┴──────────────────────────┐
富化层(可插拔)    │ L2 adapters: qoder / zcode / codex / none │  ← 缺适配器 ⇒ 降级，不阻塞
                 │    声明 capability，不提供就说"拿不到"      │
                 └───────────────┬──────────────────────────┘
                                 ↓
                 ┌──────────────────────────────────────────┐
派生层(平台无关)  │ L3 metrics → 指标（每个指标声明所需 capability）│
                 │ L4 一页 md 看板 + 异常自动开卡               │
                 └──────────────────────────────────────────┘
```

**为什么反过来**：v1/评审的方案是「观测 = 离线 ETL 读宿主日志」。但那会把体系钉死在 Qoder 上，且宿主日志会被轮转/驱逐、字段格式各家不同、关联键残缺（13% 覆盖）。所以**真相必须是本仓自己写一份最小 jsonl + git**，宿主日志能补多少算多少。

### 2.1 事件契约 `tenger.trace/v1`（一行一事件，append-only）

```json
{"schema":"tenger.trace/v1","ts":"<脚本取机器时钟>","project":"...","executionId":"...",
 "node":"ui-ux-review","skill":"ui-ux-review","role":"produce|review|fix|recheck",
 "round":2,"batch":3,"state":"UI_REVIEW_IN_PROGRESS",
 "gate":"PASS|CONDITIONAL|BLOCKED","allowDownstream":false,
 "artifacts":[{"path":".spec/设计评审/批次3-第2轮-复核报告.md","sha256":"...","bytes":18342}],
 "upstream":[{"artifact":"PRD-M09","gate":"BLOCKED","sha256":"..."}],
 "reqRefs":["REQ-...","AC-..."],"sessionHint":"<宿主 session 标识，可空>",
 "sunkOf":["DEC-V2"]}
```

写入方式：`python scripts/tsr.py node-start|node-end|gate|sink --project-root <p> ...`
- ts 与 sha256 **由脚本生成**，AI 只传语义字段 → 同时修掉「台账手写时间戳超前」和「摘要假绑定」两类已知问题
- 语义字段仍可能自报失真 → 用 §4 的机械复算兜，不靠自觉

### 2.2 适配器接口与 capability 声明

```python
class HostAdapter:                      # 每家宿主一个文件，核心层零改动
    name = "qoder"
    def discover(project_root) -> list[SessionRef]
    def spans(ref) -> list[RawSpan]
    capabilities: set[Cap]              # 见下表
```

| Capability | 含义 | qoder | zcode | codex | none |
|---|---|---|---|---|---|
| `WALL_CLOCK` | 毫秒级墙钟 | ✅ | ✅ | 待测 | 由 tsr 自给 |
| `TOOL_EVENTS` | 工具调用名+参数 | ✅ | 待测 | 待测 | ❌ |
| `TOOL_ERRORS` | 错误结果计数 | ✅ | ❌ | 待测 | ❌ |
| `ARTIFACT_WRITES` | 写盘路径 | ✅ | ❌ | 待测 | 由 tsr 自给 |
| `TOKENS` | token 用量 | ❌ | ❌ | ❌ | ❌ |
| `MODEL_ID` | 模型标识 | ✅ | ✅ | 待测 | ❌ |

**降级纪律**：指标若依赖某 capability 而当前适配器不提供 → 看板显示 `N/A (qoder 不吐 token)`，**禁止**用估算值冒充实测。这条是防自欺的硬规则。

---

## 3. 观测什么（每项标注所需 capability 与真相源）

**效率**：节点墙钟耗时（tsr/git）· 评审轮次与批次（tsr）· loop 迭代数（qoder 富化）· 工具调用分布（富化）· 工具错误率（富化）· 上下文压力代理=读写文件字节和（tsr + 富化，**明确标"代理"**）· 跨会话接续次数（tsr executionId）· 等待用户决策时长（tsr 边界）

**质量**：Gate 分布（tsr）· P0/P1 检出与残留（评审清单解析）· **摘要不一致数**（机械复算，§4）· 沉没产物数（按 lineage 算，§4.3）· BLOCKED 成因四分类 · 台账非法条数（validate_core）· traceability 覆盖率

**智能化（证明"越用越聪明"的可验证判据）**
- 同型问题复发率：`issue/` 指纹在滚动 30 天内的再犯次数 → 应随反哺下降
- 反哺有效率：问题闭环 → SKILL.md 落规则 → 之后同场景错误率变化
- 规则命中率：SKILL.md/shared 条款被真实读取引用比例 → **给后续 skill 精简提供数据，不靠拍脑袋删**
- 台账规则：每条进化必须挂 before/after，无指标一律标「未验证」，禁止写「已优化」（改 `evolution/进化台账.md` 模板）

---

## 4. 评测体系

### 4.1 A 类｜确定性合规（零 token、秒级、可当 pre-commit）

**不新增子命令**，给 `validate_core.py` 既有命令加断言：
1. `gate` ← **把 `task_preflight.py:145-170` 的 sha256 核对逻辑搬进来**（`subjectDigests`/`contentDigest`）。直接闭合已知两次的「改正文台账仍双绿」和 `BLK-GATE-ORDER-01`「闸门有字段无执法者」。**平台无关，最高性价比。**
2. `artifact` ← 必需章节齐全率（TDD overview 6 章、PRD 模块 9 章等，清单进 `governance/artifact-registry.yaml`）
3. `refs` ← **先解业务项目无 `governance/` 时不可用的问题**（回退到仓根 registry 只读），否则 A 类在真实项目上是哑的
4. 引用可解析 + 术语全变体扫描（`问题日志.md:21` 已沉淀此规则：拆/并 AC 后必须全引点重对齐）

### 4.2 B 类｜行为质量（真跑 Agent，评测配置本身平台无关）

- 载体：skill-up `evals/eval.yaml` + `cases/*.yaml` + `fixtures/`；**引擎是插件，不是身份** → 同一套 case 换 `claude_code`/`codex`/未来 `zcode` 都能跑，这才叫"不受平台影响"
- 本机首跑用 **`claude_code` 或 `codex`**（已装），**不要**把 `qodercli` 写进计划前置
- 分层：L0 每 skill 1 条 smoke（产物存在且 Gate 合法）· L1 每 skill 3–5 条核心分支 · L2 `issue/` 每个 P0/P1 闭环**必须**回流成 case · L3 改 `shared/` 或合并 skill 前全量
- 评分纪律：硬约束用 `rule_based`，结构校验用 `script`（调 4.1 的校验器），**只有语义判断才用 `agent_judge`**，且必须写 rubric
- 基线：`evals/baseline/result.json` + `skill-up run --baseline` 出 diff；**评测必须由干净会话跑**，不接受同一会话自改自评

### 4.3 量具自验（先验再信）——v1 的 4 条修订

1. 删必需章节 → A 类必须红
2. Gate 字段写非法值 → 必须红
3. 故意让 skill 跳步 → B 类对应 case 必须失败
4. **改正文不动台账 → 必须红**（当前不红，靠 4.1-① 修好；此条 v1 已做完反证，不重做）
5. 新增：**同一份产物跑两次，tsr 的 ts 与 sha256 必须一致且等于机器时钟**（防时间戳漂移）

> 全部命中才允许当门禁；否则看板如实标「检出力不足」。

### 4.4 沉没成本口径（评审指出的错误已改）

v1 的「10-10 作废 ≈55% 投入」**不可复算、口径不成立**（同一份数据按不同口径可算出 8.8%–70%，因为个人版重做复用了 `.spec/设计稿/`、`TDD/`、`原型/` 同一路径）。
**新口径**：沉没面 = 作废 DEC 的 **产物 lineage 传递闭包（sourceRefs）∩ 时间切点**，看板输出**区间 + 显式口径声明**，禁止用日期窗或目录前缀冒充。

---

## 5. 闭环（越用越聪明）

```
tsr+git 真相轨 →(可选)适配器富化 → 指标异常
  → 自动生成候选问题卡（带 executionId + ts 窗口 + 产物 sha256 指针，不靠 AI 回忆）
  → 归因到具体 skill 的具体条款（读轨迹原文）
  → 改动方案 → 用户确认（人在环保留）
  → 落改动 + 同批回流 L2 case
  → skill-up run --baseline → 进化台账记 before/after
  → 不达标回滚（台账留 commit 指针）
```
- `skill-optimizer` / `skill-evolver` 诊断入口从「读摘要」升级为「按 obs 指针读轨迹原文」；复用 `issue/`(42 条)、`bug-patterns/`、`evolution/偏好库`，**不新建第二套台账**
- 无人值守：定时任务**只允许跑纯脚本（ETL + A 类 + L0 结构检查）**，⛔ **禁止跑 agent_judge** —— 无人值守产生的 agent 轨迹会污染被观测的语料，且要 Full Access

---

## 6. 里程碑（重排，真实人日）

| # | 里程碑 | 交付 | 验收 | 人日 |
|---|---|---|---|---|
| **M1** | Gate 机械复算（可独立产生价值，最先做） | `validate_core gate` 内建 sha256 核对；`refs` 业务项目可达性 | §4.3 第 4 条反证由「不红」变「红」；KB 项目现存量重跑不炸 | **3** |
| **M2** | tsr 自记轨 + 快照固化 | `scripts/tsr.py` + `tenger.trace/v1` schema + `.spec/obs/run.jsonl` + 脱敏白名单 + `instrumentation-guide.md` 改写 | 同一 skill 两次运行可 diff；ts/sha 由脚本生成；**宿主日志丢失后仓内仍有完整快照** | **3** |
| M3 | 适配器框架 + Qoder 适配器 | `HostAdapter` 接口 + capability 表 + qoder 实现（Bash/Write 主判据、Skill 事件旁证、按 session 目录分组去重） | 有适配器时多出工具数/错误率/loop 数三类指标；拔掉适配器只降级不报错 | 2 |
| M4 | 指标层 + 一页 md 看板 | `obs/metrics.py`、异常→候选问题卡 | 每个指标标注真相源与 capability；依赖缺失项显示 N/A | 2 |
| M5 | 评测骨架（A 类完备 + B 类打通） | 4.1 断言全部；3 个高频 skill 的 `evals/` 用 `claude_code`/`codex` 跑通 + baseline diff | Windows 真实跑通一次；`skill-up` 版本锁 tag | 3–5 |
| M6 | 闭环接线 | 台账新模板 + 纯脚本定时任务 + 回滚演练 | 台账出现一次真实「未验证」判定；回滚可用 | 2 |
| M7 | 扩面 | 其余 skill 的 L0/L1；bad case 回流 | ≥50% 的 L2 case 来自 `issue/` 闭环 | 持续 |

**合计 15–20 人日**（v1 的 8–9 低估一倍）。若只能先做两步：**M1 + M2** —— 它们不依赖任何宿主、不依赖 skill-up、且各自独立产生价值。

## 7. 明确不做

- ❌ 不部署 Langfuse / Phoenix / Opik / MLflow（抽象层级不对齐：它们的 trace=请求，我们的节点=跨天阶段；自托管需 ClickHouse/PG/Redis；且 token 拿不到会让成本看板价值归零）。仅借鉴 OTel 的 span 分层与 attribute 命名纪律。
- ❌ 不自建评测格式，对齐 skill-up 的 `eval.yaml`/`cases/*.yaml`（可导入 Anthropic `evals.json`）
- ❌ 不做 HTML 交互看板、不做 cron 周报（v1 过度工程）
- ❌ 不在本阶段做 skill 精简——必须等 M4 的「规则命中率」有数据后再动，否则精简依据还是直觉

## 8. 风险

1. **skill-up 早期不稳定**（官方 Warning：命令/字段/API 会变）→ 锁 tag、评测配置独立目录、A 类不依赖它
2. **Windows full agent evals 官方指 WSL2**；Go 未安装 → M5 前必做「Windows 原生跑通」最小实验；不通则退到 `script` judge + A 类，B 类延后
3. **tsr 语义字段仍由执行方填写**（gate 值、round、batch 有自报失真风险）→ 用 §4.1-① 的机械复算 + §3 的「摘要不一致数」盯住；本轮**不引入"翻案率"作为守门指标**（记账方仍是自述方，等于自证）
4. **宿主日志会被驱逐**（zcode 实测 `eventEvicted=337745`）→ 适配器只富化、快照必须进仓（M2 交付）
5. 隐私：适配器读到的 `args` 含命令与路径 → 只留 tool_name + 路径哈希 + 字节数，正文白名单
