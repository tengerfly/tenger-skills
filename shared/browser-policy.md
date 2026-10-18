# 浏览器工具两级策略（公共约定）

> 权威源：本文件（单一事实源）。各 skill 正文只声明自身级别与动作；检测顺序、两级行为、报错文案与「无工具时如何获取」（§五）以本文件为准，不再各自重复定义。旧版曾把权威源写成仓库根 README「浏览器工具策略」，该节已随 README 重构移除（2026-10-18 核对），本文件为现行唯一出处。

## 一、检测顺序

`Playwright → browser-use → 其他（如 MCP 浏览器工具 mcp__browser__*、agent-browser）`。列举不穷举：凡当前环境可用的、能驱动真实浏览器打开页面/交互/截图的工具均算。**当前会话工具列表里看不到 ≠ 环境没装**：先按 §五 检查 DSH 环境是否已接入、插件是否加载，再判定「无浏览器工具」。

## 二、两级行为

| 级别 | 行为 |
|---|---|
| 硬依赖 | 开工前必检；任一可用即开工（记作走查/校验工具）；全部不可用 → 先按 §五 获取（DSH 环境）；仍不可用才报错并要求安装后重跑，不产出任何交付物 |
| 软检测 | 有则用（执行对应辅助步骤，如选型版本核验），无则跳过该步骤，不阻塞主流程 |

## 轻量实现与验收的边界

按 `shared/execution-profiles.md` 执行的低风险 Frontend-Dev 可在缺少浏览器时实现代码并跑现有确定性测试，但只能交付“待视觉/交互验证”，不能宣称视觉通过。UI 自写 B 草稿按其独立 SOP 处理。Prototype-Review / UI-UX-Review / Fidelity-Review 等专业验收的真实浏览器硬依赖不变，标准/完整前端流程与 Superdesign A 路径也不变。

## 三、级别清单

- **硬依赖**：Prototype-Review / UI-UX-Review / Fidelity-Review / Frontend-Tech-Design / Frontend-Dev / auto-test（L2 视觉层；其 L0/L1 确定性层无浏览器可跑）
- **软检测**：Tech-Review / Backend-Tech-Design
- **不涉及**：其余 skill 不做检测（仅截图增强的如 UI-UX-Design：浏览器不可用时以替代手段核验，并在产物注明）

## 四、硬依赖报错文案模板

```
【环境错误】未检测到任何可用浏览器工具（检测顺序：Playwright → browser-use → 其他）。
请安装任一浏览器工具后重跑；安装前本 skill 不产出任何交付物。
DSH 桌面版：先按仓库根 shared/browser-policy.md §五 接入并验证 MCP 浏览器工具或 Playwright，再重跑。
```

> 注：midscenejs 仅为 auto-test / Testing 样式视觉断言的可选增强（需装依赖 + 模型配置），不属于检测链；不可用时降级并在 Scope Gate 说明。

## 五、DSH 环境：如何获得浏览器工具

> 本节只回答「当前会话检测不到浏览器工具时怎么办」，检测顺序与两级行为不变（见 §一/§二）。下列路径为 2026-10-18 本机实测（R42，DSH 桌面版 0.2.1-rc.2）；换机、升级后按同一套步骤复验，路径以实际安装为准。

### 5.1 首选：Chrome DevTools MCP 插件（已接入）

- **机制**：DSH 桌面版的 profile patch 追加一个 `@deepseek-ai/dsh-mcp-client` 插件条目，stdio 拉起本机 npx 缓存的 `chrome-devtools-mcp`（1.0.1），模型侧获得 `mcp__browser__*` 工具（29 个：`navigate_page` / `take_screenshot` / `take_snapshot` / `click` / `fill` / `fill_form` / `evaluate_script` / `list_console_messages` / `list_network_requests` / `lighthouse_audit` 等）。
- **配置文件**：`C:\Users\15136\.dsh\profiles\desktop\cordis.patch.yml`（用户级配置，不在本仓，不要提交）。已有 `id: mcp-browser` 条目时不要重复插入。
- **最小可用配置**（追加为顶层数组的一个 `- insert:` 条目；本机实际字节见该文件 2026-10-18 的 browser plugin 注释段）：

```yaml
- insert:
    - id: mcp-browser
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: browser
        transport: stdio
        command: 'C:\Program Files\nodejs\node.exe'
        args:
          - 'C:\Users\15136\AppData\Local\npm-cache\_npx\15c61037b1978c83\node_modules\chrome-devtools-mcp\build\src\bin\chrome-devtools-mcp.js'
          - '--headless'
          - '--isolated'
          - '--no-usage-statistics'
          - '--no-performance-crux'
        env:
          SystemRoot: 'C:\Windows'
          PROGRAMFILES: 'C:\Program Files'
          PROGRAMFILES_X86: 'C:\Program Files (x86)'
          LOCALAPPDATA: 'C:\Users\15136\AppData\Local'
          APPDATA: 'C:\Users\15136\AppData\Roaming'
          TEMP: 'C:\Users\15136\AppData\Local\Temp'
          TMP: 'C:\Users\15136\AppData\Local\Temp'
          USERPROFILE: 'C:\Users\15136'
          HOME: 'C:\Users\15136'
          PATH: 'C:\Program Files\nodejs;C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem'
          CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS: '1'
          CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS: '1'
        toolCallTimeoutMs: 180000
        failOnStartupError: false
```

- **生效方式**：保存后 DSH 对 profile patch 做 HMR 热加载（本机实测无需重启）；未生效时重启 DSH 桌面版再验。
- **先决条件**：系统 `node.exe` 可用、本机已装 Chrome；`chrome-devtools-mcp` 需已在 npx 缓存（其它 coding agent 的 MCP 配置拉起过一次即会缓存），缓存路径以实际 `_npx\<hash>\node_modules\chrome-devtools-mcp` 为准。

### 5.2 验证（三步都过才算可用）

1. **工具可见**：`run_code` 内 `await tools.mcp__browser__list_pages({})` 返回页面列表（不是 undefined/报错）。
2. **页面可控**：`tools.mcp__browser__navigate_page({url})` 后 `take_screenshot({})` 或 `take_snapshot({})` 返回真实页面/截图。
3. **服务进程在跑**（可选交叉核对）：`Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -like '*chrome-devtools-mcp.js*' }` 有输出。

```powershell
# 3 的一行版（2026-10-18 实测）
Get-CimInstance Win32_Process -Filter "Name='node.exe'" |
  Where-Object { $_.CommandLine -like '*chrome-devtools-mcp.js*' } |
  Select-Object ProcessId, CommandLine
```

> 检测纪律：**「当前会话工具列表里看不到」不等于环境没装**；先查插件是否加载/生效（5.1/5.2），再判无浏览器工具，避免把「没接上」误记成「没有」而让 L2/还原度评审长期 BLOCKED。

### 5.3 已知限制：单实例 = 单浏览器，不能多 agent 并行

- 一个 MCP server 实例只驱动一套浏览器/页面集合；同一 profile 下多个 agent 共用同一实例 ⇒ 互抢页面（A 的 `navigate_page` 会换掉 B 正在截图的页），证据互相污染。
- **处置**：①浏览器阶段串行——并行编排时把 L2 视觉 E2E、还原度评审、技术方案浏览器核验排成串行队列；②确需真并行时，其中一方改用 Playwright 独立实例（见 5.4）。
- 检测通过只代表「有浏览器可用」，不代表「可以和其他 agent 同时用」。

### 5.4 备选：本机 Playwright（已装，独立实例）

- **位置**：`C:\Users\15136\AppData\Local\npm-cache\_npx\e41f203b7505f1fb\node_modules\playwright`（1.63.0，chromium 已安装）。
- **用法**：`run_code` 的 `process.env` 初始为空，启动前先补 `TEMP`/`TMP`（视需要再补 `USERPROFILE`/`HOME`/`PATH`，参照 5.1 的 env 段）再 `chromium.launch()`；不要指望继承 shell 环境。
- **适用**：需要与 MCP 浏览器并存、要脚本化多视口截图或批量比对时；常规单页走查仍首选 MCP（少一层启动与环境成本）。

### 5.5 卸载 / 回滚

1. 备份：`Copy-Item "$env:USERPROFILE\.dsh\profiles\desktop\cordis.patch.yml" "$env:USERPROFILE\.dsh\profiles\desktop\cordis.patch.yml.bak"`。
2. 删除 `cordis.patch.yml` 中 `- insert:` 的 `id: mcp-browser` 整段，其余配置不动。
3. 保存后等 HMR（或重启 DSH），按 5.2 第 1 步复验 `tools.mcp__browser__*` 不再出现即回滚成功。
4. 回滚后浏览器工具按 §一 重新检测；硬依赖 skill 回到「全部不可用 → 报错要求安装」行为（行为不变）。
