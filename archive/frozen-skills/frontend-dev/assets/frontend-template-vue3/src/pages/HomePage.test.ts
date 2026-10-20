import ElementPlus from 'element-plus';
import { QueryClient, VueQueryPlugin } from '@tanstack/vue-query';
import { flushPromises, mount } from '@vue/test-utils';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import HomePage from './HomePage.vue';
import { fetchDemoPing } from '../api/demo';

// 测试约定：mock 掉 api 层（不 mock 组件/网络），页面行为照常走 Vue Query
vi.mock('../api/demo', () => ({
  fetchDemoPing: vi.fn(),
}));
const mockedPing = vi.mocked(fetchDemoPing);

/** 挂载被测页面：注入 Vue Query + Element Plus（两者经 main.ts 全局注册，单测需显式装插件） */
function mountPage() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return mount(HomePage, {
    global: { plugins: [ElementPlus, [VueQueryPlugin, { queryClient: client }]] },
  });
}

describe('HomePage（模板三态示例）', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('成功态：展示后端返回的 message', async () => {
    mockedPing.mockResolvedValue({ message: 'pong' });
    const wrapper = mountPage();
    await flushPromises();
    await flushPromises();

    expect(wrapper.text()).toContain('pong');
  });

  it('错误态：展示失败提示，重试成功后恢复', async () => {
    mockedPing.mockRejectedValue(new Error('boom'));
    const wrapper = mountPage();
    await flushPromises();
    await flushPromises();

    expect(wrapper.text()).toContain('请求失败');

    mockedPing.mockResolvedValue({ message: 'pong' });
    const retry = wrapper.findAll('button').find((b) => b.text().includes('重新加载'));
    expect(retry).toBeTruthy();
    await retry!.trigger('click');
    await flushPromises();
    await flushPromises();

    expect(wrapper.text()).toContain('pong');
  });
});
