---
name: auto-test
description: AI 代码全景验收测试编排与修复闭环（分层 L0-L4）。AI 编码完成后的自动化验收：确定性门禁（install/typecheck/lint/单测/build）→ API 契约与 live 主链 → AI 视觉 E2E（状态注入 + mock 数据全流程覆盖）→ 探索性测试 → 专项压测（负载/压力/稳定）、安全扫描、兼容/无障碍（按需求信号触发）；产出带证据的测试报告、覆盖率门禁与修复任务卡，驱动「发现问题→AI 修复→fresh-agent 回归」正向循环。触发：测试 AI 写的代码、验收、跑全流程、回归、找 bug、E2E、修复后复测、覆盖率检查、压测、负载测试、性能测试、安全扫描。
compatibility: ZCode / Claude Code 等 coding agent。需要 Bash；L2 需浏览器工具（Playwright/Midscene 任一）；auto-test 引擎 CLI 或 MCP 可用时自动切换引擎模式。
license: Proprietary
metadata:
  author: auto-test-project
  version: "0.1.0"
  spec: "https://agentskills.io"
---

# Auto-Test：AI 代码验收测试与修复闭环

> **Iron Law：证据先于声明，永远。** 没有本次实测证据（命令输出 / 截图 / 实测耗时），禁止宣称「通过 / 已修复 / 没问题」。
> **Iron Law 2：分层短路。** L0 未过不跑 L1，L1 未过不跑 L2——错误越晚发现代价越高，AI token 只花在确定性检查之后。
> **Iron Law 3：真实优先，mock 兜底。** 被测项目已支持真实 AI/外部服务时，默认打**真实链路**；仅当接口不通、无凭证、服务不可用时才降级 mock，且必须在报告「覆盖边界声明」中逐条列出降级项。把项目核心 AI 链路整体 mock 掉 = 核心功能零覆盖。

## 一、定位与边界

**角色**：验收测试编排者。把「AI 说写好了」变成「机器证明能用」：分层测试 → 证据报告 → 修复任务卡 → 回归闭环。

| 本 skill 负责 | 不负责（归谁） |
|---|---|
| 分层执行测试、收集证据、判定通过与否 | 写代码修复（回归时交编码 agent） |
| 生成用例库（可重复执行的资产） | 改需求 / 写 PRD（基准来源方） |
| 生成修复任务卡并驱动回归循环 | 代码质量评审（归 Code-Review 类 skill） |
| 状态覆盖率与门禁判定 | 单测编写（开发自测；缺测时本 skill 登记风险并按需补关键层） |

**基准来源**：对错基准 = PRD 验收标准（AC）/ 需求文档；视觉基准 = 设计稿（缺失回退原型并**明示降级**）；接口基准 = 接口文档 / OpenAPI 契约。**零臆断**：预期必须有来源，拿不准标 `【设计假设】` 并登记风险。

## 二、模式探测（每次开工第一步）

1. **引擎模式**：`auto-test` CLI 在 PATH 或 MCP 工具（如 `auto-test run / get_report`）可用 → 全部执行委托引擎，本 skill 只负责：解释报告、生成/消化修复任务卡、把握回归轮次纪律。
2. **会话模式**（引擎未部署时的完整降级）：由当前 agent 按第三节流程亲自执行，产物格式与引擎模式完全一致（`.spec/auto-test/`），保证未来无缝迁移。

判定方法：`command -v auto-test`；或检查 MCP 工具列表。两种模式都走同一套铁律与产物规范。

## 三、主流程（7 步）

> 先计划后执行，禁边测边想。◉ = 强制暂停等用户确认。

1. **输入解析**：项目位置 + 启动命令（缺则必问）；读 PRD/需求文档提取验收标准与**状态机**（无状态机则按页面清单盘点，并登记「无状态机基准」风险）；读上轮 `.spec/auto-test/` 产物（有则进入回归模式，只跑上轮失败 + 全量冒烟）。
2. **L0 确定性门禁**（秒~分钟级，零 token）：install → typecheck → lint → 单元测试 → build。任一失败**立即停止**，输出失败证据与修复任务卡，不进入 L1。
3. **L1 契约冒烟**（分钟级）：按接口清单对关键路径做请求级断言（状态码 / 结构 / 关键字段）。失败即停。
4. **◉ 计划确认**：呈现用例清单（编号 + 覆盖的状态/迁移 + mock 方案 + 慢接口阈值），确认后放行。回归模式跳过此步。
5. **L2 视觉 E2E**：按三段式用例（`setup 注入 → act 操作 → assert 断言`）逐条执行；全状态 + 全点击 + 三态必测（加载/空/错误）；样式问题与异常**必截图**；监听 console 报错与网络（慢接口必记：>1000ms 慢 / >3000ms 很慢 / >5000ms 严重）。细则见 [references/layered-testing-guide.md](references/layered-testing-guide.md)，用例编写见 [references/case-authoring-guide.md](references/case-authoring-guide.md)。
6. **L3 探索性测试（可选）**：无预设脚本自由探索找 bug（乱点乱填、非常规路径）；沙箱内执行；只出报告不阻断。被测系统含不可控外部副作用（发邮件/支付）时必须先 mock。
7. **L4 专项测试（信号触发，可选）**：默认不跑；命中需求信号才执行——性能/并发关键词 → 负载/压力/稳定（负载模型与指标见 [references/specialty-testing-guide.md](references/specialty-testing-guide.md)）；敏感数据/对外接口 → 安全扫描（依赖审计 + SAST 快扫，DAST 可选）；多端/多浏览器 → 兼容矩阵；无障碍要求 → axe 扫描。结果只分级报告，P0（如压测下数据损坏/错误率爆表）才阻断。
8. **汇总与门禁**：计算状态覆盖率 / 迁移覆盖率 / 元素点击率（见 [references/coverage-gate.md](references/coverage-gate.md)）；L4 有执行则附专项指标表；产出报告（[assets/report-template.md](assets/report-template.md)）+ 每条缺陷一张修复任务卡（[assets/bug-card-template.md](assets/bug-card-template.md)），归档 `.spec/auto-test/`。

## 四、修复闭环（本 skill 的灵魂）

```
报告全绿 → 结束
报告有缺陷 → 生成修复任务卡 → 交编码 agent 修复（fresh：不带本轮测试上下文）
          → 回归：重跑全量用例（不是只跑失败项）→ 全绿结束 / 计数+1 继续
          → 轮次上限 3 轮 → 超限停下，升级人工，输出震荡分析（哪两个缺陷在互相打架）
```

**fresh-agent 回归纪律**（防「AI 测 AI」互相糊弄）：
- 回归执行者不得携带上轮的怀疑点、推测结论、修复意见——只给它：原始验收标准 + 用例库 + 当前代码；
- 确定性层（L0/L1）的失败，任何 AI 判断**无权覆盖**；
- 每轮回归都是新的一轮完整证据，禁止沿用上轮截图/结论。

## 五、产物与目录约定

```
.spec/auto-test/
├── 用例库/                 # 可重复执行的资产（三段式 YAML/MD）
│   ├── TC-<模块>-<序号>.md
│   └── 状态机清单.md        # 状态×迁移×用例映射（覆盖率计算依据）
├── 报告/
│   └── run-<日期>-<轮次>.md  # 含覆盖率表 + 缺陷明细 + 覆盖边界声明
├── 任务卡/
│   └── BUG-<日期>-<序号>.md  # 机器可读、AI 可执行的修复任务
└── evidence/
    ├── screenshots/         # <页面>_<问题>_<序号>.png
    ├── console/  network/   # console 日志与 HAR
    └── videos/              # 失败用例录屏（可选）
```

**覆盖边界声明（强制）**：零缺陷也必须写清——覆盖了什么 / 未覆盖什么 / 残余风险。禁只写「未发现问题」。

## 六、缺陷分级与处置（P0-P3 + Action）

| 级别 | 定义 | Action |
|---|---|---|
| **P0** | 崩溃/白屏/核心流程不可用/数据丢失风险/安全漏洞 | 阻断交付，立即生成任务卡修复 |
| **P1** | 功能错误/主要样式偏差/很慢及以上接口/验收闭环缺失 | 应修，本轮闭环内修复 |
| **P2** | 次要样式/文案/体验问题/慢接口 | 建任务卡，本轮或跟进修 |
| **P3** | 建议/风格 | 记录不建卡 |

每条缺陷 = 现象 + 复现步骤 + 期望/实际 + 证据 + 关联用例号。格式见 [assets/bug-card-template.md](assets/bug-card-template.md)。

## 七、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 没跑 L0 直接开浏览器测 | 分层短路，Iron Law 2 |
| 只测主流程，状态靠「应该能到」 | 状态注入构造前置，见 case-authoring-guide |
| mock 了被测系统自己的接口 | Mock 边界铁律：只 mock 外部依赖与异常态 |
| 轮询断言字段凭想象写（如假定 shots[].status 存在） | 断言结构先验证：先 GET 一次看真实响应，再写轮询条件 |
| 重试风暴：短间隔连发重试后拿旧失败证据判死 | 异步任务重试间隔 ≥ 单任务典型时长 1/5；判死只认「新于上次重试」的证据（时间戳/计数） |
| 多项目共用同一 LLM key 并发互打 429 | 探测到 429 → 各项目测试串行化，或显著降速 |
| 重启服务后立即回归 | **验证进程真的换了**：端口确已释放再启动、健康检查通过、最好有代码级标志位；后台任务停止会遗留孤儿进程（实测两次假回归根因） |
| 状态全绿就宣布通过 | **产物级证据**：成功状态之外核验物理产物（文件存在/大小/ffprobe 体检）——实测曾「ALL-PASS」实为旧代码的脏数据补完 |
| 共享库（libs dist）改了只重启一个消费进程 | 构建产物被多进程消费时全部重启，否则新旧代码混跑 |
| 缺陷无截图/无复现步骤 | 证据先于声明，不合格重出 |
| 修复后只跑上次失败的用例 | 全量回归，防「改 A 坏 B」 |
| 复用时沿用上轮结论 | 每轮 fresh 证据，禁沿用 |
| 零问题只写「未发现问题」 | 覆盖边界声明，强制 |
| 「should pass / 大概没问题」 | Gate：说出证明命令 → 跑 → 读输出 → 才能声明 |
| E2E 堆到最多、单测为零 | 反冰淇淋反模式：E2E 只覆盖关键链路 |
| 用例跑两遍覆盖路径不一样 | 用例是资产，固化为可重复执行的文件 |

## 八、资源清单（按需加载，禁一次全读）

| 文件 | 何时读 |
|---|---|
| [references/layered-testing-guide.md](references/layered-testing-guide.md) | 执行 L0-L3 前：各层命令模板、浏览器工具降级链、监听规范、live 主链 E2E 规范 |
| [references/case-authoring-guide.md](references/case-authoring-guide.md) | 编写用例前：三段式格式、状态注入手法、mock 边界铁律 |
| [references/coverage-gate.md](references/coverage-gate.md) | 汇总阶段：覆盖率计算与门禁阈值 |
| [references/fix-loop-guide.md](references/fix-loop-guide.md) | 进入修复闭环时：任务卡投喂方式、fresh-agent 规则、轮次状态机 |
| [references/specialty-testing-guide.md](references/specialty-testing-guide.md) | 命中 L4 信号时：负载/压力/稳定模型、指标阈值、安全扫描、兼容/无障碍 |
| [assets/case-template.md](assets/case-template.md) | 写用例时的模板 |
| [assets/bug-card-template.md](assets/bug-card-template.md) | 出缺陷时的任务卡模板 |
| [assets/report-template.md](assets/report-template.md) | 汇总时的报告模板 |

**沉淀机制**：每次翻车（漏测/误判/flaky）沉淀一条到第七节对照表或对应 reference；checklist 从 5-6 条起步，只增不改。
