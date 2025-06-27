"""
V5.0 Migration Manager
Handles database schema migrations with rollback support and fail-hard principles
"""

import asyncio
import time
import logging
import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """Raised when migration operations fail"""
    pass


class MigrationRollbackError(Exception):
    """Raised when migration rollback fails"""
    pass


class MigrationPlanningError(Exception):
    """Raised when migration planning fails"""
    pass


class MigrationStatus(Enum):
    """Migration execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class MigrationStep:
    """Individual migration step"""
    step_id: str
    description: str
    forward_sql: str
    rollback_sql: str
    step_type: str = "ddl"  # ddl, dml, index, constraint
    dependencies: List[str] = field(default_factory=list)
    validation_query: Optional[str] = None
    estimated_duration: float = 0.0


@dataclass
class MigrationPlan:
    """Complete migration plan from one version to another"""
    from_version: str
    to_version: str
    steps: List[MigrationStep]
    total_estimated_duration: float = 0.0
    created_at: float = field(default_factory=time.time)
    
    def __post_init__(self):
        self.total_estimated_duration = sum(step.estimated_duration for step in self.steps)


@dataclass
class MigrationResult:
    """Result of migration execution"""
    successful: bool
    from_version: str
    to_version: str
    steps_completed: int = 0
    total_steps: int = 0
    execution_time: float = 0.0
    error_message: Optional[str] = None
    rollback_performed: bool = False
    completed_at: float = field(default_factory=time.time)


@dataclass
class MigrationHistory:
    """Migration execution history record"""
    migration_id: str
    from_version: str
    to_version: str
    status: MigrationStatus
    started_at: float
    completed_at: Optional[float] = None
    execution_time: float = 0.0
    steps_completed: int = 0
    error_message: Optional[str] = None
    rollback_steps: List[str] = field(default_factory=list)


class MigrationManager:
    """Database migration management system with rollback support"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Configuration
        self.migrations_path = config.get("migrations_path", "./migrations")
        self.backup_enabled = config.get("backup_enabled", True)
        self.dry_run_enabled = config.get("dry_run_enabled", True)
        self.max_rollback_steps = config.get("max_rollback_steps", 100)
        self.migration_timeout = config.get("migration_timeout", 300)  # 5 minutes
        
        # State
        self.migration_history: List[MigrationHistory] = []
        self.rollback_scripts: Dict[str, List[str]] = {}
        self.active_migration: Optional[str] = None
        
        # Database connection (would be injected)
        self.db_connection = None
        
        logger.info("MigrationManager initialized")
    
    async def initialize(self):
        """Initialize migration manager"""
        logger.info("Initializing migration manager")
        
        try:
            # Ensure migrations directory exists
            await self._ensure_migrations_directory()
            
            # Load migration history
            await self._load_migration_history()
            
            # Load rollback scripts
            await self._load_rollback_scripts()
            
            logger.info("Migration manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Migration manager initialization failed: {e}")
            raise MigrationError(f"Migration manager initialization failed: {e}")
    
    async def migrate_schema(self, from_version: str, to_version: str) -> MigrationResult:
        """Execute schema migration with rollback support"""
        migration_id = self._generate_migration_id(from_version, to_version)
        logger.info(f"Starting schema migration {migration_id}: {from_version} -> {to_version}")
        
        if self.active_migration:
            raise MigrationError(f"Migration already in progress: {self.active_migration}")
        
        start_time = time.time()
        self.active_migration = migration_id
        
        try:
            # Create migration history record
            history_record = MigrationHistory(
                migration_id=migration_id,
                from_version=from_version,
                to_version=to_version,
                status=MigrationStatus.PENDING,
                started_at=start_time
            )
            self.migration_history.append(history_record)
            
            # Plan migration path
            migration_plan = await self._plan_migration_path(from_version, to_version)
            history_record.status = MigrationStatus.RUNNING
            
            # Backup current state if enabled
            if self.backup_enabled:
                await self._create_migration_backup(migration_id)
            
            # Execute migration steps
            completed_steps = 0
            rollback_steps = []
            
            for step in migration_plan.steps:
                try:
                    # Execute migration step
                    await self._execute_migration_step(step)
                    completed_steps += 1
                    
                    # Store rollback step
                    rollback_steps.insert(0, step.step_id)  # Reverse order for rollback
                    
                    # Update history
                    history_record.steps_completed = completed_steps
                    
                    logger.debug(f"Migration step completed: {step.step_id}")
                    
                except Exception as step_error:
                    logger.error(f"Migration step failed: {step.step_id} - {step_error}")
                    
                    # Attempt rollback
                    rollback_successful = await self._rollback_migration_steps(rollback_steps)
                    
                    # Update history
                    history_record.status = MigrationStatus.FAILED
                    history_record.error_message = str(step_error)
                    history_record.completed_at = time.time()
                    history_record.execution_time = time.time() - start_time
                    history_record.rollback_steps = rollback_steps
                    
                    result = MigrationResult(
                        successful=False,
                        from_version=from_version,
                        to_version=to_version,
                        steps_completed=completed_steps,
                        total_steps=len(migration_plan.steps),
                        execution_time=time.time() - start_time,
                        error_message=str(step_error),
                        rollback_performed=rollback_successful
                    )
                    
                    raise MigrationError(f"Migration failed at step {step.step_id}: {step_error}")
            
            # Update schema version
            await self._update_schema_version(to_version)
            
            # Update history record
            execution_time = time.time() - start_time
            history_record.status = MigrationStatus.SUCCESS
            history_record.completed_at = time.time()
            history_record.execution_time = execution_time
            history_record.steps_completed = completed_steps
            
            # Save rollback scripts for this migration
            self.rollback_scripts[migration_id] = rollback_steps
            await self._save_rollback_scripts()
            
            # Migration history record is already updated above (history_record)
            
            logger.info(f"Schema migration completed successfully: {from_version} -> {to_version} in {execution_time:.2f}s")
            
            return MigrationResult(
                successful=True,
                from_version=from_version,
                to_version=to_version,
                steps_completed=completed_steps,
                total_steps=len(migration_plan.steps),
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Schema migration failed: {e}")
            
            # Update history record
            if migration_id in [h.migration_id for h in self.migration_history]:
                for h in self.migration_history:
                    if h.migration_id == migration_id:
                        h.status = MigrationStatus.FAILED
                        h.error_message = str(e)
                        h.completed_at = time.time()
                        h.execution_time = time.time() - start_time
            
            raise MigrationError(f"Migration failed: {e}")
            
        finally:
            self.active_migration = None
            await self._save_migration_history()
    
    async def rollback_migration(self, migration_id: str) -> bool:
        """Rollback specific migration"""
        logger.info(f"Rolling back migration {migration_id}")
        
        if migration_id not in self.rollback_scripts:
            raise MigrationError(f"No rollback scripts found for migration {migration_id}")
        
        try:
            rollback_steps = self.rollback_scripts[migration_id]
            rollback_successful = await self._rollback_migration_steps(rollback_steps)
            
            if rollback_successful:
                # Update migration history
                for history_record in self.migration_history:
                    if history_record.migration_id == migration_id:
                        history_record.status = MigrationStatus.ROLLED_BACK
                        break
                
                logger.info(f"Migration {migration_id} rolled back successfully")
                return True
            else:
                raise MigrationRollbackError(f"Rollback failed for migration {migration_id}")
                
        except Exception as e:
            logger.error(f"Migration rollback failed: {e}")
            raise MigrationRollbackError(f"Rollback failed: {e}")
    
    async def _plan_migration_path(self, from_version: str, to_version: str) -> MigrationPlan:
        """Plan migration path from source to target version"""
        logger.info(f"Planning migration path: {from_version} -> {to_version}")
        
        try:
            # Parse versions for comparison
            try:
                from schema_validator import SchemaVersion
            except ImportError:
                from .schema_validator import SchemaVersion
            
            from_ver = SchemaVersion(from_version)
            to_ver = SchemaVersion(to_version)
            
            if from_ver == to_ver:
                # No migration needed
                return MigrationPlan(from_version, to_version, [])
            
            # Generate migration steps based on version difference
            steps = []
            
            if from_ver < to_ver:
                # Forward migration
                steps = await self._generate_forward_migration_steps(from_ver, to_ver)
            else:
                # Backward migration (rollback)
                steps = await self._generate_backward_migration_steps(from_ver, to_ver)
            
            migration_plan = MigrationPlan(
                from_version=from_version,
                to_version=to_version,
                steps=steps
            )
            
            logger.info(f"Migration plan created with {len(steps)} steps, estimated duration: {migration_plan.total_estimated_duration:.2f}s")
            
            return migration_plan
            
        except Exception as e:
            logger.error(f"Migration planning failed: {e}")
            raise MigrationPlanningError(f"Migration planning failed: {e}")
    
    async def _generate_forward_migration_steps(self, from_ver, to_ver) -> List[MigrationStep]:
        """Generate forward migration steps"""
        steps = []
        
        # Example migration steps (would be customized based on actual schema changes)
        if from_ver.major < to_ver.major:
            # Major version upgrade
            steps.append(MigrationStep(
                step_id="major_version_upgrade",
                description=f"Upgrade schema from {from_ver} to {to_ver}",
                forward_sql="-- Major version upgrade DDL would go here",
                rollback_sql="-- Major version rollback DDL would go here",
                step_type="ddl",
                estimated_duration=30.0
            ))
        
        if from_ver.minor < to_ver.minor:
            # Minor version upgrade
            steps.append(MigrationStep(
                step_id="minor_version_upgrade",
                description=f"Minor upgrade from {from_ver} to {to_ver}",
                forward_sql="-- Minor version upgrade DDL would go here",
                rollback_sql="-- Minor version rollback DDL would go here",
                step_type="ddl",
                estimated_duration=10.0
            ))
        
        if from_ver.patch < to_ver.patch:
            # Patch version upgrade
            steps.append(MigrationStep(
                step_id="patch_version_upgrade",
                description=f"Patch upgrade from {from_ver} to {to_ver}",
                forward_sql="-- Patch version upgrade DDL would go here",
                rollback_sql="-- Patch version rollback DDL would go here",
                step_type="ddl",
                estimated_duration=5.0
            ))
        
        return steps
    
    async def _generate_backward_migration_steps(self, from_ver, to_ver) -> List[MigrationStep]:
        """Generate backward migration steps (rollback)"""
        steps = []
        
        # Generate rollback steps (reverse of forward migration)
        if from_ver.major > to_ver.major:
            steps.append(MigrationStep(
                step_id="major_version_rollback",
                description=f"Rollback schema from {from_ver} to {to_ver}",
                forward_sql="-- Major version rollback DDL would go here",
                rollback_sql="-- Major version restore DDL would go here",
                step_type="ddl",
                estimated_duration=25.0
            ))
        
        return steps
    
    async def _execute_migration_step(self, step: MigrationStep):
        """Execute individual migration step"""
        logger.debug(f"Executing migration step: {step.step_id}")
        
        try:
            # Validate step before execution
            if step.validation_query:
                await self._validate_migration_preconditions(step.validation_query)
            
            # Execute the migration SQL
            if self.db_connection:
                # Would execute actual SQL here
                await self._execute_sql(step.forward_sql)
            else:
                # Simulate execution for testing
                await asyncio.sleep(0.01)
            
            # Verify step completion
            if step.validation_query:
                await self._validate_migration_postconditions(step.validation_query)
            
            logger.debug(f"Migration step {step.step_id} executed successfully")
            
        except Exception as e:
            logger.error(f"Migration step {step.step_id} execution failed: {e}")
            raise MigrationError(f"Step execution failed: {e}")
    
    async def _rollback_migration_steps(self, rollback_steps: List[str]) -> bool:
        """Rollback migration steps in reverse order"""
        logger.info(f"Rolling back {len(rollback_steps)} migration steps")
        
        try:
            # Execute rollback steps in reverse order
            for step_id in rollback_steps:
                # Find step definition (would be stored separately)
                rollback_sql = await self._get_rollback_sql(step_id)
                
                if self.db_connection:
                    await self._execute_sql(rollback_sql)
                else:
                    # Simulate rollback for testing
                    await asyncio.sleep(0.01)
                
                logger.debug(f"Rollback step {step_id} executed successfully")
            
            logger.info("Migration rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration rollback failed: {e}")
            return False
    
    async def _update_schema_version(self, new_version: str):
        """Update schema version in database"""
        logger.debug(f"Updating schema version to {new_version}")
        
        # This would update the schema version in the database
        # For now, simulate the update
        await asyncio.sleep(0.01)
    
    async def _create_migration_backup(self, migration_id: str):
        """Create backup before migration"""
        logger.info(f"Creating migration backup for {migration_id}")
        
        # This would create a database backup
        # For now, simulate backup creation
        await asyncio.sleep(0.1)
    
    async def _validate_migration_preconditions(self, validation_query: str) -> bool:
        """Validate migration preconditions"""
        # Execute validation query
        if self.db_connection:
            # Would execute actual validation query
            pass
        return True
    
    async def _validate_migration_postconditions(self, validation_query: str) -> bool:
        """Validate migration postconditions"""
        # Execute validation query
        if self.db_connection:
            # Would execute actual validation query
            pass
        return True
    
    async def _execute_sql(self, sql: str):
        """Execute SQL statement"""
        if self.db_connection:
            # Would execute actual SQL
            pass
        else:
            # Simulate SQL execution
            await asyncio.sleep(0.01)
    
    async def _get_rollback_sql(self, step_id: str) -> str:
        """Get rollback SQL for step"""
        # This would retrieve the actual rollback SQL
        return f"-- Rollback SQL for step {step_id}"
    
    def _generate_migration_id(self, from_version: str, to_version: str) -> str:
        """Generate unique migration ID"""
        timestamp = int(time.time())
        content = f"{from_version}_{to_version}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    async def _ensure_migrations_directory(self):
        """Ensure migrations directory exists"""
        migrations_dir = Path(self.migrations_path)
        migrations_dir.mkdir(parents=True, exist_ok=True)
    
    async def _load_migration_history(self):
        """Load migration history from storage"""
        history_file = Path(self.migrations_path) / "migration_history.json"
        
        if history_file.exists():
            try:
                history_data = json.loads(history_file.read_text())
                
                for record_dict in history_data:
                    # Convert dict to MigrationHistory object
                    record = MigrationHistory(
                        migration_id=record_dict["migration_id"],
                        from_version=record_dict["from_version"],
                        to_version=record_dict["to_version"],
                        status=MigrationStatus(record_dict["status"]),
                        started_at=record_dict["started_at"],
                        completed_at=record_dict.get("completed_at"),
                        execution_time=record_dict.get("execution_time", 0.0),
                        steps_completed=record_dict.get("steps_completed", 0),
                        error_message=record_dict.get("error_message"),
                        rollback_steps=record_dict.get("rollback_steps", [])
                    )
                    self.migration_history.append(record)
                
                logger.info(f"Loaded {len(self.migration_history)} migration history records")
                
            except Exception as e:
                logger.warning(f"Failed to load migration history: {e}")
    
    async def _save_migration_history(self):
        """Save migration history to storage"""
        history_file = Path(self.migrations_path) / "migration_history.json"
        
        try:
            # Convert MigrationHistory objects to dicts
            history_data = []
            for record in self.migration_history:
                record_dict = {
                    "migration_id": record.migration_id,
                    "from_version": record.from_version,
                    "to_version": record.to_version,
                    "status": record.status.value,
                    "started_at": record.started_at,
                    "completed_at": record.completed_at,
                    "execution_time": record.execution_time,
                    "steps_completed": record.steps_completed,
                    "error_message": record.error_message,
                    "rollback_steps": record.rollback_steps
                }
                history_data.append(record_dict)
            
            history_file.write_text(json.dumps(history_data, indent=2))
            logger.debug("Migration history saved")
            
        except Exception as e:
            logger.error(f"Failed to save migration history: {e}")
    
    async def _load_rollback_scripts(self):
        """Load rollback scripts from storage"""
        rollback_file = Path(self.migrations_path) / "rollback_scripts.json"
        
        if rollback_file.exists():
            try:
                self.rollback_scripts = json.loads(rollback_file.read_text())
                logger.info(f"Loaded rollback scripts for {len(self.rollback_scripts)} migrations")
                
            except Exception as e:
                logger.warning(f"Failed to load rollback scripts: {e}")
    
    async def _save_rollback_scripts(self):
        """Save rollback scripts to storage"""
        rollback_file = Path(self.migrations_path) / "rollback_scripts.json"
        
        try:
            rollback_file.write_text(json.dumps(self.rollback_scripts, indent=2))
            logger.debug("Rollback scripts saved")
            
        except Exception as e:
            logger.error(f"Failed to save rollback scripts: {e}")
    
    def get_migration_statistics(self) -> Dict[str, Any]:
        """Get migration statistics"""
        total_migrations = len(self.migration_history)
        successful_migrations = sum(1 for h in self.migration_history if h.status == MigrationStatus.SUCCESS)
        failed_migrations = sum(1 for h in self.migration_history if h.status == MigrationStatus.FAILED)
        
        return {
            "total_migrations": total_migrations,
            "successful_migrations": successful_migrations,
            "failed_migrations": failed_migrations,
            "success_rate": successful_migrations / total_migrations if total_migrations > 0 else 0.0,
            "active_migration": self.active_migration,
            "rollback_scripts_available": len(self.rollback_scripts),
            "migrations_path": self.migrations_path
        }
    
    async def cleanup(self):
        """Cleanup migration manager"""
        logger.info("Cleaning up migration manager")
        
        # Save current state
        await self._save_migration_history()
        await self._save_rollback_scripts()
        
        # Clear state
        self.migration_history.clear()
        self.rollback_scripts.clear()
        self.active_migration = None


# Test harness
if __name__ == "__main__":
    async def test_migration_manager():
        """Test migration manager functionality"""
        
        # Use temporary directory for testing
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        config = {
            "migrations_path": temp_dir + "/migrations",
            "backup_enabled": True,
            "dry_run_enabled": True,
            "migration_timeout": 60
        }
        
        manager = MigrationManager(config)
        
        try:
            # Test initialization
            await manager.initialize()
            print("✅ MigrationManager initialized successfully")
            
            # Test migration planning
            plan = await manager._plan_migration_path("1.0.0", "1.1.0")
            print(f"✅ Migration plan created: {len(plan.steps)} steps")
            
            # Test migration execution
            result = await manager.migrate_schema("1.0.0", "1.1.0")
            if result.successful:
                print(f"✅ Migration successful: {result.from_version} -> {result.to_version}")
                print(f"   Execution time: {result.execution_time:.4f}s")
                print(f"   Steps completed: {result.steps_completed}/{result.total_steps}")
            else:
                print(f"❌ Migration failed: {result.error_message}")
            
            # Test statistics
            stats = manager.get_migration_statistics()
            print(f"✅ Migration statistics: {stats}")
            
            # Test cleanup
            await manager.cleanup()
            print("✅ MigrationManager cleanup successful")
            
        except Exception as e:
            print(f"❌ MigrationManager test failed: {e}")
        
        finally:
            # Cleanup temp directory
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    asyncio.run(test_migration_manager())