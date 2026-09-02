# 【Monorepo 工程目录结构】{{PRODUCT_NAME}} 后端

> **责任开发**：{{AUTHOR_NAME}}　|　**创建/更新**：{{DATE}}
> **实现档位**：`[企业级生产] / [快速实现]`
> 📐 本文件是后端代码的**工程骨架**（前后端同仓库 Monorepo + 微服务）；NestJS 落地细节见 `references/tech-stack-guide.md`，分层/服务边界见 `references/architecture-guide.md`。

---

## 1. 技术栈落地清单【必须】

| 组件 | 选型（来自 TDD / 默认） | 落地版本 | 依赖文件 |
|------|----------------|---------|---------|
| 语言/框架 | TypeScript + NestJS | {{VER}} | package.json |
| 微服务通信 | {{gRPC / NATS / TCP}} | — | @nestjs/microservices |
| ORM | {{Prisma / TypeORM}} | {{VER}} | package.json + schema/migration |
| 数据库 | {{DB}} | {{VER}} | {{迁移脚本目录}} |
| 缓存/队列 | {{CACHE / MQ}} | — | {{client 依赖}} |
| 测试框架 | Jest + Supertest | {{VER}} | package.json |

## 2. Monorepo 目录结构【必须 · 前后端同仓库】

```
{{repo}}/                            # 前后端同仓库（monorepo）
├── apps/
│   ├── web/                         # 前端应用（Frontend-Tech-Design 落地目标，预留）
│   └── server/
│       ├── gateway/                 # API 网关：HTTP 入口，路由到各微服务
│       ├── {{service_01}}/          # 微服务 A（与 TDD 模块对应）
│       │   └── src/
│       │       ├── main.ts          # createMicroservice 启动
│       │       ├── {{m}}.module.ts
│       │       ├── {{m}}.controller.ts   # 接口层
│       │       ├── {{m}}.service.ts      # 业务层（接口 + 实现）
│       │       ├── {{m}}.repository.ts   # 数据访问层
│       │       ├── {{m}}.entity.ts       # 数据模型
│       │       └── *.spec.ts             # 测试（先写）
│       └── {{service_02}}/          # 微服务 B
├── libs/
│   └── shared/                      # 共享（契约单一事实源）
│       ├── dto/                     # 前后端共用 DTO
│       ├── enums/                   # 共享枚举/常量（状态、错误码分段）
│       ├── contracts/               # 服务间消息契约 / gRPC proto
│       └── index.ts
├── package.json                     # pnpm workspace 根
├── pnpm-workspace.yaml
├── tsconfig.base.json
├── .env.example                     # 环境变量样例（敏感值占位）
└── README.md                        # 运行说明
```

## 3. 服务/模块清单与文件规划【必须】

| 序号 | 服务/模块（来自 TDD） | Controller | Service | Repository | Entity | 测试 | 通信方式 |
|------|----------------|-----------|---------|-----------|--------|------|---------|
| 01 | {{SERVICE_A}} | {{files}} | {{files}} | {{files}} | {{files}} | {{files}} | {{HTTP/gRPC/NATS}} |
| 02 | {{SERVICE_B}} | {{files}} | {{files}} | {{files}} | {{files}} | {{files}} | {{HTTP/gRPC/NATS}} |

> 服务拆分与 TDD 模块清单对齐；服务间只通过对外接口通信，共享 DTO/枚举下沉 `libs/shared`。

## 4. 基础设施层落地清单【必须】

| 项 | 位置 | 说明 |
|----|------|------|
| 统一响应 | `libs/shared` 或 `common/response/` | `{code,message,data}`，成功/失败构造方法 |
| 统一错误码 | `libs/shared/enums` | 分段：1xxx 参数 / 2xxx 业务 / 3xxx 权限 / 5xxx 系统 |
| 日志 | `common/logger/` | trace_id 注入、按级别输出 |
| 配置 | `@nestjs/config` + `.env` | 读环境变量，禁止硬编码 |
| 中间件/守卫 | `common/`（拦截器/过滤器/守卫） | 鉴权、参数校验、统一异常处理 |
| 服务间通信 | `@nestjs/microservices` | gRPC/NATS client 统一封装 |

## 5. 依赖与配置【必须】

- **依赖清单**：见 `references/tech-stack-guide.md` §二，版本写死、锁定 `pnpm-lock.yaml`；
- **配置外置**：连接串/密钥/端口走环境变量，提供 `.env.example`；
- **迁移脚本**：Prisma migrate / TypeORM migration 可重复执行、可版本管理；
- **共享包**：`libs/shared` 用 workspace 引用（`"@repo/shared": "workspace:*"`）。

## 6. 启动与运行【必须】

```bash
# 依赖安装
pnpm install

# 执行迁移（每服务或统一）
pnpm --filter @repo/<service> prisma:migrate   # 或对应 migration 命令

# 启动服务（可并行）
pnpm --filter @repo/<service> dev

# 运行测试
pnpm -r test
```

---

## 附录：章节开关说明

| 项 | 开关 | 依据 |
|----|------|------|
| {{如：缓存 client}} | {{开/关}} | {{TDD 是否选缓存}} |
| {{如：消息队列 client}} | {{开/关}} | {{TDD 是否选队列}} |
| {{如：API 网关}} | {{开/关}} | {{是否需要统一 HTTP 入口}} |
