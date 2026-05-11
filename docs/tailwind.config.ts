import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  content: [],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        surface: {
          0: '#050508',
          50: '#0a0a0f',
          100: '#0f0f1a',
          200: '#13131f',
          300: '#1a1a2e',
          400: '#252542',
          500: '#2a2a4a',
        },
        brand: {
          50: '#f0f1fe',
          100: '#e2e4fd',
          200: '#c9cdfb',
          300: '#a9adf6',
          400: '#8b8aef',
          500: '#7c6ce6',
          600: '#6e52d8',
          700: '#5f41bf',
          800: '#4e369c',
          900: '#41307d',
          950: '#261c49',
        },
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.6s ease-out forwards',
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-in-right': 'slideInRight 0.5s ease-out forwards',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(124, 108, 230, 0.3)' },
          '100%': { boxShadow: '0 0 20px rgba(124, 108, 230, 0.6)' },
        },
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
