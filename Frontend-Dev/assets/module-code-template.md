# 页面/模块代码骨架模板

> 用途：步骤 7「逐页面测试先行实现」的施工骨架。一个模块/页面按本文档顺序落地：**先写测试 → api → hooks → 业务组件 → 页面容器 → 还原核对 → 功能点完成更新任务并提交**。
> 本文档是骨架（顺序与结构权威）；实际代码风格见 `references/code-style-guide.md`，分层归属见 `references/architecture-guide.md`，测试细则见 `references/test-guide.md`，不确定即问见 SKILL §八。

---

## 〇、开工前提

- [ ] 目标端已确认（web/app/小程序），技术栈已锁定（读 FTDD 或补选型确认）；
- [ ] **产出位置已确认**：用户给定的目标目录 + git 地址（代码直接落在该目录）；
- [ ] 工程骨架 + 全局基础设施已就绪（request/styles/router/hooks/测试环境）；
- [ ] FTDD 模块文档在侧：页面清单 / 组件清单 / hooks 设计 / fetch 对接 / §10 测试用例 / 对应原型文件；
- [ ] 原型还原基线已提取（结构/布局/配色/字号/三态）。

### 〇·二 不确定即问（全程，随时触发）

实现过程中只要出现下列情况，**立刻停下来问用户，不自己发挥**（有选项就给选项）：

| 触发 | 示例 |
|------|------|
| 需求口径不明 | PRD 未定义某状态/异常怎么处理 |
| 原型缺失或互斥 | 无空态/错误态；两套原型不一致 |
| 接口契约冲突 | FTDD fetch 对接与 TDD 字段/路径不一致 |
| 技术取舍 | 组件库能力不足需自研；虚拟滚动 vs 分页 |
| 组件归属难判 | 是否跨模块复用（features 还是 src/components） |
| 范围外发现 | 方案未覆盖的页面/字段/状态 |

提问模板：

```
【确认】{{一句话问题}}
影响：{{不确认会怎样}}
选项：A. {{方案A}}（推荐：{{理由}}） B. {{方案B}} C. {{暂不实现，标记 TODO}}
```

确认后把结论写进代码注释或 README 的「关键决策记录」。

---

## 一、模块边界确认（先小段声明）

每个模块开工前，用一小段文字说明「本模块做什么、包含哪些页面、复用边界」，与 FTDD 模块文档对齐：

> **模块 01_用户（features/users）**
> - 页面：用户列表（/users）、用户详情（/users/:id）
> - 复用：UserTable（用户模块内两页共用 → features/users/components）；UserSelect（用户+订单跨模块 → src/components）
> - 数据：GET /api/users、GET /api/users/:id（对齐 TDD/FTDD fetch 对接）
> - 测试用例：承接 FTDD 模块文档 §10 TC-M01-001~014（标注对应 AC-M01-xxx）

---

## 二、落地顺序（不可颠倒）

### Step 1：先写测试（承接 FTDD 用例，可先红）

按 `test-guide.md` 把 FTDD 模块文档 §10 的用例落成可运行测试文件，**测试未落、实现不开工**：

- `features/users/hooks/useUserList.test.ts` —— 数据流/异常（mock `userApi`）
- `features/users/components/UserTable.test.tsx` —— 渲染/交互/空态
- `features/users/UserListPage.test.tsx` —— 页面组装与三态
- 每个用例标注：`// TC-M01-001 —— 对应 AC-M01-001`

### Step 2：api 方法（契约对齐）

```ts
// src/api/user.ts
import { request, type PageResult, type PageParams } from './request';

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'operator';
  createdAt: string;
}

export const userApi = {
  /** 用户列表 —— GET /api/users */
  getUserList: (params: PageParams) => request<PageResult<User>>(`/api/users?${qs(params)}`),
  /** 用户详情 —— GET /api/users/:id */
  getUserById: (id: string) => request<User>(`/api/users/${id}`),
};
```

- 路径/方法/入参/出参与 FTDD fetch 对接及 TDD 接口**双向一致**；不确定先查 TDD，不改契约。

### Step 3：hooks 数据流

```ts
// src/features/users/hooks/useUserList.ts
export function useUserList(pageSize = 10) {
  // 三态：data/list + loading + error + refetch；竞态用 AbortController 取消
}
```

- 承接 FTDD hooks 设计；返回三态，供页面容器组合。

### Step 4：业务组件（先判归属，再写组件，再写该组件测试）

按「组件抽离铁律」先判定归属，再实现：

| 场景 | 归属 | 示例 |
|------|------|------|
| 仅本模块使用（模块内 ≥2 处复用） | `features/users/components/` | `UserTable`（列表页+详情页共用） |
| 跨模块（≥2 模块共用） | `src/components/` | `UserSelect`（用户+订单共用） |
| 无业务语义基础件 | 组件库 / `src/components/` | `Modal`/`Table` |

```tsx
// src/features/users/components/UserTable.tsx
import styles from './UserTable.module.scss';
export function UserTable({ users, loading, onRowClick }: UserTableProps) { /* ... */ }
```

### Step 5：页面容器（对照原型还原）

```tsx
// src/features/users/UserListPage.tsx（若 FTDD 为集中式则落 src/pages/users/）
export function UserListPage() {
  const { list, total, loading, error, fetchList } = useUserList();
  // 组合：骨架屏 / 错误重试 / 空态 / UserTable / 分页 —— 严格对照原型还原基线
}
```

- 页面只编排；对照原型逐区块还原（结构/布局/配色/字号/三态）；
- 路由注册 + 懒加载接入 `router/`。

### Step 6：还原核对（该模块页面）

按 `fidelity-guide.md` 对原型逐区块核对本模块页面，记录结论表；差异进入返工或登记基线。

### Step 7：功能点完成 → 更新任务 + 提交

- 「功能点」= 可独立验收的单元：一个页面 / 一个模块 / 一个被复用的组件 / 一个 hook + 其测试；
- 完成顺序：**① 自检 → ② 更新任务状态 → ③ 提交**：

**① 自检**（测试通过 + 还原核对 + 抽离合规 + 无调试代码）。

**② 更新任务状态**：
- todo 任务面板勾选该功能点为「已完成」；
- 同步更新 `PROJECT.md` 的「开发计划与任务清单」表（该条 → ✅ 已完成，记完成时间）；有新发现的功能点则追加。

**③ 提交**：先过三道门禁，再提交（配置见 `references/tech-stack-guide.md` §六）：

```bash
# 只暂存本次功能点涉及的文件（monorepo 下不卷入其它包）
git add <本次改动文件>

# 门禁（Husky 自动跑；未装 hook 时手动跑）
pnpm lint:es && pnpm lint:style

# 提交（commit-msg hook 校验信息格式）
git commit -m "feat(users): 用户列表页面与分页"
# feat / fix / refactor / test / chore + (模块): 说明
```

- 门禁失败 → **修到通过**，禁止 `--no-verify` 绕过；
- **不擅自 push**：是否推送远程由用户决定。

---

## 三、模块收尾自检（每模块交付前）

- [ ] 测试先行完成：组件/hooks/页面测试存在、`pnpm test` 该模块用例全绿？
- [ ] 组件归属符合抽离铁律：模块内 ≥2 次复用已抽 `features/<模块>/components/`，跨模块已提升 `src/components/`？无复制粘贴残留？
- [ ] 依赖单向向下：页面容器无业务逻辑、组件不直接调 api、hooks 不渲染？
- [ ] 接口契约对齐：fetch 方法路径/字段与 TDD/FTDD 一致？
- [ ] 三态齐全（加载/空/错误）？
- [ ] 还原度对照：结构/布局/配色/字号/三态与原型一致（含截图比对记录）？
- [ ] 注释**简单易懂 + 传参必注**：一句话讲 why、一行写完（复杂规则 ≤3 行）；方法/函数/hooks/组件每个参数写 `@param`；无废注释/死代码/魔法值？
- [ ] 共享类型只引用不重定义（monorepo：`import type` 自共享包）？
- [ ] 不确定之处已向用户确认并留痕（未自己发挥）？
- [ ] 每个功能点已更新任务状态（todo 勾选 + `PROJECT.md` 表）并单独 commit，提交信息符合 `feat(模块): 说明` 约定？
- [ ] 提交前过了 eslint + stylelint + commitlint，未 `--no-verify` 绕过？
- [ ] 提交内容 diff 自检：无 `console.log`、无临时文件、无密钥？
- [ ] 命名与 FTDD 页面/组件/hooks 一致？

---

## 四、多端差异注记（本模板为 web 例）

| 端 | 调整点 |
|----|--------|
| app | 路由/页面注册换框架路由；样式换算 dp/逻辑像素；组件目录语义不变 |
| 小程序 | `app.json`/pages 注册页面；rpx 按 750 换算；组件/逻辑抽离规则不变 |
| 通用 | 请求契约、组件抽离铁律、测试先行、还原核对顺序全端一致 |

> 组件归属、分层、抽离、测试先行等原则**不随端变化**，变的只是语法与容器适配。
