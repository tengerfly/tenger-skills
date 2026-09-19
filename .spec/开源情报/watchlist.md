# OSS-Radar Watchlist

> 本文件 = 配置 + 台账，每轮必读、每轮结束回写「台账」区。数据目录 = 本文件所在目录（`.spec/开源情报/`）。

## 采集目标

### A · skill 泳道（反哺本仓 skill）
- topics: claude-skills, agent-skills, claude-code, mcp, self-evolving
- 指定 repo:
  - <!-- 待首跑分诊后回填 -->
- 本轮定向主题（2026-09-18 用户点名）：self-evolving / self-improving agent、skill 进化、从运行反馈与用户偏好自动优化 prompt/skill、agent 记忆与行为习惯学习 —— 用于决策是否新做「skill 进化器」skill
- 反哺对象路径: D:\project\agent-project\tenger-skills（源仓库；skill 类反哺经 Skill-Optimizer 模式③执行）

### B · 项目泳道（反哺在研项目）
- 技术栈关键词: <!-- 暂无在研项目随行，下轮按需填 -->
- 指定 repo:
- 反哺对象路径: <!-- 暂无 -->

## 轮次偏好
- 单轮深读上限: 6
- 关注点加权: 反馈闭环机制（采集什么信号→怎么存储→怎么触发进化）、用户偏好/行为习惯建模、与现有 Skill-Optimizer 的边界划分、可嵌入 Agent 复用性

## 台账（每轮回写，REQUIRED）
- last_run: 2026-09-18（skill 进化器定向调研轮）
- 已扫 repo:
  - lsdefine/GenericAgent — 任务结晶成 skill + 显著点挖掘 SOP，判据可直接搬 — 2026-09-18
  - NousResearch/hermes-agent-self-evolution — skill 进化六步环+五护栏，骨架级参考 — 2026-09-18
  - gepa-ai/gepa — 读轨迹诊断的反思式优化引擎，方法论参考 — 2026-09-18
  - volcengine/OpenViking — 偏好一等公民+新建/合并/跳过三决策，存储形态参考 — 2026-09-18
  - thedotmack/claude-mem — 会话捕获→压缩→回注+按月追加感知日志 — 2026-09-18
  - EvoMap/evolver — 可审计进化（Event 留痕/策略档位/git 回滚） — 2026-09-18
- 待扫池:
  - mem0ai/mem0 — 65.6K★ 记忆层基础设施，偏 infra
  - memodb-io/Acontext — 「Agent Skills as a Memory Layer」概念对口，值得下轮深读
  - EverMind-AI/EverOS — markdown 原生便携记忆层，self-evolving across workflows
  - zhayujie/CowAgent — 自进化+记忆+知识的完整 agent 产品（原 chatgpt-on-wechat）
  - campfirein/byterover-cli — 编码 agent 便携记忆层
  - zilliztech/memsearch — Claude Code/Codex 统一持久记忆
  - aiwaves-cn/agents — 数据中心自进化 agent 框架（学术，2024 停更）
  - metauto-ai/GPTSwarm — RL/提示双优化自改进 agent
  - microsoft/PromptWizard — 任务感知 agent 驱动 prompt 优化
