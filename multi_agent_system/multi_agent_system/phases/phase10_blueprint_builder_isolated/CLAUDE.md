# Phase 10: Deterministic Blueprint Builder Implementation

**Implementation Agent Instructions - Completely Isolated**

You are implementing the Deterministic Blueprint Builder that converts semantic intent from Phase 9 into valid YAML blueprints without LLM involvement.

## 🎯 **GOAL**
Create a deterministic blueprint builder that:
1. Takes semantic intent JSON from Phase 9 Semantic Extractor
2. Builds valid YAML blueprints using deterministic logic (NO LLM)
3. Ensures 100% valid schema compliance
4. Eliminates YAML syntax errors and schema violations

## 📋 **IMPLEMENTATION REQUIREMENTS**

### **1. Create Deterministic Blueprint Builder**
Location: `/home/brian/autocoder3_cc/blueprint_language/deterministic_builder.py`

```python
class DeterministicBlueprintBuilder:
    """Build valid YAML blueprints from semantic intent without LLM"""
    
    def __init__(self, schema_path: str = None):
        # Load blueprint schema for validation
        self.schema = self._load_schema(schema_path)
        self.component_templates = self._load_component_templates()
        
    def build_blueprint(self, intent: Dict) -> str:
        """
        Convert semantic intent to valid blueprint YAML
        
        Args:
            intent: JSON from Phase 9 semantic extractor
            
        Returns:
            Valid YAML blueprint string
        """
        blueprint = {
            "name": self._sanitize_name(intent["system_name"]),
            "version": "1.0.0",
            "description": intent["description"],
            "components": {},
            "bindings": []
        }
        
        # Add components based on intent
        if intent.get("needs_api"):
            blueprint["components"]["api"] = self._build_api_component(intent)
        
        if intent.get("needs_database"):
            blueprint["components"]["store"] = self._build_store_component(intent)
            
        if intent.get("needs_ui"):
            self._add_ui_routes(blueprint["components"].get("api", {}))
            
        # Add bindings only if multiple components
        if len(blueprint["components"]) > 1:
            blueprint["bindings"] = self._build_bindings(blueprint["components"])
            
        # Validate against schema
        self._validate_blueprint(blueprint)
        
        return yaml.dump(blueprint, sort_keys=False, default_flow_style=False)
        
    def _build_api_component(self, intent: Dict) -> Dict:
        """Build APIEndpoint component from intent"""
        pass
        
    def _build_store_component(self, intent: Dict) -> Dict:
        """Build Store component from intent"""
        pass
        
    def _build_bindings(self, components: Dict) -> List[Dict]:
        """Build component bindings deterministically"""
        pass
        
    def _validate_blueprint(self, blueprint: Dict) -> None:
        """Validate blueprint against schema"""
        pass
```

### **2. Create Schema Integration**
Location: `/home/brian/autocoder3_cc/blueprint_language/schema_validator.py`

```python
class BlueprintSchemaValidator:
    """Validate blueprints against schema"""
    
    def validate_blueprint(self, blueprint: Dict) -> Tuple[bool, List[str]]:
        """Validate blueprint structure and content"""
        pass
        
    def validate_component(self, component: Dict, component_type: str) -> bool:
        """Validate individual component"""
        pass
```

### **3. Integration with Phase 9**
Location: `/home/brian/autocoder3_cc/blueprint_language/hybrid_generator.py`

```python
class HybridBlueprintGenerator:
    """Combines Phase 9 + Phase 10 for complete pipeline"""
    
    def __init__(self):
        self.semantic_extractor = SemanticExtractor()
        self.blueprint_builder = DeterministicBlueprintBuilder()
        
    def generate_blueprint(self, natural_language: str) -> str:
        """Complete pipeline: NL → Intent → Blueprint"""
        # Phase 9: Extract semantic intent
        intent = self.semantic_extractor.extract_intent(natural_language)
        
        # Phase 10: Build blueprint deterministically  
        blueprint = self.blueprint_builder.build_blueprint(intent)
        
        return blueprint
```

### **4. Component Templates**
Create templates for each component type:
- APIEndpoint templates with common route patterns
- Store templates for different database types
- UI route templates
- Integration templates

## 🧪 **TESTING REQUIREMENTS**

### **Unit Tests**
- Test blueprint construction for each component type
- Test schema validation logic
- Test edge cases (empty intent, malformed intent)
- Test YAML syntax validity

### **Integration Tests**
- Test complete NL → Intent → Blueprint pipeline
- Test with all Phase 9 test cases
- Verify 100% valid YAML output
- Test against current blueprint schema

### **Validation Tests**
- Every generated blueprint must pass schema validation
- No YAML syntax errors allowed
- All required fields present
- Component types must be valid

## 📦 **DELIVERABLES**

Create evidence package at: `/home/brian/autocoder3_cc/evidence/phase10_blueprint_builder/`

### **Required Files**:
**CRITICAL**: You MUST create ALL of these files or evaluation will FAIL

1. **implementation_summary.md** - Complete technical overview
2. **test_results.txt** - All test outputs proving 100% functionality
3. **integration_test_results.json** - Structured test results  
4. **schema_validation_results.txt** - Schema compliance verification
5. **pipeline_demo_output.txt** - Complete NL → Blueprint demo
6. **working_implementation.py** - Standalone implementation for evaluation
7. **comparison_analysis.md** - Before/after LLM vs deterministic comparison

### **Code Requirements**:
- All code must be production-ready with comprehensive error handling
- Complete docstrings and type hints
- Follow existing codebase patterns
- Integrate seamlessly with Phase 9 output

## 🚫 **CONSTRAINTS**

- NO LLM usage in blueprint construction (only Phase 9 does LLM)
- Must work with ALL Phase 9 semantic intent outputs
- Cannot modify Phase 9 - only consume its output
- Must generate 100% valid YAML (zero tolerance for syntax errors)
- Must pass schema validation every time

## ✅ **SUCCESS CRITERIA (100/100 REQUIRED)**

1. **Functional**: 100% valid blueprint generation from semantic intent
2. **Schema Compliance**: Every blueprint passes schema validation
3. **YAML Validity**: Zero syntax errors in generated YAML
4. **Integration**: Seamless pipeline with Phase 9
5. **Performance**: <1 second for blueprint construction
6. **Deterministic**: Same input always produces identical output
7. **Comprehensive**: Handles all component types and complexity levels

## 🎬 **EVIDENCE REQUIREMENTS**

Your evidence must prove:
- Deterministic builder generates valid blueprints from Phase 9 intent
- 100% schema compliance rate
- Complete NL → Intent → Blueprint pipeline working
- Performance meets requirements
- External evaluator can verify all claims

All code must be executable by external evaluator without additional setup beyond Phase 9 dependencies.

## 🔄 **AUTO-PROGRESSION AFTER PASS**

Upon achieving 100/100:
- Evidence will be automatically archived
- Phase 11 (Blueprint Integration Testing) will auto-launch
- No manual intervention required for progression