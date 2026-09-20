# NestJS 微服务工程落地骨架

> 用途：技术栈锁定后，把「微服务 + Monorepo」落成具体目录与依赖。**后端默认 TypeScript + NestJS**；TDD 明确指定其它语言时才走第四节备选。
> 版本给的是「常用稳定版」，落地时应以官方稳定版为准（有可用浏览器工具时可查最新版；无则按 TDD 指定版本或官方稳定版落定，不构成浏览器依赖）。

---

## 一、默认技术栈（TDD 未明确时直接采用）

| 项 | 默认 | 备选 | 说明 |
|----|------|------|------|
| 语言/框架 | TypeScript + NestJS | — | 后端主栈，微服务首选 |
| 包管理/仓库 | pnpm + workspace（Monorepo） | npm/yarn | 前后端同仓库 |
| ORM | Prisma | TypeORM | 不确定则给选择项 |
| 微服务通信 | gRPC（同步）+ NATS/Kafka（异步） | TCP / Redis | 按需选，见第三节 |
| 配置 | `@nestjs/config` + 环境变量 | — | 配置外置 |
| 校验 | `class-validator` + `class-transformer` | — | DTO 校验 |
| 测试 | Jest + Supertest | Vitest | NestJS 生态默认 |
| API 文档 | OpenAPI（`@nestjs/swagger`） | — | 契约单一事实源，可生成前端类型 |

---

## 二、NestJS 微服务 Monorepo 骨架

### 2.1 目录结构（前后端同仓库）

```
repo/                              # 前后端同仓库（monorepo）
├── apps/
│   ├── web/                       # 前端应用（Frontend-Tech-Design 落地目标，预留）
│   └── server/
│       ├── gateway/               # API 网关：HTTP 入口，路由到各微服务
│       │   └── src/main.ts
│       ├── user-service/          # 微服务 A（与 TDD 模块对应）
│       │   ├── src/
│       │   │   ├── main.ts        # createMicroservice 启动
│       │   │   ├── user.module.ts
│       │   │   ├── user.controller.ts
│       │   │   ├── user.service.ts        # 接口 + 实现
│       │   │   ├── user.repository.ts
│       │   │   ├── user.entity.ts
│       │   │   └── user.service.spec.ts   # 测试（先写）
│       │   └── tsconfig.json
│       └── order-service/         # 微服务 B
├── libs/
│   └── ../../shared/                    # 共享代码（单一事实源）
│       ├── dto/                   # 共享 DTO（前后端复用）
│       ├── enums/                 # 共享枚举/常量（状态值、错误码分段）
│       ├── contracts/             # 服务间消息契约 / gRPC proto
│       └── index.ts
├── package.json                   # pnpm workspace 根
├── pnpm-workspace.yaml
├── tsconfig.base.json
├── .env.example
└── README.md
```

### 2.2 依赖（根 package.json 关键项）

```json
{
  "scripts": {
    "build": "pnpm -r build",
    "test": "pnpm -r test",
    "dev": "pnpm -r --parallel dev",
    "lint": "eslint \"apps/**/src/**/*.ts\" \"libs/**/*.ts\"",
    "lint:fix": "eslint --fix \"apps/**/src/**/*.ts\" \"libs/**/*.ts\"",
    "commitlint": "commitlint",
    "prepare": "husky"
  },
  "dependencies": {
    "@nestjs/common": "^10.4.4",
    "@nestjs/core": "^10.4.4",
    "@nestjs/microservices": "^10.4.4",
    "@nestjs/config": "^3.2.3",
    "@nestjs/swagger": "^7.4.2",
    "class-validator": "^0.14.1",
    "class-transformer": "^0.5.1",
    "reflect-metadata": "^0.2.2",
    "rxjs": "^7.8.1"
  },
  "devDependencies": {
    "@nestjs/testing": "^10.4.4",
    "prisma": "^5.21.1",
    "jest": "^29.7.0",
    "ts-jest": "^29.2.5",
    "supertest": "^7.0.0",
    "typescript": "^5.6.3",
    "eslint": "^8.57.1",
    "@typescript-eslint/parser": "^7.18.0",
    "@typescript-eslint/eslint-plugin": "^7.18.0",
    "@commitlint/cli": "^19.5.0",
    "@commitlint/config-conventional": "^19.5.0",
    "lint-staged": "^15.2.10",
    "husky": "^9.1.6"
  }
}
```

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/**'
  - 'libs/**'
```

### 2.3 分层示例（服务内部四层 + 依赖注入）

```ts
// user.service.ts —— 面向接口编程，依赖接口不依赖实现
export interface UserRepository {
  findById(id: number): Promise<User>;
  create(data: CreateUserData): Promise<User>;
}

@Injectable()
export class UserService {
  // 构造器注入仓储「接口」，便于单测 mock
  constructor(private readonly userRepo: UserRepository) {}

  // getUser 查询用户：不存在时抛业务错误（错误码统一分段）
  async getUser(id: number): Promise<User> {
    const user = await this.userRepo.findById(id);
    if (!user) {
      throw new BizException(ErrorCode.USER_NOT_FOUND); // 业务错误，不吞
    }
    return user;
  }
}
```

```ts
// user.controller.ts —— 接口层：路由 + 参数校验 + 调 Service + 统一响应
@Controller('users')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Get(':id')
  async getUser(@Param('id', ParseIntPipe) id: number) {
    const user = await this.userService.getUser(id);
    return Response.ok(user); // 统一响应 {code:0,message:"ok",data}
  }
}
```

### 2.4 提交校验配置（eslint + commitlint + husky）

> 提交前强制 eslint + commitlint 校验，不通过不提交；工程初始化时一次性配好。

```js
// commitlint.config.js —— 统一 Conventional Commits
module.exports = { extends: ['@commitlint/config-conventional'] };
```

```json
// .lintstagedrc.json —— 只校验暂存文件
{ "*.{ts,js}": ["eslint --fix", "prettier --write"] }
```

```bash
# husky git hooks：提交前 lint-staged 校验代码，提交信息走 commitlint 校验
npx husky add .husky/pre-commit "npx lint-staged"
npx husky add .husky/commit-msg "npx --no -- commitlint --edit $1"
```

---

## 三、微服务通信方式选型

| 通信方式 | 适用 | 优点 | 注意 |
|---------|------|------|------|
| **gRPC** | 服务间同步调用、强类型契约 | 性能高、proto 即契约、多语言 | 需定义 `.proto`，契约放 `libs/shared/contracts` |
| **NATS** | 事件驱动、异步解耦、云原生 | 轻量、发布订阅简单 | 消息幂等/重试需自管 |
| **TCP** | 快速起步、同构微服务 | 最简单 | 无类型契约、生产慎用 |
| **Redis** | 轻量发布订阅 | 复用缓存组件 | 可靠性一般 |
| **HTTP** | 对外网关、跨端调用 | 通用、前端友好 | 服务间内部调用不推荐 |
| **Kafka** | 高吞吐事件流 | 持久化强、吞吐高 | 运维重 |

> 选型规则：**对外统一 HTTP（网关）**；**服务间同步 → gRPC**（契约强）；**异步/解耦 → NATS/Kafka**。不确定时用选择项让用户确认。

---

## 四、其它语言备选（仅当 TDD 明确指定）

> TDD 明确指定 Go / Java / Python 时才跟随；否则一律 NestJS。以下骨架仅作快速参考。

### 4.1 Go（Gin + GORM，微服务）

```
app/
├── cmd/<service>/main.go      # 每服务一个入口
├── internal/<service>/        # controller/service/repository/entity
├── pkg/shared/                # 共享：DTO/常量/工具
└── go.mod
```
关键依赖：`gin`、`gorm`、`grpc`（服务间通信）、`testify`。

### 4.2 Java（Spring Boot + Spring Cloud）

```
app/
├── <service>/
│   ├── src/main/java/...      # controller/service/impl/mapper/entity
│   └── pom.xml
├── ../../shared/                    # 共享模块
└── pom.xml（父）
```
关键依赖：Spring Boot、Spring Cloud（Nacos/OpenFeign）、MyBatis-Plus/JPA、JUnit 5。

### 4.3 Python（FastAPI + SQLAlchemy）

```
app/
├── services/<service>/        # controller/service/repository/model
├── ../../shared/                    # 共享
└── requirements.txt
```
关键依赖：FastAPI、SQLAlchemy、pydantic、pytest。

---

## 五、版本锁定与配置外置

| 项 | 约定 |
|----|------|
| 版本锁定 | 依赖写死稳定版本（不用 `latest`），锁定锁文件（`pnpm-lock.yaml`/`go.sum`/`pom.xml`） |
| 配置外置 | 连接串/密钥/端口走环境变量或 `.env`，禁止硬编码进代码 |
| 环境样例 | 提供 `.env.example`，敏感值占位不提交真实值 |
| 共享包版本 | `libs/shared` 用 workspace 引用（`"@repo/shared": "workspace:*"`），不发布私有包亦可 |
| README | 写清：Monorepo 结构、各服务启动命令、迁移执行、配置说明、服务/模块清单 |
