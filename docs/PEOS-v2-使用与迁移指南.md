# PEOS v2 使用与迁移指南

本仓库现在采用 **PEOS（Personal Engineering Operating System）** 作为上层工程体系。旧 Skill 不会被一次性删除，而是通过注册表和 Workflow 逐步迁移；已经验证过的产品、原型、UI/UX、OSS、技术方案、开发、评审和测试逻辑继续保留。

## 六层结构

1. **入口与基线**：`project-onboarding`、`change-intake`，把自然语言请求变成可追踪任务。
2. **生命周期路由**：`CREATE`、`CHANGE`、`DEFECT`、`REFACTOR`、`INCIDENT`、`OPTIMIZE`，由 `Workflow` 统一识别和调度。
3. **领域 Workflow**：PRD、UI、DEV、Testing、Inspection，旧专业 Skill 以兼容包装方式继续执行。
4. **交付治理**：产物清单、决策记录、Gate、状态转移和追踪链，统一放在 `shared/` 与 `governance/`。
5. **发布闭环**：`release-planning` → `deployment-execution` → `release-verification`，任何真实部署都需要明确授权。
6. **运行反馈**：`signal-collection` → `signal-triage` → `incident-response` / `product-analytics` → `optimization-planning` → `post-release-review`。

## 两条标准闭环

```text
CREATE:
Intake → Baseline → PRD → UI/Prototype → OSS Research → Tech Design
→ Dev → Code Review → Test → Release → Verify → Observe

DEFECT / INCIDENT:
Signal → Triage → Incident or Defect → Containment/Fix → Regression
→ Release → Verify → Post-release Observe
```

每个节点都必须输出：产物、证据、Gate、状态变更、追踪关系和下一步；“文件存在”不等于 Gate 通过。

## 技术方案前的 GitHub / OSS 研究

`shared/oss-research-policy.md` 是强制策略。技术方案、架构决策或关键实现开始前，应：

- 从 PRD、约束和风险提取检索词；
- 优先查看 GitHub 官方仓库、官方文档、测试和 release/tag；
- 至少比较两个实现样本；
- 记录仓库、commit/tag、许可证、适用边界和可验证证据；
- 区分 `FACT`、`INFERENCE`、`ASSUMPTION`、`OPEN`；
- 写出“采用 / 借鉴 / 不采用”决策后再进入 TDD/FTDD。

如果无法取得可靠源码或版本证据，不得把猜测写成已验证方案，也不得伪造 GitHub 研究结论。

## 目录约定

- `governance/`：Skill、Workflow、State、Artifact 注册表。
- `shared/`：公共契约、Gate、质量基线、OSS 研究策略、模板。
- `.spec/`：具体项目的 manifest、workflow、traceability 和业务产物；本仓库自身保留原有知识沉淀，不强制伪造项目 manifest。
- `scripts/fixtures/`：CREATE、CHANGE、生产缺陷闭环的黄金场景。
- `WorkFlow/references/legacy-pipeline.md`：原有线性流水线备份，保证迁移期间可回溯。

## 校验命令

```powershell
# 全系统校验：注册表、v1 Skill Contract、Workflow 图、模板项目和黄金场景
.\scripts\validate-system.ps1

# 单项校验
.\scripts\validate-skill-contract.ps1
.\scripts\validate-workflow-graph.ps1
.\scripts\validate-artifact-manifest.ps1 -ProjectRoot <project-root> -RequireManifest
.\scripts\validate-traceability.ps1 -ProjectRoot <project-root> -RequireTraceability
```

## 迁移原则

- 不执行 `git reset`、`git clean` 或大范围删除；
- 不覆盖用户尚未提交的内容；
- 先迁移入口、治理、发布和运行闭环，再按 PRD → UI/UX → DEV → Testing 迁移旧 Skill；
- 每批迁移都保留原逻辑，补齐输入、输出、证据、Gate、失败路由和状态变化；
- 外部仓库（`web-monitor`、`server-log`、`server-monitor`、`skills-knowledge`）只通过集成边界引用，不在本仓库直接修改；
- 生产部署、通知和例外放行必须由用户或明确授权责任人确认。