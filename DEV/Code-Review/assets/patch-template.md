# P0 建议补丁模板

> 仅 P0 附补丁，以代码块写进报告，不落盘源码。补丁只表达修复方向；是否采用由用户裁决。

## 结构

```markdown
### 补丁 P-{{编号}}
- 关联问题：{{编号 + 一句描述}}
- 定位：{{文件:行 / 接口 / 字段}}
- 根因：{{为什么对不上}}

**建议补丁（示意，不落盘）**：
​```diff
- {{原文关键行}}
+ {{建议修改后}}
​```

- 影响面：{{波及文件/接口/调用方}}
- 验证方式：{{tsc / test / 契约比对}}
- 未落盘说明：仅写于报告，未改源码。
```

## 示例

```markdown
### 补丁 P-01
- 关联问题：C-01 创建接口入参个数不一致
- 定位：order.controller.ts:42 ↔ src/api/order.ts:18
- 根因：后端收 3 参、前端只传 2 参，漏 userId
**建议补丁（示意，不落盘）**：
​```diff
- export function createOrder(productId, quantity) {
+ export function createOrder(userId, productId, quantity) {
​```
- 影响面：useCreateOrder 调用处补 userId
- 验证方式：tsc --noEmit + contract-checklist
```

## 铁律
1. 只写报告、不落盘源码。
2. 只给方向与关键行，不重写整文件。
3. 涉及业务取舍（如枚举以谁为准）标「以 TDD 为准 / 请用户裁决」。