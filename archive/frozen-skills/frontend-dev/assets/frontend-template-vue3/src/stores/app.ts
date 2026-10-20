import { defineStore } from 'pinia';

/**
 * 示例全局 store（新项目删除或改造）：
 * 演示 Pinia options 式写法（state/getters/actions）+ 暗色主题切换。
 * 暗色钩子：html.dark 同时驱动 styles/variables.scss 的 token 覆盖段与
 * Element Plus 的 dark css-vars（main.ts 引入），一处切换全站生效。
 */
export const useAppStore = defineStore('app', {
  state: () => ({
    /** 当前主题；持久化由新项目按需接入（如 localStorage） */
    theme: 'light' as 'light' | 'dark',
  }),
  getters: {
    isDark: (state) => state.theme === 'dark',
  },
  actions: {
    setTheme(theme: 'light' | 'dark') {
      this.theme = theme;
      document.documentElement.classList.toggle('dark', theme === 'dark');
    },
    toggleTheme() {
      this.setTheme(this.isDark ? 'light' : 'dark');
    },
  },
});
