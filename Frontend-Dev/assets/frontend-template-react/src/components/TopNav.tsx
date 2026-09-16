import type { ReactNode } from 'react';
import { Avatar, Dropdown, HomeOutlined, SettingOutlined } from './ui';
import type { MenuProps } from './ui';
import { NavLink } from 'react-router-dom';

/** 品牌信息：新项目改这里（Avatar 自动取 name 首字） */
const BRAND = { name: '应用名', slogan: '一句话简介' };

/** 顶栏导航项：新项目增删这里（end=true 表示路径完全匹配才高亮；新图标先在 ui/icons.ts 登记） */
const NAV_ITEMS: { to: string; label: string; icon: ReactNode; end?: boolean }[] = [
  { to: '/', label: '首页', icon: <HomeOutlined />, end: true },
];

/** 顶栏一级导航 + 右侧设置菜单 */
export default function TopNav() {
  const items: MenuProps['items'] = [
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
      // TODO: 新项目接入设置弹框：onClick 打开 state，并在 header 末尾渲染 <SettingsModal />
    },
  ];
  return (
    <header className="app-header">
      <div className="page-col app-header__inner">
        <div className="app-header__brand">
          <strong>{BRAND.name}</strong>
          <span>{BRAND.slogan}</span>
        </div>
        <nav className="app-header__nav">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end}>
              {item.icon} {item.label}
            </NavLink>
          ))}
        </nav>
        <Dropdown menu={{ items }}>
          <Avatar style={{ background: 'linear-gradient(135deg,#1E3A5F,#2C7A7B)' }}>
            {BRAND.name.slice(0, 1)}
          </Avatar>
        </Dropdown>
      </div>
    </header>
  );
}
