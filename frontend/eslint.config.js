import js from '@eslint/js'
import { defineFlatConfig } from 'eslint-config-prettier'
import vue from 'eslint-plugin-vue'
import globals from 'globals'

export default defineFlatConfig([
  {
    files: ['**/*.js', '**/*.vue'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node
      }
    },
    plugins: {
      vue
    },
    rules: {
      ...js.configs.recommended.rules,
      ...vue.configs['flat/recommended'].rules,
      'vue/multi-word-component-names': 'off'
    }
  },
  defineFlatConfig.configs.prettier
])