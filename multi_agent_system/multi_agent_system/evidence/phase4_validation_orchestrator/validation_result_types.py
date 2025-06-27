#!/usr/bin/env python3
"""
Validation Result Types for ValidationDrivenOrchestrator
======================================================

Comprehensive type definitions for all validation results, failures, and
orchestration outcomes in the V5.0 four-tier validation hierarchy.

All types enforce fail-hard principles with no fallback mechanisms.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import time


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class HealingType(Enum):
    """Types of healing that can be applied"""
    AST_HEALING = "ast_healing"
    SEMANTIC_HEALING = "semantic_healing"
    CONFIGURATION_REGENERATION = "configuration_regeneration"


@dataclass
class ValidationFailure:
    """
    Individual validation failure with context and healing information
    
    Each failure represents a specific validation issue that caused
    a validation level to fail.
    """
    component_name: Optional[str]
    failure_type: str
    error_message: str
    healing_candidate: bool = False
    severity: str = "ERROR"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """String representation of validation failure"""
        comp_str = f" in component '{self.component_name}'" if self.component_name else ""
        return f"{self.severity}: {self.failure_type}{comp_str} - {self.error_message}"


@dataclass
class ValidationResult:
    """
    Result of a single validation level execution
    
    Contains all information about validation execution including
    pass/fail status, failures, healing application, and timing.
    """
    passed: bool
    level: int
    failures: List[ValidationFailure] = field(default_factory=list)
    healing_applied: bool = False
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_failures(self) -> bool:
        """Check if this result has any failures"""
        return len(self.failures) > 0
    
    @property
    def error_count(self) -> int:
        """Count of error-level failures"""
        return len([f for f in self.failures if f.severity == "ERROR"])
    
    @property
    def warning_count(self) -> int:
        """Count of warning-level failures"""
        return len([f for f in self.failures if f.severity == "WARNING"])
    
    def add_failure(self, failure: ValidationFailure) -> None:
        """Add a failure to this result"""
        self.failures.append(failure)
        if failure.severity == "ERROR":
            self.passed = False


@dataclass
class FrameworkTestResult:
    """Result of framework unit testing"""
    all_passed: bool
    test_count: int
    failures: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate test success rate"""
        if self.test_count == 0:
            return 0.0
        passed_count = self.test_count - len(self.failures)
        return (passed_count / self.test_count) * 100.0


@dataclass
class ComponentLogicResult:
    """Result of component logic validation"""
    passed: bool
    component_name: str
    logic_errors: List[str] = field(default_factory=list)
    schema_errors: List[str] = field(default_factory=list)
    dependency_errors: List[str] = field(default_factory=list)
    
    @property
    def all_errors(self) -> List[str]:
        """Get all errors combined"""
        return self.logic_errors + self.schema_errors + self.dependency_errors


@dataclass
class IntegrationTestResult:
    """Result of system integration testing"""
    passed: bool
    service_connectivity: Dict[str, bool] = field(default_factory=dict)
    port_conflicts: List[str] = field(default_factory=list)
    resource_conflicts: List[str] = field(default_factory=list)
    dependency_issues: List[str] = field(default_factory=list)
    
    @property
    def all_services_connected(self) -> bool:
        """Check if all services are properly connected"""
        return all(self.service_connectivity.values()) if self.service_connectivity else True


@dataclass
class SemanticValidationResult:
    """Result of semantic validation using reasonableness checks"""
    passed: bool
    reasonableness_issues: List[str] = field(default_factory=list)
    coherence_issues: List[str] = field(default_factory=list)
    architectural_issues: List[str] = field(default_factory=list)
    
    @property
    def all_issues(self) -> List[str]:
        """Get all semantic issues combined"""
        return self.reasonableness_issues + self.coherence_issues + self.architectural_issues
    
    @property
    def failures(self) -> List[str]:
        """Alias for all_issues to match orchestrator expectations"""
        return self.all_issues


@dataclass
class OrchestratedHealingResult:
    """Result of orchestrated healing operation"""
    healing_successful: bool
    healing_type: Optional[HealingType] = None
    healed_component: Optional[Dict[str, Any]] = None
    healed_blueprint: Optional[Dict[str, Any]] = None
    healing_details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Ensure healing type is set if successful"""
        if self.healing_successful and not self.healing_type:
            # Infer healing type from presence of healed artifacts
            if self.healed_component:
                self.healing_type = HealingType.AST_HEALING
            elif self.healed_blueprint:
                self.healing_type = HealingType.SEMANTIC_HEALING


@dataclass
class OrchestratedRegenerationResult:
    """Result of orchestrated configuration regeneration"""
    regeneration_successful: bool
    updated_blueprint: Optional[Dict[str, Any]] = None
    regeneration_details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    @property
    def has_updated_blueprint(self) -> bool:
        """Check if regeneration produced updated blueprint"""
        return self.updated_blueprint is not None


@dataclass
class SystemGenerationResult:
    """Final result of complete system generation"""
    successful: bool
    generated_system: Optional[Any] = None
    validation_levels_passed: int = 0
    healing_applied: bool = False
    execution_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def all_levels_passed(self) -> bool:
        """Check if all four validation levels passed"""
        return self.validation_levels_passed == 4
    
    @property
    def generation_summary(self) -> str:
        """Get summary of system generation"""
        if self.successful:
            healing_note = " (with healing)" if self.healing_applied else ""
            return f"System generation successful - {self.validation_levels_passed}/4 levels passed{healing_note}"
        else:
            return f"System generation failed - {self.validation_levels_passed}/4 levels passed: {self.error_message}"


# Exception types for fail-hard validation
class ValidationDependencyError(Exception):
    """Raised when required dependencies are missing - no fallbacks available"""
    pass


class ValidationSequenceError(Exception):
    """Raised when validation sequence is broken - cannot proceed to next level"""
    pass


class FrameworkValidationError(Exception):
    """Raised when framework validation fails - indicates framework bug"""
    pass


class ComponentLogicValidationError(Exception):
    """Raised when component logic validation fails and cannot be healed"""
    pass


class SystemIntegrationError(Exception):
    """Raised when system integration validation fails and cannot be regenerated"""
    pass


class SemanticValidationError(Exception):
    """Raised when semantic validation fails and cannot be healed"""
    pass


class LLMUnavailableError(Exception):
    """Raised when LLM is required but not available for semantic validation"""
    pass


class ComponentSchemaValidationError(Exception):
    """Raised when component schema validation fails"""
    pass


class BlueprintValidationError(Exception):
    """Raised when blueprint validation fails"""
    pass


class BlueprintParsingError(Exception):
    """Raised when blueprint parsing fails"""
    pass


class ComponentGenerationSecurityError(Exception):
    """Raised when generated component fails security validation"""
    pass


# Utility functions for creating validation results
def create_success_result(level: int, execution_time: float = 0.0, metadata: Dict[str, Any] = None) -> ValidationResult:
    """Create a successful validation result"""
    return ValidationResult(
        passed=True,
        level=level,
        execution_time=execution_time,
        metadata=metadata or {}
    )


def create_failure_result(level: int, failures: List[ValidationFailure], execution_time: float = 0.0) -> ValidationResult:
    """Create a failed validation result"""
    return ValidationResult(
        passed=False,
        level=level,
        failures=failures,
        execution_time=execution_time
    )


def create_validation_failure(
    component_name: Optional[str],
    failure_type: str,
    error_message: str,
    healing_candidate: bool = False,
    severity: str = "ERROR"
) -> ValidationFailure:
    """Create a validation failure with standard format"""
    return ValidationFailure(
        component_name=component_name,
        failure_type=failure_type,
        error_message=error_message,
        healing_candidate=healing_candidate,
        severity=severity
    )


def create_framework_test_result(tests_passed: int, total_tests: int, failures: List[str] = None) -> FrameworkTestResult:
    """Create framework test result"""
    return FrameworkTestResult(
        all_passed=(tests_passed == total_tests),
        test_count=total_tests,
        failures=failures or []
    )


def create_healing_success(healing_type: HealingType, healed_artifact: Any, details: Dict[str, Any] = None) -> OrchestratedHealingResult:
    """Create successful healing result"""
    result = OrchestratedHealingResult(
        healing_successful=True,
        healing_type=healing_type,
        healing_details=details or {}
    )
    
    # Set appropriate healed artifact based on type
    if healing_type == HealingType.AST_HEALING:
        result.healed_component = healed_artifact
    elif healing_type == HealingType.SEMANTIC_HEALING:
        result.healed_blueprint = healed_artifact
    
    return result


def create_healing_failure(error_message: str, healing_type: HealingType = None) -> OrchestratedHealingResult:
    """Create failed healing result"""
    return OrchestratedHealingResult(
        healing_successful=False,
        healing_type=healing_type,
        error_message=error_message
    )


def create_regeneration_success(updated_blueprint: Dict[str, Any], details: Dict[str, Any] = None) -> OrchestratedRegenerationResult:
    """Create successful regeneration result"""
    return OrchestratedRegenerationResult(
        regeneration_successful=True,
        updated_blueprint=updated_blueprint,
        regeneration_details=details or {}
    )


def create_regeneration_failure(error_message: str) -> OrchestratedRegenerationResult:
    """Create failed regeneration result"""
    return OrchestratedRegenerationResult(
        regeneration_successful=False,
        error_message=error_message
    )


# Performance tracking utilities
class ValidationTimer:
    """Context manager for tracking validation execution time"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def execution_time(self) -> float:
        """Get execution time in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


# Validation result aggregation utilities
def aggregate_validation_results(results: List[ValidationResult]) -> Dict[str, Any]:
    """Aggregate multiple validation results into summary statistics"""
    if not results:
        return {
            'total_results': 0,
            'passed_count': 0,
            'failed_count': 0,
            'total_failures': 0,
            'total_execution_time': 0.0,
            'healing_applied_count': 0
        }
    
    passed_count = sum(1 for r in results if r.passed)
    failed_count = len(results) - passed_count
    total_failures = sum(len(r.failures) for r in results)
    total_execution_time = sum(r.execution_time for r in results)
    healing_applied_count = sum(1 for r in results if r.healing_applied)
    
    return {
        'total_results': len(results),
        'passed_count': passed_count,
        'failed_count': failed_count,
        'success_rate': (passed_count / len(results)) * 100.0,
        'total_failures': total_failures,
        'average_failures_per_result': total_failures / len(results),
        'total_execution_time': total_execution_time,
        'average_execution_time': total_execution_time / len(results),
        'healing_applied_count': healing_applied_count,
        'healing_rate': (healing_applied_count / len(results)) * 100.0
    }


# Example usage and validation
if __name__ == "__main__":
    # Test validation result types
    print("🧪 Testing Validation Result Types")
    
    # Create test failure
    test_failure = create_validation_failure(
        component_name="test_component",
        failure_type="logic_error",
        error_message="Component logic validation failed: invalid configuration",
        healing_candidate=True
    )
    
    print(f"Test failure: {test_failure}")
    
    # Create test validation result
    test_result = create_failure_result(
        level=2,
        failures=[test_failure],
        execution_time=1.5
    )
    
    print(f"Test result: passed={test_result.passed}, level={test_result.level}, failures={len(test_result.failures)}")
    
    # Test healing result
    healing_result = create_healing_success(
        healing_type=HealingType.AST_HEALING,
        healed_artifact={"name": "healed_component", "status": "fixed"},
        details={"healing_method": "ast_transformation", "issues_fixed": 3}
    )
    
    print(f"Healing result: successful={healing_result.healing_successful}, type={healing_result.healing_type}")
    
    # Test timer
    with ValidationTimer() as timer:
        time.sleep(0.1)  # Simulate validation work
    
    print(f"Timer test: execution_time={timer.execution_time:.3f}s")
    
    print("✅ Validation result types working correctly")