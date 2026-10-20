import { onCLS, onINP, onLCP, type Metric } from 'web-vitals';

/**
 * Web Vitals 性能采集：CLS / INP / LCP 三大核心指标。
 * 接入步骤：新项目把 report 实现换成监控平台 SDK（Sentry / 内部埋点）即可，
 * main.tsx 在生产环境调用本模块；dev 下的 console.info 会被构建期 drop，生产静默直到接入 SDK。
 */
function report(metric: Metric): void {
  // TODO: 新项目接入监控平台时替换为 SDK 上报
  console.info('[web-vitals]', metric.name, metric.value, metric.id);
}

/** 初始化采集（main.tsx 在 import.meta.env.PROD 时调用） */
export function initWebVitals(): void {
  onCLS(report);
  onINP(report);
  onLCP(report);
}
