# 自写风格候选（仅新方向探索时加载）

从原融合材料保留的八类启发，不是必选分类或硬性 token。以下“失格条件”仅帮助辨认原风格特征，不是通用门禁。优先使用用户已有品牌与设计系统；不要求旧项目在这些候选中重选，也不禁止有意且经确认的融合。

源材料归因沿用本地 OSS-Radar 记录（Ilm-Alan/frontend-design）；不把改编规则宣称为上游最新原文。

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


选择规则：先判断 Persuade/Operate/Read/Experience，再按产品、内容、可读性与用户意图挑候选；不把 Swiss/Industrial 固定为所有后台的默认答案。Aurora/Chaotic 可使用已批准的多色、渐变、多字体，不被其他风格的默认偏好否决。所有色彩仍须校验实际对比与语义，动效遵循用户偏好和可用性，不因选 Organic 就把所有动效设为 500ms。

候选只供沟通：实际颜色/字体/间距/组件落到本项目 `design-system.md`，规范的语义 token 才是后续唯一视觉依据。已有产品局部修改只加载其相关 token，不读取本候选库。
