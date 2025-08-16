import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { io, Socket } from 'socket.io-client'

interface WebSocketContextType {
  socket: Socket | null
  isConnected: boolean
  queenStatus: any
  beeAgents: any[]
  evolutionProgress: any
  performanceMetrics: any
}

const WebSocketContext = createContext<WebSocketContextType>({
  socket: null,
  isConnected: false,
  queenStatus: null,
  beeAgents: [],
  evolutionProgress: null,
  performanceMetrics: null,
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
  const [evolutionProgress, setEvolutionProgress] = useState<any>(null)
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null)

  useEffect(() => {
    // Initialize WebSocket connection
    const newSocket = io('http://localhost:8000', {
      transports: ['websocket'],
      autoConnect: true,
    })

    // Connection events
    newSocket.on('connect', () => {
      console.log('Connected to BeeMind WebSocket')
      setIsConnected(true)
    })

    newSocket.on('disconnect', () => {
      console.log('Disconnected from BeeMind WebSocket')
      setIsConnected(false)
    })

    // Queen AI status updates
    newSocket.on('queen-status', (data) => {
      setQueenStatus(data)
    })

    // Bee agents updates
    newSocket.on('bee-agents', (data) => {
      setBeeAgents(data)
    })

    // Evolution progress updates
    newSocket.on('evolution-progress', (data) => {
      setEvolutionProgress(data)
    })

    // Performance metrics updates
    newSocket.on('performance-metrics', (data) => {
      setPerformanceMetrics(data)
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
    evolutionProgress,
    performanceMetrics,
  }

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}
