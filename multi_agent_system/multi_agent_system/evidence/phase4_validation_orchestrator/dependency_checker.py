#!/usr/bin/env python3
"""
Pre-flight Dependency Validation for ValidationDrivenOrchestrator
===============================================================

Implements fail-hard dependency checking with NO FALLBACKS.
All required dependencies must be configured and available before
validation begins. No mock modes or graceful degradation.

Validates:
1. LLM availability for Level 4 semantic validation
2. Database availability for Level 3 integration testing  
3. External service availability for component dependencies
4. Framework component availability
"""

import asyncio
import os
import logging
from typing import Dict, Any, List, Optional, Set
import aiohttp
import socket
from pathlib import Path

from validation_result_types import ValidationDependencyError


class ValidationDependencyChecker:
    """
    Pre-flight dependency validation with fail-hard enforcement.
    
    This checker validates all required dependencies are available
    and properly configured before validation begins. NO FALLBACKS.
    """
    
    def __init__(self, testing_mode: bool = False):
        self.logger = logging.getLogger("ValidationDependencyChecker")
        
        # Testing mode allows some dependencies to be missing for unit tests
        self.testing_mode = testing_mode
        
        # Required environment variables for different validation levels
        self.REQUIRED_ENV_VARS = {
            'level4_semantic': ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY'],  # At least one required
            'level3_integration': ['DATABASE_URL', 'POSTGRES_HOST'],      # At least one required
        }
        
        # Default service ports for connectivity testing
        self.DEFAULT_SERVICE_PORTS = {
            'database': 5432,
            'redis': 6379,
            'mongodb': 27017,
            'elasticsearch': 9200,
            'mysql': 3306
        }
        
        # Timeout settings for dependency checks
        self.CONNECTION_TIMEOUT = 5.0  # seconds
        self.HTTP_TIMEOUT = 10.0       # seconds
        
        self.logger.info("✅ ValidationDependencyChecker initialized with fail-hard validation")
    
    async def validate_all_dependencies_configured(self, blueprint: 'SystemBlueprint') -> None:
        """
        Fail hard if any required dependencies are missing.
        
        This is the main pre-flight validation method that checks all
        dependencies required for the four-tier validation pipeline.
        
        Args:
            blueprint: SystemBlueprint containing component dependencies
            
        Raises:
            ValidationDependencyError: If any required dependencies are missing
        """
        self.logger.info("🔍 Starting pre-flight dependency validation")
        
        missing_deps = []
        
        # Level 4: Check LLM availability for semantic validation
        if not await self._is_llm_configured():
            if self.testing_mode:
                self.logger.warning("⚠️ LLM not configured - continuing in testing mode")
            else:
                missing_deps.append(
                    "LLM (OPENAI_API_KEY or ANTHROPIC_API_KEY required for Level 4 semantic validation)"
                )
        
        # Level 3: Check database availability for integration testing
        if not await self._is_database_available():
            if self.testing_mode:
                self.logger.warning("⚠️ Database not configured - continuing in testing mode")
            else:
                missing_deps.append(
                    "Database (DATABASE_URL or POSTGRES_HOST required for Level 3 integration testing)"
                )
        
        # Component-specific: Check external services for each component
        component_deps = await self._validate_component_external_dependencies(blueprint)
        missing_deps.extend(component_deps)
        
        # Framework: Check framework component availability
        framework_deps = await self._validate_framework_dependencies()
        missing_deps.extend(framework_deps)
        
        # Phase 2-3: Check integration dependencies
        integration_deps = await self._validate_integration_dependencies()
        missing_deps.extend(integration_deps)
        
        # Fail hard if any dependencies are missing
        if missing_deps:
            error_message = (
                f"Cannot proceed with validation - missing required dependencies:\n" +
                "\n".join(f"  - {dep}" for dep in missing_deps) +
                "\n\nAll dependencies must be configured and available during development. "
                "NO MOCK MODES OR FALLBACKS AVAILABLE."
            )
            self.logger.error(f"❌ Pre-flight dependency validation failed: {len(missing_deps)} missing dependencies")
            raise ValidationDependencyError(error_message)
        
        self.logger.info("✅ Pre-flight dependency validation passed - all dependencies available")
    
    async def _is_llm_configured(self) -> bool:
        """
        Check if LLM is properly configured for Level 4 semantic validation.
        
        Validates that at least one LLM API key is set and the service is reachable.
        """
        # Check for API keys
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not openai_key and not anthropic_key:
            self.logger.warning("No LLM API keys found in environment")
            return False
        
        # Test LLM connectivity
        if openai_key:
            if await self._test_openai_connectivity(openai_key):
                self.logger.info("✅ OpenAI LLM connectivity verified")
                return True
        
        if anthropic_key:
            if await self._test_anthropic_connectivity(anthropic_key):
                self.logger.info("✅ Anthropic LLM connectivity verified")
                return True
        
        self.logger.warning("LLM API keys present but services unreachable")
        return False
    
    async def _test_openai_connectivity(self, api_key: str) -> bool:
        """Test OpenAI API connectivity"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.HTTP_TIMEOUT)) as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                # Use models endpoint for lightweight connectivity test
                async with session.get('https://api.openai.com/v1/models', headers=headers) as response:
                    if response.status == 200:
                        return True
                    else:
                        self.logger.warning(f"OpenAI API returned status {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.warning(f"OpenAI connectivity test failed: {e}")
            return False
    
    async def _test_anthropic_connectivity(self, api_key: str) -> bool:
        """Test Anthropic API connectivity"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.HTTP_TIMEOUT)) as session:
                headers = {
                    'x-api-key': api_key,
                    'Content-Type': 'application/json',
                    'anthropic-version': '2023-06-01'
                }
                
                # Test with a minimal request
                test_payload = {
                    'model': 'claude-3-haiku-20240307',
                    'messages': [{'role': 'user', 'content': 'test'}],
                    'max_tokens': 1
                }
                
                async with session.post('https://api.anthropic.com/v1/messages', 
                                      headers=headers, json=test_payload) as response:
                    # Accept both success and rate limit responses as "reachable"
                    if response.status in [200, 429]:
                        return True
                    else:
                        self.logger.warning(f"Anthropic API returned status {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.warning(f"Anthropic connectivity test failed: {e}")
            return False
    
    async def _is_database_available(self) -> bool:
        """
        Check if database is available for Level 3 integration testing.
        
        Tests database connectivity using environment configuration.
        """
        # Check for database configuration
        database_url = os.getenv('DATABASE_URL')
        postgres_host = os.getenv('POSTGRES_HOST')
        postgres_port = int(os.getenv('POSTGRES_PORT', '5432'))
        
        if not database_url and not postgres_host:
            self.logger.warning("No database configuration found")
            return False
        
        # Test database connectivity
        if database_url:
            if await self._test_database_url_connectivity(database_url):
                self.logger.info("✅ Database connectivity verified via DATABASE_URL")
                return True
        
        if postgres_host:
            if await self._test_host_port_connectivity(postgres_host, postgres_port, "PostgreSQL"):
                self.logger.info("✅ PostgreSQL connectivity verified")
                return True
        
        self.logger.warning("Database configuration present but service unreachable")
        return False
    
    async def _test_database_url_connectivity(self, database_url: str) -> bool:
        """Test database connectivity using database URL"""
        try:
            # For now, we'll do a simple URL parsing check
            # In production, this would use asyncpg or similar to test actual connectivity
            from urllib.parse import urlparse
            
            parsed = urlparse(database_url)
            if not parsed.hostname or not parsed.port:
                return False
            
            # Test TCP connectivity to database host/port
            return await self._test_host_port_connectivity(
                parsed.hostname, 
                parsed.port or self.DEFAULT_SERVICE_PORTS.get('database', 5432),
                "Database"
            )
            
        except Exception as e:
            self.logger.warning(f"Database URL connectivity test failed: {e}")
            return False
    
    async def _test_host_port_connectivity(self, host: str, port: int, service_name: str) -> bool:
        """Test TCP connectivity to host:port"""
        try:
            # Use asyncio to test TCP connectivity
            future = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(future, timeout=self.CONNECTION_TIMEOUT)
            
            # Close the connection
            writer.close()
            await writer.wait_closed()
            
            self.logger.debug(f"{service_name} at {host}:{port} is reachable")
            return True
            
        except asyncio.TimeoutError:
            self.logger.warning(f"{service_name} at {host}:{port} connection timeout")
            return False
        except Exception as e:
            self.logger.warning(f"{service_name} at {host}:{port} connection failed: {e}")
            return False
    
    async def _validate_component_external_dependencies(self, blueprint: 'SystemBlueprint') -> List[str]:
        """Validate external service dependencies for each component"""
        missing_deps = []
        
        for component in blueprint.components:
            component_name = component.get('name', 'unnamed')
            dependencies = component.get('dependencies', [])
            
            for dependency in dependencies:
                dep_type = dependency.get('dependency_type', '')
                dep_name = dependency.get('component_name', '')
                
                # Check for external service dependencies
                if dep_type == 'service_dependency':
                    if not await self._is_external_service_available(dependency):
                        if self.testing_mode:
                            self.logger.warning(f"⚠️ External service '{dep_name}' not available - continuing in testing mode")
                        else:
                            missing_deps.append(
                                f"External service '{dep_name}' required by component '{component_name}'"
                            )
                
                # Check for configuration dependencies
                elif dep_type == 'configuration_dependency':
                    if not await self._is_configuration_available(dependency):
                        missing_deps.append(
                            f"Configuration dependency '{dep_name}' required by component '{component_name}'"
                        )
        
        return missing_deps
    
    async def _is_external_service_available(self, service_dependency: Dict[str, Any]) -> bool:
        """Check if external service is available"""
        service_name = service_dependency.get('component_name', '')
        service_config = service_dependency.get('configuration', {})
        
        # Extract service connection details
        host = service_config.get('host', 'localhost')
        port = service_config.get('port')
        
        # Use default port if not specified
        if not port:
            service_type = service_dependency.get('service_type', service_name.lower())
            port = self.DEFAULT_SERVICE_PORTS.get(service_type, 80)
        
        # Test service connectivity
        return await self._test_host_port_connectivity(host, port, f"External service '{service_name}'")
    
    async def _is_configuration_available(self, config_dependency: Dict[str, Any]) -> bool:
        """Check if configuration dependency is satisfied"""
        config_name = config_dependency.get('component_name', '')
        required_env_vars = config_dependency.get('required_env_vars', [])
        required_files = config_dependency.get('required_files', [])
        
        # Check required environment variables
        for env_var in required_env_vars:
            if not os.getenv(env_var):
                self.logger.warning(f"Missing required environment variable: {env_var}")
                return False
        
        # Check required files
        for file_path in required_files:
            if not Path(file_path).exists():
                self.logger.warning(f"Missing required file: {file_path}")
                return False
        
        return True
    
    async def _validate_framework_dependencies(self) -> List[str]:
        """Validate framework component dependencies"""
        missing_deps = []
        
        # Check Python version
        import sys
        if sys.version_info < (3, 8):
            missing_deps.append("Python 3.8+ required for V5.0 framework")
        
        # Check required packages
        required_packages = [
            'pydantic',
            'asyncio',
            'aiohttp',
            'yaml'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_deps.append(f"Python package '{package}' required for framework")
        
        return missing_deps
    
    async def _validate_integration_dependencies(self) -> List[str]:
        """Validate Phase 2-3 integration dependencies"""
        missing_deps = []
        
        # Check Phase 2 component library availability
        phase2_path = Path(__file__).parent.parent / 'phase2_component_library'
        if not phase2_path.exists():
            missing_deps.append("Phase 2 component library not found for integration")
        else:
            # Check key Phase 2 files
            required_phase2_files = [
                'component_registry.py',
                'schema_framework.py'
            ]
            
            for file_name in required_phase2_files:
                if not (phase2_path / file_name).exists():
                    missing_deps.append(f"Phase 2 file missing: {file_name}")
        
        # Check Phase 3 blueprint schema availability
        phase3_path = Path(__file__).parent.parent / 'phase3_blueprint_schema'
        if not phase3_path.exists():
            missing_deps.append("Phase 3 blueprint schema not found for integration")
        else:
            # Check key Phase 3 files
            required_phase3_files = [
                'schema_parser.py',
                'reasonableness_checks.py'
            ]
            
            for file_name in required_phase3_files:
                if not (phase3_path / file_name).exists():
                    missing_deps.append(f"Phase 3 file missing: {file_name}")
        
        return missing_deps
    
    async def validate_specific_dependencies(self, dependency_types: List[str]) -> Dict[str, bool]:
        """
        Validate specific dependency types and return detailed results.
        
        Args:
            dependency_types: List of dependency types to check
            
        Returns:
            Dict mapping dependency type to availability status
        """
        results = {}
        
        for dep_type in dependency_types:
            if dep_type == 'llm':
                results['llm'] = await self._is_llm_configured()
            elif dep_type == 'database':
                results['database'] = await self._is_database_available()
            elif dep_type == 'framework':
                framework_deps = await self._validate_framework_dependencies()
                results['framework'] = len(framework_deps) == 0
            elif dep_type == 'integration':
                integration_deps = await self._validate_integration_dependencies()
                results['integration'] = len(integration_deps) == 0
            else:
                self.logger.warning(f"Unknown dependency type: {dep_type}")
                results[dep_type] = False
        
        return results
    
    def get_dependency_status(self) -> Dict[str, Any]:
        """Get current dependency configuration status"""
        return {
            'llm_api_keys': {
                'openai_configured': bool(os.getenv('OPENAI_API_KEY')),
                'anthropic_configured': bool(os.getenv('ANTHROPIC_API_KEY'))
            },
            'database_config': {
                'database_url_configured': bool(os.getenv('DATABASE_URL')),
                'postgres_host_configured': bool(os.getenv('POSTGRES_HOST'))
            },
            'phase_integration': {
                'phase2_path_exists': (Path(__file__).parent.parent / 'phase2_component_library').exists(),
                'phase3_path_exists': (Path(__file__).parent.parent / 'phase3_blueprint_schema').exists()
            }
        }


# Convenience functions for external use
async def check_all_dependencies(blueprint: 'SystemBlueprint') -> bool:
    """Check all dependencies for blueprint - returns True if all available"""
    checker = ValidationDependencyChecker()
    try:
        await checker.validate_all_dependencies_configured(blueprint)
        return True
    except ValidationDependencyError:
        return False


async def check_specific_dependency(dependency_type: str) -> bool:
    """Check specific dependency type - returns True if available"""
    checker = ValidationDependencyChecker()
    results = await checker.validate_specific_dependencies([dependency_type])
    return results.get(dependency_type, False)


# Main execution for testing
if __name__ == "__main__":
    async def main():
        """Test ValidationDependencyChecker"""
        
        # Create test checker
        checker = ValidationDependencyChecker()
        
        # Display current dependency status
        status = checker.get_dependency_status()
        print("🔍 Current Dependency Status:")
        for category, details in status.items():
            print(f"  {category}: {details}")
        
        # Test specific dependencies
        dependency_types = ['llm', 'database', 'framework', 'integration']
        results = await checker.validate_specific_dependencies(dependency_types)
        
        print("\n🧪 Dependency Validation Results:")
        for dep_type, available in results.items():
            status_icon = "✅" if available else "❌"
            print(f"  {status_icon} {dep_type}: {'Available' if available else 'Not Available'}")
        
        # Create test blueprint for full validation
        from validation_driven_orchestrator import SystemBlueprint
        
        test_blueprint = SystemBlueprint(
            description="Test blueprint for dependency validation",
            components=[
                {
                    "name": "test_service",
                    "type": "web_service",
                    "dependencies": [
                        {
                            "component_name": "test_db",
                            "dependency_type": "service_dependency",
                            "configuration": {
                                "host": "localhost",
                                "port": 5432
                            }
                        }
                    ]
                }
            ]
        )
        
        print("\n🚀 Testing full dependency validation...")
        
        try:
            await checker.validate_all_dependencies_configured(test_blueprint)
            print("✅ All dependencies validation passed")
        except ValidationDependencyError as e:
            print(f"❌ Dependency validation failed:\n{e}")
    
    # Run the test
    asyncio.run(main())