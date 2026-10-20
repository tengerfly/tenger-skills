# auto-test —— AI 代码验收测试与修复闭环

> 一句话：把「AI 说写好了」变成「机器证明能用」——L0 确定性门禁 → L1 契约冒烟 → L2 视觉 E2E（有设计稿内嵌 Fidelity-Review）→ L3 探索 → L4 专项（压测/安全/兼容/无障碍，信号触发）→ 带证据报告 + 修复任务卡 → fresh-agent 回归闭环。

| 项 | 说明 |
|---|---|
| 主链位置 | Workflow ⑭ 测试节点（接替 Testing——Testing 已于 2026-09-22 归档，旧请求重定向 auto-test，不设第二套备用流程） |
| 输入 | 可运行代码 + PRD（AC/状态机）+ 设计稿（视觉基准，缺失回退原型明示降级）+ 接口契约 |
| 产物 | `.spec/auto-test/`：用例库 / 分层报告 / 修复任务卡 / evidence（截图·console·network） |
| 双模式 | 引擎模式（auto-test CLI / MCP 可用时委托）与会话模式（agent 亲自执行）产物格式一致 |
| 上下游 | 承接 ⑬ 代码评审放行后的代码；可运行性问题转 Bug-Fix；缺陷修复回开发 skill |
| 项目资料 | `project/`：企业级 AI 自动化测试平台 v0.1（待评审）的项目计划 / 竞品研究 / 旧问题日志；只作研究参考，不参与执行，执行入口仍是本目录 [SKILL.md](SKILL.md) |

细则见 [SKILL.md](SKILL.md)；项目研究与历史资料见 [project/README.md](project/README.md)；术语与决策记录见 [CONTEXT.md](CONTEXT.md)。
