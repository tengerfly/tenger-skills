# 无 git 仓库时开发纪律缺少建仓前置动作 ⇒ 一功能点一提交与回滚基线无法执行

> 归属 skill：`Backend-Dev`（同类问题已同步 Frontend-Dev）｜ 日期：2026-10-18 ｜ 来源：埋点（真实项目 knowledge-bases 第 41 轮）

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P1 |
| 标签 | `流程缺陷` / `边界不清` |
| 优化状态 | 处理中（规则已改，待真实开发轮复验；未标已沉淀） |

## 现象

- knowledge-bases 在第 41 轮之前**没有 git 仓库**（`git log` 报 not a repository），此前 40 轮开发无任何提交记录。
- backend-dev 铁律 6 与 S7 要求「一功能点一提交；提交前 eslint + commitlint 必过」、S7 要求「更新 PLAN 状态（附 hash）」，但 S1 的三路判定/输入表里**没有任何『先建仓』的前置动作**；frontend-dev 输入表更把「git 地址」列为必问，缺则暂停——本地个人项目没有远端地址时会直接停住。
- 后果：评审无法按 commit 定位改动；回滚无基线；trace artifacts 只能绑文件 sha；「一功能点一提交」形同虚设。

## 跟踪与证据

- 原问题 ID / 来源项目与版本：knowledge-bases，`.spec/auto-test/2026-10-18/handover.md`（第 40 轮）
- 发现时间 / 相关步骤：2026-10-18 15:25，WorkFlow 恢复后按 backend-dev S1 准备续做时
- 脱敏证据：项目根无 `.git`；`git log` fatal: not a git repository；本轮已手工 `git init` + 基线提交（commit 503e05d）
- 责任方 / 下一动作 / 修复判据：Backend-Dev / Frontend-Dev（规则已补）；判据 = 下一个无仓库项目开工时，S1 自动建仓并提交基线，无需用户提醒
- 根因与归属：已确认——规则默认项目已在 git 管理下，未覆盖「本地新建/接管无仓库项目」
- 复核证据 / 未验证项：本轮知识库项目已按新规则执行（建仓基线提交），但规则文本的复验要在下一次新项目上做
- 回退方式：3 份文本改动可按 git diff 回退

## 期望 vs 实际

- **期望**：开发 Skill 在 S1 就确认「有没有仓库」，没有就建仓并提交基线，再进入功能点循环；前端不因缺远端地址阻塞本地项目。
- **实际**：只有后端 S7 隐含假设有仓库；前端把 git 地址设为必问。

## 修复方向（本轮已落地）

1. `DEV/backend-dev/SKILL.md` S1：新增「**仓库前置（REQUIRED）**：无 git → 在允许修改范围内 `git init` + 提交基线（不 push、不改远端），否则铁律 6 与回滚基线无法执行」。
2. `DEV/frontend-dev/SKILL.md` S1：产出位置条款加「无远端仓库的本地个人项目例外」——目标目录已定即可开工，本地 `git init` + 基线提交，不因缺 git 地址停。
3. `shared/workflow-visibility.md` 换会话对账段：新增「无 git 项目的恢复」一句，与 WorkFlow 恢复动作对齐。
4. 未做：`commitlint`/husky 等提交门禁在无仓库项目上的初始化脚本；本轮以「Lead 统一提交 + 每功能点 commit」轻量替代，是否值得做模板化待评估。

## 双向落点

| 方向 | 目标 skill | 落点 |
|---|---|---|
| A · 防复发 | Backend-Dev / Frontend-Dev | S1 仓库前置动作 |
| B · 检出力 | Code-Review | 评审开工先看项目是否有 git 与提交粒度（可加入 known-issue-patterns，待复核） |

## 沉淀记录

| 字段 | 值 |
|---|---|
| 沉淀目标 | 未沉淀（处理中） |
| 沉淀位置 | 规则已改：`DEV/backend-dev/SKILL.md`、`DEV/frontend-dev/SKILL.md`、`shared/workflow-visibility.md` |
| 忽略理由 | — |
