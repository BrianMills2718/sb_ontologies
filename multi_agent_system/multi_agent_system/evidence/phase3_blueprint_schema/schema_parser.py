"""
V5.0 Blueprint Schema Parser and Validation System

This module provides comprehensive parsing and validation of V5.0 blueprint files
against the enhanced schema supporting reasonableness checks, component validation
sections, and secure property-based testing.
"""

import yaml
import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Set
from enum import Enum

# Import V5.0 validation components
try:
    from reasonableness_checks import (
        ReasonablenessValidator, SystemBlueprint, ValidationResult, 
        ValidationIssue, ValidationSeverity
    )
    from component_validation_schema import (
        ComponentValidationSchemaManager, ComponentType, ComponentValidation
    )
    from property_test_framework import PropertyTestFramework, PropertyTestType
except ImportError:
    # Fallback for when modules are in same directory
    import reasonableness_checks
    from reasonableness_checks import (
        ReasonablenessValidator, SystemBlueprint, ValidationResult, 
        ValidationIssue, ValidationSeverity
    )
    import component_validation_schema
    from component_validation_schema import (
        ComponentValidationSchemaManager, ComponentType, ComponentValidation
    )
    import property_test_framework
    from property_test_framework import PropertyTestFramework, PropertyTestType


class ParseError(Exception):
    """Exception raised when blueprint parsing fails"""
    pass


class ValidationError(Exception):
    """Exception raised when blueprint validation fails"""
    pass


class SchemaVersion(Enum):
    """Supported schema versions"""
    V5_0 = "5.0"
    V4_0 = "4.0"  # For backward compatibility
    

@dataclass
class ParsedComponent:
    """Parsed component with validation"""
    name: str
    type: str
    description: Optional[str] = None
    configuration: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[Dict[str, Any]] = field(default_factory=list)
    validation: Optional[ComponentValidation] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = {
            'name': self.name,
            'type': self.type
        }
        
        if self.description:
            result['description'] = self.description
        
        if self.configuration:
            result['configuration'] = self.configuration
        
        if self.dependencies:
            result['dependencies'] = self.dependencies
        
        if self.validation:
            # Convert validation to dict representation
            validation_dict = {}
            if self.validation.property_tests:
                validation_dict['property_tests'] = [
                    {
                        'test_type': test.test_type.value,
                        'description': test.description,
                        'parameters': test.parameters,
                        'severity': test.severity.value
                    }
                    for test in self.validation.property_tests
                ]
            
            if self.validation.contracts:
                validation_dict['contracts'] = [
                    {
                        'contract_type': contract.contract_type.value,
                        'specification': contract.specification,
                        'validation_method': contract.validation_method
                    }
                    for contract in self.validation.contracts
                ]
            
            if self.validation.behavioral_requirements:
                validation_dict['behavioral_requirements'] = [
                    {
                        'requirement_type': req.requirement_type.value,
                        'description': req.description,
                        'acceptance_criteria': req.acceptance_criteria,
                        'priority': req.priority
                    }
                    for req in self.validation.behavioral_requirements
                ]
            
            if validation_dict:
                result['validation'] = validation_dict
        
        return result


@dataclass
class ParsedBlueprint:
    """Complete parsed blueprint with V5.0 features"""
    description: str
    components: List[ParsedComponent]
    reasonableness_checks: List[Dict[str, Any]] = field(default_factory=list)
    schema_version: SchemaVersion = SchemaVersion.V5_0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_system_blueprint(self) -> SystemBlueprint:
        """Convert to SystemBlueprint for reasonableness validation"""
        return SystemBlueprint(
            description=self.description,
            components=[comp.to_dict() for comp in self.components],
            reasonableness_checks=self.reasonableness_checks
        )


@dataclass
class SchemaValidationResult:
    """Result of schema validation"""
    is_valid: bool
    schema_version: SchemaVersion
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    component_validation_results: Dict[str, List[str]] = field(default_factory=dict)
    reasonableness_result: Optional[ValidationResult] = None
    property_test_results: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has any errors"""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has any warnings"""
        return len(self.warnings) > 0


class V5SchemaParser:
    """
    V5.0 Blueprint Schema Parser and Validator.
    
    This class provides comprehensive parsing and validation of V5.0 blueprint files,
    including support for reasonableness checks, component validation sections,
    and secure property-based testing integration.
    """
    
    def __init__(self):
        self.reasonableness_validator = ReasonablenessValidator()
        self.component_schema_manager = ComponentValidationSchemaManager()
        self.property_test_framework = PropertyTestFramework()
        
        # Required fields for V5.0 schema
        self.required_root_fields = {'description', 'components'}
        self.required_component_fields = {'name', 'type'}
        
        # Valid component types
        self.valid_component_types = {ct.value for ct in ComponentType}
        
        # Schema version patterns
        self.schema_version_patterns = {
            SchemaVersion.V5_0: r'^5\.0$',
            SchemaVersion.V4_0: r'^4\.0$'
        }
    
    def parse_blueprint_file(self, blueprint_path: Union[str, Path]) -> ParsedBlueprint:
        """
        Parse a blueprint file and return ParsedBlueprint object.
        
        Args:
            blueprint_path: Path to the blueprint YAML file
            
        Returns:
            ParsedBlueprint object with parsed content
            
        Raises:
            ParseError: If parsing fails
        """
        blueprint_path = Path(blueprint_path)
        
        if not blueprint_path.exists():
            raise ParseError(f"Blueprint file not found: {blueprint_path}")
        
        if not blueprint_path.is_file():
            raise ParseError(f"Blueprint path is not a file: {blueprint_path}")
        
        try:
            with open(blueprint_path, 'r', encoding='utf-8') as file:
                raw_content = yaml.safe_load(file)
                
            if not isinstance(raw_content, dict):
                raise ParseError("Blueprint file must contain a YAML object")
            
            # Parse the blueprint content
            return self._parse_blueprint_content(raw_content)
            
        except yaml.YAMLError as e:
            raise ParseError(f"YAML parsing error: {e}")
        except Exception as e:
            raise ParseError(f"Error reading blueprint file: {e}")
    
    def parse_blueprint_string(self, blueprint_yaml: str) -> ParsedBlueprint:
        """
        Parse a blueprint from YAML string.
        
        Args:
            blueprint_yaml: YAML string containing blueprint
            
        Returns:
            ParsedBlueprint object with parsed content
            
        Raises:
            ParseError: If parsing fails
        """
        try:
            raw_content = yaml.safe_load(blueprint_yaml)
            
            if not isinstance(raw_content, dict):
                raise ParseError("Blueprint must be a YAML object")
            
            return self._parse_blueprint_content(raw_content)
            
        except yaml.YAMLError as e:
            raise ParseError(f"YAML parsing error: {e}")
    
    def _parse_blueprint_content(self, content: Dict[str, Any]) -> ParsedBlueprint:
        """Parse blueprint content dictionary"""
        
        # Check for systemBlueprint wrapper (V5.0 schema format)
        if 'systemBlueprint' in content:
            blueprint_data = content['systemBlueprint']
            metadata = {k: v for k, v in content.items() if k != 'systemBlueprint'}
        else:
            # Direct blueprint format
            blueprint_data = content
            metadata = {}
        
        # Validate required fields
        missing_fields = self.required_root_fields - set(blueprint_data.keys())
        if missing_fields:
            raise ParseError(f"Missing required fields: {missing_fields}")
        
        # Determine schema version
        schema_version = self._determine_schema_version(blueprint_data, metadata)
        
        # Parse description
        description = blueprint_data.get('description', '')
        if not isinstance(description, str):
            raise ParseError("Description must be a string")
        
        # Parse reasonableness checks (V5.0 feature)
        reasonableness_checks = []
        if 'reasonableness_checks' in blueprint_data:
            reasonableness_checks = self._parse_reasonableness_checks(
                blueprint_data['reasonableness_checks']
            )
        
        # Parse components
        components = self._parse_components(blueprint_data.get('components', []))
        
        return ParsedBlueprint(
            description=description,
            components=components,
            reasonableness_checks=reasonableness_checks,
            schema_version=schema_version,
            metadata=metadata
        )
    
    def _determine_schema_version(self, blueprint_data: Dict[str, Any], 
                                metadata: Dict[str, Any]) -> SchemaVersion:
        """Determine schema version from blueprint content"""
        
        # Check explicit schema version
        version_str = metadata.get('schema_version') or blueprint_data.get('schema_version')
        if version_str:
            for version, pattern in self.schema_version_patterns.items():
                if re.match(pattern, str(version_str)):
                    return version
        
        # Infer version from features
        if 'reasonableness_checks' in blueprint_data:
            return SchemaVersion.V5_0
        
        # Check for V5.0 component validation features
        components = blueprint_data.get('components', [])
        for component in components:
            if isinstance(component, dict) and 'validation' in component:
                validation = component['validation']
                if isinstance(validation, dict):
                    if 'property_tests' in validation or 'contracts' in validation:
                        return SchemaVersion.V5_0
        
        # Default to V5.0 for new blueprints
        return SchemaVersion.V5_0
    
    def _parse_reasonableness_checks(self, checks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse reasonableness checks section"""
        if not isinstance(checks_data, list):
            raise ParseError("reasonableness_checks must be a list")
        
        parsed_checks = []
        
        for i, check in enumerate(checks_data):
            if not isinstance(check, dict):
                raise ParseError(f"Reasonableness check {i+1} must be an object")
            
            # Validate required fields
            required_check_fields = {'check_type', 'description', 'validation_logic'}
            missing_fields = required_check_fields - set(check.keys())
            if missing_fields:
                raise ParseError(f"Reasonableness check {i+1} missing fields: {missing_fields}")
            
            # Validate check_type
            valid_check_types = {
                'component_coherence', 'resource_feasibility', 'architectural_consistency',
                'dependency_validity', 'security_requirements', 'performance_expectations'
            }
            
            check_type = check.get('check_type', '')
            if check_type not in valid_check_types:
                raise ParseError(f"Invalid check_type '{check_type}' in check {i+1}")
            
            # Validate severity
            severity = check.get('severity', 'error')
            if severity not in ['error', 'warning', 'info']:
                raise ParseError(f"Invalid severity '{severity}' in check {i+1}")
            
            parsed_checks.append({
                'check_type': check_type,
                'description': check.get('description', ''),
                'validation_logic': check.get('validation_logic', ''),
                'severity': severity,
                'parameters': check.get('parameters', {})
            })
        
        return parsed_checks
    
    def _parse_components(self, components_data: List[Dict[str, Any]]) -> List[ParsedComponent]:
        """Parse components section"""
        if not isinstance(components_data, list):
            raise ParseError("components must be a list")
        
        if not components_data:
            raise ParseError("Blueprint must have at least one component")
        
        parsed_components = []
        component_names = set()
        
        for i, component in enumerate(components_data):
            if not isinstance(component, dict):
                raise ParseError(f"Component {i+1} must be an object")
            
            # Validate required fields
            missing_fields = self.required_component_fields - set(component.keys())
            if missing_fields:
                raise ParseError(f"Component {i+1} missing fields: {missing_fields}")
            
            # Parse component name
            name = component.get('name', '')
            if not isinstance(name, str) or not name.strip():
                raise ParseError(f"Component {i+1} name must be a non-empty string")
            
            # Validate name format
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
                raise ParseError(f"Component {i+1} name '{name}' must be a valid identifier")
            
            # Check for duplicate names
            if name in component_names:
                raise ParseError(f"Duplicate component name: {name}")
            component_names.add(name)
            
            # Parse component type
            comp_type = component.get('type', '')
            if comp_type not in self.valid_component_types:
                raise ParseError(f"Invalid component type '{comp_type}' in component '{name}'")
            
            # Parse optional fields
            description = component.get('description', '')
            configuration = component.get('configuration', {})
            dependencies = component.get('dependencies', [])
            
            # Validate configuration
            if not isinstance(configuration, dict):
                raise ParseError(f"Component '{name}' configuration must be an object")
            
            # Validate dependencies
            if not isinstance(dependencies, list):
                raise ParseError(f"Component '{name}' dependencies must be a list")
            
            parsed_dependencies = self._parse_component_dependencies(dependencies, name)
            
            # Parse validation section (V5.0 feature)
            validation = None
            if 'validation' in component:
                validation = self._parse_component_validation(component['validation'], name)
            
            parsed_components.append(ParsedComponent(
                name=name,
                type=comp_type,
                description=description,
                configuration=configuration,
                dependencies=parsed_dependencies,
                validation=validation
            ))
        
        return parsed_components
    
    def _parse_component_dependencies(self, dependencies_data: List[Dict[str, Any]], 
                                    component_name: str) -> List[Dict[str, Any]]:
        """Parse component dependencies"""
        parsed_dependencies = []
        
        for i, dep in enumerate(dependencies_data):
            if not isinstance(dep, dict):
                raise ParseError(f"Component '{component_name}' dependency {i+1} must be an object")
            
            # Validate required fields
            if 'component_name' not in dep or 'dependency_type' not in dep:
                raise ParseError(f"Component '{component_name}' dependency {i+1} missing required fields")
            
            dep_name = dep.get('component_name', '')
            dep_type = dep.get('dependency_type', '')
            
            # Validate dependency type
            valid_dep_types = {'data_dependency', 'service_dependency', 'configuration_dependency'}
            if dep_type not in valid_dep_types:
                raise ParseError(f"Invalid dependency_type '{dep_type}' in component '{component_name}'")
            
            parsed_dependencies.append({
                'component_name': dep_name,
                'dependency_type': dep_type,
                'optional': dep.get('optional', False)
            })
        
        return parsed_dependencies
    
    def _parse_component_validation(self, validation_data: Dict[str, Any], 
                                  component_name: str) -> ComponentValidation:
        """Parse component validation section"""
        if not isinstance(validation_data, dict):
            raise ParseError(f"Component '{component_name}' validation must be an object")
        
        try:
            return self.component_schema_manager.create_validation_from_dict(validation_data)
        except Exception as e:
            raise ParseError(f"Error parsing validation for component '{component_name}': {e}")
    
    def validate_blueprint_schema(self, blueprint: ParsedBlueprint) -> SchemaValidationResult:
        """
        Comprehensive validation of parsed blueprint against V5.0 schema.
        
        Args:
            blueprint: ParsedBlueprint to validate
            
        Returns:
            SchemaValidationResult with validation results
        """
        errors = []
        warnings = []
        component_validation_results = {}
        
        # Basic blueprint validation
        if not blueprint.description or len(blueprint.description.strip()) < 10:
            errors.append("Blueprint description must be at least 10 characters")
        
        if not blueprint.components:
            errors.append("Blueprint must have at least one component")
        
        # Component validation
        component_names = set()
        for component in blueprint.components:
            comp_name = component.name
            
            # Check for duplicate names (should not happen if parsing was correct)
            if comp_name in component_names:
                errors.append(f"Duplicate component name: {comp_name}")
            component_names.add(comp_name)
            
            # Validate component type-specific requirements
            try:
                comp_type = ComponentType(component.type)
                if component.validation:
                    comp_errors = self.component_schema_manager.validate_component_validation_section(
                        comp_type, component.validation
                    )
                    if comp_errors:
                        component_validation_results[comp_name] = comp_errors
                        warnings.extend([f"Component '{comp_name}': {error}" for error in comp_errors])
            except ValueError:
                errors.append(f"Invalid component type: {component.type}")
        
        # Validate dependencies reference existing components
        for component in blueprint.components:
            for dep in component.dependencies:
                dep_name = dep.get('component_name', '')
                if dep_name and dep_name not in component_names:
                    errors.append(f"Component '{component.name}' depends on non-existent component '{dep_name}'")
        
        # Reasonableness validation
        reasonableness_result = None
        if blueprint.reasonableness_checks or len(blueprint.components) > 1:
            try:
                system_blueprint = blueprint.to_system_blueprint()
                reasonableness_result = self.reasonableness_validator.validate_system_reasonableness(
                    system_blueprint
                )
                
                # Convert reasonableness issues to schema validation results
                for issue in reasonableness_result.issues:
                    if issue.severity == ValidationSeverity.ERROR:
                        errors.append(f"Reasonableness check failed: {issue.message}")
                    elif issue.severity == ValidationSeverity.WARNING:
                        warnings.append(f"Reasonableness warning: {issue.message}")
                
            except Exception as e:
                errors.append(f"Reasonableness validation error: {e}")
        
        # Property test validation
        property_test_results = {}
        for component in blueprint.components:
            if component.validation and component.validation.property_tests:
                try:
                    # Convert to test format
                    test_configs = []
                    for prop_test in component.validation.property_tests:
                        test_configs.append({
                            'test_type': prop_test.test_type.value,
                            'description': prop_test.description,
                            'parameters': prop_test.parameters
                        })
                    
                    # Execute property tests
                    test_results = self.property_test_framework.execute_property_tests(
                        component.name, component.type, test_configs
                    )
                    
                    property_test_results[component.name] = {
                        'total_tests': test_results.total_tests,
                        'passed_tests': test_results.passed_tests,
                        'failed_tests': test_results.failed_tests,
                        'success_rate': test_results.success_rate,
                        'all_passed': test_results.all_passed
                    }
                    
                    # Add failed tests as warnings
                    if test_results.failed_tests > 0:
                        warnings.append(f"Component '{component.name}' has {test_results.failed_tests} failed property tests")
                    
                except Exception as e:
                    errors.append(f"Property test validation error for component '{component.name}': {e}")
        
        return SchemaValidationResult(
            is_valid=len(errors) == 0,
            schema_version=blueprint.schema_version,
            errors=errors,
            warnings=warnings,
            component_validation_results=component_validation_results,
            reasonableness_result=reasonableness_result,
            property_test_results=property_test_results
        )
    
    def create_validation_report(self, validation_result: SchemaValidationResult) -> str:
        """
        Create a human-readable validation report.
        
        Args:
            validation_result: SchemaValidationResult to report on
            
        Returns:
            Formatted validation report string
        """
        report = []
        report.append("=" * 60)
        report.append("V5.0 BLUEPRINT SCHEMA VALIDATION REPORT")
        report.append("=" * 60)
        
        # Overall status
        status = "PASSED" if validation_result.is_valid else "FAILED"
        report.append(f"Overall Status: {status}")
        report.append(f"Schema Version: {validation_result.schema_version.value}")
        report.append("")
        
        # Errors
        if validation_result.errors:
            report.append("ERRORS:")
            for error in validation_result.errors:
                report.append(f"  ❌ {error}")
            report.append("")
        
        # Warnings
        if validation_result.warnings:
            report.append("WARNINGS:")
            for warning in validation_result.warnings:
                report.append(f"  ⚠️  {warning}")
            report.append("")
        
        # Component validation results
        if validation_result.component_validation_results:
            report.append("COMPONENT VALIDATION DETAILS:")
            for comp_name, comp_errors in validation_result.component_validation_results.items():
                report.append(f"  Component '{comp_name}':")
                for error in comp_errors:
                    report.append(f"    - {error}")
            report.append("")
        
        # Reasonableness validation results
        if validation_result.reasonableness_result:
            report.append("REASONABLENESS VALIDATION:")
            result = validation_result.reasonableness_result
            report.append(f"  Status: {'PASSED' if result.passed else 'FAILED'}")
            report.append(f"  Checks performed: {result.checks_performed}")
            report.append(f"  Execution time: {result.execution_time_ms:.2f}ms")
            
            if result.issues:
                report.append("  Issues found:")
                for issue in result.issues:
                    report.append(f"    {issue.severity.value.upper()}: {issue.message}")
            report.append("")
        
        # Property test results
        if validation_result.property_test_results:
            report.append("PROPERTY TEST RESULTS:")
            for comp_name, test_results in validation_result.property_test_results.items():
                report.append(f"  Component '{comp_name}':")
                report.append(f"    Total tests: {test_results['total_tests']}")
                report.append(f"    Passed: {test_results['passed_tests']}")
                report.append(f"    Failed: {test_results['failed_tests']}")
                report.append(f"    Success rate: {test_results['success_rate']:.1f}%")
                report.append(f"    All passed: {test_results['all_passed']}")
            report.append("")
        
        # Summary
        report.append("SUMMARY:")
        report.append(f"  Total errors: {len(validation_result.errors)}")
        report.append(f"  Total warnings: {len(validation_result.warnings)}")
        report.append(f"  Validation result: {'✅ VALID' if validation_result.is_valid else '❌ INVALID'}")
        
        return "\n".join(report)


# Convenience functions for external use
def parse_blueprint_file(file_path: Union[str, Path]) -> ParsedBlueprint:
    """Parse a blueprint file"""
    parser = V5SchemaParser()
    return parser.parse_blueprint_file(file_path)


def validate_blueprint(blueprint: ParsedBlueprint) -> SchemaValidationResult:
    """Validate a parsed blueprint"""
    parser = V5SchemaParser()
    return parser.validate_blueprint_schema(blueprint)


def parse_and_validate_blueprint(file_path: Union[str, Path]) -> tuple[ParsedBlueprint, SchemaValidationResult]:
    """Parse and validate a blueprint file in one step"""
    parser = V5SchemaParser()
    blueprint = parser.parse_blueprint_file(file_path)
    validation_result = parser.validate_blueprint_schema(blueprint)
    return blueprint, validation_result


# Example usage and testing
if __name__ == "__main__":
    # Test the schema parser with an example blueprint
    example_blueprint = """
systemBlueprint:
  description: "A comprehensive web application system with user management and data processing capabilities"
  
  reasonableness_checks:
    - check_type: "component_coherence"
      description: "Ensure web service has sufficient resources"
      validation_logic: "component web_service memory_mb greater_than 512"
      severity: "warning"
    
    - check_type: "security_requirements"
      description: "Verify authentication service is included"
      validation_logic: "has_component_type authentication_service"
      severity: "error"
  
  components:
    - name: "web_service"
      type: "web_service"
      description: "Main web application server"
      configuration:
        resource_requirements:
          memory_mb: 1024
          cpu_cores: 2
          disk_gb: 20
        ports:
          - port: 8080
            protocol: "http"
            description: "Web server port"
      dependencies:
        - component_name: "database"
          dependency_type: "data_dependency"
        - component_name: "auth_service"
          dependency_type: "service_dependency"
      validation:
        property_tests:
          - test_type: "performance_validation"
            description: "Validate API response time"
            parameters:
              performance_requirements:
                response_time_ms: 1000
                throughput_rps: 500
          - test_type: "security_validation"
            description: "Validate security measures"
            parameters:
              security_checks: ["input_sanitization", "authentication_check"]
        contracts:
          - contract_type: "input_contract"
            specification: "All API inputs must be JSON with valid authentication"
            validation_method: "runtime_check"
        behavioral_requirements:
          - requirement_type: "performance_requirement"
            description: "Response time must be under 1 second"
            acceptance_criteria:
              - "95th percentile response time < 1000ms"
              - "Zero timeouts under normal load"
            priority: "high"
    
    - name: "database"
      type: "database"
      description: "PostgreSQL database for application data"
      configuration:
        resource_requirements:
          memory_mb: 2048
          cpu_cores: 2
          disk_gb: 100
      validation:
        contracts:
          - contract_type: "availability_contract"
            specification: "Database must maintain 99.9% uptime"
            validation_method: "test_suite"
    
    - name: "auth_service"
      type: "authentication_service"
      description: "JWT-based authentication service"
      configuration:
        resource_requirements:
          memory_mb: 512
          cpu_cores: 1
          disk_gb: 5
      validation:
        property_tests:
          - test_type: "security_validation"
            description: "Validate authentication security"
            parameters:
              security_checks: ["authentication_check", "authorization_check", "session_management"]

schema_version: "5.0"
"""
    
    try:
        # Parse the example blueprint
        parser = V5SchemaParser()
        blueprint = parser.parse_blueprint_string(example_blueprint)
        
        print("BLUEPRINT PARSING SUCCESSFUL")
        print(f"Description: {blueprint.description}")
        print(f"Components: {len(blueprint.components)}")
        print(f"Reasonableness checks: {len(blueprint.reasonableness_checks)}")
        print(f"Schema version: {blueprint.schema_version.value}")
        
        # Validate the blueprint
        validation_result = parser.validate_blueprint_schema(blueprint)
        
        print("\nVALIDATION RESULTS:")
        print(f"Valid: {validation_result.is_valid}")
        print(f"Errors: {len(validation_result.errors)}")
        print(f"Warnings: {len(validation_result.warnings)}")
        
        # Generate and print validation report
        report = parser.create_validation_report(validation_result)
        print("\n" + report)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()