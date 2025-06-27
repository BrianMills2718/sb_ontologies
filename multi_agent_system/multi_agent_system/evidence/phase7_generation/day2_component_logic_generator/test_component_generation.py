#!/usr/bin/env python3
"""
Test Suite for HarnessComponentGenerator
========================================

Comprehensive tests for component logic generation functionality including:
- HarnessComponent class generation
- Stream I/O code generation
- Lifecycle method generation
- Business logic integration
"""

import unittest
import asyncio
import os
import sys
import logging

# Add evidence paths for integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from blueprint_types import ComponentLogic
from harness_component_generator import HarnessComponentGenerator, GeneratedComponent
from stream_io_templates import StreamIOTemplateEngine
from lifecycle_method_generator import LifecycleMethodGenerator


class TestHarnessComponentGenerator(unittest.TestCase):
    """Test HarnessComponentGenerator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = HarnessComponentGenerator()
        
        # Sample component logic
        self.sample_component_logic = ComponentLogic(
            business_methods=[
                {
                    'name': 'process_task',
                    'description': 'Process a task request',
                    'logic': 'return {"status": "processed", "data": data}'
                }
            ],
            processing_logic={
                'type': 'task_controller',
                'mode': 'async'
            },
            stream_handlers={
                'input': {'direction': 'input'},
                'output': {'direction': 'output'}
            }
        )
    
    def test_generate_component(self):
        """Test complete component generation"""
        result = self.generator.generate_component(
            component_name="test_component",
            component_logic=self.sample_component_logic,
            component_type="task_controller"
        )
        
        self.assertIsInstance(result, GeneratedComponent)
        self.assertEqual(result.component_name, "test_component")
        self.assertEqual(result.class_name, "Test_Component")
        self.assertIn("class Test_Component(HarnessComponent):", result.component_code)
        self.assertIn("async def process_task(self, data: Any)", result.component_code)
        self.assertGreater(len(result.imports), 0)
    
    def test_generate_component_from_blueprint(self):
        """Test component generation from blueprint definition"""
        component_def = {
            'name': 'api_gateway',
            'type': 'api_gateway',
            'configuration': {
                'port': 8080,
                'host': '0.0.0.0'
            }
        }
        
        result = self.generator.generate_component_from_blueprint(component_def)
        
        self.assertEqual(result.component_name, "api_gateway")
        self.assertEqual(result.class_name, "Api_Gateway")
        self.assertIn("api_gateway", result.component_code)
        self.assertIn("HarnessComponent", result.component_code)
    
    def test_get_class_name(self):
        """Test class name generation"""
        test_cases = [
            ("api_gateway", "Api_Gateway"),
            ("task-controller", "Task_Controller"),
            ("simple", "Simple"),
            ("multi_word_component", "Multi_Word_Component")
        ]
        
        for component_name, expected in test_cases:
            result = self.generator._get_class_name(component_name, "generic")
            self.assertEqual(result, expected)
    
    def test_generate_imports(self):
        """Test import generation for different component types"""
        # Test API gateway imports
        api_imports = self.generator._generate_imports("api_gateway")
        self.assertIn("from fastapi import FastAPI, HTTPException", api_imports)
        
        # Test task store imports
        store_imports = self.generator._generate_imports("task_store")
        self.assertIn("import redis.asyncio as redis", store_imports)
        
        # Test base imports
        base_imports = self.generator._generate_imports("generic")
        self.assertIn("from evidence.phase6_harness.day1_harness_component.harness_component import HarnessComponent", base_imports)
    
    def test_determine_stream_interfaces(self):
        """Test stream interface determination"""
        interfaces = self.generator._determine_stream_interfaces("task_controller", self.sample_component_logic)
        
        self.assertIn('input', interfaces)
        self.assertIn('output', interfaces)
        self.assertIn('input', interfaces['input'])
        self.assertIn('store_commands', interfaces['output'])
    
    def test_generate_business_logic_methods(self):
        """Test business logic method generation"""
        methods = self.generator._generate_business_logic_methods(self.sample_component_logic)
        
        self.assertGreater(len(methods), 0)
        method_code = methods[0]
        self.assertIn("async def process_task(self, data: Any)", method_code)
        self.assertIn("return {\"status\": \"processed\", \"data\": data}", method_code)
    
    def test_create_component_logic_from_blueprint(self):
        """Test component logic creation from blueprint"""
        component_def = {
            'name': 'test_component',
            'type': 'data_processor',
            'configuration': {}
        }
        
        logic = self.generator._create_component_logic_from_blueprint(component_def)
        
        self.assertIsInstance(logic, ComponentLogic)
        self.assertGreater(len(logic.business_methods), 0)
        self.assertEqual(logic.processing_logic['type'], 'data_processor')
    
    def test_get_default_business_methods(self):
        """Test default business method generation"""
        # Test API gateway methods
        api_methods = self.generator._get_default_business_methods("api_gateway")
        self.assertGreater(len(api_methods), 0)
        self.assertEqual(api_methods[0]['name'], 'handle_request')
        
        # Test task controller methods
        controller_methods = self.generator._get_default_business_methods("task_controller")
        self.assertGreater(len(controller_methods), 0)
        self.assertEqual(controller_methods[0]['name'], 'process_task_request')


class TestStreamIOTemplateEngine(unittest.TestCase):
    """Test StreamIOTemplateEngine functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.template_engine = StreamIOTemplateEngine()
    
    def test_generate_stream_receive_code_single(self):
        """Test single stream receive code generation"""
        code = self.template_engine.generate_stream_receive_code(['input'])
        
        self.assertIn("receive_message('input'", code)
        self.assertIn("process_message", code)
        self.assertIn("send_result", code)
    
    def test_generate_stream_receive_code_multiple(self):
        """Test multiple stream receive code generation"""
        code = self.template_engine.generate_stream_receive_code(['input1', 'input2'])
        
        self.assertIn("input1", code)
        self.assertIn("input2", code)
        self.assertIn("Poll multiple input streams", code)
    
    def test_generate_stream_receive_code_empty(self):
        """Test empty stream list handling"""
        code = self.template_engine.generate_stream_receive_code([])
        
        self.assertIn("No input streams configured", code)
        self.assertIn("asyncio.sleep", code)
    
    def test_generate_stream_send_code(self):
        """Test stream send code generation"""
        code = self.template_engine.generate_stream_send_code(['output1', 'output2'])
        
        self.assertIn("send_message('output1'", code)
        self.assertIn("send_message('output2'", code)
        self.assertIn("Send to output1 stream", code)
        self.assertIn("Send to output2 stream", code)
    
    def test_generate_stream_helper_methods(self):
        """Test stream helper method generation"""
        stream_interfaces = {
            'input': ['input1', 'input2'],
            'output': ['output1', 'output2']
        }
        
        helpers = self.template_engine.generate_stream_helper_methods(stream_interfaces)
        
        self.assertGreater(len(helpers), 0)
        
        # Check for specific helper methods
        helper_code = '\n'.join(helpers)
        self.assertIn("handle_stream_error", helper_code)
        self.assertIn("get_stream_status", helper_code)
        self.assertIn("send_to_multiple_streams", helper_code)
        self.assertIn("check_stream_connectivity", helper_code)
    
    def test_generate_stream_multiplexer_code(self):
        """Test stream multiplexer code generation"""
        code = self.template_engine.generate_stream_multiplexer_code(['stream1', 'stream2', 'stream3'])
        
        self.assertIn("handle_stream1_stream", code)
        self.assertIn("handle_stream2_stream", code)
        self.assertIn("anyio.create_task_group", code)
        self.assertIn("tg.start_soon", code)
    
    def test_generate_backpressure_handler(self):
        """Test backpressure handler generation"""
        code = self.template_engine.generate_stream_backpressure_handler(['output1', 'output2'])
        
        self.assertIn("handle_backpressure", code)
        self.assertIn("Backpressure detected", code)
        self.assertIn("timeout=0.5", code)


class TestLifecycleMethodGenerator(unittest.TestCase):
    """Test LifecycleMethodGenerator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = LifecycleMethodGenerator()
        
        self.sample_logic = ComponentLogic(
            business_methods=[],
            processing_logic={'type': 'task_controller'},
            stream_handlers={}
        )
        
        self.stream_interfaces = {
            'input': ['input'],
            'output': ['output']
        }
    
    def test_generate_setup_method(self):
        """Test setup method generation"""
        setup_code = self.generator.generate_setup_method(self.sample_logic, self.stream_interfaces)
        
        self.assertIn("_initialize_component_resources", setup_code)
        self.assertIn("stream_errors", setup_code)
        self.assertIn("resource_handles", setup_code)
        self.assertIn("expected_input_streams", setup_code)
    
    def test_generate_cleanup_method(self):
        """Test cleanup method generation"""
        cleanup_code = self.generator.generate_cleanup_method(self.sample_logic)
        
        self.assertIn("_cleanup_component_resources", cleanup_code)
        self.assertIn("resource_handles", cleanup_code)
        self.assertIn("close", cleanup_code)
    
    def test_generate_api_gateway_setup(self):
        """Test API gateway specific setup"""
        setup_code = self.generator._generate_api_gateway_setup()
        
        self.assertIn("FastAPI", setup_code)
        self.assertIn("CORSMiddleware", setup_code)
        self.assertIn("server_config", setup_code)
    
    def test_generate_task_store_setup(self):
        """Test task store specific setup"""
        setup_code = self.generator._generate_task_store_setup()
        
        self.assertIn("storage_type", setup_code)
        self.assertIn("redis_client", setup_code)
        self.assertIn("memory_store", setup_code)
        self.assertIn("storage_metrics", setup_code)
    
    def test_generate_health_check_method(self):
        """Test health check method generation"""
        health_code = self.generator.generate_health_check_method("task_controller", self.stream_interfaces)
        
        self.assertIn("health_check", health_code)
        self.assertIn("component_health", health_code)
        self.assertIn("task_stats", health_code)
        self.assertIn("active_tasks_count", health_code)


def run_component_generation_tests():
    """Run all component generation tests"""
    logging.basicConfig(level=logging.INFO)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHarnessComponentGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestStreamIOTemplateEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestLifecycleMethodGenerator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_component_generation_tests()
    if success:
        print("\n✅ All component generation tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)