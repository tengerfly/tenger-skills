---
name: skill-optimizer
description: "Skill 元优化器（长期迭代）。记录 skill 问题、从聊天记录挖掘优化点、按八维优化/精简 skill、对 skill 做七维自洽体检、从 ../../bug-patterns/ 池与评审闭环沉淀提炼错误模式反哺方案/开发/评审 skill。触发：记问题/复盘/挖掘聊天/优化/精简/迭代/体检某 skill、检查自洽一致性、错误池提炼/反哺、沉淀 bug 模式到方案开发、沉淀评审闭环。"
metadata:
  contract-level: legacy-wrapper
  legacy-alias: "Skill-Optimizer"
  compatibility: "Claude Code / Agent SDK / OpenCode"
---


# Skill-Optimizer（Skill 元优化器）

> IRON LAW：每个改动必须可追溯到一条 issue 或核验发现；沉淀必须写明双向落点。凭感觉大改 = 违规。
> 定位：本仓库各专业 Skill 的运维 + 迭代器。只做四件事——记录、挖掘、优化、体检。评审门禁闭环管「这一次交付物」，本 skill 管「每一次都犯的方法论问题」。进化引擎为 **Skill-Evolver**（采集用户偏好/行为习惯 → 偏好库 → 触发进化）：模式②遇偏好类信号、模式③执行优化时**内部调用**它，本 skill 保留标准与调度。

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

**闭环回流（L2）**：P0/P1 条目要标「已沉淀」前，必须先回流 1 条评测用例，并在该用例声明里用 `issueRef` 指回本条问题（值＝本条问题的仓库相对路径，形如 issue/<skill>/<日期>/<NN>-<标题>.md）；没有这条用例就按「未验证」处理，优化状态停在待处理/处理中，不得写「已沉淀」。
判据与字段口径的单一来源是仓库根 `governance/eval-spec.yaml`（`caseTiers.L2` + `issueRef` 节），机械核对由 `scripts/eval/relay.py` 执行；本节只承接义务，不复述其条文。

## 一、模型：双问题池 + 四个模式

| 模式 | 触发 | 做什么 | 产物 |
|---|---|---|---|
| ① 记录 | 记问题/复盘运行 | 问题写入 issue 池 | `../../issue/<skill>/<日期>/<序号>.md` |
| ② 挖掘 | 提供 ../../chats/ 或粘贴聊天 | 提取优化点 | 提取清单 → 确认后落 issue |
| ③ 优化 | 优化/精简/迭代 XX | 按八维优化并沉淀；含从 ../../bug-patterns/ 与**评审闭环沉淀项**提炼 | SKILL.md / references / CONTEXT 改动 |
| ④ 体检 | 体检/检查 XX 自洽 | 七维自洽体检 | 问题清单 → 用户逐条裁决 |

**标准先行**：每模式有固定标准——记录 `../../shared/templates/issue-template.md`、挖掘 `assets/signal-checklist.md`、优化 `assets/optimize-checklist.md`、体检 `assets/self-audit-checklist.md`，编写规范 `assets/skill-writing-standard.md`。执行严格按标准，不凭感觉。

**自我指涉**：本 skill 自身也是优化对象，问题（含五份标准的问题）记 `../../issue/Skill-Optimizer/`；**先优化自己（先修标准再干活），再优化其他 skill**。

## 二、双问题池

**问题池（skill 自身方法论问题，`../../issue/`）**——记录 skill 怎么干活的问题，消费方 = 本 skill 模式③ 优化 skill 自身：

- 路径 `../../issue/`，结构 `../../issue/<skill>/<日期目录>/<序号>-<标题>.md`，序号当日从 01 递增。
- 每文件字段：标题、归属 skill、来源（埋点/挖掘/体检/用户/**评审闭环**）、等级（P0/P1/P2）、标签（10 枚举）、现象、期望 vs 实际、修复方向、**双向落点**（来源=评审闭环时必填：A 产出方 skill / B 评审方 skill）、状态（待处理/处理中/已沉淀/已忽略）、沉淀目标/位置（已沉淀必填）。

> 来源「评审闭环」= 门禁闭环放行后沉淀判定中「当场改不了」的项（成因不明/影响面大/不确定普遍性）；规则见仓库根 `../../shared/anti-deadloop.md` §五。

| 等级 | 含义 |
|---|---|
| P0 | 方法论硬伤/每次必犯/阻塞 |
| P1 | 明显影响/高频 |
| P2 | 轻微/建议 |

标签：触发识别、流程缺陷、边界不清、术语文案、产物格式、接口契约、工具依赖、性能体积、正面参考、反面参考。

状态机：待处理 → 处理中 → 已沉淀（填沉淀目标+位置）或已忽略。

**错误模式池（真实 bug 错误模式，`../../bug-patterns/`）**——记录各被修项目暴露的「会再犯的一类错 + 防复发规则」，消费方 = 方案/开发 skill（经本 skill 模式③ 提炼）：

- 写入方：Bug-Fix 收尾沉淀（有预防价值才沉，用户确认后落池），各项目修复都直接写入本池。
- **位置 = 本 skill 源仓库根集中池**：`../../bug-patterns/<日期>/<序号>-<标题>.md`（仓库根相对写法，可移植；池只此一处，用户在本仓库即可统一提炼，无需去各项目拉取）。模板见 `../bug-fix/assets/pattern-card-template.md`，状态 `待提炼 → 已提炼/已忽略`。
- **安装副本运行时不写源仓**：在宿主 skills 目录或其它项目里运行时，错误模式记录在用户指定的维护目录 / 项目本地（待反馈），经用户确认后再回写源仓本池，不因安装副本改写源仓路径。
- 分工：问题出在「skill 怎么干活」→ `../../issue/`；问题出在「写出的代码/方案有哪类坑」→ `../../bug-patterns/`。池规则详见 `../../bug-patterns/README.md`。

## 三、模式① 记录

1. 先按 `../../shared/problem-recording.md` 定位现有问题与授权范围；已观察事实及时落盘，归属未知标待分诊，不等待根因确认。
2. 记录现象、期望 vs 实际、证据、建议等级/标签、责任与下一步；来源=评审闭环补双向落点候选。
3. 查重后更新或新建源仓 issue；跨仓未授权先保留项目原记录及待反馈索引，不写源仓或安装副本。写后回读核对。
4. 用户确认等级/标签/归属后更新；修复/提炼结果附验证及回退方式，不以写文件成功宣称已优化或已验收。

## 四、模式② 挖掘

1. **输入源优先级（2026-10-18）**：① 项目 `.spec/` 各轮评审/测试问题文档 + `git log`（已蒸馏的全量问题史，首选）→ ② rollout `model-io-*.jsonl`（**仅近段行为证据/错误签名统计**：轮转/压缩会丢历史轮次，且同目录混存其他项目）→ ③ `../../chats/` 手工导出或用户粘贴。运行期日志/监控问题记录（server-log / server-monitor / web-monitor 导出）作为独立第二入口并列。**滚动记录不能当全量问题史**（`../../issue/Skill-Optimizer/2026-09-15/01`）。
2. 扫信号：负面（不对/重来/怎么又/别乱发挥/反复返工/纠正/质疑）、正面（好/就这样/思路对/以后都这样）、返工循环、触发痕迹（哪个 skill 被调起、产出、断在哪步）。
3. 提炼：信号聚合 → 现象 + 期望 vs 实际 + 归属 + 等级 + 标签 + 修复方向；**每条标注证据来源类型**（spec 产物 / rollout 签名 / git 提交 / 用户原话），供后续复核与去重。
4. **分流（2026-09-18）**：用户偏好/行为习惯类信号（稳定偏好的表达与反复修正，判据见 Skill-Evolver §三①）→ **REQUIRED SUB-SKILL**：交 Skill-Evolver ①采集②建模落 `../../evolution/` 池（含「沉淀内容完整展示」硬约束）；方法论问题 → 本池 `../../issue/`。界限不清问「这是用户的稳定偏好吗」。
5. **确认后才落盘**。
6. 写入 `../../issue/<skill>/<日期>/`。

## 五、模式③ 优化

顺序：先优化 Skill-Optimizer 自己（含标准）→ 再优化目标 skill。

**综合分析问题日志**：先定位用户明确授权的项目 `.spec/问题日志.md`，读取相关详情与证据，并核对源仓 `issue/` 和已授权的 `evolution/信号/`。按原 ID 去重，区分项目个例、流程缺陷、代码模式与稳定偏好；提出有依据的改动再在授权范围执行，回填源问题和反哺引用。不得只扫描源仓 issue 而漏掉项目待反馈项，也不默认扫描所有项目。

八维核验（判据：维度二~六 skill-writing-standard、维度八 vibe-principles-mapping）：
① 问题修复——读目标 issue 待处理/处理中逐条修；
② 触发精准——description 覆盖 what + when 与动词/场景/同义表达；**含量化 eval**：生成触发样本（该触发/不该触发/边界）→ 盲测 → 假阳/假阴分析 → ≤5 轮迭代调优；
③ 上下文体积——SKILL.md ≤ 500 行硬红线，长内容下沉 references，可执行代码进 scripts；L1~L4 四级加载见编写规范 §二；
④ 指令写法——问题引导、禁令清单、铁律/Red Flag；
⑤ 流程稳定——BLOCKING/REQUIRED 标记、Gate、交付检查、参数系统；
⑥ 简洁不落俗——删 AI 味套话、冗余；
⑦ 术语一致——对照 CONTEXT.md；
⑧ 心法注入——对照 vibe-principles-mapping 落到执行层。

流程：
1. 读目标 issue 列待修问题；
2. 按 optimize-checklist 八维核验；
3. 只动有依据处；
4. **old-vs-new 能力审计**：改动前记录目标 skill 能力清单，改动后对比——确认无「丢功能 / 引入未声明行为 / 声称支持却没实现」，每项变更可追溯到 ../../issue/核验发现；
5. 在目标 skill 的 CONTEXT.md 追加 D-xx（改了什么、依据哪条 issue）；
6. 回填 issue 状态：解决 → `已沉淀` + 沉淀目标/位置；不处理 → `已忽略` + 理由。

> **进化管线接入（2026-09-18）**：改动依据含「用户偏好/行为习惯」（`../../evolution/` 池信号）或需要读运行轨迹定因时，执行环节走 Skill-Evolver ④诊断⑤方案⑥执行（读轨迹原文、进化建议单、五护栏、确认后改、台账留痕）；本 skill 出八维标准与最终核验，两处留痕都要（CONTEXT D-xx + 进化台账）。

### 改进思路（避免「为几个样例打补丁」）

1. **泛化，不过拟合**：技能要服务成千上万次调用，而你手里只有几个样例。别为样例做微调式改动或堆僵硬 MUST；某个问题反复治不好，换表述 / 换工作方式，往往比继续加字有效。
2. **读 transcript，不只看产出**：产出对不代表过程对——若技能让模型把时间花在无产出的事上，删掉造成那段行为的文字再看结果；删与改一样要复测。
3. **发现重复劳动就固化成脚本**：若多个用例下模型都各自写了同一个辅助脚本（如 `build_chart.py`），说明该把它放进 `scripts/` 并在技能里写明「用它」——一次固化，此后每次调用都省。

### 模式③-附加：错误模式池 + 评审闭环沉淀提炼

优化对象为方案/开发/评审 skill，或用户点名「提炼 bug-patterns / 评审闭环沉淀」时，把待提炼项翻译成目标 skill 的**可执行规则**。两个来源：

**来源一 · `../../bug-patterns/` 集中池**（真实 bug 错误模式）：

1. 读 `../../bug-patterns/` 待提炼案例（本仓库根，一处即可），按受益 skill 归类，清单交用户确认（提炼哪几条、落哪层）。
2. 按**层级升级**落点：目标 skill「常见错误对照表」加行 → 高频/跨案例模式沉淀 references 防复发清单（如 `frontend-error-patterns-guide.md`，命名对齐该 skill 惯例）→ 重大模式进方案 skill 的 Gate/预检项。
3. 提炼=给目标 skill 加「可执行的防复发检查项」，不是贴案例（案例卡仍在池里可溯源）；粒度=一类问题。
4. 改后在目标 skill CONTEXT.md 记 D-xx；回填案例卡状态 `已提炼`（落点 + 位置）；不提炼 → `已忽略` + 理由。

**来源二 · `../../issue/` 池中来源=评审闭环的待处理项**（门禁闭环沉淀，**双向**）：

1. 读待处理项，按其「双向落点」落到两端：
   - 方向 A → 产出方 skill 的防复发规则（错误表加行 / references 清单 / Gate 预检项）；
   - 方向 B → 发现问题的那一个评审 skill 的 `references/known-issue-patterns.md` 加一条（模式 / 典型现象 / **检出方法** / 来源）——下次评审对照检查，同类再现即判为问题。
2. 两端各自记 CONTEXT D-xx；回填 issue 状态 `已沉淀` + 沉淀目标/位置（A、B 都要填）。
3. 判定「无普遍性」→ `已忽略` + 理由。

> 为什么双向：只改产出方 → 下次不做错但评审查不出；只改评审方 → 查得出但产出方照犯。两端齐备才形成正向循环（定义见 `../../shared/anti-deadloop.md` §五）。

## 六、模式④ 体检

按 `assets/self-audit-checklist.md` 七维：
① 术语/命名一致（同指异名、与 CONTEXT 冲突、旧术语残留）；
② 逻辑闭环（悬空引用、断头、Gate 未落地、枚举数量前后不一致）；
③ 文句质量（病句、错别字、占位符未替换）；
④ 声明-流程一致（声明的依赖/前置有对应检测→阻塞→报错步骤）；
⑤ 跨位置同步（关键事实/编号/引用多文件 grep 比对）；
⑥ 简洁不落俗；
⑦ 安全审计（危险指令/硬编码凭据/依赖/外联风险，带脚本的 skill 重点查）。

范围（默认）：目标 skill 全套文件 + 全仓交叉引用（根 README/WorkFlow/其他 skill/issue）。

流程：定位（显式路径 / 当前目录 / 名称匹配三方式）→ 按七维机械 grep + AI 通读 → **先列 ≥2 条「做得好」（引用具体位置，禁填充式恭维）** → 问题清单（等级+位置+现象+修复方向+判据）→ **逐条交用户裁决**（当场修→记 D-xx；记 issue→来源填体检；忽略→说明）→ 小结确认。

> 先列优点不是客套：写清「哪条做法在起作用」，才能保证后续修改不把它改坏。体检者自身的元反模式（不给含糊赞美 / 不给过度工程建议 / 不把有意省略当缺失）见 `assets/self-audit-checklist.md`。

## 七、沉淀约定（全局强约束）

1. **粒度 = 一类问题**：沉淀类别级通用判据/检查项/防复发规则，不是单点案例；单点只作附注。自问能否防「这一类」再犯。
2. **双向 = 一个问题的两端**：门禁闭环沉淀必须同时给 **A 产出方 skill**（防复发）与 **B 评审 skill**（检出力 · `references/known-issue-patterns.md`）；只沉一端算未完成。P0 双向必沉。
3. **落点 = 经确认的源仓与授权范围**：沉淀先核对真实源仓位置；业务项目执行不隐含修改源仓、外部知识库或安装副本的授权。缺权限保留本地待反馈记录。只有用户明确要求同步生效副本时才确认目标、比较差异并校验 hash；不默认使用历史硬编码路径、覆盖用户改动或外发问题池。
4. **模板**：评审方案例库结构用 `../../shared/templates/known-issue-patterns-template.md`；issue 字段用 `../../shared/templates/issue-template.md`。
5. **外部参考吸收留痕**：吸收外部 skill 仓库（如 sanyuan-skills）时，**采纳与不采纳**的做法都记入 `assets/skill-writing-standard.md` §七（含理由），防后续重复讨论；吸收点按「标准层 → 元技能层 → 具体 skill 层」逐层落地，逐层记 D-xx。
6. **落点分层（2026-09-16）**：用户要求「沉淀成标准流程 / 后续都按此执行 / 提高质量」时，改动必须落到目标 skill **主流程强制位**（SKILL.md 步骤内 REQUIRED/Gate/错误表行），案例库/references 只作承载正文的附件并在主流程标注引用点；仅落案例库 = 未完成。用户只要「记录下来」时才允许纯案例库落点。判据：问一句「下次不读这篇参考是否就会照旧做错」——是则必须进主流程。

## 八、铁律

1. **标准先行**：先加载对应标准逐项执行；标准缺失/有问题先修标准。
2. **改动有依据**：每个改动可追溯一条 issue 或核验发现，不凭空重构。
3. **先己后人**：先优化 Skill-Optimizer 自己（含标准）。
4. **沉淀留痕**：每次改动在目标 skill CONTEXT.md 记 D-xx。
5. **字段必填**：等级、标签、状态三字段；来源=评审闭环时另必填双向落点。
6. **确认后落盘**：挖掘清单未经用户确认不落盘。
7. **零加戏**：只处理确认过的问题与发现，不擅自重写风格/增删功能。
8. **沉淀双向**：门禁闭环问题先查两端（A 防复发 + B 检出力），单端沉淀不算完成。

## 九、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 凭感觉大改无依据 | 每个改动回溯 ../../issue/体检发现 |
| 跳过自优化 | 先优化自己 |
| 不写决策日志 | 追加 D-xx |
| 挖掘未确认就落盘 | 先列清单确认 |
| 问题缺三字段 | 必填 |
| 已沉淀不填目标/位置 | 必须可追溯 |
| 体检只口头说 | 按七维出清单，每条带位置/方向/判据 |
| 当场修没记 D-x | 留痕 |
| 改完不同步检查 | 旧词/编号/术语全仓清零 |
| 提炼把案例整段贴进 skill | 只提炼可执行防复发规则，案例留 bug-patterns 池 |
| 提炼无用户确认 | 先列清单（哪几条、落哪层）确认 |
| 提炼后不回填案例卡 | 状态 `已提炼` + 落点/位置 |
| 错把 bug-patterns 当 issue | 归 skill 自身问题走 ../../issue/；归代码坑走 ../../bug-patterns/ |
| 评审闭环沉淀只改一端 | 双向：A 产出方防复发 + B 评审方案例库（known-issue-patterns.md） |
| 案例库只贴案例不给检出方法 | 每条必写「检出方法」可执行判据 |

## 十、资源清单

- `../../shared/templates/issue-template.md`、`signal-checklist.md`、`skill-writing-standard.md`、`vibe-principles-mapping.md`、`optimize-checklist.md`、`self-audit-checklist.md`
- `../../shared/instrumentation-guide.md`
- `../../shared/templates/known-issue-patterns-template.md`（仓库根）：评审方案例库模板
- `../../issue/`：skill 自身问题池（源仓库根，含来源=评审闭环项）；`../../bug-patterns/`：错误模式集中池（源仓库根，池规则 `../../bug-patterns/README.md`、案例卡模板 `../bug-fix/assets/pattern-card-template.md`）；`../../evolution/`：用户偏好与进化信号池（源仓库根，Skill-Evolver 维护）；`../../chats/`：待挖掘目录
- 关联：`Skill-Evolver`（进化引擎——模式②偏好信号采集、模式③进化管线执行时内部调用）；`OSS-Radar`（外部情报输出口，反哺经本 skill 模式③）

## 十一、运行问题埋点

收尾按 `../../shared/instrumentation-guide.md` 自查上报 `../../issue/Skill-Optimizer/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `../../shared/templates/issue-template.md`）。归因未明先留事实，按共享记录规则处理；不为经验提炼阻塞主流程。

## Contract Compatibility Layer

Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.


> LEGACY BODY BOUNDARY: The preceding body, references, and assets are retained for capability compatibility. When any wording conflicts, the contracts in `../../shared/` and the sections below win.

## Purpose

Preserve the mature capability of `Skill-Optimizer` while exposing it through the v2 Skill contract.

## Trigger

Run when the user explicitly requests this capability or when `WorkFlow/` routes a compatible stage to this wrapper.

## Inputs

- the user's request and confirmed scope;
- current project artifacts, evidence, decisions, and `.spec/workflow.yaml`;
- the retained legacy body, references, assets, and scripts in this directory.

## Preconditions

- read `../../shared/skill-contract.md`, `../../shared/gate-policy.md`, and `../../shared/anti-deadloop.md`;
- read `.spec/manifest.yaml` and `.spec/workflow.yaml` when a project is available;
- verify scope, authorization, repository boundaries, and required upstream artifacts;
- do not overwrite unrelated or uncommitted files.

## Responsibilities

- execute the retained domain capability within its stated scope;
- translate legacy outputs into the current artifact, evidence, decision, and Gate vocabulary;
- record execution, traceability, residual issues, and the next action;
- route work outside this wrapper to the responsible domain Skill.

## Non-goals

- do not silently change product decisions, scope, or acceptance criteria;
- do not invent missing facts, evidence, approvals, or test results;
- do not use legacy Gate values or legacy state files as current truth;
- do not delete retained compatibility material.

## Procedure

1. Read the request, current state, manifest, and upstream handoff.
2. Load only the retained legacy resources needed for this execution.
3. Execute the domain action and keep assumptions separate from evidence.
4. Validate the output against its repair or acceptance criteria.
5. Register artifacts, evidence, decisions, and open items.
6. Write the execution record and `.spec/workflow.yaml`.
7. Emit exactly one Gate and one explicit next action.

## Outputs

- the domain artifact, report, code change, test evidence, or routed task defined by the retained capability;
- `artifactRefs`, `evidenceRefs`, `decisionRefs`, `openItems`, `gate`, and `nextAction`;
- a failure route when the wrapper cannot complete safely.

## Evidence

Use direct source files, command output, test results, screenshots, dated external sources, or explicit user decisions. Label conclusions as `FACT`, `EVIDENCE`, `INFERENCE`, `ASSUMPTION`, `RECOMMENDATION`, `DECISION`, or `OPEN`. A recommendation is not approval.

## Gate

Use only `PASS`, `CONDITIONAL`, or `BLOCKED`. `PASS` requires complete inputs and artifacts with no unresolved P0/P1. Residual P0 is always `BLOCKED`. Residual P1 is never `PASS` and may be `CONDITIONAL` only with `exceptionId`, `risk`, `owner`, `dueAt`, `remediation`, `allowDownstream`, and `approvalRef`. Three review rounds are the maximum; never force-pass or start an automatic fourth round.

## Failure Route

If evidence, authorization, scope, or an upstream Gate is missing, set `BLOCKED`, name the missing item and owner, and route to the responsible upstream Skill. If the issue is outside this wrapper's boundary, stop and route it rather than improvising.

## Downstream Contract

Downstream Skills may consume only manifest entries whose status and Gate allow downstream use. They must read `sourceRefs`, `evidenceRefs`, `decisionRefs`, `openItems`, and `nextAction`; they must not infer approval from chat context or file existence.

## State Changes

Record the old state, new state, actor, timestamp, reason, evidence references, Gate, and next action in `.spec/workflow.yaml`. The exact state names come from `governance/state-registry.yaml`.
