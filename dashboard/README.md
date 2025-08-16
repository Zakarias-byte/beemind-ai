# 🧠 BeeMind Dashboard

**Living AI Dashboard** - Immersive visualization of AI swarm intelligence

## 🎯 Overview

BeeMind Dashboard is a cutting-edge React application that visualizes AI swarm intelligence as a living organism. It provides real-time monitoring of:

- **Queen AI "Hjernen"** - Central AI brain with 3D visualization
- **Bee Agents Swarm** - Real-time agent activity and performance
- **AI Code Generation** - Live code generation simulation
- **Evolution Progress** - Genetic algorithm visualization
- **Performance Metrics** - System and model performance monitoring

## 🚀 Features

### Phase 4.1 (Current)
- ✅ React 18 + TypeScript setup
- ✅ Tailwind CSS with custom BeeMind theme
- ✅ Framer Motion animations
- ✅ WebSocket context for real-time data
- ✅ Responsive layout with placeholder components
- ✅ Custom animations and visual effects

### Upcoming Phases
- 🔄 **Phase 4.2**: Three.js 3D Queen AI visualization
- 🔄 **Phase 4.3**: Canvas/SVG Bee Agents swarm
- 🔄 **Phase 4.4**: AI Code Window with syntax highlighting
- 🔄 **Phase 4.5**: D3.js real-time charts
- 🔄 **Phase 4.6**: Backend WebSocket integration
- 🔄 **Phase 4.7**: Polish and testing

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS, Framer Motion
- **3D Graphics**: Three.js, React Three Fiber
- **Data Visualization**: D3.js, React Force Graph
- **Real-time**: Socket.io Client
- **Code Display**: React Syntax Highlighter
- **Icons**: Lucide React

## 📦 Installation

1. **Navigate to dashboard directory**:
   ```bash
   cd dashboard
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Open in browser**:
   ```
   http://localhost:3000
   ```

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

### Project Structure

```
dashboard/
├── src/
│   ├── components/          # React components
│   │   ├── Dashboard.tsx    # Main dashboard layout
│   │   ├── QueenAI.tsx      # Queen AI visualization
│   │   ├── BeeAgentsSwarm.tsx # Bee agents swarm
│   │   ├── LiveAgentLogs.tsx # Real-time logs
│   │   ├── AICodeWindow.tsx # AI code generation
│   │   ├── EventsTable.tsx  # Events table
│   │   └── RealtimeCharts.tsx # Charts and graphs
│   ├── contexts/            # React contexts
│   │   └── WebSocketContext.tsx # WebSocket management
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # App entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── package.json             # Dependencies
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind configuration
└── tsconfig.json            # TypeScript configuration
```

## 🎨 Design System

### Colors
- **Bee Yellow**: `#FFD700` - Primary brand color
- **Neural Blue**: `#00BFFF` - AI/Technology theme
- **Neural Purple**: `#8A2BE2` - Advanced features
- **Threat Red**: `#FF4444` - Alerts and warnings
- **Success Green**: `#00FF7F` - Success states
- **Warning Orange**: `#FFA500` - Warnings

### Animations
- **Pulse**: Queen AI heartbeat
- **Neural Pulse**: Neural activity
- **Bee Float**: Agent movement
- **Code Fade**: Code generation effects
- **Glow**: Interactive elements

## 🔌 Backend Integration

The dashboard is designed to connect to the BeeMind FastAPI backend:

- **Development**: `http://localhost:8000`
- **WebSocket**: `ws://localhost:8000`
- **API Proxy**: Configured in `vite.config.ts`

### WebSocket Events
- `queen-status` - Queen AI status updates
- `bee-agents` - Bee agent data
- `evolution-progress` - Genetic algorithm progress
- `performance-metrics` - System performance
- `ai-code-stream` - AI code generation

## 🎯 Next Steps

1. **Start BeeMind backend** (if not running)
2. **Test WebSocket connection**
3. **Proceed to Phase 4.2** - Three.js Queen AI implementation
4. **Enhance components** with real data integration

## 📝 Notes

- Currently using mock data for development
- WebSocket connection shows connection status
- All components are responsive and animated
- Ready for real backend integration

---

**BeeMind Dashboard** - Where AI comes to life! 🧠🐝
