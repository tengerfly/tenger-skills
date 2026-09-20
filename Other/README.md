# Other

横向能力域。放置不属于单一 PRD/UI/DEV/Test 阶段、但被多个阶段复用的 Skill，包括项目接管、变更/缺陷/事故路由、发布与运行、研究核验以及 Skill 治理。

## Skill 清单

| 类别 | Skills |
|---|---|
| 项目与路由 | `project-onboarding`、`change-intake`、`impact-analysis`、`defect-triage`、`refactor-planning`、`quality-inspection` |
| 发布与运行 | `release-planning`、`deployment-execution`、`release-verification`、`incident-response`、`signal-collection`、`signal-triage`、`post-release-review`、`optimization-planning` |
| 工程辅助 | `Bug-Fix`、`OSS-Radar`、`Fact-Check`、`Source-Reading`、`Essence-Distill` |
| Skill 治理 | `Skill-Optimizer`、`Skill-Evolver` |

## 边界

- `Other` 中的 Skill 不绕过 `WorkFlow` 的授权、状态、Gate 和产物契约。
- `Bug-Fix` 负责证据驱动的定位与委托闭环，不代替 DEV 修复代码，也不代替 Test 做深度验收。
- `OSS-Radar`、`Fact-Check`、`Source-Reading` 和 `Essence-Distill` 是研究/核验能力，不把外部结论自动升级为批准需求。
- 跨域结果必须通过 `.spec/manifest.yaml`、证据引用和决策引用交接。
