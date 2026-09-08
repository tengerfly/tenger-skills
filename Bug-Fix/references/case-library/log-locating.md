# 日志定位专项（Log Locating）

> 用途：分析日志、插桩时的专项方法。与 `log-channels-guide.md`（双通道日志识别）互补：通道是「认日志」，本文件是「怎么用日志定位」。

---

## 一、日志级别递进

- DEBUG → INFO → WARN → ERROR → FATAL，按严重度逐层切入，别一上来看全部。

## 二、结构化日志

- JSON 键值对比纯文本易解析；记录 requestId/userId/时间戳/参数。

## 三、时间线重建

- 按时间戳串起问题前后几分钟条目，因果链即事件顺序。

## 四、堆栈/异常追踪

- 不跳过 stack trace；读调用栈的 file/line/error code。

## 五、多源日志关联

- 跨 DB/网络/应用服务器日志，用事务 ID 串联（分布式系统必做）。

## 六、降噪与上下文

- 分析前先缩减噪声；单条 grep 命中必须读前后 ≥10 行上下文（防误判根因）。

## 七、日志聚合工具

- ELK Stack / Splunk / Graylog / Loki 集中收集 + 搜索 + 可视化。

## 八、取证纪律（法医规范）

- 分析前先复制日志副本（绝不原地操作）；保留原始现场；敏感数据脱敏。

## 九、Commit-Then-Instrument + 干净清理（⛔ 必抄）

> 源自 franzenzenhofer：LLM 手删 debug 日志易留悬挂括号/破坏缩进。解法：

1. 编写复现测试/脚本 → 先提交：`git commit -m "chore: add failing reproduction"`。
2. 添加 `[DEBUG-MODE]` 标签日志，让工作区变脏。
3. 分析日志（日志落文件再 grep，不灌 context）。
4. `git restore .` 一键删除所有插桩，工作区恢复干净。
5. 已提交的复现测试保留，代码干净。

**假设标签日志格式**：`[DEBUG-MODE][H1-stale-cache][getUserProfile] cache_key=user:123 hit=true age=3600s`（全局前缀 + 假设编号 + 函数名）。

**多语言插桩（全走 stderr，避免干扰正常输出）**：
| 语言 | 示例 |
|---|---|
| JS/TS | `console.error('[DEBUG-MODE]...')` |
| Python | `print('[DEBUG-MODE]...', file=sys.stderr)` |
| Go | `fmt.Fprintf(os.Stderr, "[DEBUG-MODE]...")` |

> 出处：franzenzenhofer/debug-mode-skill、oimiragieo/agent-studio debug-log-analysis。
