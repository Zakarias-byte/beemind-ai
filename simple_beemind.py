#!/usr/bin/env python3
"""
Simple working BeeMind server - bypassing HTTP issues
"""

import json
import pandas as pd
from ai_engine.drones.drone_generator import generate_drone
from ai_engine.workers.worker_pool import evaluate_model
from ai_engine.queen.queen import select_best_model
from ai_engine.memory.hivememory import log_generation_result

def run_beemind_generation(data, columns, label_index):
    """
    Run BeeMind generation process directly
    """
    print("🐝 Starting BeeMind generation...")
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=columns)
    label_col = columns[label_index]
    X = df.drop(columns=[label_col])
    y = df[label_col]
    
    print(f"📊 Data: X{X.shape}, y{y.shape}, classes: {y.unique()}")
    
    # Generate and evaluate drones
    drone_results = []
    for i in range(5):
        try:
            print(f"🤖 Generating drone {i+1}/5...")
            model, metadata = generate_drone()
            
            print(f"👷 Evaluating {metadata['type']}...")
            result = evaluate_model(model, X, y)
            
            drone_results.append(result)
            print(f"✅ Drone {i+1}: {metadata['type']} - ROC AUC={result['roc_auc']:.3f}, F1={result['f1']:.3f}")
            
        except Exception as e:
            print(f"⚠️ Drone {i+1} failed: {e}")
            continue
    
    if not drone_results:
        return {"error": "No drones succeeded"}
    
    # Select best model
    best = select_best_model(drone_results)
    print(f"👑 Best model: {best['metadata']['type']} with ROC AUC: {best['roc_auc']:.3f}")
    
    # Log result
    try:
        log_generation_result(best)
        print("🧠 Result logged to HiveMemory")
    except Exception as e:
        print(f"⚠️ Logging failed: {e}")
    
    return {
        "selected_model": best["metadata"]["type"],
        "roc_auc": best["roc_auc"],
        "f1_score": best["f1"],
        "params": best["metadata"]["params"],
        "total_drones": len(drone_results)
    }

if __name__ == "__main__":
    # Test data (Iris-like)
    test_data = [
        [5.1, 3.5, 1.4, 0.2, 0],
        [4.9, 3.0, 1.4, 0.2, 0],
        [6.2, 3.4, 5.4, 2.3, 2],
        [5.9, 3.0, 5.1, 1.8, 2],
        [5.5, 2.3, 4.0, 1.3, 1],
        [6.5, 2.8, 4.6, 1.5, 1],
        [4.7, 3.2, 1.3, 0.2, 0],
        [7.0, 3.2, 4.7, 1.4, 1],
        [6.3, 3.3, 6.0, 2.5, 2],
        [5.8, 2.7, 5.1, 1.9, 2]
    ]
    columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "class"]
    
    print("🧪 Running BeeMind test generation...")
    result = run_beemind_generation(test_data, columns, 4)
    
    print("\n🎉 BeeMind Generation Complete!")
    print(f"📊 Result: {json.dumps(result, indent=2)}")
    
    # Save result to file
    with open("beemind_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("💾 Result saved to beemind_result.json")
