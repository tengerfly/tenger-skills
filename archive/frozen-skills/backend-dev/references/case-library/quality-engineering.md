# 质量与工程化（Quality Engineering）

> 用途：搭工程质量时的落地参考。六板斧见 `decision-rules.md` §六。

---

## 一、测试

- 金字塔：单元（函数/服务）→ 集成（多组件）→ E2E（真实链路）。
- 用真实 DB 测事务；Service 单测 mock 仓储。
- 覆盖率 ≥80%，只升不降。

## 二、日志与错误处理

- 结构化 JSON + correlation ID；分级（debug/info/warn/error）。
- 不记敏感字段；全局异常中间件统一格式。

## 三、配置与 CI/CD

- 全走环境变量；分 dev/staging/prod；密钥不硬编码。
- CI：lint + typecheck + 测试 + build 全绿才合入。

## 四、可观测

- Prometheus（指标）+ Grafana（看板）+ OpenTelemetry（追踪）。
- Golden Signals：流量/延迟/错误/饱和度。

## 五、样板工程参考

| 项目 | 价值 |
|---|---|
| techschool/simplebank | Go 后端 masterclass：REST+DB+鉴权+Docker+测试完整样板 |
| fastapi/full-stack-fastapi-template | 官方全栈模板，安全默认+CI/CD |
| futurice/backend-best-practices | 行业「活文档」，质量/测试/部署/安全 |
| fpereiro/backendlore | 真实后端开发经验与踩坑 |

> 出处：github.com/techschool/simplebank、github.com/futurice/backend-best-practices。
