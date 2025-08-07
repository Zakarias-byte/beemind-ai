import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Cpu, HardDrive, Wifi, AlertCircle, CheckCircle } from 'lucide-react';

interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  apiLatency: number;
  uptime: number;
}

const SystemHealth: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0,
    apiLatency: 0,
    uptime: 0
  });
  const [systemStatus, setSystemStatus] = useState<'healthy' | 'warning' | 'critical'>('healthy');

  useEffect(() => {
    // Simulate real-time system metrics
    const updateMetrics = () => {
      const newMetrics: SystemMetrics = {
        cpu: Math.random() * 100,
        memory: 65 + Math.random() * 20,
        disk: 45 + Math.random() * 10,
        network: Math.random() * 100,
        apiLatency: 50 + Math.random() * 100,
        uptime: Date.now() - (7 * 24 * 60 * 60 * 1000) // 7 days ago
      };

      setMetrics(newMetrics);

      // Determine system status
      if (newMetrics.cpu > 90 || newMetrics.memory > 90 || newMetrics.apiLatency > 200) {
        setSystemStatus('critical');
      } else if (newMetrics.cpu > 70 || newMetrics.memory > 80 || newMetrics.apiLatency > 150) {
        setSystemStatus('warning');
      } else {
        setSystemStatus('healthy');
      }
    };

    updateMetrics();
    const interval = setInterval(updateMetrics, 5000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-400 bg-green-500/10';
      case 'warning':
        return 'text-yellow-400 bg-yellow-500/10';
      case 'critical':
        return 'text-red-400 bg-red-500/10';
      default:
        return 'text-gray-400 bg-gray-500/10';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-4 h-4" />;
      case 'warning':
      case 'critical':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  const formatUptime = (timestamp: number) => {
    const now = Date.now();
    const diffMs = now - timestamp;
    const days = Math.floor(diffMs / (24 * 60 * 60 * 1000));
    const hours = Math.floor((diffMs % (24 * 60 * 60 * 1000)) / (60 * 60 * 1000));
    const minutes = Math.floor((diffMs % (60 * 60 * 1000)) / (60 * 1000));

    return `${days}d ${hours}h ${minutes}m`;
  };

  const MetricCard = ({ 
    title, 
    value, 
    icon: Icon, 
    color,
    unit = '%',
    threshold = { warning: 70, critical: 90 }
  }: {
    title: string;
    value: number;
    icon: React.ElementType;
    color: string;
    unit?: string;
    threshold?: { warning: number; critical: number };
  }) => {
    const getMetricStatus = () => {
      if (value >= threshold.critical) return 'critical';
      if (value >= threshold.warning) return 'warning';
      return 'healthy';
    };

    const metricStatus = getMetricStatus();
    const statusColors = {
      healthy: 'text-green-400',
      warning: 'text-yellow-400',
      critical: 'text-red-400'
    };

    return (
      <div className="bg-dark-700/50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Icon className={`w-4 h-4 ${color}`} />
            <span className="text-sm text-dark-300">{title}</span>
          </div>
          <div className={`w-2 h-2 rounded-full ${
            metricStatus === 'healthy' ? 'bg-green-500' :
            metricStatus === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
          }`}></div>
        </div>
        
        <div className="space-y-2">
          <p className={`text-2xl font-bold ${statusColors[metricStatus]}`}>
            {unit === 'ms' ? Math.round(value) : Math.round(value)}{unit}
          </p>
          
          {/* Progress bar */}
          <div className="w-full bg-dark-600 rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(value, 100)}%` }}
              transition={{ duration: 0.5 }}
              className={`h-2 rounded-full ${
                metricStatus === 'healthy' ? 'bg-green-500' :
                metricStatus === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
              }`}
            />
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="beemind-card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-dark-100 flex items-center space-x-2">
          <Activity className="w-5 h-5 text-accent-500" />
          <span>System Health</span>
        </h2>
        
        <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(systemStatus)}`}>
          {getStatusIcon(systemStatus)}
          <span className="capitalize">{systemStatus}</span>
        </div>
      </div>

      {/* System Metrics Grid */}
      <div className="grid grid-cols-1 gap-4 mb-6">
        <MetricCard
          title="CPU Usage"
          value={metrics.cpu}
          icon={Cpu}
          color="text-blue-400"
          threshold={{ warning: 70, critical: 90 }}
        />
        
        <MetricCard
          title="Memory"
          value={metrics.memory}
          icon={HardDrive}
          color="text-green-400"
          threshold={{ warning: 80, critical: 95 }}
        />
        
        <MetricCard
          title="Network"
          value={metrics.network}
          icon={Wifi}
          color="text-purple-400"
          threshold={{ warning: 80, critical: 95 }}
        />
        
        <MetricCard
          title="API Latency"
          value={metrics.apiLatency}
          icon={Activity}
          color="text-yellow-400"
          unit="ms"
          threshold={{ warning: 150, critical: 200 }}
        />
      </div>

      {/* System Info */}
      <div className="space-y-4">
        <div className="bg-dark-700/30 border border-dark-600 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-dark-400">System Uptime</span>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-green-400">Online</span>
            </div>
          </div>
          <p className="text-lg font-semibold text-dark-100">
            {formatUptime(metrics.uptime)}
          </p>
        </div>

        {/* Quick Health Summary */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-dark-400">API Status:</span>
            <span className="text-green-400 font-medium">Operational</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-dark-400">Database:</span>
            <span className="text-green-400 font-medium">Connected</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-dark-400">Blockchain:</span>
            <span className="text-green-400 font-medium">Synced</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-dark-400">Workers:</span>
            <span className="text-green-400 font-medium">Active</span>
          </div>
        </div>
      </div>

      {/* Alerts Section */}
      {systemStatus !== 'healthy' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg"
        >
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="w-4 h-4 text-yellow-400" />
            <span className="text-sm font-medium text-yellow-400">System Alert</span>
          </div>
          <p className="text-sm text-dark-300">
            {systemStatus === 'critical' 
              ? 'Critical system resources detected. Immediate attention required.'
              : 'System resources are elevated. Monitor closely.'
            }
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default SystemHealth;
