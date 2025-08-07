"""
Advanced Analytics Engine for BeeMind AI Evolution
Provides statistical analysis, trend detection, and performance insights
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from scipy import stats
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import json
import warnings
warnings.filterwarnings('ignore')

class BeeMindAnalyticsEngine:
    """
    Advanced analytics engine for BeeMind evolution analysis
    """
    
    def __init__(self):
        self.evolution_history = []
        self.model_performance_cache = {}
        self.trend_analysis_cache = {}
    
    def add_generation_data(self, generation_data: Dict[str, Any]):
        """
        Add generation data to analytics history
        
        Args:
            generation_data: Complete generation data including drones and performance
        """
        # Standardize generation data format
        standardized_data = {
            'generation': generation_data.get('generation', len(self.evolution_history)),
            'timestamp': generation_data.get('timestamp', datetime.now().isoformat()),
            'drones': generation_data.get('drones', []),
            'best_roc_auc': generation_data.get('best_roc_auc', 0.0),
            'avg_roc_auc': generation_data.get('avg_roc_auc', 0.0),
            'best_f1': generation_data.get('best_f1', 0.0),
            'avg_f1': generation_data.get('avg_f1', 0.0),
            'diversity_score': generation_data.get('diversity_score', 0.0),
            'generation_time': generation_data.get('generation_time', 0.0),
            'elite_count': generation_data.get('elite_count', 0)
        }
        
        self.evolution_history.append(standardized_data)
        
        # Clear caches when new data is added
        self.model_performance_cache.clear()
        self.trend_analysis_cache.clear()
    
    def calculate_evolution_trends(self, window_size: int = 5) -> Dict[str, Any]:
        """
        Calculate evolution trends and patterns
        
        Args:
            window_size: Moving average window size
            
        Returns:
            Dictionary with trend analysis results
        """
        if len(self.evolution_history) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(self.evolution_history)
        
        # Calculate moving averages
        df['roc_auc_ma'] = df['best_roc_auc'].rolling(window=window_size, min_periods=1).mean()
        df['f1_ma'] = df['best_f1'].rolling(window=window_size, min_periods=1).mean()
        df['diversity_ma'] = df['diversity_score'].rolling(window=window_size, min_periods=1).mean()
        
        # Calculate trends (slope of linear regression)
        generations = np.array(df['generation'])
        
        trends = {}
        for metric in ['best_roc_auc', 'best_f1', 'diversity_score', 'generation_time']:
            if metric in df.columns:
                values = np.array(df[metric])
                if len(values) > 1:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(generations, values)
                    trends[metric] = {
                        'slope': slope,
                        'r_squared': r_value ** 2,
                        'p_value': p_value,
                        'trend_direction': 'improving' if slope > 0 else 'declining' if slope < 0 else 'stable',
                        'significance': 'significant' if p_value < 0.05 else 'not_significant'
                    }
        
        # Calculate convergence metrics
        recent_generations = df.tail(min(10, len(df)))
        convergence_analysis = {
            'roc_auc_variance': recent_generations['best_roc_auc'].var(),
            'f1_variance': recent_generations['best_f1'].var(),
            'is_converging': recent_generations['best_roc_auc'].var() < 0.001,
            'plateau_detected': self._detect_plateau(df['best_roc_auc'].values),
            'generations_since_improvement': self._generations_since_improvement(df)
        }
        
        return {
            'trends': trends,
            'convergence': convergence_analysis,
            'moving_averages': {
                'roc_auc': df['roc_auc_ma'].tolist(),
                'f1': df['f1_ma'].tolist(),
                'diversity': df['diversity_ma'].tolist()
            },
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def analyze_model_performance_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns in model performance across generations
        
        Returns:
            Dictionary with model performance analysis
        """
        if not self.evolution_history:
            return {"error": "No evolution data available"}
        
        # Aggregate model performance data
        model_stats = {}
        all_performances = []
        
        for gen_data in self.evolution_history:
            for drone in gen_data.get('drones', []):
                model_type = drone.get('model_type', 'unknown')
                roc_auc = drone.get('roc_auc', 0.0)
                f1_score = drone.get('f1_score', 0.0)
                
                if model_type not in model_stats:
                    model_stats[model_type] = {
                        'performances': [],
                        'generations_used': [],
                        'total_count': 0
                    }
                
                model_stats[model_type]['performances'].append({
                    'roc_auc': roc_auc,
                    'f1_score': f1_score,
                    'generation': gen_data['generation']
                })
                model_stats[model_type]['generations_used'].append(gen_data['generation'])
                model_stats[model_type]['total_count'] += 1
                
                all_performances.append({
                    'model_type': model_type,
                    'roc_auc': roc_auc,
                    'f1_score': f1_score,
                    'generation': gen_data['generation']
                })
        
        # Calculate statistics for each model type
        model_analysis = {}
        for model_type, stats_data in model_stats.items():
            performances = stats_data['performances']
            roc_scores = [p['roc_auc'] for p in performances]
            f1_scores = [p['f1_score'] for p in performances]
            
            model_analysis[model_type] = {
                'count': len(performances),
                'avg_roc_auc': np.mean(roc_scores),
                'std_roc_auc': np.std(roc_scores),
                'max_roc_auc': np.max(roc_scores),
                'min_roc_auc': np.min(roc_scores),
                'avg_f1': np.mean(f1_scores),
                'std_f1': np.std(f1_scores),
                'max_f1': np.max(f1_scores),
                'min_f1': np.min(f1_scores),
                'consistency_score': 1.0 - (np.std(roc_scores) / (np.mean(roc_scores) + 1e-8)),
                'generations_active': len(set(stats_data['generations_used'])),
                'usage_frequency': len(performances) / len(self.evolution_history)
            }
        
        # Identify best performing model types
        if model_analysis:
            best_avg_model = max(model_analysis.keys(), key=lambda k: model_analysis[k]['avg_roc_auc'])
            most_consistent_model = max(model_analysis.keys(), key=lambda k: model_analysis[k]['consistency_score'])
            most_used_model = max(model_analysis.keys(), key=lambda k: model_analysis[k]['count'])
        else:
            best_avg_model = most_consistent_model = most_used_model = None
        
        return {
            'model_statistics': model_analysis,
            'recommendations': {
                'best_average_performer': best_avg_model,
                'most_consistent': most_consistent_model,
                'most_frequently_used': most_used_model
            },
            'total_models_tested': len(model_analysis),
            'total_evaluations': len(all_performances)
        }
    
    def detect_anomalies(self, threshold: float = 2.0) -> Dict[str, Any]:
        """
        Detect anomalies in evolution performance
        
        Args:
            threshold: Z-score threshold for anomaly detection
            
        Returns:
            Dictionary with anomaly detection results
        """
        if len(self.evolution_history) < 5:
            return {"error": "Insufficient data for anomaly detection"}
        
        df = pd.DataFrame(self.evolution_history)
        anomalies = {}
        
        # Detect anomalies in key metrics
        for metric in ['best_roc_auc', 'best_f1', 'diversity_score', 'generation_time']:
            if metric in df.columns:
                values = df[metric].values
                z_scores = np.abs(stats.zscore(values))
                anomaly_indices = np.where(z_scores > threshold)[0]
                
                anomalies[metric] = {
                    'anomaly_generations': df.iloc[anomaly_indices]['generation'].tolist(),
                    'anomaly_values': df.iloc[anomaly_indices][metric].tolist(),
                    'z_scores': z_scores[anomaly_indices].tolist(),
                    'count': len(anomaly_indices)
                }
        
        # Detect sudden performance drops
        roc_values = df['best_roc_auc'].values
        performance_drops = []
        for i in range(1, len(roc_values)):
            drop = roc_values[i-1] - roc_values[i]
            if drop > 0.1:  # Significant drop threshold
                performance_drops.append({
                    'generation': df.iloc[i]['generation'],
                    'drop_amount': drop,
                    'previous_performance': roc_values[i-1],
                    'current_performance': roc_values[i]
                })
        
        return {
            'metric_anomalies': anomalies,
            'performance_drops': performance_drops,
            'total_anomalies': sum(len(a['anomaly_generations']) for a in anomalies.values()),
            'analysis_threshold': threshold
        }
    
    def calculate_diversity_insights(self) -> Dict[str, Any]:
        """
        Calculate insights about population diversity and model variety
        
        Returns:
            Dictionary with diversity analysis
        """
        if not self.evolution_history:
            return {"error": "No evolution data available"}
        
        # Analyze model type diversity over generations
        diversity_timeline = []
        model_type_evolution = {}
        
        for gen_data in self.evolution_history:
            generation = gen_data['generation']
            drones = gen_data.get('drones', [])
            
            # Count model types in this generation
            model_counts = {}
            for drone in drones:
                model_type = drone.get('model_type', 'unknown')
                model_counts[model_type] = model_counts.get(model_type, 0) + 1
            
            # Calculate diversity metrics
            total_drones = len(drones)
            if total_drones > 0:
                # Shannon diversity index
                shannon_diversity = -sum(
                    (count / total_drones) * np.log(count / total_drones)
                    for count in model_counts.values()
                )
                
                # Simpson diversity index
                simpson_diversity = 1 - sum(
                    (count / total_drones) ** 2
                    for count in model_counts.values()
                )
            else:
                shannon_diversity = simpson_diversity = 0
            
            diversity_timeline.append({
                'generation': generation,
                'model_types_count': len(model_counts),
                'shannon_diversity': shannon_diversity,
                'simpson_diversity': simpson_diversity,
                'model_distribution': model_counts,
                'total_drones': total_drones
            })
            
            # Track model type evolution
            for model_type, count in model_counts.items():
                if model_type not in model_type_evolution:
                    model_type_evolution[model_type] = []
                model_type_evolution[model_type].append({
                    'generation': generation,
                    'count': count,
                    'percentage': count / total_drones if total_drones > 0 else 0
                })
        
        # Calculate diversity trends
        if len(diversity_timeline) > 1:
            shannon_values = [d['shannon_diversity'] for d in diversity_timeline]
            simpson_values = [d['simpson_diversity'] for d in diversity_timeline]
            generations = [d['generation'] for d in diversity_timeline]
            
            shannon_trend = stats.linregress(generations, shannon_values).slope
            simpson_trend = stats.linregress(generations, simpson_values).slope
        else:
            shannon_trend = simpson_trend = 0
        
        return {
            'diversity_timeline': diversity_timeline,
            'model_type_evolution': model_type_evolution,
            'diversity_trends': {
                'shannon_trend': shannon_trend,
                'simpson_trend': simpson_trend,
                'diversity_direction': 'increasing' if shannon_trend > 0 else 'decreasing' if shannon_trend < 0 else 'stable'
            },
            'current_diversity': diversity_timeline[-1] if diversity_timeline else None,
            'avg_model_types_per_generation': np.mean([d['model_types_count'] for d in diversity_timeline])
        }
    
    def generate_performance_predictions(self, generations_ahead: int = 5) -> Dict[str, Any]:
        """
        Generate performance predictions for future generations
        
        Args:
            generations_ahead: Number of generations to predict
            
        Returns:
            Dictionary with performance predictions
        """
        if len(self.evolution_history) < 3:
            return {"error": "Insufficient data for predictions"}
        
        df = pd.DataFrame(self.evolution_history)
        generations = np.array(df['generation'])
        
        predictions = {}
        
        # Predict key metrics using linear regression
        for metric in ['best_roc_auc', 'best_f1', 'diversity_score']:
            if metric in df.columns:
                values = np.array(df[metric])
                
                # Fit linear regression
                slope, intercept, r_value, p_value, std_err = stats.linregress(generations, values)
                
                # Generate predictions
                future_generations = np.arange(
                    generations[-1] + 1, 
                    generations[-1] + 1 + generations_ahead
                )
                predicted_values = slope * future_generations + intercept
                
                # Calculate confidence intervals
                confidence_interval = 1.96 * std_err * np.sqrt(1 + 1/len(generations))
                
                predictions[metric] = {
                    'predicted_values': predicted_values.tolist(),
                    'future_generations': future_generations.tolist(),
                    'confidence_interval': confidence_interval,
                    'model_r_squared': r_value ** 2,
                    'trend_slope': slope,
                    'prediction_reliability': 'high' if r_value ** 2 > 0.7 else 'medium' if r_value ** 2 > 0.4 else 'low'
                }
        
        return {
            'predictions': predictions,
            'prediction_horizon': generations_ahead,
            'base_generation': int(generations[-1]),
            'prediction_timestamp': datetime.now().isoformat()
        }
    
    def _detect_plateau(self, values: np.ndarray, window: int = 5, threshold: float = 0.01) -> bool:
        """
        Detect if performance has plateaued
        
        Args:
            values: Performance values
            window: Window size for plateau detection
            threshold: Threshold for considering plateau
            
        Returns:
            True if plateau detected
        """
        if len(values) < window:
            return False
        
        recent_values = values[-window:]
        return np.std(recent_values) < threshold
    
    def _generations_since_improvement(self, df: pd.DataFrame, threshold: float = 0.01) -> int:
        """
        Calculate generations since last significant improvement
        
        Args:
            df: DataFrame with evolution history
            threshold: Threshold for significant improvement
            
        Returns:
            Number of generations since improvement
        """
        if len(df) < 2:
            return 0
        
        best_values = df['best_roc_auc'].values
        best_so_far = best_values[0]
        generations_since = 0
        
        for i in range(1, len(best_values)):
            if best_values[i] - best_so_far > threshold:
                best_so_far = best_values[i]
                generations_since = 0
            else:
                generations_since += 1
        
        return generations_since
    
    def export_analytics_report(self, output_path: str = "beemind_analytics_report.json") -> str:
        """
        Export comprehensive analytics report
        
        Args:
            output_path: Path to save report
            
        Returns:
            Path to saved report
        """
        report = {
            'report_metadata': {
                'generation_timestamp': datetime.now().isoformat(),
                'total_generations': len(self.evolution_history),
                'analysis_period': {
                    'start': self.evolution_history[0]['timestamp'] if self.evolution_history else None,
                    'end': self.evolution_history[-1]['timestamp'] if self.evolution_history else None
                }
            },
            'evolution_trends': self.calculate_evolution_trends(),
            'model_performance_analysis': self.analyze_model_performance_patterns(),
            'anomaly_detection': self.detect_anomalies(),
            'diversity_insights': self.calculate_diversity_insights(),
            'performance_predictions': self.generate_performance_predictions(),
            'raw_evolution_history': self.evolution_history
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return output_path
