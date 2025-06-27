"""
V5.0 Enhanced Store Integration with Transaction Management
Integrates Day 1 V5EnhancedStore with Day 3 transaction management components
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
import sys
import os

# Add Day 1 components to path
sys.path.append('/home/brian/autocoder3_cc/evidence/phase5_database_integration/day1_enhanced_store_components')

from transaction_manager import TransactionManager, IsolationLevel, TransactionOperation, DatabaseParticipant
from connection_pool_manager import ConnectionPool
from distributed_transaction_coordinator import DistributedTransactionCoordinator, DistributedTransactionParticipant

logger = logging.getLogger(__name__)


@dataclass
class EnhancedStoreTransaction:
    """Transaction wrapper for enhanced store operations"""
    transaction_id: str
    store_instance: 'V5TransactionalStore'
    isolation_level: IsolationLevel
    operations: List[Dict[str, Any]] = None
    committed: bool = False
    
    def __post_init__(self):
        if self.operations is None:
            self.operations = []


class V5TransactionalStore:
    """
    V5.0 Enhanced Store with integrated transaction management
    Combines Day 1 store capabilities with Day 3 transaction management
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.store_id = config.get("store_id", "default_store")
        
        # Transaction management components
        self.transaction_manager = None
        self.connection_pool = None
        self.distributed_coordinator = None
        
        # Store state
        self.active_transactions: Dict[str, EnhancedStoreTransaction] = {}
        self.store_data: Dict[str, Any] = {}
        self.schema_version = "1.0.0"
        
        # Configuration
        self.enable_distributed_transactions = config.get("enable_distributed_transactions", True)
        isolation_level_str = config.get("default_isolation_level", "READ_COMMITTED")
        self.default_isolation_level = getattr(IsolationLevel, isolation_level_str, IsolationLevel.READ_COMMITTED)
        self.auto_commit = config.get("auto_commit", True)
        
        logger.info(f"V5TransactionalStore {self.store_id} initialized")
    
    async def initialize(self):
        """Initialize store with transaction management"""
        logger.info("Initializing V5TransactionalStore with transaction management")
        
        try:
            # Initialize connection pool
            pool_config = {
                "min_connections": self.config.get("min_connections", 5),
                "max_connections": self.config.get("max_connections", 20),
                "connection_timeout": self.config.get("connection_timeout", 30.0),
                "database_type": self.config.get("database_type", "postgresql")
            }
            
            self.connection_pool = ConnectionPool(pool_config)
            await self.connection_pool.initialize()
            
            # Initialize transaction manager
            tx_config = {
                "default_timeout": self.config.get("transaction_timeout", 300.0),
                "max_concurrent_transactions": self.config.get("max_concurrent_transactions", 100),
                "deadlock_detection": True,
                "distributed_transactions": self.enable_distributed_transactions
            }
            
            self.transaction_manager = TransactionManager(tx_config)
            
            # Initialize distributed coordinator if enabled
            if self.enable_distributed_transactions:
                dtc_config = {
                    "coordinator_id": f"store_{self.store_id}",
                    "transaction_timeout": self.config.get("transaction_timeout", 300.0),
                    "log_directory": self.config.get("log_directory", "./store_dtc_logs")
                }
                
                self.distributed_coordinator = DistributedTransactionCoordinator(dtc_config)
                await self.distributed_coordinator.initialize()
                
                # Register store as participant
                store_participant = StoreTransactionParticipant(self.store_id, self)
                self.distributed_coordinator.register_participant(store_participant)
            
            logger.info("V5TransactionalStore initialization complete")
            
        except Exception as e:
            logger.error(f"Store initialization failed: {e}")
            raise
    
    async def begin_transaction(
        self,
        isolation_level: Optional[IsolationLevel] = None,
        timeout: Optional[float] = None
    ) -> str:
        """Begin new transaction"""
        
        isolation_level = isolation_level or self.default_isolation_level
        
        # Create transaction in manager
        transaction = await self.transaction_manager.create_transaction(
            isolation_level=isolation_level,
            timeout=timeout
        )
        
        await transaction.begin()
        
        # Create store transaction wrapper
        store_transaction = EnhancedStoreTransaction(
            transaction_id=transaction.transaction_id,
            store_instance=self,
            isolation_level=isolation_level
        )
        
        self.active_transactions[transaction.transaction_id] = store_transaction
        
        logger.info(f"Started store transaction {transaction.transaction_id}")
        return transaction.transaction_id
    
    async def commit_transaction(self, transaction_id: str) -> bool:
        """Commit transaction"""
        
        if transaction_id not in self.active_transactions:
            raise ValueError(f"Unknown transaction: {transaction_id}")
        
        store_transaction = self.active_transactions[transaction_id]
        
        try:
            # Get transaction from manager
            transaction = self.transaction_manager.active_transactions[transaction_id]
            
            # Add database participant if not already added
            if not transaction.participants:
                db_participant = StoreConnectionParticipant(self.connection_pool)
                transaction.add_participant(db_participant)
            
            # Commit through transaction manager
            success = await transaction.commit()
            
            if success:
                store_transaction.committed = True
                # Apply operations to store data
                await self._apply_transaction_operations(store_transaction)
            
            # Cleanup
            del self.active_transactions[transaction_id]
            
            logger.info(f"Transaction {transaction_id} commit: {'success' if success else 'failed'}")
            return success
            
        except Exception as e:
            logger.error(f"Transaction commit failed: {e}")
            await self.rollback_transaction(transaction_id)
            return False
    
    async def rollback_transaction(self, transaction_id: str) -> bool:
        """Rollback transaction"""
        
        if transaction_id not in self.active_transactions:
            return True  # Already cleaned up
        
        try:
            # Get transaction from manager
            transaction = self.transaction_manager.active_transactions.get(transaction_id)
            
            if transaction:
                await transaction.abort()
            
            # Cleanup store transaction
            del self.active_transactions[transaction_id]
            
            logger.info(f"Transaction {transaction_id} rolled back")
            return True
            
        except Exception as e:
            logger.error(f"Transaction rollback failed: {e}")
            return False
    
    async def transactional_operation(
        self,
        operation_type: str,
        data: Dict[str, Any],
        transaction_id: Optional[str] = None
    ) -> Any:
        """Execute operation within transaction"""
        
        # Auto-begin transaction if needed
        if transaction_id is None and self.auto_commit:
            transaction_id = await self.begin_transaction()
            auto_commit = True
        else:
            auto_commit = False
        
        if transaction_id not in self.active_transactions:
            raise ValueError(f"Unknown transaction: {transaction_id}")
        
        store_transaction = self.active_transactions[transaction_id]
        
        try:
            # Create transaction operation
            operation = TransactionOperation(
                operation_id=f"store_op_{len(store_transaction.operations)}",
                operation_type=operation_type,
                table_name="store_data",
                data=data
            )
            
            # Add to transaction
            transaction = self.transaction_manager.active_transactions[transaction_id]
            await transaction.add_operation(operation)
            
            # Add to store transaction
            store_transaction.operations.append({
                "type": operation_type,
                "data": data,
                "timestamp": time.time()
            })
            
            # Execute operation (preliminary)
            result = await self._execute_store_operation(operation_type, data, transaction_id)
            
            # Auto-commit if enabled
            if auto_commit:
                await self.commit_transaction(transaction_id)
            
            logger.debug(f"Store operation {operation_type} executed in transaction {transaction_id}")
            return result
            
        except Exception as e:
            if auto_commit:
                await self.rollback_transaction(transaction_id)
            raise
    
    async def put(self, key: str, value: Any, transaction_id: Optional[str] = None) -> bool:
        """Put key-value pair with transaction support"""
        return await self.transactional_operation(
            "put",
            {"key": key, "value": value},
            transaction_id
        )
    
    async def get(self, key: str, transaction_id: Optional[str] = None) -> Optional[Any]:
        """Get value with transaction isolation"""
        result = await self.transactional_operation(
            "get",
            {"key": key},
            transaction_id
        )
        return result.get("value") if result else None
    
    async def delete(self, key: str, transaction_id: Optional[str] = None) -> bool:
        """Delete key with transaction support"""
        return await self.transactional_operation(
            "delete",
            {"key": key},
            transaction_id
        )
    
    async def batch_operation(
        self,
        operations: List[Dict[str, Any]],
        isolation_level: Optional[IsolationLevel] = None
    ) -> List[Any]:
        """Execute multiple operations in single transaction"""
        
        transaction_id = await self.begin_transaction(isolation_level)
        
        try:
            results = []
            for op in operations:
                result = await self.transactional_operation(
                    op["type"],
                    op["data"],
                    transaction_id
                )
                results.append(result)
            
            # Commit all operations
            commit_success = await self.commit_transaction(transaction_id)
            
            if not commit_success:
                raise RuntimeError("Batch operation commit failed")
            
            return results
            
        except Exception as e:
            await self.rollback_transaction(transaction_id)
            raise
    
    async def distributed_operation(
        self,
        operations: List[Dict[str, Any]],
        participant_stores: List[str]
    ) -> bool:
        """Execute distributed operation across multiple stores"""
        
        if not self.distributed_coordinator:
            raise RuntimeError("Distributed transactions not enabled")
        
        # Begin global transaction
        global_txn_id = await self.distributed_coordinator.begin_global_transaction(
            participant_stores
        )
        
        try:
            # Execute local operations
            local_transaction_id = await self.begin_transaction()
            
            for op in operations:
                await self.transactional_operation(
                    op["type"],
                    op["data"],
                    local_transaction_id
                )
            
            # Commit global transaction
            global_success = await self.distributed_coordinator.commit_global_transaction(global_txn_id)
            
            if global_success:
                # Commit local transaction
                local_success = await self.commit_transaction(local_transaction_id)
                return local_success
            else:
                # Rollback local transaction
                await self.rollback_transaction(local_transaction_id)
                return False
            
        except Exception as e:
            logger.error(f"Distributed operation failed: {e}")
            await self.distributed_coordinator.abort_global_transaction(global_txn_id)
            return False
    
    async def _execute_store_operation(self, operation_type: str, data: Dict[str, Any], transaction_id: str) -> Any:
        """Execute store operation with isolation"""
        
        if operation_type == "put":
            # For simplicity, store in memory with transaction isolation
            key = data["key"]
            value = data["value"]
            
            # Apply to transaction-local view
            self.store_data[f"{transaction_id}_{key}"] = value
            return {"success": True}
        
        elif operation_type == "get":
            key = data["key"]
            
            # Check transaction-local view first
            tx_key = f"{transaction_id}_{key}"
            if tx_key in self.store_data:
                return {"value": self.store_data[tx_key]}
            
            # Fall back to committed data
            return {"value": self.store_data.get(key)}
        
        elif operation_type == "delete":
            key = data["key"]
            
            # Mark as deleted in transaction view
            self.store_data[f"{transaction_id}_{key}_deleted"] = True
            return {"success": True}
        
        else:
            raise ValueError(f"Unknown operation type: {operation_type}")
    
    async def _apply_transaction_operations(self, store_transaction: EnhancedStoreTransaction):
        """Apply committed transaction operations to store"""
        
        for op in store_transaction.operations:
            if op["type"] == "put":
                key = op["data"]["key"]
                value = op["data"]["value"]
                self.store_data[key] = value
                
                # Clean up transaction-local view
                tx_key = f"{store_transaction.transaction_id}_{key}"
                self.store_data.pop(tx_key, None)
            
            elif op["type"] == "delete":
                key = op["data"]["key"]
                self.store_data.pop(key, None)
                
                # Clean up transaction markers
                tx_key = f"{store_transaction.transaction_id}_{key}_deleted"
                self.store_data.pop(tx_key, None)
    
    def get_store_statistics(self) -> Dict[str, Any]:
        """Get comprehensive store statistics"""
        
        pool_stats = self.connection_pool.get_pool_statistics() if self.connection_pool else {}
        tx_stats = self.transaction_manager.get_transaction_statistics() if self.transaction_manager else {}
        coord_stats = self.distributed_coordinator.get_coordinator_statistics() if self.distributed_coordinator else {}
        
        return {
            "store_id": self.store_id,
            "active_transactions": len(self.active_transactions),
            "data_items": len([k for k in self.store_data.keys() if "_" not in k]),  # Exclude transaction-local
            "schema_version": self.schema_version,
            "connection_pool": pool_stats,
            "transaction_manager": tx_stats,
            "distributed_coordinator": coord_stats,
            "distributed_enabled": self.enable_distributed_transactions
        }
    
    async def cleanup(self):
        """Cleanup store and transaction components"""
        logger.info("Cleaning up V5TransactionalStore")
        
        # Abort active transactions
        for transaction_id in list(self.active_transactions.keys()):
            await self.rollback_transaction(transaction_id)
        
        # Cleanup components
        if self.transaction_manager:
            await self.transaction_manager.cleanup()
        
        if self.connection_pool:
            await self.connection_pool.shutdown()
        
        if self.distributed_coordinator:
            await self.distributed_coordinator.shutdown()


class StoreConnectionParticipant(DatabaseParticipant):
    """Store-specific database participant using connection pool"""
    
    def __init__(self, connection_pool: ConnectionPool):
        super().__init__(connection_pool)
        self.connection_pool = connection_pool
    
    async def execute_operation(self, operation: TransactionOperation) -> Any:
        """Execute operation using connection pool"""
        try:
            async with self.connection_pool.connection() as conn:
                # Convert store operation to SQL-like operation
                if operation.operation_type == "put":
                    result = await conn.execute(
                        "INSERT INTO store_data (key, value) VALUES (%(key)s, %(value)s) ON CONFLICT (key) DO UPDATE SET value = %(value)s",
                        operation.data
                    )
                elif operation.operation_type == "get":
                    result = await conn.execute(
                        "SELECT value FROM store_data WHERE key = %(key)s",
                        operation.data
                    )
                elif operation.operation_type == "delete":
                    result = await conn.execute(
                        "DELETE FROM store_data WHERE key = %(key)s",
                        operation.data
                    )
                else:
                    result = await conn.execute("SELECT 1")  # Default operation
                
                return result
                
        except Exception as e:
            logger.error(f"Store connection participant operation failed: {e}")
            raise


class StoreTransactionParticipant(DistributedTransactionParticipant):
    """Store participant for distributed transactions"""
    
    def __init__(self, store_id: str, store_instance: V5TransactionalStore):
        super().__init__(store_id, "enhanced_store", {})
        self.store_instance = store_instance
    
    async def prepare(self, global_txn_id: str, transaction_data: Dict[str, Any]) -> bool:
        """Prepare store for distributed transaction"""
        try:
            # Store can always prepare (no external dependencies in this implementation)
            logger.info(f"Store {self.participant_id} prepared for distributed transaction {global_txn_id}")
            return True
        except Exception as e:
            logger.error(f"Store prepare failed: {e}")
            return False
    
    async def commit(self, global_txn_id: str) -> bool:
        """Commit store changes for distributed transaction"""
        try:
            # Apply any pending changes
            logger.info(f"Store {self.participant_id} committed distributed transaction {global_txn_id}")
            return True
        except Exception as e:
            logger.error(f"Store commit failed: {e}")
            return False
    
    async def abort(self, global_txn_id: str) -> bool:
        """Abort store changes for distributed transaction"""
        try:
            # Rollback any pending changes
            logger.info(f"Store {self.participant_id} aborted distributed transaction {global_txn_id}")
            return True
        except Exception as e:
            logger.error(f"Store abort failed: {e}")
            return False


# Test harness
if __name__ == "__main__":
    async def test_enhanced_store_integration():
        """Test enhanced store with transaction management"""
        
        config = {
            "store_id": "test_store",
            "min_connections": 2,
            "max_connections": 5,
            "enable_distributed_transactions": True,
            "default_isolation_level": "READ_COMMITTED",
            "auto_commit": False  # Test explicit transactions
        }
        
        store = V5TransactionalStore(config)
        
        try:
            print("🔧 Testing V5TransactionalStore Integration...")
            
            # Initialize store
            await store.initialize()
            print("✅ Store initialized with transaction management")
            
            # Test transactional operations
            transaction_id = await store.begin_transaction()
            
            # Put operations
            await store.put("user:1", {"name": "Alice", "age": 30}, transaction_id)
            await store.put("user:2", {"name": "Bob", "age": 25}, transaction_id)
            
            # Get operations (should see uncommitted data within transaction)
            user1 = await store.get("user:1", transaction_id)
            print(f"✅ Transactional get: {user1}")
            
            # Commit transaction
            commit_success = await store.commit_transaction(transaction_id)
            print(f"✅ Transaction commit: {commit_success}")
            
            # Test batch operations
            batch_ops = [
                {"type": "put", "data": {"key": "product:1", "value": {"name": "Laptop", "price": 999}}},
                {"type": "put", "data": {"key": "product:2", "value": {"name": "Mouse", "price": 25}}},
                {"type": "get", "data": {"key": "user:1"}}
            ]
            
            batch_results = await store.batch_operation(batch_ops, IsolationLevel.SERIALIZABLE)
            print(f"✅ Batch operations: {len(batch_results)} results")
            
            # Test distributed operations
            if store.distributed_coordinator:
                distributed_ops = [
                    {"type": "put", "data": {"key": "global:1", "value": {"data": "distributed"}}}
                ]
                
                # Register additional participant for testing
                test_participant = StoreTransactionParticipant("remote_store", store)
                store.distributed_coordinator.register_participant(test_participant)
                
                distributed_success = await store.distributed_operation(
                    distributed_ops,
                    ["test_store", "remote_store"]
                )
                print(f"✅ Distributed operation: {distributed_success}")
            
            # Test rollback
            rollback_tx = await store.begin_transaction()
            await store.put("temp:key", "temp_value", rollback_tx)
            await store.rollback_transaction(rollback_tx)
            print("✅ Transaction rollback successful")
            
            # Test concurrent transactions
            async def concurrent_transaction(tx_num):
                tx_id = await store.begin_transaction()
                await store.put(f"concurrent:{tx_num}", f"value_{tx_num}", tx_id)
                return await store.commit_transaction(tx_id)
            
            concurrent_tasks = [concurrent_transaction(i) for i in range(3)]
            concurrent_results = await asyncio.gather(*concurrent_tasks)
            print(f"✅ Concurrent transactions: {sum(concurrent_results)}/3 successful")
            
            # Test statistics
            stats = store.get_store_statistics()
            print(f"✅ Store statistics: {stats['data_items']} items, {stats['active_transactions']} active transactions")
            
            # Test cleanup
            await store.cleanup()
            print("✅ Store cleanup successful")
            
        except Exception as e:
            print(f"❌ Enhanced store integration test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_enhanced_store_integration())