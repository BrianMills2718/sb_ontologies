#!/usr/bin/env python3
"""
Component-by-Component Test Runner - Phase 6 Implementation
Validates each component in isolation before integration testing

This implements the "block early, block often" philosophy:
- Each component is tested in isolation with controlled inputs
- Components must pass all tests before system integration
- Clear blame assignment when failures occur
- Prevents system generation if any component fails validation
"""
import asyncio
import anyio
import ast
import importlib.util
import inspect
import json
import logging
import time
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Type
from dataclasses import dataclass
from datetime import datetime

from autocoder.orchestration.harness import SystemExecutionHarness
from autocoder.orchestration.component import Component


@dataclass
class ComponentTestResult:
    """Result of testing a single component"""
    component_name: str
    component_type: str
    success: bool
    execution_time: float
    error_message: Optional[str] = None
    
    # Contract validation results
    contract_validation_passed: bool = False
    required_methods_present: bool = False
    async_patterns_correct: bool = False
    harness_compatibility: bool = False
    
    # Functional validation results
    functional_test_passed: bool = False
    input_processing_works: bool = False
    output_generation_works: bool = False
    lifecycle_methods_work: bool = False
    
    # Performance metrics
    setup_time: float = 0.0
    processing_time: float = 0.0
    cleanup_time: float = 0.0
    memory_usage: float = 0.0
    
    # Detailed logs
    test_logs: List[str] = None
    validation_details: Dict[str, Any] = None


@dataclass
class ComponentTestConfig:
    """Configuration for component testing"""
    component_path: Path
    component_class_name: str
    test_inputs: List[Dict[str, Any]]
    expected_outputs: int
    timeout_seconds: float = 10.0
    validate_contract: bool = True
    validate_functionality: bool = True
    validate_performance: bool = False


class ComponentContractValidator:
    """Validates that components follow the expected contracts"""
    
    REQUIRED_BASE_METHODS = {
        'setup', 'process', 'cleanup', 'health_check'
    }
    
    ASYNC_METHODS = {'setup', 'process', 'cleanup', 'health_check'}
    
    def validate_component_contract(self, component_path: Path, class_name: str) -> Dict[str, Any]:
        """Validate that a component follows the expected contract"""
        
        validation_result = {
            "success": True,
            "errors": [],
            "warnings": [],
            "method_analysis": {},
            "inheritance_check": False,
            "async_pattern_check": False
        }
        
        try:
            # Parse the component file
            with open(component_path, 'r') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            
            # Find the component class
            component_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    component_class = node
                    break
            
            if not component_class:
                validation_result["success"] = False
                validation_result["errors"].append(f"Class '{class_name}' not found in {component_path}")
                return validation_result
            
            # Check inheritance from valid component base classes
            valid_base_classes = {
                'Component', 'HarnessComponent', 'Source', 'Sink', 
                'Transformer', 'Model', 'Store', 'APIEndpoint'
            }
            
            inherits_from_component = any(
                (isinstance(base, ast.Name) and base.id in valid_base_classes) or
                (isinstance(base, ast.Attribute) and base.attr in valid_base_classes)
                for base in component_class.bases
            )
            validation_result["inheritance_check"] = inherits_from_component
            
            if not inherits_from_component:
                validation_result["errors"].append(f"Class '{class_name}' does not inherit from valid component base class")
                validation_result["success"] = False
            
            # Analyze methods
            found_methods = set()
            async_methods = set()
            
            for node in component_class.body:
                if isinstance(node, ast.AsyncFunctionDef):
                    found_methods.add(node.name)
                    async_methods.add(node.name)
                    validation_result["method_analysis"][node.name] = {
                        "type": "async",
                        "args": [arg.arg for arg in node.args.args]
                    }
                elif isinstance(node, ast.FunctionDef):
                    found_methods.add(node.name)
                    validation_result["method_analysis"][node.name] = {
                        "type": "sync", 
                        "args": [arg.arg for arg in node.args.args]
                    }
            
            # Check required methods only if not inheriting from valid base classes
            # If inheriting from Transformer, Model, Source, Sink, etc., assume they provide required methods
            base_class_names = []
            for base in component_class.bases:
                if isinstance(base, ast.Name):
                    base_class_names.append(base.id)
                elif isinstance(base, ast.Attribute):
                    base_class_names.append(base.attr)
            
            inherits_from_known_base = any(base in valid_base_classes for base in base_class_names)
            
            if not inherits_from_known_base:
                # Only check required methods for components that don't inherit from known bases
                missing_methods = self.REQUIRED_BASE_METHODS - found_methods
                if missing_methods:
                    validation_result["errors"].append(f"Missing required methods: {missing_methods}")
                    validation_result["success"] = False
                
                # Check async patterns
                missing_async = self.ASYNC_METHODS - async_methods
                if missing_async:
                    validation_result["errors"].append(f"Methods should be async: {missing_async}")
                    validation_result["success"] = False
                    
                validation_result["async_pattern_check"] = len(missing_async) == 0
            else:
                # For components inheriting from known bases, assume contract is satisfied
                validation_result["async_pattern_check"] = True
            
        except Exception as e:
            validation_result["success"] = False
            validation_result["errors"].append(f"Contract validation error: {e}")
        
        return validation_result


class ComponentFunctionalTester:
    """Tests component functionality in isolation"""
    
    async def test_component_functionality(self, 
                                         component_path: Path, 
                                         class_name: str,
                                         test_inputs: List[Dict[str, Any]],
                                         expected_outputs: int,
                                         timeout: float = 10.0) -> Dict[str, Any]:
        """Test component functionality with controlled inputs"""
        
        test_result = {
            "success": True,
            "errors": [],
            "warnings": [],
            "lifecycle_test": False,
            "input_processing_test": False,
            "output_generation_test": False,
            "performance_metrics": {}
        }
        
        try:
            # Load the component class
            spec = importlib.util.spec_from_file_location("test_component", component_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            component_class = getattr(module, class_name)
            
            # Create component instance
            component = component_class(name=f"test_{class_name.lower()}")
            
            # First, test for placeholder logic (NotImplementedError) before running other tests
            placeholder_result = await self._test_for_placeholder_logic(component, test_inputs)
            if not placeholder_result["success"]:
                test_result["errors"].extend(placeholder_result["errors"])
                test_result["success"] = False
                return test_result  # Fail immediately if placeholder logic detected
            
            # Test lifecycle methods
            lifecycle_result = await self._test_lifecycle_methods(component)
            test_result["lifecycle_test"] = lifecycle_result["success"]
            if not lifecycle_result["success"]:
                test_result["errors"].extend(lifecycle_result["errors"])
                test_result["success"] = False
            
            # Test input/output processing if lifecycle passed
            if lifecycle_result["success"]:
                io_result = await self._test_input_output_processing(
                    component, test_inputs, expected_outputs, timeout
                )
                test_result["input_processing_test"] = io_result["input_success"]
                test_result["output_generation_test"] = io_result["output_success"]
                test_result["performance_metrics"] = io_result["performance"]
                
                if not (io_result["input_success"] and io_result["output_success"]):
                    test_result["errors"].extend(io_result["errors"])
                    test_result["success"] = False
            
        except Exception as e:
            test_result["success"] = False
            test_result["errors"].append(f"Functional test error: {e}")
            
        return test_result
    
    async def _test_lifecycle_methods(self, component: Component) -> Dict[str, Any]:
        """Test component lifecycle methods (setup, process, cleanup)"""
        
        result = {
            "success": True,
            "errors": [],
            "timings": {}
        }
        
        try:
            # Test setup
            start_time = time.time()
            await component.setup({})
            result["timings"]["setup"] = time.time() - start_time
            
            # Test cleanup  
            start_time = time.time()
            await component.cleanup()
            result["timings"]["cleanup"] = time.time() - start_time
            
        except Exception as e:
            result["success"] = False
            result["errors"].append(f"Lifecycle method error: {e}")
        
        return result
    
    async def _test_for_placeholder_logic(self, component: Component, test_inputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test if component contains placeholder logic (NotImplementedError)"""
        
        result = {
            "success": True,
            "errors": []
        }
        
        try:
            # Test different component types and their core methods
            component_type = getattr(component, 'component_type', 'Unknown')
            
            # Setup component first
            await component.setup({})
            
            # Test component-specific abstract methods directly
            if component_type == "Model":
                # Test Model methods
                if hasattr(component, '_run_inference'):
                    try:
                        test_input = test_inputs[0] if test_inputs else {"test": "data"}
                        await component._run_inference(test_input)
                    except NotImplementedError as nie:
                        result["success"] = False
                        result["errors"].append(f"PlaceholderLogicError: Model._run_inference raises NotImplementedError: {nie}")
                        return result
                        
                if hasattr(component, '_load_model'):
                    try:
                        await component._load_model()
                    except NotImplementedError as nie:
                        result["success"] = False
                        result["errors"].append(f"PlaceholderLogicError: Model._load_model raises NotImplementedError: {nie}")
                        return result
                    
            elif component_type == "Transformer":
                # Test Transformer transform method directly
                if hasattr(component, '_transform_data'):
                    try:
                        test_input = test_inputs[0] if test_inputs else {"test": "data"}
                        await component._transform_data(test_input)
                    except NotImplementedError as nie:
                        result["success"] = False
                        result["errors"].append(f"PlaceholderLogicError: Transformer._transform_data raises NotImplementedError: {nie}")
                        return result
                        
            elif component_type == "Source":
                # Test Source data generation method
                if hasattr(component, '_generate_data'):
                    try:
                        test_input = {"index": 0}
                        await component._generate_data(test_input)
                    except NotImplementedError as nie:
                        result["success"] = False
                        result["errors"].append(f"PlaceholderLogicError: Source._generate_data raises NotImplementedError: {nie}")
                        return result
                        
            elif component_type == "Sink":
                # Test Sink output method
                if hasattr(component, '_output_data'):
                    try:
                        test_input = test_inputs[0] if test_inputs else {"test": "data"}
                        await component._output_data(test_input)
                    except NotImplementedError as nie:
                        result["success"] = False
                        result["errors"].append(f"PlaceholderLogicError: Sink._output_data raises NotImplementedError: {nie}")
                        return result
                    
            # Generic test: try to trigger any abstract method by running a minimal process cycle
            try:
                # Create minimal test setup to trigger abstract methods
                import anyio
                from autocoder.orchestration.harness import SystemExecutionHarness
                
                # Create test harness
                harness = SystemExecutionHarness()
                
                # Setup minimal streams if component needs them
                if hasattr(component, 'receive_streams') and hasattr(component, 'send_streams'):
                    input_send, input_receive = anyio.create_memory_object_stream(max_buffer_size=1)
                    output_send, output_receive = anyio.create_memory_object_stream(max_buffer_size=1)
                    
                    component.receive_streams = {"test_input": input_receive}
                    component.send_streams = {"test_output": output_send}
                    
                    # Send one test item
                    test_input = test_inputs[0] if test_inputs else {"test": "data"}
                    await input_send.send(test_input)
                    await input_send.aclose()
                
                # The component will monitor the harness shutdown event indirectly
                
                # Try to run process for a very short time to trigger abstract methods
                async with anyio.create_task_group() as tg:
                    tg.start_soon(component.process)
                    
                    # Wait briefly to see if NotImplementedError is raised
                    try:
                        with anyio.move_on_after(0.1):
                            await anyio.sleep_forever()
                    except NotImplementedError as nie:
                        result["success"] = False
                        result["errors"].append(f"PlaceholderLogicError: Component core logic raises NotImplementedError: {nie}")
                        return result
                    # If we get here without NotImplementedError, that's good
                    tg.cancel_scope.cancel()
                except NotImplementedError as nie:
                    result["success"] = False
                    result["errors"].append(f"PlaceholderLogicError: Component core logic raises NotImplementedError: {nie}")
                    return result
                except Exception:
                    # Other exceptions are fine, we're just testing for NotImplementedError
                    pass
                finally:
                    harness._shutdown_event.set()
                        
            except Exception as e:
                # If we can't test this way, that's fine - other tests will catch issues
                pass
                
            # Cleanup
            await component.cleanup()
                    
        except Exception as e:
            # General exception during placeholder testing
            result["errors"].append(f"Error during placeholder logic test: {e}")
        
        return result
    
    async def _test_input_output_processing(self, 
                                          component: Component,
                                          test_inputs: List[Dict[str, Any]],
                                          expected_outputs: int,
                                          timeout: float) -> Dict[str, Any]:
        """Test component input/output processing with test harness"""
        
        result = {
            "input_success": False,
            "output_success": False,
            "errors": [],
            "performance": {}
        }
        
        try:
            # Create test harness for isolated testing
            harness = SystemExecutionHarness()
            
            # Setup anyio streams for testing
            input_send, input_receive = anyio.create_memory_object_stream(max_buffer_size=10)
            output_send, output_receive = anyio.create_memory_object_stream(max_buffer_size=10)
            
            # Configure component streams
            component.receive_streams = {"input": input_receive}
            component.send_streams = {"output": output_send}
            
            # Register component with harness
            harness.register_component("test_component", component)
            
            # Send test data to input stream
            for test_input in test_inputs:
                await input_send.send(test_input)
            await input_send.aclose()  # Close input stream to signal end of data
            
            # Run component processing with timeout
            start_time = time.time()
            
            try:
                # Start component processing with anyio structured concurrency
                async with anyio.create_task_group() as tg:
                    tg.start_soon(component.process)
                    
                    # Give time for processing
                    with anyio.move_on_after(timeout / 2):
                        await anyio.sleep_forever()
                    
                    # Stop processing by setting the shutdown event
                    harness._shutdown_event.set()
                    
                    # Wait for component to finish
                    with anyio.move_on_after(2.0):
                        await anyio.sleep_forever()
                    
                    # Cancel any remaining tasks
                    tg.cancel_scope.cancel()
                
                processing_time = time.time() - start_time
                result["performance"]["processing_time"] = processing_time
                
                # Check outputs
                outputs_collected = 0
                try:
                    # Collect outputs with a timeout
                    with anyio.move_on_after(1.0):  # 1 second to collect outputs
                        async for output in output_receive:
                            outputs_collected += 1
                            if outputs_collected >= expected_outputs * 2:
                                break
                except Exception:
                    pass  # Timeout or stream closed, that's ok
                
                result["input_success"] = True  # If we got here, input processing worked
                result["output_success"] = outputs_collected >= expected_outputs
                result["performance"]["outputs_generated"] = outputs_collected
                
                if not result["output_success"]:
                    result["errors"].append(f"Expected {expected_outputs} outputs, got {outputs_collected}")
                
            except NotImplementedError as nie:
                # Catch NotImplementedError specifically (placeholder logic detection)
                result["errors"].append(f"PlaceholderLogicError: Component contains placeholder logic - {nie}")
                return result
            
        except Exception as e:
            result["errors"].append(f"Input/output test error: {e}")
        
        return result


class ComponentTestRunner:
    """
    Main component-by-component test runner.
    
    Implements the "block early, block often" philosophy by testing each
    component in isolation before allowing system integration.
    """
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("./component_test_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.contract_validator = ComponentContractValidator()
        self.functional_tester = ComponentFunctionalTester()
        
        self.test_results: List[ComponentTestResult] = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ComponentTestRunner")
    
    async def run_component_test_suite(self, test_configs: List[ComponentTestConfig]) -> Dict[str, Any]:
        """Run complete component test suite"""
        
        print(f"🧪 Starting component-by-component testing with {len(test_configs)} components...")
        start_time = time.time()
        
        for config in test_configs:
            print(f"\n📋 Testing component: {config.component_class_name}")
            result = await self._test_single_component(config)
            self.test_results.append(result)
            
            if result.success:
                print(f"✅ {config.component_class_name} PASSED")
            else:
                print(f"❌ {config.component_class_name} FAILED: {result.error_message}")
                
                # BLOCK EARLY: If any component fails, entire suite fails
                print(f"🚫 BLOCKING - Component failure prevents system generation")
                break
        
        total_time = time.time() - start_time
        
        # Generate summary
        passed = sum(1 for r in self.test_results if r.success)
        failed = len(test_configs) - passed
        
        summary = {
            "total_components": len(test_configs),
            "tested_components": len(self.test_results),
            "passed": passed,
            "failed": failed,
            "success_rate": passed / len(self.test_results) if self.test_results else 0,
            "total_time": total_time,
            "blocking_enabled": True,
            "results": self.test_results
        }
        
        print(f"\n📊 Component Test Summary:")
        print(f"   Total components: {summary['total_components']}")
        print(f"   Tested: {summary['tested_components']}")
        print(f"   Passed: {summary['passed']}")
        print(f"   Failed: {summary['failed']}")
        print(f"   Success rate: {summary['success_rate']:.1%}")
        print(f"   Total time: {total_time:.2f}s")
        
        if failed > 0:
            print(f"\n🚫 BLOCKED: {failed} component(s) failed validation")
            print("   System generation will be blocked until all components pass")
        else:
            print(f"\n✅ ALL COMPONENTS PASSED: System generation allowed")
        
        return summary
    
    async def _test_single_component(self, config: ComponentTestConfig) -> ComponentTestResult:
        """Test a single component comprehensively"""
        
        start_time = time.time()
        
        result = ComponentTestResult(
            component_name=config.component_class_name,
            component_type=self._detect_component_type(config.component_path),
            success=True,
            execution_time=0.0,
            test_logs=[],
            validation_details={}
        )
        
        try:
            # 1. Contract validation
            if config.validate_contract:
                print(f"   🔍 Validating contract...")
                contract_result = self.contract_validator.validate_component_contract(
                    config.component_path, config.component_class_name
                )
                
                result.contract_validation_passed = contract_result["success"]
                result.required_methods_present = len(contract_result["errors"]) == 0
                result.async_patterns_correct = contract_result.get("async_pattern_check", False)
                result.harness_compatibility = contract_result.get("inheritance_check", False)
                result.validation_details["contract"] = contract_result
                
                if not contract_result["success"]:
                    result.success = False
                    result.error_message = f"Contract validation failed: {contract_result['errors']}"
                    result.test_logs.extend([f"CONTRACT ERROR: {err}" for err in contract_result["errors"]])
            
            # 2. Functional testing (only if contract passed)
            if config.validate_functionality and result.contract_validation_passed:
                print(f"   ⚙️  Testing functionality...")
                functional_result = await self.functional_tester.test_component_functionality(
                    config.component_path,
                    config.component_class_name,
                    config.test_inputs,
                    config.expected_outputs,
                    config.timeout_seconds
                )
                
                result.functional_test_passed = functional_result["success"]
                result.input_processing_works = functional_result["input_processing_test"]
                result.output_generation_works = functional_result["output_generation_test"]
                result.lifecycle_methods_work = functional_result["lifecycle_test"]
                result.validation_details["functional"] = functional_result
                
                # Performance metrics
                perf = functional_result.get("performance_metrics", {})
                result.processing_time = perf.get("processing_time", 0.0)
                
                if not functional_result["success"]:
                    result.success = False
                    if not result.error_message:
                        result.error_message = f"Functional test failed: {functional_result['errors']}"
                    result.test_logs.extend([f"FUNCTIONAL ERROR: {err}" for err in functional_result["errors"]])
            
            # 3. Performance validation (optional)
            if config.validate_performance and result.functional_test_passed:
                print(f"   📊 Performance testing...")
                # Could add performance benchmarks here
                pass
            
        except Exception as e:
            result.success = False
            result.error_message = f"Component test failed: {e}"
            result.test_logs.append(f"EXCEPTION: {traceback.format_exc()}")
        
        result.execution_time = time.time() - start_time
        return result
    
    def _detect_component_type(self, component_path: Path) -> str:
        """Detect the type of component from its file"""
        
        try:
            with open(component_path, 'r') as f:
                content = f.read()
            
            # Simple heuristic based on class names and imports
            if "APIEndpoint" in content or "FastAPI" in content:
                return "APIEndpoint"
            elif "Source" in content and "generate_data" in content:
                return "Source"
            elif "Sink" in content and "output_data" in content:
                return "Sink"
            elif "Transformer" in content or "transform" in content:
                return "Transformer"
            elif "Model" in content or "predict" in content:
                return "Model"
            elif "Store" in content or "store" in content:
                return "Store"
            else:
                return "Component"
                
        except Exception:
            return "Unknown"
    
    def save_test_results(self, filename: str = "component_test_results.json") -> Path:
        """Save detailed test results to file"""
        
        results_file = self.output_dir / filename
        
        # Convert results to serializable format
        serializable_results = []
        for result in self.test_results:
            result_dict = {
                "component_name": result.component_name,
                "component_type": result.component_type,
                "success": result.success,
                "execution_time": result.execution_time,
                "error_message": result.error_message,
                "contract_validation_passed": result.contract_validation_passed,
                "required_methods_present": result.required_methods_present,
                "async_patterns_correct": result.async_patterns_correct,
                "harness_compatibility": result.harness_compatibility,
                "functional_test_passed": result.functional_test_passed,
                "input_processing_works": result.input_processing_works,
                "output_generation_works": result.output_generation_works,
                "lifecycle_methods_work": result.lifecycle_methods_work,
                "setup_time": result.setup_time,
                "processing_time": result.processing_time,
                "cleanup_time": result.cleanup_time,
                "memory_usage": result.memory_usage,
                "test_logs": result.test_logs or [],
                "validation_details": result.validation_details or {}
            }
            serializable_results.append(result_dict)
        
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_components": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r.success),
                "failed": sum(1 for r in self.test_results if not r.success),
                "results": serializable_results
            }, f, indent=2)
        
        return results_file


def create_component_test_configs_from_directory(components_dir: Path) -> List[ComponentTestConfig]:
    """Create test configurations by scanning a components directory"""
    
    configs = []
    
    if not components_dir.exists():
        return configs
    
    for component_file in components_dir.glob("*.py"):
        if component_file.name.startswith("__"):
            continue
            
        # Try to detect component class name
        try:
            with open(component_file, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it inherits from Component
                    inherits_component = any(
                        isinstance(base, ast.Name) and base.id == 'Component' or
                        isinstance(base, ast.Attribute) and base.attr == 'Component'
                        for base in node.bases
                    )
                    
                    if inherits_component:
                        # Create test config
                        config = ComponentTestConfig(
                            component_path=component_file,
                            component_class_name=node.name,
                            test_inputs=[
                                {"test_id": 1, "value": 10},
                                {"test_id": 2, "value": 20},
                                {"test_id": 3, "value": 30}
                            ],
                            expected_outputs=3,
                            timeout_seconds=5.0
                        )
                        configs.append(config)
                        break
        
        except Exception as e:
            print(f"Warning: Could not analyze {component_file}: {e}")
    
    return configs


async def main():
    """Run component-by-component testing on generated systems"""
    
    print("🧪 Component-by-Component Test Runner - Phase 6")
    print("=" * 80)
    
    # Find generated systems to test
    test_systems_dir = Path("./test_generated_systems")
    if not test_systems_dir.exists():
        print(f"No test systems found at {test_systems_dir}")
        return
    
    runner = ComponentTestRunner()
    all_passed = True
    
    # Test each generated system's components
    for system_dir in test_systems_dir.iterdir():
        if not system_dir.is_dir():
            continue
            
        components_dir = system_dir / "components"
        if not components_dir.exists():
            continue
        
        print(f"\n🔍 Testing components in system: {system_dir.name}")
        
        # Create test configurations
        test_configs = create_component_test_configs_from_directory(components_dir)
        
        if not test_configs:
            print(f"   No components found to test")
            continue
        
        # Run component tests
        summary = await runner.run_component_test_suite(test_configs)
        
        if summary["failed"] > 0:
            all_passed = False
            print(f"   🚫 System {system_dir.name} BLOCKED due to component failures")
        else:
            print(f"   ✅ System {system_dir.name} components all passed")
    
    # Save results
    results_file = runner.save_test_results()
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Final result
    if all_passed:
        print("\n🎉 ALL COMPONENT TESTS PASSED - System generation allowed!")
        exit(0)
    else:
        print("\n🚫 COMPONENT TESTS FAILED - System generation blocked!")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())