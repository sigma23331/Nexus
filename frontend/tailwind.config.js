/** @type {import('tailwindcss').Config} */
export default {
  theme: {
    extend: {
      colors: {
        'bg-primary': '#e8ecf7',
        'bg-secondary': '#f4f6fc',
        card: '#fff',
        text: '#1e293b',
        muted: '#64748b',
        border: '#e2e8f0',
        accent: '#6366f1',
        'accent-soft': '#e0e7ff',
        love: '#ec4899',
        work: '#3b82f6',
        health: '#22c55e',
        money: '#f59e0b',
      },
      boxShadow: {
        card: '0 4px 14px rgba(15,23,42,.08)',
      },
      borderRadius: {
        card: '12px',
      },
      backgroundImage: {
        'gradient-body': 'linear-gradient(165deg, #e8ecf7 0%, #f4f6fc 45%, #eef2ff 100%)',
      },
    },
  },
}