import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import socketio
from ai_engine.memory.hivememory import HiveMemory
from ai_engine.scalability.performance_monitor import PerformanceMonitor
from ai_engine.scalability.cache_manager import CacheManager
from ai_engine.scalability.database_manager import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardWebSocketManager:
    """Manages WebSocket connections for the BeeMind dashboard"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.sio = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True
        )
        self.app = socketio.ASGIApp(self.sio)
        self.hive_memory = HiveMemory()
        self.performance_monitor = PerformanceMonitor()
        self.cache_manager = CacheManager()
        self.db_manager = DatabaseManager()
        
        # Dashboard data
        self.queen_status = {
            "is_active": True,
            "evolution_progress": 0.0,
            "current_generation": 0,
            "total_generations": 0,
            "best_fitness": 0.0,
            "last_update": datetime.now().isoformat()
        }
        
        self.bee_agents = []
        self.live_logs = []
        self.performance_metrics = {}
        
        # Setup Socket.IO events
        self._setup_socketio_events()
        
    def _setup_socketio_events(self):
        """Setup Socket.IO event handlers"""
        
        @self.sio.event
        async def connect(sid, environ):
            logger.info(f"Dashboard client connected: {sid}")
            await self.sio.emit('queen_status', self.queen_status, room=sid)
            await self.sio.emit('bee_agents', self.bee_agents, room=sid)
            await self.sio.emit('live_logs', self.live_logs[-50:], room=sid)  # Last 50 logs
            await self.sio.emit('performance_metrics', self.performance_metrics, room=sid)
            
        @self.sio.event
        async def disconnect(sid):
            logger.info(f"Dashboard client disconnected: {sid}")
            
        @self.sio.event
        async def request_queen_status(sid, data):
            """Handle queen status requests"""
            await self.sio.emit('queen_status', self.queen_status, room=sid)
            
        @self.sio.event
        async def request_bee_agents(sid, data):
            """Handle bee agents requests"""
            await self.sio.emit('bee_agents', self.bee_agents, room=sid)
            
        @self.sio.event
        async def request_live_logs(sid, data):
            """Handle live logs requests"""
            await self.sio.emit('live_logs', self.live_logs[-50:], room=sid)
            
        @self.sio.event
        async def request_performance_metrics(sid, data):
            """Handle performance metrics requests"""
            await self.sio.emit('performance_metrics', self.performance_metrics, room=sid)
            
        @self.sio.event
        async def request_evolution_stats(sid, data):
            """Handle evolution statistics requests"""
            try:
                stats = await self._get_evolution_stats()
                await self.sio.emit('evolution_stats', stats, room=sid)
            except Exception as e:
                logger.error(f"Error getting evolution stats: {e}")
                await self.sio.emit('error', {'message': 'Failed to get evolution stats'}, room=sid)
    
    async def _get_evolution_stats(self) -> Dict[str, Any]:
        """Get evolution statistics from database"""
        try:
            # Get recent evolution sessions
            sessions = await self.db_manager.get_recent_evolution_sessions(limit=10)
            
            # Get performance metrics
            metrics = await self.db_manager.get_performance_logs(limit=100)
            
            # Calculate statistics
            total_sessions = len(sessions)
            avg_fitness = sum(session.get('best_fitness', 0) for session in sessions) / max(total_sessions, 1)
            total_generations = sum(session.get('generations_completed', 0) for session in sessions)
            
            return {
                'total_sessions': total_sessions,
                'avg_fitness': round(avg_fitness, 4),
                'total_generations': total_generations,
                'recent_sessions': sessions,
                'performance_trend': metrics
            }
        except Exception as e:
            logger.error(f"Error getting evolution stats: {e}")
            return {
                'total_sessions': 0,
                'avg_fitness': 0.0,
                'total_generations': 0,
                'recent_sessions': [],
                'performance_trend': []
            }
    
    async def update_queen_status(self, status: Dict[str, Any]):
        """Update queen AI status and broadcast to all clients"""
        self.queen_status.update(status)
        self.queen_status['last_update'] = datetime.now().isoformat()
        
        logger.info(f"Queen status updated: {status}")
        await self.sio.emit('queen_status', self.queen_status)
    
    async def update_bee_agents(self, agents: List[Dict[str, Any]]):
        """Update bee agents status and broadcast to all clients"""
        self.bee_agents = agents
        
        logger.info(f"Bee agents updated: {len(agents)} agents")
        await self.sio.emit('bee_agents', self.bee_agents)
    
    async def add_live_log(self, log_entry: Dict[str, Any]):
        """Add a new log entry and broadcast to all clients"""
        log_entry['timestamp'] = datetime.now().isoformat()
        log_entry['id'] = f"log-{datetime.now().timestamp()}"
        
        self.live_logs.append(log_entry)
        
        # Keep only last 1000 logs
        if len(self.live_logs) > 1000:
            self.live_logs = self.live_logs[-1000:]
        
        logger.info(f"Live log added: {log_entry['message']}")
        await self.sio.emit('live_logs', [log_entry])
    
    async def update_performance_metrics(self, metrics: Dict[str, Any]):
        """Update performance metrics and broadcast to all clients"""
        self.performance_metrics.update(metrics)
        self.performance_metrics['timestamp'] = datetime.now().isoformat()
        
        logger.info(f"Performance metrics updated: {metrics}")
        await self.sio.emit('performance_metrics', self.performance_metrics)
    
    async def broadcast_ai_code_generation(self, code_data: Dict[str, Any]):
        """Broadcast AI code generation events"""
        await self.sio.emit('ai_code_generation', code_data)
    
    async def broadcast_evolution_progress(self, progress: Dict[str, Any]):
        """Broadcast evolution progress updates"""
        await self.sio.emit('evolution_progress', progress)
    
    async def broadcast_threat_detection(self, threat_data: Dict[str, Any]):
        """Broadcast threat detection events"""
        await self.sio.emit('threat_detection', threat_data)
    
    async def start_background_tasks(self):
        """Start background tasks for data updates"""
        asyncio.create_task(self._update_performance_loop())
        asyncio.create_task(self._update_queen_status_loop())
        asyncio.create_task(self._generate_mock_data_loop())
    
    async def _update_performance_loop(self):
        """Background loop to update performance metrics"""
        while True:
            try:
                # Get system metrics
                system_metrics = self.performance_monitor.get_system_metrics()
                
                # Get model performance
                model_metrics = self.performance_monitor.get_model_performance_metrics()
                
                # Combine metrics
                combined_metrics = {
                    'system': system_metrics,
                    'model': model_metrics,
                    'cache_stats': self.cache_manager.get_stats(),
                    'timestamp': datetime.now().isoformat()
                }
                
                await self.update_performance_metrics(combined_metrics)
                
            except Exception as e:
                logger.error(f"Error updating performance metrics: {e}")
            
            await asyncio.sleep(5)  # Update every 5 seconds
    
    async def _update_queen_status_loop(self):
        """Background loop to update queen status"""
        while True:
            try:
                # Simulate queen activity
                if self.queen_status['is_active']:
                    # Increment evolution progress
                    self.queen_status['evolution_progress'] += 0.01
                    if self.queen_status['evolution_progress'] >= 1.0:
                        self.queen_status['evolution_progress'] = 0.0
                        self.queen_status['current_generation'] += 1
                    
                    # Update fitness
                    self.queen_status['best_fitness'] = min(1.0, self.queen_status['best_fitness'] + 0.001)
                
                await self.update_queen_status(self.queen_status)
                
            except Exception as e:
                logger.error(f"Error updating queen status: {e}")
            
            await asyncio.sleep(2)  # Update every 2 seconds
    
    async def _generate_mock_data_loop(self):
        """Background loop to generate mock data for testing"""
        while True:
            try:
                # Generate mock bee agents
                mock_agents = []
                agent_types = ['threat', 'evolution', 'performance', 'system']
                
                for i in range(5):
                    agent_type = agent_types[i % len(agent_types)]
                    mock_agents.append({
                        'id': f'{agent_type}-{i+1}',
                        'type': agent_type,
                        'status': 'active' if i % 2 == 0 else 'idle',
                        'position': {'x': 100 + i * 50, 'y': 100 + i * 30},
                        'angle': i * 0.5,
                        'radius': 80 + i * 10,
                        'opacity': 0.8,
                        'last_activity': datetime.now().isoformat()
                    })
                
                await self.update_bee_agents(mock_agents)
                
                # Generate mock logs
                log_messages = [
                    'Analyzing network traffic patterns',
                    'Model accuracy improved to 94.2%',
                    'CPU usage optimized to 78%',
                    'Suspicious IP detected: 192.168.1.100',
                    'Blockchain hash logged successfully',
                    'New mutation applied to neural network',
                    'Performance optimization applied',
                    'Threat pattern analysis completed'
                ]
                
                log_levels = ['info', 'success', 'warning', 'error']
                log_types = ['threat', 'evolution', 'performance', 'system']
                
                import random
                mock_log = {
                    'agent_id': f'{random.choice(log_types)}-{random.randint(1, 100)}',
                    'message': random.choice(log_messages),
                    'level': random.choice(log_levels),
                    'type': random.choice(log_types)
                }
                
                await self.add_live_log(mock_log)
                
            except Exception as e:
                logger.error(f"Error generating mock data: {e}")
            
            await asyncio.sleep(3)  # Generate data every 3 seconds

# Create global instance
dashboard_ws_manager = DashboardWebSocketManager()

# FastAPI app with WebSocket support
app = FastAPI(title="BeeMind Dashboard API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO app
app.mount("/ws", dashboard_ws_manager.app)

# REST API endpoints for dashboard
@app.get("/api/dashboard/status")
async def get_dashboard_status():
    """Get overall dashboard status"""
    return {
        "queen_status": dashboard_ws_manager.queen_status,
        "active_agents": len(dashboard_ws_manager.bee_agents),
        "total_logs": len(dashboard_ws_manager.live_logs),
        "last_update": datetime.now().isoformat()
    }

@app.get("/api/dashboard/queen")
async def get_queen_status():
    """Get queen AI status"""
    return dashboard_ws_manager.queen_status

@app.get("/api/dashboard/agents")
async def get_bee_agents():
    """Get bee agents status"""
    return dashboard_ws_manager.bee_agents

@app.get("/api/dashboard/logs")
async def get_live_logs(limit: int = 50):
    """Get live logs"""
    return dashboard_ws_manager.live_logs[-limit:]

@app.get("/api/dashboard/metrics")
async def get_performance_metrics():
    """Get performance metrics"""
    return dashboard_ws_manager.performance_metrics

@app.get("/api/dashboard/evolution-stats")
async def get_evolution_stats():
    """Get evolution statistics"""
    return await dashboard_ws_manager._get_evolution_stats()

@app.post("/api/dashboard/log")
async def add_log_entry(log_entry: Dict[str, Any]):
    """Add a new log entry"""
    await dashboard_ws_manager.add_live_log(log_entry)
    return {"status": "success", "message": "Log entry added"}

@app.post("/api/dashboard/queen/update")
async def update_queen_status(status: Dict[str, Any]):
    """Update queen status"""
    await dashboard_ws_manager.update_queen_status(status)
    return {"status": "success", "message": "Queen status updated"}

@app.post("/api/dashboard/agents/update")
async def update_bee_agents(agents: List[Dict[str, Any]]):
    """Update bee agents"""
    await dashboard_ws_manager.update_bee_agents(agents)
    return {"status": "success", "message": "Bee agents updated"}

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting BeeMind Dashboard WebSocket Manager...")
    await dashboard_ws_manager.start_background_tasks()
    logger.info("Dashboard WebSocket Manager started successfully!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
