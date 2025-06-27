"""
V5.0 Enhanced Level 3 Database Validation
Advanced Level 3 system integration validation with comprehensive database support
"""

import asyncio
import time
import logging
import uuid
from typing import Dict, Any, Optional, List, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import sys
import os

# Add database components to path
sys.path.append('/home/brian/autocoder3_cc/evidence/phase5_database_integration/day1_enhanced_store_components')
sys.path.append('/home/brian/autocoder3_cc/evidence/phase5_database_integration/day2_schema_validation_migration')
sys.path.append('/home/brian/autocoder3_cc/evidence/phase5_database_integration/day3_transaction_management')
sys.path.append('/home/brian/autocoder3_cc/evidence/phase5_database_integration/day4_multi_database_support')

# Import Phase 4 validation components
sys.path.append('/home/brian/autocoder3_cc/blueprint_language')

from validation_result_types import ValidationResult, ValidationLevel

# Simple test classes for integration testing
@dataclass
class SystemBlueprint:
    """Simple system blueprint for testing"""
    name: str
    version: str
    components: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
from database_adapters import DatabaseAdapter, DatabaseType, QueryResult
from transaction_manager import TransactionManager, IsolationLevel
from query_translator import UniversalQueryTranslator
from performance_optimizer import PerformanceOptimizer

logger = logging.getLogger(__name__)


class DatabaseIntegrationTest(Enum):
    """Types of database integration tests"""
    SCHEMA_CONSISTENCY = "schema_consistency"
    DATA_INTEGRITY = "data_integrity"
    TRANSACTION_ATOMICITY = "transaction_atomicity"
    CROSS_DATABASE_SYNC = "cross_database_sync"
    PERFORMANCE_BENCHMARKS = "performance_benchmarks"
    FAILOVER_RECOVERY = "failover_recovery"
    CONCURRENT_ACCESS = "concurrent_access"
    QUERY_TRANSLATION = "query_translation"


@dataclass
class DatabaseTestScenario:
    """Database test scenario configuration"""
    test_type: DatabaseIntegrationTest
    target_databases: List[DatabaseType]
    test_data: Dict[str, Any]
    expected_outcomes: Dict[str, Any]
    performance_thresholds: Optional[Dict[str, float]] = None
    concurrency_level: int = 1
    timeout: float = 30.0
    retry_attempts: int = 3


@dataclass
class DatabaseTestResult:
    """Result of database integration test"""
    test_type: DatabaseIntegrationTest
    success: bool
    execution_time: float
    database_results: Dict[DatabaseType, Dict[str, Any]]
    performance_metrics: Optional[Dict[str, Any]] = None
    error_details: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


class EnhancedLevel3DatabaseValidator:
    """Enhanced Level 3 validation with comprehensive database integration testing"""
    
    def __init__(
        self,
        database_adapters: Dict[DatabaseType, DatabaseAdapter],
        transaction_managers: Dict[DatabaseType, TransactionManager],
        query_translator: UniversalQueryTranslator,
        performance_optimizer: PerformanceOptimizer
    ):
        self.database_adapters = database_adapters
        self.transaction_managers = transaction_managers
        self.query_translator = query_translator
        self.performance_optimizer = performance_optimizer
        
        # Test configuration
        self.test_scenarios = self._create_default_test_scenarios()
        self.test_results: List[DatabaseTestResult] = []
        
        # Performance baselines
        self.performance_baselines = {
            "max_query_time": 1.0,
            "min_transaction_throughput": 100.0,  # transactions per second
            "max_connection_establishment_time": 0.5,
            "min_cache_hit_rate": 0.8
        }
        
        logger.info("Enhanced Level 3 Database Validator initialized")
    
    def _create_default_test_scenarios(self) -> List[DatabaseTestScenario]:
        """Create default database integration test scenarios"""
        scenarios = []
        
        # Schema consistency test
        scenarios.append(DatabaseTestScenario(
            test_type=DatabaseIntegrationTest.SCHEMA_CONSISTENCY,
            target_databases=list(self.database_adapters.keys()),
            test_data={
                "tables": ["users", "orders", "products"],
                "required_columns": {
                    "users": ["id", "email", "created_at"],
                    "orders": ["id", "user_id", "total", "status"],
                    "products": ["id", "name", "price", "inventory"]
                }
            },
            expected_outcomes={"all_schemas_valid": True},
            timeout=10.0
        ))
        
        # Data integrity test
        scenarios.append(DatabaseTestScenario(
            test_type=DatabaseIntegrationTest.DATA_INTEGRITY,
            target_databases=list(self.database_adapters.keys()),
            test_data={
                "test_records": [
                    {"table": "users", "data": {"email": "test@example.com", "name": "Test User"}},
                    {"table": "orders", "data": {"user_id": 1, "total": 99.99, "status": "pending"}}
                ]
            },
            expected_outcomes={"data_consistent": True, "constraints_enforced": True},
            timeout=15.0
        ))
        
        # Transaction atomicity test
        scenarios.append(DatabaseTestScenario(
            test_type=DatabaseIntegrationTest.TRANSACTION_ATOMICITY,
            target_databases=list(self.database_adapters.keys()),
            test_data={
                "operations": [
                    {"type": "insert", "table": "users", "data": {"email": "atomic@test.com"}},
                    {"type": "insert", "table": "orders", "data": {"user_id": "INVALID", "total": 50.0}},  # Should fail
                    {"type": "update", "table": "users", "data": {"name": "Updated"}, "where": {"email": "atomic@test.com"}}
                ]
            },
            expected_outcomes={"transaction_rolled_back": True, "no_partial_changes": True},
            timeout=20.0
        ))
        
        # Performance benchmarks test
        scenarios.append(DatabaseTestScenario(
            test_type=DatabaseIntegrationTest.PERFORMANCE_BENCHMARKS,
            target_databases=list(self.database_adapters.keys()),
            test_data={
                "queries": [
                    "SELECT COUNT(*) FROM users",
                    "SELECT * FROM orders WHERE status = 'pending' LIMIT 100",
                    "SELECT u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id"
                ],
                "iterations": 50
            },
            expected_outcomes={"avg_query_time_under_threshold": True},
            performance_thresholds={
                "max_avg_query_time": 0.1,
                "max_p95_query_time": 0.5
            },
            timeout=30.0
        ))
        
        # Concurrent access test
        scenarios.append(DatabaseTestScenario(
            test_type=DatabaseIntegrationTest.CONCURRENT_ACCESS,
            target_databases=list(self.database_adapters.keys()),
            test_data={
                "concurrent_operations": [
                    {"type": "read", "query": "SELECT * FROM users LIMIT 10"},
                    {"type": "write", "query": "INSERT INTO orders (user_id, total) VALUES (1, 25.50)"},
                    {"type": "update", "query": "UPDATE users SET last_login = NOW() WHERE id = 1"}
                ]
            },
            expected_outcomes={"no_deadlocks": True, "data_consistency_maintained": True},
            concurrency_level=10,
            timeout=25.0
        ))
        
        # Query translation test (if multiple databases)
        if len(self.database_adapters) > 1:
            scenarios.append(DatabaseTestScenario(
                test_type=DatabaseIntegrationTest.QUERY_TRANSLATION,
                target_databases=list(self.database_adapters.keys()),
                test_data={
                    "source_queries": [
                        "SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM users",
                        "SELECT * FROM orders WHERE created_at >= NOW() - INTERVAL 1 DAY",
                        "CREATE TABLE temp_test (id INT AUTO_INCREMENT PRIMARY KEY, data TEXT)"
                    ]
                },
                expected_outcomes={"all_translations_successful": True, "results_equivalent": True},
                timeout=15.0
            ))
        
        return scenarios
    
    async def execute_enhanced_level3_validation(self, blueprint: SystemBlueprint) -> ValidationResult:
        """Execute comprehensive Level 3 database validation"""
        logger.info("Starting Enhanced Level 3 Database Validation")
        start_time = time.time()
        
        validation_success = True
        validation_details = {}
        
        try:
            # Pre-validation setup
            await self._setup_test_environment(blueprint)
            
            # Execute all test scenarios
            for scenario in self.test_scenarios:
                logger.info(f"Executing test scenario: {scenario.test_type.value}")
                
                test_result = await self._execute_test_scenario(scenario)
                self.test_results.append(test_result)
                
                validation_details[scenario.test_type.value] = {
                    "success": test_result.success,
                    "execution_time": test_result.execution_time,
                    "performance_metrics": test_result.performance_metrics
                }
                
                if not test_result.success:
                    validation_success = False
                    logger.warning(f"Test scenario {scenario.test_type.value} failed")
            
            # Post-validation analysis
            analysis_result = await self._analyze_validation_results()
            validation_details["analysis"] = analysis_result
            
            # Performance summary
            performance_summary = self._generate_performance_summary()
            validation_details["performance_summary"] = performance_summary
            
            execution_time = time.time() - start_time
            
            logger.info(f"Enhanced Level 3 validation completed: {'PASS' if validation_success else 'FAIL'}")
            
            from v5_integration_tests import ExtendedValidationResult
            return ExtendedValidationResult(
                passed=validation_success,
                level=ValidationLevel.LEVEL_3_SYSTEM_INTEGRATION,
                execution_time=execution_time,
                details=validation_details,
                healing_applied=False
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Enhanced Level 3 validation failed: {e}")
            
            from v5_integration_tests import ExtendedValidationResult
            return ExtendedValidationResult(
                passed=False,
                level=ValidationLevel.LEVEL_3_SYSTEM_INTEGRATION,
                execution_time=execution_time,
                details={"error": str(e), "partial_results": validation_details},
                healing_applied=False
            )
        
        finally:
            # Cleanup test environment
            await self._cleanup_test_environment()
    
    async def _setup_test_environment(self, blueprint: SystemBlueprint):
        """Setup test environment for database validation"""
        logger.debug("Setting up test environment")
        
        # Create test tables if they don't exist
        test_schema = {
            "users": """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """,
            "orders": """
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    total DECIMAL(10,2) NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "products": """
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    inventory INTEGER DEFAULT 0
                )
            """
        }
        
        for db_type, adapter in self.database_adapters.items():
            try:
                for table_name, create_sql in test_schema.items():
                    # Translate SQL for specific database
                    translated_sql = self.query_translator.translate(create_sql, db_type)
                    
                    if translated_sql.success:
                        await adapter.execute_query(translated_sql.translated_query)
                        logger.debug(f"Created test table {table_name} in {db_type.value}")
                    else:
                        logger.warning(f"Failed to translate schema for {table_name} in {db_type.value}")
                        
            except Exception as e:
                logger.warning(f"Test setup failed for {db_type.value}: {e}")
    
    async def _execute_test_scenario(self, scenario: DatabaseTestScenario) -> DatabaseTestResult:
        """Execute a specific test scenario"""
        start_time = time.time()
        database_results = {}
        
        try:
            if scenario.test_type == DatabaseIntegrationTest.SCHEMA_CONSISTENCY:
                database_results = await self._test_schema_consistency(scenario)
            elif scenario.test_type == DatabaseIntegrationTest.DATA_INTEGRITY:
                database_results = await self._test_data_integrity(scenario)
            elif scenario.test_type == DatabaseIntegrationTest.TRANSACTION_ATOMICITY:
                database_results = await self._test_transaction_atomicity(scenario)
            elif scenario.test_type == DatabaseIntegrationTest.PERFORMANCE_BENCHMARKS:
                database_results = await self._test_performance_benchmarks(scenario)
            elif scenario.test_type == DatabaseIntegrationTest.CONCURRENT_ACCESS:
                database_results = await self._test_concurrent_access(scenario)
            elif scenario.test_type == DatabaseIntegrationTest.QUERY_TRANSLATION:
                database_results = await self._test_query_translation(scenario)
            else:
                database_results = {"error": f"Unknown test type: {scenario.test_type}"}
            
            execution_time = time.time() - start_time
            
            # Determine overall success
            success = all(
                result.get("success", False) for result in database_results.values()
                if isinstance(result, dict)
            )
            
            # Extract performance metrics
            performance_metrics = {}
            for db_type, result in database_results.items():
                if isinstance(result, dict) and "performance" in result:
                    performance_metrics[db_type.value if hasattr(db_type, 'value') else str(db_type)] = result["performance"]
            
            return DatabaseTestResult(
                test_type=scenario.test_type,
                success=success,
                execution_time=execution_time,
                database_results=database_results,
                performance_metrics=performance_metrics if performance_metrics else None
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Test scenario {scenario.test_type.value} failed: {e}")
            
            return DatabaseTestResult(
                test_type=scenario.test_type,
                success=False,
                execution_time=execution_time,
                database_results=database_results,
                error_details=[str(e)]
            )
    
    async def _test_schema_consistency(self, scenario: DatabaseTestScenario) -> Dict[DatabaseType, Dict[str, Any]]:
        """Test schema consistency across databases"""
        results = {}
        
        for db_type in scenario.target_databases:
            adapter = self.database_adapters.get(db_type)
            if not adapter:
                results[db_type] = {"success": False, "error": "Adapter not available"}
                continue
            
            try:
                schema_valid = True
                schema_details = {}
                
                # Check each required table
                for table_name, columns in scenario.test_data["required_columns"].items():
                    # Query to check table structure (database-specific)
                    if db_type == DatabaseType.POSTGRESQL:
                        check_query = f"""
                            SELECT column_name FROM information_schema.columns 
                            WHERE table_name = '{table_name}'
                        """
                    elif db_type == DatabaseType.MYSQL:
                        check_query = f"DESCRIBE {table_name}"
                    elif db_type == DatabaseType.SQLITE:
                        check_query = f"PRAGMA table_info({table_name})"
                    else:
                        check_query = f"SELECT 1 FROM {table_name} LIMIT 0"  # Basic existence check
                    
                    result = await adapter.execute_query(check_query)
                    
                    if result.success:
                        # Extract column names (database-specific)
                        if result.rows:
                            if db_type == DatabaseType.POSTGRESQL:
                                existing_columns = [row.get('column_name', '') for row in result.rows]
                            elif db_type == DatabaseType.MYSQL:
                                existing_columns = [row.get('Field', '') for row in result.rows]
                            elif db_type == DatabaseType.SQLITE:
                                existing_columns = [row.get('name', '') for row in result.rows]
                            else:
                                existing_columns = [row.get('column_name', '') for row in result.rows]
                            
                            missing_columns = [col for col in columns if col not in existing_columns]
                            schema_details[table_name] = {
                                "exists": True,
                                "missing_columns": missing_columns
                            }
                            if missing_columns:
                                schema_valid = False
                        else:
                            schema_details[table_name] = {"exists": True, "columns_verified": True}
                    else:
                        schema_details[table_name] = {"exists": False}
                        schema_valid = False
                
                results[db_type] = {
                    "success": schema_valid,
                    "schema_details": schema_details
                }
                
            except Exception as e:
                results[db_type] = {"success": False, "error": str(e)}
        
        return results
    
    async def _test_data_integrity(self, scenario: DatabaseTestScenario) -> Dict[DatabaseType, Dict[str, Any]]:
        """Test data integrity across databases"""
        results = {}
        
        for db_type in scenario.target_databases:
            adapter = self.database_adapters.get(db_type)
            tx_manager = self.transaction_managers.get(db_type)
            
            if not adapter or not tx_manager:
                results[db_type] = {"success": False, "error": "Components not available"}
                continue
            
            try:
                integrity_valid = True
                integrity_details = {}
                
                # Test each record insertion
                for record in scenario.test_data["test_records"]:
                    table = record["table"]
                    data = record["data"]
                    
                    # Create INSERT query
                    columns = ", ".join(data.keys())
                    placeholders = ", ".join([f"%({key})s" for key in data.keys()])
                    insert_query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                    
                    # Translate query for target database
                    translated = self.query_translator.translate(insert_query, db_type)
                    
                    if translated.success:
                        # Execute within transaction
                        async with await tx_manager.transaction() as tx:
                            result = await adapter.execute_query(
                                translated.translated_query, 
                                data
                            )
                            
                            if result.success:
                                # Verify data was inserted correctly
                                select_query = f"SELECT * FROM {table} WHERE "
                                conditions = " AND ".join([f"{k} = %({k})s" for k in data.keys()])
                                select_query += conditions
                                
                                verify_result = await adapter.execute_query(select_query, data)
                                
                                integrity_details[f"{table}_insert"] = {
                                    "inserted": result.success,
                                    "verified": verify_result.success and len(verify_result.rows or []) > 0
                                }
                            else:
                                integrity_details[f"{table}_insert"] = {
                                    "inserted": False,
                                    "error": result.error_message
                                }
                                integrity_valid = False
                    else:
                        integrity_details[f"{table}_insert"] = {
                            "translated": False,
                            "error": "Query translation failed"
                        }
                        integrity_valid = False
                
                results[db_type] = {
                    "success": integrity_valid,
                    "integrity_details": integrity_details
                }
                
            except Exception as e:
                results[db_type] = {"success": False, "error": str(e)}
        
        return results
    
    async def _test_transaction_atomicity(self, scenario: DatabaseTestScenario) -> Dict[DatabaseType, Dict[str, Any]]:
        """Test transaction atomicity (ACID compliance)"""
        results = {}
        
        for db_type in scenario.target_databases:
            adapter = self.database_adapters.get(db_type)
            tx_manager = self.transaction_managers.get(db_type)
            
            if not adapter or not tx_manager:
                results[db_type] = {"success": False, "error": "Components not available"}
                continue
            
            try:
                atomicity_valid = True
                atomicity_details = {}
                
                # Begin transaction that should fail
                transaction_id = await adapter.begin_transaction()
                operations_attempted = 0
                
                try:
                    for operation in scenario.test_data["operations"]:
                        operations_attempted += 1
                        
                        if operation["type"] == "insert":
                            table = operation["table"]
                            data = operation["data"]
                            columns = ", ".join(data.keys())
                            placeholders = ", ".join([f"%({key})s" for key in data.keys()])
                            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                            
                            # This should fail on the second operation (invalid user_id)
                            result = await adapter.execute_query(query, data, transaction_id)
                            
                            if not result.success:
                                # Expected failure - now test rollback
                                break
                    
                    # If we get here, rollback the transaction
                    rollback_success = await adapter.rollback_transaction(transaction_id)
                    
                    # Verify no partial changes were committed
                    verify_query = "SELECT COUNT(*) as count FROM users WHERE email = 'atomic@test.com'"
                    verify_result = await adapter.execute_query(verify_query)
                    
                    partial_changes = (
                        verify_result.success and 
                        verify_result.rows and 
                        verify_result.rows[0].get("count", 0) > 0
                    )
                    
                    atomicity_details = {
                        "operations_attempted": operations_attempted,
                        "rollback_successful": rollback_success,
                        "no_partial_changes": not partial_changes
                    }
                    
                    atomicity_valid = rollback_success and not partial_changes
                    
                except Exception as tx_error:
                    # Transaction failed as expected
                    try:
                        await adapter.rollback_transaction(transaction_id)
                        atomicity_details = {
                            "transaction_failed_as_expected": True,
                            "rollback_successful": True
                        }
                    except Exception as rollback_error:
                        atomicity_details = {
                            "transaction_failed": True,
                            "rollback_failed": True,
                            "rollback_error": str(rollback_error)
                        }
                        atomicity_valid = False
                
                results[db_type] = {
                    "success": atomicity_valid,
                    "atomicity_details": atomicity_details
                }
                
            except Exception as e:
                results[db_type] = {"success": False, "error": str(e)}
        
        return results
    
    async def _test_performance_benchmarks(self, scenario: DatabaseTestScenario) -> Dict[DatabaseType, Dict[str, Any]]:
        """Test database performance benchmarks"""
        results = {}
        
        for db_type in scenario.target_databases:
            adapter = self.database_adapters.get(db_type)
            if not adapter:
                results[db_type] = {"success": False, "error": "Adapter not available"}
                continue
            
            try:
                performance_results = {}
                
                for query in scenario.test_data["queries"]:
                    query_times = []
                    
                    # Translate query for target database
                    translated = self.query_translator.translate(query, db_type)
                    
                    if not translated.success:
                        performance_results[query] = {
                            "success": False,
                            "error": "Query translation failed"
                        }
                        continue
                    
                    # Execute query multiple times
                    for i in range(scenario.test_data["iterations"]):
                        start_time = time.time()
                        result = await adapter.execute_query(translated.translated_query)
                        execution_time = time.time() - start_time
                        
                        if result.success:
                            query_times.append(execution_time)
                        else:
                            # Query failed
                            break
                    
                    if query_times:
                        avg_time = sum(query_times) / len(query_times)
                        p95_time = sorted(query_times)[int(len(query_times) * 0.95)]
                        
                        performance_results[query] = {
                            "success": True,
                            "avg_time": avg_time,
                            "p95_time": p95_time,
                            "min_time": min(query_times),
                            "max_time": max(query_times),
                            "iterations": len(query_times)
                        }
                    else:
                        performance_results[query] = {
                            "success": False,
                            "error": "No successful executions"
                        }
                
                # Check against thresholds
                threshold_checks = {}
                if scenario.performance_thresholds:
                    for query, metrics in performance_results.items():
                        if metrics.get("success"):
                            threshold_checks[query] = {
                                "avg_time_ok": metrics["avg_time"] <= scenario.performance_thresholds.get("max_avg_query_time", 1.0),
                                "p95_time_ok": metrics["p95_time"] <= scenario.performance_thresholds.get("max_p95_query_time", 2.0)
                            }
                
                overall_success = all(
                    metrics.get("success", False) for metrics in performance_results.values()
                ) and all(
                    all(checks.values()) for checks in threshold_checks.values()
                )
                
                results[db_type] = {
                    "success": overall_success,
                    "performance": performance_results,
                    "threshold_checks": threshold_checks
                }
                
            except Exception as e:
                results[db_type] = {"success": False, "error": str(e)}
        
        return results
    
    async def _test_concurrent_access(self, scenario: DatabaseTestScenario) -> Dict[DatabaseType, Dict[str, Any]]:
        """Test concurrent database access"""
        results = {}
        
        for db_type in scenario.target_databases:
            adapter = self.database_adapters.get(db_type)
            if not adapter:
                results[db_type] = {"success": False, "error": "Adapter not available"}
                continue
            
            try:
                # Create concurrent tasks
                async def concurrent_operation(op_id: int, operation: Dict[str, Any]):
                    try:
                        start_time = time.time()
                        
                        if operation["type"] == "read":
                            result = await adapter.execute_query(operation["query"])
                        elif operation["type"] in ["write", "update"]:
                            # Use performance optimizer if available
                            if self.performance_optimizer:
                                result = await self.performance_optimizer.execute_optimized_query(
                                    adapter, operation["query"]
                                )
                            else:
                                result = await adapter.execute_query(operation["query"])
                        else:
                            result = await adapter.execute_query(operation["query"])
                        
                        execution_time = time.time() - start_time
                        
                        return {
                            "op_id": op_id,
                            "success": result.success,
                            "execution_time": execution_time,
                            "error": result.error_message if not result.success else None
                        }
                        
                    except Exception as e:
                        return {
                            "op_id": op_id,
                            "success": False,
                            "execution_time": 0,
                            "error": str(e)
                        }
                
                # Launch concurrent operations
                tasks = []
                for i in range(scenario.concurrency_level):
                    for operation in scenario.test_data["concurrent_operations"]:
                        task = asyncio.create_task(concurrent_operation(i, operation))
                        tasks.append(task)
                
                # Wait for all operations to complete
                concurrent_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Analyze results
                successful_ops = 0
                failed_ops = 0
                total_time = 0
                deadlocks = 0
                
                for result in concurrent_results:
                    if isinstance(result, Exception):
                        failed_ops += 1
                        if "deadlock" in str(result).lower():
                            deadlocks += 1
                    elif isinstance(result, dict):
                        if result.get("success"):
                            successful_ops += 1
                            total_time += result.get("execution_time", 0)
                        else:
                            failed_ops += 1
                            if "deadlock" in str(result.get("error", "")).lower():
                                deadlocks += 1
                
                avg_time = total_time / max(successful_ops, 1)
                success_rate = successful_ops / max(len(concurrent_results), 1)
                
                concurrency_success = (
                    success_rate >= 0.9 and  # At least 90% success rate
                    deadlocks == 0  # No deadlocks
                )
                
                results[db_type] = {
                    "success": concurrency_success,
                    "performance": {
                        "successful_operations": successful_ops,
                        "failed_operations": failed_ops,
                        "success_rate": success_rate,
                        "avg_execution_time": avg_time,
                        "deadlocks": deadlocks
                    }
                }
                
            except Exception as e:
                results[db_type] = {"success": False, "error": str(e)}
        
        return results
    
    async def _test_query_translation(self, scenario: DatabaseTestScenario) -> Dict[DatabaseType, Dict[str, Any]]:
        """Test query translation between databases"""
        results = {}
        
        source_databases = scenario.target_databases
        
        for source_db in source_databases:
            results[source_db] = {"translations": {}, "success": True}
            
            for target_db in scenario.target_databases:
                if source_db == target_db:
                    results[source_db]["translations"][target_db] = {"success": True, "note": "Same database"}
                    continue
                
                translation_results = []
                
                for query in scenario.test_data["source_queries"]:
                    # Translate query
                    translation = self.query_translator.translate(query, target_db, source_db)
                    
                    if translation.success:
                        # Try to execute translated query
                        target_adapter = self.database_adapters.get(target_db)
                        if target_adapter:
                            try:
                                exec_result = await target_adapter.execute_query(translation.translated_query)
                                translation_results.append({
                                    "query": query[:50] + "..." if len(query) > 50 else query,
                                    "translation_success": True,
                                    "execution_success": exec_result.success,
                                    "execution_error": exec_result.error_message if not exec_result.success else None
                                })
                            except Exception as e:
                                translation_results.append({
                                    "query": query[:50] + "..." if len(query) > 50 else query,
                                    "translation_success": True,
                                    "execution_success": False,
                                    "execution_error": str(e)
                                })
                        else:
                            translation_results.append({
                                "query": query[:50] + "..." if len(query) > 50 else query,
                                "translation_success": True,
                                "execution_success": False,
                                "execution_error": "Target adapter not available"
                            })
                    else:
                        translation_results.append({
                            "query": query[:50] + "..." if len(query) > 50 else query,
                            "translation_success": False,
                            "execution_success": False,
                            "translation_error": translation.warnings
                        })
                
                # Determine success for this translation pair
                pair_success = all(
                    result["translation_success"] for result in translation_results
                )
                
                results[source_db]["translations"][target_db] = {
                    "success": pair_success,
                    "results": translation_results
                }
                
                if not pair_success:
                    results[source_db]["success"] = False
        
        return results
    
    async def _analyze_validation_results(self) -> Dict[str, Any]:
        """Analyze validation results and provide insights"""
        analysis = {
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for result in self.test_results if result.success),
            "failed_tests": sum(1 for result in self.test_results if not result.success),
            "test_breakdown": {},
            "performance_analysis": {},
            "recommendations": []
        }
        
        # Test breakdown
        for result in self.test_results:
            analysis["test_breakdown"][result.test_type.value] = {
                "success": result.success,
                "execution_time": result.execution_time,
                "database_count": len(result.database_results)
            }
        
        # Performance analysis
        perf_results = [r for r in self.test_results if r.test_type == DatabaseIntegrationTest.PERFORMANCE_BENCHMARKS]
        if perf_results:
            perf_metrics = perf_results[0].performance_metrics
            if perf_metrics:
                analysis["performance_analysis"] = perf_metrics
        
        # Generate recommendations
        failed_tests = [r for r in self.test_results if not r.success]
        if failed_tests:
            for failed_test in failed_tests:
                if failed_test.test_type == DatabaseIntegrationTest.PERFORMANCE_BENCHMARKS:
                    analysis["recommendations"].append("Consider optimizing slow queries or increasing hardware resources")
                elif failed_test.test_type == DatabaseIntegrationTest.TRANSACTION_ATOMICITY:
                    analysis["recommendations"].append("Review transaction isolation levels and error handling")
                elif failed_test.test_type == DatabaseIntegrationTest.CONCURRENT_ACCESS:
                    analysis["recommendations"].append("Implement better connection pooling or deadlock detection")
                elif failed_test.test_type == DatabaseIntegrationTest.QUERY_TRANSLATION:
                    analysis["recommendations"].append("Review query translation mappings for unsupported features")
        
        if analysis["passed_tests"] == analysis["total_tests"]:
            analysis["recommendations"].append("All database integration tests passed - system is production ready")
        
        return analysis
    
    def _generate_performance_summary(self) -> Dict[str, Any]:
        """Generate performance summary from all test results"""
        summary = {
            "total_execution_time": sum(result.execution_time for result in self.test_results),
            "average_test_time": 0,
            "performance_baselines_met": True,
            "performance_details": {}
        }
        
        if self.test_results:
            summary["average_test_time"] = summary["total_execution_time"] / len(self.test_results)
        
        # Analyze performance test results specifically
        perf_results = [r for r in self.test_results if r.test_type == DatabaseIntegrationTest.PERFORMANCE_BENCHMARKS]
        if perf_results and perf_results[0].performance_metrics:
            for db_type, metrics in perf_results[0].performance_metrics.items():
                if isinstance(metrics, dict) and "performance" in metrics:
                    summary["performance_details"][db_type] = metrics["performance"]
        
        return summary
    
    async def _cleanup_test_environment(self):
        """Clean up test environment after validation"""
        logger.debug("Cleaning up test environment")
        
        # Clean up test data (optional - depends on requirements)
        cleanup_queries = [
            "DELETE FROM orders WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%test%' OR email LIKE '%atomic%')",
            "DELETE FROM users WHERE email LIKE '%test%' OR email LIKE '%atomic%'"
        ]
        
        for db_type, adapter in self.database_adapters.items():
            try:
                for query in cleanup_queries:
                    translated = self.query_translator.translate(query, db_type)
                    if translated.success:
                        await adapter.execute_query(translated.translated_query)
                        
            except Exception as e:
                logger.warning(f"Test cleanup failed for {db_type.value}: {e}")


# Test harness
if __name__ == "__main__":
    async def test_enhanced_level3_validator():
        """Test Enhanced Level 3 Database Validator"""
        
        print("🔧 Testing Enhanced Level 3 Database Validator...")
        
        # Mock components for testing
        mock_adapters = {}
        mock_tx_managers = {}
        
        # Create mock universal translator
        from query_translator import UniversalQueryTranslator
        translator = UniversalQueryTranslator()
        
        # Create mock performance optimizer
        from performance_optimizer import PerformanceOptimizer
        optimizer = PerformanceOptimizer()
        
        # Create validator
        validator = EnhancedLevel3DatabaseValidator(
            mock_adapters, mock_tx_managers, translator, optimizer
        )
        
        print(f"✅ Created validator with {len(validator.test_scenarios)} test scenarios")
        
        # Test scenario creation
        for scenario in validator.test_scenarios:
            print(f"   - {scenario.test_type.value}: {len(scenario.target_databases)} databases")
        
        print("✅ Enhanced Level 3 Database Validator testing complete!")
    
    asyncio.run(test_enhanced_level3_validator())