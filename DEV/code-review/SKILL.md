---
name: code-review
description: "代码评审（后端 + 前端，支持分端单批评审）。对照 PRD AC、原型、TDD、FTDD 核查后端/前端代码，重点为接口契约一致性（路径/方法/入参/出参/错误码/分页/枚举/共享类型单一源）与可运行性（install/tsc/build/test/lint），兼查架构、代码质量、安全数据、六大闭环、性能与边界、删除候选与清理计划。前端批次固定并行 Fidelity-Review 做页面还原度审查，问题合并同一清单。不做业务逻辑正确性评审。只审不改：P0 附建议补丁进报告、不落盘源码；产出后端/前端评审、汇总、任务清单至 `.spec/代码评审/`。防死循环：判据 + P0/P1 冻结 + 复核只验本轮 + 轮次上限 3（超限后 P0 残留 BLOCKED；P1 残留只能经授权 CONDITIONAL，不得 PASS。触发：评审/检测/审查/走查代码、检查前后端联调、清理死代码。"
metadata:
  contract-level: legacy-wrapper
  legacy-alias: "Code-Review"
  compatibility: "Claude Code / Agent SDK / OpenCode"
---

> **独立调用**：先按 `../../shared/execution-profiles.md` 判强度，按 `../../shared/requirements-context.md` 取相关需求。低风险局部任务不要求完整上游文档/Envelope，只执行本领域相关动作并记录真实证据；下文正式建档用于标准/完整。专业检查的必需工具、只审不改边界、相关阻塞和安全授权不降级，不把局部验证冒充全量或正式 Gate。


# 代码评审 Skill

> IRON LAW：**只审不改**——问题进清单，改动归产出方，评审时改源码 = 违规。
> 头号目标：接口契约对不上。问题定位到 `文件:行`，结论可追溯 AC / 接口。
> 术语：TDD = 后端技术文档；FTDD = 前端技术文档；AC = PRD 验收标准编号（`AC-Mxx-nnn`）。
> 分端两批：⑬-后（只审后端）与 ⑬-前（只审前端，前端视角 ∥ Fidelity-Review）；单批只出对应角色文档。

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## 一、定位与铁律

**角色**：代码评审专家（立场隔离的双视角 + 契约专项）。**不做**业务逻辑正确性评审（是否算对、边界是否判对，归测试流程）；测试闭环只查「可运行 + 先行 + 标 AC」，不评业务覆盖是否充分。**不做**（交并行方）：页面视觉/交互还原 → `Fidelity-Review`（⑬-前 并行），本 skill 不重复评审、不代出还原度结论。

**铁律**：

1. **只审不改**：不改源码；P0 补丁只进报告。改代码归 Backend-Dev / Frontend-Dev，经任务清单交接；删除候选只出计划不代删。
2. **定位到代码**：每条标文件 / 行 / 接口 / 字段，引用关键片段。
3. **零幻觉**：结论基于代码与四类文档；区分「缺失（该写没写）」与「越界（写了不该写的）」。
4. **视角隔离 + 独立上下文**：各视角独立评审、独立上下文，互不可见，不参考生成过程；契约归因到责任方。
5. **不设门禁**：只出问题清单，不判通过/不通过；放行由 Workflow 按 `../../shared/anti-deadloop.md` 判定。
6. **不评业务逻辑**：业务正确性归测试流程；页面还原度归并行方 Fidelity-Review。
7. **成因必写**：写清为何产生（如后端改字段未同步共享类型）；推不出标「成因未明」，禁臆造。
8. **沉淀只改方法论**：沉淀动作只加产出方 skill 的防复发规则，不改对方框架、不改被审产物。

**两条强制收尾口径**：

- **零问题也必须说明覆盖边界**：检查了什么 / 没查什么（如未验迁移脚本、未做端到端）/ 残余风险，禁一句「无问题」收尾。
- **取证口径**：未运行验证不得声明通过，不得采信子 agent 的成功汇报（见仓库根 `../../shared/evidence-before-claims.md`）。

## 二、输入与前置

| 输入 | 角色 | 说明 |
|---|---|---|
| PRD（AC） | 需求基线 | 判断代码漏做 / 凭空 |
| 原型 HTML | 结构基线 | 前端**结构**还原（结构基线 = 低保真原型，见 `../../shared/baseline-terms.md`）；**不作视觉基准** |
| 设计稿 | **视觉主基准** | 有则以 `.spec/设计稿/` + `design-system.md` 为视觉唯一应然（含 token 对账）；无则视觉值从原型收敛并明示降级。⑬-前 并行还原度审查的基准 |
| TDD / FTDD | 设计基线 | 后端表结构·接口·模块边界 / 前端页面·组件·fetch + 契约源 |
| 后端代码 + 前端代码 + `libs/shared` | 被审对象 | 实际落地工程 |

- 优先读 `.spec/` 已有产出（PRD 先读 `PRD速查表.md` 建索引、原型、`.spec/TDD/VN/`、`.spec/FTDD/VN/`、代码工程目录）；缺失回退用户指定路径或粘贴。
- 代码与文档不同仓时：以 TDD「接口清单」+ FTDD「fetch 对接表」为契约中介做三方比对。
- **批次裁剪**：⑬-后 只收后端代码 + TDD + FTDD（fetch 清单）；⑬-前 只收前端代码 + FTDD + 设计稿/原型。
- **大批量分批**：代码量过大（变更 >500 行或跨服务多模块）→ 先按模块 / 功能域汇总范围，再逐批评审、逐批出清单，禁一次性粗扫；混合关注点按功能分组，不按文件顺序切。

**视角分工（立场隔离）**：

| 视角 | 标准 | 检查 | 不检查 |
|---|---|---|---|
| 后端代码评审 | 对齐 TDD 接口/表结构且内部一致 | 接口实现、数据模型、四层分层、微服务边界、异常/事务/并发 | 前端页面/组件/交互 |
| 前端代码评审 | 对齐 FTDD fetch/原型且内部一致 | api 方法、hooks、组件抽离、还原度、三态、渲染性能 | 数据库、服务端实现 |
| 接口契约一致性 | 前后端接口与共享类型三方一致 | 路径/方法/入参个数与类型/出参字段/错误码/分页/枚举 | 业务逻辑正确性 |

契约命中项归因：前端调了后端没实现的接口 → 后端；后端字段前端没消费 → 前端；两端字段名不一致 → 双方。⑬-后 只跑「后端视角 + 契约专项（后端侧）」；⑬-前 跑「前端视角 + 契约专项（前端侧）」并在 ⑬-前 收口完整三方比对。

## 三、主流程（9 步）

```
输入 → 解析 → 静态验证 → 视角评审（⑬-前 与 Fidelity-Review 并行）→ 删除候选与清理计划 → 契约专项
→ 角色文档 → 汇总 → 任务清单 + 用户确认 → 闭环复核 + 双向沉淀 → 归档
```

1. **输入解析**：定位本批次代码与 `libs/shared`、四类文档；抽取 AC 清单、TDD 接口清单、FTDD fetch 表、原型布局清单；代码量大按「大批量分批」先汇总范围。**〔REQUIRED · 开工前闸门核对〕**逐条读 `.spec/manifest.yaml` 中本批所依据上游（PRD／原型／TDD／FTDD）的 `status`、`version`、`gate`、`allowDownstream`：任一 `SUPERSEDED`／非 `PASS`／`false` ⇒ **不在作废基线上继续评审**，把关闸事实写入汇总 §0「上游闸门核对」表并交回 Workflow 判停（本 skill 不设门禁，见铁律 5，故只报事实、不自判放行）；限定条件只能落字段、不得写注释或正文（`../../shared/gate-policy.md` §6）。
2. **静态验证（取证）**：本批次代码 `pnpm install → tsc --noEmit（或 build）→ test → lint`；跑不了 → 降级静态读码并在报告标「未取证（原因）」。只证伪可编译 / 可测试 / 可 lint，不做端到端冒烟（规程见 §4.4）。
3. **视角评审**：后端批次按 `references/backend-checklist.md`、前端批次按 `references/frontend-checklist.md`（A~N 组）逐条执行；独立产出断点清单，独立上下文（subagent / 新会话）互不可见，不参考代码生成过程；条件允许可用不同模型交叉审查。另对照 `references/known-issue-patterns.md`（评审方案例库）逐条过一遍，命中即入本批次清单。
   **⑬-前 并行还原度**：同时启用 `Fidelity-Review`（代码评审场景模式）做页面还原度审查，两侧并行、互不可见；Fidelity-Review 按自身清单出问题（含截图），**问题合并进本批次清单**（标「来源=Fidelity-Review」）。
4. **删除候选与清理计划**：按两清单 M 组扫描死代码 / 未用依赖 / 重复实现 / 调试残留，按 `references/removal-plan-template.md` 分列「现在可安全删」与「需延后（前置条件 / 迁移 / 验证 / 回滚）」，落 `.spec/代码评审/删除候选与清理计划.md`；**只给计划不代删**。
5. **契约专项**：按 `references/contract-checklist.md` 做前端 fetch ↔ 后端实现 ↔ 共享类型三方比对，逐接口核对；命中项按 §二 归因。
6. **角色文档落盘**：按 `assets/role-review-template.md` 写本批次角色文档至 `.spec/代码评审/`；P0 按 `assets/patch-template.md` 附建议补丁（仅代码块，不落盘源码）。
7. **汇总**：按 `../../shared/problem-recording.md` 将本批次清单及问题 ID/范围登记至项目 `.spec/问题日志.md`；Code-Review 负责合并 Fidelity-Review 结果后的唯一索引，复核同步状态，主方中断时保留待合并引用。按 `assets/summary-template.md` 合并去重（⑬-前 含 Fidelity-Review 并行结果），重点标「前后端契约错误」，按 P0/P1/P2 统计；**零问题也要写清覆盖边界**（见 §一）。
8. **任务清单 + 用户确认**：按 `assets/issue-list-template.md` 生成任务清单，状态 `待确认`，按归因填修改方（Backend-Dev / Frontend-Dev / 双方）；每条附**修复判据**；逐条请用户确认（要改 → `已确认`；不改 → `已忽略` + 理由）；P0/P1 阻断、P2 可留后续；确认后交对应 Dev skill 修改并回填状态。
9. **闭环复核 + 双向沉淀判定**：修改方回填 `已修复` 后只验本轮 `已确认` 项；新发现降 P2；同批满 3 轮不收敛：P0 残留保持 BLOCKED；P1 残留不得 PASS，只能经授权并登记例外后 CONDITIONAL；不自动开启第 4 轮

> 防评审死循环三招、门禁闭环放行判据与任务清单状态机的定义见仓库根 `../../shared/anti-deadloop.md`，本 skill 只保留流程参数，不重复定义。

## 四、评审规范

> 正文只留判据；细则按需加载对应 references。

**4.1.0 资产与契约检查（外部 AI 知识库，后端/前端通用）**：① 组合契约——组合图（composition.yaml）的 requires/provides/ordering 与实现一致，无绕过统一契约的写法；② Pattern 不变量——命中资产的 Invariants/禁止事项逐条成立；③ 零复制分叉——无 `xxx-full-copy` 式整体复制；④ 零静默发明——未命中资产的关键规则不得擅自发明（须走封装七步法或标注待确认）；⑤ 使用与版本——asset-usage 记录的实际版本与 asset-selection 锁定一致；⑥ **零冗余并列**——未检索 / 未适配即新建与库内既有资产并列重复的组件（防冗余硬性条件：近似资产应兼容适配或走「更新既有」出口，新建须 asset-gap 差异说明）。违反任一记 P1；绕过统一契约、复制分叉、冗余并列记 P0。组件库位置：`D:\project\agent-project\skills-knowledge\asset-library\`（调度侧引用层与映射表：仓库根 `../../skill-knowledge/`）。

**4.1 六大闭环（代码层）**：

| 闭环 | 含义 | 典型断点 |
|---|---|---|
| 需求 | 每条 AC 有代码承接 + 测试标注 AC | AC 漏实现；无来源实现；测试未标 AC |
| 流程 | 业务入口→出口代码贯通 | 只创建不查询；只走成功路径；事件无消费 |
| 状态 | 状态机初态/终态/合法流转 | 缺终态；无触发方；状态枚举两端各写 |
| 数据 | 字段产生→传输→消费一致 | 字段未消费/未定义；分页/枚举/时间格式不一致 |
| 异常 | 定义→抛出→捕获→反馈→可恢复 | 空 catch；错误码未分段；缺空/错/加载态；事务未回滚 |
| 测试 | 先行、可运行、标 AC | 先实现后补测试；测试跑不通；无 AC 编号 |

**4.2 六项正确性**：

1. **可运行性**：install → `tsc --noEmit`（或 build）→ test → lint（见 `references/static-verification-guide.md`）。
2. **架构合规**：后端四层单向依赖 / 微服务边界；前端 `pages→components→hooks→api`、组件抽离。
3. **接口契约一致**：路径/方法/入参/出参/错误码/分页/枚举/字段术语双向 + 共享类型单一源。
4. **代码质量**：单一职责、无魔法值、注释讲 why + 传参必注、统一响应、配置外置、无密钥硬编码。
5. **安全与数据**：入参校验、鉴权、注入 / XSS / SSRF / 越权、金额整数分、事务 / 幂等 / 并发竞态。
6. **可维护性（删除候选）**：死代码 / 未用依赖 / 重复实现 / 调试残留 → 区分「现在可安全删」与「需延后（出计划）」。

**4.3 严重度分级（只标注，不设门禁）**——P0/P1/P2 定义与处理口径见仓库根 `../../shared/anti-deadloop.md` §三，下表为本域典型示例：

| 级别 | 含义 | 典型 |
|---|---|---|
| P0 | 契约对不上无法联调；无法编译/启动；共享类型被绕过；可利用的安全漏洞 | 入参个数不符；字段名/类型不一致；tsc 报错；拼接 SQL；越权可读他人数据 |
| P1 | 契约字段命名不一致但类型兼容、错误码缺失、三态缺失、架构越层、测试跑不通、竞态隐患、N+1 | 缺错误态/空态；跨层调用；test 失败；check-then-act；循环内单条查询 |
| P2 | 命名不统一、注释缺失/冗余、魔法值、死代码/未用依赖、非关键细节 | 中英混用；裸字符串散落；未引用导出 |

**4.4 静态验证规程**：目标 = 证伪可编译 / 可测试 / 可 lint，不证业务正确性；本批次代码跑，结果记入对应角色文档；跑不了 → 降级读码并标「本项未取证（原因：{{原因}}）」——**未取证 ≠ 通过**。

## 五、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 评审时改源码 | 只记问题，补丁进报告 |
| 两视角混写 | 分视角成文，汇总合并 |
| 单批漏出对应角色文档 | ⑬-后 出后端、⑬-前 出前端 |
| ⑬-前 漏挂还原度审查 | 固定并行 Fidelity-Review，问题合并同一清单 |
| 重复评还原度结论 | 视觉/交互还原归 Fidelity-Review |
| 漏契约专项 | 步骤 5 逐接口三方比对 |
| 漏删除候选 | 步骤 4 按 M 组扫描并出清理计划 |
| 大代码量一次性粗扫 | 先按模块汇总再分批评审 |
| 无问题只写「无问题」 | 写清检查范围 / 未覆盖项 / 残余风险 |
| 评业务逻辑 | 归测试流程 |
| 验证跑不了写「通过」 | 标「未取证」 |
| 无出处 | 定位到文件:行/接口/字段 |
| 越界当缺失 | 区分两类分别标注 |
| 无成因 | 补成因，可考才写 |
| 闭环后不沉淀 | 步骤 9 沉淀判定，P0 必沉 |

## 六、资源清单

- `references/backend-checklist.md` / `frontend-checklist.md`：双视角清单（A~N 组，每组附提问式引导）
- `references/contract-checklist.md`：契约一致性清单（核心）
- `references/static-verification-guide.md`：静态验证规程
- `references/removal-plan-template.md`：删除候选与清理计划模板（安全删 vs 延后删）
- `references/known-issue-patterns.md`：评审方案例库（闭环沉淀的已知问题模式 + 检出方法）
- `references/case-library/`：审查方法学（优先级 / 评论规范 / AI 边界）+ 同行样本（按需加载）
- `assets/role-review-template.md` / `summary-template.md` / `patch-template.md` / `issue-list-template.md`
- `../../shared/anti-deadloop.md`、`../../shared/evidence-before-claims.md`（仓库根）：公共约定
- 并行方 `Fidelity-Review`（⑬-前 页面还原度审查）
- `.spec/代码评审/`：归档目录

## 七、运行问题埋点

收尾按 `../../shared/instrumentation-guide.md` 自查上报 `../../issue/Code-Review/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `../../shared/templates/issue-template.md`）。归因未明先留事实，按共享记录规则处理；不为经验提炼阻塞主流程。

## Contract Compatibility Layer

下方正式状态/manifest/Gate 写入步骤适用于标准/完整交接；轻量独立任务按共享执行强度使用同一任务摘要，不执行正式状态写入、不伪造批准。

Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.


> LEGACY BODY BOUNDARY: The preceding body, references, and assets are retained for capability compatibility. When any wording conflicts, the contracts in `../../shared/` and the sections below win.

## Purpose

Preserve the mature capability of `Code-Review` while exposing it through the v2 Skill contract.

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
