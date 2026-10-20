# Code-Review —— 代码评审 Skill

> 状态：✅ 定稿
> 定位：只审不改；P0 附建议补丁进报告，不落盘源码。契约对不上 = 头号目标；定位到 `文件:行`，结论可追溯 AC/接口。

## 一、评审什么

对 Backend-Dev / Frontend-Dev 产出的代码，对照 PRD AC、原型、TDD、FTDD，从后端、前端两个视角 + 接口契约专项评审。

- 做：接口契约一致（核心）、可运行性、架构合规、代码质量、安全与数据、六大闭环。
- 不做：业务逻辑正确性（交测试流程）；测试闭环只查可运行/先行/标 AC。

## 二、核心

| 项 | 内容 |
|---|---|
| 输入 | 前后端代码 + libs/shared + PRD/原型/TDD/FTDD |
| 输出 | 后端评审 + 前端评审 + 汇总报告 + 任务清单（`.spec/代码评审/`） |
| 头号目标 | 接口对不上：入参个数、字段名/类型/大小写/术语、路径/方法、枚举/分页、共享类型被绕过 |

## 三、流程

```
解析 → 静态验证（install/tsc/build/test/lint，跑不了降级读码并标注）→ 按批次单端评审（⑬-后 后端 / ⑬-前 前端 ∥ Fidelity-Review 还原度）
→ 删除候选与清理计划 → 契约专项三方比对 → 本批次角色文档 → 汇总 → 任务清单 + 用户确认 → 闭环复核 + 双向沉淀判定 → 归档
```

> 评审上下文隔离：评审判断由 fresh 评审子代理执行——⑬-后 1 个批次评审者；⑬-前 前端批次评审者 ∥ Fidelity-Review 评审者、再由独立汇总子代理合并；产出/修复代码的上下文只做建包、派发、收账与 Gate，不自审（`../../shared/review-context-isolation.md`）。


## 四、目录

```
../code-review/
├── SKILL.md
├── README.md
├── CONTEXT.md
├── references/   # backend-checklist / frontend-checklist / contract-checklist / static-verification-guide / removal-plan-template / case-library / known-issue-patterns（案例库）
└── assets/       # role-review / summary / patch / issue-list 模板
```

> 产物落**被开发项目** `.spec/代码评审/`（后端/前端评审 + 汇总报告 + 任务清单），不在本 skill 目录内。

## 五、严重度

- P0：契约对不上无法联调、无法编译/启动、共享类型被绕过。
- P1：命名不一致但类型兼容、错误码缺失、三态缺失、架构越层、测试跑不通。
- P2：命名/注释/魔法值等建议项。

## 六、上下游

- 输入：Backend-Dev / Frontend-Dev 代码与四类文档。
- 输出：任务清单交对应 Dev skill 修改；修改方内部含清单检测与回填。