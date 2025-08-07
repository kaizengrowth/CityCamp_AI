/**
 * Environment detection utilities
 * Centralized logic for development environment detection and API fallback behavior
 */

export interface EnvironmentConfig {
  isDevelopment: boolean;
  shouldUseBackupData: boolean;
  shouldShowDevMode: boolean;
}

/**
 * Detect if the application is running in development environment
 */
export const isDevelopmentEnvironment = (): boolean => {
  return window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
};

/**
 * Check if the URL contains the use-api parameter to force API usage
 */
export const shouldForceApiUsage = (): boolean => {
  return window.location.search.includes('use-api');
};

/**
 * Get comprehensive environment configuration for data loading behavior
 */
export const getEnvironmentConfig = (): EnvironmentConfig => {
  const isDevelopment = isDevelopmentEnvironment();

  return {
    isDevelopment,
    shouldUseBackupData: false, // Always use API when available
    shouldShowDevMode: isDevelopment
  };
};

/**
 * Get appropriate display text for demo/dev mode badges
 */
export const getDevModeDisplayText = (fallbackText: string = 'Demo Mode'): string => {
  return isDevelopmentEnvironment() ? '⚠️ Sample Data (Dev Mode)' : fallbackText;
};

/**
 * Get appropriate button text for API retry actions
 */
export const getApiRetryButtonText = (
  devText: string = 'Try API instead',
  prodText: string = 'Try to load real data'
): string => {
  return isDevelopmentEnvironment() ? devText : prodText;
};

/**
 * Get appropriate info message for development mode
 */
export const getDevModeInfoMessage = (hasError?: boolean): string => {
  if (isDevelopmentEnvironment()) {
    return 'Sample data loaded for local development. Add "?use-api" to the URL to test API integration.';
  }

  if (hasError) {
    return 'API connection issue detected. Showing sample data to demonstrate functionality. Click "Load Latest Data" to retry.';
  }

  return 'Showing sample data. This demonstrates how your generated content will appear when the backend API is connected.';
};
