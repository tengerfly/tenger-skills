# chats/ —— 待挖掘的聊天记录

把希望 Skill-Optimizer 分析提取优化点的聊天记录文件放到这里：

- **支持多个子文件夹 + 多个文件**（按项目 / 会话自由组织）；
- 格式支持 `.md` / `.txt` / `.json` / `.html`；
- 放好后对 Skill-Optimizer 说「挖掘 chats/ 里的优化点」。

## 流程

1. Skill-Optimizer 按 `assets/signal-checklist.md` 扫描四类信号（负面 / 正面 / 返工 / 触发痕迹）；
2. 提取清单经你逐条确认（增删 / 改归属 / 改等级标签）；
3. 确认后落盘到 `issue/`。

> 挖掘完成的记录建议移走或删除，避免下次重复挖掘。

> 本目录是问题数据流的「原材料入口」，确认后的问题一律落 `issue/`；总流向见 `issue/README.md` §问题数据流总览。
