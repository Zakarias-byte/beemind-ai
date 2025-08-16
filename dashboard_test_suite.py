#!/usr/bin/env python3
"""
BeeMind Dashboard Test Suite
Comprehensive testing for Fase 4.7: Final Integration & Testing
"""

import asyncio
import json
import time
import requests
import socketio
import pytest
from datetime import datetime
from typing import Dict, Any, List

# Test configuration
DASHBOARD_URL = "http://localhost:8001"
WEBSOCKET_URL = f"{DASHBOARD_URL}/ws"
API_BASE_URL = f"{DASHBOARD_URL}/api/dashboard"

class DashboardTestSuite:
    """Comprehensive test suite for BeeMind Dashboard"""
    
    def __init__(self):
        self.sio = socketio.Client()
        self.test_results = []
        self.websocket_connected = False
        self.received_data = {
            'queen_status': None,
            'bee_agents': None,
            'live_logs': [],
            'performance_metrics': None,
            'evolution_stats': None
        }
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        print(f"[{status.upper()}] {test_name}: {details}")
    
    async def setup_websocket(self):
        """Setup WebSocket connection for testing"""
        try:
            @self.sio.event
            def connect():
                self.websocket_connected = True
                self.log_test("WebSocket Connection", "PASS", "Successfully connected")
            
            @self.sio.event
            def disconnect():
                self.websocket_connected = False
                self.log_test("WebSocket Disconnection", "INFO", "Disconnected")
            
            @self.sio.on('queen_status')
            def on_queen_status(data):
                self.received_data['queen_status'] = data
                self.log_test("Queen Status Reception", "PASS", f"Received: {data.get('is_active', 'N/A')}")
            
            @self.sio.on('bee_agents')
            def on_bee_agents(data):
                self.received_data['bee_agents'] = data
                self.log_test("Bee Agents Reception", "PASS", f"Received {len(data)} agents")
            
            @self.sio.on('live_logs')
            def on_live_logs(data):
                self.received_data['live_logs'].extend(data)
                self.log_test("Live Logs Reception", "PASS", f"Received {len(data)} logs")
            
            @self.sio.on('performance_metrics')
            def on_performance_metrics(data):
                self.received_data['performance_metrics'] = data
                self.log_test("Performance Metrics Reception", "PASS", "Received metrics")
            
            @self.sio.on('evolution_stats')
            def on_evolution_stats(data):
                self.received_data['evolution_stats'] = data
                self.log_test("Evolution Stats Reception", "PASS", "Received stats")
            
            self.sio.connect(WEBSOCKET_URL)
            await asyncio.sleep(2)  # Wait for connection
            
        except Exception as e:
            self.log_test("WebSocket Setup", "FAIL", f"Setup failed: {str(e)}")
    
    def test_rest_api_endpoints(self):
        """Test all REST API endpoints"""
        endpoints = [
            ("/status", "GET"),
            ("/queen", "GET"),
            ("/agents", "GET"),
            ("/logs", "GET"),
            ("/metrics", "GET"),
            ("/evolution-stats", "GET")
        ]
        
        for endpoint, method in endpoints:
            try:
                url = f"{API_BASE_URL}{endpoint}"
                if method == "GET":
                    response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"API {endpoint}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_test(f"API {endpoint}", "FAIL", f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"API {endpoint}", "FAIL", f"Request failed: {str(e)}")
    
    def test_websocket_events(self):
        """Test WebSocket event emission"""
        try:
            # Test queen status request
            self.sio.emit('request_queen_status')
            time.sleep(1)
            
            # Test bee agents request
            self.sio.emit('request_bee_agents')
            time.sleep(1)
            
            # Test live logs request
            self.sio.emit('request_live_logs')
            time.sleep(1)
            
            # Test performance metrics request
            self.sio.emit('request_performance_metrics')
            time.sleep(1)
            
            # Test evolution stats request
            self.sio.emit('request_evolution_stats')
            time.sleep(1)
            
            self.log_test("WebSocket Events", "PASS", "All events emitted successfully")
            
        except Exception as e:
            self.log_test("WebSocket Events", "FAIL", f"Event emission failed: {str(e)}")
    
    def test_data_validation(self):
        """Validate received data structure"""
        try:
            # Validate queen status
            if self.received_data['queen_status']:
                queen_data = self.received_data['queen_status']
                required_fields = ['is_active', 'evolution_progress', 'current_generation', 'best_fitness']
                
                for field in required_fields:
                    if field not in queen_data:
                        self.log_test("Queen Status Validation", "FAIL", f"Missing field: {field}")
                        return
                
                self.log_test("Queen Status Validation", "PASS", "All required fields present")
            
            # Validate bee agents
            if self.received_data['bee_agents']:
                agents = self.received_data['bee_agents']
                if isinstance(agents, list):
                    self.log_test("Bee Agents Validation", "PASS", f"Valid list with {len(agents)} agents")
                else:
                    self.log_test("Bee Agents Validation", "FAIL", "Not a valid list")
            
            # Validate live logs
            if self.received_data['live_logs']:
                logs = self.received_data['live_logs']
                if isinstance(logs, list) and len(logs) > 0:
                    self.log_test("Live Logs Validation", "PASS", f"Valid logs list with {len(logs)} entries")
                else:
                    self.log_test("Live Logs Validation", "FAIL", "Invalid logs structure")
            
            # Validate performance metrics
            if self.received_data['performance_metrics']:
                metrics = self.received_data['performance_metrics']
                if isinstance(metrics, dict):
                    self.log_test("Performance Metrics Validation", "PASS", "Valid metrics object")
                else:
                    self.log_test("Performance Metrics Validation", "FAIL", "Invalid metrics structure")
                    
        except Exception as e:
            self.log_test("Data Validation", "FAIL", f"Validation failed: {str(e)}")
    
    def test_performance_metrics(self):
        """Test performance monitoring"""
        try:
            # Test system metrics
            response = requests.get(f"{API_BASE_URL}/metrics", timeout=10)
            if response.status_code == 200:
                metrics = response.json()
                
                # Check for required system metrics
                if 'system' in metrics:
                    system_metrics = metrics['system']
                    required_system_fields = ['cpu_percent', 'memory_percent', 'disk_percent']
                    
                    for field in required_system_fields:
                        if field in system_metrics:
                            value = system_metrics[field]
                            if isinstance(value, (int, float)) and 0 <= value <= 100:
                                self.log_test(f"System Metric {field}", "PASS", f"Value: {value}")
                            else:
                                self.log_test(f"System Metric {field}", "FAIL", f"Invalid value: {value}")
                        else:
                            self.log_test(f"System Metric {field}", "FAIL", "Field missing")
                
                # Check for cache stats
                if 'cache_stats' in metrics:
                    self.log_test("Cache Stats", "PASS", "Cache statistics present")
                else:
                    self.log_test("Cache Stats", "WARN", "Cache statistics missing")
                    
        except Exception as e:
            self.log_test("Performance Metrics Test", "FAIL", f"Test failed: {str(e)}")
    
    def test_evolution_integration(self):
        """Test evolution algorithm integration"""
        try:
            # Test evolution stats endpoint
            response = requests.get(f"{API_BASE_URL}/evolution-stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                
                # Validate evolution statistics
                required_fields = ['total_sessions', 'avg_fitness', 'total_generations']
                for field in required_fields:
                    if field in stats:
                        value = stats[field]
                        if isinstance(value, (int, float)):
                            self.log_test(f"Evolution Stats {field}", "PASS", f"Value: {value}")
                        else:
                            self.log_test(f"Evolution Stats {field}", "FAIL", f"Invalid type: {type(value)}")
                    else:
                        self.log_test(f"Evolution Stats {field}", "FAIL", "Field missing")
                        
        except Exception as e:
            self.log_test("Evolution Integration", "FAIL", f"Test failed: {str(e)}")
    
    def test_real_time_updates(self):
        """Test real-time data updates"""
        try:
            initial_logs_count = len(self.received_data['live_logs'])
            
            # Wait for new data
            time.sleep(5)
            
            current_logs_count = len(self.received_data['live_logs'])
            
            if current_logs_count > initial_logs_count:
                self.log_test("Real-time Updates", "PASS", f"Received {current_logs_count - initial_logs_count} new logs")
            else:
                self.log_test("Real-time Updates", "WARN", "No new logs received in 5 seconds")
                
        except Exception as e:
            self.log_test("Real-time Updates", "FAIL", f"Test failed: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        try:
            # Test invalid endpoint
            response = requests.get(f"{DASHBOARD_URL}/api/invalid", timeout=5)
            if response.status_code == 404:
                self.log_test("Error Handling - Invalid Endpoint", "PASS", "Correctly returned 404")
            else:
                self.log_test("Error Handling - Invalid Endpoint", "FAIL", f"Unexpected status: {response.status_code}")
                
            # Test invalid WebSocket event
            self.sio.emit('invalid_event', {'test': 'data'})
            time.sleep(1)
            self.log_test("Error Handling - Invalid WebSocket Event", "PASS", "No crash occurred")
            
        except Exception as e:
            self.log_test("Error Handling", "FAIL", f"Error handling test failed: {str(e)}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warning_tests = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'warnings': warning_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'test_results': self.test_results,
            'recommendations': []
        }
        
        # Generate recommendations
        if failed_tests > 0:
            report['recommendations'].append("Fix failed tests before deployment")
        
        if warning_tests > 0:
            report['recommendations'].append("Review warnings and address critical issues")
        
        if passed_tests / total_tests < 0.8:
            report['recommendations'].append("Low success rate - review test failures")
        
        # Save report
        with open('dashboard_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("BEE MIND DASHBOARD TEST REPORT")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Warnings: {warning_tests} ⚠️")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print("="*60)
        
        if report['recommendations']:
            print("\nRECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"• {rec}")
        
        return report
    
    async def run_full_test_suite(self):
        """Run complete test suite"""
        print("🚀 Starting BeeMind Dashboard Test Suite...")
        print("="*60)
        
        # Setup WebSocket
        await self.setup_websocket()
        
        # Run tests
        self.test_rest_api_endpoints()
        self.test_websocket_events()
        self.test_data_validation()
        self.test_performance_metrics()
        self.test_evolution_integration()
        self.test_real_time_updates()
        self.test_error_handling()
        
        # Generate report
        report = self.generate_test_report()
        
        # Cleanup
        if self.websocket_connected:
            self.sio.disconnect()
        
        return report

async def main():
    """Main test runner"""
    test_suite = DashboardTestSuite()
    report = await test_suite.run_full_test_suite()
    
    # Exit with appropriate code
    if report['summary']['failed'] > 0:
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    asyncio.run(main())
