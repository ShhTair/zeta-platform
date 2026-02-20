import type { Config } from "tailwindcss";

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Google Drive color palette
        background: "#FFFFFF",
        sidebar: "#F9FAFB",
        text: {
          primary: "#202124",
          secondary: "#5F6368",
        },
        border: "#DADCE0",
        hover: "#F1F3F4",
        primary: "#1A73E8",
        active: "#E8F0FE",
      },
      boxShadow: {
        'google-sm': '0 1px 3px rgba(0, 0, 0, 0.12)',
        'google-md': '0 1px 2px rgba(0, 0, 0, 0.05), 0 2px 4px rgba(0, 0, 0, 0.08)',
      },
      spacing: {
        // Google's 8px grid
        '1': '8px',
        '2': '16px',
        '3': '24px',
        '4': '32px',
        '5': '40px',
        '6': '48px',
      },
    },
  },
  plugins: [],
} satisfies Config;
