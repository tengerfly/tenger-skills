# issue/：问题池（v4 从 0 开始）

一张卡记一个真实问题，30 秒写完；用来反哺 Skill，不用来堆报告。

- 规则唯一事实源：[../shared/issue-loop.md](../shared/issue-loop.md)。
- 新池从 0 开始：旧 65 张卡冻结在 `archive/issue-v3/`（只读），不迁移、不复用。

## 怎么记

1. 复制 [000-template.md](000-template.md)，命名 `NNN-slug.md`（001 起，三位递增）。
2. 填 frontmatter 七个字段 + 正文四节：现象 / 证据 / 影响 / 建议改动。
3. 同现象先 `grep` 本目录查重；已存在就补证据，不新建。
4. 写完把卡号回填到任务产物与 [loop-log.md](../loop-log.md) 的「新增问题」列。

## 状态

`open → fixed → verified → closed`。已修复 ≠ 已验证；无法验证保持 `open`。

## 谁写、谁消费

- 写：任何 Skill 执行中发现的问题——评审、验收发现的问题优先入池；测试失败、修复复盘、用户纠正同样入池。
- 消费：每 2 周批改窗口（≤3 处、每处 ≤10 行）；改动回链卡号，下个真实任务记 `verifiedBy`，4 周未验证回滚。

## 与 bug-patterns/ 的分工

- 问题出在「Skill 怎么干活」→ 本池。
- 问题出在「写出来的代码有哪类坑」→ [../bug-patterns/README.md](../bug-patterns/README.md)（评审检出清单）。

## 目录

```text
issue/
├── README.md        # 本说明
├── 000-template.md  # 问题卡模板
└── NNN-slug.md      # 真实问题卡（当前 0 张）
```
