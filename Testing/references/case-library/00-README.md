# 测试案例库（Case Library）索引与使用说明

> 定位：写测试计划/用例/选框架时**按需加载**的参考素材。不是必读，是查证与借鉴用。
> 来源：QA 开源聚合清单（TheJambo/awesome-testing 等）、同类 Agent Skill（qaskills/petrkindlmann/kakawaa）、中文社区（TesterHome）。已精编浓缩，非原文搬运。

## 一、目录

| 文件 | 内容 | 何时读 |
|---|---|---|
| `testing-methods.md` | 测试金字塔/TDD/BDD/四象限/风险驱动/Page Object/测试数据 | 定测试策略、写计划时 |
| `testing-frameworks.md` | 按语言/类型框架速查（单测/API/E2E） | 选测试框架时 |
| `testing-special.md` | 性能/安全/契约/可视化/AI 测试专项 | 命中专项需求时 |
| `agent-skill-samples.md` | 同类 QA Skill 结构样本（qaskills 等） | 优化本 Skill 结构时 |

## 二、统一案例字段

> 场景 → 问题 → 解法/工具 → 关键代码 → 反模式/坑 → 出处。

## 三、使用原则

1. **框架选型回溯到场景**：每个框架选择要能答「为什么这个语言/这个类型用这个」。
2. **专项测试不默认上**：性能/安全/契约/可视化/AI 命中需求信号才启用（见 `decision-rules.md` §三）。
3. **借鉴决策不照搬**：案例工具/阈值是参考起点，最终以 SKILL.md 铁律与项目实际为准。
