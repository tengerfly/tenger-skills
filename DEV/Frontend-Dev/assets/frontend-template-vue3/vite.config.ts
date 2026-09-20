import { fileURLToPath, URL } from 'node:url';
import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';

/**
 * 构建配置（工程优化）——与 React 版同构：
 * - dev 代理 /api → 本地后端（新项目按实际端口改 target）
 * - 分包：业务代码（路由级懒加载）与库代码（manualChunks 抽 vendor）分离 + 内容 hash——
 *   业务改动不影响 vendor hash，浏览器/CDN 长缓存命中，用户侧等效「增量加载」
 * - 生产：无 sourcemap（防源码映射泄露）、去 console.log/info/debug 与 debugger（保留 warn/error 便于线上排障）
 */
export default defineConfig(({ command }) => ({
  plugins: [vue()],
  resolve: {
    alias: {
      // '@/xxx' → src/xxx：SCSS 注入与 SFC 均可用（tsconfig 已配 paths）
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        // 全量注入 SCSS 工具层：所有 scss 文件（含 SFC 的 <style lang="scss">）直接用 @mixin，无需逐文件 @use/@import。
        // 注意 _mixins.scss 只放编译期工具（@mixin/$var），放 CSS 规则会被重复输出。
        // CSS 自定义属性 var(--token) 是运行时级联，main.ts 引入 variables.scss 一次后全项目可用，无需注入。
        additionalData: '@use "@/styles/mixins" as *;',
      },
    },
  },
  esbuild:
    command === 'build'
      ? {
          // 仅生产构建移除，dev 保留完整输出
          pure: ['console.log', 'console.info', 'console.debug'],
          drop: ['debugger'],
        }
      : undefined,
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:3000',
    },
  },
  build: {
    target: 'es2020',
    // 显式禁用生产 sourcemap（Vite 默认即为关，写出自文档化，防误开）
    sourcemap: false,
    // vendor 抽离后单 chunk 超过默认 500KB 属预期，上调阈值消构建噪音
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        // 库分包：element-plus 系（组件库）/vue 系（框架运行时）各自独立，其余依赖归 vendor；
        // 组件库更换时只影响 vendor-element 一个 chunk，符合 ui/ 隔离层的换库策略
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined;
          if (/element-plus|@element-plus/.test(id)) return 'vendor-element';
          if (/@tanstack|@vue|vue|pinia/.test(id)) return 'vendor-vue';
          return 'vendor';
        },
      },
    },
  },
}));
