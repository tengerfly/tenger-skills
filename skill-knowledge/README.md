# skill-knowledge —— AI 知识库引用层（本体在外部仓）

> 定位：本目录**不存组件本体**。AI 知识库本体 = 外部仓 `D:\project\agent-project\skills-knowledge\`（asset-library + 组件总清单 + 使用手册）；本目录是 tenger-skills 调度侧的**引用层 + 映射表**——skill 只保留对应引用，使用时从 skills-knowledge 检索，避免两仓混放导致项目混乱。
> 池属性：与 `issue/`、`bug-patterns/`、`evolution/` 同类——源仓库根集中物，不随 skill 副本部署。
> 单一事实源：资产逐项清单 = 外部仓 `asset-library/registry.yaml` 与 `组件总清单.md`；本仓 `映射表.md` 只记**调度侧对接关系**（消费 skill ↔ 能力域 ↔ 检索/沉淀入口），不复制资产明细，防双份维护漂移。

## 外部库使用入口

| 要做什么 | 去哪 |
|---|---|
| 冷启动/怎么用 | `skills-knowledge\AI组件库使用手册.md`（方法论一页纸） |
| 检索组件（组件决策链） | `skills-knowledge\asset-library\`：先判项目类型命中 `blueprints/`（可叠加取严）→ `capabilities/`（能力卡）→ `patterns/composites/`（方案）→ `adapters/`（落地） |
| 查全部资产清单 | `skills-knowledge\组件总清单.md`（盘点单一事实源）/ `asset-library/registry.yaml`（资产总索引） |
| 造新组件 | 封装七步法 `asset-library/shared/component-authoring.md`（新组件七步全走，小改动轻量通道①+⑥，造前写 asset-gap） |
| 沉淀/晋级/退役 | 外部仓沉淀闭环（evidence 回写 → 四出口判断），见使用手册 §六 |

## 消费方（谁在什么环节检索）

| 环节 | Skill | 入口 |
|---|---|---|
| 设计方案 | Frontend-Tech-Design / Backend-Tech-Design | S1.5 资产检索与选择（命中直接进方案组件清单） |
| 写代码 | Frontend-Dev / Backend-Dev | S1 组件决策链（命中复用/适配复用，禁重复手写） |
| 代码评审 | Code-Review | §4.1.0 资产与契约检查（零复制分叉 / 零静默发明 / 版本一致） |
| 测试 | auto-test / Testing | 开工盘点测试基建，命中锁版本 |

## 防冗余硬规则（硬性条件，三层生效）

**组件库不允许出现大量冗余并列组件。** 已有近似组件但不适用时——

1. **兼容性适配优先**：优先扩展现有资产（加参数/加 adapter/发新版本），而不是新建并列组件；
2. **无法适配才新建**：必须说明与既有资产的差异理由（写进 asset-gap），经用户确认才新建；
3. **或采用其他方案**：适配与新建都不划算时，留在项目内用不进池（项目特有组件不沉，判据：换个项目还能不能直接用或小改就用）。

设计（方案层就标注组件来源）、编码（决策链第③步）、沉淀（四出口判断前先查重）三层都按此执行；Code-Review 检出「并列冗余组件」记 P1。

## 双仓同步协议（更新时两边同时更新映射表）

外部库资产发生**新增 / 晋级（candidate→正式）/ 版本变更 / 废弃退役**时，同一次改动里完成两侧更新：

1. 外部仓：`registry.yaml` + `组件总清单.md` 对应条目；
2. 本仓：`映射表.md` 中受影响的「能力域 ↔ 消费 skill」行（含基建组件 ↔ 能力卡映射）。

只改一侧 = 同步未完成。映射表找不到对应资产时以外部仓清单为准并回补映射表。

## 目录约定

```text
skill-knowledge/
├── README.md    # 本文件：引用说明 + 使用入口 + 防冗余硬规则 + 同步协议
└── 映射表.md     # 调度侧对接关系：能力域 ↔ 外部资产 ↔ 消费 skill ↔ 状态
```
