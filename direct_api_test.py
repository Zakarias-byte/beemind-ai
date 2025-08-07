#!/usr/bin/env python3
"""
Direct test of the FastAPI endpoint logic without HTTP layer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import DatasetInput, generate_best_model

def test_api_logic():
    print("🧪 Testing API logic directly...")
    
    # Create test input
    test_input = DatasetInput(
        data=[
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
        ],
        columns=["sepal_length", "sepal_width", "petal_length", "petal_width", "class"],
        label_index=4
    )
    
    print(f"📊 Input: {len(test_input.data)} rows, {len(test_input.columns)} columns")
    
    try:
        result = generate_best_model(test_input)
        print("✅ API logic successful!")
        print(f"📊 Result: {result}")
        return True
    except Exception as e:
        print(f"❌ API logic failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_logic()
    if success:
        print("\n🎉 Direct API test passed! The issue might be with HTTP layer.")
    else:
        print("\n💥 Direct API test failed! Issue is in the logic.")
