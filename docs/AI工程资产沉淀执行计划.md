# AI 工程资产沉淀执行计划

> 版本：v1.0（计划稿，未执行）
>
> 日期：2026-09-17
>
> 依据文档：《AI工程资产沉淀与执行实施方案-登录案例.md》
>
> 性质声明：本文只输出具体执行计划，不做任何修改。所有任务拍板后按里程碑独立执行、独立提交。

---

## 1. 计划目标

把「AI 先检索资产，再依据契约组合、适配、实现、验证并回写证据」落成可运行的工程流程，核心成果：

1. 建成 `asset-library/` 资产库（五类资产 + 三类运行记录 + 业务流程资产），与 Skill 解耦；
2. 以**登录**为第一个示范领域，完成最小资产集并打通「有资产走资产」全链路；
3. 以**前端上传**为第二个示范领域，验证跨组件库 Adapter 拆分；
4. 建立「没资产定规范」的规格化开发流程（资产缺失状态机 + 十二步 + 规格编译门）；
5. 建立资产长期维护机制（变更提案、晋级、迁移、弃用、月度指标）。

两条总规则贯穿全程：**有资产走资产；没资产定规范。**

## 2. 现状基线（2026-09-17 已核实）

| 项 | 现状 |
|---|---|
| asset-library/ | 不存在，需从零建立 |
| 现有可迁移内容 | `shared/`（公共规则+templates）、`bug-patterns/`（可作 Failure Case / Anti-Pattern 素材）、各 Skill 的 references/case-library 与 assets/（按三阶段渐进迁移，不一次搬空） |
| Skill 侧接口 | PRD/PRD-Design/PRD-Review、前后端 Tech-Design、前后端 Dev、DEV/Tech-Review/Code-Review、Testing、Bug-Fix、Workflow 共 13 个 Skill 存在集成点 |
| 治理角色 | 单人维护为主，需按「一人可兼多角色、高风险资产不得单人自批」执行 |

## 3. 里程碑总览（90 天 + 两条并行线）

```text
M0  第 1~7 天    定规则：asset-library 骨架 + schema + 规范 + 模板（不改全库）
M1  第 8~21 天   登录最小资产集（13 个资产）
M2  第 22~35 天  打通一个 NestJS 项目全链路（项目 A：手机号登录）
M3  第 36~50 天  变体验证（项目 B：账号密码 + 微信登录）
M4  第 51~65 天  Spring 换栈（项目 C：验证语言解耦）
M5  第 66~75 天  自动化校验（7 项脚本）
M6  第 76~90 天  接入现有 Skill 和 Workflow（五个资产门禁）

并行线 P-A  资产缺失规格化流程：规则随 M0 落地，M2 起在真实任务中试用
并行线 P-B  前端上传资产：M4 完成后启动，作第二示范领域
运营线 P-C  变更提案 / 晋级 / 月度指标：M2 起记账，长期运行
```

每个里程碑完成即停下验收，不通过不进入下一里程碑；与《Skill体系优化计划》的 Phase 5（资产分层）共用同一套 asset-library，不重复建设。

---

## 4. M0（第 1~7 天）：定规则，不改全库

**目标**：资产库的宪法先行，只选登录作示范领域。

| 任务 | 具体动作 | 产出物 |
|---|---|---|
| T0.1 | 建立 asset-library 目录骨架：README、registry.yaml、schemas/、methods/、patterns/、composites/、adapters/、templates/、processes/、cases/（production/failure/experiment）、anti-patterns/、evidence/、migrations/ | asset-library/ 完整骨架 |
| T0.2 | 编写 8 个 schema：asset / method / pattern / composite / adapter / template / case / evidence .schema.yaml | schemas/ |
| T0.3 | 定 ID 规范：`<kind>.<domain>.<subdomain>.<name>`，全小写字母数字点连字符，版本不入 ID；明确不推荐命名（login-v1、java-login 等反例） | README 规范节 |
| T0.4 | 定版本规范：MAJOR.MINOR.PATCH；Pattern 与 Adapter 分别版本化，项目锁定组合（pattern@1.x + adapter@2.x） | README 规范节 |
| T0.5 | 定生命周期三正交字段：status（draft/active/deprecated/retired）、maturity（experimental/validated/stable）、evidence_level（L0~L4）；另加置信度 + assumptions + unknowns 约定 | README 规范节 |
| T0.6 | 定单资产最小目录：asset.yaml（机器可读索引）+ 正文 MD + contract.yaml（requires/provides/side_effects/conflicts/commonly_composed_with/ordering）+ verification.yaml + examples/ + evidence-links.yaml + CHANGELOG.md | 模板 |
| T0.7 | 定项目侧九件套模板：asset-needs / asset-selection / composition / implementation-plan / asset-usage / verification-report / evidence / case-draft / pipeline-state .yaml|md | templates/ |
| T0.8 | 定迁移策略（三阶段渐进，一事一源，禁止两份独立正文）：references/case-library→暂留、assets→补 asset.yaml、shared/→保持单一来源、bug-patterns/→补结构化 metadata 关联修复模式、issue/→只作入口不当作稳定资产 | 迁移映射表 |

**验收门禁**：schema 与模板齐备；ID/版本/生命周期规范可执行；未动任何现有 Skill 正文。

---

## 5. M1（第 8~21 天）：登录最小资产集

**目标**：13 个资产覆盖真实需求和关键边界，不建几十种登录 Pattern。

| # | 资产 ID | kind |
|---|---|---|
| 1 | method.security.authentication | Method（问题分析、决策树、stop_conditions） |
| 2 | pattern.authentication.identity-model | Pattern |
| 3 | pattern.authentication.password-login | Pattern |
| 4 | pattern.authentication.phone-otp-login | Pattern |
| 5 | pattern.authentication.oauth-login | Pattern |
| 6 | pattern.authentication.account-linking | Pattern |
| 7 | pattern.authentication.account-provisioning | Pattern |
| 8 | pattern.authentication.session-management | Pattern（jwt-stateless / redis-session 等为变体） |
| 9 | pattern.security.audit-logging | Pattern |
| 10 | adapter.backend.nestjs.authentication | Adapter |
| 11 | adapter.backend.spring-security.authentication | Adapter |
| 12 | adapter.provider.wechat-oauth | Adapter |
| 13 | composite.authentication.web-login | Composite |

**每个 Pattern 的编写要求**（以 phone-otp-login 为基准样例，先写它，其余照模板复制结构）：

- 正文 14 节：Problem / Context / When to use / When not to use / Inputs / Provides / Invariants / Security requirements / Trade-offs / Composition contract / Verification / Anti-patterns / Evidence / Change history；
- 适用条件必须可判断（不写「适合大多数项目」），必须写不适用条件；
- contract 六要素齐备，ordering 声明 before/after；
- verification 列必须验证的用例（如 OTP：有效/无效/过期/重复使用/超次/供应商超时/重复提交）与安全不变量（单次使用、过期、限次、不记原文、防枚举、限流）。

**Method 卡要求**：Goal / Required questions / Decision tree / Output contract / Common failure modes / References；stop_conditions 覆盖账号绑定策略未知、token 生命周期未知、安全边界未知。

**Adapter 卡要求**：语言框架版本范围、依赖、目录边界、DTO/异常/错误码映射、事务幂等并发、测试命令、旧项目集成方式、不覆盖的业务决策（不写死「是否允许微信登录」）。

**Composite 卡要求**：必选/可选组件、顺序、输入输出连接、互斥组件、整体验收标准（web-login = identity-model + 凭证验证 + 建档/绑定 + session + audit 的组合骨架）。

**验收门禁**：13 个资产全部通过 M5 的 schema 校验（提前人工执行检查清单）；每个 Pattern 有 requires/provides/conflicts/ordering；全部为 experimental 及以下，无 Stable 虚标。

---

## 6. M2（第 22~35 天）：打通一个 NestJS 项目（项目 A：手机号登录）

**目标**：跑通「PRD → 资产需求 → 技术方案 → 资产选择 → 组合 → 开发 → 评审 → 测试 → Case/Evidence」全链路。

按九步协议执行，每步有明确产物：

| 步 | 动作 | 产物 |
|---|---|---|
| 1 | 创建任务上下文 | .spec/phone-login/asset-usage.yaml |
| 2 | 生成标准标签（domain/capabilities/constraints/runtime） | 同上 tags 节 |
| 3 | 检索候选资产：元数据过滤 → requires/conflicts 过滤 → 匹配 Adapter → 按证据等级排序 → 读正文 | candidates/selected/rejected/unresolved 四类清单 |
| 4 | 建立组合图（identity-model → phone-otp → auto-provision → session(jwt) → audit） | composition.yaml |
| 5 | 锁定版本与 Adapter | asset-selection.yaml（含 project_decisions：短信供应商、OTP 有效期、错误次数、默认角色、JWT/Redis 等项目参数） |
| 6 | 先生成实现计划（改哪些文件、各文件对应哪个资产、哪些是项目特有、哪些待人工确认、如何测试） | implementation-plan.md |
| 7 | 实现与验证（不得改资产库正文迁就项目；差异进项目配置；通用缺口记 Candidate；构建/单测/集成/E2E/安全/回归） | 代码 + 测试 |
| 8 | 回写使用证据（实际版本、提交、命令、结果、失败、局限） | evidence.yaml |
| 9 | 沉淀判断（本次产出 Pattern Candidate：phone-otp-login；Adapter Candidate：nestjs-authentication；Case：project-a.phone-login；Evidence 四件） | case-draft.md + 资产库回写 |

**验收门禁**（方案 §17 原文）：能输出资产选择；能锁定版本；能生成组合图；能执行测试；能回写 Case 和 Evidence。本地跑通但无有效边界与证据的，不得写 Stable。

**并行执行 P-A 试点**：M2 期间选择一个无资产可命中的真实小需求，完整走一遍「资产缺失规格化」路径（见 §10），验证规则可执行。

---

## 7. M3（第 36~50 天）：变体验证（项目 B：账号密码 + 微信登录）

**目标**：验证拆分正确性——不复制项目 A 资产，而是原子组合。

| 任务 | 具体动作 |
|---|---|
| T3.1 | 反复制检查：确认未把项目 A 手机号资产复制改造；未出现 login-v2 式整体副本 |
| T3.2 | 组合选择：identity-model + password-login + oauth-login + account-linking + session-management + nestjs Adapter + wechat-oauth Adapter；rejected（如 magic-link：无邮箱链路）；unresolved（微信首登是否自动建档、手机号冲突是否人工绑定、是否踢旧设备）必须显式列出待决策 |
| T3.3 | 顺序校验：身份模型 → 双通道凭证验证 → 外部身份映射 → 查找/创建/绑定确认 → 内部会话签发 → 审计风控；对照常见错误顺序清单（先发 Session 后验身份、Provider Token 当内部 Session、先绑定后确认归属等）逐条排查 |
| T3.4 | 新增沉淀判断：account-linking 是否需要从 Candidate 补齐晋级；错误做法是否产生新 Anti-Pattern |

**验收门禁**：项目 B 的 asset-selection 中 selected/rejected/unresolved 三类齐备；组合图与 M1 的 contract 一致；无复制分叉。

---

## 8. M4（第 51~65 天）：Spring 换栈（项目 C）

**目标**：同一组业务 Pattern，仅替换 Adapter，验证语言解耦。

| 任务 | 具体动作 |
|---|---|
| T4.1 | 复用清单核对：method + 7 个 Pattern 原样复用，零改动（如有改动记录为 Pattern 缺陷提案） |
| T4.2 | 替换：adapter.backend.nestjs.authentication → adapter.backend.spring-security.authentication；按需新增 adapter.provider.wechat-spring-sdk |
| T4.3 | 边界核对：语言无关内容（密码不明文、第三方身份不当内部 ID、state/nonce 校验、内部会话自签发、绑定显式策略、失败限流审计）在 Spring 实现中逐条成立；NestJS Guard / Spring Filter / DTO / ORM 差异全部落在 Adapter 层 |

**验收门禁**：业务 Pattern 零改动复用；Spring Adapter 通过 verification.yaml 全部用例；形成「不是 login-v1/v2/v3，而是原子能力 + 组合 + 适配器 + 证据」的对照结论。

---

## 9. M5（第 66~75 天）：自动化校验

**目标**：机械检查脚本化，脚本只做确定性检查，不替代专家判断。

| # | 校验项 | 检查内容 |
|---|---|---|
| 1 | asset-id 校验 | 命名格式、唯一性、kind 前缀一致 |
| 2 | asset.yaml schema 校验 | 必填字段、枚举值（status/maturity/evidence_level） |
| 3 | 引用存在性校验 | contract/evidence 中引用的资产 ID、文件路径存在 |
| 4 | 版本格式校验 | semver 合法、CHANGELOG 与版本同步 |
| 5 | requires/provides 兼容性校验 | 组合图每个下游 requires 能从前置 provides 获得 |
| 6 | 循环依赖检测 | 资产依赖图无环 |
| 7 | 生成物扫描 | asset-library 与各 Skill assets/ 中无 node_modules/dist/coverage 等 |

**验收门禁**：7 项脚本对现有 13+ 资产全量跑通；校验结果可输出为报告文件。

---

## 10. M6（第 76~90 天）：接入现有 Skill 和 Workflow

**目标**：资产流程成为 Skill 链路的内置环节。优先接入 5 个：Backend-Tech-Design、Backend-Dev、Code-Review、Testing、Workflow；再扩展前端、产品、设计和 Bug-Fix。

| Skill | 接入改动（计划） |
|---|---|
| PRD-Design / PRD-Review | 产物增加 .spec/\<feature\>/asset-needs.yaml（capabilities/constraints/existing-system/non-functional/legacy-boundaries）；评审检查是否错误复用资产 |
| Backend-Tech-Design / Frontend-Tech-Design | 增加资产检索与选择环节，输出 asset-decision.yaml、asset-selection.yaml、composition.yaml、implementation-profile.yaml；Tech-Review 检查组合契约与迁移方案 |
| Backend-Dev / Frontend-Dev | 固定九条输出顺序（使用资产及版本 → 契约不变量 → 项目差异 → 禁改边界 → 实现计划 → 代码 → 测试结果 → 资产缺口 → 是否提交资产变更）；偏差记录 deviation.yaml；完成回写 usage_record（无数据写 not_measured 不留空） |
| Tech-Review / Code-Review | 新增检查项：组合契约、Pattern 不变量、是否绕过统一契约、是否复制资产、是否静默发明关键规则 |
| Testing | 按 Pattern 的 verification.required 生成测试矩阵；按 Adapter 命令执行构建/单测/集成/E2E；跨 Adapter 跑同一组场景（比较行为与错误语义，不比 DOM 文本）；失败模式回写 failure case / anti-patterns |
| Bug-Fix | 增加根因分层判断：项目参数→改配置/Case；Adapter 缺陷→修 Adapter 评估影响面；Pattern 契约→走变更提案；业务规格→更新 Process Asset；均不直接在项目里打补丁了事 |
| Workflow | 增加五个资产门禁：检索门禁（完成候选分析）、选择门禁（selected/rejected/unresolved 记录）、实现门禁（实际使用版本）、验证门禁（可定位证据）、沉淀门禁（Case/Pattern/Adapter 判断完成）；引入双状态机——项目任务态（REQUIREMENT→…→USAGE_RECORDED）与资产变更态（DRAFT→…→RETIRED）分开推进 |

**验收门禁**：五个试点 Skill 的 SKILL.md 增补完成并同步安装副本；一次真实任务能被五道门禁完整拦截校验。

---

## 11. 并行线 P-A：资产缺失规格化流程（规则随 M0 落地）

**落地物（M0 期间写入规范）**：

1. 资产缺失状态机：ASSET_MISSING → DISCOVERY_REQUIRED → SPEC_DRAFT → SPEC_REVIEW →（NEEDS_CLARIFICATION 回退 / APPROVED）→ IMPLEMENTATION_PLANNED → IMPLEMENTED → VERIFIED → CASE_RECORDED（分 PROJECT_SPECIFIC / PATTERN_CANDIDATE / COMPOSITE_CANDIDATE / ADAPTER_CANDIDATE 四出口）；每状态列「可做 / 禁做 / 必备产物」；
2. 十二步流程与产物模板：asset-gap.yaml（missing_reason 必须说明不匹配原因）→ 术语表 → 领域模型 → 状态机（无则记 not_applicable+理由）→ 规则与不变量 → 数据/接口/事务契约 → 验收场景（每条强制规则一正一反）→ 规格编译门 → 实现计划 → 固定目录边界 → 按规格验证 → 沉淀类型判定；
3. 规格编译门 10 项检查（术语唯一、实体有界、状态可达、转换有命令角色条件、规则无冲突、权限覆盖读写审批导出、数据关系删除并发幂等已定义、强制规则有场景、未确认项标 OPEN_QUESTION/ASSUMPTION、版本评审人决策源已记录）；未通过停留在 SPEC_REVIEW，不得进 Dev；
4. 业务流程资产 processes/ 目录规范（process/domain-model/state-machine/rules/permissions/data-contract/api-contract/acceptance-scenarios/implementation-profile）；
5. 跨 AI 一致性四层约定：源码文本不保证相同（允许），结构边界、业务行为、维护入口必须一致；一致性报告模板；确需源码可重复的部分走固定 Generator + 锁工具链 + 输入/输出 Hash；
6. 维护 SPEC_DRIFT 标记：代码与规格不一致时在 Workflow 中挂起直到回写。

**试用安排**：M2 起任一「检索不到资产」的任务必须显式进入该状态机，禁止悄悄绕过；M2 结束时输出一次试用复盘。

## 12. 并行线 P-B：前端上传资产（第二示范领域，M4 后启动）

**目标**：验证「同一业务契约 + 不同组件库 Adapter」的前端拆分。

| 任务 | 具体动作 |
|---|---|
| TB.1 | 先定统一业务契约（与 UI 库无关）：UploadStatus 七态、UploadFileInput / UploadPolicy / UploadedFile / UploadPort 接口 |
| TB.2 | 建资产：method.frontend.upload-validation + pattern.frontend.file-upload-policy + pattern.frontend.upload-state-machine（IDLE→VALIDATING→SIGNING→UPLOADING→SUCCESS/ERROR/CANCELLED/RETRYING/REMOVING）+ adapter.frontend.antd-upload + adapter.frontend.element-plus-upload + adapter.storage.object-storage + composite.frontend.attachment-upload（+ avatar-upload 视需求） |
| TB.3 | 组合门禁：UI 组件不得绕过 Policy、不得拼接签名、不得自定义错误码；重试逻辑只允许一处 |
| TB.4 | 跨 Adapter 同场景测试（约 14 个场景：正常单/多文件、类型/大小/数量超限、重复文件、签名失败、中断、取消、自动/手动重试、成功但确认失败、删远端失败、刷新回显、事件顺序变化）在两个 UI Adapter 上跑通 |
| TB.5 | 沉淀核对：最终形成 2 Pattern + 1 Method + 3 Adapter + 1~2 Composite + 2 Case + 1 Evidence，**不得出现 crm-element-plus-upload-full-copy 式整体副本** |

## 13. 运营线 P-C：长期维护机制（M2 起运行）

| 机制 | 具体安排 |
|---|---|
| 变更提案 | 一切回写走 Asset Change Proposal（id/type/target/problem/proposed_change/version_plan/validation/approvals）；Stable 资产禁止静默覆盖 |
| 晋级规则 | Candidate（需人工确认）→ Experimental（完整契约+负责人+验证计划）→ Validated（真实项目证据+失败路径已录+无未闭 P0/P1）→ Stable（≥2 个不同场景验证+回归+观察期无重复严重缺陷）；高风险领域（认证/支付/权限）提高门槛 |
| 角色分工 | 资产提出人 / 业务 Owner / 资产 Owner / Adapter Owner / 测试 Owner / 安全合规 Owner / Workflow Owner / 项目负责人；一人可兼多岗，高风险资产不得单人设计+批准+发布 |
| 权限三类 | 使用 / 提案 / 发布（仅 Owner 与指定评审人）；禁止删除在用资产、改版本不记 CHANGELOG、只改代码不改契约测试 |
| 缺陷三路径 | 项目局部修复（记 Case 不动库）/ 向后兼容修复（Patch 版本+关联项目回归）/ 契约变更（Minor/Major+迁移说明 migrations/1.x-to-2.x.md）；变更必做七问影响分析 |
| 弃用流程 | Stable → Deprecated（检索可见、标 replacement 与 sunset_date）→ Freeze → 迁移存量 → Retired → Archive；不直接删除 |
| 月度指标 | 使用（引用次数/命中率/采用率/节省时长）、质量（缺陷率/事故数/回滚数/契约测试通过率/未验证资产误用数）、维护（评审时长/修复时长/迁移完成率/长期未维护数/项目本地分叉数）三组；出现「同一能力大量相似资产、大量复制不引用」即执行整顿 |
| 缓存友好规范 | 稳定内容前置、动态后置；资产用 ID+版本+Hash 引用；固定序列化与摘要；项目差异不入稳定资产正文；缓存绑定版本与隔离范围，不缓存真实用户数据/密钥/租户数据 |

## 14. 验收清单

**第一阶段验收（对应方案 §18，M6 完成时逐项核验）**：

- [ ] 统一资产 ID、类型、版本、状态和 owner；
- [ ] Method / Pattern / Adapter / Template / Case / Evidence / Anti-Pattern 边界清晰；
- [ ] 登录领域最小资产集完成（13 项）；
- [ ] 手机号、账号密码、微信登录以原子 Pattern 组合；
- [ ] Spring 与 NestJS 复用同一组业务 Pattern；
- [ ] 资产选择有 selected / rejected / unresolved；
- [ ] 组合含 requires / provides / conflicts / ordering；
- [ ] 每次项目使用有版本和证据；
- [ ] 能判断新建 Pattern / 更新 Pattern / 增加 Adapter / 仅记 Case；
- [ ] 未验证资产未被标 Stable；
- [ ] 至少一个成功案例和一个失败/反模式案例；
- [ ] 旧项目可通过 Adapter 渐进接入。

**补充验收（对应方案 §22，覆盖资产缺失与前端线）**：

- [ ] 检索不到资产时进入 ASSET_MISSING，不直接生成代码；
- [ ] 业务事实、实现方式、项目配置分层记录；
- [ ] 唯一规格事实源，四端引用同一版本；
- [ ] 未确认规则标 OPEN_QUESTION / ASSUMPTION；
- [ ] 规格通过结构/状态机/规则/权限/数据/行为检查；
- [ ] 先实现计划后编码；
- [ ] 不同 AI 结果过规格/结构/契约/行为/架构五层一致性检查；
- [ ] 需源码一致处用固定生成器与锁定工具链；
- [ ] 资产缺失首次实现至少沉淀 Case/Evidence；
- [ ] 多项目验证后才晋级 Pattern/Composite/Adapter；
- [ ] 前端上传按契约/状态机/UI Adapter/存储 Adapter 拆分；
- [ ] 不同组件库跑相同场景、比较行为不比 DOM；
- [ ] 业务规则变化先改规格再改代码和测试。

## 15. 风险与执行注意事项

| 风险 | 应对 |
|---|---|
| 试点项目不可得（M2~M4 需要真实项目） | 优先用真实在办项目充当项目 A/B/C；确无则用最小脚手架项目，但 Evidence 等级如实记 L2（本地实验），不虚标 L3 |
| 资产库与 Skill references 双源漂移 | 严格执行三阶段迁移 + 一事一源；迁移期间只允许索引或兼容文件 |
| 单人治理形同虚设 | 高风险资产（认证/权限/支付）至少引入一次外部评审（第二 AI 独立评审或人工复审）再晋级 |
| 规则过多导致执行成本高 | M0~M1 只落登录域；五门禁在 M6 才接入 Workflow，此前靠人工检查清单过渡 |
| 双副本同步遗漏 | Skill 侧改动（M6）每次提交后同步 `.zcode\skills` 安装副本，列入 M6 验收项 |
| 缓存收益依赖平台策略 | 缓存指标只作观测不作承诺；先落「稳定前缀组装顺序」等零成本规范 |

## 16. 执行顺序原则（收尾）

```text
先规则后资产：M0 的 schema 和规范未定稿，不开始写 13 个资产。
先单点后组合：Pattern 未通过 schema 校验，不建 Composite。
先后端后前端：登录主线（M1~M6）完成后再启动上传线（P-B）。
先试点后推广：五门禁先接 5 个后端链 Skill，跑通一轮再扩产品/设计/前端/Bug-Fix。
先证据后晋级：每个里程碑的 Case/Evidence 是下一个里程碑的唯一晋级依据。
```
