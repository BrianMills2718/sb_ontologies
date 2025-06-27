# EXCERPT showing the fallback anti-pattern in validation_framework.py

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
        
        # Initialize semantic validator (will use API key from env)
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
                # Fall back to mock mode if no API keys available
                self.logger.warning("No LLM API keys found, using mock mode for semantic validation")
                validator = SemanticValidator(mock_mode=True)
        
        # Also check for component skipping:
        if components_generated < total_components_in_blueprint:
            skipped_components = []
            supported_types = {"Source", "Transformer", "Sink", "Model", "Store", "APIEndpoint"}
            
            for component in system_blueprint.system.components:
                if component.type not in supported_types:
                    skipped_components.append(f"{component.name} ({component.type})")
            
            return ValidationResult(
                level="Level 4",
                passed=False,
                error_message=f"System incomplete: {len(skipped_components)} components skipped due to unsupported types: {', '.join(skipped_components)}",
                details={
                    "total_components": total_components_in_blueprint,
                    "components_generated": components_generated,
                    "skipped_components": skipped_components,
                    "unsupported_types": list(set(comp.type for comp in system_blueprint.system.components if comp.type not in supported_types))
                }
            )