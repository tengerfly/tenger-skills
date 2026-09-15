import { request } from './request';

/**
 * 示例 API 模块（新项目删除）：演示「一个业务域一个文件 + 类型与请求函数同文件」的约定。
 * 路径不含 BASE_URL；出参类型与后端 data 段对齐并加注释。
 */
export interface DemoPing {
  /** 后端回显消息 */
  message: string;
}

export function fetchDemoPing() {
  return request<DemoPing>('/demo/ping');
}
