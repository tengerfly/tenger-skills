# 竞品分析 Skill（Competitive Analysis）

> 给定产品想法，用全球中英文数据驱动调研，客观呈现五层竞争全貌，输出工业级竞品分析报告。判断交给用户，本 skill 不下可行性结论。
> 状态：✅ 完成

> LEGACY COMPATIBILITY NOTICE: This file preserves historical material. The active Skill, Gate, state, artifact, and evidence rules are defined by `shared/skill-contract.md`, `shared/gate-policy.md`, `shared/anti-deadloop.md`, `shared/artifact-contract.md`, `governance/`, and `.spec/workflow.yaml`. 现行交付与边界见 [SKILL.md](SKILL.md)；旧版 11 模块报告与数据红线全文见 references/legacy-skill.md。

## 一、交付

- active 交付：research 产物（研究范围、竞品选择、带来源的功能全景/对比矩阵、限制与未知项、裁剪依据 scopeBasis）+ 功能清单；旧版 11 模块报告模板见 assets/report-template.md，按需复用。
- 纪律：一切结论有据可依；禁编造；预测必标；多方口径并列。

## 二、五层框架

市场趋势 / 竞品优缺点 / 用户痛点 / 商业模式 / 技术可行性。

赛道自适应：红海看 CAC/价格带缝隙；内容平台看 UGC vs 结构化；灰区看合规链路；出海调海外研报+真实槽点；数据稀缺走口径并列 + 单位经济测算。

## 三、Pass Gate

- Gate 口径见 ../../shared/gate-policy.md：仅 PASS/CONDITIONAL/BLOCKED；残留 P0⇒BLOCKED；残留 P1 不得 PASS，仅完整授权 CONDITIONAL（exceptionId/risk/owner/dueAt/remediation/allowDownstream/approvalRef）；无 force-pass。
- BLOCKED: fabricated, conflated, or materially incomplete evidence; record the missing evidence and Failure Route.

数据红线 8 条见 SKILL.md §Evidence；全文见 references/legacy-skill.md。

## 四、目录

```
competitive-analysis/
├── SKILL.md
├── references/（dimensions / frameworks / decision-rules / case-library）
├── assets/（report / matrix / eval 模板）
└── .spec/<主题>竞品分析/
```

快速上手：给想法并说做竞品调研；本 skill 自动调研、过门禁后落盘。
