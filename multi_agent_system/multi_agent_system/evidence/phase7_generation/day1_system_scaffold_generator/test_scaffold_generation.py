#!/usr/bin/env python3
"""
Test Suite for SystemScaffoldGenerator
=====================================

Comprehensive tests for scaffold generation functionality including:
- Main.py generation
- Configuration generation  
- Connection mapping
- Template rendering
- Blueprint validation
"""

import unittest
import asyncio
import os
import sys
import tempfile
import logging
from pathlib import Path

# Add evidence paths for integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from blueprint_types import SystemBlueprint
from system_scaffold_generator import SystemScaffoldGenerator, ComponentInfo
from harness_template_engine import HarnessTemplateEngine
from connection_mapper import ConnectionMapper, StreamConnection


class TestSystemScaffoldGenerator(unittest.TestCase):
    """Test SystemScaffoldGenerator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = SystemScaffoldGenerator()
        self.sample_blueprint = SystemBlueprint(
            description="Test task management API system",
            components=[
                {
                    "name": "api_gateway",
                    "type": "api_gateway",
                    "configuration": {
                        "port": 8080,
                        "host": "0.0.0.0"
                    },
                    "bindings": [
                        {
                            "source": "requests",
                            "target": "task_controller.input"
                        }
                    ]
                },
                {
                    "name": "task_controller", 
                    "type": "task_controller",
                    "configuration": {
                        "max_concurrent_tasks": 10
                    },
                    "dependencies": [
                        {"component_name": "task_store"}
                    ],
                    "bindings": [
                        {
                            "source": "store_commands",
                            "target": "task_store.input"
                        }
                    ]
                },
                {
                    "name": "task_store",
                    "type": "task_store", 
                    "configuration": {
                        "storage_type": "memory"
                    }
                }
            ]
        )
    
    def test_extract_components(self):
        """Test component extraction from blueprint"""
        components = self.generator._extract_components(self.sample_blueprint)
        
        self.assertEqual(len(components), 3)
        
        # Check first component
        api_gateway = components[0]
        self.assertEqual(api_gateway.name, "api_gateway")
        self.assertEqual(api_gateway.class_name, "APIGateway")
        self.assertEqual(api_gateway.component_type, "api_gateway")
        
        # Check second component  
        task_controller = components[1]
        self.assertEqual(task_controller.name, "task_controller")
        self.assertEqual(task_controller.class_name, "TaskController")
        self.assertEqual(task_controller.dependencies, ["task_store"])
    
    def test_generate_component_imports(self):
        """Test component import generation"""
        components = self.generator._extract_components(self.sample_blueprint)
        imports = self.generator._generate_component_imports(components)
        
        expected_imports = [
            "from components.api_gateway import APIGateway",
            "from components.task_controller import TaskController", 
            "from components.task_store import TaskStore"
        ]
        
        self.assertEqual(imports, expected_imports)
    
    def test_generate_component_registration(self):
        """Test component registration code generation"""
        components = self.generator._extract_components(self.sample_blueprint)
        registration_code = self.generator._generate_component_registration(components)
        
        # Check that all components are included
        self.assertIn("api_gateway_component = APIGateway", registration_code)
        self.assertIn("task_controller_component = TaskController", registration_code)
        self.assertIn("task_store_component = TaskStore", registration_code)
        
        # Check registration calls
        self.assertIn("harness.register_component('api_gateway'", registration_code)
        self.assertIn("harness.register_component('task_controller'", registration_code)
        self.assertIn("harness.register_component('task_store'", registration_code)
    
    def test_generate_main_py(self):
        """Test complete main.py generation"""
        main_py_code = self.generator.generate_main_py(self.sample_blueprint)
        
        # Check essential elements are present
        self.assertIn("SystemExecutionHarness", main_py_code)
        self.assertIn("async def main():", main_py_code)
        self.assertIn("from components.api_gateway import APIGateway", main_py_code)
        self.assertIn("harness.register_component", main_py_code)
        self.assertIn("harness.connect", main_py_code)
        self.assertIn("await harness.run()", main_py_code)
    
    def test_generate_config_file(self):
        """Test configuration file generation"""
        config_code = self.generator.generate_config_file(self.sample_blueprint)
        
        # Check essential elements
        self.assertIn("SYSTEM_CONFIG", config_code)
        self.assertIn("def get_config()", config_code)
        self.assertIn("def get_component_config", config_code)
        self.assertIn("api_gateway", config_code)
        self.assertIn("task_controller", config_code)
        self.assertIn("task_store", config_code)
    
    def test_generate_complete_scaffold(self):
        """Test complete scaffold generation"""
        scaffold = self.generator.generate_complete_scaffold(self.sample_blueprint)
        
        # Check scaffold structure
        self.assertIsNotNone(scaffold.main_py_code)
        self.assertIsNotNone(scaffold.config_code)
        self.assertEqual(len(scaffold.components), 3)
        self.assertGreater(len(scaffold.connections), 0)
        self.assertGreater(len(scaffold.imports), 0)
        self.assertGreater(scaffold.generation_time, 0)
    
    def test_validate_blueprint_for_scaffold(self):
        """Test blueprint validation for scaffold generation"""
        # Valid blueprint
        is_valid, errors = self.generator.validate_blueprint_for_scaffold(self.sample_blueprint)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid blueprint - no components
        invalid_blueprint = SystemBlueprint(
            description="Invalid blueprint",
            components=[]
        )
        is_valid, errors = self.generator.validate_blueprint_for_scaffold(invalid_blueprint)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Invalid blueprint - missing component name
        invalid_blueprint2 = SystemBlueprint(
            description="Invalid blueprint 2",
            components=[
                {"type": "api_gateway"}  # Missing name
            ]
        )
        is_valid, errors = self.generator.validate_blueprint_for_scaffold(invalid_blueprint2)
        self.assertFalse(is_valid)
        self.assertIn("missing 'name' field", ' '.join(errors))


class TestHarnessTemplateEngine(unittest.TestCase):
    """Test HarnessTemplateEngine functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.template_engine = HarnessTemplateEngine()
    
    def test_render_main_template(self):
        """Test main template rendering"""
        imports = ["from components.test import TestComponent"]
        registration_code = "harness.register_component('test', TestComponent())"
        connection_code = "harness.connect('test.output', 'other.input')"
        config = {"test": "config"}
        
        rendered = self.template_engine.render_main_template(
            imports=imports,
            registration_code=registration_code,
            connection_code=connection_code,
            config=config
        )
        
        # Check essential elements
        self.assertIn("SystemExecutionHarness", rendered)
        self.assertIn("from components.test import TestComponent", rendered)
        self.assertIn("harness.register_component('test'", rendered)
        self.assertIn("harness.connect('test.output'", rendered)
        self.assertIn("async def main():", rendered)
    
    def test_render_component_template(self):
        """Test component template rendering"""
        rendered = self.template_engine.render_component_template(
            component_name="test_component",
            class_name="TestComponent", 
            component_type="test",
            config={"key": "value"}
        )
        
        self.assertIn("test_component", rendered)
        self.assertIn("TestComponent", rendered)
        self.assertIn("get_component_config", rendered)
    
    def test_render_dockerfile_template(self):
        """Test Dockerfile template rendering"""
        dockerfile = self.template_engine.render_dockerfile_template(
            system_name="test_system",
            requirements=["fastapi", "uvicorn"]
        )
        
        self.assertIn("test_system", dockerfile)
        self.assertIn("FROM python", dockerfile)
        self.assertIn("COPY requirements.txt", dockerfile)
        self.assertIn("CMD [\"python\", \"main.py\"]", dockerfile)
    
    def test_render_requirements_template(self):
        """Test requirements.txt template rendering"""
        requirements = self.template_engine.render_requirements_template(
            additional_requirements=["fastapi>=0.100.0"]
        )
        
        self.assertIn("anyio>=3.7.0", requirements)
        self.assertIn("fastapi>=0.100.0", requirements)
        
        # Check sorted order
        lines = requirements.split('\n')
        self.assertEqual(lines, sorted(lines))


class TestConnectionMapper(unittest.TestCase):
    """Test ConnectionMapper functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mapper = ConnectionMapper()
        self.blueprint = SystemBlueprint(
            description="Test system with connections",
            components=[
                {
                    "name": "api_gateway",
                    "type": "api_gateway",
                    "bindings": [
                        {
                            "source": "requests",
                            "target": "task_controller.input"
                        }
                    ]
                },
                {
                    "name": "task_controller",
                    "type": "task_controller", 
                    "dependencies": [{"component_name": "task_store"}],
                    "bindings": [
                        {
                            "source": "store_commands",
                            "target": "task_store.input"
                        }
                    ]
                },
                {
                    "name": "task_store",
                    "type": "task_store"
                }
            ]
        )
    
    def test_derive_connections(self):
        """Test connection derivation from blueprint"""
        connections = self.mapper.derive_connections(self.blueprint)
        
        self.assertGreater(len(connections), 0)
        
        # Check specific connections exist
        connection_pairs = [(conn.source, conn.target) for conn in connections]
        self.assertIn(("api_gateway.requests", "task_controller.input"), connection_pairs)
    
    def test_process_explicit_bindings(self):
        """Test explicit binding processing"""
        connections = self.mapper._process_explicit_bindings(self.blueprint)
        
        # Should have explicit bindings from blueprint
        self.assertGreater(len(connections), 0)
        
        # Check first connection
        first_conn = connections[0]
        self.assertEqual(first_conn.source, "api_gateway.requests")
        self.assertEqual(first_conn.target, "task_controller.input")
        self.assertEqual(first_conn.metadata['binding_type'], 'explicit')
    
    def test_generate_implicit_connections(self):
        """Test implicit connection generation"""
        connections = self.mapper._generate_implicit_connections(self.blueprint)
        
        # Should generate connections based on dependencies
        self.assertGreaterEqual(len(connections), 0)
        
        if connections:
            # Check connection properties
            conn = connections[0]
            self.assertIsInstance(conn, StreamConnection)
            self.assertIn('.', conn.source)
            self.assertIn('.', conn.target)
    
    def test_validate_connections(self):
        """Test connection validation"""
        # Create test connections with duplicates and invalid references
        test_connections = [
            StreamConnection(
                source="api_gateway.output",
                target="task_controller.input",
                buffer_size=100,
                connection_type="data_stream",
                metadata={}
            ),
            StreamConnection(
                source="api_gateway.output", 
                target="task_controller.input",  # Duplicate
                buffer_size=100,
                connection_type="data_stream",
                metadata={}
            ),
            StreamConnection(
                source="nonexistent.output",
                target="task_controller.input",  # Invalid source
                buffer_size=100,
                connection_type="data_stream",
                metadata={}
            )
        ]
        
        validated = self.mapper._validate_connections(test_connections, self.blueprint)
        
        # Should remove duplicates and invalid connections
        self.assertEqual(len(validated), 1)
        self.assertEqual(validated[0].source, "api_gateway.output")
    
    def test_get_connection_summary(self):
        """Test connection summary generation"""
        connections = self.mapper.derive_connections(self.blueprint)
        summary = self.mapper.get_connection_summary(connections)
        
        self.assertIn("total_connections", summary)
        self.assertIn("components_involved", summary)
        self.assertIn("connection_types", summary)
        self.assertIn("connection_details", summary)
        
        self.assertGreaterEqual(summary["total_connections"], 0)
    
    def test_visualize_connections(self):
        """Test connection visualization"""
        connections = self.mapper.derive_connections(self.blueprint)
        visualization = self.mapper.visualize_connections(connections)
        
        self.assertIn("Connection Graph:", visualization)
        if connections:
            self.assertIn("──→", visualization)


def run_scaffold_generation_tests():
    """Run all scaffold generation tests"""
    logging.basicConfig(level=logging.INFO)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSystemScaffoldGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestHarnessTemplateEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectionMapper))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_scaffold_generation_tests()
    if success:
        print("\n✅ All scaffold generation tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)