/** Stylelint：SCSS 检查——核心诉求「样式值走 variables.scss token，禁写死色值」 */
module.exports = {
  extends: ['stylelint-config-standard-scss'],
  rules: {
    // 色值一律走 token（variables.scss 是唯一例外，见 overrides）
    'color-no-hex': true,
    // 视觉 token 与设计稿逐字对账，不强改写法（rgba(...) legacy 写法不强制转 rgb() modern）
    'color-function-notation': null,
    'alpha-value-notation': null,
    // BEM 命名约定：block__element--modifier
    'selector-class-pattern':
      '^([a-z][a-z0-9]*)(-[a-z0-9]+)*(__[a-z][a-z0-9]*(-[a-z0-9]+)*)?(--[a-z][a-z0-9]*(-[a-z0-9]+)*)?$',
    // token 文件按语义分组，组间空行提升可读性
    'custom-property-empty-line-before': null,
  },
  overrides: [
    {
      // token 定义文件本身是色值唯一来源
      files: ['src/styles/variables.scss'],
      rules: { 'color-no-hex': null },
    },
  ],
  ignoreFiles: ['dist/**', 'node_modules/**'],
};
