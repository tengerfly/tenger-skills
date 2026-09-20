import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/**/*.{ts,tsx}'],
      // 排除无业务逻辑的样板代码；业务排除项按项目增补
      exclude: ['src/test/**', 'src/**/*.test.{ts,tsx}', 'src/main.tsx', 'src/vite-env.d.ts'],
      // 覆盖率门禁（pnpm test:coverage 触发；CI 同跑）：当前实测 75%，阈值留 ~5% 回归缓冲，项目按需上调
      thresholds: {
        lines: 70,
        statements: 70,
        functions: 70,
        branches: 75,
      },
    },
  },
});
