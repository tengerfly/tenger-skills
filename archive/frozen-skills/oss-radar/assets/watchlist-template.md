# OSS-Radar Watchlist

> 本文件 = 配置 + 台账，每轮必读、每轮结束回写「台账」区。数据目录 = 本文件所在目录（`.spec/开源情报/`）。

## 采集目标

### A · skill 泳道（反哺本仓 skill）
- topics: claude-skills, agent-skills, claude-code, mcp
- 指定 repo:
  - <!-- 例：anthropics/skills — 官方 skill 库，结构与触发描述参考 -->
- 反哺对象路径: skill 源仓库根（tenger-skills 仓——`bug-patterns/`、`issue/`、`evolution/` 同一根目录；skill 类反哺经 Skill-Optimizer 模式③执行。安装副本 / 其它机器运行时填该仓的实际本地路径或用户指定维护目录，不写死个人绝对路径）

### B · 项目泳道（反哺在研项目）
- 技术栈关键词: <!-- 按当前在研项目填，例：nestjs, vue3, monorepo, ai-agent -->
- 指定 repo:
- 反哺对象路径: <!-- 在研项目绝对路径 -->

## 轮次偏好
- 单轮深读上限: 6
- 关注点加权: <!-- 可选：测试基建 / 组件库 / 工程化 / 触发描述 …有则提炼时优先 -->

## 台账（每轮回写，REQUIRED）
- last_run: 未运行
- 已扫 repo:
  - <!-- <owner/repo> — 一句话结论 — <日期> -->
- 待扫池:
  - <!-- 分诊后未深读的候选，下轮优先 -->
