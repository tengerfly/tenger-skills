import js from '@eslint/js';
import pluginVue from 'eslint-plugin-vue';
import globals from 'globals';
import tseslint from 'typescript-eslint';

/**
 * ESLint flat config（ESLint 9）：TS + Vue SFC。
 * 与 React 版职责一致——静态检查交给本文件，样式检查走 .stylelintrc.cjs，提交门禁走 .husky/。
 */
export default tseslint.config(
  { ignores: ['dist/**', 'coverage/**', 'node_modules/**'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...pluginVue.configs['flat/essential'],
  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: { parser: tseslint.parser },
    },
  },
  {
    languageOptions: {
      globals: { ...globals.browser },
    },
    rules: {
      // 下划线开头参数允许省略（占位参数约定）
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      // 命名规范由模板约定保证（页面 XxxPage.vue 多词；App.vue / 顶栏等按功能命名），不强制机器判定
      'vue/multi-word-component-names': 'off',
    },
  },
);
