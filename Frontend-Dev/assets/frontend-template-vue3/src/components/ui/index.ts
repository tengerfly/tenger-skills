/**
 * 组件库统一出口（当前 Element Plus）。
 *
 * 铁律：业务代码（pages / features / 其他 components）禁止直接 import 'element-plus' 与
 * '@element-plus/icons-vue'，script 侧一律从本目录引入（命令式 API、类型、图标）。
 * 模板里的 <el-xxx> 组件由 main.ts 全量注册提供，无需逐个 import。
 * 这是为「后续换组件库」预留的隔离层：换库时改本目录 + main.ts + variables.scss 三处，差异不外溢到页面。
 */

/** 命令式 API（函数调用型组件，模板标签用不了，必须从出口引入） */
export { ElMessage, ElMessageBox, ElNotification } from 'element-plus';

/** 常用类型（表单/表格实例与规则等，script 侧从出口引入） */
export type { FormInstance, FormRules, TableInstance } from 'element-plus';

export * from './icons';
