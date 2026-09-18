# OSS-Radar（开源情报雷达）

GitHub 开源情报采集 → 提炼 → 反哺：定时或按需扫描优秀的开源 skill 与同域工程项目，提炼优秀实践点，产出情报报告与反哺任务清单，反哺本仓 skill（经 Skill-Optimizer 落地）与在研项目。**链外 skill**，支持无人值守定时巡逻与增量采集。

## 文件结构

- `SKILL.md` — 主流程：双泳道（skill/项目）× 双模式（交互/无人值守）× 五步（装载→发现→采集→提炼→反哺→台账）+ 铁律
- `references/github-api-playbook.md` — GitHub API 通道/限流/查询语法/增量技巧（①② 执行时加载）
- `assets/watchlist-template.md` — watchlist 初始化模板（配置 + 台账）
- `assets/report-template.md` — 轮次报告结构 + 发现/任务条目格式
- `CONTEXT.md` — 决策日志

## 数据目录（运行时产物，在被运行的工作区）

`.spec/开源情报/`：`watchlist.md`（配置+台账）、`YYYY-MM-DD-<主题>.md`（轮次报告）、`情报库.md`（累积）、`任务清单.md`（反哺任务单一事实源）

## 与其他 skill 的关系

- `Skill-Optimizer`：反哺执行方——本 skill 只出任务清单，skill 类改动经用户确认后由其模式③执行
- `Competitive-Analysis`：边界——产品/商业层竞品归它，本 skill 管工程实现层与 skill 层
- Workflow 主链：不参与 14 节点链；产出可作主链各 skill 的外部参考输入

## 接入定时自动化

用自动化定时任务创建（建议 1~2 周/轮），prompt 示例：

> 运行 OSS-Radar skill：按 `<工作区>/.spec/开源情报/watchlist.md` 增量采集，产出本轮报告并更新台账；无人值守模式，不等确认。
