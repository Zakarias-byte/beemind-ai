/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // BeeMind theme colors
        'bee-yellow': '#FFD700',
        'bee-orange': '#FF8C00',
        'bee-dark': '#1a1a1a',
        'bee-darker': '#0a0a0a',
        'neural-blue': '#00BFFF',
        'neural-purple': '#8A2BE2',
        'threat-red': '#FF4444',
        'success-green': '#00FF7F',
        'warning-orange': '#FFA500',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'spin-slow': 'spin 3s linear infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'neural-pulse': 'neural-pulse 1.5s ease-in-out infinite',
        'bee-float': 'bee-float 4s ease-in-out infinite',
        'code-fade': 'code-fade 0.5s ease-in-out',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #00BFFF' },
          '100%': { boxShadow: '0 0 20px #00BFFF, 0 0 30px #00BFFF' },
        },
        'neural-pulse': {
          '0%, 100%': { opacity: '0.5', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.1)' },
        },
        'bee-float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'code-fade': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0px)' },
        },
      },
      backgroundImage: {
        'neural-gradient': 'radial-gradient(circle, rgba(0,191,255,0.1) 0%, rgba(138,43,226,0.1) 100%)',
        'bee-pattern': 'radial-gradient(circle at 50% 50%, rgba(255,215,0,0.1) 0%, transparent 70%)',
      },
    },
  },
  plugins: [],
}
