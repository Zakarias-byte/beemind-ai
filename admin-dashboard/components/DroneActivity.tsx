import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Zap, Users, Activity, Clock, Play, Pause, RotateCcw } from 'lucide-react';

interface DroneData {
  id: string;
  status: 'active' | 'idle' | 'training' | 'evaluating';
  modelType: string;
  currentTask: string;
  progress: number;
  rocAuc: number;
  startTime: string;
  estimatedCompletion: string;
}

const DroneActivity: React.FC = () => {
  const [drones, setDrones] = useState<DroneData[]>([]);
  const [totalStats, setTotalStats] = useState({
    activeDrones: 0,
    idleDrones: 0,
    totalTasks: 0,
    avgPerformance: 0
  });
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    // Mock drone data
    const mockDrones: DroneData[] = [
      {
        id: 'drone-001',
        status: 'training',
        modelType: 'RandomForest',
        currentTask: 'Hyperparameter optimization',
        progress: 75,
        rocAuc: 0.94,
        startTime: new Date(Date.now() - 180000).toISOString(),
        estimatedCompletion: new Date(Date.now() + 60000).toISOString()
      },
      {
        id: 'drone-002',
        status: 'evaluating',
        modelType: 'XGBoost',
        currentTask: 'Model validation',
        progress: 45,
        rocAuc: 0.97,
        startTime: new Date(Date.now() - 120000).toISOString(),
        estimatedCompletion: new Date(Date.now() + 90000).toISOString()
      },
      {
        id: 'drone-003',
        status: 'active',
        modelType: 'ExtraTrees',
        currentTask: 'Feature selection',
        progress: 90,
        rocAuc: 1.00,
        startTime: new Date(Date.now() - 300000).toISOString(),
        estimatedCompletion: new Date(Date.now() + 30000).toISOString()
      },
      {
        id: 'drone-004',
        status: 'idle',
        modelType: 'SVC',
        currentTask: 'Waiting for assignment',
        progress: 0,
        rocAuc: 0.82,
        startTime: new Date(Date.now() - 600000).toISOString(),
        estimatedCompletion: ''
      },
      {
        id: 'drone-005',
        status: 'training',
        modelType: 'GradientBoosting',
        currentTask: 'Cross-validation',
        progress: 30,
        rocAuc: 0.89,
        startTime: new Date(Date.now() - 90000).toISOString(),
        estimatedCompletion: new Date(Date.now() + 150000).toISOString()
      }
    ];

    setDrones(mockDrones);
    
    const activeDrones = mockDrones.filter(d => d.status !== 'idle').length;
    const idleDrones = mockDrones.filter(d => d.status === 'idle').length;
    const avgPerformance = mockDrones.reduce((sum, d) => sum + d.rocAuc, 0) / mockDrones.length;

    setTotalStats({
      activeDrones,
      idleDrones,
      totalTasks: mockDrones.length,
      avgPerformance
    });
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-400 bg-green-500/10';
      case 'training':
        return 'text-blue-400 bg-blue-500/10';
      case 'evaluating':
        return 'text-yellow-400 bg-yellow-500/10';
      case 'idle':
        return 'text-gray-400 bg-gray-500/10';
      default:
        return 'text-gray-400 bg-gray-500/10';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Play className="w-3 h-3" />;
      case 'training':
        return <Activity className="w-3 h-3" />;
      case 'evaluating':
        return <RotateCcw className="w-3 h-3 animate-spin" />;
      case 'idle':
        return <Pause className="w-3 h-3" />;
      default:
        return <Pause className="w-3 h-3" />;
    }
  };

  const formatTime = (timestamp: string) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = Math.abs(now.getTime() - date.getTime());
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return '< 1m';
    if (diffMins < 60) return `${diffMins}m`;
    return `${Math.floor(diffMins / 60)}h ${diffMins % 60}m`;
  };

  const startGeneration = () => {
    setIsGenerating(true);
    // Simulate generation process
    setTimeout(() => {
      setIsGenerating(false);
      // Update drone statuses
      setDrones(prev => prev.map(drone => ({
        ...drone,
        status: drone.status === 'idle' ? 'training' : drone.status,
        progress: drone.status === 'idle' ? 10 : drone.progress
      })));
    }, 3000);
  };

  return (
    <div className="beemind-card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-dark-100 flex items-center space-x-2">
          <Users className="w-5 h-5 text-accent-500" />
          <span>Drone Activity</span>
        </h2>
        
        <button
          onClick={startGeneration}
          disabled={isGenerating}
          className="beemind-button-primary text-sm py-2 px-3"
        >
          {isGenerating ? (
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Generating...</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <Zap className="w-4 h-4" />
              <span>New Generation</span>
            </div>
          )}
        </button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-dark-700/50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Activity className="w-4 h-4 text-green-400" />
            <span className="text-sm text-dark-300">Active Drones</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">
            {totalStats.activeDrones}
          </p>
        </div>

        <div className="bg-dark-700/50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Pause className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-dark-300">Idle Drones</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">
            {totalStats.idleDrones}
          </p>
        </div>
      </div>

      {/* Average Performance */}
      <div className="bg-gradient-to-r from-accent-500/10 to-green-500/10 border border-accent-500/20 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-dark-100 mb-1">
              Average Performance
            </h3>
            <p className="text-sm text-dark-400">
              Across all active drones
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-accent-400">
              {(totalStats.avgPerformance * 100).toFixed(1)}%
            </p>
            <p className="text-sm text-dark-400">ROC AUC</p>
          </div>
        </div>
      </div>

      {/* Drone List */}
      <div className="space-y-3">
        <h3 className="text-lg font-medium text-dark-200">Individual Drones</h3>
        
        {drones.map((drone, index) => (
          <motion.div
            key={drone.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-dark-700/30 border border-dark-600 rounded-lg p-4 hover:bg-dark-700/50 transition-colors"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(drone.status)}`}>
                  {getStatusIcon(drone.status)}
                  <span className="capitalize">{drone.status}</span>
                </div>
                <span className="font-medium text-dark-100">{drone.id}</span>
              </div>
              
              <div className="text-right">
                <p className="text-sm font-medium text-dark-200">
                  {(drone.rocAuc * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-dark-400">ROC AUC</p>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-2 text-sm mb-3">
              <div className="flex justify-between">
                <span className="text-dark-400">Model:</span>
                <span className="text-dark-200">{drone.modelType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-400">Task:</span>
                <span className="text-dark-200">{drone.currentTask}</span>
              </div>
              {drone.status !== 'idle' && (
                <>
                  <div className="flex justify-between">
                    <span className="text-dark-400">Runtime:</span>
                    <span className="text-dark-200">{formatTime(drone.startTime)}</span>
                  </div>
                  {drone.estimatedCompletion && (
                    <div className="flex justify-between">
                      <span className="text-dark-400">ETA:</span>
                      <span className="text-dark-200">{formatTime(drone.estimatedCompletion)}</span>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Progress Bar */}
            {drone.status !== 'idle' && (
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-dark-400">Progress</span>
                  <span className="text-dark-300">{drone.progress}%</span>
                </div>
                <div className="w-full bg-dark-600 rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${drone.progress}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className="bg-gradient-to-r from-accent-500 to-green-500 h-2 rounded-full"
                  />
                </div>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mt-6 pt-4 border-t border-dark-600">
        <div className="flex items-center justify-between text-sm">
          <span className="text-dark-400">
            {totalStats.activeDrones} of {totalStats.totalTasks} drones active
          </span>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-dark-300">Real-time monitoring</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DroneActivity;
