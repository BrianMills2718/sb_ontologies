"""
V5.0 Component Validation Schema Definitions

This module defines comprehensive validation schemas for component-specific
validation sections in V5.0 blueprints, including property tests, contracts,
and behavioral requirements.
"""

import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Set
from enum import Enum


class ComponentType(Enum):
    """Supported component types in V5.0"""
    WEB_SERVICE = "web_service"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    CACHE_SERVICE = "cache_service"
    API_GATEWAY = "api_gateway"
    AUTHENTICATION_SERVICE = "authentication_service"
    FILE_STORAGE = "file_storage"
    MONITORING_SERVICE = "monitoring_service"
    LOAD_BALANCER = "load_balancer"
    DATA_PROCESSOR = "data_processor"


class PropertyTestType(Enum):
    """Secure property test types allowed in V5.0"""
    RANGE_CHECK = "range_check"
    FORMAT_VALIDATION = "format_validation"
    DEPENDENCY_CHECK = "dependency_check"
    RESOURCE_VALIDATION = "resource_validation"
    INTERFACE_VALIDATION = "interface_validation"
    SECURITY_VALIDATION = "security_validation"
    PERFORMANCE_VALIDATION = "performance_validation"


class ContractType(Enum):
    """Types of formal contracts for components"""
    INPUT_CONTRACT = "input_contract"
    OUTPUT_CONTRACT = "output_contract"
    PERFORMANCE_CONTRACT = "performance_contract"
    AVAILABILITY_CONTRACT = "availability_contract"
    SECURITY_CONTRACT = "security_contract"


class RequirementType(Enum):
    """Types of behavioral requirements"""
    FUNCTIONAL_REQUIREMENT = "functional_requirement"
    PERFORMANCE_REQUIREMENT = "performance_requirement"
    SECURITY_REQUIREMENT = "security_requirement"
    RELIABILITY_REQUIREMENT = "reliability_requirement"
    SCALABILITY_REQUIREMENT = "scalability_requirement"


class ValidationSeverity(Enum):
    """Severity levels for validation results"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class PropertyTest:
    """Definition of a secure property test"""
    test_type: PropertyTestType
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    severity: ValidationSeverity = ValidationSeverity.ERROR
    
    def validate_parameters(self) -> List[str]:
        """Validate property test parameters against type-specific schemas"""
        errors = []
        
        if self.test_type == PropertyTestType.RANGE_CHECK:
            if 'expected_range' not in self.parameters:
                errors.append("range_check requires 'expected_range' parameter")
            else:
                range_config = self.parameters['expected_range']
                if not isinstance(range_config, dict):
                    errors.append("expected_range must be an object")
                elif 'min' not in range_config or 'max' not in range_config:
                    errors.append("expected_range must have 'min' and 'max' values")
                elif not isinstance(range_config['min'], (int, float)) or not isinstance(range_config['max'], (int, float)):
                    errors.append("range min and max must be numeric")
                elif range_config['min'] >= range_config['max']:
                    errors.append("range min must be less than max")
        
        elif self.test_type == PropertyTestType.FORMAT_VALIDATION:
            if 'format_pattern' not in self.parameters:
                errors.append("format_validation requires 'format_pattern' parameter")
            else:
                pattern = self.parameters['format_pattern']
                if not isinstance(pattern, str):
                    errors.append("format_pattern must be a string")
                else:
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        errors.append(f"Invalid regex pattern: {e}")
        
        elif self.test_type == PropertyTestType.DEPENDENCY_CHECK:
            if 'dependencies' not in self.parameters:
                errors.append("dependency_check requires 'dependencies' parameter")
            else:
                deps = self.parameters['dependencies']
                if not isinstance(deps, list):
                    errors.append("dependencies must be a list")
                elif not all(isinstance(dep, str) for dep in deps):
                    errors.append("all dependencies must be strings")
        
        elif self.test_type == PropertyTestType.RESOURCE_VALIDATION:
            if 'resource_limits' not in self.parameters:
                errors.append("resource_validation requires 'resource_limits' parameter")
            else:
                limits = self.parameters['resource_limits']
                if not isinstance(limits, dict):
                    errors.append("resource_limits must be an object")
                else:
                    valid_keys = {'memory_mb', 'cpu_cores', 'disk_gb', 'network_bandwidth_mbps'}
                    for key in limits:
                        if key not in valid_keys:
                            errors.append(f"Invalid resource limit '{key}'. Valid: {valid_keys}")
                        elif not isinstance(limits[key], (int, float)) or limits[key] <= 0:
                            errors.append(f"Resource limit '{key}' must be a positive number")
        
        elif self.test_type == PropertyTestType.INTERFACE_VALIDATION:
            if 'interface_requirements' not in self.parameters:
                errors.append("interface_validation requires 'interface_requirements' parameter")
            else:
                interface = self.parameters['interface_requirements']
                if not isinstance(interface, dict):
                    errors.append("interface_requirements must be an object")
                else:
                    if 'protocols' in interface:
                        protocols = interface['protocols']
                        if not isinstance(protocols, list):
                            errors.append("protocols must be a list")
                        else:
                            valid_protocols = {'http', 'https', 'tcp', 'udp', 'grpc', 'websocket'}
                            for protocol in protocols:
                                if protocol not in valid_protocols:
                                    errors.append(f"Invalid protocol '{protocol}'. Valid: {valid_protocols}")
        
        return errors


@dataclass
class ComponentContract:
    """Definition of a formal component contract"""
    contract_type: ContractType
    specification: str
    validation_method: str = "runtime_check"
    
    def validate_specification(self) -> List[str]:
        """Validate contract specification"""
        errors = []
        
        if not self.specification or len(self.specification.strip()) < 10:
            errors.append("Contract specification must be at least 10 characters")
        
        if self.validation_method not in ["runtime_check", "static_analysis", "test_suite"]:
            errors.append("Invalid validation_method. Must be: runtime_check, static_analysis, or test_suite")
        
        # Type-specific validation
        if self.contract_type == ContractType.PERFORMANCE_CONTRACT:
            if not any(word in self.specification.lower() for word in ['response', 'latency', 'throughput', 'performance']):
                errors.append("Performance contract should specify performance metrics")
        
        elif self.contract_type == ContractType.SECURITY_CONTRACT:
            if not any(word in self.specification.lower() for word in ['authentication', 'authorization', 'encryption', 'security']):
                errors.append("Security contract should specify security requirements")
        
        elif self.contract_type == ContractType.AVAILABILITY_CONTRACT:
            if not any(word in self.specification.lower() for word in ['uptime', 'availability', 'redundancy', 'failover']):
                errors.append("Availability contract should specify availability requirements")
        
        return errors


@dataclass
class BehavioralRequirement:
    """Definition of a behavioral requirement"""
    requirement_type: RequirementType
    description: str
    acceptance_criteria: List[str] = field(default_factory=list)
    priority: str = "medium"
    
    def validate_requirement(self) -> List[str]:
        """Validate behavioral requirement"""
        errors = []
        
        if not self.description or len(self.description.strip()) < 10:
            errors.append("Requirement description must be at least 10 characters")
        
        if self.priority not in ["critical", "high", "medium", "low"]:
            errors.append("Priority must be: critical, high, medium, or low")
        
        if not self.acceptance_criteria:
            errors.append("Behavioral requirements should have acceptance criteria")
        else:
            for i, criteria in enumerate(self.acceptance_criteria):
                if not isinstance(criteria, str) or len(criteria.strip()) < 5:
                    errors.append(f"Acceptance criteria {i+1} must be at least 5 characters")
        
        return errors


@dataclass
class ComponentValidation:
    """Complete validation section for a component"""
    property_tests: List[PropertyTest] = field(default_factory=list)
    contracts: List[ComponentContract] = field(default_factory=list)
    behavioral_requirements: List[BehavioralRequirement] = field(default_factory=list)
    
    def validate_all(self) -> List[str]:
        """Validate entire component validation section"""
        errors = []
        
        # Validate property tests
        for i, prop_test in enumerate(self.property_tests):
            prop_errors = prop_test.validate_parameters()
            for error in prop_errors:
                errors.append(f"Property test {i+1}: {error}")
        
        # Validate contracts
        for i, contract in enumerate(self.contracts):
            contract_errors = contract.validate_specification()
            for error in contract_errors:
                errors.append(f"Contract {i+1}: {error}")
        
        # Validate behavioral requirements
        for i, requirement in enumerate(self.behavioral_requirements):
            req_errors = requirement.validate_requirement()
            for error in req_errors:
                errors.append(f"Behavioral requirement {i+1}: {error}")
        
        return errors


class ComponentValidationSchemaManager:
    """
    Manager for component validation schemas and type-specific validation rules.
    
    This class provides the central interface for validating component validation
    sections according to V5.0 schema requirements and component-specific rules.
    """
    
    def __init__(self):
        # Component-specific validation rules
        self.component_validation_rules = self._initialize_component_rules()
        
        # Security constraints for property tests
        self.security_constraints = {
            PropertyTestType.SECURITY_VALIDATION: {
                'required_parameters': ['security_checks'],
                'allowed_security_checks': [
                    'input_sanitization', 'output_encoding', 'authentication_check',
                    'authorization_check', 'rate_limiting', 'ssl_verification'
                ]
            }
        }
    
    def _initialize_component_rules(self) -> Dict[ComponentType, Dict[str, Any]]:
        """Initialize component-specific validation rules"""
        rules = {}
        
        # Web Service validation rules
        rules[ComponentType.WEB_SERVICE] = {
            'recommended_property_tests': [
                PropertyTestType.PERFORMANCE_VALIDATION,
                PropertyTestType.SECURITY_VALIDATION,
                PropertyTestType.INTERFACE_VALIDATION
            ],
            'required_contracts': [ContractType.INPUT_CONTRACT, ContractType.OUTPUT_CONTRACT],
            'critical_requirements': [RequirementType.SECURITY_REQUIREMENT, RequirementType.PERFORMANCE_REQUIREMENT]
        }
        
        # Database validation rules
        rules[ComponentType.DATABASE] = {
            'recommended_property_tests': [
                PropertyTestType.RESOURCE_VALIDATION,
                PropertyTestType.PERFORMANCE_VALIDATION,
                PropertyTestType.SECURITY_VALIDATION
            ],
            'required_contracts': [ContractType.AVAILABILITY_CONTRACT, ContractType.SECURITY_CONTRACT],
            'critical_requirements': [RequirementType.RELIABILITY_REQUIREMENT, RequirementType.SECURITY_REQUIREMENT]
        }
        
        # Authentication Service validation rules
        rules[ComponentType.AUTHENTICATION_SERVICE] = {
            'recommended_property_tests': [
                PropertyTestType.SECURITY_VALIDATION,
                PropertyTestType.PERFORMANCE_VALIDATION
            ],
            'required_contracts': [ContractType.SECURITY_CONTRACT, ContractType.AVAILABILITY_CONTRACT],
            'critical_requirements': [RequirementType.SECURITY_REQUIREMENT, RequirementType.RELIABILITY_REQUIREMENT]
        }
        
        # API Gateway validation rules
        rules[ComponentType.API_GATEWAY] = {
            'recommended_property_tests': [
                PropertyTestType.PERFORMANCE_VALIDATION,
                PropertyTestType.SECURITY_VALIDATION,
                PropertyTestType.INTERFACE_VALIDATION
            ],
            'required_contracts': [ContractType.PERFORMANCE_CONTRACT, ContractType.SECURITY_CONTRACT],
            'critical_requirements': [RequirementType.PERFORMANCE_REQUIREMENT, RequirementType.SCALABILITY_REQUIREMENT]
        }
        
        # Load Balancer validation rules
        rules[ComponentType.LOAD_BALANCER] = {
            'recommended_property_tests': [
                PropertyTestType.PERFORMANCE_VALIDATION,
                PropertyTestType.RESOURCE_VALIDATION
            ],
            'required_contracts': [ContractType.PERFORMANCE_CONTRACT, ContractType.AVAILABILITY_CONTRACT],
            'critical_requirements': [RequirementType.PERFORMANCE_REQUIREMENT, RequirementType.RELIABILITY_REQUIREMENT]
        }
        
        # Set default rules for other component types
        default_rule = {
            'recommended_property_tests': [PropertyTestType.RESOURCE_VALIDATION],
            'required_contracts': [],
            'critical_requirements': [RequirementType.FUNCTIONAL_REQUIREMENT]
        }
        
        for comp_type in ComponentType:
            if comp_type not in rules:
                rules[comp_type] = default_rule.copy()
        
        return rules
    
    def validate_component_validation_section(self, component_type: ComponentType, 
                                            validation: ComponentValidation) -> List[str]:
        """
        Validate a component's validation section against type-specific rules.
        
        Args:
            component_type: Type of the component
            validation: Component validation section to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # First validate the basic structure
        basic_errors = validation.validate_all()
        errors.extend(basic_errors)
        
        # Then apply component-specific rules
        if component_type in self.component_validation_rules:
            rules = self.component_validation_rules[component_type]
            
            # Check for recommended property tests
            existing_test_types = {test.test_type for test in validation.property_tests}
            recommended_tests = set(rules.get('recommended_property_tests', []))
            missing_tests = recommended_tests - existing_test_types
            
            if missing_tests:
                test_names = [test.value for test in missing_tests]
                errors.append(f"Component type {component_type.value} should include property tests: {test_names}")
            
            # Check for required contracts
            existing_contract_types = {contract.contract_type for contract in validation.contracts}
            required_contracts = set(rules.get('required_contracts', []))
            missing_contracts = required_contracts - existing_contract_types
            
            if missing_contracts:
                contract_names = [contract.value for contract in missing_contracts]
                errors.append(f"Component type {component_type.value} requires contracts: {contract_names}")
            
            # Check for critical requirements
            existing_req_types = {req.requirement_type for req in validation.behavioral_requirements}
            critical_requirements = set(rules.get('critical_requirements', []))
            missing_critical = critical_requirements - existing_req_types
            
            if missing_critical:
                req_names = [req.value for req in missing_critical]
                errors.append(f"Component type {component_type.value} should include requirements: {req_names}")
        
        return errors
    
    def create_property_test_from_dict(self, test_data: Dict[str, Any]) -> PropertyTest:
        """Create PropertyTest object from dictionary data"""
        test_type_str = test_data.get('test_type', '')
        try:
            test_type = PropertyTestType(test_type_str)
        except ValueError:
            raise ValueError(f"Invalid property test type: {test_type_str}")
        
        severity_str = test_data.get('severity', 'error')
        try:
            severity = ValidationSeverity(severity_str)
        except ValueError:
            severity = ValidationSeverity.ERROR
        
        return PropertyTest(
            test_type=test_type,
            description=test_data.get('description', ''),
            parameters=test_data.get('parameters', {}),
            severity=severity
        )
    
    def create_contract_from_dict(self, contract_data: Dict[str, Any]) -> ComponentContract:
        """Create ComponentContract object from dictionary data"""
        contract_type_str = contract_data.get('contract_type', '')
        try:
            contract_type = ContractType(contract_type_str)
        except ValueError:
            raise ValueError(f"Invalid contract type: {contract_type_str}")
        
        return ComponentContract(
            contract_type=contract_type,
            specification=contract_data.get('specification', ''),
            validation_method=contract_data.get('validation_method', 'runtime_check')
        )
    
    def create_requirement_from_dict(self, req_data: Dict[str, Any]) -> BehavioralRequirement:
        """Create BehavioralRequirement object from dictionary data"""
        req_type_str = req_data.get('requirement_type', '')
        try:
            req_type = RequirementType(req_type_str)
        except ValueError:
            raise ValueError(f"Invalid requirement type: {req_type_str}")
        
        return BehavioralRequirement(
            requirement_type=req_type,
            description=req_data.get('description', ''),
            acceptance_criteria=req_data.get('acceptance_criteria', []),
            priority=req_data.get('priority', 'medium')
        )
    
    def create_validation_from_dict(self, validation_data: Dict[str, Any]) -> ComponentValidation:
        """Create ComponentValidation object from dictionary data"""
        property_tests = []
        if 'property_tests' in validation_data:
            for test_data in validation_data['property_tests']:
                try:
                    property_test = self.create_property_test_from_dict(test_data)
                    property_tests.append(property_test)
                except ValueError as e:
                    # Log error but continue processing
                    print(f"Warning: Skipping invalid property test: {e}")
        
        contracts = []
        if 'contracts' in validation_data:
            for contract_data in validation_data['contracts']:
                try:
                    contract = self.create_contract_from_dict(contract_data)
                    contracts.append(contract)
                except ValueError as e:
                    print(f"Warning: Skipping invalid contract: {e}")
        
        behavioral_requirements = []
        if 'behavioral_requirements' in validation_data:
            for req_data in validation_data['behavioral_requirements']:
                try:
                    requirement = self.create_requirement_from_dict(req_data)
                    behavioral_requirements.append(requirement)
                except ValueError as e:
                    print(f"Warning: Skipping invalid behavioral requirement: {e}")
        
        return ComponentValidation(
            property_tests=property_tests,
            contracts=contracts,
            behavioral_requirements=behavioral_requirements
        )
    
    def get_validation_template(self, component_type: ComponentType) -> Dict[str, Any]:
        """
        Get a validation template for a specific component type.
        
        Returns a dictionary template that shows the recommended validation
        structure for the given component type.
        """
        if component_type not in self.component_validation_rules:
            return {}
        
        rules = self.component_validation_rules[component_type]
        template = {
            "property_tests": [],
            "contracts": [],
            "behavioral_requirements": []
        }
        
        # Add recommended property tests
        for test_type in rules.get('recommended_property_tests', []):
            test_template = {
                "test_type": test_type.value,
                "description": f"Validate {test_type.value.replace('_', ' ')} for {component_type.value}",
                "parameters": self._get_test_parameter_template(test_type)
            }
            template["property_tests"].append(test_template)
        
        # Add required contracts
        for contract_type in rules.get('required_contracts', []):
            contract_template = {
                "contract_type": contract_type.value,
                "specification": f"Specify {contract_type.value.replace('_', ' ')} requirements",
                "validation_method": "runtime_check"
            }
            template["contracts"].append(contract_template)
        
        # Add critical requirements
        for req_type in rules.get('critical_requirements', []):
            req_template = {
                "requirement_type": req_type.value,
                "description": f"Define {req_type.value.replace('_', ' ')} for {component_type.value}",
                "acceptance_criteria": [
                    "Define specific acceptance criteria here"
                ],
                "priority": "high"
            }
            template["behavioral_requirements"].append(req_template)
        
        return template
    
    def _get_test_parameter_template(self, test_type: PropertyTestType) -> Dict[str, Any]:
        """Get parameter template for a specific property test type"""
        templates = {
            PropertyTestType.RANGE_CHECK: {
                "expected_range": {
                    "min": 0,
                    "max": 100
                }
            },
            PropertyTestType.FORMAT_VALIDATION: {
                "format_pattern": "^[a-zA-Z0-9]+$"
            },
            PropertyTestType.DEPENDENCY_CHECK: {
                "dependencies": ["example_dependency"]
            },
            PropertyTestType.RESOURCE_VALIDATION: {
                "resource_limits": {
                    "memory_mb": 1024,
                    "cpu_cores": 2,
                    "disk_gb": 10
                }
            },
            PropertyTestType.INTERFACE_VALIDATION: {
                "interface_requirements": {
                    "input_format": "json",
                    "output_format": "json",
                    "protocols": ["http", "https"]
                }
            },
            PropertyTestType.SECURITY_VALIDATION: {
                "security_checks": ["input_sanitization", "authentication_check"]
            },
            PropertyTestType.PERFORMANCE_VALIDATION: {
                "performance_requirements": {
                    "response_time_ms": 1000,
                    "throughput_rps": 100
                }
            }
        }
        
        return templates.get(test_type, {})


# Example usage and testing
if __name__ == "__main__":
    # Test the component validation schema system
    schema_manager = ComponentValidationSchemaManager()
    
    # Create a test validation section
    test_validation_data = {
        "property_tests": [
            {
                "test_type": "performance_validation",
                "description": "Validate API response time",
                "parameters": {
                    "performance_requirements": {
                        "response_time_ms": 500,
                        "throughput_rps": 1000
                    }
                }
            },
            {
                "test_type": "security_validation",
                "description": "Validate authentication and authorization",
                "parameters": {
                    "security_checks": ["authentication_check", "authorization_check"]
                }
            }
        ],
        "contracts": [
            {
                "contract_type": "input_contract",
                "specification": "All API inputs must be JSON formatted with required authentication headers",
                "validation_method": "runtime_check"
            }
        ],
        "behavioral_requirements": [
            {
                "requirement_type": "performance_requirement",
                "description": "API must respond within 500ms for 95% of requests",
                "acceptance_criteria": [
                    "Response time < 500ms for 95th percentile",
                    "Zero timeouts under normal load"
                ],
                "priority": "high"
            }
        ]
    }
    
    # Create validation object and validate
    validation = schema_manager.create_validation_from_dict(test_validation_data)
    errors = schema_manager.validate_component_validation_section(
        ComponentType.WEB_SERVICE, validation
    )
    
    print("Component Validation Schema Test Results:")
    print(f"Property tests: {len(validation.property_tests)}")
    print(f"Contracts: {len(validation.contracts)}")
    print(f"Behavioral requirements: {len(validation.behavioral_requirements)}")
    print(f"Validation errors: {len(errors)}")
    
    if errors:
        print("Errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Validation passed successfully!")
    
    # Test template generation
    print("\nValidation template for web service:")
    template = schema_manager.get_validation_template(ComponentType.WEB_SERVICE)
    print(json.dumps(template, indent=2))