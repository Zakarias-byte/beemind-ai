#!/usr/bin/env python3
"""
Debug script to test BeeMind components individually
"""

import pandas as pd
from ai_engine.drones.drone_generator import generate_drone
from ai_engine.workers.worker_pool import evaluate_model
from ai_engine.queen.queen import select_best_model
from ai_engine.memory.hivememory import log_generation_result

def test_components():
    print("🧪 Testing BeeMind components...")
    
    # Test data (Iris-like)
    data = [
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
    
    df = pd.DataFrame(data, columns=columns)
    X = df.drop(columns=["class"])
    y = df["class"]
    
    print(f"📊 Data shape: X={X.shape}, y={y.shape}")
    print(f"📊 Unique labels: {y.unique()}")
    
    # Test drone generation
    print("\n🤖 Testing drone generation...")
    try:
        model, metadata = generate_drone()
        print(f"✅ Generated {metadata['type']} successfully")
    except Exception as e:
        print(f"❌ Drone generation failed: {e}")
        return
    
    # Test model evaluation
    print("\n👷 Testing model evaluation...")
    try:
        result = evaluate_model(model, X, y)
        print(f"✅ Evaluation successful: ROC AUC={result['roc_auc']:.3f}, F1={result['f1']:.3f}")
    except Exception as e:
        print(f"❌ Model evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test multiple drones
    print("\n🐝 Testing multiple drones...")
    drone_results = []
    for i in range(3):
        try:
            model, metadata = generate_drone()
            result = evaluate_model(model, X, y)
            drone_results.append(result)
            print(f"  Drone {i+1}: {result['metadata']['type']} - ROC AUC={result['roc_auc']:.3f}")
        except Exception as e:
            print(f"  Drone {i+1} failed: {e}")
    
    if not drone_results:
        print("❌ No drones succeeded")
        return
    
    # Test queen selection
    print("\n👑 Testing queen selection...")
    try:
        best = select_best_model(drone_results)
        print(f"✅ Best model: {best['metadata']['type']} with ROC AUC={best['roc_auc']:.3f}")
    except Exception as e:
        print(f"❌ Queen selection failed: {e}")
        return
    
    # Test hive memory logging
    print("\n🧠 Testing hive memory...")
    try:
        log_generation_result(best)
        print("✅ Logging successful")
    except Exception as e:
        print(f"❌ Logging failed: {e}")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    test_components()
