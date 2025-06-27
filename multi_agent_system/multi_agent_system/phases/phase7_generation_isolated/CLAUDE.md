# Phase 7: Two-Phase Generation Pipeline Implementation

**PHASE**: P7 CRITICAL - Transform ValidationDrivenOrchestrator to generate SystemExecutionHarness-based systems  
**EVIDENCE LOG**: All output and evidence must be saved to `evidence/phase7_generation/`

## Phase 7 Objective

Transform the current ValidationDrivenOrchestrator to generate SystemExecutionHarness-based component systems instead of simple Flask applications. Implement a two-phase generation pipeline that creates harness-compatible main.py files and HarnessComponent-based components with stream communication.

## Evidence-Based Success Criteria

**100% Success Definition**: External evaluator can review evidence log and confirm the generation pipeline successfully produces SystemExecutionHarness-based systems from natural language input, with working stream communication and component orchestration.

## Required Evidence Log Structure

```
evidence/phase7_generation/
├── day1_system_scaffold_generator/
│   ├── system_scaffold_generator.py         # SystemScaffoldGenerator implementation
│   ├── harness_template_engine.py           # Template generation for main.py
│   ├── connection_mapper.py                 # Blueprint binding → stream connections
│   ├── test_scaffold_generation.py          # Scaffold generator tests
│   └── scaffold_generation_demo.py          # Working demo with output logs
├── day2_component_logic_generator/
│   ├── harness_component_generator.py       # HarnessComponent code generation
│   ├── stream_io_templates.py               # Stream I/O code templates
│   ├── lifecycle_method_generator.py        # Setup/process/cleanup generation
│   ├── test_component_generation.py         # Component generator tests
│   └── component_generation_demo.py         # Working demo with output logs
├── day3_orchestrator_integration/
│   ├── enhanced_orchestrator.py             # Enhanced ValidationDrivenOrchestrator
│   ├── generation_coordinator.py            # Coordinates scaffold + component generation
│   ├── validation_integration.py            # Integration with 4-tier validation
│   ├── test_orchestrator_integration.py     # Integration tests
│   └── orchestrator_integration_demo.py     # Working demo with output logs
├── day4_end_to_end_generation/
│   ├── blueprint_to_harness_pipeline.py     # Complete natural language → harness pipeline
│   ├── generated_system_validator.py        # Validates generated harness systems
│   ├── test_end_to_end_generation.py        # Complete pipeline tests
│   ├── e2e_test_output.txt                  # Raw test execution logs
│   └── natural_language_demo.py             # Natural language → working harness system
├── day5_performance_optimization/
│   ├── generation_performance_optimizer.py  # Optimize generation speed
│   ├── template_caching_system.py           # Cache templates and patterns
│   ├── parallel_generation_engine.py        # Parallel component generation
│   ├── test_performance_optimization.py     # Performance tests
│   └── performance_benchmark_results.txt    # Raw performance measurements
└── phase7_completion_evidence/
    ├── generated_harness_system_example/     # Complete generated system
    │   ├── main.py                           # Generated harness main
    │   ├── components/                       # Generated HarnessComponents
    │   │   ├── api_gateway.py
    │   │   ├── task_controller.py
    │   │   └── task_store.py
    │   ├── config/
    │   │   └── system_config.py
    │   └── run_system_log.txt                # Raw execution log of generated system
    ├── generation_performance_report.txt     # Complete performance analysis
    ├── external_evaluator_checklist.txt      # External validation checklist
    └── implementation_summary.txt            # Complete implementation summary
```

## Daily Implementation Protocol

### Day 1: System Scaffold Generator

1. **Create SystemScaffoldGenerator**
   ```python
   # Create: /evidence/phase7_generation/day1_system_scaffold_generator/system_scaffold_generator.py
   class SystemScaffoldGenerator:
       """
       Generates main.py files with SystemExecutionHarness setup from SystemBlueprint.
       
       Transforms blueprint component definitions into harness-based orchestration code.
       """
       
       def __init__(self, template_engine: HarnessTemplateEngine):
           self.template_engine = template_engine
           self.connection_mapper = ConnectionMapper()
           
       def generate_main_py(self, blueprint: SystemBlueprint) -> str:
           """
           Generate main.py with SystemExecutionHarness setup.
           
           Current Flask Output:
           ```python
           from flask import Flask
           app = Flask(__name__)
           
           @app.route('/tasks', methods=['GET'])
           def list_tasks():
               return jsonify(tasks)
           ```
           
           Target Harness Output:
           ```python
           from autocoder.orchestration import SystemExecutionHarness
           from components.api_gateway import TaskAPIGateway
           from components.task_controller import TaskController
           from components.task_store import TaskStore
           
           async def main():
               harness = SystemExecutionHarness()
               
               # Component registration
               harness.register_component('api_gateway', TaskAPIGateway(config))
               harness.register_component('task_controller', TaskController(config))
               harness.register_component('task_store', TaskStore(config))
               
               # Stream connections (derived from blueprint bindings)
               harness.connect('api_gateway.requests', 'task_controller.input')
               harness.connect('task_controller.store_commands', 'task_store.input')
               harness.connect('task_store.responses', 'task_controller.store_data')
               harness.connect('task_controller.responses', 'api_gateway.responses')
               
               await harness.run()
           ```
           """
           
           # Extract components from blueprint
           components = self._extract_components(blueprint)
           
           # Generate component imports
           imports = self._generate_component_imports(components)
           
           # Generate component registration code
           registration_code = self._generate_component_registration(components)
           
           # Generate stream connections from blueprint bindings
           connections = self.connection_mapper.derive_connections(blueprint)
           connection_code = self._generate_connection_code(connections)
           
           # Generate complete main.py
           return self.template_engine.render_main_template(
               imports=imports,
               registration_code=registration_code,
               connection_code=connection_code,
               config=blueprint.config
           )
   ```

2. **Create HarnessTemplateEngine**
   ```python
   # Create: /evidence/phase7_generation/day1_system_scaffold_generator/harness_template_engine.py
   class HarnessTemplateEngine:
       """
       Template engine for generating SystemExecutionHarness-based code.
       """
       
       def __init__(self):
           self.main_template = self._load_main_template()
           self.component_templates = self._load_component_templates()
           
       def render_main_template(self, imports: List[str], registration_code: str, 
                               connection_code: str, config: Dict[str, Any]) -> str:
           """Render complete main.py with harness setup"""
           
           template = '''#!/usr/bin/env python3
   """
   Generated SystemExecutionHarness-based system
   Generated from: Natural Language via V5.0 Two-Phase Generation Pipeline
   """
   
   import asyncio
   import logging
   from autocoder.orchestration import SystemExecutionHarness
   {imports}
   
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   
   async def main():
       """Main harness orchestration function"""
       logger.info("🚀 Starting SystemExecutionHarness-based system...")
       
       try:
           # Initialize harness
           harness = SystemExecutionHarness()
           
           # Component registration
           {registration_code}
           
           # Stream connections
           {connection_code}
           
           # Start system
           logger.info("✅ All components registered and connected")
           await harness.run()
           
       except Exception as e:
           logger.error(f"❌ System startup failed: {{e}}")
           raise
   
   if __name__ == "__main__":
       asyncio.run(main())
   '''
           
           return template.format(
               imports='\n'.join(imports),
               registration_code=registration_code,
               connection_code=connection_code
           )
   ```

3. **Create ConnectionMapper**
   ```python
   # Create: /evidence/phase7_generation/day1_system_scaffold_generator/connection_mapper.py
   class ConnectionMapper:
       """
       Maps SystemBlueprint component bindings to SystemExecutionHarness stream connections.
       """
       
       def derive_connections(self, blueprint: SystemBlueprint) -> List[StreamConnection]:
           """
           Derive stream connections from blueprint component bindings.
           
           Blueprint Binding Example:
           ```yaml
           components:
             api_gateway:
               bindings:
                 - source: "request_input"
                   target: "task_controller.process_request"
             task_controller:
               bindings:
                 - source: "store_operation"
                   target: "task_store.execute"
           ```
           
           Generated Connections:
           ```python
           harness.connect('api_gateway.request_input', 'task_controller.process_request')
           harness.connect('task_controller.store_operation', 'task_store.execute')
           ```
           """
           
           connections = []
           
           for component_name, component_def in blueprint.components.items():
               if 'bindings' in component_def:
                   for binding in component_def['bindings']:
                       source_endpoint = f"{component_name}.{binding['source']}"
                       target_endpoint = binding['target']
                       
                       connections.append(StreamConnection(
                           source=source_endpoint,
                           target=target_endpoint,
                           buffer_size=binding.get('buffer_size', 100),
                           connection_type=binding.get('type', 'data_stream')
                       ))
           
           return connections
   ```

### Day 2: Component Logic Generator

1. **Create HarnessComponentGenerator**
   ```python
   # Create: /evidence/phase7_generation/day2_component_logic_generator/harness_component_generator.py
   class HarnessComponentGenerator:
       """
       Generates HarnessComponent-based component code from ComponentLogic definitions.
       """
       
       def __init__(self):
           self.template_engine = StreamIOTemplateEngine()
           self.lifecycle_generator = LifecycleMethodGenerator()
           
       def generate_component(self, component_name: str, component_logic: ComponentLogic, 
                             component_type: str) -> str:
           """
           Generate HarnessComponent class from ComponentLogic.
           
           Current Function-Based Output:
           ```python
           def process_task_request(request_data):
               # Business logic here
               task = create_task(request_data['title'], request_data['description'])
               return {'status': 'created', 'task': task}
           ```
           
           Target HarnessComponent Output:
           ```python
           class TaskController(HarnessComponent):
               async def setup(self):
                   self.task_storage = {}
                   logger.info("TaskController initialized")
                   
               async def process(self):
                   async for request in self.receive_streams['input']:
                       try:
                           # Business logic here
                           result = await self.process_task_request(request.payload)
                           await self.send_streams['output'].send(result)
                       except Exception as e:
                           await self.send_streams['error'].send({'error': str(e)})
                           
               async def process_task_request(self, request_data):
                   task = self.create_task(request_data['title'], request_data['description'])
                   return {'status': 'created', 'task': task}
                   
               async def cleanup(self):
                   logger.info("TaskController cleanup completed")
           ```
           """
           
           # Generate class definition
           class_def = self._generate_class_definition(component_name, component_type)
           
           # Generate lifecycle methods
           setup_method = self.lifecycle_generator.generate_setup_method(component_logic)
           process_method = self._generate_process_method(component_logic)
           cleanup_method = self.lifecycle_generator.generate_cleanup_method(component_logic)
           
           # Generate business logic methods
           business_methods = self._generate_business_logic_methods(component_logic)
           
           # Generate complete component
           return self.template_engine.render_component_template(
               class_def=class_def,
               setup_method=setup_method,
               process_method=process_method,
               cleanup_method=cleanup_method,
               business_methods=business_methods,
               component_logic=component_logic
           )
   ```

2. **Create StreamIOTemplateEngine**
   ```python
   # Create: /evidence/phase7_generation/day2_component_logic_generator/stream_io_templates.py
   class StreamIOTemplateEngine:
       """
       Template engine for generating stream-based I/O code in HarnessComponents.
       """
       
       def generate_stream_receive_code(self, input_streams: List[str]) -> str:
           """Generate code for receiving from multiple input streams"""
           
           if len(input_streams) == 1:
               return f'''
               async for message in self.receive_streams['{input_streams[0]}']:
                   try:
                       result = await self.process_message(message.payload)
                       if result:
                           await self.send_result(result)
                   except Exception as e:
                       await self.handle_error(e, message)
               '''
           else:
               # Multiple input streams - use anyio to multiplex
               return f'''
               import anyio
               
               async with anyio.create_task_group() as tg:
                   {self._generate_multiple_stream_handlers(input_streams)}
               '''
               
       def generate_stream_send_code(self, output_streams: List[str]) -> str:
           """Generate code for sending to output streams"""
           
           send_methods = []
           for stream in output_streams:
               send_methods.append(f'''
               async def send_to_{stream}(self, data):
                   if '{stream}' in self.send_streams:
                       await self.send_streams['{stream}'].send(data)
               ''')
           
           return '\n'.join(send_methods)
   ```

### Day 3: ValidationDrivenOrchestrator Integration

1. **Create Enhanced Orchestrator**
   ```python
   # Create: /evidence/phase7_generation/day3_orchestrator_integration/enhanced_orchestrator.py
   class EnhancedValidationDrivenOrchestrator(ValidationDrivenOrchestrator):
       """
       Enhanced ValidationDrivenOrchestrator with Two-Phase Generation Pipeline.
       
       Generates SystemExecutionHarness-based systems instead of Flask applications.
       """
       
       def __init__(self):
           super().__init__()
           
           # Phase 7 components
           self.scaffold_generator = SystemScaffoldGenerator(HarnessTemplateEngine())
           self.component_generator = HarnessComponentGenerator()
           self.generation_coordinator = GenerationCoordinator()
           
       async def generate_system_with_validation(self, blueprint: SystemBlueprint):
           """
           Enhanced system generation with harness-based output.
           
           Pipeline Flow:
           1. Natural Language → SystemBlueprint (existing)
           2. 4-tier validation pipeline (existing)
           3. Two-phase generation (NEW):
              - Phase 1: Generate harness scaffold (main.py)
              - Phase 2: Generate HarnessComponent classes
           4. Harness system validation and testing
           """
           
           # Existing validation pipeline (unchanged)
           level1_result = await self._execute_level1_validation()
           level2_result = await self._execute_level2_validation(blueprint, level1_result)
           level3_result = await self._execute_level3_validation(blueprint, level2_result)
           level4_result = await self._execute_level4_validation(blueprint, level3_result)
           
           if not level4_result.passed:
               raise ValidationPipelineError("4-tier validation failed")
           
           # NEW: Two-phase harness generation
           harness_system = await self.generation_coordinator.generate_harness_system(blueprint)
           
           # NEW: Harness system validation
           harness_validation = await self._validate_harness_system(harness_system)
           
           if not harness_validation.passed:
               # Apply harness-specific healing
               healed_system = await self._heal_harness_system(harness_system, harness_validation)
               return healed_system
           
           return harness_system
   ```

2. **Create GenerationCoordinator**
   ```python
   # Create: /evidence/phase7_generation/day3_orchestrator_integration/generation_coordinator.py
   class GenerationCoordinator:
       """
       Coordinates scaffold generation and component generation for complete harness systems.
       """
       
       def __init__(self):
           self.scaffold_generator = SystemScaffoldGenerator(HarnessTemplateEngine())
           self.component_generator = HarnessComponentGenerator()
           
       async def generate_harness_system(self, blueprint: SystemBlueprint) -> HarnessSystem:
           """
           Two-phase generation of complete harness system.
           
           Phase 1: System Scaffold Generation
           - Generate main.py with harness setup
           - Generate component registration code
           - Generate stream connection code
           
           Phase 2: Component Logic Generation  
           - Generate HarnessComponent classes
           - Generate stream I/O code
           - Generate lifecycle methods
           """
           
           # Phase 1: Generate system scaffold
           main_py_code = self.scaffold_generator.generate_main_py(blueprint)
           config_code = self.scaffold_generator.generate_config_file(blueprint)
           
           # Phase 2: Generate components
           generated_components = {}
           for component_name, component_logic in blueprint.component_logic.items():
               component_code = self.component_generator.generate_component(
                   component_name, component_logic, blueprint.components[component_name]['type']
               )
               generated_components[component_name] = component_code
           
           # Create complete harness system
           harness_system = HarnessSystem(
               main_py=main_py_code,
               config=config_code,
               components=generated_components,
               blueprint=blueprint
           )
           
           return harness_system
   ```

### Day 4: End-to-End Generation Testing

1. **Create Complete Pipeline**
   ```python
   # Create: /evidence/phase7_generation/day4_end_to_end_generation/blueprint_to_harness_pipeline.py
   class BlueprintToHarnessPipeline:
       """
       Complete natural language → working harness system pipeline.
       """
       
       def __init__(self):
           self.orchestrator = EnhancedValidationDrivenOrchestrator()
           self.system_validator = GeneratedSystemValidator()
           
       async def generate_from_natural_language(self, natural_language_request: str) -> DeployedHarnessSystem:
           """
           Complete pipeline: Natural Language → Deployed Harness System
           
           Example Input:
           "Create a task management API with the following features:
            - Add new tasks with title and description  
            - Mark tasks as completed
            - List all tasks
            - Store data in memory"
           
           Example Output:
           - Generated main.py with SystemExecutionHarness
           - Generated TaskAPIGateway(HarnessComponent)
           - Generated TaskController(HarnessComponent) 
           - Generated TaskStore(HarnessComponent)
           - Working stream connections between components
           - Deployed and tested harness system
           """
           
           # Step 1: Natural language → SystemBlueprint
           blueprint = await self.orchestrator.natural_language_to_blueprint(natural_language_request)
           
           # Step 2: 4-tier validation + harness generation
           harness_system = await self.orchestrator.generate_system_with_validation(blueprint)
           
           # Step 3: Write generated system to filesystem
           system_path = await self._write_harness_system(harness_system)
           
           # Step 4: Validate generated system
           validation_result = await self.system_validator.validate_generated_system(system_path)
           
           if not validation_result.passed:
               raise GeneratedSystemError(f"Generated system validation failed: {validation_result.errors}")
           
           # Step 5: Deploy and test system
           deployed_system = await self._deploy_and_test_harness_system(system_path)
           
           return deployed_system
   ```

2. **Create Natural Language Demo**
   ```python
   # Create: /evidence/phase7_generation/day4_end_to_end_generation/natural_language_demo.py
   async def main():
       """
       Live demonstration of natural language → working harness system
       """
       
       print("🚀 Phase 7 Two-Phase Generation Pipeline Demo")
       print("=" * 60)
       
       # Natural language input
       natural_language_request = """
       Create a simple task management API with the following features:
       - Add new tasks with title and description
       - Mark tasks as completed  
       - List all tasks
       - Delete tasks
       - Store data in memory for simplicity
       - Expose REST endpoints on port 8080
       """
       
       print(f"📝 Natural Language Input:")
       print(natural_language_request.strip())
       print()
       
       # Generate harness system
       pipeline = BlueprintToHarnessPipeline()
       
       print("⚙️ Generating SystemExecutionHarness-based system...")
       deployed_system = await pipeline.generate_from_natural_language(natural_language_request)
       
       print(f"✅ Generated harness system in: {deployed_system.path}")
       print()
       
       # Show generated main.py structure
       print("📋 Generated main.py structure:")
       print("```python")
       print(deployed_system.main_py_preview)
       print("```")
       print()
       
       # Test the deployed system
       print("🧪 Testing deployed harness system...")
       test_results = await deployed_system.run_integration_tests()
       
       for test_name, result in test_results.items():
           status = "✅" if result.passed else "❌"
           print(f"{status} {test_name}: {result.message}")
       
       print()
       print("🎉 Phase 7 Two-Phase Generation Pipeline SUCCESS!")
       print("Natural language successfully converted to working harness system!")
   ```

### Day 5: Performance Optimization

1. **Create Generation Performance Optimizer**
   ```python
   # Create: /evidence/phase7_generation/day5_performance_optimization/generation_performance_optimizer.py
   class GenerationPerformanceOptimizer:
       """
       Optimizes the two-phase generation pipeline for production performance.
       """
       
       def __init__(self):
           self.template_cache = TemplateCachingSystem()
           self.parallel_engine = ParallelGenerationEngine()
           
       async def optimize_generation_pipeline(self) -> OptimizationResults:
           """
           Performance targets:
           - Blueprint → Harness System: <2 seconds
           - Component generation: <500ms per component
           - Template rendering: <100ms total
           - Memory usage: <100MB for typical system
           """
           
           # Optimization 1: Template caching
           cache_optimization = await self.template_cache.optimize_template_loading()
           
           # Optimization 2: Parallel component generation
           parallel_optimization = await self.parallel_engine.optimize_component_generation()
           
           # Optimization 3: Code generation caching
           generation_cache_optimization = await self._optimize_generation_caching()
           
           return OptimizationResults(
               template_caching=cache_optimization,
               parallel_generation=parallel_optimization,
               generation_caching=generation_cache_optimization,
               overall_improvement=self._calculate_overall_improvement()
           )
   ```

## Phase 7 Completion Criteria

**Phase 7 is 100% complete when the evidence log contains:**

1. ✅ **SystemScaffoldGenerator** generating main.py with harness setup
2. ✅ **HarnessComponentGenerator** generating stream-based components
3. ✅ **Enhanced ValidationDrivenOrchestrator** with two-phase generation
4. ✅ **End-to-end pipeline** from natural language → working harness system
5. ✅ **Performance optimization** meeting generation speed targets
6. ✅ **Generated system example** that external evaluator can run and verify
7. ✅ **Integration tests** showing compatibility with Phase 6 SystemExecutionHarness
8. ✅ **Raw execution logs** proving the generated systems work

## External Evaluator Checklist

An external evaluator reviewing `evidence/phase7_generation/` must be able to confirm:

- [ ] Natural language input generates SystemExecutionHarness-based systems (not Flask)
- [ ] Generated main.py uses harness component registration and stream connections
- [ ] Generated components extend HarnessComponent with proper lifecycle methods
- [ ] Stream communication works correctly between generated components
- [ ] Two-phase generation pipeline is integrated with ValidationDrivenOrchestrator
- [ ] Generated systems can be deployed and tested successfully
- [ ] Performance targets are met for generation speed
- [ ] Complete integration with existing V5.0 validation pipeline

## Implementation Success Requirements

**CRITICAL**: This implementation must demonstrate:

1. **Actual Code Generation**: Not documentation, but working code generators
2. **System Integration**: Must work with existing ValidationDrivenOrchestrator
3. **Harness Compatibility**: Generated systems must work with Phase 6 SystemExecutionHarness
4. **End-to-End Functionality**: Natural language → deployed harness system pipeline
5. **Performance**: Generation must be fast enough for production use

---

**Current Status**: 🔄 **PHASE 7 READY FOR IMPLEMENTATION**  
**Evidence Location**: `evidence/phase7_generation/`  
**Success Requirement**: 100% evidence-based confirmation of working two-phase generation pipeline