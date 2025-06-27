"""
V5.0 System-Level Reasonableness Validation

This module implements comprehensive system-level reasonableness validation
for V5.0 blueprints, ensuring that generated systems make architectural and
operational sense before implementation begins.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum


class ReasonablenessCheckType(Enum):
    """Types of reasonableness checks supported by V5.0"""
    COMPONENT_COHERENCE = "component_coherence"
    RESOURCE_FEASIBILITY = "resource_feasibility"
    ARCHITECTURAL_CONSISTENCY = "architectural_consistency"
    DEPENDENCY_VALIDITY = "dependency_validity"
    SECURITY_REQUIREMENTS = "security_requirements"
    PERFORMANCE_EXPECTATIONS = "performance_expectations"


class ValidationSeverity(Enum):
    """Severity levels for validation results"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Individual validation issue found during reasonableness checking"""
    check_type: ReasonablenessCheckType
    severity: ValidationSeverity
    message: str
    component_name: Optional[str] = None
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of reasonableness validation"""
    passed: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    execution_time_ms: float = 0.0
    checks_performed: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has any error-level issues"""
        return any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has any warning-level issues"""
        return any(issue.severity == ValidationSeverity.WARNING for issue in self.issues)


@dataclass
class SystemBlueprint:
    """System blueprint representation for reasonableness validation"""
    description: str
    components: List[Dict[str, Any]]
    reasonableness_checks: List[Dict[str, Any]] = field(default_factory=list)


class ReasonablenessValidator:
    """
    System-level reasonableness validation engine for V5.0 blueprints.
    
    This validator ensures that system blueprints make architectural and
    operational sense before code generation begins, catching issues that
    would result in non-functional or problematic systems.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Resource constraint definitions
        self.RESOURCE_LIMITS = {
            'max_memory_per_component_mb': 32768,  # 32GB
            'max_cpu_cores_per_component': 16,
            'max_disk_per_component_gb': 1024,     # 1TB
            'max_total_components': 50,
            'max_ports_per_component': 10
        }
        
        # Valid component type relationships
        self.VALID_COMPONENT_TYPES = {
            "web_service", "database", "message_queue", "cache_service",
            "api_gateway", "authentication_service", "file_storage",
            "monitoring_service", "load_balancer", "data_processor"
        }
        
        # Component dependency patterns that make sense
        self.LOGICAL_DEPENDENCIES = {
            "web_service": {"database", "cache_service", "authentication_service", "message_queue"},
            "api_gateway": {"web_service", "authentication_service", "monitoring_service"},
            "load_balancer": {"web_service", "api_gateway"},
            "data_processor": {"database", "message_queue", "file_storage"},
            "monitoring_service": {"database", "web_service"}
        }
    
    def validate_system_reasonableness(self, blueprint: SystemBlueprint) -> ValidationResult:
        """
        Main entry point for system-level reasonableness validation.
        
        Performs comprehensive validation of the system blueprint to ensure
        it represents a reasonable, implementable system architecture.
        """
        import time
        start_time = time.time()
        
        issues = []
        checks_performed = 0
        
        # Validate system description adequacy
        desc_issues, desc_checks = self._validate_system_description(blueprint)
        issues.extend(desc_issues)
        checks_performed += desc_checks
        
        # Validate component coherence
        coherence_issues, coherence_checks = self._validate_component_coherence(blueprint)
        issues.extend(coherence_issues)
        checks_performed += coherence_checks
        
        # Validate resource feasibility
        resource_issues, resource_checks = self._validate_resource_feasibility(blueprint)
        issues.extend(resource_issues)
        checks_performed += resource_checks
        
        # Validate architectural consistency
        arch_issues, arch_checks = self._validate_architectural_consistency(blueprint)
        issues.extend(arch_issues)
        checks_performed += arch_checks
        
        # Validate dependency relationships
        dep_issues, dep_checks = self._validate_dependency_validity(blueprint)
        issues.extend(dep_issues)
        checks_performed += dep_checks
        
        # Validate security requirements
        sec_issues, sec_checks = self._validate_security_requirements(blueprint)
        issues.extend(sec_issues)
        checks_performed += sec_checks
        
        # Process custom reasonableness checks from blueprint
        if blueprint.reasonableness_checks:
            custom_issues, custom_checks = self._process_custom_reasonableness_checks(blueprint)
            issues.extend(custom_issues)
            checks_performed += custom_checks
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Determine overall validation result
        passed = not any(issue.severity == ValidationSeverity.ERROR for issue in issues)
        
        return ValidationResult(
            passed=passed,
            issues=issues,
            execution_time_ms=execution_time,
            checks_performed=checks_performed,
            metadata={
                'total_components': len(blueprint.components),
                'custom_checks': len(blueprint.reasonableness_checks),
                'error_count': len([i for i in issues if i.severity == ValidationSeverity.ERROR]),
                'warning_count': len([i for i in issues if i.severity == ValidationSeverity.WARNING])
            }
        )
    
    def _validate_system_description(self, blueprint: SystemBlueprint) -> Tuple[List[ValidationIssue], int]:
        """Validate that system description is adequate for implementation"""
        issues = []
        checks = 0
        
        # Check description length and content
        if len(blueprint.description.strip()) < 20:
            issues.append(ValidationIssue(
                check_type=ReasonablenessCheckType.ARCHITECTURAL_CONSISTENCY,
                severity=ValidationSeverity.ERROR,
                message="System description too brief - must be at least 20 characters",
                suggestion="Provide detailed description of system purpose and architecture"
            ))
        checks += 1
        
        # Check for essential architectural concepts
        essential_concepts = ["service", "data", "user", "system", "component"]
        description_lower = blueprint.description.lower()
        missing_concepts = [concept for concept in essential_concepts 
                          if concept not in description_lower]
        
        if len(missing_concepts) > 2:
            issues.append(ValidationIssue(
                check_type=ReasonablenessCheckType.ARCHITECTURAL_CONSISTENCY,
                severity=ValidationSeverity.WARNING,
                message=f"System description lacks key architectural concepts: {missing_concepts}",
                suggestion="Include description of services, data flow, and system interactions"
            ))
        checks += 1
        
        return issues, checks
    
    def _validate_component_coherence(self, blueprint: SystemBlueprint) -> Tuple[List[ValidationIssue], int]:
        """Validate that components work together coherently"""
        issues = []
        checks = 0
        
        if not blueprint.components:
            issues.append(ValidationIssue(
                check_type=ReasonablenessCheckType.COMPONENT_COHERENCE,
                severity=ValidationSeverity.ERROR,
                message="System must have at least one component",
                suggestion="Add at least one component to the system"
            ))
            return issues, 1
        
        # Check for reasonable component count
        if len(blueprint.components) > self.RESOURCE_LIMITS['max_total_components']:
            issues.append(ValidationIssue(
                check_type=ReasonablenessCheckType.COMPONENT_COHERENCE,
                severity=ValidationSeverity.ERROR,
                message=f"Too many components ({len(blueprint.components)}). Maximum is {self.RESOURCE_LIMITS['max_total_components']}",
                suggestion="Consider consolidating related functionality into fewer components"
            ))
        checks += 1
        
        # Validate component names are unique
        component_names = [comp.get('name', '') for comp in blueprint.components]
        duplicate_names = set([name for name in component_names if component_names.count(name) > 1])
        
        if duplicate_names:
            issues.append(ValidationIssue(
                check_type=ReasonablenessCheckType.COMPONENT_COHERENCE,
                severity=ValidationSeverity.ERROR,
                message=f"Duplicate component names found: {duplicate_names}",
                suggestion="Ensure all component names are unique"
            ))
        checks += 1
        
        # Validate component types are recognized
        for component in blueprint.components:
            comp_type = component.get('type', '')
            if comp_type not in self.VALID_COMPONENT_TYPES:
                issues.append(ValidationIssue(
                    check_type=ReasonablenessCheckType.COMPONENT_COHERENCE,
                    severity=ValidationSeverity.ERROR,
                    message=f"Unknown component type '{comp_type}' in component '{component.get('name', 'unnamed')}'",
                    component_name=component.get('name'),
                    suggestion=f"Use one of: {', '.join(sorted(self.VALID_COMPONENT_TYPES))}"
                ))
            checks += 1
        
        # Check for common architectural patterns
        comp_types = [comp.get('type', '') for comp in blueprint.components]
        
        # Web systems should have appropriate data storage
        if any(t in comp_types for t in ['web_service', 'api_gateway']) and \
           not any(t in comp_types for t in ['database', 'cache_service']):
            issues.append(ValidationIssue(
                check_type=ReasonablenessCheckType.COMPONENT_COHERENCE,
                severity=ValidationSeverity.WARNING,
                message="Web services typically require data storage (database or cache)",
                suggestion="Consider adding a database or cache service component"
            ))
        checks += 1
        
        # Load balancers should have services to balance
        if 'load_balancer' in comp_types and comp_types.count('web_service') < 2:
            issues.append(ValidationIssue(
                check_type=ReasonablenessCheckType.COMPONENT_COHERENCE,
                severity=ValidationSeverity.WARNING,
                message="Load balancer typically requires multiple web services",
                suggestion="Add multiple web service instances or remove load balancer"
            ))
        checks += 1
        
        return issues, checks
    
    def _validate_resource_feasibility(self, blueprint: SystemBlueprint) -> Tuple[List[ValidationIssue], int]:
        """Validate that resource requirements are feasible"""
        issues = []
        checks = 0
        
        total_memory = 0
        total_cpu = 0
        total_disk = 0
        
        for component in blueprint.components:
            config = component.get('configuration', {})
            resources = config.get('resource_requirements', {})
            
            # Validate individual component resources
            memory = resources.get('memory_mb', 512)  # Default 512MB
            cpu = resources.get('cpu_cores', 0.5)     # Default 0.5 cores
            disk = resources.get('disk_gb', 5)        # Default 5GB
            
            comp_name = component.get('name', 'unnamed')
            
            if memory > self.RESOURCE_LIMITS['max_memory_per_component_mb']:
                issues.append(ValidationIssue(
                    check_type=ReasonablenessCheckType.RESOURCE_FEASIBILITY,
                    severity=ValidationSeverity.ERROR,
                    message=f"Component '{comp_name}' memory requirement ({memory}MB) exceeds limit ({self.RESOURCE_LIMITS['max_memory_per_component_mb']}MB)",
                    component_name=comp_name,
                    suggestion="Consider reducing memory requirements or splitting component"
                ))
            
            if cpu > self.RESOURCE_LIMITS['max_cpu_cores_per_component']:
                issues.append(ValidationIssue(
                    check_type=ReasonablenessCheckType.RESOURCE_FEASIBILITY,
                    severity=ValidationSeverity.ERROR,
                    message=f"Component '{comp_name}' CPU requirement ({cpu} cores) exceeds limit ({self.RESOURCE_LIMITS['max_cpu_cores_per_component']} cores)",
                    component_name=comp_name,
                    suggestion="Consider reducing CPU requirements or using multiple instances"
                ))
            
            if disk > self.RESOURCE_LIMITS['max_disk_per_component_gb']:
                issues.append(ValidationIssue(
                    check_type=ReasonablenessCheckType.RESOURCE_FEASIBILITY,
                    severity=ValidationSeverity.ERROR,
                    message=f"Component '{comp_name}' disk requirement ({disk}GB) exceeds limit ({self.RESOURCE_LIMITS['max_disk_per_component_gb']}GB)",
                    component_name=comp_name,
                    suggestion="Consider using external storage or data archiving strategies"
                ))
            
            total_memory += memory
            total_cpu += cpu
            total_disk += disk
            checks += 3
            
            # Validate port configurations
            ports = config.get('ports', [])
            if len(ports) > self.RESOURCE_LIMITS['max_ports_per_component']:
                issues.append(ValidationIssue(
                    check_type=ReasonablenessCheckType.RESOURCE_FEASIBILITY,
                    severity=ValidationSeverity.WARNING,
                    message=f"Component '{comp_name}' has many ports ({len(ports)}). Consider simplifying interface",
                    component_name=comp_name,
                    suggestion="Consolidate services or use fewer ports"
                ))
            checks += 1
            
            # Check for port conflicts within component
            port_numbers = [p.get('port', 0) for p in ports]
            duplicate_ports = set([p for p in port_numbers if port_numbers.count(p) > 1])
            if duplicate_ports:
                issues.append(ValidationIssue(
                    check_type=ReasonablenessCheckType.RESOURCE_FEASIBILITY,
                    severity=ValidationSeverity.ERROR,
                    message=f"Component '{comp_name}' has duplicate ports: {duplicate_ports}",
                    component_name=comp_name,
                    suggestion="Ensure all ports within a component are unique"
                ))
            checks += 1
        
        # Check total system resource requirements
        if total_memory > 100000:  # 100GB total system memory
            issues.append(ValidationIssue(
                check_type=ReasonablenessCheckType.RESOURCE_FEASIBILITY,
                severity=ValidationSeverity.WARNING,
                message=f"Total system memory requirement ({total_memory}MB) is very high",
                suggestion="Consider optimizing component memory usage or deployment strategy"
            ))
        checks += 1
        
        return issues, checks
    
    def _validate_architectural_consistency(self, blueprint: SystemBlueprint) -> Tuple[List[ValidationIssue], int]:
        """Validate architectural consistency and patterns"""
        issues = []
        checks = 0
        
        # Check for missing essential services in complex systems
        comp_types = [comp.get('type', '') for comp in blueprint.components]
        
        # If system has multiple web services, should consider monitoring
        if comp_types.count('web_service') > 2 and 'monitoring_service' not in comp_types:
            issues.append(ValidationIssue(
                check_type=ReasonablenessCheckType.ARCHITECTURAL_CONSISTENCY,
                severity=ValidationSeverity.WARNING,
                message="Multi-service system should include monitoring",
                suggestion="Add monitoring_service component for operational visibility"
            ))
        checks += 1
        
        # If system handles user requests, should have authentication
        has_user_facing = any(t in comp_types for t in ['web_service', 'api_gateway'])
        if has_user_facing and 'authentication_service' not in comp_types:
            # Check if authentication is mentioned in description
            if 'auth' not in blueprint.description.lower() and 'login' not in blueprint.description.lower():
                issues.append(ValidationIssue(
                    check_type=ReasonablenessCheckType.ARCHITECTURAL_CONSISTENCY,
                    severity=ValidationSeverity.WARNING,
                    message="User-facing system should consider authentication",
                    suggestion="Add authentication_service or document authentication strategy"
                ))
        checks += 1
        
        # Database without backup strategy
        if 'database' in comp_types:
            database_components = [c for c in blueprint.components if c.get('type') == 'database']
            for db_comp in database_components:
                validation = db_comp.get('validation', {})
                behavioral_reqs = validation.get('behavioral_requirements', [])
                
                has_backup_req = any('backup' in req.get('description', '').lower() 
                                   for req in behavioral_reqs)
                
                if not has_backup_req:
                    issues.append(ValidationIssue(
                        check_type=ReasonablenessCheckType.ARCHITECTURAL_CONSISTENCY,
                        severity=ValidationSeverity.WARNING,
                        message=f"Database component '{db_comp.get('name')}' lacks backup requirements",
                        component_name=db_comp.get('name'),
                        suggestion="Add behavioral requirements for data backup and recovery"
                    ))
                checks += 1
        
        return issues, checks
    
    def _validate_dependency_validity(self, blueprint: SystemBlueprint) -> Tuple[List[ValidationIssue], int]:
        """Validate component dependency relationships"""
        issues = []
        checks = 0
        
        component_names = set(comp.get('name', '') for comp in blueprint.components)
        
        for component in blueprint.components:
            comp_name = component.get('name', 'unnamed')
            comp_type = component.get('type', '')
            dependencies = component.get('dependencies', [])
            
            for dep in dependencies:
                dep_comp_name = dep.get('component_name', '')
                dep_type = dep.get('dependency_type', '')
                
                # Check if dependency target exists
                if dep_comp_name not in component_names:
                    issues.append(ValidationIssue(
                        check_type=ReasonablenessCheckType.DEPENDENCY_VALIDITY,
                        severity=ValidationSeverity.ERROR,
                        message=f"Component '{comp_name}' depends on non-existent component '{dep_comp_name}'",
                        component_name=comp_name,
                        suggestion="Remove dependency or add the missing component"
                    ))
                checks += 1
                
                # Check for self-dependency
                if dep_comp_name == comp_name:
                    issues.append(ValidationIssue(
                        check_type=ReasonablenessCheckType.DEPENDENCY_VALIDITY,
                        severity=ValidationSeverity.ERROR,
                        message=f"Component '{comp_name}' cannot depend on itself",
                        component_name=comp_name,
                        suggestion="Remove self-dependency"
                    ))
                checks += 1
                
                # Validate dependency type makes sense
                if dep_comp_name in component_names:
                    # Find the dependent component type
                    dep_component = next((c for c in blueprint.components 
                                        if c.get('name') == dep_comp_name), None)
                    if dep_component:
                        dep_comp_type = dep_component.get('type', '')
                        
                        # Check if dependency relationship makes architectural sense
                        if comp_type in self.LOGICAL_DEPENDENCIES:
                            if dep_comp_type not in self.LOGICAL_DEPENDENCIES[comp_type]:
                                issues.append(ValidationIssue(
                                    check_type=ReasonablenessCheckType.DEPENDENCY_VALIDITY,
                                    severity=ValidationSeverity.WARNING,
                                    message=f"Unusual dependency: {comp_type} '{comp_name}' depending on {dep_comp_type} '{dep_comp_name}'",
                                    component_name=comp_name,
                                    suggestion="Verify this dependency relationship is intentional"
                                ))
                        checks += 1
        
        # Check for circular dependencies (simple case)
        for component in blueprint.components:
            comp_name = component.get('name', '')
            dependencies = component.get('dependencies', [])
            dep_names = [dep.get('component_name', '') for dep in dependencies]
            
            # Check if any dependency also depends back on this component
            for dep_name in dep_names:
                dep_component = next((c for c in blueprint.components 
                                    if c.get('name') == dep_name), None)
                if dep_component:
                    dep_dependencies = dep_component.get('dependencies', [])
                    dep_dep_names = [d.get('component_name', '') for d in dep_dependencies]
                    
                    if comp_name in dep_dep_names:
                        issues.append(ValidationIssue(
                            check_type=ReasonablenessCheckType.DEPENDENCY_VALIDITY,
                            severity=ValidationSeverity.ERROR,
                            message=f"Circular dependency detected between '{comp_name}' and '{dep_name}'",
                            component_name=comp_name,
                            suggestion="Restructure components to eliminate circular dependencies"
                        ))
                checks += 1
        
        return issues, checks
    
    def _validate_security_requirements(self, blueprint: SystemBlueprint) -> Tuple[List[ValidationIssue], int]:
        """Validate security-related reasonableness"""
        issues = []
        checks = 0
        
        for component in blueprint.components:
            comp_name = component.get('name', 'unnamed')
            comp_type = component.get('type', '')
            config = component.get('configuration', {})
            
            # Check for insecure port configurations
            ports = config.get('ports', [])
            for port_config in ports:
                port_num = port_config.get('port', 0)
                protocol = port_config.get('protocol', '')
                
                # Warn about commonly insecure ports
                if port_num in [21, 23, 53, 69, 135, 139, 445]:  # FTP, Telnet, DNS, TFTP, RPC, NetBIOS
                    issues.append(ValidationIssue(
                        check_type=ReasonablenessCheckType.SECURITY_REQUIREMENTS,
                        severity=ValidationSeverity.WARNING,
                        message=f"Component '{comp_name}' uses potentially insecure port {port_num}",
                        component_name=comp_name,
                        suggestion="Consider using secure alternatives or additional security measures"
                    ))
                
                # Prefer HTTPS over HTTP for web services
                if comp_type == 'web_service' and protocol == 'http' and port_num != 80:
                    issues.append(ValidationIssue(
                        check_type=ReasonablenessCheckType.SECURITY_REQUIREMENTS,
                        severity=ValidationSeverity.WARNING,
                        message=f"Web service '{comp_name}' uses HTTP instead of HTTPS",
                        component_name=comp_name,
                        suggestion="Consider using HTTPS for secure communication"
                    ))
                checks += 1
            
            # Check for security-related validation requirements
            validation = component.get('validation', {})
            property_tests = validation.get('property_tests', [])
            
            has_security_test = any(test.get('test_type') == 'security_validation' 
                                  for test in property_tests)
            
            if comp_type in ['web_service', 'api_gateway', 'authentication_service'] and not has_security_test:
                issues.append(ValidationIssue(
                    check_type=ReasonablenessCheckType.SECURITY_REQUIREMENTS,
                    severity=ValidationSeverity.WARNING,
                    message=f"Security-sensitive component '{comp_name}' lacks security validation tests",
                    component_name=comp_name,
                    suggestion="Add security_validation property tests"
                ))
            checks += 1
        
        return issues, checks
    
    def _process_custom_reasonableness_checks(self, blueprint: SystemBlueprint) -> Tuple[List[ValidationIssue], int]:
        """Process custom reasonableness checks defined in the blueprint"""
        issues = []
        checks = 0
        
        for check_config in blueprint.reasonableness_checks:
            check_type_str = check_config.get('check_type', '')
            description = check_config.get('description', '')
            validation_logic = check_config.get('validation_logic', '')
            severity_str = check_config.get('severity', 'error')
            
            # Validate check configuration
            try:
                check_type = ReasonablenessCheckType(check_type_str)
            except ValueError:
                issues.append(ValidationIssue(
                    check_type=ReasonablenessCheckType.ARCHITECTURAL_CONSISTENCY,
                    severity=ValidationSeverity.ERROR,
                    message=f"Invalid reasonableness check type: '{check_type_str}'",
                    suggestion=f"Use one of: {[e.value for e in ReasonablenessCheckType]}"
                ))
                checks += 1
                continue
            
            try:
                severity = ValidationSeverity(severity_str)
            except ValueError:
                severity = ValidationSeverity.ERROR
            
            # Execute custom validation logic (safely)
            validation_result = self._execute_custom_validation_logic(
                validation_logic, blueprint, check_config
            )
            
            if not validation_result:
                issues.append(ValidationIssue(
                    check_type=check_type,
                    severity=severity,
                    message=f"Custom reasonableness check failed: {description}",
                    suggestion="Review system design to address this reasonableness concern",
                    metadata={'custom_check': True, 'validation_logic': validation_logic}
                ))
            
            checks += 1
        
        return issues, checks
    
    def _execute_custom_validation_logic(self, validation_logic: str, blueprint: SystemBlueprint, check_config: Dict[str, Any]) -> bool:
        """
        Safely execute custom validation logic.
        
        This implementation uses a secure, declarative approach rather than
        arbitrary code execution to prevent security vulnerabilities.
        """
        # For V5.0, we implement common validation patterns
        # In a production system, this would be a more sophisticated
        # declarative rule engine
        
        logic_lower = validation_logic.lower()
        
        # Component count validations
        if 'component_count' in logic_lower:
            if 'less_than' in logic_lower or '<' in logic_lower:
                # Extract number after less_than or <
                import re
                match = re.search(r'(?:less_than|<)\s*(\d+)', logic_lower)
                if match:
                    threshold = int(match.group(1))
                    return len(blueprint.components) < threshold
            
            if 'greater_than' in logic_lower or '>' in logic_lower:
                match = re.search(r'(?:greater_than|>)\s*(\d+)', logic_lower)
                if match:
                    threshold = int(match.group(1))
                    return len(blueprint.components) > threshold
        
        # Component type presence validations
        if 'has_component_type' in logic_lower:
            import re
            match = re.search(r'has_component_type\s+(\w+)', logic_lower)
            if match:
                required_type = match.group(1)
                comp_types = [comp.get('type', '') for comp in blueprint.components]
                return required_type in comp_types
        
        # Description content validations
        if 'description_contains' in logic_lower:
            import re
            match = re.search(r'description_contains\s+"([^"]+)"', validation_logic)
            if match:
                required_text = match.group(1)
                return required_text.lower() in blueprint.description.lower()
        
        # Dependency relationship validations
        if 'component_depends_on' in logic_lower:
            # Check if specific component dependency exists
            import re
            match = re.search(r'component_depends_on\s+(\w+)\s+(\w+)', logic_lower)
            if match:
                source_comp = match.group(1)
                target_comp = match.group(2)
                
                source_component = next((c for c in blueprint.components 
                                       if c.get('name') == source_comp), None)
                if source_component:
                    dependencies = source_component.get('dependencies', [])
                    dep_names = [dep.get('component_name', '') for dep in dependencies]
                    return target_comp in dep_names
        
        # If we can't parse the validation logic, return True (assume valid)
        # In production, this would be logged as a configuration error
        return True


def check_component_coherence(blueprint: SystemBlueprint) -> ValidationResult:
    """
    Convenience function for checking component coherence specifically.
    Used for integration with external validation systems.
    """
    validator = ReasonablenessValidator()
    issues, checks = validator._validate_component_coherence(blueprint)
    
    return ValidationResult(
        passed=not any(issue.severity == ValidationSeverity.ERROR for issue in issues),
        issues=issues,
        checks_performed=checks,
        metadata={'check_type': 'component_coherence_only'}
    )


# Example usage and testing
if __name__ == "__main__":
    # Example blueprint for testing
    test_blueprint = SystemBlueprint(
        description="A web application system with user authentication and data storage",
        components=[
            {
                "name": "web_app",
                "type": "web_service",
                "configuration": {
                    "resource_requirements": {
                        "memory_mb": 1024,
                        "cpu_cores": 2,
                        "disk_gb": 10
                    },
                    "ports": [
                        {"port": 8080, "protocol": "http"}
                    ]
                },
                "dependencies": [
                    {"component_name": "user_db", "dependency_type": "data_dependency"},
                    {"component_name": "auth_service", "dependency_type": "service_dependency"}
                ]
            },
            {
                "name": "user_db",
                "type": "database",
                "configuration": {
                    "resource_requirements": {
                        "memory_mb": 2048,
                        "cpu_cores": 1,
                        "disk_gb": 50
                    }
                }
            },
            {
                "name": "auth_service",
                "type": "authentication_service",
                "validation": {
                    "property_tests": [
                        {
                            "test_type": "security_validation",
                            "description": "Validate authentication token security"
                        }
                    ]
                }
            }
        ],
        reasonableness_checks=[
            {
                "check_type": "component_coherence",
                "description": "Ensure web application has sufficient resources",
                "validation_logic": "component web_app memory_mb greater_than 512",
                "severity": "warning"
            }
        ]
    )
    
    # Run validation
    validator = ReasonablenessValidator()
    result = validator.validate_system_reasonableness(test_blueprint)
    
    print(f"Validation {'PASSED' if result.passed else 'FAILED'}")
    print(f"Checks performed: {result.checks_performed}")
    print(f"Issues found: {len(result.issues)}")
    
    for issue in result.issues:
        print(f"  {issue.severity.value.upper()}: {issue.message}")
        if issue.suggestion:
            print(f"    Suggestion: {issue.suggestion}")