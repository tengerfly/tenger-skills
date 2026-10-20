# 业务项目的 `.spec/` 控制文件没按 v2 契约模板建，导致 Gate 从未被机械校验过

> 归属 skill：`WorkFlow`（编排器 / 正式交接建档）＋ `shared/` 契约层 ｜ 日期：2026-10-10 ｜ 来源：体检（Skill-Optimizer 模式③ 八维核验④「声明-流程一致」⑤「跨位置同步」实测暴露）

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P0 |
| 标签 | `产物格式` / `接口契约` / `工具依赖` / `流程缺陷` |
| 优化状态 | 已沉淀（2026-10-10 **规则层**落地：建档结构 + 量具可达前置 + 状态词收编；**项目侧 8 步迁移未执行**——业务项目改动需单独授权；「编排器在不可解析项目上是否真停下」亦未经 fresh 复跑验证） |

> 定级理由：不是排版问题。`shared/gate-policy.md` §2 把「upstream Gates are present」列为 PASS 前提、§6（本轮新增）要求开工前读闸门字段，而**这些前提的机械检出者是 `scripts/validate_core.py`**；该项目控制文件直接解析失败 ⇒ 闸门规则对该项目一条都没被机械判过。同批两条 issue（`WorkFlow/2026-10-10/01`、`UI-UX-Review/2026-10-10/01`）描述的是「有规则没人执行」，本条描述的是**「连执行规则的量具都没接上」**——不修则 §6 只能靠执行方自觉，同根因第四次复发可预期。

## 现象

2026-10-10 落地闸门规则时，对真实项目 `knowledge-bases` 实跑校验器：

```
$ python scripts/validate_core.py gate --project-root D:/project/agent-project/knowledge-bases
cannot parse YAML D:\...\knowledge-bases\.spec\manifest.yaml: duplicate YAML key: 'sourceRefs'
workflow has invalid gate: None
gate validation failed: 2 error(s)
```

核对契约与模板后确认，**两份控制文件都是 v1 语义装进 v2 文件名**：

| 项 | 契约 / 模板要求 | 项目实况 | 偏差计数 |
|---|---|---|---|
| `manifest.yaml` 根结构 | 顶层 `projectId` + `artifacts:`（`shared/templates/project-manifest.yaml`） | 外面多包一层 `manifest:`，内含 `project` | 结构性不符 |
| 条目主键 | `artifactId` | `id` | `artifactId` 出现 **0** 次，`- id:` **24** 条 |
| 必填字段 | `lifecycle`、`owner`、`producedAt`（`governance/schemas/artifact-manifest.schema.yaml` `requiredArtifactFields`） | 三条全无 | 24/24 缺 |
| `status` 枚举 | `DRAFT / REVIEW / APPROVED / SUPERSEDED` | 写成 `REGISTERED`（5）、`READY`（6）、`APPROVED_SUPERSEDED`（2） | 13 条在枚举外 |
| `sourceRefs` | 一个映射内一个键 | 同一映射内重复键 → **YAML 解析直接失败** | ≥1 处 |
| `workflow.yaml` | 顶层 `state` / `gate` / `allowDownstream`（`shared/templates/workflow.yaml`、`shared/artifact-contract.md` §5） | 外面多包 `workflow:`，用 `currentState`，顶层无 `gate` | 校验器报 `workflow has invalid gate: None` |

同一天该项目恰好命中闸门失守（见 `01` 篇：13:57 登记 `allowDownstream: false`，14:52 编排仍排 FTDD）。**若校验器当时可解析，`APPROVED_SUPERSEDED`（枚举外值）与 `gate: None` 会当场报错**——机械门禁这条线从来没接上。

顺带确认（正面参考）：项目侧在 15:2x 已把 `currentState` 从 `TDD_CONSISTENCY_UNVERIFIED` 回退为 `PRD_REVIEW_IN_PROGRESS`，并在行内注释引用了上游第 2 轮的 `gate: BLOCKED / allowDownstream: false / round: 2/3`——说明人读得懂闸门字段，缺的是建档规范与机械检出。

## 期望 vs 实际

- **期望**：标准/完整流程建 `.spec/` 时按 `shared/templates/workflow.yaml` 与 `project-manifest.yaml` 落盘；每次正式交接前，`validate_core.py`（或 `validate.ps1`）对该项目**可解析并给出结论**；不可解析即 `WORKFLOW_BLOCKED`，不得一边写着 v2 契约一边用 v1 结构继续推进正式交接。
- **实际**：控制文件由 skill 正文里的口头字段名（`currentState`、`status: READY`）自然长成 v1 形状，全仓无一步要求「校验器读得通」；`gate`/`allowDownstream` 的执法完全依赖执行 Agent 自觉，`01`/`02` 两条 issue 的现象由此得以发生。

## 根因（已确认）

1. **建档步骤无模板锚点**：`workflow/SKILL.md` §1 只说「创建或更新 `.spec/workflow.yaml` 和执行记录」，未指向 `shared/templates/*.yaml`，也未要求落盘后过校验器。`project-onboarding` / 各评审 skill 的产物模板同理。
2. **状态词表双轨**：`REGISTERED`/`READY`/`APPROVED_SUPERSEDED` 是被各 skill 正文养出来的「业务状态词」，与 `artifact-contract.md` §2 的批准状态枚举语义重叠但不同名；`APPROVED_SUPERSEDED` 尤其危险——它同时宣称「批准」与「已作废」，而下游只看得到前半句。
3. **无「量具可达」前置闸**：仓内已有 12 个 `validate-*.ps1` 与 6 个 fixture，但没有任何主流程步骤把它们接到真实项目的交接路径上；fixture 全绿不代表业务项目可校验（本次实测即如此）。

## 修复方向（本条只登记，改哪些文件待用户在源仓裁决）

1. **主流程加 REQUIRED（A 方向主修）**：`workflow/SKILL.md` §1 与 §4 之间补一步——标准/完整流程首次建 `.spec/` 必须复制 `shared/templates/workflow.yaml` + `project-manifest.yaml` 结构，字段名与枚举以 `governance/schemas/*.schema.yaml` 为准；**每次正式交接前跑 `python scripts/validate_core.py gate --project-root <项目>` 与 `artifact --project-root <项目>`（业务项目用这两条；`system` 仅适用于本仓自检——它还要项目内另有 `governance/` 与 `.spec/traceability.yaml`，对外部项目会报无关红），解析失败或字段非法即停 `WORKFLOW_BLOCKED`，不得继续正式交接**。
2. **业务状态词收编**：`shared/baseline-terms.md` 或 `artifact-contract.md` §2 加一张映射表，明确 `REGISTERED`/`READY`/`APPROVED_SUPERSEDED` 一律不得写入 `status`（各自的正确落点：批准状态 vs 评审轮次 vs `supersedes` 字段），防换形复发。
3. **模板承接位**：各评审/产出 skill 的产物模板凡涉及 `.spec/` 登记，统一引用上述两份 yaml，不再各自简写。
4. **项目侧迁移（需单独授权，不在本轮）**：`knowledge-bases/.spec/` 对齐 v2 的动作清单——
   1. `manifest.yaml`：去掉 `manifest:` 包裹 → 顶层 `projectId: knowledge-bases` + `artifacts:`；`id:` → `artifactId:`；保留 `domain`/`version`/`consumedBy`（校验器只查必填、不拒额外字段）；
   2. 补 `lifecycle`/`owner`/`producedAt`：取值须从该产物自身的批准记录、评审报告或文件 mtime 取证，**取不到就标「待用户裁决」，禁止臆造时间戳**；
   3. `status` 逐条映射（语义判级，**不得批量替换**）：`REGISTERED`→`DRAFT` 或 `REVIEW`（视是否已有评审记录）；`READY`→`REVIEW`/`APPROVED`（须有对应批准 DEC 才可 `APPROVED`）；`APPROVED_SUPERSEDED`→`SUPERSEDED`，批准历史改由 `decisionRefs` + `supersedes` 承载；把「已批准」读回来的风险全在这一步；
   4. 合并同一映射内重复的 `sourceRefs` 键；并按 §2（本轮新规则）把各下游产物的上游基线 id 补进 `sourceRefs`；
   5. `workflow.yaml`：去掉 `workflow:` 包裹，`currentState` → `state`，补顶层 `gate` / `allowDownstream` / `reason` / `nextAction`；
   6. 验收：业务项目跑 `validate_core.py gate` + `artifact` 两项可解析（`system` 留本仓自检；已实测：对合成项目 `system` 会额外报 `governance/state-registry.yaml`、`traceability.yaml`、`shared/templates/task-envelope.yaml` 缺失共 10 条无关红）；
   7. **如实上报第一次机械判出的结果**：对齐后该项目很可能立刻冒出若干 `BLOCKED`（例如 13 条枚举外状态背后的批准记录缺失），这是暴露真实状态，不是迁移失败；
   8. 回退：迁移前对 `.spec/` 做一次带时间戳的副本（或单独一次 commit），只回退结构不回退结论。

## 跟踪与证据

- 原问题 ID / 来源项目：本仓直接建档，稳定标识 = `issue/WorkFlow/2026-10-10/02`；相关项目 `knowledge-bases`（`.spec/manifest.yaml`、`.spec/workflow.yaml`）
- 发现时间 / 相关步骤：2026-10-10 16:0x，Skill-Optimizer 模式③ 落地 `shared/gate-policy.md` §6 时的验收实测；步骤=正式交接建档与 Gate 校验
- 脱敏证据：上方命令与三行输出原文；计数由 `grep -c` 得出（`artifactId` 0 次、`- id:` 24 条、`REGISTERED` 5、`READY` 6、`APPROVED_SUPERSEDED` 2、`sourceRefs` 13 行含重复键）；契约口径见 `governance/schemas/artifact-manifest.schema.yaml`、`shared/templates/project-manifest.yaml`、`shared/templates/workflow.yaml`
- 责任方 / 下一动作 / 修复判据：`WorkFlow` + `shared/`（规则）；用户单独授权后由业务项目侧执行迁移 4-1~4-8。判据＝① 对该项目跑 `validate_core.py gate` 与 `artifact`，从「cannot parse YAML」变为可解析并给出错误/通过清单；② **已实测的阳性对照**：合成项目 `s2-superseded`（下游 `sourceRefs` 绑 `SUPERSEDED` 基线）→ `artifact` 报 `TDD-20261010-001 is built on a superseded baseline via sourceRefs: PRD-20261009-001`；对照组 `s1-blocked`（无作废基线）→ 通过，不虚报
- 根因与归属：已确认（建档无模板锚点 + 状态词双轨 + 无「量具可达」前置闸）；归属 `WorkFlow` 主流程与 `shared/` 契约层，**非某个业务项目的个例脏数据**
- 复核证据 / 未验证项：**未验证**——本条为静态取证，未跑第 4 项迁移、未起 fresh 会话复测「编排器在不可解析项目上是否真的停下」；本轮 §6 规则落地后也尚未经历一次真实「上游关闸」场景复跑
- 回退方式：规则改动单列一次提交（`shared/gate-policy.md` §6 与 `artifact-contract.md` §2 属同族闸门规则，可与本条修复分开）；项目侧迁移按 4-8 副本回退

## 双向落点

| 方向 | 目标 | 落点 |
|---|---|---|
| A · 防复发 | `WorkFlow`（主流程）+ `shared/artifact-contract.md` | §1/§4 之间 REQUIRED「按模板建档 + 交接前校验器必须可解析，否则停 `WORKFLOW_BLOCKED`」；`status` 业务词收编映射表 |
| B · 检出力 | `Skill-Optimizer`（编排器无上游评审方，按 `issue/README.md` 出口②收敛） | `Other/skill-optimizer/references/known-issue-patterns.md` **模式 5 检出方法④**「量具可达性核查：对项目实跑 `validate_core.py gate`，解析失败即判 Gate 从未被机械校验」——本轮已落（见 `01` 篇双向落点同一处） |

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | A · 防复发：`WorkFlow`（建档结构与交接前置）+ `shared/artifact-contract.md`（状态词收编）；B · 检出力：`Skill-Optimizer` 案例库模式 5 检出方法④；另对称补齐 4 个评审节点的开工前闸门核对 |
| 沉淀位置 | `workflow/SKILL.md` §1「标准/完整」步新增〔REQUIRED · 建档结构与量具可达〕（模板锚点 + `validate_core.py system` 必须可解析，否则停 `WORKFLOW_BLOCKED`）——记 `workflow/CONTEXT.md` **D-25**；`shared/artifact-contract.md` §2 新增「Status vocabulary」映射（`REGISTERED`→`DRAFT`、`READY`→`REVIEW`/`APPROVED`、`APPROVED_SUPERSEDED`→`SUPERSEDED`，轮次归 Gate 记录）；对称补齐——`shared/templates/review-summary-template.md` 新增 **§0**，`tech-review` **D-10**／`code-review` **D-17**／`prd-review` **D-12**／`prototype-review` **D-09** 各加同一 REQUIRED 并挂 §0 指针（汇总记 `Skill-Optimizer` **D-41**）；B——`Other/skill-optimizer/references/known-issue-patterns.md` 模式 5 方法④（**D-40**） |
| 忽略理由 | 不适用 |

> **仍未收口（如实记录）**：本条「修复方向 4」的项目侧 8 步迁移（`knowledge-bases/.spec/` 对齐 v2 schema）**未执行**——业务项目文件改动需用户单独授权；且迁移后第一次机械判出的结果可能立刻暴露新的 `BLOCKED`，属暴露真实状态而非迁移失败。另：`fidelity-review` 按公共模板「单报告无需汇总」口径未挂 §0，其基线有效性依赖 Code-Review／auto-test 的核对覆盖，**该覆盖是否足够尚未验证**。
