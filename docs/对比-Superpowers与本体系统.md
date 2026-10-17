# 对比研究：obra/superpowers vs 本仓体系

> 读的是你机器上已安装的 v7.0.0（`~/.zcode/skills/`，15 个 skill），不是二手转述。
> 目的：找**值得借的**，也找**不能借的**。结论先放前面，证据在后。
> 实测日期 2026-10-17。

---

## 0. 结论先行

**两套东西解决的不是同一个问题。**

| | Superpowers | 本仓体系 |
|---|---|---|
| 解决 | **执行者的纪律**：让 agent 不停、不偷懒、不自我欺骗 | **产物的可验证性**：是否闭环、可追溯、未被篡改 |
| 手段 | 文档 + git + ledger + subagent 隔离 | 注册表 + 状态机 + digest + Gate + 证据标签 |
| 质量从哪来 | 新鲜上下文的评审者 + TDD + 证据门禁 | 判据 + 门禁 + 可复算的摘要 |
| 规模 | 15 个 skill / 161,962 字符 / 目录 2,319 字符 | 45 个 skill / 264,644 字符 / 目录 6,752 字符 |

一句话：**它教你"怎么让 agent 一直往前走"，你教它"怎么证明走对了"。**

所以不是二选一。你要借的是它的**执行纪律层**，保留自己的**产物验证层**。

---

## 1. 规模对照（同为"目录常驻 + 按需正文"）

| 指标 | Superpowers | 本仓 |
|---|---|---|
| skill 数 | 15 | 45 |
| SKILL.md 总量 | 161,962 字符 | 264,644 字符 |
| 平均单个 | 10,797（**更大**） | 5,881 |
| 目录常驻（description 合计） | **2,319** 字符 | **6,752** 字符 |
| 平均 description | 154 字符 | 150 字符 |
| references/assets | 少而精（几个 prompt 模板 + 3–5 个脚本） | 688,364 字符 references |

**两个反直觉读数**：

1. 它的单个 skill **比你的大**（10.8K vs 5.9K）。说明"技能多不多"不取决于每个写多长，取决于**入口有几个**。
2. description 平均长度几乎一样（154 vs 150）。所以目录膨胀的锅不在写法，在**数量**。

---

## 2. 值得借的七个机制

### ① 裁决而非停等（Rulings, not stalls）—— 最值钱的一条

原文（`subagent-driven-development/SKILL.md:19-25`）：

> **Rulings, not stalls.** A running plan does not wait on a human. Conflicts, ambiguities, plan defects, a cap you would have asked to exceed — decide them. The spec is the binding authority, the plan is its argument, and your judgment settles what neither answers. Record every decision in the ledger as `Ruling: <what you decided> — <why> — <what it costs if wrong>`, and keep going. **A wrong ruling costs rework your human partner can see and undo; a session parked on a question costs their whole day and buys nothing.**

只有四件事停（`:27-31`）：不可逆/破坏性操作、安全敏感动作、worktree 外的副作用（合并/推送/发布）、计划烂到每条路都是猜。

**对照你的体系**：你知道库项目走了 9 天还没到技术方案，中途有大量"必须确认/强制暂停"。你的 `execution-profiles.md` 甚至专门写了一段防止"以并行不空等为借口"——约束方向是**少跑**，而它约束的方向是**别停**。

**借法**：把"必须等用户确认"分两类：
- **真决策**（范围、取舍、付费、生产操作）→ 停，问；
- **其余全部**→ 裁决 + 记账 + 继续，记账格式照抄它的三段式（决定/理由/错了的代价）。

这一条是对"一周多"最直接的一刀。

### ② 断路器 + 逐条裁决（而不是例外登记）

它的修复循环（`:75-81`）：

```text
Fix round R of 5：R≤3 让原 implementer 改；R≥4 换新鲜 implementer + 更强模型
R=5 → 逐条裁决 → 只有 load-bearing 的才继续问；其余「停靠」进 ledger 并继续
```

**对照你的体系**：3 轮上限打满 → 强制 `CONDITIONAL` + 七字段例外登记 → 依然 `BLOCKED`。

差别不在轮次数（3 vs 5），在**收尾方式**：它以"一个决定"收尾，你以"一个阻塞状态"收尾。**阻塞状态不会自己消失，决定会。**

### ③ Review package + 上下文隔离

原文（`subagent-driven-development/SKILL.md:10`）：

> They should never inherit your session's context or history — you construct exactly what they need.

配套脚本 `scripts/review-package` 把 diff + spec + plan 打成评审包；reviewer 只看这个包。

**对照你的体系**：评审者拿到的是整个会话 + 全部产物 + "找没闭环"的开放式职责。**开放职责 + 全量上下文 = 每轮都能发现新东西**，这正好解释原型评审第 3 轮还能报 93 个 P2。

**借法**：评审输入必须是**闭合的包**（diff/产物 + 判据集 + 上轮 F1），不是"你去看吧"。

### ④ 技能即 TDD：写之前先看它怎么失败

`writing-skills/SKILL.md:30-45` 给了一张完整映射：

| TDD | 写技能 |
|---|---|
| 测试用例 | 带压力的场景 + subagent |
| 生产代码 | SKILL.md |
| RED | 没有技能时 agent 违规（baseline） |
| GREEN | 有技能时遵守 |
| Refactor | 堵住新找出的借口 |

`testing-skills-with-subagents.md:11`：**"If you didn't watch an agent fail without the skill, you don't know if the skill prevents the right failures."**

**对照你的体系**：行为层评测 19/19 blocked、360 行台账只真跑 6 条、单条 3–10 万 token、默认不跑。**你是把行为评测当回归套件，它是把行为测试当写作工序。**

成本结构完全不同：回归套件要"每次改动 × 全部用例"；写作工序只要"改这个技能时 × 1 次"。

**借法**：行为测试挂到"改技能"这个动作上，不挂到 CI 上；且**强制先跑 baseline**（无技能时必须失败，否则说明这条技能本来就不需要）。

### ⑤ 借口对照表（Rationalization Prevention）

它的纪律型技能几乎都有一张表，而且**表里的借口是从 baseline 测试里逐字抄出来的**：

`verification-before-completion/SKILL.md:61-72`：

| Excuse | Reality |
|---|---|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |

`using-superpowers/SKILL.md:37-50` 有 12 行同类表。

**对照你的体系**：你有 306 条错误对照行，但那是"**技术上犯的错**"（怎么写错），不是"**心理上找的借口**"（怎么说服自己可以不做）。后者才是纪律失效的真实入口。

**借法**：从 `issue/` 池里抄真实借口（"这条很简单不用评""先跑起来再说""看起来一样"），建一张 ≤15 行的借口表。**这比再写 10 条禁令有用。**

### ⑥ 薄宿主适配层

`using-superpowers/references/` 有 7 个文件：`claude-code-tools.md`、`codex-tools.md`、`pi-tools.md`、`gemini-tools.md`、`hermes-tools.md`、`muse-tools.md`、`antigravity-tools.md`（1.2–4.8KB）。

核心技能里**不写任何宿主细节**，只在入口按宿主名分派。

**对照你的体系**：`sync-skills.sh` 把 45 个 skill + 三份 shared 复制到宿主目录；宿主差异靠"目标目录"处理，但没有"这个宿主能干什么"的声明。

**借法**：`hosts/<host>.md`（每个 ≤1KB）：有没有 subagent、有没有浏览器、超时上限、skills 根在哪。核心判据只引用"能力名"，不写"在某某宿主要怎么点"。

### ⑦ 一次工具调用完成两件事

`executing-plans/scripts/task-start` 注释：

> One tool call instead of two, **because every call in an inline session is a turn that re-reads the whole context.**

`task-done` 更狠：跑测试 → 留全量日志 → **只有成功才写 ledger**（"A failing command records nothing: the task is not complete."）。

**对照你的体系**：每个节点 `tsr node-start` + `tsr node-end` = 2 次调用；13 节点 ≈ 26 次上下文重读。而 TSR 的 JSONL 事件流对人不友好，人要看的是"走到哪了"。

**借法**：合并成一次（如 `tsr node --start/--end` 仍是一次调用完成校验+记账），并额外维护一份**人可读的一行式 ledger**（给用户看状态卡，给机器留事件流）。两者不冲突：ledger 给人和下一轮 agent 读，JSONL 给复算。

---

## 3. 不能借的三件

### ✗ 模型路由

它在 `:75` 明确写：R≥4 时 **"fresh implementer, more capable model"**，并有 `## Model Selection` 一节。

**这与你的第四不变量（模型无关）直接冲突。** 它靠"换更强的模型"兜住质量；你要靠"判据"兜住质量。

**更重要的警告**：模型路由是最容易**伪装成质量保证**的偷懒——一旦允许"难的就换强模型"，判据就不会被写硬了。**这条不要学，而且要防。**

### ✗ 用 15 个 skill 覆盖全生命周期

它只覆盖"有 spec + plan 之后怎么实现"。没有多端、多环境、发布、运维、事故、需求竞品研究。你的复杂度不是它想解决的问题，直接砍到 15 个会丢能力。

### ✗ 依赖 subagent 作为唯一评审手段

它的评审几乎全靠"派一个新鲜 subagent"。宿主没有多 agent 时它降级成"自己读一遍"（`brainstorming/SKILL.md:176-177` 明说）。**你要求宿主无关，就不能把核心机制押在 subagent 上**——subagent 只能是增强路径。

---

## 4. 你的优势（别在"借鉴"里丢掉）

| 能力 | Superpowers | 本仓 |
|---|---|---|
| 需求→产物→代码→测试→发布 的追溯链 | ✗（只有 git diff） | ✓ traceability |
| 产物内容防篡改（digest 复算） | ✗ | ✓ `contentDigest`/`subjectDigests` |
| 严重度与 Gate 的客观定义 | ✗（Critical/Important/Minor 无标定） | ✓ Gate 三值 + P0/P1/P2 |
| 体系自身的观测与进化 | ✗ | ✓ obs / tsr / evolution |
| 换模型后质量可验证 | ✗（靠换模型） | 目标，尚未做到 |
| 执行纪律（不停、不偷懒） | ✓✓ | ✗ 这是你缺的 |

最后一行就是这次对比的全部价值：**它的强项恰好是你的弱项，你的强项它根本没有。**

---

## 5. 对 v3 方案的修正（五处）

| # | v3 原设计 | 改成 | 理由 |
|---|---|---|---|
| 1 | 收敛器只管"停得住" | 增一条 **"裁决优先"**：非四类硬停，一律裁决+记账+继续 | 你的痛点是"停太多"，不是"停不住" |
| 2 | 3 轮后 → 例外登记 + BLOCKED | 3 轮后 → **逐条裁决 + 非关键项停靠 + 继续**；只把 load-bearing 拿出来问 | 以决定收尾，不以阻塞收尾 |
| 3 | 判据三层（L1/L2/L3） | L3 的输入改成**闭合评审包**（diff/产物 + 判据 + 上轮 F1） | 开放职责 + 全量上下文 = 永远有新增 |
| 4 | 行为评测留在 `evals/` 回归 | 挂到**"改 skill"这个动作**上，且强制 baseline（无技能必须失败） | 成本结构从回归变成工序 |
| 5 | 宿主无关靠"文件+脚本" | 补 `hosts/<host>.md` 薄适配 + **核心机制不依赖 subagent** | subagent 只能是增强，不能是必需品 |

**外加两条新判据类型**（原 J/M/D 不够用）：

- **E 借口类**：从真实 issue 抄出来的"自我说服话术"，配对照表；它防的不是"不会做"，是"知道却不做"。
- 现有 D（纪律）保留，但要求 **D 类尽量配一张 E 类表**，否则纪律只是标语。

---

## 6. 下一步（等你选）

1. **只借 ①（裁决）**：最小改动，直接改 `execution-profiles.md` + 3 个评审 skill，1 天见效。风险最低。
2. **借 ①②③**：再加断路器与闭合评审包，等于把 v3 的收敛器按它的成熟形状改一遍。
3. **全借（①–⑦）**：等于重做执行层，2–3 周，收益最大也最容易失控。

我的建议：**先做 1，用真实项目验一周**。因为"停太多"是你现在唯一的硬痛点，其余都是它的衍生。若一周后停等明显下降，再做 2。

---

## 附：证据索引

| 结论 | 出处 |
|---|---|
| 裁决而非停等 | `~/.zcode/skills/subagent-driven-development/SKILL.md:19-31` |
| 断路器 R=5 / 换模型 | 同上 `:75, :104-113` |
| 上下文隔离 | 同上 `:10`；`requesting-code-review/SKILL.md:8, :79-80` |
| 技能即 TDD | `writing-skills/SKILL.md:30-45`；`testing-skills-with-subagents.md:7-41` |
| 借口对照表 | `verification-before-completion/SKILL.md:61-72`；`using-superpowers/SKILL.md:37-50` |
| 宿主适配层 | `using-superpowers/SKILL.md:52-61` + `references/*-tools.md`（7 份） |
| 一次调用 / 失败不记账 | `executing-plans/scripts/task-start`、`task-done` |
| 设计批准前的硬门 | `brainstorming/SKILL.md:179-193`（`<HARD-GATE>`） |
| 不检查就声明完成 | `verification-before-completion/SKILL.md:16-36` |
