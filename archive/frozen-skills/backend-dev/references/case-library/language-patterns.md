# 语言级代码规范（Language Patterns）

> 用途：按语言落地分层与代码模式。黄金规则 + 目录结构 + 代码模式。

---

## 一、Node.js（NestJS 默认）

- **目录**：`src/modules/<domain>/`（controller/service/repository/entity + dto）。
- **统一响应**：`{code, message, data}`；DTO 用 class-validator。
- **代码模式**：`@Injectable()` Service 面向接口 + DI；SQL 只进 Repository。

## 二、Go（Gin/GORM）

- **目录**：`internal/<domain>/`（handler/service/repository/model）。
- **代码模式**：Repository 原生 SQL + `context.Context` 取消；错误上抛不吞。
- **范例**（字节青训营风格）：
  ```go
  // UserRepository 数据访问，只做单表操作
  func (r *UserRepo) GetByID(ctx context.Context, id int64) (*User, error)
  ```

## 三、Java（Spring Boot）

- **目录**：`com.x.<domain>/`（controller/service/repository/entity）。
- **代码模式**：`JpaRepository` 接口 + 查询方法；`@Transactional` 边界在 Service。
- **安全**：Spring Security `SecurityFilterChain` + BCrypt。

## 四、Python（FastAPI）

- **目录**：`app/<domain>/`（router/service/repository/model）。
- **代码模式**：Pydantic schema 做 DTO；SQLAlchemy 在 repository。

## 五、通用规范

- 命名业务化；方法小驼峰、类大驼峰；禁 a/b/tmp/data。
- 金额整数分；时间戳/ISO8601。
- 统一响应 + 错误码分段（1xxx 参数/2xxx 业务/3xxx 权限/5xxx 系统）。

> 出处：skillmd.ai/skills/backend-developer、github.com/khalidbelk/awesome-backend、字节青训营。
