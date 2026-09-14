# 提交期拦截——prettier / commitlint 在 husky 阶段批量拒绝

> 归属：`bug-patterns/` 错误模式池 ｜ 日期：2026-09-15 ｜ 来源：会话记录挖掘（rollout 签名：prettier×29 / commitlint 拒绝×31，V2 迭代期间 ≥3 次提交被拒）
> 依据：learning-assistant 会话 rollout `model-io-sess_369efc48-*.jsonl`
> 原则：存「一类会再犯的错误」+ 防复发规则。

## 基本信息

| 字段 | 值 |
|---|---|
| 根因类型 | 环境依赖（工具链纪律未前置） |
| 受益 skill | Backend-Dev / Frontend-Dev / Workflow（提交节奏） |
| 等级 | P2（每次被拒浪费一轮提交+排障，不影响产物质量） |
| 建议落点层级 | 错误表加行 |
| 状态 | 已提炼（落点见文末） |

## 现象（同类 bug 长什么样）

- `git commit` 被 husky 拒：①pre-commit lint-staged 报 prettier/prettier 几十处格式错；②commit-msg 报 `header-max-length`（>100 字符）或 `subject must not be sentence-case`（大写开头/含大写缩写开头）；
- 中文提交说明里夹大写英文缩写（如 `FP-33`/`V2`）开头时尤易触发 subject-case。

## 根因（证据链摘要）

当格式化（prettier --fix）与 commitlint 预检没有作为提交前动作执行时，拦截发生在 husky 钩子里——一轮提交失败 + 返修 + 重提，纯浪费；多文件批次还会把格式修复混进功能提交。

## 防复发规则（核心，给目标 skill 的可执行规则）

- [ ] 提交前主动跑 `npx eslint <改动目录> --fix`，不依赖 pre-commit 钩子替你修
- [ ] 提交信息先用 `npx commitlint <<< "<msg>"` 预检：header ≤100 字符、subject 小写开头（中文天然合规，避免大写缩写开头）
- [ ] 格式修复与功能变更分开提交，避免 lint-staged 把无关文件卷进功能提交

## 提炼回填（Skill-Optimizer 模式③ 填）

| 字段 | 值 |
|---|---|
| 提炼落点 | `Backend-Dev/SKILL.md` 常见错误对照表新增行（提交前预检） |
| 决策记录 | `Backend-Dev/CONTEXT.md` D-09 |
| 忽略理由 | — |
