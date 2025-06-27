"""
V5.0 Store Implementation Tests
Functional tests for V5EnhancedStore implementation and database integration
"""

import pytest
import asyncio
import time
import tempfile
import os
from typing import Dict, Any, List

# Import components under test
import sys
sys.path.append('/home/brian/autocoder3_cc/evidence/phase5_database_integration/day1_enhanced_store_components')

from v5_enhanced_store import V5EnhancedStore, create_v5_enhanced_store
from database_connection_manager import DatabaseConnectionManager


class TestV5EnhancedStoreImplementation:
    """Functional tests for V5EnhancedStore implementation"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database file for testing"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
    
    @pytest.fixture
    def production_config(self, temp_db_path):
        """Production-like configuration for testing"""
        return {
            "database": {
                "database_type": "sqlite",
                "database_path": temp_db_path,
                "pool": {
                    "min_connections": 3,
                    "max_connections": 10,
                    "connection_timeout": 30,
                    "health_check_interval": 60,
                    "max_idle_time": 300
                }
            },
            "performance": {
                "cache_enabled": True,
                "optimization_level": "aggressive",
                "batch_size": 100
            },
            "validation": {
                "schema_version": "2.0.0",
                "strict_validation": True,
                "migration_enabled": True
            }
        }
    
    @pytest.mark.asyncio
    async def test_store_factory_creation(self, production_config):
        """Test store creation via factory function"""
        store = create_v5_enhanced_store("factory_test_store", production_config)
        
        assert isinstance(store, V5EnhancedStore)
        assert store.name == "factory_test_store"
        assert store.config == production_config
        
        await store.setup()
        
        # Test basic functionality
        result = await store.consume({"test": "factory_data"})
        assert result["success"] is True
        
        await store.cleanup()
    
    @pytest.mark.asyncio
    async def test_production_like_workload(self, production_config):
        """Test store with production-like workload"""
        store = V5EnhancedStore("production_test", production_config)
        
        try:
            await store.setup()
            
            # Simulate production workload
            operations = []
            for i in range(100):
                operation = store.consume({
                    "event_id": f"evt_{i}",
                    "timestamp": time.time(),
                    "user_id": f"user_{i % 10}",
                    "action": "page_view",
                    "metadata": {
                        "page": f"/page_{i % 5}",
                        "session_id": f"session_{i % 20}",
                        "ip_address": f"192.168.1.{i % 255}"
                    }
                })
                operations.append(operation)
            
            # Execute all operations
            results = await asyncio.gather(*operations)
            
            # Verify all operations succeeded
            success_count = sum(1 for r in results if r["success"])
            assert success_count == 100
            
            # Check performance metrics
            metrics = store.get_performance_metrics()
            assert metrics["operations"] == 100
            assert metrics["error_rate"] == 0.0
            assert metrics["average_execution_time"] > 0
            
            print(f"✅ Production workload test completed:")
            print(f"   Operations: {metrics['operations']}")
            print(f"   Success rate: {metrics['success_rate']:.2%}")
            print(f"   Average execution time: {metrics['average_execution_time']:.4f}s")
            
        finally:
            await store.cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_high_load(self, production_config):
        """Test store under concurrent high load"""
        store = V5EnhancedStore("high_load_test", production_config)
        
        try:
            await store.setup()
            
            # Create high concurrent load
            async def worker(worker_id: int, operation_count: int):
                results = []
                for i in range(operation_count):
                    result = await store.consume({
                        "worker_id": worker_id,
                        "operation_id": i,
                        "timestamp": time.time(),
                        "data": f"worker_{worker_id}_op_{i}"
                    })
                    results.append(result)
                return results
            
            # Run 10 workers with 20 operations each
            worker_count = 10
            operations_per_worker = 20
            
            start_time = time.time()
            worker_tasks = [
                worker(worker_id, operations_per_worker) 
                for worker_id in range(worker_count)
            ]
            
            all_results = await asyncio.gather(*worker_tasks)
            total_time = time.time() - start_time
            
            # Flatten results
            flat_results = [result for worker_results in all_results for result in worker_results]
            
            # Verify results
            total_operations = worker_count * operations_per_worker
            success_count = sum(1 for r in flat_results if r["success"])
            
            assert len(flat_results) == total_operations
            assert success_count == total_operations
            
            # Check performance metrics
            metrics = store.get_performance_metrics()
            throughput = total_operations / total_time
            
            print(f"✅ High load test completed:")
            print(f"   Total operations: {total_operations}")
            print(f"   Success rate: {success_count / total_operations:.2%}")
            print(f"   Total time: {total_time:.2f}s")
            print(f"   Throughput: {throughput:.2f} ops/sec")
            print(f"   Average execution time: {metrics['average_execution_time']:.4f}s")
            
            # Performance assertions
            assert throughput > 50  # Should handle at least 50 ops/sec
            assert metrics["error_rate"] == 0.0
            
        finally:
            await store.cleanup()
    
    @pytest.mark.asyncio
    async def test_data_validation_scenarios(self, production_config):
        """Test various data validation scenarios"""
        store = V5EnhancedStore("validation_test", production_config)
        
        try:
            await store.setup()
            
            # Test valid data formats
            valid_test_cases = [
                {"simple": "string"},
                {"number": 42},
                {"nested": {"key": "value", "count": 123}},
                {"array": [1, 2, 3, "four"]},
                {"complex": {
                    "user": {"id": 123, "name": "test"},
                    "events": [{"type": "click", "timestamp": time.time()}],
                    "metadata": {"version": "1.0", "source": "test"}
                }}
            ]
            
            valid_results = []
            for i, test_data in enumerate(valid_test_cases):
                result = await store.consume(test_data)
                valid_results.append(result)
                print(f"   Test case {i+1}: {'✅' if result['success'] else '❌'}")
            
            # All valid cases should succeed
            valid_success_count = sum(1 for r in valid_results if r["success"])
            assert valid_success_count == len(valid_test_cases)
            
            # Test invalid data formats
            invalid_test_cases = [
                None,
                "",  # Empty string might be invalid depending on schema
            ]
            
            invalid_results = []
            for i, test_data in enumerate(invalid_test_cases):
                result = await store.consume(test_data)
                invalid_results.append(result)
                print(f"   Invalid case {i+1}: {'❌' if not result['success'] else '⚠️'}")
            
            # Check that at least None is handled as invalid
            none_result = invalid_results[0]
            assert none_result["success"] is False
            
            print(f"✅ Data validation test completed:")
            print(f"   Valid cases passed: {valid_success_count}/{len(valid_test_cases)}")
            print(f"   Invalid cases handled: {sum(1 for r in invalid_results if not r['success'])}/{len(invalid_test_cases)}")
            
        finally:
            await store.cleanup()
    
    @pytest.mark.asyncio
    async def test_error_recovery_and_resilience(self, production_config):
        """Test error recovery and system resilience"""
        store = V5EnhancedStore("resilience_test", production_config)
        
        try:
            await store.setup()
            
            # Test normal operation
            result1 = await store.consume({"test": "normal_operation"})
            assert result1["success"] is True
            
            # Simulate error condition
            result2 = await store.consume(None)  # Should fail
            assert result2["success"] is False
            
            # Test recovery after error
            result3 = await store.consume({"test": "recovery_operation"})
            assert result3["success"] is True
            
            # Simulate multiple errors
            error_results = []
            for i in range(5):
                error_result = await store.consume(None)
                error_results.append(error_result)
            
            # All error cases should be handled gracefully
            for error_result in error_results:
                assert error_result["success"] is False
                assert "error_message" in error_result
            
            # Test recovery after multiple errors
            recovery_results = []
            for i in range(3):
                recovery_result = await store.consume({"recovery": f"test_{i}"})
                recovery_results.append(recovery_result)
            
            # All recovery operations should succeed
            for recovery_result in recovery_results:
                assert recovery_result["success"] is True
            
            # Check final metrics
            metrics = store.get_performance_metrics()
            total_ops = 1 + 1 + 1 + 5 + 3  # normal + error + recovery + errors + recoveries
            expected_errors = 1 + 5  # first error + 5 simulated errors
            
            assert metrics["operations"] == total_ops
            assert metrics["error_count"] == expected_errors
            assert metrics["success_rate"] == (total_ops - expected_errors) / total_ops
            
            print(f"✅ Error recovery test completed:")
            print(f"   Total operations: {metrics['operations']}")
            print(f"   Error count: {metrics['error_count']}")
            print(f"   Success rate: {metrics['success_rate']:.2%}")
            print(f"   System remained resilient through {expected_errors} errors")
            
        finally:
            await store.cleanup()
    
    @pytest.mark.asyncio
    async def test_performance_optimization_features(self, production_config):
        """Test performance optimization features"""
        store = V5EnhancedStore("performance_test", production_config)
        
        try:
            await store.setup()
            
            # Test operations with performance monitoring
            baseline_data = []
            optimization_data = []
            
            # Baseline operations
            for i in range(50):
                start_time = time.time()
                result = await store.consume({"baseline": f"operation_{i}"})
                execution_time = time.time() - start_time
                
                baseline_data.append({
                    "success": result["success"],
                    "execution_time": execution_time
                })
            
            # Get metrics after baseline
            baseline_metrics = store.get_performance_metrics()
            
            # Performance optimized operations (simulated)
            for i in range(50):
                start_time = time.time()
                result = await store.consume({
                    "optimized": f"operation_{i}",
                    "cache_hint": True,
                    "batch_eligible": True
                })
                execution_time = time.time() - start_time
                
                optimization_data.append({
                    "success": result["success"],
                    "execution_time": execution_time
                })
            
            # Final metrics
            final_metrics = store.get_performance_metrics()
            
            # Calculate performance statistics
            baseline_avg = sum(op["execution_time"] for op in baseline_data) / len(baseline_data)
            optimized_avg = sum(op["execution_time"] for op in optimization_data) / len(optimization_data)
            
            print(f"✅ Performance optimization test completed:")
            print(f"   Baseline average: {baseline_avg:.4f}s")
            print(f"   Optimized average: {optimized_avg:.4f}s")
            print(f"   Overall average: {final_metrics['average_execution_time']:.4f}s")
            print(f"   Total operations: {final_metrics['operations']}")
            print(f"   Success rate: {final_metrics['success_rate']:.2%}")
            
            # Verify all operations succeeded
            assert final_metrics["error_rate"] == 0.0
            assert final_metrics["operations"] == 100
            
        finally:
            await store.cleanup()
    
    @pytest.mark.asyncio
    async def test_connection_pool_behavior(self, production_config):
        """Test connection pool behavior under various scenarios"""
        store = V5EnhancedStore("pool_test", production_config)
        
        try:
            await store.setup()
            
            # Get connection manager for direct testing
            connection_manager = store.connection_manager
            
            # Test initial pool state
            initial_stats = connection_manager.get_pool_statistics()
            print(f"✅ Initial pool state:")
            print(f"   Total connections: {initial_stats['total_connections']}")
            print(f"   Available connections: {initial_stats['available_connections']}")
            
            # Test concurrent connection usage
            async def use_connection_briefly():
                result = await store.consume({"pool_test": time.time()})
                return result["success"]
            
            # Create concurrent load on connection pool
            tasks = [use_connection_briefly() for _ in range(20)]
            results = await asyncio.gather(*tasks)
            
            # All operations should succeed
            assert all(results)
            
            # Check pool statistics after load
            final_stats = connection_manager.get_pool_statistics()
            print(f"✅ Pool state after load:")
            print(f"   Total connections: {final_stats['total_connections']}")
            print(f"   Available connections: {final_stats['available_connections']}")
            print(f"   Connections in use: {final_stats['connections_in_use']}")
            
            # Pool should be within configured limits
            assert final_stats['total_connections'] <= production_config["database"]["pool"]["max_connections"]
            assert final_stats['total_connections'] >= production_config["database"]["pool"]["min_connections"]
            
        finally:
            await store.cleanup()


class TestStoreSystemIntegration:
    """System integration tests for Store components"""
    
    @pytest.mark.asyncio
    async def test_multiple_store_instances(self):
        """Test multiple store instances working together"""
        config = {
            "database": {
                "database_type": "sqlite",
                "database_path": ":memory:",
                "pool": {"min_connections": 2, "max_connections": 8}
            },
            "performance": {"cache_enabled": True},
            "validation": {"schema_version": "1.0.0"}
        }
        
        # Create multiple stores
        stores = [
            V5EnhancedStore(f"store_{i}", config)
            for i in range(3)
        ]
        
        try:
            # Setup all stores
            for store in stores:
                await store.setup()
            
            # Test concurrent operations across all stores
            async def store_operation(store, operation_id):
                return await store.consume({
                    "store_name": store.name,
                    "operation_id": operation_id,
                    "timestamp": time.time()
                })
            
            # Create operations for all stores
            all_operations = []
            for i, store in enumerate(stores):
                for j in range(10):
                    all_operations.append(store_operation(store, f"{i}_{j}"))
            
            # Execute all operations concurrently
            results = await asyncio.gather(*all_operations)
            
            # All operations should succeed
            success_count = sum(1 for r in results if r["success"])
            assert success_count == len(all_operations)
            
            # Check metrics for each store
            for i, store in enumerate(stores):
                metrics = store.get_performance_metrics()
                assert metrics["operations"] == 10  # Each store should have 10 operations
                assert metrics["error_rate"] == 0.0
                
                print(f"✅ Store {i} metrics:")
                print(f"   Operations: {metrics['operations']}")
                print(f"   Success rate: {metrics['success_rate']:.2%}")
                print(f"   Average time: {metrics['average_execution_time']:.4f}s")
            
        finally:
            # Cleanup all stores
            for store in stores:
                await store.cleanup()
    
    @pytest.mark.asyncio
    async def test_system_stress_test(self):
        """Comprehensive system stress test"""
        config = {
            "database": {
                "database_type": "sqlite",
                "database_path": ":memory:",
                "pool": {"min_connections": 5, "max_connections": 15}
            },
            "performance": {"cache_enabled": True, "optimization_level": "aggressive"},
            "validation": {"schema_version": "1.0.0", "strict_validation": True}
        }
        
        store = V5EnhancedStore("stress_test_store", config)
        
        try:
            await store.setup()
            
            # Stress test parameters
            total_operations = 500
            concurrent_workers = 25
            operations_per_worker = total_operations // concurrent_workers
            
            async def stress_worker(worker_id: int):
                worker_results = []
                for i in range(operations_per_worker):
                    try:
                        result = await store.consume({
                            "worker_id": worker_id,
                            "operation_index": i,
                            "timestamp": time.time(),
                            "payload": {
                                "data": f"stress_test_data_{worker_id}_{i}",
                                "size": "medium",
                                "priority": i % 3,
                                "metadata": {
                                    "source": "stress_test",
                                    "batch_id": f"batch_{worker_id}",
                                    "sequence": i
                                }
                            }
                        })
                        worker_results.append(result)
                    except Exception as e:
                        worker_results.append({"success": False, "error": str(e)})
                
                return worker_results
            
            # Execute stress test
            print(f"🔥 Starting stress test:")
            print(f"   Workers: {concurrent_workers}")
            print(f"   Operations per worker: {operations_per_worker}")
            print(f"   Total operations: {total_operations}")
            
            start_time = time.time()
            worker_tasks = [stress_worker(i) for i in range(concurrent_workers)]
            all_worker_results = await asyncio.gather(*worker_tasks)
            total_time = time.time() - start_time
            
            # Analyze results
            flat_results = [result for worker_results in all_worker_results for result in worker_results]
            success_count = sum(1 for r in flat_results if r.get("success", False))
            
            # Calculate performance metrics
            throughput = len(flat_results) / total_time
            success_rate = success_count / len(flat_results)
            
            print(f"✅ Stress test completed:")
            print(f"   Total operations: {len(flat_results)}")
            print(f"   Successful operations: {success_count}")
            print(f"   Success rate: {success_rate:.2%}")
            print(f"   Total time: {total_time:.2f}s")
            print(f"   Throughput: {throughput:.2f} ops/sec")
            
            # Get store metrics
            store_metrics = store.get_performance_metrics()
            print(f"   Store average execution time: {store_metrics['average_execution_time']:.4f}s")
            print(f"   Store error rate: {store_metrics['error_rate']:.2%}")
            
            # Performance assertions
            assert success_rate >= 0.95  # At least 95% success rate
            assert throughput >= 30  # At least 30 operations per second
            assert store_metrics["error_rate"] <= 0.05  # At most 5% error rate
            
        finally:
            await store.cleanup()


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v", "-s"])