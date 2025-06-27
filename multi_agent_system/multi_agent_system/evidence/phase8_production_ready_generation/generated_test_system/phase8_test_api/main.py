#!/usr/bin/env python3
"""
phase8_test_api - Production Flask Application
Test API system for Phase 8 production-ready generation validation

PRODUCTION CONFIGURATION:
- Uses Gunicorn WSGI server for production deployment
- Handles concurrent requests properly
- Includes health checks for load balancer integration
- Configured for horizontal scaling
"""
import os
import logging
import yaml
from pathlib import Path
from flask import Flask, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

# V5.1 Component imports
from components.test_api import GeneratedAPIEndpoint_test_api

# Configuration
CONFIG_FILE = Path(__file__).parent / "config" / "system_config.yaml"

# Setup production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/phase8_test_api.log')
    ]
)

logger = logging.getLogger("phase8_test_api")

def create_app():
    """
    Flask application factory for production deployment.
    
    This function creates and configures the Flask application for production use.
    Called by Gunicorn WSGI server to create application instances.
    """
    app = Flask(__name__)
    
    # Production middleware configuration
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Load configuration
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f) or {}
            logger.info(f"Loaded configuration from {CONFIG_FILE}")
    else:
        logger.warning(f"Configuration file not found: {CONFIG_FILE}")
    
    # Production configuration
    app.config.update({
        'ENV': os.getenv('FLASK_ENV', 'production'),
        'DEBUG': False,  # Never debug in production
        'TESTING': False,
        'SECRET_KEY': os.getenv('API_SECRET_KEY', 'production-secret-required'),
        'JSON_SORT_KEYS': False,
        'JSONIFY_PRETTYPRINT_REGULAR': False  # Disable pretty printing for performance
    })
    
    # Create and configure components
    test_api = GeneratedAPIEndpoint_test_api("test_api", config.get("test_api", {}))
    
    # Register component blueprints with Flask app
    app.register_blueprint(test_api.blueprint)
    
    # Production health check endpoints
    @app.route('/health')
    def health_check():
        """
        Production health check endpoint for load balancers.
        
        Returns:
            200 OK if system is healthy
            503 Service Unavailable if system has issues
        """
        try:
            health_status = {
                'status': 'healthy',
                'service': 'phase8_test_api',
                'version': '1.0.0',
                'components': {}
            }
            
            # Check each component health using sync wrappers
            for comp_name, comp in [
                ('test_api', test_api)
            ]:
                try:
                    # Use sync health check wrapper for V5 components
                    if hasattr(comp, 'get_sync_health_status'):
                        comp_health = comp.get_sync_health_status()
                    else:
                        comp_health = {'status': 'healthy', 'message': 'No health check available'}
                    
                    health_status['components'][comp_name] = comp_health
                except Exception as e:
                    logger.error(f"Health check failed for component {comp_name}: {e}")
                    health_status['components'][comp_name] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
                    health_status['status'] = 'degraded'
            
            # Return appropriate status code
            status_code = 200
            if health_status['status'] in ['unhealthy', 'degraded']:
                status_code = 503
                
            return jsonify(health_status), status_code
            
        except Exception as e:
            logger.error(f"Health check endpoint failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'service': 'phase8_test_api',
                'error': str(e)
            }), 503
    
    @app.route('/ready')
    def readiness_check():
        """
        Kubernetes readiness probe endpoint.
        
        Returns:
            200 OK if service is ready to accept traffic
            503 Service Unavailable if service is not ready
        """
        try:
            # Basic readiness check - ensure core components are initialized
            ready_status = {
                'status': 'ready',
                'service': 'phase8_test_api',
                'components_initialized': len([
                    test_api
                ])
            }
            
            return jsonify(ready_status), 200
            
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return jsonify({
                'status': 'not_ready',
                'service': 'phase8_test_api',
                'error': str(e)
            }), 503
    
    @app.route('/metrics')
    def metrics_endpoint():
        """
        Production metrics endpoint for monitoring systems.
        
        Provides application metrics in a format compatible with
        Prometheus and other monitoring systems.
        """
        try:
            metrics = {
                'system': 'phase8_test_api',
                'uptime': 'TODO: implement uptime tracking',
                'requests_total': 'TODO: implement request counting',
                'components': {}
            }
            
            # Collect component metrics
            for comp_name, comp in [
                ('test_api', test_api)
            ]:
                try:
                    if hasattr(comp, 'get_metrics'):
                        comp_metrics = comp.get_metrics()
                        metrics['components'][comp_name] = comp_metrics
                except Exception as e:
                    logger.warning(f"Failed to get metrics for {comp_name}: {e}")
                    metrics['components'][comp_name] = {'error': str(e)}
            
            return jsonify(metrics), 200
            
        except Exception as e:
            logger.error(f"Metrics endpoint failed: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Production error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({'error': 'Service temporarily unavailable'}), 503
    
    # CORS headers for production API
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    logger.info(f"{system_name} Flask application initialized for production")
    return app

# Create the WSGI application instance
# This is called by Gunicorn to create the application
app = create_app()

if __name__ == "__main__":
    # Development mode fallback (should not be used in production)
    logger.warning("Running in development mode - use Gunicorn for production")
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 8080)),
        debug=False
    )
