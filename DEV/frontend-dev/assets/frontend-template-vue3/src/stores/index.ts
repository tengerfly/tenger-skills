import { createPinia } from 'pinia';

/**
 * Pinia 实例出口：main.ts `app.use(pinia)` 一次性挂载。
 * 各业务域 store 用 defineStore 定义在 stores/<domain>.ts，组件内 useXxxStore() 消费。
 *
 * 状态分层约定（避免滥用全局状态）：
 * - 服务端数据（列表/详情/轮询）→ @tanstack/vue-query，不进 store；
 * - 跨页面客户端状态（主题/登录用户/全局开关）→ 本目录 store；
 * - 页面局部状态 → 组件内 ref/reactive，不外提。
 */
export const pinia = createPinia();

export * from './app';
