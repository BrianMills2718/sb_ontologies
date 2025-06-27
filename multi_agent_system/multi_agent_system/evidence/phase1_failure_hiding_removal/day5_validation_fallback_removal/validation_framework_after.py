# EXCERPT showing the fixed validation_framework.py without fallback anti-patterns

class ValidationFailureError(Exception):
    """Exception raised when validation configuration is invalid or missing"""
    pass

async def _level4_semantic_validation(self, system_blueprint: ParsedSystemBlueprint) -> ValidationResult:
    """
    Level 4: Semantic Validation (Business Logic Reasonableness)
    
    Validates that:
    - System outputs make business sense for the stated purpose
    - Component transformations are reasonable
    - Test data is domain-specific, not generic placeholders
    - No nonsensical or placeholder logic accepted
    """
    try:
        # Import SemanticValidator
        from .semantic_validator import SemanticValidator
        
        # Initialize semantic validator - fail hard if LLM not available
        validator = None
        try:
            validator = SemanticValidator(llm_provider="openai")
            self.logger.info("Using OpenAI for semantic validation")
        except Exception as e:
            # If OpenAI fails, try Anthropic
            try:
                validator = SemanticValidator(llm_provider="anthropic")
                self.logger.info("Using Anthropic for semantic validation")
            except Exception as e2:
                # Fail hard if no LLM configuration available
                raise ValidationFailureError(
                    "Level 4 semantic validation requires LLM configuration. "
                    "Set OPENAI_API_KEY or ANTHROPIC_API_KEY. "
                    "NO FALLBACK MODES AVAILABLE - this exposes real dependency issues."
                )
        
        # Also fixed component skipping:
        # Check if all components were successfully generated - fail hard for incomplete systems
        total_components_in_blueprint = len(system_blueprint.system.components)
        components_generated = len(components)

        if components_generated < total_components_in_blueprint:
            unsupported_components = []
            supported_types = {"Source", "Transformer", "Sink", "Model", "Store", "APIEndpoint"}
            
            for component in system_blueprint.system.components:
                if component.type not in supported_types:
                    unsupported_components.append(f"{component.name} ({component.type})")
            
            # Fail hard instead of allowing incomplete systems
            raise ValidationFailureError(
                f"System generation incomplete: {len(unsupported_components)} components have unsupported types: {', '.join(unsupported_components)}. "
                f"All component types must be supported. No component skipping allowed - this hides system incompleteness."
            )