#!/usr/bin/env python3
"""
Pytest configuration for generated component tests
"""
# Configure Python path for component imports
import importlib.util
from pathlib import Path

# Use direct module loading instead of sys.path manipulation
def load_components_module():
    """Load components module directly without sys.path manipulation"""
    components_path = Path(__file__).parent.parent / "components" / "__init__.py"
    if components_path.exists():
        spec = importlib.util.spec_from_file_location("components", components_path)
        if spec and spec.loader:
            components_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(components_module)
            return components_module
    return None

# Try clean import first, fallback to direct module loading
try:
    import components
except ImportError:
    components = load_components_module()
    if not components:
        # If still failing, the test environment needs to be configured properly
        raise ImportError("Components module not available. Ensure the test is run from the correct directory.")
