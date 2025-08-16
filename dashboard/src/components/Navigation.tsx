import { motion } from 'framer-motion'
import { Brain, Wifi, WifiOff } from 'lucide-react'
import { useWebSocket } from '../contexts/WebSocketContext'

const Navigation = () => {
  const { isConnected } = useWebSocket()

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-bee-dark/80 backdrop-blur-md border-b border-neural-blue/20 sticky top-0 z-50"
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Brand */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="flex items-center space-x-3"
          >
            <div className="relative">
              <Brain className="w-8 h-8 text-bee-yellow" />
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="absolute inset-0 bg-neural-blue/20 rounded-full blur-sm"
              />
            </div>
            <div>
              <h1 className="text-xl font-bold text-glow text-bee-yellow">
                BeeMind
              </h1>
              <p className="text-xs text-neural-blue">
                Living AI Dashboard
              </p>
            </div>
          </motion.div>

          {/* Connection Status */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <Wifi className="w-5 h-5 text-success-green" />
              ) : (
                <WifiOff className="w-5 h-5 text-threat-red" />
              )}
              <span className={`text-sm ${isConnected ? 'text-success-green' : 'text-threat-red'}`}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {/* Status Indicator */}
            <div className={`status-indicator ${isConnected ? 'status-active' : 'status-error'}`} />
          </div>
        </div>
      </div>
    </motion.nav>
  )
}

export default Navigation
