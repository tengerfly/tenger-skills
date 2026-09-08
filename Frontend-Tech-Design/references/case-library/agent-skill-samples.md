# 同类前端 Skill 结构样本（Agent Skill Samples）

> 用途：优化本 Skill 结构时的借鉴范本（只借鉴组织方式，不搬运内容）。

---

## 一、peterhdd engineering-frontend-developer（决策规则范本）

- 结构：SKILL.md（When X do Y）+ references/{css-patterns,data-table,react-patterns,typescript-patterns} + scripts/check_bundle.sh（包体 <200KB 检查）。
- 借鉴点：决策规则写法 + 量化阈值（LCP>2.5s、bundle>200KB、CI 覆盖率≥80%、组件>300 行拆分）——已融入 decision-rules.md。

## 二、Vercel agent-skills（官方）

- React/Next 5 个 skill：React 最佳实践、组合模式、Web 设计、RN、部署。
- 借鉴点：官方出品，组合模式 + 部署，最贴合前端方案命题。

## 三、Anthropic 官方 skills（含 frontend）

- 16 官方 skill，frontend/web artifacts 直接对标。
- 借鉴点：渐进式披露 + 触发词写法。

## 四、miles990/claude-software-skills

- 47 领域 skill：frontend / architecture-patterns / api-design / performance-optimization 分模块写法。
- 借鉴点：按关注点拆分 references 子文件。

> 出处：github.com/PeterHdd/agent-skills、github.com/vercel-labs/agent-skills、github.com/anthropics/skills。
