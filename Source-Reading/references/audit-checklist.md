# 深读命题清单（步骤③ REQUIRED 加载）

> **三段式成文法**（2026-09-18 用户定法）：④ **大纲先行**——深读后先产出功能点大纲（每条带锚点 + 九命题结论行），多章文档呈用户确认；⑤ **按纲填充**——大纲一条 = 文档一个关键点，边写边勾，新发现先补大纲再写正文；⑥ **成文复核**——交付前对纲逐条核对落点 + 九命题复核 + 锚点抽验。三段式 + 九命题 = 遗漏的双保险。

> 来源：2026-09-18 六仓 agent harness 审计（deepseek-harness / pi / opencode / hermes-agent / openclaw / OpenHands SDK）的实际漏项复盘。深读收尾时九个命题逐仓过一遍，**每个命题三选一**：
> A. 有机制 → 产出关键点（锚点 + 干什么 + 为什么）
> B. 确认不存在 → 写一行结论 + 检索证据（搜了什么关键词、哪些目录，为空）
> C. 归入「本次未覆盖」显式清单（只允许用户点名的聚焦范围使用）
>
> 铁律延伸：**「确认不存在」也是结论，必须有检索证据**——口嗨「不存在」和口嗨「有」同样害人。

## 九命题

| # | 命题 | 追什么 |
|---|---|---|
| 1 | 主循环 | 入口函数、循环形态、终止条件、中断/取消 |
| 2 | 工具系统 | 定义/注册/执行、权限审批、死循环防护 |
| 3 | **工具规模治理** | 工具太多怎么加载：搜索/目录/分页/延迟加载/塌缩（如 dsh PTC 只发 run_code、openclaw tool-search 目录压缩、按 agent/权限过滤） |
| 4 | 上下文处理流程 | system prompt 拼装、注入器、压缩/裁剪（触发/策略/恢复） |
| 5 | LLM 接入 | 适配器抽象、流式规范化、多协议 |
| 6 | **LLM 错误降级** | 重试（策略/退避/哪些码重试）、失败转移（fallback 模型链）、错误分类器、凭据刷新、配额兜底 |
| 7 | 会话持久化 | 存储/格式/恢复/迁移/锁 |
| 8 | **记忆机制** | 跨会话记忆：检索索引（FTS/向量）、记忆文件（MEMORY.md 类）、会话引用/搜索；与「会话历史」区分开 |
| 9 | **Multi-Agent** | 子代理 spawn/委托/fork、并行代理、MoA/评审团、agent 注册表、把外部 agent 当子代理 |

## 审计实操（每命题 ≤2 分钟）

1. `grep -riE "<命题关键词>" <src>/` 看命中面（如记忆：`memory|recall|remember|FTS|vector`；多代理：`subagent|sub_agent|spawn|delegate|swarm|MoA|fleet`）
2. 目录树里名字沾边的目录/包，读其 README 或主文件头注释（前 15 行通常就是定性句）
3. 命中 → 找主循环/核心服务的调用点（机制在哪被消费）；无命中 → 记录检索词与范围作「不存在」证据
4. 模块文档第一段 = 定性金句，直接引用进导读（注明锚点）

## 六仓实测参考答案（2026-09-18，供新仓导读时对照发现差异）

| 命题 | 有代表性的解法 |
|---|---|
| 工具规模治理 | dsh：PTC 模式塌缩成 run_code + schema 白名单投影；openclaw：tool-search 16 模块族（目录压缩+排序+code-mode）；pi/opencode/OpenHands：显式数组+权限过滤，无搜索 |
| LLM 错误降级 | dsh：重试=注册期数据+独立插件+事件先行；openclaw：预解析 fallback 模型候选链+attempt 重试预算；hermes：错误分类器（FailoverReason）+凭据池；OpenHands：FallbackStrategy（6 类异常触发换 LLM）+tenacity RetryMixin；opencode：Effect retry 组合子+免费额度升级提示；pi：错误即数据，上层 retryAssistantCall |
| 记忆 | OpenHands：两层 MEMORY.md 加载器（用户层+项目层，日志按需读）；hermes：SQLite FTS5 会话检索（CJK 双字分词）；openclaw：memory/ 目录+root-memory-files；pi：SessionSearchService 会话检索；dsh：session-reference 跨会话快照引用；opencode：无（已核实） |
| Multi-Agent | dsh：subagent 域 11 包（含把 claude-code/codex 当子代理）；OpenHands：subagent registry（用户/项目目录加载定义）+parallel_executor；openclaw：swarm+claws 多实例+CLI 后端外包；hermes：MoA 顾问团（/moa 回合，参考模型上下文收集）；opencode：subtask 任务队列；pi：无（已核实，单 agent 工具箱） |
