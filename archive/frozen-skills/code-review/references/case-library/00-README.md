# 代码评审案例库（Case Library）索引

> 定位：写评审/走查时的**审查方法学参考**。本 Skill 的铁律（只审不改/定位到行/视角隔离/不评业务逻辑）与六大闭环优先，本库补「审查顺序/评论规范/AI 边界」等元方法论。
> 来源：jaess/mathieu/burakisk code-review-checklist、Google/Microsoft 评审实践、anthroos/googs1025 同类 Skill。已精编浓缩。

## 一、目录

| 文件 | 内容 | 何时读 |
|---|---|---|
| `review-methods.md` | 审查优先级/自动化/轻量/评论约定/反馈文化/反模式/AI 边界 | 定审查顺序、写评论时 |
| `agent-skill-samples.md` | 同类代码评审 Skill 结构样本 | 优化本 Skill 结构时 |

## 二、统一案例字段

> 场景 → 问题 → 方法/清单 → 出处 → 适用边界。

## 三、使用原则

1. **审查顺序优先于逐行挑刺**：先 Design → Correctness → Security → Readability → Testing，防 nitpick 战争。
2. **AI 审查边界是红线**：AI 适合 style/api/错误处理，不指望架构性建议；文件过多质量下降——写进自查，防过度自信。
3. **借鉴不照搬**：本 Skill 已有双视角 + 契约专项 + 六大闭环，案例方法学只作补充。
