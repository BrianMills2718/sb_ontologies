# Phase 1: Purpose Classification System

**Implementation Agent Instructions - Completely Isolated**

You are implementing a balanced purpose classification system for computational social science theories that treats descriptive, explanatory, predictive, causal, and intervention modeling with equal sophistication.

## 🎯 **GOAL**
Create a purpose classification system that identifies theoretical purposes with equal emphasis across all five analytical approaches, eliminating causal over-emphasis.

## 📋 **IMPLEMENTATION REQUIREMENTS**

### **1. Create Purpose Classifier Component**
Location: `/home/brian/lit_review/evidence/phase1_purpose_classification/purpose_classifier.py`

```python
class PurposeClassifier:
    """Balanced purpose classification for computational social science theories"""
    
    def classify_theory_purposes(self, theory_text: str) -> dict:
        """
        Classify theory purposes with equal sophistication across all types
        Returns: {
            'primary_purpose': str,  # descriptive|explanatory|predictive|causal|intervention
            'secondary_purposes': List[str],
            'purpose_confidence': dict,  # confidence scores for each purpose
            'balanced_analysis': dict  # analysis ensuring equal treatment
        }
        """
        pass
    
    def detect_descriptive_elements(self, theory_text: str) -> dict:
        """Extract taxonomies, typologies, classification systems"""
        pass
    
    def detect_explanatory_elements(self, theory_text: str) -> dict:
        """Extract mechanisms, processes, structural relationships"""
        pass
    
    def detect_predictive_elements(self, theory_text: str) -> dict:
        """Extract forecasting capabilities, variable specifications"""
        pass
    
    def detect_causal_elements(self, theory_text: str) -> dict:
        """Extract causal relationships, intervention points"""
        pass
    
    def detect_intervention_elements(self, theory_text: str) -> dict:
        """Extract action specifications, implementation strategies"""
        pass
    
    def ensure_balanced_analysis(self, purpose_scores: dict) -> dict:
        """Ensure no single purpose is over-emphasized"""
        pass
```

### **2. Create Balanced Detection Prompts**
Location: `/home/brian/lit_review/evidence/phase1_purpose_classification/balanced_prompts.py`

Create detection prompts that give equal sophistication to all five purposes.

### **3. Create Test Framework**
Location: `/home/brian/lit_review/evidence/phase1_purpose_classification/test_purpose_classification.py`

Test with examples across all five purposes to ensure balanced treatment.

## 🧪 **TESTING REQUIREMENTS**
- Test 1: Descriptive theory identification (taxonomies, typologies)
- Test 2: Explanatory theory identification (mechanisms, processes)  
- Test 3: Predictive theory identification (forecasting, variables)
- Test 4: Causal theory identification (relationships, interventions)
- Test 5: Intervention theory identification (actions, implementation)
- Test 6: Multi-purpose theory handling
- Test 7: Balance validation (no causal over-emphasis)

## 📦 **DELIVERABLES**
Create evidence package at: `/home/brian/lit_review/evidence/phase1_purpose_classification/`

### **Required Files**:
**CRITICAL**: You MUST create ALL of these files or evaluation will FAIL

1. **implementation_summary.md** - Technical overview of balanced approach
2. **test_results.txt** - All test outputs showing balanced classification
3. **working_implementation.py** - Standalone demonstration script
4. **purpose_classifier.py** - Main classifier implementation
5. **balanced_prompts.py** - Equal-sophistication detection prompts
6. **test_purpose_classification.py** - Comprehensive test suite
7. **balance_validation_report.md** - Evidence of equal treatment across purposes

## ✅ **SUCCESS CRITERIA (100/100 REQUIRED)**
1. **Balanced Classification**: Equal sophistication across all five purposes (descriptive/explanatory/predictive/causal/intervention)
2. **No Causal Over-Emphasis**: Causal analysis treated equally with other purposes
3. **Comprehensive Detection**: Accurate identification of all purpose types
4. **Multi-Purpose Support**: Handles theories serving multiple purposes
5. **Production Ready**: Clean, testable, documented implementation

**CRITICAL BALANCE REQUIREMENT**: The system must demonstrate equal analytical sophistication for descriptive, explanatory, predictive, causal, and intervention purposes. Any causal over-emphasis will result in FAILURE.