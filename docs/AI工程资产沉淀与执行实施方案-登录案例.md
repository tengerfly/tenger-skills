# AI 工程资产沉淀与执行实施方案

> 版本：v1.0
>
> 日期：2026-09-16
>
> 适用仓库：tenger-skills
>
> 目标：把“AI 先检索资产，再依据契约组合、适配、实现、验证并回写证据”的思想，落成一套可执行的工程流程。

## 0. 一句话定义

资产不是一段让 AI 复制的代码，而是一个拥有适用边界、输入输出、组合契约、实现适配、验证证据和生命周期的可复用工程决策单元。

AI 开发的标准过程不应是：

    需求 → AI 自由生成代码 → 代码能跑

而应是：

    需求
      → 识别问题与约束
      → 检索候选资产
      → 过滤不适用资产
      → 选择或组合已有资产
      → 绑定技术栈 Adapter
      → 生成实现计划
      → 实现代码
      → 自动/人工验证
      → 记录本次使用证据
      → 判断是否升级或新增资产

核心原则：

1. **先搜后做**：没有完成资产检索，不能直接声称“没有可复用方案”。
2. **先组合后创造**：优先复用已有 Pattern 和 Adapter；确实不适用时才提出新资产候选。
3. **模式与实现分离**：业务解决思路不绑定 Java、NestJS、Go 或 Python；语言和框架差异由 Adapter 承担。
4. **案例与模式分离**：案例说明“某项目怎么做、结果如何”，模式说明“一般情况下应该怎么做”。
5. **验证后沉淀**：未经真实项目、实验或可靠证据验证的内容只能是候选资产，不能进入稳定资产库。
6. **资产必须可追溯**：每次使用都能知道使用了哪个版本、哪个 Adapter、在哪个项目验证、结果如何。
7. **资产必须可拒绝**：资产要明确什么时候不能用，避免 AI 把熟悉的模式套到所有问题上。
8. **Agent 可替换**：资产、契约和验证证据不能依赖某一个 Agent 的记忆或特殊提示词。

---

# 1. 目标架构：五类资产 + 三类运行记录

## 1.1 五类核心资产

| 资产类型 | 回答的问题 | 是否绑定技术栈 | 典型内容 |
|---|---|---:|---|
| Method 方法 | 这个问题应该如何分析和决策 | 否 | 认证方法、幂等方法、遗留项目接手方法 |
| Pattern 模式 | 在什么条件下采用什么通用解法 | 否或弱绑定 | 密码登录、OTP 登录、OAuth 登录、Cache Aside |
| Composite 组合模式 | 多个模式的成熟组合顺序是什么 | 弱绑定 | 登录 + 会话 + 权限 + 审计 |
| Adapter 适配器 | 如何把通用模式落到具体技术栈 | 是 | NestJS、Spring Security、Express 适配器 |
| Template 模板 | 产物或工程骨架应该长什么样 | 通常绑定 | Auth 模块模板、测试用例模板、manifest 模板 |

## 1.2 三类运行记录

| 记录类型 | 作用 | 示例 |
|---|---|---|
| Case 实战案例 | 记录某一次真实项目的选型、实现和结果 | project-a.auth-login-2026-09 |
| Evidence 验证证据 | 证明资产是否有效 | 测试报告、压测数据、截图、日志、评审报告 |
| Anti-Pattern 反模式 | 记录不要采用的做法及其失败原因 | 把微信 access token 当作内部会话 |

关键区分：

    Method       = 怎么思考
    Pattern      = 一般怎么解决
    Composite    = 多个解法怎么组合
    Adapter      = 在某技术栈怎么实现
    Template     = 产出物怎么长
    Case         = 某项目实际怎么做
    Evidence     = 凭什么相信它有效
    Anti-Pattern = 什么做法不要再用

不要把这些东西混在一张“万能案例卡”里。单个项目的特殊约束不能污染通用模式；Java 代码不能被误认为登录模式本身；一次成功也不能证明方案已经稳定。

## 1.3 资产和代码的关系

    资产库：定义问题、决策、组合、适配和验证规则
    项目代码：在具体项目约束下实现资产
    项目 .spec：记录本次选择、差异、证据和结果

资产库不是代码仓库的替代品，也不是把所有项目代码复制一份。只有当项目实现中的内容满足通用性、可组合性和验证性要求时，才抽取回资产库。

---

# 2. 资产库目录规范

## 2.1 推荐目标目录

建议在仓库根目录逐步建立一个与 Skill 解耦的资产库：

    asset-library/
    ├── README.md
    ├── registry.yaml
    ├── schemas/
    │   ├── asset.schema.yaml
    │   ├── method.schema.yaml
    │   ├── pattern.schema.yaml
    │   ├── composite.schema.yaml
    │   ├── adapter.schema.yaml
    │   ├── template.schema.yaml
    │   ├── case.schema.yaml
    │   └── evidence.schema.yaml
    ├── methods/
    ├── patterns/
    ├── composites/
    ├── adapters/
    ├── templates/
    ├── cases/
    ├── anti-patterns/
    ├── evidence/
    └── migrations/

推荐的领域目录：

    patterns/authentication/
    patterns/authorization/
    patterns/session/
    patterns/reliability/
    patterns/data-access/
    adapters/backend/nestjs/
    adapters/backend/spring-security/
    templates/modules/
    cases/production/
    cases/failure/
    cases/experiment/

## 2.2 与当前仓库的渐进式兼容

当前仓库已经有 Skill 下的 references/case-library、assets、shared、issue 和 bug-patterns。不要一次性移动全部内容，采用三阶段迁移：

1. 阶段一：资产仍放原处，但统一 metadata、稳定 ID 和引用格式。
2. 阶段二：跨 Skill、跨项目复用的资产迁入 asset-library，旧位置保留索引文件。
3. 阶段三：asset-library 成为唯一来源，旧位置只保留迁移说明或兼容引用。

迁移期间禁止存在两份独立正文。可以有索引或兼容文件，但必须保持“一事一源”。

建议映射：

| 当前目录 | 目标逻辑类型 | 迁移规则 |
|---|---|---|
| <Skill>/references/case-library/ | Skill 专属案例或评审知识 | 稳定、跨 Skill 的条目再迁入案例库或模式库 |
| <Skill>/assets/ | Template、Adapter、工程骨架 | 增加 asset.yaml，明确资产类型 |
| shared/ | 公共规则、模板、方法 | 保持单一来源，不重复复制到各 Skill |
| bug-patterns/ | Failure Case、Anti-Pattern | 增加结构化 metadata，并关联修复模式 |
| issue/ | 未决问题和待沉淀事项 | 作为入口，不直接当作稳定资产 |

## 2.3 单个资产的最小目录

每个可被检索的资产建议使用独立目录：

    patterns/authentication/phone-otp-login/
    ├── asset.yaml
    ├── PATTERN.md
    ├── contract.yaml
    ├── verification.yaml
    ├── examples/
    ├── evidence-links.yaml
    └── CHANGELOG.md

文件职责：

| 文件 | 作用 |
|---|---|
| asset.yaml | 机器可读的发现信息、身份、状态、标签 |
| PATTERN.md | 给人和 Agent 阅读的决策说明 |
| contract.yaml | 输入、输出、依赖、冲突、顺序和组合约束 |
| verification.yaml | 必须验证什么、最低证据是什么 |
| examples/ | 最小示例，不放完整业务项目 |
| evidence-links.yaml | 项目证据索引 |
| CHANGELOG.md | 稳定资产的版本变更说明 |

asset.yaml 负责索引，正文负责理解，contract 负责组合，verification 负责证明。不要把全部内容塞进一份无法校验的大 Markdown。

---

# 3. 统一命名、ID 与版本规范

## 3.1 ID 命名

资产 ID 必须全小写，只使用字母、数字、点和连字符；身份稳定，不因为正文改一句话就改变；版本放在 version 字段而不是 ID 中。

推荐格式：

    <kind>.<domain>.<subdomain>.<name>

示例：

    method.security.authentication
    pattern.authentication.password-login
    pattern.authentication.phone-otp-login
    pattern.authentication.oauth-login
    composite.authentication.web-login
    adapter.backend.nestjs.authentication
    adapter.backend.spring-security.authentication
    adapter.provider.wechat-oauth
    template.module.auth-module
    case.production.project-a.auth-login
    anti-pattern.authentication.frontend-only-auth-state

不推荐：

    login-v1
    java-login
    my-best-login
    project-a-login-2026
    new-login-final-final

这些名称把版本、语言、个人判断或项目上下文混入身份，后续无法稳定复用和去重。

## 3.2 版本规范

推荐采用 MAJOR.MINOR.PATCH：

| 变化 | 版本变化 | 示例 |
|---|---:|---|
| 修正错别字、补充不改变含义的说明 | PATCH | 1.0.0 → 1.0.1 |
| 增加可选输入、增加兼容 Adapter、不破坏已有使用方式 | MINOR | 1.0.0 → 1.1.0 |
| 改变核心决策、输入输出、组合前置或安全语义 | MAJOR | 1.0.0 → 2.0.0 |

Pattern 和 Adapter 分别版本化：

    pattern.authentication.oauth-login@1.2.0
    adapter.backend.nestjs.authentication@2.0.0

项目锁定的是二者组合，而不是一个模糊的 login-v2：

    pattern.authentication.oauth-login@1.2.0
    adapter.backend.nestjs.authentication@2.0.0

Pattern 改变不应强制所有 Adapter 同步升级；Adapter 改变也不应自动改变 Pattern 的业务语义。

## 3.3 生命周期、成熟度和证据等级分开

这三个字段不能混成一个“状态”。

生命周期 status：

    draft       草稿，可讨论，不建议自动使用
    active      正常维护，可被候选检索
    deprecated  已弃用，不建议新项目使用
    retired     退役，仅保留历史追溯

成熟度 maturity：

    experimental  实验中
    validated     已经过真实验证
    stable        跨项目稳定复用

证据等级 evidence_level：

    L0  仅为推理或常识，没有本仓库验证
    L1  有一般经验、官方文档或标准支持
    L2  有本地实验、单元测试或集成测试
    L3  在一个真实项目验证过
    L4  在多个真实项目或线上生产数据中验证过

例如：

    status: active
    maturity: experimental
    evidence_level: L2

这表示它可以被试点使用，但还不应被当成组织级稳定标准。

## 3.4 置信度、假设和未知项

置信度不是 AI 的主观自信，而是证据和关键决策的完整程度：

    decision:
      confidence: medium
      assumptions:
        - identity_provider_supports_authorization_code_flow
        - access_token_is_not_used_as_internal_session
        - callback_domain_is_https_in_production
      unknowns:
        - expected_login_qps_is_not_confirmed
        - account_linking_policy_is_not_confirmed

关键假设未确认时，AI 必须把它列为待决策项，不能默认为成立。

---

# 4. 各类资产的规范

## 4.1 Method 方法卡

Method 不提供某个框架的代码，而是规定如何分析一类问题、收集哪些信息、做出什么决策。

必填内容：

    id: method.security.authentication
    kind: method
    problem: 如何为项目选择和设计认证方案
    inputs:
      - business-login-requirements
      - client-types
      - identity-sources
      - security-requirements
    outputs:
      - authentication-decision
      - selected-patterns
      - unresolved-decisions
    stop_conditions:
      - account-linking-policy-unknown
      - token-lifecycle-unknown
      - security-boundary-unknown

Method 正文建议包含：Goal、Required questions、Decision tree、Output contract、Common failure modes、References。

认证方法的关键问题包括：支持哪些登录主体；是否需要手机号、账号、邮箱或第三方登录；是否允许多种方式绑定同一用户；是否需要多端会话；是否需要高风险操作二次认证；身份源和内部用户体系如何映射。

## 4.2 Pattern 模式卡

Pattern 必须表达“什么时候用、什么时候不用、怎么组合、如何验证”，不能只是技术介绍文章。

正文最低结构：

    # Pattern name
    ## Problem
    ## Context
    ## When to use
    ## When not to use
    ## Inputs
    ## Provides
    ## Invariants
    ## Security requirements
    ## Trade-offs
    ## Composition contract
    ## Verification
    ## Anti-patterns
    ## Evidence
    ## Change history

每个 Pattern 必须声明：

    contract:
      requires:
        - user-identity-model
        - credential-validation
      provides:
        - authenticated-user
        - authentication-result
      side_effects:
        - failed-login-counter-update
        - security-audit-event
      conflicts_with:
        - password-plaintext-storage
      commonly_composed_with:
        - session-management
        - login-rate-limit
        - audit-logging
      ordering:
        before:
          - protected-resource-access
        after:
          - user-identity-model

适用条件必须可判断。不要写“适合大多数项目”，要写“项目拥有内部用户体系、要求服务端验证账号凭证、且用户可接受该认证方式”。同时必须写出不适用条件。

## 4.3 Composite 组合模式卡

当同一组 Pattern 在多个项目中以相同顺序组合，并且组合本身有稳定验证结果时，才建立 Composite。

Composite 必须定义：

- 必选组件；
- 可选组件和变体；
- 组件顺序；
- 输入输出连接；
- 互斥组件；
- 整体验收标准。

Composite 不是把所有能力强制开启，而是提供经过验证的组合骨架。

## 4.4 Adapter 适配器卡

Adapter 负责把 Pattern 落到具体语言、框架、ORM、数据库、认证 SDK 和项目目录约定。

必须说明：

- 语言、框架和版本范围；
- 依赖的库和运行环境；
- 目录和模块边界；
- DTO、异常和错误码映射；
- 事务、幂等和并发处理；
- 测试命令；
- 与旧项目的集成方式；
- 不覆盖哪些业务决策。

Adapter 不得把“是否允许微信登录”“是否自动注册”写死。它只说明这些决策如何映射到代码。

## 4.5 Template 模板卡

Template 是可复制的产物骨架，不等于完整方案。模板必须定义显式槽位：

    {{SUPPORTED_LOGIN_METHODS}}
    {{SESSION_STRATEGY}}
    {{ACCOUNT_LINKING_POLICY}}
    {{AUTH_PROVIDER_CONFIG}}

禁止 AI 通过猜测填写关键安全配置。

## 4.6 Case 实战案例卡

Case 记录一次具体项目，必须回答：项目约束是什么；选用了哪些资产和版本；为什么拒绝其他候选；哪些是项目特有差异；结果和证据是什么；哪些内容可以升级为通用资产；哪些只能保留为案例。

Case 不等于 Pattern。一个项目用了手机号登录，不代表所有登录都应该使用手机号登录。

## 4.7 Evidence 证据卡

Evidence 必须能定位到项目、文件、提交、命令、时间、结果和局限：

    claim: 混合登录流程在测试环境通过
    verification_type: e2e
    command: pnpm test:e2e -- auth-login
    executed_at: 2026-09-16T10:30:00+08:00
    result: passed
    limitations:
      - 未覆盖高并发压测
      - 未覆盖第三方供应商故障演练

“测试通过”不能扩大解释为“在线上任何条件下稳定”。

## 4.8 Anti-Pattern 反模式卡

反模式建议使用以下结构：

    symptom: 前端保存 isLoggedIn=true，服务端不验证会话
    risk:
      - unauthorized-access
      - forged-client-state
    root_cause: 把界面状态当成身份认证事实
    corrective_patterns:
      - pattern.authentication.session-management
      - pattern.security.server-side-authorization
    found_in:
      - case.failure.project-b.auth-bypass-2026-08

反模式最好形成“症状 → 根因 → 影响 → 修复模式 → 发现证据”的闭环。

---

# 5. 资产创建、使用、沉淀和升级流程

## 5.1 四个沉淀时点

资产沉淀不是开发结束时写一篇总结，而是贯穿全过程：

    T0  需求/方案阶段：发现候选资产并记录选型
    T1  开发阶段：记录资产如何被适配和组合
    T2  验证阶段：保存真实验证证据
    T3  交付/复盘阶段：判断新增、更新、弃用或反模式

这样可以保留“为什么选它、为什么拒绝其他方案、哪些是项目特有差异、经过多少轮修复”等信息。

## 5.2 资产状态机

    OBSERVED
      ↓ 识别出可复用问题
    CANDIDATE
      ↓ 补齐契约、边界、实现映射
    EXPERIMENTAL
      ↓ 实验或单项目真实验证
    VALIDATED
      ↓ 跨项目复用或长期观察
    STABLE
      ↓ 发现不适用或被替代
    DEPRECATED
      ↓ 完成迁移，仅保留历史追溯
    RETIRED

| 状态 | 是否可被 AI 自动选用 | 规则 |
|---|---:|---|
| OBSERVED | 否 | 只有现象记录 |
| CANDIDATE | 否，需人工确认 | 尚未补齐契约 |
| EXPERIMENTAL | 可用于试点 | 必须显式提示风险 |
| VALIDATED | 可正常候选 | 有至少一次真实验证 |
| STABLE | 可作为默认候选 | 有跨项目或长期证据 |
| DEPRECATED | 否 | 新项目不可选，旧项目可维护 |
| RETIRED | 否 | 仅追溯 |

## 5.3 每次开发的九步协议

### Step 1：创建任务上下文

在项目中建立 .spec/<feature>/asset-usage.yaml，记录任务、问题、约束和技术栈。

### Step 2：生成标准标签

例如：

    domain:
      - authentication
      - security
    capabilities:
      - password-login
      - phone-otp-login
      - oauth-login
    constraints:
      - existing-user-model
      - account-linking-required
    runtime:
      language: typescript
      framework: nestjs

### Step 3：检索候选资产

顺序固定为：元数据过滤 → requires/conflicts 过滤 → 匹配 Adapter → 按证据等级和成熟度排序 → 阅读候选正文和案例。

检索结果必须有 candidates、selected、rejected、unresolved 四类，不允许只输出一个推荐结论。

### Step 4：建立组合图

明确每个节点的前置、输出、顺序、冲突、错误和安全边界。

### Step 5：锁定版本和 Adapter

在 asset-selection.yaml 中记录 Pattern、Composite、Adapter、Template 的 ID 和版本。

### Step 6：先生成实现计划

计划必须说明：修改哪些文件；每个文件对应哪个资产；哪些内容来自 Adapter；哪些是项目特有逻辑；哪些决策仍需人工确认；如何测试每条验收标准。

### Step 7：实现和验证

开发时不得修改资产库正文来适应单个项目；项目差异写入项目配置或 Case；通用缺口记为 Candidate；执行构建、单元、集成、E2E、安全和回归验证。

### Step 8：回写使用证据

记录实际使用版本、代码提交、测试命令、结果、失败和局限。

### Step 9：提交沉淀判断

判断本次应更新 Pattern、增加 Adapter、创建 Composite、创建 Template、记录 Case，还是新增 Anti-Pattern。未补齐信息的内容进入 Candidate 区，不进入 Stable 索引。

---

# 6. 去重规范：什么时候新建，什么时候更新

## 6.1 四种差异分类

| 差异 | 处理方式 | 是否新建完整资产 |
|---|---|---:|
| 项目配置变化 | 项目配置或 Case | 否 |
| 语言、框架、SDK、目录变化 | Adapter | 否 |
| 核心业务规则变化但仍是同一问题 | Pattern 新版本或变体 | 通常否 |
| 输入输出、威胁模型、组合顺序完全不同 | 新 Pattern | 是 |
| 多个 Pattern 形成稳定流程 | Composite | 是 |
| 失败做法及原因 | Anti-Pattern / Failure Case | 通常不是新 Pattern |

## 6.2 新建 Pattern 的六个判定问题

以下问题不能全部回答“是”，就不要急着新建完整 Pattern：

1. 这是不是独立问题，而不是已有 Pattern 的配置差异？
2. 是否有独立输入和输出？
3. 是否有独立适用和不适用条件？
4. 是否有独立失败模式或安全边界？
5. 是否能被其他项目独立组合？
6. 是否需要独立版本和独立验证？

如果只是“同一个方案换了框架、字段名或 SDK”，应更新或新增 Adapter。

## 6.3 什么时候更新已有 Pattern

以下情况更新已有 Pattern：

- 适用边界不完整；
- 发现普遍适用的安全约束；
- 验证结果改变原有结论；
- 增加不改变核心语义的兼容变体；
- 补充普遍失败模式。

如果改变核心输入输出、组合顺序或安全语义，必须升级 MAJOR 版本，保留旧版本和迁移说明。

---

# 7. 登录案例一：项目 A 的手机号登录

## 7.1 需求

    用户可以通过手机号和短信验证码登录。
    首次登录自动创建用户。
    登录成功后获得登录态。

## 7.2 需求阶段的资产标签

    domain:
      - authentication
      - security
    capabilities:
      - phone-otp-login
      - account-provisioning
      - session-management
    constraints:
      - existing-user-table
      - sms-provider-required
      - auto-register-is-required
      - session-strategy-must-be-decided

## 7.3 候选资产

    method.security.authentication
    pattern.authentication.identity-model
    pattern.authentication.phone-otp-login
    pattern.authentication.account-provisioning
    pattern.authentication.session-management
    adapter.backend.nestjs.authentication

项目特有配置：短信供应商、验证码过期时间、错误次数、默认角色、JWT 或 Redis Session。这些不能直接写入通用 Pattern。

## 7.4 组合顺序

    identity-model
      → phone-otp-login
      → account-provisioning(auto-create)
      → session-management(jwt)
      → audit-logging

## 7.5 项目侧选择文件

    feature: project-a.phone-login
    selected:
      - id: method.security.authentication
        version: 1.0.0
      - id: pattern.authentication.identity-model
        version: 1.0.0
      - id: pattern.authentication.phone-otp-login
        version: 1.0.0
      - id: pattern.authentication.account-provisioning
        version: 1.0.0
      - id: pattern.authentication.session-management
        version: 1.0.0
      - id: adapter.backend.nestjs.authentication
        version: 1.0.0
    project_decisions:
      sms_provider: aliyun-sms
      otp_expire_seconds: 300
      max_attempts: 5
      auto_register: true
      default_role: user
      session_strategy: jwt

## 7.6 第一次沉淀结果

第一次完成后形成：

    Pattern Candidate：phone-otp-login
    Adapter Candidate：nestjs-authentication
    Case：project-a.phone-login
    Evidence：integration test、E2E、Code Review、安全检查

如果只有“本地代码跑通”而没有有效边界和验证证据，不能写成 Stable。

---

# 8. 登录案例二：项目 B 的账号登录 + 微信登录

## 8.1 需求

    用户可以使用账号密码登录，也可以使用微信登录。
    微信首次登录可以自动创建账号。
    微信身份与已有手机号匹配时，进入绑定确认流程。

## 8.2 错误做法

复制项目 A 的完整“手机号登录资产”，改账号字段，再把微信 SDK 粘进去，另存为 login-v2。

问题：手机号、账号、微信逻辑互相嵌套；修复无法定位；版本没有语义；相似实现越来越多。

## 8.3 正确拆分

    Method
    └── method.security.authentication

    Identity / Account
    ├── pattern.authentication.identity-model
    ├── pattern.authentication.account-provisioning
    └── pattern.authentication.account-linking

    Credential / Provider
    ├── pattern.authentication.password-login
    ├── pattern.authentication.phone-otp-login
    └── pattern.authentication.oauth-login

    Session / Security
    ├── pattern.authentication.session-management
    ├── pattern.authentication.login-rate-limit
    └── pattern.security.audit-logging

    Technology
    ├── adapter.backend.nestjs.authentication
    └── adapter.provider.wechat-oauth

手机号登录不是被升级成“登录 v2”，而是一个可选原子组件；项目 B 选择账号密码和微信 OAuth，没有选择手机号 Pattern。

## 8.4 组合流程

    用户身份模型
      ↓
      ├─ 账号密码验证
      └─ 微信 OAuth 验证
              ↓
        外部身份映射
              ↓
        账号查找 / 创建 / 绑定确认
              ↓
        内部会话签发
              ↓
        审计与风控

## 8.5 选择结果示例

    selected:
      - method.security.authentication@1.0.0
      - pattern.authentication.identity-model@1.0.0
      - pattern.authentication.password-login@1.0.0
      - pattern.authentication.oauth-login@1.0.0
      - pattern.authentication.account-linking@1.0.0
      - pattern.authentication.session-management@1.0.0
      - adapter.backend.nestjs.authentication@1.0.0
      - adapter.provider.wechat-oauth@1.0.0
    rejected:
      - id: pattern.authentication.magic-link
        reason: 当前没有邮箱验证链路
    unresolved:
      - 微信首次登录是否自动创建用户
      - 微信身份与已有手机号冲突时是否允许人工绑定
      - 是否需要踢出旧设备

---

# 9. 登录案例三：Java / Spring Security 实现

项目 C 的业务需求和项目 B 类似，但后端从 NestJS 换为 Spring Boot。

## 9.1 复用的资产

    method.security.authentication
    pattern.authentication.identity-model
    pattern.authentication.password-login
    pattern.authentication.oauth-login
    pattern.authentication.account-linking
    pattern.authentication.session-management
    pattern.security.audit-logging

## 9.2 更换的资产

    adapter.backend.nestjs.authentication
    → adapter.backend.spring-security.authentication

可能新增：

    adapter.provider.wechat-spring-sdk

## 9.3 为什么业务资产仍然成立

与语言无关的内容包括：密码不能明文存储；第三方身份不能直接当内部用户 ID；回调需要校验 state/nonce；内部会话必须由本系统签发或明确验证；账号绑定需要明确策略；失败登录需要限流和审计。

属于 Adapter 的内容包括 NestJS Guard、Spring Security Filter、TypeScript DTO、Java Request/Response Model、ORM Repository、JPA Repository。

结论：不是 login-v1、login-v2、login-v3，而是稳定的原子能力、组合流程、技术栈适配器和项目证据。

---

# 10. 登录 Pattern 示例

## 10.1 phone-otp-login

元数据示例：

    id: pattern.authentication.phone-otp-login
    kind: pattern
    version: 1.0.0
    status: active
    maturity: validated
    evidence_level: L3
    problem: 使用手机号和一次性验证码完成身份验证
    when_to_use:
      - system_accepts_phone_identity
      - otp_provider_available
    when_not_to_use:
      - high_assurance_identity_required_without_step_up
      - provider_reliability_or_cost_is_uncontrolled
    requires:
      - otp-challenge-storage
      - otp-send-provider
      - attempt-limit
    provides:
      - verified-identity-factor
      - authentication-result
    ordering:
      after: otp-challenge-created
      before: session-issued

必须验证：有效验证码、无效验证码、过期验证码、重复使用、超过次数、供应商超时、重复提交。

安全不变量：验证码单次使用、有过期时间、限制尝试次数、不记录原始验证码、避免用户枚举、按手机号和客户端限流。

它不负责：用户表设计、是否自动注册、Session 是 JWT 还是 Redis、短信供应商、前端页面。

## 10.2 oauth-login

元数据示例：

    id: pattern.authentication.oauth-login
    kind: pattern
    version: 1.0.0
    status: active
    maturity: experimental
    evidence_level: L2
    requires:
      - provider-adapter
      - state-validation
      - nonce-validation
      - redirect-uri-validation
      - account-mapping-policy
    provides:
      - verified-external-identity
      - external-account-reference
    conflicts_with:
      - trusting-unverified-client-profile
      - using-provider-access-token-as-internal-session

必须验证：成功回调、错误 state、错误 nonce、重复 code、供应商错误、重复回调、已有账号绑定、首次登录创建。

安全边界：不信任客户端传来的身份；不把微信 access token 当作本系统 Session；不记录 Provider Secret；明确定义 token 存储、过期和撤销策略。

## 10.3 session-management

它是独立 Pattern，可以有 jwt-stateless、redis-session、opaque-token-with-introspection 等变体。变更 Session 策略不需要复制整套登录流程，只需选择不同变体或 Adapter 配置。

---

# 11. 组合契约与顺序规范

## 11.1 五类关系

| 关系 | 含义 | 登录示例 |
|---|---|---|
| requires | 没有它无法使用 | OAuth 需要 Provider Adapter |
| enhances | 对已有能力增强 | 登录限流增强密码登录 |
| conflicts | 不能同时或不能这样使用 | 明文密码存储与安全密码登录冲突 |
| replaces | 新模式替代旧模式 | OIDC Adapter 替代不安全自定义 OAuth |
| commonly-composed-with | 常见但非强制组合 | 登录常与审计、会话管理组合 |

## 11.2 输入输出

每个 Pattern 至少声明输入类型、必填字段、输出类型、错误类型。下一个 Pattern 的 requires 必须能从前置节点的 provides 获得。

## 11.3 登录的最小正确顺序

    1. 接收登录请求
    2. 校验请求格式和基础限流
    3. 验证内部凭证或第三方身份
    4. 解析内部用户身份
    5. 执行创建、绑定或冲突处理
    6. 签发内部会话
    7. 写入审计事件
    8. 返回最小必要信息

常见错误顺序：先签发 Session 再验证第三方身份；把前端 userId 当作已认证用户；先自动绑定再确认归属；将 Provider Token 直接作为内部 Session；失败登录不计数、不限流、不审计。

这些错误应沉淀为 Anti-Pattern 或评审检查项。

---

# 12. 项目侧文件规范

每个需要资产化管理的功能，在项目 .spec/<feature>/ 下建议有：

    asset-needs.yaml
    asset-selection.yaml
    composition.yaml
    implementation-plan.md
    asset-usage.yaml
    verification-report.md
    evidence.yaml
    case-draft.md
    pipeline-state.yaml

## 12.1 asset-needs.yaml

    task:
      id: project-b.feature.auth-login
      problem: 支持账号、手机号和微信登录
    tags:
      domain: [authentication, security]
      capabilities: [password-login, phone-otp-login, oauth-login]
      constraints: [existing-user-model, account-linking-required]
    runtime:
      language: typescript
      framework: nestjs

## 12.2 asset-selection.yaml

    selected:
      - id: pattern.authentication.oauth-login
        version: 1.0.0
        reason: 需求要求微信登录
    rejected:
      - id: pattern.authentication.magic-link
        reason: 没有邮箱验证链路
    unresolved:
      - 微信首次登录是否自动创建用户

## 12.3 composition.yaml

    components:
      - id: pattern.authentication.identity-model
        version: 1.0.0
        role: identity
      - id: pattern.authentication.password-login
        version: 1.0.0
        role: credential-verification
      - id: pattern.authentication.oauth-login
        version: 1.0.0
        role: external-verification
      - id: pattern.authentication.account-linking
        version: 1.0.0
        role: identity-resolution
      - id: pattern.authentication.session-management
        version: 1.0.0
        role: session
      - id: adapter.backend.nestjs.authentication
        version: 1.0.0
        role: implementation
    edges:
      - from: identity-model
        to: credential-verification
      - from: credential-verification
        to: identity-resolution
      - from: external-verification
        to: identity-resolution
      - from: identity-resolution
        to: session
    constraints:
      - provider-token-is-not-internal-session
      - account-linking-requires-explicit-policy
      - all-login-failures-are-rate-limited

## 12.4 asset-usage.yaml

    feature: project-b.auth-login
    selected:
      - id: pattern.authentication.oauth-login
        version: 1.0.0
        actual_changes: 微信 Provider 使用 authorization-code flow
      - id: adapter.backend.nestjs.authentication
        version: 1.0.0
        actual_changes: Repository 遵循现有 monorepo 边界
    not_used:
      - id: pattern.authentication.phone-otp-login
        reason: 本项目本期没有手机号登录需求
    new_candidates:
      - name: existing-account-conflict-resolution
        reason: 微信身份与历史手机号冲突，需要人工确认
    verification:
      status: passed
      evidence: .spec/auth-login/evidence.yaml

---

# 13. 与现有 Skill 的集成

## 13.1 PRD-Design / PRD-Review

产品阶段负责识别能力、约束和复用机会，不决定框架代码。产物建议增加：

    .spec/<feature>/asset-needs.yaml

内容包括 capabilities、constraints、existing-system、non-functional-requirements、legacy-boundaries。

## 13.2 Backend-Tech-Design / Frontend-Tech-Design

技术方案阶段负责检索并选择 Pattern、Composite、Adapter；形成组合图；记录替代方案和拒绝理由；输出资产锁定清单：

    .spec/<feature>/asset-selection.yaml
    .spec/<feature>/composition.yaml

## 13.3 Backend-Dev / Frontend-Dev

开发阶段按锁定版本实现；不私自修改全局 Pattern；将项目差异放在项目层；发现通用缺口时提交 Candidate；回写实际使用版本和代码变更。

## 13.4 Tech-Review / Code-Review

评审检查组合契约、Pattern 不变量、Adapter 约定、不必要的重复实现、未记录的项目决策和安全反模式。

## 13.5 Testing

测试根据 Pattern 的 verification.required 生成测试矩阵，根据 Adapter 的命令执行构建、单元、集成和 E2E，并把新增失败模式回写到 failure case 和 anti-patterns。

## 13.6 Workflow

Workflow 增加五个资产门禁：

    检索门禁：是否完成候选分析
    选择门禁：是否记录 selected/rejected/unresolved
    实现门禁：是否记录实际使用版本
    验证门禁：是否有可定位证据
    沉淀门禁：是否完成 Case/Pattern/Adapter 判断

Workflow 不替代专家选择，也不把所有资产决策硬编码为固定流程。

---

# 14. 资产沉淀评审规范

## 14.1 通用性检查

- 是否解决独立问题？
- 是否把项目配置误写成通用规则？
- 是否把框架实现误写成 Pattern？
- 是否可以被另一个项目独立引用？

## 14.2 契约检查

- requires、provides、conflicts、ordering 是否完整？
- 组合后错误路径是否覆盖？
- 安全不变量是否可验证？
- 是否声明副作用、幂等和数据一致性要求？

## 14.3 证据检查

- 是否至少有一种可定位证据？
- 证据是否包含项目、提交、命令、时间和范围？
- 是否记录局限？
- 是否把一次通过夸大成稳定结论？

## 14.4 去重检查

- 是否检索 aliases 和相近资产？
- 是更新已有资产还是新建资产？
- 技术差异是否应该进入 Adapter？
- 是否产生了重复的完整代码模板？

## 14.5 晋级规则

Candidate → Experimental：有完整契约、边界、负责人和验证计划。

Experimental → Validated：真实项目或可重复实验通过；有测试、评审或运行证据；失败路径已记录；无未关闭 P0/P1。

Validated → Stable：建议至少在两个不同项目或明显不同场景使用；有回归验证；观察期无重复严重缺陷；有默认选择和禁用条件。

---

# 15. 遗留项目的资产接入

接手运行十几年的项目时，不要先把全部旧代码“资产化”，也不要先重写。采用：

    Inventory：盘点入口、服务、数据库和外部依赖
    Observe：记录真实运行行为
    Characterize：为关键行为补特征测试
    Map：旧代码先记录为现状 Case
    Boundary：确定新增代码与旧代码边界
    Golden Slice：选择一个小功能走新资产流程
    Adapter：通过适配层接入旧系统
    Verify：回归和线上观察
    Extract：从验证过的改造中提炼资产

旧代码通常只能先作为 Case 或 Evidence。运行时间长不等于设计可以直接复用。

老登录模块的处理示例：

1. 通过日志和接口调用确认旧登录行为。
2. 为登录成功、失败、过期、退出和权限检查补 characterization tests。
3. 把旧实现记录为 case.observed.legacy-auth-baseline。
4. 新增登录方式走新的 Pattern 和模块。
5. 旧用户表通过 adapter.legacy.user-table-readonly 接入。
6. 对密码升级、Session 替换、微信绑定分别建立迁移任务。
7. 新旧链路并行观察，完成迁移后再将旧实现标记 Deprecated。

---

# 16. Git 与资产变更规范

资产变更尽量独立提交：

    feat(asset): add oauth login pattern
    feat(adapter): add nestjs auth adapter
    feat(case): record project-b mixed login
    fix(pattern): clarify oauth token boundary
    fix(anti-pattern): add frontend-only auth failure

修改 Stable 资产必须：增加版本；记录变更原因；运行关联场景；检查项目影响；必要时保留旧版本和迁移说明。

禁止静默修改稳定资产。业务代码可以先在项目中验证，资产库的升级应在证据形成后单独提交。

---

# 17. 90 天落地计划

## 第 1～7 天：定规则，不改全库

产出 asset-library/README.md、schema、ID 规范、生命周期规范、证据等级规范和登录任务模板。只选择登录作为第一个示范领域。

## 第 8～21 天：建立登录最小资产集

    method.security.authentication
    pattern.authentication.identity-model
    pattern.authentication.password-login
    pattern.authentication.phone-otp-login
    pattern.authentication.oauth-login
    pattern.authentication.account-linking
    pattern.authentication.account-provisioning
    pattern.authentication.session-management
    pattern.security.audit-logging
    adapter.backend.nestjs.authentication
    adapter.backend.spring-security.authentication
    adapter.provider.wechat-oauth
    composite.authentication.web-login

先不要建立几十种登录 Pattern，只覆盖真实需求和关键边界。

## 第 22～35 天：打通一个 NestJS 项目

    PRD → 资产需求 → 技术方案 → 资产选择 → 组合 → 开发 → 评审 → 测试 → Case/Evidence

验收：能输出资产选择；能锁定版本；能生成组合图；能执行测试；能回写 Case 和 Evidence。

## 第 36～50 天：验证账号密码 + 微信变体

检查是否复制手机号资产；是否拆出 OAuth 和账号绑定；是否复用 Session Pattern；是否出现新的通用 Pattern。

## 第 51～65 天：增加 Spring Adapter

使用同一组业务 Pattern 替换 NestJS Adapter，验证语言解耦。

## 第 66～75 天：自动化校验

    asset-id 校验
    asset.yaml schema 校验
    引用存在性校验
    版本格式校验
    requires/provides 基础兼容性校验
    循环依赖检测
    生成物扫描

## 第 76～90 天：接入现有 Skill 和 Workflow

优先接入 Backend-Tech-Design、Backend-Dev、Code-Review、Testing、Workflow，再扩展到前端、产品、设计和 BugFix。

---

# 18. 第一阶段验收标准

- [ ] 有统一资产 ID、类型、版本、状态和 owner。
- [ ] 有 Method、Pattern、Adapter、Template、Case、Evidence、Anti-Pattern 的边界。
- [ ] 完成登录领域的最小资产集。
- [ ] 手机号、账号密码、微信登录能以原子 Pattern 组合。
- [ ] Java/Spring 和 NestJS 能复用同一组业务 Pattern。
- [ ] 资产选择有 selected、rejected、unresolved 记录。
- [ ] 组合关系包含 requires、provides、conflicts、ordering。
- [ ] 每次项目使用都有版本和证据。
- [ ] 新需求能判断新建 Pattern、更新 Pattern、增加 Adapter 还是只记录 Case。
- [ ] 未验证资产不会被标为 Stable。
- [ ] 至少有一个成功案例和一个失败/反模式案例。
- [ ] 旧项目可以通过 Adapter 渐进接入，而不是一次性重写。

---

# 19. 最终执行原则

    需求不是直接进入代码生成，而是先转化为问题标签和约束。
    AI 不是从空白开始发明方案，而是在候选资产中进行选择、组合和适配。
    Pattern 不承载所有差异；项目差异进入配置和 Case，技术差异进入 Adapter。
    代码不是资产的唯一形态；契约、模板、验证证据和失败模式同样是资产。
    未经验证的经验只能是 Candidate；一次成功只能是 Evidence，不自动等于 Stable。

这套体系真正要沉淀的不是“登录代码”，而是：

    登录问题的分析方法
    + 可组合的认证能力
    + 不同技术栈的实现适配
    + 可验证的安全不变量
    + 项目使用和失败证据
    + 可持续演进的版本关系

# 20. 没有现成资产时的规格化开发与质量保证

## 20.1 对这个理解的确认

你的理解是正确的，但需要补充一个关键限定：**没有现成的代码资产，不等于没有可复用的工程资产，也不等于可以直接让 AI 从自然语言跳到代码。**

没有现成 Pattern、Template 或 Composite 时，仍然要按照一套固定流程，把本次业务先沉淀成：

    业务流程规格
    + 领域模型
    + 状态机
    + 业务规则
    + 权限规则
    + 数据约束
    + API/事件契约
    + 验收场景
    + 实现边界
    + 开发和验证证据

然后再让 AI 根据这套规格实现代码。

因此，资产缺失时的正确模式不是：

    没有模板 → AI 自由发挥 → 代码跑通

而是：

    没有现成实现资产
    → 按统一方法梳理业务
    → 形成可评审的规范资产
    → 通过规格编译门
    → 选择技术实现适配器
    → AI 实现代码
    → 用契约、测试和评审验证
    → 将本次结果沉淀为 Case/Evidence
    → 判断是否晋级为新的 Pattern/Composite

**资产库不仅保存已经写好的代码，也保存“以后如何稳定地解决这类问题”的方法和事实。**

## 20.2 资产缺失时，必须区分三种情况

| 情况 | 实际含义 | AI 的处理方式 | 最终沉淀物 |
|---|---|---|---|
| 实现资产缺失 | 有明确业务规则，只是没有现成代码 | 根据规格设计并实现 | Case、Evidence，必要时提炼 Pattern |
| 业务规格缺失 | 连业务规则、边界和异常都没有明确 | 先提问、建模、评审，禁止直接编码 | Business Process Asset |
| 技术适配器缺失 | 业务模式已存在，但新技术栈没有实现方式 | 复用业务规格，新增 Adapter | Adapter Candidate、技术验证证据 |

例如“报表查询”通常不是缺少一个 `ReportService` 模板，而是每个报表的指标定义、数据口径、权限范围、时间口径和聚合逻辑不同。此时不能为了复用而制造一个过度抽象的万能报表模板，而应先沉淀报表定义和查询契约，再由 AI 实现该报表的专属查询逻辑。

## 20.3 资产缺失时的核心原则

### 原则一：先沉淀事实，再沉淀实现

业务事实包括“谁在什么条件下执行什么动作，状态如何变化，结果是什么”。实现方式包括表、接口、类、函数和框架配置。事实必须先于实现确定。

### 原则二：AI 可以自主实现，不可以静默发明关键规则

AI 可以自主选择合理的表名、模块组织方式和技术实现细节，但以下内容必须由人确认或由已有资产明确规定：

    金额、时间、数量等边界值
    状态及状态转换条件
    权限范围和数据隔离规则
    是否允许重复提交、重试、撤销和并发操作
    事务边界和一致性要求
    删除、归档和数据保留策略
    外部系统调用失败后的补偿策略
    审计、合规和敏感数据处理规则

当这些信息缺失时，AI 的输出必须是 `OPEN_QUESTION` 或 `ASSUMPTION`，不能把猜测直接写进生产代码。

### 原则三：先形成最小可执行规格，不追求一开始写完所有文档

规格可以从最小闭环开始：

    目标
    → 核心实体
    → 核心状态
    → 核心命令
    → 核心规则
    → 关键异常
    → 验收场景

后续再补充性能、审计、迁移和运营要求。不能因为没有完成全部设计，就跳过最小规格直接生成代码。

### 原则四：质量保证靠“规格 + 门禁 + 证据”，不是靠 AI 自觉

同一个业务交给不同 AI，不能仅靠 Prompt 保证代码一样。要把输入规格固定下来，把生成过程和验证过程标准化：

    Canonical Specification（规范事实源）
    + Implementation Profile（实现配置）
    + 固定检查规则
    + 固定验收场景
    + 固定代码评审清单
    + 可追溯的生成和测试证据

这样即使源码文本不同，也可以保证结构、行为和维护边界一致。

## 20.4 资产缺失状态机

所有“没有找到匹配资产”的任务，都要显式进入以下状态，不能悄悄绕过资产流程：

```text
ASSET_MISSING
    ↓
DISCOVERY_REQUIRED
    ↓
SPEC_DRAFT
    ↓
SPEC_REVIEW
    ├── NEEDS_CLARIFICATION → 返回 SPEC_DRAFT
    └── APPROVED
            ↓
IMPLEMENTATION_PLANNED
            ↓
IMPLEMENTED
            ↓
VERIFIED
            ↓
CASE_RECORDED
            ├── PROJECT_SPECIFIC
            ├── PATTERN_CANDIDATE
            ├── COMPOSITE_CANDIDATE
            └── ADAPTER_CANDIDATE
```

各状态的含义和门禁如下：

| 状态 | 可以做什么 | 不可以做什么 | 必须有的产物 |
|---|---|---|---|
| `ASSET_MISSING` | 记录检索不到的原因 | 直接开始生成生产代码 | `asset-gap.yaml` |
| `DISCOVERY_REQUIRED` | 识别业务术语和范围 | 自行补充关键规则 | 问题清单、术语表 |
| `SPEC_DRAFT` | 建模、写规则和场景 | 把假设伪装成已确认事实 | 规格草案 |
| `SPEC_REVIEW` | 由产品、技术、测试共同评审 | 只由 AI 自行批准 | 评审记录、决策记录 |
| `APPROVED` | 制定实现计划 | 未经变更流程修改事实源 | 已批准规格版本 |
| `IMPLEMENTED` | 编码、迁移、补测试 | 宣称已稳定复用 | 代码、测试、迁移脚本 |
| `VERIFIED` | 记录证据并运行真实场景 | 省略失败场景 | 测试报告、评审报告 |
| `CASE_RECORDED` | 判断是否提炼通用资产 | 直接把一次实现标为 Stable | Case、Evidence、沉淀决策 |

## 20.5 资产缺失时的十二步执行流程

### Step 1：记录资产缺口

在任务上下文中记录：

```yaml
asset_gap:
  id: gap.report.monthly-sales.v1
  requested_capability: monthly-sales-report
  search_scope:
    - asset-library/patterns
    - asset-library/composites
    - asset-library/adapters
  matched_assets: []
  missing_reason: no_matching_business_metric_definition
  risk_level: high
  owner: product-owner
```

`missing_reason` 必须说明“为什么不匹配”，不能只写“没有找到”。常见原因包括：业务口径不同、权限范围不同、性能约束不同、数据源不同、技术栈不同或资产质量不足。

### Step 2：建立术语表和边界

先定义业务语言，避免 AI 根据同一个词作出不同解释：

```yaml
ubiquitous_language:
  order_amount:
    definition: 订单最终支付金额，不包含已取消订单
  active_customer:
    definition: 在统计周期内至少有一笔已支付订单的客户
  report_period:
    definition: 按业务时区 Asia/Shanghai 的自然月
```

每个术语至少包含名称、定义、数据来源、排除条件和责任人。

### Step 3：识别业务角色、实体和边界

输出领域模型，而不是直接输出数据库表：

```yaml
entities:
  - id: order
    purpose: 记录订单及订单生命周期
    ownership: order-domain
  - id: customer
    purpose: 记录客户主体
    ownership: customer-domain
  - id: report-query
    purpose: 报表查询请求，不持久化为业务实体
    ownership: reporting-domain
```

AI 可以根据领域模型提出表设计建议，但不能反过来用数据库表名定义业务事实。

### Step 4：定义状态、命令和事件

对有生命周期的实体，必须显式写出状态机：

```yaml
state_machine:
  entity: order
  initial: CREATED
  states: [CREATED, PAID, CANCELLED, REFUNDED]
  transitions:
    - command: pay-order
      from: CREATED
      to: PAID
      actor: customer
    - command: cancel-order
      from: CREATED
      to: CANCELLED
      actor: customer
    - command: refund-order
      from: PAID
      to: REFUNDED
      actor: operator
```

如果业务没有状态机，也要明确记录 `state_machine: not_applicable` 和理由，不能默认遗漏。

### Step 5：定义规则和不变量

规则应可执行、可测试，避免只写“系统应正确处理”：

```yaml
rules:
  - id: report.exclude-cancelled-orders
    statement: 统计销售额时排除 CANCELLED 状态订单
    priority: mandatory
    source: product-decision-2026-09-17-001
  - id: report.use-business-timezone
    statement: 月份边界按 Asia/Shanghai 计算
    priority: mandatory
    source: product-decision-2026-09-17-002
  - id: report.customer-scope
    statement: 普通用户只能查询自己所属组织的数据
    priority: mandatory
    source: security-policy
invariants:
  - 查询结果不得包含无权限组织的数据
  - 同一查询参数和同一数据快照得到的结果可重复
```

### Step 6：定义数据、接口和事务契约

至少明确：

    主键和唯一约束
    外键或逻辑关联
    空值和默认值
    金额、数量、时区和精度
    分页、排序和最大查询范围
    API 请求/响应结构
    错误码和错误信息
    事务边界、锁和幂等要求

建议使用机器可读的 `api-contract.yaml` 或 OpenAPI，并同时写出业务语义，不要只依赖 Controller 上的类型定义。

### Step 7：编写验收场景

每一条强制业务规则至少对应一个正例和一个反例。报表类需求至少覆盖：

    有数据、无数据
    时间边界和跨时区
    分页和排序
    权限过滤
    状态过滤
    重复请求
    大数据量和超时
    数据为空或关联数据缺失
    SQL 注入和非法参数

验收场景应成为后续 AI 实现和代码评审的固定输入。

### Step 8：通过“业务规格编译门”

在开发前自动或人工检查：

```text
[ ] 每个术语有唯一含义
[ ] 每个核心实体有责任边界
[ ] 状态都能从初始状态到达或被明确标记为不可达
[ ] 每个状态转换都有命令、角色和条件
[ ] 规则之间不存在冲突
[ ] 权限规则覆盖读、写、审批和导出
[ ] 数据关系、删除策略、并发和幂等已定义
[ ] 每条强制规则都有验收场景
[ ] 未确认内容都被标记为 OPEN_QUESTION 或 ASSUMPTION
[ ] 规格版本、评审人和决策来源已记录
```

规格编译门未通过时，Workflow 应停留在 `SPEC_REVIEW`，不能进入 `Backend-Dev` 或 `Frontend-Dev`。

### Step 9：生成实现计划，而不是直接生成全部代码

AI 先输出：

    模块边界
    领域层、应用层、基础设施层职责
    数据库迁移计划
    API 和事件清单
    事务边界
    依赖方向
    需要复用的资产
    需要新增的 Adapter
    未决问题和风险
    测试映射表

人类评审实现计划后，AI 再进入分阶段编码。这样可以在成本最低时发现模型误解。

### Step 10：按固定边界实现

建议采用以下目录边界：

```text
src/
├── generated/       # 由规格或生成器产生；禁止手工修改
├── domain/          # 实体、值对象、状态机、业务规则
├── application/     # 用例编排、事务入口、权限用例
├── infrastructure/  # ORM、数据库、消息、外部服务 Adapter
├── interfaces/      # HTTP、GraphQL、CLI、事件入口
└── tests/            # 单元、集成、契约、验收和性能测试
```

并非所有项目都必须机械采用相同目录，但职责边界必须保持一致。技术栈变化进入 Adapter，业务事实变化回到规格。

### Step 11：按规格验证并生成证据

验证至少包括：

    规格到数据库结构的映射
    规格到 API 契约的映射
    状态机测试
    规则单元测试
    权限测试
    集成测试
    迁移测试
    性能和大数据量测试
    代码评审和架构依赖检查

测试结果必须记录输入规格版本、代码提交、依赖版本和环境信息，避免“测试通过”无法重现。

### Step 12：决定最终沉淀类型

完成一个项目后，不要自动把全部代码搬进资产库。按以下规则判断：

| 结果 | 沉淀方式 |
|---|---|
| 只对本项目成立，业务口径高度专属 | `Case + Evidence` |
| 业务流程可复用，但实现方式不同 | `Business Process Asset + Pattern Candidate` |
| 多个项目共享同一组业务步骤和规则 | `Composite` |
| 只有技术栈实现不同，业务规则相同 | `Adapter` |
| 结构稳定、变量有限、可重复生成 | `Template` 或确定性 Codegen |
| 发现失败或危险做法 | `Anti-Pattern` |

**一次成功的代码实现不自动等于通用资产。** 至少经过第二个相似项目验证，才考虑晋级为 Stable Pattern；经过多个项目验证后再提炼模板或生成器。

## 20.6 业务流程资产的标准目录

对于公司特有、没有现成实现模板的业务流程，建议使用独立的 `processes/` 目录，不要把它强行塞进 `patterns/`：

```text
asset-library/
├── processes/                   # 公司业务流程资产
│   └── expense-approval/
│       ├── asset.yaml
│       ├── process.yaml
│       ├── domain-model.yaml
│       ├── state-machine.yaml
│       ├── rules.yaml
│       ├── permissions.yaml
│       ├── data-contract.yaml
│       ├── api-contract.yaml
│       ├── acceptance-scenarios.yaml
│       ├── implementation-profile.yaml
│       ├── evidence/
│       └── CHANGELOG.md
├── patterns/                    # 可复用的解决模式
├── composites/                  # 多个模式的组合
├── adapters/                    # 技术栈、供应商和基础设施适配
├── templates/                   # 结构稳定的生成模板
├── cases/                       # 项目实战记录
└── evidence/                    # 验证证据
```

业务流程资产的核心不是“这次生成了哪些 Java 类”，而是“公司规定的业务行为是什么”。因此它可以被 NestJS、Spring Boot、Go 或其他技术栈实现。

### `asset.yaml` 示例

```yaml
id: process.expense-approval
kind: BusinessProcess
version: 1.0.0
lifecycle: stable
maturity: proven
evidence_level: verified
owner: finance-domain
canonical_spec:
  process: process.yaml
  domain_model: domain-model.yaml
  state_machine: state-machine.yaml
  rules: rules.yaml
  permissions: permissions.yaml
  acceptance: acceptance-scenarios.yaml
supports:
  - adapter.backend.nestjs
  - adapter.backend.spring-boot
```

## 20.7 跨 AI 的一致性：保证什么，不保证什么

必须在团队规范中明确四种一致性：

| 一致性层级 | 是否应保证 | 保证方式 |
|---|---:|---|
| 每一行源码完全相同 | 通常不保证 | 固定代码生成器、模板和工具链 |
| 模块、表、接口、职责边界相同 | 必须保证 | 规范事实源、架构规则和结构检查 |
| 业务行为和异常结果相同 | 必须保证 | 状态机、业务规则、契约测试、验收场景 |
| 后续修改入口和维护方式一致 | 必须保证 | 固定目录边界、依赖方向、变更流程 |

不同 AI 生成的代码可以有不同的变量名或局部写法，但不能出现以下差异：

    一个 AI 把审批状态放在订单表，另一个 AI 另建一套互相冲突的状态
    一个 AI 默认按 UTC 统计，另一个 AI 按本地时间统计
    一个 AI 绕过权限过滤，另一个 AI 正确做数据隔离
    一个 AI 直接修改已支付数据，另一个 AI 通过补偿流程修改
    一个 AI 把外部调用放在事务内，另一个 AI 把它放在事务外而没有补偿

### 一致性校验报告示例

```yaml
consistency_report:
  task: report.monthly-sales
  spec_version: 1.0.0
  implementation:
    ai_provider: example-model
    framework: nestjs
    commit: 4f92a1d
  checks:
    canonical_spec: passed
    domain_model: passed
    database_schema: passed
    api_contract: passed
    state_machine: not_applicable
    business_rules: passed
    permission_rules: passed
    architecture_dependency: passed
    acceptance_scenarios: passed
    source_text:
      status: different
      allowed: true
  decision: acceptable
```

### 如果必须做到源码可重复

对迁移脚本、DTO、OpenAPI、状态机代码、基础 CRUD 等稳定结构，可以使用确定性代码生成：

```text
Canonical Specification
    ↓
固定 Generator 版本
    ↓
固定技术 Adapter 版本
    ↓
固定模板、命名、排序和格式化工具
    ↓
可重复生成的代码
```

并记录：

```yaml
generation:
  generator: tenger-codegen
  generator_version: 1.2.0
  adapter: nestjs
  adapter_version: 1.0.0
  template_version: 3.1.0
  input_hash: sha256:...
  output_hash: sha256:...
  toolchain_lockfile: sha256:...
```

只有输入规格、生成器、模板、Adapter 和工具链都固定时，才有可能保证字节级一致。业务专属的复杂逻辑仍然应由 AI 或开发者实现，但必须受同一份规格和测试约束。

## 20.8 维护时的规格优先原则

后续需求发生变化时，使用以下顺序：

```text
需求变化
→ 修改业务流程规格
→ 生成影响分析
→ 修改领域模型、规则、状态机或权限
→ 评审规格变更
→ 重新生成可生成部分
→ 修改领域和应用层扩展逻辑
→ 执行迁移、契约测试和回归测试
→ 记录新版本和证据
```

禁止只改某个 `if`、某张表或某个接口，就认为业务流程已经完成变更。代码和规格不一致时，必须在 Workflow 中标记为 `SPEC_DRIFT`，直到完成回写或明确记录为临时差异。

---

# 21. 前端资产沉淀案例：跨组件库的上传组件

## 21.1 案例目标

上传是一个典型的前端资产问题。不同项目可能使用：

    Ant Design / Ant Design Vue
    Element Plus
    Naive UI
    MUI 或公司自研组件库
    React、Vue、Angular 等不同框架
    本地服务器、对象存储、分片上传或第三方文件服务

它们的按钮、拖拽区域、进度条和事件 API 不同，但用户真正需要的业务逻辑往往相同：

    选择文件
    → 校验文件
    → 获取上传凭证
    → 上传文件
    → 显示进度
    → 处理成功或失败
    → 支持取消、重试和删除
    → 返回业务可使用的文件引用

因此不能把“Ant Design Upload 代码”直接当成通用上传资产，也不能为每个组件库复制一份完整业务逻辑。正确拆分是：

```text
上传业务规则和生命周期       = Business Process / Pattern
上传状态和校验                = Domain/UI Pattern
组件库事件和视觉实现          = UI Adapter
对象存储、分片、签名接口       = Infrastructure Adapter
项目的文件类型和大小配置       = Project Config / Case
完整的带预览上传区域           = Composite
```

## 21.2 上传逻辑的统一业务契约

先定义与 UI 组件库无关的领域接口：

```ts
export type UploadStatus =
  | 'idle'
  | 'validating'
  | 'signing'
  | 'uploading'
  | 'success'
  | 'error'
  | 'cancelled'

export interface UploadFileInput {
  localId: string
  name: string
  size: number
  mimeType: string
  lastModified?: number
  content: Blob
}

export interface UploadPolicy {
  acceptedMimeTypes: string[]
  maxSizeBytes: number
  maxCount: number
  allowDuplicate: boolean
  allowRetry: boolean
  allowCancel: boolean
}

export interface UploadedFile {
  fileId: string
  objectKey: string
  url?: string
  name: string
  size: number
  mimeType: string
  checksum?: string
}

export interface UploadPort {
  upload(
    input: UploadFileInput,
    onProgress: (percent: number) => void,
    signal?: AbortSignal,
  ): Promise<UploadedFile>
}
```

组件库不应该直接决定业务规则。组件库只是把用户操作转换成统一的 `UploadFileInput`，再把统一状态映射为它自己的 UI。

## 21.3 上传资产的分层

### A. `pattern.frontend.file-upload-policy`

定义文件类型、大小、数量、重名、重复提交和安全校验等规则。它不依赖 React、Vue 或任何组件库。

### B. `pattern.frontend.upload-state-machine`

定义上传生命周期：

```text
IDLE
  → VALIDATING
  → SIGNING
  → UPLOADING
  → SUCCESS

VALIDATING → ERROR
SIGNING    → ERROR
UPLOADING  → ERROR
UPLOADING  → CANCELLED
ERROR      → RETRYING → SIGNING 或 UPLOADING
SUCCESS    → REMOVING → REMOVED
```

状态转换必须有明确触发条件，不能让组件库事件直接修改任意状态。

### C. `method.frontend.upload-validation`

描述校验顺序：

```text
1. 文件数量校验
2. 文件名和路径安全校验
3. MIME 类型和扩展名双重校验
4. 文件大小校验
5. 图片尺寸、视频时长或内容扫描（如适用）
6. 重复文件校验
7. 调用上传凭证接口
```

### D. `adapter.frontend.antd-upload`

负责把 Ant Design 的 `beforeUpload`、`customRequest`、`onChange` 等机制适配到统一上传端口。

### E. `adapter.frontend.element-plus-upload`

负责把 Element Plus 的 `before-upload`、`http-request`、`on-progress`、`on-success`、`on-error` 等机制适配到统一上传端口。

### F. `adapter.storage.object-storage`

负责签名 URL、对象存储、分片、断点续传、取消请求和最终确认等基础设施细节。

### G. `composite.frontend.avatar-upload`

在原子上传能力之上增加头像裁剪、图片预览、尺寸限制和回显。

### H. `composite.frontend.attachment-upload`

在原子上传能力之上增加多文件、排序、删除、批量重试和附件列表。

## 21.4 上传资产目录示例

```text
asset-library/
├── methods/frontend/upload-validation/
│   ├── asset.yaml
│   ├── method.md
│   └── verification.yaml
├── patterns/frontend/file-upload-policy/
│   ├── asset.yaml
│   ├── contract.yaml
│   ├── policy.yaml
│   └── verification.yaml
├── patterns/frontend/upload-state-machine/
│   ├── asset.yaml
│   ├── state-machine.yaml
│   ├── contract.yaml
│   └── verification.yaml
├── adapters/frontend/antd-upload/
│   ├── asset.yaml
│   ├── mapping.yaml
│   ├── implementation.md
│   └── verification.yaml
├── adapters/frontend/element-plus-upload/
│   ├── asset.yaml
│   ├── mapping.yaml
│   ├── implementation.md
│   └── verification.yaml
├── adapters/storage/object-storage/
│   ├── asset.yaml
│   ├── contract.yaml
│   └── implementation.md
└── composites/frontend/attachment-upload/
    ├── asset.yaml
    ├── composition.yaml
    └── verification.yaml
```

## 21.5 统一上传契约示例

```yaml
id: pattern.frontend.file-upload-policy
kind: Pattern
version: 1.0.0
lifecycle: stable
maturity: proven
requires:
  - contract: upload-file-input
  - contract: upload-port
provides:
  - rule: file-type-validation
  - rule: file-size-validation
  - rule: file-count-validation
  - rule: duplicate-file-policy
invariants:
  - invalid files never enter UPLOADING
  - upload progress is between 0 and 100
  - successful upload must return a stable fileId or objectKey
  - cancelled upload must not be reported as success
  - UI component cannot bypass policy validation
```

上传流程组合契约示例：

```yaml
id: composite.frontend.attachment-upload
kind: Composite
version: 1.0.0
requires:
  - pattern.frontend.file-upload-policy@1.x
  - pattern.frontend.upload-state-machine@1.x
  - adapter.storage.object-storage@1.x
  - ui-adapter: project-selected
ordering:
  - file-upload-policy before upload-state-machine
  - upload-state-machine before ui-adapter
  - object-storage implements upload-port
provides:
  - multi-file-upload
  - progress-display
  - retry
  - cancel
  - remove
```

## 21.6 项目 A：Vue 3 + Element Plus

### 项目差异配置

```yaml
project: crm-web
upload:
  component_adapter: adapter.frontend.element-plus-upload@1.0.0
  storage_adapter: adapter.storage.object-storage@1.2.0
  policy:
    accepted_mime_types: [image/png, image/jpeg, application/pdf]
    max_size_bytes: 10485760
    max_count: 5
    allow_duplicate: false
    allow_retry: true
    allow_cancel: true
  purpose: customer-attachment
```

### AI 的执行步骤

```text
1. 读取统一上传契约和项目策略
2. 选择 Element Plus Adapter
3. 选择对象存储 Adapter
4. 生成 useUploadController 或等价应用层逻辑
5. 通过 http-request 接入统一 UploadPort
6. 通过 on-progress/on-success/on-error 映射状态
7. 生成组件级测试和验收场景
```

### 边界要求

`before-upload` 只负责进入统一校验入口，不能在组件内部另写一套文件类型或大小判断；`http-request` 只负责调用 `UploadPort`，不能在 UI 组件里拼接签名、处理重试或决定业务成功。

## 21.7 项目 B：React + Ant Design

### 项目差异配置

```yaml
project: finance-web
upload:
  component_adapter: adapter.frontend.antd-upload@1.1.0
  storage_adapter: adapter.storage.object-storage@1.2.0
  policy:
    accepted_mime_types: [application/pdf, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet]
    max_size_bytes: 52428800
    max_count: 20
    allow_duplicate: false
    allow_retry: true
    allow_cancel: true
  purpose: invoice-attachment
```

### 必须保持一致的部分

虽然 Ant Design 使用 `beforeUpload`、`customRequest` 和 `onChange`，而 Element Plus 使用另一组事件，但以下内容必须保持同一份契约：

    文件校验顺序
    错误分类和错误码
    上传状态转换
    进度含义
    取消和重试语义
    成功返回值
    删除是否删除远端对象
    权限和审计要求

### 允许不同的部分

    JSX 与 Vue SFC 的写法
    组件库的视觉属性和插槽
    事件名称及事件参数形状
    组件库特有的 loading、message 和样式 API
    框架生命周期和响应式实现

这些差异属于 Adapter，不应污染上传业务 Pattern。

## 21.8 上传组件的组合顺序和契约

推荐的调用顺序为：

```text
UI Adapter 接收文件
    ↓
Upload Policy 校验
    ↓
Upload State Machine 进入 SIGNING
    ↓
Storage Adapter 获取上传凭证
    ↓
UploadPort 执行上传
    ↓
State Machine 更新进度
    ↓
Storage Adapter 确认文件
    ↓
返回 UploadedFile
    ↓
UI Adapter 展示成功或错误
```

禁止以下组合：

```text
UI 组件直接调用数据库或对象存储管理 API
UI 组件绕过 Policy 直接发送文件
Storage Adapter 直接修改 UI loading 状态
重试逻辑同时存在于 UI、Hook 和 Storage Adapter 三处
错误码在每个组件库 Adapter 中各自定义一套
```

## 21.9 上传组件的质量门禁

### 契约门禁

```text
[ ] 不同组件库都实现相同的 UploadPort
[ ] 所有输入和输出类型有统一定义
[ ] 成功、失败、取消、重试状态明确
[ ] 进度范围和进度来源明确
[ ] 文件 ID、对象 Key 和 URL 的含义明确
```

### 安全门禁

```text
[ ] MIME 和扩展名均校验
[ ] 文件大小和数量有限制
[ ] 文件名不会直接拼入路径或 SQL
[ ] 服务端重新校验，不能只依赖前端
[ ] 上传凭证有过期时间和最小权限
[ ] 敏感文件访问需要授权或临时 URL
[ ] 取消、删除和失败清理策略明确
```

### 行为测试门禁

至少覆盖：

    正常单文件上传
    正常多文件上传
    类型不允许
    文件超限
    数量超限
    重复文件
    获取签名失败
    上传中断
    用户取消
    自动重试和手动重试
    上传成功但确认失败
    删除远端文件失败
    刷新页面后的回显
    组件库事件顺序变化

同一组场景应同时运行在 Element Plus Adapter 和 Ant Design Adapter 上。测试比较的是状态、结果和错误语义，而不是组件库的具体 DOM 文本。

## 21.10 上传资产的去重与版本规则

### 不应该新建完整上传资产的情况

以下只是项目配置，不应复制一套新组件：

    PDF 改成图片
    10MB 改成 50MB
    单文件改成最多 20 个
    上传用途从头像改成附件
    成功后跳转不同页面

### 应该新增或更新资产的情况

| 差异 | 处理方式 |
|---|---|
| Element Plus 与 Ant Design API 不同 | 新增两个 UI Adapter |
| OSS 与 S3 签名流程不同 | 新增 Storage Adapter |
| 普通上传变为分片断点续传 | 更新/新增上传传输 Pattern |
| 头像需要裁剪和尺寸检查 | 新增 `avatar-upload` Composite |
| 业务规定上传后必须人工审核 | 新增业务流程 Pattern 或 Composite |
| 只有某项目的附件字段不同 | 保留为项目配置和 Case |

### 版本兼容示例

```yaml
compatibility:
  policy: pattern.frontend.file-upload-policy@1.x
  state_machine: pattern.frontend.upload-state-machine@1.x
  component_adapter:
    - adapter.frontend.element-plus-upload@1.x
    - adapter.frontend.antd-upload@1.x
  storage_adapter: adapter.storage.object-storage@1.x
```

如果上传策略增加“必须病毒扫描后才算成功”，这是业务不变量变化，应升级 Pattern 版本，并同步更新状态机、验收场景和所有 Adapter 的测试，而不是只在某个项目中加一段隐藏逻辑。

## 21.11 前端资产与现有 Skill 的接入点

```text
PRD-Design
    识别上传用途、数量、文件类型、大小、权限和后续业务动作

Prototype-Design / UI-UX-Design
    选择展示形态，但不得重新定义上传业务契约

Frontend-Tech-Design
    检索 Policy、State Machine、UI Adapter 和 Storage Adapter

Frontend-Dev
    按组合契约实现组件和页面接入

Code-Review
    检查是否绕过统一契约、是否重复实现校验和状态机

Testing
    执行跨 Adapter 的统一场景和项目特有场景

Workflow
    在 Adapter、Pattern、Composite 和 Case 之间推进状态，并阻止未验证资产进入 Stable
```

## 21.12 前端案例的最终沉淀结果

两个项目完成后，资产库不应出现：

```text
crm-element-plus-upload-full-copy
finance-antd-upload-full-copy
```

而应形成：

```text
pattern.frontend.file-upload-policy
pattern.frontend.upload-state-machine
method.frontend.upload-validation
adapter.frontend.element-plus-upload
adapter.frontend.antd-upload
adapter.storage.object-storage
composite.frontend.attachment-upload
case.crm.customer-attachment-upload
case.finance.invoice-attachment-upload
evidence.frontend.upload-cross-adapter-compatibility
```

这样沉淀的是“同一上传逻辑在不同组件库中的稳定契约和适配方式”，而不是两份以后难以同步的复制代码。

---

# 22. 对资产缺失场景的补充验收标准

- [ ] 检索不到资产时会进入 `ASSET_MISSING`，不会直接跳到代码生成。
- [ ] 业务事实、实现方式和项目配置被分层记录。
- [ ] 有唯一的业务规格事实源，产品、后端、前端和测试引用同一版本。
- [ ] 未确认的业务规则被标记为 `OPEN_QUESTION` 或 `ASSUMPTION`。
- [ ] 业务规格通过结构、状态机、规则、权限、数据和行为检查。
- [ ] AI 先输出实现计划，再分阶段实现代码。
- [ ] 不同 AI 的结果至少通过规格、结构、契约、行为和架构五层一致性检查。
- [ ] 需要源码完全一致的部分使用固定生成器和锁定工具链。
- [ ] 资产缺失的首次实现至少沉淀为 Case/Evidence。
- [ ] 经过多个项目验证后，才将稳定共性提炼为 Pattern、Composite 或 Adapter。
- [ ] 前端上传逻辑按业务契约、状态机、组件库 Adapter 和存储 Adapter 拆分。
- [ ] 不同组件库运行相同的业务场景测试，比较行为结果而不是 DOM 文本。
- [ ] 业务规则变化会先修改规格，再修改代码和测试。

# 23. 更新后的最终原则

```text
没有模板，不等于没有方法。
没有代码资产，不等于没有业务资产。

资产缺失时，先把业务流程规格化，再把规格变成可执行的实现计划。
AI 可以自主写实现代码，但不能静默发明关键业务规则。

业务 Pattern 负责“做什么”和“不变量是什么”。
技术 Adapter 负责“在当前技术栈中怎么做”。
项目配置负责“本项目的参数是什么”。
Case/Evidence 负责“这次实际发生了什么、是否验证过”。

同一业务交给不同 AI，追求的不是自然产生相同源码，
而是由同一事实源、同一契约、同一架构边界和同一验收标准，
约束出相同的结构、行为和维护方式。

当某部分需要高度重复且可预测时，再使用确定性生成器，
把它从“AI 自由实现”升级为“规格驱动生成”。
```

# 24. 资产维护总纲：有资产走资产，没资产定规范

## 24.1 两条正式工程规则

从现在开始，所有开发任务统一遵循两条规则：

### 规则一：有资产，走资产

```text
需求识别
→ 检索资产
→ 评估匹配度
→ 锁定资产版本
→ 根据契约组合
→ 通过 Adapter 接入当前技术栈
→ 按验证规范开发
→ 回写使用记录和证据
```

“走资产”不等于复制资产代码，而是：

    使用已批准的资产版本
    遵守资产的 requires/provides/conflicts/ordering 契约
    只通过规定的配置点和扩展点适配项目差异
    发现缺陷时优先修复源资产，而不是在项目中打补丁
    将本次使用结果、偏差和证据回写到资产库

### 规则二：没资产，定规范

```text
检索确认缺失
→ 建立业务流程和领域规范
→ 评审业务规则和技术边界
→ 按规范实现
→ 记录 Case/Evidence
→ 多项目验证后提炼新资产
```

“定规范”不等于一开始就设计一个万能模板，而是先保证本次业务有唯一事实源、明确边界和可验证行为。只有发现多个项目之间存在稳定共性，才把共性提炼为 Pattern、Composite、Adapter 或 Template。

## 24.2 资产的完整生命周期

资产不是提交到 Git 后就完成了。完整生命周期包括：

```text
识别
  ↓
设计
  ↓
创建
  ↓
评审
  ↓
发布
  ↓
项目采用
  ↓
使用反馈
  ↓
缺陷修复/兼容迭代
  ↓
多项目验证
  ↓
提炼或拆分
  ↓
版本升级
  ↓
迁移
  ↓
弃用
  ↓
归档
```

每个阶段都必须有责任人、输入、输出和门禁。资产库的维护本质上是一个持续运营的产品，而不是一个静态的代码文件夹。

## 24.3 资产维护的五个对象

维护时不能只维护资产正文，还要同时维护以下五个对象：

| 对象 | 说明 | 典型文件 |
|---|---|---|
| 事实 | 资产解决什么问题，业务和技术边界是什么 | `asset.yaml`、`README.md` |
| 契约 | 输入、输出、前置条件、不变量和组合关系 | `contract.yaml` |
| 实现 | 参考代码、脚本、模板或 Adapter | `src/`、`scripts/`、`templates/` |
| 验证 | 如何证明资产能工作、不能做什么 | `verification.yaml`、测试 |
| 影响关系 | 被哪些项目使用、哪些资产依赖它、如何迁移 | `registry.yaml`、`usage/`、`migrations/` |

任何一个对象缺失，资产都可能出现“看起来可以复用、实际无法维护”的问题。

---

# 25. 从设计阶段开始维护资产

## 25.1 设计阶段的目标：决定复用、规范化还是项目专属

在 PRD、原型和技术方案阶段，就要完成第一次资产决策，不能等代码写完后才判断是否沉淀。

每个需求至少要回答：

```text
1. 是否命中已有资产？
2. 命中的资产是业务资产、工程资产还是 Adapter？
3. 本项目与资产的差异属于配置、组合、适配还是业务规则变化？
4. 如果没有命中资产，是否需要形成新的业务规范？
5. 哪些内容必须保持统一，哪些内容允许项目自定义？
6. 本次实现完成后需要回写哪些证据？
```

## 25.2 设计阶段的资产决策树

```text
开始
  ↓
是否存在候选资产？
  ├── 否 → ASSET_MISSING → 定义业务规范 → 进入规格评审
  └── 是
        ↓
      是否满足业务语义和不变量？
        ├── 否 → 不能强行复用 → 定义规范或新增 Pattern
        └── 是
              ↓
            差异是什么？
              ├── 参数不同       → Project Config
              ├── 组合方式不同   → Composite
              ├── 技术栈不同     → Adapter
              ├── 业务规则扩展   → Pattern 版本/新 Pattern
              ├── 结构固定       → Template/Codegen
              └── 仅项目偶发     → Case
```

## 25.3 设计阶段必须生成的文件

### `asset-needs.yaml`

记录本次需求需要哪些能力：

```yaml
request: project-a.expense-approval
created_at: 2026-09-17
needs:
  - capability: identity.authentication
    required: true
    candidates:
      - pattern.authentication.phone-otp-login@1.x
  - capability: approval.state-machine
    required: true
    candidates: []
    status: asset_missing
    next_action: define_business_process_spec
  - capability: file-upload
    required: false
    candidates:
      - composite.frontend.attachment-upload@1.x
```

### `asset-decision.yaml`

记录为什么采用、拒绝或新增资产：

```yaml
request: project-a.expense-approval
decisions:
  - capability: identity.authentication
    decision: reuse
    selected: pattern.authentication.phone-otp-login@1.2.0
    reason: business_semantics_match
  - capability: approval.state-machine
    decision: define_spec
    reason: no_existing_asset_and_company_specific_rule
  - capability: file-upload
    decision: reuse_and_adapt
    selected: composite.frontend.attachment-upload@1.1.0
    adapter: adapter.frontend.element-plus-upload@1.0.0
```

### `implementation-profile.yaml`

记录当前项目的实现参数，而不是复制一套资产：

```yaml
project: project-a
profile_version: 1.0.0
backend:
  framework: nestjs
  database: postgresql
frontend:
  framework: vue3
  component_library: element-plus
business:
  timezone: Asia/Shanghai
  tenant_mode: organization
assets:
  authentication: pattern.authentication.phone-otp-login@1.2.0
  upload: adapter.frontend.element-plus-upload@1.0.0
```

## 25.4 设计评审中的资产门禁

PRD 评审需要检查业务目标和规则是否与已有资产冲突；技术方案评审需要检查资产组合和实现边界；原型评审需要检查交互是否绕开已有行为契约。

设计阶段禁止：

```text
未检索资产就直接设计一套新实现
为了复用资产而改变真实业务规则
把组件库 API 当成业务契约
把某个项目的临时约定写进通用 Pattern
用“以后再整理”为理由省略规范和决策记录
```

---

# 26. 开发阶段的资产使用与回写

## 26.1 项目使用资产时必须“引用”，不能“复制即分叉”

项目应通过清单引用资产版本：

```yaml
project: crm-web
asset_usage:
  - asset_id: pattern.frontend.file-upload-policy
    version: 1.0.0
    role: file_validation
  - asset_id: pattern.frontend.upload-state-machine
    version: 1.0.0
    role: upload_lifecycle
  - asset_id: adapter.frontend.element-plus-upload
    version: 1.0.0
    role: component_library_adapter
```

项目代码可以通过依赖、生成、Adapter 或约定目录使用资产，但不能把资产复制到项目后独立演化并继续声称它仍然受资产库管理。

如果确实需要项目专属改动，必须明确选择一种方式：

```text
配置扩展
Adapter 扩展
Composite 组合
提交资产变更
记录为项目专属 Case
```

## 26.2 AI 开发时的固定输出顺序

`Backend-Dev` 和 `Frontend-Dev` 在执行任务时应要求 AI 按以下顺序输出：

```text
1. 本次使用的资产及版本
2. 资产契约和关键不变量
3. 项目差异和配置项
4. 不允许修改的边界
5. 实现计划
6. 代码变更
7. 测试和验证结果
8. 发现的资产缺口或资产缺陷
9. 是否需要提交资产变更
```

AI 不应只返回代码。没有资产使用清单和验证结果，就不能认为本次开发完成了资产闭环。

## 26.3 开发阶段的“偏差记录”

实际开发中，项目可能遇到资产与真实环境不完全匹配的情况，必须记录偏差：

```yaml
deviation:
  id: deviation.crm-upload-001
  project: crm-web
  asset: composite.frontend.attachment-upload@1.1.0
  type: adapter_gap
  description: 当前对象存储需要二次确认接口，现有 Adapter 只支持一次确认
  impact: success_state_cannot_be_finalized
  temporary_solution: project_local_adapter_extension
  upstream_action: create_adapter_change_proposal
  owner: frontend-platform
  due: 2026-09-24
```

偏差记录有三个作用：

    防止临时方案被误认为标准方案
    让资产维护者知道真实项目需求
    支持多个项目的共性分析和后续提炼

## 26.4 开发完成时必须回写的最小信息

每次使用资产的项目，都必须回写：

```yaml
usage_record:
  project: crm-web
  asset: pattern.frontend.file-upload-policy
  version: 1.0.0
  used_at: 2026-09-17
  result: success
  scenarios_passed:
    - single-image-upload
    - invalid-mime-type
    - oversized-file
  deviations: []
  defects: []
  performance:
    p95_upload_start_ms: 320
  recommendation: keep
```

如果某项没有数据，应写明 `not_measured`，不能留空。

---

# 27. 多个项目使用后的资产沉淀流程

## 27.1 不能把多个项目的代码简单合并

多个项目使用后，最容易出现两种错误：

### 错误一：每个项目都复制一份

```text
项目 A 登录代码
项目 B 登录代码
项目 C 登录代码
```

短期看每个项目都能运行，长期会造成：

    安全修复无法同步
    业务规则逐渐分叉
    同一个概念出现多个实现
    AI 检索到大量相似但互相冲突的资产
    维护者不知道哪个版本是事实源

### 错误二：过早抽象成万能资产

第一个项目完成后，就把全部代码抽成“通用平台组件”，会导致：

    项目特有规则被硬编码进通用资产
    参数数量不断增加
    资产契约难以理解
    每个项目都需要特殊开关
    修改一个项目影响所有使用者

正确做法是：**项目先独立验证，多个项目对比差异，再提炼稳定共性。**

## 27.2 多项目沉淀的六步法

### 第一步：每个项目独立记录事实

每个项目都必须保留自己的：

```text
asset-usage.yaml
project-config.yaml
case.yaml
evidence/
deviation.yaml
```

项目记录不能被资产库的通用描述替代，因为项目中的真实约束和例外情况同样是重要证据。

### 第二步：对项目使用结果做差异矩阵

示例：三个项目都使用上传能力：

| 能力维度 | 项目 A：客户附件 | 项目 B：发票附件 | 项目 C：头像上传 |
|---|---|---|---|
| 文件数量 | 多文件 | 多文件 | 单文件 |
| 文件类型 | 图片/PDF | PDF/Excel | 图片 |
| 存储方式 | OSS | OSS | OSS |
| 是否需要裁剪 | 否 | 否 | 是 |
| 是否需要人工审核 | 否 | 是 | 否 |
| 删除语义 | 删除引用和对象 | 仅删除引用 | 替换头像 |
| 业务状态 | 上传即成功 | 病毒扫描后成功 | 裁剪后成功 |

从矩阵可以看出：

    文件校验、上传进度、取消和重试是稳定共性
    头像裁剪是 Composite
    发票人工审核是新的业务流程扩展
    删除语义不能简单统一为一个默认实现

### 第三步：提取“稳定不变量”

只有在多个项目中都成立的内容，才进入通用 Pattern：

```text
稳定不变量：
- 非法文件不能进入上传阶段
- 取消后不能报告为成功
- 成功必须返回稳定文件标识
- 上传进度范围为 0～100
- 服务端必须再次校验文件
```

不稳定的内容进入：

```text
项目配置
Adapter
Composite
业务流程扩展
Case
```

### 第四步：建立资产变更提案

任何从项目回写资产库的行为，都通过 `Asset Change Proposal`，而不是直接修改 Stable 资产：

```yaml
proposal:
  id: acp.frontend-upload.0003
  type: extract_common_pattern
  source_projects:
    - crm-web
    - finance-web
    - hr-web
  target_asset: pattern.frontend.file-upload-policy
  current_version: 1.0.0
  proposed_version: 1.1.0
  change:
    add:
      - server-side-validation-required
      - checksum-verification
    preserve:
      - existing_upload_port
      - existing_success_contract
  compatibility: backward_compatible
  evidence:
    - case.crm.customer-attachment-upload@1.0.0
    - case.finance.invoice-attachment-upload@1.0.0
    - evidence.frontend.upload-cross-adapter-compatibility@1.0.0
  migration_required: false
  reviewers:
    - frontend-platform-owner
    - security-owner
    - testing-owner
```

### 第五步：资产评审和验证

资产评审至少检查：

```text
[ ] 提取的内容是否真的跨项目成立
[ ] 是否把项目特殊规则误提取为通用规则
[ ] 是否破坏原有 requires/provides 契约
[ ] 是否影响已有项目
[ ] 是否需要迁移或兼容层
[ ] 是否补充了新的正例、反例和失败证据
[ ] 是否更新了文档、示例、脚本和测试
[ ] 是否有明确 owner 和回滚方案
```

### 第六步：发布、通知和项目迁移

资产变更合并后，必须：

```text
生成 CHANGELOG
→ 更新 registry
→ 通知受影响项目
→ 创建迁移任务
→ 按项目优先级升级
→ 回写迁移证据
→ 关闭旧版本使用记录
```

发布资产新版本不等于所有项目已经升级。资产库必须能区分：

    已发布版本
    项目已采用版本
    项目待升级版本
    项目暂缓升级原因

## 27.3 多项目沉淀的晋级规则

建议采用以下晋级标准：

| 级别 | 条件 | 允许被如何使用 |
|---|---|---|
| `Candidate` | 仅有设计或一次实现 | 只能试用，必须显式声明风险 |
| `Proven` | 至少一个真实项目成功并有证据 | 可被评估后采用 |
| `Stable` | 至少两个不同场景验证，契约稳定 | 可进入默认检索结果 |
| `Standard` | 多项目使用、有人维护、有自动化验证 | 可作为组织级标准 |
| `Deprecated` | 有替代资产，不建议新项目使用 | 只允许存量维护 |
| `Retired` | 无存量项目或已完成迁移 | 不再被检索和采用 |

“两个项目”只是最低门槛，不是绝对规则。安全认证、支付、权限等高风险资产，还需要更高等级的审查、回归和运行证据。

---

# 28. 资产维护、缺陷修复和版本迭代

## 28.1 发现问题时先判断问题属于哪里

项目出现问题后，不要直接修改项目代码，先判断根因：

```text
问题发生
  ↓
是项目参数错误吗？
  ├── 是 → 修复项目配置/Case
  └── 否
        ↓
是 Adapter 实现错误吗？
  ├── 是 → 修复 Adapter，评估受影响项目
  └── 否
        ↓
是 Pattern 契约或规则错误吗？
  ├── 是 → 变更 Pattern，执行兼容性和迁移流程
  └── 否
        ↓
是业务规格错误或需求变化吗？
  ├── 是 → 更新 Business Process Asset
  └── 否 → 新增 Anti-Pattern 或基础设施问题记录
```

## 28.2 缺陷修复的三种路径

### 路径 A：项目局部修复

适用于：

    项目配置写错
    项目误用了资产
    项目拥有特殊业务规则
    资产本身没有缺陷

处理方式：只修改项目，并记录 Case，不修改资产库。

### 路径 B：资产向后兼容修复

适用于：

    资产实现有明确缺陷
    不改变输入输出契约
    不改变业务语义
    已有项目可以无感升级

处理方式：发布 Patch 版本，运行所有关联项目的回归测试。

### 路径 C：资产契约变更

适用于：

    业务规则发生变化
    输入输出结构变化
    状态机增加或删除状态
    权限语义变化
    事务边界变化
    旧行为存在安全或合规风险

处理方式：发布 Minor 或 Major 版本，提供迁移说明，不允许静默覆盖旧版本。

## 28.3 版本号规则

推荐使用语义化版本：

```text
MAJOR.MINOR.PATCH
```

### Patch

不改变契约的修复：

```text
1.2.0 → 1.2.1
```

例如：修复上传进度计算、补充空值处理、优化错误提示，但不改变状态和成功结果。

### Minor

向后兼容的能力增加：

```text
1.2.0 → 1.3.0
```

例如：增加可选的 checksum 字段、增加可选重试策略，但旧项目不升级也能继续运行。

### Major

不兼容变更：

```text
1.2.0 → 2.0.0
```

例如：成功返回值结构改变、状态定义改变、删除行为改变、权限规则收紧或调用顺序改变。

## 28.4 资产变更影响分析

每次资产变更都必须查询：

```text
1. 哪些资产依赖它？
2. 哪些项目正在使用它？
3. 哪些 Adapter 需要同步修改？
4. 哪些测试和验收场景会受影响？
5. 是否需要数据库迁移或数据修复？
6. 是否存在安全、合规和性能影响？
7. 是否可以灰度发布和回滚？
```

建议在 `registry.yaml` 中记录反向依赖：

```yaml
asset: pattern.frontend.upload-state-machine@1.0.0
used_by:
  - composite.frontend.attachment-upload@1.1.0
  - composite.frontend.avatar-upload@1.0.0
projects:
  - crm-web@main
  - finance-web@release/2026-q3
required_tests:
  - upload-state-transition-suite
  - adapter-cross-framework-suite
```

## 28.5 资产迁移文件

发生不兼容变更时，资产包必须提供迁移说明：

```text
migrations/
└── 1.x-to-2.x.md
```

迁移说明至少包括：

```text
变更原因
影响范围
旧行为与新行为对比
项目代码迁移步骤
配置迁移步骤
数据库/数据迁移步骤
回归测试要求
灰度与回滚方案
无法迁移的特殊情况
```

## 28.6 资产弃用和归档

资产不能因为“暂时没人使用”就直接删除。弃用流程为：

```text
Stable
  ↓
Deprecated
  ↓
Freeze（只修复高风险问题）
  ↓
迁移存量项目
  ↓
Retired
  ↓
Archive
```

`Deprecated` 资产必须在检索结果中显示：

```yaml
lifecycle: deprecated
replacement: pattern.frontend.file-upload-policy@2.0.0
new_project_allowed: false
sunset_date: 2027-03-31
migration_guide: migrations/1.x-to-2.x.md
```

---

# 29. 资产库的组织、权限和责任分工

## 29.1 资产库不是所有人随意修改的共享目录

资产需要明确的治理角色：

| 角色 | 责任 |
|---|---|
| 资产提出人 | 从项目中发现需求或共性，提交提案 |
| 业务 Owner | 确认业务语义、规则和边界 |
| 资产 Owner | 维护资产契约、版本、文档和发布 |
| Adapter Owner | 维护具体技术栈或组件库适配 |
| 测试 Owner | 维护验证场景、自动化测试和证据 |
| 安全/合规 Owner | 审核权限、敏感数据和安全风险 |
| Workflow Owner | 维护状态机、门禁和调度规则 |
| 项目负责人 | 决定项目采用、迁移和上线风险 |

同一个人可以承担多个角色，但高风险资产不能由单人自行设计、批准和发布。

## 29.2 资产修改权限

建议分为三类权限：

```text
使用权限：可以检索和引用已发布资产
提案权限：可以提交新增、修改、弃用提案
发布权限：只能由资产 Owner 和指定评审人批准
```

禁止：

```text
直接修改 Stable 资产正文并跳过评审
删除仍被项目使用的资产
修改版本号但不记录 CHANGELOG
只修改代码不修改契约和测试
只修改文档不更新真实验证结果
```

## 29.3 Asset Change Proposal 的统一模板

```yaml
proposal:
  id: acp.authentication.0012
  type: bugfix | enhancement | breaking_change | deprecate | extract | split
  submitted_by: developer-a
  submitted_at: 2026-09-17
  target:
    asset_id: pattern.authentication.session-management
    current_version: 1.3.0
  problem:
    summary: refresh token rotation is not atomic under concurrent requests
    affected_projects:
      - project-a
      - project-b
  proposed_change:
    behavior: rotate token inside a transaction and reject reused token
    contract_change: true
  version_plan:
    next_version: 2.0.0
    migration_required: true
  validation:
    required_scenarios:
      - concurrent-refresh
      - reused-token-rejection
      - logout-after-rotation
    security_review: required
  approvals:
    business_owner: pending
    asset_owner: pending
    test_owner: pending
```

## 29.4 资产发布包的最小组成

一个可以被其他项目采用的资产版本，至少应包含：

```text
asset.yaml
README.md
contract.yaml
verification.yaml
CHANGELOG.md
examples/
references/
```

有实现代码时还应包含：

```text
src/ 或 templates/
scripts/
tests/
fixtures/
migrations/（如适用）
```

没有这些内容的代码片段只能作为聊天记录、草稿或 Case，不应直接标记为 Stable Asset。

---

# 30. 资产维护与现有 Skill / Workflow 的完整衔接

## 30.1 设计阶段

```text
PRD-Design
  → 识别业务能力、规则、角色、边界
  → 生成 asset-needs.yaml

PRD-Review
  → 确认业务事实和未决问题
  → 检查是否错误复用已有资产

Prototype-Design / UI-UX-Design
  → 产出交互设计和组件选择
  → 不改变业务行为契约

Prototype-Review / UI-UX-Review
  → 检查设计是否覆盖资产规定的状态和异常
```

## 30.2 技术方案阶段

```text
Backend-Tech-Design / Frontend-Tech-Design
  → 检索资产
  → 判断复用、组合、适配或定规范
  → 生成 asset-decision.yaml
  → 输出 implementation-profile.yaml
  → 形成组合图和影响分析

Tech-Review
  → 检查模块边界、依赖方向、Adapter 和迁移方案
```

## 30.3 开发与验证阶段

```text
Backend-Dev / Frontend-Dev
  → 读取已锁定的资产版本
  → 先输出实现计划
  → 按契约和边界实现
  → 记录 deviation

Code-Review
  → 检查是否复制资产、绕过契约或静默发明规则

Testing
  → 执行资产通用测试、项目特有测试和跨 Adapter 测试
  → 生成 Evidence
```

## 30.4 维护和迭代阶段

```text
Bug-Fix
  → 判断问题属于项目、Adapter、Pattern、业务规格还是基础设施
  → 选择正确修复路径
  → 创建 Asset Change Proposal

Workflow
  → 管理资产状态、评审门禁、版本发布、迁移和弃用

Skill-Optimizer
  → 根据资产使用数据、失败案例和重复问题优化 Skill
```

## 30.5 推荐的统一状态机

项目任务和资产变更可以通过两个相互关联的状态机管理：

### 项目任务状态

```text
REQUIREMENT
→ ASSET_DISCOVERY
→ ASSET_SELECTED 或 SPEC_DEFINED
→ TECH_DESIGN
→ IMPLEMENTATION
→ REVIEW
→ TESTING
→ RELEASED
→ USAGE_RECORDED
```

### 资产变更状态

```text
DRAFT
→ REVIEWING
→ VERIFIED
→ RELEASE_CANDIDATE
→ RELEASED
→ ADOPTED
→ EVOLVING
→ DEPRECATED
→ RETIRED
```

项目任务中的 `USAGE_RECORDED` 是资产库迭代的输入；资产变更中的 `RELEASED` 不代表项目已经完成采用，二者不能混为一谈。

---

# 31. 两个完整的多项目维护案例

## 31.1 登录资产的多项目演进

### 项目 A：手机号 + OTP

第一次实现时：

```text
复用：identity-model、session-management、audit-logging
新增规范：phone-otp-login 的业务流程和安全规则
沉淀：Case + Evidence
```

此时不直接把完整登录代码标记为通用 Pattern，而是记录：

```text
OTP 有效期
验证码错误次数
重发间隔
设备绑定规则
登录失败锁定规则
Session 创建规则
审计字段
```

### 项目 B：账号密码 + 微信登录

对比项目 A：

```text
保持不变：账户主体、Session、审计和退出机制
新增能力：password-login、oauth-login
新增差异：账号绑定和首次登录建档
```

此时提炼出：

```text
pattern.authentication.identity-model
pattern.authentication.password-login
pattern.authentication.oauth-login
pattern.authentication.account-linking
pattern.authentication.session-management
```

### 项目 C：Java/Spring Security

项目 C 不复制项目 A 或项目 B 的业务代码，而是：

```text
复用业务 Pattern
新增 adapter.backend.spring-security.authentication
记录 Spring 的过滤器、Provider、Session 和异常映射方式
```

三个项目完成后，资产库维护的是：

    认证业务不变量
    登录方式 Pattern
    账号绑定流程
    Session 契约
    NestJS Adapter
    Spring Security Adapter
    项目差异和迁移证据

如果项目 C 发现 Spring Adapter 的并发刷新存在缺陷，应修复 Adapter 并评估所有采用该 Adapter 的项目；不能只在项目 C 中改一段代码后结束。

## 31.2 上传资产的多项目演进

### 项目 A：客户附件

沉淀：

```text
文件类型、大小和数量校验
对象存储上传
进度、取消和重试
```

### 项目 B：发票附件

发现：

```text
上传成功后还需要病毒扫描和人工审核
```

这不是简单增加一个 `isInvoice` 参数，而是新增或扩展业务状态：

```text
UPLOADED → SCANNING → PENDING_REVIEW → APPROVED / REJECTED
```

该流程应作为新的业务 Composite 或 Process Asset 管理，不能污染所有普通附件上传。

### 项目 C：头像上传

发现：

```text
需要裁剪、尺寸检查和替换旧头像
```

这属于：

```text
composite.frontend.avatar-upload
```

它复用基础上传能力，但拥有独立的裁剪和替换规则。

最终形成的不是一个参数无限膨胀的万能组件，而是：

```text
基础上传 Pattern
+ 组件库 Adapter
+ 存储 Adapter
+ 附件 Composite
+ 发票审核 Process/Composite
+ 头像 Composite
```

---

# 32. 资产库的持续运营指标

没有指标，就无法判断资产库是在产生价值还是在制造冗余。建议每月统计：

## 32.1 使用指标

```text
资产被项目引用次数
各资产版本的实际使用项目数
资产检索命中率
资产命中后最终采用率
资产复用节省的开发时间
```

## 32.2 质量指标

```text
资产使用后的缺陷率
资产相关线上事故数
资产回滚次数
资产契约测试通过率
不同 Adapter 的行为一致性
未验证资产被误用的次数
```

## 32.3 维护指标

```text
资产变更平均评审时长
从项目发现问题到源资产修复的时间
资产版本迁移完成率
Deprecated 资产剩余项目数
长期未维护资产数量
项目本地分叉数量
```

## 32.4 健康度判断

以下情况说明资产库正在恶化：

```text
同一能力出现大量相似资产
项目大量复制资产而非引用版本
Stable 资产长期没有验证和实际使用
资产变更没有影响分析
项目修复很少回写源资产
一个资产包含大量项目专属开关
AI 检索到多个语义冲突的“标准答案”
```

出现这些情况时，应执行资产整顿：合并、拆分、降级、弃用或删除无价值资产。

---

# 33. 资产维护中的常见错误和处理方式

| 错误 | 后果 | 正确处理 |
|---|---|---|
| 资产一旦建立就不再维护 | 资产逐渐失真 | 每次使用都回写证据和版本 |
| 多项目直接复制代码 | 安全和缺陷无法同步 | 使用引用、Adapter 和变更提案 |
| 第一个项目后就抽象成万能模板 | 资产参数爆炸 | 先 Case，再比较多个项目后提炼 |
| 只维护代码不维护契约 | AI 不知道边界 | 代码、契约、测试同步变更 |
| 只改项目不修源资产 | 同类项目重复踩坑 | 先判断根因，再选择修复层级 |
| 版本号不变直接覆盖 | 无法回滚和审计 | 语义化版本和 CHANGELOG |
| Deprecated 资产直接删除 | 存量项目失效 | 迁移、冻结、归档 |
| 失败案例不沉淀 | AI 继续重复错误 | 记录 Anti-Pattern 和 Evidence |
| 用组件库 API 代表业务逻辑 | 技术栈耦合 | 业务 Pattern 与 Adapter 分离 |
| 认为线上运行久就是稳定资产 | 错误设计被固化 | 以验证证据和契约质量判断成熟度 |

---

# 34. 资产维护的最终闭环

每个项目结束时，必须执行以下闭环：

```text
项目需求
  ↓
资产检索或业务规范定义
  ↓
设计评审
  ↓
锁定版本或创建规范版本
  ↓
开发实现
  ↓
代码评审和测试
  ↓
上线和运行观察
  ↓
记录 Usage / Case / Evidence / Deviation
  ↓
分析多个项目之间的共性和差异
  ↓
提交 Asset Change Proposal
  ↓
资产评审和自动化验证
  ↓
发布新版本、迁移或弃用
  ↓
更新 Registry 和项目采用清单
```

最终要形成以下关系：

```text
业务需求
  ↕
业务规范 / Business Process Asset
  ↕
Pattern / Composite / Adapter / Template
  ↕
项目实现
  ↕
测试、运行数据和失败证据
  ↕
资产版本迭代
```

这意味着资产库不是开发完成后的“资料归档处”，而是贯穿设计、开发、上线、维护和迭代的工程控制面。

# 35. 补充后的执行准则

```text
有资产走资产：先检索、再评估、锁版本、按契约组合、回写证据。
没资产定规范：先梳理业务事实、形成规格、评审通过后再实现。

项目不能静默复制并分叉资产。
项目发现问题时，先判断问题属于配置、Case、Adapter、Pattern 还是业务规范。
跨项目共性不能凭感觉抽象，必须通过差异矩阵和真实证据提炼。
一次成功只能形成 Case/Evidence，多个项目验证后才晋级通用资产。
Stable 资产不能被直接覆盖，所有变更都要有版本、影响分析、测试和迁移方案。
Deprecated 资产必须可追踪、可迁移、可回滚，不能直接删除。

资产维护的最小闭环是：
使用记录 + 偏差记录 + 测试证据 + 版本变更 + 影响项目 + 迁移状态。

AI 的开发行为必须被资产契约、业务规范、代码边界和验证证据共同约束。
```

# 36. 资产化设计与 AI 缓存命中率

## 36.1 结论：可以提高，但不能简单理解为“用了资产就一定命中”

按照资产化方式组织 AI 开发，确实有助于提高缓存命中率，但需要区分不同类型的缓存：

```text
上下文前缀缓存
+ 资产检索缓存
+ 语义结果缓存
+ 确定性生成缓存
+ 测试和构建缓存
```

资产化的价值在于让重复出现的内容更加稳定、结构化和可复用：

    系统提示词更加稳定
    Skill 指令更加稳定
    资产契约和规范更加稳定
    资产引用可以使用固定 ID 和版本
    任务上下文可以按固定顺序组装
    生成器输入可以产生稳定 Hash
    相同资产可以被多个项目重复使用

但最终是否命中，还取决于具体 AI 平台或 Agent 框架的缓存策略。资产化只能提高“具备缓存条件的概率”，不能保证第三方模型服务一定返回缓存命中。

## 36.2 需要区分的五类缓存

### 一、上下文前缀缓存

这是模型服务可能提供的 Prompt Prefix Cache。通常只有一段上下文在以下内容完全或高度一致时，才更容易被复用：

```text
模型或部署版本
系统提示词
Skill 指令
工具定义
资产规范文本
资产内容的排列顺序
序列化格式
```

因此，将稳定内容放在 Prompt 前部，将每次变化的项目需求放在后部，有利于前缀复用：

```text
稳定前缀：
  系统规则
  Workflow 规则
  Skill 指令
  资产分类规范
  资产契约
  代码边界

动态后缀：
  当前项目
  当前需求
  当前分支
  当前错误日志
  当前待修改文件
```

### 二、资产检索缓存

当多个任务拥有相同的问题标签时，可以缓存检索结果：

```text
问题标签
→ 候选资产列表
→ 资产匹配评分
→ 推荐组合
```

例如：

```text
authentication + phone + otp + nestjs
→ phone-otp-login
→ session-management
→ nestjs-authentication-adapter
```

下一次遇到相同或高度相似的任务时，可以先复用候选资产结果，不必重新扫描整个资产库。

### 三、语义结果缓存

如果某个资产组合已经经过验证，可以缓存其实现计划、架构决策和常见风险：

```text
资产组合：
  pattern.authentication.phone-otp-login@1.2.0
  pattern.authentication.session-management@1.3.0
  adapter.backend.nestjs.authentication@1.1.0

已验证结果：
  模块边界
  数据表建议
  API 结构
  测试场景
  常见失败模式
```

这类缓存不一定直接复用代码，但可以减少 AI 每次重新分析同一问题的成本。

### 四、确定性生成缓存

对于由规范驱动生成的内容，可以使用输入 Hash 判断是否需要重新生成：

```text
规格 Hash
+ Generator 版本
+ Adapter 版本
+ Template 版本
+ 工具链版本
→ 生成结果 Hash
```

如果这些输入没有变化，就可以复用之前生成的数据库迁移、DTO、OpenAPI、状态机代码或测试骨架。

### 五、测试和构建缓存

资产版本和实现边界稳定后，测试也可以按资产和代码 Hash 复用：

```text
asset_version
+ implementation_profile_hash
+ source_hash
+ test_suite_version
→ test_result_cache_key
```

例如上传组件的通用策略没有变化，某些跨 Adapter 契约测试可以复用历史结果；但只要代码、依赖、浏览器版本或运行环境变化，就必须按规则失效缓存。

## 36.3 资产化为什么有利于缓存

### 原因一：稳定内容变多

没有资产时，AI 每次都从自然语言重新推导：

```text
登录怎么做？
上传怎么做？
审批怎么做？
```

每次 Prompt 的描述方式、顺序、细节和代码上下文都可能不同，难以形成稳定前缀。

有资产后，变成：

```text
使用：
pattern.authentication.phone-otp-login@1.2.0
pattern.authentication.session-management@1.3.0
adapter.backend.nestjs.authentication@1.1.0
```

然后由系统按固定格式加载相同的契约和规范，重复任务更容易产生相同的上下文前缀。

### 原因二：资产 ID 和版本可以作为稳定引用

稳定引用应优先使用：

```text
asset_id + version + content_hash
```

而不是每次通过自然语言描述：

```text
请按照之前那个手机号登录方式实现
```

固定 ID 能够用于：

    检索缓存
    Prompt 组装
    资产锁定
    变更追踪
    影响分析
    结果复现

### 原因三：资产可以按需加载

如果每次都把整个资产库塞给 AI，不仅浪费上下文，也会降低稳定性。应采用渐进式加载：

```text
第一层：资产索引和摘要
第二层：资产契约和关键不变量
第三层：实现说明和示例
第四层：脚本、模板和完整参考代码
```

只有命中某个资产后，才加载它的详细内容。这样可以缩小动态上下文，增加稳定前缀的比例。

### 原因四：项目差异被隔离

如果业务规则、资产内容和项目临时信息混在一起，任何项目变化都会破坏整个 Prompt。通过分层可以保持：

```text
稳定资产层
项目配置层
任务上下文层
运行日志层
```

稳定层不变，缓存更容易复用；动态层只影响后续上下文。

## 36.4 推荐的 AI 上下文组装顺序

建议 Workflow 按以下顺序组装上下文：

```text
[1] System Policy
[2] Organization Engineering Rules
[3] Workflow / Skill Instructions
[4] Asset Registry Snapshot
[5] Selected Asset Bundle
[6] Canonical Business Specification
[7] Implementation Profile
[8] Current Task
[9] Current Files and Errors
[10] Required Output Format
```

其中前 5 层应尽可能稳定，后 5 层是项目或任务动态内容。

### 稳定前缀示例

```yaml
context_prefix:
  system_policy_version: 1.0.0
  skill_bundle_version: 2026.09.1
  asset_registry_revision: 8c12e7a
  selected_assets:
    - id: pattern.frontend.file-upload-policy
      version: 1.0.0
      hash: sha256:aaa...
    - id: pattern.frontend.upload-state-machine
      version: 1.0.0
      hash: sha256:bbb...
    - id: adapter.frontend.element-plus-upload
      version: 1.0.0
      hash: sha256:ccc...
  serialization: canonical-yaml-v1
```

### 动态任务示例

```yaml
task_context:
  project: crm-web
  branch: feature/customer-attachment
  request: 增加客户附件上传
  policy:
    max_size_bytes: 10485760
    accepted_mime_types: [image/png, image/jpeg, application/pdf]
  changed_files:
    - src/modules/customer/attachment/
```

## 36.5 缓存键设计

建议将缓存键拆成不同层级，不要把所有信息拼成一个不可解释的字符串。

### 资产检索缓存键

```yaml
retrieval_cache_key:
  domain: authentication
  capabilities:
    - phone
    - otp
    - session
  framework: nestjs
  policy_version: 1.0.0
  registry_revision: 8c12e7a
```

### 资产组合缓存键

```yaml
composition_cache_key:
  selected_assets:
    - pattern.authentication.phone-otp-login@1.2.0
    - pattern.authentication.session-management@1.3.0
    - adapter.backend.nestjs.authentication@1.1.0
  project_profile_hash: sha256:...
  composition_rule_version: 1.0.0
```

### 代码生成缓存键

```yaml
generation_cache_key:
  spec_hash: sha256:...
  generator_version: 1.2.0
  template_version: 3.1.0
  adapter_version: 1.1.0
  formatter_version: 2.4.0
  dependency_lock_hash: sha256:...
```

### 测试缓存键

```yaml
test_cache_key:
  asset_bundle_hash: sha256:...
  source_hash: sha256:...
  test_suite_version: 1.4.0
  runtime:
    node: 22.x
    browser: chromium-xxx
    database: postgres-16
```

## 36.6 提高命中率的资产编写规范

### 规范一：稳定的序列化方式

同一资产每次加载时，字段顺序、标题层级和内容格式应保持稳定。推荐：

```text
固定 YAML 字段顺序
固定 Markdown 标题顺序
固定列表排序规则
固定依赖资产顺序
固定代码格式化工具
```

不要让 AI 每次自由生成资产摘要再放入上下文，这会导致相同资产产生不同 Prompt 文本。

### 规范二：稳定的资产摘要

每个资产提供固定摘要：

```yaml
summary:
  purpose: 提供手机号 OTP 登录能力
  inputs:
    - phone_number
    - otp_code
  outputs:
    - authenticated_session
  invariants:
    - otp_expires_after_configured_duration
    - failed_attempts_are_limited
  not_for:
    - password_login
    - social_oauth
```

摘要用于第一层检索和缓存；只有确定采用后才加载完整实现说明。

### 规范三：动态信息不要放进稳定资产正文

以下内容不应该直接写入稳定资产正文：

```text
当前项目名称
当前分支名
当前时间
当前用户姓名
临时日志
一次性错误信息
随机生成的示例 ID
环境专属路径
```

这些内容应放在任务上下文或项目配置层，否则会导致整个资产上下文频繁失效。

### 规范四：避免无意义的内容变化

以下变化不应导致资产正文和版本无意义变化：

```text
空格变化
非语义的排序变化
随机示例数据变化
生成时间变化
本地绝对路径变化
```

可以通过 Canonical Serializer、格式化工具和规范化脚本消除这类差异。

### 规范五：只加载必要资产

AI 不应该默认读取整个资产库。应先通过：

```text
领域标签
能力标签
技术栈标签
风险标签
项目阶段
```

筛选候选资产，再加载选中的资产包。

## 36.7 缓存和资产版本之间的关系

资产版本变化后，必须判断哪些缓存失效：

| 变化 | 资产检索缓存 | 组合缓存 | 代码生成缓存 | 测试缓存 |
|---|---:|---:|---:|---:|
| 文档拼写修复 | 通常不失效 | 通常不失效 | 不失效 | 不失效 |
| 契约说明变化 | 失效 | 失效 | 失效 | 失效 |
| 实现 Patch 修复 | 通常不失效 | 可能失效 | 失效 | 失效 |
| Adapter 版本变化 | 按技术栈失效 | 失效 | 失效 | 相关 Adapter 失效 |
| 业务规则变化 | 失效 | 失效 | 失效 | 失效 |
| 测试用例增加 | 不失效 | 不失效 | 不失效 | 失效 |

所有缓存都必须绑定资产版本或内容 Hash，不能只按资产 ID 缓存，否则资产升级后可能继续使用旧结果。

## 36.8 资产缓存与安全边界

缓存命中不能凌驾于安全和业务正确性。以下内容禁止跨项目或跨租户复用：

```text
真实用户数据
敏感业务数据
权限判断结果
包含密钥、Token 或 Cookie 的上下文
项目专属数据库结构
未经脱敏的日志
客户代码和私有配置
```

可以复用的是：

```text
通用资产契约
脱敏后的示例
规则和状态机
测试夹具
通用实现计划
错误模式
架构约束
```

缓存键中必须包含必要的隔离维度：

```yaml
isolation:
  organization: tenger
  project: crm-web
  environment: development
  tenant_scope: project_only
  data_classification: non_sensitive
```

## 36.9 如何衡量是否真的提高了缓存命中率

不能只凭感觉判断。建议记录：

```yaml
cache_metrics:
  period: 2026-09
  context_prefix:
    requests: 1000
    hits: 720
    hit_rate: 0.72
  asset_retrieval:
    requests: 300
    hits: 255
    hit_rate: 0.85
  composition:
    requests: 180
    hits: 126
    hit_rate: 0.70
  deterministic_generation:
    requests: 90
    reused: 54
    reuse_rate: 0.60
  test_cache:
    requests: 500
    reused: 310
    reuse_rate: 0.62
```

同时观察质量指标：

```text
缓存命中后是否使用了错误版本
缓存命中是否导致遗漏业务差异
缓存命中后的代码评审问题数
缓存命中后的测试失败率
缓存命中节省的 Token 和时间
缓存失效后的重新计算成本
```

缓存命中率提高但错误版本被复用，是失败而不是成功。

## 36.10 登录案例中的缓存复用

项目 A 使用手机号登录：

```text
pattern.authentication.identity-model@1.0.0
pattern.authentication.phone-otp-login@1.0.0
pattern.authentication.session-management@1.0.0
adapter.backend.nestjs.authentication@1.0.0
```

项目 B 使用账号密码和微信登录：

```text
pattern.authentication.identity-model@1.0.0
pattern.authentication.password-login@1.0.0
pattern.authentication.oauth-login@1.0.0
pattern.authentication.account-linking@1.0.0
pattern.authentication.session-management@1.0.0
adapter.backend.nestjs.authentication@1.0.0
```

两个项目可以复用：

```text
System Policy
认证领域资产摘要
identity-model
session-management
NestJS Adapter 的稳定说明
通用安全不变量
通用测试结构
```

不能直接复用：

```text
手机号校验参数
微信 AppId 和 Secret
项目用户表名
项目租户字段
项目权限范围
项目环境变量
```

这就是“稳定前缀复用 + 动态项目配置隔离”。

## 36.11 上传案例中的缓存复用

Element Plus 和 Ant Design 的上传任务可以共享：

```text
file-upload-policy
upload-state-machine
UploadFileInput / UploadedFile 契约
通用安全检查
通用异常场景
对象存储的抽象 UploadPort
```

分别变化：

```text
组件库 Adapter
框架事件映射
项目文件类型配置
项目页面布局
项目上传用途
```

如果每个项目都把完整页面代码和当前项目日志放进缓存前缀，命中率会下降；如果只把稳定契约和 Adapter 规范放在前部，动态页面信息放在后部，就更适合缓存复用。

## 36.12 缓存友好的 Workflow 设计

Workflow 应把缓存看作资产执行的一部分：

```text
1. 计算 Skill Bundle Hash
2. 计算 Asset Registry Revision
3. 根据需求标签检索资产
4. 计算 Selected Asset Bundle Hash
5. 读取可复用的组合计划
6. 拼接稳定前缀
7. 追加项目动态上下文
8. 执行 AI 任务
9. 记录缓存命中和失效原因
10. 将新证据回写资产库
```

缓存失效原因也要记录：

```yaml
cache_miss:
  layer: composition
  reason: asset_version_changed
  old_key: sha256:old...
  new_key: sha256:new...
  impacted_assets:
    - pattern.authentication.session-management@2.0.0
  recomputation_required: true
```

这样可以判断是资产变化、项目变化、工具变化还是缓存配置问题导致未命中。

## 36.13 最终结论

资产化设计确实能够提高 AI 缓存的可复用性，主要原因是它让以下内容变得稳定：

```text
稳定的系统规则
稳定的 Skill 指令
稳定的资产 ID 和版本
稳定的契约和规范
稳定的上下文组装顺序
稳定的生成器输入
稳定的测试场景
```

但应牢记：

```text
资产复用 ≠ 一定命中模型缓存
缓存命中 ≠ 业务结果一定正确
缓存复用 ≠ 可以跳过版本校验
缓存命中率 ≠ AI 工程质量的唯一指标
```

正确目标是：

```text
通过资产化提高稳定上下文的复用率，
通过版本和 Hash 保证缓存结果不陈旧，
通过业务规格、契约和测试保证缓存结果正确，
通过确定性生成器保证可生成部分可重复。
```

# 37. 关于 AI 缓存的补充执行准则

```text
稳定内容放前面，动态内容放后面。
资产使用 ID + 版本 + Hash，不使用模糊自然语言引用。
同一资产采用固定序列化、固定排序和固定摘要。
项目差异放在配置层，不写入稳定资产正文。
缓存必须绑定版本、工具链和隔离范围。
缓存命中后仍必须检查规格版本和资产状态。
涉及业务规则、权限、安全和数据结构的变化必须使相关缓存失效。
不缓存真实用户数据、密钥、Token、租户数据和未经脱敏的日志。
用命中率、错误率、测试结果和节省成本共同评价缓存效果。
```
