#!/usr/bin/env python3
"""
Semantic Healer for Autocoder v5.0

Uses LLM to fix business logic issues:
- Corrects unreasonable transformations
- Enhances test data to be domain-specific
- Injects output validation
- Fixes business logic errors
"""

import logging
import ast
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import os

# Import semantic validator for reasonableness checking
try:
    from blueprint_language.semantic_validator import SemanticValidator
    HAS_SEMANTIC_VALIDATOR = True
except ImportError:
    HAS_SEMANTIC_VALIDATOR = False

# Check for LLM libraries
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class SemanticHealingConfigurationError(Exception):
    """Exception raised when semantic healing configuration is invalid or missing"""
    pass


@dataclass
class SemanticHealingResult:
    """Result of semantic healing operation"""
    success: bool
    original_code: str
    healed_code: str
    reasoning: str
    changes_made: List[str]
    error_message: Optional[str] = None


class SemanticHealer:
    """
    Heals business logic issues using LLM reasoning.
    
    Focuses on:
    - Business logic corrections
    - Domain-specific test data generation
    - Output validation injection
    - Placeholder detection and replacement
    """
    
    def __init__(self, llm_provider: str = "openai", api_key: Optional[str] = None):
        self.logger = logging.getLogger("SemanticHealer")
        self.llm_provider = llm_provider
        
        # Fail hard if LLM configuration is missing
        if not self._is_llm_available():
            raise SemanticHealingConfigurationError(
                "Semantic healing requires LLM configuration. "
                "Set OPENAI_API_KEY or ANTHROPIC_API_KEY. "
                "NO MOCK MODES AVAILABLE - this exposes real dependency issues."
            )
        
        # Initialize LLM client
        self.logger.info("🤖 SEMANTIC HEALER USING LLM MODE")
        if llm_provider == "openai" and HAS_OPENAI:
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                raise SemanticHealingConfigurationError("OpenAI API key required for semantic healing")
            self.client = openai.OpenAI(api_key=self.api_key)
            self.model = os.environ.get("OPENAI_MODEL", "o3")
        elif llm_provider == "anthropic" and HAS_ANTHROPIC:
            self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise SemanticHealingConfigurationError("Anthropic API key required for semantic healing")
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = os.environ.get("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        else:
            raise SemanticHealingConfigurationError(f"Unsupported or unavailable LLM provider: {llm_provider}")
        
        # Initialize semantic validator if available
        self.semantic_validator = None
        if HAS_SEMANTIC_VALIDATOR:
            try:
                self.semantic_validator = SemanticValidator(llm_provider, api_key)
            except:
                self.logger.warning("Could not initialize semantic validator")
    
    def _is_llm_available(self) -> bool:
        """Check if LLM configuration is available"""
        return (
            (HAS_OPENAI and os.environ.get("OPENAI_API_KEY")) or
            (HAS_ANTHROPIC and os.environ.get("ANTHROPIC_API_KEY"))
        )
    
    def heal_business_logic(self, code: str, component_purpose: str, 
                          input_schema: Dict[str, Any], output_schema: Dict[str, Any]) -> SemanticHealingResult:
        """
        Fix business logic issues in component code.
        
        Args:
            code: Component code with potential logic issues
            component_purpose: What the component should do
            input_schema: Expected input data schema
            output_schema: Expected output data schema
            
        Returns:
            SemanticHealingResult with corrected business logic
        """
        self.logger.debug("🤖 PERFORMING LLM-ENHANCED SEMANTIC HEALING")
        prompt = f"""You are fixing business logic in a data processing component.

COMPONENT PURPOSE:
{component_purpose}

INPUT SCHEMA:
{json.dumps(input_schema, indent=2)}

OUTPUT SCHEMA:
{json.dumps(output_schema, indent=2)}

CURRENT CODE:
```python
{code}
```

TASK:
1. Analyze if the current code correctly implements the stated purpose
2. Fix any business logic errors or unreasonable transformations
3. Ensure the code produces outputs that match the schema and make business sense
4. Remove any placeholder logic (like return {{"value": 42}})
5. Add proper data validation and error handling

Return the corrected code that properly implements the business logic.
Format your response as:
REASONING: [explain what was wrong and what you fixed]
FIXED_CODE:
```python
[corrected code here]
```
CHANGES:
- [list each change made]"""

        try:
            response = self._query_llm(prompt)
            return self._parse_healing_response(response, code)
        except Exception as e:
            return SemanticHealingResult(
                success=False,
                original_code=code,
                healed_code=code,
                reasoning="",
                changes_made=[],
                error_message=f"Failed to heal business logic: {str(e)}"
            )

    # ... rest of methods remain the same but without mock modes ...