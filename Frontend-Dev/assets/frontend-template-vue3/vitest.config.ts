import { fileURLToPath, URL } from 'node:url';
import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vitest/config';

/**
 * 测试配置（jsdom + globals + setup + 覆盖率门禁）。
 * 注意与 React 版的差异：.vue 单文件组件必须经 @vitejs/plugin-vue 编译才能在测试中挂载，
 * 因此本文件需要带 vue 插件与 @/ 别名（SFC 的 <style> 默认不处理，不拖慢测试）。
 */
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/**/*.{ts,vue}'],
      // 排除无业务逻辑的样板代码；业务排除项按项目增补
      exclude: [
        'src/test/**',
        'src/**/*.test.{ts,tsx}',
        'src/main.ts',
        'src/vite-env.d.ts',
        'src/App.vue',
        'src/stores/index.ts',
        'src/components/ui/**',
      ],
      // 覆盖率门禁（pnpm test:coverage 触发；CI 同跑）：阈值与 React 版一致，项目按需上调
      thresholds: {
        lines: 70,
        statements: 70,
        functions: 70,
        branches: 75,
      },
    },
  },
});
