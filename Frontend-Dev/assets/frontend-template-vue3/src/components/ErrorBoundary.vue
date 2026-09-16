<script setup lang="ts">
import { onErrorCaptured, ref } from 'vue';

/**
 * 全局错误边界：捕获子树异常，降级为可重试错误页，防白屏。
 * 在 AppLayout 包裹路由内容区并以 route.path 为 key（切换路由自动复位错误态）。
 * 与 React 版差异：Vue 的 onErrorCaptured 能力更强——渲染、生命周期、watch、事件处理器的错误都能捕获。
 */
const error = ref<Error | null>(null);

onErrorCaptured((err, _instance, info) => {
  error.value = err instanceof Error ? err : new Error(String(err));
  // TODO: 新项目接入监控上报（如 Sentry）在此埋点
  console.error('[ErrorBoundary]', err, info);
  return false; // 阻断继续向上传播（避免重复上报与控制台噪音）
});

/** 重试：清空错误态重新渲染子内容 */
function retry() {
  error.value = null;
}
</script>

<template>
  <slot v-if="!error" />
  <el-result v-else icon="error" title="页面出错了" :sub-title="error.message">
    <template #extra>
      <el-button type="primary" @click="retry">重试</el-button>
    </template>
  </el-result>
</template>
