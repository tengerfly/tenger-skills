# Traceability Contract v1

## 1. 目标

把“想法为何变成这段代码、这次错误为何触发这个修复、修复后是否改善”串成一条可查询链：

```text
idea/intake
  → problem/research
  → requirement
  → acceptance-criteria
  → prototype/ui/tech-design
  → code-change
  → test-case/test-run
  → release
  → commit/version
  → signal/log/metric
  → triage/incident
  → change/defect/refactor/optimize
```

## 2. 关系类型

首批关系：`derived-from`、`satisfies`、`implements`、`verified-by`、`released-as`、`observed-by`、`caused-by`、`fixes`、`supersedes`、`blocks`、`routes-to`。

## 3. 最小格式

项目 `.spec/traceability.yaml`：

```yaml
links:
  - linkId: LINK-20260920-001
    from: REQ-001
    relation: implements
    to: COMMIT-abc123
    lifecycle: CHANGE
    evidenceRefs: [EVID-001]
    recordedBy: dev-workflow
    recordedAt: 2026-09-20T12:00:00+08:00
```

每条链接必须有唯一 `linkId`、两端标识、关系、生命周期、记录 Skill 和时间；关键关系必须有证据。

## 4. 运行反馈的关联键

优先使用：`projectId`、`environment`、`appVersion`、`releaseId`、`commitSha`、`traceId`、`requestId`、`sessionId`、`eventId`。来自 `web-monitor`、`server-log`、`server-monitor` 的信号如果无法关联版本，必须标记 `OPEN`，不能据此断言某次提交导致问题。

## 5. 追踪完整性

最低要求：

- 每个已批准需求至少关联一个验收标准；
- 每个代码变更至少关联一个需求、缺陷、重构计划或事故；
- 每个发布版本至少关联变更集合和验证报告；
- 每个线上问题至少关联信号证据、影响版本、分诊结论和后续任务；
- `REFACTOR` 必须关联行为基线和保护测试；
- `OPTIMIZE` 必须关联优化前后指标。