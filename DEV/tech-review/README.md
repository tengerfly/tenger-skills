# Tech-Review —— 技术方案评审 Skill

> 状态：✅ 定稿
> 定位：只做评审，不改稿。审 TDD/FTDD 的闭环与关联错误；PRD 与原型是尺子，TDD/FTDD 是被量物。

## 一、双视角

| 视角 | 标准 |
|---|---|
| 后端技术方案评审 | TDD 完整承接 PRD 且内部闭环 |
| 前端技术方案评审 | FTDD 完整承接 PRD+原型+TDD 且内部闭环 |

关联问题谁命中归谁，双方命中双方记。

## 二、重点

- 闭环：需求 / 流程 / 状态 / 数据。
- 关联：后端模块 / 前端模块 / 前后端接口 / 页面—原型（结构）/ 页面—设计稿（视觉）。

## 三、流程

```
输入解析 → 浏览器软检测 → 按批次单端评审（⑩-后 只审 TDD / ⑩-前 只审 FTDD，单批只出对应角色文档）→ 关联一致性专项
→ 本批次角色文档 → 汇总 → 任务清单+P0 确认（P1/P2 按 shared/ruling-policy.md 裁决） → 闭环复核与双向沉淀判定 → 归档
```

> 评审上下文隔离：评审判断由 fresh 评审子代理执行——单批由该批次评审者直接出汇总；双批 2 个批次评审者互不可见 + 1 个独立汇总子代理；产出/修订方案的上下文只做建包、派发、收账与 Gate，不自审（`../../shared/review-context-isolation.md`）。

浏览器软检测（全无跳过）。P0/P1 阻断，每条附修复判据，复核只验本轮，轮次上限 3（满 3 轮仍未收敛：P0 残留 BLOCKED；P1 残留仅可授权 CONDITIONAL）。清单交 Backend/Frontend-Tech-Design。

## 四、严重度

- P0：需求无承接、断头、接口对不上无法联调。
- P1：关联不一致、字段冲突、异常缺失、数据流断链。
- P2：表达/术语/越界/细节。

## 五、目录

```
../tech-review/
├── SKILL.md / README.md / CONTEXT.md
├── references/（backend / frontend / integration-checklist + known-issue-patterns 案例库）
├── assets/（role-review / summary / issue-list 模板）
└── .spec/技术方案评审/
```