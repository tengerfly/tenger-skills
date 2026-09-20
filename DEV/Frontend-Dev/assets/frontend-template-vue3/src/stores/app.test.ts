import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, it } from 'vitest';
import { useAppStore } from './app';

describe('useAppStore（示例全局 store）', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('默认亮色；toggleTheme 切换主题并同步 html.dark 钩子', () => {
    const store = useAppStore();

    expect(store.theme).toBe('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);

    store.toggleTheme();
    expect(store.isDark).toBe(true);
    expect(document.documentElement.classList.contains('dark')).toBe(true);

    store.toggleTheme();
    expect(store.isDark).toBe(false);
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });
});
