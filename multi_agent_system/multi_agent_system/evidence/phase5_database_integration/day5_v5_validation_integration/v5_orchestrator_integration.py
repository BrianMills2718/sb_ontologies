"""
V5.0 ValidationDrivenOrchestrator Integration with Database Support
Enhanced ValidationDrivenOrchestrator with comprehensive database integration capabilities
"""

import asyncio
import time
import logging
import uuid
from typing import Dict, Any, Optional, List, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import sys
import os

# Add database components to path
sys.path.append('/home/brian/autocoder3_cc/evidence/phase5_database_integration/day1_enhanced_store_components')
sys.path.append('/home/brian/autocoder3_cc/evidence/phase5_database_integration/day2_schema_validation_migration')
sys.path.append('/home/brian/autocoder3_cc/evidence/phase5_database_integration/day3_transaction_management')
sys.path.append('/home/brian/autocoder3_cc/evidence/phase5_database_integration/day4_multi_database_support')

# Import Phase 4 ValidationDrivenOrchestrator
sys.path.append('/home/brian/autocoder3_cc/blueprint_language')

from validation_result_types import ValidationLevel, ValidationResult
# Note: In a real implementation, these would come from the actual ValidationDrivenOrchestrator
class ValidationSequenceError(Exception):
    pass

class SystemIntegrationError(Exception):
    pass

@dataclass  
class SystemBlueprint:
    """Simple system blueprint for testing"""
    name: str
    version: str
    components: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ValidationDrivenOrchestrator:
    """Mock ValidationDrivenOrchestrator for testing"""
    def __init__(self):
        pass
    
    async def _execute_level1_validation(self):
        return ValidationResult(passed=True, level=ValidationLevel.LEVEL_1_FRAMEWORK, execution_time=0.1, metadata={"framework_validation": "passed"})
    
    async def _execute_level2_validation(self, blueprint, level1_result):
        return ValidationResult(passed=True, level=ValidationLevel.LEVEL_2_COMPONENT_LOGIC, execution_time=0.1, metadata={"component_logic": "passed"})
    
    async def _execute_level3_validation(self, blueprint, level2_result):
        return ValidationResult(passed=True, level=ValidationLevel.LEVEL_3_SYSTEM_INTEGRATION, execution_time=0.1, metadata={"system_integration": "passed"})
    
    async def _execute_level4_validation(self, blueprint, level3_result):
        return ValidationResult(passed=True, level=ValidationLevel.LEVEL_4_SEMANTIC_VALIDATION, execution_time=0.1, metadata={"semantic_validation": "passed"})
    
    async def _finalize_system_generation(self, blueprint, level4_result):
        return {"system": "generated", "blueprint": blueprint}

# Import database components
from database_adapters import DatabaseAdapter, DatabaseConfiguration, DatabaseType
from database_factory import DatabaseFactory, FactoryConfiguration
from query_translator import UniversalQueryTranslator
from performance_optimizer import PerformanceOptimizer, QueryOptimizationLevel
from schema_validator import SchemaValidator
from transaction_manager import TransactionManager, IsolationLevel

logger = logging.getLogger(__name__)


class DatabaseValidationLevel(Enum):
    """Database-specific validation levels"""
    SCHEMA_VALIDATION = "schema_validation"
    TRANSACTION_INTEGRITY = "transaction_integrity"
    CROSS_DATABASE_COMPATIBILITY = "cross_database_compatibility"
    PERFORMANCE_VALIDATION = "performance_validation"


@dataclass
class DatabaseValidationConfig:
    """Configuration for database validation"""
    enabled_databases: List[DatabaseType] = field(default_factory=lambda: [DatabaseType.POSTGRESQL])
    schema_validation_enabled: bool = True
    transaction_validation_enabled: bool = True
    cross_database_validation_enabled: bool = True
    performance_validation_enabled: bool = True
    performance_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "max_query_time": 1.0,
        "min_cache_hit_rate": 0.8,
        "max_transaction_time": 5.0
    })
    isolation_levels: List[IsolationLevel] = field(default_factory=lambda: [
        IsolationLevel.READ_COMMITTED, IsolationLevel.SERIALIZABLE
    ])


@dataclass
class DatabaseValidationResult:
    """Result of database validation"""
    success: bool
    validation_level: DatabaseValidationLevel
    database_type: Optional[DatabaseType] = None
    schema_validation_passed: bool = False
    transaction_validation_passed: bool = False
    performance_validation_passed: bool = False
    cross_database_validation_passed: bool = False
    execution_time: float = 0.0
    performance_metrics: Optional[Dict[str, Any]] = None
    error_details: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


class DatabaseIntegratedOrchestrator(ValidationDrivenOrchestrator):
    """Enhanced ValidationDrivenOrchestrator with comprehensive database integration"""
    
    def __init__(self, database_config: Optional[DatabaseValidationConfig] = None):
        super().__init__()
        
        # Database configuration
        self.database_config = database_config or DatabaseValidationConfig()
        
        # Database components
        self.database_factory = None
        self.query_translator = UniversalQueryTranslator()
        self.performance_optimizer = None
        self.schema_coordinators: Dict[DatabaseType, SchemaValidator] = {}
        self.transaction_managers: Dict[DatabaseType, TransactionManager] = {}
        
        # Database adapters
        self.database_adapters: Dict[DatabaseType, DatabaseAdapter] = {}
        
        # Validation state
        self.database_validation_results: List[DatabaseValidationResult] = []
        self.cross_database_compatibility_matrix: Dict[str, Dict[str, bool]] = {}
        
        logger.info("Database-integrated ValidationDrivenOrchestrator initialized")
    
    async def initialize_database_integration(self):
        """Initialize database integration components"""
        logger.info("Initializing database integration for ValidationDrivenOrchestrator")
        
        try:
            # Initialize database factory
            factory_config = FactoryConfiguration(
                default_database_type=self.database_config.enabled_databases[0],
                auto_reconnect=True,
                health_monitoring=True,
                performance_monitoring=True
            )
            
            self.database_factory = DatabaseFactory(factory_config)
            
            # Initialize performance optimizer
            self.performance_optimizer = PerformanceOptimizer(
                cache_config={
                    "max_size": 500,
                    "max_memory_mb": 50,
                    "strategy": "adaptive"
                },
                optimization_level=QueryOptimizationLevel.INTERMEDIATE
            )
            
            # Initialize database adapters for each enabled database type
            for db_type in self.database_config.enabled_databases:
                await self._initialize_database_adapter(db_type)
            
            # Initialize schema coordinators
            await self._initialize_schema_coordinators()
            
            # Initialize transaction managers
            await self._initialize_transaction_managers()
            
            logger.info("Database integration initialization complete")
            
        except Exception as e:
            logger.error(f"Database integration initialization failed: {e}")
            raise SystemIntegrationError(f"Database integration failed: {e}")
    
    async def _initialize_database_adapter(self, db_type: DatabaseType):
        """Initialize database adapter for specific database type"""
        try:
            # Create database configuration
            db_config = DatabaseConfiguration(
                database_type=db_type,
                host="localhost",
                port=self._get_default_port(db_type),
                database="validation_test_db",
                username="validation_user",
                password="validation_pass",
                pool_size=5,
                max_connections=10
            )
            
            # Register database with factory
            self.database_factory.registry.register_database(f"validation_{db_type.value}", db_config)
            
            # Create adapter
            adapter = await self.database_factory.create_adapter(f"validation_{db_type.value}")
            
            # Apply performance optimization
            self.performance_optimizer.optimize_adapter(adapter)
            
            # Store adapter
            self.database_adapters[db_type] = adapter
            
            logger.info(f"Database adapter initialized for {db_type.value}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize {db_type.value} adapter: {e}")
            # Continue with other databases
    
    async def _initialize_schema_coordinators(self):
        """Initialize schema coordinators for each database"""
        for db_type, adapter in self.database_adapters.items():
            try:
                schema_config = {
                    "database_type": db_type.value,
                    "validation_enabled": True,
                    "migration_enabled": True
                }
                
                schema_coordinator = SchemaValidator(schema_config)
                self.schema_coordinators[db_type] = schema_coordinator
                
                logger.debug(f"Schema coordinator initialized for {db_type.value}")
                
            except Exception as e:
                logger.warning(f"Failed to initialize schema coordinator for {db_type.value}: {e}")
    
    async def _initialize_transaction_managers(self):
        """Initialize transaction managers for each database"""
        for db_type in self.database_adapters.keys():
            try:
                tx_config = {
                    "default_timeout": 30.0,
                    "max_concurrent_transactions": 50,
                    "deadlock_detection": True,
                    "distributed_transactions": True
                }
                
                tx_manager = TransactionManager(tx_config)
                self.transaction_managers[db_type] = tx_manager
                
                logger.debug(f"Transaction manager initialized for {db_type.value}")
                
            except Exception as e:
                logger.warning(f"Failed to initialize transaction manager for {db_type.value}: {e}")
    
    def _get_default_port(self, db_type: DatabaseType) -> int:
        """Get default port for database type"""
        port_map = {
            DatabaseType.POSTGRESQL: 5432,
            DatabaseType.MYSQL: 3306,
            DatabaseType.SQLITE: 0  # SQLite doesn't use network ports
        }
        return port_map.get(db_type, 5432)
    
    async def generate_system_with_validation(self, blueprint: SystemBlueprint) -> Dict[str, Any]:
        """Enhanced system generation with database validation integration"""
        logger.info("Starting enhanced system generation with database validation")
        
        # Initialize database integration if not already done
        if not self.database_factory:
            await self.initialize_database_integration()
        
        # Pre-flight: Validate database schemas are ready
        await self._prepare_schemas_for_blueprint(blueprint)
        
        # Level 1: Framework validation (unchanged)
        level1_result = await self._execute_level1_validation()
        
        # Level 2: Component logic validation (unchanged) 
        level2_result = await self._execute_level2_validation(blueprint, level1_result)
        
        # Level 3: Enhanced system integration with database validation
        level3_result = await self._execute_enhanced_level3_validation(blueprint, level2_result)
        
        # Level 4: Semantic validation (unchanged)
        level4_result = await self._execute_level4_validation(blueprint, level3_result)
        
        # Generate final system with database integration
        return await self._finalize_system_generation_with_database(blueprint, level4_result)
    
    async def _prepare_schemas_for_blueprint(self, blueprint: SystemBlueprint):
        """Prepare database schemas for blueprint validation"""
        logger.info("Preparing database schemas for blueprint validation")
        
        schema_preparation_tasks = []
        
        for db_type, schema_coordinator in self.schema_coordinators.items():
            task = asyncio.create_task(
                self._prepare_schema_for_database(blueprint, db_type, schema_coordinator)
            )
            schema_preparation_tasks.append(task)
        
        # Wait for all schema preparations
        schema_results = await asyncio.gather(*schema_preparation_tasks, return_exceptions=True)
        
        # Check for failures
        failed_schemas = []
        for i, result in enumerate(schema_results):
            if isinstance(result, Exception):
                db_type = list(self.schema_coordinators.keys())[i]
                failed_schemas.append(f"{db_type.value}: {result}")
                logger.warning(f"Schema preparation failed for {db_type.value}: {result}")
        
        if failed_schemas:
            logger.warning(f"Some schema preparations failed: {failed_schemas}")
            # Continue anyway - not all databases may be required
    
    async def _prepare_schema_for_database(
        self, 
        blueprint: SystemBlueprint, 
        db_type: DatabaseType, 
        schema_coordinator: SchemaValidator
    ):
        """Prepare schema for specific database"""
        try:
            # Extract schema requirements from blueprint
            schema_requirements = self._extract_schema_requirements(blueprint, db_type)
            
            # Validate or create schema
            if schema_requirements:
                await schema_coordinator.validate_or_create_schema()
                logger.debug(f"Schema prepared for {db_type.value}")
            
        except Exception as e:
            logger.error(f"Schema preparation failed for {db_type.value}: {e}")
            raise
    
    def _extract_schema_requirements(self, blueprint: SystemBlueprint, db_type: DatabaseType) -> Dict[str, Any]:
        """Extract schema requirements from blueprint for specific database"""
        # In a real implementation, this would parse the blueprint for database schema requirements
        # For now, return basic requirements
        return {
            "tables": ["users", "sessions", "validation_results"],
            "indexes": ["idx_users_email", "idx_sessions_token"],
            "constraints": ["users_email_unique", "sessions_fk_user"]
        }
    
    async def _execute_enhanced_level3_validation(self, blueprint: SystemBlueprint, level2_result: ValidationResult) -> ValidationResult:
        """Enhanced Level 3 validation with comprehensive database integration"""
        if not level2_result.passed:
            raise ValidationSequenceError("Level 3 cannot proceed - Level 2 validation failed")
        
        logger.info("Executing enhanced Level 3 validation with database integration")
        start_time = time.time()
        
        # Standard Level 3 validation
        base_result = await super()._execute_level3_validation(blueprint, level2_result)
        
        # Enhanced database integration validation
        db_validation_result = await self._validate_database_integration(blueprint)
        
        execution_time = time.time() - start_time
        
        if not db_validation_result.success:
            # Trigger enhanced configuration regeneration with database healing
            logger.warning("Database validation failed, attempting enhanced healing")
            
            healing_result = await self._enhanced_database_healing(blueprint, db_validation_result)
            
            if healing_result.success:
                # Re-validate with healed configuration
                retry_result = await self._validate_database_integration(healing_result.healed_blueprint)
                
                return ValidationResult(
                    passed=retry_result.success and base_result.passed,
                    level=ValidationLevel.LEVEL_3_SYSTEM_INTEGRATION,
                    healing_applied=True,
                    execution_time=execution_time + retry_result.execution_time,
                    metadata={
                        "base_validation": getattr(base_result, 'metadata', {}),
                        "database_validation": retry_result.__dict__ if hasattr(retry_result, '__dict__') else {},
                        "healing_applied": True
                    }
                )
            else:
                raise SystemIntegrationError(
                    f"Enhanced Level 3 validation failed: {db_validation_result.error_details}"
                )
        
        # Combine results
        return ValidationResult(
            passed=base_result.passed and db_validation_result.success,
            level=ValidationLevel.LEVEL_3_SYSTEM_INTEGRATION,
            healing_applied=base_result.healing_applied,
            execution_time=execution_time,
            metadata={
                "base_validation": getattr(base_result, 'metadata', {}),
                "database_validation": db_validation_result.__dict__ if hasattr(db_validation_result, '__dict__') else {},
                "performance_metrics": getattr(db_validation_result, 'performance_metrics', {})
            }
        )
    
    async def _validate_database_integration(self, blueprint: SystemBlueprint) -> DatabaseValidationResult:
        """Comprehensive database integration validation"""
        logger.info("Executing comprehensive database integration validation")
        start_time = time.time()
        
        validation_tasks = []
        
        # Schema validation
        if self.database_config.schema_validation_enabled:
            validation_tasks.append(
                self._validate_database_schemas(blueprint)
            )
        
        # Transaction validation
        if self.database_config.transaction_validation_enabled:
            validation_tasks.append(
                self._validate_transaction_integrity(blueprint)
            )
        
        # Cross-database compatibility validation
        if self.database_config.cross_database_validation_enabled and len(self.database_adapters) > 1:
            validation_tasks.append(
                self._validate_cross_database_compatibility(blueprint)
            )
        
        # Performance validation
        if self.database_config.performance_validation_enabled:
            validation_tasks.append(
                self._validate_database_performance(blueprint)
            )
        
        # Execute all validations
        validation_results = await asyncio.gather(*validation_tasks, return_exceptions=True)
        
        # Aggregate results
        schema_passed = True
        transaction_passed = True
        cross_db_passed = True
        performance_passed = True
        error_details = []
        warnings = []
        performance_metrics = {}
        
        for i, result in enumerate(validation_results):
            if isinstance(result, Exception):
                error_details.append(f"Validation {i} failed: {result}")
                if i == 0:  # Schema validation
                    schema_passed = False
                elif i == 1:  # Transaction validation
                    transaction_passed = False
                elif i == 2:  # Cross-database validation
                    cross_db_passed = False
                elif i == 3:  # Performance validation
                    performance_passed = False
            else:
                if i == 0 and isinstance(result, dict):
                    schema_passed = result.get("success", False)
                    if not schema_passed:
                        error_details.extend(result.get("errors", []))
                elif i == 1 and isinstance(result, dict):
                    transaction_passed = result.get("success", False)
                    if not transaction_passed:
                        error_details.extend(result.get("errors", []))
                elif i == 2 and isinstance(result, dict):
                    cross_db_passed = result.get("success", False)
                    if not cross_db_passed:
                        error_details.extend(result.get("errors", []))
                elif i == 3 and isinstance(result, dict):
                    performance_passed = result.get("success", False)
                    performance_metrics = result.get("metrics", {})
                    if not performance_passed:
                        warnings.extend(result.get("warnings", []))
        
        execution_time = time.time() - start_time
        overall_success = schema_passed and transaction_passed and cross_db_passed and performance_passed
        
        validation_result = DatabaseValidationResult(
            success=overall_success,
            validation_level=DatabaseValidationLevel.CROSS_DATABASE_COMPATIBILITY,
            schema_validation_passed=schema_passed,
            transaction_validation_passed=transaction_passed,
            cross_database_validation_passed=cross_db_passed,
            performance_validation_passed=performance_passed,
            execution_time=execution_time,
            performance_metrics=performance_metrics,
            error_details=error_details if error_details else None,
            warnings=warnings if warnings else None
        )
        
        self.database_validation_results.append(validation_result)
        
        logger.info(f"Database integration validation completed: {'PASS' if overall_success else 'FAIL'}")
        return validation_result
    
    async def _validate_database_schemas(self, blueprint: SystemBlueprint) -> Dict[str, Any]:
        """Validate database schemas across all enabled databases"""
        logger.debug("Validating database schemas")
        
        schema_results = {}
        errors = []
        
        for db_type, schema_coordinator in self.schema_coordinators.items():
            try:
                # Validate schema exists and is compatible
                schema_valid = await schema_coordinator.validate_or_create_schema()
                schema_results[db_type.value] = schema_valid
                
                if not schema_valid:
                    errors.append(f"Schema validation failed for {db_type.value}")
                    
            except Exception as e:
                errors.append(f"Schema validation error for {db_type.value}: {e}")
                schema_results[db_type.value] = False
        
        success = all(schema_results.values()) and len(errors) == 0
        
        return {
            "success": success,
            "schema_results": schema_results,
            "errors": errors
        }
    
    async def _validate_transaction_integrity(self, blueprint: SystemBlueprint) -> Dict[str, Any]:
        """Validate transaction integrity across all databases"""
        logger.debug("Validating transaction integrity")
        
        transaction_results = {}
        errors = []
        
        for db_type, tx_manager in self.transaction_managers.items():
            try:
                adapter = self.database_adapters.get(db_type)
                if not adapter:
                    errors.append(f"No adapter available for {db_type.value}")
                    continue
                
                # Test transaction functionality
                success = await self._test_transaction_functionality(tx_manager, adapter, db_type)
                transaction_results[db_type.value] = success
                
                if not success:
                    errors.append(f"Transaction integrity test failed for {db_type.value}")
                    
            except Exception as e:
                errors.append(f"Transaction validation error for {db_type.value}: {e}")
                transaction_results[db_type.value] = False
        
        success = all(transaction_results.values()) and len(errors) == 0
        
        return {
            "success": success,
            "transaction_results": transaction_results,
            "errors": errors
        }
    
    async def _test_transaction_functionality(
        self, 
        tx_manager: TransactionManager, 
        adapter: DatabaseAdapter, 
        db_type: DatabaseType
    ) -> bool:
        """Test transaction functionality for specific database"""
        try:
            # Test basic transaction
            async with await tx_manager.transaction(IsolationLevel.READ_COMMITTED) as tx:
                # Execute a simple test query
                result = await adapter.execute_query("SELECT 1 as test")
                if not result.success:
                    return False
            
            # Test transaction with rollback
            tx_id = await adapter.begin_transaction()
            await adapter.execute_query("SELECT 1 as rollback_test", transaction_id=tx_id)
            rollback_success = await adapter.rollback_transaction(tx_id)
            
            return rollback_success
            
        except Exception as e:
            logger.warning(f"Transaction test failed for {db_type.value}: {e}")
            return False
    
    async def _validate_cross_database_compatibility(self, blueprint: SystemBlueprint) -> Dict[str, Any]:
        """Validate cross-database compatibility using query translation"""
        logger.debug("Validating cross-database compatibility")
        
        compatibility_matrix = {}
        errors = []
        
        # Test queries that should work across all databases
        test_queries = [
            "SELECT 1 as test",
            "SELECT COUNT(*) FROM users",
            "SELECT name, email FROM users WHERE active = true LIMIT 10"
        ]
        
        db_types = list(self.database_adapters.keys())
        
        for source_db in db_types:
            compatibility_matrix[source_db.value] = {}
            
            for target_db in db_types:
                try:
                    if source_db == target_db:
                        compatibility_matrix[source_db.value][target_db.value] = True
                        continue
                    
                    # Test query translation and execution
                    translation_success = await self._test_query_translation(
                        source_db, target_db, test_queries
                    )
                    
                    compatibility_matrix[source_db.value][target_db.value] = translation_success
                    
                    if not translation_success:
                        errors.append(f"Cross-database compatibility failed: {source_db.value} -> {target_db.value}")
                        
                except Exception as e:
                    errors.append(f"Cross-database compatibility error: {source_db.value} -> {target_db.value}: {e}")
                    compatibility_matrix[source_db.value][target_db.value] = False
        
        # Update global compatibility matrix
        self.cross_database_compatibility_matrix = compatibility_matrix
        
        # Calculate overall success
        all_translations = [
            result for db_results in compatibility_matrix.values() 
            for result in db_results.values()
        ]
        success = all(all_translations) and len(errors) == 0
        
        return {
            "success": success,
            "compatibility_matrix": compatibility_matrix,
            "errors": errors
        }
    
    async def _test_query_translation(
        self, 
        source_db: DatabaseType, 
        target_db: DatabaseType, 
        test_queries: List[str]
    ) -> bool:
        """Test query translation between two database types"""
        try:
            target_adapter = self.database_adapters[target_db]
            
            for query in test_queries:
                # Translate query
                translation_result = self.query_translator.translate(
                    query, target_db, source_database=source_db
                )
                
                if not translation_result.success:
                    logger.warning(f"Query translation failed: {source_db.value} -> {target_db.value}")
                    return False
                
                # Test execution of translated query
                execution_result = await target_adapter.execute_query(translation_result.translated_query)
                
                if not execution_result.success:
                    logger.warning(f"Translated query execution failed: {source_db.value} -> {target_db.value}")
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Query translation test failed: {source_db.value} -> {target_db.value}: {e}")
            return False
    
    async def _validate_database_performance(self, blueprint: SystemBlueprint) -> Dict[str, Any]:
        """Validate database performance meets requirements"""
        logger.debug("Validating database performance")
        
        performance_results = {}
        warnings = []
        metrics = {}
        
        for db_type, adapter in self.database_adapters.items():
            try:
                # Test query performance
                perf_result = await self._test_database_performance(adapter, db_type)
                performance_results[db_type.value] = perf_result["success"]
                metrics[db_type.value] = perf_result["metrics"]
                
                if not perf_result["success"]:
                    warnings.extend(perf_result.get("warnings", []))
                    
            except Exception as e:
                warnings.append(f"Performance validation error for {db_type.value}: {e}")
                performance_results[db_type.value] = False
        
        # Check optimizer performance
        if self.performance_optimizer:
            optimizer_stats = self.performance_optimizer.get_performance_report()
            metrics["optimizer"] = optimizer_stats
            
            # Validate cache hit rate
            cache_hit_rate = optimizer_stats["cache_statistics"]["hit_rate"]
            if cache_hit_rate < self.database_config.performance_thresholds["min_cache_hit_rate"]:
                warnings.append(f"Cache hit rate {cache_hit_rate:.2%} below threshold")
        
        success = all(performance_results.values()) and len(warnings) == 0
        
        return {
            "success": success,
            "performance_results": performance_results,
            "metrics": metrics,
            "warnings": warnings
        }
    
    async def _test_database_performance(self, adapter: DatabaseAdapter, db_type: DatabaseType) -> Dict[str, Any]:
        """Test performance for specific database adapter"""
        try:
            # Test query execution time
            start_time = time.time()
            result = await adapter.execute_query("SELECT 1 as performance_test")
            query_time = time.time() - start_time
            
            # Test transaction time
            tx_start = time.time()
            tx_id = await adapter.begin_transaction()
            await adapter.execute_query("SELECT 1 as tx_test", transaction_id=tx_id)
            await adapter.commit_transaction(tx_id)
            tx_time = time.time() - tx_start
            
            # Check against thresholds
            warnings = []
            max_query_time = self.database_config.performance_thresholds["max_query_time"]
            max_tx_time = self.database_config.performance_thresholds["max_transaction_time"]
            
            if query_time > max_query_time:
                warnings.append(f"{db_type.value} query time {query_time:.3f}s exceeds threshold {max_query_time}s")
            
            if tx_time > max_tx_time:
                warnings.append(f"{db_type.value} transaction time {tx_time:.3f}s exceeds threshold {max_tx_time}s")
            
            return {
                "success": len(warnings) == 0,
                "metrics": {
                    "query_time": query_time,
                    "transaction_time": tx_time,
                    "query_success": result.success
                },
                "warnings": warnings
            }
            
        except Exception as e:
            return {
                "success": False,
                "metrics": {},
                "warnings": [f"Performance test failed: {e}"]
            }
    
    async def _enhanced_database_healing(self, blueprint: SystemBlueprint, validation_result: DatabaseValidationResult) -> 'DatabaseHealingResult':
        """Enhanced database healing when validation fails"""
        logger.info("Executing enhanced database healing")
        
        healing_actions = []
        healed_blueprint = blueprint  # In real implementation, this would be modified
        
        try:
            # Schema healing
            if not validation_result.schema_validation_passed:
                schema_healing = await self._heal_database_schemas()
                healing_actions.extend(schema_healing)
            
            # Transaction healing
            if not validation_result.transaction_validation_passed:
                transaction_healing = await self._heal_transaction_issues()
                healing_actions.extend(transaction_healing)
            
            # Performance healing
            if not validation_result.performance_validation_passed:
                performance_healing = await self._heal_performance_issues()
                healing_actions.extend(performance_healing)
            
            # Cross-database healing
            if not validation_result.cross_database_validation_passed:
                cross_db_healing = await self._heal_cross_database_issues()
                healing_actions.extend(cross_db_healing)
            
            success = len(healing_actions) > 0
            
            return DatabaseHealingResult(
                success=success,
                healing_actions=healing_actions,
                healed_blueprint=healed_blueprint
            )
            
        except Exception as e:
            logger.error(f"Database healing failed: {e}")
            return DatabaseHealingResult(
                success=False,
                healing_actions=[],
                healed_blueprint=blueprint,
                error=str(e)
            )
    
    async def _heal_database_schemas(self) -> List[str]:
        """Heal database schema issues"""
        healing_actions = []
        
        for db_type, schema_coordinator in self.schema_coordinators.items():
            try:
                # Attempt schema recreation
                await schema_coordinator.validate_or_create_schema()
                healing_actions.append(f"Recreated schema for {db_type.value}")
                
            except Exception as e:
                logger.warning(f"Schema healing failed for {db_type.value}: {e}")
        
        return healing_actions
    
    async def _heal_transaction_issues(self) -> List[str]:
        """Heal transaction-related issues"""
        healing_actions = []
        
        for db_type, tx_manager in self.transaction_managers.items():
            try:
                # Clean up any stuck transactions
                await tx_manager.cleanup()
                healing_actions.append(f"Cleaned up transactions for {db_type.value}")
                
            except Exception as e:
                logger.warning(f"Transaction healing failed for {db_type.value}: {e}")
        
        return healing_actions
    
    async def _heal_performance_issues(self) -> List[str]:
        """Heal performance-related issues"""
        healing_actions = []
        
        try:
            # Clear performance optimizer cache
            if self.performance_optimizer:
                self.performance_optimizer.invalidate_cache()
                healing_actions.append("Cleared performance optimizer cache")
            
            # Reconnect adapters
            for db_type, adapter in self.database_adapters.items():
                try:
                    await adapter.disconnect()
                    await adapter.connect()
                    healing_actions.append(f"Reconnected {db_type.value} adapter")
                except Exception as e:
                    logger.warning(f"Adapter reconnection failed for {db_type.value}: {e}")
                    
        except Exception as e:
            logger.warning(f"Performance healing failed: {e}")
        
        return healing_actions
    
    async def _heal_cross_database_issues(self) -> List[str]:
        """Heal cross-database compatibility issues"""
        healing_actions = []
        
        try:
            # Clear query translation cache
            for translator in self.query_translator.translators.values():
                translator.translation_cache.clear()
            
            healing_actions.append("Cleared query translation cache")
            
        except Exception as e:
            logger.warning(f"Cross-database healing failed: {e}")
        
        return healing_actions
    
    async def _finalize_system_generation_with_database(self, blueprint: SystemBlueprint, level4_result: ValidationResult) -> Dict[str, Any]:
        """Finalize system generation with database integration"""
        logger.info("Finalizing system generation with database integration")
        
        # Get base system generation result
        base_result = await super()._finalize_system_generation(blueprint, level4_result)
        
        # Add database integration information
        database_info = {
            "enabled_databases": [db.value for db in self.database_config.enabled_databases],
            "database_adapters": {
                db.value: {
                    "connection_id": adapter.connection_id,
                    "state": adapter.state.value,
                    "statistics": adapter.get_adapter_statistics()
                }
                for db, adapter in self.database_adapters.items()
            },
            "validation_results": [
                {
                    "success": result.success,
                    "validation_level": result.validation_level.value,
                    "execution_time": result.execution_time,
                    "performance_metrics": result.performance_metrics
                }
                for result in self.database_validation_results
            ],
            "cross_database_compatibility": self.cross_database_compatibility_matrix,
            "performance_optimizer_stats": (
                self.performance_optimizer.get_performance_report() 
                if self.performance_optimizer else None
            )
        }
        
        # Merge with base result
        base_result["database_integration"] = database_info
        
        return base_result
    
    async def cleanup_database_integration(self):
        """Cleanup database integration components"""
        logger.info("Cleaning up database integration")
        
        try:
            # Cleanup transaction managers
            for tx_manager in self.transaction_managers.values():
                await tx_manager.cleanup()
            
            # Cleanup database factory
            if self.database_factory and hasattr(self.database_factory, 'shutdown'):
                await self.database_factory.shutdown()
            
            # Clear caches
            if self.performance_optimizer:
                self.performance_optimizer.invalidate_cache()
            
            logger.info("Database integration cleanup complete")
            
        except Exception as e:
            logger.error(f"Database integration cleanup failed: {e}")


@dataclass
class DatabaseHealingResult:
    """Result of database healing operations"""
    success: bool
    healing_actions: List[str]
    healed_blueprint: SystemBlueprint
    error: Optional[str] = None


# Test harness
if __name__ == "__main__":
    async def test_database_orchestrator_integration():
        """Test database-integrated orchestrator"""
        
        print("🔧 Testing Database-Integrated ValidationDrivenOrchestrator...")
        
        # Create test configuration
        db_config = DatabaseValidationConfig(
            enabled_databases=[DatabaseType.POSTGRESQL, DatabaseType.SQLITE],
            schema_validation_enabled=True,
            transaction_validation_enabled=True,
            cross_database_validation_enabled=True,
            performance_validation_enabled=True
        )
        
        # Create orchestrator
        orchestrator = DatabaseIntegratedOrchestrator(db_config)
        
        try:
            # Initialize database integration
            await orchestrator.initialize_database_integration()
            print("✅ Database integration initialized")
            
            # Create mock blueprint
            blueprint = SystemBlueprint(
                name="test_system",
                version="1.0.0",
                components=[],
                metadata={}
            )
            
            # Test database validation
            validation_result = await orchestrator._validate_database_integration(blueprint)
            print(f"✅ Database validation: {'PASS' if validation_result.success else 'FAIL'}")
            
            if validation_result.performance_metrics:
                print(f"   Performance metrics: {validation_result.performance_metrics}")
            
            # Test enhanced system generation
            system_result = await orchestrator.generate_system_with_validation(blueprint)
            print("✅ Enhanced system generation completed")
            
            if "database_integration" in system_result:
                db_info = system_result["database_integration"]
                print(f"   Enabled databases: {db_info['enabled_databases']}")
                print(f"   Validation results: {len(db_info['validation_results'])}")
            
            # Cleanup
            await orchestrator.cleanup_database_integration()
            print("✅ Database integration cleanup successful")
            
        except Exception as e:
            print(f"❌ Database orchestrator integration test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_database_orchestrator_integration())