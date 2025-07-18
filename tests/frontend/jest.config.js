const path = require('path');

module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/setupTests.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/../../frontend/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  transform: {
    '^.+\\.(ts|tsx)$': [
      path.resolve(__dirname, '../../frontend/node_modules/ts-jest'),
      {
        tsconfig: path.resolve(__dirname, '../../frontend/tsconfig.json')
      }
    ],
  },
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
