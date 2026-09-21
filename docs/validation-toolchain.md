# 工程验证与任务预检

## 1. 本地入口

在仓库根目录运行（Python 3.10+；Windows PowerShell 5 或 PowerShell 7）：

```powershell
.\scripts\bootstrap.ps1
.\scripts\validate.ps1
.\scripts\run-tests.ps1
```

- bootstrap 创建仓库内 .venv，安装固定版本 PyYAML==6.0.3，并执行全套验证；中断后缺失 pip 可通过 ensurepip 恢复。不修改全局 Python。
- validate 包含回归测试，不需要另跑 run-tests 才算“一键验证”。run-tests 用于单独调试。
- 所有入口优先使用 TENGER_PYTHON，其次 .venv/Scripts/python.exe 或 .venv/bin/python，最后系统 python。
- CI 配置在 Ubuntu / Windows 上运行 bootstrap。配置存在不代表远端 CI 已执行。
- 沙箱若阻止临时目录读写，需要在获准的本地环境运行；失败不得被记录为通过。

## 2. 检查范围

| 层级 | 实际检查 |
|---|---|
| 注册表 | 45 个本地 Skill、canonical ID、别名冲突、路径与 Git 大小写、实际文件漏登记；不遍历源码克隆与 node_modules |
| Skill 契约 | v1 / legacy-wrapper 的 13 章节；legacy-adapter 的共享边界，保留原领域能力 |
| 流程图 | actor / lifecycle / artifact / evidenceRole / failureRoute；可达状态到完成或显式事故移交；不能绕过代码评审和测试进入发布 |
| 项目记录 | 根目录 manifest / workflow / traceability 必需；重复 YAML 键、必填字段、引用类型和本地产物路径 |
| Gate | PASS 禁止未解决 P0/P1；BLOCKED 禁止下游；CONDITIONAL 必须有未过期、限定范围且由登记负责人签批的例外 |
| 授权 | decision 与 manifest 身份/状态一致；projectId / executionId、审批人、动作、有效期、例外或产物范围 |
| 样例 | 6 个旧样例只做 manifest/traceability 结构检查，不能证明旧 APPROVED 字样具有真实授权 |
| 知识依赖 | 缺少 SKILLS_KNOWLEDGE_ROOT 输出 WARNING，属于降级；-StrictKnowledge 则失败 |

schema.yaml 是描述型 YAML，不是 JSON Schema。核心引擎读取其必填字段和关系枚举，跨文件语义由 Python 实现。
外部 sourceRefs 的 USER-/REQ-/EXT-/URL-/ISSUE-/PR-/COMMIT-/RUN- 前缀只作标识语法检查，不证明外部对象存在。

## 3. 真实任务：只读转换就绪检查

复制 shared/templates/task-envelope.yaml 到项目的 .spec/tasks/，填写实际值，然后运行：

```powershell
python scripts/task_preflight.py --project-root <项目目录> --task-file .spec/tasks/TASK-001.yaml
```

这不是自动执行器。成功只输出 JSON 计划，stateChanged 和 skillExecuted 始终为 false。失败退出码为 1。
模板本身不具备授权，也不是可直接放行的实例。

预检要求：
1. task 与当前 workflow 的 projectId、executionId、lifecycle、revision、currentState 一致；transitionId/from/to/actor 与注册表一致。
2. Gate outcome 与注册转换条件一致；必需产物与 evidenceRole 均齐备。不能用任务中的 PASS 覆盖当前 BLOCKED。
3. .spec/authorization.yaml 登记审批人和允许动作；decision 是 manifest 登记的 APPROVED YAML，限定 actor、transitionIds、allowedPaths，具有有效 approvedAt/expiresAt。
4. execute-task 为基础授权；部署另需 deploy；解除 BLOCKED 另需 clear-block 和 clearanceEvidenceRefs。
5. allowedPaths 为目录前缀范围，forbiddenPaths 优先；禁止绝对路径、跨目录和 symlink 越界。
6. evidence manifest 条目包含 executionId、revision、lifecycle、result: PASS、role、subjectRefs、subjectDigests 与 contentDigest。摘要为文件原始字节的 SHA-256；每条证据须覆盖本次全部 inputRefs/artifactRefs。组合证据可拆分为更小的原子任务，不得用旧报告验证新代码。
7. expectedOutput 说明下一动作交接约定；不是“该文件已经生成”的证明。

**阶段边界**：执行前由负责人确认输入/范围/权限；执行后归档实际产物与证据；在落盘状态转换前调用此预检。缺少尚未生成的完成证据时不放行，不要求伪造证据才能开始工作。
预检通过后仍需受控的状态写入/实际执行流程；发生任何输入、授权或证据变化必须重跑。
INCIDENT_ROUTED 的 handoffFrom 只表示当前执行移交结束，必须建立新的 INCIDENT executionId，不静默更改原 lifecycle。

## 4. 授权记录格式（说明，不是实际授权）

.spec/authorization.yaml 最小结构：

```yaml
projectId: your-project
approvers:
  - id: accountable-owner
    actions: [execute-task, accept-risk, approve-artifact, clear-block, deploy]
```

decision 文件由真实审批流程记录 decisionId、projectId、executionId、status: APPROVED、decision: approve、approvedBy、approvedAt、expiresAt 和 scope。
scope.actions 限定动作；任务需 actor / transitionIds / allowedPaths；产物批准需 artifactIds；风险例外需 exceptionId，且 decision.owner 对应例外 owner。
Envelope.authorization 的 grantedBy / grantedAt 必须与 decision 一致，不能只填任意非空字符串。

**信任边界**：本地 YAML 和摘要只能验证记录一致性，不认证人的身份、不验证签名、不隔离恶意代理。如果同一人可同时修改策略、批准记录和摘要，就能伪造它们。生产使用必须由受保护分支、独立审批或外部签名/审计系统控制这些记录。此仓库不声称实现这些外部保障。

## 5. 兼容与未自动化规则

- Registry 的 legacyAliases 只用于旧名称映射，新实例使用 canonical ID。
- IncludeLegacy 保留为兼容参数；默认不会跳过已注册 wrapper / adapter。
- 原 ManifestPath、TraceabilityPath、SkipPathExistence、SkillPath 过滤和单个 registry override 不再静默忽略：传入即报错，要求使用一致的 ProjectRoot / 注册表集合。
- 三轮评审上限、超时调度、并发任务锁、原子状态写入、真实部署/回滚和生产观测仍由流程执行者负责；注册元数据不等于实现了调度器。
- 本地测试通过不等于独立验收或发布批准；当前自举 Gate 保持 BLOCKED，等待真实项目试跑和授权负责人验收。
