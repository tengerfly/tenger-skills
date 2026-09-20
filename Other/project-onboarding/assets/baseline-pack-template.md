# Baseline Pack Template

> 采集日期：YYYY-MM-DD；项目：；commit：；环境：；生命周期模式：

## 1. project-profile.yaml

```yaml
projectId: ""
mode: CREATE | CHANGE | DEFECT | REFACTOR | INCIDENT | OPTIMIZE
platform: web | backend | mini-program | desktop | ios | android | harmony | mixed
runtime: ""
packageManager: ""
entrypoints: []
branch: ""
commit: ""
baselineId: ""
collectedAt: "YYYY-MM-DD"
privacy: no-secrets-no-customer-data
```

## 2. architecture-map.md

- 模块与边界：
- 关键数据/请求流：
- 外部依赖：
- 证据：
- INFERENCE / OPEN：

## 3. behavior-baseline.md

| 主链 | 入口 | 前置条件 | 正常结果 | 异常结果 | 可恢复动作 | 证据 | 标签 |
|---|---|---|---|---|---|---|---|

## 4. api-and-data-inventory.md

- 对外接口/事件：
- 数据存储与迁移：
- 兼容性约束：
- 事实与目标规则冲突：
- 证据：

## 5. test-baseline.md

- 可执行命令：
- 通过/失败/跳过：
- 覆盖率与可信度：
- 主链回归保护：
- 缺口和风险：

## 6. observability-baseline.md

- 前端错误/性能/行为：
- 服务日志与 reqId/traceId：
- 主机/服务指标与告警：
- appVersion、commit、环境关联：
- 缺口：

## 7. release-baseline.md

- 构建产物：
- 部署方式：
- 灰度/开关：
- 回滚路径及证据：
- 发布后验证：

## 8. unknowns-and-risks.md

| ID | 类别 | 问题 | 影响 | 最小补证动作 | 路由 | 状态 |
|---|---|---|---|---|---|---|
