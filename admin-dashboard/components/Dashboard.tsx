import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Activity, 
  Brain, 
  Zap, 
  Shield, 
  TrendingUp, 
  Database,
  Settings,
  RefreshCw
} from 'lucide-react';

// Import modular components
import EvolutionStats from './EvolutionStats';
import ModelPerformance from './ModelPerformance';
import BlockchainStatus from './BlockchainStatus';
import DroneActivity from './DroneActivity';
import SystemHealth from './SystemHealth';
import RealtimeMonitor from './RealtimeMonitor';

interface DashboardProps {
  className?: string;
}

const Dashboard: React.FC<DashboardProps> = ({ className = '' }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [systemStatus, setSystemStatus] = useState<'online' | 'offline' | 'warning'>('online');

  // Simulate data loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setIsLoading(true);
    setLastUpdate(new Date());
    
    // Simulate refresh
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="relative">
            <div className="w-16 h-16 border-4 border-accent-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <Brain className="w-8 h-8 text-accent-500 absolute top-4 left-1/2 transform -translate-x-1/2" />
          </div>
          <h2 className="text-xl font-semibold text-dark-100 mb-2">
            Initializing BeeMind Dashboard
          </h2>
          <p className="text-dark-400">Loading evolution data and system status...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-900 ${className}`}>
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass border-b border-dark-600 px-6 py-4"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Brain className="w-8 h-8 text-accent-500" />
                <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full status-${systemStatus}`}></div>
              </div>
              <div>
                <h1 className="text-2xl font-bold gradient-text">
                  BeeMind Dashboard
                </h1>
                <p className="text-sm text-dark-400">
                  AI Evolution Monitoring & Analytics
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-dark-300">
                Last Updated
              </p>
              <p className="text-xs text-dark-500">
                {lastUpdate.toLocaleTimeString()}
              </p>
            </div>
            
            <button
              onClick={handleRefresh}
              className="beemind-button-secondary p-2"
              title="Refresh Dashboard"
            >
              <RefreshCw className="w-4 h-4" />
            </button>

            <button className="beemind-button-secondary p-2" title="Settings">
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </motion.header>

      {/* Main Dashboard Grid */}
      <main className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* System Health - Full width on mobile, 4 cols on desktop */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-4"
          >
            <SystemHealth />
          </motion.div>

          {/* Evolution Stats - Full width on mobile, 4 cols on desktop */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-4"
          >
            <EvolutionStats />
          </motion.div>

          {/* Blockchain Status - Full width on mobile, 4 cols on desktop */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-4"
          >
            <BlockchainStatus />
          </motion.div>

          {/* Model Performance - Full width on mobile, 8 cols on desktop */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="lg:col-span-8"
          >
            <ModelPerformance />
          </motion.div>

          {/* Drone Activity - Full width on mobile, 4 cols on desktop */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="lg:col-span-4"
          >
            <DroneActivity />
          </motion.div>

          {/* Realtime Monitor - Full width */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="lg:col-span-12"
          >
            <RealtimeMonitor />
          </motion.div>

        </div>
      </main>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="glass border-t border-dark-600 px-6 py-4 mt-8"
      >
        <div className="flex items-center justify-between text-sm text-dark-400">
          <div className="flex items-center space-x-4">
            <span>BeeMind v1.0.0</span>
            <span>•</span>
            <span>Evolutionary AI System</span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <Shield className="w-3 h-3" />
              <span>Blockchain Secured</span>
            </span>
          </div>
          
          <div className="flex items-center space-x-4">
            <span>Status: </span>
            <div className="flex items-center space-x-1">
              <div className={`w-2 h-2 rounded-full status-${systemStatus}`}></div>
              <span className="capitalize">{systemStatus}</span>
            </div>
          </div>
        </div>
      </motion.footer>
    </div>
  );
};

export default Dashboard;
