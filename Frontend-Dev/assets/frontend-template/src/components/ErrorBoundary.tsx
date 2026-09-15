import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Button, Result } from './ui';

interface ErrorBoundaryProps {
  /** 子内容（页面级内容区） */
  children: ReactNode;
}

interface ErrorBoundaryState {
  /** 捕获到的渲染期异常；null = 正常 */
  error: Error | null;
}

/**
 * 全局错误边界：捕获子树渲染期异常，降级为可重试错误页，防白屏。
 * 在 AppLayout 包裹路由内容区并以 pathname 为 key（切换路由自动复位错误态）。
 */
export default class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // TODO: 新项目接入监控上报（如 Sentry）在此埋点
    console.error('[ErrorBoundary]', error, info.componentStack);
  }

  /** @returns 异常时渲染降级错误页（重试即复位），否则渲染子内容 */
  render(): ReactNode {
    if (this.state.error) {
      return (
        <Result
          status="error"
          title="页面出错了"
          subTitle={this.state.error.message}
          extra={
            <Button type="primary" onClick={() => this.setState({ error: null })}>
              重试
            </Button>
          }
        />
      );
    }
    return this.props.children;
  }
}
