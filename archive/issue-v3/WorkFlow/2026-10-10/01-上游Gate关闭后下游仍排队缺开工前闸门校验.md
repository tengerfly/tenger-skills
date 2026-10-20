# 上游 Gate 关闭后下游仍继续排队：体系缺「开工前强制读上游闸门」这一步

> 归属 skill：`WorkFlow`（编排器 / 生命周期闸门执法）｜ 日期：2026-10-10 ｜ 来源：用户（业务项目 `knowledge-bases` 现场追问）

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P0 |
| 标签 | `流程缺陷` / `接口契约` / `产物格式` |
| 优化状态 | 已沉淀（2026-10-10 源仓规则层落地；**尚未经真实「上游关闸」场景 fresh 会话复跑验证**，见「修复方向」上方新增 issue `02` 的量具缺口） |

> 定级理由：不是个例返工，而是**闸门模型有字段、无执法者**——`shared/gate-policy.md` §2 把「upstream Gates are present」写成 PASS 前提、§3 写「`allowDownstream: false` 即使记了 Gate 也挡下游」，但没有任何一步在**启动下游节点前**去读这两个字段。同一天内在同一项目命中两次（见「现象」），且下游产物已成沉没成本，属方法论硬伤。

## 现象

项目 `knowledge-bases`，2026-10-10 实测时间线（文件 mtime 取证）：

| 时刻 | 事件 | 上游闸门 |
|---|---|---|
| 10-09 | PRD v0.2 用户批准 + `REQ-REVIEW-20261009-001` gate PASS | 开 ✅ |
| 10-10 03:03–04:47 | 设计稿第一轮返工（31 任务）；04:45 设计评审第二轮复核 | v0.2 基线，合法 |
| 10-10 05:28 / 08:00 | OSS-Radar 后端调研 / **TDD V1** 产出 | v0.2 基线，合法 |
| **10-10 10:53** | `DEC-20261010-PRODUCT-DIRECTION` 方向重定 → PRD v0.2 转 `APPROVED_SUPERSEDED` | ⚠ 基线作废 |
| 10-10 12:27 | PRD v0.3 评审第 1 轮 `gate: BLOCKED` | **关** |
| 10-10 13:57 | PRD v0.3.2 + 评审第 2 轮 `gate: BLOCKED`、**`allowDownstream: false # 不放行 prototype-design`**、`round: 2/3`、`nextAction: 第 3 轮复核` | **关（已显式登记）** |
| 10-10 14:52 | 编排器仍在推进下游：`workflow.yaml.currentState = TDD_CONSISTENCY_UNVERIFIED`、`nextAction` 排「补 TDD 三件事 → FTDD」；`ui-ux-review` 第三轮在作废基线上收口 | 未读闸门 ❌ |

两处失守：

1. **编排指针与闸门相反**：上游 13:57 已记 `allowDownstream: false`，`currentState` 与 `nextAction` 却停在技术阶段并继续往 FTDD 排——等于默认「下游先往前赶，上游慢慢补」。
2. **基线作废后无人回头清点**：10:53 作废 v0.2 基线时，已建在其上的 05:28 OSS 调研与 08:00 TDD V1 没有被自动标废，TDD V1 事后判「回炉重写」——产出沉没。

用户追问原文（要点）：「PRD 有问题要回头修 PRD 时，也应该坚持 PRD 完成之后再走下一步……现在是这样吗」。核对结论：**规则本身是对的（且已写明），执行没有做到**——缺的是执法步骤，不是缺规则文本。

## 根因

1. **闸门是数据不是检查点**：`gate` / `allowDownstream` 只存在于 `manifest.yaml`、`workflow.yaml` 和各评审报告的执行记录里；`WorkFlow` 主流程没有「调度任一节点前，先读其上游 artifact 的 `gate` + `allowDownstream`，非 `PASS`/`true` 即拒绝开工并把 `nextAction` 指回上游 owner」这一 REQUIRED 步骤。是否遵守全凭执行 Agent 自觉。
2. **下游产物不绑定基线指纹**：产物只写「依据 PRD」（如 `设计稿/README.md:14` 记「PRD v0.2 APPROVED」），没有 `baselineRef`（上游 artifact id + 版本 + sha256）。上游被覆盖式改写（v0.2 → v0.3.2 直接改同名文件，v0.2 正文无版本化副本，仅 `archive/*.yaml` 存 REQ/AC 索引）后，下游不会自动失效，也无人被提醒重判。
3. **`currentState` 可被下游节点单方面推进**：技术阶段节点把状态写成 TDD 语境，没有任何约束要求「存在 `allowDownstream: false` 的上游时，状态机必须停在最上游的阻塞点」。

## 期望 vs 实际

- **期望**：任一上游 Gate 为 `BLOCKED` 或 `allowDownstream: false` 时，其全部下游节点一律不可开工；编排状态停在最上游阻塞点并命名 owner/清除条件；上游基线变更时，依赖它的产物自动标 `STALE` 并触发重判。
- **实际**：闸门写在字段里没人读，编排指针停在下游阶段继续排队；旧基线产物照常交付并在同日收了尾（见同批 issue `UI-UX-Review/2026-10-10/01`）。

## 修复方向（本轮未改任何 skill 规则，仅登记；以下建议待用户在源仓裁决）

1. **加硬闸（主修）**：在 `WorkFlow` 主流程「调度专业 skill 之前」插入 REQUIRED 步骤——读目标节点在上游 `manifest.yaml` 对应 artifact 的 `gate` + `allowDownstream` + `blockedBy`；任一不满足即：不启动该节点、`nextAction` 指回上游 owner、在 `workflow.yaml.blockedItems` 记 `BLK-*`（含 `clearCondition`）。规则文本落点建议 `shared/gate-policy.md`（补一节「Gate enforcement」）+ `shared/lifecycle-contract.md`，`WorkFlow/SKILL.md` 主流程引用。
2. **状态机不得越过未清阻塞**：`currentState` 更新前校验「是否存在 `allowDownstream: false` 的上游 artifact」，有则拒绝前移，只能写 `*_WAITING_UPSTREAM` 类状态。
3. **基线指纹**：`shared/artifact-contract.md` 的产物登记字段增 `baselineRef: {artifactId, version, sha256}`；`manifest.yaml` 的上游条目状态转 `SUPERSEDED` 时，把所有引用它的产物标 `STALE`（可由 `scripts/` 下校验器机械检出，接入 `validate-reference-integrity.ps1` 同族门禁）。
4. **基线作废即触发沉没产出清点**：方向类 DEC（`DEC-*-PRODUCT-DIRECTION`）落盘时，REQUIRED 输出「受影响下游产物清单 + 各自处置（回炉/增量/作废）」，不得等到下游节点自己发现。

## 跟踪与证据

- 原问题 ID：`BLK-GATE-ORDER-01`（`knowledge-bases/.spec/workflow.yaml` `blockedItems`）；关联 `BLK-DESIGN-01`、`DEF-TDD-01`
- 发现时间 / 相关步骤：2026-10-10 15:0x，`ui-ux-review` 第三轮收口后被用户追问暴露；步骤=编排调度（节点启动前置检查）
- 脱敏证据：上表 mtime 时间线；`knowledge-bases/.spec/需求评审/PRD-20261010-评审-第2轮.md` 执行记录（`round: 2/3`、`allowDownstream: false`）；`.spec/manifest.yaml` `PRD-20261009.status=APPROVED_SUPERSEDED`、`PRD-20261010.gate=BLOCKED`；项目索引行见 `knowledge-bases/.spec/问题日志.md`（2026-10-10 第三轮行）
- 责任方 / 下一动作 / 修复判据：`WorkFlow`（源仓规则由用户在其 skill 项目内落地）；判据=构造「上游 `allowDownstream: false`」场景时，编排器必须拒绝启动下游并回写 `blockedItems`，且 `currentState` 不前移
- 根因与归属：**已确认**（缺执法步骤 + 缺基线绑定），归属 `WorkFlow` 与 `shared/` 契约层
- 复核证据 / 未验证项：本轮只做事实登记，未改 skill、未跑验收；修复后需 fresh 会话复测
- 回退方式：新增闸门前后可对同一场景跑两次（旧规则放行 / 新规则拒绝）作正反对照；规则文本改动单列一次提交便于 revert

## 双向落点

| 方向 | 目标 | 落点 |
|---|---|---|
| A · 防复发 | `WorkFlow` + `shared/gate-policy.md` / `lifecycle-contract.md` / `artifact-contract.md` | 主流程 REQUIRED「开工前读上游闸门」；`currentState` 前移校验；产物 `baselineRef` + SUPERSEDED → STALE 传播 |
| B · 检出力 | 编排器无上游评审方 → 按 `issue/README.md` 收敛约定落 `Other/Skill-Optimizer/references/known-issue-patterns.md`（由模式④体检检出） | 新增模式「**闸门失守 / 基线漂移未清点**」；检出方法：① 取 `manifest.yaml` 全部 `gate != PASS` 或 `allowDownstream: false` 的 artifact，与 `workflow.yaml.currentState`、`nextAction` 指向的阶段比对，下游阶段指针 + 上游关闸 = 命中；② 对每个下游产物 grep 其声明的上游版本，与上游 artifact 当前 `version` 比对；③ 比 DEC/PRD 版本行 mtime 与下游产物 mtime |

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | A · 防复发：`WorkFlow` + `shared/` 契约层；B · 检出力：`Skill-Optimizer`（编排器无上游评审方，按 `issue/README.md` 出口②收敛） |
| 沉淀位置 | `workflow/SKILL.md` §4 新增两步 REQUIRED（开工前闸门核对 / 基线作废即清点沉没产出）+ `Responsibilities`、`Non-goals` 各补 1 行——`workflow/CONTEXT.md` **D-24**；`shared/gate-policy.md` 新增 **§6 Gate enforcement**（规则 1–5）；`shared/artifact-contract.md` §2 新增「Baseline binding」（用已有 `sourceRefs`，未新增 `baselineRef` 字段）；B——`Other/skill-optimizer/references/known-issue-patterns.md` **模式 5**（四条检出方法）＋ `Other/skill-optimizer/CONTEXT.md` **D-40** |
| 忽略理由 | 不适用 |

> 与原「修复方向」的两处偏离（已在 D-24 记因）：① 不新增 `*_WAITING_UPSTREAM` 状态——改用已注册的 `WORKFLOW_BLOCKED` + 「状态停在阻塞点不前移」，避免改状态注册表与全部转移边而收益重叠；② 不新增 `baselineRef{artifactId,version,sha256}`——`scripts/validate_core.py:386` 已有「非 `BLOCKED` 的 Gate 引用 `DRAFT`/`SUPERSEDED` 记录即报错」的判据，缺的只是没人把上游 id 写进 `sourceRefs`；用现有字段可让既有量具直接长出牙齿，且零 schema 变更（**落地时自纠**：`validate_core.py:386` 那条判据实际只覆盖 Gate 记录的 `evidenceRefs`/`decisionRefs`，**不查产物 `sourceRefs`**——「量具本就有牙齿」这句原断言不成立。已在 `scripts/validate_core.py` `check_artifact` 补上该判据（`status != SUPERSEDED` 的产物以 `sourceRefs` 指向 `SUPERSEDED` 上游、又未在 `supersedes` 声明取代关系 ⇒ 报 `is built on a superseded baseline`），并加带对照组的单测 `test_sourceRefs_binding_rejects_superseded_baseline`；字段仍零新增，但机械检出属本轮新补，记 `workflow/CONTEXT.md` D-24 ③）。
>
> **本轮新暴露的前置缺口**：实跑校验器发现该项目控制文件根本不被 v2 契约接受（解析失败、`gate: None`），即**上述所有闸门规则对该项目从未被机械校验过**——已另登 `issue/WorkFlow/2026-10-10/02`（P0），其修复是本条规则执法从「靠自觉」转为「有检出者」的必要条件。
