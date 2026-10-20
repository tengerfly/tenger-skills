---
name: prototype-review
description: 低保真原型评审（Prototype-Review 兼容入口）。对照 PRD 对已生成的低保真原型做四维只读评审：页面/载体完整性（防漏+防加戏）、文案与字段逐字一致、交互与流程闭环、原型自身实现质量（不查视觉）。浏览器工具硬前置，全无则报错停用。触发：评审原型、走查原型、原型验收、查页面遗漏、查交互闭环、对照 PRD 查原型。
metadata:
  legacy-alias: Prototype-Review
  migration-target: prd-workflow
---

# Prototype-Review 兼容入口

本目录保留旧版成熟逻辑和资源；旧版完整说明已归档到 `references/legacy-skill.md`，原有 references/assets 不删除。新流程通过本入口承接，但职责和 Gate 受 `../../shared/product-workflow-contract.md` 约束。

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

**闭环回流（L2）**：P0/P1 条目要标「已沉淀」前，必须先回流 1 条评测用例，并在该用例声明里用 `issueRef` 指回本条问题（值＝本条问题的仓库相对路径，形如 issue/<skill>/<日期>/<NN>-<标题>.md）；没有这条用例就按「未验证」处理，优化状态停在待处理/处理中，不得写「已沉淀」。
判据与字段口径的单一来源是仓库根 `governance/eval-spec.yaml`（`caseTiers.L2` + `issueRef` 节），机械核对由 `scripts/eval/relay.py` 执行；本节只承接义务，不复述其条文。

## 评审上下文隔离（执行必需）

强制适用 `../../shared/review-context-isolation.md`（优先级高于本正文）：参与过被评原型（或其评审基线 PRD）产出、修订、内部自检或评审调度的会话/子代理，不得作为该原型的评审者；同一会话里换角色不算隔离。评审判断只发生在隔离上下文，评审者只拿评审包，不继承产出会话历史、草稿与自检结论。

- **评审形态（四维各自独立）**：页面与载体完整性 / 文案与字段一致性 / 交互与流程闭环 / 原型自身实现质量，**各由 1 个独立 fresh 评审子代理执行、互不可见**；每个子代理只拿评审包 + 本维清单/模板，不读产出会话记录。
- **汇总形态（独立汇总子代理）**：由独立汇总子代理只读四份维度报告 + `assets/summary-template.md` 完成汇总，不参与任一维度评审。
- **编排形态**：只做基线核对、建评审包、派发、收产物核验、落 Gate，不做评审判断。

派发计划：4 个维度子代理 + 1 个独立汇总子代理（共 5 个，互不可见）；评审包按 `../../shared/templates/review-package.md` 落在 `.spec/原型评审/评审包-REV-*.md`。维度子代理同样按 `references/browser-inspection-guide.md` 做浏览器硬性预检。

无子代理能力时：按 `../../shared/review-context-isolation.md` §4 写评审包 + `dispatch-prompt.md` 交新会话执行（主会话停住）；仍无隔离能力 ⇒ `BLOCKED`（缺评审隔离能力），可先出「自查（非评审）」，不得自查冒充评审、不得产出评审报告 / 任务清单 / Gate 建议。

报告必须记录隔离信息：汇总报告含 `assets/summary-template.md` §0.5，四份维度报告的元数据含「评审上下文 / 评审包摘要」；缺记录 ⇒ Gate 只能 `BLOCKED`（缺评审隔离证据）。

## Purpose
平滑接入新的 PRD Workflow，同时保留已经验证过的领域规则和模板。

## Trigger
用户明确要求执行本领域动作，或 `prd-workflow` 在对应阶段调度时触发。请求属于上游研究、定位、蓝图或范围决策时先路由上游。

## Inputs
- 上游 artifact、manifest、决策记录和 traceability；
- 用户确认、研究证据、PRD/原型原文；
- 本目录 legacy-skill、references、assets 和既有脚本。

## Preconditions
- 上游输入可定位，OPEN/ASSUMPTION 不能被当作批准结论；
- 上游输入的**批准状态现行有效**：逐条读 `.spec/manifest.yaml` 上游条目的 `status`、`version`、`gate`、`allowDownstream`，任一 `SUPERSEDED`／非 `PASS`／`false` ⇒ 本轮只能 `BLOCKED`（判据全闭只作事实；限定条件只能落字段，`../../shared/gate-policy.md` §6），汇总报告须含公共基线 §0 的上游闸门核对表；
- 工作区边界已检查，不覆盖未提交内容；
- 读取产品契约和 Gate 规则；
- 浏览器工具为**硬依赖**：按 `../../shared/browser-policy.md` §一/§二 预检（任一可用即开工；全无 → 先按 §五 获取，仍全无 → 报错停止，不产出评审文档；报错文案模板见 §四，本 skill 只声明级别与动作、不重复定义）；
- 评审类入口必须只审不改；
- **评审上下文隔离前置**：本上下文未参与被评原型（及其 PRD 基线）的产出 / 修订 / 自检；评审按 `../../shared/review-context-isolation.md` 派发隔离子代理（四维各 1 + 汇总 1），评审包按 `../../shared/templates/review-package.md` 构建；宿主无子代理且无法开新会话 ⇒ 本轮只能 `BLOCKED`（缺评审隔离能力），不得同上下文自审。

## Responsibilities
- 校验输入 artifact、证据和用户确认；
- 在职责边界内复用旧版成熟规则；
- 产出带 artifactId、sourceRefs、evidenceRefs、decisionRefs 的结果；
- 失败时回退到正确上游；
- 将 execution、Gate 和问题写入项目 `.spec/`。

## Non-goals
- 不替用户决定产品定位、MVP、范围或重大取舍；
- 不删除旧版 references/assets；
- 不把竞品存在、模型推荐或原型表现升级为产品事实。

## Procedure
0. **〔隔离派发 · REQUIRED〕** 开工前按 `../../shared/review-context-isolation.md` 判形态并派发：本上下文参与过被评原型（或作为评审基线的 PRD）的产出 / 修订 / 自检 / 评审调度 ⇒ 只能作编排形态（基线核对、建评审包、派发、收产物核验、落 Gate），不得在本上下文执行步骤 3–5 的评审判断。四维各派 1 个 fresh 评审子代理（互不可见，只给评审包 + 本维清单/模板 + 浏览器预检要求），汇总派 1 个独立汇总子代理（只读四份维度报告 + 汇总模板）。无子代理则写评审包 + `dispatch-prompt.md` 交新会话；仍无隔离能力 ⇒ `BLOCKED`（缺评审隔离能力）。`reviewerRef` / `packageDigest` 记入汇总 §0.5 与各维度报告元数据。
1. 阅读本目录 legacy-skill 和资源，识别要复用的成熟规则。
2. 校验生命周期、上游状态、证据和开放项。
3. 执行本领域动作，只生成职责范围内的草案、报告或结果。
4. **〔评审形态 · fresh 子代理〕** 四维各自在隔离子代理中执行，不得在本上下文合并维度判断；子代理按评审包使用旧模板、清单、脚本和案例库做逐维评审与自检，产出四份维度报告（元数据须含「评审上下文 / 评审包摘要」）。
5. **〔汇总形态 · 独立汇总子代理〕** 由独立汇总子代理只读四份维度报告 + `assets/summary-template.md` 产出汇总（含 §0.5 隔离记录）；编排者写入 manifest、traceability、decision/execution record 并输出 Gate。
6. **〔编排者收账 / 裁决 / Gate〕** 编排者只做收产物核验、裁决与 Gate，不做评审判断；评审最多 3 轮，问题路由到产品定义、蓝图、范围、原型或 UI/DEV。

## Outputs
- 本领域 artifact、问题清单或评审报告；
- 评审包（`.spec/原型评审/评审包-REV-*.md`）、四维隔离记录（各维度报告元数据 + 汇总 §0.5）、派发与核验证据；
- 证据、决策、开放项和下游接口；
- executionId、status、gate、evidenceRefs、artifactRefs、decisionRefs、nextAction。

## Evidence
使用上游 artifact、用户确认、文件/源码/截图、可核验外部来源和确定性命令结果；评审者引用（reviewerRef / isolationMode）与评审包摘要（packageDigest）、派发与收产物核验记录（截图 / 命令 / 文件:行）。无来源数据标 OPEN；预测/估算显式标注；多方口径并列保留；子代理口头「已评审通过」不构成证据。

## Gate
PASS：输入、产物、证据和关键确认齐全；CONDITIONAL：风险、责任人、期限、补证动作和 allowDownstream 已登记；BLOCKED：关键证据、授权、范围或上游 Gate 缺失。文件存在不等于 Gate 通过。

## Failure Route
证据/用户问题不足回 `prototype-design`；产品定位/核心价值回 `product-definition`；业务流程/状态回 `application-blueprint`；MVP/功能范围回 `feature-decision`；技术未知交 DEV Workflow；页面/视觉问题交 `ui-ux-design` / `ui-ux-review`。

## Downstream Contract
下游只能消费 manifest 中状态明确的 artifact，必须读取 sourceRefs、evidenceRefs、decisionRefs 和 openItems，不得从聊天上下文补齐未确认结论。

## State Changes
`PROTOTYPE_REVIEW_IN_PROGRESS → PROTOTYPE_APPROVED`；仅当 Gate 为 `PASS` 且上游批准现行有效时由编排器写入，评审方不得自判放行。
