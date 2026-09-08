# 代码审查方法学（Review Methods）

> 用途：审查顺序、评论规范、AI 边界的元方法论参考。

---

## 一、审查优先级（先架构后风格）

Design（抽象层级/模式一致）→ Correctness（边界/错误/并发）→ Security → Readability → Testing。

- 前两项是 P0 级关注点，风格/命名是 P2，勿倒置。

## 二、该自动化的别人工看

- 格式/import/类型 → prettier/black/gofmt/eslint/semgrep 自动化；人只看设计与逻辑，防 nitpick 战争。

## 三、轻量评审规范

- PR 100–400 行；异步 30–90min；跨组 reviewer；下游消费者优先；超出请求拆分（Stacked PR）。

## 四、评论前缀约定

- `nit`（小瑕疵）/ `suggestion`（建议）/ `question`（提问）/ `issue`（阻塞）/ `praise`（认可）。

## 五、反馈文化（对事不对人）

- 用「这块代码」而非「你」；解释 why；给具体建议；提问代替命令；认可优点。

## 六、反模式（不要做）

- 橡皮图章（LGTM）/ 吹毛求疵战 / 守门员依赖 / 巨型 PR / 队列腐烂 / 自我 ego 评审。

## 七、审查速度 SLA（参考）

- 首响 <4 业务小时；总时长 <1 天；PR <400 行；轮次 ≤2。

## 八、AI 审查边界（⛔ 红线，防过度自信）

- AI 对 **style / API 一致性 / 错误处理** 有用；**不指望架构性建议**；文件过多时 AI 质量下降。
- 结论须基于代码与文档（本 Skill 铁律「零幻觉」），不确定标「成因未明」，禁臆造。

## 九、CI 自动化检查

- GitHub Actions：lint + type-check + test + coverage（<80 拦截），与静态验证规程互补。

> 出处：jaess105/code-review-checklist、kbase/project_guides、Google Code Review。
