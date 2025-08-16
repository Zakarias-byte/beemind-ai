import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { io, Socket } from 'socket.io-client'

interface WebSocketContextType {
  socket: Socket | null
  isConnected: boolean
  queenStatus: any
  beeAgents: any[]
  liveLogs: any[]
  evolutionProgress: number
  performanceMetrics: any
  evolutionStats: any
}

const WebSocketContext = createContext<WebSocketContextType>({
  socket: null,
  isConnected: false,
  queenStatus: null,
  beeAgents: [],
  liveLogs: [],
  evolutionProgress: 0,
  performanceMetrics: null,
  evolutionStats: null
})

export const useWebSocket = () => useContext(WebSocketContext)

interface WebSocketProviderProps {
  children: ReactNode
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [queenStatus, setQueenStatus] = useState<any>(null)
  const [beeAgents, setBeeAgents] = useState<any[]>([])
  const [liveLogs, setLiveLogs] = useState<any[]>([])
  const [evolutionProgress, setEvolutionProgress] = useState(0)
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null)
  const [evolutionStats, setEvolutionStats] = useState<any>(null)

  useEffect(() => {
    // Initialize Socket.IO connection to dashboard backend
    const newSocket = io('http://localhost:8001/ws', {
      transports: ['websocket', 'polling'],
      autoConnect: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
      path: '/ws/socket.io'
    })

    // Connection events
    newSocket.on('connect', () => {
      console.log('Connected to BeeMind Dashboard WebSocket server')
      setIsConnected(true)
      
      // Request initial data
      newSocket.emit('request_queen_status')
      newSocket.emit('request_bee_agents')
      newSocket.emit('request_live_logs')
      newSocket.emit('request_performance_metrics')
      newSocket.emit('request_evolution_stats')
    })

    newSocket.on('disconnect', () => {
      console.log('Disconnected from BeeMind Dashboard WebSocket server')
      setIsConnected(false)
    })

    newSocket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      setIsConnected(false)
    })

    // Queen AI status updates
    newSocket.on('queen_status', (data) => {
      console.log('Received queen status:', data)
      setQueenStatus(data)
      setEvolutionProgress(data.evolution_progress || 0)
    })

    // Bee agents updates
    newSocket.on('bee_agents', (data) => {
      console.log('Received bee agents:', data)
      setBeeAgents(data)
    })

    // Live logs updates
    newSocket.on('live_logs', (data) => {
      console.log('Received live logs:', data)
      if (Array.isArray(data)) {
        setLiveLogs(prev => {
          const newLogs = [...prev, ...data]
          // Keep only last 100 logs
          return newLogs.slice(-100)
        })
      }
    })

    // Performance metrics updates
    newSocket.on('performance_metrics', (data) => {
      console.log('Received performance metrics:', data)
      setPerformanceMetrics(data)
    })

    // Evolution stats updates
    newSocket.on('evolution_stats', (data) => {
      console.log('Received evolution stats:', data)
      setEvolutionStats(data)
    })

    // Evolution progress updates
    newSocket.on('evolution_progress', (data) => {
      console.log('Received evolution progress:', data)
      setEvolutionProgress(data.progress || 0)
    })

    // AI code generation events
    newSocket.on('ai_code_generation', (data) => {
      console.log('Received AI code generation:', data)
    })

    // Threat detection events
    newSocket.on('threat_detection', (data) => {
      console.log('Received threat detection:', data)
    })

    // Error handling
    newSocket.on('error', (error) => {
      console.error('WebSocket error:', error)
    })

    setSocket(newSocket)

    // Cleanup on unmount
    return () => {
      newSocket.close()
    }
  }, [])

  const value = {
    socket,
    isConnected,
    queenStatus,
    beeAgents,
    liveLogs,
    evolutionProgress,
    performanceMetrics,
    evolutionStats
  }

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}
