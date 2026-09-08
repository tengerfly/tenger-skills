# 案例库总索引（Case Library · 生长型）

> 用途：UI-UX-Design 的**外部与模式类案例资产总入口**。步骤 3（风格情报）按本索引检索，步骤 4（风格决策）引用，步骤 5（设计规范）仍须落 design-system 并经用户确认。
> 原则：**参考 ≠ 照抄**——外部资源只提取思路与 token 结构，禁止整站复刻；外部站点可能改版失效，**取用前先验证可达并核对许可**；库更新由用户手动发起。

---

## 一、案例库地图（四库分工）

| 库 | 文件 | 管什么 | 粒度 |
|---|---|---|---|
| 体系基线库 | `../open-source-design-systems.md` | Ant/Arco/shadcn/M3 四大体系的 token 结构思路与适用场景 | 体系级 |
| 外部产品 token 案例库 | `design-systems.md`（含 awesome-design-md 54 站） | 真实产品级设计系统的完整 token 细节（色彩/字体/组件/阴影/响应式/Do's&Don'ts） | 站点级·深 |
| **本案例库** | `case-library/`（本目录） | 布局模式 / 可复制组件 / 微交互 / 用户流 / 无障碍的资源索引与案例沉淀 | 模式级·广 |
| 自有项目案例库 | `../style-case-library.md` | 自家定稿项目的风格 DNA + 布局模式 + 踩坑清单 | 项目级·深 |
| 高频模式速查 | `../patterns/index.md` | 从案例中提炼的高频模式（导航/表单/反馈/空态） | 模式卡 |

---

## 二、检索顺序（步骤 3 风格情报）

```
读 PRD 定位（产品类型 × register[brand/product] × 端）
1. patterns/index.md          → 有无现成高频模式
2. flows.md                   → 同类产品的流程/状态怎么处理
3. layouts.md / components.md → 页面骨架与组件范式
4. interactions.md            → 微交互与动效表达
5. design-systems.md          → 体系基线选型 + 外部产品 token 案例（awesome-design-md 54 站）
6. style-case-library.md      → 自家已验证案例与踩坑
→ extract-website --design-md / 抓取摘录 → 步骤 4 风格决策 → 步骤 5 规范化（用户确认）
```

**实抓纪律**：检索命中后，对匹配场景的 **1~3 个资源用 `web_fetch` / `extract-website --design-md` 实抓提取**（教学类页提取模式要点，案例类提取场景/解法/参考截图），把要点带入步骤 4 风格决策与步骤 5 规范；抓取失败或站点失效 → 产出中标注「资源未取用（原因）」，**禁止凭链接名编造内容**。

---

## 三、条目统一字段（沉淀案例必填）

```
场景 → 问题 → 解法 → 可借鉴点 → 出处链接 → 截图/录屏 → 代码路径 → 无障碍备忘
```

- 每条带**元数据标签**：产品类型 / 气质（克制度·密度·圆角语言）/ 端（Web PC/H5/小程序/App）——供按 PRD 定位快速匹配；
- 微交互类按「触发方式（hover/click/scroll/state）× 反馈类型（确认/引导/奖励/状态）」入矩阵；
- 无障碍备忘为交互类条目**必填**（键盘可达 + 屏幕阅读器要点）。

---

## 四、本目录文件

| 文件 | 内容 |
|---|---|
| `design-systems.md` | 设计系统总集（10 大体系索引）+ awesome-design-md 54 站 token 级案例 |
| `layouts.md` | 布局资源与案例（C 端落地页 / 中后台信息架构 / 导航 / 响应式栅格） |
| `components.md` | 可复制组件/区块库（组件解剖样板） |
| `interactions.md` | 微交互矩阵 + 动效实现资源 |
| `flows.md` | 灵感/用户流（含状态表达：空态/错误态等） |
| `a11y-checklist.md` | 无障碍必检项 + 权威参考 |
| `../patterns/index.md` | 高频模式速查卡 |

> 建设参考（同类 Skill 的组织方式，元参考非案例）：interaction-design-skills、micro-interactions-skill、ui-ux-gold-standard、web-animation-skills——借鉴其 flows/states/micro-interactions 的结构化写法与模式卡组织。
