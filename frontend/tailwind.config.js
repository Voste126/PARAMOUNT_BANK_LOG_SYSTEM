/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,html}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        // Dark blue gradient
        "paramount-blue-900": "#0a1045",
        "paramount-blue-800": "#13266f",
        // Lighter blues
        "paramount-blue-50":  "#f0f6ff",
        "paramount-blue-100": "#e5ebf8",
        "paramount-blue-200": "#cbd6f0",
        // Yellow palette
        "paramount-yellow-100": "#fde68a",
        "paramount-yellow-200": "#fef3c7",
        "paramount-yellow-400": "#facc15",
        "paramount-yellow-500": "#fbbf24",
        "paramount-yellow-600": "#f59e0b",
        // White
        "paramount-white": "#ffffff"
      },
    },
  },
  plugins: [],
};
