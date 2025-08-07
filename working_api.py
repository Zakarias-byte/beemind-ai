#!/usr/bin/env python3
"""
Working BeeMind API - Step by step integration
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import json
import logging
from typing import List, Dict, Any
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BeeMind Working API", version="1.0.0")

class DatasetInput(BaseModel):
    data: List[List[float]]
    columns: List[str] 
    label_index: int

@app.get("/")
def root():
    return {"message": "🐝 BeeMind Working API", "status": "running"}

@app.get("/test-components")
def test_components():
    """Test if all BeeMind components can be imported"""
    try:
        from ai_engine.drones.drone_generator import generate_drone
        from ai_engine.workers.worker_pool import evaluate_model
        from ai_engine.queen.queen import select_best_model
        from ai_engine.memory.hivememory import log_generation_result
        
        return {
            "status": "success",
            "components": {
                "drone_generator": "✅ imported",
                "worker_pool": "✅ imported", 
                "queen_selector": "✅ imported",
                "hive_memory": "✅ imported"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/generate-simple")
def generate_simple(input_data: DatasetInput):
    """Simplified generation endpoint for testing"""
    try:
        logger.info(f"🔄 Received data: {len(input_data.data)} rows")
        
        # Basic validation
        if not input_data.data:
            raise HTTPException(status_code=400, detail="No data provided")
            
        # Create DataFrame
        df = pd.DataFrame(input_data.data, columns=input_data.columns)
        logger.info(f"📊 DataFrame created: {df.shape}")
        
        # Simple response without ML for now
        return {
            "status": "success",
            "data_shape": df.shape,
            "columns": input_data.columns,
            "message": "Data processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
def generate_best_model(input_data: DatasetInput):
    """Full BeeMind generation endpoint"""
    try:
        logger.info(f"🔄 Starting BeeMind generation...")
        
        # Import components inside the function to isolate any import issues
        from ai_engine.drones.drone_generator import generate_drone
        from ai_engine.workers.worker_pool import evaluate_model
        from ai_engine.queen.queen import select_best_model
        from ai_engine.memory.hivememory import log_generation_result
        
        logger.info("✅ Components imported successfully")
        
        # Validate input
        if not input_data.data or len(input_data.data) < 4:
            raise HTTPException(status_code=400, detail="Need at least 4 data points")
            
        # Create DataFrame
        df = pd.DataFrame(input_data.data, columns=input_data.columns)
        label_col = input_data.columns[input_data.label_index]
        X = df.drop(columns=[label_col])
        y = df[label_col]
        
        logger.info(f"📊 Data prepared: X{X.shape}, y{y.shape}, classes: {y.unique()}")
        
        # Generate and evaluate drones
        drone_results = []
        for i in range(3):  # Reduced to 3 for faster testing
            try:
                logger.info(f"🤖 Generating drone {i+1}/3...")
                model, metadata = generate_drone()
                
                logger.info(f"👷 Evaluating {metadata['type']}...")
                result = evaluate_model(model, X, y)
                
                drone_results.append(result)
                logger.info(f"✅ Drone {i+1}: ROC AUC={result['roc_auc']:.3f}")
                
            except Exception as e:
                logger.warning(f"⚠️ Drone {i+1} failed: {e}")
                continue
        
        if not drone_results:
            raise HTTPException(status_code=500, detail="No drones succeeded")
        
        # Select best model
        best = select_best_model(drone_results)
        logger.info(f"👑 Best: {best['metadata']['type']}")
        
        # Log result
        try:
            log_generation_result(best)
            logger.info("🧠 Logged to HiveMemory")
        except Exception as e:
            logger.warning(f"⚠️ Logging failed: {e}")
        
        return {
            "selected_model": best["metadata"]["type"],
            "roc_auc": float(best["roc_auc"]),
            "f1_score": float(best["f1"]),
            "total_drones": len(drone_results),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": "BeeMind Error",
                "traceback": traceback.format_exc()
            }
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Working BeeMind API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
