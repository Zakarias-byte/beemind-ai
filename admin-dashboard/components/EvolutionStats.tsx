import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Zap, Target, Award, ChevronUp, ChevronDown } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface EvolutionData {
  generation: number;
  bestROC: number;
  avgROC: number;
  diversity: number;
  eliteCount: number;
}

const EvolutionStats: React.FC = () => {
  const [evolutionData, setEvolutionData] = useState<EvolutionData[]>([]);
  const [currentStats, setCurrentStats] = useState({
    totalGenerations: 0,
    bestOverallROC: 0,
    avgGenerationTime: 0,
    totalDrones: 0,
    diversityTrend: 0
  });

  // Simulate real evolution data
  useEffect(() => {
    const mockData: EvolutionData[] = [
      { generation: 1, bestROC: 0.85, avgROC: 0.72, diversity: 0.75, eliteCount: 2 },
      { generation: 2, bestROC: 0.91, avgROC: 0.78, diversity: 0.80, eliteCount: 3 },
      { generation: 3, bestROC: 0.94, avgROC: 0.82, diversity: 0.85, eliteCount: 3 },
      { generation: 4, bestROC: 0.97, avgROC: 0.86, diversity: 0.78, eliteCount: 2 },
      { generation: 5, bestROC: 1.00, avgROC: 0.89, diversity: 0.82, eliteCount: 4 },
    ];

    setEvolutionData(mockData);
    setCurrentStats({
      totalGenerations: mockData.length,
      bestOverallROC: Math.max(...mockData.map(d => d.bestROC)),
      avgGenerationTime: 1.2,
      totalDrones: mockData.length * 7,
      diversityTrend: 0.82
    });
  }, []);

  const StatCard = ({ 
    title, 
    value, 
    change, 
    icon: Icon, 
    color = 'accent',
    format = 'number'
  }: {
    title: string;
    value: number;
    change?: number;
    icon: React.ElementType;
    color?: 'accent' | 'green' | 'yellow' | 'red';
    format?: 'number' | 'percentage' | 'time';
  }) => {
    const formatValue = (val: number) => {
      switch (format) {
        case 'percentage':
          return `${(val * 100).toFixed(1)}%`;
        case 'time':
          return `${val.toFixed(1)}s`;
        default:
          return val.toLocaleString();
      }
    };

    const colorClasses = {
      accent: 'text-accent-400 bg-accent-500/10',
      green: 'text-green-400 bg-green-500/10',
      yellow: 'text-yellow-400 bg-yellow-500/10',
      red: 'text-red-400 bg-red-500/10'
    };

    return (
      <motion.div
        whileHover={{ scale: 1.02 }}
        className="beemind-card p-4"
      >
        <div className="flex items-center justify-between mb-3">
          <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
            <Icon className="w-5 h-5" />
          </div>
          {change !== undefined && (
            <div className={`flex items-center text-sm ${
              change >= 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              {change >= 0 ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              <span>{Math.abs(change).toFixed(1)}%</span>
            </div>
          )}
        </div>
        
        <div>
          <p className="text-2xl font-bold text-dark-100 mb-1">
            {formatValue(value)}
          </p>
          <p className="text-sm text-dark-400">{title}</p>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="beemind-card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-dark-100 flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-accent-500" />
            <span>Evolution Statistics</span>
          </h2>
          <div className="flex items-center space-x-2 text-sm text-dark-400">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Live</span>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <StatCard
            title="Total Generations"
            value={currentStats.totalGenerations}
            change={12.5}
            icon={Zap}
            color="accent"
          />
          <StatCard
            title="Best ROC AUC"
            value={currentStats.bestOverallROC}
            change={8.2}
            icon={Award}
            color="green"
            format="percentage"
          />
          <StatCard
            title="Avg Gen Time"
            value={currentStats.avgGenerationTime}
            change={-5.3}
            icon={Target}
            color="yellow"
            format="time"
          />
          <StatCard
            title="Total Drones"
            value={currentStats.totalDrones}
            change={15.8}
            icon={TrendingUp}
            color="accent"
          />
        </div>

        {/* Evolution Trend Chart */}
        <div className="chart-container">
          <h3 className="text-lg font-medium text-dark-200 mb-4">
            Performance Evolution
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={evolutionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis 
                dataKey="generation" 
                stroke="#64748b"
                fontSize={12}
              />
              <YAxis 
                stroke="#64748b"
                fontSize={12}
                domain={[0.5, 1]}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #475569',
                  borderRadius: '8px',
                  color: '#e2e8f0'
                }}
                labelFormatter={(label) => `Generation ${label}`}
                formatter={(value: number, name: string) => [
                  `${(value * 100).toFixed(1)}%`,
                  name === 'bestROC' ? 'Best ROC AUC' : 'Avg ROC AUC'
                ]}
              />
              <Line
                type="monotone"
                dataKey="bestROC"
                stroke="#22c55e"
                strokeWidth={3}
                dot={{ fill: '#22c55e', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#22c55e', strokeWidth: 2 }}
              />
              <Line
                type="monotone"
                dataKey="avgROC"
                stroke="#3b82f6"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Quick Stats */}
        <div className="mt-6 pt-4 border-t border-dark-600">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-green-400">
                {(currentStats.diversityTrend * 100).toFixed(0)}%
              </p>
              <p className="text-xs text-dark-400">Model Diversity</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-accent-400">
                {evolutionData.length > 0 ? evolutionData[evolutionData.length - 1].eliteCount : 0}
              </p>
              <p className="text-xs text-dark-400">Elite Drones</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-yellow-400">
                {evolutionData.length > 0 ? 
                  ((evolutionData[evolutionData.length - 1].bestROC - evolutionData[0].bestROC) * 100).toFixed(1) 
                  : 0}%
              </p>
              <p className="text-xs text-dark-400">Improvement</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EvolutionStats;
