import { motion } from 'framer-motion'
import QueenAI from './QueenAI'
import BeeAgentsSwarm from './BeeAgentsSwarm'
import LiveAgentLogs from './LiveAgentLogs'
import AICodeWindow from './AICodeWindow'
import EventsTable from './EventsTable'
import RealtimeCharts from './RealtimeCharts'

const Dashboard = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <h1 className="text-4xl font-bold text-glow text-bee-yellow mb-2">
          🧠 Queen AI "Hjernen"
        </h1>
        <p className="text-neural-blue">
          3D pulserende node med sirkulerende agents
        </p>
      </motion.div>

      {/* Queen AI Section */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.7, delay: 0.2 }}
        className="bee-card neural-glow"
      >
        <QueenAI />
      </motion.div>

      {/* Bee Agents Swarm */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.4 }}
        className="bee-card"
      >
        <BeeAgentsSwarm />
      </motion.div>

      {/* Middle Section - Logs and Code Window */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.6 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        {/* Live Agent Logs */}
        <div className="bee-card">
          <LiveAgentLogs />
        </div>

        {/* AI Code Window */}
        <div className="bee-card">
          <AICodeWindow />
        </div>
      </motion.div>

      {/* Bottom Section - Events and Charts */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.8 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        {/* Events Table */}
        <div className="bee-card">
          <EventsTable />
        </div>

        {/* Realtime Charts */}
        <div className="bee-card">
          <RealtimeCharts />
        </div>
      </motion.div>
    </div>
  )
}

export default Dashboard
