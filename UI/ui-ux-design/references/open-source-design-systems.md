# 开源设计系统沉淀库（Open Source Design Systems）

> 用途：UI-UX-Design 步骤 3（风格情报）与步骤 5（设计规范展开）的**体系基线**。风格方案推导时，从中选择与产品定位匹配的体系作为 token 结构与组件约定的参考基线——不自造无依据的值。
> 免责：具体色值随上游版本演进，**关键决策前以官方文档为准**（各节附官方地址）；本库沉淀的是「体系特征 + token 结构思路 + 适用场景」。

## 一、Ant Design 5（蚂蚁 · 企业级中后台事实标准）

- 官方：https://ant.design/docs/spec/introduce-cn · 主题：https://ant.design/docs/react/customize-theme-cn

| 维度 | 要点 |
|---|---|
| 气质定位 | 专业、克制、信息密度高；中后台系统的「默认普通话」 |
| Token 结构 | 三层：**Seed**（品牌种子，如 colorPrimary）→ **Map**（梯度派生，色板 1-10 级）→ **Alias**（语义别名，colorBgContainer、colorText…）——推导风格 token 时可借用此分层思路 |
| 关键默认值 | colorPrimary `#1677ff`；borderRadius `6px`；controlHeight `32px`；fontSize `14px`；三套预设算法（默认 / 暗色 / 紧凑） |
| 间距与密度 | 8px 基准；表格行高适中（~47px），紧凑算法可压缩 |
| 适用产品 | 中后台、数据密集工具、B 端 SaaS 主面板 |
| 本 skill 用法 | 风格方案定「专业/效率」向时的默认基线；设计规范 §5 组件状态约定（hover/active/disabled 三态）可对齐其交互规范 |

## 二、Arco Design（字节 · 精密工具风）

- 官方：https://arco.design/docs/spec/introduce

| 维度 | 要点 |
|---|---|
| 气质定位 | 精密、利落、工程师审美；比 Ant 更紧凑 |
| Token 特征 | colorPrimary `#165DFF`；**小圆角 2px** 为主（利落感来源）；描边式组件多 |
| 间距与密度 | 紧凑密度见长；适合表格/配置类重信息界面 |
| 适用产品 | 数据工具、开发者产品、监控/配置台 |
| 本 skill 用法 | 产品定位偏「工具效率、信息密度高、用户专业」时选它做基线；小圆角语言是它与 Ant 的最直观区分 |

## 三、shadcn/ui（社区 · 现代 SaaS 极简）

- 官方：https://ui.shadcn.com · 主题：https://ui.shadcn.com/themes

| 维度 | 要点 |
|---|---|
| 气质定位 | 极简、留白、当代感；开发者/SaaS 圈审美顶流 |
| Token 结构 | **纯 CSS variables**（`--background/--foreground/--primary/--muted/--ring`…），HSL 记法；中性基底 + 单一主色，强调色克制 |
| 关键默认值 | radius `0.5rem`（可整体切换 0~1rem 改气质）；字体 Inter/Geist 类现代无衬线；动效 subtle |
| 交互基座 | Radix Primitives（无障碍行为完备）——本 skill 输出纯 HTML 不依赖它，但其「状态命名」（default/hover/active/disabled + focus ring）值得对齐 |
| 适用产品 | 开发者工具、AI 产品、现代 SaaS、注重气质的 C 端轻工具 |
| 本 skill 用法 | 风格方案定「极简现代」向时的基线；CSS 变量组织方式与本 skill §7 Token 汇总结构同源 |

## 四、Material Design 3（Google · 内容消费与移动）

- 官方：https://m3.material.io

| 维度 | 要点 |
|---|---|
| 气质定位 | 亲和、活泼、内容优先；移动端体验标杆 |
| Token 结构 | **动态色（Dynamic Color）**：从种子色生成 tonal palette（primary/on-primary/surface/surface-variant…）；色彩即语义 |
| 关键默认值 | 大圆角语言（extra-large `28px`）；elevation 用「色调叠层」而非纯阴影；state layer 交互反馈 |
| 适用产品 | 移动端应用、内容消费、面向大众的轻产品 |
| 本 skill 用法 | 移动端任务或 C 端活泼方案时借其 tonal palette 思路（主色浅底对/深字对）与圆角语言 |

## 五、体系选择速查（风格方案推导用）

| 产品画像 | 首选基线 | 备选 |
|---|---|---|
| B 端中后台 / 数据密集 | Ant Design 5 | Arco（更紧凑） |
| 开发者工具 / 监控配置 | Arco | shadcn |
| 现代 SaaS / AI 产品 | shadcn/ui | Ant（偏 B 端时） |
| 移动端 / C 端轻产品 | Material 3 | shadcn（偏极简时） |

> 使用纪律：一次只借**一个体系**做基线（官方红线：两套风格混搭互相稀释）；借的是「token 结构 + 组件约定 + 气质」，主色等品牌值仍从产品定位推导（不默认 AI 蓝）。
