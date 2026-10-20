> LEGACY COMPATIBILITY NOTICE: This file preserves historical material. The active Skill, Gate, state, artifact, and evidence rules are defined by `shared/skill-contract.md`, `shared/gate-policy.md`, `shared/anti-deadloop.md`, `shared/artifact-contract.md`, `governance/`, and `.spec/workflow.yaml`. 现行流程与边界见 [SKILL.md](SKILL.md)；旧流程全文见 references/legacy-skill.md。

# PRD-Review —— PRD 检测 / 评审 Skill（历史名称；canonical id：`prd-review`）

> 状态：✅ 定稿
> 定位：只做评审，不改稿；问题定位原文，逐条列出并给修改方向，结论可追溯。

## 一、评审视角（互不越界）

| 层级 | 角色 | 唯一标准 |
|---|---|---|
| 一审 | 前端开发专家 | 能否照 PRD 独立写完前端 |
| 一审 | 后端开发专家 | 能否照 PRD 独立完成服务端/数据设计 |
| 一审 | 测试专家 | 能否照 PRD 直接写可执行测试 |
| 总审 | 产品专家（兼调度者） | 需求在业务语义层是否立得住、说得通、叫得统一、写得准（目标 / 业务闭环 / 规则完整 / 术语 / 文案 / 一致性 + 兜底档按需 + 调度三角色问题） |

- 一审三角色并行且互不可见；产品专家为**总审层 + 调度者**，在三角色完成后读「三份角色评审 + PRD 原文」做补充与调度。
- **术语与文案的「正确性」由产品专家唯一认领**（含调度时从 FE / BE 归并的同类问题）；FE / BE / TE 只判「有无 / 是否可开发 / 是否可测」，不判写法对错。

## 二、流程

```
解析 PRD → 三角色独立上下文并行评审 → 三份角色文档 → 产品专家总审（核心 6 维 + 扩展兜底档 + 调度三角色问题）→ 汇总去重 → 任务清单+用户确认 → 双向沉淀判定（P0 必沉）→ 归档
```

P0/P1 阻断、P2 可留；问题逐条直接列出，每条附出处/成因/**修改方向**与修复判据；复核只验本轮，轮次上限 3（超限后残留 P0⇒BLOCKED、残留 P1 只能经完整授权 CONDITIONAL；无自动第 4 轮、无 force-pass，见 `../../shared/anti-deadloop.md` §3）。清单交 `prd-design` 修复回填。

> **现行规则（2026-10-19 起，历史流程文字保留）**：评审判断按 `../../shared/review-context-isolation.md` 由隔离上下文执行（fresh 子代理首选，新会话次选；无隔离能力 ⇒ `BLOCKED`），产出 / 修订 PRD 的上下文不得自审；上文三角色拆分仅作**可选方案**（拆分时前端 / 后端 / 测试各 1 个独立子代理 + 产品专家总审 1 个）。

## 三、严重度

> 严重度定义见仓库根 `../../shared/gate-policy.md` §1；轮次与残留处理见 `../../shared/anti-deadloop.md` §2/§3。下为本域典型表述。

- P0：断头/无头/流程走不通/需求自相矛盾/缺失到无法开工。
- P1：模糊歧义/状态边界异常未定义/数据口径不一致/验收不可测/术语同名不同义致规则冲突。
- P2：表达/术语不统一/非关键细节。

## 四、目录与产出

```
prd-review/
├── SKILL.md / README.md / CONTEXT.md
├── references/（frontend / backend / test / product-checklist + known-issue-patterns 案例库）
├── assets/（role-review / summary / issue-list 模板）
└── .spec/需求评审/（四份评审 + 汇总 + 任务清单）
```

快速上手：给 PRD 路径或粘贴内容说「评审 PRD」，本 skill 自动跑三角色 + 产品总审并归档。
