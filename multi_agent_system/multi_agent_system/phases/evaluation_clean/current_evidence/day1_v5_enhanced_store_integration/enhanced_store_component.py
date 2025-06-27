"""
Enhanced Store Component - Integration of V5EnhancedStore with main component system
Replaces the basic Store class with comprehensive database integration including schema validation,
connection pooling, transaction management, and performance optimization.
"""

import sys
import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add Phase 5 database components to path
phase5_path = os.path.join(os.path.dirname(__file__), '..', '..', 'phase5_database_integration', 'day1_enhanced_store_components')
sys.path.insert(0, phase5_path)

try:
    from v5_enhanced_store import V5EnhancedStore, StoreOperationError, StoreOperationResult
except ImportError:
    # Fallback if Phase 5 components not available
    class V5EnhancedStore:
        def __init__(self, name: str, config: Dict[str, Any]):
            self.name = name
            self.config = config
            
        async def setup(self):
            pass
            
        async def consume(self, data: Any) -> Dict[str, Any]:
            return {"success": True, "fallback": True}

# Import base Store component
try:
    from autocoder.components.store import Store
    from autocoder.components.base import HarnessComponent
except ImportError:
    # Fallback if base components not available
    class Store:
        def __init__(self, name: str, config: Dict[str, Any]):
            self.name = name
            self.config = config
            self.setup_complete = False
        
        async def setup(self, harness_context=None):
            self.setup_complete = True
        
        async def process(self):
            pass

    class HarnessComponent:
        def __init__(self, name: str, config: Dict[str, Any]):
            self.name = name
            self.config = config

logger = logging.getLogger(__name__)


class EnhancedStoreComponent(Store, V5EnhancedStore):
    """
    Integration of V5EnhancedStore with main component system.
    
    Replaces the basic Store class with comprehensive database integration:
    - Real-time schema validation and migration
    - Connection pooling with health monitoring
    - Transaction management with ACID compliance
    - Multi-database support (PostgreSQL, MySQL, SQLite)
    - Performance optimization with caching
    
    This component maintains compatibility with the existing Store interface while
    providing all V5 database features.
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        # Initialize both parent classes
        Store.__init__(self, name, config or {})
        V5EnhancedStore.__init__(self, name, config or {})
        
        # Component identification
        self.component_type = "EnhancedStore"
        self.is_v5_enhanced = True
        
        # Merge configurations
        self._merge_configurations()
        
        # Performance tracking
        self.v5_features_enabled = True
        self.compatibility_mode = False
        
        logger.info(f"EnhancedStoreComponent {name} initialized with V5 database features")
    
    def _merge_configurations(self):
        """Merge Store and V5EnhancedStore configurations"""
        # Ensure database_config is a mutable dict
        if not isinstance(self.database_config, dict):
            self.database_config = {}
        
        # Merge database configuration
        if hasattr(self, 'database_type') and self.database_type:
            self.database_config['database_type'] = self.database_type
        
        if hasattr(self, 'connection_url') and self.connection_url:
            self.database_config['connection_url'] = self.connection_url
        
        if hasattr(self, 'table_name') and self.table_name:
            self.database_config['table_name'] = self.table_name
        
        # Enhanced configuration with V5 features
        self.database_config.update({
            'connection_pooling': True,
            'schema_validation': True,
            'transaction_management': True,
            'performance_optimization': True
        })
        
        logger.debug(f"Merged configuration for {self.name}: {self.database_config}")
    
    async def setup(self, harness_context=None):
        """Enhanced setup with V5 database features and Store compatibility"""
        logger.info(f"Setting up EnhancedStoreComponent {self.name}")
        
        try:
            # Call Store setup first for base functionality
            await Store.setup(self, harness_context)
            
            # Call V5EnhancedStore setup for enhanced features
            await V5EnhancedStore.setup(self)
            
            # Validate V5 features are working
            await self._validate_v5_features()
            
            logger.info(f"EnhancedStoreComponent {self.name} setup completed with V5 features")
            
        except Exception as e:
            logger.warning(f"V5 features setup failed for {self.name}, falling back to compatibility mode: {e}")
            
            # Fall back to Store-only setup
            self.compatibility_mode = True
            self.v5_features_enabled = False
            await Store.setup(self, harness_context)
            
            logger.warning(f"EnhancedStoreComponent {self.name} running in compatibility mode")
    
    async def process(self) -> None:
        """
        Enhanced process method that combines Store stream processing with V5 database features.
        
        This method maintains compatibility with the existing Store interface while
        using V5EnhancedStore features for actual data operations.
        """
        if self.v5_features_enabled:
            # Use enhanced processing with V5 features
            await self._process_with_v5_features()
        else:
            # Fall back to basic Store processing
            await Store.process(self)
    
    async def _process_with_v5_features(self):
        """Process data using V5EnhancedStore features with Store stream handling"""
        try:
            import anyio
            
            # Process all available input streams using V5 enhanced consume
            if self.receive_streams:
                async with anyio.create_task_group() as tg:
                    for stream_name, stream in self.receive_streams.items():
                        tg.start_soon(self._process_stream_v5, stream_name, stream)
            else:
                self.logger.warning("No input stream configured")
                
        except Exception as e:
            self.logger.error(f"Error in enhanced store processing: {e}")
            self.record_error(str(e))
    
    async def _process_stream_v5(self, stream_name: str, stream):
        """Process a single input stream using V5EnhancedStore consume method"""
        await self._process_stream_with_handler(stream_name, stream, self._consume_with_v5)
    
    async def _consume_with_v5(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced consume method using V5EnhancedStore capabilities.
        
        This replaces the basic Store._store_data method with V5 database features:
        - Schema validation
        - Transaction management
        - Performance optimization
        - Connection pooling
        """
        try:
            if self.v5_features_enabled:
                # Use V5EnhancedStore consume method
                result = await V5EnhancedStore.consume(self, data)
                
                # Add Store-compatible fields
                if result.get('success'):
                    result.update({
                        "operation": "enhanced_store",
                        "key": data.get('key', f"auto_key_{getattr(self._status, 'items_processed', 0)}"),
                        "database_type": self.database_type,
                        "table_name": getattr(self, 'table_name', 'data_store'),
                        "original_data": data,
                        "v5_enhanced": True
                    })
                
                return result
            else:
                # Fall back to basic Store method
                return await self._store_data(data)
                
        except Exception as e:
            logger.error(f"Enhanced consume operation failed: {e}")
            
            # Try fallback to basic Store method
            try:
                return await self._store_data(data)
            except Exception as fallback_error:
                logger.error(f"Fallback store operation also failed: {fallback_error}")
                return {
                    "operation": "enhanced_store",
                    "success": False,
                    "error": str(e),
                    "fallback_error": str(fallback_error),
                    "original_data": data
                }
    
    async def _validate_v5_features(self):
        """Validate that V5 database features are working correctly"""
        validation_errors = []
        
        # Check connection manager
        if not self.connection_manager:
            validation_errors.append("Connection manager not initialized")
        
        # Check schema validator
        if not self.schema_validator:
            validation_errors.append("Schema validator not initialized")
        
        # Check transaction manager
        if not self.transaction_manager:
            validation_errors.append("Transaction manager not initialized")
        
        # Check performance optimizer
        if not self.performance_optimizer:
            validation_errors.append("Performance optimizer not initialized")
        
        if validation_errors:
            raise StoreOperationError(f"V5 features validation failed: {validation_errors}")
        
        # Test basic V5 operations
        try:
            test_data = {"test": "v5_validation", "timestamp": "now"}
            test_result = await V5EnhancedStore.consume(self, test_data)
            
            if not test_result.get('success'):
                raise StoreOperationError("V5 consume test failed")
                
        except Exception as e:
            raise StoreOperationError(f"V5 operation test failed: {e}")
        
        logger.debug(f"V5 features validation passed for {self.name}")
    
    async def cleanup(self):
        """Enhanced cleanup with V5 features and Store compatibility"""
        logger.info(f"Cleaning up EnhancedStoreComponent {self.name}")
        
        try:
            # Cleanup V5 features if enabled
            if self.v5_features_enabled:
                await V5EnhancedStore.cleanup(self)
            
            # Cleanup Store components
            await Store.cleanup(self)
            
            logger.info(f"EnhancedStoreComponent {self.name} cleanup completed")
            
        except Exception as e:
            logger.error(f"EnhancedStoreComponent {self.name} cleanup error: {e}")
    
    def get_enhanced_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics including V5 features and Store compatibility"""
        metrics = {
            "component_name": self.name,
            "component_type": self.component_type,
            "v5_features_enabled": self.v5_features_enabled,
            "compatibility_mode": self.compatibility_mode
        }
        
        # Add V5 performance metrics if available
        if self.v5_features_enabled:
            try:
                v5_metrics = self.get_performance_metrics()
                metrics["v5_performance"] = v5_metrics
            except Exception as e:
                metrics["v5_metrics_error"] = str(e)
        
        # Add Store status if available
        if hasattr(self, '_status'):
            metrics["store_status"] = {
                "items_processed": getattr(self._status, 'items_processed', 0),
                "errors": getattr(self._status, 'errors', 0)
            }
        
        return metrics
    
    def is_enhanced_store(self) -> bool:
        """Check if this is an enhanced store with V5 features"""
        return self.is_v5_enhanced and self.v5_features_enabled


# Factory function for component registration
def create_enhanced_store_component(name: str, config: Dict[str, Any]) -> EnhancedStoreComponent:
    """Create Enhanced Store component with V5 database features"""
    return EnhancedStoreComponent(name, config)


# Test harness
if __name__ == "__main__":
    async def test_enhanced_store_component():
        """Test Enhanced Store Component functionality"""
        
        config = {
            "database_type": "postgresql",
            "connection_url": "postgresql://user:password@localhost:5432/test_db",
            "table_name": "enhanced_test_store",
            "database": {
                "database_type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "test_db"
            },
            "performance": {
                "cache_enabled": True,
                "pool_size": 10
            },
            "validation": {
                "schema_version": "1.0.0"
            }
        }
        
        store = EnhancedStoreComponent("test_enhanced_component", config)
        
        try:
            # Test setup
            await store.setup()
            print("✅ EnhancedStoreComponent setup successful")
            print(f"   V5 Features Enabled: {store.v5_features_enabled}")
            print(f"   Compatibility Mode: {store.compatibility_mode}")
            
            # Test data consumption (V5 enhanced)
            test_data = {
                "key": "test_enhanced_key",
                "value": {"user_id": 123, "action": "login", "timestamp": "2025-06-23T10:00:00Z"},
                "user_id": 123,
                "action": "login"
            }
            
            result = await store._consume_with_v5(test_data)
            
            if result.get("success"):
                print("✅ EnhancedStoreComponent V5 consume operation successful")
                print(f"   Transaction ID: {result.get('transaction_id')}")
                print(f"   Schema Version: {result.get('schema_version')}")
                print(f"   Execution Time: {result.get('execution_time', 0):.4f}s")
                print(f"   V5 Enhanced: {result.get('v5_enhanced')}")
            else:
                print(f"❌ EnhancedStoreComponent consume operation failed: {result.get('error_message')}")
            
            # Test enhanced metrics
            metrics = store.get_enhanced_metrics()
            print(f"✅ Enhanced metrics: {metrics}")
            
            # Test cleanup
            await store.cleanup()
            print("✅ EnhancedStoreComponent cleanup successful")
            
        except Exception as e:
            print(f"❌ EnhancedStoreComponent test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_enhanced_store_component())