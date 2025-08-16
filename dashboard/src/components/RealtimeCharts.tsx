import { motion } from 'framer-motion'
import { BarChart3, TrendingUp, Activity } from 'lucide-react'
import { useWebSocket } from '../contexts/WebSocketContext'

const RealtimeCharts = () => {
  const { isConnected } = useWebSocket()

  // Mock data for now - will be replaced with real WebSocket data and D3.js charts
  const mockEvolutionData = [
    { generation: 1, fitness: 0.65 },
    { generation: 2, fitness: 0.72 },
    { generation: 3, fitness: 0.78 },
    { generation: 4, fitness: 0.81 },
    { generation: 5, fitness: 0.85 },
    { generation: 6, fitness: 0.88 },
    { generation: 7, fitness: 0.91 },
    { generation: 8, fitness: 0.93 },
    { generation: 9, fitness: 0.94 },
    { generation: 10, fitness: 0.95 },
  ]

  const mockPerformanceData = [
    { metric: 'CPU', value: 78 },
    { metric: 'Memory', value: 65 },
    { metric: 'GPU', value: 45 },
    { metric: 'Network', value: 32 },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-bee-yellow flex items-center space-x-2">
          <BarChart3 className="w-5 h-5" />
          <span>📈 Realtime Charts</span>
        </h2>
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-neural-blue" />
          <span className="text-sm text-neural-blue">Live Data</span>
        </div>
      </div>

      {/* Evolution Progress Chart Placeholder */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-neural-blue mb-3 flex items-center space-x-2">
          <TrendingUp className="w-4 h-4" />
          <span>Evolution Progress</span>
        </h3>
        
        <div className="h-32 bg-bee-dark/30 rounded-lg p-4 relative">
          {/* Simple bar chart representation */}
          <div className="flex items-end justify-between h-full space-x-1">
            {mockEvolutionData.map((data, index) => (
              <motion.div
                key={data.generation}
                initial={{ height: 0 }}
                animate={{ height: `${(data.fitness * 100)}%` }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-gradient-to-t from-neural-blue to-neural-purple rounded-t flex-1"
                style={{ minHeight: '4px' }}
              />
            ))}
          </div>
          
          {/* Chart labels */}
          <div className="flex justify-between text-xs text-gray-400 mt-2">
            <span>Gen 1</span>
            <span>Gen 5</span>
            <span>Gen 10</span>
          </div>
        </div>

        {/* Evolution Stats */}
        <div className="grid grid-cols-2 gap-4 mt-3">
          <div className="text-center">
            <div className="text-lg font-bold text-neural-blue">
              {mockEvolutionData[mockEvolutionData.length - 1].fitness.toFixed(3)}
            </div>
            <div className="text-xs text-gray-400">Best Fitness</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-bee-yellow">
              {mockEvolutionData.length}
            </div>
            <div className="text-xs text-gray-400">Generations</div>
          </div>
        </div>
      </div>

      {/* Performance Metrics Chart Placeholder */}
      <div>
        <h3 className="text-lg font-semibold text-neural-blue mb-3">Performance Metrics</h3>
        
        <div className="space-y-3">
          {mockPerformanceData.map((data, index) => (
            <motion.div
              key={data.metric}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="space-y-1"
            >
              <div className="flex justify-between text-sm">
                <span className="text-gray-300">{data.metric}</span>
                <span className="text-neural-blue font-bold">{data.value}%</span>
              </div>
              <div className="w-full bg-bee-dark rounded-full h-2">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${data.value}%` }}
                  transition={{ duration: 1, delay: index * 0.2 }}
                  className={`h-2 rounded-full ${
                    data.value > 80 ? 'bg-threat-red' :
                    data.value > 60 ? 'bg-warning-orange' :
                    'bg-success-green'
                  }`}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Connection Status */}
      <div className="mt-4 text-center">
        <div className="flex items-center justify-center space-x-2">
          <div className={`status-indicator ${isConnected ? 'status-active' : 'status-error'}`} />
          <span className={`text-sm ${isConnected ? 'text-success-green' : 'text-threat-red'}`}>
            {isConnected ? 'Live Charts Active' : 'No Live Data'}
          </span>
        </div>
      </div>

      {/* Chart Controls Placeholder */}
      <div className="mt-4 flex justify-center space-x-2">
        <button className="bee-button text-xs px-3 py-1">
          Evolution
        </button>
        <button className="bee-button text-xs px-3 py-1">
          Performance
        </button>
        <button className="bee-button text-xs px-3 py-1">
          Threats
        </button>
      </div>
    </div>
  )
}

export default RealtimeCharts
