import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from ..exceptions import HiveMemoryError, handle_exception, log_operation

logger = logging.getLogger(__name__)

HIVE_LOG_FILE = "hivememory_log.json"
MAX_LOG_SIZE = 1000  # Maximum number of entries to keep

@handle_exception
def log_generation_result(result: Dict[str, Any]) -> None:
    """Log generation result to HiveMemory with proper error handling"""
    log_operation("log_generation_result", {
        "model_type": result.get("metadata", {}).get("type", "unknown"),
        "roc_auc": result.get("roc_auc", 0.0)
    })
    
    try:
        # Validate result structure
        if not isinstance(result, dict):
            raise HiveMemoryError("Result must be a dictionary")
        
        if "metadata" not in result:
            raise HiveMemoryError("Result missing metadata")
        
        if "roc_auc" not in result or "f1" not in result:
            raise HiveMemoryError("Result missing performance metrics")
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": result["metadata"]["type"],
            "roc_auc": result["roc_auc"],
            "f1": result["f1"],
            "params": result["metadata"]["params"],
            "generation_id": f"gen_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Add additional metadata if available
        if "evaluation_timestamp" in result.get("metadata", {}):
            log_entry["evaluation_timestamp"] = result["metadata"]["evaluation_timestamp"]
        
        # Write to file with proper error handling
        _write_log_entry(log_entry)
        
        logger.info(f"Logged generation result: {log_entry['type']} with ROC AUC: {log_entry['roc_auc']:.3f}")
        
    except Exception as e:
        if isinstance(e, HiveMemoryError):
            raise
        raise HiveMemoryError(f"Failed to log generation result: {str(e)}", operation="log_generation_result")

def _write_log_entry(log_entry: Dict[str, Any]) -> None:
    """Write log entry to file with rotation"""
    try:
        # Read existing logs
        existing_logs = []
        if os.path.exists(HIVE_LOG_FILE):
            try:
                with open(HIVE_LOG_FILE, "r") as f:
                    existing_logs = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning("Corrupted or missing log file, starting fresh")
                existing_logs = []
        
        # Add new entry
        existing_logs.append(log_entry)
        
        # Rotate logs if too large
        if len(existing_logs) > MAX_LOG_SIZE:
            existing_logs = existing_logs[-MAX_LOG_SIZE:]
            logger.info(f"Log rotation: kept last {MAX_LOG_SIZE} entries")
        
        # Write back to file
        with open(HIVE_LOG_FILE, "w") as f:
            json.dump(existing_logs, f, indent=2)
            
    except Exception as e:
        raise HiveMemoryError(f"Failed to write log entry: {str(e)}", operation="write_log_entry")

def get_generation_history(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve generation history from HiveMemory"""
    try:
        if not os.path.exists(HIVE_LOG_FILE):
            return []
        
        with open(HIVE_LOG_FILE, "r") as f:
            logs = json.load(f)
        
        # Return most recent entries
        return logs[-limit:] if limit else logs
        
    except Exception as e:
        logger.error(f"Failed to retrieve generation history: {e}")
        return []

def get_best_performance() -> Dict[str, Any]:
    """Get the best performing model from history"""
    try:
        history = get_generation_history()
        if not history:
            return {}
        
        best_entry = max(history, key=lambda x: x.get("roc_auc", 0.0))
        return best_entry
        
    except Exception as e:
        logger.error(f"Failed to get best performance: {e}")
        return {}
