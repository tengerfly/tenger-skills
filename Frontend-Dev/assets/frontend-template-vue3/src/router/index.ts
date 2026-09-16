import { createRouter, createWebHistory } from 'vue-router';
import AppLayout from '@/components/AppLayout.vue';
import { setupRouterGuard } from './guard';

/**
 * 全局路由：AppLayout（顶栏 + 错误边界 + 懒加载出口）作为布局路由包裹全部页面。
 * 页面组件一律 () => import() 懒加载（路由级代码分割），新页面照此注册；
 * 需要登录的页面在 meta 传 { requiresAuth: true }（守卫逻辑见 src/router/guard.ts，单文件收口）。
 */
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/pages/HomePage.vue'),
          meta: { title: '首页' },
        },
        // { path: '/example', name: 'example', component: () => import('@/pages/ExamplePage.vue'),
        //   meta: { title: '示例', requiresAuth: true } }, ← 新页面照此注册
      ],
    },
  ],
});

setupRouterGuard(router);

export default router;
