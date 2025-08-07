#!/usr/bin/env python3
"""
Robust BeeMind API Server with comprehensive error handling
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import traceback
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import BeeMind components
try:
    from ai_engine.drones.drone_generator import generate_drone
    from ai_engine.workers.worker_pool import evaluate_model
    from ai_engine.queen.queen import select_best_model
    from ai_engine.memory.hivememory import log_generation_result
    logger.info("✅ All BeeMind components imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import BeeMind components: {e}")
    raise

# Create FastAPI app
app = FastAPI(
    title="BeeMind API",
    description="🐝 Evolutionary AI system inspired by bee colony dynamics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DatasetInput(BaseModel):
    data: List[List[float]]
    columns: List[str]
    label_index: int

class BeeMindResponse(BaseModel):
    selected_model: str
    roc_auc: float
    f1_score: float
    params: Dict[str, Any]
    total_drones: int
    generation_time: float

@app.get("/")
def root():
    """Root endpoint - API status"""
    return {
        "message": "🐝 BeeMind API is running!",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": ["/generate", "/health", "/docs"]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "BeeMind",
        "components": {
            "drone_generator": "✅",
            "worker_pool": "✅", 
            "queen_selector": "✅",
            "hive_memory": "✅"
        }
    }

@app.post("/generate", response_model=BeeMindResponse)
def generate_best_model(input_data: DatasetInput):
    """
    Generate and evaluate drone models, select the best one
    
    This endpoint:
    1. 🤖 Generates 5 random drone models
    2. 👷 Evaluates each drone on the provided dataset
    3. 👑 Selects the best performing drone
    4. 🧠 Logs the result to HiveMemory
    5. 📊 Returns the best model's performance metrics
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"🔄 Processing request: {len(input_data.data)} rows, {len(input_data.columns)} columns")
        
        # Validate input
        if not input_data.data:
            raise HTTPException(status_code=400, detail="No data provided")
        
        if input_data.label_index >= len(input_data.columns):
            raise HTTPException(status_code=400, detail="Invalid label_index")
        
        # Create DataFrame
        try:
            df = pd.DataFrame(input_data.data, columns=input_data.columns)
            label_col = input_data.columns[input_data.label_index]
            X = df.drop(columns=[label_col])
            y = df[label_col]
            logger.info(f"📊 Features: {X.shape}, Labels: {y.shape}, Classes: {y.unique()}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Data processing error: {str(e)}")
        
        # Generate and evaluate drones
        drone_results = []
        for i in range(5):
            try:
                logger.info(f"🤖 Generating drone {i+1}/5...")
                model, metadata = generate_drone()
                
                logger.info(f"👷 Evaluating {metadata['type']}...")
                result = evaluate_model(model, X, y)
                
                drone_results.append(result)
                logger.info(f"✅ Drone {i+1}: {metadata['type']} - ROC AUC={result['roc_auc']:.3f}, F1={result['f1']:.3f}")
                
            except Exception as e:
                logger.warning(f"⚠️ Drone {i+1} failed: {e}")
                continue
        
        if not drone_results:
            raise HTTPException(
                status_code=500,
                detail="No drones could be evaluated successfully"
            )
        
        # Select best model
        try:
            best = select_best_model(drone_results)
            logger.info(f"👑 Best model: {best['metadata']['type']} with ROC AUC: {best['roc_auc']:.3f}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model selection error: {str(e)}")
        
        # Log result
        try:
            log_generation_result(best)
            logger.info("🧠 Result logged to HiveMemory")
        except Exception as e:
            logger.warning(f"⚠️ Logging failed: {e}")
        
        generation_time = time.time() - start_time
        
        return BeeMindResponse(
            selected_model=best["metadata"]["type"],
            roc_auc=best["roc_auc"],
            f1_score=best["f1"],
            params=best["metadata"]["params"],
            total_drones=len(drone_results),
            generation_time=generation_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": "BeeMind Generation Error",
                "message": "Failed to generate and evaluate drone models"
            }
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting BeeMind API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
