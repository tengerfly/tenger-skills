import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { guard, routeGuard } from './guard';

describe('路由守卫（模板默认全放行）', () => {
  it('默认登录态恒真：requiresAuth 页面直接渲染', () => {
    render(
      <MemoryRouter>
        {guard(<div>受保护内容</div>, { requiresAuth: true })}
      </MemoryRouter>,
    );
    expect(screen.getByText('受保护内容')).toBeInTheDocument();
  });

  it('guard 不传 meta：视作公开页', () => {
    render(
      <MemoryRouter>
        {guard(<div>公开内容</div>)}
      </MemoryRouter>,
    );
    expect(screen.getByText('公开内容')).toBeInTheDocument();
  });

  it('routeGuard：公开页放行返回 undefined', () => {
    expect(routeGuard({ to: '/anything?q=1', meta: {} })).toBeUndefined();
  });
});
