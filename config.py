"""
BeeMind Configuration Management
Centralized configuration for environment variables and settings
"""

import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    API_TITLE: str = "BeeMind API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Evolutionary AI system inspired by bee colony dynamics"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # CORS Configuration
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # AI Engine Configuration
    DRONE_COUNT: int = 5
    TEST_SIZE: float = 0.2
    RANDOM_STATE: int = 42
    
    # Evolution Configuration
    DEFAULT_POPULATION_SIZE: int = 10
    DEFAULT_GENERATIONS: int = 5
    DEFAULT_MUTATION_RATE: float = 0.1
    DEFAULT_CROSSOVER_RATE: float = 0.8
    DEFAULT_ELITE_SIZE: int = 2
    DEFAULT_FOCUS_MODEL: str = "xgb"
    ENABLE_MODEL_CROSSOVER: bool = True
    MODEL_CROSSOVER_RATE: float = 0.1
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "beemind.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # HiveMemory Configuration
    HIVE_LOG_FILE: str = "hivememory_log.json"
    MAX_LOG_SIZE: int = 1000
    
    # Model Configuration
    MODEL_TYPES: list = ["xgb", "rf", "gb", "lr"]
    
    # XGBoost Configuration
    XGB_N_ESTIMATORS_MIN: int = 50
    XGB_N_ESTIMATORS_MAX: int = 300
    XGB_MAX_DEPTH_MIN: int = 3
    XGB_MAX_DEPTH_MAX: int = 10
    XGB_LEARNING_RATE_MIN: float = 0.01
    XGB_LEARNING_RATE_MAX: float = 0.3
    
    # Random Forest Configuration
    RF_N_ESTIMATORS_MIN: int = 50
    RF_N_ESTIMATORS_MAX: int = 200
    RF_MAX_DEPTH_MIN: int = 3
    RF_MAX_DEPTH_MAX: int = 15
    RF_MIN_SAMPLES_SPLIT_MIN: int = 2
    RF_MIN_SAMPLES_SPLIT_MAX: int = 10
    
    # Gradient Boosting Configuration
    GB_N_ESTIMATORS_MIN: int = 50
    GB_N_ESTIMATORS_MAX: int = 200
    GB_MAX_DEPTH_MIN: int = 3
    GB_MAX_DEPTH_MAX: int = 8
    GB_LEARNING_RATE_MIN: float = 0.01
    GB_LEARNING_RATE_MAX: float = 0.3
    
    # Logistic Regression Configuration
    LR_C_MIN: float = 0.1
    LR_C_MAX: float = 10.0
    LR_MAX_ITER: int = 1000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_setting(key: str, default: Optional[str] = None) -> str:
    """Get a setting value with fallback to environment variable"""
    return getattr(settings, key, os.getenv(key, default))

def is_development() -> bool:
    """Check if running in development mode"""
    return settings.ENVIRONMENT.lower() == "development"

def is_production() -> bool:
    """Check if running in production mode"""
    return settings.ENVIRONMENT.lower() == "production"

def is_debug() -> bool:
    """Check if debug mode is enabled"""
    return settings.DEBUG or is_development()

