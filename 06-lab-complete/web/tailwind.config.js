/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        vin: {
          blue: '#0057B8',
          orange: '#F59E0B',
          teal: '#12B3A8',
          ink: '#07182E',
          gold: '#F7C948',
          royal: '#123C69',
        }
      }
    },
  },
  plugins: [],
}
