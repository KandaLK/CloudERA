/**
 * Application configuration utility
 * Handles environment variables and provides type-safe configuration
 */

export interface AppConfig {
  env: 'development' | 'production';
  apiBaseUrl: string;
  appName: string;
  appVersion: string;
  debug: boolean;
  enableLogging: boolean;
  enableDevTools: boolean;
  geminiApiKey?: string;
  securitySettings: {
    secureCookies: boolean;
    httpsOnly: boolean;
  };
}

// Helper function to get environment variable with fallback
const getEnvVar = (key: string, fallback: string = ''): string => {
  return import.meta.env[key as keyof ImportMetaEnv] || fallback;
};

// Helper function to get boolean environment variable
const getBoolEnvVar = (key: string, fallback: boolean = false): boolean => {
  const value = import.meta.env[key as keyof ImportMetaEnv];
  if (value === undefined) return fallback;
  return value === 'true';
};

// Application configuration
export const config: AppConfig = {
  env: (getEnvVar('VITE_APP_ENV', 'development') as 'development' | 'production'),
  apiBaseUrl: getEnvVar('VITE_API_BASE_URL', 'http://localhost:8000'),
  appName: getEnvVar('VITE_APP_NAME', 'Cloud ERA - AI Cloud Services Assistant'),
  appVersion: getEnvVar('VITE_APP_VERSION', '1.0.0'),
  debug: getBoolEnvVar('VITE_DEBUG', true),
  enableLogging: getBoolEnvVar('VITE_ENABLE_LOGGING', true),
  enableDevTools: getBoolEnvVar('VITE_ENABLE_DEV_TOOLS', false),
  geminiApiKey: getEnvVar('VITE_GEMINI_API_KEY'),
  securitySettings: {
    secureCookies: getBoolEnvVar('VITE_SECURE_COOKIES', false),
    httpsOnly: getBoolEnvVar('VITE_ENABLE_HTTPS_ONLY', false),
  },
};

// Development helpers
export const isDevelopment = config.env === 'development';
export const isProduction = config.env === 'production';

// Logging utility (only logs in development or when logging is enabled)
export const logger = {
  log: (...args: any[]) => {
    if (config.enableLogging || isDevelopment) {
      console.log('[Cloud ERA]', ...args);
    }
  },
  error: (...args: any[]) => {
    if (config.enableLogging || isDevelopment) {
      console.error('[Cloud ERA Error]', ...args);
    }
  },
  warn: (...args: any[]) => {
    if (config.enableLogging || isDevelopment) {
      console.warn('[Cloud ERA Warning]', ...args);
    }
  },
  debug: (...args: any[]) => {
    if (config.debug && (config.enableLogging || isDevelopment)) {
      console.debug('[Cloud ERA Debug]', ...args);
    }
  },
};

// Export environment info for debugging
if (isDevelopment) {
  logger.debug('Application Configuration:', config);
}