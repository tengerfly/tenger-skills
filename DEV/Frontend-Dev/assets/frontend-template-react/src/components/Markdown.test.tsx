import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import Markdown from './Markdown';

describe('Markdown（轻量渲染）', () => {
  it('覆盖高频语法：标题/粗体/行内代码/列表', () => {
    render(<Markdown text={'## 小节\n\n**重点**与`token`\n\n- 苹果\n- 香蕉'} />);

    expect(screen.getByText('小节')).toBeInTheDocument();
    expect(screen.getByText('重点').tagName).toBe('STRONG');
    expect(screen.getByText('token').tagName).toBe('CODE');
    expect(screen.getByText('苹果').tagName).toBe('LI');
    expect(screen.getByText('香蕉').tagName).toBe('LI');
  });

  it('围栏代码块与表格', () => {
    render(<Markdown text={'```js\nconst a = 1;\n```\n\n| 列A | 列B |\n| --- | --- |\n| 1 | 2 |'} />);

    expect(screen.getByText('const a = 1;')).toBeInTheDocument();
    expect(screen.getByText('列A').tagName).toBe('TH');
    expect(screen.getByText('2').tagName).toBe('TD');
  });

  it('空文本渲染为空不抛错', () => {
    const { container } = render(<Markdown text="" />);
    expect(container).toBeEmptyDOMElement();
  });
});
