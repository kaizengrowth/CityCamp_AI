module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/setupTests.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/../../frontend/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
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
    '<rootDir>/**/*.{ts,tsx}',
    '<rootDir>/**/*.(test|spec).{ts,tsx}',
  ],
  rootDir: '.',
  testEnvironmentOptions: {
    customExportConditions: [''],
  },
};
