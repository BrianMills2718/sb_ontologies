"""
V5.0 Security Validation System

This module provides comprehensive security validation for property tests and blueprint
configurations, ensuring NO arbitrary code execution and preventing security vulnerabilities
in the V5.0 blueprint schema system.

SECURITY PRINCIPLES:
1. NO arbitrary code execution (no eval, exec, compile, etc.)
2. All validation logic is predefined and sandboxed
3. Input sanitization and validation for all parameters
4. Comprehensive threat detection and prevention
5. Fail-safe defaults for all security checks
"""

import re
import json
import hashlib
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum
import ast


class SecurityThreatLevel(Enum):
    """Security threat classification levels"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityViolationType(Enum):
    """Types of security violations detected"""
    CODE_INJECTION = "code_injection"
    PATH_TRAVERSAL = "path_traversal"
    REGEX_DOS = "regex_dos"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    INFORMATION_DISCLOSURE = "information_disclosure"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNSAFE_PROTOCOL = "unsafe_protocol"
    MALFORMED_INPUT = "malformed_input"


@dataclass
class SecurityViolation:
    """Individual security violation detected"""
    violation_type: SecurityViolationType
    threat_level: SecurityThreatLevel
    description: str
    detected_pattern: str
    location: str
    mitigation: str
    blocked: bool = True


@dataclass
class SecurityScanResult:
    """Result of comprehensive security scan"""
    is_secure: bool
    overall_threat_level: SecurityThreatLevel
    violations: List[SecurityViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    scan_metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def critical_violations(self) -> List[SecurityViolation]:
        """Get critical security violations"""
        return [v for v in self.violations if v.threat_level == SecurityThreatLevel.CRITICAL]
    
    @property
    def high_violations(self) -> List[SecurityViolation]:
        """Get high-risk security violations"""
        return [v for v in self.violations if v.threat_level == SecurityThreatLevel.HIGH]
    
    @property
    def blocked_violations(self) -> List[SecurityViolation]:
        """Get violations that result in blocking"""
        return [v for v in self.violations if v.blocked]


class SecurityPatternDatabase:
    """
    Database of security patterns for threat detection.
    
    This class maintains comprehensive patterns for detecting various
    security threats in blueprint parameters and configurations.
    """
    
    def __init__(self):
        # Critical patterns that ALWAYS result in blocking
        self.CRITICAL_PATTERNS = {
            # Code execution patterns
            SecurityViolationType.CODE_INJECTION: [
                r'__import__\s*\(',
                r'eval\s*\(',
                r'exec\s*\(',
                r'compile\s*\(',
                r'execfile\s*\(',
                r'reload\s*\(',
                r'getattr\s*\(',
                r'setattr\s*\(',
                r'hasattr\s*\(',
                r'delattr\s*\(',
                r'globals\s*\(',
                r'locals\s*\(',
                r'vars\s*\(',
                r'dir\s*\(',
                r'callable\s*\(',
                r'lambda\s*[:=]',
                r'yield\s+',
                r'import\s+\w+',
                r'from\s+\w+\s+import',
                r'__[a-zA-Z_]+__',  # Dunder methods
                r'subprocess\.',
                r'os\.',
                r'sys\.',
                r'shutil\.',
                r'pickle\.',
                r'marshal\.',
                r'socket\.',
                r'urllib',
                r'http\.',
                r'ftplib\.',
                r'telnetlib\.',
                r'smtplib\.',
            ],
            
            # Path traversal patterns
            SecurityViolationType.PATH_TRAVERSAL: [
                r'\.\./+',
                r'\.\.\\+',
                r'/etc/passwd',
                r'/etc/shadow',
                r'C:\\Windows\\System32',
                r'\.\.[\\/]',
                r'~[\\/]',
                r'/root/',
                r'/home/[^/]+/\.',
                r'\\\\[^\\]+\\',  # UNC paths
            ],
            
            # Privilege escalation patterns
            SecurityViolationType.PRIVILEGE_ESCALATION: [
                r'\bsudo\b',
                r'\bsu\b\s',
                r'\bchmod\s+777',
                r'\bchown\s+root',
                r'\brunas\b',
                r'\belevate\b',
                r'\badministrator\b',
                r'\broot\b.*password',
                r'\bsetuid\b',
                r'\bsetgid\b',
            ]
        }
        
        # High-risk patterns that usually result in blocking
        self.HIGH_RISK_PATTERNS = {
            # Resource exhaustion patterns
            SecurityViolationType.RESOURCE_EXHAUSTION: [
                r'\*{10,}',  # Excessive wildcards
                r'[0-9]{10,}',  # Very large numbers
                r'[\{\[\(]{5,}',  # Nested structures
                r'[\}\]\)]{5,}',
                r'.{1000,}',  # Very long strings
            ],
            
            # Information disclosure patterns
            SecurityViolationType.INFORMATION_DISCLOSURE: [
                r'\bpassword\s*[=:]\s*[\'"][^\'"]+[\'"]',
                r'\bsecret\s*[=:]\s*[\'"][^\'"]+[\'"]',
                r'\bapi[_-]?key\s*[=:]\s*[\'"][^\'"]+[\'"]',
                r'\btoken\s*[=:]\s*[\'"][^\'"]+[\'"]',
                r'\baccess[_-]?key\s*[=:]\s*[\'"][^\'"]+[\'"]',
                r'\bprivate[_-]?key\s*[=:]\s*[\'"][^\'"]+[\'"]',
                r'-----BEGIN\s+[A-Z\s]+KEY-----',
                r'[A-Za-z0-9+/]{32,}={0,2}',  # Base64 patterns that might be keys
            ],
            
            # Unsafe protocols
            SecurityViolationType.UNSAFE_PROTOCOL: [
                r'\bftp://',
                r'\btelnet://',
                r'\brsh://',
                r'\brlogin://',
                r'\bldap://',  # Non-SSL LDAP
                r'\bhttp://.*password',
                r'\bhttp://.*token',
            ]
        }
        
        # Medium-risk patterns that generate warnings
        self.MEDIUM_RISK_PATTERNS = {
            SecurityViolationType.MALFORMED_INPUT: [
                r'["\'].*["\'].*["\']',  # Multiple nested quotes
                r'.*\$\{.*\}.*',  # Variable interpolation
                r'.*`.*`.*',  # Backticks
                r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\xFF]',  # Control characters
                r'%[0-9a-fA-F]{2}',  # URL encoding that might hide attacks
                r'\\[xuU][0-9a-fA-F]{2,8}',  # Unicode/hex escapes
            ],
            
            # Potentially dangerous regex patterns (ReDoS)
            SecurityViolationType.REGEX_DOS: [
                r'\([^)]*\*[^)]*\)\*',  # (.*)*
                r'\([^)]*\+[^)]*\)\+',  # (.+)+
                r'\([^)]*\{[^}]*,[^}]*\}[^)]*\)\{[^}]*,[^}]*\}',  # Nested quantifiers
                r'\(\?\=[^)]*\)\*',  # (?=.*)*
                r'\(\?\![^)]*\)\*',  # (?!.*)*
            ]
        }
        
        # Compile all patterns for efficient matching
        self.compiled_patterns = {}
        for threat_level, categories in [
            (SecurityThreatLevel.CRITICAL, self.CRITICAL_PATTERNS),
            (SecurityThreatLevel.HIGH, self.HIGH_RISK_PATTERNS),
            (SecurityThreatLevel.MEDIUM, self.MEDIUM_RISK_PATTERNS)
        ]:
            self.compiled_patterns[threat_level] = {}
            for violation_type, patterns in categories.items():
                self.compiled_patterns[threat_level][violation_type] = [
                    re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                    for pattern in patterns
                ]


class PropertyTestSecurityValidator:
    """
    Advanced security validator specifically for property test parameters.
    
    This validator provides comprehensive security scanning for property test
    configurations to prevent code injection, data exfiltration, and other
    security vulnerabilities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pattern_db = SecurityPatternDatabase()
        
        # Security constraints
        self.MAX_STRING_LENGTH = 1000
        self.MAX_PARAMETER_DEPTH = 5
        self.MAX_PARAMETER_COUNT = 50
        self.MAX_REGEX_LENGTH = 200
        self.MAX_REGEX_GROUPS = 10
        
        # Allowed character sets for different contexts
        self.SAFE_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
        self.SAFE_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
        self.SAFE_URL_PATTERN = re.compile(r'^https?://[a-zA-Z0-9\-\._~:/?#\[\]@!$&\'()*+,;=%]+$')
    
    def validate_property_test_security(self, test_type: str, 
                                      parameters: Dict[str, Any]) -> SecurityScanResult:
        """
        Comprehensive security validation of property test parameters.
        
        Args:
            test_type: Type of property test being validated
            parameters: Parameters dictionary to validate
            
        Returns:
            SecurityScanResult with detailed security analysis
        """
        violations = []
        warnings = []
        scan_metadata = {
            'test_type': test_type,
            'parameter_count': 0,
            'parameter_depth': 0,
            'total_string_length': 0,
            'scan_time_ms': 0
        }
        
        import time
        start_time = time.time()
        
        try:
            # Convert parameters to JSON for analysis
            param_json = json.dumps(parameters, ensure_ascii=True, separators=(',', ':'))
            scan_metadata['total_string_length'] = len(param_json)
            scan_metadata['parameter_count'] = self._count_parameters(parameters)
            scan_metadata['parameter_depth'] = self._calculate_depth(parameters)
            
            # Basic structure validation
            structure_violations = self._validate_parameter_structure(parameters)
            violations.extend(structure_violations)
            
            # Pattern-based threat detection
            pattern_violations = self._scan_security_patterns(param_json, test_type)
            violations.extend(pattern_violations)
            
            # Test-type specific validation
            type_violations = self._validate_test_type_security(test_type, parameters)
            violations.extend(type_violations)
            
            # AST-based validation for any string that looks like code
            ast_violations = self._validate_ast_security(parameters)
            violations.extend(ast_violations)
            
            # Protocol and URL validation
            protocol_violations = self._validate_protocols_and_urls(parameters)
            violations.extend(protocol_violations)
            
        except Exception as e:
            self.logger.error(f"Security validation error: {e}")
            violations.append(SecurityViolation(
                violation_type=SecurityViolationType.MALFORMED_INPUT,
                threat_level=SecurityThreatLevel.HIGH,
                description=f"Security validation failed: {str(e)[:100]}",
                detected_pattern="validation_error",
                location="security_validator",
                mitigation="Review parameter format and content",
                blocked=True
            ))
        
        scan_metadata['scan_time_ms'] = (time.time() - start_time) * 1000
        
        # Determine overall threat level and security status
        overall_threat_level = self._calculate_overall_threat_level(violations)
        is_secure = overall_threat_level not in [SecurityThreatLevel.HIGH, SecurityThreatLevel.CRITICAL]
        
        return SecurityScanResult(
            is_secure=is_secure,
            overall_threat_level=overall_threat_level,
            violations=violations,
            warnings=warnings,
            scan_metadata=scan_metadata
        )
    
    def _count_parameters(self, obj: Any, count: int = 0) -> int:
        """Recursively count total parameters"""
        if isinstance(obj, dict):
            count += len(obj)
            for value in obj.values():
                count = self._count_parameters(value, count)
        elif isinstance(obj, list):
            count += len(obj)
            for item in obj:
                count = self._count_parameters(item, count)
        return count
    
    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_depth(value, current_depth + 1) for value in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth
    
    def _validate_parameter_structure(self, parameters: Dict[str, Any]) -> List[SecurityViolation]:
        """Validate basic parameter structure for security"""
        violations = []
        
        # Check parameter count
        param_count = self._count_parameters(parameters)
        if param_count > self.MAX_PARAMETER_COUNT:
            violations.append(SecurityViolation(
                violation_type=SecurityViolationType.RESOURCE_EXHAUSTION,
                threat_level=SecurityThreatLevel.HIGH,
                description=f"Excessive parameter count: {param_count} > {self.MAX_PARAMETER_COUNT}",
                detected_pattern=f"parameter_count_{param_count}",
                location="structure_validation",
                mitigation="Reduce number of parameters or restructure data",
                blocked=True
            ))
        
        # Check nesting depth
        depth = self._calculate_depth(parameters)
        if depth > self.MAX_PARAMETER_DEPTH:
            violations.append(SecurityViolation(
                violation_type=SecurityViolationType.RESOURCE_EXHAUSTION,
                threat_level=SecurityThreatLevel.HIGH,
                description=f"Excessive nesting depth: {depth} > {self.MAX_PARAMETER_DEPTH}",
                detected_pattern=f"nesting_depth_{depth}",
                location="structure_validation",
                mitigation="Flatten data structure to reduce nesting",
                blocked=True
            ))
        
        # Check string lengths
        self._check_string_lengths(parameters, violations, "")
        
        return violations
    
    def _check_string_lengths(self, obj: Any, violations: List[SecurityViolation], path: str):
        """Recursively check string lengths in parameters"""
        if isinstance(obj, str):
            if len(obj) > self.MAX_STRING_LENGTH:
                violations.append(SecurityViolation(
                    violation_type=SecurityViolationType.RESOURCE_EXHAUSTION,
                    threat_level=SecurityThreatLevel.MEDIUM,
                    description=f"String too long at {path}: {len(obj)} > {self.MAX_STRING_LENGTH}",
                    detected_pattern=f"long_string_{len(obj)}",
                    location=path or "root",
                    mitigation="Shorten string or use external reference",
                    blocked=True
                ))
        elif isinstance(obj, dict):
            for key, value in obj.items():
                self._check_string_lengths(value, violations, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._check_string_lengths(item, violations, f"{path}[{i}]" if path else f"[{i}]")
    
    def _scan_security_patterns(self, content: str, test_type: str) -> List[SecurityViolation]:
        """Scan content against security pattern database"""
        violations = []
        
        for threat_level, categories in self.pattern_db.compiled_patterns.items():
            for violation_type, patterns in categories.items():
                for pattern in patterns:
                    matches = pattern.finditer(content)
                    for match in matches:
                        detected_text = match.group(0)
                        violations.append(SecurityViolation(
                            violation_type=violation_type,
                            threat_level=threat_level,
                            description=f"Security pattern detected: {violation_type.value}",
                            detected_pattern=detected_text[:50] + ("..." if len(detected_text) > 50 else ""),
                            location=f"{test_type}_parameters",
                            mitigation=self._get_mitigation_advice(violation_type),
                            blocked=threat_level in [SecurityThreatLevel.CRITICAL, SecurityThreatLevel.HIGH]
                        ))
        
        return violations
    
    def _validate_test_type_security(self, test_type: str, parameters: Dict[str, Any]) -> List[SecurityViolation]:
        """Test-type specific security validation"""
        violations = []
        
        if test_type == "format_validation":
            violations.extend(self._validate_regex_security(parameters))
        elif test_type == "dependency_check":
            violations.extend(self._validate_dependency_security(parameters))
        elif test_type == "resource_validation":
            violations.extend(self._validate_resource_security(parameters))
        elif test_type == "interface_validation":
            violations.extend(self._validate_interface_security(parameters))
        elif test_type == "security_validation":
            violations.extend(self._validate_security_check_security(parameters))
        
        return violations
    
    def _validate_regex_security(self, parameters: Dict[str, Any]) -> List[SecurityViolation]:
        """Validate regex patterns for ReDoS and other attacks"""
        violations = []
        
        pattern = parameters.get('format_pattern', '')
        if isinstance(pattern, str) and pattern:
            # Check pattern length
            if len(pattern) > self.MAX_REGEX_LENGTH:
                violations.append(SecurityViolation(
                    violation_type=SecurityViolationType.RESOURCE_EXHAUSTION,
                    threat_level=SecurityThreatLevel.MEDIUM,
                    description=f"Regex pattern too long: {len(pattern)} > {self.MAX_REGEX_LENGTH}",
                    detected_pattern=pattern[:50] + "...",
                    location="format_pattern",
                    mitigation="Simplify regex pattern or use multiple simpler patterns",
                    blocked=True
                ))
            
            # Check for excessive groups
            group_count = pattern.count('(')
            if group_count > self.MAX_REGEX_GROUPS:
                violations.append(SecurityViolation(
                    violation_type=SecurityViolationType.RESOURCE_EXHAUSTION,
                    threat_level=SecurityThreatLevel.MEDIUM,
                    description=f"Too many regex groups: {group_count} > {self.MAX_REGEX_GROUPS}",
                    detected_pattern=f"groups_{group_count}",
                    location="format_pattern",
                    mitigation="Reduce number of capturing groups in regex",
                    blocked=True
                ))
            
            # Test regex compilation and basic safety
            try:
                compiled_pattern = re.compile(pattern)
                
                # Test for catastrophic backtracking patterns
                test_strings = ["a" * 100, "a" * 1000]
                for test_str in test_strings:
                    try:
                        # Set a timeout-like limit by checking pattern complexity
                        if self._is_potentially_dangerous_regex(pattern):
                            violations.append(SecurityViolation(
                                violation_type=SecurityViolationType.REGEX_DOS,
                                threat_level=SecurityThreatLevel.HIGH,
                                description="Regex pattern may cause catastrophic backtracking",
                                detected_pattern=pattern[:50] + "...",
                                location="format_pattern",
                                mitigation="Rewrite regex to avoid nested quantifiers and backtracking",
                                blocked=True
                            ))
                            break
                    except Exception:
                        # Regex caused an error during execution
                        violations.append(SecurityViolation(
                            violation_type=SecurityViolationType.REGEX_DOS,
                            threat_level=SecurityThreatLevel.HIGH,
                            description="Regex pattern causes execution errors",
                            detected_pattern=pattern[:50] + "...",
                            location="format_pattern",
                            mitigation="Fix regex syntax or simplify pattern",
                            blocked=True
                        ))
                        break
                        
            except re.error as e:
                violations.append(SecurityViolation(
                    violation_type=SecurityViolationType.MALFORMED_INPUT,
                    threat_level=SecurityThreatLevel.MEDIUM,
                    description=f"Invalid regex pattern: {e}",
                    detected_pattern=pattern[:50] + "...",
                    location="format_pattern",
                    mitigation="Fix regex syntax errors",
                    blocked=True
                ))
        
        return violations
    
    def _is_potentially_dangerous_regex(self, pattern: str) -> bool:
        """Check if regex pattern has potentially dangerous constructs"""
        dangerous_patterns = [
            r'\([^)]*\*[^)]*\)\*',  # (.*)*
            r'\([^)]*\+[^)]*\)\+',  # (.+)+
            r'\([^)]*\*[^)]*\)\+',  # (.*)+
            r'\([^)]*\+[^)]*\)\*',  # (.+)*
            r'\(\?\=[^)]*\*',       # (?=...)*
            r'\(\?\![^)]*\*',       # (?!...)*
        ]
        
        for dangerous in dangerous_patterns:
            if re.search(dangerous, pattern):
                return True
        
        return False
    
    def _validate_dependency_security(self, parameters: Dict[str, Any]) -> List[SecurityViolation]:
        """Validate dependency specifications for security"""
        violations = []
        
        dependencies = parameters.get('dependencies', [])
        if isinstance(dependencies, list):
            for i, dep in enumerate(dependencies):
                if isinstance(dep, str):
                    # Check for path traversal
                    if '..' in dep or '/' in dep or '\\' in dep:
                        violations.append(SecurityViolation(
                            violation_type=SecurityViolationType.PATH_TRAVERSAL,
                            threat_level=SecurityThreatLevel.HIGH,
                            description=f"Dependency contains path traversal: {dep}",
                            detected_pattern=dep,
                            location=f"dependencies[{i}]",
                            mitigation="Use simple dependency names without paths",
                            blocked=True
                        ))
                    
                    # Check for suspicious dependency names
                    if not self.SAFE_IDENTIFIER_PATTERN.match(dep):
                        violations.append(SecurityViolation(
                            violation_type=SecurityViolationType.MALFORMED_INPUT,
                            threat_level=SecurityThreatLevel.MEDIUM,
                            description=f"Dependency name format suspicious: {dep}",
                            detected_pattern=dep,
                            location=f"dependencies[{i}]",
                            mitigation="Use valid identifier format for dependency names",
                            blocked=False
                        ))
        
        return violations
    
    def _validate_resource_security(self, parameters: Dict[str, Any]) -> List[SecurityViolation]:
        """Validate resource specifications for security"""
        violations = []
        
        limits = parameters.get('resource_limits', {})
        if isinstance(limits, dict):
            # Check for unreasonable resource requests (potential DoS)
            resource_limits = {
                'memory_mb': 100000,     # 100GB
                'cpu_cores': 100,
                'disk_gb': 10000,        # 10TB
                'network_bandwidth_mbps': 100000  # 100Gbps
            }
            
            for resource, value in limits.items():
                if isinstance(value, (int, float)):
                    max_limit = resource_limits.get(resource, float('inf'))
                    if value > max_limit:
                        violations.append(SecurityViolation(
                            violation_type=SecurityViolationType.RESOURCE_EXHAUSTION,
                            threat_level=SecurityThreatLevel.MEDIUM,
                            description=f"Excessive resource request: {resource}={value} > {max_limit}",
                            detected_pattern=f"{resource}_{value}",
                            location=f"resource_limits.{resource}",
                            mitigation="Use reasonable resource limits",
                            blocked=False
                        ))
        
        return violations
    
    def _validate_interface_security(self, parameters: Dict[str, Any]) -> List[SecurityViolation]:
        """Validate interface specifications for security"""
        violations = []
        
        interface = parameters.get('interface_requirements', {})
        if isinstance(interface, dict):
            # Check protocols
            protocols = interface.get('protocols', [])
            if isinstance(protocols, list):
                insecure_protocols = {'ftp', 'telnet', 'rsh', 'rlogin', 'http'}
                for protocol in protocols:
                    if isinstance(protocol, str) and protocol.lower() in insecure_protocols:
                        violations.append(SecurityViolation(
                            violation_type=SecurityViolationType.UNSAFE_PROTOCOL,
                            threat_level=SecurityThreatLevel.HIGH,
                            description=f"Insecure protocol specified: {protocol}",
                            detected_pattern=protocol,
                            location="interface_requirements.protocols",
                            mitigation="Use secure protocols (https, tls, ssh, etc.)",
                            blocked=True
                        ))
        
        return violations
    
    def _validate_security_check_security(self, parameters: Dict[str, Any]) -> List[SecurityViolation]:
        """Validate security check specifications"""
        violations = []
        
        security_checks = parameters.get('security_checks', [])
        if isinstance(security_checks, list):
            # Ensure security checks are from allowed list
            allowed_checks = {
                'input_sanitization', 'output_encoding', 'authentication_check',
                'authorization_check', 'rate_limiting', 'ssl_verification',
                'csrf_protection', 'xss_prevention', 'sql_injection_prevention',
                'session_management'
            }
            
            for check in security_checks:
                if isinstance(check, str) and check not in allowed_checks:
                    violations.append(SecurityViolation(
                        violation_type=SecurityViolationType.MALFORMED_INPUT,
                        threat_level=SecurityThreatLevel.MEDIUM,
                        description=f"Unknown security check: {check}",
                        detected_pattern=check,
                        location="security_checks",
                        mitigation=f"Use allowed security checks: {allowed_checks}",
                        blocked=False
                    ))
        
        return violations
    
    def _validate_ast_security(self, parameters: Dict[str, Any]) -> List[SecurityViolation]:
        """Validate parameters using AST parsing for code detection"""
        violations = []
        
        # Convert parameters to strings and check if any look like Python code
        strings_to_check = []
        self._extract_strings(parameters, strings_to_check)
        
        for string_val in strings_to_check:
            if len(string_val) > 20 and self._looks_like_code(string_val):
                try:
                    # Try to parse as Python AST
                    parsed = ast.parse(string_val, mode='eval')
                    
                    # If it parses successfully, it's likely code
                    violations.append(SecurityViolation(
                        violation_type=SecurityViolationType.CODE_INJECTION,
                        threat_level=SecurityThreatLevel.CRITICAL,
                        description="Parameter contains executable code",
                        detected_pattern=string_val[:50] + "..." if len(string_val) > 50 else string_val,
                        location="ast_validation",
                        mitigation="Remove executable code from parameters",
                        blocked=True
                    ))
                except (SyntaxError, ValueError):
                    # Not valid Python code, which is good
                    pass
                except Exception:
                    # Other parsing errors, treat as suspicious
                    violations.append(SecurityViolation(
                        violation_type=SecurityViolationType.MALFORMED_INPUT,
                        threat_level=SecurityThreatLevel.MEDIUM,
                        description="Parameter contains suspicious code-like content",
                        detected_pattern=string_val[:50] + "..." if len(string_val) > 50 else string_val,
                        location="ast_validation",
                        mitigation="Review parameter content for code-like patterns",
                        blocked=False
                    ))
        
        return violations
    
    def _extract_strings(self, obj: Any, strings: List[str]):
        """Recursively extract all strings from parameters"""
        if isinstance(obj, str):
            strings.append(obj)
        elif isinstance(obj, dict):
            for value in obj.values():
                self._extract_strings(value, strings)
        elif isinstance(obj, list):
            for item in obj:
                self._extract_strings(item, strings)
    
    def _looks_like_code(self, text: str) -> bool:
        """Heuristic check if text looks like code"""
        code_indicators = [
            r'\bdef\s+\w+\s*\(',
            r'\bclass\s+\w+\s*:',
            r'\bif\s+.*:',
            r'\bfor\s+\w+\s+in\s+',
            r'\bwhile\s+.*:',
            r'\btry\s*:',
            r'\bexcept\s+.*:',
            r'\bimport\s+\w+',
            r'\bfrom\s+\w+\s+import',
            r'[a-zA-Z_]\w*\s*\([^)]*\)',  # Function calls
            r'[a-zA-Z_]\w*\.[a-zA-Z_]\w*',  # Attribute access
        ]
        
        for pattern in code_indicators:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _validate_protocols_and_urls(self, parameters: Dict[str, Any]) -> List[SecurityViolation]:
        """Validate URLs and protocols in parameters"""
        violations = []
        
        urls_to_check = []
        self._extract_urls(parameters, urls_to_check)
        
        for url in urls_to_check:
            if not self.SAFE_URL_PATTERN.match(url):
                violations.append(SecurityViolation(
                    violation_type=SecurityViolationType.MALFORMED_INPUT,
                    threat_level=SecurityThreatLevel.MEDIUM,
                    description=f"Suspicious URL format: {url}",
                    detected_pattern=url,
                    location="url_validation",
                    mitigation="Use properly formatted HTTPS URLs",
                    blocked=False
                ))
            
            # Check for insecure protocols
            if url.startswith(('ftp://', 'telnet://', 'http://')):
                violations.append(SecurityViolation(
                    violation_type=SecurityViolationType.UNSAFE_PROTOCOL,
                    threat_level=SecurityThreatLevel.HIGH,
                    description=f"Insecure protocol in URL: {url}",
                    detected_pattern=url,
                    location="url_validation",
                    mitigation="Use HTTPS instead of HTTP, or secure alternatives",
                    blocked=True
                ))
        
        return violations
    
    def _extract_urls(self, obj: Any, urls: List[str]):
        """Extract potential URLs from parameters"""
        if isinstance(obj, str):
            # Simple URL detection
            url_pattern = r'https?://[^\s]+'
            matches = re.findall(url_pattern, obj)
            urls.extend(matches)
        elif isinstance(obj, dict):
            for value in obj.values():
                self._extract_urls(value, urls)
        elif isinstance(obj, list):
            for item in obj:
                self._extract_urls(item, urls)
    
    def _calculate_overall_threat_level(self, violations: List[SecurityViolation]) -> SecurityThreatLevel:
        """Calculate overall threat level from individual violations"""
        if not violations:
            return SecurityThreatLevel.SAFE
        
        # Get maximum threat level by mapping to numeric values
        threat_values = {
            SecurityThreatLevel.SAFE: 0,
            SecurityThreatLevel.LOW: 1,
            SecurityThreatLevel.MEDIUM: 2,
            SecurityThreatLevel.HIGH: 3,
            SecurityThreatLevel.CRITICAL: 4
        }
        
        max_value = max(threat_values[violation.threat_level] for violation in violations)
        
        # Map back to enum
        for level, value in threat_values.items():
            if value == max_value:
                return level
        
        return SecurityThreatLevel.SAFE
    
    def _get_mitigation_advice(self, violation_type: SecurityViolationType) -> str:
        """Get mitigation advice for specific violation types"""
        advice = {
            SecurityViolationType.CODE_INJECTION: "Remove executable code and use declarative configuration only",
            SecurityViolationType.PATH_TRAVERSAL: "Use relative paths within allowed directories only",
            SecurityViolationType.REGEX_DOS: "Simplify regex patterns and avoid nested quantifiers",
            SecurityViolationType.RESOURCE_EXHAUSTION: "Use reasonable resource limits and avoid excessive nesting",
            SecurityViolationType.INFORMATION_DISCLOSURE: "Remove sensitive information and use secure credential management",
            SecurityViolationType.PRIVILEGE_ESCALATION: "Use least-privilege principles and avoid admin operations",
            SecurityViolationType.UNSAFE_PROTOCOL: "Use secure protocols (HTTPS, TLS, SSH) instead",
            SecurityViolationType.MALFORMED_INPUT: "Validate and sanitize all input parameters"
        }
        
        return advice.get(violation_type, "Review and fix security issue")


# Example usage and testing
if __name__ == "__main__":
    # Test the security validation system
    validator = PropertyTestSecurityValidator()
    
    # Test with safe parameters
    safe_params = {
        "expected_range": {
            "min": 100,
            "max": 2000
        }
    }
    
    result = validator.validate_property_test_security("range_check", safe_params)
    print(f"Safe parameters result: {'SECURE' if result.is_secure else 'INSECURE'}")
    print(f"Threat level: {result.overall_threat_level.value}")
    
    # Test with dangerous parameters
    dangerous_params = {
        "format_pattern": "__import__('os').system('rm -rf /')",
        "dependencies": ["../../../etc/passwd"],
        "resource_limits": {
            "memory_mb": 999999999
        }
    }
    
    result = validator.validate_property_test_security("format_validation", dangerous_params)
    print(f"\nDangerous parameters result: {'SECURE' if result.is_secure else 'INSECURE'}")
    print(f"Threat level: {result.overall_threat_level.value}")
    print(f"Violations found: {len(result.violations)}")
    
    for violation in result.violations:
        print(f"  {violation.threat_level.value.upper()}: {violation.description}")
        print(f"    Mitigation: {violation.mitigation}")
    
    # Test regex patterns
    regex_params = {
        "format_pattern": "(a+)+b"  # Potentially dangerous regex
    }
    
    result = validator.validate_property_test_security("format_validation", regex_params)
    print(f"\nRegex test result: {'SECURE' if result.is_secure else 'INSECURE'}")
    print(f"Violations: {len(result.violations)}")
    
    for violation in result.violations:
        print(f"  {violation.description}")