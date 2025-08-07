#!/usr/bin/env python3
"""
Complete BeeMind System - Integrated solution with all advanced features
"""

import json
import pandas as pd
import time
import logging
from datetime import datetime
from typing import List, Dict, Any

# Import all BeeMind components
from ai_engine.drones.advanced_drone_generator import generate_advanced_drone
from ai_engine.workers.worker_pool import evaluate_model
from ai_engine.queen.queen import select_best_model
from ai_engine.memory.hivememory import log_generation_result
from blockchain.beemind_blockchain import (
    log_evolution_to_blockchain, 
    mine_evolution_block,
    save_blockchain,
    beemind_blockchain
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteBeeMind:
    """
    Complete BeeMind System with all advanced features:
    - Advanced drone generation with genetic algorithms
    - Multi-drone evolution with elite selection
    - Blockchain-based tamper-proof logging
    - Comprehensive performance analytics
    - HiveMemory integration
    """
    
    def __init__(self, num_drones=7, elite_ratio=0.3, blockchain_enabled=True):
        self.num_drones = num_drones
        self.elite_ratio = elite_ratio
        self.blockchain_enabled = blockchain_enabled
        self.evolution_history = []
        
        logger.info(f"🐝 Complete BeeMind System initialized")
        logger.info(f"   Drones per generation: {num_drones}")
        logger.info(f"   Elite selection ratio: {elite_ratio}")
        logger.info(f"   Blockchain logging: {'✅' if blockchain_enabled else '❌'}")
    
    def run_complete_evolution(self, X, y, generation_name="Evolution"):
        """
        Run complete BeeMind evolution with all advanced features
        """
        generation_id = len(self.evolution_history) + 1
        start_time = time.time()
        
        logger.info(f"🚀 Starting Complete BeeMind Evolution #{generation_id}: {generation_name}")
        logger.info(f"📊 Dataset: X{X.shape}, y{y.shape}, classes: {sorted(y.unique())}")
        
        # Phase 1: Advanced Drone Generation & Evaluation
        logger.info(f"🤖 Phase 1: Advanced Drone Generation ({self.num_drones} drones)")
        drone_results = []
        drone_failures = 0
        
        for i in range(self.num_drones):
            try:
                logger.info(f"   🔬 Generating drone {i+1}/{self.num_drones}...")
                
                # Generate advanced drone with genetic algorithms
                model, metadata = generate_advanced_drone()
                
                # Evaluate drone performance
                result = evaluate_model(model, X, y)
                result['generation_id'] = generation_id
                result['drone_id'] = i + 1
                result['generation_name'] = generation_name
                
                drone_results.append(result)
                
                logger.info(f"   ✅ {metadata['type']} ({metadata.get('model_family', 'unknown')}) - "
                          f"ROC AUC: {result['roc_auc']:.3f}, F1: {result['f1']:.3f}")
                
            except Exception as e:
                drone_failures += 1
                logger.warning(f"   ⚠️ Drone {i+1} failed: {e}")
                continue
        
        if not drone_results:
            raise Exception("No drones survived evaluation phase")
        
        logger.info(f"   📊 Phase 1 Complete: {len(drone_results)} successful, {drone_failures} failed")
        
        # Phase 2: Natural Selection & Elite Selection
        logger.info("👑 Phase 2: Natural Selection & Elite Identification")
        
        # Sort by performance (ROC AUC primary, F1 secondary)
        drone_results.sort(key=lambda x: (x['roc_auc'], x['f1']), reverse=True)
        
        # Select elite drones for future breeding
        num_elite = max(1, int(len(drone_results) * self.elite_ratio))
        elite_drones = drone_results[:num_elite]
        
        # Queen selection (best overall drone)
        best_drone = select_best_model(drone_results)
        
        logger.info(f"   👑 Queen selected: {best_drone['metadata']['type']}")
        logger.info(f"   🏆 Elite population: {num_elite}/{len(drone_results)} drones")
        logger.info(f"   📈 Performance range: {drone_results[-1]['roc_auc']:.3f} - {drone_results[0]['roc_auc']:.3f}")
        
        # Phase 3: Advanced Analytics & Statistics
        logger.info("📊 Phase 3: Evolution Analytics")
        
        generation_time = time.time() - start_time
        
        # Calculate comprehensive statistics
        evolution_stats = self._calculate_evolution_stats(
            generation_id, generation_name, drone_results, elite_drones, 
            best_drone, generation_time
        )
        
        logger.info(f"   📈 Model diversity: {evolution_stats['model_diversity']['diversity_ratio']:.1%}")
        logger.info(f"   ⚡ Generation time: {generation_time:.2f}s")
        logger.info(f"   🎯 Average performance: ROC AUC {evolution_stats['performance_distribution']['avg_roc_auc']:.3f}")
        
        # Phase 4: Multi-Layer Logging
        logger.info("🧠 Phase 4: Multi-Layer Evolution Logging")
        
        # Traditional HiveMemory logging
        try:
            log_generation_result(best_drone)
            logger.info("   ✅ HiveMemory logged")
        except Exception as e:
            logger.warning(f"   ⚠️ HiveMemory logging failed: {e}")
        
        # Blockchain logging (tamper-proof)
        if self.blockchain_enabled:
            try:
                log_evolution_to_blockchain(evolution_stats)
                logger.info("   🔗 Evolution logged to blockchain")
                
                # Mine blockchain block every few generations
                if generation_id % 3 == 0:  # Mine every 3 generations
                    block = mine_evolution_block()
                    if block:
                        logger.info(f"   ⛏️ Blockchain block mined: {block.hash[:16]}...")
                        save_blockchain()
                        logger.info("   💾 Blockchain saved")
                
            except Exception as e:
                logger.warning(f"   ⚠️ Blockchain logging failed: {e}")
        
        # Store in evolution history
        self.evolution_history.append(evolution_stats)
        
        # Phase 5: Evolution Summary
        logger.info("🎉 Phase 5: Evolution Complete!")
        logger.info(f"   🏆 Champion: {best_drone['metadata']['type']}")
        logger.info(f"   📊 Performance: ROC AUC {best_drone['roc_auc']:.3f}, F1 {best_drone['f1']:.3f}")
        logger.info(f"   ⏱️ Total time: {generation_time:.2f}s")
        logger.info(f"   🧬 Genetic diversity: {len(set(d['metadata']['type'] for d in drone_results))} unique models")
        
        return {
            "generation_id": generation_id,
            "generation_name": generation_name,
            "best_drone": {
                "model_type": best_drone['metadata']['type'],
                "model_family": best_drone['metadata'].get('model_family', 'unknown'),
                "roc_auc": best_drone['roc_auc'],
                "f1_score": best_drone['f1'],
                "params": best_drone['metadata']['params']
            },
            "evolution_stats": evolution_stats,
            "elite_drones": len(elite_drones),
            "total_drones": len(drone_results),
            "generation_time": generation_time,
            "blockchain_enabled": self.blockchain_enabled
        }
    
    def _calculate_evolution_stats(self, generation_id, generation_name, drone_results, 
                                 elite_drones, best_drone, generation_time):
        """Calculate comprehensive evolution statistics"""
        
        # Model diversity analysis
        model_types = [d['metadata']['type'] for d in drone_results]
        model_families = [d['metadata'].get('model_family', 'unknown') for d in drone_results]
        
        model_diversity = {
            "unique_model_types": len(set(model_types)),
            "unique_model_families": len(set(model_families)),
            "diversity_ratio": len(set(model_types)) / len(drone_results) if drone_results else 0,
            "model_distribution": {model: model_types.count(model) for model in set(model_types)},
            "family_distribution": {family: model_families.count(family) for family in set(model_families)}
        }
        
        # Performance distribution analysis
        roc_scores = [d['roc_auc'] for d in drone_results]
        f1_scores = [d['f1'] for d in drone_results]
        
        performance_distribution = {
            "avg_roc_auc": sum(roc_scores) / len(roc_scores),
            "avg_f1": sum(f1_scores) / len(f1_scores),
            "max_roc_auc": max(roc_scores),
            "min_roc_auc": min(roc_scores),
            "max_f1": max(f1_scores),
            "min_f1": min(f1_scores),
            "roc_std": self._calculate_std(roc_scores),
            "f1_std": self._calculate_std(f1_scores)
        }
        
        return {
            "generation_id": generation_id,
            "generation_name": generation_name,
            "timestamp": datetime.utcnow().isoformat(),
            "total_drones": len(drone_results),
            "elite_drones": len(elite_drones),
            "best_drone": {
                "type": best_drone['metadata']['type'],
                "model_family": best_drone['metadata'].get('model_family', 'unknown'),
                "roc_auc": best_drone['roc_auc'],
                "f1_score": best_drone['f1'],
                "generation_id": best_drone['metadata'].get('generation_id', 'unknown')
            },
            "model_diversity": model_diversity,
            "performance_distribution": performance_distribution,
            "generation_time": generation_time,
            "evolution_metadata": {
                "elite_ratio": self.elite_ratio,
                "selection_pressure": len(elite_drones) / len(drone_results),
                "survival_rate": len(drone_results) / self.num_drones
            }
        }
    
    def _calculate_std(self, values):
        """Calculate standard deviation"""
        if len(values) <= 1:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def get_evolution_summary(self):
        """Get comprehensive evolution summary"""
        if not self.evolution_history:
            return {"message": "No evolution cycles completed yet"}
        
        total_generations = len(self.evolution_history)
        avg_time = sum(g['generation_time'] for g in self.evolution_history) / total_generations
        
        best_overall = max(self.evolution_history, 
                          key=lambda g: g['best_drone']['roc_auc'])
        
        return {
            "total_generations": total_generations,
            "average_generation_time": avg_time,
            "best_overall_champion": best_overall['best_drone'],
            "evolution_trend": [g['best_drone']['roc_auc'] for g in self.evolution_history],
            "diversity_trend": [g['model_diversity']['diversity_ratio'] for g in self.evolution_history],
            "blockchain_stats": beemind_blockchain.get_blockchain_stats() if self.blockchain_enabled else None
        }

def run_complete_beemind(data, columns, label_index, num_drones=7, 
                        generation_name="BeeMind Evolution"):
    """
    Run complete BeeMind evolution with all advanced features
    """
    # Create DataFrame
    df = pd.DataFrame(data, columns=columns)
    label_col = columns[label_index]
    X = df.drop(columns=[label_col])
    y = df[label_col]
    
    # Initialize complete BeeMind system
    beemind = CompleteBeeMind(num_drones=num_drones, blockchain_enabled=True)
    
    # Run complete evolution
    result = beemind.run_complete_evolution(X, y, generation_name)
    
    return result

if __name__ == "__main__":
    # Enhanced test dataset
    test_data = [
        [5.1, 3.5, 1.4, 0.2, 0], [4.9, 3.0, 1.4, 0.2, 0], [4.7, 3.2, 1.3, 0.2, 0],
        [4.6, 3.1, 1.5, 0.2, 0], [5.0, 3.6, 1.4, 0.2, 0], [5.4, 3.9, 1.7, 0.4, 0],
        [6.2, 3.4, 5.4, 2.3, 2], [5.9, 3.0, 5.1, 1.8, 2], [6.3, 3.3, 6.0, 2.5, 2],
        [5.8, 2.7, 5.1, 1.9, 2], [7.1, 3.0, 5.9, 2.1, 2], [6.3, 2.9, 5.6, 1.8, 2],
        [5.5, 2.3, 4.0, 1.3, 1], [6.5, 2.8, 4.6, 1.5, 1], [7.0, 3.2, 4.7, 1.4, 1],
        [6.4, 3.2, 4.5, 1.5, 1], [6.9, 3.1, 4.9, 1.5, 1], [5.7, 2.8, 4.5, 1.3, 1],
        [6.8, 2.8, 4.8, 1.4, 1], [5.7, 2.6, 3.5, 1.0, 1], [5.8, 2.6, 4.0, 1.2, 1]
    ]
    columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "class"]
    
    print("🐝 Running Complete BeeMind Evolution System...")
    result = run_complete_beemind(
        test_data, columns, 4, 
        num_drones=8, 
        generation_name="Complete BeeMind Demo"
    )
    
    print("\n🎉 Complete BeeMind Evolution Finished!")
    print(f"📊 Result Summary: {json.dumps(result, indent=2)}")
    
    # Save complete result
    with open("complete_beemind_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("💾 Complete result saved to complete_beemind_result.json")
