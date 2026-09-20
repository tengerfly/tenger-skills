# 同类 QA Skill 结构样本（Agent Skill Samples）

> 用途：优化本 Skill 结构时的借鉴范本（只借鉴组织方式，不搬运内容）。

---

## 一、qaskills（PramodDutta，最成熟的分类维度）

- **分类维度**：E2E / API / Unit / Performance / Security / Contract / Visual / Accessibility / Mobile + DevOps / BDD / Test Data / Process。
- **SKILL.md frontmatter** 带元数据字段：`testingTypes` / `frameworks` / `languages` / `agents`，便于检索与安装。
- **CLI 自动检测** agent（Claude Code/Cursor/Copilot 等 27+）并装到正确目录。
- 借鉴点：测试类型维度可直接作本 Skill case-library 的分类参照。

## 二、petrkindlmann/qa-skills（渐进式披露范本）

- 50 技能 / 10 类，每个 SKILL.md < 500 行，重代码下沉 `references/`，跨技能 cross-reference。
- 含 ai-test-generation / ai-bug-triage / test-reliability。
- 借鉴点：薄 SKILL.md + references/ 分层（与本仓库 skill 架构一致）。

## 三、kakawaa/qa-skills（目录规范范本）

- 57 技能 / 169 参考文件 / 14 模板；完整 `tests/` 目录规范（unit/e2e/api/performance/security/accessibility）。
- 借鉴点：测试产物目录约定、orchestrator 多技能串联。

## 四、super-smoke-test（nchemb，测试门禁）

- Stop hook 强制「代码评审 + Playwright 冒烟」后才算 done。
- 借鉴点：测试门禁做成强制 hook，而非可选项。

> 出处：github.com/PramodDutta/qaskills、github.com/petrkindlmann/qa-skills、github.com/kakawaa/qa-skills。
