# Phase 7: Two-Phase Generation Pipeline - External Evaluation Criteria

**EVALUATION CONTEXT**: You are an external evaluator with NO knowledge of the implementation process. Your job is to execute the evidence provided and determine if Phase 7 objectives are met.

**EVALUATION METHOD**: Execute all provided code, run tests, examine outputs, and verify against these specific criteria.

## Core Evaluation Criteria

### ✅ **PASS Criteria - All Must Be Met**

#### **1. System Scaffold Generation (25 points)**
- [ ] **SystemScaffoldGenerator exists** and can be imported
- [ ] **Generates main.py** with SystemExecutionHarness setup (not Flask)
- [ ] **Component registration code** properly generated from blueprint
- [ ] **Stream connection code** properly derived from component bindings
- [ ] **Template engine** renders complete, executable main.py files
- [ ] **Generated main.py runs** without import errors when executed

**Evidence Required**:
- Working `system_scaffold_generator.py` implementation
- Generated `main.py` example that imports SystemExecutionHarness
- Test output showing successful scaffold generation
- Demo script showing scaffold generation working

#### **2. Component Logic Generation (25 points)**  
- [ ] **HarnessComponentGenerator exists** and can be imported
- [ ] **Generates HarnessComponent classes** (not standalone functions)
- [ ] **Stream I/O code generation** with proper async for receive_streams loops
- [ ] **Lifecycle methods** (setup/process/cleanup) properly generated
- [ ] **Business logic integration** within HarnessComponent framework
- [ ] **Generated components import** and instantiate without errors

**Evidence Required**:
- Working `harness_component_generator.py` implementation  
- Generated component examples extending HarnessComponent
- Test output showing successful component generation
- Demo script showing component generation working

#### **3. ValidationDrivenOrchestrator Integration (25 points)**
- [ ] **Enhanced orchestrator exists** and inherits from ValidationDrivenOrchestrator
- [ ] **Two-phase generation** integrated into existing validation pipeline
- [ ] **Generation coordinator** successfully coordinates scaffold + component generation
- [ ] **Harness system validation** works with generated systems
- [ ] **Integration with existing** 4-tier validation pipeline preserved
- [ ] **Generated systems pass** orchestrator validation

**Evidence Required**:
- Working `enhanced_orchestrator.py` implementation
- Integration test showing orchestrator + generation working
- Test output showing validation pipeline with generation
- Demo script showing orchestrator generating harness systems

#### **4. End-to-End Generation Pipeline (25 points)**
- [ ] **Natural language input** generates working harness systems
- [ ] **Complete pipeline** from English → deployed SystemExecutionHarness
- [ ] **Generated system deploys** and responds to requests successfully  
- [ ] **Stream communication** works between generated components
- [ ] **System validation** confirms generated system functionality
- [ ] **Integration tests** pass for complete pipeline

**Evidence Required**:
- Working `blueprint_to_harness_pipeline.py` implementation
- Natural language demo showing complete pipeline
- Generated system example with working components
- Test logs showing deployed system responding to requests
- End-to-end test execution output

### ❌ **AUTOMATIC FAIL Conditions**

#### **Critical Failures**:
- Generated systems still use Flask instead of SystemExecutionHarness
- SystemScaffoldGenerator or HarnessComponentGenerator missing or non-functional
- Generated components don't extend HarnessComponent
- No working end-to-end demo from natural language → deployed system
- Integration with ValidationDrivenOrchestrator broken or missing
- Generated systems fail to deploy or run successfully

#### **Implementation Failures**:
- Missing core evidence files (scaffold generator, component generator, etc.)
- Test failures with <80% pass rate
- Generated code has syntax errors or import failures
- Performance targets not met (>5 second generation time)
- No working demos or only mock implementations

## Evaluation Process

### **Step 1: Code Execution Verification**
```bash
# Execute each major component
cd evidence/phase7_generation/day1_system_scaffold_generator/
python test_scaffold_generation.py

cd ../day2_component_logic_generator/  
python test_component_generation.py

cd ../day3_orchestrator_integration/
python test_orchestrator_integration.py

cd ../day4_end_to_end_generation/
python test_end_to_end_generation.py
```

**Expected Results**: All tests pass with >90% success rate

### **Step 2: Generated System Verification**
```bash
# Test generated system example
cd evidence/phase7_generation/phase7_completion_evidence/generated_harness_system_example/
python main.py &

# Test system responds
curl http://localhost:8080/health
curl -X POST http://localhost:8080/tasks -H "Content-Type: application/json" -d '{"title":"Test Task"}'
curl http://localhost:8080/tasks
```

**Expected Results**: System starts, responds to requests, shows harness-based architecture

### **Step 3: Natural Language Pipeline Verification**
```bash
# Test complete natural language → system pipeline
cd evidence/phase7_generation/day4_end_to_end_generation/
python natural_language_demo.py
```

**Expected Results**: Natural language input produces working SystemExecutionHarness system

### **Step 4: Architecture Compliance Verification**

**Check Generated main.py Structure**:
```python
# Generated main.py MUST contain:
from autocoder.orchestration import SystemExecutionHarness  # NOT Flask
harness = SystemExecutionHarness()                          # NOT app = Flask(__name__)
harness.register_component(...)                             # NOT @app.route
harness.connect(...)                                        # Stream connections
await harness.run()                                         # NOT app.run()
```

**Check Generated Components**:
```python
# Generated components MUST:
class SomeComponent(HarnessComponent):                      # NOT standalone functions
    async def setup(self): ...                             # Lifecycle methods
    async def process(self):                                # Stream processing
        async for message in self.receive_streams[...]:    # Stream I/O
            await self.send_streams[...].send(...)
    async def cleanup(self): ...
```

## Performance Verification

### **Generation Speed Requirements**:
- Blueprint → complete harness system: **<3 seconds**
- Individual component generation: **<500ms each**
- Template rendering: **<200ms total**
- System deployment: **<5 seconds**

### **System Performance Requirements**:
- Generated system startup: **<2 seconds**
- Response to health check: **<100ms**
- Stream message throughput: **>100 msg/sec**

## Evidence Quality Standards

### **Required Evidence Types**:
- ✅ **Executable code** that external evaluator can run
- ✅ **Raw test output** showing actual test execution results
- ✅ **Working demonstrations** with terminal output logs
- ✅ **Generated system examples** that can be deployed and tested
- ✅ **Performance measurements** with actual timing data

### **Insufficient Evidence** (Automatic Fail):
- Documentation without working code
- Test descriptions without actual test execution
- Claims without proof (raw output)
- Non-functional demonstrations
- Generated examples that don't work

## Final Evaluation Decision

### **PASS Requirements** (All must be true):
1. ✅ All 4 core criteria met (100/100 points)
2. ✅ All critical functionality working
3. ✅ Generated systems use SystemExecutionHarness architecture
4. ✅ Natural language → harness system pipeline functional
5. ✅ Integration with existing ValidationDrivenOrchestrator preserved
6. ✅ Performance targets met
7. ✅ Evidence quality standards met

### **FAIL Conditions** (Any one triggers fail):
- Core criteria score <90/100 points
- Any automatic fail condition met
- Generated systems don't use harness architecture
- End-to-end pipeline non-functional
- Integration broken
- Evidence quality insufficient

## Evaluation Report Template

```
PHASE 7 EXTERNAL EVALUATION REPORT
================================

Evaluation Date: [DATE]
Evaluator: External Agent (No Implementation Context)

CORE CRITERIA SCORES:
1. System Scaffold Generation: ___/25
2. Component Logic Generation: ___/25  
3. Orchestrator Integration: ___/25
4. End-to-End Pipeline: ___/25

TOTAL SCORE: ___/100

CRITICAL VERIFICATIONS:
□ Generated systems use SystemExecutionHarness (not Flask)
□ Generated components extend HarnessComponent
□ Natural language → harness system pipeline works
□ Integration with ValidationDrivenOrchestrator preserved
□ Performance targets met

EVIDENCE QUALITY:
□ All code executes successfully
□ Raw test outputs provided
□ Working demonstrations functional
□ Generated examples deployable

FINAL DECISION: [PASS/FAIL]

JUSTIFICATION:
[Detailed explanation based on objective evidence execution]

REMEDIATION REQUIRED (if FAIL):
[Specific items that must be fixed for PASS]
```

---

**NOTE**: This evaluation will be conducted by an isolated agent with no implementation context. Only evidence provided in `evidence/phase7_generation/` will be considered.