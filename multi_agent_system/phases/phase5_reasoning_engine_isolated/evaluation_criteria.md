# Evaluation Criteria: Cross-Purpose Reasoning Engine

**Success Threshold**: Must achieve exactly 100/100 points to PASS

## 📊 **EVALUATION CRITERIA**

### **1. Equal Reasoning Sophistication (25 points)**
**Test reasoning across all five purposes:**
```bash
cd /home/brian/lit_review/evidence/phase5_reasoning_engine
python working_implementation.py
```

**Scoring**:
- 25 points: Equal analytical sophistication demonstrated for descriptive, explanatory, predictive, causal, and intervention reasoning
- 0 points: Any purpose showing significantly stronger or weaker reasoning capabilities

### **2. Cross-Purpose Integration (25 points)**
**Test integrated reasoning capabilities:**
```bash
python test_reasoning_engine.py --test-cross-purpose
```

**Scoring**:
- 25 points: Sophisticated reasoning that effectively integrates insights across multiple purposes
- 0 points: Poor integration or conflicting reasoning across purposes

### **3. Advanced Query Handling (25 points)**
**Test complex reasoning scenarios:**
```bash
python test_reasoning_engine.py --test-complex-queries
```

**Scoring**:
- 25 points: Handles complex multi-purpose queries with high-quality insights
- 0 points: Fails on complex queries or provides poor-quality reasoning

### **4. Performance and Production Readiness (25 points)**
**Test reasoning performance and robustness:**
```bash
python -m pytest /home/brian/lit_review/evidence/phase5_reasoning_engine/ -v
python test_reasoning_engine.py --performance-test
```

**Scoring**:
- 25 points: Excellent performance with production-ready implementation
- 0 points: Poor performance or implementation issues

## ✅ **PASS CRITERIA**
**PASS (100 points ONLY)**: Perfect cross-purpose reasoning engine
**FAIL (<100 points)**: Any reasoning imbalance, integration failures, or performance issues

## 📋 **VALIDATION CHECKLIST**
- [ ] Equal analytical sophistication across all five purposes
- [ ] Cross-purpose integration working effectively
- [ ] Complex multi-purpose queries handled successfully
- [ ] Excellent reasoning performance and efficiency
- [ ] Query examples demonstrate balanced capabilities
- [ ] Reasoning balance report shows equal analytical depth
- [ ] Production-ready implementation with robust architecture

Write evaluation to: `/home/brian/lit_review/multi_agent_system/phases/evaluation_clean/phase5_evaluation_result.md`