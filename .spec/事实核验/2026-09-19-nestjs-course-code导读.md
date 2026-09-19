# Fact-Check · 通关秘籍案例仓导读核验（第 1 轮）

- 核验对象：`.spec/源码学习/QuarkGluonPlasma__nestjs-course-code/导读.md`
- 证据源：L3 本地克隆（main@831b16c）。地图部分的案例目录以 `ls` 全量清单为准；精读案例代码亲读
- TL;DR：**承重断言全 ✅；1 处计数失准（122→120 个案例目录）当轮修正；树形案例断言升级为带锚点的精确版**。

## 承重断言判定表

| # | 断言 | 判定 | 证据 |
|---|---|---|---|
| 1 | aop-test 一控制器挂多件（管道类级/守卫方法级/拦截器注释态） | ✅ | aop-test/src/app.controller.ts:8-25（:10 UsePipes、:21 UseGuards、:9 注释的 UseInterceptors） |
| 2 | 五横切件顺序：中间件→守卫→拦截器前→管道→handler→拦截器后→过滤器 | ✅ | 五组件文件实读 + Nest 官方生命周期（L2 docs.nestjs.com FAQ/middleware） |
| 3 | RequireLogin/RequirePermission=SetMetadata | ✅ | rbac-test/src/custom-decorator.ts:3-5 |
| 4 | LoginGuard 读元数据/验 JWT/挂 request.user；Request 类型扩展 | ✅ | rbac-test/src/login.guard.ts:31-53、:8-15 |
| 5 | PermissionGuard 角色权限聚合+getAllAndOverride 两级+逐项校验 | ✅ | permission.guard.ts:25-47（:34-37） |
| 6 | User↔Role↔Permission 两个多对多 | ✅ | user.entity.ts:25-26、role.entity.ts:20-21（JoinTable） |
| 7 | 双 token：login 双签、/refresh 校验并双发 | ✅ | access_token_and_refresh_token/src/user/user.controller.ts:13-33、:37-62 |
| 8 | rabbitmq-test 为原生 amqplib 四种交换机（direct/fanout/topic/headers 各 producer+consumer） | ✅ | rabbitmq-test/src 文件清单实列 |
| 9 | microservice：createMicroservice+Transport.TCP / ClientProxy.send('sum') | ✅ | microservice-test-user/src/main.ts:6-9；microservice-test-main/src/app.controller.ts:15,22 |
| 10 | schedule-task 运行时增删 cron | ✅ | schedule-task/src/app.module.ts:23-33 |
| 11 | cache-manager：CacheModule.register(Redis)+自定义 MyCacheInterceptor | ✅ | cache-manager-test/src/app.module.ts:10；app.controller.ts:37 |
| 12 | typeorm-tree-entity-test 用 materialized-path | ✅（升级锚点） | city.entity.ts:4 @Tree('materialized-path')、:21 TreeChildren、:24 TreeParent |
| 13 | 120 个案例目录 | ✅（第 1 轮修正） | find -maxdepth 1 -type d 计数=120（ls 122 项含 qrcode.jpg） |
| 14 | README 链接即小册章节索引 | ✅ | README.md 前 60 行实读 |

## 反证搜索记录

- 「无单列事务案例」在十命题表中标 ⚠️ 而非 ❌——未逐一核 122 目录，诚实不口嗨
- 未证实清单：无
