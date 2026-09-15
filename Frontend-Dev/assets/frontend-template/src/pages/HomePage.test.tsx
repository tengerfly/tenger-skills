import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import HomePage from './HomePage';
import { fetchDemoPing } from '../api/demo';

// 测试约定：mock 掉 api 层（不 mock 组件/网络），页面行为照常走 React Query
vi.mock('../api/demo', () => ({
  fetchDemoPing: vi.fn(),
}));
const mockedPing = vi.mocked(fetchDemoPing);

/** 渲染被测页面：注入 Router + QueryClient（真实页面用到 useNavigate 等也不缺上下文） */
function renderPage(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter>
      <QueryClientProvider client={client}>{ui}</QueryClientProvider>
    </MemoryRouter>,
  );
}

describe('HomePage（模板三态示例）', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('成功态：展示后端返回的 message', async () => {
    mockedPing.mockResolvedValue({ message: 'pong' });
    renderPage(<HomePage />);
    expect(await screen.findByText('pong')).toBeInTheDocument();
  });

  it('错误态：展示失败提示，重试成功后恢复', async () => {
    mockedPing.mockRejectedValue(new Error('boom'));
    renderPage(<HomePage />);
    expect(await screen.findByText('请求失败')).toBeInTheDocument();
    mockedPing.mockResolvedValue({ message: 'pong' });
    await userEvent.click(screen.getByRole('button', { name: '重新加载' }));
    expect(await screen.findByText('pong')).toBeInTheDocument();
  });
});
