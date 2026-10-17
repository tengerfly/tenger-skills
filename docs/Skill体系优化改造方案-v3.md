# 技能体系优化改造方案 v1（可执行版 · 待审核）

> v0 → v1 变更：按你 2026-10-17 的三点澄清重写。**v0 的"轻量档太重"是误读，故删除该主线。**
> 状态：**方案稿**，代码与 Skill 正文一字未动。分支 `refactor/skill-system-v3`。
> 实测日期：2026-10-17。所有数字可复现，口径见 §8。

---

## 0. 我理解的需求（v1 修订，请继续纠正）

| # | 你的原话 | 我的复述（v1） |
|---|---|---|
| A | 我开发一次全量 46 个 skill 全部加载，流程慢进度慢，占用 token 上下文 | **核心诉求是装载面**：一次开发不该把整套体系端上来。跟"流程档位分几档"无关。 |
| B | 补充量化指标，先做一般，后期运行项目记录问题迭代自进化 | 指标**先粗后细**；靠真实项目跑出来的问题驱动改进，不是先设计完美指标。 |
| C | 失去哪些能力暂时不能判定；技术性内容要弱化 | **任何以"删/合并能力"为前提的方案，现在都不能做。** |

v0 里我按"轻量档多重"去理解 A，方向偏了。修正后的主线是：**一次开发会话的装载量。**

### 一个必须先说的发现

`~/.zcode/AGENTS.md`（2026-10-17，今天）写着：

> mattpocock/skills 已于 2026-10-17 应用户要求全部禁用……更早的 tenger-skills/PEOS 也已删除。开发方法论统一使用 **obra/superpowers**（v7.0.0，15 个 skill 装入 ZCode 用户级 `~/.zcode/skills/`）。

而 `~/.qoder-cn/skills/` 里仍然是 47 个目录（45 个自有 skill + `shared` + 1 个外来的 `code-review-expert`）。

也就是说：**你现在两家宿主跑两套方法论**。这件事会改变方案取舍（见 §2.3），所以先摆出来。

---

## 1. 事实

### 1.1 "全量加载"是真的，但要看它发生在哪一层

| 层 | 量 | 性质 |
|---|---|---|
| **目录层**：46 条 `name + description` | **6,752 字符**（≈4.5k token） | 每次会话都带，是**常数税** |
| **正文层**：一次完整 CREATE 累计读入的 SKILL.md + 契约 | **203,674 字符**（≈213k token） | 任务越长越贵，是**主要成本** |

**结论：只压目录，收益有限（常数小头）；真正吃掉上下文的是一次任务里被读进来的 20 个正文 + 3.6 万字符的契约。**

两个层次都要收，但权重不同：正文层占 97%。

> 如果你观察到的是"46 个**正文**全进上下文"，那说明还有一层宿主行为我没测到。**S0 第一步就是把它测出来**（`tsr load-audit`），不靠猜。

### 1.2 真实使用数据（这是回答 C 的关键）

来自宿主自己的 `~/.qoder-cn/skill-usage.json`：**共 112 次调用，45 个 skill 里 24 个用过，21 个从未使用。**

| 次数 | skill |
|---|---|
| 38 | workflow |
| 12 | ui-ux-review |
| 8 | ui-ux-design |
| 6 | backend-tech-design · idea-intake |
| 4 | prd-design · prd-review · competitive-analysis |
| 3 | oss-radar · tech-review |
| 2 | auto-test · backend-dev · product-discovery · product-definition · application-blueprint · feature-decision · prd-workflow · prototype-design · prototype-review · skill-optimizer |
| 1 | refactor-planning · code-review · frontend-dev · source-reading |

**前 3 名占全部调用的 52%。**

**21 个从未使用**：bug-fix、change-intake、defect-triage、deployment-execution、essence-distill、fact-check、fidelity-review、frontend-tech-design、impact-analysis、incident-response、optimization-planning、post-release-review、product-analytics、project-onboarding、quality-inspection、release-planning、release-verification、signal-collection、signal-triage、skill-evolver、skill-lifecycle。

分布很说明问题：

- **发布/运维/事故 8 个，全部 0 次** —— 这套子系统从没在你真实任务里跑过；
- **技术设计/开发/测试**：backend-tech-design 6、backend-dev 2、auto-test 2、frontend-dev 1、frontend-tech-design **0** —— 方法论区几乎没被用起来；
- **评审门禁**：ui-ux-review 12、prd-review 4、tech-review 3、code-review 1 —— **门禁区是真正在用**。

> 注意：**0 使用 ≠ 该删**。事故响应、发布验证这类是"保险"，平时不用才对。所以下面的方案不删任何能力。

### 1.3 另外两处装载面污染

1. 安装副本多出一个仓库里没有的 `code-review-expert`（第三方 skill，5,544 字符），与你自己的 `code-review` 抢同一批触发词。**你说的"46 个"是准确的：45 自有 + 1 外来。**
2. `sync-skills.sh` 只增不删（"stale 交人工判断"），所以安装副本会持续漂移。

### 1.4 纯重复：56KB（去重不动任何规则）

| 重复项 | 处数 | 字符 |
|---|---|---|
| Contract Compatibility Layer | 12 个 skill × 约 4.1K | 49,920 |
| 问题记录块 | **45/45** | 9,823 |
| L2 回流块 | 11 | 3,135 |
| 小计 | | **62,878**，减去三份真身 = **净重复约 56,000**（占全量 21%） |

这一块是**纯技术债**：删掉它一条规则都不会消失（`shared/` 里都已有单一源）。

---

## 2. 方案选择

### 2.1 三条路

| 路线 | 做什么 | 代价 | 现在能做吗 |
|---|---|---|---|
| **A 大改造** | 45 → 7 个"阶段包"，重写所有正文 | 周期长、回归面大、需先判定能失去什么 | ✗ 撞上你的 C |
| **B 收口**（**推荐**） | 能力全留，**只改"宿主能看到什么"**；顺带去掉 56KB 重复 | 中等、可回滚、不动规则 | ✓ |
| C 只做去重 | 只拿 56KB | 小、但解不了装载面 | ✓ 但不够 |

### 2.2 为什么推荐 B

1. **不依赖你的 C**：能力一个不删，只把"自动发现"改成"按需进入"。你不必现在判定能失去什么。
2. **数据已经替你分好档**：24 个热 / 21 个冷，这是 112 次真实调用给的，不需要拍脑袋。
3. **收益对得上痛点**：目录 46 → 7；一次开发的正文装载量砍一半以上。
4. **可回滚**：`sync-skills.sh` 一处开关就能退回 45 个平铺。

### 2.3 一个需要你回答的战略问题（它决定 B 的边界）

你今天在 ZCode 换成了 Superpowers（15 个 skill，覆盖 需求访谈 → 写计划 → 执行 → TDD → 评审 → 完成验证）。**这与你这套体系在"开发方法论"区间高度重叠**（你的 frontend-dev / backend-dev / frontend-tech-design / backend-tech-design / auto-test / code-review 共 6 个，112 次里只被调用 12 次）。

Superpowers **没有**的东西，恰好是你在用的东西：Gate 三值、证据摘要、TSR 追溯、注册表、可观测。

所以有两种收口方式：

| | 做法 | 适用 |
|---|---|---|
| **B1 自成一体** | 7 个包覆盖全生命周期（含方法论） | 你仍主要用自家体系做开发 |
| **B2 分工**（推荐） | 方法论交给 Superpowers；自家体系只保留 **质量门禁 + 追溯 + 可观测**（评审、Gate、证据、指标） | 你在两家宿主上各用其长 |

**我推荐 B1 先做**（改动小、不依赖外部），但在 S2 分层时把"方法论 6 个"标成可插拔——将来若要转 B2，只换包内成员，不动架构。

---

## 3. 推荐方案：三刀 + 一表 + 一道闸

### 3.1 第一刀 · 装载面分层（解 A）

**宿主只看到 7 个入口，45 份正文全部保留。**

| 入口 | 热的（有使用记录，包内逐条写"何时读"） | 冷的（0 使用，一行清单 + 点名即加载） |
|---|---|---|
| `workflow` | workflow | — |
| `product` | idea-intake、competitive-analysis、product-discovery、product-definition、application-blueprint、feature-decision、prd-design、prd-review、prd-workflow | change-intake、impact-analysis、product-analytics |
| `design` | ui-ux-design、ui-ux-review、prototype-design、prototype-review | fidelity-review |
| `build` | backend-tech-design、tech-review、backend-dev、frontend-dev、code-review | frontend-tech-design |
| `verify` | auto-test | — |
| `ship` | —（全部 0 使用） | release-planning、deployment-execution、release-verification、post-release-review、signal-collection、signal-triage、incident-response、quality-inspection |
| `meta` | oss-radar、skill-optimizer、source-reading、refactor-planning | skill-evolver、skill-lifecycle、essence-distill、fact-check |
| 独立入口 | — | bug-fix、project-onboarding、defect-triage、optimization-planning |

- 冷的不进目录，**包正文里有一张 4 行清单**：名字 + 一句话触发条件 + "点名或命中条件时才读它"。代价约 600 字符。
- **能力零损失的可验证判据**：随机抽 5 个冷门 skill（含 0 使用的），用**原名字**显式调用，必须能完成同一任务。做不到就算方案失败。

### 3.2 第二刀 · 去重（-56KB，零风险，与 A/B/C 都无关）

| 动作 | 收益 |
|---|---|
| 45 处问题记录块 → 1 行引用 | −9,823 |
| 12 处 Contract Compatibility Layer → `shared/legacy-skill-adapter.md` 一处 + 各留差异 | −47,800 |
| 11 处 L2 回流块 → 引用 `governance/eval-spec.yaml` | −2,900 |
| 5 个 legacy-adapter 补章节或显式登记豁免 | 契约三档 → 一档 |

**一条规则不删。** 验收：`validate_core` 四子命令 + 12 套 eval 结构层**仍全绿**；反向对照：删掉一个引用目标，校验器必须红。

### 3.3 第三刀 · 技术型正文机械化（只做 2 个最热的，先证明路子对）

**范围严格限定在"技术型 / 参考型"**，纪律型（铁律）一条不动。

| 对象 | 现状 | 做多少 | 出口 |
|---|---|---|---|
| `frontend-dev` | 20,744 字符，48 行错误表，6 条高危坑 | 全文 | 检查器 / references / 删（模型已会且判不出） |
| `ui-ux-design` | 18,535 字符，35 行错误表 | 全文 | 同上 |

这两个占全部 306 行错误表的 **27%**，且是使用频次最高的两个（ui-ux-design 8、ui-ux-review 12 会读它）。

**规则三出口，每行必须选一个并留痕**：

| 出口 | 判据 | 例 |
|---|---|---|
| **检查器** | 给产物能返回 finding | 禁 `父级>标签` 通配、`@media` 断点随 token 搬、`calc(100vh-header)`、弹框负 margin |
| **references** | 查得到、用完就不需要 | 框架等价写法、动效曲线库、组件库用法 |
| **删** | 模型已经会 + 机器判不出 + 删了也没再犯过 | 命名规范、目录约定、JSDoc 逐参注释 |

**正文预算（进校验器）**：包 `SKILL.md` ≤ 6,000 字符；单个成员 ≤ 12,000 字符。超了必须下沉，不许加长。

### 3.4 一表 · 量化指标 V1（解 B，先粗后细）

**V1 只追求"能比较、能排序"，不追求精确。全部来自现有数据，不新增埋点。**

| # | 指标 | 数据来源 | 现状 | V1 口径 |
|---|---|---|---|---|
| 1 | skill 使用频次 / 0 使用名单 | 宿主 `skill-usage.json` | **已有** | 直接读，月度过一次 |
| 2 | 一次任务装载量（字符） | 本仓脚本按任务节点算 | 已有基线（203,674） | 每个任务跑完记一行 |
| 3 | 返工轮次 | TSR `round`/`batch`（已有字段，未聚合） | 未聚合 | 每产物均值 |
| 4 | 缺陷复发率 | `tsr recurrence`（已有 6.9%） | 未按 skill 分组 | 按 skill/包分组 |
| 5 | 规则命中率 | 检查器 finding 的 `ruleId` | **依赖 S3** | 0 命中进观察名单 |
| 6 | 项目侧可维护性（粗） | 项目仓 | 无 | 重复代码块数 / 超长文件数 / 契约漂移次数 |

- 第 6 项就是你说的"屎山"的**先做一般版**：3 个便宜指标，够排序、不够考核。后期用真实项目的问题记录再细化。
- 所有指标输出到 `.spec/obs/`（派生、不入库），**不新增报表系统**。

### 3.5 一道闸 · 新增付费（先只对新增，不动存量）

- 新增 **M 类**规则必须同时给 `ruleId`（可机器查）；
- 新增 **J 类**规则必须写一句"为什么既不能机械化、也不是纪律型"；
- **存量 306 行不管**——避免一次性大清理（撞你的 C）。

这条闸只防"继续膨胀"，不要求你现在做减法。

---

## 4. 执行顺序与审核点

| 步 | 产物 | 工期 | 验收 | 回滚 | **你要审核什么** |
|---|---|---|---|---|---|
| **S0 体检** | `docs/装载面基线.md` + `tsr load-audit` 子命令 | 2h | 能打印"这次任务该读哪些文件、共多少字符"；46 条目录实测字节 | 纯新增 | 分档名单（24 热 / 21 冷）是否认可 |
| **S1 去重** | 45 个 SKILL.md 改引用 | 0.5d | `validate_core` + 12 套 eval 全绿；总字符 −56K | 单 commit revert | 是否有规则被误删（抽查 10 个 skill） |
| **S2 分层** | `packs/` 7 个入口 + 45 成员 + sync 改造 | 1–2d | 宿主目录 46→7；抽 5 个冷门 skill 按原名仍可执行；旧项目 `.spec` 不受影响 | 改 sync 一处退回 | 7 个包的边界；冷门清单是否有一条你其实在用 |
| **S3 机械化** | frontend-dev / ui-ux-design 正文 + 检查器 | 2–3d | 每条新检查带反向对照（改坏必须红）；正文各降 ≥35% | 单 commit revert | 被删/下沉的那 83 行里有没有你舍不得的 |
| **S4 指标接线** | `tsr metrics` 输出 6 项 | 1d | 用 112 次真实调用跑通；能指出 ≥1 个 skill 的返工轮次显著高于均值 | 纯新增 | 指标口径是否对得上你的直觉 |

**S0 完就先给你看数据再动手**，避免"方案看着对、名单不对"。

---

## 5. 目标与不做

### 可测目标（S2 完成后重测）

| 指标 | 基线 | 目标 |
|---|---|---|
| 宿主目录条目 | 46 | **7** |
| 目录常驻字符 | 6,752 | ≤ 1,600 |
| 一次完整 CREATE 累计装载 | 203,674 | ≤ 100,000 |
| 单步峰值（frontend-dev） | 67,827 | ≤ 38,000 |
| 全量 SKILL.md 字符 | 264,644 | ≤ 195,000 |
| 能力损失 | — | **0**（抽 5 个原名字调用必须成功） |

### 明确不做

1. 不删任何 skill、不删任何规则、不合并能力（撞 C）。
2. 不动 Gate / Envelope / digest / TSR / 证据标签（护城河）。
3. 不新增流程节点、不加第二个运行时 CLI（用 `tsr.py` 子命令）。
4. 不加报表系统、不引入可视化评测台。
5. 不把判断类（J）规则机械化。
6. 不为让指标好看而改闸门。

---

## 6. 待你确认（三件 + 一件战略）

| # | 问题 | 我的建议 |
|---|---|---|
| 1 | S0 的 24 热 / 21 冷 分档，你是否认？特别是有没有"0 使用但你马上要用"的？ | 先按数据分，名单你改一版 |
| 2 | 7 个包的边界（workflow / product / design / build / verify / ship / meta）是否合理？ | 认可即按此建 |
| 3 | 正文预算（包 ≤6K、成员 ≤12K）是否接受？这是防再次膨胀的唯一硬约束 | 接受，超限即下沉 |
| 4 | **战略**：这套体系以后主要跑在哪家宿主？与 Superpowers 是"并存各用其长"（B2）还是"自家全包"（B1）？ | 先按 B1 做，但把方法论 6 个标成可插拔 |

---

## 7. 与 v0 / 历史方案的关系

| 提法 | 处置 |
|---|---|
| v0 的"轻量档指令量"分析（§1.2 数据） | **数据保留**（仍是有用的成本证据），但不再是主线 |
| v0 的"9 个阶段包" | 收窄为 **7 个**，且改为"只改装载面、能力全留" |
| 历史"按需加载"×4 次 | 前三次都只落"写作规范"；**这次落"宿主能看到什么"**——这正是过去失败的那一步 |
| 历史"精简 skill"（tsr slim 三读数闸门） | 闸门不动；**给它接 finding 输入**是 S3 之后的事 |
| 历史"不合并、不新增数量" | 遵守；本方案不合并 |
| `skill-writing-standard.md` §二/§八 | 直接复用（L1–L4、归位原则），把 L1 从节点改成入口 |

## 8. 口径

- 字符数：Python 遍历 `SKILL.md`（排除 `.git/.venv/__pycache__/.tmp-eval/_clones/.spec/evals/chats/issue/.codebuddy`）。
- 一次任务装载量：该任务节点的 `SKILL.md` + 其正文按文件名命中的 `shared/*.md` + `workflow/SKILL.md` + `execution-profiles.md`（去重）。
- token 折算：1.05 字符/token。
- 使用数据：`C:\Users\15136\.qoder-cn\skill-usage.json`（宿主自记，112 次）。
- 均未计入 references（688K，本就按需）与 assets。
