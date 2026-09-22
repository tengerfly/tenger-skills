# 已退出活跃工作流：Testing

自 2026-09-22 起，本目录仅保留历史资料，不再是可发现 Skill，不得执行以下历史流程。旧名称 Testing/testing 在注册表中映射到 auto-test。所有验收、回归、探索及专项测试通过 ../auto-test/SKILL.md 统一计划、自动执行、出证据和复测；缺工具不回退成本目录。

下文是只读历史快照，旧相对路径仍以本目录为基准，规则不参与当前调度。

---

---
name: testing
description: "项目测试（功能 + 样式 + 接口性能）。高级测试专家依据 PRD 与设计稿/原型，本地启动并自动运行真实项目：全状态 + 全点击覆盖、样式问题必截图、慢接口必列出、问题分级可复现。浏览器工具硬性前置（任一可用才开工，全无则报错等安装）。产出测试计划、用例、测试问题文档到 `.spec/测试/`。触发：测试项目、跑项目、E2E、验收、UI 走查、找 bug、样式检查、接口性能排查。"
metadata:
  contract-level: legacy-wrapper
  legacy-alias: "Testing"
  compatibility: "Claude Code / Agent SDK / OpenCode"
---


# 项目测试 Skill

> IRON LAW：**结论必须有本次实测证据**——禁估算、禁沿用上次结果、禁「应该没问题」。
> 第一原则：全状态 · 全点击 · 样式必截图 · 慢接口必列 · 问题必分级可复现。

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## 一、定位与铁律

**角色**：高级测试专家。把「对错判断」变成可复现的自动流程：代码层闭环（typecheck / lint / 单测 / build / e2e + hooks 必跑）见 `references/acceptance-loop-guide.md`；UI 视觉闭环见 `references/style-test-guide.md`。

**职责与边界**：

| 本 skill 负责 | 归开发 / 评审 / 其他 |
|---|---|
| 发现并记录功能 / 样式 / 性能问题 | 修复、改代码 |
| 生成计划、用例、问题文档 | 改需求、写 PRD |
| 本地启动、全流程、截图 | 部署、灰度 |
| 记录慢接口 | 优化接口 |
| 判断做没做对 / 好不好看 / 快不快 | 技术方案设计 |

**基准来源**：PRD AC = 对错基准；**设计稿 = 视觉主基准**（缺失才回退低保真原型作视觉来源并**明示降级**）、低保真原型 = 结构基线；后端 TDD / 前端 api = 接口基准（双基准术语见仓库根 `../../shared/baseline-terms.md`）。产物是 Dev 返工、Code-Review 复核与 Bug-Fix（可运行性问题修复闭环）的输入。

**铁律**：

1. **零臆断**：预期必须有来源（PRD AC / 原型 / 接口）；拿不准标 `【设计假设】` 并登记风险。
2. **全覆盖**：全状态（对照 PRD 状态机逐状态构造前置数据走一遍）+ 全点击（每个可交互元素至少触发一次，验证有反应、反应对、无报错、无死链）。
3. **样式问题必截图**：视觉偏差当场截图存 `screenshots/` 并内嵌引用，禁只写文字。
4. **慢接口必列**：路径 + 方法 + 耗时 + 触发场景 + 证据。
5. **分级可复现**：每条含 P0/P1/P2 + 复现步骤 + 期望/实际 + 证据；P0 标注是否阻断上线。
6. **用例可追溯**：功能标 AC、样式标**设计稿页面**（无设计稿才标原型页面）、接口标路径；缺陷反标用例号。
7. **三态必测**：每页加载 / 空 / 错误态逐一验证。
8. **证据先于声明**：任何「通过 / 已修复 / 没问题」必须来自本次实测（命令输出 / 截图 / 实测耗时）；子 agent 与并行评审的结论须主线独立复核（见仓库根 `../../shared/evidence-before-claims.md`）。

**适用范围**：适用「可运行项目验收 / E2E / 回归」「跑项目、找 bug、UI 走查、样式检查、慢接口排查」；不适用写需求 / 原型 / 技术方案 / 开发 / 评审，以及无运行项目只测文档。

## 二、输入与前置

| 输入 | 作用 | 缺失处理 |
|---|---|---|
| 项目代码位置 + 启动命令 | 被测对象 | ⛔ 未给必问 |
| `.spec/PRD/VN/`（先读速查表建索引，AC 断言回模块 §9） | 对错基准 | ⛔ 阻塞 |
| `.spec/设计稿/`（**视觉主基准**）→ 缺失时回退 `.spec/原型/`（**结构基线**，视觉降级） | 好看基准 | 回退并**明示视觉基准降级** |
| `.spec/TDD/VN/`、前端 api 文件 | 接口基准 + 接口清单 | 缺则按路由/网络请求现场提取 |
| `README` / `package.json` / 路由 / api | 页面清单 + 状态集合 + 可交互元素 + 接口清单 | 无则先盘点 |
| 浏览器工具（**硬依赖**） | 功能遍历 + 网络监听 + 截图 | **全无 → 报错停止，不产出**（策略见 `../../shared/browser-policy.md`） |
| `midscenejs`（可选增强） | 视觉断言 | 需装依赖 + 模型配置；不可用则降级 `toHaveScreenshot` / 截图人工比对，**并在 Scope Gate 说明** |

## 三、主流程（9 步）

> 先计划后执行，禁止边测边想；◉ = 强制暂停等用户确认。

1. **输入解析**：确认项目代码位置（未给必问）；读上表输入，提取页面清单 + 状态集合 + 可交互元素 + 接口清单；**组件决策链（调度组件库）**：盘点项目已有测试基建（已有必须用）→ 检索 AI 组件库 `D:\project\agent-project\skills-knowledge\asset-library\`（capabilities → patterns → adapters），命中锁版本，未命中走封装七步法（`asset-library/shared/component-authoring.md`，造前写 asset-gap），交付时做沉淀判断。
2. **环境准备 + ◉ 浏览器预检**：按 `acceptance-loop-guide` 核查 typecheck / lint / 单测 / build / e2e 与 hooks；install + 启动 dev server 确认可访问；浏览器工具硬性预检（任一可用即功能遍历 + 网络监听）。
3. **测试计划 + 用例**：按 `assets/test-process-template.md` 写计划；按 `assets/test-case-template.md` 写功能（全状态 + 全点击）/ 样式（三态 + 视觉）/ 性能三类用例；**矩阵来源**：命中的 pattern/adapter 带 `verification.required` 时，测试矩阵由其驱动生成，不自造。
4. **◉ Scope Gate（强制暂停）**：呈现范围 + 用例总数 + 工具方案 + 慢接口阈值，确认后放行。
5. **功能测试**：按 §4.1 全状态、§4.2 全点击执行，回填用例。
6. **样式测试**：按 §4.3 执行。
7. **接口性能测试**：按 §4.4 执行。
8. **汇总**：按 `assets/bug-report-template.md` 汇总三类缺陷（P0/P1/P2 + 复现 + 证据），规范见 §4.5。
9. **归档**：`.spec/测试/` 下测试计划、用例、问题文档、接口性能清单、`screenshots/`；命中资产的失败模式回写组件库 `asset-library/anti-patterns/` 与 `cases/failure/`（沉淀门禁：走查/测试证据随 asset-usage 回写）。**问题日志**：归档同时在项目 `.spec/问题日志.md` 台账追加一行索引（日期｜来源｜问题产物｜轮次｜状态｜反哺出口；格式见 skill 源仓库 `../../shared/templates/problem-log-template.md`）。

## 四、关键规范

> 正文只留判据；细则按需加载对应 references。

**4.1 全状态覆盖**：从 PRD 模块状态机图提取全量状态 → 用接口 / 种子 / 页面操作构造前置数据 → 逐状态验证展示、可执行操作、流转入口 → 对照状态机逐项勾选，**100% 才进下一模块**。

**4.2 全点击覆盖**：逐页盘点全部可交互元素（按钮 / 链接 / 输入 / 下拉 / 开关 / 勾选 / 卡片 / 行操作 / 图标 / 分页）→ 逐一点击并验证「有反应 → 符合预期 → 无报错 → 无死链」→ 记录状态变化、弹窗、跳转、请求 → 逐项勾选；**未点到的标原因**（如需权限则登记风险）。

**4.3 样式测试**：视觉断言用 midscenejs `aiAssert/aiQuery` 判符合**设计稿**或自然语言描述，不可用按层级降级并明示；三态必测（加载 / 空 / 错误逐页验证并截图）；有设计稿基准（`.spec/设计稿/` 或外部稿）→ 调用 `Fidelity-Review`（Testing 场景模式）做 UI 还原度检查（视觉以设计稿为准），就地接收 mini-issue 并入本文档；**无设计稿才回退原型基准并在报告中明示「视觉基准降级」**。

**4.4 接口性能测试**：监听用 Playwright `page.on('response')` + `response.timing()` 或 `performance.getEntriesByType('resource')`；阈值默认 >1000ms 慢 / >3000ms 很慢 / >5000ms 严重（可调）；逐条记录路径 + 方法 + 平均/最大耗时 + 触发场景 + 证据到接口性能清单；慢接口按 P1/P2 进问题文档（严重到致功能失败可升 P0，与 `api-perf-guide.md` 口径一致）。

**4.5 问题文档规范**：P0 阻断 / P1 严重 / P2 一般；每条含 现象 + 复现 + 期望/实际 + 级别 + 用例号 + 证据（样式 / 性能必附）；**统计用重新实测值，禁止估算**；**零问题也要说明覆盖边界**——覆盖了什么 / 未覆盖什么（未验的浏览器与设备、未构造的极端数据、未测的权限组合）/ 残余风险，禁只输出「未发现问题」。

**4.6 不确定即问**：

| 场景 | 处理 |
|---|---|
| 代码位置 / 启动命令不明 | 问 |
| 阈值需自定义 | 问 |
| 是否启用 midscenejs | 问（依赖 + API Key） |
| 范围外发现 | 问 |
| 无法本地启动 | 停并反馈，不硬跑 |

提问给选项和推荐；纯测试细节不打断。

## 五、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 没计划 / 用例直接跑 | 先步骤 3 |
| 只测主流程 | 逐状态覆盖（§4.1） |
| 只点主按钮 | 全元素点击（§4.2） |
| 样式问题不截图 | 铁律 3 |
| 慢接口缺耗时 | 记录路径 + 耗时 + 场景 |
| 缺陷无分级 / 复现 | 按 bug-report-template |
| 预期自己编 | 标来源或【设计假设】 |
| 三态没测 | 逐页验证截图 |
| 无接口清单做性能 | 先提取 |
| 浏览器不可用硬跑 | 报错等安装 |
| 不确定自己拍板 | 停下问 |
| 没实测就说「通过」 | 铁律 8，出本次证据 |
| 零问题只写「未发现问题」 | 写清覆盖边界与残余风险 |

## 六、资源清单

- `assets/test-process-template.md`、`test-case-template.md`、`bug-report-template.md`
- `references/test-case-guide.md`、`style-test-guide.md`、`acceptance-loop-guide.md`、`api-perf-guide.md`、`browser-guide.md`、`decision-rules.md`
- `references/case-library/`：测试方法学 + 框架速查 + 专项 + 同行样本（按需加载）
- `../../shared/baseline-terms.md`、`../../shared/browser-policy.md`、`../../shared/evidence-before-claims.md`（仓库根）：公共约定
- `CONTEXT.md`；产出位置 `.spec/测试/`
- 兄弟 skill：`Fidelity-Review`（Testing 场景模式，有设计稿时承接 UI 还原度检查）、`Bug-Fix`（发现的可运行性问题转其修复闭环）

## 七、运行问题埋点

收尾按 `../../Other/Skill-Optimizer/references/instrumentation-guide.md` 自查上报 `../../issue/Testing/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `../../Other/Skill-Optimizer/assets/issue-template.md`）。归因未明先留事实，按共享记录规则处理；不为经验提炼阻塞主流程。

## Contract Compatibility Layer

Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.


> LEGACY BODY BOUNDARY: The preceding body, references, and assets are retained for capability compatibility. When any wording conflicts, the contracts in `../../shared/` and the sections below win.

## Purpose

Preserve the mature capability of `Testing` while exposing it through the v2 Skill contract.

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
