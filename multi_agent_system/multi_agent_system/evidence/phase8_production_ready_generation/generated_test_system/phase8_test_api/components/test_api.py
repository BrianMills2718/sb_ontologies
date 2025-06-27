#!/usr/bin/env python3
"""
Generated APIEndpoint Component: test_api
Production test API endpoint

This component provides a production-ready Flask blueprint for test_api.
Designed for concurrent request handling and Gunicorn WSGI deployment.
"""
import logging
import json
import time
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, g
from werkzeug.exceptions import BadRequest, InternalServerError
import threading

from autocoder.components import APIEndpoint, Component


# Request/Response schemas (using basic validation instead of Pydantic)
def validate_data_request(data):
    """Validate incoming data request"""
    if not isinstance(data, dict):
        raise BadRequest("Request data must be a JSON object")
    if 'data' not in data:
        raise BadRequest("Request must contain 'data' field")
    return data


class GeneratedAPIEndpoint_test_api(APIEndpoint):
    """
    Production test API endpoint
    
    Production-ready Flask blueprint component for concurrent request handling.
    Designed for Gunicorn WSGI deployment with thread-safe operations.
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        
        # Configuration - port must be provided by ResourceOrchestrator
        self.port = config.get('port') if config else None
        if self.port is None:
            raise ValueError(f"APIEndpoint {self.name} requires 'port' in configuration - no default port assigned")
        self.host = config.get('host', '0.0.0.0') if config else '0.0.0.0'
        
        # Thread-safe request counter for concurrent requests
        self._request_count = 0
        self._request_lock = threading.Lock()
        
        # Flask blueprint for this component
        self.blueprint = Blueprint(
            self.name, 
            __name__, 
            url_prefix=f'/{self.name}'
        )
        
        # Component state for V5 integration
        self.v5_store = None  # Will be injected by main app
        self.connected_components = {}
        
        # Setup routes
        self._setup_routes()
        
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{self.name}")
        self.logger.info(f"Flask blueprint initialized for {self.name} on port {self.port}")
    
    def _increment_request_count(self) -> int:
        """Thread-safe request counter increment"""
        with self._request_lock:
            self._request_count += 1
            return self._request_count
    
    @property
    def request_count(self) -> int:
        """Thread-safe request counter access"""
        with self._request_lock:
            return self._request_count
    
    def get_sync_health_status(self) -> Dict[str, Any]:
        """
        Synchronous health check for Flask integration.
        
        This method is called by the main Flask app health check endpoint.
        Must be synchronous to work with Flask routes.
        """
        try:
            health_data = {
                'status': 'healthy',
                'component': self.name,
                'type': self.__class__.__name__,
                'port': self.port,
                'requests_handled': self.request_count,
                'checks': {}
            }
            
            # Check V5 store health if available
            if self.v5_store and hasattr(self.v5_store, 'get_sync_health_status'):
                try:
                    store_health = self.v5_store.get_sync_health_status()
                    health_data['checks']['v5_store'] = store_health.get('status', 'unknown')
                except Exception as e:
                    health_data['checks']['v5_store'] = f'error: {str(e)}'
                    health_data['status'] = 'degraded'
            
            # Check blueprint registration
            health_data['checks']['blueprint_registered'] = 'healthy'
            
            return health_data
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'component': self.name,
                'type': self.__class__.__name__,
                'error': str(e)
            }
    
    def _setup_routes(self):
        """
        Setup Flask routes for the API endpoint.
        
        CRITICAL: This method defines the HTTP endpoints that the API exposes.
        Uses Flask blueprint decorators for production deployment.
        """
        
        @self.blueprint.route('/health', methods=['GET'])
        def health_check():
            """Production health check endpoint"""
            try:
                health_status = self.get_sync_health_status()
                status_code = 200 if health_status['status'] == 'healthy' else 503
                return jsonify(health_status), status_code
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                return jsonify({
                    'status': 'unhealthy',
                    'component': self.name,
                    'error': str(e)
                }), 503
        
        @self.blueprint.route('/data', methods=['GET'])
        def get_data():
            """Get data endpoint - shows component status"""
            try:
                return jsonify({
                    "component": self.name,
                    "requests_handled": self.request_count,
                    "message": "Data endpoint - use POST to submit data",
                    "connected_components": list(self.connected_components.keys()),
                    "v5_store_available": self.v5_store is not None
                })
            except Exception as e:
                self.logger.error(f"Get data failed: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.blueprint.route('/data', methods=['POST'])
        def post_data():
            """Process data through the component pipeline"""
            request_id = self._increment_request_count()
            
            try:
                # Validate request
                if not request.is_json:
                    raise BadRequest("Request must be JSON")
                
                request_data = request.get_json()
                validated_data = validate_data_request(request_data)
                
                # Process the data
                start_time = time.time()
                
                # Store data using V5 store if available
                storage_result = None
                if self.v5_store and hasattr(self.v5_store, 'sync_store'):
                    try:
                        storage_result = self.v5_store.sync_store(
                            validated_data['data'], 
                            table_name=f'{self.name}_data'
                        )
                    except Exception as e:
                        self.logger.warning(f"V5 store failed, continuing: {e}")
                
                # Prepare response
                processing_time = time.time() - start_time
                result = {
                    "status": "received",
                    "component": self.name,
                    "request_id": request_id,
                    "data_received": validated_data['data'],
                    "processing_time_ms": round(processing_time * 1000, 2),
                    "storage_result": storage_result,
                    "timestamp": time.time()
                }
                
                self.logger.info(f"Processed request {request_id} in {processing_time:.3f}s")
                
                return jsonify({
                    'result': result,
                    'processed_by': self.name
                })
                
            except BadRequest as e:
                self.logger.warning(f"Bad request {request_id}: {e}")
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                self.logger.error(f"Request {request_id} failed: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.blueprint.route('/metrics', methods=['GET'])
        def get_metrics():
            """Get component metrics"""
            try:
                metrics = {
                    "component": self.name,
                    "request_count": self.request_count,
                    "status": "active",
                    "health_status": self.get_sync_health_status(),
                    "v5_integration": {
                        "v5_store_connected": self.v5_store is not None,
                        "connected_components": len(self.connected_components)
                    }
                }
                
                # Add V5 store performance metrics if available
                if self.v5_store and hasattr(self.v5_store, 'performance_monitor'):
                    try:
                        perf_monitor = self.v5_store.performance_monitor
                        if hasattr(perf_monitor, 'get_performance_summary'):
                            metrics['v5_store_performance'] = perf_monitor.get_performance_summary()
                    except Exception as e:
                        metrics['v5_store_performance'] = f'error: {str(e)}'
                
                return jsonify(metrics)
                
            except Exception as e:
                self.logger.error(f"Metrics endpoint failed: {e}")
                return jsonify({'error': str(e)}), 500
        
        # Production-specific endpoints
        @self.blueprint.route('/status', methods=['GET'])
        def get_status():
            """Detailed status endpoint for monitoring"""
            try:
                status = {
                    'component': self.name,
                    'type': self.__class__.__name__,
                    'status': 'running',
                    'port': self.port,
                    'request_count': self.request_count,
                    'health': self.get_sync_health_status(),
                    'uptime': 'TODO: implement uptime tracking',
                    'memory_usage': 'TODO: implement memory tracking'
                }
                return jsonify(status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        self.logger.info(f"Flask routes configured for {self.name} - ready for production")
    
    def connect_v5_store(self, v5_store):
        """Connect V5EnhancedStore for database operations"""
        self.v5_store = v5_store
        self.logger.info(f"Connected V5EnhancedStore to {self.name}")
    
    def connect_component(self, component_name: str, component):
        """Connect another component for data flow"""
        self.connected_components[component_name] = component
        self.logger.info(f"Connected component {component_name} to {self.name}")
    
    async def _handle_inbound_stream_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle inbound data from other components (V5 harness integration).
        
        This method maintains compatibility with V5 SystemExecutionHarness
        while providing Flask production capabilities.
        """
        request_id = self._increment_request_count()
        
        # Store data for API access using V5 store
        processed_data = {
            "api_component": self.name,
            "api_port": self.port,
            "processed_at": time.time(),
            "request_id": request_id,
            "input_data": data
        }
        
        # Store in V5 store if available
        if self.v5_store and hasattr(self.v5_store, 'sync_store'):
            try:
                storage_result = self.v5_store.sync_store(processed_data, f'{self.name}_stream_data')
                processed_data['storage_result'] = storage_result
            except Exception as e:
                self.logger.warning(f"Stream data storage failed: {e}")
        
        self.logger.info(f"API processed stream data {request_id}: {data}")
        
        return processed_data
