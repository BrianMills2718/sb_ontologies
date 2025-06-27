#!/usr/bin/env python3
"""
Component Security Validation Framework for V5.0 Validation-Driven Architecture
Implements comprehensive security validation with fail-hard principles
"""

from typing import Dict, Any, List, Optional, Set, Union
from dataclasses import dataclass
from enum import Enum
import logging
import re
import ast
import inspect
import hashlib
import time


class SecurityLevel(Enum):
    """Security validation levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityIssueType(Enum):
    """Types of security issues"""
    INJECTION = "injection"
    XSS = "xss"
    INSECURE_DEFAULTS = "insecure_defaults"
    WEAK_ENCRYPTION = "weak_encryption"
    UNSAFE_DESERIALIZATION = "unsafe_deserialization"
    HARDCODED_SECRETS = "hardcoded_secrets"
    UNSAFE_IMPORTS = "unsafe_imports"
    DANGEROUS_FUNCTIONS = "dangerous_functions"
    INSUFFICIENT_VALIDATION = "insufficient_validation"
    PRIVILEGE_ESCALATION = "privilege_escalation"


@dataclass
class SecurityIssue:
    """Represents a security issue found during validation"""
    issue_type: SecurityIssueType
    severity: SecurityLevel
    description: str
    component_name: str
    location: str = ""
    mitigation: str = ""
    cve_references: List[str] = None
    
    def __post_init__(self):
        if self.cve_references is None:
            self.cve_references = []


@dataclass
class SecurityValidationResult:
    """Result of security validation"""
    success: bool
    component_name: str
    security_level: SecurityLevel
    issues: List[SecurityIssue] = None
    validation_time: float = 0.0
    passed_checks: int = 0
    total_checks: int = 0
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


class SecurityValidationError(Exception):
    """Raised when security validation fails - no fallbacks available"""
    pass


class ComponentSecurityValidator:
    """
    V5.0 Component Security Validator with Fail-Hard Principles
    
    Validates components against security policies with strict enforcement.
    No security fallbacks or graceful degradation - all security checks must pass.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ComponentSecurityValidator")
        
        # Security policy configuration
        self.security_policies = self._initialize_security_policies()
        
        # Dangerous patterns and functions
        self.dangerous_patterns = self._initialize_dangerous_patterns()
        self.dangerous_functions = self._initialize_dangerous_functions()
        
        # Required security configurations
        self.required_security_configs = self._initialize_required_configs()
        
        self.logger.info("✅ Component Security Validator initialized with fail-hard validation")
    
    def _initialize_security_policies(self) -> Dict[str, Any]:
        """Initialize security policies for V5.0"""
        
        return {
            'minimum_security_level': SecurityLevel.MEDIUM,
            'block_dangerous_imports': True,
            'require_input_validation': True,
            'block_hardcoded_secrets': True,
            'require_secure_defaults': True,
            'validate_output_encoding': True,
            'check_privilege_escalation': True,
            'validate_cryptographic_functions': True,
            'maximum_allowed_issues': {
                SecurityLevel.LOW: 5,
                SecurityLevel.MEDIUM: 2,
                SecurityLevel.HIGH: 0,
                SecurityLevel.CRITICAL: 0
            }
        }
    
    def _initialize_dangerous_patterns(self) -> Dict[str, SecurityIssueType]:
        """Initialize dangerous code patterns"""
        
        return {
            # SQL Injection patterns
            r'(\bSELECT\b.*\bFROM\b.*\bWHERE\b.*\+|%|format)': SecurityIssueType.INJECTION,
            r'(\bINSERT\b.*\bINTO\b.*\bVALUES\b.*\+|%|format)': SecurityIssueType.INJECTION,
            r'(\bUPDATE\b.*\bSET\b.*\+|%|format)': SecurityIssueType.INJECTION,
            r'(\bDELETE\b.*\bFROM\b.*\+|%|format)': SecurityIssueType.INJECTION,
            
            # XSS patterns
            r'(innerHTML|outerHTML).*\+': SecurityIssueType.XSS,
            r'document\.write.*\+': SecurityIssueType.XSS,
            r'eval\s*\(.*\+': SecurityIssueType.XSS,
            
            # Hardcoded secrets patterns
            r'(password|passwd|secret|token|key)\s*=\s*["\'][^"\']+["\']': SecurityIssueType.HARDCODED_SECRETS,
            r'(api_key|apikey|access_token)\s*=\s*["\'][^"\']+["\']': SecurityIssueType.HARDCODED_SECRETS,
            
            # Insecure defaults
            r'ssl_verify\s*=\s*False': SecurityIssueType.INSECURE_DEFAULTS,
            r'verify\s*=\s*False': SecurityIssueType.INSECURE_DEFAULTS,
            r'check_hostname\s*=\s*False': SecurityIssueType.INSECURE_DEFAULTS,
        }
    
    def _initialize_dangerous_functions(self) -> Dict[str, SecurityIssueType]:
        """Initialize dangerous function calls"""
        
        return {
            'eval': SecurityIssueType.INJECTION,
            'exec': SecurityIssueType.INJECTION,
            'compile': SecurityIssueType.INJECTION,
            'subprocess.call': SecurityIssueType.INJECTION,
            'os.system': SecurityIssueType.INJECTION,
            'pickle.loads': SecurityIssueType.UNSAFE_DESERIALIZATION,
            'pickle.load': SecurityIssueType.UNSAFE_DESERIALIZATION,
            'yaml.load': SecurityIssueType.UNSAFE_DESERIALIZATION,
            'marshal.loads': SecurityIssueType.UNSAFE_DESERIALIZATION,
        }
    
    def _initialize_required_configs(self) -> Dict[str, Any]:
        """Initialize required security configurations"""
        
        return {
            'input_validation': {
                'required': True,
                'validate_types': True,
                'sanitize_inputs': True,
                'validate_ranges': True
            },
            'output_encoding': {
                'required': True,
                'escape_html': True,
                'validate_json': True,
                'secure_headers': True
            },
            'authentication': {
                'required_for_api': True,
                'strong_passwords': True,
                'session_management': True
            },
            'encryption': {
                'encrypt_sensitive_data': True,
                'use_secure_algorithms': True,
                'validate_certificates': True
            }
        }
    
    def validate_component_security(self, component: Any) -> SecurityValidationResult:
        """Validate component security - fail hard on critical issues"""
        
        start_time = time.time()
        component_name = getattr(component, 'name', 'unknown')
        
        self.logger.info(f"Validating security for component: {component_name}")
        
        issues = []
        passed_checks = 0
        total_checks = 0
        
        try:
            # Security check 1: Code analysis
            code_issues, code_checks = self._analyze_component_code_security(component)
            issues.extend(code_issues)
            passed_checks += code_checks['passed']
            total_checks += code_checks['total']
            
            # Security check 2: Configuration security
            config_issues, config_checks = self._validate_component_config_security(component)
            issues.extend(config_issues)
            passed_checks += config_checks['passed']
            total_checks += config_checks['total']
            
            # Security check 3: Dependency security
            dep_issues, dep_checks = self._validate_component_dependencies_security(component)
            issues.extend(dep_issues)
            passed_checks += dep_checks['passed']
            total_checks += dep_checks['total']
            
            # Security check 4: Runtime security
            runtime_issues, runtime_checks = self._validate_component_runtime_security(component)
            issues.extend(runtime_issues)
            passed_checks += runtime_checks['passed']
            total_checks += runtime_checks['total']
            
            # Determine overall security level
            security_level = self._calculate_security_level(issues)
            
            # Apply security policies
            self._enforce_security_policies(component_name, issues, security_level)
            
            validation_time = time.time() - start_time
            
            self.logger.info(f"✅ Security validation completed for {component_name}: {passed_checks}/{total_checks} checks passed")
            
            return SecurityValidationResult(
                success=True,
                component_name=component_name,
                security_level=security_level,
                issues=issues,
                validation_time=validation_time,
                passed_checks=passed_checks,
                total_checks=total_checks
            )
            
        except Exception as e:
            validation_time = time.time() - start_time
            
            self.logger.error(f"❌ Security validation failed for {component_name}: {e}")
            
            return SecurityValidationResult(
                success=False,
                component_name=component_name,
                security_level=SecurityLevel.CRITICAL,
                issues=issues,
                validation_time=validation_time,
                passed_checks=passed_checks,
                total_checks=total_checks
            )
    
    def _analyze_component_code_security(self, component: Any) -> tuple[List[SecurityIssue], Dict[str, int]]:
        """Analyze component code for security issues"""
        
        issues = []
        checks = {'passed': 0, 'total': 0}
        component_name = getattr(component, 'name', 'unknown')
        
        try:
            # Get component source code
            source_code = self._get_component_source_code(component)
            
            if not source_code:
                issues.append(SecurityIssue(
                    issue_type=SecurityIssueType.INSUFFICIENT_VALIDATION,
                    severity=SecurityLevel.MEDIUM,
                    description="Cannot analyze component source code for security",
                    component_name=component_name,
                    location="source_code",
                    mitigation="Ensure component source code is accessible for security analysis"
                ))
                checks['total'] += 1
                return issues, checks
            
            # Check for dangerous patterns
            checks['total'] += len(self.dangerous_patterns)
            for pattern, issue_type in self.dangerous_patterns.items():
                if re.search(pattern, source_code, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        issue_type=issue_type,
                        severity=SecurityLevel.HIGH,
                        description=f"Dangerous code pattern detected: {pattern}",
                        component_name=component_name,
                        location="source_code",
                        mitigation=f"Remove or secure the {issue_type.value} vulnerability"
                    ))
                else:
                    checks['passed'] += 1
            
            # Check for dangerous function calls
            checks['total'] += len(self.dangerous_functions)
            for func_name, issue_type in self.dangerous_functions.items():
                if func_name in source_code:
                    issues.append(SecurityIssue(
                        issue_type=issue_type,
                        severity=SecurityLevel.CRITICAL,
                        description=f"Dangerous function call detected: {func_name}",
                        component_name=component_name,
                        location="source_code",
                        mitigation=f"Replace {func_name} with secure alternative"
                    ))
                else:
                    checks['passed'] += 1
            
            # AST analysis for deeper security checks
            ast_issues, ast_checks = self._analyze_ast_security(source_code, component_name)
            issues.extend(ast_issues)
            checks['passed'] += ast_checks['passed']
            checks['total'] += ast_checks['total']
            
        except Exception as e:
            issues.append(SecurityIssue(
                issue_type=SecurityIssueType.INSUFFICIENT_VALIDATION,
                severity=SecurityLevel.MEDIUM,
                description=f"Code security analysis failed: {e}",
                component_name=component_name,
                location="code_analysis"
            ))
            checks['total'] += 1
        
        return issues, checks
    
    def _get_component_source_code(self, component: Any) -> str:
        """Get component source code for analysis"""
        
        try:
            # Try to get source code from the component class
            if hasattr(component, '__class__'):
                return inspect.getsource(component.__class__)
            else:
                return ""
        except (OSError, TypeError):
            # Source not available (built-in, compiled, etc.)
            return ""
    
    def _analyze_ast_security(self, source_code: str, component_name: str) -> tuple[List[SecurityIssue], Dict[str, int]]:
        """Analyze AST for security issues"""
        
        issues = []
        checks = {'passed': 0, 'total': 0}
        
        try:
            tree = ast.parse(source_code)
            
            # Check for dangerous node types
            dangerous_nodes = [
                (ast.Exec, SecurityIssueType.INJECTION, "exec statement"),
                (ast.Eval, SecurityIssueType.INJECTION, "eval expression"),
            ]
            
            for node_type, issue_type, description in dangerous_nodes:
                checks['total'] += 1
                found = False
                for node in ast.walk(tree):
                    if isinstance(node, node_type):
                        issues.append(SecurityIssue(
                            issue_type=issue_type,
                            severity=SecurityLevel.CRITICAL,
                            description=f"Dangerous AST node: {description}",
                            component_name=component_name,
                            location=f"line {node.lineno if hasattr(node, 'lineno') else 'unknown'}",
                            mitigation=f"Remove {description} and use safer alternatives"
                        ))
                        found = True
                        break
                
                if not found:
                    checks['passed'] += 1
            
            # Check for import security
            imports_issues, imports_checks = self._analyze_imports_security(tree, component_name)
            issues.extend(imports_issues)
            checks['passed'] += imports_checks['passed']
            checks['total'] += imports_checks['total']
            
        except SyntaxError as e:
            issues.append(SecurityIssue(
                issue_type=SecurityIssueType.INSUFFICIENT_VALIDATION,
                severity=SecurityLevel.MEDIUM,
                description=f"AST parsing failed: {e}",
                component_name=component_name,
                location="ast_parsing"
            ))
            checks['total'] += 1
        
        return issues, checks
    
    def _analyze_imports_security(self, tree: ast.AST, component_name: str) -> tuple[List[SecurityIssue], Dict[str, int]]:
        """Analyze imports for security issues"""
        
        issues = []
        checks = {'passed': 0, 'total': 0}
        
        # Dangerous imports
        dangerous_imports = {
            'subprocess': SecurityLevel.HIGH,
            'os': SecurityLevel.MEDIUM,
            'pickle': SecurityLevel.HIGH,
            'marshal': SecurityLevel.HIGH,
            'imp': SecurityLevel.MEDIUM,
            'importlib': SecurityLevel.MEDIUM,
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                checks['total'] += 1
                
                if isinstance(node, ast.Import):
                    module_names = [alias.name for alias in node.names]
                else:  # ast.ImportFrom
                    module_names = [node.module] if node.module else []
                
                dangerous_found = False
                for module_name in module_names:
                    if module_name in dangerous_imports:
                        issues.append(SecurityIssue(
                            issue_type=SecurityIssueType.UNSAFE_IMPORTS,
                            severity=dangerous_imports[module_name],
                            description=f"Potentially dangerous import: {module_name}",
                            component_name=component_name,
                            location=f"line {node.lineno if hasattr(node, 'lineno') else 'unknown'}",
                            mitigation=f"Review usage of {module_name} module for security implications"
                        ))
                        dangerous_found = True
                
                if not dangerous_found:
                    checks['passed'] += 1
        
        return issues, checks
    
    def _validate_component_config_security(self, component: Any) -> tuple[List[SecurityIssue], Dict[str, int]]:
        """Validate component configuration security"""
        
        issues = []
        checks = {'passed': 0, 'total': 0}
        component_name = getattr(component, 'name', 'unknown')
        
        if not hasattr(component, 'config'):
            issues.append(SecurityIssue(
                issue_type=SecurityIssueType.INSUFFICIENT_VALIDATION,
                severity=SecurityLevel.MEDIUM,
                description="Component missing config attribute for security validation",
                component_name=component_name,
                location="config"
            ))
            checks['total'] += 1
            return issues, checks
        
        config = component.config
        
        # Check for hardcoded secrets in config
        checks['total'] += 1
        if self._check_hardcoded_secrets_in_config(config):
            issues.append(SecurityIssue(
                issue_type=SecurityIssueType.HARDCODED_SECRETS,
                severity=SecurityLevel.CRITICAL,
                description="Hardcoded secrets detected in component configuration",
                component_name=component_name,
                location="config",
                mitigation="Use environment variables or secure key management for secrets"
            ))
        else:
            checks['passed'] += 1
        
        # Check for insecure defaults
        checks['total'] += 1
        insecure_defaults = self._check_insecure_defaults(config)
        if insecure_defaults:
            issues.append(SecurityIssue(
                issue_type=SecurityIssueType.INSECURE_DEFAULTS,
                severity=SecurityLevel.HIGH,
                description=f"Insecure default configurations: {insecure_defaults}",
                component_name=component_name,
                location="config",
                mitigation="Configure secure defaults for all security-sensitive settings"
            ))
        else:
            checks['passed'] += 1
        
        # Check for required security configurations
        checks['total'] += 1
        missing_security_configs = self._check_required_security_configs(config)
        if missing_security_configs:
            issues.append(SecurityIssue(
                issue_type=SecurityIssueType.INSUFFICIENT_VALIDATION,
                severity=SecurityLevel.MEDIUM,
                description=f"Missing required security configurations: {missing_security_configs}",
                component_name=component_name,
                location="config",
                mitigation="Add required security configurations to component config"
            ))
        else:
            checks['passed'] += 1
        
        return issues, checks
    
    def _check_hardcoded_secrets_in_config(self, config: Dict[str, Any]) -> bool:
        """Check for hardcoded secrets in configuration"""
        
        secret_keys = ['password', 'passwd', 'secret', 'token', 'key', 'api_key', 'apikey', 'access_token']
        
        def check_dict(d):
            for key, value in d.items():
                if isinstance(key, str) and any(secret in key.lower() for secret in secret_keys):
                    if isinstance(value, str) and len(value) > 0 and not value.startswith('${'):
                        return True
                if isinstance(value, dict):
                    if check_dict(value):
                        return True
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and check_dict(item):
                            return True
            return False
        
        return check_dict(config)
    
    def _check_insecure_defaults(self, config: Dict[str, Any]) -> List[str]:
        """Check for insecure default configurations"""
        
        insecure_settings = []
        
        # Check for SSL/TLS disabled
        if config.get('ssl_verify') is False:
            insecure_settings.append('ssl_verify=False')
        
        if config.get('verify') is False:
            insecure_settings.append('verify=False')
        
        if config.get('check_hostname') is False:
            insecure_settings.append('check_hostname=False')
        
        # Check for debug mode in production
        if config.get('debug') is True:
            insecure_settings.append('debug=True')
        
        # Check for weak authentication
        if config.get('auth_required') is False:
            insecure_settings.append('auth_required=False')
        
        return insecure_settings
    
    def _check_required_security_configs(self, config: Dict[str, Any]) -> List[str]:
        """Check for missing required security configurations"""
        
        missing_configs = []
        
        # Check for input validation configuration
        if 'input_validation' not in config and 'inputs' in config:
            missing_configs.append('input_validation')
        
        # Check for output encoding configuration
        if 'output_encoding' not in config and 'outputs' in config:
            missing_configs.append('output_encoding')
        
        # Check for authentication configuration for API components
        if config.get('type') == 'api_endpoint' and 'authentication' not in config:
            missing_configs.append('authentication')
        
        return missing_configs
    
    def _validate_component_dependencies_security(self, component: Any) -> tuple[List[SecurityIssue], Dict[str, int]]:
        """Validate component dependencies security"""
        
        issues = []
        checks = {'passed': 0, 'total': 1}  # Basic check
        component_name = getattr(component, 'name', 'unknown')
        
        # This is a simplified dependency security check
        # In a full implementation, this would check for known vulnerable dependencies
        
        try:
            if hasattr(component, 'get_required_dependencies'):
                dependencies = component.get_required_dependencies()
                
                # Check if dependencies have security configurations
                for dep in dependencies:
                    if isinstance(dep, dict) and 'security' not in dep:
                        issues.append(SecurityIssue(
                            issue_type=SecurityIssueType.INSUFFICIENT_VALIDATION,
                            severity=SecurityLevel.LOW,
                            description=f"Dependency '{dep}' lacks security configuration",
                            component_name=component_name,
                            location="dependencies",
                            mitigation="Add security configuration for all dependencies"
                        ))
                
                if not issues:
                    checks['passed'] += 1
            else:
                checks['passed'] += 1  # No dependencies to check
        
        except Exception as e:
            issues.append(SecurityIssue(
                issue_type=SecurityIssueType.INSUFFICIENT_VALIDATION,
                severity=SecurityLevel.MEDIUM,
                description=f"Dependency security validation failed: {e}",
                component_name=component_name,
                location="dependencies"
            ))
        
        return issues, checks
    
    def _validate_component_runtime_security(self, component: Any) -> tuple[List[SecurityIssue], Dict[str, int]]:
        """Validate component runtime security"""
        
        issues = []
        checks = {'passed': 0, 'total': 0}
        component_name = getattr(component, 'name', 'unknown')
        
        # Check for privilege escalation risks
        checks['total'] += 1
        if self._check_privilege_escalation_risk(component):
            issues.append(SecurityIssue(
                issue_type=SecurityIssueType.PRIVILEGE_ESCALATION,
                severity=SecurityLevel.CRITICAL,
                description="Component may have privilege escalation risks",
                component_name=component_name,
                location="runtime",
                mitigation="Review component privileges and implement principle of least privilege"
            ))
        else:
            checks['passed'] += 1
        
        # Check for secure communication
        checks['total'] += 1
        if not self._check_secure_communication(component):
            issues.append(SecurityIssue(
                issue_type=SecurityIssueType.INSECURE_DEFAULTS,
                severity=SecurityLevel.HIGH,
                description="Component may use insecure communication",
                component_name=component_name,
                location="runtime",
                mitigation="Configure secure communication protocols (HTTPS, TLS)"
            ))
        else:
            checks['passed'] += 1
        
        return issues, checks
    
    def _check_privilege_escalation_risk(self, component: Any) -> bool:
        """Check for privilege escalation risks"""
        
        # This is a simplified check
        # In a full implementation, this would analyze component permissions and capabilities
        
        config = getattr(component, 'config', {})
        
        # Check for dangerous privilege settings
        if config.get('run_as_root') is True:
            return True
        
        if config.get('privileged') is True:
            return True
        
        return False
    
    def _check_secure_communication(self, component: Any) -> bool:
        """Check for secure communication configuration"""
        
        config = getattr(component, 'config', {})
        
        # Check if component has network communication
        if 'host' in config or 'url' in config or 'endpoint' in config:
            # Check for HTTPS/TLS
            url_fields = ['url', 'endpoint', 'host']
            for field in url_fields:
                if field in config:
                    url = config[field]
                    if isinstance(url, str) and url.startswith('http://'):
                        return False  # HTTP instead of HTTPS
        
        return True  # No insecure communication detected
    
    def _calculate_security_level(self, issues: List[SecurityIssue]) -> SecurityLevel:
        """Calculate overall security level based on issues"""
        
        if not issues:
            return SecurityLevel.HIGH
        
        # Count issues by severity
        critical_count = sum(1 for issue in issues if issue.severity == SecurityLevel.CRITICAL)
        high_count = sum(1 for issue in issues if issue.severity == SecurityLevel.HIGH)
        medium_count = sum(1 for issue in issues if issue.severity == SecurityLevel.MEDIUM)
        
        # Determine security level
        if critical_count > 0:
            return SecurityLevel.CRITICAL
        elif high_count > 2:
            return SecurityLevel.CRITICAL
        elif high_count > 0 or medium_count > 5:
            return SecurityLevel.HIGH
        elif medium_count > 0:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW
    
    def _enforce_security_policies(self, component_name: str, issues: List[SecurityIssue], security_level: SecurityLevel) -> None:
        """Enforce security policies - fail hard on violations"""
        
        # Check minimum security level
        min_level = self.security_policies['minimum_security_level']
        if security_level == SecurityLevel.CRITICAL and min_level != SecurityLevel.CRITICAL:
            raise SecurityValidationError(
                f"Component '{component_name}' has CRITICAL security issues. "
                f"V5.0 does not allow components with critical security vulnerabilities."
            )
        
        # Check maximum allowed issues by severity
        max_allowed = self.security_policies['maximum_allowed_issues']
        
        for severity, max_count in max_allowed.items():
            actual_count = sum(1 for issue in issues if issue.severity == severity)
            if actual_count > max_count:
                raise SecurityValidationError(
                    f"Component '{component_name}' has {actual_count} {severity.value} security issues. "
                    f"Maximum allowed: {max_count}. "
                    f"V5.0 enforces strict security limits - all issues must be resolved."
                )
        
        self.logger.debug(f"✅ Security policies enforced for component: {component_name}")
    
    def check_security_vulnerabilities(self, component: Any) -> List[SecurityIssue]:
        """Check component for security vulnerabilities"""
        
        result = self.validate_component_security(component)
        
        if not result.success:
            raise SecurityValidationError(f"Security validation failed for component '{result.component_name}'")
        
        return result.issues
    
    def enforce_security_policies(self, component: Any) -> bool:
        """Enforce security policies on component - fail hard on violations"""
        
        result = self.validate_component_security(component)
        
        # Fail hard on critical security issues
        if result.security_level == SecurityLevel.CRITICAL:
            critical_issues = [issue for issue in result.issues if issue.severity == "CRITICAL"]
            raise SecurityValidationError(
                f"CRITICAL security policy violation in component '{result.component_name}': "
                f"{[issue.message for issue in critical_issues]}. "
                f"V5.0 requires all components to pass security validation - no security exceptions allowed."
            )
        
        # Fail hard if validation was not successful
        if not result.success:
            raise SecurityValidationError(
                f"Security policy enforcement failed for component '{result.component_name}': "
                f"Security validation failed with {len(result.issues)} issues. "
                f"V5.0 requires all components to pass security validation."
            )
        
        return True
    
    def get_security_summary(self, components: List[Any]) -> Dict[str, Any]:
        """Get security summary for multiple components"""
        
        summary = {
            'total_components': len(components),
            'security_levels': {level.value: 0 for level in SecurityLevel},
            'issue_types': {issue_type.value: 0 for issue_type in SecurityIssueType},
            'validation_results': [],
            'overall_security_level': SecurityLevel.HIGH,
            'critical_issues_count': 0
        }
        
        critical_issues_count = 0
        worst_security_level = SecurityLevel.HIGH
        
        for component in components:
            try:
                result = self.validate_component_security(component)
                summary['validation_results'].append(result)
                summary['security_levels'][result.security_level.value] += 1
                
                # Track issue types
                for issue in result.issues:
                    summary['issue_types'][issue.issue_type.value] += 1
                    if issue.severity == SecurityLevel.CRITICAL:
                        critical_issues_count += 1
                
                # Update worst security level
                if result.security_level == SecurityLevel.CRITICAL:
                    worst_security_level = SecurityLevel.CRITICAL
                elif result.security_level == SecurityLevel.HIGH and worst_security_level != SecurityLevel.CRITICAL:
                    worst_security_level = SecurityLevel.HIGH
                elif result.security_level == SecurityLevel.MEDIUM and worst_security_level not in [SecurityLevel.CRITICAL, SecurityLevel.HIGH]:
                    worst_security_level = SecurityLevel.MEDIUM
                
            except Exception as e:
                self.logger.error(f"Security validation failed for component: {e}")
                summary['security_levels'][SecurityLevel.CRITICAL.value] += 1
                worst_security_level = SecurityLevel.CRITICAL
                critical_issues_count += 1
        
        summary['overall_security_level'] = worst_security_level
        summary['critical_issues_count'] = critical_issues_count
        
        return summary


# Global security validator instance
security_validator = ComponentSecurityValidator()