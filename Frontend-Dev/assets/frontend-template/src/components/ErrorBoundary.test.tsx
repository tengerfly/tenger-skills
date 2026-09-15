import { useState } from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import ErrorBoundary from './ErrorBoundary';

// 边界捕获异常后 React 会走 console.error，静默避免测试输出噪音
beforeEach(() => {
  vi.spyOn(console, 'error').mockImplementation(() => undefined);
});

let shouldThrow = true;

/** 可控抛错子组件：重试后不再抛，验证错误态可复位 */
function Bomb() {
  if (shouldThrow) throw new Error('boom');
  return <div>已恢复</div>;
}

function Demo() {
  const [visible, setVisible] = useState(true);
  if (!visible) return <div>已卸载</div>;
  return (
    <ErrorBoundary>
      <Bomb />
      <button onClick={() => setVisible(false)}>卸载</button>
    </ErrorBoundary>
  );
}

describe('ErrorBoundary（全局错误边界）', () => {
  it('子树抛错降级为错误页，重试后恢复', async () => {
    shouldThrow = true;
    render(<Demo />);

    expect(screen.getByText('页面出错了')).toBeInTheDocument();
    expect(screen.getByText(/boom/)).toBeInTheDocument();

    shouldThrow = false;
    // AntD 两字中文按钮会自动插空格（重 试），断言用正则兼容
    await userEvent.click(screen.getByRole('button', { name: /重\s*试/ }));
    expect(screen.getByText('已恢复')).toBeInTheDocument();
  });
});
