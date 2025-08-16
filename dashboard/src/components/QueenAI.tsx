import { motion } from 'framer-motion'
import { Brain, Activity, Zap } from 'lucide-react'
import { useWebSocket } from '../contexts/WebSocketContext'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Text, Sphere } from '@react-three/drei'
import { useRef, useState } from 'react'
import * as THREE from 'three'

// Simple Neural Node Component
const NeuralNode = ({ position, size = 0.1, color = '#3B82F6', pulse = false }: {
  position: [number, number, number]
  size?: number
  color?: string
  pulse?: boolean
}) => {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (meshRef.current && pulse) {
      meshRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 3) * 0.2)
    }
  })

  return (
    <Sphere
      ref={meshRef}
      args={[size, 16, 16]}
      position={position}
    >
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={pulse ? 0.3 : 0.1}
        transparent
        opacity={0.8}
      />
    </Sphere>
  )
}

// Central Brain Component
const CentralBrain = ({ evolutionProgress, isConnected }: {
  evolutionProgress: number
  isConnected: boolean
}) => {
  const groupRef = useRef<THREE.Group>(null)
  const [neuralNodes] = useState(() => {
    const nodes: Array<{
      position: [number, number, number]
      size: number
      color: string
      pulse: boolean
    }> = []
    
    const radius = 2
    const layers = 3
    const nodesPerLayer = 6

    for (let layer = 0; layer < layers; layer++) {
      const layerRadius = radius * (layer + 1) / layers
      const layerHeight = (layer - layers / 2) * 0.5

      for (let i = 0; i < nodesPerLayer; i++) {
        const angle = (i / nodesPerLayer) * Math.PI * 2
        const x = Math.cos(angle) * layerRadius
        const z = Math.sin(angle) * layerRadius
        const y = layerHeight

        nodes.push({
          position: [x, y, z] as [number, number, number],
          size: 0.05 + Math.random() * 0.05,
          color: isConnected ? '#3B82F6' : '#6B7280',
          pulse: Math.random() > 0.7 && isConnected
        })
      }
    }

    // Add central node
    nodes.push({
      position: [0, 0, 0],
      size: 0.2,
      color: isConnected ? '#F59E0B' : '#6B7280',
      pulse: true
    })

    return nodes
  })

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.005
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
    }
  })

  return (
    <group ref={groupRef}>
      {/* Neural Nodes */}
      {neuralNodes.map((node, index) => (
        <NeuralNode
          key={index}
          position={node.position}
          size={node.size}
          color={node.color}
          pulse={node.pulse}
        />
      ))}

      {/* Status Text */}
      <Text
        position={[0, -3, 0]}
        fontSize={0.3}
        color={isConnected ? '#10B981' : '#EF4444'}
        anchorX="center"
        anchorY="middle"
      >
        {isConnected ? 'QUEEN ACTIVE' : 'QUEEN INACTIVE'}
      </Text>

      {/* Evolution Progress Ring */}
      <group position={[0, 0, 0]}>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[2.5, 2.7, 64]} />
          <meshStandardMaterial
            color="#3B82F6"
            transparent
            opacity={0.3}
            side={THREE.DoubleSide}
          />
        </mesh>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[2.5, 2.7, 64, 1, 0, Math.PI * 2 * evolutionProgress]} />
          <meshStandardMaterial
            color="#F59E0B"
            transparent
            opacity={0.8}
            side={THREE.DoubleSide}
          />
        </mesh>
      </group>
    </group>
  )
}

// Main Queen AI Component
const QueenAI = () => {
  const { evolutionProgress, isConnected } = useWebSocket()

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-bee-yellow flex items-center space-x-2">
          <Brain className="w-6 h-6" />
          <span>🧠 Queen AI</span>
        </h2>
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-neural-blue" />
          <span className="text-sm text-neural-blue">Neural Network</span>
        </div>
      </div>

      {/* 3D Canvas */}
      <div className="h-96 bg-bee-dark rounded-lg overflow-hidden relative">
        <Canvas
          camera={{ position: [0, 0, 8], fov: 60 }}
          style={{ background: 'transparent' }}
        >
          <ambientLight intensity={0.4} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <pointLight position={[-10, -10, -10]} intensity={0.5} color="#3B82F6" />
          
          <CentralBrain
            evolutionProgress={evolutionProgress || 0}
            isConnected={isConnected}
          />
          
          <OrbitControls
            enableZoom={true}
            enablePan={false}
            enableRotate={true}
            maxDistance={15}
            minDistance={3}
            autoRotate={false}
          />
        </Canvas>

        {/* Overlay Controls */}
        <div className="absolute top-4 right-4 flex space-x-2">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="bee-button text-xs px-3 py-1"
          >
            <Zap className="w-3 h-3 mr-1" />
            Reset View
          </motion.button>
        </div>

        {/* Status Overlay */}
        <div className="absolute bottom-4 left-4 right-4">
          <div className="bg-bee-dark/80 backdrop-blur-sm rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className={`status-indicator ${isConnected ? 'status-active' : 'status-error'}`} />
                <span className={`text-sm font-semibold ${isConnected ? 'text-success-green' : 'text-threat-red'}`}>
                  {isConnected ? 'Neural Network Active' : 'Neural Network Inactive'}
                </span>
              </div>
              <div className="text-right">
                <div className="text-sm text-neural-blue">Evolution Progress</div>
                <div className="text-lg font-bold text-bee-yellow">
                  {Math.round((evolutionProgress || 0) * 100)}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Neural Activity Stats */}
      <div className="mt-4 grid grid-cols-3 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <div className="text-2xl font-bold text-neural-blue">
            19
          </div>
          <div className="text-xs text-gray-400">Neural Nodes</div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-center"
        >
          <div className="text-2xl font-bold text-neural-purple">
            {Math.round((evolutionProgress || 0) * 100)}%
          </div>
          <div className="text-xs text-gray-400">Evolution</div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-center"
        >
          <div className="text-2xl font-bold text-bee-yellow">
            {isConnected ? 'Active' : 'Inactive'}
          </div>
          <div className="text-xs text-gray-400">Status</div>
        </motion.div>
      </div>

      {/* Connection Status */}
      <div className="mt-4 text-center">
        <div className="flex items-center justify-center space-x-2">
          <div className={`status-indicator ${isConnected ? 'status-active' : 'status-error'}`} />
          <span className={`text-sm ${isConnected ? 'text-success-green' : 'text-threat-red'}`}>
            {isConnected ? 'Live Neural Activity' : 'No Live Data'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default QueenAI
