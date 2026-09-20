import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import Markdown from './Markdown.vue';

describe('Markdown（轻量渲染）', () => {
  it('覆盖高频语法：标题/粗体/行内代码/列表', () => {
    const wrapper = mount(Markdown, {
      props: { text: '## 小节\n\n**重点**与`token`\n\n- 苹果\n- 香蕉' },
    });

    expect(wrapper.text()).toContain('小节');
    expect(wrapper.find('strong').text()).toBe('重点');
    expect(wrapper.find('code').text()).toBe('token');
    expect(wrapper.findAll('li')).toHaveLength(2);
  });

  it('围栏代码块与表格', () => {
    const wrapper = mount(Markdown, {
      props: { text: '```js\nconst a = 1;\n```\n\n| 列A | 列B |\n| --- | --- |\n| 1 | 2 |' },
    });

    expect(wrapper.find('pre').text()).toBe('const a = 1;');
    expect(wrapper.find('th').text()).toBe('列A');
    const cellWith2 = wrapper.findAll('td').find((c) => c.text() === '2');
    expect(cellWith2?.text()).toBe('2');
  });

  it('空文本渲染为空不抛错', () => {
    const wrapper = mount(Markdown, { props: { text: '' } });
    expect(wrapper.text()).toBe('');
  });
});
