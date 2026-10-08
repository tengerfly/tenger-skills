# 竞品分析 Skill（Competitive Analysis）

> 给定产品想法，用全球中英文数据驱动调研，客观呈现五层竞争全貌，输出工业级竞品分析报告。判断交给用户，本 skill 不下可行性结论。
> 状态：✅ 完成

## 一、交付

- `.spec/<主题>竞品分析/`：报告（11 模块）+ 验收结果详细说明（三段式 Pass Gate）。
- 纪律：一切结论有据可依；禁编造；预测必标；多方口径并列。

## 二、五层框架

市场趋势 / 竞品优缺点 / 用户痛点 / 商业模式 / 技术可行性。

赛道自适应：红海看 CAC/价格带缝隙；内容平台看 UGC vs 结构化；灰区看合规链路；出海调海外研报+真实槽点；数据稀缺走口径并列 + 单位经济测算。

## 三、Pass Gate

- Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.
- Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.
- BLOCKED: fabricated, conflated, or materially incomplete evidence; record the missing evidence and Failure Route.

数据红线 8 条见 SKILL.md。

## 四、目录

```
../competitive-analysis/
├── SKILL.md
├── references/（dimensions / frameworks / decision-rules / case-library）
├── assets/（report / matrix / eval 模板）
└── .spec/<主题>竞品分析/
```

快速上手：给想法并说做竞品调研；本 skill 自动调研、过门禁后落盘。
