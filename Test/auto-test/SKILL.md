---
name: auto-test
description: "AI 代码全景验收测试编排与修复闭环（分层 L0-L4）。AI 编码完成后的自动化验收：确定性门禁（install/typecheck/lint/单测/build）→ API 契约与 live 主链 → AI 视觉 E2E（状态注入 + mock 数据全流程覆盖）→ 探索性测试 → 专项压测（负载/压力/稳定）、安全扫描、兼容/无障碍（按需求信号触发）；产出带证据的测试报告、覆盖率门禁与修复任务卡，驱动「发现问题→AI 修复→fresh-agent 回归」正向循环。触发：测试 AI 写的代码、验收、跑全流程、回归、找 bug、E2E、修复后复测、覆盖率检查、压测、负载测试、性能测试、安全扫描。"
metadata:
  contract-level: legacy-wrapper
  legacy-alias: null
  compatibility: "ZCode / Claude Code 等 coding agent。需要 Bash；L2 需浏览器工具（Playwright/Midscene 任一）；auto-test 引擎 CLI 或 MCP 可用时自动切换引擎模式。"
---

> **独立调用**：先按 `../../shared/execution-profiles.md` 判强度，按 `../../shared/requirements-context.md` 取相关需求。低风险局部任务不要求完整上游文档/Envelope，只执行本领域相关动作并记录真实证据；下文正式建档用于标准/完整。专业检查的必需工具、只审不改边界、相关阻塞和安全授权不降级，不把局部验证冒充全量或正式 Gate。


# Auto-Test：AI 代码验收测试与修复闭环

> **Iron Law：证据先于声明，永远。** 没有本次实测证据（命令输出 / 截图 / 实测耗时），禁止宣称「通过 / 已修复 / 没问题」。
> **Iron Law 2：分层短路。** L0 未过不跑 L1，L1 未过不跑 L2——错误越晚发现代价越高，AI token 只花在确定性检查之后。
> **Iron Law 3：真实优先，mock 兜底。** 被测项目已支持真实 AI/外部服务时，默认打**真实链路**；仅当接口不通、无凭证、服务不可用时才降级 mock，且必须在报告「覆盖边界声明」中逐条列出降级项。把项目核心 AI 链路整体 mock 掉 = 核心功能零覆盖。

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## 唯一测试入口

本 Skill 是工作流内验收、回归、探索性和专项测试的唯一执行入口；历史 Testing/testing 请求重定向到这里，不运行第二套备用流程。testing-workflow 仅是领域注册 ID，内部只调用 auto-test。

自动化包括脚本、测试框架、API 断言与浏览器工具驱动的交互/视觉检查；会话模式同样要实际调用工具，不是人工勾选清单或静态读代码冒充运行测试。L0–L4 按项目形态与风险选适用层，未测/不适用/通过分开报告；缺浏览器、凭证、环境或预期基准时明确阻塞/降级，不回退 Testing。开发阶段单元测试仍可自测，正式验收证据由本入口汇总。

按 `../../shared/workflow-visibility.md` 展示当前层、工具/命令、已测/未测、阻塞与下一步。运行真实外部链路前确认本次授权、数据隔离和副作用；真实优先不授予付费、生产写入或通知权限。

## 一、定位与边界

**角色**：验收测试编排者。把「AI 说写好了」变成「机器证明能用」：分层测试 → 证据报告 → 修复任务卡 → 回归闭环。

| 本 skill 负责 | 不负责（归谁） |
|---|---|
| 分层执行测试、收集证据、判定通过与否 | 写代码修复（回归时交编码 agent） |
| 生成用例库（可重复执行的资产） | 改需求 / 写 PRD（基准来源方） |
| 生成修复任务卡并驱动回归循环 | 代码质量评审（归 Code-Review 类 skill） |
| 状态覆盖率与门禁判定 | 单测编写（开发自测；缺测时本 skill 登记风险并按需补关键层） |

**基准来源**：对错基准 = PRD 验收标准（AC）/ 需求文档；视觉基准 = 设计稿（缺失回退原型并**明示降级**）；接口基准 = 接口文档 / OpenAPI 契约。**零臆断**：预期必须有来源，拿不准标 `【设计假设】` 并登记风险。

## 二、模式探测（每次开工第一步）

1. **引擎模式**：`auto-test` CLI 在 PATH 或 MCP 工具（如 `auto-test run / get_report`）可用 → 全部执行委托引擎，本 skill 只负责：解释报告、生成/消化修复任务卡、把握回归轮次纪律。
2. **会话模式**（引擎未部署时的完整降级）：由当前 agent 按第三节流程亲自执行，产物格式与引擎模式完全一致（`.spec/auto-test/`），保证未来无缝迁移。

判定方法：`command -v auto-test`；或检查 MCP 工具列表。两种模式都走同一套铁律与产物规范。

## 三、主流程（7 步）

> 先计划后执行，禁边测边想。◉ = 强制暂停等用户确认。

1. **输入解析**：项目位置 + 启动命令（先读 README/脚本/CI，仍无法确定再问，不猜命令）；读 PRD/需求文档提取验收标准与**状态机**（无状态机则按页面清单盘点，并登记「无状态机基准」风险）；读上轮 `.spec/auto-test/` 产物（有则进入回归模式，只跑上轮失败 + 全量冒烟）。
2. **L0 确定性门禁**（秒~分钟级，零 token）：install → typecheck → lint → 单元测试 → build。任一失败**立即停止**，输出失败证据与修复任务卡，不进入 L1。
3. **L1 契约冒烟**（分钟级）：按接口清单对关键路径做请求级断言（状态码 / 结构 / 关键字段）。失败即停。
4. **◉ 计划确认**：呈现用例清单（编号 + 覆盖的状态/迁移 + mock 方案 + 慢接口阈值），确认后放行。回归模式跳过此步。
5. **L2 视觉 E2E**：按三段式用例（`setup 注入 → act 操作 → assert 断言`）逐条执行；全状态 + 全点击 + 三态必测（加载/空/错误）；样式问题与异常**必截图**；监听 console 报错与网络（慢接口必记：>1000ms 慢 / >3000ms 很慢 / >5000ms 严重）；**有设计稿时（`.spec/设计稿/`）内嵌 `Fidelity-Review`（还原场景模式）做 UI 还原度检查**——其轻量问题清单并入本轮报告，视觉以设计稿为唯一应然（双基准术语见仓库根 `../../shared/baseline-terms.md`）；无设计稿才回退原型并明示降级。细则见 [references/layered-testing-guide.md](references/layered-testing-guide.md)，用例编写见 [references/case-authoring-guide.md](references/case-authoring-guide.md)。
6. **L3 探索性测试（可选）**：无预设脚本自由探索找 bug（乱点乱填、非常规路径）；沙箱内执行；只出报告不阻断。被测系统含不可控外部副作用（发邮件/支付）时必须先 mock。
7. **L4 专项测试（信号触发，可选）**：默认不跑；命中需求信号才执行——性能/并发关键词 → 负载/压力/稳定（负载模型与指标见 [references/specialty-testing-guide.md](references/specialty-testing-guide.md)）；敏感数据/对外接口 → 安全扫描（依赖审计 + SAST 快扫，DAST 可选）；多端/多浏览器 → 兼容矩阵；无障碍要求 → axe 扫描。结果只分级报告，P0（如压测下数据损坏/错误率爆表）才阻断。
8. **汇总与门禁**：计算状态覆盖率 / 迁移覆盖率 / 元素点击率（见 [references/coverage-gate.md](references/coverage-gate.md)）；L4 有执行则附专项指标表；产出报告（[assets/report-template.md](assets/report-template.md)）+ 每条缺陷一张修复任务卡（[assets/bug-card-template.md](assets/bug-card-template.md)），归档 `.spec/auto-test/`。**问题索引**：按 `../../shared/problem-recording.md`，失败在下一安全节点先记事实，汇总/复测后以原 BUG ID（P3 用报告锚点）更新项目 `.spec/问题日志.md`，详情不重复复制。

## 四、修复闭环（本 skill 的灵魂）

```
报告全绿 → 结束
报告有缺陷 → 生成修复任务卡 → 交编码 agent 修复（fresh：不带本轮测试上下文）
          → 回归：重跑全量用例（不是只跑失败项）→ 全绿结束 / 计数+1 继续
          → 轮次上限 3 轮 → 超限停下，升级人工，输出震荡分析（哪两个缺陷在互相打架）
```

**fresh-agent 回归纪律**（防「AI 测 AI」互相糊弄）：
- 回归执行者不得携带上轮的怀疑点、推测结论、修复意见——只给它：原始验收标准 + 用例库 + 当前代码；
- 确定性层（L0/L1）的失败，任何 AI 判断**无权覆盖**；
- 每轮回归都是新的一轮完整证据，禁止沿用上轮截图/结论。

## 五、产物与目录约定

```
.spec/auto-test/
├── 用例库/                 # 可重复执行的资产（三段式 YAML/MD）
│   ├── TC-<模块>-<序号>.md
│   └── 状态机清单.md        # 状态×迁移×用例映射（覆盖率计算依据）
├── 报告/
│   └── run-<日期>-<轮次>.md  # 含覆盖率表 + 缺陷明细 + 覆盖边界声明
├── 任务卡/
│   └── BUG-<日期>-<序号>.md  # 机器可读、AI 可执行的修复任务
└── evidence/
    ├── screenshots/         # <页面>_<问题>_<序号>.png
    ├── console/  network/   # console 日志与 HAR
    └── videos/              # 失败用例录屏（可选）
```

**覆盖边界声明（强制）**：零缺陷也必须写清——覆盖了什么 / 未覆盖什么 / 残余风险。禁只写「未发现问题」。

## 六、缺陷分级与处置（P0-P3 + Action）

| 级别 | 定义 | Action |
|---|---|---|
| **P0** | 崩溃/白屏/核心流程不可用/数据丢失风险/安全漏洞 | 阻断交付，立即生成任务卡修复 |
| **P1** | 功能错误/主要样式偏差/很慢及以上接口/验收闭环缺失 | 应修，本轮闭环内修复 |
| **P2** | 次要样式/文案/体验问题/慢接口 | 建任务卡，本轮或跟进修 |
| **P3** | 建议/风格 | 记录不建卡 |

每条缺陷 = 现象 + 复现步骤 + 期望/实际 + 证据 + 关联用例号。格式见 [assets/bug-card-template.md](assets/bug-card-template.md)。

## 七、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 没跑 L0 直接开浏览器测 | 分层短路，Iron Law 2 |
| 只测主流程，状态靠「应该能到」 | 状态注入构造前置，见 case-authoring-guide |
| mock 了被测系统自己的接口 | Mock 边界铁律：只 mock 外部依赖与异常态 |
| 轮询断言字段凭想象写（如假定 shots[].status 存在） | 断言结构先验证：先 GET 一次看真实响应，再写轮询条件 |
| 重试风暴：短间隔连发重试后拿旧失败证据判死 | 异步任务重试间隔 ≥ 单任务典型时长 1/5；判死只认「新于上次重试」的证据（时间戳/计数） |
| 多项目共用同一 LLM key 并发互打 429 | 探测到 429 → 各项目测试串行化，或显著降速 |
| 重启服务后立即回归 | **验证进程真的换了**：端口确已释放再启动、健康检查通过、最好有代码级标志位；后台任务停止会遗留孤儿进程（实测两次假回归根因） |
| 状态全绿就宣布通过 | **产物级证据**：成功状态之外核验物理产物（文件存在/大小/ffprobe 体检）——实测曾「ALL-PASS」实为旧代码的脏数据补完 |
| 共享库（libs dist）改了只重启一个消费进程 | 构建产物被多进程消费时全部重启，否则新旧代码混跑 |
| 缺陷无截图/无复现步骤 | 证据先于声明，不合格重出 |
| 修复后只跑上次失败的用例 | 全量回归，防「改 A 坏 B」 |
| 复用时沿用上轮结论 | 每轮 fresh 证据，禁沿用 |
| 零问题只写「未发现问题」 | 覆盖边界声明，强制 |
| 「should pass / 大概没问题」 | Gate：说出证明命令 → 跑 → 读输出 → 才能声明 |
| E2E 堆到最多、单测为零 | 反冰淇淋反模式：E2E 只覆盖关键链路 |
| 用例跑两遍覆盖路径不一样 | 用例是资产，固化为可重复执行的文件 |

## 八、资源清单（按需加载，禁一次全读）

| 文件 | 何时读 |
|---|---|
| [references/layered-testing-guide.md](references/layered-testing-guide.md) | 执行 L0-L3 前：各层命令模板、浏览器工具降级链、监听规范、live 主链 E2E 规范 |
| [references/case-authoring-guide.md](references/case-authoring-guide.md) | 编写用例前：三段式格式、状态注入手法、mock 边界铁律 |
| [references/coverage-gate.md](references/coverage-gate.md) | 汇总阶段：覆盖率计算与门禁阈值 |
| [references/fix-loop-guide.md](references/fix-loop-guide.md) | 进入修复闭环时：任务卡投喂方式、fresh-agent 规则、轮次状态机 |
| [references/specialty-testing-guide.md](references/specialty-testing-guide.md) | 命中 L4 信号时：负载/压力/稳定模型、指标阈值、安全扫描、兼容/无障碍 |
| [assets/case-template.md](assets/case-template.md) | 写用例时的模板 |
| [assets/bug-card-template.md](assets/bug-card-template.md) | 出缺陷时的任务卡模板 |
| [assets/report-template.md](assets/report-template.md) | 汇总时的报告模板 |
| 仓库根 `../../shared/baseline-terms.md` / `browser-policy.md` / `evidence-before-claims.md` / `anti-deadloop.md` | 双基准术语 / 浏览器两级策略 / 取证口径 / 门禁闭环与轮次上限（对应环节按需加载） |

**兄弟 skill**：`Fidelity-Review`（L2 内嵌还原检查）、`Bug-Fix`（可运行性问题转其「定位→方案→开发→回归」诊断修复闭环）、`Code-Review`（静态评审互补——本 skill 管运行时验收与证据）。

**沉淀机制**：每次翻车（漏测/误判/flaky）沉淀一条到第七节对照表或对应 reference；checklist 从 5-6 条起步，只增不改。

## 九、运行问题埋点

收尾按 `../../Other/Skill-Optimizer/references/instrumentation-guide.md` 自查上报 `../../issue/auto-test/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `../../Other/Skill-Optimizer/assets/issue-template.md`）。归因未明先留事实，按共享记录规则处理；不为经验提炼阻塞主流程。

## Contract Compatibility Layer

下方正式状态/manifest/Gate 写入步骤适用于标准/完整交接；轻量独立任务按共享执行强度使用同一任务摘要，不执行正式状态写入、不伪造批准。

Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.


> LEGACY BODY BOUNDARY: The preceding body, references, and assets are retained for capability compatibility. When any wording conflicts, the contracts in `../../shared/` and the sections below win.

## Purpose

Preserve the mature capability of `null` while exposing it through the v2 Skill contract.

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
