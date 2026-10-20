# Quality Inspection Checklist

## A. 质量门禁

- [ ] 分支、commit、工作区和巡检时间窗已记录
- [ ] typecheck / lint / unit / integration / E2E / build 已按项目配置执行或明确 `NOT_CONFIGURED`
- [ ] 依赖、锁文件、构建产物和安全检查已记录
- [ ] 失败项有复现命令、日志摘要和影响

## B. 可维护性

- [ ] 模块边界和依赖方向
- [ ] 超大文件、重复逻辑、复杂度和魔法值
- [ ] 错误处理、异常吞噬、类型逃逸和隐式副作用
- [ ] 命名、注释、抽象和既有项目风格
- [ ] 日志结构化、脱敏、reqId/traceId 关联

## C. 回归与漂移

- [ ] 与批准基线、技术设计和变更范围对比
- [ ] 新增/修改行为有测试或明确缺口
- [ ] API、数据迁移、依赖和关键旅程无未登记漂移
- [ ] 不稳定测试已分类，不把环境失败当产品失败
- [ ] `.spec/` 任务清单「状态」列与裁决记录、`workflow.yaml`、`manifest.yaml` 一致（防状态漂移，对账规则见 `../../../shared/workflow-visibility.md`）

## D. 运行与发布

- [ ] web-monitor 前端信号
- [ ] server-log 结构化服务日志
- [ ] server-monitor 主机/服务指标与告警
- [ ] traceId / reqId / sessionId / appVersion / commit 可关联
- [ ] 发布、回滚和发布后观察证据
- [ ] 重复错误、延迟、资源和关键旅程趋势

## E. 路由

- [ ] 每条发现有证据、严重级别、影响、路由和验证方式
- [ ] 区分 CHANGE / DEFECT / REFACTOR / INCIDENT / OPTIMIZE
- [ ] 没有未经授权的自动改码、提交或上线
- [ ] 去敏后可沉淀的模式已标记
