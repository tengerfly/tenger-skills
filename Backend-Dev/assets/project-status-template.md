# 【项目说明文档】{{PRODUCT_NAME}} 后端（PROJECT.md）

> 断点续做的总入口：再次开发先读本文件恢复项目情况、规则与进度。

## 1. 项目基本情况

| 项 | 内容 |
|----|------|
| 项目名称 | {{PRODUCT_NAME}} |
| 需求来源 | PRD `{{PRD_PATH}}` / 原型 `{{PROTO_PATH}}` |
| 技术方案 | 后端 TDD `{{TDD_PATH}}` / 前端 FTDD `{{FTDD_PATH}}` |
| 技术栈 | TypeScript + NestJS（微服务）+ {{ORM}} + {{DB}} |
| 架构 | 微服务 + Monorepo |
| 档位 | {{企业级生产 / 快速实现}} |

## 2. Monorepo 结构

```
{{repo}}/
├── apps/web/                # 前端应用（预留）
├── apps/server/
│   ├── gateway/             # API 网关
│   └── {{service_xx}}/      # 微服务
├── libs/shared/             # 共享 DTO/枚举/契约
└── ...
```

## 3. 服务清单

| 服务 | 职责 | 通信方式 | 代码位置 |
|------|------|---------|---------|
| {{service}} | {{职责}} | {{HTTP/gRPC/NATS}} | {{apps/server/xxx}} |

## 4. 项目规则（必须遵守）

- 分层：Controller → Service → Repository → Entity，单向向下，禁跨层。
- 命名：业务语言、语义化；状态/枚举/错误码常量化。
- 注释：讲 why；传参必写作用。
- 错误：统一响应 `{code,message,data}`；错误码分段；不吞异常。
- 提交：功能点一次提交 + eslint/commitlint + Conventional Commits。
- 契约：共享 DTO 放 `libs/shared`，单一事实源。

## 5. 开发进度

- 已完成 {{X}} / 共 {{Y}} 个功能点。
- 进行中：{{...}}；待做：{{...}}（详见 PLAN.md）。
- 业务组件沉淀判定：{{已沉淀 <组件名>（skill-knowledge/业务组件/backend/…） / 不沉（项目特有：<原因>）}}

## 6. 续做指引

1. 读 PLAN.md 定位「🚧 / ⏳」功能点。
2. 沿用本文规则与基础设施继续实现。
3. 完成一个更新 PLAN.md；结束时更新第 5 节。

> 最后更新：{{DATE}}