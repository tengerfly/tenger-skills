# EVID-SYSTEM-ACCEPTANCE-20261020 · 体系验收证据包（GATE-SYSTEM-001 解除用）

> 状态：**证据包 / 待签字草案，不是批准**。本文件由 Lead 起草，未由产出体系变更的会话自审；`§0.5` 与签字栏必须由授权 owner 指定的独立验收执行者填写。
> 依据：`shared/gate-policy.md` §2（PASS 要件）、§3（CONDITIONAL 七字段）、§4（BLOCKED）；`docs/validation-toolchain.md` §4（信任边界：本地 YAML/摘要只验证记录一致性，不认证签名身份）。
> 采集日期：2026-10-20；采集环境：Windows，DSH danger-full-access，Python 3.11.15。

## §0.5 评审上下文隔离记录（独立验收执行者填写；缺此表或 producedByContextInvolved 非 false ⇒ 按 gate-policy §6 第 8 条 Gate 只能 BLOCKED）

| 字段 | 值 |
|---|---|
| isolationMode | 待填（`subagent` 或 `new-session`） |
| reviewerRef | 待填（独立验收执行者 id / 会话 id） |
| packageDigest | 待填（对 §2 证据清单按约定规范化后复算 sha256） |
| parentExecution | `EXEC-20260920-SYSTEM-001` |
| producedByContextInvolved | 待填（必须为 `false`：执行者未参与被验收体系的产出/修订/自检/评审调度） |
| verifiedArtifacts | 待填（至少含本记录 + E1–E8；复算命令见 §2 末） |

## 1. 验收范围与输入版本

| 项 | 值 |
|---|---|
| 仓库 | `D:\\project\\agent-project\\tenger-skills`，分支 `refactor/skill-system-v3` |
| 代码字节 | HEAD `47d69082597ddb90f52b38e4525b50d6de300e6b`（2026-10-20 08:28:47 +08），已推送 origin（ahead=0） |
| 流程 | `WF-20260920-001` / `EXEC-20260920-SYSTEM-001` / lifecycle `OPTIMIZE` / state `INSPECTION_IN_PROGRESS` |
| 验收对象 | PEOS Skill 体系：45 个本地 Skill、shared 契约、governance 注册表、scripts 校验器与预检、自举 .spec；**不覆盖** 业务项目代码 |
| 本次提交内容 | 仅新增/修改文档类证据（本包、E3、E5/E6 日志、E8 独立验收、旧报告 SUPERSEDED 追记、README 状态行）；**未改任何 Skill 正文/shared 契约/注册表/脚本字节**（提交后用 `git diff --stat` 复核） |
| 不覆盖 | 远端 Windows/Linux CI 实跑、部署/回滚演练、生产观测、宿主无 subagent 的 L2/L3、安装副本实际加载、付费行为评测（20 条 blocked） |

## 2. 证据清单（路径 · 时间 · sha256）

| 编号 | 路径 | 生成时间 | sha256 | 说明 |
|---|---|---|---|---|
| E1 | `.spec/evidence/system-validation-2026-09-20.md` | 2026-09-21 | `5209c17b9436e8b2e7dfe42cab530b75b7f392be9c38bb475e9e7320104c38e2` | 历史结构验证记录（30 tests），自述非批准 |
| E2 | `docs/技能体系试跑记录-20261018.md` | 2026-10-18 | `e5b59c7d86f971b85d7ca370117f8c03618abc2b78824fae0cd15401c03ee56b` | R41/R42 真实项目试跑记录（状态：进行中） |
| E3 | `.spec/evidence/real-project-pilot-20261018.md` | 2026-10-20 | `36ce24d26fa991d7f06343e9d4da03c8b68d0e69b31c0c2e3ead39edb060b83e` | R41–R43 pilot 证据汇总（含外部 KB 三文件 sha256；外部路径不入 manifest） |
| E4 | `.spec/体系评审/2026-10-19/评审上下文隔离改造-独立验收.md` | 2026-10-19 | `bab7a574aa55bfc4789a4c3c5759e94016b7a556252d7dd4b1cf2b65194c4bdf` | 10-19 结构层验收；**2026-10-20 已标 SUPERSEDED，不作为 Gate 隔离证据**，仅历史 |
| E5 | `.spec/evidence/logs/validate-20261020.out.log` | 2026-10-20 09:50 | `3c963a5f2ca26975ee4e6c9cdd4efe81b6558d750f7e511abb6e0612a53138ee` | 全量校验 stdout（`system validation passed`） |
| E5b | `.spec/evidence/logs/validate-20261020.err.log` | 2026-10-20 09:50 | `dbab50c6502346202d49e3a304c2d9696da95d2d7c623ab40798c26f23403c6d` | 全量校验 stderr（unittest -v 原始输出：`Ran 551 tests in 1522.113s` / `OK (skipped=2)`） |
| E6 | `.spec/evidence/logs/eval-run-20261020.log` | 2026-10-20 09:53 | `d987d8b0f9b95a1364cc7d0c9c354a227984e2fb2ca85fdb7774c18189e64992` | 12 套 eval 零成本回归：67 条 = passed 47 / failed 0 / error 0 / 待引擎 20；L2 回流 28/28、缺回流 0 |
| E6b | `.spec/evidence/logs/install-check-20261020.log` | 2026-10-20 09:55 | `a75c3c111741703fcb5bbffcd319a7cce359d3cd72575090db81d8f6cf4a0071` | 6 宿主 copy `--check` 全 PASS drift=0；export 自检 PASS（2461 文件）；link 模式结构性 drift（qoder 1 / zcode 46，内容经 copy 模式核验一致） |
| E7 | `.spec/obs/behaviour-runs.jsonl` | 2026-10-18 / 2026-10-20 | 入库（append-only 真相，本次 +20 行） | 行为层台账：本轮追加 20 条 blocked（`TSR_ALLOW_ENGINE` 未授权，零 token） |
| E8 | `.spec/体系评审/2026-10-20/评审上下文隔离硬性化-独立验收.md` | 2026-10-20 | `399d68fd1c688032f9ff92d6d2283a55b5149fce3c4f7da83cd6c31331d95c02` | fresh 独立验收（含 §0.5）：R2 结论 **PASS（结构/文档层）**，P0=0 / P1=0 / P2=5 / P3=7 |

复算命令：`Get-FileHash <path> -Algorithm SHA256`；E5 判定：`validate.ps1` exit **0**、总耗时 **1588.4s**（含校验器约 60s + unittest 1522.113s）。

## 3. 结构层结论

**PASS（限定口径：体系结构 / 验证工具链 / 契约与治理记录）**。依据：

- E5 全量校验 exit 0：注册表、状态机、Gate、授权、产物、trace、引用、知识降级、goalplan、evolution、crossrefs、fixtures 全部通过；`Ran 551 tests in 1522.113s`、`OK (skipped=2)`；
- E6：12 套 eval 基线 `baseline.py diff` 结论「同一锚下无回退」（passed 47 / failed 0 / error 0 / 待引擎 20，行为层 blocked 不冒充通过）；6 宿主 copy 模式 drift=0；export pack 自检 PASS；
- E8：HEAD 47d6908（评审上下文隔离硬性化）经 fresh 独立验收，R2 定向复核后 **P0=0、P1=0**，结构/文档层 PASS；其 R1 发现的 P1（旧报告缺 §0.5 被当 PASS 证据）已修（E4 加 SUPERSEDED 追记），R2 复判 FIXED；
- E7 交付面：HEAD 已推送（ahead=0）；推送前 `goalplan` 曾因 delivery 判据报红 1 次，push 后全量运行绿——如实记录，不隐藏中间红。

口径限制：本结论**不覆盖**问题池中按迭代流程跟踪的技能内容缺陷（`issue/` 65 条：P0 21 / P1 29，其中状态「处理中 22 / 待处理 2 / 重开或未通过 2」）；这些是独立工作项，不是本次验收范围内的「未决 P0/P1」。是否接受该口径由授权 owner 在签字栏决定。

## 4. 行为层结论：未验证（不得记 PASS）

以下行为层**没有**通过声明：

1. 评审上下文隔离的 fresh 子代理派发实证（issue 判据 ⑥）；E8 §1.3 已声明未覆盖；
2. 宿主无 subagent 时的 L2/L3 实测；
3. 宿主安装副本实际加载（6 宿主 `--check` 只证明文件一致/结构，不证明运行时加载）；
4. 付费行为评测：20 条行为层用例在零成本回归中一律 blocked（E6/E7），真跑需 `TSR_ALLOW_ENGINE=1` 与用户授权；
5. 真实项目版本对齐：pilot 证据 E3/R43 时点（2026-10-18）早于 HEAD 47d6908，10-19/10-20 改动未被真实业务试跑覆盖。

按 `shared/gate-policy.md` §1，若授权 owner 将上述任一项判定为范围内 P1，则本体系 Gate **不能记 PASS**，只能走 CONDITIONAL（七字段例外）或保持 BLOCKED。

## 5. 残留风险

- E8 记录的 P2×5 / P3×7（如：ui-ux-review 回填改包与 review-package 冲突、3 个 Skill 无错误表、维度/角色模板 §0.5 字段仅 2/6、包摘要自引用不可复算、fidelity/quality 评审包归档路径缺失、issue:28 仍直引旧报告）；
- 安装器 link 模式结构性 drift：`.qoder-cn/skills/frontend-dev` 是真实目录（其余 46 为链接）、`.zcode/skills` 46 个真实目录 + 1 链接；当前内容与源仓一致（copy 模式 unchanged），但未来源仓改动不会自动同步这两个宿主的对应目录；
- 环境降级：`SKILLS_KNOWLEDGE_ROOT` 未配置（warn-and-degrade，未阻断）；
- 未执行：远端 CI 实跑、部署/回滚演练、生产观测、macOS/Linux link 真机；
- 本机验证耗时约 25 分钟（10-19 记录 1593s；本轮 1522s），显著高于文档预期，主因本机进程创建被安全客户端拖慢（单模块 40.7s / python 冷启动 1.9s）；不影响结果，但影响门禁可用性。

## 6. 签字栏与建议路径

### 6.1 签字栏

- 独立验收执行者（id/会话）：________　isolationMode：________　日期：________
- 结构层结论：________　行为层结论：________
- 授权 owner（批准人）：________　日期：________
- 决定：☐ PASS　☐ CONDITIONAL　☐ 拒绝（保持 BLOCKED）
- CONDITIONAL 必填：`exceptionId` ______ `risk` ______ `owner` ______ `dueAt` ______ `remediation` ______ `allowDownstream` ______ `approvalRef` ______

> 声明：本地 YAML 与 sha256 只验证记录一致性，不认证签名人身份；本证据包不替代 owner 批准，也不构成生产发布授权。

### 6.2 三条可选路径

1. **CONDITIONAL（建议，若近期要解 BLOCKED）**：owner 把「行为层未验证 + pilot 版本差」作为 P1 风险明示接受，填写七字段例外；Gate 记 CONDITIONAL、`allowDownstream` 按需，`approvalRef` 指向新 decision。风险接受必须由 owner 完成，AI 不得代填。
2. **PASS（严格口径）**：先补行为层验收（fresh 派发实测 + 宿主无 subagent L2/L3 + 安装副本加载）并用对齐 HEAD 的真实项目跑一轮，再评 PASS；预计需另开一轮完整验收。
3. **保持 BLOCKED**：维持现状，等上述任一路径具备条件后重开验收；期间不得以「测试全绿」宣称体系已验收。

### 6.3 签字后需要修改的 YAML（逐项，须在预检通过后同批落盘）

| # | 文件:字段 | 现值 → 目标值 | 签字要求 |
|---|---|---|---|
| 1 | 新建 `.spec/authorization.yaml` | 无 → projectId + approvers[].id/actions（`execute-task`,`clear-block`,`approve-artifact`） | owner 身份只能用户给 |
| 2 | 新建 `.spec/tasks/TASK-20261020-SYSTEM-ACCEPT.yaml` | 无 → executionId `EXEC-20260920-SYSTEM-001`、transition `TR-083`、target `INSPECTION_PASS`、gate.outcome PASS、evidenceRefs 含本证据包 | 预检通过后写入 |
| 3 | `.spec/decisions/DEC-SYSTEM-001.yaml` | DRAFT → APPROVED；decision `pending-acceptance` → `approve`；补 approvedBy/approvedAt/expiresAt/scope | **必须用户签** |
| 4 | `.spec/manifest.yaml` | DEC status DRAFT→APPROVED（同批）；新增 EVID 条目（type inspection / role inspection / result PASS / subjectDigests / contentDigest / decisionRefs） | 签字后同批 |
| 5 | `.spec/workflow.yaml` | gate BLOCKED→PASS；allowDownstream false→true；state INSPECTION_IN_PROGRESS→INSPECTION_PASS；reason/nextAction/evidenceRefs/decisionRefs/revision/updatedAt 同步；`unresolvedRisks` P1 清空（PASS 不得含 P0/P1） | 签字后按 TR-083 写 |
| 6 | `.spec/gates/GATE-SYSTEM-001.yaml` | gate BLOCKED→PASS；allowDownstream false→true；reason/nextAction/recordedAt/evidenceRefs/decisionRefs 同步；删除 BLOCKED 专属 owner/requiredInput/clearanceCondition | 签字后按 TR-083 写 |
| 7 | `.spec/traceability.yaml` | 新增 LINK：本证据包 validated-by GATE-SYSTEM-001（另可 E3 同链） | 签字后同批 |
| 8 | `README.md` / `docs/当前项目介绍与目标对齐说明书.md` / `docs/工程体系使用手册.md` | BLOCKED 叙述 → 实际结论 + 本证据包链接 | 签字后同步 |

> 若走 CONDITIONAL：workflow gate 记 `CONDITIONAL`、`allowDownstream` 通常 `false`，并新增七字段与 decision scope `accept-risk`（仍必须用户签）。

## 7. 附：本次如何避免「假绿」

- 全量校验直接执行 `validate.ps1` 并保留 stdout/stderr 原始日志（E5/E5b），不手抄数字；
- eval 明示 20 条行为层 blocked 不计入通过（E6）；
- 独立验收走 fresh 子代理（E8），且其 R1 主动抓出「旧报告无 §0.5 仍当 PASS 证据」的假绿并标 P1；修复后只做定向 R2 复判，未重跑 A/B/C/D 面；
- 推送前 goalplan 的 delivery 红被如实记录并修复（push），不留「本地绿、远端旧」的假象；
- 结构层 PASS 与行为层未验证分开陈述，不互相代偿。