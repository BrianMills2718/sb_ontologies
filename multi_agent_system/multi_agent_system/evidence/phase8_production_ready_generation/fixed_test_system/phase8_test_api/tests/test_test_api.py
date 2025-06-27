#!/usr/bin/env python3
"""
Generated test for test_api component
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import respx
import httpx
from typing import Dict, Any

# Import the component we're testing
try:
    from components.test_api import GeneratedAPIEndpoint_test_api
except ImportError:
    # Use relative import fallback for test environments
    try:
        import importlib.util
        from pathlib import Path
        
        # Load component module directly without sys.path manipulation
        component_path = Path(__file__).parent.parent / "components" / f"test_api.py"
        if component_path.exists():
            spec = importlib.util.spec_from_file_location(f"components.test_api", component_path)
            if spec and spec.loader:
                component_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(component_module)
                GeneratedAPIEndpoint_test_api = getattr(component_module, "GeneratedAPIEndpoint_test_api")
            else:
                raise ImportError(f"Could not load component spec for test_api")
        else:
            raise ImportError(f"Component file not found: {component_path}")
    except Exception as e:
        raise ImportError(f"Failed to import component test_api: {e}")


class TestGeneratedAPIEndpoint_test_api:
    """Test class for test_api component with mocked dependencies"""
    
    @pytest.fixture
    def component_config(self):
        """Component configuration for testing"""
        return {
            "port": 8080,
            "host": "0.0.0.0",
            "auth_required": false,
            "rate_limiting": false
}
    
    @pytest.fixture
    def component(self, component_config):
        """Create component instance for testing"""
        return GeneratedAPIEndpoint_test_api("test_api", component_config)
    
    @pytest.mark.asyncio
    async def test_test_api_with_mocked_dependencies(self, component):
        """Test test_api component with mocked external dependencies"""
        
        # Sample input from test specification
        sample_input =         {   'input': {   'description': 'Normal case ‑ fetch an existing user profile '
                                        'with usage statistics.',
                         'expectedResponse': {   'schemaVersion': '2023-10-01',
                                                 'statusCode': 200},
                         'request': {   'headers': {   'Accept': 'application/json',
                                                       'Authorization': 'Bearer '
                                                                        'prod-token-2f89a7ac0c',
                                                       'X-Request-Id': '9b1d4e7f-6c71-4478-b615-98d5cbda3a52'},
                                        'method': 'GET',
                                        'query': {   'include': 'stats,preferences',
                                                     'tz': 'UTC'},
                                        'url': '/v1/users/987654321'}}}
        
        # Expected output from test specification  
        expected_output =             {   'input': {   'description': 'Normal case ‑ fetch an existing user profile '
                                            'with usage statistics.',
                             'expectedResponse': {   'schemaVersion': '2023-10-01',
                                                     'statusCode': 200},
                             'request': {   'headers': {   'Accept': 'application/json',
                                                           'Authorization': 'Bearer '
                                                                            'prod-token-2f89a7ac0c',
                                                           'X-Request-Id': '9b1d4e7f-6c71-4478-b615-98d5cbda3a52'},
                                            'method': 'GET',
                                            'query': {   'include': 'stats,preferences',
                                                         'tz': 'UTC'},
                                            'url': '/v1/users/987654321'}},
                'processed': True}
        
        
        # Setup component
        await component.setup({})
        
        try:
            # Execute component logic
            result = await component._generate_data(sample_input)
            
            # Validate output matches expected
            assert result is not None, "Component returned None"
            
            # Check that result contains expected fields
            for key, expected_value in expected_output.items():
                assert key in result, f"Missing expected key '{key}' in result: {result}"
                assert result[key] == expected_value, f"Expected {key}={expected_value}, got {result[key]}"
                
        finally:
            # Cleanup component
            await component.cleanup()
