# 【服务/模块代码骨架】{{NN}} {{MODULE_NAME}}

> **所属工程**：{{PRODUCT_NAME}} 后端（Monorepo）　|　**对应 TDD 方案**：`{{NN}}_{{module_name}}.md`　|　**创建/更新**：{{DATE}}
> 📐 本文件是单个服务/模块的**代码骨架**：测试先行 + 四层实现。示例语言为 **NestJS（TypeScript）**，其它语言见 `references/tech-stack-guide.md` §四。

---

## 1. 服务/模块边界（来自 TDD 模块方案）

| 应做（技术职责） | 不应做（负向边界） |
|----------------|-------------------|
| {{DO}} | {{DONT}} |

- 上下游依赖：上游 {{UP}}，下游 {{DOWN}}，通信方式 {{HTTP/gRPC/NATS}}（与 TDD「上下游依赖」一致）。

## 2. 测试先行【必须 · 先写】

> 先把 TDD 模块方案的「TDD 测试用例」落地成测试代码（此时未实现，运行应为失败）。

```ts
// {{module}}.service.spec.ts —— 承接 TDD 用例 TC-{{NN}}-001/002/003/004/005
describe('{{ServiceName}}.{{Method}}', () => {
  // mock 仓储接口，隔离外部依赖
  const repo = { findById: jest.fn(), create: jest.fn() } as any;

  beforeEach(() => {
    service = new {{ServiceName}}(repo);
  });

  it('正向用例 —— 正常创建', async () => {   // 正向
    repo.create.mockResolvedValue({ id: 1 });
    const r = await service.create({ ... });
    expect(r.id).toBe(1);
  });

  it('边界用例 —— 库存刚好', async () => { }); // 边界
  it('异常用例 —— 库存不足抛业务错误', async () => { // 异常
    await expect(service.create({ qty: 2 })).rejects.toThrow(BizException);
  });
  it('幂等用例 —— 相同幂等键重复提交', async () => { }); // 幂等
  it('并发用例 —— 并发扣减不超卖', async () => { });       // 并发
});
```

## 3. 数据模型层 Entity/Model【第 4 层】

> 与 TDD「全局表结构设计」逐字段对应，纯数据载体，无业务逻辑。

```ts
// {{module}}.entity.ts —— 表：{{table}}（对应 TDD 表结构）
export class {{Table}} {
  id: number;                     // 主键
  {{field}}: {{type}};            // {{注释，与表结构一致}}
  amount: number;                 // 金额（单位：分）
  status: {{StatusEnum}};         // 状态：{{枚举含义，引用 libs/shared/enums}}
  createdAt: Date;                // 创建时间
  updatedAt: Date;                // 更新时间
  deletedAt: Date | null;         // 软删除时间
}
```

## 4. 数据访问层 Repository【第 3 层】

> 只做表增删改查，SQL/ORM 只在这一层；不写业务规则。

```ts
// {{module}}.repository.ts
export interface {{Table}}Repository {
  findById(id: number): Promise<{{Table}} | null>;
  create(data: Create{{Table}}Data): Promise<{{Table}}>;
  updateStatus(id: number, status: {{StatusEnum}}): Promise<void>;
}

@Injectable()
export class Prisma{{Table}}Repository implements {{Table}}Repository {
  constructor(private readonly prisma: PrismaService) {}

  async findById(id: number) {
    return this.prisma.{{table}}.findUnique({ where: { id } });
  }
  // ...
}
```

## 5. 业务层 Service【第 2 层】

> 核心流程、业务规则、事务边界；面向接口；不碰传输层、不写 SQL。

```ts
// {{module}}.service.ts
@Injectable()
export class {{Module}}Service {
  // 依赖注入仓储「接口」，便于测试 mock
  constructor(private readonly repo: {{Table}}Repository) {}

  // {{Method}} {{做什么}}。
  // 参数：req {{逐个说明参数作用——req.xx 是什么、取值范围、是否必填}}。
  // 业务规则：{{关键规则，如「金额以分为单位」「状态未支付才可操作」}}。
  // 幂等/并发：{{如「orderNo 唯一索引兜底幂等」「乐观锁 version 防超卖」}}。
  async {{method}}(req: {{Method}}Req): Promise<{{Table}}> {
    // 1. 业务校验（存在性/状态/权限）
    // 2. 核心逻辑（事务边界在 Service）
    // 3. 返回结果
    throw new Error('not implemented');
  }
}
```

## 6. 接口层 Controller【第 1 层】

> 只做路由、参数校验、调 Service、统一响应；不写业务逻辑。

```ts
// {{module}}.controller.ts
@Controller('{{path}}')
export class {{Module}}Controller {
  constructor(private readonly svc: {{Module}}Service) {}

  // {{Method}} {{HTTP 方法 + 路径}} —— 对应 TDD 接口 & 前端 FTDD fetch 对接
  // 参数：dto {{请求体参数作用——字段含义、必填性、格式校验}}。
  @Post()
  async {{method}}(@Body() dto: {{Method}}Dto) {   // class-validator 格式校验在接口层
    const data = await this.svc.{{method}}(dto);
    return Response.ok(data);   // 统一响应 {code:0,message:"ok",data}
  }
}
```

## 7. 接口契约对齐【必须】

| 后端接口 | TDD 接口 | 前端 FTDD fetch | 共享 DTO（libs/shared） | 是否一致 |
|---------|---------|----------------|------------------------|---------|
| `{{METHOD}} {{PATH}}` | {{TDD 出处}} | {{FTDD 出处}} | {{dto 名}} | ✅ / ❌ |

- 入参/出参字段、枚举值、分页结构（`{list,total}`）前后端统一，DTO 放 `libs/shared` 复用。

## 8. 服务/模块自检清单

- [ ] 测试先写，五类用例（正向/边界/异常/幂等/并发）齐全，标注 AC 编号？
- [ ] 四层齐全，依赖单向，无跨层调用？
- [ ] Entity 与表结构逐字段一致，金额整数分、状态枚举引用共享包？
- [ ] Repository 只有 SQL，无业务判断；Service 无 SQL、无传输层解析？
- [ ] 接口路径/参数/返回与 TDD + FTDD 一致，DTO 下沉 `libs/shared`？
- [ ] 无跨服务直连数据库、无跨服务 import 内部实现？
- [ ] 关键逻辑有「为什么」注释，公共方法有说明？
- [ ] 方法有传参时，注释逐个写明每个参数的作用与约束？
- [ ] 错误不吞，统一响应/错误码（引用共享枚举）？
- [ ] 功能点完成后已跑 eslint + commitlint 校验并自动提交？
