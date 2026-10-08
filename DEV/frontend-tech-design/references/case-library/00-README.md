# 前端技术方案案例库（Case Library）索引

> 定位：写前端技术方案时**按需加载**的架构/选型参考。与 Frontend-Dev 的 case-library 分工：本份管「架构/工程化/选型」，那份管「组件模式/框架写法/编码规范」。
> 来源：Feature-Sliced Design 官方、Vercel/Anthropic agent-skills、微前端实战。已精编浓缩。

## 一、目录

| 文件 | 内容 | 何时读 |
|---|---|---|
| `architecture-patterns.md` | FSD/Atomic/Clean/Micro-FE/Next 架构范式 | 选架构风格时 |
| `state-management.md` | 状态分类 + 框架选型 | 定状态方案时 |
| `performance-security.md` | 性能六板斧 + 安全清单 | 写性能/安全章节时 |
| `agent-skill-samples.md` | 同类前端 Skill 结构样本 | 优化本 Skill 结构时 |

## 二、统一案例字段

> 场景 → 问题 → 解法/架构 → 出处 → 适用边界。

## 三、使用原则

1. **架构选型回溯到规模**：Flat/FSD/Micro-FE 按团队规模与独立部署诉求选，不做减法反例。
2. **选型结论仍须收敛证明**：案例范式是参考起点，写入方案前过 socratic-grilling 收敛（失败/涨 10 倍/漏项 + 用户认可）。
3. **不写死框架**：端形态+技术框架每次必问，案例只给决策依据。
