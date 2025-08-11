import path from 'path';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    // Define environment variables for client-side access
    define: {
      'process.env.API_KEY': JSON.stringify(env['VITE_GEMINI_API_KEY']),
      'process.env.GEMINI_API_KEY': JSON.stringify(env['VITE_GEMINI_API_KEY'])
    },
    
    // Path aliases for cleaner imports
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      }
    },

    // Server configuration
    server: {
      port: 5173,
      host: true,
      cors: true,
    },

    // Build configuration
    build: {
      outDir: 'dist',
      sourcemap: mode === 'development',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            codemirror: ['@uiw/react-codemirror'],
            markdown: ['react-markdown', 'remark-gfm'],
          }
        }
      }
    },

    // Environment file priority
    envDir: '.',
    envPrefix: 'VITE_',
  };
});
