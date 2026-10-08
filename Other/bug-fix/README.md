# Bug-Fix —— 日志驱动的 Bug 诊断与修复委托闭环 Skill

> 状态：✅ 初版定稿（09-07）
> 定位：链外专业 Skill，不占主链 14 节点。只做「诊断 + 委托 + 沉淀」：从日志/报障出发，证据链定位根因，根因 Gate 后只交付定位报告（含修复方向）与修复任务清单——具体技术方案、改码、深度测试各委托对应 skill，本 skill 核对原场景不再现并迭代判定闭环；有预防价值的错误模式沉淀 `../../bug-patterns/` 池反哺方案/开发 skill。

## 一、核心

| 项 | 内容 |
|---|---|
| 输入 | 前后端日志（粘贴/文件/线上导出/本地复现）+ 代码位置 + 现象描述 |
| 输出 | `.spec/bug修复/<日期>-<简述>/`：问题定位报告 + 修复任务清单 + 复现材料/截图 |
| 委托 | 方案 → Frontend/Backend-Tech-Design（增量 TDD/FTDD）；改码 → Frontend/Backend-Dev；回归 → 开发自测 + 按需 Testing |
| 边界 | 只诊断与委托——不产 TDD/FTDD、不改码、不做深度测试；需求问题移交 PRD-Design；不做无关重构 |

## 二、流程

```
报障输入 → 1 解析三要素 → 2 双通道日志解析 → 3 复现确认 → 4 根因定位（证据链三段）
→ 5 ◉ 根因 Gate → 6 委托技术方案 → 7 委托开发修复 → 8 回归（自测+按需Testing+原场景核对）
→ 9 归档回填 → 10 沉淀反哺（有预防价值才沉 ../../bug-patterns/）
```

Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.

## 三、目录与产出

```
../bug-fix/
├── SKILL.md / README.md / CONTEXT.md
├── references/（log-channels-guide / root-cause-guide / case-library）
├── assets/（locate-report / fix-task-list / pattern-card 模板）
└── .spec/bug修复/<日期>-<简述>/
    ├── 问题定位报告.md
    ├── 修复任务清单.md
    └── 复现材料/截图
```

沉淀池：**skill 源仓库根** `../../bug-patterns/<日期>/<NN>-<错误模式>.md`（集中池，案例卡模板 assets/pattern-card-template.md）。无论 bug 修在哪个项目都直接写入本池，用户只需在本仓库一处定期提炼。

## 四、上下游

- 上游：用户报障 / Testing 问题文档 / Code-Review 可运行性问题
- 委托：Frontend/Backend-Tech-Design（方案）、Frontend/Backend-Dev（修复）、Testing（按需完整回归）
- 沉淀：有预防价值错误 → skill 源仓库根 `../../bug-patterns/` 集中池（Bug-Fix 写）；提炼目标 skill → Skill-Optimizer 模式③（本仓库一处提炼）
- 移交：需求本身不合理 → PRD-Design
