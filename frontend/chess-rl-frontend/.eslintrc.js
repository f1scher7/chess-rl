module.exports = {
    root: true,

    parser: '@typescript-eslint/parser',
    parserOptions: {
        project: './tsconfig.json',
        ecmaVersion: 'latest',
        sourceType: 'module',
    },

    env: {
        browser: true,
        es2021: true,
    },

    plugins: [
        '@typescript-eslint',
        'react',
    ],

    extends: [
        'eslint:recommended',
        'plugin:@typescript-eslint/recommended',
        'plugin:react/recommended',
    ],

    rules: {
        indent: ['error', 4],
        quotes: ['warn', 'single'],
        semi: ['warn', 'always'],
        'arrow-parens': ['error', 'always'],
        'object-curly-spacing': ['warn', 'always'],
        'comma-dangle': ['warn', 'always-multiline'],
    },

    settings: {
        react: {
            version: 'detect',
        },
    },
};
