import ElementPlus from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { QueryClient, VueQueryPlugin } from '@tanstack/vue-query';
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { pinia } from './stores';
import { initWebVitals } from './metrics/webVitals';
import 'element-plus/dist/index.css';
import 'element-plus/theme-chalk/dark/css-vars.css';
import './styles/variables.scss';
import './styles/global.scss';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});

// 性能采集仅生产环境开启（上报实现见 src/metrics/webVitals.ts，接入监控 SDK 后生效）
if (import.meta.env.PROD) {
  initWebVitals();
}

// Element Plus 全量注册 + zh_CN locale；视觉 token 见 src/styles/variables.scss 的「Element Plus 映射」段
// （换组件库时的触点：本文件全局注册/locale/dark css + components/ui/ 出口 + variables.scss）
createApp(App)
  .use(pinia)
  .use(router)
  .use(VueQueryPlugin, { queryClient })
  .use(ElementPlus, { locale: zhCn })
  .mount('#app');
