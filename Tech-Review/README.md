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
- 关联：后端模块 / 前端模块 / 前后端接口 / 页面—原型。

## 三、流程

```
输入解析 → 双视角独立并行评审 → 关联一致性专项 → 两份角色文档 → 汇总 → 任务清单+确认 → 归档
```

浏览器软检测（全无跳过）。P0/P1 阻断，每条附修复判据，复核只验本轮，轮次上限 3。清单交 Backend/Frontend-Tech-Design。

## 四、严重度

- P0：需求无承接、断头、接口对不上无法联调。
- P1：关联不一致、字段冲突、异常缺失、数据流断链。
- P2：表达/术语/越界/细节。

## 五、目录

```
Tech-Review/
├── SKILL.md / README.md / CONTEXT.md
├── references/（backend / frontend / integration-checklist）
├── assets/（role-review / summary / issue-list 模板）
└── .spec/技术方案评审/
```