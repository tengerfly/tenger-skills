# CSS 架构规范

> 用途：指导 CSS 预编译、模块化与全局样式抽离的落地方式。

---

## 一、总则（四项铁律）

1. **预编译**：Sass（SCSS）/Less 二选一，按组件库与团队生态在 FTDD 选型中确定（本文示例以 SCSS 表述，Less 等价映射），禁止裸 CSS；
2. **组件样式隔离（随框架动态定）**：React→CSS Modules（`*.module.scss/less`）；Vue→`<style scoped>`（或 CSS Modules）；
3. **全局样式抽离**：`src/styles/` 集中管理设计 token 与全局基础样式；
4. **颜色一律引用变量**：禁止在组件内写死色值，主题切换才能生效。

---

## 二、全局样式目录（`src/styles/`）

```
src/styles/
├── variables.scss   # 设计 token（颜色/字号/间距/圆角/阴影），CSS 变量
├── mixins.scss      # 复用 mixin（文本省略/居中/响应式断点等）
├── global.scss      # reset + 全局基础样式（body/滚动条/通用类）
└── theme.scss       # 暗黑模式 / 主题切换（可选，按需）
```

> 扩展名随所选预处理器（.scss / .less）；Vue 项目文件位置与命名约定一致。

---

## 三、设计 token（variables.scss / variables.less）

```scss
// src/styles/variables.scss
:root {
  // 主色
  --color-primary: #4f6ef2;
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-danger: #ef4444;
  // 中性色
  --color-text: #1f2329;
  --color-text-secondary: #646a73;
  --color-bg: #ffffff;
  --color-bg-container: #f5f6f7;
  --color-border: #e5e6eb;
  // 字号（阶梯式层级：以正文 14 为基准逐级拉开，禁全部同级）
  --font-size-sm: 12px;
  --font-size-base: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 20px;
  // 字重（标题 600~700 / 正文 400，语义化引用禁写魔数）
  --font-weight-regular: 400;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  // 间距
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  // 圆角
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
}

// 暗黑模式（按需）
[data-theme='dark'] {
  --color-primary: #6b8afd;
  --color-text: #e8eaed;
  --color-text-secondary: #9aa0a6;
  --color-bg: #1f1f1f;
  --color-bg-container: #2a2a2a;
  --color-border: #3a3a3a;
}
```

---

## 四、mixins（mixins.scss）

```scss
// src/styles/mixins.scss
@mixin text-ellipsis {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

@mixin flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

@mixin respond-to($breakpoint) {
  @if $breakpoint == 'sm' {
    @media (max-width: 576px) { @content; }
  } @else if $breakpoint == 'md' {
    @media (max-width: 768px) { @content; }
  } @else if $breakpoint == 'lg' {
    @media (max-width: 1024px) { @content; }
  }
}
```

---

## 五、全局基础样式（global.scss）

```scss
// src/styles/global.scss
@use './variables.scss';
@use './mixins.scss';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#root {
  height: 100%;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: var(--font-size-base);
  color: var(--color-text);
  background-color: var(--color-bg);
}

a {
  color: var(--color-primary);
  text-decoration: none;
}
```

> 入口 `main.tsx` 统一引入：`import '@/styles/global.scss';`（若含主题，再 `import '@/styles/theme.scss';`）。

---

## 六、组件级样式（React CSS Modules / Vue scoped）

```tsx
// src/components/UserCard.tsx
import styles from './UserCard.module.scss';

export function UserCard({ name, role }: { name: string; role: string }) {
  return (
    <div className={styles.card}>
      <span className={styles.name}>{name}</span>
      <span className={styles.role}>{role}</span>
    </div>
  );
}
```

```scss
// src/components/UserCard.module.scss
.card {
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg-container);
}

.name {
  font-size: var(--font-size-lg);
  font-weight: 600;
}

.role {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}
```

Vue 3 等价写法（scoped）：

```vue
<!-- src/components/UserCard.vue -->
<template>
  <div class="card">
    <span class="name">{{ name }}</span>
    <span class="role">{{ role }}</span>
  </div>
</template>

<style scoped lang="scss">
/* 或 lang="less"，随 FTDD 选型 */
.card {
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg-container);
}
.name { font-size: var(--font-size-lg); font-weight: var(--font-weight-semibold); }
.role { color: var(--color-text-secondary); font-size: var(--font-size-sm); }
</style>
```

---

## 七、暗黑模式 / 主题切换（可选）

1. 设计 token 用 CSS 变量定义（§三），暗黑模式通过 `[data-theme='dark']` 覆盖变量；
2. 切换逻辑封装 `useTheme` hook：切换时给 `<html>` 设置 `data-theme`，并持久化到 `localStorage`；
3. 组件库需确认支持 `ConfigProvider` 主题算法（如 AntD 的 `theme.darkAlgorithm`）；
4. 主题切换组件在总文档 §5 组件清单中登记。

---

## 八、CSS 方案自检清单

- [ ] 预处理器统一（Sass/Less 二选一，与 FTDD 选型一致），无裸 CSS？
- [ ] 组件样式按框架隔离（React CSS Modules / Vue scoped）？
- [ ] 全局样式抽离到 `src/styles/`（variables/mixins/global/theme）？
- [ ] 颜色全部引用 CSS 变量，无写死色值？
- [ ] 暗黑模式/主题（若开启）用 `data-theme` + CSS 变量覆盖？
- [ ] 入口统一引入 global.scss？
