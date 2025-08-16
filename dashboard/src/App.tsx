import { Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import Dashboard from './components/Dashboard'
import Navigation from './components/Navigation'
import { WebSocketProvider } from './contexts/WebSocketContext'

function App() {
  return (
    <WebSocketProvider>
      <div className="min-h-screen bg-bee-darker">
        <Navigation />
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="container mx-auto px-4 py-8"
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </motion.div>
      </div>
    </WebSocketProvider>
  )
}

export default App
