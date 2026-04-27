/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Habilita modo escuro via classe
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      colors: {
        'medvision-primary': '#3b82f6', // Azul claro moderno
        'medvision-secondary': '#60a5fa', // Azul ainda mais claro
        'medvision-accent': '#0ea5e9', // Sky blue
        'medvision-bg': '#f8fafc', // Fundo branco-azulado suave
        'medvision-border': '#e2e8f0', // Cinza claro para bordas
        'medvision-alert-critical': '#dc2626',
        'medvision-alert-high': '#d97706',
        'medvision-alert-medium': '#eab308',
        'medvision-alert-low': '#22c55e',
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            maxWidth: 'none',
          },
        },
      }),
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
