# 测试实现规范（测试先行）

> 用途：把 TDD 文档里的测试用例落地成可运行的测试代码。**先写测试，再写实现。**

---

## 一、测试先行总则

- **测试用例来源 = TDD 模块方案的「TDD 测试用例」**：已写好的「Gherkin 场景 + 代码级用例骨架」，直接落地成可运行测试，**不必重新设计用例**；
- **顺序固定**：先写测试（此时测试是红的，编译/运行失败）→ 再写实现（让测试转绿）→ 重构保持简洁；
- **测试随代码交付**：测试能 `go test` / `mvn test` / `pytest` / `npm test` 一键跑通，不是摆设。

---

## 二、五类用例覆盖（缺一不可）

| 类型 | 测什么 | 示例 |
|------|--------|------|
| 正向 | 正常输入得到预期结果 | 库存充足 → 下单成功、库存扣减 |
| 边界 | 临界值 / 空值 / 极值 | 库存刚好等于购买量、空列表、0 值 |
| 异常 | 非法输入 / 依赖失败 | 库存不足、数据库错误、参数非法 |
| 幂等 | 重复请求结果一致 | 相同幂等键重复提交不产生新订单 |
| 并发 | 并发场景数据一致 | 并发扣减库存不超卖 |

> 每条测试标注对应 AC 编号（`AC-Mxx-nnn`），与 TDD 用例、PRD 验收标准可追溯。

---

## 三、分层测试策略

| 层 | 测试类型 | 怎么测 | 重点 |
|----|---------|--------|------|
| Service | 单元测试 | mock 掉 Repository（用接口 mock） | 业务规则、状态流转、事务边界 |
| Repository | 集成测试 | 连测试库 / 事务回滚 | SQL 正确性、字段映射 |
| Controller/Handler | 接口契约测试 | mock 掉 Service，测路由/校验/响应 | 路径、参数校验、统一响应结构 |

- **Service 是测试重点**：业务规则、异常分支、边界、幂等、并发都在这一层，单测覆盖最密集；
- **mock 面向接口**：因为 Service 面向接口编程，mock 接口实现即可隔离外部依赖，这也是「接口解耦」的测试红利。

---

## 四、测试代码示例（默认 NestJS，其它语言备选）

### 4.1 NestJS（Jest）

```ts
// order.service.spec.ts —— 承接 TDD 用例 TC-M03-001/002/003
describe('OrderService.createOrder', () => {
  const repo = { findStock: jest.fn(), save: jest.fn() } as any;

  beforeEach(() => {
    service = new OrderService(repo);
  });

  it('正向：正常创建并扣减库存', async () => {
    repo.findStock.mockResolvedValue(10);
    repo.save.mockResolvedValue({ id: 1 });
    const r = await service.createOrder({ qty: 2 });
    expect(r.id).toBe(1);
  });

  it('边界：库存刚好', async () => { /* 库存 2 买 2，成功且库存为 0 */ });

  it('异常：库存不足抛业务错误', async () => {
    repo.findStock.mockResolvedValue(1);
    await expect(service.createOrder({ qty: 2 })).rejects.toThrow(BizException);
  });
});
```

### 4.2 Go（table-driven）

```go
// CreateOrder 创建订单 —— 承接 TDD 用例 TC-M03-001/002/003
func TestCreateOrder(t *testing.T) {
    cases := []struct {
        name      string
        stock     int  // 输入：库存
        qty       int  // 输入：购买数量
        wantErr   bool // 预期：是否报错
        wantStock int  // 预期：扣减后库存
    }{
        {"正常创建", 10, 2, false, 8}, // 正向
        {"库存刚好", 2, 2, false, 0},  // 边界
        {"库存不足", 1, 2, true, 1},   // 异常
    }
    for _, c := range cases {
        t.Run(c.name, func(t *testing.T) {
            repo := newMockRepo(c.stock)              // mock 仓储
            svc := NewOrderService(repo)
            err := svc.CreateOrder(context.Background(), c.qty)
            if (err != nil) != c.wantErr {
                t.Fatalf("wantErr=%v, got err=%v", c.wantErr, err)
            }
            if got := repo.stock(); got != c.wantStock {
                t.Fatalf("wantStock=%d, got=%d", c.wantStock, got)
            }
        })
    }
}
```

### 4.3 Java（JUnit）

```java
// CreateOrder 创建订单 —— 承接 TDD 用例 TC-M03-001/002/003
@Test
void createOrder_库存不足_抛业务异常() {
    when(orderRepo.findStock(anyLong())).thenReturn(1); // mock 仓储
    assertThrows(BizException.class, () ->
        orderService.createOrder(new CreateOrderReq(2L, 2)));
}
```

### 4.4 Python（pytest）

```python
# CreateOrder 创建订单 —— 承接 TDD 用例 TC-M03-001/002/003
@pytest.mark.parametrize("stock,qty,want_err", [
    (10, 2, False),  # 正常创建
    (2, 2, False),   # 库存刚好
    (1, 2, True),    # 库存不足
])
def test_create_order(stock, qty, want_err):
    repo = MockRepo(stock)                 # mock 仓储
    svc = OrderService(repo)
    if want_err:
        with pytest.raises(BizError):
            svc.create_order(qty=qty)
    else:
        svc.create_order(qty=qty)
```

---

## 五、幂等与并发用例写法

### 5.1 幂等

```go
// 幂等：相同幂等键重复提交，不产生新订单，返回原订单
func TestCreateOrder_Idempotent(t *testing.T) {
    svc := NewOrderService(newMockRepo(10))
    key := "idem-001"
    o1, _ := svc.CreateOrder(ctx, qty=2, idemKey=key)
    o2, _ := svc.CreateOrder(ctx, qty=2, idemKey=key)
    if o1.ID != o2.ID {
        t.Fatalf("幂等失效：%d != %d", o1.ID, o2.ID)
    }
}
```

### 5.2 并发（不超卖）

```go
// 并发：100 并发各买 1 件，库存 10，只允许 10 单成功，最终库存 0
func TestCreateOrder_Concurrent(t *testing.T) {
    repo := newMockRepo(10)
    svc := NewOrderService(repo)
    var wg sync.WaitGroup
    var success atomic.Int32
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            if err := svc.CreateOrder(ctx, 1); err == nil {
                success.Add(1)
            }
        }()
    }
    wg.Wait()
    if success.Load() != 10 {
        t.Fatalf("超卖：成功 %d 单，应 10 单", success.Load())
    }
}
```

> 并发正确性依赖实现层的乐观锁/悲观锁/唯一索引，测试只负责「验证不超卖」，锁方案在 Service/Repository 实现（对齐 TDD 关键技术点）。

---

## 六、测试自检清单

- [ ] 每个模块先写测试再写实现（测试先行）？
- [ ] 测试用例直接承接 TDD 用例，标注 AC 编号，不重造？
- [ ] 五类覆盖（正向/边界/异常/幂等/并发）齐全？
- [ ] Service 层单测 mock 仓储、覆盖业务规则最密集？
- [ ] Repository 集成测试、Controller 契约测试各就位？
- [ ] 测试能一键跑通，随代码一起交付？
