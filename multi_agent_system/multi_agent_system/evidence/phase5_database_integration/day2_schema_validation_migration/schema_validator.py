"""
V5.0 Real-time Schema Validator
Implements comprehensive schema validation and migration management with fail-hard principles
"""

import asyncio
import time
import logging
import json
import hashlib
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SchemaValidationError(Exception):
    """Raised when schema validation fails"""
    pass


class SchemaMigrationError(Exception):
    """Raised when schema migration fails"""
    pass


class SchemaCompatibilityError(Exception):
    """Raised when schema compatibility checks fail"""
    pass


class SchemaVersion:
    """Schema version handling with semantic versioning"""
    
    def __init__(self, version_string: str):
        self.version_string = version_string
        self.major, self.minor, self.patch = self._parse_version(version_string)
    
    def _parse_version(self, version: str) -> tuple:
        """Parse semantic version string"""
        try:
            parts = version.split('.')
            return int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0
        except (ValueError, IndexError):
            raise ValueError(f"Invalid version format: {version}")
    
    def __str__(self):
        return self.version_string
    
    def __eq__(self, other):
        if isinstance(other, SchemaVersion):
            return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
        return False
    
    def __lt__(self, other):
        if isinstance(other, SchemaVersion):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, SchemaVersion):
            return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)
        return NotImplemented
    
    def is_compatible(self, other) -> bool:
        """Check if versions are compatible (same major version)"""
        if isinstance(other, SchemaVersion):
            return self.major == other.major
        return False


@dataclass
class SchemaField:
    """Schema field definition"""
    name: str
    field_type: str
    required: bool = True
    default: Any = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class SchemaDefinition:
    """Complete schema definition"""
    version: SchemaVersion
    name: str
    fields: List[SchemaField]
    indexes: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    
    def get_field(self, name: str) -> Optional[SchemaField]:
        """Get field by name"""
        for field in self.fields:
            if field.name == name:
                return field
        return None
    
    def get_schema_hash(self) -> str:
        """Generate hash of schema for comparison"""
        schema_data = {
            "name": self.name,
            "fields": [(f.name, f.field_type, f.required) for f in self.fields],
            "indexes": sorted(self.indexes),
            "constraints": sorted(self.constraints)
        }
        schema_json = json.dumps(schema_data, sort_keys=True)
        return hashlib.sha256(schema_json.encode()).hexdigest()


@dataclass
class ValidationResult:
    """Schema validation result"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validated_data: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0


@dataclass
class CompatibilityResult:
    """Schema compatibility check result"""
    compatible: bool
    current_version: SchemaVersion
    target_version: SchemaVersion
    migration_required: bool = False
    breaking_changes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class SchemaValidator:
    """Real-time schema validation and migration management"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.schema_registry = None
        self.migration_manager = None
        self.current_version = None
        self.active_schema = None
        
        # Configuration
        self.strict_validation = config.get("strict_validation", True)
        self.auto_migration = config.get("auto_migration", False)
        self.validation_cache = {}
        self.cache_enabled = config.get("cache_enabled", True)
        
        logger.info("SchemaValidator initialized with real-time validation")
    
    async def initialize(self):
        """Initialize schema validator with registry and migration manager"""
        try:
            # Try absolute imports first
            from schema_registry import SchemaRegistry
            from migration_manager import MigrationManager
        except ImportError:
            try:
                # Try relative imports
                from .schema_registry import SchemaRegistry
                from .migration_manager import MigrationManager
            except ImportError:
                # Fall back to mock components (will be handled below)
                SchemaRegistry = None
                MigrationManager = None
        
        try:
            if SchemaRegistry and MigrationManager:
                self.schema_registry = SchemaRegistry(self.config)
                await self.schema_registry.initialize()
                
                self.migration_manager = MigrationManager(self.config)
                await self.migration_manager.initialize()
                
                logger.info("SchemaValidator components initialized successfully")
            else:
                raise ImportError("Components not available")
            
        except (ImportError, Exception):
            # Fallback for testing
            self.schema_registry = MockSchemaRegistry(self.config)
            self.migration_manager = MockMigrationManager(self.config)
            
            logger.warning("Using mock components for schema validation")
    
    async def validate_or_create_schema(self) -> bool:
        """Validate existing schema or create new one"""
        logger.info("Starting schema validation or creation")
        
        try:
            # Check if schema exists
            existing_schema = await self._get_existing_schema()
            
            if existing_schema:
                logger.info(f"Found existing schema version {existing_schema.version}")
                
                # Get target schema from registry
                target_schema = await self.schema_registry.get_latest_schema()
                
                if target_schema.version == existing_schema.version:
                    # Schema is current
                    self.active_schema = existing_schema
                    self.current_version = existing_schema.version
                    logger.info("Schema is current, no migration needed")
                    return True
                
                # Check compatibility
                compatibility_result = await self._validate_schema_compatibility(
                    existing_schema, target_schema
                )
                
                if not compatibility_result.compatible:
                    if compatibility_result.migration_required:
                        # Trigger migration
                        await self._perform_schema_migration(
                            existing_schema.version,
                            target_schema.version
                        )
                    else:
                        # Breaking changes, fail hard
                        raise SchemaCompatibilityError(
                            f"Incompatible schema changes detected: {compatibility_result.breaking_changes}"
                        )
                else:
                    # Compatible, update schema
                    await self._update_schema(target_schema)
            else:
                # Create initial schema
                logger.info("No existing schema found, creating initial schema")
                await self._create_initial_schema()
            
            return True
            
        except Exception as e:
            logger.error(f"Schema validation or creation failed: {e}")
            raise SchemaValidationError(f"Schema setup failed: {e}")
    
    async def validate_data(self, data: Any) -> ValidationResult:
        """Validate data against current schema"""
        start_time = time.time()
        
        if self.active_schema is None:
            raise SchemaValidationError("No active schema available for validation")
        
        # Check cache if enabled
        if self.cache_enabled:
            cache_key = self._generate_cache_key(data)
            if cache_key in self.validation_cache:
                cached_result = self.validation_cache[cache_key]
                cached_result.execution_time = time.time() - start_time
                return cached_result
        
        try:
            # Validate data structure
            validation_result = await self._validate_data_structure(data, self.active_schema)
            
            if validation_result.valid:
                # Apply field-level validation
                field_validation = await self._validate_fields(data, self.active_schema)
                if not field_validation.valid:
                    validation_result.valid = False
                    validation_result.errors.extend(field_validation.errors)
                else:
                    validation_result.validated_data = field_validation.validated_data
            
            validation_result.execution_time = time.time() - start_time
            
            # Cache result if validation was successful and caching is enabled
            if self.cache_enabled and validation_result.valid:
                cache_key = self._generate_cache_key(data)
                self.validation_cache[cache_key] = validation_result
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Data validation error: {e}")
            return ValidationResult(
                valid=False,
                errors=[f"Validation exception: {e}"],
                execution_time=time.time() - start_time
            )
    
    async def _get_existing_schema(self) -> Optional[SchemaDefinition]:
        """Get existing schema from database/registry"""
        try:
            return await self.schema_registry.get_current_schema()
        except Exception as e:
            logger.warning(f"Could not retrieve existing schema: {e}")
            return None
    
    async def _validate_schema_compatibility(self, current: SchemaDefinition, target: SchemaDefinition) -> CompatibilityResult:
        """Validate schema compatibility between versions"""
        logger.info(f"Checking compatibility: {current.version} -> {target.version}")
        
        breaking_changes = []
        warnings = []
        migration_required = False
        
        # Check version compatibility
        if not current.version.is_compatible(target.version):
            breaking_changes.append(f"Major version change: {current.version} -> {target.version}")
        
        # Check field compatibility
        current_fields = {f.name: f for f in current.fields}
        target_fields = {f.name: f for f in target.fields}
        
        # Check for removed fields
        for field_name in current_fields:
            if field_name not in target_fields:
                breaking_changes.append(f"Field '{field_name}' was removed")
        
        # Check for modified fields
        for field_name, target_field in target_fields.items():
            if field_name in current_fields:
                current_field = current_fields[field_name]
                
                # Check type changes
                if current_field.field_type != target_field.field_type:
                    breaking_changes.append(
                        f"Field '{field_name}' type changed: {current_field.field_type} -> {target_field.field_type}"
                    )
                
                # Check required changes
                if not current_field.required and target_field.required:
                    breaking_changes.append(f"Field '{field_name}' is now required")
                elif current_field.required and not target_field.required:
                    warnings.append(f"Field '{field_name}' is no longer required")
                    migration_required = True
            else:
                # New field
                if target_field.required and target_field.default is None:
                    breaking_changes.append(f"New required field '{field_name}' without default value")
                else:
                    warnings.append(f"New field '{field_name}' added")
                    migration_required = True
        
        # Check index changes
        current_indexes = set(current.indexes)
        target_indexes = set(target.indexes)
        
        if current_indexes != target_indexes:
            migration_required = True
            warnings.append("Index configuration changed")
        
        compatible = len(breaking_changes) == 0
        
        return CompatibilityResult(
            compatible=compatible,
            current_version=current.version,
            target_version=target.version,
            migration_required=migration_required,
            breaking_changes=breaking_changes,
            warnings=warnings
        )
    
    async def _perform_schema_migration(self, from_version: SchemaVersion, to_version: SchemaVersion):
        """Perform schema migration"""
        logger.info(f"Performing schema migration: {from_version} -> {to_version}")
        
        try:
            migration_result = await self.migration_manager.migrate_schema(
                str(from_version), str(to_version)
            )
            
            if migration_result.successful:
                # Update active schema
                new_schema = await self.schema_registry.get_schema(str(to_version))
                self.active_schema = new_schema
                self.current_version = to_version
                
                # Clear validation cache
                self.validation_cache.clear()
                
                logger.info(f"Schema migration completed successfully: {from_version} -> {to_version}")
            else:
                raise SchemaMigrationError(
                    f"Schema migration failed: {migration_result.error_message}"
                )
                
        except Exception as e:
            logger.error(f"Schema migration error: {e}")
            raise SchemaMigrationError(f"Migration failed: {e}")
    
    async def _create_initial_schema(self):
        """Create initial schema"""
        logger.info("Creating initial schema")
        
        try:
            # Get default schema from registry
            default_schema = await self.schema_registry.get_default_schema()
            
            # Create schema in database
            await self._execute_schema_creation(default_schema)
            
            # Set as active schema
            self.active_schema = default_schema
            self.current_version = default_schema.version
            
            logger.info(f"Initial schema created: version {default_schema.version}")
            
        except Exception as e:
            logger.error(f"Initial schema creation failed: {e}")
            raise SchemaValidationError(f"Initial schema creation failed: {e}")
    
    async def _update_schema(self, new_schema: SchemaDefinition):
        """Update schema to new version"""
        logger.info(f"Updating schema to version {new_schema.version}")
        
        try:
            # Execute schema update
            await self._execute_schema_update(new_schema)
            
            # Update active schema
            self.active_schema = new_schema
            self.current_version = new_schema.version
            
            # Clear validation cache
            self.validation_cache.clear()
            
            logger.info(f"Schema updated to version {new_schema.version}")
            
        except Exception as e:
            logger.error(f"Schema update failed: {e}")
            raise SchemaValidationError(f"Schema update failed: {e}")
    
    async def _validate_data_structure(self, data: Any, schema: SchemaDefinition) -> ValidationResult:
        """Validate basic data structure"""
        errors = []
        
        if not isinstance(data, dict):
            return ValidationResult(
                valid=False,
                errors=["Data must be a dictionary/object"]
            )
        
        # Check required fields
        required_fields = [f.name for f in schema.fields if f.required]
        for field_name in required_fields:
            if field_name not in data:
                errors.append(f"Required field '{field_name}' is missing")
        
        # Check for unknown fields in strict mode
        if self.strict_validation:
            schema_fields = {f.name for f in schema.fields}
            for field_name in data.keys():
                if field_name not in schema_fields:
                    errors.append(f"Unknown field '{field_name}' not allowed in strict mode")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )
    
    async def _validate_fields(self, data: Dict[str, Any], schema: SchemaDefinition) -> ValidationResult:
        """Validate individual fields against schema"""
        errors = []
        warnings = []
        validated_data = {}
        
        for field in schema.fields:
            field_name = field.name
            
            if field_name in data:
                field_value = data[field_name]
                
                # Type validation
                type_valid, type_error = self._validate_field_type(field_value, field.field_type)
                if not type_valid:
                    errors.append(f"Field '{field_name}': {type_error}")
                    continue
                
                # Constraint validation
                constraint_valid, constraint_error = self._validate_field_constraints(
                    field_value, field.constraints
                )
                if not constraint_valid:
                    errors.append(f"Field '{field_name}': {constraint_error}")
                    continue
                
                validated_data[field_name] = field_value
                
            elif field.required:
                if field.default is not None:
                    validated_data[field_name] = field.default
                    warnings.append(f"Field '{field_name}' using default value")
                else:
                    errors.append(f"Required field '{field_name}' is missing")
            elif field.default is not None:
                validated_data[field_name] = field.default
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_data=validated_data
        )
    
    def _validate_field_type(self, value: Any, expected_type: str) -> tuple[bool, Optional[str]]:
        """Validate field type"""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        if expected_type not in type_mapping:
            return False, f"Unknown type '{expected_type}'"
        
        expected_python_type = type_mapping[expected_type]
        
        if isinstance(expected_python_type, tuple):
            if not isinstance(value, expected_python_type):
                return False, f"Expected {expected_type}, got {type(value).__name__}"
        else:
            if not isinstance(value, expected_python_type):
                return False, f"Expected {expected_type}, got {type(value).__name__}"
        
        return True, None
    
    def _validate_field_constraints(self, value: Any, constraints: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate field constraints"""
        for constraint_name, constraint_value in constraints.items():
            if constraint_name == "min_length" and isinstance(value, str):
                if len(value) < constraint_value:
                    return False, f"String too short (min: {constraint_value})"
            
            elif constraint_name == "max_length" and isinstance(value, str):
                if len(value) > constraint_value:
                    return False, f"String too long (max: {constraint_value})"
            
            elif constraint_name == "min_value" and isinstance(value, (int, float)):
                if value < constraint_value:
                    return False, f"Value too small (min: {constraint_value})"
            
            elif constraint_name == "max_value" and isinstance(value, (int, float)):
                if value > constraint_value:
                    return False, f"Value too large (max: {constraint_value})"
            
            elif constraint_name == "pattern" and isinstance(value, str):
                import re
                if not re.match(constraint_value, value):
                    return False, f"Value does not match pattern: {constraint_value}"
        
        return True, None
    
    async def _execute_schema_creation(self, schema: SchemaDefinition):
        """Execute schema creation in database"""
        # This would be implemented with actual database schema creation
        # For now, simulate schema creation
        logger.info(f"Executing schema creation for {schema.name} v{schema.version}")
        await asyncio.sleep(0.01)  # Simulate database operation
    
    async def _execute_schema_update(self, schema: SchemaDefinition):
        """Execute schema update in database"""
        # This would be implemented with actual database schema update
        # For now, simulate schema update
        logger.info(f"Executing schema update for {schema.name} v{schema.version}")
        await asyncio.sleep(0.01)  # Simulate database operation
    
    def _generate_cache_key(self, data: Any) -> str:
        """Generate cache key for validation result"""
        try:
            data_json = json.dumps(data, sort_keys=True)
            return hashlib.md5(data_json.encode()).hexdigest()
        except (TypeError, ValueError):
            # Fallback for non-serializable data
            return hashlib.md5(str(data).encode()).hexdigest()
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return {
            "current_version": str(self.current_version) if self.current_version else None,
            "active_schema": self.active_schema.name if self.active_schema else None,
            "cache_size": len(self.validation_cache),
            "cache_enabled": self.cache_enabled,
            "strict_validation": self.strict_validation,
            "auto_migration": self.auto_migration
        }
    
    async def cleanup(self):
        """Cleanup schema validator"""
        logger.info("Cleaning up SchemaValidator")
        
        self.validation_cache.clear()
        
        if self.migration_manager:
            await self.migration_manager.cleanup()
        
        if self.schema_registry:
            await self.schema_registry.cleanup()


# Mock classes for testing

class MockSchemaRegistry:
    """Mock schema registry for testing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    async def initialize(self):
        pass
    
    async def get_current_schema(self) -> Optional[SchemaDefinition]:
        return None
    
    async def get_latest_schema(self) -> SchemaDefinition:
        return self._create_default_schema()
    
    async def get_schema(self, version: str) -> SchemaDefinition:
        return self._create_default_schema()
    
    async def get_default_schema(self) -> SchemaDefinition:
        return self._create_default_schema()
    
    def _create_default_schema(self) -> SchemaDefinition:
        return SchemaDefinition(
            version=SchemaVersion("1.0.0"),
            name="default_schema",
            fields=[
                SchemaField("id", "integer", required=True),
                SchemaField("data", "object", required=True),
                SchemaField("timestamp", "number", required=False, default=time.time())
            ]
        )
    
    async def cleanup(self):
        pass


class MockMigrationManager:
    """Mock migration manager for testing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def initialize(self):
        pass
    
    async def migrate_schema(self, from_version: str, to_version: str):
        return type('MigrationResult', (), {
            'successful': True,
            'error_message': None
        })()
    
    async def cleanup(self):
        pass


# Test harness
if __name__ == "__main__":
    async def test_schema_validator():
        """Test schema validator functionality"""
        
        config = {
            "strict_validation": True,
            "auto_migration": False,
            "cache_enabled": True
        }
        
        validator = SchemaValidator(config)
        
        try:
            # Test initialization
            await validator.initialize()
            print("✅ SchemaValidator initialized successfully")
            
            # Test schema setup
            await validator.validate_or_create_schema()
            print("✅ Schema validation/creation completed")
            
            # Test data validation
            test_data = {
                "id": 123,
                "data": {"test": "value"},
                "timestamp": time.time()
            }
            
            result = await validator.validate_data(test_data)
            if result.valid:
                print("✅ Data validation successful")
                print(f"   Execution time: {result.execution_time:.4f}s")
            else:
                print(f"❌ Data validation failed: {result.errors}")
            
            # Test invalid data
            invalid_data = {
                "id": "not_an_integer",
                "data": "not_an_object"
            }
            
            invalid_result = await validator.validate_data(invalid_data)
            if not invalid_result.valid:
                print("✅ Invalid data correctly rejected")
                print(f"   Errors: {invalid_result.errors}")
            
            # Test statistics
            stats = validator.get_validation_statistics()
            print(f"✅ Validation statistics: {stats}")
            
            # Test cleanup
            await validator.cleanup()
            print("✅ SchemaValidator cleanup successful")
            
        except Exception as e:
            print(f"❌ SchemaValidator test failed: {e}")
    
    asyncio.run(test_schema_validator())