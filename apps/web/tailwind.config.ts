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
        // Google Drive exact color palette
        'gdrive-bg': '#F8F9FA',        // Main background (very light gray)
        'gdrive-white': '#FFFFFF',      // Cards, sidebar
        'gdrive-blue': '#1A73E8',       // Primary blue
        'gdrive-blue-hover': '#1765CC', // Darker blue on hover
        'gdrive-blue-active': '#1557B0', // Even darker on active
        'gdrive-hover': '#E8F0FE',      // Light blue hover/active background
        'gdrive-gray-hover': '#F1F3F4', // Gray hover background
        'gdrive-border': '#DADCE0',     // Borders
        'gdrive-text': '#202124',       // Primary text (dark gray)
        'gdrive-secondary': '#5F6368',  // Secondary text (gray)
        'gdrive-success': '#1E8E3E',    // Success green
        'gdrive-success-bg': '#E6F4EA', // Success background
        'gdrive-danger': '#D93025',     // Danger red
        'gdrive-danger-bg': '#FCE8E6',  // Danger background
        'gdrive-warning': '#E37400',    // Warning orange
        'gdrive-warning-bg': '#FEF7E0', // Warning background
      },
      fontFamily: {
        'google': ['Google Sans', 'Roboto', 'sans-serif'],
      },
      fontSize: {
        'xs': '11px',
        'sm': '13px',
        'base': '14px',
        'lg': '16px',
        'xl': '18px',
        '2xl': '22px',
        '3xl': '28px',
      },
      borderRadius: {
        'google': '8px',
        'google-sm': '4px',
      },
      boxShadow: {
        'google-sm': '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
        'google-md': '0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15)',
        'google-lg': '0 2px 6px 2px rgba(60,64,67,0.15), 0 8px 24px 4px rgba(60,64,67,0.15)',
      },
    },
  },
  plugins: [],
} satisfies Config;
