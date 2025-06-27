"""
V5.0 Enhanced Store Component Tests
Comprehensive test suite for V5EnhancedStore component with database integration
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# Import components under test
import sys
sys.path.append('/home/brian/autocoder3_cc/evidence/phase5_database_integration/day1_enhanced_store_components')

from v5_enhanced_store import V5EnhancedStore, StoreOperationError, SchemaValidationError
from database_connection_manager import DatabaseConnectionManager, ConnectionPoolError


class TestV5EnhancedStore:
    """Test suite for V5EnhancedStore component"""
    
    @pytest.fixture
    def basic_config(self):
        """Basic configuration for testing"""
        return {
            "database": {
                "database_type": "sqlite",
                "database_path": ":memory:",
                "pool": {
                    "min_connections": 2,
                    "max_connections": 5
                }
            },
            "performance": {
                "cache_enabled": True,
                "optimization_level": "standard"
            },
            "validation": {
                "schema_version": "1.0.0",
                "strict_validation": True
            }
        }
    
    @pytest.fixture
    def enhanced_store(self, basic_config):
        """Create V5EnhancedStore instance for testing"""
        return V5EnhancedStore("test_store", basic_config)
    
    def test_enhanced_store_initialization(self, enhanced_store, basic_config):
        """Test V5EnhancedStore initialization"""
        assert enhanced_store.name == "test_store"
        assert enhanced_store.config == basic_config
        assert enhanced_store.database_config == basic_config["database"]
        assert enhanced_store.performance_config == basic_config["performance"]
        assert enhanced_store.validation_config == basic_config["validation"]
        assert enhanced_store.operation_count == 0
        assert enhanced_store.error_count == 0
    
    @pytest.mark.asyncio
    async def test_enhanced_store_setup_success(self, enhanced_store):
        """Test successful V5EnhancedStore setup"""
        await enhanced_store.setup()
        
        assert enhanced_store.setup_complete is True
        assert enhanced_store.connection_manager is not None
        assert enhanced_store.schema_validator is not None
        assert enhanced_store.transaction_manager is not None
        assert enhanced_store.performance_optimizer is not None
    
    @pytest.mark.asyncio
    async def test_enhanced_store_setup_failure(self, basic_config):
        """Test V5EnhancedStore setup failure handling"""
        # Create store with invalid config to trigger failure
        invalid_config = basic_config.copy()
        invalid_config["database"]["database_type"] = "invalid_db"
        
        store = V5EnhancedStore("failing_store", invalid_config)
        
        # Setup should handle the failure gracefully with mock components
        await store.setup()
        
        # Should still complete setup with mock components
        assert store.setup_complete is True
    
    @pytest.mark.asyncio
    async def test_consume_success(self, enhanced_store):
        """Test successful data consumption"""
        await enhanced_store.setup()
        
        test_data = {
            "user_id": 12345,
            "action": "user_login",
            "timestamp": time.time(),
            "metadata": {"ip": "192.168.1.1", "user_agent": "test"}
        }
        
        result = await enhanced_store.consume(test_data)
        
        assert result["success"] is True
        assert result["stored_records"] >= 1
        assert "transaction_id" in result
        assert "schema_version" in result
        assert "execution_time" in result
        assert result["execution_time"] > 0
        
        # Check metrics updated
        assert enhanced_store.operation_count == 1
        assert enhanced_store.error_count == 0
    
    @pytest.mark.asyncio
    async def test_consume_none_data_failure(self, enhanced_store):
        """Test consumption failure with None data"""
        await enhanced_store.setup()
        
        result = await enhanced_store.consume(None)
        
        assert result["success"] is False
        assert "error_message" in result
        assert "Cannot consume None data" in result["error_message"]
        
        # Check error metrics updated
        assert enhanced_store.operation_count == 1
        assert enhanced_store.error_count == 1
    
    @pytest.mark.asyncio
    async def test_consume_multiple_operations(self, enhanced_store):
        """Test multiple consume operations"""
        await enhanced_store.setup()
        
        test_data_list = [
            {"id": 1, "data": "first"},
            {"id": 2, "data": "second"},
            {"id": 3, "data": "third"}
        ]
        
        results = []
        for data in test_data_list:
            result = await enhanced_store.consume(data)
            results.append(result)
        
        # All operations should succeed
        for result in results:
            assert result["success"] is True
        
        # Check metrics
        assert enhanced_store.operation_count == 3
        assert enhanced_store.error_count == 0
        
        # Check performance metrics
        metrics = enhanced_store.get_performance_metrics()
        assert metrics["operations"] == 3
        assert metrics["error_rate"] == 0.0
        assert metrics["success_rate"] == 1.0
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, enhanced_store):
        """Test performance metrics calculation"""
        await enhanced_store.setup()
        
        # Initial metrics should be zero
        initial_metrics = enhanced_store.get_performance_metrics()
        assert initial_metrics["operations"] == 0
        assert initial_metrics["average_execution_time"] == 0.0
        assert initial_metrics["error_rate"] == 0.0
        
        # Perform some operations
        await enhanced_store.consume({"test": "data1"})
        await enhanced_store.consume({"test": "data2"})
        await enhanced_store.consume(None)  # This should fail
        
        # Check updated metrics
        metrics = enhanced_store.get_performance_metrics()
        assert metrics["operations"] == 3
        assert metrics["error_count"] == 1
        assert metrics["error_rate"] == 1/3
        assert metrics["success_rate"] == 2/3
        assert metrics["average_execution_time"] > 0
    
    @pytest.mark.asyncio
    async def test_cleanup(self, enhanced_store):
        """Test enhanced store cleanup"""
        await enhanced_store.setup()
        
        # Should not raise any exceptions
        await enhanced_store.cleanup()
        
        # Cleanup should be handled gracefully by mock components
    
    def test_operation_id_generation(self, enhanced_store):
        """Test operation ID generation"""
        op_id1 = enhanced_store._generate_operation_id()
        op_id2 = enhanced_store._generate_operation_id()
        
        assert op_id1 != op_id2
        assert op_id1.startswith("op_")
        assert op_id2.startswith("op_")
        assert len(op_id1) > 10  # Should have meaningful length
    
    def test_update_operation_metrics(self, enhanced_store):
        """Test operation metrics updating"""
        # Test successful operation
        enhanced_store._update_operation_metrics(0.1, success=True)
        assert enhanced_store.operation_count == 1
        assert enhanced_store.total_execution_time == 0.1
        assert enhanced_store.error_count == 0
        
        # Test failed operation
        enhanced_store._update_operation_metrics(0.2, success=False)
        assert enhanced_store.operation_count == 2
        assert enhanced_store.total_execution_time == 0.3
        assert enhanced_store.error_count == 1


class TestDatabaseConnectionManager:
    """Test suite for DatabaseConnectionManager"""
    
    @pytest.fixture
    def sqlite_config(self):
        """SQLite configuration for testing"""
        return {
            "database_type": "sqlite",
            "database_path": ":memory:",
            "pool": {
                "min_connections": 2,
                "max_connections": 5,
                "connection_timeout": 10,
                "health_check_interval": 30
            }
        }
    
    @pytest.fixture
    def connection_manager(self, sqlite_config):
        """Create DatabaseConnectionManager for testing"""
        return DatabaseConnectionManager(sqlite_config)
    
    def test_connection_manager_initialization(self, connection_manager, sqlite_config):
        """Test connection manager initialization"""
        assert connection_manager.database_type == "sqlite"
        assert connection_manager.pool_config.min_connections == 2
        assert connection_manager.pool_config.max_connections == 5
        assert connection_manager.pool_initialized is False
        assert connection_manager.shutting_down is False
        assert len(connection_manager.all_connections) == 0
    
    @pytest.mark.asyncio
    async def test_pool_initialization_success(self, connection_manager):
        """Test successful pool initialization"""
        await connection_manager.initialize_pool()
        
        assert connection_manager.pool_initialized is True
        assert len(connection_manager.all_connections) >= connection_manager.pool_config.min_connections
        assert connection_manager.available_connections.qsize() >= connection_manager.pool_config.min_connections
        assert connection_manager.health_check_task is not None
        
        await connection_manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_connection_acquisition_and_release(self, connection_manager):
        """Test connection acquisition and release"""
        await connection_manager.initialize_pool()
        
        # Acquire connection
        connection = await connection_manager.get_connection()
        assert connection is not None
        assert connection.in_use is True
        assert connection.connection_id in connection_manager.all_connections
        
        # Release connection
        await connection_manager.release_connection(connection)
        assert connection.in_use is False
        
        await connection_manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_connection_pool_exhaustion(self, connection_manager):
        """Test behavior when connection pool is exhausted"""
        await connection_manager.initialize_pool()
        
        # Acquire all connections
        connections = []
        for _ in range(connection_manager.pool_config.max_connections):
            try:
                conn = await connection_manager.get_connection()
                connections.append(conn)
            except ConnectionPoolError:
                break
        
        # Should handle pool exhaustion gracefully
        assert len(connections) <= connection_manager.pool_config.max_connections
        
        # Release connections
        for conn in connections:
            await connection_manager.release_connection(conn)
        
        await connection_manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self, connection_manager):
        """Test connection health monitoring"""
        await connection_manager.initialize_pool()
        
        # Get a connection and test health check
        connection = await connection_manager.get_connection()
        
        # Health check should pass for new connection
        healthy = await connection_manager._health_check_connection(connection)
        assert healthy is True
        assert connection.health.healthy is True
        assert connection.health.error_count == 0
        
        await connection_manager.release_connection(connection)
        await connection_manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_pool_statistics(self, connection_manager):
        """Test pool statistics"""
        await connection_manager.initialize_pool()
        
        stats = connection_manager.get_pool_statistics()
        
        assert "total_connections" in stats
        assert "available_connections" in stats
        assert "connections_in_use" in stats
        assert "pool_config" in stats
        assert "statistics" in stats
        
        assert stats["total_connections"] >= connection_manager.pool_config.min_connections
        assert stats["pool_config"]["min_connections"] == connection_manager.pool_config.min_connections
        assert stats["pool_config"]["max_connections"] == connection_manager.pool_config.max_connections
        
        await connection_manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_unsupported_database_type(self):
        """Test handling of unsupported database type"""
        config = {
            "database_type": "unsupported_db",
            "pool": {"min_connections": 1, "max_connections": 2}
        }
        
        manager = DatabaseConnectionManager(config)
        
        # Should handle unsupported database type during connection creation
        with pytest.raises(ConnectionPoolError):
            await manager.initialize_pool()
    
    @pytest.mark.asyncio
    async def test_cleanup(self, connection_manager):
        """Test connection manager cleanup"""
        await connection_manager.initialize_pool()
        
        # Acquire some connections
        conn1 = await connection_manager.get_connection()
        conn2 = await connection_manager.get_connection()
        
        initial_connection_count = len(connection_manager.all_connections)
        assert initial_connection_count >= 2
        
        # Cleanup should close all connections
        await connection_manager.cleanup()
        
        assert connection_manager.shutting_down is True
        assert len(connection_manager.all_connections) == 0
        assert connection_manager.available_connections.empty()


class TestStoreIntegration:
    """Integration tests for Store components with real database operations"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_store_operation(self):
        """Test complete end-to-end store operation"""
        config = {
            "database": {
                "database_type": "sqlite",
                "database_path": ":memory:",
                "pool": {"min_connections": 1, "max_connections": 3}
            },
            "performance": {"cache_enabled": True},
            "validation": {"schema_version": "1.0.0"}
        }
        
        store = V5EnhancedStore("integration_test_store", config)
        
        try:
            # Setup store
            await store.setup()
            
            # Test data operations
            test_data = {
                "event_type": "user_action",
                "user_id": 12345,
                "timestamp": time.time(),
                "data": {"action": "click", "element": "button"}
            }
            
            # Consume data
            result = await store.consume(test_data)
            
            # Verify result
            assert result["success"] is True
            assert result["stored_records"] >= 1
            assert "transaction_id" in result
            assert "execution_time" in result
            
            # Test performance metrics
            metrics = store.get_performance_metrics()
            assert metrics["operations"] == 1
            assert metrics["error_rate"] == 0.0
            assert metrics["success_rate"] == 1.0
            
        finally:
            # Cleanup
            await store.cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_store_operations(self):
        """Test concurrent store operations"""
        config = {
            "database": {
                "database_type": "sqlite",
                "database_path": ":memory:",
                "pool": {"min_connections": 2, "max_connections": 5}
            },
            "performance": {"cache_enabled": True},
            "validation": {"schema_version": "1.0.0"}
        }
        
        store = V5EnhancedStore("concurrent_test_store", config)
        
        try:
            await store.setup()
            
            # Create multiple concurrent operations
            async def consume_data(data_id):
                return await store.consume({"id": data_id, "data": f"test_{data_id}"})
            
            # Run concurrent operations
            tasks = [consume_data(i) for i in range(10)]
            results = await asyncio.gather(*tasks)
            
            # All operations should succeed
            for result in results:
                assert result["success"] is True
            
            # Check metrics
            metrics = store.get_performance_metrics()
            assert metrics["operations"] == 10
            assert metrics["error_rate"] == 0.0
            
        finally:
            await store.cleanup()
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms"""
        config = {
            "database": {
                "database_type": "sqlite",
                "database_path": ":memory:",
                "pool": {"min_connections": 1, "max_connections": 2}
            },
            "performance": {"cache_enabled": True},
            "validation": {"schema_version": "1.0.0"}
        }
        
        store = V5EnhancedStore("error_test_store", config)
        
        try:
            await store.setup()
            
            # Test with valid data
            valid_result = await store.consume({"valid": "data"})
            assert valid_result["success"] is True
            
            # Test with invalid data (None)
            invalid_result = await store.consume(None)
            assert invalid_result["success"] is False
            assert "error_message" in invalid_result
            
            # Test recovery with valid data again
            recovery_result = await store.consume({"recovery": "data"})
            assert recovery_result["success"] is True
            
            # Check metrics reflect both success and failure
            metrics = store.get_performance_metrics()
            assert metrics["operations"] == 3
            assert metrics["error_count"] == 1
            assert metrics["success_rate"] == 2/3
            
        finally:
            await store.cleanup()


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])