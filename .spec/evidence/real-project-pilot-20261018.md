# EVID-SYSTEM-ACCEPTANCE-PILOT · 真实项目试跑证据汇总（R41–R43）

> 状态：证据汇总，**不是批准、不是验收结论**。用途：为 GATE-SYSTEM-001 的 `clearanceCondition`（real project pilot）提供仓内可回查引用；pilot 是否满足要件，由授权 owner 在《体系验收记录》签字栏确认（AI 不得代判）。
> 生成：2026-10-20，由 Lead 起草（未参与被引用的试跑生产会话）。外部项目绝对路径按仓库规则**不写入 manifest**，仅在本汇总中作证据引用。

## 1. 试跑项目与口径

| 项 | 值 |
|---|---|
| 项目 | `knowledge-bases`（个人知识库 Agent，真实业务项目，独立 git 仓与 .spec） |
| 外部路径（证据引用，不入 manifest） | `D:\project\agent-project\knowledge-bases` |
| 试跑日期 | 2026-10-18（R41 / R42 / R43） |
| 仓内试跑记录 | [docs/技能体系试跑记录-20261018.md](../docs/技能体系试跑记录-20261018.md)（状态：进行中，第 42 轮；R43 不在其中） |
| 体系侧使用方式 | 试跑使用本仓 Skill 的宿主安装副本/链接（45 skills + shared） |

## 2. 轮次与结果（事实）

| 轮次 | executionId | 结果 | 证据来源 |
|---|---|---|---|
| R41 | `EXEC-20261018-KB-DEV-R41` | 13 模块 / 13 页落地；L0 **358** 用例全绿；L1 smoke **14/14**；code-review 两轮后 P0=0；auto-test Gate=**CONDITIONAL**（L2 无浏览器 BLOCKED、真实外部链路未验、release 未授权） | 试跑记录 §3.1 |
| R42 | `EXEC-20261018-KB-DEV-R42` | 补齐浏览器能力（DSH profile patch + chrome-devtools-mcp 29 工具），L2 / 还原度评审恢复可执行；本轮性质为补能力，不重跑项目验收 | 试跑记录 §4 |
| R43 | `EXEC-20261018-KB-DEV-R43` | L0 **56 文件 / 420 用例**全绿；L1 9/9；L2 PASS 且修复后回归复验 PASS；还原度 **6/6 P1 PASS**（独立）；code-review P0=0/P1=0；技术方案第 2 轮 PASS；业务项目 Gate **CONDITIONAL → PASS**；release/部署未授权 | 外部项目 .spec：workflow.yaml / DEC-20261018-R43-GATE-PASS / EVID-20261018-R43-VERIFY |

外部项目证据文件（sha256 由本会话独立复算，2026-10-20 核对）：

| 文件（外部） | mtime | 字节 | sha256 |
|---|---|---|---|
| `.spec/workflow.yaml` | 2026-10-18 21:23:33 | 145629 | `8232ff7b777a80c4c7b86b7007fd103ea2fe17506eeacc108bd8ae37704c5ba3` |
| `.spec/decisions/DEC-20261018-R43-GATE-PASS.yaml` | 2026-10-18 21:23:33 | 1189 | `f517da660b50c529893db271d2b1158be1b317661cd0da006d21badb9d7a8ad9` |
| `.spec/evidence/EVID-20261018-R43-VERIFY.md` | 2026-10-18 21:23:33 | 4091 | `60895acf4e5b2a048905d47ffd9adcfe2088bfb00c5b2aa4570781f8c35aac42` |

R43 关键字段（外部 workflow.yaml）：`state: TEST_PASSED`、`gate: PASS`、`allowDownstream: true`、`approvalRef: DEC-20261018-R43-GATE-PASS`、`revision: 2026-10-18T21:25:00+08:00-r43-pass`、`risk` 摘要 P0=0/P1=0；DEC 为 `status: APPROVED`、`approvedBy: product-owner`、`approvedAt: 2026-10-18T21:20:00+08:00`。

## 3. 边界与差异（必须与签字栏一并读）

1. **R43 是业务项目 Gate PASS，不是体系验收**：GATE-SYSTEM-001 的 `clearanceCondition` 要求授权 owner 对**体系**记录 acceptance，不能拿业务项目 PASS 代替。
2. **版本差**：R43 收口时点（2026-10-18T21:25）早于本仓 HEAD `47d6908`（2026-10-20 08:28:47）。10-19～10-20 的改动（评审上下文隔离硬性化、安装器 copy/link、全体系评审修复）**未被真实项目试跑覆盖**；若按严格口径，需由 owner 决定是否要求版本对齐后重跑一轮。
3. **证据角色差异**：外部项目该证据 `role: verification` 不在本仓 `evidenceRoles` 枚举内；若在本仓登记，口径应写 `role: inspection`（见《体系验收记录》§2）。
4. **外部路径不入 manifest**：仓库校验器禁止 manifest 引用外部绝对路径；本汇总文件即仓内可回查入口。
5. R41 终审为 CONDITIONAL，R42 只补环境能力，**R43 才是有 PASS 证据的最新一轮**。

## 4. 结论（供签字栏引用，非 AI 判定）

- **事实**：真实业务项目已按体系完整链路试跑（需求→方案→评审→开发→L0/L1/L2→Gate 决策），证据可回查（§2 sha256）。
- **待授权 owner 确认**：该 pilot 是否满足 GATE-SYSTEM-001 的 "real project pilot" 要件；版本差是否需要补跑；确认后由 owner 在《体系验收记录》签字栏记录结论。
