# 同类后端开发 Skill 结构样本（Agent Skill Samples）

> 用途：优化本 Skill 结构时的借鉴范本（只借鉴组织方式，不搬运内容）。

---

## 一、peterhdd/engineering-backend-architect（已复用为 Backend-Tech-Design 范本）

- 结构：SKILL.md（When X do Y）+ references/（api-patterns/database-patterns/distributed-patterns/infrastructure/code-examples）+ scripts/。
- 借鉴点：决策规则写法 + 量化阈值（单机 PG ~10k 读）。详见 Backend-Tech-Design 的 decision-rules。

## 二、d-padmanabhan/claude-engineering-skills

- 语言级 skill 拆分：python-development / typescript-javascript / go-rust-systems / database-postgresql，每个含 references/ 渐进式披露。
- 借鉴点：按语言拆 references，渐进式披露。

## 三、skillmd backend-developer

- Go/Java/Node 三套「黄金规则 + 目录结构 + 代码模式 + 安全」直接可抄。
- 借鉴点：语言代码范式的组织方式（已融入 language-patterns.md）。

## 四、lobehub backend-api

- 「先定契约再写代码」工作流 + 鉴权围绕客户端决策树。
- 借鉴点：契约优先 + 鉴权决策树（已融入 decision-rules.md §四）。

> 出处：github.com/PeterHdd/agent-skills、d-padmanabhan/claude-engineering-skills、skillmd.ai/skills/backend-developer、lobehub.com。
