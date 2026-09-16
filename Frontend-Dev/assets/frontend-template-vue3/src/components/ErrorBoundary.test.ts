import ElementPlus from 'element-plus';
import { flushPromises, mount } from '@vue/test-utils';
import { defineComponent, h, ref } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import ErrorBoundary from './ErrorBoundary.vue';

// 边界捕获异常后我们自身会 console.error，静默避免测试输出噪音
beforeEach(() => {
  vi.spyOn(console, 'error').mockImplementation(() => undefined);
});

const shouldThrow = ref(true);

/** 可控抛错子组件：重试后不再抛，验证错误态可复位 */
const Bomb = defineComponent({
  setup() {
    if (shouldThrow.value) throw new Error('boom');
    return () => h('div', '已恢复');
  },
});

/** 挂载被测边界：Element Plus 靠 main.ts 全局注册，单测需显式装插件（模板组件才能渲染） */
function mountBoundary() {
  return mount(ErrorBoundary, {
    slots: { default: Bomb },
    global: { plugins: [ElementPlus] },
  });
}

describe('ErrorBoundary（全局错误边界）', () => {
  it('子树抛错降级为错误页，重试后恢复', async () => {
    shouldThrow.value = true;
    const wrapper = mountBoundary();
    await flushPromises();

    expect(wrapper.text()).toContain('页面出错了');
    expect(wrapper.text()).toContain('boom');

    shouldThrow.value = false;
    const retry = wrapper.findAll('button').find((b) => b.text().includes('重试'));
    expect(retry).toBeTruthy();
    await retry!.trigger('click');
    expect(wrapper.text()).toContain('已恢复');
  });
});
