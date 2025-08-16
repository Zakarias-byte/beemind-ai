import { motion } from 'framer-motion'
import { ScrollText, Clock } from 'lucide-react'
import { useWebSocket } from '../contexts/WebSocketContext'

const LiveAgentLogs = () => {
  const { isConnected } = useWebSocket()

  // Mock data for now - will be replaced with real WebSocket data
  const mockLogs = [
    { id: 1, timestamp: '14:23:45', agent: 'ThreatBie-123', message: 'Analyzing network traffic...', level: 'info' },
    { id: 2, timestamp: '14:23:42', agent: 'LogBie-45', message: 'Processing log files completed', level: 'success' },
    { id: 3, timestamp: '14:23:40', agent: 'EvolutionBie-67', message: 'Model mutation in progress', level: 'warning' },
    { id: 4, timestamp: '14:23:38', agent: 'PerformanceBie-89', message: 'System monitoring active', level: 'info' },
    { id: 5, timestamp: '14:23:35', agent: 'ThreatBie-123', message: 'Threat detected: Suspicious IP', level: 'error' },
  ]

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'info': return 'text-neural-blue'
      case 'success': return 'text-success-green'
      case 'warning': return 'text-warning-orange'
      case 'error': return 'text-threat-red'
      default: return 'text-gray-400'
    }
  }

  const getLogLevelIcon = (level: string) => {
    switch (level) {
      case 'info': return 'ℹ️'
      case 'success': return '✅'
      case 'warning': return '⚠️'
      case 'error': return '❌'
      default: return '📝'
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-bee-yellow flex items-center space-x-2">
          <ScrollText className="w-5 h-5" />
          <span>🐝 Live Agent Logs</span>
        </h2>
        <div className="flex items-center space-x-2">
          <Clock className="w-4 h-4 text-neural-blue" />
          <span className="text-sm text-neural-blue">Real-time</span>
        </div>
      </div>

      {/* Logs Container */}
      <div className="h-64 overflow-y-auto bg-bee-dark/30 rounded-lg p-4 space-y-2">
        {mockLogs.map((log, index) => (
          <motion.div
            key={log.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className={`p-3 rounded-lg border-l-4 ${
              log.level === 'error' ? 'bg-threat-red/10 border-threat-red' :
              log.level === 'warning' ? 'bg-warning-orange/10 border-warning-orange' :
              log.level === 'success' ? 'bg-success-green/10 border-success-green' :
              'bg-neural-blue/10 border-neural-blue'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-2 flex-1">
                <span className="text-sm">{getLogLevelIcon(log.level)}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-xs text-gray-400">{log.timestamp}</span>
                    <span className="text-sm font-mono text-bee-yellow">{log.agent}</span>
                  </div>
                  <p className={`text-sm ${getLogLevelColor(log.level)}`}>
                    {log.message}
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Connection Status */}
      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className={`status-indicator ${isConnected ? 'status-active' : 'status-error'}`} />
          <span className={`text-sm ${isConnected ? 'text-success-green' : 'text-threat-red'}`}>
            {isConnected ? 'Live Feed Active' : 'Connection Lost'}
          </span>
        </div>
        <span className="text-xs text-gray-400">
          {mockLogs.length} recent logs
        </span>
      </div>
    </div>
  )
}

export default LiveAgentLogs
