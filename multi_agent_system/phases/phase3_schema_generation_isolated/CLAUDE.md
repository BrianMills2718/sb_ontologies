# Phase 3: Multi-Purpose Schema Generation

**Implementation Agent Instructions - Completely Isolated**

You are implementing a schema generation system that creates schemas supporting all five analytical purposes (descriptive, explanatory, predictive, causal, intervention) with equal sophistication and capabilities.

## 🎯 **GOAL**
Create a schema generation system that produces schemas with equal analytical capabilities across all theoretical purposes.

## 📋 **IMPLEMENTATION REQUIREMENTS**

### **1. Create Multi-Purpose Schema Generator**
Location: `/home/brian/lit_review/evidence/phase3_schema_generation/schema_generator.py`

```python
class MultiPurposeSchemaGenerator:
    """Balanced schema generation for all theoretical purposes"""
    
    def generate_balanced_schema(self, vocabulary: dict, purposes: list, model_type: str) -> dict:
        """
        Generate schema with equal capabilities across all purposes
        Returns: {
            'model_type': str,
            'theoretical_purposes': dict,
            'schema_blueprint': dict,
            'purpose_capabilities': dict,  # equal capabilities for each purpose
            'cross_purpose_integration': dict,
            'balance_validation': dict
        }
        """
        pass
    
    def generate_descriptive_capabilities(self, vocabulary: dict) -> dict:
        """Generate taxonomic, typological, classification capabilities"""
        pass
    
    def generate_explanatory_capabilities(self, vocabulary: dict) -> dict:
        """Generate mechanism, process, structural analysis capabilities"""
        pass
    
    def generate_predictive_capabilities(self, vocabulary: dict) -> dict:
        """Generate forecasting, modeling, prediction capabilities"""
        pass
    
    def generate_causal_capabilities(self, vocabulary: dict) -> dict:
        """Generate causal analysis, intervention design capabilities"""
        pass
    
    def generate_intervention_capabilities(self, vocabulary: dict) -> dict:
        """Generate action, implementation, strategy capabilities"""
        pass
    
    def integrate_cross_purpose_capabilities(self, capabilities: dict) -> dict:
        """Integrate capabilities across multiple purposes"""
        pass
    
    def validate_schema_balance(self, schema: dict) -> dict:
        """Ensure equal sophistication across all purposes"""
        pass
```

### **2. Create Balanced Schema Templates**
Location: `/home/brian/lit_review/evidence/phase3_schema_generation/schema_templates.py`

Create templates that provide equal analytical sophistication for all purposes.

### **3. Create Purpose-Specific Enhancers**
Location: `/home/brian/lit_review/evidence/phase3_schema_generation/purpose_enhancers.py`

Implement enhancers that ensure equal capabilities across all purposes.

## 🧪 **TESTING REQUIREMENTS**
- Test 1: Descriptive schema generation (taxonomies, classifications)
- Test 2: Explanatory schema generation (mechanisms, processes)
- Test 3: Predictive schema generation (models, forecasting)
- Test 4: Causal schema generation (relationships, interventions)
- Test 5: Intervention schema generation (actions, implementation)
- Test 6: Multi-purpose schema integration
- Test 7: Cross-purpose capability validation
- Test 8: Schema balance verification (equal sophistication)

## 📦 **DELIVERABLES**
Create evidence package at: `/home/brian/lit_review/evidence/phase3_schema_generation/`

### **Required Files**:
**CRITICAL**: You MUST create ALL of these files or evaluation will FAIL

1. **implementation_summary.md** - Technical overview of balanced schema generation
2. **test_results.txt** - All test outputs showing balanced schema capabilities
3. **working_implementation.py** - Standalone demonstration script
4. **schema_generator.py** - Main generator implementation
5. **schema_templates.py** - Balanced schema templates
6. **purpose_enhancers.py** - Equal-sophistication enhancers
7. **test_schema_generation.py** - Comprehensive test suite
8. **schema_balance_report.md** - Evidence of equal capabilities across purposes
9. **example_schemas/** - Example schemas demonstrating balance

## ✅ **SUCCESS CRITERIA (100/100 REQUIRED)**
1. **Equal Schema Capabilities**: Schemas provide equal analytical sophistication for all five purposes
2. **Balanced Templates**: Schema templates support all purposes equally
3. **Cross-Purpose Integration**: Schemas handle multi-purpose theories effectively
4. **Comprehensive Coverage**: Complete schema generation for all model types
5. **Production Ready**: Clean, extensible, well-documented implementation

**CRITICAL BALANCE REQUIREMENT**: Generated schemas must demonstrate equal analytical capabilities for descriptive, explanatory, predictive, causal, and intervention purposes. Any capability imbalance will result in FAILURE.