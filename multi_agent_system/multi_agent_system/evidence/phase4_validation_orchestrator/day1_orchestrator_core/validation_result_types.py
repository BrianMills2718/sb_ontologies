"""
Validation_Result_Types Module
Generated/Enhanced: 2025-06-23T17:44:11.217564
"""
# Validation Result Types Implementation Evidence
# This file documents the complete validation result type system

# File: /blueprint_language/validation_result_types.py
# Lines: 275 total
# Key Features Implemented:

# 1. COMPREHENSIVE TYPE SYSTEM
# - ValidationLevel enum for four-tier hierarchy
# - FailureType enum for all validation failure categories
# - HealingType enum for orchestrated healing operations
# - Complete type safety throughout validation pipeline

# 2. VALIDATION RESULT STRUCTURES
# - ValidationFailure with component context and healing metadata
# - ValidationResult for individual validation levels
# - SystemGenerationResult for complete pipeline results
# - HealingResult for tracking healing operations

# 3. SYSTEM GENERATION RESULT FEATURES
# - Boolean properties for each validation level (level1_passed, etc.)
# - all_levels_passed property for complete validation status
# - system_generated property for generation success
# - Complete metadata and timing information

# 4. HEALING INTEGRATION TYPES
# - OrchestratedHealingResult for AST and semantic healing
# - OrchestratedRegenerationResult for configuration regeneration
# - RegenerationStrategy for configuration change tracking
# - Complete healing operation audit trail

# 5. EXCEPTION HIERARCHY
# - ValidationDependencyError for missing dependencies
# - Level-specific errors (FrameworkValidationError, etc.)
# - ValidationSequenceError for out-of-order execution
# - Security-specific errors (ComponentGenerationSecurityError)

# 6. SERIALIZATION SUPPORT
# - to_dict() methods for all result types
# - JSON-serializable structure for external evaluation
# - Timestamp and metadata preservation
# - Complete audit trail capability

# 7. FAIL-HARD COMPLIANCE
# - No success/partial states - boolean pass/fail only
# - Detailed error context for debugging
# - Component-level failure attribution
# - Healing candidate identification

# TYPE SAFETY FEATURES:
# - Enum-based constants prevent string errors
# - Optional typing for proper null handling
# - Dataclass validation for required fields
# - Type hints throughout for IDE support

# AUDIT TRAIL FEATURES:
# - Timestamp tracking for all operations
# - Component name attribution for failures
# - Healing operation details preservation
# - Execution time tracking for performance analysis

# INTEGRATION FEATURES:
# - Blueprint path tracking for external evaluation
# - Metadata dictionaries for extensible information
# - Error message standardization across validation levels
# - Healing result correlation with validation failures

# This type system provides the foundation for complete validation pipeline
# tracking, external evaluation, and audit trail requirements while maintaining
# strict fail-hard semantics throughout V5.0 architecture.