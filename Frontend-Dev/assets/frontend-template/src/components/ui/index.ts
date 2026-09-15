/**
 * 组件库统一出口（当前 Ant Design 5）。
 *
 * 铁律：业务代码（pages / features / 其他 components）禁止直接 import 'antd' 与 '@ant-design/icons'，
 * 一律从本目录引入。这是为「后续换组件库」预留的隔离层：
 * - 出口为纯 re-export 时零成本（API 一致，改一处 import 来源即可整体替换）；
 * - 换库后 API 有差异的组件，在本目录内做适配包装（保持项目内用法不变），差异不外溢到页面。
 * 换库另需同步的两处：src/main.tsx（Providers/主题/locale）、src/styles/variables.scss（视觉 token）。
 */

export {
  Alert,
  Avatar,
  Button,
  Card,
  ConfigProvider,
  Dropdown,
  Result,
  Skeleton,
  Space,
  Spin,
  Tag,
  Typography,
} from 'antd';

export type { MenuProps } from 'antd';

export * from './icons';
