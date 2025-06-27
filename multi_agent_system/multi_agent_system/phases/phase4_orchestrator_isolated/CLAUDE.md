# Phase 4: ValidationDrivenOrchestrator - ISOLATED IMPLEMENTATION

**CONTEXT**: You are implementing Phase 4 ValidationDrivenOrchestrator with ZERO knowledge of other phases. Focus ONLY on Phase 4 requirements.

**PREVIOUS ATTEMPT**: This phase previously FAILED external evaluation with critical integration failures. Read `evaluation_feedback.md` in this directory for specific feedback.

**INTEGRATION**: Phase 2 (Enhanced Component Library) and Phase 3 (Blueprint Schema V5) are complete and available for integration.

**EVIDENCE LOCATION**: All output must be saved to `evidence/phase4_validation_orchestrator/`

## Phase 4 Objective

Implement the ValidationDrivenOrchestrator as the central organizing principle of V5.0 architecture with fail-hard dependency checking and four-tier validation hierarchy, integrating with completed Phase 2 and Phase 3 systems.

## Success Criteria (100% Required)

1. **ValidationDrivenOrchestrator Core** - Central orchestration with four-tier validation
2. **Pre-flight Dependency Validation** - Fail-hard dependency checking before validation begins
3. **AST Healing Integration** - Level 2 component logic healing from Phase 1
4. **Configuration Regeneration** - Level 3 integration failure handling (safer than modification)
5. **Semantic Healing Integration** - Level 4 semantic validation with LLM healing
6. **Phase 2 Component Integration** - Integration with enhanced component library
7. **Phase 3 Blueprint Integration** - Integration with V5.0 blueprint schema system
8. **Complete Integration Tests** - All validation levels working together
9. **Performance Validation** - Production-ready performance characteristics

## Required Evidence Structure

```
evidence/phase4_validation_orchestrator/
├── validation_driven_orchestrator.py      # Core orchestrator system
├── dependency_checker.py                  # Pre-flight dependency validation
├── validation_result_types.py             # Result type definitions
├── level1_framework_integration.py        # Level 1 framework validation
├── level2_component_integration.py        # Level 2 component logic + AST healing
├── level3_system_integration.py           # Level 3 system integration + config regen
├── level4_semantic_integration.py         # Level 4 semantic validation + healing
├── phase2_integration.py                  # Phase 2 component library integration
├── phase3_integration.py                  # Phase 3 blueprint schema integration
├── healing_orchestration.py               # Coordinated healing systems
├── integration_tests.py                   # Complete integration test suite
├── test_results.txt                       # All test execution results
└── implementation_summary.md              # Complete implementation documentation
```

## Implementation Requirements

### 1. ValidationDrivenOrchestrator Core
```python
class ValidationDrivenOrchestrator:
    """Central orchestrator implementing four-tier validation hierarchy with fail-hard principles"""
    
    def __init__(self):
        self.development_mode = True  # Always fail hard during development
        self.dependency_checker = ValidationDependencyChecker()
        self.level_validators = self._initialize_level_validators()
        self.healers = self._initialize_healers()
        
    async def generate_system_with_validation(self, blueprint: SystemBlueprint):
        """Validation-driven system generation pipeline - NO FALLBACKS"""
        
        # Pre-flight: Validate all dependencies are available
        await self.dependency_checker.validate_all_dependencies_configured(blueprint)
        
        # Level 1: Framework Unit Testing
        level1_result = await self._execute_level1_validation()
        
        # Level 2: Component Logic Validation (with healing if needed)
        level2_result = await self._execute_level2_validation(blueprint, level1_result)
        
        # Level 3: System Integration Testing (with config regeneration if needed)
        level3_result = await self._execute_level3_validation(blueprint, level2_result)
        
        # Level 4: Semantic Validation (with semantic healing if needed)
        level4_result = await self._execute_level4_validation(blueprint, level3_result)
        
        return self._finalize_system_generation(blueprint, level4_result)
```

### 2. Four-Tier Validation Hierarchy

**Level 1: Framework Validation**
- Validate Autocoder framework itself
- Unit test framework components
- Fail hard on framework issues

**Level 2: Component Logic Validation + AST Healing**
- Validate component logic using Phase 2 systems
- Integrate with Phase 1 AST healing on failures
- Re-validate after healing

**Level 3: System Integration + Configuration Regeneration**
- Test system integration with real services
- Regenerate configuration (safer than modification) on failures
- Re-validate with new configuration

**Level 4: Semantic Validation + Semantic Healing**
- Use Phase 3 blueprint reasonableness checks for semantic validation
- Integrate with Phase 1 semantic healing on failures
- Require LLM availability (fail hard if not configured)

### 3. Phase Integration Requirements

**Phase 2 Integration:**
```python
async def _integrate_with_phase2_components(self, blueprint: SystemBlueprint):
    """Integrate with Phase 2 enhanced component library"""
    from evidence.phase2_component_library.component_registry import ComponentRegistry
    from evidence.phase2_component_library.schema_framework import SchemaFramework
    
    self.component_registry = ComponentRegistry()
    self.schema_framework = SchemaFramework()
    
    # Validate all blueprint components are registered
    for component in blueprint.components:
        if not self.component_registry.is_component_registered(component.type):
            raise ValidationDependencyError(
                f"Component type '{component.type}' not found in Phase 2 component registry"
            )
```

**Phase 3 Integration:**
```python
async def _integrate_with_phase3_blueprint_schema(self, blueprint_path: str):
    """Integrate with Phase 3 V5.0 blueprint schema system"""
    from evidence.phase3_blueprint_schema.schema_parser import parse_and_validate_blueprint
    from evidence.phase3_blueprint_schema.reasonableness_checks import ReasonablenessValidator
    
    # Parse blueprint using Phase 3 schema parser
    blueprint, validation_result = parse_and_validate_blueprint(blueprint_path)
    
    if not validation_result.is_valid:
        raise BlueprintValidationError(
            f"Blueprint failed Phase 3 schema validation: {validation_result.errors}"
        )
    
    return blueprint
```

### 4. Healing System Orchestration

**AST Healing (Level 2):**
```python
async def _execute_level2_validation_with_healing(self, blueprint, level1_result):
    """Level 2 with AST healing integration"""
    if not level1_result.passed:
        raise ValidationSequenceError("Level 2 cannot proceed - Level 1 validation failed")
    
    for component in blueprint.components:
        logic_result = await self.component_validator.validate_component_logic(component)
        
        if not logic_result.passed:
            # Trigger AST healing
            healed_result = await self.ast_healer.heal_component_logic(component, logic_result.failures)
            
            if healed_result.healing_successful:
                # Re-validate after healing
                retry_result = await self.component_validator.validate_component_logic(healed_result.healed_component)
                if not retry_result.passed:
                    raise ComponentLogicValidationError("Component logic validation failed even after AST healing")
            else:
                raise ComponentLogicValidationError("Component logic validation failed and AST healing was unsuccessful")
```

**Semantic Healing (Level 4):**
```python
async def _execute_level4_validation_with_healing(self, blueprint, level3_result):
    """Level 4 with semantic healing integration"""
    if not level3_result.passed:
        raise ValidationSequenceError("Level 4 cannot proceed - Level 3 validation failed")
    
    # Use Phase 3 reasonableness checks for semantic validation
    semantic_result = await self.semantic_validator.validate_system_semantics(blueprint)
    
    if not semantic_result.passed:
        # Trigger semantic healing
        healed_result = await self.semantic_healer.heal_system_semantics(blueprint, semantic_result.failures)
        
        if healed_result.healing_successful:
            # Re-validate after semantic healing
            retry_result = await self.semantic_validator.validate_system_semantics(healed_result.healed_blueprint)
            if not retry_result.passed:
                raise SemanticValidationError("Semantic validation failed even after semantic healing")
        else:
            raise SemanticValidationError("Semantic validation failed and semantic healing was unsuccessful")
```

## Critical Requirements

- **NO mock modes or fallback mechanisms** - All validation must be real
- **Fail-hard validation** - Any validation failure must stop the process
- **Complete Phase 2-3 integration** - Must use actual Phase 2-3 systems
- **All four validation levels must work** - No level can be skipped or mocked
- **Evidence-based success** - Every claim must be backed by evidence files

## Completion Criteria

Phase 4 is complete when:
1. All evidence files are present and complete
2. ValidationDrivenOrchestrator orchestrates all four validation levels
3. Phase 2 component library integration works seamlessly
4. Phase 3 blueprint schema integration works seamlessly  
5. All healing systems are orchestrated correctly
6. Integration tests demonstrate complete functionality
7. Performance meets production requirements
8. External evaluator can verify 100% success from evidence alone

**IMPORTANT**: Focus ONLY on Phase 4. Integrate with completed Phase 2 and Phase 3 systems. Implement complete, working ValidationDrivenOrchestrator with full evidence package.