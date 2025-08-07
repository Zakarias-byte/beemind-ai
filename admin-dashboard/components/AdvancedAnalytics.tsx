import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterPlot, Scatter, BarChart, Bar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { TrendingUp, Brain, Target, AlertTriangle, Zap, BarChart3, Activity, Lightbulb } from 'lucide-react';

interface AnalyticsData {
  evolutionTrends: {
    trends: Record<string, any>;
    convergence: Record<string, any>;
    movingAverages: Record<string, number[]>;
  };
  modelPerformance: {
    modelStatistics: Record<string, any>;
    recommendations: Record<string, string>;
  };
  anomalies: {
    metricAnomalies: Record<string, any>;
    performanceDrops: any[];
    totalAnomalies: number;
  };
  diversityInsights: {
    diversityTimeline: any[];
    diversityTrends: Record<string, any>;
    currentDiversity: any;
  };
  predictions: {
    predictions: Record<string, any>;
    predictionHorizon: number;
  };
}

const AdvancedAnalytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [selectedView, setSelectedView] = useState<'trends' | 'models' | 'anomalies' | 'diversity' | 'predictions'>('trends');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate advanced analytics data
    const mockAnalytics: AnalyticsData = {
      evolutionTrends: {
        trends: {
          best_roc_auc: {
            slope: 0.025,
            r_squared: 0.89,
            trend_direction: 'improving',
            significance: 'significant'
          },
          best_f1: {
            slope: 0.018,
            r_squared: 0.76,
            trend_direction: 'improving',
            significance: 'significant'
          },
          diversity_score: {
            slope: -0.008,
            r_squared: 0.45,
            trend_direction: 'declining',
            significance: 'not_significant'
          }
        },
        convergence: {
          roc_auc_variance: 0.0008,
          is_converging: false,
          plateau_detected: false,
          generations_since_improvement: 2
        },
        movingAverages: {
          roc_auc: [0.85, 0.87, 0.91, 0.94, 0.97],
          f1: [0.82, 0.84, 0.88, 0.91, 0.94],
          diversity: [0.75, 0.78, 0.76, 0.74, 0.72]
        }
      },
      modelPerformance: {
        modelStatistics: {
          'RandomForest': {
            avg_roc_auc: 0.91,
            consistency_score: 0.85,
            count: 12,
            usage_frequency: 0.35
          },
          'XGBoost': {
            avg_roc_auc: 0.94,
            consistency_score: 0.78,
            count: 8,
            usage_frequency: 0.25
          },
          'ExtraTrees': {
            avg_roc_auc: 0.96,
            consistency_score: 0.92,
            count: 6,
            usage_frequency: 0.18
          }
        },
        recommendations: {
          best_average_performer: 'ExtraTrees',
          most_consistent: 'ExtraTrees',
          most_frequently_used: 'RandomForest'
        }
      },
      anomalies: {
        metricAnomalies: {
          best_roc_auc: {
            anomaly_generations: [3],
            anomaly_values: [0.65],
            count: 1
          },
          generation_time: {
            anomaly_generations: [4],
            anomaly_values: [4.2],
            count: 1
          }
        },
        performanceDrops: [
          {
            generation: 3,
            drop_amount: 0.15,
            previous_performance: 0.89,
            current_performance: 0.74
          }
        ],
        totalAnomalies: 2
      },
      diversityInsights: {
        diversityTimeline: [
          { generation: 1, shannon_diversity: 1.2, model_types_count: 4 },
          { generation: 2, shannon_diversity: 1.4, model_types_count: 5 },
          { generation: 3, shannon_diversity: 1.1, model_types_count: 4 },
          { generation: 4, shannon_diversity: 1.3, model_types_count: 5 },
          { generation: 5, shannon_diversity: 1.0, model_types_count: 3 }
        ],
        diversityTrends: {
          shannon_trend: -0.05,
          diversity_direction: 'decreasing'
        },
        currentDiversity: {
          shannon_diversity: 1.0,
          model_types_count: 3
        }
      },
      predictions: {
        predictions: {
          best_roc_auc: {
            predicted_values: [0.98, 0.99, 1.00, 1.00, 1.00],
            future_generations: [6, 7, 8, 9, 10],
            prediction_reliability: 'high'
          },
          best_f1: {
            predicted_values: [0.95, 0.96, 0.97, 0.98, 0.99],
            future_generations: [6, 7, 8, 9, 10],
            prediction_reliability: 'medium'
          }
        },
        predictionHorizon: 5
      }
    };

    setTimeout(() => {
      setAnalyticsData(mockAnalytics);
      setIsLoading(false);
    }, 1500);
  }, []);

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'improving':
        return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'declining':
        return <TrendingUp className="w-4 h-4 text-red-400 rotate-180" />;
      default:
        return <Activity className="w-4 h-4 text-yellow-400" />;
    }
  };

  const getTrendColor = (direction: string) => {
    switch (direction) {
      case 'improving':
        return 'text-green-400 bg-green-500/10';
      case 'declining':
        return 'text-red-400 bg-red-500/10';
      default:
        return 'text-yellow-400 bg-yellow-500/10';
    }
  };

  if (isLoading) {
    return (
      <div className="beemind-card">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-accent-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-dark-300">Analyzing evolution patterns...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="beemind-card">
        <div className="text-center py-8">
          <AlertTriangle className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
          <p className="text-dark-300">Analytics data unavailable</p>
        </div>
      </div>
    );
  }

  return (
    <div className="beemind-card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-dark-100 flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-accent-500" />
          <span>Advanced Analytics</span>
        </h2>

        {/* View Selector */}
        <div className="flex items-center space-x-2">
          {[
            { key: 'trends', label: 'Trends', icon: TrendingUp },
            { key: 'models', label: 'Models', icon: Brain },
            { key: 'anomalies', label: 'Anomalies', icon: AlertTriangle },
            { key: 'diversity', label: 'Diversity', icon: Target },
            { key: 'predictions', label: 'Predictions', icon: Lightbulb }
          ].map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setSelectedView(key as any)}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1 ${
                selectedView === key
                  ? 'bg-accent-600 text-white'
                  : 'bg-dark-700 text-dark-300 hover:bg-dark-600'
              }`}
            >
              <Icon className="w-3 h-3" />
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Trends View */}
      {selectedView === 'trends' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Trend Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(analyticsData.evolutionTrends.trends).map(([metric, data]: [string, any]) => (
              <div key={metric} className={`p-4 rounded-lg border ${getTrendColor(data.trend_direction)}`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium capitalize">
                    {metric.replace('_', ' ')}
                  </span>
                  {getTrendIcon(data.trend_direction)}
                </div>
                <div className="space-y-1">
                  <p className="text-lg font-bold">
                    R² = {data.r_squared.toFixed(3)}
                  </p>
                  <p className="text-xs opacity-75">
                    Slope: {data.slope > 0 ? '+' : ''}{data.slope.toFixed(4)}
                  </p>
                  <p className="text-xs opacity-75 capitalize">
                    {data.significance}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Moving Averages Chart */}
          <div className="chart-container">
            <h3 className="text-lg font-medium text-dark-200 mb-4">Performance Trends</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analyticsData.evolutionTrends.movingAverages.roc_auc.map((value, index) => ({
                generation: index + 1,
                roc_auc: value,
                f1: analyticsData.evolutionTrends.movingAverages.f1[index],
                diversity: analyticsData.evolutionTrends.movingAverages.diversity[index]
              }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="generation" stroke="#64748b" />
                <YAxis stroke="#64748b" domain={[0, 1]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: '8px',
                    color: '#e2e8f0'
                  }}
                />
                <Line type="monotone" dataKey="roc_auc" stroke="#22c55e" strokeWidth={3} name="ROC AUC" />
                <Line type="monotone" dataKey="f1" stroke="#3b82f6" strokeWidth={2} name="F1 Score" />
                <Line type="monotone" dataKey="diversity" stroke="#f59e0b" strokeWidth={2} name="Diversity" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Convergence Analysis */}
          <div className="bg-dark-700/30 rounded-lg p-4">
            <h3 className="text-lg font-medium text-dark-200 mb-3">Convergence Analysis</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-dark-400">ROC AUC Variance</p>
                <p className="text-lg font-semibold text-dark-100">
                  {analyticsData.evolutionTrends.convergence.roc_auc_variance.toFixed(6)}
                </p>
              </div>
              <div>
                <p className="text-dark-400">Converging</p>
                <p className={`text-lg font-semibold ${
                  analyticsData.evolutionTrends.convergence.is_converging ? 'text-yellow-400' : 'text-green-400'
                }`}>
                  {analyticsData.evolutionTrends.convergence.is_converging ? 'Yes' : 'No'}
                </p>
              </div>
              <div>
                <p className="text-dark-400">Plateau Detected</p>
                <p className={`text-lg font-semibold ${
                  analyticsData.evolutionTrends.convergence.plateau_detected ? 'text-red-400' : 'text-green-400'
                }`}>
                  {analyticsData.evolutionTrends.convergence.plateau_detected ? 'Yes' : 'No'}
                </p>
              </div>
              <div>
                <p className="text-dark-400">Gens Since Improvement</p>
                <p className="text-lg font-semibold text-dark-100">
                  {analyticsData.evolutionTrends.convergence.generations_since_improvement}
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Models View */}
      {selectedView === 'models' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Model Performance Chart */}
          <div className="chart-container">
            <h3 className="text-lg font-medium text-dark-200 mb-4">Model Performance Comparison</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Object.entries(analyticsData.modelPerformance.modelStatistics).map(([name, stats]: [string, any]) => ({
                name,
                avg_roc_auc: stats.avg_roc_auc,
                consistency: stats.consistency_score,
                usage: stats.usage_frequency
              }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#64748b" />
                <YAxis stroke="#64748b" domain={[0, 1]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: '8px',
                    color: '#e2e8f0'
                  }}
                />
                <Bar dataKey="avg_roc_auc" fill="#22c55e" name="Avg ROC AUC" />
                <Bar dataKey="consistency" fill="#3b82f6" name="Consistency" />
                <Bar dataKey="usage" fill="#f59e0b" name="Usage Frequency" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Recommendations */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(analyticsData.modelPerformance.recommendations).map(([category, model]) => (
              <div key={category} className="bg-dark-700/50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-dark-300 mb-2 capitalize">
                  {category.replace('_', ' ')}
                </h4>
                <p className="text-lg font-bold text-accent-400">{model}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Anomalies View */}
      {selectedView === 'anomalies' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Anomaly Summary */}
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-3">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              <h3 className="text-lg font-medium text-red-400">Anomaly Detection</h3>
            </div>
            <p className="text-dark-300">
              Detected {analyticsData.anomalies.totalAnomalies} anomalies across evolution history
            </p>
          </div>

          {/* Performance Drops */}
          {analyticsData.anomalies.performanceDrops.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-lg font-medium text-dark-200">Significant Performance Drops</h4>
              {analyticsData.anomalies.performanceDrops.map((drop, index) => (
                <div key={index} className="bg-dark-700/30 border border-dark-600 rounded-lg p-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-dark-400">Generation</p>
                      <p className="text-lg font-semibold text-dark-100">{drop.generation}</p>
                    </div>
                    <div>
                      <p className="text-dark-400">Drop Amount</p>
                      <p className="text-lg font-semibold text-red-400">
                        -{(drop.drop_amount * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-dark-400">Previous</p>
                      <p className="text-lg font-semibold text-dark-100">
                        {(drop.previous_performance * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-dark-400">Current</p>
                      <p className="text-lg font-semibold text-dark-100">
                        {(drop.current_performance * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      )}

      {/* Diversity View */}
      {selectedView === 'diversity' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Diversity Timeline */}
          <div className="chart-container">
            <h3 className="text-lg font-medium text-dark-200 mb-4">Diversity Evolution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analyticsData.diversityInsights.diversityTimeline}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="generation" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: '8px',
                    color: '#e2e8f0'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="shannon_diversity" 
                  stroke="#8b5cf6" 
                  strokeWidth={3}
                  name="Shannon Diversity"
                />
                <Line 
                  type="monotone" 
                  dataKey="model_types_count" 
                  stroke="#06b6d4" 
                  strokeWidth={2}
                  name="Model Types Count"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Current Diversity Status */}
          <div className="bg-dark-700/30 rounded-lg p-4">
            <h3 className="text-lg font-medium text-dark-200 mb-3">Current Diversity Status</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <p className="text-dark-400">Shannon Diversity</p>
                <p className="text-2xl font-bold text-purple-400">
                  {analyticsData.diversityInsights.currentDiversity?.shannon_diversity.toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-dark-400">Model Types</p>
                <p className="text-2xl font-bold text-cyan-400">
                  {analyticsData.diversityInsights.currentDiversity?.model_types_count}
                </p>
              </div>
              <div>
                <p className="text-dark-400">Trend</p>
                <p className={`text-2xl font-bold capitalize ${
                  analyticsData.diversityInsights.diversityTrends.diversity_direction === 'increasing' 
                    ? 'text-green-400' : 'text-red-400'
                }`}>
                  {analyticsData.diversityInsights.diversityTrends.diversity_direction}
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Predictions View */}
      {selectedView === 'predictions' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Predictions Chart */}
          <div className="chart-container">
            <h3 className="text-lg font-medium text-dark-200 mb-4">
              Performance Predictions (Next {analyticsData.predictions.predictionHorizon} Generations)
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analyticsData.predictions.predictions.best_roc_auc.future_generations.map((gen, index) => ({
                generation: gen,
                predicted_roc_auc: analyticsData.predictions.predictions.best_roc_auc.predicted_values[index],
                predicted_f1: analyticsData.predictions.predictions.best_f1.predicted_values[index]
              }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="generation" stroke="#64748b" />
                <YAxis stroke="#64748b" domain={[0.9, 1]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: '8px',
                    color: '#e2e8f0'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="predicted_roc_auc" 
                  stroke="#22c55e" 
                  strokeWidth={3}
                  strokeDasharray="5 5"
                  name="Predicted ROC AUC"
                />
                <Line 
                  type="monotone" 
                  dataKey="predicted_f1" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="Predicted F1"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Prediction Reliability */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(analyticsData.predictions.predictions).map(([metric, data]: [string, any]) => (
              <div key={metric} className="bg-dark-700/30 rounded-lg p-4">
                <h4 className="text-lg font-medium text-dark-200 mb-2 capitalize">
                  {metric.replace('_', ' ')} Prediction
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-dark-400">Reliability:</span>
                    <span className={`font-medium capitalize ${
                      data.prediction_reliability === 'high' ? 'text-green-400' :
                      data.prediction_reliability === 'medium' ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {data.prediction_reliability}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-dark-400">Next Value:</span>
                    <span className="font-medium text-dark-100">
                      {(data.predicted_values[0] * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-dark-400">Final Value:</span>
                    <span className="font-medium text-dark-100">
                      {(data.predicted_values[data.predicted_values.length - 1] * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default AdvancedAnalytics;
