"""
BeeMind Exception Handling Module
Centralized exception classes and error handling utilities
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('beemind.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BeeMindError(Exception):
    """Base exception for all BeeMind errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        
        # Log the error
        logger.error(f"BeeMind Error [{error_code}]: {message}", extra={
            'error_code': error_code,
            'details': details,
            'timestamp': self.timestamp.isoformat()
        })

class ModelGenerationError(BeeMindError):
    """Raised when model generation fails"""
    
    def __init__(self, message: str, model_type: Optional[str] = None, params: Optional[Dict[str, Any]] = None):
        super().__init__(message, "MODEL_GENERATION_ERROR", {
            'model_type': model_type,
            'params': params
        })

class ModelEvaluationError(BeeMindError):
    """Raised when model evaluation fails"""
    
    def __init__(self, message: str, model_type: Optional[str] = None, dataset_info: Optional[Dict[str, Any]] = None):
        super().__init__(message, "MODEL_EVALUATION_ERROR", {
            'model_type': model_type,
            'dataset_info': dataset_info
        })

class DataValidationError(BeeMindError):
    """Raised when input data validation fails"""
    
    def __init__(self, message: str, data_info: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATA_VALIDATION_ERROR", {
            'data_info': data_info
        })

class HiveMemoryError(BeeMindError):
    """Raised when HiveMemory operations fail"""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(message, "HIVE_MEMORY_ERROR", {
            'operation': operation
        })

class QueenSelectionError(BeeMindError):
    """Raised when queen selection fails"""
    
    def __init__(self, message: str, candidates_count: Optional[int] = None):
        super().__init__(message, "QUEEN_SELECTION_ERROR", {
            'candidates_count': candidates_count
        })

def handle_exception(func):
    """Decorator for handling exceptions in BeeMind functions"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BeeMindError:
            # Re-raise BeeMind errors as they're already handled
            raise
        except Exception as e:
            # Convert generic exceptions to BeeMindError
            logger.exception(f"Unexpected error in {func.__name__}: {str(e)}")
            raise BeeMindError(
                f"Unexpected error in {func.__name__}: {str(e)}",
                "UNEXPECTED_ERROR",
                {'function': func.__name__, 'args': str(args), 'kwargs': str(kwargs)}
            )
    return wrapper

def log_operation(operation_name: str, details: Optional[Dict[str, Any]] = None):
    """Log operation details for monitoring"""
    logger.info(f"Operation: {operation_name}", extra={
        'operation': operation_name,
        'details': details or {},
        'timestamp': datetime.utcnow().isoformat()
    })
