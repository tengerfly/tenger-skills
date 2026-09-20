# AI 自写设计稿 SOP（B 路径）

> 定位：Superdesign 无额度（或用户指定）时的生成本体——会话模型自己写设计稿 HTML。本 SOP 保证质量对齐 A 路径。
> 质量来源：2026-09-20 OSS-Radar 采集 14 个开源设计 skill 的精华整合（出处见 skills-knowledge 仓 `.spec/开源情报/情报库.md`）。三大支柱：**生成前的设计计划自查**（anthropics frontend-design）、**写作中的红线**（taste-skill / emil / vercel / avoid-ai-design）、**交付前的有界自检 + pre-flight**（impeccable / design-taste）。

## 一、总纲：Iron Law 与生成主循环

- **Iron Law：第一版永远不算数**（never ship the first version）。第一版是草稿，精华在第二三遍；跳过自检 = 自写路径最大失败模式。
- **主循环**：读输入（布局清单/原型/design-system）→ 设计计划（§三）→ 唯一性自查 → 成稿（守 §四红线）→ 自检环（§六）→ pre-flight（§七）→ 交付。
- **有界验证封顶**（防无限打磨烧 token，对齐 impeccable）：渲染截图全量检查 **1 次** → 一次批量修复 → 复核确认 **1 次** → 停。仍有问题 → 停下与用户对齐（3 轮上限沿用 `../../shared/anti-deadloop.md`）。
- 页面级时间预算意识：开放式自检是在烧用户的钱；批量检查（桌面+移动一起看）优于逐条挤牙膏。

## 二、生成契约（每页 HTML 必须满足）

继承原直编契约（它本来就是给 AI 手写 HTML 定的规范）：

1. 单个完整文档：`<!DOCTYPE html>` … `</html>`，单屏页面稿；
2. Tailwind utility 类做样式（CDN 引入）；图标 `<iconify-icon>` 且 `<head>` 自带其 CDN script；
3. `<body>` 无 class，布局全在单个根 `<div>`；
4. 每个 `<a>` 唯一描述性 id 且不嵌套；链接只用完整 `https://` 或 `#hash`，**禁相对路径**（交互结构随布局零改动保留：原型中真实可跳转的入口必须是真 `<a>`/等价触发，禁降级为死样式）；
5. 所有视觉值出自 design-system 的 token（页面 `:root` 落其 §7 汇总），规范外值 = 门禁返工。

## 三、设计计划（写码前必做 · anthropics 两遍式）

每页先出**简短设计计划**（不写码），包含：

| 项 | 要求 |
|---|---|
| 色彩 | 从 design-system token 取，4–6 个命名 hex + 各自角色 |
| 字体 | 各层级角色（display/正文/数据），对齐 §2 排版 |
| 布局概念 | 一句话 + 区块顺序（照布局清单，禁发明） |
| 本页记忆点 | **大胆只花在一个地方**：一个元素当记忆点，其余安静（对齐 §4.3 自我约束） |
| 动效与交互 | 按 design-system §6 强度档 + §5 状态规范 |

**唯一性自查**（过一遍才准写码）：「拿一个相似产品的 brief 来，我会写出同一版吗？」会 → 落入通用默认，改掉并说明改了什么、为什么（对齐主 SKILL §4.3 自查法）。

**禁美学形容词堆砌**：计划里写具体 token 值，不写 premium / elegant / 高级感——形容词渲染不出东西，值才可以。

## 四、写作红线（成稿时逐条自检）

1. **反 AI 味 12 条**：主 SKILL §4.3 全文有效（含五聚类判据与 AI Slop Test）。
2. **布局零改动**：只穿衣服不动结构；区块/组件/跳转逐项照布局清单与原型。
3. **文案保真 + 文案即设计**：PRD/布局清单一字不差、无出处不出现；界面文案按「动词条目（Save changes 非 OK）、错误指路不道歉、空态是行动邀请」写——文字是设计内容不是装饰。
4. **视觉纪律（hex 级禁令，精选自 taste-skill）**：
   - **三把锁**：页面唯一主题锁（明暗不中途翻转）；唯一强调色锁（全页同值，禁第 7 区突然换个蓝）；唯一圆角制锁（一套半径体系全页贯彻）；
   - `—`（em-dash）**零容忍**——出现在任何可见文本即返工；
   - **eyebrow 配额**：小号全大写宽字距标签 ≤ 每 3 区块 1 个（机械数 `uppercase` + `tracking` 实例）；禁装饰性编号（`01 / 02 / 03` 除非内容真是序列）；
   - **米+黄铜禁令**（高端消费者 AI 默认色板）：底 `#f5f1ea / #f7f5f1 / #efeae0` 系 + 点缀 `#b08947 / #b6553a / #9a2436` 系 + 文字 `#1a1714` 系，**默认禁**；brief 明示复古手工风才可用，且连续项目轮换色板族；
   - **衬线纪律**：衬线不做默认（"显得有质感"不是理由）；`Fraunces / Instrument Serif` 点名禁作默认；标题内强调词用**同字体**斜体/加粗，禁混族；
   - **CTA**：主按钮文字桌面端单行不折行（3 词内）；**一意图一标签**（"联系我们/Get in touch/Let's talk" 同页只留一个措辞）；
   - **图片**：内容图优先真实素材；占位用显式注释槽 `<!-- TODO: 首屏产品图 1600x1200 -->` 并在交付时列出；**禁 div 假截图、禁手绘装饰 SVG、禁 unicode 字符当图标（▣ ◊）**；logo 墙用真 SVG（`cdn.simpleicons.org/<slug>`）非文字 wordmark；
   - **动效硬规则**：禁 `transition: all`（列明属性）；只动 `transform/opacity`；常规 UI <300ms；禁 ease-in（用 design-system 的自定义曲线）；`:active { transform: scale(0.97) }`；弹层从触发器缩放（模态居中例外）；键盘触发的动作永不动画；`prefers-reduced-motion` 兜底。
5. **交互红线（vercel MUST 精选）**：导航用 `<a>` 禁 `div onClick`；移动命中目标 ≥44px；表单错误内联于字段旁、提交时聚焦首个错误；焦点可见（禁裸 `outline:none`）；hero 用 `min-h-[100dvh]` 禁 `h-screen`；长文本容器给 truncate/`min-w-0`。
6. **内容纪律**（content ≠ design）：屏上每个字符串要么是真信息、要么自知是占位；**禁**编造数据（假用户/假指标）、filler 标签（没人要的 mono-caps 小字幕）、主题化替换标准文案（"Authenticate Session" 代替 "登录"）、假精确数字（92%、4.1× 无出处）。

## 五、动效四问（写任何动画前，emil 框架）

| 问 | 判据 |
|---|---|
| ① 该不该动？ | 频率表：天天见（100+/日）→ 不动；高频 hover → 减或免；偶发弹层 → 标准；键盘触发 → **永不动画** |
| ② 什么目的？ | 空间一致 / 状态指示 / 解释 / 反馈 / 防跳变——答不出一句话目的 = 删 |
| ③ 什么缓动？ | 进出 → ease-out（自定义曲线）；屏内移动 → ease-in-out；hover/色变 → ease；匀速 → linear；**禁 ease-in** |
| ④ 多快？ | 按压反馈 100–160ms；tooltip/小浮层 125–200ms；下拉 150–250ms；弹层抽屉 200–500ms |

> 完整曲线 token 与强度档见 `motion-design-guide.md` 与 design-system §6/§7。

## 六、自检环（成稿后、交付前）

1. **渲染截图**：浏览器工具打开本地 HTML（`file://` 或 `python -m http.server`）截图，桌面 + 移动视口一起看；浏览器工具不可用 → 降级为源码机械检查（grep 红线项）+ 请用户打开确认，README「已知边界」注明；
2. **全量检查 1 次**：对照门禁六查 + 本 SOP 红线逐项过，问题记 **Before / After / Why 表**（一行一问题，Why 一句话讲理由）；
3. **一次批量修复 → 复核确认（第 2 次也是最后一次）→ 停**；
4. **对比纪律**：两版对比必须一次调用传两张图（分开调 = 两个幻觉面）；先 diff 出框、再对框内细看；
5. **置信标签**：检查结论标注 `code-certain`（源码可证，如 em-dash、hex 出处）/ `inferred`（需渲染判断，如节奏、层级；无渲染时显式降置信）。

## 七、Pre-flight 矩阵（放行前最后一道，全勾才交付）

- [ ] 设计读已宣示且用户未纠偏；设计计划做过唯一性自查
- [ ] 布局零改动逐项过（区块/组件/载体/跳转；入口可达非死链）
- [ ] 视觉值全出处（grep 色值/字号比对 token 表）
- [ ] em-dash = 0；eyebrow ≤ 1/3 区；无装饰编号；无 filler 标签
- [ ] 三把锁一致（主题 / 强调色 / 圆角制）
- [ ] CTA 单行 + 一意图一标签；无白底白字式对比度翻车
- [ ] 无 div 假截图 / unicode 图标 / emoji 图标；占位图有 TODO 槽
- [ ] 无 `transition:all` / 无 ease-in / 时长合规 / reduced-motion 兜底 / 键盘动作未动画
- [ ] 焦点可见；命中目标达标；表单错误内联；无 `h-screen`
- [ ] 文案与 PRD/布局清单逐字一致；无杜撰
- [ ] 反 AI 味 12 条全过 + **AI Slop Test**（告诉人「这是 AI 做的」，他会立刻信吗？会 → 回记忆点重审）
- [ ] 状态稿齐（布局清单涉及的空/错/加载/禁用态，对齐 design-system §5.10）
- [ ] **三成功判据**：Justified（每处改动服务既定方向）/ Coherent（字体·色板·布局·签名细节互相强化）/ Not-a-re-run（不是上一个项目的风格复刻——二阶默认也是默认，跨项目刻意换）

## 八、风格情报（步骤 3 的 B 路径通道）

1. 本仓 `references/case-library/`（检索顺序见其 00-README）；
2. **VoltAgent/awesome-design-md**（GitHub ⭐116k）：一线品牌 DESIGN.md 集合，按产品气质取 1–3 个实抓提取 token 结构；
3. 站点风格提取：browser 实抓截图 + 读 CSS，或 `npx extract-design-system <url>`（安全边界：不覆盖既有规范、不推断未清晰提取的值、单页不代表整站）；
4. **0 结果诚实**：检索不到 → 显式标注「无命中，采用 XX 通用基线」，禁凭链接名编造内容；
5. 全部遵守 case-library 总则：参考 ≠ 照抄，取用前验证可达与许可。

## 九、变体与迭代路由（B 路径版）

| 意图 | 做法 |
|---|---|
| 看不同方向 | 同布局并行写 2 版（不同锚点 token 包，§十），用户二选一 |
| 选定方向上改 | 该页 replace 式重写（受 §六有界验证约束） |
| 确定性修正（文案/链接/精确间距） | 本地直改（免全量自检环，pre-flight 抽查相关项） |
| 回旧版 | git 版本（本仓 .spec/设计稿 随仓库管理）或 `<页面>.v<n>.html` 副本 |

- 首张主流程页先出并请用户确认视觉方向，确认后再延展其余页（与 A 路径节奏一致）；
- 用户原话要求 → 原样进计划与红线，禁转译走样。

## 十、八锚点 token 包（三套方案的差异化弹药）

> 改编自 Ilm-Alan/frontend-design。每套风格方案绑定**一个**锚点；锚点锁定 token，出现「失格条件」即锚点没守住。中后台/产品 UI 优先 Swiss / Industrial（Operate 模式），营销页可放胆。brief 钉死方向时 **brief wins**。

| 锚点 | 底色 | 字体 | 点缀 | 结构特征 | 失格条件（Breaks if） |
|---|---|---|---|---|---|
| Swiss | `#FFFFFF` / `#F7F7F8` | Helvetica Neue / Söhne，单族 | Swiss Red `#E4002B` / Klein Blue `#002FA7` 择一 | 可见网格线/发丝线，左对齐不对称 | 暖纸底、衬线标题、居中排版 |
| Industrial | `#000000` / `#0B0C0A` | IBM Plex Mono / JetBrains Mono | 语义色一个：`#00E676` / `#FFB800` / `#C6FF4A` | 平面 1px 描边无阴影，tabular-nums | 衬线、圆角、装饰阴影、暖纸 |
| Brutalist | 纯原色对抗 `#FF0000/#0000FF/#FFFF00` | 系统字体混用 | 无点缀（原色即一切） | 硬偏移阴影 `8px 8px 0 #000`，原生控件，贴边排版 | webfont、柔和阴影、圆角 |
| Aurora | 深底渐变 `#5D34D0→#FF006E→#00F0FF` | Inter Variable / PP Neue Machina | 霓虹 glow text-shadow | mesh 渐变主面、弹性动效编排 | 平底、暖纸、克制发丝线 |
| Chaotic | 粉彩×霓虹对撞 `#FF71CE+#DFFF00+#00FFFF` | 3+ 族故意混排 | —— | 每面有图案，超大 display 对撞 | 和谐色板、单一字体、留白当结构 |
| Retro-Futuristic | `#0A0014` | VT323 / Orbitron / Space Mono | `#FF006E+#00FFFF` 或磷绿 `#00FF41` | CRT 扫描线 / 色差错位 `text-shadow` | 现代无衬线（Inter）、纸面、无质感 |
| Organic | 大地色 `#8B9D83 / #B08B6E / #C66B3D` | 人文衬线或暖几何无衬线 | —— | 圆角 16–32px，1–3% 噪点，300–500ms 缓动 | **奶 Cream `#F0+` 暖纸**、冷灰、纯黑纯白 |
| Lo-Fi | 纸黄 `#E8E0C0`（比 cream 饱和） | 系统字体混撞（Times+Helvetica+Courier） | —— | 元素 2–8° 旋转、半调网点、Risograph 错版 | 精确对齐、单一字体、平滑动效 |

**使用规则**：一次绑一个锚点，禁混装（"Swiss 带点 Brutalist"是范畴错误）；「意外配对」防安全默认（工业风花店 / 极简律所）——但配对要服务 brief，不为怪而怪。

**四模式定密度**（改自 impeccable，按页面成功标准选）：Persuade（营销/落地，表达优先）/ Operate（后台/工具，扫读与一致性优先）/ Read（文档/帮助，理解优先）/ Experience（作品/展示，内容本身优先）。模式写进设计计划，影响密度、表达与动效档。
