# 代码编写规范（简洁 + 注释）

> 落地「代码简洁易懂、注释简洁清晰」；规则通用，示例按语言选读。

---

## 一、简洁性规范

### 1.1 函数短小、单一职责

- 一个函数只做一件事，超过约 30 行考虑拆分；
- 函数签名 = 一句话能说清「做什么」；签名里出现「and」通常说明职责过多该拆。

```go
// ❌ 一个函数既查库存又下单又发通知
func CreateOrderAndNotify(...) {}

// ✅ 拆分，各司其职
func CreateOrder(...) error      // 创建订单
func DeductStock(...) error      // 扣减库存
func NotifyUser(...) error       // 通知用户
```

### 1.2 命名规范（自解释 + 格式）

| 类型 | 要求 | 格式 | 反例 |
|------|------|------|------|
| 方法/函数 | 动词开头，见名知意 | **小驼峰（camelCase）** | `handle()` / `GetUser()` / `do_it()` |
| 类/接口 | 名词，见名知意 | **大驼峰（PascalCase），首字符必须大写** | `userService` / `order_controller` |
| 变量 | 业务语义，禁用无意义名 | 小驼峰 | `a` / `b` / `tmp` / `data` / `info` |
| 布尔 | `is`/`has`/`can` 前缀 | 小驼峰 | `flag` / `ok` |
| 常量/枚举 | 业务语义 + 分组 | 常量 `UPPER_SNAKE_CASE`，枚举名大驼峰 | 裸 `0` / `1` / `"1"` |

**命名格式铁律（NestJS/TS）**：
- **方法名小驼峰**：`createOrder`、`getUserById`、`deductStock`；
- **类名首字符必须大写**：`UserService`、`OrderController`、`PrismaUserRepository`；
- 接口名用 `I` 前缀或纯大驼峰（全库统一，二选一）。

### 1.3 禁止魔法值

状态、枚举、错误码、超时时间等一律定义常量/枚举，禁止散落裸值：

```go
// ❌ 魔法值散落
if order.Status == 1 { ... }

// ✅ 枚举 + 语义
type OrderStatus int
const (
    StatusPending   OrderStatus = 0 // 待支付
    StatusPaid      OrderStatus = 1 // 已支付
    StatusCancelled OrderStatus = 2 // 已取消
)
if order.Status == StatusPaid { ... }
```

### 1.4 少写「聪明」代码

- 能用清晰 if/else 就不用炫技三元链、位运算黑魔法、过度反射/泛型；
- 性能优化只在 TDD 明确有指标要求时做，且必须加注释说明依据；
- 控制嵌套深度（一般 ≤ 3 层），过深用「提前 return」展平。

```go
// ❌ 嵌套深、难读
func X(o *Order) error {
    if o != nil {
        if o.Status == StatusPaid {
            if o.Amount > 0 {
                // ...
            }
        }
    }
    return nil
}

// ✅ 提前 return 展平
func X(o *Order) error {
    if o == nil {
        return errors.New("订单不存在")
    }
    if o.Status != StatusPaid {
        return errors.New("订单未支付")
    }
    if o.Amount <= 0 {
        return errors.New("金额非法")
    }
    // ...
    return nil
}
```

---

## 二、注释规范（讲「为什么」）

### 2.1 核心原则

> **注释解释「为什么」，不解释「是什么」。** 代码本身已经表达了「是什么」，注释负责补充代码表达不了的「设计意图、业务规则、边界条件、取舍原因」。

### 2.2 必写注释的位置

| 位置 | 写什么 |
|------|--------|
| 对外接口 / 公共方法 | 一行说明「做什么 + 关键入参出参 / 异常」 |
| **方法传参** | **逐个写明每个参数的作用与约束（类型含义、取值范围、是否可空/可选）** |
| 复杂业务规则 | 说明「为什么这么判」+ 可引 TDD 方案/AC 编号 |
| 状态/枚举值 | 每个值的业务含义 |
| 关键技术点（事务/并发/缓存/幂等） | 方案与依据 |
| 非显而易见的边界处理 | 为什么这里要特判 |

### 2.3 禁止的注释

| 反例 | 问题 | 纠正 |
|------|------|------|
| `// 循环 i 从 0 到 n` | 重复代码 | 删除 |
| `// 待办：以后优化` 长期堆积 | 过时/无用 | 要么做要么删 |
| `// 判断是否为空` 配 `if x == nil` | 废话 | 删除 |
| 注释与代码不符 | 误导 | 改注释或改代码，保持一致 |

### 2.4 注释示例（NestJS）

```ts
// createOrder 创建订单：校验库存、预扣库存、生成订单记录。
// 入库失败时回滚库存，保证数据一致；幂等以 orderNo 唯一索引兜底。
async createOrder(
  // userId 下单用户 ID（必填，来自鉴权上下文）
  userId: number,
  // req 下单请求；amount 为金额（单位：分，必填，> 0），qty 为数量（必填，> 0）
  req: CreateOrderReq,
): Promise<Order> {
  // 金额统一以「分」为单位，避免浮点误差
  const amount = req.amount;
  // 乐观锁：version 字段更新时 +1 校验，防止并发超卖
  // ...
}
```

---

## 三、错误处理与统一响应

### 3.1 统一响应结构

所有接口返回同一结构（或团队约定），前端据此统一处理：

```json
{ "code": 0, "message": "ok", "data": { } }
```

- `code == 0` 成功；非 0 为业务/系统错误；
- `message` 对用户友好（中文可读），`data` 为业务数据。

### 3.2 统一错误码分段

| 分段 | 含义 | 示例 |
|------|------|------|
| 0 | 成功 | — |
| 1xxx | 参数错误 | 1001 参数缺失、1002 参数格式错误 |
| 2xxx | 业务错误 | 2001 库存不足、2002 订单已支付 |
| 3xxx | 权限错误 | 3001 未登录、3002 无权限 |
| 5xxx | 系统错误 | 5001 数据库异常、5002 内部错误 |

### 3.3 错误不吞

- 异常要么处理要么向上抛，**禁止空 catch / 空 defer recover**；
- 错误信息：对用户友好、对日志可追踪（带 trace_id）；
- 边界处统一兜底：未知异常归入 5xxx，不把堆栈/内部细节透出给前端。

```go
// ❌ 吞异常
func X() error {
    if err := do(); err != nil {
        // 什么都不做
    }
    return nil
}

// ✅ 要么处理，要么上抛
func X() error {
    if err := do(); err != nil {
        return fmt.Errorf("do failed: %w", err) // 上抛，保留上下文
    }
    return nil
}
```

### 3.4 参数校验分层

- Controller/Handler 做「格式校验」（非空、类型、长度、格式）；
- Service 做「业务校验」（存在性、状态合法性、权限归属）；
- 两层各司其职，不重复、不漏检。

---

## 四、多语言落点速查（默认 NestJS/TS）

> 后端默认 **NestJS（TypeScript）**；TDD 明确指定其它语言才用对应列。上文示例用 Go 作通用示意，各语言落点如下：

| 关注点 | NestJS/TS（默认） | Go | Java | Python |
|--------|------------------|----|----|--------|
| 接口解耦 | `@Injectable` + `interface` + DI | `interface` + 结构体 | `interface` + 构造器注入 | `Protocol` / ABC |
| 错误上抛 | `throw new BizException(...)` | `fmt.Errorf("%w", err)` | `throw` / 受检异常 | `raise` |
| 命名 | 方法小驼峰 / 类大驼峰（首字符大写） | 导出首字母大写 | 方法小驼峰 / 类大驼峰 | snake_case |
| 测试 | Jest（`describe`/`it`） | table-driven `go test` | JUnit `@Test` | pytest |
| 注释 | `/** */` + `//` | `//` | `/** */` + `//` | `#` + docstring |

> 各语言工程骨架、依赖清单、目录结构见 `references/tech-stack-guide.md`。

---

## 五、代码规范自检清单

- [ ] 函数单一职责、短小（≤30 行），命名见名知意（方法小驼峰、类名首字符大写）？
- [ ] 无魔法值（状态/枚举/错误码均已常量化）？
- [ ] 无炫技写法，嵌套深度 ≤ 3 层？
- [ ] 注释讲「为什么」，公共接口/复杂规则/枚举均有注释，无废注释？
- [ ] 统一响应结构 `{code,message,data}`，错误码分段统一？
- [ ] 异常不吞，未知异常统一兜底 5xxx 且不泄露内部细节？
- [ ] 参数格式校验在接口层、业务校验在 Service 层，不重复不漏检？
