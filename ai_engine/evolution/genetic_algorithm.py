"""
BeeMind Genetic Algorithm Module
Implements evolutionary optimization for ML model hyperparameters
"""

import random
import logging
from typing import List, Dict, Any, Tuple, Optional
from copy import deepcopy
import numpy as np
from datetime import datetime

from ..exceptions import BeeMindError, handle_exception, log_operation
from ..drones.drone_generator import generate_drone
from ..workers.worker_pool import evaluate_model
from ..queen.queen import select_best_model

logger = logging.getLogger(__name__)

class GeneticAlgorithm:
    """Genetic Algorithm for evolving ML model hyperparameters"""
    
    def __init__(self, 
                 population_size: int = 10,
                 generations: int = 5,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 elite_size: int = 2,
                 model_types: List[str] = None,
                 focus_model: str = "xgb"):
        """
        Initialize genetic algorithm
        
        Args:
            population_size: Number of models in each generation
            generations: Number of generations to evolve
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
            elite_size: Number of best models to preserve
            model_types: List of model types to use (default: all available)
            focus_model: Primary model type to focus on ("xgb", "rf", "gb", "lr")
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        self.focus_model = focus_model
        self.model_types = model_types or ["xgb", "rf", "gb", "lr"]
        self.generation_history = []
        
        # Adjust model distribution based on focus
        self.model_distribution = self._calculate_model_distribution()
        
        log_operation("genetic_algorithm_init", {
            "population_size": population_size,
            "generations": generations,
            "mutation_rate": mutation_rate,
            "crossover_rate": crossover_rate,
            "elite_size": elite_size,
            "focus_model": focus_model,
            "model_types": self.model_types,
            "model_distribution": self.model_distribution
        })
        """
        Initialize genetic algorithm
        
        Args:
            population_size: Number of models in each generation
            generations: Number of generations to evolve
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
            elite_size: Number of best models to preserve
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        self.generation_history = []
        
        log_operation("genetic_algorithm_init", {
            "population_size": population_size,
            "generations": generations,
            "mutation_rate": mutation_rate,
            "crossover_rate": crossover_rate,
            "elite_size": elite_size
        })
    
    def create_initial_population(self) -> List[Dict[str, Any]]:
        """Create initial population of models with focus distribution"""
        population = []
        
        for i in range(self.population_size):
            try:
                # Use weighted random selection based on focus
                model_type = self._select_model_type_by_distribution()
                model, metadata = self._generate_focused_drone(model_type)
                
                population.append({
                    "model": model,
                    "metadata": metadata,
                    "fitness": 0.0,
                    "generation": 0,
                    "id": f"gen0_drone{i}_{model_type}"
                })
                logger.info(f"Created drone {i+1}/{self.population_size}: {metadata['type']} (focus: {self.focus_model})")
            except Exception as e:
                logger.warning(f"Failed to create drone {i+1}: {e}")
                continue
        
        return population
    
    def _select_model_type_by_distribution(self) -> str:
        """Select model type based on probability distribution"""
        rand = random.random()
        cumulative = 0.0
        
        for model_type, probability in self.model_distribution.items():
            cumulative += probability
            if rand <= cumulative:
                return model_type
        
        # Fallback to focus model
        return self.focus_model
    
    def _generate_focused_drone(self, model_type: str) -> Tuple[Any, Dict[str, Any]]:
        """Generate a drone with specific model type and enhanced parameters"""
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from xgboost import XGBClassifier
        from sklearn.linear_model import LogisticRegression
        import random
        
        if model_type == "xgb":
            model = XGBClassifier(
                n_estimators=random.randint(100, 500),
                max_depth=random.randint(3, 12),
                learning_rate=random.uniform(0.01, 0.5),
                subsample=random.uniform(0.8, 1.0),
                colsample_bytree=random.uniform(0.8, 1.0),
                random_state=42
            )
        elif model_type == "rf":
            model = RandomForestClassifier(
                n_estimators=random.randint(100, 400),
                max_depth=random.randint(3, 20),
                min_samples_split=random.randint(2, 15),
                min_samples_leaf=random.randint(1, 10),
                max_features=random.choice(['sqrt', 'log2', None]),
                random_state=42
            )
        elif model_type == "gb":
            model = GradientBoostingClassifier(
                n_estimators=random.randint(100, 400),
                max_depth=random.randint(3, 10),
                learning_rate=random.uniform(0.01, 0.3),
                subsample=random.uniform(0.8, 1.0),
                random_state=42
            )
        else:  # lr
            model = LogisticRegression(
                C=random.uniform(0.1, 20.0),
                max_iter=1000,
                solver=random.choice(['lbfgs', 'liblinear', 'saga']),
                penalty=random.choice(['l2', 'l1', 'elasticnet', None]),
                random_state=42
            )
        
        metadata = {
            "type": type(model).__name__,
            "params": model.get_params(),
            "model_type": model_type,
            "focus_model": self.focus_model
        }
        
        return model, metadata
    
    def _calculate_model_distribution(self) -> Dict[str, float]:
        """Calculate probability distribution for model types based on focus"""
        if self.focus_model == "xgb":
            # 60% XGBoost, 40% others
            return {
                "xgb": 0.6,
                "rf": 0.15,
                "gb": 0.15,
                "lr": 0.1
            }
        elif self.focus_model == "rf":
            # 60% Random Forest, 40% others
            return {
                "xgb": 0.15,
                "rf": 0.6,
                "gb": 0.15,
                "lr": 0.1
            }
        elif self.focus_model == "gb":
            # 60% Gradient Boosting, 40% others
            return {
                "xgb": 0.15,
                "rf": 0.15,
                "gb": 0.6,
                "lr": 0.1
            }
        elif self.focus_model == "lr":
            # 60% Logistic Regression, 40% others
            return {
                "xgb": 0.15,
                "rf": 0.15,
                "gb": 0.1,
                "lr": 0.6
            }
        else:
            # Balanced distribution
            return {
                "xgb": 0.25,
                "rf": 0.25,
                "gb": 0.25,
                "lr": 0.25
            }
    
    def evaluate_population(self, population: List[Dict[str, Any]], X, y) -> List[Dict[str, Any]]:
        """Evaluate fitness of all models in population"""
        evaluated_population = []
        
        for individual in population:
            try:
                result = evaluate_model(individual["model"], X, y)
                individual["fitness"] = result["roc_auc"]
                individual["evaluation_result"] = result
                evaluated_population.append(individual)
                logger.info(f"Drone {individual['id']} fitness: {individual['fitness']:.3f}")
            except Exception as e:
                logger.warning(f"Failed to evaluate {individual['id']}: {e}")
                individual["fitness"] = 0.0
                evaluated_population.append(individual)
        
        return evaluated_population
    
    def select_parents(self, population: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Select two parents using tournament selection"""
        tournament_size = 3
        
        # Tournament selection for first parent
        tournament1 = random.sample(population, tournament_size)
        parent1 = max(tournament1, key=lambda x: x["fitness"])
        
        # Tournament selection for second parent
        tournament2 = random.sample(population, tournament_size)
        parent2 = max(tournament2, key=lambda x: x["fitness"])
        
        return parent1, parent2
    
    def crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Perform crossover between two parents with multi-modal support"""
        if random.random() > self.crossover_rate:
            return parent1, parent2
        
        # Decide if we should do model type crossover (10% chance)
        model_crossover = random.random() < 0.1
        
        if model_crossover and parent1["metadata"]["type"] != parent2["metadata"]["type"]:
            # Model type crossover - create hybrid models
            child1_model_type = self._select_model_type_by_distribution()
            child2_model_type = self._select_model_type_by_distribution()
            
            # Combine parameters from both parents
            combined_params = self._combine_hyperparameters(
                parent1["metadata"]["params"], 
                parent2["metadata"]["params"]
            )
            
            child1_model = self._create_model_from_params(child1_model_type, combined_params)
            child2_model = self._create_model_from_params(child2_model_type, combined_params)
            
            child1_metadata = {
                "type": type(child1_model).__name__,
                "params": child1_model.get_params(),
                "parent1": parent1["id"],
                "parent2": parent2["id"],
                "model_type": child1_model_type,
                "crossover_type": "model_type"
            }
            
            child2_metadata = {
                "type": type(child2_model).__name__,
                "params": child2_model.get_params(),
                "parent1": parent2["id"],
                "parent2": parent1["id"],
                "model_type": child2_model_type,
                "crossover_type": "model_type"
            }
        else:
            # Standard parameter crossover within same model type
            child1_params = self._combine_hyperparameters(parent1["metadata"]["params"], parent2["metadata"]["params"])
            child2_params = self._combine_hyperparameters(parent2["metadata"]["params"], parent1["metadata"]["params"])
            
            # Keep same model type as parents
            child1_model = self._create_model_from_params(parent1["metadata"]["type"], child1_params)
            child2_model = self._create_model_from_params(parent2["metadata"]["type"], child2_params)
            
            child1_metadata = {
                "type": parent1["metadata"]["type"],
                "params": child1_params,
                "parent1": parent1["id"],
                "parent2": parent2["id"],
                "model_type": parent1["metadata"].get("model_type", "unknown"),
                "crossover_type": "parameter"
            }
            
            child2_metadata = {
                "type": parent2["metadata"]["type"],
                "params": child2_params,
                "parent1": parent2["id"],
                "parent2": parent1["id"],
                "model_type": parent2["metadata"].get("model_type", "unknown"),
                "crossover_type": "parameter"
            }
        
        child1 = {
            "model": child1_model,
            "metadata": child1_metadata,
            "fitness": 0.0,
            "generation": parent1["generation"] + 1,
            "id": f"gen{parent1['generation'] + 1}_crossover_{random.randint(1000, 9999)}"
        }
        
        child2 = {
            "model": child2_model,
            "metadata": child2_metadata,
            "fitness": 0.0,
            "generation": parent2["generation"] + 1,
            "id": f"gen{parent2['generation'] + 1}_crossover_{random.randint(1000, 9999)}"
        }
        
        return child1, child2
    
    def _combine_hyperparameters(self, params1: Dict[str, Any], params2: Dict[str, Any]) -> Dict[str, Any]:
        """Combine hyperparameters from two parents"""
        combined_params = {}
        
        for key in params1:
            if key in params2:
                # Randomly choose from either parent or average numeric values
                if isinstance(params1[key], (int, float)) and isinstance(params2[key], (int, float)):
                    if random.random() < 0.5:
                        combined_params[key] = params1[key]
                    else:
                        combined_params[key] = params2[key]
                else:
                    combined_params[key] = params1[key] if random.random() < 0.5 else params2[key]
            else:
                combined_params[key] = params1[key]
        
        return combined_params
    
    def _create_model_from_params(self, model_type: str, params: Dict[str, Any]):
        """Create a model instance with given parameters"""
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from xgboost import XGBClassifier
        from sklearn.linear_model import LogisticRegression
        
        if model_type == "XGBClassifier":
            return XGBClassifier(**params)
        elif model_type == "RandomForestClassifier":
            return RandomForestClassifier(**params)
        elif model_type == "GradientBoostingClassifier":
            return GradientBoostingClassifier(**params)
        elif model_type == "LogisticRegression":
            return LogisticRegression(**params)
        else:
            # Fallback to generating a new random model
            model, _ = generate_drone()
            return model
    
    def mutate(self, individual: Dict[str, Any]) -> Dict[str, Any]:
        """Apply mutation to an individual"""
        if random.random() > self.mutation_rate:
            return individual
        
        # Create a copy for mutation
        mutated = deepcopy(individual)
        params = mutated["metadata"]["params"]
        
        # Apply random mutations to numeric parameters
        for key, value in params.items():
            if isinstance(value, (int, float)):
                if random.random() < 0.3:  # 30% chance to mutate each parameter
                    if isinstance(value, int):
                        # Integer mutation: add/subtract random amount
                        mutation = random.randint(-2, 2)
                        params[key] = max(1, value + mutation)
                    else:
                        # Float mutation: multiply by random factor
                        mutation_factor = random.uniform(0.8, 1.2)
                        params[key] = value * mutation_factor
        
        # Update model with new parameters
        mutated["model"] = self._create_model_from_params(mutated["metadata"]["type"], params)
        mutated["id"] = f"{mutated['id']}_mutated"
        
        return mutated
    
    @handle_exception
    def evolve(self, X, y) -> Dict[str, Any]:
        """Run the complete genetic algorithm evolution"""
        log_operation("genetic_algorithm_evolve", {
            "population_size": self.population_size,
            "generations": self.generations,
            "data_shape": X.shape if hasattr(X, 'shape') else len(X)
        })
        
        # Create initial population
        population = self.create_initial_population()
        
        best_fitness_history = []
        avg_fitness_history = []
        
        for generation in range(self.generations):
            logger.info(f"Starting generation {generation + 1}/{self.generations}")
            
            # Evaluate current population
            population = self.evaluate_population(population, X, y)
            
            # Sort by fitness
            population.sort(key=lambda x: x["fitness"], reverse=True)
            
            # Record statistics
            fitness_scores = [ind["fitness"] for ind in population]
            best_fitness = max(fitness_scores)
            avg_fitness = sum(fitness_scores) / len(fitness_scores)
            
            best_fitness_history.append(best_fitness)
            avg_fitness_history.append(avg_fitness)
            
            logger.info(f"Generation {generation + 1}: Best={best_fitness:.3f}, Avg={avg_fitness:.3f}")
            
            # Store generation info
            generation_info = {
                "generation": generation + 1,
                "best_fitness": best_fitness,
                "avg_fitness": avg_fitness,
                "population_size": len(population),
                "best_model": population[0]["metadata"]["type"],
                "timestamp": datetime.utcnow().isoformat()
            }
            self.generation_history.append(generation_info)
            
            # Stop if this is the last generation
            if generation == self.generations - 1:
                break
            
            # Create next generation
            new_population = []
            
            # Elitism: keep best individuals
            elite = population[:self.elite_size]
            new_population.extend(elite)
            
            # Generate rest of population through crossover and mutation
            while len(new_population) < self.population_size:
                # Select parents
                parent1, parent2 = self.select_parents(population)
                
                # Perform crossover
                child1, child2 = self.crossover(parent1, parent2)
                
                # Apply mutation
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                new_population.extend([child1, child2])
            
            # Trim to exact population size
            population = new_population[:self.population_size]
        
        # Final evaluation
        population = self.evaluate_population(population, X, y)
        population.sort(key=lambda x: x["fitness"], reverse=True)
        
        best_individual = population[0]
        
        log_operation("genetic_algorithm_complete", {
            "best_fitness": best_individual["fitness"],
            "best_model_type": best_individual["metadata"]["type"],
            "total_generations": self.generations,
            "final_population_size": len(population)
        })
        
        return {
            "best_model": best_individual["model"],
            "best_metadata": best_individual["metadata"],
            "best_fitness": best_individual["fitness"],
            "generation_history": self.generation_history,
            "final_population": population,
            "evolution_stats": {
                "best_fitness_history": best_fitness_history,
                "avg_fitness_history": avg_fitness_history,
                "improvement": best_fitness_history[-1] - best_fitness_history[0]
            }
        }

