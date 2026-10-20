# UI-UX-Design —— UI/UX 设计稿生成 Skill（双路径：Superdesign 云端 / AI 自写）

把「PRD + 布局清单 + 低保真原型」变成布局零改动、反 AI 味、风格统一的设计稿 HTML。

- 角色：设计总监 + 编排器；生成本体双路径——**A = Superdesign CLI 云端出稿**（有额度时），**B = AI 自写**（`references/self-write-sop.md`，无额度时默认，不阻塞）。
- 上游：Prototype-Design 的布局清单（载体级）+ 低保真原型 HTML（区块结构实物）。
- 流程：环境检测与路径路由 Gate（含 Superdesign 额度探测）→ 输入校验 + 任务清单 → 风格情报 → 风格决策 Gate → 设计规范 Gate → 〔A〕项目创建（基线复刻 → create-project）+ 逐页生成 / 〔B〕自写生成环 → 质量门禁 → 归档 `.spec/设计稿/`。

## 目录

| 文件 | 说明 |
|---|---|
| SKILL.md | 9 步 4 Gate / 双路径分工 / 迭代路由 / 额度红线 / 反 AI 味 12 条 |
| CONTEXT.md | 术语 + 决策日志 D-xx |
| assets/ | layout-inventory-contract / design-task-list / style-proposal / design-system（含 §0.5 YAML token 头）/ archive-readme |
| references/ | superdesign-sop（A 路径）/ self-write-sop（B 路径）/ design-review-gate（A 门禁）/ self-write-review-gate（B 门禁，唯一检查记录）/ motion-design-guide / open-source-design-systems / style-case-library / case-library/（总索引 + design-systems/layouts/components/interactions/flows/a11y）/ patterns/ |

## 环境依赖

- **A 路径**（Superdesign 云端）：

```bash
npm install -g @superdesign/cli@latest
superdesign login
```

  CLI 已装 + 账号已授权 + 额度可用，任一不过 → 转 B 路径，不阻塞。
- **B 路径**（AI 自写）：仅需浏览器工具（自检环截图；不可用 → 降级源码机械检查 + 用户确认）。

## 关键约定

- 布局零改动：只改好不好看，结构问题回 Prototype-Design。**冻结的是结构（有什么/在哪/怎么跳），不是呈现判断**。
- 设计稿不是原型换皮：原型文字分 ① 已批准产品文案（逐字保真）／② 原型说明层（编号牌、`【设计假设】`、`台账 §x`、元信息徽标、演示切换条等，禁入可见层）／③ 原型口语（按文案规范重写）；以「与原型文案逐字一致」当验收判据即违反铁律 4。
- 规范先行：design-system.md 未确认，不生成。
- 第一版不算数：任何路径的初稿必过自检环 + pre-flight（B 路径见 self-write-sop）。
- 跨页不变量必实测：多页交付的宽度档位与全局组件恒定，须逐页实测三值（A 门禁 §五 / B 门禁 §2）；design-system 里写了规范 ≠ 稿件已遵守，无测量值只能标「未验证」。**宽度先分角色**：承载跨页入口的全局导航外壳跨页恒定同宽同左缘，`max-width` 只落内容主列；只有页内标题栏才与内容主列对齐——两口径不可互换（见 design-system 模板 §5.11）。
- 额度即预算：变体/花钱动作由用户裁决；额度不足不是阻塞理由，转 B 路径；确定性修正走直编。
- 双目录：〔A〕`.superdesign/` 工作目录；`.spec/设计稿/` 交付目录（〔B〕下即唯一事实源）。
