# 流程可见性与 PRD / 测试路由修订：自动化报告

## 一、运行概览

- 日期：2026-09-22；项目：tenger-skills；基线提交：7935eeb + 本次未提交工作区变更。
- 模式：auto-test 会话模式，通过本地 Python / Git 命令实际执行；未使用独立 auto-test 引擎。
- 本次范围：Skill 契约、注册表和状态迁移约束、PRD 基线预检、只读状态 CLI、测试入口唯一性。
- 关联问题：`issue/WorkFlow/2026-09-22/01-流程可见性与产品需求入口纠正.md`。

## 二、分层结果与命令

| 检查 | 命令/执行方式 | 结果 |
|---|---|---|
| L0 契约、注册表及状态图 + L1 Python 自动化回归 | `.venv/Scripts/python.exe scripts/validate_core.py system --project-root .` | 48 项测试通过，退出码 0 |
| 修改的 18 个活跃 Skill 格式 | skill-creator 的 quick_validate.py，逐目录运行，UTF-8 模式 | 18/18 通过 |
| 状态 CLI 集成冒烟 | `.venv/Scripts/python.exe scripts/workflow_status.py --project-root . --json` | 退出码 0，读取既有 BLOCKED，stateChanged=false |
| 补丁格式 | `git diff --check` | 退出码 0 |
| L2 浏览器/接口及 L3 用户旅程 | 本变更不包含 Web 应用或 API 服务，浏览器层不适用；真实 Agent 对话另列待验证 | 未将未运行项计为通过 |
| L4 性能、安全扫描、负载 | 本轮无专项信号，未执行 | 不宣称专项结论 |

**范围内自动化检查：PASS。体系整体验收：仍为 BLOCKED。** 没有执行状态迁移或签署独立验收，未修改既有 workflow.yaml 的 Gate。外部知识库未配置（SKILLS_KNOWLEDGE_ROOT 未设置）为显式降级警告，本轮未配置外部依赖。

## 三、覆盖与未覆盖

- 已覆盖：注册表/契约一致性、正式 PRD 入口必须具备产品定义/蓝图/功能决策、APPROVED 状态及对应批准决策核验、已有有效基线复用、Testing 活跃入口移除及别名指向 auto-test。
- 状态工具覆盖：缺失/损坏/重复 YAML 字段、非法或冲突记录、只读不写入、待决定与下一步展示、Windows 非 UTF-8 环境下的中文输出。
- 未覆盖：真实模型是否执行逐模块深入追问、是否正确解释竞品全景、暂停恢复的实际对话体验、真实旧项目接管与增量交付、已安装 Skill 环境。
- 未运行真实 AI/竞品在线链路，也没有用 mock 结果冒充行为验证。行为回归场景见 `docs/task-scope-regression.md`，须另行执行并存证。
- 不报告状态/迁移覆盖百分比或模型成功率：本轮没有对应完整行为覆盖分母或真实会话样本。工具单测通过不等于所有业务路径通过。

## 四、修复与复验

1. 初次 Skill 格式检查 16/18：BOM 与顶层 compatibility 元数据兼容问题；已移除 BOM，将兼容信息保留在 metadata 内。
2. 第一次复验 17/18：Fact-Check 描述含校验器禁止的尖括号，编辑管道引入问号；改为 Unicode 箭头。最终 18/18 通过。
3. 发现过程和修复记录统一归入上述 WorkFlow 问题，不重复建立原始反馈详情。剩余风险是行为未验证，不是已确认解决。

## 五、证据索引

目录：`.spec/auto-test/evidence/workflow-prd-routing-20260922/`。

- `system-validation-final.log`：最终全量校验与 48 项测试输出。
- `skill-validation.log` / `skill-validation-recheck.log` / `skill-validation-final.log`：初次、首次复验、最终格式校验；保留失败历史。
- `workflow-status-final.log`：只读状态快照。
- `diff-check-final.log`：补丁空白检查。
- `results-final.json`：最终各检查与逐 Skill 退出码。

下一步：以真实对标产品需求和一个旧项目执行行为试跑，再由授权负责人记录独立验收；不得用本报告替代用户范围决策或体系 Gate 批准。
