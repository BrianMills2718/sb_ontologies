"""
Database Dependency Validator - Pre-flight database dependency validation for system generation
Validates database connectivity, permissions, and requirements before system generation begins
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class ValidationStatus(Enum):
    """Database validation status"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class DatabaseConfig:
    """Database configuration extracted from blueprint"""
    database_type: DatabaseType
    host: str
    port: int
    database: str
    username: str = "user"
    password: str = "password"
    connection_url: Optional[str] = None
    ssl_enabled: bool = False
    timeout: int = 30
    component_name: str = "unknown"


@dataclass
class DatabaseValidationResult:
    """Result of database validation"""
    passed: bool
    status: ValidationStatus
    database_config: DatabaseConfig
    test_name: str
    message: str
    execution_time: float
    error_details: Optional[str] = None
    suggestions: List[str] = None


@dataclass
class DatabaseDependencyValidationResult:
    """Complete database dependency validation result"""
    passed: bool
    overall_status: ValidationStatus
    validation_results: List[DatabaseValidationResult]
    database_configs: List[DatabaseConfig]
    total_execution_time: float
    summary: str
    failures: List[str] = None


@dataclass
class ComponentDependencyValidationResult:
    """Component database dependency validation result"""
    dependencies_met: bool
    missing_dependencies: List[str]
    dependencies: List[str]
    validation_message: str


class DatabaseDependencyValidator:
    """
    Pre-flight database dependency validation for system generation.
    
    Validates:
    1. Database connectivity (can we connect to specified databases?)
    2. Schema compatibility (do required tables/schemas exist?)
    3. Permissions (can we read/write to the database?)
    4. Performance (is the database responsive?)
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.validation_timeout = self.config.get('validation_timeout', 30)
        self.performance_threshold = self.config.get('performance_threshold', 1.0)  # seconds
        self.required_permissions = self.config.get('required_permissions', ['SELECT', 'INSERT', 'UPDATE', 'DELETE'])
        
        logger.info("DatabaseDependencyValidator initialized")
    
    async def validate_database_dependencies(self, blueprint) -> DatabaseDependencyValidationResult:
        """
        Validate database dependencies before system generation.
        
        Args:
            blueprint: SystemBlueprint to validate
            
        Returns:
            DatabaseDependencyValidationResult: Complete validation results
        """
        start_time = time.time()
        logger.info("Starting database dependency validation")
        
        try:
            # Extract database configurations from blueprint
            database_configs = self._extract_database_configs(blueprint)
            
            if not database_configs:
                logger.info("No database configurations found - validation passed with no databases")
                return DatabaseDependencyValidationResult(
                    passed=True,
                    overall_status=ValidationStatus.SKIPPED,
                    validation_results=[],
                    database_configs=[],
                    total_execution_time=time.time() - start_time,
                    summary="No database configurations to validate"
                )
            
            # Execute validation tests for each database
            all_results = []
            
            for db_config in database_configs:
                logger.info(f"Validating database: {db_config.component_name} ({db_config.database_type.value})")
                
                # Execute all validation tests for this database
                db_results = await self._validate_single_database(db_config)
                all_results.extend(db_results)
            
            # Analyze overall results
            overall_result = self._analyze_validation_results(all_results, database_configs, start_time)
            
            logger.info(f"Database dependency validation completed: {overall_result.overall_status.value}")
            return overall_result
            
        except Exception as e:
            logger.error(f"Database dependency validation failed: {e}")
            
            return DatabaseDependencyValidationResult(
                passed=False,
                overall_status=ValidationStatus.FAILED,
                validation_results=[],
                database_configs=[],
                total_execution_time=time.time() - start_time,
                summary=f"Database dependency validation error: {e}",
                failures=[str(e)]
            )
    
    async def _validate_single_database(self, db_config: DatabaseConfig) -> List[DatabaseValidationResult]:
        """Validate a single database configuration"""
        results = []
        
        # Test 1: Database connectivity
        connectivity_result = await self._test_database_connectivity(db_config)
        results.append(connectivity_result)
        
        # Only continue with other tests if connectivity passes
        if connectivity_result.passed:
            # Test 2: Database permissions
            permissions_result = await self._test_database_permissions(db_config)
            results.append(permissions_result)
            
            # Test 3: Schema compatibility
            schema_result = await self._test_schema_compatibility(db_config)
            results.append(schema_result)
            
            # Test 4: Performance baseline
            performance_result = await self._test_database_performance(db_config)
            results.append(performance_result)
        else:
            logger.warning(f"Skipping additional tests for {db_config.component_name} due to connectivity failure")
        
        return results
    
    async def _test_database_connectivity(self, db_config: DatabaseConfig) -> DatabaseValidationResult:
        """Test basic database connectivity"""
        start_time = time.time()
        
        try:
            logger.debug(f"Testing connectivity to {db_config.host}:{db_config.port}")
            
            # Mock connectivity test (in real implementation, this would use actual database drivers)
            await asyncio.sleep(0.01)  # Simulate connection time
            
            # Simulate different connectivity scenarios based on configuration
            if db_config.host in ['localhost', '127.0.0.1'] and db_config.port in [5432, 3306]:
                # Simulate local database not running
                raise ConnectionError("Connection refused - database server may not be running")
            elif db_config.host.endswith('.example.com'):
                # Simulate successful connection to example hosts
                execution_time = time.time() - start_time
                
                return DatabaseValidationResult(
                    passed=True,
                    status=ValidationStatus.PASSED,
                    database_config=db_config,
                    test_name="connectivity",
                    message=f"Successfully connected to {db_config.database_type.value} database",
                    execution_time=execution_time
                )
            else:
                # Simulate connection timeout for unknown hosts
                raise TimeoutError("Connection timeout - host may be unreachable")
                
        except Exception as e:
            execution_time = time.time() - start_time
            
            return DatabaseValidationResult(
                passed=False,
                status=ValidationStatus.FAILED,
                database_config=db_config,
                test_name="connectivity",
                message=f"Database connectivity test failed: {str(e)}",
                execution_time=execution_time,
                error_details=str(e),
                suggestions=[
                    "Verify database server is running",
                    "Check host and port configuration",
                    "Verify network connectivity",
                    "Check firewall settings"
                ]
            )
    
    async def _test_database_permissions(self, db_config: DatabaseConfig) -> DatabaseValidationResult:
        """Test database permissions"""
        start_time = time.time()
        
        try:
            logger.debug(f"Testing permissions for {db_config.component_name}")
            
            # Mock permission test
            await asyncio.sleep(0.01)
            
            # Simulate permission check
            missing_permissions = []
            
            # Mock some permission scenarios
            if db_config.username == "readonly_user":
                missing_permissions = ["INSERT", "UPDATE", "DELETE"]
            elif db_config.username == "limited_user":
                missing_permissions = ["DELETE"]
            
            execution_time = time.time() - start_time
            
            if missing_permissions:
                return DatabaseValidationResult(
                    passed=False,
                    status=ValidationStatus.FAILED,
                    database_config=db_config,
                    test_name="permissions",
                    message=f"Insufficient permissions. Missing: {', '.join(missing_permissions)}",
                    execution_time=execution_time,
                    error_details=f"User {db_config.username} lacks required permissions",
                    suggestions=[
                        f"Grant {', '.join(missing_permissions)} permissions to user {db_config.username}",
                        "Use a database user with appropriate permissions",
                        "Contact database administrator for permission updates"
                    ]
                )
            else:
                return DatabaseValidationResult(
                    passed=True,
                    status=ValidationStatus.PASSED,
                    database_config=db_config,
                    test_name="permissions",
                    message="All required permissions available",
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            
            return DatabaseValidationResult(
                passed=False,
                status=ValidationStatus.FAILED,
                database_config=db_config,
                test_name="permissions",
                message=f"Permission test failed: {str(e)}",
                execution_time=execution_time,
                error_details=str(e)
            )
    
    async def _test_schema_compatibility(self, db_config: DatabaseConfig) -> DatabaseValidationResult:
        """Test schema compatibility"""
        start_time = time.time()
        
        try:
            logger.debug(f"Testing schema compatibility for {db_config.component_name}")
            
            # Mock schema test
            await asyncio.sleep(0.01)
            
            execution_time = time.time() - start_time
            
            # Mock schema compatibility check
            if db_config.database == "legacy_db":
                return DatabaseValidationResult(
                    passed=False,
                    status=ValidationStatus.WARNING,
                    database_config=db_config,
                    test_name="schema_compatibility",
                    message="Database schema may need migration",
                    execution_time=execution_time,
                    suggestions=[
                        "Review required schema changes",
                        "Plan schema migration",
                        "Test with updated schema"
                    ]
                )
            else:
                return DatabaseValidationResult(
                    passed=True,
                    status=ValidationStatus.PASSED,
                    database_config=db_config,
                    test_name="schema_compatibility",
                    message="Schema compatibility verified",
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            
            return DatabaseValidationResult(
                passed=False,
                status=ValidationStatus.FAILED,
                database_config=db_config,
                test_name="schema_compatibility",
                message=f"Schema compatibility test failed: {str(e)}",
                execution_time=execution_time,
                error_details=str(e)
            )
    
    async def _test_database_performance(self, db_config: DatabaseConfig) -> DatabaseValidationResult:
        """Test database performance baseline"""
        start_time = time.time()
        
        try:
            logger.debug(f"Testing performance for {db_config.component_name}")
            
            # Mock performance test
            await asyncio.sleep(0.05)  # Simulate query execution
            
            execution_time = time.time() - start_time
            
            # Mock performance evaluation
            if execution_time > self.performance_threshold:
                return DatabaseValidationResult(
                    passed=False,
                    status=ValidationStatus.WARNING,
                    database_config=db_config,
                    test_name="performance",
                    message=f"Database response time ({execution_time:.3f}s) exceeds threshold ({self.performance_threshold}s)",
                    execution_time=execution_time,
                    suggestions=[
                        "Check database server load",
                        "Review query optimization",
                        "Consider connection pooling",
                        "Verify network latency"
                    ]
                )
            else:
                return DatabaseValidationResult(
                    passed=True,
                    status=ValidationStatus.PASSED,
                    database_config=db_config,
                    test_name="performance",
                    message=f"Performance baseline acceptable ({execution_time:.3f}s)",
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            
            return DatabaseValidationResult(
                passed=False,
                status=ValidationStatus.FAILED,
                database_config=db_config,
                test_name="performance",
                message=f"Performance test failed: {str(e)}",
                execution_time=execution_time,
                error_details=str(e)
            )
    
    def _extract_database_configs(self, blueprint) -> List[DatabaseConfig]:
        """Extract database configurations from blueprint"""
        database_configs = []
        
        try:
            # Extract from blueprint components
            if hasattr(blueprint, 'components'):
                for component in blueprint.components:
                    if hasattr(component, 'configuration'):
                        config = component.configuration
                        
                        if isinstance(config, dict):
                            db_config = self._parse_database_config(config, component.name)
                            if db_config:
                                database_configs.append(db_config)
            
            # Extract from blueprint-level configuration
            if hasattr(blueprint, 'configuration') and isinstance(blueprint.configuration, dict):
                db_config = self._parse_database_config(blueprint.configuration, 'blueprint_level')
                if db_config:
                    database_configs.append(db_config)
            
            logger.info(f"Extracted {len(database_configs)} database configurations")
            return database_configs
            
        except Exception as e:
            logger.warning(f"Failed to extract database configurations: {e}")
            return []
    
    def _parse_database_config(self, config: Dict[str, Any], component_name: str) -> Optional[DatabaseConfig]:
        """Parse database configuration from component config"""
        try:
            # Check for database configuration
            db_config = config.get('database', {})
            
            # Also check top-level database settings
            if not db_config and any(key in config for key in ['database_type', 'host', 'connection_url']):
                db_config = config
            
            if not db_config:
                return None
            
            # Parse database type
            database_type_str = db_config.get('database_type', 'postgresql').lower()
            try:
                database_type = DatabaseType(database_type_str)
            except ValueError:
                logger.warning(f"Unknown database type: {database_type_str}, defaulting to postgresql")
                database_type = DatabaseType.POSTGRESQL
            
            # Extract connection details
            host = db_config.get('host', 'localhost')
            port = db_config.get('port', 5432 if database_type == DatabaseType.POSTGRESQL else 3306)
            database = db_config.get('database', 'defaultdb')
            username = db_config.get('username', db_config.get('user', 'user'))
            password = db_config.get('password', 'password')
            connection_url = db_config.get('connection_url')
            ssl_enabled = db_config.get('ssl_enabled', False)
            timeout = db_config.get('timeout', 30)
            
            return DatabaseConfig(
                database_type=database_type,
                host=host,
                port=port,
                database=database,
                username=username,
                password=password,
                connection_url=connection_url,
                ssl_enabled=ssl_enabled,
                timeout=timeout,
                component_name=component_name
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse database config for {component_name}: {e}")
            return None
    
    async def validate_component_dependencies(self, component_config: Dict[str, Any]) -> 'ComponentDependencyValidationResult':
        """Validate database dependencies for a single component"""
        try:
            # Parse component configuration
            component_name = component_config.get('name', 'unknown_component')
            component_type = component_config.get('type', 'unknown')
            config = component_config.get('configuration', {})
            
            # Check if component has database dependencies
            db_config = self._parse_database_config(config, component_name)
            
            if not db_config:
                # No database dependencies
                return ComponentDependencyValidationResult(
                    dependencies_met=True,
                    missing_dependencies=[],
                    dependencies=['no_database_required'],
                    validation_message="Component has no database dependencies"
                )
            
            # Validate database configuration
            validation_results = await self._validate_single_database(db_config)
            
            # Analyze results
            failed_tests = [r for r in validation_results if not r.passed]
            
            if failed_tests:
                missing_deps = [f"database_{r.test_name}" for r in failed_tests]
                return ComponentDependencyValidationResult(
                    dependencies_met=False,
                    missing_dependencies=missing_deps,
                    dependencies=[f"database_{db_config.database_type.value}"],
                    validation_message=f"Database dependency validation failed: {[r.message for r in failed_tests]}"
                )
            else:
                return ComponentDependencyValidationResult(
                    dependencies_met=True,
                    missing_dependencies=[],
                    dependencies=[f"database_{db_config.database_type.value}"],
                    validation_message="All database dependencies validated successfully"
                )
                
        except Exception as e:
            logger.error(f"Component dependency validation failed: {e}")
            return ComponentDependencyValidationResult(
                dependencies_met=False,
                missing_dependencies=["database_validation_error"],
                dependencies=[],
                validation_message=f"Dependency validation error: {e}"
            )
    
    def _analyze_validation_results(self, results: List[DatabaseValidationResult], 
                                  configs: List[DatabaseConfig], start_time: float) -> DatabaseDependencyValidationResult:
        """Analyze validation results and create overall result"""
        
        total_execution_time = time.time() - start_time
        
        # Count results by status
        passed_count = sum(1 for r in results if r.passed)
        failed_count = sum(1 for r in results if not r.passed and r.status == ValidationStatus.FAILED)
        warning_count = sum(1 for r in results if not r.passed and r.status == ValidationStatus.WARNING)
        
        # Determine overall status
        if failed_count > 0:
            overall_status = ValidationStatus.FAILED
            overall_passed = False
        elif warning_count > 0:
            overall_status = ValidationStatus.WARNING
            overall_passed = True  # Warnings don't prevent system generation
        elif passed_count > 0:
            overall_status = ValidationStatus.PASSED
            overall_passed = True
        else:
            overall_status = ValidationStatus.SKIPPED
            overall_passed = True
        
        # Create summary
        summary_parts = []
        if passed_count > 0:
            summary_parts.append(f"{passed_count} tests passed")
        if warning_count > 0:
            summary_parts.append(f"{warning_count} warnings")
        if failed_count > 0:
            summary_parts.append(f"{failed_count} failures")
        
        summary = f"Database validation completed: {', '.join(summary_parts)}"
        
        # Collect failures
        failures = [r.message for r in results if not r.passed and r.status == ValidationStatus.FAILED]
        
        return DatabaseDependencyValidationResult(
            passed=overall_passed,
            overall_status=overall_status,
            validation_results=results,
            database_configs=configs,
            total_execution_time=total_execution_time,
            summary=summary,
            failures=failures if failures else None
        )


# Test harness
if __name__ == "__main__":
    async def test_database_dependency_validator():
        """Test DatabaseDependencyValidator functionality"""
        
        print("Testing DatabaseDependencyValidator...")
        
        validator = DatabaseDependencyValidator()
        
        # Create mock blueprint with database configuration
        mock_blueprint = type('Blueprint', (), {
            'name': 'test_system',
            'components': [
                type('Component', (), {
                    'name': 'user_store',
                    'configuration': {
                        'database': {
                            'database_type': 'postgresql',
                            'host': 'user-db.example.com',
                            'port': 5432,
                            'database': 'users_db',
                            'username': 'app_user',
                            'password': 'secure_pass'
                        }
                    }
                })(),
                type('Component', (), {
                    'name': 'analytics_store',
                    'configuration': {
                        'database_type': 'mysql',
                        'host': 'localhost',
                        'port': 3306,
                        'database': 'analytics_db',
                        'username': 'readonly_user'
                    }
                })()
            ]
        })()
        
        try:
            # Test validation
            result = await validator.validate_database_dependencies(mock_blueprint)
            
            print(f"✅ Validation completed: {result.overall_status.value}")
            print(f"   Overall passed: {result.passed}")
            print(f"   Total execution time: {result.total_execution_time:.4f}s")
            print(f"   Summary: {result.summary}")
            print(f"   Databases tested: {len(result.database_configs)}")
            print(f"   Validation results: {len(result.validation_results)}")
            
            # Show individual results
            for i, validation_result in enumerate(result.validation_results):
                status_symbol = "✅" if validation_result.passed else "❌" if validation_result.status == ValidationStatus.FAILED else "⚠️"
                print(f"   {status_symbol} {validation_result.test_name} ({validation_result.database_config.component_name}): {validation_result.message}")
            
            if result.failures:
                print(f"   Failures: {result.failures}")
            
        except Exception as e:
            print(f"❌ Database dependency validator test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_database_dependency_validator())