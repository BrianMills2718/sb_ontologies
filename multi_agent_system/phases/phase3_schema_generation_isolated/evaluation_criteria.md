# Evaluation Criteria: Multi-Purpose Schema Generation

**Success Threshold**: Must achieve exactly 100/100 points to PASS

## 📊 **EVALUATION CRITERIA**

### **1. Equal Schema Capabilities (25 points)**
**Test schema generation across all purposes:**
```bash
cd /home/brian/lit_review/evidence/phase3_schema_generation
python working_implementation.py
```

**Scoring**:
- 25 points: Generated schemas provide equal analytical sophistication for descriptive, explanatory, predictive, causal, and intervention purposes
- 0 points: Any purpose showing significantly stronger or weaker schema capabilities

### **2. Cross-Purpose Integration (25 points)**
**Test multi-purpose schema handling:**
```bash
python test_schema_generation.py --test-multi-purpose
```

**Scoring**:
- 25 points: Schemas effectively integrate capabilities across multiple purposes
- 0 points: Poor integration or conflicting purpose capabilities

### **3. Schema Template Balance (25 points)**
**Validate balanced templates:**
```bash
python test_schema_generation.py --validate-templates
```

**Scoring**:
- 25 points: All schema templates provide equal support for all purposes
- 0 points: Templates biased toward particular purposes

### **4. Comprehensive Generation (25 points)**
**Run full generation test suite:**
```bash
python -m pytest /home/brian/lit_review/evidence/phase3_schema_generation/ -v
```

**Scoring**:
- 25 points: Complete schema generation with comprehensive coverage
- 0 points: Incomplete generation or failed tests

## ✅ **PASS CRITERIA**
**PASS (100 points ONLY)**: Perfect balanced schema generation system
**FAIL (<100 points)**: Any capability imbalance, template bias, or generation failures

## 📋 **VALIDATION CHECKLIST**
- [ ] Equal analytical capabilities across all five purposes in generated schemas
- [ ] Cross-purpose integration working effectively
- [ ] Schema templates provide balanced support for all purposes
- [ ] Comprehensive schema generation for all model types
- [ ] Example schemas demonstrate balanced capabilities
- [ ] Schema balance report shows equal sophistication
- [ ] Production-ready implementation with clean architecture

Write evaluation to: `/home/brian/lit_review/multi_agent_system/phases/evaluation_clean/phase3_evaluation_result.md`