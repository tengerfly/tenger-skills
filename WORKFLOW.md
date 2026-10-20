# WORKFLOW — 一条主链

> 所有任务走同一条主链；任务大小只决定「跑几步、评审多厚、要不要签收」。
> 交付的定义不是「代码写完」，是验收 ACCEPT。

## 主链

```text
需求 → 方案 → 开发 → 测试 → 评审 → 验收 → 交付
```

| 步 | 调度 Skill | 产物（落在项目 `.spec/tasks/<日期>-<slug>/`） |
|---|---|---|
| 需求 | requirements | `task.md`（目标/范围/AC） |
| 方案 | tech-design | `design.md`（选型/接口/数据/回滚） |
| 开发 | backend-dev / frontend-dev | 代码 + 自测证据 |
| 测试 | auto-test | `test-report.md`（L0-L2 + 可复现声明） |
| 评审 | review | `review-report.md`（独立评审 + 三值结论） |
| 验收 | acceptance | `acceptance-report.md` + 证据包 + 签收 |
| 交付 | workflow 收口 | 交付结论、遗留风险、loop-log 一行 |

- 轻量可跳过方案与测试文档，但不跳验收。
- 每步交接一句话状态卡：当前步/Skill、产物路径、证据、待决、下一步。
- 入口与路由见 [skills/workflow/SKILL.md](skills/workflow/SKILL.md)。

## 三档选择

| 档位 | 适用 | 最少做什么 |
|---|---|---|
| 轻量 | 文案/样式/单文件小改 | 自检 + 1 次快速评审 |
| 标准 | 一般功能开发 | 独立评审 + 测试证据 + 验收清单 |
| 完整 | 生产/发布/迁移/权限/资金 | 标准全部 + owner 签收 + 回滚验证 |

判不了按标准。完整判据见 [shared/review-contract.md](shared/review-contract.md)，DoD 与三值结论见 [shared/acceptance-contract.md](shared/acceptance-contract.md)。

## 五类硬停

只有这五类停下来问用户，其余裁决 + 记账 + 继续：

1. 不可逆或破坏性：删除、覆盖已批准基线、数据迁移、重置。
2. 安全敏感：认证授权、资金计费、敏感数据、外部凭据。
3. 本仓之外的副作用：push、发布部署、改外部仓、付费调用。
4. 关键产品决策：范围、定位、目标用户、MVP、验收口径的实质变更。
5. 无路可走：缺关键输入且无法推断。

## 任务工作区

- 真实业务项目内 `.spec/tasks/<YYYY-MM-DD>-<slug>/`；本规划仓不建 `.spec/`。
- `task.md` 必建（目标/范围/AC/状态）；其余按档位按需。
- 一套产物只存一份，评审/验收报告不回写到多个位置。

## 验收后才算完

- acceptance 结论 `ACCEPT` = 交付；`FIX` 修后复验；`REJECT` 阻塞，不得宣布完成。
- 交付时必须给：验收报告、证据路径、遗留风险与豁免、回滚方式。
- 每任务一行记 [loop-log.md](loop-log.md)（11 列）；问题进 `issue/`，可复用的缺陷模式进 `bug-patterns/`。