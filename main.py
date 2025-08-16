from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import pandas as pd
import traceback
import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ai_engine.drones.drone_generator import generate_drone
from ai_engine.workers.worker_pool import evaluate_model
from ai_engine.queen.queen import select_best_model
from ai_engine.memory.hivememory import log_generation_result, get_generation_history, get_best_performance
from ai_engine.evolution.genetic_algorithm import GeneticAlgorithm
from ai_engine.exceptions import BeeMindError, ModelGenerationError, ModelEvaluationError, DataValidationError
from cors_config import setup_cors
from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BeeMind API",
    description="""
    🐝 BeeMind - Evolutionary AI System
    
    An intelligent AI system inspired by bee colony dynamics that automatically generates,
    evaluates, and evolves machine learning models.
    
    ## Features
    - **Drone Generation**: Creates diverse ML models with random hyperparameters
    - **Worker Evaluation**: Evaluates models using ROC AUC and F1 scores
    - **Queen Selection**: Selects the best performing model
    - **Hive Memory**: Logs and tracks evolution history
    - **Blockchain Integration**: Tamper-proof logging of model decisions
    
    ## Quick Start
    1. Send your dataset to `/generate` endpoint
    2. Receive the best performing model and its metrics
    3. Monitor evolution history via `/history` endpoint
    
    ## Model Types
    - XGBoost Classifier
    - Random Forest Classifier
    - Gradient Boosting Classifier
    - Logistic Regression
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "BeeMind Team",
        "url": "https://beemind.dev",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Strategic CORS setup for api.beemind.dev
app = setup_cors(app)

# Global exception handler for BeeMind errors
@app.exception_handler(BeeMindError)
async def beemind_exception_handler(request, exc: BeeMindError):
    """Handle BeeMind-specific exceptions"""
    logger.error(f"BeeMind error: {exc.message}", extra={
        "error_code": exc.error_code,
        "details": exc.details,
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
            "timestamp": exc.timestamp.isoformat(),
            "type": "BeeMind Error"
        }
    )

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {"message": "BeeMind API is running!", "version": "1.0.0"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for load balancer and monitoring
    
    Returns:
        HealthResponse: Service health status and information
    """
    try:
        # Basic health checks
        health_status = "healthy"
        
        # Check if we can import AI engine modules
        try:
            from ai_engine.drones.drone_generator import generate_drone
            from ai_engine.workers.worker_pool import evaluate_model
            from ai_engine.queen.queen import select_best_model
        except ImportError as e:
            logger.error(f"Health check failed - import error: {e}")
            health_status = "unhealthy"
        
        # Check if log directory is writable
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
                f.write("health_check")
        except Exception as e:
            logger.error(f"Health check failed - file system error: {e}")
            health_status = "unhealthy"
        
        return HealthResponse(
            status=health_status,
            service="BeeMind",
            version="1.0.0",
            environment=os.getenv("ENVIRONMENT", "development"),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            service="BeeMind",
            version="1.0.0",
            environment=os.getenv("ENVIRONMENT", "development"),
            timestamp=datetime.utcnow().isoformat()
        )

@app.get("/api/health", response_model=HealthResponse)
async def api_health_check():
    """
    Alternative health endpoint for nginx routing
    
    Returns:
        HealthResponse: Service health status and information
    """
    return await health_check()

@app.get("/history", response_model=HistoryResponse)
async def get_generation_history(limit: int = 100):
    """
    Get generation history from HiveMemory
    
    Args:
        limit: Maximum number of entries to return (default: 100)
        
    Returns:
        HistoryResponse: Generation history and statistics
    """
    try:
        history = get_generation_history(limit)
        best_performance = get_best_performance()
        
        return HistoryResponse(
            history=history,
            total_entries=len(history),
            best_performance=best_performance
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": str(e),
                "type": "History Retrieval Error",
                "message": "Failed to retrieve generation history"
            }
        )

@app.get("/evolution/stats")
async def get_evolution_stats():
    """
    Get evolution statistics and performance metrics
    
    Returns:
        Dict: Evolution statistics including best models, improvement trends, etc.
    """
    try:
        history = get_generation_history()
        
        if not history:
            return {
                "total_evolutions": 0,
                "evolution_models": {},
                "best_evolution_performance": 0.0,
                "improvement_trends": [],
                "focus_model_distribution": {}
            }
        
        # Filter evolution results
        evolution_results = [entry for entry in history if entry.get("metadata", {}).get("evolution_used", False)]
        
        if not evolution_results:
            return {
                "total_evolutions": 0,
                "evolution_models": {},
                "best_evolution_performance": 0.0,
                "improvement_trends": [],
                "focus_model_distribution": {}
            }
        
        # Calculate evolution statistics
        focus_models = [entry.get("metadata", {}).get("focus_model", "unknown") for entry in evolution_results]
        focus_distribution = {}
        for model in focus_models:
            focus_distribution[model] = focus_distribution.get(model, 0) + 1
        
        roc_auc_scores = [entry.get("roc_auc", 0.0) for entry in evolution_results]
        best_evolution_performance = max(roc_auc_scores)
        
        # Calculate improvement trends
        improvement_trends = []
        for entry in evolution_results:
            if "evolution_stats" in entry.get("metadata", {}):
                stats = entry["metadata"]["evolution_stats"]
                improvement_trends.append({
                    "timestamp": entry.get("timestamp"),
                    "improvement": stats.get("improvement", 0.0),
                    "generations": entry.get("metadata", {}).get("generations", 0),
                    "focus_model": entry.get("metadata", {}).get("focus_model", "unknown")
                })
        
        return {
            "total_evolutions": len(evolution_results),
            "evolution_models": {
                "total": len(evolution_results),
                "best_performance": best_evolution_performance,
                "average_performance": sum(roc_auc_scores) / len(roc_auc_scores)
            },
            "best_evolution_performance": best_evolution_performance,
            "improvement_trends": improvement_trends,
            "focus_model_distribution": focus_distribution,
            "recent_evolutions": evolution_results[-10:] if len(evolution_results) > 10 else evolution_results
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve evolution stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": str(e),
                "type": "Evolution Stats Error",
                "message": "Failed to retrieve evolution statistics"
            }
        )

@app.get("/stats")
async def get_system_stats():
    """
    Get system statistics and performance metrics
    
    Returns:
        Dict: System statistics including total generations, best performance, etc.
    """
    try:
        history = get_generation_history()
        best_performance = get_best_performance()
        
        if not history:
            return {
                "total_generations": 0,
                "best_roc_auc": 0.0,
                "best_f1_score": 0.0,
                "average_roc_auc": 0.0,
                "average_f1_score": 0.0,
                "model_distribution": {},
                "last_generation": None
            }
        
        # Calculate statistics
        roc_auc_scores = [entry.get("roc_auc", 0.0) for entry in history]
        f1_scores = [entry.get("f1", 0.0) for entry in history]
        model_types = [entry.get("type", "unknown") for entry in history]
        
        model_distribution = {}
        for model_type in model_types:
            model_distribution[model_type] = model_distribution.get(model_type, 0) + 1
        
        return {
            "total_generations": len(history),
            "best_roc_auc": max(roc_auc_scores),
            "best_f1_score": max(f1_scores),
            "average_roc_auc": sum(roc_auc_scores) / len(roc_auc_scores),
            "average_f1_score": sum(f1_scores) / len(f1_scores),
            "model_distribution": model_distribution,
            "last_generation": history[-1] if history else None,
            "best_performance": best_performance
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": str(e),
                "type": "Stats Retrieval Error",
                "message": "Failed to retrieve system statistics"
            }
        )

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle preflight OPTIONS requests for CORS"""
    return {"message": "OK"}

class DatasetInput(BaseModel):
    """Input dataset for model generation"""
    data: List[List[Any]] = Field(..., description="Dataset rows as list of lists")
    columns: List[str] = Field(..., description="Column names for the dataset")
    label_index: int = Field(..., description="Index of the label column", ge=0)
    
    # Evolution parameters
    use_evolution: bool = Field(False, description="Use genetic algorithm evolution")
    focus_model: str = Field("xgb", description="Primary model type to focus on (xgb, rf, gb, lr)")
    population_size: int = Field(10, description="Population size for evolution", ge=5, le=50)
    generations: int = Field(5, description="Number of generations", ge=1, le=20)
    mutation_rate: float = Field(0.1, description="Mutation rate", ge=0.0, le=1.0)
    crossover_rate: float = Field(0.8, description="Crossover rate", ge=0.0, le=1.0)
    
    @validator('data')
    def validate_data(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Data cannot be empty')
        if len(v) < 4:
            raise ValueError('Dataset must have at least 4 rows')
        return v
    
    @validator('columns')
    def validate_columns(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Columns cannot be empty')
        if len(set(v)) != len(v):
            raise ValueError('Column names must be unique')
        return v
    
    @validator('label_index')
    def validate_label_index(cls, v, values):
        if 'columns' in values and v >= len(values['columns']):
            raise ValueError('Label index must be less than number of columns')
        return v

class GenerationResponse(BaseModel):
    """Response from model generation"""
    selected_model: str = Field(..., description="Type of the selected model")
    roc_auc: float = Field(..., description="ROC AUC score of the best model")
    f1_score: float = Field(..., description="F1 score of the best model")
    params: Dict[str, Any] = Field(..., description="Model parameters")
    total_drones: int = Field(..., description="Total number of drones generated")
    generation_time: Optional[float] = Field(None, description="Generation time in seconds")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    
    # Evolution results
    evolution_used: bool = Field(False, description="Whether evolution was used")
    generation_history: Optional[List[Dict[str, Any]]] = Field(None, description="Evolution generation history")
    evolution_stats: Optional[Dict[str, Any]] = Field(None, description="Evolution statistics")
    focus_model: Optional[str] = Field(None, description="Focus model type used")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment")
    timestamp: str = Field(..., description="Current timestamp")
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")

class HistoryResponse(BaseModel):
    """Generation history response"""
    history: List[Dict[str, Any]] = Field(..., description="Generation history")
    total_entries: int = Field(..., description="Total number of entries")
    best_performance: Optional[Dict[str, Any]] = Field(None, description="Best performing model")

@app.post("/generate", response_model=GenerationResponse)
async def generate_best_model(input_data: DatasetInput):
    """
    Generate and evaluate multiple ML models, returning the best performing one
    
    This endpoint implements the BeeMind evolutionary algorithm:
    1. Generates multiple "drones" (ML models) with random hyperparameters
    2. Evaluates each model using ROC AUC and F1 scores
    3. Selects the best performing model (Queen selection)
    4. Logs the result to HiveMemory
    
    Args:
        input_data: DatasetInput containing the training data
        
    Returns:
        GenerationResponse: Best model information and performance metrics
        
    Raises:
        HTTPException: If generation fails or data is invalid
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"Starting model generation: {len(input_data.data)} rows, {len(input_data.columns)} columns")
        
        # Create DataFrame
        df = pd.DataFrame(input_data.data, columns=input_data.columns)
        label_col = input_data.columns[input_data.label_index]
        X = df.drop(columns=[label_col])
        y = df[label_col]
        
        logger.info(f"Data prepared: Features shape={X.shape}, Labels shape={y.shape}, Unique labels={len(y.unique())}")
        
        # Check if evolution should be used
        if input_data.use_evolution:
            logger.info(f"Using genetic algorithm evolution with focus: {input_data.focus_model}")
            
            # Initialize genetic algorithm
            ga = GeneticAlgorithm(
                population_size=input_data.population_size,
                generations=input_data.generations,
                mutation_rate=input_data.mutation_rate,
                crossover_rate=input_data.crossover_rate,
                focus_model=input_data.focus_model
            )
            
            # Run evolution
            evolution_result = ga.evolve(X, y)
            
            # Extract best model from evolution
            best_model = evolution_result["best_model"]
            best_metadata = evolution_result["best_metadata"]
            best_fitness = evolution_result["best_fitness"]
            
            # Get final evaluation result
            final_evaluation = evaluate_model(best_model, X, y)
            
            # Log result
            try:
                log_generation_result({
                    "model": best_model,
                    "roc_auc": final_evaluation["roc_auc"],
                    "f1": final_evaluation["f1"],
                    "metadata": {
                        **best_metadata,
                        "evolution_used": True,
                        "focus_model": input_data.focus_model,
                        "generations": input_data.generations
                    }
                })
                logger.info("Evolution result logged to HiveMemory")
            except Exception as e:
                logger.error(f"Failed to log evolution result: {e}")
            
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return GenerationResponse(
                selected_model=best_metadata["type"],
                roc_auc=final_evaluation["roc_auc"],
                f1_score=final_evaluation["f1"],
                params=best_metadata["params"],
                total_drones=len(evolution_result["final_population"]),
                generation_time=generation_time,
                evolution_used=True,
                generation_history=evolution_result["generation_history"],
                evolution_stats=evolution_result["evolution_stats"],
                focus_model=input_data.focus_model
            )
        
        # Standard generation (non-evolutionary)
        logger.info("Using standard drone generation")
        drone_results = []
        successful_drones = 0
        
        for i in range(settings.DRONE_COUNT):
            try:
                logger.info(f"Generating drone {i+1}/{settings.DRONE_COUNT}...")
                model, metadata = generate_drone()
                logger.info(f"Generated {metadata['type']} model")
                
                result = evaluate_model(model, X, y)
                logger.info(f"Drone {i+1} evaluation: ROC AUC={result['roc_auc']:.3f}, F1={result['f1']:.3f}")
                drone_results.append(result)
                successful_drones += 1
                
            except (ModelGenerationError, ModelEvaluationError) as e:
                logger.warning(f"Drone {i+1} failed: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error with drone {i+1}: {e}")
                continue
        
        if not drone_results:
            logger.error("No drones could be evaluated successfully")
            return GenerationResponse(
                error="No drones could be evaluated successfully",
                selected_model="None",
                roc_auc=0.0,
                f1_score=0.0,
                params={},
                total_drones=0,
                generation_time=(datetime.utcnow() - start_time).total_seconds()
            )
        
        # Select best model
        best = select_best_model(drone_results)
        logger.info(f"Best model selected: {best['metadata']['type']} with ROC AUC: {best['roc_auc']:.3f}")
        
        # Log result
        try:
            log_generation_result(best)
            logger.info("Result logged to HiveMemory")
        except Exception as e:
            logger.error(f"Failed to log result: {e}")
        
        generation_time = (datetime.utcnow() - start_time).total_seconds()
        
        return GenerationResponse(
            selected_model=best["metadata"]["type"],
            roc_auc=best["roc_auc"],
            f1_score=best["f1"],
            params=best["metadata"]["params"],
            total_drones=successful_drones,
            generation_time=generation_time
        )
        
    except DataValidationError as e:
        logger.error(f"Data validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": str(e),
                "type": "Data Validation Error",
                "message": "Invalid input data provided"
            }
        )
    except (ModelGenerationError, ModelEvaluationError) as e:
        logger.error(f"AI engine error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": str(e),
                "type": "AI Engine Error",
                "message": "Failed to generate or evaluate models"
            }
        )
    except Exception as e:
        logger.error(f"Critical error in generate_best_model: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": str(e),
                "type": "BeeMind Generation Error",
                "message": "Failed to generate and evaluate drone models"
            }
        )
