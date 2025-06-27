#!/usr/bin/env python3
"""
Component Class Tests for V5.0 Phase 2 Enhanced Components
=========================================================

Test suite for enhanced base component classes and their implementations.
Tests cover Source, Transformer, and Sink components with various service types.
"""

import asyncio
import pytest
import logging
import tempfile
import json
from pathlib import Path
from typing import Dict, Any

from enhanced_base import (
    ComponentConfiguration, EnhancedBaseComponent, ComponentValidationError,
    ComponentInitializationError, ComponentOperationError, EnhancedComponentFactory
)
from source_components import EnhancedSource
from transformer_components import EnhancedTransformer
from sink_components import EnhancedSink


class TestEnhancedBaseComponent:
    """Test enhanced base component functionality"""
    
    def test_component_configuration_creation(self):
        """Test component configuration creation"""
        config = ComponentConfiguration(
            name="test_component",
            component_type="test_type",
            service_type="web_service",
            base_type="Transformer"
        )
        
        assert config.name == "test_component"
        assert config.service_type == "web_service"
        assert config.base_type == "Transformer"
        assert config.inputs == {}
        assert config.outputs == {}
    
    def test_component_factory_validation(self):
        """Test component factory configuration validation"""
        valid_config = {
            "name": "test_component",
            "service_type": "web_service",
            "base_type": "Transformer",
            "inputs": {"request_data": {"schema": {"type": "object"}}},
            "outputs": {"response_data": {"schema": {"type": "object"}}}
        }
        
        validated_config = EnhancedComponentFactory.validate_component_config(valid_config)
        assert validated_config.name == "test_component"
        assert validated_config.service_type == "web_service"
        assert validated_config.base_type == "Transformer"
    
    def test_component_factory_missing_fields(self):
        """Test component factory validation with missing fields"""
        invalid_config = {
            "name": "test_component"
            # Missing service_type and base_type
        }
        
        with pytest.raises(ComponentValidationError, match="Missing required configuration fields"):
            EnhancedComponentFactory.validate_component_config(invalid_config)


class TestEnhancedSource:
    """Test enhanced source component functionality"""
    
    def test_data_source_creation(self):
        """Test creation of data source component"""
        config = ComponentConfiguration(
            name="test_data_source",
            component_type="data_source",
            service_type="data_source",
            base_type="Source",
            outputs={"data_stream": {"schema": {"type": "object", "properties": {"id": {"type": "integer"}}}}}
        )
        
        source = EnhancedSource(config)
        assert source.name == "test_data_source"
        assert source.service_type == "data_source"
        assert source.base_type == "Source"
        assert not source.is_initialized
    
    @pytest.mark.asyncio
    async def test_data_source_initialization(self):
        """Test data source initialization"""
        config = ComponentConfiguration(
            name="test_data_source",
            component_type="data_source",
            service_type="data_source",
            base_type="Source",
            outputs={"data_stream": {"schema": {"type": "object", "properties": {"id": {"type": "integer"}}}}},
            resource_requirements={"generation_rate": 2.0}
        )
        
        source = EnhancedSource(config)
        await source.initialize()
        
        assert source.is_initialized
        assert source.health_status == "healthy"
        assert source.generation_rate == 2.0
    
    @pytest.mark.asyncio
    async def test_api_source_validation(self):
        """Test API source configuration validation"""
        config = ComponentConfiguration(
            name="test_api_source",
            component_type="api_source",
            service_type="api_source",
            base_type="Source",
            outputs={"api_data": {"schema": {"type": "object"}}},
            environment_variables={"endpoint": "https://api.example.com/data"}
        )
        
        source = EnhancedSource(config)
        is_valid = await source.validate_configuration()
        assert is_valid
    
    @pytest.mark.asyncio
    async def test_file_source_missing_path(self):
        """Test file source with missing file path"""
        config = ComponentConfiguration(
            name="test_file_source",
            component_type="file_source",
            service_type="file_source",
            base_type="Source",
            outputs={"file_data": {"schema": {"type": "object"}}}
            # Missing file_path environment variable
        )
        
        source = EnhancedSource(config)
        is_valid = await source.validate_configuration()
        assert not is_valid
    
    def test_wrong_base_type(self):
        """Test source with wrong base type"""
        config = ComponentConfiguration(
            name="test_source",
            component_type="data_source",
            service_type="data_source",
            base_type="Transformer",  # Wrong base type
            outputs={"data_stream": {"schema": {"type": "object"}}}
        )
        
        with pytest.raises(ComponentValidationError, match="requires base_type='Source'"):
            EnhancedSource(config)


class TestEnhancedTransformer:
    """Test enhanced transformer component functionality"""
    
    def test_web_service_creation(self):
        """Test creation of web service transformer"""
        config = ComponentConfiguration(
            name="test_web_service",
            component_type="web_service",
            service_type="web_service",
            base_type="Transformer",
            inputs={"request_data": {"schema": {"type": "object"}}},
            outputs={"response_data": {"schema": {"type": "object"}}},
            resource_requirements={"port": 8080}
        )
        
        transformer = EnhancedTransformer(config)
        assert transformer.name == "test_web_service"
        assert transformer.service_type == "web_service"
        assert transformer.base_type == "Transformer"
    
    @pytest.mark.asyncio
    async def test_web_service_initialization(self):
        """Test web service initialization"""
        config = ComponentConfiguration(
            name="test_web_service",
            component_type="web_service",
            service_type="web_service",
            base_type="Transformer",
            inputs={"request_data": {"schema": {"type": "object"}}},
            outputs={"response_data": {"schema": {"type": "object"}}},
            resource_requirements={"port": 8080, "processing_timeout": 10.0}
        )
        
        transformer = EnhancedTransformer(config)
        await transformer.initialize()
        
        assert transformer.is_initialized
        assert transformer.health_status == "healthy"
        assert transformer.service_port == 8080
    
    @pytest.mark.asyncio
    async def test_data_processor_transformation(self):
        """Test data processor transformation"""
        config = ComponentConfiguration(
            name="test_processor",
            component_type="data_processor",
            service_type="data_processor",
            base_type="Transformer",
            inputs={"input_data": {"schema": {"type": "object", "required": ["value"]}}},
            outputs={"processed_data": {"schema": {"type": "object", "required": ["result"]}}},
            validation_config={"transformation_logic": {"type": "add_metadata"}}
        )
        
        transformer = EnhancedTransformer(config)
        await transformer.initialize()
        await transformer.start()
        
        input_data = {"input_data": {"value": 42}}
        result = await transformer.transform(input_data)
        
        assert "processed_data" in result
        assert "_metadata" in result["processed_data"]
        assert result["processed_data"]["_metadata"]["transformer"] == "test_processor"
    
    @pytest.mark.asyncio
    async def test_ml_model_missing_path(self):
        """Test ML model with missing model path"""
        config = ComponentConfiguration(
            name="test_model",
            component_type="ml_model",
            service_type="ml_model",
            base_type="Transformer",
            inputs={"model_input": {"schema": {"type": "object"}}},
            outputs={"model_output": {"schema": {"type": "object"}}}
            # Missing model_path environment variable
        )
        
        transformer = EnhancedTransformer(config)
        is_valid = await transformer.validate_configuration()
        assert not is_valid
    
    @pytest.mark.asyncio
    async def test_invalid_port_number(self):
        """Test web service with invalid port number"""
        config = ComponentConfiguration(
            name="test_web_service",
            component_type="web_service",
            service_type="web_service",
            base_type="Transformer",
            inputs={"request_data": {"schema": {"type": "object"}}},
            outputs={"response_data": {"schema": {"type": "object"}}},
            resource_requirements={"port": 80}  # Port below 1024
        )
        
        transformer = EnhancedTransformer(config)
        is_valid = await transformer.validate_configuration()
        assert not is_valid


class TestEnhancedSink:
    """Test enhanced sink component functionality"""
    
    def test_database_sink_creation(self):
        """Test creation of database sink"""
        config = ComponentConfiguration(
            name="test_database",
            component_type="database",
            service_type="database",
            base_type="Sink",
            inputs={"data_to_store": {"schema": {"type": "object"}}},
            environment_variables={"database_url": "postgresql://user:pass@localhost/db"}
        )
        
        sink = EnhancedSink(config)
        assert sink.name == "test_database"
        assert sink.service_type == "database"
        assert sink.base_type == "Sink"
    
    @pytest.mark.asyncio
    async def test_file_output_initialization(self):
        """Test file output sink initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output.jsonl"
            
            config = ComponentConfiguration(
                name="test_file_output",
                component_type="file_output",
                service_type="file_output",
                base_type="Sink",
                inputs={"data_to_write": {"schema": {"type": "object"}}},
                environment_variables={"output_path": str(output_path)},
                resource_requirements={"storage_format": "json"}
            )
            
            sink = EnhancedSink(config)
            await sink.initialize()
            
            assert sink.is_initialized
            assert sink.health_status == "healthy"
    
    @pytest.mark.asyncio
    async def test_file_output_storage(self):
        """Test file output storage functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output.jsonl"
            
            config = ComponentConfiguration(
                name="test_file_output",
                component_type="file_output",
                service_type="file_output",
                base_type="Sink",
                inputs={"data_to_write": {"schema": {"type": "object", "required": ["id"]}}},
                environment_variables={"output_path": str(output_path)},
                resource_requirements={"storage_format": "json"}
            )
            
            sink = EnhancedSink(config)
            await sink.initialize()
            await sink.start()
            
            # Store test data
            test_data = {"id": 1, "message": "test"}
            result = await sink.store(test_data)
            assert result is True
            
            await sink.stop()
            
            # Verify data was written
            assert output_path.exists()
            content = output_path.read_text()
            stored_data = json.loads(content.strip())
            assert stored_data == test_data
    
    @pytest.mark.asyncio
    async def test_api_output_validation(self):
        """Test API output sink configuration validation"""
        config = ComponentConfiguration(
            name="test_api_output",
            component_type="api_output",
            service_type="api_output",
            base_type="Sink",
            inputs={"data_to_send": {"schema": {"type": "object"}}},
            environment_variables={"endpoint": "https://api.example.com/store"}
        )
        
        sink = EnhancedSink(config)
        is_valid = await sink.validate_configuration()
        assert is_valid
    
    @pytest.mark.asyncio
    async def test_message_queue_missing_config(self):
        """Test message queue sink with missing configuration"""
        config = ComponentConfiguration(
            name="test_queue",
            component_type="message_queue",
            service_type="message_queue",
            base_type="Sink",
            inputs={"message_data": {"schema": {"type": "object"}}}
            # Missing queue_config in validation_config
        )
        
        sink = EnhancedSink(config)
        is_valid = await sink.validate_configuration()
        assert not is_valid


class TestIntegrationScenarios:
    """Test integration scenarios between components"""
    
    @pytest.mark.asyncio
    async def test_source_to_sink_pipeline(self):
        """Test data flow from source to sink"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "pipeline_output.jsonl"
            
            # Create source
            source_config = ComponentConfiguration(
                name="test_source",
                component_type="data_source",
                service_type="data_source",
                base_type="Source",
                outputs={"data_stream": {"schema": {"type": "object", "properties": {"id": {"type": "integer"}}}}},
                resource_requirements={"generation_rate": 5.0, "max_records": 3}
            )
            source = EnhancedSource(source_config)
            
            # Create sink
            sink_config = ComponentConfiguration(
                name="test_sink",
                component_type="file_output",
                service_type="file_output",
                base_type="Sink",
                inputs={"data_to_write": {"schema": {"type": "object"}}},
                environment_variables={"output_path": str(output_path)}
            )
            sink = EnhancedSink(sink_config)
            
            # Initialize and start components
            await source.initialize()
            await sink.initialize()
            await source.start()
            await sink.start()
            
            # Process data pipeline
            record_count = 0
            async for data in source.generate_data():
                await sink.store(data)
                record_count += 1
                if record_count >= 3:  # Match max_records
                    break
            
            await source.stop()
            await sink.stop()
            
            # Verify results
            assert output_path.exists()
            lines = output_path.read_text().strip().split('\n')
            assert len(lines) == 3
            
            # Verify each line is valid JSON
            for line in lines:
                data = json.loads(line)
                assert "id" in data
    
    @pytest.mark.asyncio
    async def test_source_transformer_sink_pipeline(self):
        """Test complete data pipeline with transformation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "transformed_output.jsonl"
            
            # Create source
            source_config = ComponentConfiguration(
                name="pipeline_source",
                component_type="data_source",
                service_type="data_source",
                base_type="Source",
                outputs={"data_stream": {"schema": {"type": "object", "properties": {"value": {"type": "string"}}}}},
                resource_requirements={"max_records": 2}
            )
            source = EnhancedSource(source_config)
            
            # Create transformer
            transformer_config = ComponentConfiguration(
                name="pipeline_transformer",
                component_type="data_processor",
                service_type="data_processor",
                base_type="Transformer",
                inputs={"input_data": {"schema": {"type": "object", "required": ["value"]}}},
                outputs={"processed_data": {"schema": {"type": "object", "required": ["value"]}}},
                validation_config={"transformation_logic": {"type": "add_metadata"}}
            )
            transformer = EnhancedTransformer(transformer_config)
            
            # Create sink
            sink_config = ComponentConfiguration(
                name="pipeline_sink",
                component_type="file_output",
                service_type="file_output",
                base_type="Sink",
                inputs={"data_to_write": {"schema": {"type": "object"}}},
                environment_variables={"output_path": str(output_path)}
            )
            sink = EnhancedSink(sink_config)
            
            # Initialize and start all components
            await source.initialize()
            await transformer.initialize()
            await sink.initialize()
            await source.start()
            await transformer.start()
            await sink.start()
            
            # Process pipeline
            record_count = 0
            async for source_data in source.generate_data():
                # Transform data
                transformed_data = await transformer.transform({"input_data": source_data})
                
                # Store transformed data
                await sink.store(transformed_data["processed_data"])
                
                record_count += 1
                if record_count >= 2:
                    break
            
            # Stop all components
            await source.stop()
            await transformer.stop()
            await sink.stop()
            
            # Verify pipeline results
            assert output_path.exists()
            lines = output_path.read_text().strip().split('\n')
            assert len(lines) == 2
            
            # Verify transformation was applied
            for line in lines:
                data = json.loads(line)
                assert "_metadata" in data  # Added by transformation
                assert data["_metadata"]["transformer"] == "pipeline_transformer"


# Run tests if executed directly
if __name__ == "__main__":
    # Configure logging for tests
    logging.basicConfig(level=logging.INFO)
    
    # Run tests using pytest
    pytest.main([__file__, "-v"])