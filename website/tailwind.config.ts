import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        clara: {
          50: '#f0f7ff',
          100: '#e0effe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        mood: {
          happy: '#22c55e',
          neutral: '#64748b',
          sad: '#3b82f6',
          confused: '#eab308',
          distressed: '#ef4444',
          nostalgic: '#a855f7',
        },
        severity: {
          low: '#3b82f6',
          medium: '#eab308',
          high: '#ef4444',
        },
      },
    },
  },
  plugins: [],
}
export default config
