import logging
from typing import List, Dict, Any
from ..exceptions import QueenSelectionError, handle_exception, log_operation

logger = logging.getLogger(__name__)

@handle_exception
def select_best_model(drone_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Select the best model from drone results based on ROC AUC score"""
    log_operation("select_best_model", {
        "candidates_count": len(drone_results),
        "step": "starting"
    })
    
    try:
        if not drone_results:
            raise QueenSelectionError("No drone results provided for selection", candidates_count=0)
        
        if len(drone_results) == 1:
            logger.info("Only one drone available, selecting it as best")
            best_model = drone_results[0]
        else:
            # Filter out failed evaluations (those with errors)
            valid_results = [drone for drone in drone_results if "error" not in drone.get("metadata", {})]
            
            if not valid_results:
                raise QueenSelectionError("No valid drone results found", candidates_count=len(drone_results))
            
            # Select best model based on ROC AUC
            best_model = max(valid_results, key=lambda d: d["roc_auc"])
            
            logger.info(f"Selected best model: {best_model['metadata']['type']} with ROC AUC: {best_model['roc_auc']:.3f}")
        
        log_operation("select_best_model", {
            "step": "completed",
            "selected_model_type": best_model["metadata"]["type"],
            "selected_roc_auc": best_model["roc_auc"],
            "total_candidates": len(drone_results),
            "valid_candidates": len([d for d in drone_results if "error" not in d.get("metadata", {})])
        })
        
        return best_model
        
    except Exception as e:
        if isinstance(e, QueenSelectionError):
            raise
        raise QueenSelectionError(
            f"Failed to select best model: {str(e)}",
            candidates_count=len(drone_results) if drone_results else 0
        )
