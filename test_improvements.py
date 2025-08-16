#!/usr/bin/env python3
"""
Test script to verify BeeMind improvements
Tests error handling, logging, configuration, and API functionality
"""

import requests
import json
import time
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_health_endpoint():
    """Test health check endpoint"""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_api_docs():
    """Test API documentation endpoint"""
    print("🔍 Testing API documentation...")
    
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
            return True
        else:
            print(f"❌ API documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API documentation error: {e}")
        return False

def test_generate_endpoint():
    """Test model generation endpoint"""
    print("🔍 Testing model generation...")
    
    # Sample Iris dataset
    test_data = {
        "data": [
            [5.1, 3.5, 1.4, 0.2, 0],
            [4.9, 3.0, 1.4, 0.2, 0],
            [4.7, 3.2, 1.3, 0.2, 0],
            [4.6, 3.1, 1.5, 0.2, 0],
            [5.0, 3.6, 1.4, 0.2, 0],
            [7.0, 3.2, 4.7, 1.4, 1],
            [6.4, 3.2, 4.5, 1.5, 1],
            [6.9, 3.1, 4.9, 1.5, 1],
            [5.5, 2.3, 4.0, 1.3, 1],
            [6.5, 2.8, 4.6, 1.5, 1],
            [6.3, 3.3, 6.0, 2.5, 2],
            [5.8, 2.7, 5.1, 1.9, 2],
            [7.1, 3.0, 5.9, 2.1, 2],
            [6.3, 2.9, 5.6, 1.8, 2],
            [6.5, 3.0, 5.8, 2.2, 2]
        ],
        "columns": ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"],
        "label_index": 4,
        "use_evolution": False  # Test standard generation first
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model generation successful!")
            print(f"   Selected model: {data['selected_model']}")
            print(f"   ROC AUC: {data['roc_auc']:.3f}")
            print(f"   F1 Score: {data['f1_score']:.3f}")
            print(f"   Total drones: {data['total_drones']}")
            print(f"   Generation time: {data.get('generation_time', end_time - start_time):.2f}s")
            return True
        else:
            print(f"❌ Model generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Model generation error: {e}")
        return False

def test_history_endpoint():
    """Test history endpoint"""
    print("🔍 Testing history endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/history")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ History endpoint working: {data['total_entries']} entries")
            return True
        else:
            print(f"❌ History endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ History endpoint error: {e}")
        return False

def test_evolution_endpoint():
    """Test evolution endpoint"""
    print("🔍 Testing evolution generation...")
    
    # Sample Iris dataset for evolution
    test_data = {
        "data": [
            [5.1, 3.5, 1.4, 0.2, 0],
            [4.9, 3.0, 1.4, 0.2, 0],
            [4.7, 3.2, 1.3, 0.2, 0],
            [4.6, 3.1, 1.5, 0.2, 0],
            [5.0, 3.6, 1.4, 0.2, 0],
            [7.0, 3.2, 4.7, 1.4, 1],
            [6.4, 3.2, 4.5, 1.5, 1],
            [6.9, 3.1, 4.9, 1.5, 1],
            [5.5, 2.3, 4.0, 1.3, 1],
            [6.5, 2.8, 4.6, 1.5, 1],
            [6.3, 3.3, 6.0, 2.5, 2],
            [5.8, 2.7, 5.1, 1.9, 2],
            [7.1, 3.0, 5.9, 2.1, 2],
            [6.3, 2.9, 5.6, 1.8, 2],
            [6.5, 3.0, 5.8, 2.2, 2]
        ],
        "columns": ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"],
        "label_index": 4,
        "use_evolution": True,
        "focus_model": "xgb",
        "population_size": 8,
        "generations": 3,
        "mutation_rate": 0.1,
        "crossover_rate": 0.8
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Evolution generation successful!")
            print(f"   Selected model: {data['selected_model']}")
            print(f"   ROC AUC: {data['roc_auc']:.3f}")
            print(f"   F1 Score: {data['f1_score']:.3f}")
            print(f"   Evolution used: {data['evolution_used']}")
            print(f"   Focus model: {data['focus_model']}")
            print(f"   Generation time: {data.get('generation_time', end_time - start_time):.2f}s")
            return True
        else:
            print(f"❌ Evolution generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Evolution generation error: {e}")
        return False

def test_evolution_stats_endpoint():
    """Test evolution stats endpoint"""
    print("🔍 Testing evolution stats endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/evolution/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Evolution stats endpoint working: {data['total_evolutions']} evolutions")
            return True
        else:
            print(f"❌ Evolution stats endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Evolution stats endpoint error: {e}")
        return False

def test_stats_endpoint():
    """Test stats endpoint"""
    print("🔍 Testing stats endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint working: {data['total_generations']} generations")
            return True
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid data"""
    print("🔍 Testing error handling...")
    
    # Test with invalid data
    invalid_data = {
        "data": [],  # Empty data
        "columns": ["col1", "col2"],
        "label_index": 0
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/generate",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 422:  # Validation error
            print("✅ Error handling working - validation error caught")
            return True
        else:
            print(f"❌ Error handling failed: expected 422, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error handling test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting BeeMind improvement tests...")
    print("=" * 50)
    
    tests = [
        test_health_endpoint,
        test_api_docs,
        test_generate_endpoint,
        test_evolution_endpoint,
        test_evolution_stats_endpoint,
        test_history_endpoint,
        test_stats_endpoint,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! BeeMind improvements are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

