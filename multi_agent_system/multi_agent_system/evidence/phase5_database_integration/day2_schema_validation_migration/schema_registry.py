"""
V5.0 Schema Registry
Manages schema definitions, versions, and registration with comprehensive tracking
"""

import asyncio
import time
import logging
import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


class SchemaRegistryError(Exception):
    """Raised when schema registry operations fail"""
    pass


class SchemaNotFoundError(Exception):
    """Raised when requested schema is not found"""
    pass


class SchemaVersionConflictError(Exception):
    """Raised when schema version conflicts occur"""
    pass


@dataclass
class SchemaMetadata:
    """Schema metadata for tracking"""
    name: str
    version: str
    hash: str
    created_at: float
    created_by: str = "system"
    description: str = ""
    tags: List[str] = None
    is_active: bool = False
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class SchemaRegistry:
    """Schema registry for managing schema definitions and versions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Configuration
        self.registry_path = config.get("registry_path", "./schema_registry")
        self.auto_backup = config.get("auto_backup", True)
        self.max_versions = config.get("max_versions", 10)
        self.compression_enabled = config.get("compression", False)
        
        # Internal state
        self.schemas: Dict[str, Any] = {}  # version -> schema
        self.metadata: Dict[str, SchemaMetadata] = {}  # version -> metadata
        self.version_history: List[str] = []
        self.active_version: Optional[str] = None
        
        # Registry loaded flag
        self.registry_loaded = False
        
        logger.info(f"SchemaRegistry initialized with path: {self.registry_path}")
    
    async def initialize(self):
        """Initialize schema registry"""
        logger.info("Initializing schema registry")
        
        try:
            # Create registry directory if it doesn't exist
            await self._ensure_registry_directory()
            
            # Load existing schemas
            await self._load_registry()
            
            # Mark registry as loaded before initializing default schema
            self.registry_loaded = True
            
            # Initialize default schema if registry is empty
            if not self.schemas:
                await self._initialize_default_schema()
            
            logger.info(f"Schema registry initialized with {len(self.schemas)} schemas")
            
        except Exception as e:
            logger.error(f"Schema registry initialization failed: {e}")
            raise SchemaRegistryError(f"Registry initialization failed: {e}")
    
    async def register_schema(self, schema_definition, version: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Register new schema version"""
        logger.info(f"Registering schema version {version}")
        
        if not self.registry_loaded:
            raise SchemaRegistryError("Registry not initialized")
        
        try:
            # Check if version already exists
            if version in self.schemas:
                raise SchemaVersionConflictError(f"Schema version {version} already exists")
            
            # Validate schema
            await self._validate_schema_definition(schema_definition)
            
            # Create schema metadata
            schema_metadata = SchemaMetadata(
                name=schema_definition.name,
                version=version,
                hash=schema_definition.get_schema_hash(),
                created_at=time.time(),
                description=metadata.get("description", "") if metadata else "",
                tags=metadata.get("tags", []) if metadata else []
            )
            
            # Check for hash conflicts
            existing_hash = await self._find_schema_by_hash(schema_metadata.hash)
            if existing_hash:
                logger.warning(f"Schema with same hash already exists: {existing_hash}")
            
            # Store schema and metadata
            self.schemas[version] = schema_definition
            self.metadata[version] = schema_metadata
            self.version_history.append(version)
            
            # Persist to storage
            await self._persist_schema(version, schema_definition, schema_metadata)
            
            # Update registry index
            await self._update_registry_index()
            
            # Set as active if first schema or explicitly requested
            if not self.active_version or (metadata and metadata.get("set_active", False)):
                await self.set_active_version(version)
            
            # Cleanup old versions if needed
            await self._cleanup_old_versions()
            
            logger.info(f"Schema version {version} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Schema registration failed for version {version}: {e}")
            raise SchemaRegistryError(f"Schema registration failed: {e}")
    
    async def get_schema(self, version: str):
        """Get schema by version"""
        if not self.registry_loaded:
            raise SchemaRegistryError("Registry not initialized")
        
        if version not in self.schemas:
            raise SchemaNotFoundError(f"Schema version {version} not found")
        
        return self.schemas[version]
    
    async def get_current_schema(self):
        """Get current active schema"""
        if not self.registry_loaded:
            raise SchemaRegistryError("Registry not initialized")
        
        if not self.active_version:
            return None
        
        return await self.get_schema(self.active_version)
    
    async def get_latest_schema(self):
        """Get latest schema version"""
        if not self.registry_loaded:
            raise SchemaRegistryError("Registry not initialized")
        
        if not self.version_history:
            raise SchemaNotFoundError("No schemas available")
        
        # Sort versions and get latest
        try:
            from schema_validator import SchemaVersion
        except ImportError:
            from .schema_validator import SchemaVersion
        
        sorted_versions = sorted(
            self.version_history,
            key=lambda v: SchemaVersion(v),
            reverse=True
        )
        
        latest_version = sorted_versions[0]
        return await self.get_schema(latest_version)
    
    async def get_default_schema(self):
        """Get default schema definition"""
        # Create default schema
        try:
            from schema_validator import SchemaDefinition, SchemaField, SchemaVersion
        except ImportError:
            from .schema_validator import SchemaDefinition, SchemaField, SchemaVersion
        
        default_schema = SchemaDefinition(
            version=SchemaVersion("1.0.0"),
            name="default_store_schema",
            fields=[
                SchemaField("id", "string", required=True, description="Unique identifier"),
                SchemaField("timestamp", "number", required=True, description="Event timestamp"),
                SchemaField("event_type", "string", required=True, description="Type of event"),
                SchemaField("data", "object", required=True, description="Event data payload"),
                SchemaField("user_id", "string", required=False, description="User identifier"),
                SchemaField("session_id", "string", required=False, description="Session identifier"),
                SchemaField("metadata", "object", required=False, description="Additional metadata")
            ],
            indexes=["id", "timestamp", "event_type", "user_id"],
            constraints=["UNIQUE(id)", "CHECK(timestamp > 0)"],
            metadata={
                "created_by": "system",
                "purpose": "default_store_schema",
                "version_type": "initial"
            }
        )
        
        return default_schema
    
    async def set_active_version(self, version: str) -> bool:
        """Set active schema version"""
        logger.info(f"Setting active schema version to {version}")
        
        if version not in self.schemas:
            raise SchemaNotFoundError(f"Schema version {version} not found")
        
        # Update metadata for previous active version
        if self.active_version and self.active_version in self.metadata:
            self.metadata[self.active_version].is_active = False
        
        # Set new active version
        self.active_version = version
        self.metadata[version].is_active = True
        
        # Persist changes
        await self._update_registry_index()
        
        logger.info(f"Active schema version set to {version}")
        return True
    
    async def list_versions(self) -> List[Dict[str, Any]]:
        """List all schema versions with metadata"""
        if not self.registry_loaded:
            raise SchemaRegistryError("Registry not initialized")
        
        version_list = []
        for version in self.version_history:
            metadata = self.metadata.get(version)
            if metadata:
                version_info = {
                    "version": version,
                    "name": metadata.name,
                    "created_at": metadata.created_at,
                    "description": metadata.description,
                    "is_active": metadata.is_active,
                    "hash": metadata.hash,
                    "tags": metadata.tags
                }
                version_list.append(version_info)
        
        # Sort by creation time (newest first)
        version_list.sort(key=lambda x: x["created_at"], reverse=True)
        
        return version_list
    
    async def delete_version(self, version: str) -> bool:
        """Delete schema version"""
        logger.info(f"Deleting schema version {version}")
        
        if version not in self.schemas:
            raise SchemaNotFoundError(f"Schema version {version} not found")
        
        if version == self.active_version:
            raise SchemaRegistryError("Cannot delete active schema version")
        
        if len(self.schemas) <= 1:
            raise SchemaRegistryError("Cannot delete last schema version")
        
        try:
            # Remove from memory
            del self.schemas[version]
            del self.metadata[version]
            self.version_history.remove(version)
            
            # Remove from storage
            await self._delete_schema_file(version)
            
            # Update registry index
            await self._update_registry_index()
            
            logger.info(f"Schema version {version} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Schema deletion failed for version {version}: {e}")
            raise SchemaRegistryError(f"Schema deletion failed: {e}")
    
    async def backup_registry(self, backup_path: Optional[str] = None) -> str:
        """Create backup of entire registry"""
        if backup_path is None:
            timestamp = int(time.time())
            backup_path = f"{self.registry_path}_backup_{timestamp}"
        
        logger.info(f"Creating registry backup at {backup_path}")
        
        try:
            # Create backup directory
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all schema files
            registry_dir = Path(self.registry_path)
            for schema_file in registry_dir.glob("*.json"):
                backup_file = backup_dir / schema_file.name
                backup_file.write_text(schema_file.read_text())
            
            # Copy registry index
            index_file = registry_dir / "registry_index.json"
            if index_file.exists():
                backup_index = backup_dir / "registry_index.json"
                backup_index.write_text(index_file.read_text())
            
            logger.info(f"Registry backup created successfully at {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Registry backup failed: {e}")
            raise SchemaRegistryError(f"Registry backup failed: {e}")
    
    async def _ensure_registry_directory(self):
        """Ensure registry directory exists"""
        registry_dir = Path(self.registry_path)
        registry_dir.mkdir(parents=True, exist_ok=True)
    
    async def _load_registry(self):
        """Load existing registry from storage"""
        logger.info("Loading schema registry from storage")
        
        registry_dir = Path(self.registry_path)
        
        # Load registry index if it exists
        index_file = registry_dir / "registry_index.json"
        if index_file.exists():
            try:
                index_data = json.loads(index_file.read_text())
                self.active_version = index_data.get("active_version")
                self.version_history = index_data.get("version_history", [])
                
                # Load metadata
                for version, metadata_dict in index_data.get("metadata", {}).items():
                    self.metadata[version] = SchemaMetadata(**metadata_dict)
                
            except Exception as e:
                logger.warning(f"Failed to load registry index: {e}")
        
        # Load individual schema files
        for schema_file in registry_dir.glob("schema_*.json"):
            try:
                version = schema_file.stem.replace("schema_", "")
                schema_data = json.loads(schema_file.read_text())
                
                # Reconstruct schema object
                schema = await self._deserialize_schema(schema_data)
                self.schemas[version] = schema
                
                # Add to version history if not already there
                if version not in self.version_history:
                    self.version_history.append(version)
                
            except Exception as e:
                logger.warning(f"Failed to load schema file {schema_file}: {e}")
        
        logger.info(f"Loaded {len(self.schemas)} schemas from registry")
    
    async def _initialize_default_schema(self):
        """Initialize default schema"""
        logger.info("Initializing default schema")
        
        default_schema = await self.get_default_schema()
        
        await self.register_schema(
            default_schema,
            str(default_schema.version),
            {
                "description": "Default schema for V5.0 store components",
                "tags": ["default", "initial"],
                "set_active": True
            }
        )
    
    async def _validate_schema_definition(self, schema_definition) -> bool:
        """Validate schema definition"""
        # Basic validation
        if not hasattr(schema_definition, 'name') or not schema_definition.name:
            raise ValueError("Schema must have a name")
        
        if not hasattr(schema_definition, 'version') or not schema_definition.version:
            raise ValueError("Schema must have a version")
        
        if not hasattr(schema_definition, 'fields') or not schema_definition.fields:
            raise ValueError("Schema must have fields")
        
        # Validate field names are unique
        field_names = [f.name for f in schema_definition.fields]
        if len(field_names) != len(set(field_names)):
            raise ValueError("Schema fields must have unique names")
        
        return True
    
    async def _find_schema_by_hash(self, schema_hash: str) -> Optional[str]:
        """Find schema version by hash"""
        for version, metadata in self.metadata.items():
            if metadata.hash == schema_hash:
                return version
        return None
    
    async def _persist_schema(self, version: str, schema_definition, metadata: SchemaMetadata):
        """Persist schema to storage"""
        registry_dir = Path(self.registry_path)
        
        # Serialize schema
        schema_data = await self._serialize_schema(schema_definition)
        
        # Write schema file
        schema_file = registry_dir / f"schema_{version}.json"
        schema_file.write_text(json.dumps(schema_data, indent=2))
        
        logger.debug(f"Schema {version} persisted to {schema_file}")
    
    async def _update_registry_index(self):
        """Update registry index file"""
        registry_dir = Path(self.registry_path)
        index_file = registry_dir / "registry_index.json"
        
        # Prepare index data
        index_data = {
            "active_version": self.active_version,
            "version_history": self.version_history,
            "metadata": {
                version: asdict(metadata)
                for version, metadata in self.metadata.items()
            },
            "last_updated": time.time()
        }
        
        # Write index file
        index_file.write_text(json.dumps(index_data, indent=2))
        
        logger.debug(f"Registry index updated at {index_file}")
    
    async def _cleanup_old_versions(self):
        """Cleanup old schema versions if limit exceeded"""
        if len(self.schemas) <= self.max_versions:
            return
        
        # Sort versions by creation time
        sorted_versions = sorted(
            self.version_history,
            key=lambda v: self.metadata[v].created_at
        )
        
        # Keep max_versions most recent
        versions_to_delete = sorted_versions[:-self.max_versions]
        
        for version in versions_to_delete:
            if version != self.active_version:  # Never delete active version
                try:
                    await self.delete_version(version)
                    logger.info(f"Cleaned up old schema version {version}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup version {version}: {e}")
    
    async def _delete_schema_file(self, version: str):
        """Delete schema file from storage"""
        registry_dir = Path(self.registry_path)
        schema_file = registry_dir / f"schema_{version}.json"
        
        if schema_file.exists():
            schema_file.unlink()
            logger.debug(f"Schema file {schema_file} deleted")
    
    async def _serialize_schema(self, schema_definition) -> Dict[str, Any]:
        """Serialize schema definition to JSON-compatible format"""
        try:
            from schema_validator import SchemaDefinition
        except ImportError:
            from .schema_validator import SchemaDefinition
        
        if hasattr(schema_definition, '__dict__'):
            # Convert dataclass to dict
            schema_dict = asdict(schema_definition)
            
            # Handle version object
            if 'version' in schema_dict:
                version_obj = schema_dict['version']
                if hasattr(version_obj, 'version_string'):
                    schema_dict['version'] = version_obj.version_string
                else:
                    schema_dict['version'] = str(version_obj)
            
            return schema_dict
        
        return {"error": "Unable to serialize schema"}
    
    async def _deserialize_schema(self, schema_data: Dict[str, Any]):
        """Deserialize schema definition from JSON format"""
        try:
            from schema_validator import SchemaDefinition, SchemaField, SchemaVersion
        except ImportError:
            from .schema_validator import SchemaDefinition, SchemaField, SchemaVersion
        
        try:
            # Reconstruct fields
            fields = []
            for field_data in schema_data.get('fields', []):
                field = SchemaField(**field_data)
                fields.append(field)
            
            # Reconstruct schema
            schema = SchemaDefinition(
                version=SchemaVersion(schema_data['version']),
                name=schema_data['name'],
                fields=fields,
                indexes=schema_data.get('indexes', []),
                constraints=schema_data.get('constraints', []),
                metadata=schema_data.get('metadata', {}),
                created_at=schema_data.get('created_at', time.time())
            )
            
            return schema
            
        except Exception as e:
            logger.error(f"Schema deserialization failed: {e}")
            raise SchemaRegistryError(f"Schema deserialization failed: {e}")
    
    def get_registry_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_schemas": len(self.schemas),
            "active_version": self.active_version,
            "registry_path": self.registry_path,
            "registry_loaded": self.registry_loaded,
            "version_history_count": len(self.version_history),
            "auto_backup_enabled": self.auto_backup,
            "max_versions": self.max_versions
        }
    
    async def cleanup(self):
        """Cleanup schema registry"""
        logger.info("Cleaning up schema registry")
        
        # Create backup if auto_backup is enabled
        if self.auto_backup and self.schemas:
            try:
                await self.backup_registry()
                logger.info("Auto-backup created during cleanup")
            except Exception as e:
                logger.warning(f"Auto-backup failed during cleanup: {e}")
        
        # Clear memory
        self.schemas.clear()
        self.metadata.clear()
        self.version_history.clear()
        self.active_version = None
        self.registry_loaded = False


# Test harness
if __name__ == "__main__":
    async def test_schema_registry():
        """Test schema registry functionality"""
        
        # Use temporary directory for testing
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        config = {
            "registry_path": temp_dir + "/test_registry",
            "auto_backup": True,
            "max_versions": 5
        }
        
        registry = SchemaRegistry(config)
        
        try:
            # Test initialization
            await registry.initialize()
            print("✅ SchemaRegistry initialized successfully")
            
            # Test getting default schema
            default_schema = await registry.get_default_schema()
            print(f"✅ Default schema created: {default_schema.name} v{default_schema.version}")
            
            # Test current schema
            current_schema = await registry.get_current_schema()
            if current_schema:
                print(f"✅ Current schema: {current_schema.name} v{current_schema.version}")
            
            # Test version listing
            versions = await registry.list_versions()
            print(f"✅ Available versions: {len(versions)}")
            for version in versions:
                print(f"   - {version['version']}: {version['name']} {'(active)' if version['is_active'] else ''}")
            
            # Test latest schema
            latest_schema = await registry.get_latest_schema()
            print(f"✅ Latest schema: {latest_schema.name} v{latest_schema.version}")
            
            # Test registry statistics
            stats = registry.get_registry_statistics()
            print(f"✅ Registry statistics: {stats}")
            
            # Test backup
            backup_path = await registry.backup_registry()
            print(f"✅ Registry backup created at: {backup_path}")
            
            # Test cleanup
            await registry.cleanup()
            print("✅ SchemaRegistry cleanup successful")
            
        except Exception as e:
            print(f"❌ SchemaRegistry test failed: {e}")
        
        finally:
            # Cleanup temp directory
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    asyncio.run(test_schema_registry())