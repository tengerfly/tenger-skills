<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query';
import { fetchDemoPing } from '../api/demo';

/**
 * 模板首页（活示例）：演示标准「加载/错误/成功」三态 + 请求层用法。
 * 组件库经 main.ts 全量注册，模板直接写 <el-xxx>；script 侧需要命令式 API/类型/图标时从 components/ui 出口引入。
 * 新项目接入真实首页后整页替换本文件。
 */
const { data, isLoading, isError, refetch, isFetching } = useQuery({
  queryKey: ['demo', 'ping'],
  queryFn: fetchDemoPing,
});
</script>

<template>
  <div class="page-col">
    <section class="home-hero">
      <h1>前端模板已就绪</h1>
      <p>
        Vite + Vue 3 + TypeScript strict + Pinia + Vue Query + Sass token，组件库经 ui 出口隔离可整体替换。
        下方示例演示了页面三态约定。
      </p>
      <el-space>
        <el-tag type="primary">request() 统一解包</el-tag>
        <el-tag type="success">三态渲染</el-tag>
        <el-tag type="warning">SSE 流式（api/stream.ts）</el-tag>
      </el-space>
    </section>

    <el-card class="home-demo-card" header="请求层三态演示（GET /demo/ping，未启动后端时应看到错误态）">
      <el-skeleton v-if="isLoading" :rows="1" animated />
      <el-alert v-else-if="isError" type="error" show-icon title="请求失败" :closable="false">
        <template #default>
          <p>后端未就绪或接口不存在。真实页面照此模式：Skeleton / Alert+重新加载 / 数据渲染。</p>
          <el-button size="small" type="danger" :loading="isFetching" @click="refetch()">重新加载</el-button>
        </template>
      </el-alert>
      <code v-else class="home-demo-data">{{ data?.message }}</code>
    </el-card>
  </div>
</template>
