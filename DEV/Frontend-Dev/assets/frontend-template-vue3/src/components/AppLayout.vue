<script setup lang="ts">
import { Loading } from './ui';
import TopNav from './TopNav.vue';
import ErrorBoundary from './ErrorBoundary.vue';

// 懒加载页面切换时的占位（Suspense fallback 统一在这里，路由处不用重复包）
</script>

<template>
  <div>
    <TopNav />
    <main>
      <RouterView v-slot="{ Component, route }">
        <!-- 以 path 为 key：切换路由重建页面并自动复位错误边界/加载态（与 React 版 key={pathname} 等价） -->
        <ErrorBoundary :key="route.path">
          <Suspense>
            <component :is="Component" />
            <template #fallback>
              <div class="spin-center">
                <el-icon class="is-loading" :size="28" color="var(--color-primary)">
                  <Loading />
                </el-icon>
              </div>
            </template>
          </Suspense>
        </ErrorBoundary>
      </RouterView>
    </main>
  </div>
</template>
