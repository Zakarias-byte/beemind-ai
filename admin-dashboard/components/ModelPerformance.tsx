import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Brain, Target, Zap, TrendingUp, Filter } from 'lucide-react';

interface ModelData {
  name: string;
  type: string;
  rocAuc: number;
  f1Score: number;
  count: number;
  avgTime: number;
  color: string;
}

const ModelPerformance: React.FC = () => {
  const [modelData, setModelData] = useState<ModelData[]>([]);
  const [selectedMetric, setSelectedMetric] = useState<'rocAuc' | 'f1Score' | 'count'>('rocAuc');
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('7d');

  useEffect(() => {
    // Mock model performance data
    const mockData: ModelData[] = [
      {
        name: 'RandomForest',
        type: 'Ensemble',
        rocAuc: 0.94,
        f1Score: 0.91,
        count: 12,
        avgTime: 0.8,
        color: '#22c55e'
      },
      {
        name: 'XGBoost',
        type: 'Gradient Boosting',
        rocAuc: 0.97,
        f1Score: 0.94,
        count: 8,
        avgTime: 1.2,
        color: '#3b82f6'
      },
      {
        name: 'ExtraTrees',
        type: 'Ensemble',
        rocAuc: 1.00,
        f1Score: 1.00,
        count: 6,
        avgTime: 0.9,
        color: '#f59e0b'
      },
      {
        name: 'GradientBoosting',
        type: 'Gradient Boosting',
        rocAuc: 0.89,
        f1Score: 0.87,
        count: 10,
        avgTime: 1.5,
        color: '#ef4444'
      },
      {
        name: 'LogisticRegression',
        type: 'Linear',
        rocAuc: 0.76,
        f1Score: 0.73,
        count: 4,
        avgTime: 0.3,
        color: '#8b5cf6'
      },
      {
        name: 'SVC',
        type: 'Support Vector',
        rocAuc: 0.82,
        f1Score: 0.79,
        count: 5,
        avgTime: 2.1,
        color: '#06b6d4'
      }
    ];

    setModelData(mockData);
  }, [timeRange]);

  const getMetricValue = (model: ModelData) => {
    switch (selectedMetric) {
      case 'rocAuc':
        return model.rocAuc;
      case 'f1Score':
        return model.f1Score;
      case 'count':
        return model.count;
      default:
        return model.rocAuc;
    }
  };

  const getMetricLabel = () => {
    switch (selectedMetric) {
      case 'rocAuc':
        return 'ROC AUC Score';
      case 'f1Score':
        return 'F1 Score';
      case 'count':
        return 'Usage Count';
      default:
        return 'ROC AUC Score';
    }
  };

  const formatMetricValue = (value: number) => {
    if (selectedMetric === 'count') {
      return value.toString();
    }
    return (value * 100).toFixed(1) + '%';
  };

  // Prepare data for pie chart (model type distribution)
  const typeDistribution = modelData.reduce((acc, model) => {
    const existing = acc.find(item => item.name === model.type);
    if (existing) {
      existing.value += model.count;
    } else {
      acc.push({
        name: model.type,
        value: model.count,
        color: model.color
      });
    }
    return acc;
  }, [] as { name: string; value: number; color: string }[]);

  return (
    <div className="beemind-card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-dark-100 flex items-center space-x-2">
          <Brain className="w-5 h-5 text-accent-500" />
          <span>Model Performance Analytics</span>
        </h2>

        <div className="flex items-center space-x-3">
          {/* Metric Selector */}
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value as any)}
            className="beemind-input text-sm py-1 px-2"
          >
            <option value="rocAuc">ROC AUC</option>
            <option value="f1Score">F1 Score</option>
            <option value="count">Usage Count</option>
          </select>

          {/* Time Range Selector */}
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as any)}
            className="beemind-input text-sm py-1 px-2"
          >
            <option value="24h">Last 24h</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Bar Chart */}
        <div className="lg:col-span-2">
          <div className="chart-container">
            <h3 className="text-lg font-medium text-dark-200 mb-4">
              {getMetricLabel()} by Model
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={modelData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis 
                  dataKey="name" 
                  stroke="#64748b"
                  fontSize={12}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  stroke="#64748b"
                  fontSize={12}
                  domain={selectedMetric === 'count' ? [0, 'dataMax'] : [0, 1]}
                  tickFormatter={(value) => 
                    selectedMetric === 'count' ? value.toString() : `${(value * 100).toFixed(0)}%`
                  }
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: '8px',
                    color: '#e2e8f0'
                  }}
                  formatter={(value: number) => [formatMetricValue(value), getMetricLabel()]}
                  labelFormatter={(label) => `Model: ${label}`}
                />
                <Bar 
                  dataKey={selectedMetric} 
                  fill="#3b82f6"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Model Type Distribution */}
        <div className="space-y-6">
          <div className="chart-container">
            <h3 className="text-lg font-medium text-dark-200 mb-4">
              Model Type Distribution
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={typeDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {typeDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: '8px',
                    color: '#e2e8f0'
                  }}
                  formatter={(value: number, name: string) => [
                    `${value} models`,
                    name
                  ]}
                />
              </PieChart>
            </ResponsiveContainer>
            
            {/* Legend */}
            <div className="space-y-2">
              {typeDistribution.map((entry, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: entry.color }}
                    ></div>
                    <span className="text-dark-300">{entry.name}</span>
                  </div>
                  <span className="text-dark-400">{entry.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Top Performer */}
          <div className="beemind-card bg-gradient-to-r from-green-500/10 to-blue-500/10 border-green-500/20">
            <div className="flex items-center space-x-3 mb-3">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <Target className="w-5 h-5 text-green-400" />
              </div>
              <div>
                <h4 className="font-medium text-dark-100">Top Performer</h4>
                <p className="text-sm text-dark-400">Best ROC AUC Score</p>
              </div>
            </div>
            
            {(() => {
              const topModel = modelData.reduce((prev, current) => 
                (prev.rocAuc > current.rocAuc) ? prev : current
              );
              return (
                <div>
                  <p className="text-xl font-bold text-green-400 mb-1">
                    {topModel.name}
                  </p>
                  <p className="text-sm text-dark-300 mb-2">
                    {(topModel.rocAuc * 100).toFixed(1)}% ROC AUC
                  </p>
                  <div className="flex items-center justify-between text-xs text-dark-400">
                    <span>F1: {(topModel.f1Score * 100).toFixed(1)}%</span>
                    <span>Avg: {topModel.avgTime}s</span>
                  </div>
                </div>
              );
            })()}
          </div>
        </div>
      </div>

      {/* Model Details Table */}
      <div className="mt-6 pt-6 border-t border-dark-600">
        <h3 className="text-lg font-medium text-dark-200 mb-4">
          Detailed Performance Metrics
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-dark-600">
                <th className="text-left py-3 px-4 text-dark-300 font-medium">Model</th>
                <th className="text-left py-3 px-4 text-dark-300 font-medium">Type</th>
                <th className="text-right py-3 px-4 text-dark-300 font-medium">ROC AUC</th>
                <th className="text-right py-3 px-4 text-dark-300 font-medium">F1 Score</th>
                <th className="text-right py-3 px-4 text-dark-300 font-medium">Usage</th>
                <th className="text-right py-3 px-4 text-dark-300 font-medium">Avg Time</th>
              </tr>
            </thead>
            <tbody>
              {modelData
                .sort((a, b) => b.rocAuc - a.rocAuc)
                .map((model, index) => (
                <motion.tr
                  key={model.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border-b border-dark-700 hover:bg-dark-700/50 transition-colors"
                >
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: model.color }}
                      ></div>
                      <span className="text-dark-100 font-medium">{model.name}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-dark-300">{model.type}</td>
                  <td className="py-3 px-4 text-right">
                    <span className={`font-medium ${
                      model.rocAuc >= 0.95 ? 'text-green-400' :
                      model.rocAuc >= 0.85 ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {(model.rocAuc * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <span className={`font-medium ${
                      model.f1Score >= 0.95 ? 'text-green-400' :
                      model.f1Score >= 0.85 ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {(model.f1Score * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right text-dark-300">{model.count}</td>
                  <td className="py-3 px-4 text-right text-dark-300">{model.avgTime}s</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ModelPerformance;
