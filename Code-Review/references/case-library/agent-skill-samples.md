# 同类代码评审 Skill 结构样本（Agent Skill Samples）

> 用途：优化本 Skill 结构时的借鉴范本（只借鉴组织方式，不搬运内容）。

---

## 一、anthroos/claude-code-review-skill（维度最全）

- 280+ 自动检查 / 15 类（Security OWASP+扩展 / Bugs&Logic / Performance / Code Quality SOLID / Testing / Accessibility WCAG / i18n / Docs / DevOps / Git / React·Next / TypeScript / Python / Node·Express / SQL·DB）。
- 4 并行 agent + 置信度评分（≥70）+ git blame 分析。
- 借鉴点：15 类检查维度可映射为审查清单顶层分类；并行 agent + 置信度架构。

## 二、googs1025/code-review-skill（中文范本，落地门槛最低）

- 输入类型自动检测（PR URL/Issue URL/diff/代码片段/commit）。
- **4 维分析**：Code Quality / Security / Performance / OSS 合规。
- **分级输出**：🔴Critical / 🟠Major / 💡Minor + merge 结论（REQUEST_CHANGES）。
- `references/security_checklist.md`（按语言）+ `scripts/fetch_pr.sh`/`fetch_issue.sh`/`fetch_commits.sh`。
- 借鉴点：分级输出范式 + 按语言安全清单 + 输入自动检测。

## 三、luongnv89/claude-howto code-review-specialist（模板范本）

- `templates/review-checklist.md` + `templates/finding-template.md`（位置/影响/严重度/Fix 示例）+ `scripts/analyze-metrics.py`。
- 借鉴点：双模板 + finding 模板（本 Skill 已有 patch-template，可对照增强）。

> 出处：github.com/anthroos/claude-code-review-skill、github.com/googs1025/code-review-skill。
