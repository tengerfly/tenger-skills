# 无障碍必检项（A11y Checklist）

> 定位：案例库·底线类。交互类案例的**必填备忘**来源；也是设计规范 §5 组件状态约定的可访问性基准。
> 与 Fidelity-Review 的关系：还原评审用 axe-core 数值判定（WCAG ≥ 4.5:1）——本清单是设计期的前置自查，评审期是机器复检。

## 一、权威参考

| 名称 | 链接 | 许可 | 案例库价值 |
|---|---|---|---|
| WAI-ARIA Authoring Practices | https://www.w3.org/WAI/ARIA/apg/patterns/ | 公开 | 官方组件无障碍模式（键盘/焦点/ARIA）权威参考 |
| React Aria | https://www.react-spectrum.org/react-aria | Apache-2.0 | Adobe 的无障碍原语实现 |
| Ark UI | https://ark-ui.com | MIT | 基于状态机的无头组件，默认可达 |
| Zag.js | https://zagjs.com | MIT | 框架无关、状态机驱动的无头交互逻辑 |

## 二、设计期必检要点

| 检查项 | 要求 |
|---|---|
| 对比度 | 正文 ≥ 4.5:1；大字 ≥ 3:1（占位/禁用态允许豁免，但须可辨识） |
| 焦点可见 | 所有可交互元素有 focus ring（勿 `outline: none` 不补偿） |
| 键盘可达 | 弹框/菜单/命令面板：Tab 循环 + Esc 关闭 + 焦点陷阱 |
| 触控目标 | 移动端 ≥ 44px；Web 常规 32~40px（对齐 design-system §3） |
| 语义与 ARIA | 图标按钮有 aria-label；弹层用 role + aria-expanded；勿滥用 role |
| 动效降级 | 装饰性动效支持 `prefers-reduced-motion` |
| 纯色辨信息 | 状态不用颜色单维表达（配文字/图标，色盲可辨） |

## 三、沉淀约定

每个交互类案例（interactions/flows）沉淀时必填「无障碍备忘」字段：键盘路径 + 焦点行为 + 屏幕阅读器要点；案例转设计规范时同步写入组件状态约定。
