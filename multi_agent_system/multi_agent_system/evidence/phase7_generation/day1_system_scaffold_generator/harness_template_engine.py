#!/usr/bin/env python3
"""
HarnessTemplateEngine: Template engine for generating SystemExecutionHarness-based code
=====================================================================================

Provides templates and rendering functionality for generating harness-compatible code
from SystemBlueprint definitions.

Key Features:
- Main template for complete harness-based main.py files
- Component registration templates
- Stream connection templates
- Configuration templates
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
from string import Template
from datetime import datetime

# Add evidence paths for integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))


class HarnessTemplateEngine:
    """
    Template engine for generating SystemExecutionHarness-based code.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("HarnessTemplateEngine")
        self.logger.info("🎨 HarnessTemplateEngine initialized")
        
        # Load templates
        self.main_template = self._load_main_template()
        self.component_templates = self._load_component_templates()
    
    def render_main_template(self, imports: List[str], registration_code: str, 
                           connection_code: str, config: Dict[str, Any]) -> str:
        """
        Render complete main.py with harness setup.
        
        Args:
            imports: List of import statements
            registration_code: Component registration code
            connection_code: Stream connection code  
            config: System configuration
            
        Returns:
            Complete main.py file content
        """
        self.logger.info("🎨 Rendering main template")
        
        try:
            # Prepare template variables
            template_vars = {
                'generation_timestamp': datetime.now().isoformat(),
                'imports': '\n'.join(imports) if imports else '# No custom imports',
                'registration_code': registration_code if registration_code else '        # No components to register',
                'connection_code': connection_code if connection_code else '        # No connections to establish',
                'config_dict': self._format_config_for_template(config)
            }
            
            # Render template
            rendered = self.main_template.format(**template_vars)
            
            self.logger.info("✅ Main template rendered successfully")
            return rendered
            
        except Exception as e:
            self.logger.error(f"❌ Failed to render main template: {e}")
            raise
    
    def render_component_template(self, component_name: str, class_name: str, 
                                component_type: str, config: Dict[str, Any]) -> str:
        """
        Render component registration template.
        
        Args:
            component_name: Name of the component
            class_name: Class name for the component
            component_type: Type of component
            config: Component configuration
            
        Returns:
            Component registration code
        """
        template = self.component_templates.get('registration', '')
        
        template_vars = {
            'component_name': component_name,
            'class_name': class_name,
            'component_type': component_type,
            'config': self._format_config_for_template(config)
        }
        
        return template.format(**template_vars)
    
    def _load_main_template(self) -> str:
        """Load the main template for harness-based systems"""
        template = '''#!/usr/bin/env python3
"""
Generated SystemExecutionHarness-based system
Generated from: Natural Language via V5.0 Two-Phase Generation Pipeline
Generated on: {generation_timestamp}
"""

import asyncio
import logging
from pathlib import Path
import sys
import os

# Add component paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'components'))

# Import SystemExecutionHarness
from evidence.phase6_harness.day2_execution_harness.system_execution_harness import (
    SystemExecutionHarness, HarnessConfiguration
)

# Import generated components
{imports}

# Import configuration
from config.system_config import get_config, get_component_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main harness orchestration function"""
    logger.info("🚀 Starting SystemExecutionHarness-based system...")
    
    try:
        # Load system configuration
        system_config = get_config()
        harness_config = HarnessConfiguration(**system_config.get('harness', {{}}))
        
        # Initialize harness
        harness = SystemExecutionHarness(harness_config)
        logger.info("✨ SystemExecutionHarness initialized")
        
        # Component registration
{registration_code}
        
        logger.info("📝 All components registered")
        
        # Stream connections
{connection_code}
        
        logger.info("🔗 All stream connections established")
        
        # Start system
        logger.info("▶️ Starting harness system...")
        await harness.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received shutdown signal")
    except Exception as e:
        logger.error(f"❌ System startup failed: {{e}}")
        raise
    finally:
        logger.info("🏁 System shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n🛑 System interrupted by user")
    except Exception as e:
        print(f"❌ System failed: {{e}}")
        sys.exit(1)
'''
        
        return template
    
    def _load_component_templates(self) -> Dict[str, str]:
        """Load component-related templates"""
        templates = {}
        
        # Component registration template
        templates['registration'] = '''
        # Register {component_name} ({component_type})
        {component_name}_config = get_component_config('{component_name}')
        {component_name}_instance = {class_name}({component_name}_config)
        harness.register_component('{component_name}', {component_name}_instance)'''
        
        # Component class template
        templates['component_class'] = '''
class {class_name}(HarnessComponent):
    """Generated {component_type} component"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(ComponentConfiguration(
            name='{component_name}',
            service_type='{component_type}',
            **config
        ))
    
    async def process(self):
        """Main processing logic"""
        # TODO: Implement component logic
        await asyncio.sleep(0.1)
'''
        
        return templates
    
    def _format_config_for_template(self, config: Dict[str, Any]) -> str:
        """Format configuration dictionary for template insertion"""
        if not config:
            return "{}"
        
        import json
        return json.dumps(config, indent=8)
    
    def render_dockerfile_template(self, system_name: str, requirements: List[str]) -> str:
        """
        Render Dockerfile template for the generated system.
        
        Args:
            system_name: Name of the system
            requirements: List of Python requirements
            
        Returns:
            Dockerfile content
        """
        dockerfile_template = '''# Generated Dockerfile for {system_name}
# Generated by V5.0 Two-Phase Generation Pipeline

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose any necessary ports
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["python", "main.py"]
'''
        
        return dockerfile_template.format(system_name=system_name)
    
    def render_requirements_template(self, additional_requirements: List[str] = None) -> str:
        """
        Render requirements.txt template.
        
        Args:
            additional_requirements: Additional requirements to include
            
        Returns:
            requirements.txt content
        """
        base_requirements = [
            "anyio>=3.7.0",
            "asyncio-mqtt>=0.11.0", 
            "aiofiles>=23.2.1",
            "structlog>=23.1.0",
            "pydantic>=2.0.0",
            "httpx>=0.24.0",
            "uvloop>=0.17.0; sys_platform != 'win32'"
        ]
        
        if additional_requirements:
            base_requirements.extend(additional_requirements)
        
        return '\n'.join(sorted(base_requirements))
    
    def render_docker_compose_template(self, system_name: str, services: List[str]) -> str:
        """
        Render docker-compose.yml template.
        
        Args:
            system_name: Name of the system
            services: List of service names
            
        Returns:
            docker-compose.yml content
        """
        compose_template = '''version: '3.8'

services:
  {system_name}:
    build: .
    container_name: {system_name}
    ports:
      - "8080:8080"
    environment:
      - LOG_LEVEL=INFO
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Additional services can be added here
  # redis:
  #   image: redis:7-alpine
  #   ports:
  #     - "6379:6379"
  
  # postgres:
  #   image: postgres:15-alpine
  #   environment:
  #     POSTGRES_DB: {system_name}
  #     POSTGRES_USER: app
  #     POSTGRES_PASSWORD: password
  #   ports:
  #     - "5432:5432"
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:

networks:
  default:
    name: {system_name}_network
'''
        
        return compose_template.format(system_name=system_name)


# Export main class
__all__ = ['HarnessTemplateEngine']