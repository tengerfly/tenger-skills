# auto-test —— CONTEXT（术语 + 决策日志）

## 一、术语表

| 术语 | 英文 | 含义 | 边界 |
|---|---|---|---|
| 分层短路 | Layered Short-Circuit | L0 未过不跑 L1、L1 未过不跑 L2；AI token 只花在确定性检查之后 | 不是「全层都跑一遍再说」 |
| 确定性门禁 | L0 Gate | install → typecheck → lint → 单测 → build，零 token 秒~分钟级 | 不是可选建议 |
| 三段式用例 | Three-Phase Case | setup 注入 → act 操作 → assert 断言；用例是可重复执行资产 | 不是一次性操作记录 |
| fresh-agent 回归 | Fresh-Agent Regression | 回归执行者不带本轮怀疑点/结论/修复意见，只给标准+用例库+代码；全量重跑 | 不是只跑失败项 |
| 覆盖边界声明 | Coverage Boundary Statement | 零缺陷也必须写清覆盖/未覆盖/残余风险 | 不是「未发现问题」一句话 |
| 修复任务卡 | Bug Card | 每条缺陷一卡：现象+复现+期望/实际+证据+关联用例号，机器可读可执行 | 不是文字描述 |
| 引擎/会话双模式 | Engine / Session Mode | auto-test 引擎 CLI 或 MCP 可用则委托引擎，否则当前 agent 按同套铁律亲自执行，产物格式一致 | 两种模式产物互通 |

## 二、与仓库体系的关系

- 主链定位：Workflow ⑭ 测试节点（接替 Testing——Testing 已于 2026-09-22 归档，旧请求重定向 auto-test；源码仅作只读历史）。
- 产物：`.spec/auto-test/`（用例库 / 报告 / 任务卡 / evidence）。
- 兄弟 skill：Fidelity-Review（L2 内嵌还原检查）、Bug-Fix（可运行性问题转诊断修复闭环）、Code-Review（静态评审互补）。
- 项目资料：`project/` 为企业级 AI 自动化测试平台 v0.1（待评审）的项目计划 / 竞品分析 / 旧问题日志，只作研究参考，不参与执行；执行入口仍是本目录 `SKILL.md`。

## 三、决策日志

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 2026-09-19 | 从 auto-test 项目仓（当时本机生效副本）复制入本仓，成为源仓库管理副本；入仓适配三处：L2 增「有设计稿时内嵌 Fidelity-Review 还原检查（视觉以设计稿为唯一应然）」、资源清单补仓库根 shared 四约定与兄弟 skill、新增 §九 运行问题埋点（对齐本仓统一口径）；version 0.1.0→0.1.1 | 用户要求：auto-test 加入当前仓库并在流程中替换 Testing（Testing 源码不动；Testing 已于 2026-09-22 归档，旧请求重定向 auto-test）；Fidelity 内嵌保持原 ⑭ 还原闭环不断链 | ✅ 已确认 |
| D-02 | 2026-10-18 | 旧独立项目（原仓库远端 https://github.com/tengerfly/auto-test，2026-09-18）的项目计划 / 竞品研究 / 问题日志迁入 `Test/auto-test/project/`（文件名统一、正文旧 `.spec/` 路径改同目录可达写法）；删除 `docs/auto-test-legacy/` 整套归档（含已被取代的旧 skill 骨架）；修掉 `SKILL.md` 中 legacy-alias 渲染出的 `null` 占位（改为 auto-test；frontmatter 的 `legacy-alias: null` 是契约允许的 YAML null，保留不动（已被 D-03 修订为 "Testing"）） | 用户 2026-10-18 反馈：auto-test 被改成 auto-test-legacy 不可接受，要求体系可直接在其他地方使用；旧项目资料有独立价值但不该标 legacy 埋进 docs；`null` 是自动包装模板占位缺陷，不是能力名 | ✅ 已确认 || D-03 | 2026-10-18 | 按评审 D-13：frontmatter `legacy-alias` 由 null 改为 "Testing"（与 registry legacyAliases 对齐；D-02「保留不动」的结论据此修订） | 宿主展示不再出现 null 占位，历史名可检索 | ✅ 已确认 |

## 四、待决问题

无。
