#!/usr/bin/env python3
"""
Enhanced Source Components for V5.0 Phase 2 Component Library
============================================================

Enhanced Source components for V5.0 data ingestion with proper service type support.

Supported V5.0 Service Types:
- data_source: General data ingestion
- api_source: API-based data source
- file_source: File-based data source
- stream_source: Real-time stream data source

All source components map to Phase 2 base type: Source
"""

from enhanced_base import (
    EnhancedBaseComponent, ComponentConfiguration, ComponentValidationError,
    ComponentInitializationError, ComponentOperationError, ConfigurationValidator
)
from typing import Dict, Any, AsyncGenerator, Optional, List
import asyncio
import json
import time
from pathlib import Path


class EnhancedSource(EnhancedBaseComponent):
    """Enhanced Source component for V5.0 data ingestion"""
    
    def __init__(self, config: ComponentConfiguration):
        super().__init__(config)
        
        # Validate this is a Source-type component
        self.validate_base_type("Source")
        
        # Source-specific configuration
        self.output_schema = self._extract_schema_from_outputs()
        self.generation_rate = self.get_resource_requirement("generation_rate", 1.0)
        self.max_records = self.get_resource_requirement("max_records", None)
        self.data_format = self.outputs.get("format", "json")
        
        # Source state tracking
        self.records_generated = 0
        self.last_generation_time = None
        self.generation_errors = 0
        
        self.logger.info(f"🔌 Enhanced Source '{self.name}' created (service_type: {self.service_type})")
    
    async def initialize(self) -> None:
        """Initialize source component"""
        try:
            self.initialization_time = time.time()
            
            # Validate output schema
            if not self.output_schema:
                raise ComponentValidationError(f"Source component '{self.name}' must define output schema")
            
            if not ConfigurationValidator.validate_schema_format(self.output_schema):
                raise ComponentValidationError(f"Invalid output schema format for source '{self.name}'")
            
            # Initialize based on service type
            if self.service_type == "data_source":
                await self._initialize_data_source()
            elif self.service_type == "api_source":
                await self._initialize_api_source()
            elif self.service_type == "file_source":
                await self._initialize_file_source()
            elif self.service_type == "stream_source":
                await self._initialize_stream_source()
            else:
                raise ComponentValidationError(f"Unsupported service type for Source: {self.service_type}")
            
            self.is_initialized = True
            self.health_status = "healthy"
            self.logger.info(f"✅ Enhanced Source '{self.name}' initialized successfully")
            
        except Exception as e:
            self.health_status = "failed"
            self.logger.error(f"❌ Failed to initialize Source '{self.name}': {e}")
            raise ComponentInitializationError(f"Source initialization failed: {e}") from e
    
    async def start(self) -> None:
        """Start source data generation"""
        if not self.is_initialized:
            raise ComponentOperationError(f"Source '{self.name}' not initialized")
        
        await self.safe_operation("start", self._start_generation)
        self.is_running = True
        self.startup_time = time.time()
        self.logger.info(f"🚀 Enhanced Source '{self.name}' started")
    
    async def stop(self) -> None:
        """Stop source data generation"""
        await self.safe_operation("stop", self._stop_generation)
        self.is_running = False
        self.logger.info(f"🛑 Enhanced Source '{self.name}' stopped")
    
    async def generate_data(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate data according to output schema"""
        if not self.is_running:
            raise ComponentOperationError(f"Source '{self.name}' not running")
        
        # Implementation depends on service type
        try:
            if self.service_type == "data_source":
                async for data in self._generate_data_source():
                    yield data
            elif self.service_type == "api_source":
                async for data in self._generate_api_source():
                    yield data
            elif self.service_type == "file_source":
                async for data in self._generate_file_source():
                    yield data
            elif self.service_type == "stream_source":
                async for data in self._generate_stream_source():
                    yield data
        except Exception as e:
            self.generation_errors += 1
            self.logger.error(f"❌ Data generation failed for '{self.name}': {e}")
            raise ComponentOperationError(f"Data generation failed: {e}") from e
    
    async def health_check(self) -> Dict[str, Any]:
        """Return source health status"""
        health_data = {
            "component": self.name,
            "type": "Source",
            "service_type": self.service_type,
            "status": self.health_status,
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "output_schema_valid": bool(self.output_schema),
            "generation_rate": self.generation_rate,
            "records_generated": self.records_generated,
            "generation_errors": self.generation_errors,
            "last_generation_time": self.last_generation_time
        }
        
        # Service-type specific health checks
        if self.service_type == "api_source":
            endpoint = self.get_environment_variable("endpoint")
            health_data["endpoint_configured"] = bool(endpoint)
        elif self.service_type == "file_source":
            file_path = self.get_environment_variable("file_path")
            health_data["file_path_configured"] = bool(file_path)
            if file_path:
                health_data["file_exists"] = Path(file_path).exists()
        
        return health_data
    
    async def validate_configuration(self) -> bool:
        """Validate source configuration"""
        try:
            # Validate required outputs
            if not self.outputs:
                self.logger.error("Source component must define outputs")
                return False
            
            # Validate schema
            if not self.output_schema:
                self.logger.error("Source component must define output schema")
                return False
            
            if not ConfigurationValidator.validate_schema_format(self.output_schema):
                self.logger.error("Invalid output schema format")
                return False
            
            # Service-type specific validation
            if self.service_type == "api_source":
                endpoint = self.get_environment_variable("endpoint")
                if not endpoint:
                    self.logger.error("API source requires 'endpoint' environment variable")
                    return False
                if not ConfigurationValidator.validate_url_format(endpoint):
                    self.logger.error(f"Invalid endpoint URL format: {endpoint}")
                    return False
            
            elif self.service_type == "file_source":
                file_path = self.get_environment_variable("file_path")
                if not file_path:
                    self.logger.error("File source requires 'file_path' environment variable")
                    return False
            
            elif self.service_type == "stream_source":
                stream_config = self.validation_config.get("stream_config", {}) if self.validation_config else {}
                if not stream_config:
                    self.logger.error("Stream source requires stream_config in validation section")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    # Service-type specific initialization methods
    async def _initialize_data_source(self) -> None:
        """Initialize generic data source"""
        self.logger.info(f"Initializing data source '{self.name}'")
        # Validate data generation parameters
        if self.generation_rate <= 0:
            raise ComponentValidationError("Generation rate must be positive")
    
    async def _initialize_api_source(self) -> None:
        """Initialize API-based source"""
        endpoint = self.get_environment_variable("endpoint", required=True)
        api_key = self.get_environment_variable("api_key")
        
        self.logger.info(f"Initializing API source '{self.name}' with endpoint: {endpoint}")
        
        # Test API connectivity
        import aiohttp
        try:
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers, timeout=10) as response:
                    if response.status >= 400:
                        raise ComponentInitializationError(f"API endpoint returned status {response.status}")
                    self.logger.info(f"✅ API connectivity test passed for '{self.name}'")
        except Exception as e:
            raise ComponentInitializationError(f"API connectivity test failed: {e}")
    
    async def _initialize_file_source(self) -> None:
        """Initialize file-based source"""
        file_path = self.get_environment_variable("file_path", required=True)
        
        self.logger.info(f"Initializing file source '{self.name}' with file: {file_path}")
        
        # Validate file exists and is readable
        path = Path(file_path)
        if not path.exists():
            raise ComponentInitializationError(f"Source file does not exist: {file_path}")
        if not path.is_file():
            raise ComponentInitializationError(f"Source path is not a file: {file_path}")
        
        self.logger.info(f"✅ File validation passed for '{self.name}'")
    
    async def _initialize_stream_source(self) -> None:
        """Initialize stream-based source"""
        stream_config = self.validation_config.get("stream_config", {}) if self.validation_config else {}
        stream_type = stream_config.get("type", "kafka")
        
        self.logger.info(f"Initializing stream source '{self.name}' with type: {stream_type}")
        
        if stream_type == "kafka":
            bootstrap_servers = stream_config.get("bootstrap_servers")
            topic = stream_config.get("topic")
            if not bootstrap_servers or not topic:
                raise ComponentValidationError("Kafka stream requires bootstrap_servers and topic")
        
        self.logger.info(f"✅ Stream configuration validated for '{self.name}'")
    
    # Service-type specific operation methods
    async def _start_generation(self) -> None:
        """Start data generation process"""
        self.logger.info(f"Starting data generation for '{self.name}'")
        # Service-specific startup logic would go here
    
    async def _stop_generation(self) -> None:
        """Stop data generation process"""
        self.logger.info(f"Stopping data generation for '{self.name}'")
        # Service-specific shutdown logic would go here
    
    # Service-type specific data generation methods
    async def _generate_data_source(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate data for generic data source"""
        while self.is_running:
            if self.max_records and self.records_generated >= self.max_records:
                break
            
            # Generate sample data based on schema
            data = self._generate_sample_data()
            self.records_generated += 1
            self.last_generation_time = time.time()
            
            self.log_component_metrics({
                "records_generated": self.records_generated,
                "generation_rate": self.generation_rate
            })
            
            yield data
            
            # Control generation rate
            await asyncio.sleep(1.0 / self.generation_rate)
    
    async def _generate_api_source(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate data from API source"""
        endpoint = self.get_environment_variable("endpoint", required=True)
        api_key = self.get_environment_variable("api_key")
        
        import aiohttp
        
        while self.is_running:
            if self.max_records and self.records_generated >= self.max_records:
                break
            
            try:
                headers = {}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.records_generated += 1
                            self.last_generation_time = time.time()
                            yield data
                        else:
                            self.logger.warning(f"API returned status {response.status}")
            except Exception as e:
                self.generation_errors += 1
                self.logger.error(f"API request failed: {e}")
            
            await asyncio.sleep(1.0 / self.generation_rate)
    
    async def _generate_file_source(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate data from file source"""
        file_path = self.get_environment_variable("file_path", required=True)
        
        with open(file_path, 'r') as file:
            for line in file:
                if not self.is_running:
                    break
                if self.max_records and self.records_generated >= self.max_records:
                    break
                
                try:
                    if self.data_format == "json":
                        data = json.loads(line.strip())
                    else:
                        data = {"content": line.strip()}
                    
                    self.records_generated += 1
                    self.last_generation_time = time.time()
                    yield data
                    
                    await asyncio.sleep(1.0 / self.generation_rate)
                except Exception as e:
                    self.generation_errors += 1
                    self.logger.error(f"Failed to parse line: {e}")
    
    async def _generate_stream_source(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate data from stream source"""
        # Mock stream data generation for now
        # In real implementation, this would connect to Kafka, Pulsar, etc.
        stream_config = self.validation_config.get("stream_config", {}) if self.validation_config else {}
        
        while self.is_running:
            if self.max_records and self.records_generated >= self.max_records:
                break
            
            # Generate stream-like data
            data = {
                "stream_id": stream_config.get("topic", "default"),
                "timestamp": time.time(),
                "sequence": self.records_generated,
                "payload": self._generate_sample_data()
            }
            
            self.records_generated += 1
            self.last_generation_time = time.time()
            yield data
            
            await asyncio.sleep(1.0 / self.generation_rate)
    
    def _extract_schema_from_outputs(self) -> Dict[str, Any]:
        """Extract schema from outputs configuration"""
        # Look for schema in direct outputs
        if "schema" in self.outputs:
            return self.outputs["schema"]
        
        # Look for schema in first output definition
        for output_name, output_config in self.outputs.items():
            if isinstance(output_config, dict) and "schema" in output_config:
                return output_config["schema"]
        
        # Return empty schema if none found
        return {}
    
    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample data based on output schema"""
        # Simple sample data generation based on schema type
        schema_type = self.output_schema.get("type", "object")
        
        if schema_type == "object":
            properties = self.output_schema.get("properties", {})
            sample_data = {}
            
            for prop_name, prop_schema in properties.items():
                prop_type = prop_schema.get("type", "string")
                if prop_type == "string":
                    sample_data[prop_name] = f"sample_{prop_name}_{self.records_generated}"
                elif prop_type == "integer":
                    sample_data[prop_name] = self.records_generated
                elif prop_type == "number":
                    sample_data[prop_name] = float(self.records_generated) * 1.5
                elif prop_type == "boolean":
                    sample_data[prop_name] = self.records_generated % 2 == 0
                else:
                    sample_data[prop_name] = f"value_{self.records_generated}"
            
            return sample_data
        else:
            return {"id": self.records_generated, "data": f"sample_data_{self.records_generated}"}


# Export the enhanced source component
__all__ = ['EnhancedSource']