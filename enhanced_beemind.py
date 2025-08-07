#!/usr/bin/env python3
"""
Enhanced BeeMind System - Using advanced drone generator and improved evolution
"""

import json
import pandas as pd
import time
import logging
from datetime import datetime
from typing import List, Dict, Any

# Import BeeMind components
from ai_engine.drones.advanced_drone_generator import generate_advanced_drone
from ai_engine.workers.worker_pool import evaluate_model
from ai_engine.queen.queen import select_best_model
from ai_engine.memory.hivememory import log_generation_result

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedBeeMind:
    """
    Enhanced BeeMind system with advanced evolution capabilities
    """
    
    def __init__(self, num_drones=7, elite_ratio=0.3):
        self.num_drones = num_drones
        self.elite_ratio = elite_ratio
        self.generation_history = []
        
    def run_evolution_cycle(self, X, y, generation_id=None):
        """
        Run a complete evolution cycle
        """
        if generation_id is None:
            generation_id = len(self.generation_history) + 1
            
        logger.info(f"🐝 Starting Evolution Cycle #{generation_id}")
        logger.info(f"📊 Data: X{X.shape}, y{y.shape}, classes: {y.unique()}")
        
        start_time = time.time()
        
        # Phase 1: Drone Generation & Evaluation
        logger.info(f"🤖 Phase 1: Generating {self.num_drones} drones...")
        drone_results = []
        
        for i in range(self.num_drones):
            try:
                logger.info(f"   Drone {i+1}/{self.num_drones}...")
                
                # Generate advanced drone
                model, metadata = generate_advanced_drone()
                
                # Evaluate drone
                result = evaluate_model(model, X, y)
                result['generation_id'] = generation_id
                result['drone_id'] = i + 1
                
                drone_results.append(result)
                
                logger.info(f"   ✅ {metadata['type']} ({metadata['model_family']}) - "
                          f"ROC AUC: {result['roc_auc']:.3f}, F1: {result['f1']:.3f}")
                
            except Exception as e:
                logger.warning(f"   ⚠️ Drone {i+1} failed: {e}")
                continue
        
        if not drone_results:
            raise Exception("No drones survived evaluation")
        
        # Phase 2: Natural Selection
        logger.info("👑 Phase 2: Queen Selection (Natural Selection)...")
        
        # Sort by performance (ROC AUC primary, F1 secondary)
        drone_results.sort(key=lambda x: (x['roc_auc'], x['f1']), reverse=True)
        
        # Select elite drones
        num_elite = max(1, int(len(drone_results) * self.elite_ratio))
        elite_drones = drone_results[:num_elite]
        
        # Best drone (Queen's choice)
        best_drone = select_best_model(drone_results)
        
        logger.info(f"   👑 Queen selected: {best_drone['metadata']['type']}")
        logger.info(f"   🏆 Elite drones: {num_elite}/{len(drone_results)}")
        
        # Phase 3: Evolution Statistics
        generation_time = time.time() - start_time
        
        evolution_stats = {
            "generation_id": generation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "total_drones": len(drone_results),
            "elite_drones": num_elite,
            "best_drone": {
                "type": best_drone['metadata']['type'],
                "model_family": best_drone['metadata'].get('model_family', 'unknown'),
                "roc_auc": best_drone['roc_auc'],
                "f1_score": best_drone['f1'],
                "generation_id": best_drone['metadata'].get('generation_id', 'unknown')
            },
            "performance_distribution": {
                "avg_roc_auc": sum(d['roc_auc'] for d in drone_results) / len(drone_results),
                "avg_f1": sum(d['f1'] for d in drone_results) / len(drone_results),
                "max_roc_auc": max(d['roc_auc'] for d in drone_results),
                "min_roc_auc": min(d['roc_auc'] for d in drone_results),
                "max_f1": max(d['f1'] for d in drone_results),
                "min_f1": min(d['f1'] for d in drone_results)
            },
            "model_diversity": self._calculate_model_diversity(drone_results),
            "generation_time": generation_time
        }
        
        # Phase 4: HiveMemory Logging
        logger.info("🧠 Phase 4: Logging to HiveMemory...")
        try:
            log_generation_result(best_drone)
            self._log_evolution_stats(evolution_stats)
            logger.info("   ✅ Evolution logged to HiveMemory")
        except Exception as e:
            logger.warning(f"   ⚠️ Logging failed: {e}")
        
        # Store in generation history
        self.generation_history.append(evolution_stats)
        
        logger.info(f"🎉 Evolution Cycle #{generation_id} completed in {generation_time:.2f}s")
        logger.info(f"   Best: {best_drone['metadata']['type']} - "
                   f"ROC AUC: {best_drone['roc_auc']:.3f}, F1: {best_drone['f1']:.3f}")
        
        return {
            "evolution_stats": evolution_stats,
            "best_drone": best_drone,
            "elite_drones": elite_drones,
            "all_drones": drone_results
        }
    
    def _calculate_model_diversity(self, drone_results):
        """Calculate diversity metrics for the drone population"""
        model_types = [d['metadata']['type'] for d in drone_results]
        model_families = [d['metadata'].get('model_family', 'unknown') for d in drone_results]
        
        unique_types = len(set(model_types))
        unique_families = len(set(model_families))
        
        return {
            "unique_model_types": unique_types,
            "unique_model_families": unique_families,
            "diversity_ratio": unique_types / len(drone_results) if drone_results else 0,
            "model_distribution": {model: model_types.count(model) for model in set(model_types)}
        }
    
    def _log_evolution_stats(self, stats):
        """Log evolution statistics to separate file"""
        try:
            filename = "evolution_history.json"
            try:
                with open(filename, "r") as f:
                    history = json.load(f)
            except FileNotFoundError:
                history = []
            
            history.append(stats)
            
            with open(filename, "w") as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to log evolution stats: {e}")
    
    def get_evolution_summary(self):
        """Get summary of all evolution cycles"""
        if not self.generation_history:
            return {"message": "No evolution cycles completed yet"}
        
        total_generations = len(self.generation_history)
        avg_time = sum(g['generation_time'] for g in self.generation_history) / total_generations
        
        best_overall = max(self.generation_history, 
                          key=lambda g: g['best_drone']['roc_auc'])
        
        return {
            "total_generations": total_generations,
            "average_generation_time": avg_time,
            "best_overall": best_overall['best_drone'],
            "evolution_trend": [g['best_drone']['roc_auc'] for g in self.generation_history]
        }

def run_enhanced_beemind(data, columns, label_index, num_drones=7):
    """
    Run enhanced BeeMind evolution process
    """
    # Create DataFrame
    df = pd.DataFrame(data, columns=columns)
    label_col = columns[label_index]
    X = df.drop(columns=[label_col])
    y = df[label_col]
    
    # Initialize enhanced BeeMind
    beemind = EnhancedBeeMind(num_drones=num_drones)
    
    # Run evolution cycle
    result = beemind.run_evolution_cycle(X, y)
    
    return {
        "selected_model": result['best_drone']['metadata']['type'],
        "model_family": result['best_drone']['metadata'].get('model_family', 'unknown'),
        "roc_auc": result['best_drone']['roc_auc'],
        "f1_score": result['best_drone']['f1'],
        "params": result['best_drone']['metadata']['params'],
        "total_drones": result['evolution_stats']['total_drones'],
        "elite_drones": result['evolution_stats']['elite_drones'],
        "generation_time": result['evolution_stats']['generation_time'],
        "model_diversity": result['evolution_stats']['model_diversity'],
        "performance_stats": result['evolution_stats']['performance_distribution']
    }

if __name__ == "__main__":
    # Test data (Enhanced Iris-like dataset)
    test_data = [
        [5.1, 3.5, 1.4, 0.2, 0], [4.9, 3.0, 1.4, 0.2, 0], [4.7, 3.2, 1.3, 0.2, 0],
        [6.2, 3.4, 5.4, 2.3, 2], [5.9, 3.0, 5.1, 1.8, 2], [6.3, 3.3, 6.0, 2.5, 2],
        [5.5, 2.3, 4.0, 1.3, 1], [6.5, 2.8, 4.6, 1.5, 1], [7.0, 3.2, 4.7, 1.4, 1],
        [5.8, 2.7, 5.1, 1.9, 2], [6.4, 3.2, 4.5, 1.5, 1], [5.2, 3.5, 1.5, 0.2, 0],
        [5.7, 4.4, 1.5, 0.4, 0], [6.1, 2.8, 4.7, 1.2, 1], [6.3, 2.9, 5.6, 1.8, 2],
        [5.1, 3.8, 1.5, 0.3, 0], [4.6, 3.2, 1.4, 0.2, 0], [6.7, 3.1, 4.4, 1.4, 1]
    ]
    columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "class"]
    
    print("🐝 Running Enhanced BeeMind Evolution...")
    result = run_enhanced_beemind(test_data, columns, 4, num_drones=7)
    
    print("\n🎉 Enhanced BeeMind Evolution Complete!")
    print(f"📊 Result: {json.dumps(result, indent=2)}")
    
    # Save result to file
    with open("enhanced_beemind_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("💾 Result saved to enhanced_beemind_result.json")
