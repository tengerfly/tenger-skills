# PRD

产品需求域。负责把模糊想法收敛为可确认、可追踪、可交接的产品与原型基线。

## 主流程

`idea-intake` → `product-discovery` → `Competitive-Analysis` → `product-definition` → `application-blueprint` → `feature-decision` → `PRD-Design` → `PRD-Review` → `Prototype-Design` → `Prototype-Review`

## Skill 清单

| Skill | 职责 |
|---|---|
| `idea-intake` | 登记模糊产品想法、证据边界、未知项和确认问题 |
| `product-discovery` | 验证目标用户、问题场景、替代方案和证据强度 |
| `Competitive-Analysis` | 竞品、市场和用户反馈证据研究 |
| `product-definition` | 收敛问题、定位、价值、非目标和成功指标 |
| `application-blueprint` | 展开用户旅程、业务流程、能力地图、状态和异常闭环 |
| `feature-decision` | 冻结 MVP、功能价值/成本/风险/依赖和行为边界 |
| `PRD-Design` | 已确认产品定义、蓝图和功能决策的 PRD 兼容入口 |
| `PRD-Review` | PRD 多角色质量评审与问题回退 |
| `Prototype-Design` | 根据已批准 PRD 构建结构原型 |
| `Prototype-Review` | 原型完整性、交互闭环和状态覆盖评审 |
| `change-intake` | 变更任务入口和初步分类 |
| `impact-analysis` | 分析变更对产品、接口、数据、权限、测试、发布和运行的影响 |
| `product-analytics` | 用行为数据和产品指标判断功能效果与证据不足 |

## 边界

- 先记录事实、证据、推断、假设和开放项，再形成产品决策。
- 产品定位、目标用户、非目标、MVP、成功指标、关键规则和重大取舍必须经过用户或授权责任人确认。
- `PRD-Design` 是兼容入口，具体的发现、定义、蓝图和功能决策由前置原子 Skill 完成；不要把所有需求继续堆进一个大而全的 PRD Skill。
- 评审只审不改；问题回退到正确的上游 Skill，不用下游补丁掩盖需求缺口。

各 Skill 的入口文件为 `SKILL.md`，公共契约见仓库根 `../shared/`，系统注册见 `../governance/skill-registry.yaml`。
