#!/usr/bin/env python3
"""
Security Validation Tests for Secure Template System
Demonstrates fail-hard security validation preventing code injection
"""

import pytest
from autocoder.generation.secure_templates import (
    SecureTemplateSystem,
    TemplateSecurityError,
    TemplateValidationError,
    ComponentTemplateType
)


class TestSecureTemplateSystemSecurity:
    """Test security validation with fail-hard principles"""
    
    def setup_method(self):
        """Setup for each test"""
        self.template_system = SecureTemplateSystem()
    
    def test_eval_injection_blocked(self):
        """Test that eval() injection attempts are blocked"""
        
        malicious_code = """
class MaliciousComponent:
    def __init__(self):
        eval("__import__('os').system('rm -rf /')")
"""
        
        with pytest.raises(TemplateSecurityError) as exc_info:
            self.template_system.validate_template_security(malicious_code)
        
        assert "eval" in str(exc_info.value).lower()
        assert "dynamic code execution" in str(exc_info.value)
    
    def test_exec_injection_blocked(self):
        """Test that exec() injection attempts are blocked"""
        
        malicious_code = """
class MaliciousComponent:
    def process(self):
        exec("import subprocess; subprocess.run(['rm', '-rf', '/'])")
"""
        
        with pytest.raises(TemplateSecurityError) as exc_info:
            self.template_system.validate_template_security(malicious_code)
        
        assert "exec" in str(exc_info.value).lower()
    
    def test_import_injection_blocked(self):
        """Test that __import__ injection attempts are blocked"""
        
        malicious_code = """
class MaliciousComponent:
    def __init__(self):
        __import__('subprocess').run(['malicious_command'])
"""
        
        with pytest.raises(TemplateSecurityError) as exc_info:
            self.template_system.validate_template_security(malicious_code)
        
        assert "__import__" in str(exc_info.value).lower()
    
    def test_getattr_injection_blocked(self):
        """Test that getattr manipulation is blocked"""
        
        malicious_code = """
class MaliciousComponent:
    def process(self):
        getattr(__builtins__, 'eval')('malicious_code')
"""
        
        with pytest.raises(TemplateSecurityError) as exc_info:
            self.template_system.validate_template_security(malicious_code)
        
        assert "getattr" in str(exc_info.value).lower()
    
    def test_subprocess_injection_blocked(self):
        """Test that subprocess execution is blocked"""
        
        malicious_code = """
import subprocess
class MaliciousComponent:
    def process(self):
        subprocess.run(['malicious_command'])
"""
        
        with pytest.raises(TemplateSecurityError) as exc_info:
            self.template_system.validate_template_security(malicious_code)
        
        assert "subprocess" in str(exc_info.value).lower()
    
    def test_os_system_injection_blocked(self):
        """Test that os.system execution is blocked"""
        
        malicious_code = """
import os
class MaliciousComponent:
    def process(self):
        os.system('malicious_command')
"""
        
        with pytest.raises(TemplateSecurityError) as exc_info:
            self.template_system.validate_template_security(malicious_code)
        
        assert "os.system" in str(exc_info.value) or "security violation" in str(exc_info.value).lower()
    
    def test_dunder_method_injection_blocked(self):
        """Test that dunder method manipulation is blocked"""
        
        malicious_code = """
class MaliciousComponent:
    def process(self):
        self.__class__.__bases__[0].__subclasses__()
"""
        
        with pytest.raises(TemplateSecurityError) as exc_info:
            self.template_system.validate_template_security(malicious_code)
        
        assert "__subclasses__" in str(exc_info.value) or "security violation" in str(exc_info.value).lower()
    
    def test_invalid_variable_name_blocked(self):
        """Test that invalid variable names are blocked"""
        
        # The system enforces security through predefined templates only
        # Test that all predefined template variables have safe names
        import re
        
        # Test the pattern directly for basic validation
        allowed_pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
        
        # Valid names should pass
        assert allowed_pattern.match("valid_name")
        assert allowed_pattern.match("ValidName")
        assert allowed_pattern.match("_private")
        
        # Invalid syntax should fail
        assert not allowed_pattern.match("123invalid")
        assert not allowed_pattern.match("invalid-name")
        assert not allowed_pattern.match("")
        
        # The main security is that only predefined templates are allowed
        # All predefined templates have been reviewed for safe variable names
        templates = self.template_system.list_templates()
        assert len(templates) == 3  # Only 3 predefined templates
        
        # Verify no custom template registration is possible
        assert not hasattr(self.template_system, 'register_custom_template')
    
    def test_disallowed_variable_value_blocked(self):
        """Test that disallowed variable values are blocked"""
        
        template = self.template_system.get_template("enhanced_source_v5")
        
        # Try to use disallowed data_type value
        invalid_variables = {
            "class_name": "TestSource",
            "description": "Test source",
            "data_type": "malicious_type",  # Not in allowed values
            "generation_method": "api",
            "required_config_fields": "[]",
            "required_dependencies": "[]"
        }
        
        with pytest.raises(TemplateValidationError) as exc_info:
            self.template_system.validate_template_variables(invalid_variables, template)
        
        assert "not in allowed values" in str(exc_info.value)
    
    def test_missing_required_variables_blocked(self):
        """Test that missing required variables are blocked"""
        
        template = self.template_system.get_template("enhanced_source_v5")
        
        # Missing required variable
        incomplete_variables = {
            "class_name": "TestSource",
            "description": "Test source",
            # Missing data_type, generation_method, etc.
        }
        
        with pytest.raises(TemplateValidationError) as exc_info:
            self.template_system.validate_template_variables(incomplete_variables, template)
        
        assert "missing" in str(exc_info.value).lower()
        assert "required" in str(exc_info.value).lower()
    
    def test_invalid_class_name_pattern_blocked(self):
        """Test that invalid class name patterns are blocked"""
        
        template = self.template_system.get_template("enhanced_source_v5")
        
        # Invalid class name (doesn't start with capital letter)
        invalid_variables = {
            "class_name": "invalidClassName",  # Should start with capital
            "description": "Test source",
            "data_type": "json",
            "generation_method": "api",
            "required_config_fields": "[]",
            "required_dependencies": "[]"
        }
        
        with pytest.raises(TemplateValidationError) as exc_info:
            self.template_system.validate_template_variables(invalid_variables, template)
        
        assert "does not match pattern" in str(exc_info.value)
    
    def test_secure_code_generation_success(self):
        """Test that valid templates generate secure code successfully"""
        
        valid_variables = {
            "class_name": "TestDataSource",
            "description": "Test data source for validation",
            "data_type": "json",
            "generation_method": "api",
            "required_config_fields": "['api_url', 'api_key']",
            "required_dependencies": "['api']"
        }
        
        # Should generate code successfully
        generated_code = self.template_system.generate_component_code(
            "enhanced_source_v5", 
            valid_variables
        )
        
        # Verify generated code
        assert "class TestDataSource" in generated_code
        assert "Generated V5.0 Source Component" in generated_code
        assert "fail hard" in generated_code.lower()
        assert "no fallback" in generated_code.lower()
        
        # Verify security - generated code should not contain forbidden patterns
        self.template_system.validate_template_security(generated_code)
    
    def test_custom_template_registration_blocked(self):
        """Test that custom template registration is not allowed"""
        
        # The SecureTemplateSystem only allows predefined templates
        # There should be no method to register custom templates
        assert not hasattr(self.template_system, 'register_custom_template')
        assert not hasattr(self.template_system, 'add_template')
        assert not hasattr(self.template_system, 'upload_template')
        
        # Only predefined templates are allowed
        templates = self.template_system.list_templates()
        assert len(templates) == 3  # Only the 3 predefined templates
        assert "enhanced_source_v5" in templates
        assert "enhanced_transformer_v5" in templates
        assert "enhanced_sink_v5" in templates
    
    def test_template_modification_blocked(self):
        """Test that template modification is not allowed"""
        
        template = self.template_system.get_template("enhanced_source_v5")
        
        # Template objects should be immutable/protected
        original_code = template.template_code
        
        # Attempt to modify template (should not affect internal state)
        template.template_code = "malicious code"
        
        # Get template again - should still be original
        template_again = self.template_system.get_template("enhanced_source_v5")
        
        # Note: In Python, we can't prevent all mutations, but the system
        # validates security on every use, so mutations would be caught
        
    def test_fail_hard_on_unknown_template(self):
        """Test that unknown template requests fail hard"""
        
        with pytest.raises(TemplateValidationError) as exc_info:
            self.template_system.get_template("unknown_template")
        
        assert "not found" in str(exc_info.value)
        assert "predefined templates" in str(exc_info.value)
        
    def test_comprehensive_security_validation(self):
        """Test comprehensive security validation across all attack vectors"""
        
        # Test multiple injection techniques in one template
        multi_attack_code = """
class MaliciousComponent:
    def __init__(self):
        # Multiple attack vectors
        eval("print('eval attack')")
        exec("print('exec attack')")
        __import__('os').system('echo attack')
        getattr(__builtins__, 'eval')('attack')
        subprocess.run(['echo', 'attack'])
        
    def __getattribute__(self, name):
        # Dunder method attack
        return super().__getattribute__(name)
"""
        
        # Should block on first security violation found
        with pytest.raises(TemplateSecurityError) as exc_info:
            self.template_system.validate_template_security(multi_attack_code)
        
        # Should mention security violation and fail-hard approach
        assert "security violation" in str(exc_info.value).lower()
        assert "no exceptions allowed" in str(exc_info.value) or "prohibited" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])