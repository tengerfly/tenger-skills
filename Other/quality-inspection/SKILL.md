---
name: quality-inspection
description: 按周期或用户要求巡检项目的可维护性、测试、依赖、架构漂移、可观测性和运行质量，并将带证据的问题路由到迭代、缺陷、重构或优化流程；不未经授权直接改码或上线。
metadata:
  short-description: 周期巡检代码质量与运行健康度
---

# Quality Inspection

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose

把“代码是不是越来越差、系统是不是在退化、监控是否还能定位问题”变成可重复的巡检，而不是依赖个人感觉。该 Skill 是正向工程循环的稳定入口，也是模型无关质量的持续验证层。

## Trigger

- 到达项目设定的日/周/月巡检周期；
- 用户要求做代码体检、架构巡检、质量审计或发布后复盘；
- `web-monitor`、`server-log`、`server-monitor` 出现重复错误、性能回退、告警噪声或可观测性缺口；
- 更换模型、技术栈、关键依赖或完成大规模重构后，需要验证质量是否保持。

不适用于单个已知 Bug 的定位修复；此时转 `Defect-Triage` / `Bug-Fix`。

## Inputs

1. 项目当前分支、commit、工作区状态和上次巡检基线；
2. `.spec/baseline/`、`.spec/workflow.yaml`、质量门禁和发布记录；
3. 项目可执行的 install/typecheck/lint/test/build/security/dependency 命令；
4. 代码结构、变更范围、测试结果和依赖差异；
5. `web-monitor`、`server-log`、`server-monitor` 的错误、指标、告警和关联 ID；
6. 最近发布后的错误率、P95、可用性、关键旅程和成本（若项目有这些指标）；
7. 上期未关闭的巡检发现和已批准的例外。

## Preconditions

- 先确认项目路径、分支和未提交变更；不得 reset、clean、覆盖用户内容。
- 默认只读检查；任何自动修复、升级依赖、格式化、生成文件、生产查询或部署都必须另行授权。
- 记录检查日期（绝对日期，例如 `2026-09-20`）、commit、工具版本、命令和退出码。
- 运行命令前先阅读脚本和配置，确认不会迁移数据、发布或清理目录。
- 不复制 secrets、客户数据或原始敏感日志；报告引用脱敏后的证据定位。

## Responsibilities

- 运行确定性质量门禁并保存证据；
- 检查代码可读性、模块边界、重复、复杂度、错误处理、日志关联、测试健康度、依赖和架构漂移；
- 关联运行时信号与发布/commit，识别重复问题和回归；
- 按影响和证据给出发现项、路由、优先级和最小修复建议；
- 比较本次与上次基线，形成趋势，而不是只给一次性评分。

## Non-goals

- 不以“所有指标都为零风险”为目标；
- 不把风格偏好当成缺陷；
- 不为了提高分数大面积重写代码；
- 不把模型生成的代码天然判定为问题，也不因模型更换而放宽门禁；
- 不在没有 Gate 和用户授权时直接修复、提交、部署或关闭告警。

## Procedure

### 1. 固定巡检范围与安全快照

记录本次检查的项目、环境、分支、commit、时间窗口、检查层级和排除项。若工作区存在未提交变更，分别标注“基线代码”和“工作区变更”，避免把开发中内容误判为已发布质量。

### 2. 运行确定性门禁

按项目实际配置运行可用的类型检查、lint、单元/集成/E2E、构建、依赖安全和生成物校验。每项记录命令、版本、退出码、持续时间和摘要。未配置的检查标为 `NOT_CONFIGURED`，不能写成通过。

### 3. 检查可维护性与反 AI 味风险

以代码证据检查：

- 模块职责和依赖方向是否清晰；
- 是否出现超大文件、重复逻辑、过深嵌套、魔法值、隐式全局状态；
- 命名、类型、错误处理和边界行为是否可读；
- 是否吞异常、伪造成功、滥用 `any`/类型断言、复制粘贴或引入无必要抽象；
- 注释是否解释约束和原因，而不是重复代码；
- 新代码是否符合项目既有约定，是否留下无法验证的“AI 生成痕迹”；
- 日志是否结构化、脱敏、可通过 `reqId`/`traceId` 关联，是否存在敏感信息泄露风险。

“AI 味”只能作为待核验信号，最终发现必须绑定具体文件、行、行为或测试证据。

### 4. 检查测试与架构漂移

比较当前结构与 `.spec/baseline/`、技术设计和批准的变更：模块边界、API、数据模型、依赖、关键旅程和质量指标是否漂移。检查新增/修改逻辑是否有相应单测、契约、集成或 E2E 保护；对不稳定测试区分产品失败、环境失败和测试本身不可靠。

**检查流程状态一致性（防状态漂移）**：核对 `.spec/` 下评审/测试任务清单的「状态」列、裁决/修复记录、`workflow.yaml` 与 `manifest.yaml` 是否一致；不一致时以 `workflow.yaml` + 实际产物文件证据为准，报告 stale 文件并建议修正（对账规则见 `../../shared/workflow-visibility.md`）。

### 5. 检查依赖、发布和可观测性

检查锁文件与依赖升级、过期/高风险依赖、构建时间/产物体积、发布回滚证据、版本与 commit 关联。确认前端错误、服务日志、主机/服务指标、告警和关键旅程信号能否关联到版本和请求；缺失时生成可执行缺口，不以“上线后再补”通过。

### 6. 关联运行证据

从 `web-monitor`、`server-log`、`server-monitor` 或项目导出中按 `traceId`、`reqId`、`sessionId`、`appVersion`、环境和时间窗口做去重与聚合。重点看：重复错误、错误率/延迟回退、资源异常、告警噪声、关键旅程失败、修复后是否复发。没有运行数据时标 `OBSERVABILITY_GAP`，不要凭代码审查推断线上健康。

### 7. 形成发现项并路由

每条发现至少包含：ID、证据、影响、严重级别、是否回归、推荐路由、最小下一步和验证方式。

- 行为偏离批准基线 → `DEFECT` / `Defect-Triage`；
- 外部需求或业务规则要变化 → `CHANGE` / `Impact-Analysis`；
- 内部结构、测试或可观测性治理且默认行为不变 → `REFACTOR` / `Refactor-Planning`；
- 指标、成本、性能或用户行为驱动的收益机会 → `OPTIMIZE` / `Optimization-Planning`；
- 正在造成高影响生产事故 → `INCIDENT` / `Incident-Response`。

不要把所有发现都路由成重构；优先按证据和外部影响分类。

### 8. 更新巡检基线

保存本次结果、已关闭项、延期项、风险接受和与上次的趋势。重复且已确认的工程问题可沉淀到 `../../bug-patterns/`、项目基线或 Skill 治理流程；公司/客户项目只沉淀去敏后的通用模式。

## Outputs

```text
.spec/inspection/YYYY-MM-DD/
├── inspection-report.md
├── gate-results.yaml
├── findings.md
├── trend.md
└── evidence-index.md
```

其中 `inspection-report.md` 为正式报告；`gate-results.yaml` / `findings.md` / `trend.md` / `evidence-index.md` 为报告派生件，分别取模板 §1 门禁结果 / §3 发现项 / §2 趋势摘要 / 证据列汇总。

报告必须写明：范围、commit、命令、结果、证据位置、未检查项、发现分类、路由、下一次巡检日期和是否建议人工确认。

模板见 `assets/inspection-report-template.md`，检查项见 `references/inspection-checklist.md`。

## Evidence

合格证据：命令输出、测试报告、构建产物摘要、代码定位、依赖锁文件差异、脱敏日志/指标、发布记录或已确认的基线。不得用“看起来不错”“模型判断质量高”“没有听说问题”替代证据。

## Gate

- `PASS`：确定性检查结果可复核，关键范围已覆盖，发现项有证据和路由，无未说明的阻塞（对应状态 `INSPECTION_PASS`）；
- `CONDITIONAL`：存在已登记的缺口、例外或未配置检查，但影响和后续动作明确（对应状态 `INSPECTION_CONDITIONAL`；例外必须完整记录 exceptionId、risk、owner、dueAt、remediation、allowDownstream、approvalRef 七字段，缺项即按 BLOCKED 处理）；
- `BLOCKED`：无法确定检查范围/版本，或安全、权限、生产风险阻止继续（对应状态 `INSPECTION_BLOCKED`）。

通过巡检不等于代码没有问题，而是代表问题已被发现、分类、排序并进入可追踪闭环。巡检本身不授权改码或上线。

## Failure Route

- 检查命令会改变环境：停止并改为静态检查或请求授权；
- 运行数据缺失：标 `OBSERVABILITY_GAP`，转 `signal-collection` 补采集/补埋点，不宣称运行健康；
- 发现疑似安全事件：停止扩展读取范围，转 `Incident-Response`；
- 发现功能偏差：转 `Defect-Triage`，不要直接按“质量问题”重构；
- 基线过旧或不存在：转 `Project-Onboarding`，先补基线。

## Downstream Contract

下游接收的是带证据的发现清单，而不是未经排序的意见：

- `Impact-Analysis` 读取影响范围和外部行为证据；
- `Defect-Triage` 读取复现、版本、日志和回归证据；
- `Refactor-Planning` 读取内部质量目标和行为保护边界；
- `Optimization-Planning` 读取指标基线、预期收益和保护指标；
- `Skill-Optimizer` / `Skill-Evolver` 只接收去敏后的流程问题和可复用模式。

## State Changes

```text
INSPECTION_REQUESTED
→ INSPECTION_IN_PROGRESS
→ INSPECTION_PASS | INSPECTION_CONDITIONAL | INSPECTION_BLOCKED
→ CHANGE / DEFECT / REFACTOR / INCIDENT / OPTIMIZE / NO_ACTION
```
