import React from 'react';
import ReactDOM from 'react-dom/client';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import { initWebVitals } from './metrics/webVitals';
import './styles/variables.scss';
import './styles/global.scss';

// TODO: 新项目改主题色（与 src/styles/variables.scss 的 --color-primary 同步改）
const THEME = {
  colorPrimary: '#1E3A5F',
  colorLink: '#2C7A7B',
  borderRadius: 6,
  fontSize: 14,
};

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});

// 性能采集仅生产环境开启（上报实现见 src/metrics/webVitals.ts，接入监控 SDK 后生效）
if (import.meta.env.PROD) {
  initWebVitals();
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider locale={zhCN} theme={{ token: THEME }}>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </ConfigProvider>
  </React.StrictMode>,
);
