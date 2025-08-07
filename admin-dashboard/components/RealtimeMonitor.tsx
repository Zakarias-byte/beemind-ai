import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Monitor, Play, Pause, RotateCcw, Download, Filter } from 'lucide-react';

interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'success';
  category: 'drone' | 'evolution' | 'blockchain' | 'system';
  message: string;
  details?: any;
}

const RealtimeMonitor: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [filter, setFilter] = useState<'all' | 'info' | 'warning' | 'error' | 'success'>('all');
  const [categoryFilter, setCategoryFilter] = useState<'all' | 'drone' | 'evolution' | 'blockchain' | 'system'>('all');

  useEffect(() => {
    // Mock real-time log generation
    if (!isMonitoring) return;

    const generateLog = () => {
      const categories = ['drone', 'evolution', 'blockchain', 'system'];
      const levels = ['info', 'warning', 'error', 'success'];
      const messages = {
        drone: [
          'Drone drone-001 started training RandomForest model',
          'Drone drone-002 completed evaluation with ROC AUC: 0.94',
          'Drone drone-003 failed hyperparameter optimization',
          'New drone drone-006 spawned for generation 6'
        ],
        evolution: [
          'Generation 5 completed with best ROC AUC: 1.00',
          'Elite selection identified 3 top performers',
          'Diversity metrics calculated: 0.82',
          'Evolution cycle initiated for generation 6'
        ],
        blockchain: [
          'Block #5 mined successfully with nonce: 12847',
          'Chain validation completed - integrity verified',
          'New transaction added to mempool',
          'Blockchain sync status: up to date'
        ],
        system: [
          'API endpoint /generate responded in 145ms',
          'Memory usage: 67% - within normal range',
          'Database connection pool: 8/10 connections active',
          'System health check completed successfully'
        ]
      };

      const category = categories[Math.floor(Math.random() * categories.length)] as LogEntry['category'];
      const level = levels[Math.floor(Math.random() * levels.length)] as LogEntry['level'];
      const categoryMessages = messages[category];
      const message = categoryMessages[Math.floor(Math.random() * categoryMessages.length)];

      const newLog: LogEntry = {
        id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
        level,
        category,
        message,
        details: Math.random() > 0.7 ? { 
          duration: `${(Math.random() * 2000 + 100).toFixed(0)}ms`,
          memory: `${(Math.random() * 100 + 50).toFixed(1)}MB`
        } : undefined
      };

      setLogs(prev => [newLog, ...prev.slice(0, 99)]); // Keep last 100 logs
    };

    const interval = setInterval(generateLog, 2000 + Math.random() * 3000);
    return () => clearInterval(interval);
  }, [isMonitoring]);

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'success':
        return 'text-green-400 bg-green-500/10 border-green-500/20';
      case 'info':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
      case 'warning':
        return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
      case 'error':
        return 'text-red-400 bg-red-500/10 border-red-500/20';
      default:
        return 'text-gray-400 bg-gray-500/10 border-gray-500/20';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'drone':
        return 'text-purple-400 bg-purple-500/10';
      case 'evolution':
        return 'text-green-400 bg-green-500/10';
      case 'blockchain':
        return 'text-blue-400 bg-blue-500/10';
      case 'system':
        return 'text-orange-400 bg-orange-500/10';
      default:
        return 'text-gray-400 bg-gray-500/10';
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const filteredLogs = logs.filter(log => {
    const levelMatch = filter === 'all' || log.level === filter;
    const categoryMatch = categoryFilter === 'all' || log.category === categoryFilter;
    return levelMatch && categoryMatch;
  });

  const exportLogs = () => {
    const dataStr = JSON.stringify(filteredLogs, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `beemind-logs-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  return (
    <div className="beemind-card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-dark-100 flex items-center space-x-2">
          <Monitor className="w-5 h-5 text-accent-500" />
          <span>Real-time System Monitor</span>
        </h2>

        <div className="flex items-center space-x-3">
          {/* Filters */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="beemind-input text-sm py-1 px-2"
          >
            <option value="all">All Levels</option>
            <option value="info">Info</option>
            <option value="success">Success</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value as any)}
            className="beemind-input text-sm py-1 px-2"
          >
            <option value="all">All Categories</option>
            <option value="drone">Drone</option>
            <option value="evolution">Evolution</option>
            <option value="blockchain">Blockchain</option>
            <option value="system">System</option>
          </select>

          {/* Controls */}
          <button
            onClick={() => setIsMonitoring(!isMonitoring)}
            className={`beemind-button-secondary p-2 ${isMonitoring ? 'text-green-400' : 'text-gray-400'}`}
            title={isMonitoring ? 'Pause monitoring' : 'Resume monitoring'}
          >
            {isMonitoring ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>

          <button
            onClick={() => setLogs([])}
            className="beemind-button-secondary p-2"
            title="Clear logs"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          <button
            onClick={exportLogs}
            className="beemind-button-secondary p-2"
            title="Export logs"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Status Bar */}
      <div className="flex items-center justify-between mb-4 p-3 bg-dark-700/30 rounded-lg">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isMonitoring ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
            <span className="text-sm text-dark-300">
              {isMonitoring ? 'Monitoring Active' : 'Monitoring Paused'}
            </span>
          </div>
          <div className="text-sm text-dark-400">
            {filteredLogs.length} entries
          </div>
        </div>

        <div className="flex items-center space-x-4 text-xs">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-dark-400">Success</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-dark-400">Info</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <span className="text-dark-400">Warning</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <span className="text-dark-400">Error</span>
          </div>
        </div>
      </div>

      {/* Log Entries */}
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredLogs.length === 0 ? (
          <div className="text-center py-8 text-dark-400">
            <Monitor className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>No log entries match the current filters</p>
          </div>
        ) : (
          filteredLogs.map((log, index) => (
            <motion.div
              key={log.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: Math.min(index * 0.05, 0.5) }}
              className={`border rounded-lg p-3 hover:bg-dark-700/30 transition-colors ${getLevelColor(log.level)}`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(log.category)}`}>
                    {log.category}
                  </span>
                  <span className="text-xs text-dark-400">
                    {formatTime(log.timestamp)}
                  </span>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${getLevelColor(log.level)}`}>
                  {log.level}
                </span>
              </div>

              <p className="text-sm text-dark-200 mb-2">
                {log.message}
              </p>

              {log.details && (
                <div className="text-xs text-dark-400 bg-dark-800/50 rounded p-2">
                  <pre className="whitespace-pre-wrap">
                    {JSON.stringify(log.details, null, 2)}
                  </pre>
                </div>
              )}
            </motion.div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-dark-600 flex items-center justify-between text-sm text-dark-400">
        <div>
          Auto-refresh: {isMonitoring ? 'Enabled' : 'Disabled'}
        </div>
        <div>
          Last updated: {logs.length > 0 ? formatTime(logs[0].timestamp) : 'Never'}
        </div>
      </div>
    </div>
  );
};

export default RealtimeMonitor;
