import { lazy } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import { guard } from './router/guard';

/** 页面一律懒加载（React.lazy 动态 import）：路由级代码分割，新页面照此注册 */
const HomePage = lazy(() => import('./pages/HomePage'));

/**
 * 全局路由：AppLayout（顶栏 + 错误边界 + Suspense）包裹全部页面。
 * 新页面照此注册；需要登录的页面 guard 第二参传 { requiresAuth: true }（守卫逻辑见 src/router/guard.tsx）。
 */
const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      { path: '/', element: guard(<HomePage />) },
      // { path: '/example', element: guard(<ExamplePage />, { requiresAuth: true }) }, ← 新页面照此注册
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
