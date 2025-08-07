"""
MLFlow Integration for BeeMind AI Evolution Tracking
Provides experiment tracking, model versioning, and performance analytics
"""

import mlflow
import mlflow.sklearn
import mlflow.xgboost
import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np
from pathlib import Path

class BeeMindMLFlowTracker:
    """
    MLFlow integration for tracking BeeMind evolution experiments
    """
    
    def __init__(self, tracking_uri: str = None, experiment_name: str = "BeeMind_Evolution"):
        """
        Initialize MLFlow tracker
        
        Args:
            tracking_uri: MLFlow tracking server URI (default: local file store)
            experiment_name: Name of the MLFlow experiment
        """
        # Set tracking URI (default to local file store)
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        else:
            # Create local mlflow directory
            mlflow_dir = Path("mlflow_runs")
            mlflow_dir.mkdir(exist_ok=True)
            mlflow.set_tracking_uri(f"file://{mlflow_dir.absolute()}")
        
        # Set or create experiment
        try:
            self.experiment_id = mlflow.create_experiment(experiment_name)
        except mlflow.exceptions.MlflowException:
            # Experiment already exists
            experiment = mlflow.get_experiment_by_name(experiment_name)
            self.experiment_id = experiment.experiment_id
        
        self.experiment_name = experiment_name
        print(f"MLFlow tracker initialized - Experiment: {experiment_name}")
    
    def start_evolution_run(self, generation: int, population_size: int, 
                           evolution_params: Dict[str, Any]) -> str:
        """
        Start a new MLFlow run for an evolution generation
        
        Args:
            generation: Generation number
            population_size: Number of drones in generation
            evolution_params: Evolution configuration parameters
            
        Returns:
            MLFlow run ID
        """
        run_name = f"Generation_{generation:03d}"
        
        with mlflow.start_run(experiment_id=self.experiment_id, run_name=run_name) as run:
            # Log evolution parameters
            mlflow.log_params({
                "generation": generation,
                "population_size": population_size,
                "evolution_strategy": evolution_params.get("strategy", "genetic"),
                "selection_method": evolution_params.get("selection", "elite"),
                "mutation_rate": evolution_params.get("mutation_rate", 0.1),
                "crossover_rate": evolution_params.get("crossover_rate", 0.8)
            })
            
            # Log additional evolution config
            for key, value in evolution_params.items():
                if isinstance(value, (int, float, str, bool)):
                    mlflow.log_param(f"config_{key}", value)
            
            # Log generation start time
            mlflow.log_param("start_time", datetime.now().isoformat())
            
            return run.info.run_id
    
    def log_drone_performance(self, run_id: str, drone_id: str, model_type: str,
                             performance_metrics: Dict[str, float],
                             model_params: Dict[str, Any],
                             model_object: Any = None):
        """
        Log individual drone performance within an evolution run
        
        Args:
            run_id: MLFlow run ID
            drone_id: Unique drone identifier
            model_type: Type of ML model (RandomForest, XGBoost, etc.)
            performance_metrics: Performance metrics (ROC AUC, F1, etc.)
            model_params: Model hyperparameters
            model_object: Trained model object (optional)
        """
        with mlflow.start_run(run_id=run_id):
            # Log drone-specific metrics with prefix
            for metric_name, value in performance_metrics.items():
                mlflow.log_metric(f"drone_{drone_id}_{metric_name}", value)
            
            # Log model parameters with drone prefix
            for param_name, value in model_params.items():
                if isinstance(value, (int, float, str, bool)):
                    mlflow.log_param(f"drone_{drone_id}_{param_name}", value)
            
            # Log model type
            mlflow.log_param(f"drone_{drone_id}_model_type", model_type)
            
            # Log model artifact if provided
            if model_object is not None:
                try:
                    if model_type.lower() in ['xgboost', 'xgb']:
                        mlflow.xgboost.log_model(model_object, f"models/drone_{drone_id}")
                    else:
                        mlflow.sklearn.log_model(model_object, f"models/drone_{drone_id}")
                except Exception as e:
                    print(f"Warning: Could not log model artifact for drone {drone_id}: {e}")
    
    def log_generation_summary(self, run_id: str, generation_stats: Dict[str, Any],
                              elite_drones: List[Dict[str, Any]],
                              diversity_metrics: Dict[str, float]):
        """
        Log summary statistics for the entire generation
        
        Args:
            run_id: MLFlow run ID
            generation_stats: Overall generation statistics
            elite_drones: List of elite drone information
            diversity_metrics: Population diversity metrics
        """
        with mlflow.start_run(run_id=run_id):
            # Log generation-level metrics
            mlflow.log_metrics({
                "best_roc_auc": generation_stats.get("best_roc_auc", 0.0),
                "avg_roc_auc": generation_stats.get("avg_roc_auc", 0.0),
                "std_roc_auc": generation_stats.get("std_roc_auc", 0.0),
                "best_f1": generation_stats.get("best_f1", 0.0),
                "avg_f1": generation_stats.get("avg_f1", 0.0),
                "elite_count": len(elite_drones),
                "generation_time": generation_stats.get("generation_time", 0.0)
            })
            
            # Log diversity metrics
            for metric_name, value in diversity_metrics.items():
                mlflow.log_metric(f"diversity_{metric_name}", value)
            
            # Log elite drone summary as artifact
            elite_summary = pd.DataFrame(elite_drones)
            elite_summary.to_csv("elite_drones.csv", index=False)
            mlflow.log_artifact("elite_drones.csv", "generation_artifacts")
            
            # Clean up temporary file
            os.remove("elite_drones.csv")
            
            # Log generation completion time
            mlflow.log_param("end_time", datetime.now().isoformat())
    
    def log_blockchain_metrics(self, run_id: str, blockchain_stats: Dict[str, Any]):
        """
        Log blockchain-related metrics
        
        Args:
            run_id: MLFlow run ID
            blockchain_stats: Blockchain statistics and integrity metrics
        """
        with mlflow.start_run(run_id=run_id):
            # Log blockchain metrics
            mlflow.log_metrics({
                "blockchain_length": blockchain_stats.get("chain_length", 0),
                "last_block_difficulty": blockchain_stats.get("difficulty", 0),
                "chain_valid": float(blockchain_stats.get("is_valid", False)),
                "mining_time": blockchain_stats.get("mining_time", 0.0),
                "block_size": blockchain_stats.get("block_size", 0)
            })
            
            # Log blockchain hash as parameter
            if "latest_hash" in blockchain_stats:
                mlflow.log_param("latest_block_hash", blockchain_stats["latest_hash"])
    
    def get_experiment_history(self, max_results: int = 100) -> pd.DataFrame:
        """
        Retrieve experiment history as DataFrame
        
        Args:
            max_results: Maximum number of runs to retrieve
            
        Returns:
            DataFrame with experiment history
        """
        runs = mlflow.search_runs(
            experiment_ids=[self.experiment_id],
            max_results=max_results,
            order_by=["start_time DESC"]
        )
        return runs
    
    def get_best_models(self, metric: str = "metrics.best_roc_auc", 
                       top_k: int = 5) -> pd.DataFrame:
        """
        Get top performing models based on specified metric
        
        Args:
            metric: Metric to rank by
            top_k: Number of top models to return
            
        Returns:
            DataFrame with top models
        """
        runs = self.get_experiment_history()
        
        if metric in runs.columns:
            top_runs = runs.nlargest(top_k, metric)
            return top_runs[['run_id', 'start_time', metric, 'status']]
        else:
            print(f"Warning: Metric '{metric}' not found in runs")
            return pd.DataFrame()
    
    def export_experiment_data(self, output_path: str = "beemind_experiment_export.json"):
        """
        Export all experiment data to JSON file
        
        Args:
            output_path: Path to save export file
        """
        runs_df = self.get_experiment_history()
        
        export_data = {
            "experiment_name": self.experiment_name,
            "experiment_id": self.experiment_id,
            "export_timestamp": datetime.now().isoformat(),
            "total_runs": len(runs_df),
            "runs": runs_df.to_dict('records')
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"Experiment data exported to {output_path}")
        return output_path
    
    def create_performance_dashboard_data(self) -> Dict[str, Any]:
        """
        Create data structure for dashboard visualization
        
        Returns:
            Dictionary with dashboard-ready data
        """
        runs_df = self.get_experiment_history()
        
        if runs_df.empty:
            return {"error": "No experiment data available"}
        
        # Extract generation numbers and performance metrics
        generations = []
        performance_data = []
        
        for _, run in runs_df.iterrows():
            if 'params.generation' in run and pd.notna(run['params.generation']):
                gen_num = int(run['params.generation'])
                
                gen_data = {
                    "generation": gen_num,
                    "best_roc_auc": run.get('metrics.best_roc_auc', 0.0),
                    "avg_roc_auc": run.get('metrics.avg_roc_auc', 0.0),
                    "best_f1": run.get('metrics.best_f1', 0.0),
                    "avg_f1": run.get('metrics.avg_f1', 0.0),
                    "elite_count": run.get('metrics.elite_count', 0),
                    "diversity_score": run.get('metrics.diversity_population_diversity', 0.0),
                    "generation_time": run.get('metrics.generation_time', 0.0),
                    "run_id": run['run_id'],
                    "start_time": run['start_time']
                }
                performance_data.append(gen_data)
        
        # Sort by generation
        performance_data.sort(key=lambda x: x['generation'])
        
        # Calculate summary statistics
        if performance_data:
            best_overall = max(performance_data, key=lambda x: x['best_roc_auc'])
            avg_generation_time = np.mean([d['generation_time'] for d in performance_data if d['generation_time'] > 0])
        else:
            best_overall = None
            avg_generation_time = 0
        
        dashboard_data = {
            "total_generations": len(performance_data),
            "performance_history": performance_data,
            "best_overall_performance": best_overall,
            "average_generation_time": avg_generation_time,
            "experiment_summary": {
                "experiment_name": self.experiment_name,
                "total_runs": len(runs_df),
                "active_since": runs_df['start_time'].min() if not runs_df.empty else None
            }
        }
        
        return dashboard_data

# Utility functions for easy integration
def initialize_mlflow_tracking(experiment_name: str = "BeeMind_Evolution") -> BeeMindMLFlowTracker:
    """
    Initialize MLFlow tracking for BeeMind
    
    Args:
        experiment_name: Name of the experiment
        
    Returns:
        Configured MLFlow tracker instance
    """
    return BeeMindMLFlowTracker(experiment_name=experiment_name)

def log_beemind_evolution(tracker: BeeMindMLFlowTracker, 
                         generation_data: Dict[str, Any]) -> str:
    """
    Convenience function to log a complete BeeMind evolution generation
    
    Args:
        tracker: MLFlow tracker instance
        generation_data: Complete generation data including drones and stats
        
    Returns:
        MLFlow run ID
    """
    generation = generation_data.get("generation", 0)
    drones = generation_data.get("drones", [])
    stats = generation_data.get("stats", {})
    evolution_params = generation_data.get("evolution_params", {})
    
    # Start evolution run
    run_id = tracker.start_evolution_run(
        generation=generation,
        population_size=len(drones),
        evolution_params=evolution_params
    )
    
    # Log each drone
    for drone in drones:
        tracker.log_drone_performance(
            run_id=run_id,
            drone_id=drone.get("id", "unknown"),
            model_type=drone.get("model_type", "unknown"),
            performance_metrics=drone.get("metrics", {}),
            model_params=drone.get("params", {}),
            model_object=drone.get("model")
        )
    
    # Log generation summary
    elite_drones = [d for d in drones if d.get("is_elite", False)]
    diversity_metrics = stats.get("diversity", {})
    
    tracker.log_generation_summary(
        run_id=run_id,
        generation_stats=stats,
        elite_drones=elite_drones,
        diversity_metrics=diversity_metrics
    )
    
    # Log blockchain metrics if available
    if "blockchain" in generation_data:
        tracker.log_blockchain_metrics(run_id, generation_data["blockchain"])
    
    return run_id
