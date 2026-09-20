# 编码层工程决策规则（Backend-Dev Decision Rules）

> 用途：写后端代码时的「怎么写、用什么写、边界在哪」硬规则库。与 `../Backend-Tech-Design/decision-rules.md` 分工：那份管「方案层怎么设计/选型/扛量」，本份管「编码层怎么落地」。
> 写法范式（借鉴 peterhdd）：`When + 场景 → 动作 + 理由`。本 Skill 铁律（四层/维护性五条/做减法）优先级最高，冲突以 SKILL.md 为准。

---

## 一、框架选型决策树（无 TDD 全新项目时用）

| 语言 | 场景 | 框架 |
|---|---|---|
| Node/TS | 简单 API | Express |
| Node/TS | 企业级 | NestJS（默认） |
| Node/TS | 高性能 | Fastify |
| Python | 现代 API | FastAPI（类型+OpenAPI） |
| Python | 全栈/后台 | Django |
| Python | 轻量 | Flask |
| Go | 高性能微服务 | Gin/Echo |
| Go | 云原生 | Hertz/Kitex（字节） |
| Java | 企业级 | Spring Boot |
| Java | 分布式 | Spring Cloud（Nacos/OpenFeign/Gateway/Sentinel） |

> 有 TDD 时逐项采用 TDD 选型，不重选；有既有代码按现状基线。

## 二、分层职责（Controller → Service → Repository → Entity）

| 层 | 职责 | 禁止 |
|---|---|---|
| Controller | 协议转换：路由/校验/统一响应 | 不写业务逻辑 |
| Service | 核心业务规则 + 事务边界，无状态 | 不写 SQL |
| Repository | 数据访问：SQL/ORM 只在此层 | 不写业务 |
| Entity | 纯数据，无业务逻辑 | 不含行为 |

- 依赖单向向下，禁跨层/反向。
- DTO 边界：请求/响应用 DTO（Zod/Pydantic/Bean Validation），**不暴露 ORM 实体**。

## 三、REST API 规范

- 资源命名复数（`/orders`）；HTTP 动词语义化；状态码正确。
- 统一响应 `{code, message, data}`；错误码分段，禁 `{"msg"}` 与 `{"error"}` 混用。
- 版本化：公共 API URL 前缀 `/v1`；内部 header 版本化。
- 分页：常规场景统一 `{list, total}`（offset 分页）；大表/深翻页用游标分页，禁深 OFFSET——游标场景 total 可为近似值或省略，须在接口文档注明。

## 四、鉴权实现决策树

| 客户端 | 方案 |
|---|---|
| 第一方浏览器 | Session Cookie 或 BFF 令牌中介（令牌不落浏览器） |
| 原生/移动 App | OAuth/OIDC 授权码 + PKCE |
| 第三方集成 | OAuth/OIDC 或带 scope 的 API Key |
| 服务间调用 | 平台身份/短期服务凭证，**不用用户态鉴权** |

- BFF：Browser → BFF(session) → BFF 附加 Bearer → 上游 API，浏览器永不接触 access token。
- access token 短时效；refresh token 存 HttpOnly Cookie。

## 五、数据层

| 语言 | ORM |
|---|---|
| Node | Prisma（默认）/Drizzle/TypeORM |
| Java | MyBatis / Spring Data JPA |
| Go | GORM |
| Python | SQLAlchemy |

- 事务边界放 Service；Repository 只做单表/单聚合。
- 迁移用工具（Prisma Migrate/Flyway/Alembic），**禁手工改线上表结构**。
- `context.Context` 贯穿 DB 调用，支持超时与链路追踪取消。

## 六、质量六板斧

1. **测试**：单元→集成→E2E；用真实 DB 测事务。
2. **日志**：结构化 JSON + correlation ID，分级，不记敏感字段。
3. **错误处理**：全局异常中间件统一格式，不在 controller 散落 try/catch。
4. **配置**：全走环境变量，密钥不硬编码，分 dev/staging/prod。
5. **安全编码**：输入校验+转义防注入、密码 BCrypt 加盐、HTTPS+安全头+限流。
6. **可观测**：Prometheus（指标）+ Grafana（看板）+ OpenTelemetry（追踪）。

## 七、安全编码要点

- 认证（who）vs 授权（what）：JWT/OAuth/API Key 做认证，RBAC 做授权，边界统一判定。
- 密码 BCrypt/Argon2 加盐，禁明文/可逆。
- 防注入：参数化查询/ORM，禁字符串拼接 SQL。
- 依赖注入：不在内部 `new` 依赖，从外部注入 → 解耦、易 mock。
