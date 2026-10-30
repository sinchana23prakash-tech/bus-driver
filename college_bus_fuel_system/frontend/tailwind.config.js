/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Map blue to GM University Rich Burgundy / Maroon
        blue: {
          50: '#fdf2f4',
          100: '#fce7ea',
          200: '#fad0d6',
          300: '#f4a7b3',
          400: '#d44359',
          500: '#9e1c31',
          600: '#68131f', // GMU Primary button maroon
          700: '#541019', // GMU Deep Maroon
          800: '#430d14', // GMU Dark Wine
          900: '#32090f', // GMU Header Wine
          950: '#200509',
        },
        gmu: {
          maroon: {
            DEFAULT: '#541019',
            light: '#68131f',
            dark: '#380a10',
            deep: '#25050a',
          },
          gold: {
            DEFAULT: '#e5ad35',
            light: '#f5cc51',
            dark: '#ca8a1b',
            banner: '#df9f28',
            soft: '#fef7dc',
          },
          cream: '#fcf8ee'
        },
        college: {
          50: '#fdf2f4',
          100: '#fce7ea',
          500: '#9e1c31',
          600: '#68131f',
          700: '#541019',
          800: '#430d14',
          900: '#32090f',
        }
      }
    },
  },
  plugins: [],
}
