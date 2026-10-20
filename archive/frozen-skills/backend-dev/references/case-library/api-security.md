# API 设计与安全编码（API & Security）

> 用途：写接口与鉴权时的落地参考。决策树见 `decision-rules.md` §三/§四/§七。

---

## 一、API 设计要点

- 资源命名复数 + HTTP 动词语义化 + 状态码正确。
- 统一响应 `{success, data, error:{code,message}}`，错误码分段。
- 版本化：公共 API URL 前缀 `/v1`；内部 header。
- 游标分页，禁深 OFFSET（大表 O(N) 退化）。

## 二、鉴权实现决策树

| 客户端 | 方案 |
|---|---|
| 第一方浏览器 | Session Cookie / BFF 令牌中介 |
| 移动 App | OAuth/OIDC 授权码 + PKCE |
| 第三方 | OAuth/OIDC 或带 scope API Key |
| 服务间 | 平台身份/短期凭证，不用用户态 |

- BFF：Browser → BFF(session) → BFF 附加 Bearer → 上游，浏览器不接触 access token。
- access token 短时效；refresh token 存 HttpOnly Cookie。

## 三、安全编码要点

- 认证（who）vs 授权（what）：边界统一判定。
- 密码 BCrypt/Argon2 加盐，禁明文/可逆。
- 防注入：参数化查询/ORM，禁字符串拼接。
- 输入校验（白名单）+ 转义防 XSS。
- 令牌：短时效 access + HttpOnly refresh。

## 四、常见坑

- 返回 ORM 实体直接给客户端 → 用 DTO 剥离敏感字段。
- controller 散落 try/catch → 全局异常中间件统一。
- 密钥硬编码 → 全走环境变量。

> 出处：futurice/backend-best-practices、apipark API Checklist、OWASP。
