/** Tailwind 정적 빌드 (index.html 전용). 재생성:
 *   cd docs && npx --yes tailwindcss@3.4.17 -i tailwind.input.css -o maru-tailwind.css --config tailwind.docs.config.cjs --minify
 */
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html"],
  theme: {
    extend: {
      colors: {
        maru: {
          50: "#f0fdfa",
          100: "#ccfbf1",
          200: "#99f6e4",
          300: "#5eead4",
          400: "#2dd4bf",
          500: "#14b8a6",
          600: "#0d9488",
          700: "#0f766e",
          800: "#115e59",
          900: "#134e4a",
          950: "#042f2e",
        },
        dark: {
          950: "#030712",
          900: "#0a0a0f",
          800: "#12121a",
          700: "#1a1a2e",
          600: "#232336",
        },
      },
      fontFamily: {
        sans: ["Inter", "Noto Sans KR", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        glow: "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-20px)" },
        },
        glow: {
          "0%": { boxShadow: "0 0 20px rgba(20,184,166,0.3)" },
          "100%": { boxShadow: "0 0 40px rgba(20,184,166,0.6)" },
        },
      },
    },
  },
  plugins: [],
};
