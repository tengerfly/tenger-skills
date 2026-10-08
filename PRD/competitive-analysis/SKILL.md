---
name: competitive-analysis
description: 研究竞品并产出带来源的模块能力全景与功能对比清单。用于寻找同类产品、对标应用、市场或竞品功能调研；不做本产品定位、功能取舍或 PRD 编写。
metadata:
  legacy-alias: Competitive-Analysis
  migration-target: competitive-analysis
---

# Competitive Analysis

本 Skill 只负责外部研究。职责与交接见 `../../shared/product-workflow-contract.md`。旧资料按需读取，不加载旧版端到端指令覆盖当前边界。

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
回答“同类产品有哪些、各自具备哪些能力、证据是什么”，让不熟悉产品全貌的用户能够据此选择范围，而不是只得到几段竞品概述。

## Trigger
用户明确要求找竞品、调研功能、做类似某产品的应用，或 prd-workflow 调度 COMPETITIVE_RESEARCH。独立研究不要求先批准完整产品定义；定位与范围确认另交对应原子 Skill。

## Inputs
原始想法/对标产品、intake/discovery 研究问题、目标场景、研究边界和已有来源；正式交接同时读取 manifest 与 Gate。

## Preconditions
明确研究对象和本轮边界。对标名称有歧义时先澄清具体产品形态，或分别列候选及差异，不能默选其一。用户不知道完整功能不是阻塞研究的理由。

## Responsibilities
- 搜索并选择相关竞品，说明入选理由、直接/间接替代关系和研究覆盖范围。
- 核验功能来源、版本/套餐、限制和访问日期；区分已证实、不支持和未查明。
- 建立模块级全景与稳定编号的功能清单，记录竞品差异、使用场景和依赖线索。
- 把来源缺口及需用户/产品域判断的问题交接，不生成范围批准。

## Non-goals
不替用户访谈结论（product-discovery）、产品定位（product-definition）、业务规则设计（application-blueprint）或功能取舍（feature-decision）；不决定自建还是开源；不写 PRD。

## Procedure
1. 复述研究命题、已知场景和待查范围。用户要求先竞品后选功能时明确保留这一顺序。
2. 检索相关竞品，优先官方产品文档/帮助中心/版本说明及可核验演示；社区反馈标为反馈，不等同功能事实。范围足够时对比多个有区分度的竞品，不为凑数量加入无关产品。
3. 按 `assets/feature-inventory-template.md` 盘点模块，再展开关键功能；需要补研究维度时用 `references/dimensions.md`，分析方法按需用 `references/frameworks.md`，不把旧决策规则当范围授权。不能只研究用户提及的单点，也不能声称穷尽未能访问的能力。
4. 每条功能注明功能 ID、含义/场景、各竞品支持及限制、来源和日期、证据缺口。产品形态/套餐不同时分开，不混称全版本支持。
5. 向用户先展示模块全景，再按模块展示明细与差异；说明“这是候选能力，不代表都要做”。未知项保持 OPEN，AI 补充想法标 RECOMMENDATION。
6. 输出 research 和功能清单作为同一研究产物的正文/附件。交 product-definition 定位，交 application-blueprint 梳理业务，最终由 feature-decision 组织范围选择。

## Outputs
research artifact：研究范围、竞品选择、带来源的功能全景/对比矩阵、限制和未知项。保留功能 ID 供后续追踪，不新建第二需求源。正式执行输出 executionId、status、gate、artifactRefs、evidenceRefs、decisionRefs、nextAction。

## Evidence
在线研究必须实际查阅来源，保存 URL、标题、访问日期及相关原文位置；不能只凭模型记忆或搜索摘要。无联网/授权/页面访问能力时交付明确标注的未验证草案，说明补证路径，不能捏造竞品现状或宣称研究完成。

## Gate
PASS：约定研究范围有可追踪的模块/功能清单、来源与缺口声明；不表示产品范围已批准。CONDITIONAL 按共享 Gate 契约记录例外与下游限制。BLOCKED：关键对标不明或功能清单/关键来源缺失；不得据此冻结范围或写正式 PRD。

## Failure Route
来源缺失在本节点补证；用户问题证据交 product-discovery；定位交 product-definition；业务规则交 application-blueprint；取舍交 feature-decision；实现路线交 DEV/oss-radar。旧 references/legacy-skill.md 只作研究方法参考，冲突规则以本入口为准。

## Downstream Contract
下游以 research artifact 和功能 ID 消费证据；不得把竞品支持或研究推荐转成 APPROVED 需求。未经用户确认的能力不能直接进入 PRD。

## State Changes
`DISCOVERY_READY → COMPETITIVE_RESEARCH_IN_PROGRESS → COMPETITIVE_RESEARCH_READY | WORKFLOW_BLOCKED`；正式推进由编排器沿注册表合法边执行。独立研究不伪造正式状态。
