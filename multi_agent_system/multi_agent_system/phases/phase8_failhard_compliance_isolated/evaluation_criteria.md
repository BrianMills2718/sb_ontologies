# Phase 8 External Evaluation Criteria: Fail-Hard Compliance & LLM-Native Architecture

**EXTERNAL EVALUATOR INSTRUCTIONS**

## 🎯 EVALUATION OBJECTIVE
Verify that V5.1 autocoder implements true fail-hard compliance with zero lazy fallbacks and 100% LLM-native operation.

## 📋 EVALUATION CHECKLIST

### **1. Lazy Fallback Elimination** [40 points]

#### **A. Blueprint Generation [15 points]**
- [ ] **5 pts**: `blueprint_language/natural_language_to_blueprint.py` has NO `_generate_mock_intermediate` method
- [ ] **5 pts**: No mock blueprint generation capability exists anywhere in codebase
- [ ] **5 pts**: All blueprint generation requires LLM and fails hard when unavailable

#### **B. Test Generator [10 points]**  
- [ ] **5 pts**: `blueprint_language/test_generator.py` fails hard when LLM unavailable for test generation
- [ ] **3 pts**: No fallback to mock test data in production scenarios
- [ ] **2 pts**: Strategic test mocks (if any) are clearly labeled and justified for testing isolation only

#### **C. Base Component Implementations [15 points]**
- [ ] **5 pts**: `autocoder/components/source.py` `_generate_data` raises `NotImplementedError` instead of providing sample data
- [ ] **3 pts**: `autocoder/components/transformer.py` `_transform_data` raises `NotImplementedError`
- [ ] **3 pts**: `autocoder/components/sink.py` `_output_data` raises `NotImplementedError`  
- [ ] **2 pts**: `autocoder/components/model.py` `_run_inference` raises `NotImplementedError`
- [ ] **2 pts**: All base components fail hard when generation doesn't override required methods

### **2. Production Validation Quality** [25 points]

#### **A. Test Pass Rate [15 points]**
- [ ] **10 pts**: Production validation achieves 100% test pass rate (not 50%)
- [ ] **3 pts**: `v5_health_check` test passes completely
- [ ] **2 pts**: `load_testing` test passes with acceptable performance metrics

#### **B. Generated System Quality [10 points]**
- [ ] **5 pts**: All generated components in `examples/task_management_api/components/` properly override base methods
- [ ] **3 pts**: No generated component relies on default implementations
- [ ] **2 pts**: Generated system demonstrates complete, production-ready functionality

### **3. Security & Environment Handling** [15 points]

#### **A. Environment-Aware Configuration [10 points]**
- [ ] **5 pts**: Production environment detection fails hard when secrets missing
- [ ] **3 pts**: Development environment provides convenient defaults
- [ ] **2 pts**: Clear distinction between production vs development behavior

#### **B. No Insecure Defaults [5 points]**
- [ ] **3 pts**: No hardcoded secrets in production paths
- [ ] **2 pts**: All security-sensitive defaults are environment-aware

### **4. Test Infrastructure** [10 points]

#### **A. Valid Test Scenarios [7 points]**
- [ ] **4 pts**: No tests for "no LLM available" scenario (invalid for LLM-native system)
- [ ] **3 pts**: Tests cover proper LLM failure scenarios (invalid keys, network failures, rate limiting)

#### **B. Test Execution [3 points]**
- [ ] **2 pts**: All fail-hard compliance tests execute successfully
- [ ] **1 pt**: 100% test pass rate in test suite

### **5. LLM-Native Verification** [10 points]

#### **A. LLM Dependency Verification [7 points]**
- [ ] **4 pts**: Blueprint generation fails immediately without valid LLM
- [ ] **3 pts**: Component generation fails immediately without valid LLM

#### **B. Error Quality [3 points]**
- [ ] **2 pts**: Clear, informative error messages when LLM unavailable
- [ ] **1 pt**: No degraded functionality modes available

## 🔍 TESTING METHODOLOGY

### **Required Tests**:

1. **Lazy Fallback Detection**:
   ```bash
   # Search for any remaining fallback patterns
   grep -r "fallback\|mock.*when\|if.*not.*available" . --include="*.py"
   ```

2. **LLM Dependency Test**:
   ```bash
   # Test blueprint generation without LLM
   export OPENAI_API_KEY=""
   export ANTHROPIC_API_KEY=""
   python -c "from blueprint_language.natural_language_to_blueprint import *; ..."
   # Should fail hard, not provide fallback
   ```

3. **Base Component Test**:
   ```python
   # Test that base components fail hard
   from autocoder.components.source import Source
   s = Source("test")
   # This should raise NotImplementedError
   await s._generate_data({})
   ```

4. **Production Validation**:
   ```bash
   # Run full production validation
   python production_validation.py
   # Must achieve 100% pass rate
   ```

## 📊 SCORING

### **Grade Scale**:
- **90-100 points**: PASS - True fail-hard compliance achieved
- **80-89 points**: PARTIAL - Major issues remain, remediation required
- **Below 80 points**: FAIL - Fundamental fail-hard violations

### **Critical Requirements** (Must achieve ALL for PASS):
- [ ] **Zero lazy fallbacks**: No mock modes or degraded functionality
- [ ] **100% production tests**: All validation tests pass
- [ ] **Complete LLM-native**: All core functions require LLM
- [ ] **Proper error handling**: Clear failures when dependencies missing

## 🚫 AUTOMATIC FAIL CONDITIONS

The following conditions result in immediate FAIL regardless of other scores:
- Any mock blueprint generation capability exists
- Any base component provides sample data instead of failing
- Production validation pass rate below 100%
- Any "no LLM available" operational mode exists
- Any security-sensitive hardcoded defaults in production

## 📝 EVALUATION REPORT FORMAT

```markdown
# Phase 8 Evaluation: Fail-Hard Compliance

**Overall Result**: [PASS/PARTIAL/FAIL]
**Score**: [X]/100 points

## Section Scores:
1. Lazy Fallback Elimination: [X]/40
2. Production Validation Quality: [X]/25  
3. Security & Environment Handling: [X]/15
4. Test Infrastructure: [X]/10
5. LLM-Native Verification: [X]/10

## Critical Issues Found:
- [List any critical violations]

## Recommendations:
- [Specific fixes needed for PASS]
```

This evaluation ensures V5.1 achieves true fail-hard compliance with zero compromise on quality or functionality.