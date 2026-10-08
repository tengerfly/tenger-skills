import '@testing-library/jest-dom/vitest';

/**
 * jsdom 未实现 matchMedia，而 AntD（Grid 响应式、Modal 滚动锁）会在挂载时调用；
 * 不补齐会在渲染用例里抛出未捕获异常导致误判失败。
 * 此处提供最小可用实现：统一返回「未匹配」的 MediaQueryList。
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
