# Phase 2: Multi-Purpose Vocabulary Extraction

**Implementation Agent Instructions - Completely Isolated**

You are implementing a comprehensive vocabulary extraction system that extracts theoretical terms supporting all five analytical purposes (descriptive, explanatory, predictive, causal, intervention) with equal sophistication.

## 🎯 **GOAL**
Create a vocabulary extraction system that comprehensively extracts theoretical terms for all purposes without causal over-emphasis.

## 📋 **IMPLEMENTATION REQUIREMENTS**

### **1. Create Multi-Purpose Vocabulary Extractor**
Location: `/home/brian/lit_review/evidence/phase2_vocabulary_extraction/vocabulary_extractor.py`

```python
class MultiPurposeVocabularyExtractor:
    """Balanced vocabulary extraction for all theoretical purposes"""
    
    def extract_comprehensive_vocabulary(self, theory_text: str, purposes: list) -> dict:
        """
        Extract vocabulary supporting all specified theoretical purposes
        Returns: {
            'descriptive_terms': dict,  # taxonomies, categories, classifications
            'explanatory_terms': dict,  # mechanisms, processes, structures
            'predictive_terms': dict,   # variables, models, forecasting elements
            'causal_terms': dict,       # relationships, pathways, interventions
            'intervention_terms': dict, # actions, implementations, strategies
            'cross_purpose_terms': dict,# terms serving multiple purposes
            'extraction_balance': dict  # balance metrics across purposes
        }
        """
        pass
    
    def extract_descriptive_vocabulary(self, theory_text: str) -> dict:
        """Extract taxonomic, typological, and classification terms"""
        pass
    
    def extract_explanatory_vocabulary(self, theory_text: str) -> dict:
        """Extract mechanism, process, and structural terms"""
        pass
    
    def extract_predictive_vocabulary(self, theory_text: str) -> dict:
        """Extract forecasting, variable, and model terms"""
        pass
    
    def extract_causal_vocabulary(self, theory_text: str) -> dict:
        """Extract causal relationship and intervention terms"""
        pass
    
    def extract_intervention_vocabulary(self, theory_text: str) -> dict:
        """Extract action, implementation, and strategy terms"""
        pass
    
    def ensure_extraction_balance(self, extracted_terms: dict) -> dict:
        """Validate balanced extraction across all purposes"""
        pass
```

### **2. Create Balanced Extraction Prompts**
Location: `/home/brian/lit_review/evidence/phase2_vocabulary_extraction/extraction_prompts.py`

Create extraction prompts that give equal attention to all five purposes.

### **3. Create Cross-Purpose Integration**
Location: `/home/brian/lit_review/evidence/phase2_vocabulary_extraction/cross_purpose_integration.py`

Handle terms that serve multiple theoretical purposes.

## 🧪 **TESTING REQUIREMENTS**
- Test 1: Descriptive vocabulary extraction (categories, classifications)
- Test 2: Explanatory vocabulary extraction (mechanisms, processes)
- Test 3: Predictive vocabulary extraction (variables, models)
- Test 4: Causal vocabulary extraction (relationships, pathways)
- Test 5: Intervention vocabulary extraction (actions, strategies)
- Test 6: Cross-purpose term identification
- Test 7: Extraction balance validation (equal comprehensiveness)
- Test 8: Multi-purpose theory vocabulary handling

## 📦 **DELIVERABLES**
Create evidence package at: `/home/brian/lit_review/evidence/phase2_vocabulary_extraction/`

### **Required Files**:
**CRITICAL**: You MUST create ALL of these files or evaluation will FAIL

1. **implementation_summary.md** - Technical overview of balanced extraction
2. **test_results.txt** - All test outputs showing balanced vocabulary extraction
3. **working_implementation.py** - Standalone demonstration script
4. **vocabulary_extractor.py** - Main extractor implementation
5. **extraction_prompts.py** - Balanced extraction prompts
6. **cross_purpose_integration.py** - Multi-purpose term handling
7. **test_vocabulary_extraction.py** - Comprehensive test suite
8. **extraction_balance_report.md** - Evidence of equal comprehensiveness

## ✅ **SUCCESS CRITERIA (100/100 REQUIRED)**
1. **Balanced Extraction**: Equal comprehensiveness across all five purposes
2. **No Single-Purpose Bias**: No over-emphasis on any particular purpose
3. **Cross-Purpose Integration**: Handles terms serving multiple purposes
4. **Comprehensive Coverage**: Extracts complete theoretical vocabulary
5. **Production Ready**: Clean, efficient, documented implementation

**CRITICAL BALANCE REQUIREMENT**: The system must demonstrate equal extraction comprehensiveness for descriptive, explanatory, predictive, causal, and intervention vocabulary. Any single-purpose bias will result in FAILURE.