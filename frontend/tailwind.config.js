/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          500: '#0d6efd',
          600: '#0258d9',
          700: '#0345b5',
          900: '#0a2540',
        }
      }
    },
  },
  plugins: [],
}
