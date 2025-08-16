"""
BeeMind Performance Monitoring Module
GPU acceleration, system metrics, and performance optimization
"""

import os
import logging
import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import numpy as np

from ..exceptions import BeeMindError, handle_exception, log_operation

logger = logging.getLogger(__name__)

# Try to import GPU libraries
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available - GPU acceleration disabled")

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False
    logger.warning("CuPy not available - GPU acceleration disabled")

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage_percent: float
    network_sent_mb: float
    network_recv_mb: float
    load_average: List[float]
    process_count: int

@dataclass
class GPUMetrics:
    """GPU performance metrics"""
    timestamp: datetime
    gpu_id: int
    memory_used_mb: float
    memory_total_mb: float
    memory_percent: float
    utilization_percent: float
    temperature_celsius: float
    power_usage_watts: float

@dataclass
class ModelPerformanceMetrics:
    """Model performance metrics"""
    timestamp: datetime
    model_id: str
    model_type: str
    inference_time_ms: float
    memory_usage_mb: float
    throughput_samples_per_sec: float
    accuracy: float
    roc_auc: float
    f1_score: float
    batch_size: int
    dataset_size: int

class PerformanceMonitor:
    """Performance monitoring and optimization for BeeMind"""
    
    def __init__(self, monitoring_interval: float = 5.0):
        self.monitoring_interval = monitoring_interval
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Metrics storage
        self.system_metrics_history: List[SystemMetrics] = []
        self.gpu_metrics_history: List[GPUMetrics] = []
        self.model_metrics_history: List[ModelPerformanceMetrics] = []
        
        # Performance thresholds
        self.thresholds = {
            'cpu_warning': 80.0,
            'cpu_critical': 95.0,
            'memory_warning': 85.0,
            'memory_critical': 95.0,
            'gpu_memory_warning': 90.0,
            'gpu_memory_critical': 95.0,
            'inference_time_warning': 1000.0,  # ms
            'inference_time_critical': 5000.0  # ms
        }
        
        # Callbacks for alerts
        self.alert_callbacks: List[Callable] = []
        
        # Initialize GPU monitoring
        self.gpu_available = self._initialize_gpu_monitoring()
        
        # Performance optimization settings
        self.optimization_settings = {
            'auto_scale_workers': True,
            'memory_cleanup_threshold': 85.0,
            'gpu_memory_cleanup_threshold': 90.0,
            'enable_parallel_processing': True,
            'batch_size_optimization': True
        }
    
    def _initialize_gpu_monitoring(self) -> bool:
        """Initialize GPU monitoring capabilities"""
        try:
            if TORCH_AVAILABLE and torch.cuda.is_available():
                self.gpu_count = torch.cuda.device_count()
                logger.info(f"GPU monitoring initialized: {self.gpu_count} GPUs available")
                return True
            else:
                logger.info("No CUDA-capable GPUs available")
                return False
        except Exception as e:
            logger.warning(f"Failed to initialize GPU monitoring: {e}")
            return False
    
    def start_monitoring(self):
        """Start continuous performance monitoring"""
        if self.monitoring_active:
            logger.warning("Performance monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self.system_metrics_history.append(system_metrics)
                
                # Collect GPU metrics if available
                if self.gpu_available:
                    gpu_metrics = self._collect_gpu_metrics()
                    self.gpu_metrics_history.extend(gpu_metrics)
                
                # Check thresholds and trigger alerts
                self._check_thresholds(system_metrics)
                
                # Cleanup old metrics (keep last 24 hours)
                self._cleanup_old_metrics()
                
                # Sleep for monitoring interval
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Network metrics
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / (1024**2)
            network_recv_mb = network.bytes_recv / (1024**2)
            
            # Load average
            load_average = list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            # Process count
            process_count = len(psutil.pids())
            
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_gb=memory_used_gb,
                memory_total_gb=memory_total_gb,
                disk_usage_percent=disk_usage_percent,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                load_average=load_average,
                process_count=process_count
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_gb=0.0,
                memory_total_gb=0.0,
                disk_usage_percent=0.0,
                network_sent_mb=0.0,
                network_recv_mb=0.0,
                load_average=[0, 0, 0],
                process_count=0
            )
    
    def _collect_gpu_metrics(self) -> List[GPUMetrics]:
        """Collect GPU metrics if available"""
        gpu_metrics = []
        
        try:
            if TORCH_AVAILABLE and torch.cuda.is_available():
                for gpu_id in range(self.gpu_count):
                    # Get GPU memory info
                    memory_allocated = torch.cuda.memory_allocated(gpu_id) / (1024**2)  # MB
                    memory_reserved = torch.cuda.memory_reserved(gpu_id) / (1024**2)  # MB
                    memory_total = torch.cuda.get_device_properties(gpu_id).total_memory / (1024**2)  # MB
                    memory_percent = (memory_allocated / memory_total) * 100
                    
                    # Note: Some metrics require nvidia-ml-py or similar
                    # For now, we'll use basic PyTorch metrics
                    gpu_metrics.append(GPUMetrics(
                        timestamp=datetime.utcnow(),
                        gpu_id=gpu_id,
                        memory_used_mb=memory_allocated,
                        memory_total_mb=memory_total,
                        memory_percent=memory_percent,
                        utilization_percent=0.0,  # Would need nvidia-ml-py
                        temperature_celsius=0.0,  # Would need nvidia-ml-py
                        power_usage_watts=0.0  # Would need nvidia-ml-py
                    ))
            
        except Exception as e:
            logger.error(f"Error collecting GPU metrics: {e}")
        
        return gpu_metrics
    
    def _check_thresholds(self, system_metrics: SystemMetrics):
        """Check performance thresholds and trigger alerts"""
        alerts = []
        
        # CPU threshold checks
        if system_metrics.cpu_percent > self.thresholds['cpu_critical']:
            alerts.append({
                'level': 'critical',
                'metric': 'cpu',
                'value': system_metrics.cpu_percent,
                'threshold': self.thresholds['cpu_critical'],
                'message': f"CPU usage critical: {system_metrics.cpu_percent:.1f}%"
            })
        elif system_metrics.cpu_percent > self.thresholds['cpu_warning']:
            alerts.append({
                'level': 'warning',
                'metric': 'cpu',
                'value': system_metrics.cpu_percent,
                'threshold': self.thresholds['cpu_warning'],
                'message': f"CPU usage high: {system_metrics.cpu_percent:.1f}%"
            })
        
        # Memory threshold checks
        if system_metrics.memory_percent > self.thresholds['memory_critical']:
            alerts.append({
                'level': 'critical',
                'metric': 'memory',
                'value': system_metrics.memory_percent,
                'threshold': self.thresholds['memory_critical'],
                'message': f"Memory usage critical: {system_metrics.memory_percent:.1f}%"
            })
        elif system_metrics.memory_percent > self.thresholds['memory_warning']:
            alerts.append({
                'level': 'warning',
                'metric': 'memory',
                'value': system_metrics.memory_percent,
                'threshold': self.thresholds['memory_warning'],
                'message': f"Memory usage high: {system_metrics.memory_percent:.1f}%"
            })
        
        # Trigger alert callbacks
        for alert in alerts:
            self._trigger_alert(alert)
    
    def _trigger_alert(self, alert: Dict[str, Any]):
        """Trigger performance alerts"""
        logger.warning(f"Performance alert: {alert['message']}")
        
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory bloat"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Clean system metrics
        self.system_metrics_history = [
            m for m in self.system_metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        # Clean GPU metrics
        self.gpu_metrics_history = [
            m for m in self.gpu_metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        # Clean model metrics
        self.model_metrics_history = [
            m for m in self.model_metrics_history 
            if m.timestamp > cutoff_time
        ]
    
    @handle_exception
    def record_model_performance(self, metrics: ModelPerformanceMetrics):
        """Record model performance metrics"""
        self.model_metrics_history.append(metrics)
        
        # Check model performance thresholds
        if metrics.inference_time_ms > self.thresholds['inference_time_critical']:
            self._trigger_alert({
                'level': 'critical',
                'metric': 'inference_time',
                'value': metrics.inference_time_ms,
                'threshold': self.thresholds['inference_time_critical'],
                'message': f"Model {metrics.model_id} inference time critical: {metrics.inference_time_ms:.1f}ms"
            })
        elif metrics.inference_time_ms > self.thresholds['inference_time_warning']:
            self._trigger_alert({
                'level': 'warning',
                'metric': 'inference_time',
                'value': metrics.inference_time_ms,
                'threshold': self.thresholds['inference_time_warning'],
                'message': f"Model {metrics.model_id} inference time high: {metrics.inference_time_ms:.1f}ms"
            })
    
    def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter recent metrics
        recent_system = [m for m in self.system_metrics_history if m.timestamp > cutoff_time]
        recent_gpu = [m for m in self.gpu_metrics_history if m.timestamp > cutoff_time]
        recent_model = [m for m in self.model_metrics_history if m.timestamp > cutoff_time]
        
        if not recent_system:
            return {'error': 'No recent metrics available'}
        
        # Calculate system averages
        avg_cpu = np.mean([m.cpu_percent for m in recent_system])
        avg_memory = np.mean([m.memory_percent for m in recent_system])
        max_cpu = np.max([m.cpu_percent for m in recent_system])
        max_memory = np.max([m.memory_percent for m in recent_system])
        
        # Calculate model performance averages
        if recent_model:
            avg_inference_time = np.mean([m.inference_time_ms for m in recent_model])
            avg_throughput = np.mean([m.throughput_samples_per_sec for m in recent_model])
            avg_accuracy = np.mean([m.accuracy for m in recent_model])
        else:
            avg_inference_time = 0.0
            avg_throughput = 0.0
            avg_accuracy = 0.0
        
        # GPU summary
        gpu_summary = {}
        if recent_gpu:
            for gpu_id in set(m.gpu_id for m in recent_gpu):
                gpu_metrics = [m for m in recent_gpu if m.gpu_id == gpu_id]
                gpu_summary[f'gpu_{gpu_id}'] = {
                    'avg_memory_percent': np.mean([m.memory_percent for m in gpu_metrics]),
                    'max_memory_percent': np.max([m.memory_percent for m in gpu_metrics]),
                    'avg_memory_used_mb': np.mean([m.memory_used_mb for m in gpu_metrics])
                }
        
        return {
            'timeframe_hours': hours,
            'system_metrics': {
                'avg_cpu_percent': avg_cpu,
                'max_cpu_percent': max_cpu,
                'avg_memory_percent': avg_memory,
                'max_memory_percent': max_memory,
                'current_memory_gb': recent_system[-1].memory_used_gb if recent_system else 0.0,
                'total_memory_gb': recent_system[-1].memory_total_gb if recent_system else 0.0
            },
            'model_metrics': {
                'avg_inference_time_ms': avg_inference_time,
                'avg_throughput_samples_per_sec': avg_throughput,
                'avg_accuracy': avg_accuracy,
                'total_models_evaluated': len(recent_model)
            },
            'gpu_metrics': gpu_summary,
            'alerts': {
                'cpu_warning_threshold': self.thresholds['cpu_warning'],
                'cpu_critical_threshold': self.thresholds['cpu_critical'],
                'memory_warning_threshold': self.thresholds['memory_warning'],
                'memory_critical_threshold': self.thresholds['memory_critical']
            }
        }
    
    def add_alert_callback(self, callback: Callable):
        """Add callback function for performance alerts"""
        self.alert_callbacks.append(callback)
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Perform automatic performance optimization"""
        optimization_results = {
            'memory_cleanup': False,
            'gpu_memory_cleanup': False,
            'worker_scaling': False,
            'batch_size_adjustment': False
        }
        
        try:
            # Get current system metrics
            current_metrics = self._collect_system_metrics()
            
            # Memory cleanup if needed
            if current_metrics.memory_percent > self.optimization_settings['memory_cleanup_threshold']:
                import gc
                gc.collect()
                optimization_results['memory_cleanup'] = True
                logger.info("Performed memory cleanup due to high usage")
            
            # GPU memory cleanup if needed
            if self.gpu_available and TORCH_AVAILABLE:
                for gpu_id in range(self.gpu_count):
                    memory_percent = (torch.cuda.memory_allocated(gpu_id) / 
                                    torch.cuda.get_device_properties(gpu_id).total_memory) * 100
                    
                    if memory_percent > self.optimization_settings['gpu_memory_cleanup_threshold']:
                        torch.cuda.empty_cache()
                        optimization_results['gpu_memory_cleanup'] = True
                        logger.info(f"Cleared GPU {gpu_id} memory cache")
            
            # Worker scaling (placeholder for future implementation)
            if self.optimization_settings['auto_scale_workers']:
                # This would integrate with Celery worker scaling
                pass
            
            logger.info("Performance optimization completed")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error during performance optimization: {e}")
            return {'error': str(e)}

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Performance measurement decorator
def measure_performance(model_id: str = None):
    """Decorator to measure function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / (1024**2)  # MB
            
            try:
                result = func(*args, **kwargs)
                
                # Calculate metrics
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss / (1024**2)  # MB
                
                inference_time_ms = (end_time - start_time) * 1000
                memory_usage_mb = end_memory - start_memory
                
                # Record performance metrics
                if model_id:
                    metrics = ModelPerformanceMetrics(
                        timestamp=datetime.utcnow(),
                        model_id=model_id,
                        model_type=func.__name__,
                        inference_time_ms=inference_time_ms,
                        memory_usage_mb=memory_usage_mb,
                        throughput_samples_per_sec=0.0,  # Would need batch size info
                        accuracy=0.0,  # Would need actual metrics
                        roc_auc=0.0,
                        f1_score=0.0,
                        batch_size=1,
                        dataset_size=0
                    )
                    performance_monitor.record_model_performance(metrics)
                
                return result
                
            except Exception as e:
                logger.error(f"Error in performance measurement: {e}")
                raise
        
        return wrapper
    return decorator
