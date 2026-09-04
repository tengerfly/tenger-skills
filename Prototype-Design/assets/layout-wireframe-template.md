# 页面布局骨架（Wireframe）模板

> 用途：`Prototype-Design` 步骤 4.5「页面布局骨架确认」产出物的实现模板。
> 目标：用极简灰线框展示每个核心页面的**大致布局**（区块位置 + 相对比例），让用户在进入高保真前确认信息架构，防止后期布局返工。
> 铁律：只表达布局骨架——**不写真内容 / 不套真实配色字号 / 不引入视觉细节**。

## 一、产出物结构

```
.spec/原型/_layout/
├── _skeleton.css     # 极简骨架样式（灰块占位，本目录专用，不污染 style-guide.md）
├── index.html        # 入口页骨架（对应正式原型 index.html）
├── <页面2>.html      # 其余核心页骨架，命名与高保真页面一一对应
└── 说明：确认通过后高保真沿用同一命名与布局；_layout/ 去留由用户决定
```

## 二、区块写法示例

每块用灰色圆角矩形 + 区块名文字；导航 / 侧栏 / 内容用 flex / grid 表达真实分栏，不用最终视觉。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><title>布局骨架 — {{页面名}}</title>
<style>
  /* Wireframe 专用极简样式：灰块占位，非最终视觉 */
  body { margin:0; font-family:system-ui,sans-serif; background:#fafafa; color:#333; }
  .frame { max-width:{{容器宽}}; margin:0 auto; padding:16px; }
  .block { background:#e2e2e2; border:1px dashed #999; border-radius:6px; padding:12px; margin:6px 0; }
  .row { display:flex; gap:12px; }
  .row > .block { flex:1; }
  .page-tag { font-size:13px; color:#888; margin:2px 0 10px; }
</style>
</head>
<body>
<div class="frame">
  <div class="page-tag">布局骨架（非正式稿）· {{页面名}} · 对应 PRD：{{页面出处}}</div>
  <div class="block">顶部导航：Logo / 一级导航 / 用户入口</div>
  <div class="row">
    <div class="block">侧边栏：{{菜单项}}</div>
    <div class="block">主内容区：{{核心功能区块描述}}</div>
  </div>
  <div class="block">底部操作区：{{操作 / 分页}}</div>
</div>
</body>
</html>
```

## 三、规则

- **端类型匹配**：遵循已确认方案——Web 顶部导航 / 侧栏分栏；移动端底部 Tab / 单列堆叠；
- **可点跳转**：页面间放真实 `<a>` 链接，骨架也可点击走通导航；
- **区块文字用功能区块名**（列表区 / 筛选区 / 操作区 / 表单字段区），禁真实样例数据、禁控件级细节；
- **明确标注**：每页顶部标「布局骨架（非正式稿）」，避免被误认为成品；
- **改布局零成本**：用户有异议 → 只调整对应区块排布 / 比例 → 重出骨架，不进入高保真。

## 四、红线

1. 不写真实内容，不用最终配色 / 字体层级（那是高保真阶段套 token 的事）；
2. 高保真阶段布局**严格以已确认骨架为准**；如需改布局，回到步骤 4.5 重新确认，禁止绕过。