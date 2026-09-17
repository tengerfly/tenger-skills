# 动效实现指南（Motion Implementation）

> 用途：Frontend-Dev S7 实现动效时 REQUIRED 加载；S9 验收动效自查项依据。
> 分工：**动效值**（时长 / 缓动 / 强度档）以 `design-system.md` §6/§7 为准（设计侧判据见 UI-UX-Design `references/motion-design-guide.md`）；本文件管**怎么实现得对**——组件手感、性能、无障碍。
> 降级路径：项目无 `design-system`（无设计稿、视觉基准回退原型）时，按本指南默认曲线与时长档收敛，并在 PROJECT.md 明示「动效值 = motion-guide 默认档」。
> 原则：不自造时长 / 曲线；动效是「反馈与过渡」不是装饰。

## 目录

- [一、组件手感（默认必做）](#一组件手感默认必做)
- [二、性能规则](#二性能规则)
- [三、无障碍](#三无障碍)
- [四、手势与拖拽（项目涉及时）](#四手势与拖拽项目涉及时)
- [五、交错与编排](#五交错与编排)
- [六、调试与自查](#六调试与自查)

## 一、组件手感（默认必做）

1. **按压反馈**：可点元素 `:active { transform: scale(0.97) }`（0.95-0.98 区间），`transition: transform 160ms ease-out`——让界面「听得见」用户按下；
2. **禁止从 `scale(0)` 进入**：入场从 `scale(0.95) + opacity: 0` 起步（现实中没有东西凭空出现，scale(0) 像凭空蹦出）；
3. **浮层 origin-aware**：popover / 下拉 / 菜单的 `transform-origin` 对准触发点，不居中缩放；**弹框例外**——弹框在视口居中出现，保持 center；
4. **Tooltip 延迟策略**：首个延迟出现（防误触）；已有一个打开时，相邻 tooltip 立即显示并跳过动画（工具栏整体变「快」）；
5. **可打断的 UI 用 transition，不用 keyframes**：transition 可中途改向（Toast 连发、快速开关不重启归零）；keyframes 中断即从头开始；
6. **blur 掩蔽不完美过渡**：两态 crossfade 重叠显得生硬时，过渡期加 `filter: blur(2px)`（不超过 20px，Safari 高开销）桥接两态；
7. **进场优先 `@starting-style`**（现代 CSS，免 JS 挂载态）：浏览器兼容不足时回退 `data-mounted` 属性模式（useEffect 置位）。

## 二、性能规则

1. **只动 `transform` 和 `opacity`**（跳过布局与绘制，走 GPU）；禁动画化 `padding` / `margin` / `width` / `height` / `top` / `left`；
2. **不在父级更新 CSS 变量驱动位移**：CSS 变量可继承，父级改动触发全部子元素样式重算——直接改元素自身 `transform`；
3. **使用动效库时（Motion / framer-motion）**：其 `x` / `y` 简写走主线程 rAF，**不是**硬件加速；密集场景用完整 `transform: "translateX(...)"` 字符串；
4. **预定动画优先 CSS**：CSS 动画在主线程外运行，页面加载 / 脚本繁忙时不掉帧；JS 只用于动态、可打断的场景；程序化控制用 WAAPI（`element.animate(...)`，CSS 性能 + JS 控制力）；
5. **`will-change` 克制**：只加在确实要动的元素上，不批量预加；
6. **`translateY(100%)` 用百分比**：相对元素自身尺寸，自适应内容高度，不硬编码像素（抽屉 / Toast 通用）。

## 三、无障碍

1. **reduced-motion 必做**（存在动效即必做）：`@media (prefers-reduced-motion: reduce)` 下**减少而非清零**——保留 opacity / 颜色过渡（帮助理解状态变化），去掉位移 / 缩放 / 视差 / 循环动画；
2. **hover 门控**：hover 动效包在 `@media (hover: hover) and (pointer: fine)` 内——触摸设备 tap 会误触发 hover；
3. **循环动画**：自动播放且与内容并存的动效 >5 秒时，提供暂停 / 停止；
4. **不阻塞交互**：交错 / 入场播放期间元素可点，不给关键内容加长延迟。

## 四、手势与拖拽（项目涉及时）

- **动量关闭**：速度 `|位移| / 耗时 > 0.11` 即关闭，不要求拖过距离阈值（轻扫即可关）；
- **边界阻尼**：越界拖动越拖越缓（摩擦感），不用硬停（撞隐形墙）；
- **pointer capture**：拖动开始后捕获指针，移出元素边界仍跟随；
- **多点保护**：首次拖动开始后忽略后续触点（防跳位）；
- 拖动期间禁文本选择。

## 五、交错与编排

- 多元素整体入场时用交错（`animation-delay` 递增），间隔 **30-80ms**（更长显慢）；
- 交错是装饰：不 delay 关键内容、不阻塞交互；
- 一个编排好的页面级入场 > 每个区块都 fade-up + 每张卡都 hover（反 AI 味一致）。

## 六、调试与自查

- 慢放 / 逐帧：DevTools Animations 面板减速播放，检查——两态过渡是否平滑（有无双影）、easing 是否突兀、`transform-origin` 是否正确、多属性是否同步；
- 触摸交互（抽屉 / 滑动）上真机验证效果与跟手度；
- **交付前动效自查表**：

| 检查 | 修正 |
|---|---|
| `transition: all` | 列明具体属性：`transition: transform 200ms ease-out` |
| `ease-in` 用于 UI | 换 ease-out 或 design-system 自定义曲线 |
| `scale(0)` 入场 | 从 `scale(0.95) + opacity: 0` 起步 |
| 常规 UI 动效 >300ms | 按 design-system 时长档收敛（常规 <300ms；弹层 / 抽屉类据档） |
| 动画化布局属性（width/height/top…） | 改 transform / opacity |
| 无 reduced-motion 分支 | 补 `@media` 包裹（减少非清零） |
| hover 动效无门控 | 补 `@media (hover: hover) and (pointer: fine)` |
| 自造时长 / 曲线值 | 换 design-system token |
