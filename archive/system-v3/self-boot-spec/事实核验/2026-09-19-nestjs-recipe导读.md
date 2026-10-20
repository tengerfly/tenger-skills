# Fact-Check · nestjs-recipe 导读核验（第 1 轮）

- 核验对象：`.spec/源码学习/arielweinberger__nestjs-recipe/导读.md`
- 证据源：L3 本地克隆（master@4ebf945）。**本仓 src 仅 600 行，已 100% 通读**，全部锚点本会话直接读取
- TL;DR：**首轮零错误**。两个「坑位」断言（synchronize、eager+password 无 @Exclude）均以源码原文为证。

## 承重断言判定表

| # | 断言 | 判定 | 证据 |
|---|---|---|---|
| 1 | 全局 ValidationPipe + TransformInterceptor + CORS 在 bootstrap | ✅ | main.ts:10-14 |
| 2 | 多环境 .env.stage.${STAGE} + Joi 校验必填项 | ✅ | app.module.ts:10-13；config.schema.ts:3-12 |
| 3 | forRootAsync 工厂注入 ConfigService；ssl 按环境；autoLoadEntities；synchronize:true | ✅ | app.module.ts:15-36（:28 synchronize） |
| 4 | classToPlain 序列化拦截器；password 未标 @Exclude（隐患成立） | ✅ | transform.interceptor.ts:11-14；user.entity.ts 全文 17 行无 @Exclude，:12-13 password 普通 @Column |
| 5 | bcrypt genSalt+hash；23505→ConflictException | ✅ | users.repository.ts:15-16,23-25 |
| 6 | signIn bcrypt.compare + sign({username}) | ✅ | auth.service.ts:27-30 |
| 7 | @UseGuards(AuthGuard()) 类级守卫；策略 validate 回库；secret 取自配置 | ✅ | tasks.controller.ts:23；jwt.strategy.ts:18,23-32 |
| 8 | @GetUser() createParamDecorator 取 req.user | ✅ | get-user.decorator.ts:4-9 |
| 9 | 任务查询全带 user 条件（数据隔离最简形态） | ✅ | tasks.service.ts:22；tasks.repository.ts:17 |
| 10 | QueryBuilder 动态条件+参数化；仓储记日志抛 500 | ✅ | tasks.repository.ts:16-28,33-40 |
| 11 | DTO @IsNotEmpty；mock 仓储单测样例 | ✅ | create-task.dto.ts:3-8；tasks.service.spec.ts:7-27,35-38 |
| 12 | NestJS 7.x（2021）；❌ 无 MQ/缓存/定时/角色权限体系 | ✅(不存在) | package.json 依赖清单；src 文件清单全列（无 roles/schedule/redis 模块） |
| 13 | User.tasks eager:true | ✅ | user.entity.ts:15 |

## 反证搜索记录

- 「无 @Exclude」：user.entity.ts 全文亲读（17 行）为证
- 「无角色体系」：src 全部 23 个文件清单核对 + package.json 依赖核对
- 未证实清单：无
