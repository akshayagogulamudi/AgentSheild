module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: { 900: '#0a0e1a', 800: '#0f1629', 700: '#141b38', 600: '#1a2347' },
        cyber: { blue: '#3b82f6', cyan: '#06b6d4', green: '#10b981', red: '#ef4444', yellow: '#f59e0b' }
      }
    }
  },
  plugins: []
}
