# P0 建议补丁模板

> 用途：仅对 P0 问题附「建议补丁」。补丁以代码块形式写在评审报告里，**绝不落盘到源码**。
> 改代码是 `Backend-Dev` / `Frontend-Dev` 的职责，本补丁只表达"修复方向"，最终由用户裁决是否采用、由谁执行。

## 单个补丁结构

```markdown
### 补丁 P-{{编号}}

- **关联问题**：{{断点编号 + 一句问题描述}}
- **定位**：{{文件:行 / 接口 / 字段}}
- **根因**：{{为什么对不上 / 跑不起来}}

**建议补丁（示意，不落盘）**：

​```diff
- {{原文关键行}}
+ {{建议修改后}}
​```

- **影响面**：{{改动波及哪些文件 / 接口 / 调用方}}
- **验证方式**：{{改后如何验证：tsc / test / 契约比对}}
- **未落盘说明**：本补丁仅写于报告，未改动任何源码；是否采纳由用户决定。
```

## 示例（接口契约：入参个数不一致）

```markdown
### 补丁 P-01

- **关联问题**：C-01 订单创建接口入参个数不一致
- **定位**：`apps/server/order-service/order.controller.ts:42` ↔ `src/api/order.ts:18`
- **根因**：后端 `createOrder` 收 3 参（`userId, productId, quantity`），前端 `createOrder` 只传 2 参（`productId, quantity`），漏传 `userId`。

**建议补丁（示意，不落盘）**：

​```diff
- export function createOrder(productId: string, quantity: number) {
+ export function createOrder(userId: string, productId: string, quantity: number) {
```

- **影响面**：`src/features/orders/hooks/useCreateOrder.ts` 调用处需同步补 `userId`（从登录态取）。
- **验证方式**：`tsc --noEmit` + 对照 `contract-checklist.md` §3.1。
- **未落盘说明**：本补丁仅写于报告，未改动任何源码。
```

## 铁律

1. 补丁**只写报告、不落盘源码**；评审全程不改任何代码文件；
2. 补丁只给**方向与关键行**，不重写整个文件；
3. 涉及业务取舍的补丁（如枚举值以谁为准），必须标注「以 TDD 为准 / 请用户裁决」，不擅自定论。
