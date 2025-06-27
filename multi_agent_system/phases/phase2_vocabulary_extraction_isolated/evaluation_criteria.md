# Evaluation Criteria: Multi-Purpose Vocabulary Extraction

**Success Threshold**: Must achieve exactly 100/100 points to PASS

## 📊 **EVALUATION CRITERIA**

### **1. Balanced Vocabulary Extraction (25 points)**
**Test extraction across all five purposes:**
```bash
cd /home/brian/lit_review/evidence/phase2_vocabulary_extraction
python working_implementation.py
```

**Scoring**:
- 25 points: Equal comprehensiveness across descriptive, explanatory, predictive, causal, and intervention vocabulary
- 0 points: Any purpose showing significantly more or less extraction depth

### **2. Cross-Purpose Integration (25 points)**
**Test multi-purpose term handling:**
```bash
python test_vocabulary_extraction.py --test-cross-purpose
```

**Scoring**:
- 25 points: Accurately identifies and handles terms serving multiple purposes
- 0 points: Fails to properly integrate cross-purpose terms

### **3. Extraction Comprehensiveness (25 points)**
**Run comprehensive extraction tests:**
```bash
python -m pytest /home/brian/lit_review/evidence/phase2_vocabulary_extraction/ -v
```

**Scoring**:
- 25 points: Complete vocabulary extraction with high coverage across all purposes
- 0 points: Incomplete extraction or missed vocabulary categories

### **4. Balance Validation (25 points)**
**Verify no single-purpose bias:**
```bash
python test_vocabulary_extraction.py --validate-balance
```

**Scoring**:
- 25 points: Extraction balance report shows equal treatment across all purposes
- 0 points: Evidence of bias toward any single purpose

## ✅ **PASS CRITERIA**
**PASS (100 points ONLY)**: Perfect balanced vocabulary extraction system
**FAIL (<100 points)**: Any extraction imbalance, bias, or incompleteness

## 📋 **VALIDATION CHECKLIST**
- [ ] Equal extraction comprehensiveness across all five purposes
- [ ] Cross-purpose terms properly identified and integrated
- [ ] Complete vocabulary coverage for each theoretical purpose
- [ ] No single-purpose bias in extraction depth or quality
- [ ] Balance validation report demonstrates equal treatment
- [ ] Production-ready implementation with efficient extraction

Write evaluation to: `/home/brian/lit_review/multi_agent_system/phases/evaluation_clean/phase2_evaluation_result.md`