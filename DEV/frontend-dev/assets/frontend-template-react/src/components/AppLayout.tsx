import { Suspense } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Spin } from './ui';
import TopNav from './TopNav';
import ErrorBoundary from './ErrorBoundary';

/** 懒加载页面切换时的占位（Suspense fallback 统一在这里，路由处不用重复包） */
function PageLoading() {
  return (
    <div className="spin-center">
      <Spin />
    </div>
  );
}

/** 全局布局：顶栏（brand + 导航 + 头像）+ 错误边界 + Suspense 包裹的子路由内容区 */
export default function AppLayout() {
  const { pathname } = useLocation();
  return (
    <div>
      <TopNav />
      <main>
        {/* ErrorBoundary 以 pathname 为 key：切换路由自动复位错误态，无需手动重试 */}
        <ErrorBoundary key={pathname}>
          <Suspense fallback={<PageLoading />}>
            <Outlet />
          </Suspense>
        </ErrorBoundary>
      </main>
    </div>
  );
}
