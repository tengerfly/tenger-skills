# 【前端模块技术方案】{{MODULE_INDEX}}_{{MODULE_NAME}}

> **所属总文档**：{{PRODUCT_NAME}} 前端 FTDD　|　**模块定位**：{{MODULE_SUMMARY}}
> **责任前端架构师**：{{AUTHOR_NAME}}　|　**文档状态**：`[草稿]/[待评审]/[已定稿]`
> 📐 本文件是前端技术方案 **L2 模块细节**：边界 → 页面组件拆分 → hooks 数据流 → fetch 对接 → 状态管理 → 关键点 → 实现细节与决策 → 异常 → 测试用例。

---

## 1. 模块概述与边界

### 1.1 定位与职责
{{MODULE_FRONTEND_RESPONSIBILITY}}

### 1.2 应做 / 不应做（负向边界）
| 应做（前端技术职责） | 不应做（明确排除） |
|---------------------|-------------------|
| {{承载哪些页面 / 提供哪些 hooks / 消费哪些接口}} | {{明确排除，如不负责全局权限校验}} |

---

## 2. 上下游依赖

| 方向 | 模块/系统 | 传递产物/前提 | 方式 |
|------|----------|--------------|------|
| 上游 | {{页面入口来源 / 路由}} | {{入口前提}} | 路由跳转 / 共享状态 |
| 下游 | {{下游模块/页面}} | {{产物}} | 路由跳转 / 回调 |
| 接口 | 后端 {{SERVICE}} | {{接口列表}} | fetch（见 §4） |

---

## 3. 页面与组件拆分

### 3.1 页面清单（本模块）

| 页面 | 路由 | 职责 | 对应原型文件 |
|------|------|------|-------------|
| {{PAGE_A}} | {{/path}} | {{DUTY}} | {{proto.html}} |

### 3.2 组件拆分表

| 组件 | 分层 | 职责 | 复用范围 |
|------|------|------|---------|
| {{Component_A}} | 业务组件 | {{DUTY}} | 模块内 / 全局 |

### 3.3 页面组件结构图（Mermaid，可选但推荐）

```mermaid
flowchart TD
    Page[{{页面容器}}] --> Search[{{筛选组件}}]
    Page --> Table[{{列表组件}}]
    Page --> Modal[{{表单弹窗组件}}]
    Page --> Hook[{{数据 hooks}}]
```

---

## 4. hooks 数据流设计

| hook | 职责 | 依赖接口 | 返回 |
|------|------|---------|------|
| {{useXxxList}} | {{数据获取 + 筛选分页}} | {{api.getXxxList}} | `{ list, total, loading, error, fetchList }` |
| {{useXxxForm}} | {{表单值与提交}} | {{api.createXxx / updateXxx}} | `{ form, submitting, submit }` |

> 数据流原则：页面容器组合 hooks → hooks 调用业务 api → 数据经 props 下发到业务组件。

---

## 5. fetch 接口对接（与后端 TDD 一一对应）

| 前端方法 | 后端接口（TDD） | 方法 | 入参 | 出参 |
|---------|----------------|------|------|------|
| `{{api.getXxxList}}` | {{/api/xxx}} | GET | {{IN}} | {{OUT}} |
| `{{api.createXxx}}` | {{/api/xxx}} | POST | {{IN}} | {{OUT}} |
| `{{api.updateXxx}}` | {{/api/xxx/:id}} | PUT | {{IN}} | {{OUT}} |
| `{{api.deleteXxx}}` | {{/api/xxx/:id}} | DELETE | {{IN}} | {{OUT}} |

---

## 6. 状态管理设计

| 状态 | 归属 | 管理方式 |
|------|------|---------|
| {{列表筛选/分页/表单值}} | 局部 | hooks 局部 state |
| {{跨模块共享态}} | 全局 | {{Zustand / Redux}} |
| {{列表/详情数据}} | 服务端 | {{TanStack Query / useFetch}} |

---

## 7. 关键技术点与难点

| 难点 | 方案 |
|------|------|
| {{列表大数据渲染}} | {{虚拟滚动 + 分页}} |
| {{表单校验}} | {{受控组件 + zod schema}} |
| {{请求竞态}} | {{AbortController 取消 + 去重}} |
| {{权限控制}} | {{usePermission + 按钮级权限}} |

---

## 8. 实现细节与决策【必须】（逐功能点展开到可编码）

> 每个功能点写清「前端每一步怎么做」+ 关键工程决策点结论，不能一句话带过。

| 功能点 | 实现步骤（前端每一步怎么做） | 关键决策点 + 结论 |
|---|---|---|
| {{功能点，如文件上传}} | {{① 选文件 → ② 分片/整传 → ③ 进度 → ④ 秒传 → ⑤ 重试}} | {{分片 or 整传 / 断点续传进度 / 秒传 / 取消 / 重试 / 大文件}} |

> 逐点过一遍前端工程决策点清单（数据来源/请求/加载态/竞态取消/权限/超大列表），能定写结论、前置已明确标「继承 PRD/TDD」、拿不准标「待用户确认」。

## 9. 异常与边界处理

| 异常场景 | 处理方案 |
|---------|---------|
| 接口加载中 | {{loading 骨架屏 / 占位}} |
| 接口失败 | {{错误态 + 重试按钮}} |
| 空数据 | {{空状态占位 + 引导}} |
| 未登录/无权限 | {{路由守卫 / 隐藏按钮}} |
| 请求超时/取消 | {{AbortController + ApiError 提示}} |

---

## 10. TDD 测试用例（先写测试，后写代码）

### 9.1 Gherkin 场景（承接 PRD 的 AC）

```gherkin
Feature: {{MODULE_NAME}}
  # 承接 AC-M{{MODULE_INDEX}}-001
  Scenario: {{正向场景}}【P0】
    Given {{前置状态}}
    When {{用户操作}}
    Then {{可见结果 / 状态变化}}

  Scenario: {{异常场景}}【P0】
    Given {{前置状态}}
    When {{用户操作}}
    Then {{异常反馈}}
```

### 9.2 组件测试骨架

```tsx
// {{Component}}.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { {{Component}} } from './{{Component}}';

describe('{{Component}}', () => {
  // 承接 AC-M{{MODULE_INDEX}}-001
  it('正常渲染', () => {
    render(<{{Component}} {...props} />);
    expect(screen.getByText('{{文案}}')).toBeInTheDocument();
  });

  // 承接 AC-M{{MODULE_INDEX}}-002
  it('点击触发回调', async () => {
    const onXxx = vi.fn();
    render(<{{Component}} onXxx={onXxx} />);
    await userEvent.click(screen.getByRole('button', { name: '{{按钮}}' }));
    expect(onXxx).toHaveBeenCalled();
  });
});
```

### 9.3 hooks 测试骨架

```tsx
// {{useXxx}}.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { {{api}} } from '@/api/{{module}}';
import { {{useXxx}} } from './{{useXxx}}';

vi.mock('@/api/{{module}}');

describe('{{useXxx}}', () => {
  it('获取成功写入数据', async () => {
    vi.mocked({{api}}.getXxx).mockResolvedValue({/* mock 数据 */} as never);
    const { result } = renderHook(() => {{useXxx}}());
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.data).toEqual(/* 预期 */);
  });

  it('接口失败置 error', async () => {
    vi.mocked({{api}}.getXxx).mockRejectedValue(new Error('网络异常'));
    const { result } = renderHook(() => {{useXxx}}());
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.error).not.toBeNull();
  });
});
```

### 9.4 覆盖矩阵

| 用例编号 | 对应 AC | 类型 | 测试对象 | 场景 |
|---------|---------|------|---------|------|
| TC-M{{MODULE_INDEX}}-001 | AC-M{{MODULE_INDEX}}-001 | 渲染 | {{组件}} | {{正常渲染}} |
| TC-M{{MODULE_INDEX}}-002 | AC-M{{MODULE_INDEX}}-002 | 交互 | {{组件}} | {{用户操作}} |
| TC-M{{MODULE_INDEX}}-003 | AC-M{{MODULE_INDEX}}-003 | 数据流 | {{hook}} | {{数据获取成功}} |
| TC-M{{MODULE_INDEX}}-004 | AC-M{{MODULE_INDEX}}-004 | 异常 | {{hook}} | {{接口失败}} |
| TC-M{{MODULE_INDEX}}-005 | AC-M{{MODULE_INDEX}}-005 | 边界 | {{组件}} | {{空态/极值}} |
