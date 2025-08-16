import { motion } from 'framer-motion'
import { Table, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import { useWebSocket } from '../contexts/WebSocketContext'

const EventsTable = () => {
  const { isConnected } = useWebSocket()

  // Mock data for now - will be replaced with real WebSocket data
  const mockEvents = [
    { id: 1, time: '14:23', event: 'Threat Detection', status: 'alert', details: 'Suspicious IP detected' },
    { id: 2, time: '14:22', event: 'Model Generation', status: 'success', details: 'XGBoost model created' },
    { id: 3, time: '14:21', event: 'System Health', status: 'running', details: 'Performance monitoring' },
    { id: 4, time: '14:20', event: 'Evolution', status: 'success', details: 'Generation 15 completed' },
    { id: 5, time: '14:19', event: 'Log Analysis', status: 'running', details: 'Processing security logs' },
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'alert': return <AlertTriangle className="w-4 h-4 text-threat-red" />
      case 'success': return <CheckCircle className="w-4 h-4 text-success-green" />
      case 'running': return <Clock className="w-4 h-4 text-warning-orange" />
      default: return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'alert': return 'text-threat-red'
      case 'success': return 'text-success-green'
      case 'running': return 'text-warning-orange'
      default: return 'text-gray-400'
    }
  }



  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-bee-yellow flex items-center space-x-2">
          <Table className="w-5 h-5" />
          <span>📊 Events Table</span>
        </h2>
        <div className="flex items-center space-x-2">
          <div className={`status-indicator ${isConnected ? 'status-active' : 'status-error'}`} />
          <span className="text-sm text-neural-blue">Live Events</span>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-neural-blue/20">
              <th className="text-left py-2 px-3 text-sm font-semibold text-neural-blue">Time</th>
              <th className="text-left py-2 px-3 text-sm font-semibold text-neural-blue">Event</th>
              <th className="text-left py-2 px-3 text-sm font-semibold text-neural-blue">Status</th>
              <th className="text-left py-2 px-3 text-sm font-semibold text-neural-blue">Details</th>
            </tr>
          </thead>
          <tbody>
            {mockEvents.map((event, index) => (
              <motion.tr
                key={event.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="border-b border-bee-dark/30 hover:bg-bee-dark/20 transition-colors"
              >
                <td className="py-3 px-3 text-sm font-mono text-gray-400">
                  {event.time}
                </td>
                <td className="py-3 px-3 text-sm font-semibold text-white">
                  {event.event}
                </td>
                <td className="py-3 px-3">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(event.status)}
                    <span className={`text-sm capitalize ${getStatusColor(event.status)}`}>
                      {event.status}
                    </span>
                  </div>
                </td>
                <td className="py-3 px-3 text-sm text-gray-300">
                  {event.details}
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary Stats */}
      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-threat-red">
            {mockEvents.filter(e => e.status === 'alert').length}
          </div>
          <div className="text-xs text-gray-400">Alerts</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-success-green">
            {mockEvents.filter(e => e.status === 'success').length}
          </div>
          <div className="text-xs text-gray-400">Success</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-warning-orange">
            {mockEvents.filter(e => e.status === 'running').length}
          </div>
          <div className="text-xs text-gray-400">Running</div>
        </div>
      </div>

      {/* Connection Status */}
      <div className="mt-4 text-center">
        <span className={`text-sm ${isConnected ? 'text-success-green' : 'text-threat-red'}`}>
          {isConnected ? 'Live Events Streaming' : 'No Live Data'}
        </span>
      </div>
    </div>
  )
}

export default EventsTable
