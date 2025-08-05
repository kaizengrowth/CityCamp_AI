const path = require('path');

module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/setupTests.ts'],
  moduleNameMapper: {
    '^@/assets/images/(.*)\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/__mocks__/fileMock.js',
    '^@/(.*)$': '<rootDir>/../../frontend/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^react-markdown$': '<rootDir>/__mocks__/react-markdown.js'
  },
  transform: {
    '^.+\\.(ts|tsx)$': [
      path.resolve(__dirname, '../../frontend/node_modules/ts-jest'),
      {
        tsconfig: path.resolve(__dirname, '../../frontend/tsconfig.json')
      }
    ],
  },
  transformIgnorePatterns: [
    'node_modules/(?!(react-markdown|remark-.*|unified|bail|is-plain-obj|trough|vfile|unist-.*|mdast-.*|micromark|decode-named-character-reference|character-entities|property-information|hast-util-whitespace|space-separated-tokens|comma-separated-tokens|zwitch)/)'
  ],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  collectCoverageFrom: [
    '../../frontend/src/**/*.{ts,tsx}',
    '!../../frontend/src/**/*.d.ts',
    '!../../frontend/src/main.tsx',
    '!../../frontend/src/vite-env.d.ts',
  ],
  coverageReporters: ['text', 'lcov', 'html'],
  testMatch: [
    '<rootDir>/**/*.(test|spec).{ts,tsx}',
  ],
  rootDir: '.',
  testEnvironmentOptions: {
    customExportConditions: [''],
  },
  // Ensure Jest can find node_modules from the frontend directory
  moduleDirectories: ['node_modules', path.resolve(__dirname, '../../frontend/node_modules')],
  // Transform node_modules if needed
  transformIgnorePatterns: [
    'node_modules/(?!(date-fns)/)'
  ]
};
