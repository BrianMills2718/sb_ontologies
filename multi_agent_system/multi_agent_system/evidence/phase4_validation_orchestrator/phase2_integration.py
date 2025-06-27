#!/usr/bin/env python3
"""
Phase 2 Component Library Integration for ValidationDrivenOrchestrator
====================================================================

Integrates ValidationDrivenOrchestrator with Phase 2 enhanced component library
including component registry, schema framework, and enhanced component classes.

This integration provides:
- Component registry integration for component validation
- Schema framework integration for schema validation
- Enhanced component class integration
- Component lifecycle management
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Add Phase 2 component library to path
phase2_path = Path(__file__).parent.parent / 'phase2_component_library'
sys.path.insert(0, str(phase2_path))


class Phase2ComponentIntegrator:
    """
    Integration layer for Phase 2 enhanced component library.
    
    This class provides seamless integration between the ValidationDrivenOrchestrator
    and the Phase 2 component library systems including component registry,
    schema framework, and enhanced component classes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("Phase2ComponentIntegrator")
        
        # Integration status
        self.integration_active = False
        self.component_registry = None
        self.schema_framework = None
        self.enhanced_components_available = False
        
        # Initialize Phase 2 integration
        self._initialize_phase2_integration()
        
        self.logger.info("✅ Phase2ComponentIntegrator initialized")
    
    def _initialize_phase2_integration(self):
        """Initialize integration with Phase 2 component library"""
        try:
            # Import Phase 2 component registry
            from component_registry import ComponentRegistry, component_registry
            self.component_registry = component_registry
            
            # Import Phase 2 schema framework
            from schema_framework import SchemaFramework, schema_framework
            self.schema_framework = schema_framework
            
            # Import enhanced component classes
            from day1_core_component_classes.enhanced_base import (
                EnhancedComponentBase, EnhancedSource, EnhancedTransformer, EnhancedSink
            )
            self.enhanced_base_class = EnhancedComponentBase
            self.enhanced_source_class = EnhancedSource
            self.enhanced_transformer_class = EnhancedTransformer
            self.enhanced_sink_class = EnhancedSink
            
            self.enhanced_components_available = True
            self.integration_active = True
            
            # Register V5.0 service types with actual Phase 2 registry
            self._register_v5_service_types()
            
            self.logger.info("✅ Phase 2 component library integration successful")
            
        except ImportError as e:
            self.logger.error(f"❌ Failed to initialize Phase 2 integration: {e}")
            self.logger.warning("⚠️  Creating mock implementations for testing")
            self._create_mock_implementations()
    
    def _create_mock_implementations(self):
        """Create mock implementations when Phase 2 components not available"""
        
        class MockComponentRegistry:
            def __init__(self):
                # Register V5.0 service component types that are commonly used
                self._registered_types = {
                    'web_service', 'database', 'authentication_service', 'api_gateway',
                    'load_balancer', 'message_queue', 'cache_service', 'file_storage',
                    'monitoring_service', 'data_processor', 'Source', 'Transformer', 'Sink'
                }
            
            def list_component_types(self):
                return list(self._registered_types)
            
            def is_component_registered(self, component_type):
                return component_type in self._registered_types
            
            def create_component(self, component_type, name, config):
                if component_type not in self._registered_types:
                    raise Exception(f"Component type '{component_type}' not registered")
                return {'name': name, 'type': component_type, 'config': config}
            
            def unregister_component(self, name):
                return True
            
            def validate_all_components(self):
                return {'mock_component': True}
            
            def register_component_class(self, component_type, component_class):
                self._registered_types.add(component_type)
        
        class MockSchemaFramework:
            def validate_component_schema(self, component):
                return {'valid': True, 'component_name': getattr(component, 'name', 'mock')}
            
            def validate_component_interfaces(self, component):
                return {'valid': True, 'component_name': getattr(component, 'name', 'mock')}
            
            def validate_component_dependencies(self, component):
                return {'valid': True, 'component_name': getattr(component, 'name', 'mock')}
        
        self.component_registry = MockComponentRegistry()
        # Ensure all V5.0 service types are registered
        self._register_v5_service_types()
        self.schema_framework = MockSchemaFramework()
        self.enhanced_components_available = False
        self.integration_active = True  # Mock integration is active
    
    def _register_v5_service_types(self):
        """Register V5.0 service component types with the component registry"""
        if not self.component_registry:
            return
        
        # V5.0 service component types that need to be supported
        v5_service_types = [
            'web_service', 'database', 'authentication_service', 'api_gateway',
            'load_balancer', 'message_queue', 'cache_service', 'file_storage', 
            'monitoring_service', 'data_processor'
        ]
        
        # Register each service type if component registry supports it
        if hasattr(self.component_registry, 'register_component_class'):
            for service_type in v5_service_types:
                try:
                    # Create a basic enhanced component class for this service type
                    if self.enhanced_components_available and hasattr(self, 'enhanced_base_class'):
                        # Use actual enhanced base class - map service types to component types
                        component_type_mapping = {
                            'web_service': 'Transformer',  # Web services transform requests to responses
                            'database': 'Sink',            # Databases store data (sink)
                            'authentication_service': 'Transformer',  # Auth services transform credentials to tokens
                            'api_gateway': 'Transformer', 
                            'load_balancer': 'Transformer',
                            'message_queue': 'Transformer',
                            'cache_service': 'Transformer',
                            'file_storage': 'Sink',
                            'monitoring_service': 'Sink',
                            'data_processor': 'Transformer'
                        }
                        
                        base_type = component_type_mapping.get(service_type, 'Transformer')
                        
                        # Get the appropriate enhanced base class
                        if base_type == 'Source':
                            base_class = self.enhanced_source_class
                        elif base_type == 'Sink':
                            base_class = self.enhanced_sink_class
                        else:
                            base_class = self.enhanced_transformer_class
                        
                        class ServiceComponent(base_class):
                            def __init__(self, name, config):
                                # Override the component_type to be the service type
                                config = config.copy()
                                config['type'] = base_type  # Use the base component type for Phase 2
                                super().__init__(name, config)
                                self.service_type = service_type  # Keep track of original service type
                            
                            def get_required_config_fields(self):
                                return ['name', 'type']
                            
                            def get_required_dependencies(self):
                                return []
                        
                        # Register using the base component type
                        self.component_registry.register_component_class(base_type, ServiceComponent)
                    else:
                        # For mock mode, just register the type
                        if hasattr(self.component_registry, 'register_component_class'):
                            self.component_registry.register_component_class(service_type, dict)
                            
                except Exception as e:
                    self.logger.debug(f"Could not register service type {service_type}: {e}")
        
        self.logger.info(f"✅ Registered V5.0 service component types with Phase 2 registry")
    
    async def integrate_with_component_library(self, blueprint: 'SystemBlueprint') -> Dict[str, Any]:
        """
        Integrate with Phase 2 component library for validation.
        
        This method sets up integration with Phase 2 components and validates
        that all blueprint components are compatible with the component library.
        
        Args:
            blueprint: SystemBlueprint to integrate with Phase 2 systems
            
        Returns:
            Dict containing integration results and status
        """
        self.logger.info("🔗 Integrating with Phase 2 component library")
        
        if not self.integration_active:
            raise RuntimeError("Phase 2 integration not available")
        
        integration_results = {
            'registry_validation': {},
            'schema_validation': {},
            'component_compatibility': {},
            'integration_successful': True,
            'issues': []
        }
        
        try:
            # Validate all components with component registry
            registry_results = await self._validate_with_component_registry(blueprint.components)
            integration_results['registry_validation'] = registry_results
            
            # Validate all components with schema framework
            schema_results = await self._validate_with_schema_framework(blueprint.components)
            integration_results['schema_validation'] = schema_results
            
            # Check component compatibility
            compatibility_results = await self._check_component_compatibility(blueprint.components)
            integration_results['component_compatibility'] = compatibility_results
            
            # Aggregate results
            if not registry_results['all_valid'] or not schema_results['all_valid'] or not compatibility_results['all_compatible']:
                integration_results['integration_successful'] = False
                integration_results['issues'].extend(registry_results.get('issues', []))
                integration_results['issues'].extend(schema_results.get('issues', []))
                integration_results['issues'].extend(compatibility_results.get('issues', []))
            
            if integration_results['integration_successful']:
                self.logger.info("✅ Phase 2 component library integration successful")
            else:
                self.logger.warning(f"⚠️  Phase 2 integration issues found: {len(integration_results['issues'])}")
            
            return integration_results
            
        except Exception as e:
            self.logger.error(f"❌ Phase 2 integration error: {e}")
            integration_results['integration_successful'] = False
            integration_results['issues'].append(f"Integration error: {e}")
            return integration_results
    
    async def _validate_with_component_registry(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate components with Phase 2 component registry"""
        results = {
            'all_valid': True,
            'validated_components': [],
            'issues': []
        }
        
        if not self.component_registry:
            results['all_valid'] = False
            results['issues'].append("Component registry not available")
            return results
        
        # Get available component types
        available_types = self.component_registry.list_component_types()
        
        for component in components:
            component_name = component.get('name', 'unnamed')
            component_type = component.get('type', 'unknown')
            component_config = component.get('configuration', {})
            
            validation_result = {
                'component_name': component_name,
                'type_registered': False,
                'creation_successful': False,
                'issues': []
            }
            
            # Check if component type is registered
            type_registered = False
            
            # Map service types to Phase 2 component types for availability check
            component_type_mapping = {
                'web_service': 'Transformer',
                'database': 'Sink', 
                'authentication_service': 'Transformer',
                'api_gateway': 'Transformer',
                'load_balancer': 'Transformer',
                'message_queue': 'Transformer',
                'cache_service': 'Transformer',
                'file_storage': 'Sink',
                'monitoring_service': 'Sink',
                'data_processor': 'Transformer'
            }
            
            # Check for service type in available types or use mapped type
            if component_type in available_types:
                type_registered = True
            elif hasattr(self.component_registry, 'is_component_registered'):
                # Use the method if available (mock registry)
                type_registered = self.component_registry.is_component_registered(component_type)
            else:
                # Check if mapped Phase 2 type is available
                phase2_type = component_type_mapping.get(component_type)
                if phase2_type and phase2_type in available_types:
                    type_registered = True
            
            validation_result['type_registered'] = type_registered
            
            if type_registered:
                # Test component creation
                try:
                    # Map service types to Phase 2 component types
                    component_type_mapping = {
                        'web_service': 'Transformer',
                        'database': 'Sink', 
                        'authentication_service': 'Transformer',
                        'api_gateway': 'Transformer',
                        'load_balancer': 'Transformer',
                        'message_queue': 'Transformer',
                        'cache_service': 'Transformer',
                        'file_storage': 'Sink',
                        'monitoring_service': 'Sink',
                        'data_processor': 'Transformer'
                    }
                    
                    # Get the Phase 2 component type
                    phase2_component_type = component_type_mapping.get(component_type, 'Transformer')
                    
                    # Ensure config has required fields for Phase 2 components
                    test_config = component_config.copy()
                    test_config['name'] = f"test_{component_name}"
                    test_config['type'] = phase2_component_type  # Use mapped type
                    
                    test_component = self.component_registry.create_component(
                        component_type=phase2_component_type,
                        name=f"test_{component_name}",
                        config=test_config
                    )
                    
                    validation_result['creation_successful'] = True
                    
                    # Clean up test component
                    self.component_registry.unregister_component(f"test_{component_name}")
                    
                except Exception as e:
                    validation_result['issues'].append(f"Component creation failed: {e}")
                    results['all_valid'] = False
                    results['issues'].append(f"Component {component_name} creation failed: {e}")
            else:
                validation_result['issues'].append(f"Component type '{component_type}' not registered")
                results['all_valid'] = False
                results['issues'].append(f"Component type '{component_type}' not registered in Phase 2 registry")
            
            results['validated_components'].append(validation_result)
        
        return results
    
    async def _validate_with_schema_framework(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate components with Phase 2 schema framework"""
        results = {
            'all_valid': True,
            'validated_components': [],
            'issues': []
        }
        
        if not self.schema_framework:
            results['all_valid'] = False
            results['issues'].append("Schema framework not available")
            return results
        
        for component in components:
            component_name = component.get('name', 'unnamed')
            
            # Create mock component object for schema validation
            class MockComponent:
                def __init__(self, config):
                    self.config = config
                    self.name = config.get('name', 'mock')
            
            mock_component = MockComponent(component)
            
            validation_result = {
                'component_name': component_name,
                'schema_valid': False,
                'interface_valid': False,
                'dependency_valid': False,
                'issues': []
            }
            
            try:
                # Validate component schema
                schema_result = self.schema_framework.validate_component_schema(mock_component)
                validation_result['schema_valid'] = schema_result.get('valid', False)
                
                if not validation_result['schema_valid']:
                    error_msg = schema_result.get('error', 'Unknown schema validation error')
                    validation_result['issues'].append(f"Schema validation failed: {error_msg}")
                    results['issues'].append(f"Component {component_name} schema validation failed: {error_msg}")
                
                # Validate component interfaces
                interface_result = self.schema_framework.validate_component_interfaces(mock_component)
                validation_result['interface_valid'] = interface_result.get('valid', False)
                
                if not validation_result['interface_valid']:
                    interface_errors = interface_result.get('interface_validation', {}).get('interface_errors', [])
                    for error in interface_errors:
                        validation_result['issues'].append(f"Interface validation failed: {error}")
                        results['issues'].append(f"Component {component_name} interface validation failed: {error}")
                
                # Validate component dependencies
                dependency_result = self.schema_framework.validate_component_dependencies(mock_component)
                validation_result['dependency_valid'] = dependency_result.get('valid', False)
                
                if not validation_result['dependency_valid']:
                    error_msg = dependency_result.get('error', 'Unknown dependency validation error')
                    validation_result['issues'].append(f"Dependency validation failed: {error_msg}")
                    results['issues'].append(f"Component {component_name} dependency validation failed: {error_msg}")
                
                # Overall component validation
                component_valid = (validation_result['schema_valid'] and 
                                 validation_result['interface_valid'] and 
                                 validation_result['dependency_valid'])
                
                if not component_valid:
                    results['all_valid'] = False
                
            except Exception as e:
                validation_result['issues'].append(f"Schema framework validation error: {e}")
                results['all_valid'] = False
                results['issues'].append(f"Component {component_name} schema framework error: {e}")
            
            results['validated_components'].append(validation_result)
        
        return results
    
    async def _check_component_compatibility(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check component compatibility with Phase 2 enhanced classes"""
        results = {
            'all_compatible': True,
            'compatibility_checks': [],
            'issues': []
        }
        
        for component in components:
            component_name = component.get('name', 'unnamed')
            component_type = component.get('type', 'unknown')
            
            compatibility_check = {
                'component_name': component_name,
                'type_supported': False,
                'enhanced_class_available': False,
                'issues': []
            }
            
            # Check if component type is supported by enhanced classes
            supported_types = ['Source', 'Transformer', 'Sink', 'web_service', 'database', 'authentication_service']
            
            if component_type in supported_types or any(comp_type in component_type for comp_type in ['service', 'source', 'sink']):
                compatibility_check['type_supported'] = True
            else:
                compatibility_check['issues'].append(f"Component type '{component_type}' may not be fully supported")
                results['issues'].append(f"Component {component_name} type '{component_type}' compatibility uncertain")
            
            # Check enhanced class availability
            if self.enhanced_components_available:
                compatibility_check['enhanced_class_available'] = True
            else:
                compatibility_check['issues'].append("Enhanced component classes not available")
                results['issues'].append(f"Component {component_name} cannot use enhanced classes")
            
            # Overall compatibility
            component_compatible = (compatibility_check['type_supported'] and 
                                  compatibility_check['enhanced_class_available'])
            
            if not component_compatible:
                results['all_compatible'] = False
            
            results['compatibility_checks'].append(compatibility_check)
        
        return results
    
    async def validate_component_with_phase2(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate single component with Phase 2 systems.
        
        This method provides detailed validation of a single component
        using both the component registry and schema framework.
        
        Args:
            component: Component dictionary to validate
            
        Returns:
            Dict containing detailed validation results
        """
        component_name = component.get('name', 'unnamed')
        self.logger.debug(f"🔍 Validating component '{component_name}' with Phase 2 systems")
        
        validation_result = {
            'component_name': component_name,
            'overall_valid': True,
            'registry_validation': {},
            'schema_validation': {},
            'issues': []
        }
        
        try:
            # Registry validation
            registry_results = await self._validate_with_component_registry([component])
            validation_result['registry_validation'] = registry_results
            
            if not registry_results['all_valid']:
                validation_result['overall_valid'] = False
                validation_result['issues'].extend(registry_results['issues'])
            
            # Schema validation
            schema_results = await self._validate_with_schema_framework([component])
            validation_result['schema_validation'] = schema_results
            
            if not schema_results['all_valid']:
                validation_result['overall_valid'] = False
                validation_result['issues'].extend(schema_results['issues'])
            
            return validation_result
            
        except Exception as e:
            validation_result['overall_valid'] = False
            validation_result['issues'].append(f"Phase 2 validation error: {e}")
            return validation_result
    
    async def get_phase2_component_types(self) -> List[str]:
        """Get list of available component types from Phase 2 registry"""
        if self.component_registry:
            return self.component_registry.list_component_types()
        else:
            return []
    
    async def create_enhanced_component(self, component_type: str, name: str, config: Dict[str, Any]) -> Optional[Any]:
        """
        Create enhanced component instance using Phase 2 classes.
        
        This method creates an actual enhanced component instance
        that can be used for advanced validation and processing.
        
        Args:
            component_type: Type of component to create
            name: Name of the component
            config: Component configuration
            
        Returns:
            Enhanced component instance or None if creation fails
        """
        if not self.component_registry:
            self.logger.warning("⚠️  Component registry not available for enhanced component creation")
            return None
        
        try:
            enhanced_component = self.component_registry.create_component(
                component_type=component_type,
                name=name,
                config=config
            )
            
            self.logger.debug(f"✅ Created enhanced component: {name} ({component_type})")
            return enhanced_component
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create enhanced component {name}: {e}")
            return None
    
    async def get_integration_summary(self) -> Dict[str, Any]:
        """Get comprehensive integration summary"""
        return {
            'integration_active': self.integration_active,
            'component_registry_available': self.component_registry is not None,
            'schema_framework_available': self.schema_framework is not None,
            'enhanced_components_available': self.enhanced_components_available,
            'available_component_types': await self.get_phase2_component_types(),
            'integration_capabilities': {
                'component_validation': True,
                'schema_validation': True,
                'enhanced_component_creation': self.enhanced_components_available,
                'lifecycle_management': True
            }
        }
    
    def get_integrator_status(self) -> Dict[str, Any]:
        """Get current integrator status"""
        return {
            'integrator_initialized': True,
            'phase2_path_exists': (Path(__file__).parent.parent / 'phase2_component_library').exists(),
            'integration_active': self.integration_active,
            'components_available': {
                'component_registry': self.component_registry is not None,
                'schema_framework': self.schema_framework is not None,
                'enhanced_base_class': self.enhanced_components_available
            },
            'mock_mode': not self.enhanced_components_available
        }


# Convenience functions for external use
async def integrate_with_phase2(blueprint: 'SystemBlueprint') -> Dict[str, Any]:
    """Integrate blueprint with Phase 2 component library"""
    integrator = Phase2ComponentIntegrator()
    return await integrator.integrate_with_component_library(blueprint)


async def validate_component_phase2(component: Dict[str, Any]) -> Dict[str, Any]:
    """Validate single component with Phase 2 systems"""
    integrator = Phase2ComponentIntegrator()
    return await integrator.validate_component_with_phase2(component)


async def get_phase2_status() -> Dict[str, Any]:
    """Get Phase 2 integration status"""
    integrator = Phase2ComponentIntegrator()
    return integrator.get_integrator_status()


# Main execution for testing
if __name__ == "__main__":
    async def main():
        """Test Phase2ComponentIntegrator"""
        
        # Create integrator
        integrator = Phase2ComponentIntegrator()
        
        # Display integrator status
        status = integrator.get_integrator_status()
        print("🔗 Phase 2 Component Integrator Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # Create test blueprint
        class MockBlueprint:
            def __init__(self, components):
                self.components = components
        
        test_components = [
            {
                "name": "web_service",
                "type": "web_service",
                "configuration": {
                    "resource_requirements": {
                        "memory_mb": 1024,
                        "cpu_cores": 2,
                        "disk_gb": 20
                    },
                    "ports": [
                        {"port": 8080, "protocol": "http"}
                    ]
                },
                "dependencies": [
                    {"component_name": "database", "dependency_type": "data_dependency"}
                ]
            },
            {
                "name": "database",
                "type": "database",
                "configuration": {
                    "resource_requirements": {
                        "memory_mb": 2048,
                        "cpu_cores": 2,
                        "disk_gb": 100
                    }
                }
            }
        ]
        
        test_blueprint = MockBlueprint(test_components)
        
        print(f"\n🚀 Testing Phase 2 integration with {len(test_components)} components...")
        
        # Test integration
        integration_result = await integrator.integrate_with_component_library(test_blueprint)
        
        print(f"\n📊 Integration Results:")
        print(f"  Integration successful: {'✅ YES' if integration_result['integration_successful'] else '❌ NO'}")
        print(f"  Registry validation: {integration_result['registry_validation'].get('all_valid', 'unknown')}")
        print(f"  Schema validation: {integration_result['schema_validation'].get('all_valid', 'unknown')}")
        print(f"  Component compatibility: {integration_result['component_compatibility'].get('all_compatible', 'unknown')}")
        
        if integration_result['issues']:
            print(f"\n⚠️  Integration Issues ({len(integration_result['issues'])}):")
            for issue in integration_result['issues']:
                print(f"    - {issue}")
        
        # Test individual component validation
        print(f"\n🔍 Testing individual component validation...")
        for component in test_components:
            component_name = component.get('name', 'unknown')
            validation_result = await integrator.validate_component_with_phase2(component)
            
            print(f"  {component_name}: {'✅ VALID' if validation_result['overall_valid'] else '❌ INVALID'}")
            if validation_result['issues']:
                for issue in validation_result['issues']:
                    print(f"    - {issue}")
        
        # Test integration summary
        print(f"\n📋 Integration Summary:")
        summary = await integrator.get_integration_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
    
    # Run the test
    asyncio.run(main())