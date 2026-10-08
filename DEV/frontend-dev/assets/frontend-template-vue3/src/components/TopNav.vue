<script setup lang="ts">
import { markRaw, type Component } from 'vue';
import { HomeFilled, Setting } from './ui';
import { useAppStore } from '../stores';

/** 品牌信息：新项目改这里（Avatar 自动取 name 首字） */
const BRAND = { name: '应用名', slogan: '一句话简介' };

/** 顶栏导航项：新项目增删这里（RouterLink 完全匹配才高亮；新图标先在 ui/icons.ts 登记） */
const NAV_ITEMS: { to: string; label: string; icon: Component }[] = [
  { to: '/', label: '首页', icon: markRaw(HomeFilled) },
];

const appStore = useAppStore();
</script>

<template>
  <header class="app-header">
    <div class="page-col app-header__inner">
      <div class="app-header__brand">
        <strong>{{ BRAND.name }}</strong>
        <span>{{ BRAND.slogan }}</span>
      </div>
      <nav class="app-header__nav">
        <RouterLink v-for="item in NAV_ITEMS" :key="item.to" :to="item.to">
          <el-icon><component :is="item.icon" /></el-icon>
          {{ item.label }}
        </RouterLink>
      </nav>
      <el-dropdown>
        <el-avatar :style="{ background: 'linear-gradient(135deg,#1E3A5F,#2C7A7B)' }">
          {{ BRAND.name.slice(0, 1) }}
        </el-avatar>
        <template #dropdown>
          <el-dropdown-menu>
            <!-- 暗色切换：全局状态走 Pinia（stores/app.ts），样式钩子见 variables.scss 的 html.dark 段 -->
            <el-dropdown-item :icon="Setting" @click="appStore.toggleTheme()">
              {{ appStore.isDark ? '切换亮色' : '切换暗色' }}
            </el-dropdown-item>
            <!-- TODO: 新项目接入设置弹框：点击打开 el-dialog，并在本组件渲染对应弹框 -->
            <el-dropdown-item :icon="Setting" disabled>设置</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>
