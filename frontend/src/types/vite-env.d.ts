/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
  readonly VITE_APP_ENV: string
  readonly VITE_DEBUG: string
  readonly VITE_ENABLE_LOGGING: string
  readonly VITE_ENABLE_DEV_TOOLS: string
  readonly VITE_SECURE_COOKIES: string
  readonly VITE_ENABLE_HTTPS_ONLY: string
  readonly VITE_GEMINI_API_KEY?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}