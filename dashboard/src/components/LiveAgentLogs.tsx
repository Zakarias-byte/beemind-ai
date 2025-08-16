import { motion, AnimatePresence } from 'framer-motion'
import { Activity, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react'
import { useWebSocket } from '../contexts/WebSocketContext'
import { useRef, useEffect, useState, useCallback } from 'react'
import * as d3 from 'd3'

interface LogEntry {
  id: string
  timestamp: number
  agent_id: string
  message: string
  level: 'info' | 'warning' | 'error' | 'success'
  type: 'threat' | 'evolution' | 'performance' | 'system'
}

interface ChartData {
  time: number
  value: number
  type: string
}

const LiveAgentLogs = () => {
  const { isConnected, liveLogs } = useWebSocket()
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [selectedTimeRange, setSelectedTimeRange] = useState<'1h' | '6h' | '24h'>('1h')
  const svgRef = useRef<SVGSVGElement>(null)
  const chartRef = useRef<HTMLDivElement>(null)

  // Mock live log data
  const mockLogs: LogEntry[] = [
    { id: '1', timestamp: Date.now() - 5000, agent_id: 'threat-123', message: 'Analyzing network traffic patterns', level: 'info', type: 'threat' },
    { id: '2', timestamp: Date.now() - 4000, agent_id: 'evolution-67', message: 'Generation 15 fitness improved to 0.942', level: 'success', type: 'evolution' },
    { id: '3', timestamp: Date.now() - 3000, agent_id: 'performance-89', message: 'CPU usage optimized to 78%', level: 'info', type: 'performance' },
    { id: '4', timestamp: Date.now() - 2000, agent_id: 'threat-123', message: 'Suspicious IP detected: 192.168.1.100', level: 'warning', type: 'threat' },
    { id: '5', timestamp: Date.now() - 1000, agent_id: 'system', message: 'Blockchain hash logged successfully', level: 'success', type: 'system' },
    { id: '6', timestamp: Date.now(), agent_id: 'evolution-67', message: 'New mutation applied to neural network', level: 'info', type: 'evolution' },
  ]

  // Generate chart data
  const generateChartData = useCallback(() => {
    const now = Date.now()
    const data: ChartData[] = []
    
    for (let i = 0; i < 50; i++) {
      const time = now - (50 - i) * 60000 // 1 minute intervals
      data.push({
        time,
        value: Math.random() * 100,
        type: ['threat', 'evolution', 'performance'][Math.floor(Math.random() * 3)]
      })
    }
    
    setChartData(data)
  }, [])

  // Initialize chart data
  useEffect(() => {
    generateChartData()
  }, [generateChartData])

  // Update chart data based on live logs
  useEffect(() => {
    if (!isConnected || !liveLogs.length) return

    // Generate chart data from live logs
    const now = Date.now()
    const data: ChartData[] = []
    
    for (let i = 0; i < 50; i++) {
      const time = now - (50 - i) * 60000 // 1 minute intervals
      const logCount = liveLogs.filter(log => 
        new Date(log.timestamp).getTime() > time - 60000 && 
        new Date(log.timestamp).getTime() <= time
      ).length
      
      data.push({
        time,
        value: Math.min(100, logCount * 10), // Scale log count to 0-100
        type: 'activity'
      })
    }
    
    setChartData(data)
  }, [isConnected, liveLogs])

  // D3.js chart rendering
  useEffect(() => {
    if (!svgRef.current || !chartData.length) return

    const svg = d3.select(svgRef.current)
    const margin = { top: 20, right: 20, bottom: 30, left: 40 }
    const width = 400 - margin.left - margin.right
    const height = 200 - margin.top - margin.bottom

    // Clear previous chart
    svg.selectAll('*').remove()

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    // Scales
    const x = d3.scaleTime()
      .domain(d3.extent(chartData, d => d.time) as [number, number])
      .range([0, width])

    const y = d3.scaleLinear()
      .domain([0, d3.max(chartData, d => d.value) || 100])
      .range([height, 0])

    // Line generator
    const line = d3.line<ChartData>()
      .x(d => x(d.time))
      .y(d => y(d.value))
      .curve(d3.curveMonotoneX)

    // Add gradient
    const gradient = svg.append('defs')
      .append('linearGradient')
      .attr('id', 'line-gradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0).attr('y1', y(0))
      .attr('x2', 0).attr('y2', y(100))

    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#3B82F6')
      .attr('stop-opacity', 0.8)

    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#8B5CF6')
      .attr('stop-opacity', 0.3)

    // Add the line path
    g.append('path')
      .datum(chartData)
      .attr('fill', 'none')
      .attr('stroke', 'url(#line-gradient)')
      .attr('stroke-width', 2)
      .attr('d', line)

    // Add area
    const area = d3.area<ChartData>()
      .x(d => x(d.time))
      .y0(height)
      .y1(d => y(d.value))
      .curve(d3.curveMonotoneX)

    g.append('path')
      .datum(chartData)
      .attr('fill', 'url(#line-gradient)')
      .attr('opacity', 0.3)
      .attr('d', area)

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(5).tickFormat((d: any) => d3.timeFormat('%H:%M')(d as Date)))

    g.append('g')
      .call(d3.axisLeft(y).ticks(5))

    // Add dots
    g.selectAll('.dot')
      .data(chartData)
      .enter()
      .append('circle')
      .attr('class', 'dot')
      .attr('cx', d => x(d.time))
      .attr('cy', d => y(d.value))
      .attr('r', 3)
      .attr('fill', '#3B82F6')
      .attr('opacity', 0.7)

  }, [chartData])

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error': return 'text-threat-red'
      case 'warning': return 'text-warning-orange'
      case 'success': return 'text-success-green'
      case 'info': return 'text-neural-blue'
      default: return 'text-gray-400'
    }
  }

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'error': return <AlertTriangle className="w-3 h-3" />
      case 'warning': return <AlertTriangle className="w-3 h-3" />
      case 'success': return <CheckCircle className="w-3 h-3" />
      case 'info': return <Activity className="w-3 h-3" />
      default: return <Activity className="w-3 h-3" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'threat': return 'text-threat-red'
      case 'evolution': return 'text-neural-purple'
      case 'performance': return 'text-bee-yellow'
      case 'system': return 'text-neural-blue'
      default: return 'text-gray-400'
    }
  }

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const activeLogs = liveLogs.length > 0 ? liveLogs : mockLogs

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-bee-yellow flex items-center space-x-2">
          <Activity className="w-5 h-5" />
          <span>📝 Live Agent Logs</span>
        </h2>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-neural-blue" />
            <span className="text-sm text-neural-blue">Real-time</span>
          </div>
          <div className="flex space-x-1">
            {(['1h', '6h', '24h'] as const).map((range) => (
              <motion.button
                key={range}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSelectedTimeRange(range)}
                className={`text-xs px-2 py-1 rounded ${
                  selectedTimeRange === range
                    ? 'bg-neural-blue text-white'
                    : 'bg-bee-dark text-gray-400 hover:text-white'
                }`}
              >
                {range}
              </motion.button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-neural-blue">Activity Timeline</h3>
          <div className="flex items-center space-x-2">
            <div className={`status-indicator ${isConnected ? 'status-active' : 'status-error'}`} />
            <span className="text-xs text-gray-400">
              {isConnected ? 'Live Data' : 'Mock Data'}
            </span>
          </div>
        </div>
        
        <div 
          ref={chartRef}
          className="h-48 bg-bee-dark rounded-lg p-4 relative overflow-hidden"
        >
          <svg
            ref={svgRef}
            width="100%"
            height="100%"
            className="w-full h-full"
          />
          
          {/* Chart Overlay Info */}
          <div className="absolute top-4 right-4 bg-bee-dark/80 backdrop-blur-sm rounded-lg p-2">
            <div className="text-xs text-gray-400">Current Activity</div>
            <div className="text-sm font-bold text-neural-blue">
              {Math.round(chartData[chartData.length - 1]?.value || 0)}%
            </div>
          </div>
        </div>
      </div>

      {/* Logs Section */}
      <div className="space-y-2 max-h-64 overflow-y-auto">
        <AnimatePresence>
          {activeLogs.map((log, index) => (
            <motion.div
              key={log.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className="bee-card p-3 hover:neural-glow transition-all duration-300"
            >
              <div className="flex items-start space-x-3">
                <div className={`flex-shrink-0 ${getLevelColor(log.level)}`}>
                  {getLevelIcon(log.level)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center space-x-2">
                      <span className={`text-sm font-semibold ${getTypeColor(log.type)}`}>
                        {log.agent_id}
                      </span>
                      <span className="text-xs text-gray-400">
                        {formatTime(log.timestamp)}
                      </span>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full capitalize ${
                      log.level === 'error' ? 'bg-threat-red/20 text-threat-red' :
                      log.level === 'warning' ? 'bg-warning-orange/20 text-warning-orange' :
                      log.level === 'success' ? 'bg-success-green/20 text-success-green' :
                      'bg-neural-blue/20 text-neural-blue'
                    }`}>
                      {log.level}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-300">
                    {log.message}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Log Statistics */}
      <div className="mt-4 grid grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <div className="text-lg font-bold text-neural-blue">
            {activeLogs.filter(l => l.level === 'info').length}
          </div>
          <div className="text-xs text-gray-400">Info</div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-center"
        >
          <div className="text-lg font-bold text-success-green">
            {activeLogs.filter(l => l.level === 'success').length}
          </div>
          <div className="text-xs text-gray-400">Success</div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-center"
        >
          <div className="text-lg font-bold text-warning-orange">
            {activeLogs.filter(l => l.level === 'warning').length}
          </div>
          <div className="text-xs text-gray-400">Warning</div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="text-center"
        >
          <div className="text-lg font-bold text-threat-red">
            {activeLogs.filter(l => l.level === 'error').length}
          </div>
          <div className="text-xs text-gray-400">Error</div>
        </motion.div>
      </div>

      {/* Connection Status */}
      <div className="mt-4 text-center">
        <div className="flex items-center justify-center space-x-2">
          <div className={`status-indicator ${isConnected ? 'status-active' : 'status-error'}`} />
          <span className={`text-sm ${isConnected ? 'text-success-green' : 'text-threat-red'}`}>
            {isConnected ? 'Live Logs Streaming' : 'No Live Data'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default LiveAgentLogs
