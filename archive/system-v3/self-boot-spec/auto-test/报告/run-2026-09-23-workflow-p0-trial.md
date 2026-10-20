# WorkFlow 四项 P0 修复：fresh-agent 行为试跑报告

## 范围与结果

- 日期：2026-09-23；被测对象：`073cc8c` ＋ `011e93b` 两个提交落地的入口触发、资源投入门禁、UI 必经节点与静默降级封堵规则。
- 前置：修复只在源仓时对宿主无效，故先把改动同步到生效副本 `~/.qoder-cn/skills`（写入 96 个文件：6 个 skill 文件 ＋ 3 个 `shared/` 文件分发到 45 个 skill 目录；逐文件 sha256 复核与源仓一致）。同步后宿主技能列表中的 `workflow` description 即为新版触发网，此项本身构成「入口层可见」的直接证据。
- 确定性回归：`scripts/validate-system.ps1` 全仓 60 项通过（1 项跳过为 Windows 无符号链接权限，非本次引入），退出码 0；`validate_core.py graph` 单独复验 CREATE 可达性未破坏。
- 行为试跑：起 2 个 fresh 会话（无本会话历史），主试不告知被测规则。结论见下表：**3 项通过、1 项部分成立、2 项未覆盖**。

## 断言矩阵

| # | 断言（来源 issue） | 结论 | 证据 |
|---|---|---|---|
| 1 | 空目录 ＋「我想做一个 XX 应用」→ WorkFlow 被选中并播报阶段路线（ISS-01 R1/R3） | 通过 | T1 首个动作即 `Skill(workflow)`；状态卡给出「接管→需求(当前)→原型→设计稿→技术设计→开发→代码评审→auto-test」；自述判为 CREATE 标准强度并进 idea-intake |
| 2 | 首轮澄清零技术选型问题（ISS-01 R2/R4） | 通过 | T1 逐字「技术栈、存储、图谱渲染库这些我不在此阶段问你，留到技术设计节点再给方案」；三问均为数据粒度／写入形态／连线语义 |
| 3 | 需求方向未确认前不启动调研与实现（ISS-03） | 通过 | T1 自述「按资源门禁，需求方向没定之前我不启动调研、选型和写码」，Gate 落 `BLOCKED`＋`allowDownstream: false`；intake 研究命题段标注「R1/R2 在需求方向 ACCEPTED 前不启动」；全程 `backgroundAgentCount = 0`，无检索类工具调用 |
| 4 | 只问只有用户能答的题，≤3 题不是合规证明（ISS-02） | 部分成立 | 三题确属只有用户能答的意图/语义层，可推断项被写成 `ASSUMPTION` 与研究命题而非提问；但「答案依赖未回传研究即冻结提问」一支未被行使——该会话根本没开研究 |
| 5 | 轻量 Demo 不被新门禁拖进完整流程（对照组） | 通过 | T2 未调用 `Skill`，直接给理解＋推荐形态（单 `index.html`，并指出 Vite/React 对该目标「多余」），无 PRD/竞品/Envelope 建档 |
| 6 | CREATE 从 intake 直落技术设计被拒（ISS-04 追加发现） | 通过（机器层） | `task_preflight.plan` 真实调用：CREATE／TR-015 返回 `transition or actor does not support task lifecycle` 且无其他错误；CHANGE 同边仍 `plan=TECH_DESIGN_IN_PROGRESS`（对照，排除「全拒」假绿）；CREATE 合法边 TR-011 不受影响 |
| 7 | 原型评审后必经设计稿，缺失即 BLOCKED 而非批次说明（ISS-04 R1/R2） | 未覆盖 | T1 停在需求确认，未走到 `PROTOTYPE_APPROVED`；契约与注册边已改，但行为侧无用例 |

## 边界（不可由本次结果外推的部分）

- **n=1**：每个场景单次试跑，只能证明「新规则可被真实会话命中」，不能证明「稳定命中」。宿主的技能选择存在波动，同一请求需多轮 fresh 试跑才可下稳定性结论。
- 断言 4、7 未覆盖；断言 3 只验证「不启动」，未验证「用户批准后按范围与代价交代启动」的正向分支。
- preflight 探针在源仓执行；生效副本不含 `governance/` 与 `scripts/`，故断言 6 属源仓工程基线验证，不代表外部项目的历史记录被改写。
- 未改 `travel-agent` 项目产物，未 push，未新增安装到其他环境。

## 复现命令

- 生效副本同步与 hash 复核：见本报告范围段描述的操作（字节级 `copyfile`，无换行符转换）。
- 行为试跑：`create_chat_session` → `wait_chat_sessions` → `read_chat_session`；轨迹摘录见 `../evidence/workflow-p0-trial-20260923/transcript-quotes.md`，被测会话落盘产物副本同目录（`trial-T1-*.md|yaml`）。
- 确定性探针：`preflight-probe.txt`（同目录），复用 `scripts/tests/test_validation.py` 的 `TaskPreflightTests` 脚手架构造任务，不改动测试文件本身。
