"""
BeeMind Asynchronous Processing Module
Implements distributed task processing for scalable model evolution
"""

import os
import logging
from celery import Celery
from celery.utils.log import get_task_logger
from typing import Dict, Any, Optional
import json
from datetime import datetime

from ..exceptions import BeeMindError, handle_exception, log_operation
from ..evolution.genetic_algorithm import GeneticAlgorithm
from ..workers.worker_pool import evaluate_model
from ..memory.hivememory import log_generation_result

logger = get_task_logger(__name__)

# Celery configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Initialize Celery app
celery_app = Celery(
    'beemind',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['ai_engine.scalability.celery_app']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
    result_expires=3600,  # 1 hour
    task_routes={
        'ai_engine.scalability.celery_app.evolve_population': {'queue': 'evolution'},
        'ai_engine.scalability.celery_app.evaluate_model_async': {'queue': 'evaluation'},
        'ai_engine.scalability.celery_app.parallel_evolution': {'queue': 'parallel'},
    }
)

@celery_app.task(bind=True, name='ai_engine.scalability.celery_app.evolve_population')
@handle_exception
def evolve_population(self, 
                     population_data: Dict[str, Any], 
                     X_data: list, 
                     y_data: list,
                     generation: int,
                     evolution_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Asynchronously evolve a population of models
    
    Args:
        population_data: Current population data
        X_data: Feature data
        y_data: Target data
        generation: Current generation number
        evolution_config: Evolution configuration
        
    Returns:
        Dict containing evolved population and statistics
    """
    log_operation("celery_evolve_population", {
        "task_id": self.request.id,
        "generation": generation,
        "population_size": len(population_data),
        "evolution_config": evolution_config
    })
    
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': len(population_data), 'status': 'Starting evolution'}
        )
        
        # Initialize genetic algorithm
        ga = GeneticAlgorithm(
            population_size=evolution_config.get('population_size', 10),
            generations=1,  # Single generation evolution
            mutation_rate=evolution_config.get('mutation_rate', 0.1),
            crossover_rate=evolution_config.get('crossover_rate', 0.8),
            focus_model=evolution_config.get('focus_model', 'xgb')
        )
        
        # Convert data back to numpy arrays
        import numpy as np
        X = np.array(X_data)
        y = np.array(y_data)
        
        # Create population from data
        population = []
        for i, individual_data in enumerate(population_data):
            # Reconstruct model from parameters
            model = ga._create_model_from_params(
                individual_data['metadata']['type'],
                individual_data['metadata']['params']
            )
            
            population.append({
                "model": model,
                "metadata": individual_data['metadata'],
                "fitness": individual_data.get('fitness', 0.0),
                "generation": generation,
                "id": individual_data['id']
            })
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'current': i + 1, 'total': len(population_data), 'status': f'Reconstructed {i + 1} models'}
            )
        
        # Evolve population
        evolved_result = ga.evolve(X, y)
        
        # Convert models to serializable format
        serializable_population = []
        for individual in evolved_result['final_population']:
            serializable_population.append({
                "metadata": individual['metadata'],
                "fitness": individual['fitness'],
                "generation": individual['generation'],
                "id": individual['id'],
                "evaluation_result": individual.get('evaluation_result', {})
            })
        
        result = {
            "population": serializable_population,
            "generation": generation,
            "best_fitness": evolved_result['best_fitness'],
            "avg_fitness": sum(ind['fitness'] for ind in serializable_population) / len(serializable_population),
            "task_id": self.request.id,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        log_operation("celery_evolve_population_complete", {
            "task_id": self.request.id,
            "generation": generation,
            "best_fitness": evolved_result['best_fitness']
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Evolution task failed: {e}")
        raise

@celery_app.task(bind=True, name='ai_engine.scalability.celery_app.evaluate_model_async')
@handle_exception
def evaluate_model_async(self, 
                        model_data: Dict[str, Any], 
                        X_data: list, 
                        y_data: list) -> Dict[str, Any]:
    """
    Asynchronously evaluate a single model
    
    Args:
        model_data: Model metadata and parameters
        X_data: Feature data
        y_data: Target data
        
    Returns:
        Dict containing evaluation results
    """
    log_operation("celery_evaluate_model", {
        "task_id": self.request.id,
        "model_type": model_data['metadata']['type']
    })
    
    try:
        # Convert data back to numpy arrays
        import numpy as np
        X = np.array(X_data)
        y = np.array(y_data)
        
        # Reconstruct model
        ga = GeneticAlgorithm()
        model = ga._create_model_from_params(
            model_data['metadata']['type'],
            model_data['metadata']['params']
        )
        
        # Evaluate model
        result = evaluate_model(model, X, y)
        
        evaluation_result = {
            "model_id": model_data['id'],
            "model_type": model_data['metadata']['type'],
            "roc_auc": result['roc_auc'],
            "f1": result['f1'],
            "evaluation_metadata": result.get('metadata', {}),
            "task_id": self.request.id,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        log_operation("celery_evaluate_model_complete", {
            "task_id": self.request.id,
            "roc_auc": result['roc_auc']
        })
        
        return evaluation_result
        
    except Exception as e:
        logger.error(f"Evaluation task failed: {e}")
        raise

@celery_app.task(bind=True, name='ai_engine.scalability.celery_app.parallel_evolution')
@handle_exception
def parallel_evolution(self, 
                      evolution_config: Dict[str, Any],
                      X_data: list,
                      y_data: list) -> Dict[str, Any]:
    """
    Run parallel evolution across multiple workers
    
    Args:
        evolution_config: Evolution configuration
        X_data: Feature data
        y_data: Target data
        
    Returns:
        Dict containing evolution results
    """
    log_operation("celery_parallel_evolution", {
        "task_id": self.request.id,
        "evolution_config": evolution_config
    })
    
    try:
        # Initialize genetic algorithm
        ga = GeneticAlgorithm(
            population_size=evolution_config.get('population_size', 10),
            generations=evolution_config.get('generations', 5),
            mutation_rate=evolution_config.get('mutation_rate', 0.1),
            crossover_rate=evolution_config.get('crossover_rate', 0.8),
            focus_model=evolution_config.get('focus_model', 'xgb')
        )
        
        # Convert data back to numpy arrays
        import numpy as np
        X = np.array(X_data)
        y = np.array(y_data)
        
        # Create initial population
        population = ga.create_initial_population()
        
        # Convert population to serializable format
        serializable_population = []
        for individual in population:
            serializable_population.append({
                "metadata": individual['metadata'],
                "fitness": individual['fitness'],
                "generation": individual['generation'],
                "id": individual['id']
            })
        
        # Run evolution
        evolution_result = ga.evolve(X, y)
        
        # Convert final population to serializable format
        final_population = []
        for individual in evolution_result['final_population']:
            final_population.append({
                "metadata": individual['metadata'],
                "fitness": individual['fitness'],
                "generation": individual['generation'],
                "id": individual['id'],
                "evaluation_result": individual.get('evaluation_result', {})
            })
        
        result = {
            "best_model": {
                "metadata": evolution_result['best_metadata'],
                "fitness": evolution_result['best_fitness']
            },
            "final_population": final_population,
            "generation_history": evolution_result['generation_history'],
            "evolution_stats": evolution_result['evolution_stats'],
            "task_id": self.request.id,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        log_operation("celery_parallel_evolution_complete", {
            "task_id": self.request.id,
            "best_fitness": evolution_result['best_fitness']
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Parallel evolution task failed: {e}")
        raise

# Task monitoring and management
def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get status of a Celery task"""
    task = celery_app.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Task is pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info)
        }
    
    return response

def cancel_task(task_id: str) -> bool:
    """Cancel a running Celery task"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return True
    except Exception as e:
        logger.error(f"Failed to cancel task {task_id}: {e}")
        return False
