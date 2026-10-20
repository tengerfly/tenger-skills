import type { Router } from 'vue-router';

/**
 * 路由守卫（单文件收口）。
 * 现状：模板无登录体系，默认全部放行；接入权限时只改本文件（isLoggedIn 实现 + RouteMeta 扩展字段），
 * 路由表与页面代码零改动。
 * 与 React 版差异：Vue Router 提供全局 beforeEach，守卫天然单点，无需逐路由包装组件。
 */

/** 路由元信息扩展：守卫判定材料 + 页面标题，接入权限系统时在此扩展（如 roles / permissions） */
declare module 'vue-router' {
  interface RouteMeta {
    /** 是否需要登录（默认 false：不声明即公开页） */
    requiresAuth?: boolean;
    /** 页面标题（afterEach 写入 document.title） */
    title?: string;
  }
}

/**
 * 登录态判定：模板默认恒真（全部放行）。
 * 接入权限时替换实现：读 token / Pinia 用户 store / 权限点，守卫逻辑本身不用动。
 */
const isLoggedIn = (): boolean => true;

export interface GuardContext {
  /** 目标路径（含 query，便于登录后回跳） */
  to: string;
  /** 路由元信息 */
  meta: { requiresAuth?: boolean };
}

/**
 * 守卫判定：放行返回 undefined；拦截返回重定向目标路径。
 * @param ctx 目标路径与路由元信息
 * @returns 重定向路径或 undefined
 */
export function routeGuard(ctx: GuardContext): string | undefined {
  if (ctx.meta.requiresAuth && !isLoggedIn()) {
    return `/login?redirect=${encodeURIComponent(ctx.to)}`;
  }
  return undefined;
}

/** 挂载全局守卫（router/index.ts 使用）：beforeEach 鉴权 + afterEach 写标题 */
export function setupRouterGuard(router: Router): void {
  router.beforeEach((to) => {
    const redirect = routeGuard({ to: to.fullPath, meta: to.meta });
    return redirect ?? true;
  });
  router.afterEach((to) => {
    // TODO: 新项目改品牌名（与 TopNav 的 BRAND 同步）
    document.title = to.meta.title ? `${to.meta.title} · 应用名` : '应用名';
  });
}
