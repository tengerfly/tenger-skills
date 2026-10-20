# 浏览器工具「获取途径未文档化」⇒ 当前会话看不见就判无工具，L2 / 还原度评审长期 BLOCKED

> 归属 skill：`auto-test`（L2 视觉层，同类影响 Fidelity-Review / Frontend-Dev / Frontend-Tech-Design / UI-UX-Review）＋公共约定 `shared/browser-policy.md` ｜ 日期：2026-10-18 ｜ 来源：埋点（真实项目 knowledge-bases 第 42 轮：浏览器能力补齐）

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P1 |
| 标签 | `工具依赖` / `流程缺陷` |
| 优化状态 | 处理中（文档已补，待下一次 fresh 会话的 L2 / 还原度评审复验；未标已沉淀） |

> 定级理由：不损坏产物，但**换会话/换机器必然复现**；把「能装但没接上」误判成「环境没有」，导致 L2 与还原度评审整层 BLOCKED（R41 最终 Gate=CONDITIONAL）。这类误判会直接损失一层验收能力，不是轻微建议。

## 现象

- knowledge-bases 第 41 轮（2026-10-18）：auto-test L2 = **BLOCKED**，理由「无浏览器工具」；同轮 frontend-dev「浏览器工具全无 ⇒ 报错停」与「本环境无浏览器、一期只做 RTL+构建」直接冲突（F-6），子 agent 只能违规或全停。最终交付 Gate=CONDITIONAL，L2 未执行。
- 第 42 轮核对：本机**并非没有浏览器能力**——npx 缓存的 `chrome-devtools-mcp` 1.0.1 可用，DSH 桌面版 profile patch 追加 `@deepseek-ai/dsh-mcp-client` 插件条目后，`run_code` 内可见 `tools.mcp__browser__*`（29 个浏览器工具）；另有 Playwright 1.63.0（chromium 已装）可作独立实例。
- 根因不是环境没装，而是检测链**只认「当前会话可见工具」且获取途径从未文档化**：`shared/browser-policy.md` §一 只写「Playwright → browser-use → 其他」，没有「看不到时去哪里拿、怎么验证、怎么回滚」；且该文件开头把权威源写成仓库根 README「浏览器工具策略」，而该节已在 README 重构（ec22f6c）中移除 ⇒ 检测链的权威源本身失效（失效指针）。

## 跟踪与证据

- 原问题 ID / 来源项目与版本：新增条目；关联 `docs/技能体系试跑记录-20261018.md` §2 F-6（浏览器硬门禁冲突）与 §3.1 L2 BLOCKED
- 发现时间 / 相关步骤：2026-10-18 18:30（R42 反哺轮）；R41 试跑收尾复核时归因
- 脱敏证据（2026-10-18 本机实测）：
  - `tools.mcp__browser__list_pages({})` 返回页面列表（`1: http://127.0.0.1:5173/kb/...`），工具可用；
  - `Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -like '*chrome-devtools-mcp.js*' }` 输出 `node.exe ...chrome-devtools-mcp.js --headless --isolated`（PID 40728）；
  - `C:\Users\15136\.dsh\profiles\desktop\cordis.patch.yml` 含 `- insert: - id: mcp-browser ... serverName: browser`；
  - `C:\Users\15136\AppData\Local\npm-cache\_npx\e41f203b7505f1fb\node_modules\playwright\package.json` 版本 1.63.0；
  - `git log -S "浏览器工具策略" -- README.md`：该节由 `0d25853` 引入、`ec22f6c` 重构移除，当前 README 无该节。
- 责任方 / 下一动作 / 修复判据：公共约定（`shared/browser-policy.md` §五 + §一/§四）＋ 5 个硬依赖 skill 浏览器段回指 —— 本轮已改；判据 = 下一次 fresh 会话在 L2 / 还原度评审开工时，按 §五 在 10 分钟内接通工具并通过 §5.2 三步验证；「当前会话工具列表里看不到」不再直接判 BLOCKED。
- 根因与归属：**已确认**——检测链只认当前会话可见工具，获取途径零文档；权威源指针失效放大了误判。
- 复核证据 / 未验证项：R42 工具面已实测可用（本机当前会话）；「文档能否让未见过的执行者自己独立接通」需下一次 fresh 会话验证，本轮不标已沉淀。
- 回退方式：文本改动集中在 `shared/browser-policy.md`、5 个 skill 浏览器段（含 2 个 references）、README「Browser tool policy」小节，可按 git diff 回退。

## 期望 vs 实际

- **期望**：硬依赖 skill 开工预检发现「当前会话没有浏览器工具」时，先按公共约定检查 DSH 环境是否已接入/插件是否加载、按步骤获取并验证；只有获取失败才报「环境错误」，而不是把可安装能力误判成不存在。
- **实际**：检测链只有顺序没有获取途径；R41 连续两层评审因此 BLOCKED，Gate 降为 CONDITIONAL。

## 修复方向（本轮已落地）

1. `shared/browser-policy.md`：新增 **§五 DSH 环境：如何获得浏览器工具**（5.1 cordis.patch.yml 最小配置、5.2 三步验证、5.3 单实例并发限制、5.4 Playwright 备选、5.5 卸载/回滚）；§一 检测顺序的「其他」显式含 MCP 浏览器工具并写明「工具列表看不到 ≠ 环境没装」；§四 报错模板补获取路径；开头权威源改为本文件（修 README 失效指针）。
2. 5 个硬依赖 skill 的浏览器段 + 2 个 references 各加一句**回指 §五**（不复述检测顺序/策略）。
3. `README.md` 补「Browser tool policy」小节指回 `shared/browser-policy.md`，恢复单一事实源。
4. 未实施（留待经验证的下一步）：行为层 eval 用例（输入「会话看不到浏览器工具」，判据 = 先给 §五 获取/验证路径，不得直接判 BLOCKED 收口）。

## 双向落点

| 方向 | 目标 skill | 落点 |
|---|---|---|
| A · 防复发 | 公共约定 `shared/browser-policy.md`（被 auto-test / Fidelity-Review / Frontend-Dev / Frontend-Tech-Design / UI-UX-Review 引用） | §五 获取/验证/回滚 + §一 检测链「其他」纳入 MCP 工具 + §四 报错模板 |
| B · 检出力 | auto-test（L2）+ Fidelity-Review（还原度评审） | 待行为层用例回流（issueRef 指回本文件）；本轮不标已沉淀 |

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | 未沉淀（处理中） |
| 沉淀位置 | 文本已改：`shared/browser-policy.md` §一/§四/§五、`README.md`「Browser tool policy」、5 个 skill 浏览器段 + 2 个 references 回指 |
| 忽略理由 | — |
