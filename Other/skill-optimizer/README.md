# Skill-Optimizer —— Skill 元优化器

> 让 skill 越用越贴合需求：记录 → 挖掘 → 优化 → 体检（+ 错误池提炼）。长期迭代，不参与业务交付。

## 一、四模式（+ 提炼）

| 模式 | 触发 | 产物 |
|---|---|---|
| 记录 | 记问题/复盘 | issue 文件 |
| 挖掘 | 丢 ../../chats/ 或粘贴 | 提取清单 → 确认后 issue |
| 优化 | 优化/精简/迭代 XX | skill 文件 + CONTEXT D-xx + issue 回填 |
| 体检 | 体检/检查 XX 自洽 | 问题清单 → 逐条裁决 |
| 提炼（③-附加） | 优化方案/开发/评审 skill 或点名「提炼 bug-patterns / 评审闭环沉淀」 | 双来源：`../../bug-patterns/` 待提炼案例 + `../../issue/` 来源=评审闭环项 → 目标 skill 防复发规则 / 评审方案例库 |

## 二、机制

- 双池：`../../issue/`（skill 自身问题，含来源=评审闭环的门禁沉淀项）唯一事实源 + `../../bug-patterns/`（真实 bug 错误模式，集中池在本仓库根，Bug-Fix 沉淀）。
- 标准先行：issue-template / signal-checklist / optimize-checklist / self-audit-checklist / skill-writing-standard / vibe-principles-mapping。
- 优化八维：问题修复/触发/体积/指令/稳定/简洁/术语/心法。
- 提炼落点逐层升级：错误表加行 → references 防复发清单 → Gate 预检项；评审侧落 `references/known-issue-patterns.md` 案例库（含检出方法）。
- 自我指涉：先优化自己（先修标准），再优化其他。
- 沉淀约定：粒度=一类问题；**双向**=A 产出方 skill 防复发 + B 评审方案例库（P0 双向必沉）；落点=先源仓库再同步 CodeBuddy 副本（双池在源仓库根，副本只含 skill 文件）。

## 三、目录

```
../skill-optimizer/
├── SKILL.md / CONTEXT.md / README.md
├── assets/（五份标准）
仓库根：`shared/instrumentation-guide.md`（埋点规范）＋ `shared/templates/issue-template.md`（issue 模板）——被 16 个 skill 共用，已提升为共享约定，不留副本
../../issue/ ../../bug-patterns/ ../../chats/   # 仓库根（../../bug-patterns/ 集中池）
```

## 四、快速上手

- 记问题：说「记个问题：XX」。
- 挖掘：丢记录进 ../../chats/ 后说「挖掘」。
- 优化：说「优化 XX」。
- 体检：说「体检 XX」。
- 提炼：说「优化 Frontend-Dev（含 bug-patterns 提炼）」或「提炼错误池」。
