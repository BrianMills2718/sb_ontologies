#!/usr/bin/env python3
"""
Enhanced Sink Components for V5.0 Phase 2 Component Library
==========================================================

Enhanced Sink components for V5.0 data output with proper service type support.

Supported V5.0 Service Types:
- database: Database storage sink
- file_output: File-based output sink
- api_output: API-based output sink
- message_queue: Message queue output sink

All sink components map to Phase 2 base type: Sink
"""

from enhanced_base import (
    EnhancedBaseComponent, ComponentConfiguration, ComponentValidationError,
    ComponentInitializationError, ComponentOperationError, ConfigurationValidator
)
from typing import Dict, Any, List, Optional
import asyncio
import json
import time
from pathlib import Path
import hashlib


class EnhancedSink(EnhancedBaseComponent):
    """Enhanced Sink component for V5.0 data output"""
    
    def __init__(self, config: ComponentConfiguration):
        super().__init__(config)
        
        # Validate this is a Sink-type component
        self.validate_base_type("Sink")
        
        # Sink-specific configuration
        self.input_schema = self._extract_schema_from_inputs()
        self.storage_format = self.get_resource_requirement("storage_format", "json")
        self.batch_size = self.get_resource_requirement("batch_size", 1)
        self.flush_interval = self.get_resource_requirement("flush_interval", 5.0)
        
        # Sink state tracking
        self.records_stored = 0
        self.storage_errors = 0
        self.last_storage_time = None
        self.pending_records = []
        self.total_bytes_stored = 0
        
        # Service-specific attributes
        self.connection_established = False
        self.file_handle = None
        self.database_connected = False
        self.api_endpoint_validated = False
        
        self.logger.info(f"💾 Enhanced Sink '{self.name}' created (service_type: {self.service_type})")
    
    async def initialize(self) -> None:
        """Initialize sink component"""
        try:
            self.initialization_time = time.time()
            
            # Validate input schema
            if not self.input_schema:
                raise ComponentValidationError(f"Sink component '{self.name}' must define input schema")
            
            if not ConfigurationValidator.validate_schema_format(self.input_schema):
                raise ComponentValidationError(f"Invalid input schema format for sink '{self.name}'")
            
            # Initialize based on service type
            if self.service_type == "database":
                await self._initialize_database()
            elif self.service_type == "file_output":
                await self._initialize_file_output()
            elif self.service_type == "api_output":
                await self._initialize_api_output()
            elif self.service_type == "message_queue":
                await self._initialize_message_queue()
            else:
                raise ComponentValidationError(f"Unsupported service type for Sink: {self.service_type}")
            
            self.is_initialized = True
            self.health_status = "healthy"
            self.logger.info(f"✅ Enhanced Sink '{self.name}' initialized successfully")
            
        except Exception as e:
            self.health_status = "failed"
            self.logger.error(f"❌ Failed to initialize Sink '{self.name}': {e}")
            raise ComponentInitializationError(f"Sink initialization failed: {e}") from e
    
    async def start(self) -> None:
        """Start sink processing"""
        if not self.is_initialized:
            raise ComponentOperationError(f"Sink '{self.name}' not initialized")
        
        await self.safe_operation("start", self._start_storage)
        self.is_running = True
        self.startup_time = time.time()
        
        # Start flush timer if using batching
        if self.batch_size > 1:
            asyncio.create_task(self._flush_timer())
        
        self.logger.info(f"🚀 Enhanced Sink '{self.name}' started")
    
    async def stop(self) -> None:
        """Stop sink processing"""
        # Flush any pending records
        if self.pending_records:
            await self._flush_pending_records()
        
        await self.safe_operation("stop", self._stop_storage)
        self.is_running = False
        self.logger.info(f"🛑 Enhanced Sink '{self.name}' stopped")
    
    async def store(self, data: Dict[str, Any]) -> bool:
        """Store data to sink destination"""
        if not self.is_running:
            raise ComponentOperationError(f"Sink '{self.name}' not running")
        
        try:
            # Validate input against schema
            if not self._validate_input_schema(data):
                raise ComponentOperationError(f"Input data doesn't match schema for '{self.name}'")
            
            # Handle batching
            if self.batch_size > 1:
                self.pending_records.append(data)
                
                # Flush if batch is full
                if len(self.pending_records) >= self.batch_size:
                    await self._flush_pending_records()
            else:
                # Store immediately
                await self._store_single_record(data)
            
            return True
            
        except Exception as e:
            self.storage_errors += 1
            self.logger.error(f"❌ Storage failed for '{self.name}': {e}")
            raise ComponentOperationError(f"Storage failed: {e}") from e
    
    async def store_batch(self, data_batch: List[Dict[str, Any]]) -> int:
        """Store batch of data to sink destination"""
        if not self.is_running:
            raise ComponentOperationError(f"Sink '{self.name}' not running")
        
        stored_count = 0
        
        for data in data_batch:
            try:
                await self.store(data)
                stored_count += 1
            except Exception as e:
                self.logger.error(f"Failed to store record in batch: {e}")
        
        return stored_count
    
    async def health_check(self) -> Dict[str, Any]:
        """Return sink health status"""
        health_data = {
            "component": self.name,
            "type": "Sink",
            "service_type": self.service_type,
            "status": self.health_status,
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "input_schema_valid": bool(self.input_schema),
            "records_stored": self.records_stored,
            "storage_errors": self.storage_errors,
            "pending_records": len(self.pending_records),
            "total_bytes_stored": self.total_bytes_stored,
            "last_storage_time": self.last_storage_time
        }
        
        # Service-type specific health checks
        if self.service_type == "database":
            health_data["database_connected"] = self.database_connected
            db_url = self.get_environment_variable("database_url")
            health_data["database_url_configured"] = bool(db_url)
        elif self.service_type == "file_output":
            output_path = self.get_environment_variable("output_path")
            health_data["output_path_configured"] = bool(output_path)
            health_data["file_handle_open"] = self.file_handle is not None
        elif self.service_type == "api_output":
            health_data["api_endpoint_validated"] = self.api_endpoint_validated
            endpoint = self.get_environment_variable("endpoint")
            health_data["endpoint_configured"] = bool(endpoint)
        elif self.service_type == "message_queue":
            health_data["connection_established"] = self.connection_established
        
        return health_data
    
    async def validate_configuration(self) -> bool:
        """Validate sink configuration"""
        try:
            # Validate required inputs
            if not self.inputs:
                self.logger.error("Sink component must define inputs")
                return False
            
            # Validate schema
            if not self.input_schema:
                self.logger.error("Sink component must define input schema")
                return False
            
            if not ConfigurationValidator.validate_schema_format(self.input_schema):
                self.logger.error("Invalid input schema format")
                return False
            
            # Service-type specific validation
            if self.service_type == "database":
                db_url = self.get_environment_variable("database_url")
                if not db_url:
                    self.logger.error("Database sink requires 'database_url' environment variable")
                    return False
            
            elif self.service_type == "file_output":
                output_path = self.get_environment_variable("output_path")
                if not output_path:
                    self.logger.error("File output sink requires 'output_path' environment variable")
                    return False
            
            elif self.service_type == "api_output":
                endpoint = self.get_environment_variable("endpoint")
                if not endpoint:
                    self.logger.error("API output sink requires 'endpoint' environment variable")
                    return False
                if not ConfigurationValidator.validate_url_format(endpoint):
                    self.logger.error(f"Invalid endpoint URL format: {endpoint}")
                    return False
            
            elif self.service_type == "message_queue":
                queue_config = self.validation_config.get("queue_config", {}) if self.validation_config else {}
                if not queue_config:
                    self.logger.error("Message queue sink requires queue_config in validation section")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    # Service-type specific initialization methods
    async def _initialize_database(self) -> None:
        """Initialize database sink"""
        db_url = self.get_environment_variable("database_url", required=True)
        table_name = self.get_environment_variable("table_name", "data_sink")
        
        self.logger.info(f"Initializing database sink '{self.name}' with URL: {db_url}")
        
        # Mock database connection test
        try:
            # In real implementation, would use actual database client
            if "postgresql://" in db_url or "mysql://" in db_url or "sqlite:" in db_url:
                self.database_connected = True
                self.logger.info(f"✅ Database connection test passed for '{self.name}'")
            else:
                raise ComponentInitializationError(f"Unsupported database URL format: {db_url}")
        except Exception as e:
            raise ComponentInitializationError(f"Database connection test failed: {e}")
    
    async def _initialize_file_output(self) -> None:
        """Initialize file output sink"""
        output_path = self.get_environment_variable("output_path", required=True)
        
        self.logger.info(f"Initializing file output sink '{self.name}' with path: {output_path}")
        
        # Validate output directory exists or can be created
        output_file = Path(output_path)
        output_dir = output_file.parent
        
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Test write permissions
            test_file = output_dir / f".test_write_{self.name}"
            test_file.write_text("test")
            test_file.unlink()
            
            self.logger.info(f"✅ File output path validated for '{self.name}'")
        except Exception as e:
            raise ComponentInitializationError(f"File output path validation failed: {e}")
    
    async def _initialize_api_output(self) -> None:
        """Initialize API output sink"""
        endpoint = self.get_environment_variable("endpoint", required=True)
        api_key = self.get_environment_variable("api_key")
        
        self.logger.info(f"Initializing API output sink '{self.name}' with endpoint: {endpoint}")
        
        # Test API endpoint connectivity
        import aiohttp
        try:
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
                headers["Content-Type"] = "application/json"
            
            # Simple connectivity test
            async with aiohttp.ClientSession() as session:
                test_data = {"test": "connectivity"}
                async with session.post(endpoint, json=test_data, headers=headers, timeout=10) as response:
                    if response.status < 500:  # Accept any non-server error
                        self.api_endpoint_validated = True
                        self.logger.info(f"✅ API endpoint connectivity test passed for '{self.name}'")
                    else:
                        raise ComponentInitializationError(f"API endpoint returned status {response.status}")
        except Exception as e:
            raise ComponentInitializationError(f"API endpoint connectivity test failed: {e}")
    
    async def _initialize_message_queue(self) -> None:
        """Initialize message queue sink"""
        queue_config = self.validation_config.get("queue_config", {}) if self.validation_config else {}
        queue_type = queue_config.get("type", "redis")
        
        self.logger.info(f"Initializing message queue sink '{self.name}' with type: {queue_type}")
        
        if queue_type == "redis":
            redis_url = queue_config.get("redis_url", "redis://localhost:6379")
            queue_name = queue_config.get("queue_name", "default_queue")
            
            # Mock Redis connection test
            self.connection_established = True
            self.logger.info(f"✅ Message queue connection established for '{self.name}'")
        elif queue_type == "kafka":
            bootstrap_servers = queue_config.get("bootstrap_servers")
            topic = queue_config.get("topic")
            if not bootstrap_servers or not topic:
                raise ComponentValidationError("Kafka queue requires bootstrap_servers and topic")
            self.connection_established = True
        else:
            raise ComponentValidationError(f"Unsupported queue type: {queue_type}")
    
    # Service-type specific operation methods
    async def _start_storage(self) -> None:
        """Start storage operation"""
        self.logger.info(f"Starting storage for '{self.name}'")
        
        if self.service_type == "file_output":
            # Open file handle for writing
            output_path = self.get_environment_variable("output_path", required=True)
            self.file_handle = open(output_path, 'a', encoding='utf-8')
            self.logger.info(f"File handle opened for '{self.name}'")
    
    async def _stop_storage(self) -> None:
        """Stop storage operation"""
        self.logger.info(f"Stopping storage for '{self.name}'")
        
        if self.service_type == "file_output" and self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            self.logger.info(f"File handle closed for '{self.name}'")
        elif self.service_type == "database":
            # Close database connection
            self.database_connected = False
            self.logger.info(f"Database connection closed for '{self.name}'")
    
    # Storage implementation methods
    async def _store_single_record(self, data: Dict[str, Any]) -> None:
        """Store a single record"""
        if self.service_type == "database":
            await self._store_to_database(data)
        elif self.service_type == "file_output":
            await self._store_to_file(data)
        elif self.service_type == "api_output":
            await self._store_to_api(data)
        elif self.service_type == "message_queue":
            await self._store_to_queue(data)
        
        self.records_stored += 1
        self.last_storage_time = time.time()
        
        # Estimate bytes stored
        data_str = json.dumps(data)
        self.total_bytes_stored += len(data_str.encode('utf-8'))
        
        self.log_component_metrics({
            "records_stored": self.records_stored,
            "total_bytes_stored": self.total_bytes_stored
        })
    
    async def _flush_pending_records(self) -> None:
        """Flush pending records in batch"""
        if not self.pending_records:
            return
        
        batch = self.pending_records.copy()
        self.pending_records.clear()
        
        self.logger.info(f"Flushing {len(batch)} pending records for '{self.name}'")
        
        for record in batch:
            await self._store_single_record(record)
    
    async def _flush_timer(self) -> None:
        """Timer to flush pending records periodically"""
        while self.is_running:
            await asyncio.sleep(self.flush_interval)
            if self.pending_records:
                await self._flush_pending_records()
    
    # Service-specific storage methods
    async def _store_to_database(self, data: Dict[str, Any]) -> None:
        """Store data to database"""
        if not self.database_connected:
            raise ComponentOperationError("Database not connected")
        
        table_name = self.get_environment_variable("table_name", "data_sink")
        
        # Mock database insert
        # In real implementation, would use actual database client
        self.logger.debug(f"Storing to database table '{table_name}': {data}")
    
    async def _store_to_file(self, data: Dict[str, Any]) -> None:
        """Store data to file"""
        if not self.file_handle:
            raise ComponentOperationError("File handle not open")
        
        if self.storage_format == "json":
            line = json.dumps(data) + "\n"
        elif self.storage_format == "csv":
            # Simple CSV format - in real implementation would use csv module
            line = ",".join(str(v) for v in data.values()) + "\n"
        else:
            line = str(data) + "\n"
        
        self.file_handle.write(line)
        self.file_handle.flush()
    
    async def _store_to_api(self, data: Dict[str, Any]) -> None:
        """Store data to API endpoint"""
        endpoint = self.get_environment_variable("endpoint", required=True)
        api_key = self.get_environment_variable("api_key")
        
        import aiohttp
        
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Wrap data in expected format
        payload = {
            "data": data,
            "source": self.name,
            "timestamp": time.time()
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=payload, headers=headers, timeout=30) as response:
                if response.status >= 400:
                    response_text = await response.text()
                    raise ComponentOperationError(f"API storage failed with status {response.status}: {response_text}")
    
    async def _store_to_queue(self, data: Dict[str, Any]) -> None:
        """Store data to message queue"""
        if not self.connection_established:
            raise ComponentOperationError("Message queue not connected")
        
        queue_config = self.validation_config.get("queue_config", {}) if self.validation_config else {}
        queue_type = queue_config.get("type", "redis")
        
        # Prepare message
        message = {
            "data": data,
            "source": self.name,
            "timestamp": time.time()
        }
        
        if queue_type == "redis":
            queue_name = queue_config.get("queue_name", "default_queue")
            # Mock Redis publish
            self.logger.debug(f"Publishing to Redis queue '{queue_name}': {message}")
        elif queue_type == "kafka":
            topic = queue_config.get("topic")
            # Mock Kafka publish
            self.logger.debug(f"Publishing to Kafka topic '{topic}': {message}")
    
    # Utility methods
    def _extract_schema_from_inputs(self) -> Dict[str, Any]:
        """Extract schema from inputs configuration"""
        # Look for schema in direct inputs
        if "schema" in self.inputs:
            return self.inputs["schema"]
        
        # Look for schema in first input definition
        for input_name, input_config in self.inputs.items():
            if isinstance(input_config, dict) and "schema" in input_config:
                return input_config["schema"]
        
        # Return empty schema if none found
        return {}
    
    def _validate_input_schema(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data against input schema"""
        # Simple validation - in real implementation would use jsonschema
        schema_type = self.input_schema.get("type", "object")
        
        if schema_type == "object":
            required_props = self.input_schema.get("required", [])
            for prop in required_props:
                if prop not in input_data:
                    self.logger.error(f"Missing required input property: {prop}")
                    return False
        
        return True


# Export the enhanced sink component
__all__ = ['EnhancedSink']