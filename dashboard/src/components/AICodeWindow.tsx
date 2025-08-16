import { motion, AnimatePresence } from 'framer-motion'
import { Code, Terminal, Play, Pause, RotateCcw } from 'lucide-react'
import { useWebSocket } from '../contexts/WebSocketContext'
import { useRef, useEffect, useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface CodeLine {
  id: string
  content: string
  language: 'python' | 'javascript' | 'bash' | 'json'
  timestamp: number
  type: 'output' | 'error' | 'success' | 'info'
  isTyping: boolean
  isComplete: boolean
}

const AICodeWindow = () => {
  const { isConnected } = useWebSocket()
  const [codeLines, setCodeLines] = useState<CodeLine[]>([])
  const [isGenerating, setIsGenerating] = useState(true)
  const [currentLineIndex, setCurrentLineIndex] = useState(0)
  const [typingProgress, setTypingProgress] = useState(0)
  const [generationProgress, setGenerationProgress] = useState(0)
  const scrollRef = useRef<HTMLDivElement>(null)

  // Mock AI code generation data
  const mockCodeGeneration = [
    {
      content: '🐝 ThreatBie-147 created...',
      language: 'bash' as const,
      type: 'info' as const,
      delay: 500
    },
    {
      content: `def analyze_threat_pattern(data):
    """Analyze network traffic for threat patterns"""
    threat_score = 0
    for packet in data:
        if packet.source_ip in blacklist:
            threat_score += 10
        if packet.port in suspicious_ports:
            threat_score += 5
    return threat_score > threshold`,
      language: 'python' as const,
      type: 'output' as const,
      delay: 2000
    },
    {
      content: '🧠 Rule: IF src_ip ∈ blacklist THEN raise alert',
      language: 'bash' as const,
      type: 'info' as const,
      delay: 800
    },
    {
      content: `{
  "threat_detected": true,
  "confidence": 0.94,
  "source_ip": "192.168.1.100",
  "timestamp": "2024-01-15T14:23:45Z",
  "severity": "high"
}`,
      language: 'json' as const,
      type: 'success' as const,
      delay: 1500
    },
    {
      content: '🔐 Blockchain hash: 0x7f3a... logged...',
      language: 'bash' as const,
      type: 'info' as const,
      delay: 600
    },
    {
      content: `// Performance optimization applied
const optimizeModel = (model) => {
  const optimized = model.clone();
  optimized.setOptimizationLevel('high');
  optimized.enableCaching();
  return optimized;
};`,
      language: 'javascript' as const,
      type: 'output' as const,
      delay: 2500
    },
    {
      content: '⚡ Performance optimization applied',
      language: 'bash' as const,
      type: 'success' as const,
      delay: 700
    },
    {
      content: `def evolve_population(population, generations):
    """Evolve neural network population"""
    for gen in range(generations):
        # Selection
        parents = tournament_selection(population)
        
        # Crossover
        offspring = crossover(parents)
        
        # Mutation
        offspring = mutate(offspring)
        
        # Evaluation
        fitness = evaluate(offspring)
        
        # Replacement
        population = replace(population, offspring)
    
    return population`,
      language: 'python' as const,
      type: 'output' as const,
      delay: 3000
    },
    {
      content: '🧬 Evolution generation 15 completed',
      language: 'bash' as const,
      type: 'success' as const,
      delay: 900
    },
    {
      content: '📊 Model accuracy improved to 94.2%',
      language: 'bash' as const,
      type: 'success' as const,
      delay: 800
    },
    {
      content: '🛡️ New threat pattern detected',
      language: 'bash' as const,
      type: 'error' as const,
      delay: 1000
    },
    {
      content: '🔍 Analyzing network traffic...',
      language: 'bash' as const,
      type: 'info' as const,
      delay: 1200
    }
  ]

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [codeLines])

  // Simulate code generation
  useEffect(() => {
    if (!isGenerating) return

    const generateCode = async () => {
      for (let i = 0; i < mockCodeGeneration.length; i++) {
        const codeItem = mockCodeGeneration[i]
        
        // Add new line
        const newLine: CodeLine = {
          id: `line-${Date.now()}-${i}`,
          content: '',
          language: codeItem.language,
          timestamp: Date.now(),
          type: codeItem.type,
          isTyping: true,
          isComplete: false
        }

        setCodeLines(prev => [...prev, newLine])
        setCurrentLineIndex(i)

        // Simulate typing animation
        const content = codeItem.content
        for (let j = 0; j <= content.length; j++) {
          await new Promise(resolve => setTimeout(resolve, 50))
          setCodeLines(prev => 
            prev.map((line, index) => 
              index === prev.length - 1 
                ? { ...line, content: content.slice(0, j) }
                : line
            )
          )
          setTypingProgress((j / content.length) * 100)
        }

        // Mark line as complete
        setCodeLines(prev => 
          prev.map((line, index) => 
            index === prev.length - 1 
              ? { ...line, isTyping: false, isComplete: true }
              : line
          )
        )

        // Update generation progress
        setGenerationProgress(((i + 1) / mockCodeGeneration.length) * 100)

        // Wait before next line
        await new Promise(resolve => setTimeout(resolve, codeItem.delay))
      }

      // Reset for continuous generation
      setTimeout(() => {
        setCodeLines([])
        setCurrentLineIndex(0)
        setTypingProgress(0)
        setGenerationProgress(0)
      }, 5000)
    }

    generateCode()
  }, [isGenerating])

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'error': return 'text-threat-red'
      case 'success': return 'text-success-green'
      case 'info': return 'text-neural-blue'
      case 'output': return 'text-bee-yellow'
      default: return 'text-gray-400'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'error': return '❌'
      case 'success': return '✅'
      case 'info': return 'ℹ️'
      case 'output': return '💻'
      default: return '>'
    }
  }

  const toggleGeneration = () => {
    setIsGenerating(!isGenerating)
  }

  const resetGeneration = () => {
    setCodeLines([])
    setCurrentLineIndex(0)
    setTypingProgress(0)
    setGenerationProgress(0)
    setIsGenerating(true)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-bee-yellow flex items-center space-x-2">
          <Code className="w-5 h-5" />
          <span>💻 AI Code Window</span>
        </h2>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-neural-blue" />
            <span className="text-sm text-neural-blue">
              {isGenerating ? 'Generating...' : 'Paused'}
            </span>
          </div>
          <div className="flex space-x-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={toggleGeneration}
              className="bee-button text-xs px-3 py-1"
            >
              {isGenerating ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={resetGeneration}
              className="bee-button text-xs px-3 py-1"
            >
              <RotateCcw className="w-3 h-3" />
            </motion.button>
          </div>
        </div>
      </div>

      {/* Code Window */}
      <div className="h-64 bg-bee-dark rounded-lg overflow-hidden relative">
        {/* Terminal Header */}
        <div className="flex items-center space-x-2 p-3 pb-2 border-b border-neural-blue/20">
          <div className="flex space-x-1">
            <div className="w-3 h-3 bg-threat-red rounded-full"></div>
            <div className="w-3 h-3 bg-warning-orange rounded-full"></div>
            <div className="w-3 h-3 bg-success-green rounded-full"></div>
          </div>
          <span className="text-xs text-gray-400 ml-2">BeeMind AI Terminal</span>
          <div className="ml-auto flex items-center space-x-2">
            <div className={`status-indicator ${isConnected ? 'status-active' : 'status-error'}`} />
            <span className="text-xs text-gray-400">
              {isConnected ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>

        {/* Code Output */}
        <div 
          ref={scrollRef}
          className="h-full overflow-y-auto p-4 space-y-1"
        >
          <AnimatePresence>
                         {codeLines.map((line) => (
              <motion.div
                key={line.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
                className="flex items-start space-x-2"
              >
                <span className="text-neural-blue text-xs mt-1 flex-shrink-0">
                  {getTypeIcon(line.type)}
                </span>
                
                <div className="flex-1 min-w-0">
                  {line.language === 'bash' ? (
                    <span className={`text-sm font-mono ${getTypeColor(line.type)}`}>
                      {line.content}
                      {line.isTyping && (
                        <motion.span
                          animate={{ opacity: [1, 0, 1] }}
                          transition={{ duration: 0.8, repeat: Infinity }}
                          className="ml-1"
                        >
                          |
                        </motion.span>
                      )}
                    </span>
                  ) : (
                    <div className="relative">
                      <SyntaxHighlighter
                        language={line.language}
                        style={tomorrow}
                        customStyle={{
                          margin: 0,
                          padding: '8px 12px',
                          fontSize: '12px',
                          borderRadius: '6px',
                          backgroundColor: 'rgba(0, 0, 0, 0.3)',
                          border: '1px solid rgba(59, 130, 246, 0.2)'
                        }}
                        showLineNumbers={false}
                      >
                        {line.content}
                      </SyntaxHighlighter>
                      {line.isTyping && (
                        <motion.div
                          animate={{ opacity: [1, 0, 1] }}
                          transition={{ duration: 0.8, repeat: Infinity }}
                          className="absolute top-2 right-2 w-2 h-4 bg-neural-blue"
                        />
                      )}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Cursor Animation */}
          {isGenerating && (
            <motion.div
              animate={{ opacity: [1, 0, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
              className="flex items-center space-x-2 mt-2"
            >
                             <span className="text-neural-blue text-xs">{'>'}</span>
              <span className="text-neural-blue/80 text-sm">Waiting for next generation...</span>
            </motion.div>
          )}
        </div>
      </div>

      {/* Status Bar */}
      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className={`status-indicator ${isConnected ? 'status-active' : 'status-error'}`} />
          <span className={`text-sm ${isConnected ? 'text-success-green' : 'text-threat-red'}`}>
            {isConnected ? 'AI Active' : 'AI Inactive'}
          </span>
        </div>
        <div className="flex items-center space-x-4 text-xs text-gray-400">
          <span>Lines: {codeLines.length}</span>
          <span>Python/JS/JSON</span>
          <span>UTF-8</span>
        </div>
      </div>

      {/* Code Generation Progress */}
      <div className="mt-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-gray-400">Code Generation</span>
          <span className="text-xs text-neural-blue">{Math.round(generationProgress)}%</span>
        </div>
        <div className="w-full bg-bee-dark rounded-full h-1">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${generationProgress}%` }}
            transition={{ duration: 0.5 }}
            className="bg-gradient-to-r from-neural-blue to-neural-purple h-1 rounded-full"
          />
        </div>
      </div>

      {/* Typing Progress */}
      {currentLineIndex < mockCodeGeneration.length && (
        <div className="mt-2">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-400">Typing Progress</span>
            <span className="text-xs text-bee-yellow">{Math.round(typingProgress)}%</span>
          </div>
          <div className="w-full bg-bee-dark rounded-full h-1">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${typingProgress}%` }}
              transition={{ duration: 0.3 }}
              className="bg-gradient-to-r from-bee-yellow to-warning-orange h-1 rounded-full"
            />
          </div>
        </div>
      )}

      {/* Generation Stats */}
      <div className="mt-4 grid grid-cols-3 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <div className="text-lg font-bold text-neural-blue">
            {codeLines.filter(l => l.language === 'python').length}
          </div>
          <div className="text-xs text-gray-400">Python</div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-center"
        >
          <div className="text-lg font-bold text-bee-yellow">
            {codeLines.filter(l => l.language === 'javascript').length}
          </div>
          <div className="text-xs text-gray-400">JavaScript</div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-center"
        >
          <div className="text-lg font-bold text-success-green">
            {codeLines.filter(l => l.type === 'success').length}
          </div>
          <div className="text-xs text-gray-400">Success</div>
        </motion.div>
      </div>
    </div>
  )
}

export default AICodeWindow
