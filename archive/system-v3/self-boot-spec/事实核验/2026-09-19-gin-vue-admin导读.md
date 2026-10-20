# Fact-Check · gin-vue-admin 导读核验（第 1 轮）

- 核验对象：`.spec/源码学习/flipped-aurora__gin-vue-admin/导读.md`
- 证据源：L3 本地克隆（gin-vue-admin main@d6d4950，锚点本会话亲读/grep）；Casbin 机制描述以 casbin.org 官方概念为准
- TL;DR：**承重断言全 ✅；1 处措辞失准（BlackCache 并非 go-cache，是项目自带 local_cache 包）当轮修正**。修正后可采纳。

## 承重断言判定表

| # | 断言 | 判定 | 证据 |
|---|---|---|---|
| 1 | 私有路由链 = JWTAuth + CasbinHandler，分组挂载 | ✅ | initialize/router.go:66-68、82-87 |
| 2 | x-token 头；黑名单两级（local BlackCache + Redis 服务）；缓冲期续期走 new-token 响应头（7d/1d）；多点登录 SetRedisJWT | ✅ | middleware/jwt.go:18-33,25-30,56-68,64-67,86-89；config.yaml:4-8 |
| 3 | 被注释的「每请求查库校验禁用」代码及作者注释 | ✅ | jwt.go:47-54 亲读 |
| 4 | Casbin 三元组 Enforce(AuthorityId,path,method)，中间件约 20 行 | ✅ | middleware/casbin_rbac.go:13-31 |
| 5 | enforcer=SyncedCachedEnforcer + gormadapter(DB casbin_rule) + 模型内嵌字符串 | ✅ | utils/casbin_util.go:20-43 |
| 6 | 策略界面化维护：UpdateCasbin/回显/改 API 同步策略 | ✅ | service/system/sys_casbin.go:26,88,110 |
| 7 | 多角色 many2many 连接表；claims 只带单一 AuthorityId（默认 888）；SetUserAuthority 切换 | ✅ | sys_user.go:27,29,140+；sys_user_authority.go:4-7 |
| 8 | GORM tag 即表定义；AutoMigrate 自动建表；五数据库适配文件 | ✅ | sys_user.go:22-32；initialize/gorm_biz.go:9；gorm_{mysql,pgsql,oracle,mssql,sqlite}.go |
| 9 | 代码化种子+initOrder 常量算术编排顺序；默认密码 123456 | ✅ | source/system/authority.go:12,18；source/system/user.go:48-55 |
| 10 | GORM 函数式事务 | ✅ | service/system/sys_api.go:137 等 4+ 处 |
| 11 | 操作日志中间件读 body | ✅ | middleware/operation.go:31-79 |
| 12 | 定时任务 robfig/cron（ClearDB @daily） | ✅ | initialize/timer.go:14-17 |
| 13 | ❌ 不存在 MQ（kafka/rabbitmq/nsq/nats/rocketmq 零命中） | ✅(不存在) | go.mod 与全仓代码 grep 无命中 |
| 14 | 生成器家族（package/history/llm/mcp）与插件目录 | ✅ | service/system/ 与 plugin/ 目录实列 |
| 15 | BlackCache 为项目自带 local_cache 包 | ✅（第 1 轮修正后） | global/global.go:40；initialize/other.go:23 |

## 反证搜索记录

- 「无 MQ」以 go.mod + 代码双 grep 无命中为证
- 「无行级数据权限机制」检索未见 DataScope 类似物（十命题表已标）
- 未证实清单：无
