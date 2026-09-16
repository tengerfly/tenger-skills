import { describe, expect, it } from 'vitest';
import { createMemoryHistory, createRouter } from 'vue-router';
import { routeGuard, setupRouterGuard } from './guard';

describe('路由守卫（模板默认全放行）', () => {
  it('routeGuard：公开页放行返回 undefined', () => {
    expect(routeGuard({ to: '/anything?q=1', meta: {} })).toBeUndefined();
  });

  it('集成：requiresAuth 路由在默认登录态（恒真）下可正常进入', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div>home</div>' } },
        {
          path: '/secret',
          component: { template: '<div>secret</div>' },
          meta: { requiresAuth: true },
        },
      ],
    });
    setupRouterGuard(router);

    await router.push('/secret');
    await router.isReady();

    expect(router.currentRoute.value.path).toBe('/secret');
  });

  it('集成：afterEach 用 meta.title 写 document.title', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/titled',
          component: { template: '<div>t</div>' },
          meta: { title: '示例页' },
        },
      ],
    });
    setupRouterGuard(router);

    await router.push('/titled');
    await router.isReady();

    expect(document.title).toContain('示例页');
  });
});
