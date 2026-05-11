/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        gray: { 950: '#0a0a0f', 900: '#111118', 800: '#1f1f2e', 700: '#2a2a3c' }
      }
    },
  },
  plugins: [],
}
