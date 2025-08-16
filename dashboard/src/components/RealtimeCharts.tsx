import { motion } from 'framer-motion'
import { TrendingUp, Activity, Cpu, HardDrive } from 'lucide-react'
import { useWebSocket } from '../contexts/WebSocketContext'
import { useRef, useEffect, useState, useCallback } from 'react'
import * as d3 from 'd3'

interface ChartData {
  time: number
  value: number
  label: string
}

interface PerformanceData {
  cpu: number
  memory: number
  disk: number
  network: number
  timestamp: string
}

const RealtimeCharts = () => {
  const { isConnected, performanceMetrics, evolutionStats } = useWebSocket()
  const [cpuData, setCpuData] = useState<ChartData[]>([])
  const [memoryData, setMemoryData] = useState<ChartData[]>([])
  const [evolutionData, setEvolutionData] = useState<ChartData[]>([])
  const [currentMetrics, setCurrentMetrics] = useState<PerformanceData>({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0,
    timestamp: new Date().toISOString()
  })

  const cpuChartRef = useRef<SVGSVGElement>(null)
  const memoryChartRef = useRef<SVGSVGElement>(null)
  const evolutionChartRef = useRef<SVGSVGElement>(null)

  // Initialize chart data
  useEffect(() => {
    const now = Date.now()
    const initialData: ChartData[] = []
    
    for (let i = 0; i < 30; i++) {
      const time = now - (30 - i) * 2000 // 2 second intervals
      initialData.push({
        time,
        value: Math.random() * 100,
        label: new Date(time).toLocaleTimeString()
      })
    }
    
    setCpuData(initialData)
    setMemoryData(initialData.map(d => ({ ...d, value: Math.random() * 100 })))
    setEvolutionData(initialData.map(d => ({ ...d, value: Math.random() * 100 })))
  }, [])

  // Update data from performance metrics
  useEffect(() => {
    if (!isConnected || !performanceMetrics) return

    const now = Date.now()
    const newDataPoint: ChartData = {
      time: now,
      value: performanceMetrics.system?.cpu_percent || 0,
      label: new Date(now).toLocaleTimeString()
    }

    setCpuData(prev => {
      const newData = [...prev.slice(1), newDataPoint]
      return newData
    })

    setMemoryData(prev => {
      const newData = [...prev.slice(1), {
        ...newDataPoint,
        value: performanceMetrics.system?.memory_percent || 0
      }]
      return newData
    })

    // Update current metrics
    setCurrentMetrics({
      cpu: performanceMetrics.system?.cpu_percent || 0,
      memory: performanceMetrics.system?.memory_percent || 0,
      disk: performanceMetrics.system?.disk_percent || 0,
      network: performanceMetrics.system?.network_io || 0,
      timestamp: performanceMetrics.timestamp || new Date().toISOString()
    })

  }, [isConnected, performanceMetrics])

  // Update evolution data
  useEffect(() => {
    if (!isConnected || !evolutionStats) return

    const now = Date.now()
    const newDataPoint: ChartData = {
      time: now,
      value: evolutionStats.avg_fitness * 100 || 0,
      label: new Date(now).toLocaleTimeString()
    }

    setEvolutionData(prev => {
      const newData = [...prev.slice(1), newDataPoint]
      return newData
    })

  }, [isConnected, evolutionStats])

  // D3.js chart rendering functions
  const renderChart = useCallback((
    svgRef: React.RefObject<SVGSVGElement>,
    data: ChartData[],
    title: string,
    color: string
  ) => {
    if (!svgRef.current || !data.length) return

    const svg = d3.select(svgRef.current)
    const margin = { top: 20, right: 20, bottom: 30, left: 40 }
    const width = 300 - margin.left - margin.right
    const height = 150 - margin.top - margin.bottom

    // Clear previous chart
    svg.selectAll('*').remove()

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    // Scales
    const x = d3.scaleTime()
      .domain(d3.extent(data, d => d.time) as [number, number])
      .range([0, width])

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value) || 100])
      .range([height, 0])

    // Line generator
    const line = d3.line<ChartData>()
      .x(d => x(d.time))
      .y(d => y(d.value))
      .curve(d3.curveMonotoneX)

    // Add gradient
    const gradient = svg.append('defs')
      .append('linearGradient')
      .attr('id', `gradient-${title.toLowerCase()}`)
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0).attr('y1', y(0))
      .attr('x2', 0).attr('y2', y(100))

    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', color)
      .attr('stop-opacity', 0.8)

    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', color)
      .attr('stop-opacity', 0.2)

    // Add the line path
    g.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', color)
      .attr('stroke-width', 2)
      .attr('d', line)

    // Add area
    const area = d3.area<ChartData>()
      .x(d => x(d.time))
      .y0(height)
      .y1(d => y(d.value))
      .curve(d3.curveMonotoneX)

    g.append('path')
      .datum(data)
      .attr('fill', `url(#gradient-${title.toLowerCase()})`)
      .attr('opacity', 0.3)
      .attr('d', area)

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(3).tickFormat((d: any) => d3.timeFormat('%H:%M')(d as Date)))

    g.append('g')
      .call(d3.axisLeft(y).ticks(3))

    // Add title
    g.append('text')
      .attr('x', width / 2)
      .attr('y', -5)
      .attr('text-anchor', 'middle')
      .attr('fill', '#FFFFFF')
      .attr('font-size', '12px')
      .text(title)

  }, [])

  // Render charts when data changes
  useEffect(() => {
    renderChart(cpuChartRef, cpuData, 'CPU Usage', '#EF4444')
  }, [cpuData, renderChart])

  useEffect(() => {
    renderChart(memoryChartRef, memoryData, 'Memory Usage', '#3B82F6')
  }, [memoryData, renderChart])

  useEffect(() => {
    renderChart(evolutionChartRef, evolutionData, 'Evolution Fitness', '#10B981')
  }, [evolutionData, renderChart])

  const getStatusColor = (value: number) => {
    if (value < 50) return 'text-success-green'
    if (value < 80) return 'text-warning-orange'
    return 'text-threat-red'
  }

  const getStatusIcon = (value: number) => {
    if (value < 50) return '🟢'
    if (value < 80) return '🟡'
    return '🔴'
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-bee-yellow flex items-center space-x-2">
          <TrendingUp className="w-5 h-5" />
          <span>📊 Realtime Charts</span>
        </h2>
        <div className="flex items-center space-x-2">
          <div className={`status-indicator ${isConnected ? 'status-active' : 'status-error'}`} />
          <span className="text-sm text-neural-blue">
            {isConnected ? 'Live Data' : 'Mock Data'}
          </span>
        </div>
      </div>

      {/* Current Metrics Overview */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bee-card p-4 text-center"
        >
          <div className="flex items-center justify-center mb-2">
            <Cpu className="w-5 h-5 text-threat-red mr-2" />
            <span className="text-sm text-gray-400">CPU</span>
          </div>
          <div className={`text-2xl font-bold ${getStatusColor(currentMetrics.cpu)}`}>
            {Math.round(currentMetrics.cpu)}%
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {getStatusIcon(currentMetrics.cpu)} {currentMetrics.cpu < 50 ? 'Optimal' : currentMetrics.cpu < 80 ? 'Warning' : 'Critical'}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="bee-card p-4 text-center"
        >
          <div className="flex items-center justify-center mb-2">
            <Activity className="w-5 h-5 text-neural-blue mr-2" />
            <span className="text-sm text-gray-400">Memory</span>
          </div>
          <div className={`text-2xl font-bold ${getStatusColor(currentMetrics.memory)}`}>
            {Math.round(currentMetrics.memory)}%
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {getStatusIcon(currentMetrics.memory)} {currentMetrics.memory < 50 ? 'Optimal' : currentMetrics.memory < 80 ? 'Warning' : 'Critical'}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bee-card p-4 text-center"
        >
          <div className="flex items-center justify-center mb-2">
            <HardDrive className="w-5 h-5 text-bee-yellow mr-2" />
            <span className="text-sm text-gray-400">Disk</span>
          </div>
          <div className={`text-2xl font-bold ${getStatusColor(currentMetrics.disk)}`}>
            {Math.round(currentMetrics.disk)}%
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {getStatusIcon(currentMetrics.disk)} {currentMetrics.disk < 50 ? 'Optimal' : currentMetrics.disk < 80 ? 'Warning' : 'Critical'}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bee-card p-4 text-center"
        >
          <div className="flex items-center justify-center mb-2">
            <Activity className="w-5 h-5 text-success-green mr-2" />
            <span className="text-sm text-gray-400">Network</span>
          </div>
          <div className="text-2xl font-bold text-success-green">
            {Math.round(currentMetrics.network)} MB/s
          </div>
          <div className="text-xs text-gray-400 mt-1">
            🟢 Active
          </div>
        </motion.div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* CPU Usage Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="bee-card p-4"
        >
          <div className="h-48">
            <svg
              ref={cpuChartRef}
              width="100%"
              height="100%"
              className="w-full h-full"
            />
          </div>
        </motion.div>

        {/* Memory Usage Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="bee-card p-4"
        >
          <div className="h-48">
            <svg
              ref={memoryChartRef}
              width="100%"
              height="100%"
              className="w-full h-full"
            />
          </div>
        </motion.div>

        {/* Evolution Fitness Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bee-card p-4"
        >
          <div className="h-48">
            <svg
              ref={evolutionChartRef}
              width="100%"
              height="100%"
              className="w-full h-full"
            />
          </div>
        </motion.div>
      </div>

      {/* Evolution Stats */}
      {evolutionStats && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-6 bee-card p-4"
        >
          <h3 className="text-lg font-semibold text-neural-blue mb-4">Evolution Statistics</h3>
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-neural-blue">
                {evolutionStats.total_sessions || 0}
              </div>
              <div className="text-xs text-gray-400">Total Sessions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-success-green">
                {((evolutionStats.avg_fitness || 0) * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-gray-400">Avg Fitness</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-bee-yellow">
                {evolutionStats.total_generations || 0}
              </div>
              <div className="text-xs text-gray-400">Generations</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-neural-purple">
                {evolutionStats.recent_sessions?.length || 0}
              </div>
              <div className="text-xs text-gray-400">Recent</div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Connection Status */}
      <div className="mt-4 text-center">
        <div className="flex items-center justify-center space-x-2">
          <div className={`status-indicator ${isConnected ? 'status-active' : 'status-error'}`} />
          <span className={`text-sm ${isConnected ? 'text-success-green' : 'text-threat-red'}`}>
            {isConnected ? 'Real-time Monitoring Active' : 'No Live Data'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default RealtimeCharts
