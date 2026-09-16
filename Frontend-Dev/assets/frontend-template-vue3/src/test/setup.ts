import '@testing-library/jest-dom/vitest';

/**
 * jsdom 未实现的浏览器 API 兜底——组件库挂载时会调用，不补齐会在渲染用例里抛未捕获异常导致误判失败。
 * 此处提供最小可用实现：
 * - matchMedia：Element Plus 响应式/滚动锁等场景调用；
 * - ResizeObserver：Element Plus 布局类组件（el-table/el-scrollbar 等）调用。
 */
if (!window.matchMedia) {
  window.matchMedia = (query: string): MediaQueryList =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => undefined,
      removeListener: () => undefined,
      addEventListener: () => undefined,
      removeEventListener: () => undefined,
      dispatchEvent: () => false,
    }) as unknown as MediaQueryList;
}

if (!window.ResizeObserver) {
  window.ResizeObserver = class {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  } as unknown as typeof ResizeObserver;
}
