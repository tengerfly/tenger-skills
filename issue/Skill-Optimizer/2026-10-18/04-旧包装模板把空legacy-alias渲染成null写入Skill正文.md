# 旧包装模板把空 legacy-alias 渲染成 null 并写入 Skill 正文

> 归属 skill：`auto-test`（12 个 legacy-wrapper 中唯一空别名者） ｜ 日期：2026-10-18 ｜ 来源：体检

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P2 |
| 标签 | `术语文案` / `产物格式` |
| 优化状态 | 处理中（本轮已修 Test/auto-test/SKILL.md） |

## 现象

`Test/auto-test/SKILL.md`（Contract Compatibility Layer 的 Purpose 段）原文：

> Preserve the mature capability of `null` while exposing it through the v2 Skill contract.

其余 11 个 legacy-wrapper 此处渲染为各自旧名（如 Skill-Optimizer、Code-Review），只有 auto-test 的 `metadata.legacy-alias` 是 YAML null，于是模板把 null 当字符串写进正文。任何模型/人读到都会困惑「null 是什么能力」。

## 跟踪与证据

- 证据：`git grep -n "mature capability of"` → 13 处，12 个 wrapper 中 11 个正常，`Test/auto-test/SKILL.md:162` 为 null
- 根因与归属：已确认——包装模板对空别名缺少兜底（应回退到当前 name 或省略该句）；机器校验器只校验章节存在，不校验正文占位符。
- 影响：语义噪音 + 对外呈现不专业；不阻断执行。
- 回退方式：单行文本还原。

## 期望 vs 实际

- **期望**：正文自动使用当前 skill 名（auto-test），或空别名时不渲染该句。
- **实际**：渲染出 null。

## 修复方向

1. 本轮：把该句改为 auto-test（frontmatter 的 `legacy-alias: null` 按契约保留，表示无历史别名）。
2. 防复发（建议后续）：在 skill 契约校验中增加「正文不得出现 mature capability of null」的机械检查，或修正包装脚本模板；本轮先记 issue，不新增校验器改动。

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | 未沉淀（处理中） |
| 沉淀位置 | 本轮进行中：Test/auto-test/SKILL.md 单行 |
| 忽略理由 | — |