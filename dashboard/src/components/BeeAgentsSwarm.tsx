import { motion } from 'framer-motion'
import { Activity, Target } from 'lucide-react'
import { useWebSocket } from '../contexts/WebSocketContext'
import { useRef, useEffect, useState, useCallback } from 'react'

interface BeeAgent {
  id: string
  type: 'threat' | 'log' | 'evolution' | 'performance'
  status: 'active' | 'processing' | 'completed' | 'destroyed'
  current_task: string
  performance_metrics: {
    accuracy: number
    speed: number
    memory_usage: number
  }
  position: { x: number; y: number }
  angle: number
  radius: number
  opacity: number
}

const BeeAgentsSwarm = () => {
  const { beeAgents, isConnected } = useWebSocket()
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()
  const [agents, setAgents] = useState<BeeAgent[]>([])
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null)

  // Mock data for now - will be replaced with real WebSocket data
  const mockBeeAgents = [
    { id: 'threat-123', type: 'threat', status: 'active', current_task: 'Analyzing network traffic', performance_metrics: { accuracy: 94, speed: 87, memory_usage: 23 } },
    { id: 'log-45', type: 'log', status: 'processing', current_task: 'Processing log files', performance_metrics: { accuracy: 89, speed: 92, memory_usage: 18 } },
    { id: 'evolution-67', type: 'evolution', status: 'active', current_task: 'Mutating models', performance_metrics: { accuracy: 96, speed: 78, memory_usage: 45 } },
    { id: 'performance-89', type: 'performance', status: 'completed', current_task: 'Monitoring system', performance_metrics: { accuracy: 91, speed: 85, memory_usage: 12 } },
    { id: 'threat-234', type: 'threat', status: 'active', current_task: 'Detecting anomalies', performance_metrics: { accuracy: 88, speed: 95, memory_usage: 31 } },
    { id: 'log-56', type: 'log', status: 'processing', current_task: 'Parsing events', performance_metrics: { accuracy: 92, speed: 83, memory_usage: 27 } },
  ]

  const activeAgents = beeAgents.length > 0 ? beeAgents : mockBeeAgents

  const getAgentColor = (type: string) => {
    switch (type) {
      case 'threat': return '#EF4444'
      case 'log': return '#3B82F6'
      case 'evolution': return '#8B5CF6'
      case 'performance': return '#F59E0B'
      default: return '#6B7280'
    }
  }

  const getAgentIcon = (type: string) => {
    switch (type) {
      case 'threat': return '🛡️'
      case 'log': return '📝'
      case 'evolution': return '🧬'
      case 'performance': return '⚡'
      default: return '🐝'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#10B981'
      case 'processing': return '#F59E0B'
      case 'completed': return '#3B82F6'
      case 'destroyed': return '#EF4444'
      default: return '#6B7280'
    }
  }

  // Initialize agents with orbital positions
  useEffect(() => {
    const newAgents: BeeAgent[] = activeAgents.map((agent, index) => {
      const angle = (index / activeAgents.length) * Math.PI * 2
      const radius = 80 + Math.random() * 40
      return {
        ...agent,
        position: { x: 0, y: 0 },
        angle,
        radius,
        opacity: 1
      }
    })
    setAgents(newAgents)
  }, [activeAgents])

  // Animation loop
  const animate = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const centerX = canvas.width / 2
    const centerY = canvas.height / 2

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Draw central Queen AI
    ctx.save()
    ctx.globalAlpha = 0.8
    ctx.fillStyle = '#3B82F6'
    ctx.beginPath()
    ctx.arc(centerX, centerY, 30, 0, Math.PI * 2)
    ctx.fill()
    
    // Queen AI glow effect
    ctx.shadowColor = '#3B82F6'
    ctx.shadowBlur = 20
    ctx.fillStyle = '#3B82F6'
    ctx.beginPath()
    ctx.arc(centerX, centerY, 25, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()

    // Draw Queen AI icon
    ctx.fillStyle = '#FFFFFF'
    ctx.font = '20px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText('🧠', centerX, centerY)

    // Update and draw agents
    setAgents(prevAgents => 
      prevAgents.map(agent => {
        // Update orbital position
        const newAngle = agent.angle + 0.02
        const x = centerX + Math.cos(newAngle) * agent.radius
        const y = centerY + Math.sin(newAngle) * agent.radius

        // Draw agent
        ctx.save()
        
        // Agent glow effect
        const color = getAgentColor(agent.type)
        ctx.shadowColor = color
        ctx.shadowBlur = hoveredAgent === agent.id ? 15 : 8
        ctx.globalAlpha = agent.opacity

        // Agent circle
        ctx.fillStyle = color
        ctx.beginPath()
        ctx.arc(x, y, 15, 0, Math.PI * 2)
        ctx.fill()

        // Status indicator
        const statusColor = getStatusColor(agent.status)
        ctx.fillStyle = statusColor
        ctx.beginPath()
        ctx.arc(x + 8, y - 8, 4, 0, Math.PI * 2)
        ctx.fill()

        // Agent icon
        ctx.fillStyle = '#FFFFFF'
        ctx.font = '12px Arial'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(getAgentIcon(agent.type), x, y)

        // Connection line to Queen
        ctx.strokeStyle = color
        ctx.lineWidth = 1
        ctx.globalAlpha = 0.3
        ctx.beginPath()
        ctx.moveTo(centerX, centerY)
        ctx.lineTo(x, y)
        ctx.stroke()

        ctx.restore()

        return {
          ...agent,
          position: { x, y },
          angle: newAngle
        }
      })
    )

    animationRef.current = requestAnimationFrame(animate)
  }, [hoveredAgent])

  useEffect(() => {
    animate()
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [animate])

  // Handle canvas resize
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const resizeCanvas = () => {
      const container = canvas.parentElement
      if (container) {
        canvas.width = container.clientWidth
        canvas.height = container.clientHeight
      }
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)
    return () => window.removeEventListener('resize', resizeCanvas)
  }, [])

  // Handle mouse interaction
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    let foundAgent = null
    for (const agent of agents) {
      const distance = Math.sqrt(
        Math.pow(x - agent.position.x, 2) + Math.pow(y - agent.position.y, 2)
      )
      if (distance < 20) {
        foundAgent = agent.id
        break
      }
    }

    setHoveredAgent(foundAgent)
  }, [agents])

  const handleMouseLeave = () => {
    setHoveredAgent(null)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-bee-yellow flex items-center space-x-2">
          <Target className="w-6 h-6" />
          <span>🐝 Bee Agents Swarm</span>
        </h2>
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-neural-blue" />
          <span className="text-sm text-neural-blue">Live Swarm</span>
        </div>
      </div>

      {/* Swarm Visualization */}
      <div className="relative h-64 mb-6 overflow-hidden rounded-lg bg-bee-dark/30">
        <canvas
          ref={canvasRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          className="w-full h-full cursor-pointer"
        />
        
        {/* Hover Tooltip */}
        {hoveredAgent && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute bg-bee-dark/90 backdrop-blur-sm rounded-lg p-3 border border-neural-blue/20"
            style={{
              left: hoveredAgent ? '50%' : '0',
              top: '10px',
              transform: 'translateX(-50%)'
            }}
          >
            {(() => {
              const agent = agents.find(a => a.id === hoveredAgent)
              if (!agent) return null
              
              return (
                <div className="text-center">
                  <div className="text-lg mb-1">{getAgentIcon(agent.type)}</div>
                  <div className="text-sm font-bold text-white">{agent.id}</div>
                  <div className="text-xs text-gray-400 capitalize">{agent.type} Agent</div>
                  <div className="text-xs text-gray-300 mt-1">{agent.current_task}</div>
                </div>
              )
            })()}
          </motion.div>
        )}
      </div>

      {/* Agent List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {agents.map((agent, index) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="bee-card hover:neural-glow transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getAgentIcon(agent.type)}</span>
                <div>
                  <h3 className="font-bold text-white">{agent.id}</h3>
                  <p className={`text-sm capitalize`} style={{ color: getAgentColor(agent.type) }}>
                    {agent.type} Agent
                  </p>
                </div>
              </div>
              <div 
                className="status-indicator" 
                style={{ backgroundColor: getStatusColor(agent.status) }}
              />
            </div>

            <div className="space-y-2">
              <p className="text-sm text-gray-400 truncate">
                {agent.current_task}
              </p>

              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="text-center">
                  <p className="text-gray-400">Accuracy</p>
                  <p className="font-bold text-success-green">
                    {agent.performance_metrics.accuracy}%
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-gray-400">Speed</p>
                  <p className="font-bold text-bee-yellow">
                    {agent.performance_metrics.speed}%
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-gray-400">Memory</p>
                  <p className="font-bold text-neural-blue">
                    {agent.performance_metrics.memory_usage}MB
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Swarm Stats */}
      <div className="mt-4 grid grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <div className="text-2xl font-bold text-threat-red">
            {agents.filter(a => a.type === 'threat').length}
          </div>
          <div className="text-xs text-gray-400">Threat Agents</div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-center"
        >
          <div className="text-2xl font-bold text-neural-blue">
            {agents.filter(a => a.type === 'log').length}
          </div>
          <div className="text-xs text-gray-400">Log Agents</div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-center"
        >
          <div className="text-2xl font-bold text-neural-purple">
            {agents.filter(a => a.type === 'evolution').length}
          </div>
          <div className="text-xs text-gray-400">Evolution Agents</div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="text-center"
        >
          <div className="text-2xl font-bold text-bee-yellow">
            {agents.filter(a => a.type === 'performance').length}
          </div>
          <div className="text-xs text-gray-400">Performance Agents</div>
        </motion.div>
      </div>

      {/* Connection Status */}
      <div className="mt-4 text-center">
        <div className="flex items-center justify-center space-x-2">
          <div className={`status-indicator ${isConnected ? 'status-active' : 'status-error'}`} />
          <span className={`text-sm ${isConnected ? 'text-success-green' : 'text-threat-red'}`}>
            {isConnected ? `${agents.length} Active Agents` : 'No Live Data'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default BeeAgentsSwarm
