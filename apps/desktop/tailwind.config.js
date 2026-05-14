/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        clinical: {
          blue: "#0052CC",
          ink: "#0F172A",
          muted: "#64748B",
          panel: "#FFFFFF",
          soft: "#F8FAFC",
          line: "#D8E0EA"
        }
      },
      boxShadow: {
        clinical: "0 14px 34px rgba(15, 23, 42, 0.08)"
      },
      fontFamily: {
        sans: ["Inter", "Segoe UI", "Arial", "sans-serif"]
      }
    }
  },
  plugins: []
};
