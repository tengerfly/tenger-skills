# 设计系统总集（Design Systems）

> 定位：案例库·设计系统类。两层：①开源体系索引（体系基线选型入口，配合 `../open-source-design-systems.md` 的深读）；②awesome-design-md 54 站**外部产品 token 级案例**（真实产品怎么定色彩/字体/组件/阴影/响应式）。
> 免责：外部资源取用前验证可达、正式商用前核对 LICENSE；参考 ≠ 照抄，提取值仍须过步骤 5 用户确认。

---

## 一、开源设计系统总集（学原则 / 栅格 / 间距 Token / 组件规范）

| 名称 | 链接 | 许可 | 案例库价值 |
|---|---|---|---|
| awesome-design-systems | https://github.com/alexpate/awesome-design-systems | MIT | 200+ 设计系统索引，按「组件/语音语调/设计师套件/源码」打标，做系统选型的入口 |
| Design Systems Repo | https://www.designsystems.com/ | 免费参考 | 大厂设计系统合集 + 案例文章（栅格、图标、排版、内容策略） |
| Google Material Design (M3) | https://m3.material.io | Apache-2.0 | 栅格布局、响应式动效、色彩系统范式，最完整的官方规范之一 |
| Ant Design（阿里） | https://ant.design | MIT | 企业级组件 + 中文文档齐全，适合 B 端 / 后台案例 |
| IBM Carbon | https://carbondesignsystem.com | Apache-2.0 | 企业级复杂系统典范，栅格/无障碍/数据密集界面 |
| Shopify Polaris | https://polaris.shopify.com | MIT | 电商流程、商家后台交互范式 |
| Microsoft Fluent 2 | https://fluent2.microsoft.design | MIT | 跨平台一致性、动效与材质语言 |
| GitHub Primer | https://primer.style | MIT | 开发者工具类产品的极简 UI 范式 |
| Atlassian Design System | https://atlassian.design | MIT | 协作类产品的体系化组件与模式 |
| GOV.UK Design System | https://design-system.service.gov.uk | MIT | 公共服务 / 极简 / 高可访问性标杆 |

**沉淀格式**：每个系统抽 1 张「栅格 + 间距 Token + 主色板」速查卡，配一句设计哲学。

---

## 二、awesome-design-md：54 站外部产品 token 级案例

> 来源：https://hu-uh.github.io/awesome-design-md/ （上游 VoltAgent/awesome-design-md，MIT）。把真实产品设计系统整理为 Google Stitch 规范的 DESIGN.md 纯文本，**天然适合作为风格参考/上下文喂给 AI Agent**（配合 Superdesign `--context-file` / `extract-website --design-md`）。

### 取用方式

```
https://raw.githubusercontent.com/hu-uh/awesome-design-md/main/design-md/<站点>/DESIGN.md
示例：https://raw.githubusercontent.com/hu-uh/awesome-design-md/main/design-md/linear.app/DESIGN.md
```

每个站点 3 个文件：`DESIGN.md`（完整设计系统）+ `preview.html`（浅色 Token 预览）+ `preview-dark.html`（深色 Token 预览）。

### DESIGN.md 9 章节规范（与我们 design-system 模板的对照）

| 章节 | 内容 | 对应我们 |
|---|---|---|
| 1 Visual Theme & Atmosphere | 视觉基调与设计哲学 | §0 设计原则 |
| 2 Color Palette & Roles | 色彩体系与语义命名 | §1 色彩系统 |
| 3 Typography Rules | 字体家族 + 完整层级表（含字距） | §2 字体排版 |
| 4 Component Stylings | 按钮/卡片/输入框/导航等组件状态 | §5 组件规范 |
| 5 Layout Principles | 间距系统、网格、留白哲学 | §3 间距 + §5.7 导航 |
| 6 Depth & Elevation | 阴影系统、表面层级 | §4 圆角与阴影 |
| 7 Do's and Don'ts | **设计禁区与反模式** | （参考其写法补门禁判定） |
| 8 Responsive Behavior | 断点策略、折叠、触控目标 | 设计门禁 §五 布局基线 |
| 9 Agent Prompt Guide | **AI 提示词参考（组件级 prompt 示例）** | 生成保真约束语素材 |

### 站点清单（54，按类检索）

- **AI / 开发者产品**：claude、cohere、cursor、mistral.ai、ollama、x.ai、minimax、runwayml、elevenlabs、together.ai、raycast、warp、expo、supabase、vercel、resend、posthog、sentry、mintlify、opencode.ai、replicate、composio、voltagent、hashicorp、mongodb、clickhouse、superhuman、lovable
- **设计 / 协作工具**：figma、framer、miro、clay、webflow、sanity、linear.app、notion、airtable
- **知名品牌 / C 端**：apple、airbnb、spotify、uber、bmw、spacex、pinterest、nvidia、ibm
- **金融科技**：stripe、coinbase、wise、revolut、kraken、intercom、zapier、cal

> 暗色模式专项：深色站点（linear/cursor/raycast/vercel 等）的 DESIGN.md 含「亮度阶梯做层级、半透明白边框替代阴影」的暗色模式方法论，做暗黑主题设计时优先参考。
