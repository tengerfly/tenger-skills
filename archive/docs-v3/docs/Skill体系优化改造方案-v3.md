# 技能体系优化改造方案 v3（详细规划 · 待审核）

> **这一版换了地基。** v1 把问题看成"装载面太大"，v2 看成"评审不收敛"；两者都对，但都只是症状。
> v3 的地基是你确认的那句话：**体系的资产是判据，skill 只是判据的挂载点；评审是判据的生产线；跑完一次要比上次强一点。**
>
> 四条不变量：**换宿主质量不变 · 换模型质量不变 · 越跑越强 · 停得住**。
> 状态：方案稿。**代码与 Skill 正文一字未动。** 分支 `refactor/skill-system-v3`。

---

## 0. 一页纸

**这套体系是什么**：一台把"高质量软件"从"依赖执行者水平"变成"依赖判据覆盖面"的机器。模型负责产出，体系负责发现问题、把问题翻译成可执行的改法、循环到判据满足，然后把这次学到的东西**留下来**。

```text
        ┌──────────────── 飞轮 ────────────────┐
        │                                      │
   项目/评审发现真问题 ──► 提炼成判据(M/J/D) ──► 入库(带ID/反例/出处)
        ▲                                      │
        │                                      ▼
   下次同类问题被自动挡掉 ◄── 按阶段挂载执行 ◄── 命中/复发记账
        │
        └──► 复利率：同类问题第二次出现 → 0
```

**四条不变量怎么落**：

| 不变量 | 落点 |
|---|---|
| 宿主无关 | 判据、检查、口径全是 YAML/Markdown/Python；入口是一份清单，不依赖宿主 skill 发现 |
| 模型无关 | 判据要么是脚本断言、要么是带反例的人判清单；**没有"评审觉得可以"这种退出条件** |
| 越跑越强 | 飞轮五环 + 三道机械卡点；复发率是主指标 |
| 停得住 | 收敛器 R1'–R7；自主跑有预算闸与收敛报告 |

---

## 1. 与 v1/v2 的差别（一句话对照）

| 维度 | v1 | v2 | **v3** |
|---|---|---|---|
| 诊断 | 装载面太大 | 评审不收敛 | **判据没有积累通道，所以每次从零长** |
| 核心动作 | 分层装载 | 加收敛器 | **建判据库 + 接飞轮 + 收敛器作为配套** |
| 对评审的态度 | 成本，要压 | 障碍，要收敛 | **生产线，要让它产出的东西可复用** |
| 对规则的态度 | 冻结存量 | 机械化减量 | **资产化增值（只禁没 ID 的散文）** |
| 速度从哪来 | 少读文件 | 少走轮次 | **判据越厚，轮次越少**（需求域 3 轮收敛即证据） |
| 模板库 | 未处理 | 弱化 | **换物种：代码模板 → 判据/测试方案库** |

---

## 2. 原子对象：判据（Criterion）

### 2.1 三类

| 类 | 定义 | 判定方式 | 占比目标 |
|---|---|---|---|
| **M 机械** | 给定产物能判真假 | 脚本 exit code / 断言 | ≥60% |
| **J 判断** | 需要人/模型的品味判断 | 人判清单 + 反例 + **必须挂 `tasteRef`** | ≤30% |
| **D 纪律** | 压力下会违反的行为约束 | 尽量脚本化（用 digest / git / 文件状态），否则清单 | 其余 |

> **J 类是这套体系的特色，也是风险点。** 它承载你的工程品味，但必须挂到一条已拍板的决策（`DEC-*`）上——没有 DEC 就不许入库，先来问你。

### 2.2 字段规范

```yaml
id: CRIT-DESIGN-0012            # CRIT-<STAGE>-<4位>，全局唯一，永不复用
version: 1                      # 判据语义变更必须 +1
stage: design                   # product | design | build | verify | ship
deliverable: D2                 # D1 需求包 | D2 设计包 | D3 方案包 | D4 实现包 | 发布
class: M                        # M | J | D
title: 设计稿状态词必须在 design-system 有映射
criterion: >                    # 一句话说清"什么情况算违规"，必须能判真假
  设计稿 HTML 中出现的每个状态词，都能在 design-system.md §1.2 找到映射

source:                         # 出处：三选一以上，必填
  issue: issue/UI-UX-Review/2026-10-12/03-状态词无映射.md
  project: knowledge-bases
  decision: DEC-20261012-UIX-STATE-WORDS

check:                          # 怎么判
  kind: script                  # script | checklist | manual
  ref: checks/design/state_word_coverage.py
  args: ["--design-dir", ".spec/设计稿", "--system", ".spec/设计稿/design-system.md"]
  pass: exit 0 且 missing == 0

antiExample: >                  # 反例，必填。没有反例说明判据写不清
  12 种状态词混用，§1.2 只定义 4 种；评审靠自然语言逐页数，数出 28 处

severity: P1                    # 由 governance/severity.yaml 规则表判定，不由评审手感
ownerSkill: ui-ux-review        # 谁挂载执行
status: active                  # active | observing | retired
tasteRef: null                  # J 类必填；M/D 可为 null
```

**入库四条硬标准**（缺一条即拒绝入库）：

1. **可判真假**——给定产物能得出"违规/不违规"；
2. **有反例**——写不出反例 = 判据没想清；
3. **有出处**——来自哪个 issue / DEC / 项目；
4. **有挂载阶段**——属于哪个交付物，不知道挂哪 = 不该入库。

### 2.3 三个真实例子

**M 类（脚本）**：见上。

**J 类（判断 + 你的品味）**
```yaml
id: CRIT-DESIGN-0003
stage: design
deliverable: D2
class: J
title: 设计稿不得擅自改动原型结构
criterion: 任一页面的区块增删或顺序变化，必须能指到一条授权 DEC
check:
  kind: checklist
  ref: checks/design/structure-diff.md
  items:
    - 逐页比对原型与设计稿的区块清单
    - 出现差异时，能否指到 DEC id
antiExample: "设计稿多出三个区块，评审仅写『与原型基本一致』"
tasteRef: DEC-20260815-UIX-STRUCTURE-ZERO   # 你拍板：载体结构零改动
severity: P0
ownerSkill: ui-ux-review
```

**D 类（纪律，用 digest 机械化）**
```yaml
id: CRIT-REVIEW-D001
stage: design
class: D
title: 只审不改
criterion: 评审窗口内，被评审产物目录的文件字节不得变化（subjectDigests 复算一致）
check:
  kind: script
  ref: checks/common/review-readonly.py
antiExample: "评审报告第 3 轮发现 7 个 P0——因为前两轮之后稿面被改过"
severity: P1
```

> **最后这条值得单独说**：`只审不改` 是你早就拍过的口径，机械化之后**同时解决了不收敛**——知识库项目"第 3 轮凭空多 7 个 P0"，本质就是评审期间产物在变。一条纪律判据，抵得上一套新流程。

---

## 3. 判据库

### 3.1 目录结构

```text
governance/
  criteria/
    index.yaml            # 全量索引：id / stage / class / check.kind / status / 命中数
    product.yaml          # 按阶段分文件 —— 这是"按需加载"的真正粒度
    design.yaml
    build.yaml
    verify.yaml
    ship.yaml
  severity.yaml           # P0/P1/P2 规则表（含例与反例）
  convergence.yaml        # 收敛器参数（闭合集 / P2 预算 / 轮次 / 时长）
  taste/                  # 你的工程口径台账
    index.yaml
    DEC-*.yaml
checks/
  common/                 # 跨阶段：digest、只审不改、契约一致
  product/  design/  build/  verify/
  runner.py               # 统一执行器：跑一个阶段的全部 script 类判据
templates/
  D1-需求包.md  D2-设计包.md  D3-方案包.md  D4-实现包.md
```

### 3.2 按阶段挂载 = 真正的按需加载

你要的"某一阶段只加载对应的 skill"，正确的实现不是藏 skill，是**判据按阶段切分**：

```text
进入 design 阶段
  → 读 packs/design/SKILL.md（4–6K，阶段契约）
  → 读 governance/criteria/design.yaml（本阶段判据，只这一份）
  → 跑 python scripts/tsr.py stage check --stage design
      → checks/runner.py 执行本阶段全部 script 类判据 → findings
  → 只对 findings 里 checklist 类去读 checks/design/*.md
```

**判据库再厚，单个阶段只加载自己那一份。** 这就是"越跑越强"与"上下文不爆"能同时成立的原因。

### 3.3 完整性校验（进 CI）

- `id` 唯一、格式合法、`version` 单调；
- 每条的 `check.ref` 文件存在（或 `kind: manual` 且挂了 `tasteRef`）；
- 每条有 `antiExample` 与 `source`；
- `class: J` 必须有 `tasteRef`，且该 DEC 存在；
- `stage`/`deliverable` 在注册枚举内；
- 索引与分文件不漂移（同 `validate_core` 现有风格）。

### 3.4 从现有资产迁移（不新造，只归位）

| 现有资产 | 量 | 迁移去向 |
|---|---|---|
| 错误对照表行 | 306 | 逐行判 M/J/R：M→判据，J→判据+DEC，R→references（正文只留引用） |
| `evals/` 用例 | 64（45 结构 + 19 行为） | 结构类直接成 `kind: script` 判据；行为类保留在 evals，不混入 |
| `known-issue-patterns.md` | 11 个 skill | 多条合并成一条判据（同模式去重） |
| l2Triage「不可机械化」9 条 | 9 | **不再消失**：转成 J 类判据（人判清单 + 反例 + tasteRef） |
| `issue/` 41 条 | 41 | P0/P1 逐条生成判据；P2 进 backlog |
| `bug-patterns/` | — | 与判据库合并，避免第三套池子 |

> l2Triage 里那 9 条判"不可机械化"就消失了，是当前最大的资产流失点——**"不可机械化"不等于"不用沉淀"**。

---

## 4. 飞轮：五环 + 三道卡点

### 4.1 五环

| 环 | 触发 | 动作 | 产物 |
|---|---|---|---|
| ① 捕获 | 评审出 finding / 项目出 issue / 逃逸缺陷 | 记原始事实（现状已有） | `issue/`、finding 记录 |
| ② 分类 | 任一 P0/P1 | 判 M/J/D；判不了的写"待定"并挂 owner | 分类结论 |
| ③ 入库 | 分类完成 | 生成 `CRIT-*`，补反例、出处、挂载阶段 | criteria 文件 |
| ④ 执行 | 进入阶段 | `tsr stage check` 跑本阶段 script 判据 | findings + hits 台账 |
| ⑤ 读数 | 每次执行 | 命中/复发/0 命中统计 | `criteria-hits.jsonl` |

### 4.2 三道机械卡点（这是"自进化"能被强制的原因）

| 卡点 | 规则 | 执行者 |
|---|---|---|
| **K1 回流** | P0/P1 关闭前必须有一条判据（M/J 皆可），或显式"不可沉淀"裁决 + 理由 | `relay.py` 升级（现已有 26/27 回流） |
| **K2 复发升级** | 同一 `CRIT-*` 累计 fail ≥2 次 ⇒ 必须升级为 script 类，或补强 check；否则报红 | 新增 `tsr criteria recur` |
| **K3 沉淀退役** | 连续 N 次执行 0 命中 ⇒ `observing`（不删，只是不再挡） | `tsr criteria decay` |

> K2 是飞轮的心脏：**同一个错犯第二次，说明判据不够硬**，必须机械化或补强，而不是再写一条散文。

---

## 5. 收敛器（R1'–R7）

| 规则 | 内容 | 机械核验 |
|---|---|---|
| **R1' finding 绑版本** | 每条 finding 记 `subjectDigest`；该文件变了，只作废绑定它的 finding，不冻结整个产物 | ✅ 现成 digest |
| **R2 闭合集** | 第 1 轮产出 `F1`（固定 ID 集）；第 2 轮起只验 F1，不新增 | ✅ 复核报告只能出现 F1 的 ID |
| **R3 新发现进队列** | 新问题进 backlog 不阻断；仅 P0 或"F1 同类复发"可并入 F1 | ✅ 类型字段 |
| **R4 退出条件** | F1 全关 + L1/L2 全绿 = PASS，**不含"评审觉得可以"** | ✅ 全机器可判 |
| **R5 严重度规则表** | P0/P1/P2 由 `severity.yaml` 定义并附例，不由手感 | ✅ 规则表 + 抽查 |
| **R6 P2 预算** | 每轮新增 P2 上限（默认 10）；超出须给"为什么是新类"否则丢弃 | ✅ 计数 |
| **R7 自主预算闸** | 轮次 ≤3、时长达阈、同交付物发现数达阈 ⇒ 停下出**收敛报告**（卡哪条判据 / 为什么没关 / 要你定什么），**不自动开新批次** | ✅ 计时计数 |

`governance/convergence.yaml` 存参数，避免散落在各 skill 正文。

---

## 6. 阶段、交付物与检查集

### 6.1 七个入口、四个交付物

| 入口（你已认可） | 负责的交付物 / 检查 |
|---|---|
| `workflow` | 编排、门禁核对、失败回退 |
| `product` | **D1 需求包**（含发现/竞品/定义/蓝图/取舍/PRD 全部思维步骤） |
| `design` | **D2 设计包**（原型 + 设计稿 + token + 四维评审） |
| `build` | **D3 方案包** → **D4 实现包**（技术方案 + 开发 + 代码评审） |
| `verify` | 验收（auto-test，外部仓先定单一事实源） |
| `ship` | 发布 / 运维 / 事故 / 巡检 |
| `meta` | 体系自身的优化与进化 |

### 6.2 思维步骤不压，只合并交付物与 Gate

- **D1 内部仍走** intake → discovery → competitive → definition → blueprint → feature-decision → prd-design 的思维链，但**产出是一份 D1 文档 + 一份验收判据集**，中间不落 7 份独立产物、不设 7 个 Gate。
- **用户确认点**：每个交付物 1 次（需求范围 / 设计口径 / 方案取舍），共 3 次；其余靠判据。

> 这条是对 v2"4 个包"的修正：**压的是产物与门禁的数量，不是思考的深度。**

### 6.3 每个交付物的检查集

| 层 | 内容 | 谁跑 |
|---|---|---|
| L1 结构 | 章节/字段/引用/digest/登记 | `validate_core` |
| L2 契约 | 接口/类型/枚举/页面↔原型↔token | `checks/*` |
| L3 语义 | 闭环/口径/还原度/可维护性 | 评审 skill + 判据库里的 J 类清单 |

**硬约束：L3 只查 L1/L2 查不到的。** 逐段对账、token 搬运、契约一致这类现在交给模型用自然语言做的活，全部下沉到 L2。

### 6.4 一个 Gate、一个确认点

每个交付物：`L1+L2 全绿 + F1 全关` ⇒ `PASS`。三方（人工/模型）都不能凭感觉给 PASS。

---

## 7. 工程品味的落地（`taste/`）

### 7.1 结构

```yaml
# governance/taste/DEC-20260815-UIX-STRUCTURE-ZERO.yaml
id: DEC-20260815-UIX-STRUCTURE-ZERO
statement: 设计稿不得改动原型的区块结构；增删改必须有授权 DEC
scope: [design, D2]
rationale: 结构是产品决策，不是视觉决策；改了就不是同一个产品
enforcedBy: [CRIT-DESIGN-0003]
since: 2026-08-15
evidence: 三轮设计评审中 14 个 P0 有 9 个源于结构私自变更
```

### 7.2 为什么它是"你的"体系

- 判据可以通用，**口径不能通用**。"设计稿是唯一视觉基准""只审不改""结构零改动""不设 P3""统一 fetch 禁 axios"——这些是**你的判断**，不是行业最佳实践。
- 每条 J 类判据必须挂 `tasteRef`，等于强制把"为什么这么要求"存下来。**新宿主、新模型、新人接手，读 `taste/` 就知道这套体系为什么这么长。**
- 这也是自进化的**边界**：模型可以提新判据，但改口径必须你拍板。

### 7.3 新环境 onboarding

换宿主/换模型，第一步只做一件事：**读 `taste/index.yaml` + 当前阶段的 `criteria/<stage>.yaml`**。能不能干活，取决于这两份文件，不取决于宿主生态。

---

## 8. 改造清单（逐文件）

### 8.1 新增

| 文件 | 作用 | 量级 |
|---|---|---|
| `governance/criteria/*.yaml` | 判据库（按阶段） | 首期 60 条 |
| `governance/criteria/index.yaml` | 索引与命中数 | 自动生成 |
| `governance/severity.yaml` | 严重度规则表 | ~60 行 |
| `governance/convergence.yaml` | 收敛器参数 | ~30 行 |
| `governance/taste/*.yaml` | 工程口径台账 | 首期 ~15 条 |
| `checks/runner.py` + `checks/<stage>/*` | 判据执行器 | 首期 12 个脚本 |
| `templates/D1..D4.md` | 四个交付物模板（**小模板，不是代码脚手架**） | 4 份 |
| `shared/convergence-contract.md` | 收敛器契约（single source） | ~80 行 |

### 8.2 修改

| 文件 | 改什么 | 不改什么 |
|---|---|---|
| `shared/gate-policy.md` | 增加"PASS 由判据决定"的引用，不复述细则 | Gate 三值、例外七字段、三轮上限 |
| `shared/skill-contract.md` | 每个 skill 声明 `criteriaMount`（挂哪个阶段） | 权威序、必需章节 |
| `workflow/SKILL.md` | 13 节点 → 4 交付物 + 收敛器引用；205 行 → ≤120 行 | 路由语义、失败回退 |
| 6 个评审 skill | 产出 finding 必须带 `criterion` 候选字段与 `subjectDigest` | 四维评审的内容（那是资产） |
| `scripts/eval/relay.py` | 回流物从"一条用例"扩成"一条判据或显式裁决" | 已有 26/27 回流逻辑 |
| `governance/eval-spec.yaml` | L2 回流口径对齐判据 | 三层分层与可比性锚 |

### 8.3 不动（护城河）

Gate 三值 + 例外七字段 + 三轮上限 · Envelope + preflight 只读 · `contentDigest`/`subjectDigests` · TSR node-start/end + verify · 证据七标签 · 权威序 · 量具自验 · 四维评审的维度定义 · l2Triage 的豁免机制。

---

## 9. 实施：六个阶段

| 阶段 | 做什么 | 工期 | 验收 | 反向对照 | 回滚 | 你审核什么 |
|---|---|---|---|---|---|---|
| **S0 地基** | severity.yaml、convergence.yaml、criteria schema、`checks/runner.py` 骨架、完整性校验 | 1d | 空库能跑通校验；非法判据（缺反例/缺 tasteRef）必须红 | 故意写一条缺 `antiExample` 的判据，必须被拒 | 纯新增 | schema 是否过重/过轻 |
| **S1 首批 60 条** | 从 knowledge-bases + travel-agent + 306 行里迁 60 条（40 M / 15 J / 5 D） | 2d | 每条 M 类能真跑出 finding；每条 J 类挂得上 DEC | 拿一条已知问题，判据必须复现（红） | 单 commit | **判据写得对不对**（这是唯一需要你逐条看的） |
| **S2 执行器** | `tsr stage check`、finding 统一格式、hits 台账 | 2d | 一个阶段一条命令出 findings；台账逐条追加不覆写 | 修好一条，重跑必须转绿 | 纯新增 | finding 够不够"照着能改" |
| **S3 收敛器** | R1'/R2/R4/R6/R7 + 收敛报告 | 2d | 模拟"边审边改"必须被判违规；F1 外新增必须进 backlog | 造一个第 4 轮，必须被挡 | 纯新增 | 预算闸阈值是否太紧 |
| **S4 阶段挂载** | 7 包 = 4 交付物 + 判据挂载；workflow 压到 ≤120 行 | 2d | 进 design 只加载 design 判据；抽 3 个旧 skill 点名仍可执行 | 移除一份 criteria 文件，必须报错而不是静默通过 | 改 sync 一处 | 交付物边界 |
| **S5 飞轮接线** | relay 升级、K1/K2/K3、复发计量 | 1d | 同一判据 fail 两次必须报红升级 | 造一次复发，必须触发 K2 | 纯新增 | 复发口径 |
| **S6 收尾** | 56KB 去重、度量看板、`taste/` 首期 15 条 | 0.5d | 总字符 −56K；四子命令 + 64 用例仍全绿 | 删一个引用目标必须红 | 单 commit | — |

**总计约 10.5 天。** S0/S1 完成即可先让你看效果，不必等全部。

---

## 10. 度量

| 类型 | 指标 | 基线 | 目标 |
|---|---|---|---|
| **主** | 同类问题复发率（按 `CRIT-*` 计） | `recurrence` 6.9%，1 条 3 卡链 | 每季度降半 |
| 覆盖 | 判据数 / M 类占比 / 交付物覆盖 | 0 | 首期 60 条，M ≥60% |
| 收敛 | 交付物评审轮次中位数 / F1 关闭率 / 每轮 P2 新增 | 需求 3、原型 3+、设计 2–3；P2 峰值 93 | ≤2 轮；P2 ≤10 |
| 速度 | 新项目到 D3 的日历天 | 6 天+（未完成） | ≤2 天 |
| 复利 | 每周新增/升级判据数 | 0 | ≥3 |
| **反指标** | 判据 0 命中率 | — | 高即"判据是摆设"，必须查 |
| **反指标** | J 类占比 | — | 上升即"没机械化"，K2 必须生效 |

> 反指标是防自欺的：只看"判据变多"会造假，同时看"0 命中率"和"J 类占比"才骗不了人。

---

## 11. 风险与不做

**不做**：不删 skill / 不删规则 / 不合并能力 · 不动 Gate/Envelope/digest/TSR · 不新增流程节点 · 不加第二个运行时 CLI（复用 `tsr.py` 子命令）· 不做可视化评测台 · 不为让指标好看改闸门。

| 风险 | 缓解 |
|---|---|
| 判据库变成第 N 个没人读的登记表 | **判据是"被执行"的，不是"被阅读"的**：进入阶段就 `stage check`，不靠人记得 |
| 迁移 306 行工作量炸开 | 分批：先两个真实项目，剩下的按阶段滚动；未迁移的保持原样 |
| 判据误报 → 罚合规产物（你们被伤过） | 每条必须带反例 + 反向对照；J 类必须人判；误报立即降级并记账 |
| 收敛器太硬，卡住自主跑 | 预算闸只出报告不硬死；阈值放 `convergence.yaml` 可调 |
| 缺 DEC 导致 J 类入不了库 | 入库时缺 `tasteRef` ⇒ 报红并生成待办，不静默通过 |
| 双源 auto-test | `verify` 开工前先定单一事实源，否则不接判据 |

---

## 12. 待确认（五条）

1. **判据库的归属**：进 `governance/criteria/`（体系级、跨项目复用）——同意吗？还是你想按项目分？
2. **首期 60 条的范围**：只从 knowledge-bases + travel-agent 两个项目迁 + 306 行里最常用的 40 条，够不够？
3. **`taste/` 的粒度**：每条口径要能追溯到一次"你拍板"（DEC）。你现在回忆得起来的口径大概有几条？我按这个数量定首期。
4. **预算闸默认值**：轮次 3 / P2 每轮 10 / 单交付物发现上限 60——是否合适？
5. **D1 的用户确认点**：现在产品域有 4 次以上确认（范围、定位、功能取舍、PRD），压到 1 次会不会太狠？我倾向 **2 次**（范围一次、PRD 一次）。

---

## 13. 口径

实测数字来自 2026-10-17 本仓与 `knowledge-bases`、`travel-agent`：
- 45 个 SKILL.md / 264,644 字符 / 5,881 行；references 688,364 字符（按需，不计入）；
- 重复：合同样板 49,920 + 问题记录块 9,823 + L2 回流块 3,135，净重复约 56,000 字符；
- 评审轮次：`knowledge-bases/.spec/{需求评审,原型评审,设计评审}` 逐文件统计 P0/P1/P2；
- 项目周期：`workflow.yaml` 的 `startedAt`/`updatedAt`/`state`；
- recurrence 6.9% 取自 `tsr recurrence`。
