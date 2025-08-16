"""
BeeMind Database Integration Module
PostgreSQL integration for model metadata, artifacts, and versioning
"""

import os
import logging
import json
import pickle
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import numpy as np

from ..exceptions import BeeMindError, handle_exception, log_operation

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://beemind:password@localhost:5432/beemind')

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for database models
Base = declarative_base()

class ModelMetadata(Base):
    """Database model for storing model metadata"""
    __tablename__ = "model_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String, unique=True, index=True)
    model_type = Column(String, index=True)
    model_name = Column(String)
    version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Performance metrics
    roc_auc = Column(Float)
    f1_score = Column(Float)
    accuracy = Column(Float)
    
    # Model parameters
    parameters = Column(JSON)
    
    # Dataset information
    dataset_hash = Column(String, index=True)
    dataset_size = Column(Integer)
    feature_count = Column(Integer)
    
    # Evolution information
    generation = Column(Integer)
    fitness_score = Column(Float)
    evolution_id = Column(String, index=True)
    
    # Model status
    is_active = Column(Boolean, default=True)
    is_deployed = Column(Boolean, default=False)
    
    # Additional metadata
    tags = Column(JSON, default=list)
    description = Column(Text)
    author = Column(String)
    
    # Model artifacts
    model_path = Column(String)
    feature_importance = Column(JSON)
    confusion_matrix = Column(JSON)
    
    # Performance history
    performance_history = Column(JSON, default=list)

class EvolutionSession(Base):
    """Database model for storing evolution sessions"""
    __tablename__ = "evolution_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Evolution configuration
    population_size = Column(Integer)
    generations = Column(Integer)
    mutation_rate = Column(Float)
    crossover_rate = Column(Float)
    focus_model = Column(String)
    
    # Evolution results
    best_fitness = Column(Float)
    avg_fitness = Column(Float)
    improvement = Column(Float)
    
    # Session status
    status = Column(String, default='running')  # running, completed, failed
    progress = Column(Float, default=0.0)
    
    # Generation history
    generation_history = Column(JSON, default=list)
    
    # Dataset information
    dataset_hash = Column(String)
    dataset_size = Column(Integer)
    
    # Additional metadata
    description = Column(Text)
    tags = Column(JSON, default=list)

class ModelArtifact(Base):
    """Database model for storing model artifacts"""
    __tablename__ = "model_artifacts"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String, index=True)
    artifact_type = Column(String)  # model, metadata, evaluation, visualization
    artifact_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Artifact metadata
    size_bytes = Column(Integer)
    checksum = Column(String)
    format = Column(String)  # pickle, json, png, etc.
    
    # Additional metadata
    description = Column(Text)
    tags = Column(JSON, default=list)

class PerformanceLog(Base):
    """Database model for storing performance logs"""
    __tablename__ = "performance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Performance metrics
    roc_auc = Column(Float)
    f1_score = Column(Float)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    
    # Runtime metrics
    inference_time_ms = Column(Float)
    memory_usage_mb = Column(Float)
    
    # Context
    dataset_hash = Column(String)
    environment = Column(String)  # production, staging, development
    
    # Additional metadata
    metadata = Column(JSON, default=dict)

# Create tables
Base.metadata.create_all(bind=engine)

class DatabaseManager:
    """Database manager for BeeMind operations"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    @handle_exception
    def save_model_metadata(self, model_data: Dict[str, Any]) -> str:
        """Save model metadata to database"""
        log_operation("save_model_metadata", {"model_id": model_data.get('model_id')})
        
        with self.get_session() as session:
            try:
                # Create model metadata record
                metadata = ModelMetadata(
                    model_id=model_data['model_id'],
                    model_type=model_data['model_type'],
                    model_name=model_data.get('model_name', f"Model_{model_data['model_id']}"),
                    version=model_data.get('version', '1.0.0'),
                    roc_auc=model_data.get('roc_auc', 0.0),
                    f1_score=model_data.get('f1_score', 0.0),
                    accuracy=model_data.get('accuracy', 0.0),
                    parameters=model_data.get('parameters', {}),
                    dataset_hash=model_data.get('dataset_hash', ''),
                    dataset_size=model_data.get('dataset_size', 0),
                    feature_count=model_data.get('feature_count', 0),
                    generation=model_data.get('generation', 0),
                    fitness_score=model_data.get('fitness_score', 0.0),
                    evolution_id=model_data.get('evolution_id', ''),
                    tags=model_data.get('tags', []),
                    description=model_data.get('description', ''),
                    author=model_data.get('author', 'system'),
                    model_path=model_data.get('model_path', ''),
                    feature_importance=model_data.get('feature_importance', {}),
                    confusion_matrix=model_data.get('confusion_matrix', {}),
                    performance_history=model_data.get('performance_history', [])
                )
                
                session.add(metadata)
                session.commit()
                
                logger.info(f"Saved model metadata: {model_data['model_id']}")
                return model_data['model_id']
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error saving model metadata: {e}")
                raise BeeMindError(f"Failed to save model metadata: {e}")
    
    @handle_exception
    def get_model_metadata(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model metadata from database"""
        with self.get_session() as session:
            try:
                metadata = session.query(ModelMetadata).filter(
                    ModelMetadata.model_id == model_id
                ).first()
                
                if metadata:
                    return {
                        'model_id': metadata.model_id,
                        'model_type': metadata.model_type,
                        'model_name': metadata.model_name,
                        'version': metadata.version,
                        'created_at': metadata.created_at.isoformat(),
                        'updated_at': metadata.updated_at.isoformat(),
                        'roc_auc': metadata.roc_auc,
                        'f1_score': metadata.f1_score,
                        'accuracy': metadata.accuracy,
                        'parameters': metadata.parameters,
                        'dataset_hash': metadata.dataset_hash,
                        'dataset_size': metadata.dataset_size,
                        'feature_count': metadata.feature_count,
                        'generation': metadata.generation,
                        'fitness_score': metadata.fitness_score,
                        'evolution_id': metadata.evolution_id,
                        'is_active': metadata.is_active,
                        'is_deployed': metadata.is_deployed,
                        'tags': metadata.tags,
                        'description': metadata.description,
                        'author': metadata.author,
                        'model_path': metadata.model_path,
                        'feature_importance': metadata.feature_importance,
                        'confusion_matrix': metadata.confusion_matrix,
                        'performance_history': metadata.performance_history
                    }
                return None
                
            except SQLAlchemyError as e:
                logger.error(f"Database error getting model metadata: {e}")
                raise BeeMindError(f"Failed to get model metadata: {e}")
    
    @handle_exception
    def save_evolution_session(self, session_data: Dict[str, Any]) -> str:
        """Save evolution session to database"""
        log_operation("save_evolution_session", {"session_id": session_data.get('session_id')})
        
        with self.get_session() as session:
            try:
                # Create evolution session record
                evolution_session = EvolutionSession(
                    session_id=session_data['session_id'],
                    population_size=session_data.get('population_size', 10),
                    generations=session_data.get('generations', 5),
                    mutation_rate=session_data.get('mutation_rate', 0.1),
                    crossover_rate=session_data.get('crossover_rate', 0.8),
                    focus_model=session_data.get('focus_model', 'xgb'),
                    best_fitness=session_data.get('best_fitness', 0.0),
                    avg_fitness=session_data.get('avg_fitness', 0.0),
                    improvement=session_data.get('improvement', 0.0),
                    status=session_data.get('status', 'running'),
                    progress=session_data.get('progress', 0.0),
                    generation_history=session_data.get('generation_history', []),
                    dataset_hash=session_data.get('dataset_hash', ''),
                    dataset_size=session_data.get('dataset_size', 0),
                    description=session_data.get('description', ''),
                    tags=session_data.get('tags', [])
                )
                
                session.add(evolution_session)
                session.commit()
                
                logger.info(f"Saved evolution session: {session_data['session_id']}")
                return session_data['session_id']
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error saving evolution session: {e}")
                raise BeeMindError(f"Failed to save evolution session: {e}")
    
    @handle_exception
    def update_evolution_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update evolution session in database"""
        with self.get_session() as session:
            try:
                evolution_session = session.query(EvolutionSession).filter(
                    EvolutionSession.session_id == session_id
                ).first()
                
                if evolution_session:
                    for key, value in update_data.items():
                        if hasattr(evolution_session, key):
                            setattr(evolution_session, key, value)
                    
                    session.commit()
                    logger.info(f"Updated evolution session: {session_id}")
                    return True
                return False
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error updating evolution session: {e}")
                raise BeeMindError(f"Failed to update evolution session: {e}")
    
    @handle_exception
    def get_evolution_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get evolution session from database"""
        with self.get_session() as session:
            try:
                evolution_session = session.query(EvolutionSession).filter(
                    EvolutionSession.session_id == session_id
                ).first()
                
                if evolution_session:
                    return {
                        'session_id': evolution_session.session_id,
                        'created_at': evolution_session.created_at.isoformat(),
                        'completed_at': evolution_session.completed_at.isoformat() if evolution_session.completed_at else None,
                        'population_size': evolution_session.population_size,
                        'generations': evolution_session.generations,
                        'mutation_rate': evolution_session.mutation_rate,
                        'crossover_rate': evolution_session.crossover_rate,
                        'focus_model': evolution_session.focus_model,
                        'best_fitness': evolution_session.best_fitness,
                        'avg_fitness': evolution_session.avg_fitness,
                        'improvement': evolution_session.improvement,
                        'status': evolution_session.status,
                        'progress': evolution_session.progress,
                        'generation_history': evolution_session.generation_history,
                        'dataset_hash': evolution_session.dataset_hash,
                        'dataset_size': evolution_session.dataset_size,
                        'description': evolution_session.description,
                        'tags': evolution_session.tags
                    }
                return None
                
            except SQLAlchemyError as e:
                logger.error(f"Database error getting evolution session: {e}")
                raise BeeMindError(f"Failed to get evolution session: {e}")
    
    @handle_exception
    def get_best_models(self, limit: int = 10, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get best performing models from database"""
        with self.get_session() as session:
            try:
                query = session.query(ModelMetadata).filter(
                    ModelMetadata.is_active == True
                ).order_by(ModelMetadata.roc_auc.desc())
                
                if model_type:
                    query = query.filter(ModelMetadata.model_type == model_type)
                
                models = query.limit(limit).all()
                
                return [{
                    'model_id': model.model_id,
                    'model_type': model.model_type,
                    'model_name': model.model_name,
                    'roc_auc': model.roc_auc,
                    'f1_score': model.f1_score,
                    'accuracy': model.accuracy,
                    'created_at': model.created_at.isoformat(),
                    'generation': model.generation,
                    'fitness_score': model.fitness_score,
                    'evolution_id': model.evolution_id,
                    'tags': model.tags
                } for model in models]
                
            except SQLAlchemyError as e:
                logger.error(f"Database error getting best models: {e}")
                raise BeeMindError(f"Failed to get best models: {e}")
    
    @handle_exception
    def save_performance_log(self, log_data: Dict[str, Any]) -> int:
        """Save performance log to database"""
        with self.get_session() as session:
            try:
                performance_log = PerformanceLog(
                    model_id=log_data['model_id'],
                    roc_auc=log_data.get('roc_auc', 0.0),
                    f1_score=log_data.get('f1_score', 0.0),
                    accuracy=log_data.get('accuracy', 0.0),
                    precision=log_data.get('precision', 0.0),
                    recall=log_data.get('recall', 0.0),
                    inference_time_ms=log_data.get('inference_time_ms', 0.0),
                    memory_usage_mb=log_data.get('memory_usage_mb', 0.0),
                    dataset_hash=log_data.get('dataset_hash', ''),
                    environment=log_data.get('environment', 'development'),
                    metadata=log_data.get('metadata', {})
                )
                
                session.add(performance_log)
                session.commit()
                
                logger.info(f"Saved performance log for model: {log_data['model_id']}")
                return performance_log.id
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error saving performance log: {e}")
                raise BeeMindError(f"Failed to save performance log: {e}")

# Global database manager instance
db_manager = DatabaseManager()
