# Decision Record Contract v1

## 1. 何时必须记录

以下决定必须写入 `.spec/decisions/`，不能只留在聊天记录：产品范围、MVP 取舍、竞品能力是否采用、关键交互、技术架构、数据模型/API、组件选型、兼容性、迁移、测试例外、发布/回滚、监控阈值、Gate 放行和资产归属。

## 2. 文件命名

```text
.spec/decisions/DEC-YYYYMMDD-序号-短标题.md
```

## 3. 模板

```markdown
# DEC-YYYYMMDD-001 标题

- 状态：PROPOSED | ACCEPTED | REJECTED | SUPERSEDED
- 生命周期：CREATE | CHANGE | DEFECT | REFACTOR | INCIDENT | OPTIMIZE
- 提出人：
- 决策人：
- 日期：YYYY-MM-DD
- 影响范围：
- 关联产物：
- 关联证据：

## 背景

## 选项

| 选项 | 收益 | 成本 | 风险 | 可逆性 |
|---|---|---|---|---|

## 决策

## 原因与权衡

## 后果

## 复核条件

## Gate

- gate: PASS | CONDITIONAL | BLOCKED
- allowDownstream: true | false
```

## 4. 规则

AI 可以填写候选方案和证据，但不能替用户/授权责任人把 `PROPOSED` 改为 `ACCEPTED`。否决、延期和“暂不决定”也要记录，避免后续模型重复猜测。