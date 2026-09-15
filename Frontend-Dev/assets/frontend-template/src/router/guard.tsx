import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

/**
 * 路由守卫（单文件收口）。
 * 现状：模板无登录体系，默认全部放行；接入权限时只改本文件（isLoggedIn 实现 + RouteMeta 扩展字段），
 * 路由表与页面代码零改动。
 */

/** 路由元信息：守卫判定材料，接入权限系统时在此扩展（如 roles / permissions / 菜单可见性） */
export interface RouteMeta {
  /** 是否需要登录（默认 false：不声明即公开页） */
  requiresAuth?: boolean;
}

/**
 * 登录态判定：模板默认恒真（全部放行）。
 * 接入权限时替换实现：读 token / 全局用户 store / 权限点，守卫逻辑本身不用动。
 */
const isLoggedIn = (): boolean => true;

export interface GuardContext {
  /** 目标路径（含 query，便于登录后回跳） */
  to: string;
  /** 路由元信息 */
  meta: RouteMeta;
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

/**
 * 路由表专用包装（App.tsx 使用）：给页面元素挂守卫。
 * @param element 页面元素
 * @param meta 路由元信息（不传即公开页）
 * @returns 包装后的元素
 */
export function guard(element: ReactNode, meta: RouteMeta = {}): ReactNode {
  return <GuardedRoute meta={meta}>{element}</GuardedRoute>;
}

/** 挂载 location 并执行守卫的内部组件 */
function GuardedRoute({ meta, children }: { meta: RouteMeta; children: ReactNode }) {
  const location = useLocation();
  const redirect = routeGuard({ to: `${location.pathname}${location.search}`, meta });
  if (redirect) return <Navigate to={redirect} replace />;
  return <>{children}</>;
}
