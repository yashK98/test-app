/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: {
          900: "#0A0F1C",
          800: "#0F1729",
          700: "#141E33",
          600: "#1C2942",
        },
        line: "#26314A",
        mint: "#3DDC97",
        amber: "#F5A623",
        red: "#FF5C5C",
        blue: "#5B8DEF",
        ink: {
          100: "#E7ECF5",
          300: "#B7C1D6",
          500: "#7C8AA5",
        },
      },
      fontFamily: {
        display: ["Space Grotesk", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
    },
  },
  plugins: [],
};
