# 单浏览器 MCP 实例不支持多 agent 并行浏览器阶段 ⇒ 页面互抢，证据存在污染风险

> 归属 skill：`WorkFlow`（并行派单编排）＋公共约定 `shared/browser-policy.md` ｜ 日期：2026-10-18 ｜ 来源：埋点（真实项目 knowledge-bases 第 42 轮：auto-test L2 与 Fidelity-Review 同轮并行）

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P2 |
| 标签 | `工具依赖` / `流程缺陷` |
| 优化状态 | 处理中（限制与处置已文档化，待下一次并行轮观察；未标已沉淀） |

> 定级理由：本轮**未观察到实际证据污染**（两个 agent 的截图/报告尚未回传交叉核对），且已有明确规避手段（串行 / Playwright 独立实例）；但随并行度提升会变成系统性证据污染，故登记为 P2 并文档化，不升级为 P1。

## 现象

- 第 42 轮并行编排中，auto-test L2 与 Fidelity-Review 还原度评审同轮运行，二者共用同一个 MCP browser server：`cordis.patch.yml` 只有一个 `id: mcp-browser`（`serverName: browser`）条目，`chrome-devtools-mcp` 以 `--headless --isolated` 单实例拉起，**一个 MCP server 实例 = 一套浏览器/页面集合**。
- 后果：任一 agent 的 `navigate_page` 会替换另一个 agent 正在截图的页面；`list_pages` / `select_page` 看到的是共享页面列表（2026-10-18 18:35 实测 `list_pages` 返回 `1: http://127.0.0.1:5173/kb/...` 单页），并发下截图证据与操作对象可能错位。
- 该限制此前未写入任何共享约定；检测通过（「有浏览器」）被默认等同于「可以并发使用」。

## 跟踪与证据

- 原问题 ID / 来源项目与版本：新增条目；关联 `docs/技能体系试跑记录-20261018.md` R42 记录
- 发现时间 / 相关步骤：2026-10-18 18:35（R42 反哺轮环境核验）
- 脱敏证据：`cordis.patch.yml` 单 `mcp-browser` 条目；`chrome-devtools-mcp ... --headless --isolated` 进程（PID 40728）；`tools.mcp__browser__list_pages({})` 返回共享页列表
- 责任方 / 下一动作 / 修复判据：WorkFlow（并行派单声明）＋ shared/browser-policy（限制与处置）—— 本轮已文档化；判据 = 含浏览器阶段的并行派单显式声明「浏览器阶段串行」，或其中一方改用 Playwright 独立实例；复验 = 下一次并行浏览器阶段无「页面被切走 / 截图对象错位」证据。
- 根因与归属：**已确认**——架构限制（单 MCP server 单浏览器），非配置错误；检测链未区分「可用」与「可并发」。
- 复核证据 / 未验证项：本轮为并行运行中的风险观察，尚未拿到「互抢导致证据错位」的实际样本；串行处置也待下一次并行轮验证。
- 回退方式：文档改动可 git diff 回退；未改 WorkFlow 正文主流程。

## 期望 vs 实际

- **期望**：并行编排中若多个 agent 需要浏览器，派单时明确「浏览器阶段串行」或分配独立实例；检测结果附并发使用约束。
- **实际**：共享约定只说「任一可用即开工」，没说「同一实例不可并发」；R42 两 agent 同轮并行，风险实际存在。

## 修复方向（本轮已落地）

1. `shared/browser-policy.md` §5.3：写明「单实例 = 单浏览器，不能多 agent 并行」+ 两种处置（浏览器阶段串行 / Playwright 独立实例），并明确「检测通过 ≠ 可并发使用」。
2. WorkFlow 正文暂不改：本轮无实际污染样本，先在公共约定登记限制；下一次并行轮若再现，再进 `workflow/SKILL.md` 并行边界条款与 `Other/Skill-Optimizer/references/known-issue-patterns.md`。

## 双向落点

| 方向 | 目标 skill | 落点 |
|---|---|---|
| A · 防复发 | WorkFlow（并行边界） | 派单时声明浏览器阶段串行；共享限制见 `shared/browser-policy.md` §5.3 |
| B · 检出力 | WorkFlow（编排器无独立上游评审方） | 待实际样本后进 `Other/Skill-Optimizer/references/known-issue-patterns.md`：并行轮检查浏览器阶段是否串行/独立实例 |

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | 未沉淀（处理中） |
| 沉淀位置 | `shared/browser-policy.md` §5.3 |
| 忽略理由 | — |
