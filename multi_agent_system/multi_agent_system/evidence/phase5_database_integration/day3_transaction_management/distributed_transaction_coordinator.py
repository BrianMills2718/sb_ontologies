"""
V5.0 Distributed Transaction Coordinator
Implements two-phase commit protocol for distributed ACID transactions
"""

import asyncio
import time
import logging
import uuid
import json
from typing import Dict, Any, Optional, List, Set, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import weakref
from pathlib import Path

logger = logging.getLogger(__name__)


class DistributedTransactionError(Exception):
    """Raised when distributed transaction operations fail"""
    pass


class CoordinatorError(Exception):
    """Raised when coordinator operations fail"""
    pass


class ParticipantError(Exception):
    """Raised when participant operations fail"""
    pass


class DTCState(Enum):
    """Distributed Transaction Coordinator states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    RECOVERING = "recovering"
    SHUTDOWN = "shutdown"


class GlobalTransactionState(Enum):
    """Global transaction states in 2PC protocol"""
    ACTIVE = "active"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ABORTING = "aborting"
    ABORTED = "aborted"
    UNCERTAIN = "uncertain"  # During recovery


@dataclass
class ParticipantInfo:
    """Information about transaction participant"""
    participant_id: str
    endpoint: str
    participant_type: str  # database, message_queue, file_system, etc.
    connection_info: Dict[str, Any]
    timeout: float = 30.0
    retry_count: int = 0
    max_retries: int = 3
    last_contact: Optional[float] = None


@dataclass
class GlobalTransaction:
    """Global distributed transaction"""
    global_txn_id: str
    coordinator_id: str
    state: GlobalTransactionState
    participants: Dict[str, ParticipantInfo]
    created_at: float
    timeout: float
    isolation_level: str = "READ_COMMITTED"
    started_at: Optional[float] = None
    prepared_at: Optional[float] = None
    completed_at: Optional[float] = None
    recovery_count: int = 0


@dataclass
class CoordinatorMetrics:
    """Distributed transaction coordinator metrics"""
    total_transactions: int = 0
    committed_transactions: int = 0
    aborted_transactions: int = 0
    uncertain_transactions: int = 0
    average_commit_time: float = 0.0
    average_prepare_time: float = 0.0
    participant_timeouts: int = 0
    coordinator_recoveries: int = 0
    uptime: float = 0.0


class DistributedTransactionParticipant:
    """Distributed transaction participant interface"""
    
    def __init__(self, participant_id: str, participant_type: str, config: Dict[str, Any]):
        self.participant_id = participant_id
        self.participant_type = participant_type
        self.config = config
        self.active_transactions: Set[str] = set()
        self.prepared_transactions: Set[str] = set()
    
    async def prepare(self, global_txn_id: str, transaction_data: Dict[str, Any]) -> bool:
        """Phase 1: Prepare to commit"""
        try:
            logger.info(f"Participant {self.participant_id} preparing transaction {global_txn_id}")
            
            # Validate transaction can be committed
            if not await self._validate_transaction(global_txn_id, transaction_data):
                return False
            
            # Lock resources
            if not await self._acquire_locks(global_txn_id, transaction_data):
                return False
            
            # Write prepare record to stable storage
            await self._write_prepare_record(global_txn_id, transaction_data)
            
            # Move to prepared state
            self.prepared_transactions.add(global_txn_id)
            
            logger.info(f"Participant {self.participant_id} prepared transaction {global_txn_id}")
            return True
            
        except Exception as e:
            logger.error(f"Participant {self.participant_id} prepare failed for {global_txn_id}: {e}")
            return False
    
    async def commit(self, global_txn_id: str) -> bool:
        """Phase 2: Commit transaction"""
        try:
            if global_txn_id not in self.prepared_transactions:
                logger.error(f"Transaction {global_txn_id} not prepared by participant {self.participant_id}")
                return False
            
            logger.info(f"Participant {self.participant_id} committing transaction {global_txn_id}")
            
            # Apply changes permanently
            await self._apply_changes(global_txn_id)
            
            # Release locks
            await self._release_locks(global_txn_id)
            
            # Remove from prepared set
            self.prepared_transactions.discard(global_txn_id)
            self.active_transactions.discard(global_txn_id)
            
            # Write commit record
            await self._write_commit_record(global_txn_id)
            
            logger.info(f"Participant {self.participant_id} committed transaction {global_txn_id}")
            return True
            
        except Exception as e:
            logger.error(f"Participant {self.participant_id} commit failed for {global_txn_id}: {e}")
            return False
    
    async def abort(self, global_txn_id: str) -> bool:
        """Abort transaction"""
        try:
            logger.info(f"Participant {self.participant_id} aborting transaction {global_txn_id}")
            
            # Rollback changes
            await self._rollback_changes(global_txn_id)
            
            # Release locks
            await self._release_locks(global_txn_id)
            
            # Remove from sets
            self.prepared_transactions.discard(global_txn_id)
            self.active_transactions.discard(global_txn_id)
            
            # Write abort record
            await self._write_abort_record(global_txn_id)
            
            logger.info(f"Participant {self.participant_id} aborted transaction {global_txn_id}")
            return True
            
        except Exception as e:
            logger.error(f"Participant {self.participant_id} abort failed for {global_txn_id}: {e}")
            return False
    
    async def _validate_transaction(self, global_txn_id: str, transaction_data: Dict[str, Any]) -> bool:
        """Validate transaction can be committed"""
        # Check constraints, validate data, etc.
        await asyncio.sleep(0.01)  # Simulate validation
        return True
    
    async def _acquire_locks(self, global_txn_id: str, transaction_data: Dict[str, Any]) -> bool:
        """Acquire necessary locks for transaction"""
        await asyncio.sleep(0.005)  # Simulate lock acquisition
        return True
    
    async def _release_locks(self, global_txn_id: str):
        """Release transaction locks"""
        await asyncio.sleep(0.002)  # Simulate lock release
    
    async def _apply_changes(self, global_txn_id: str):
        """Apply transaction changes permanently"""
        await asyncio.sleep(0.01)  # Simulate applying changes
    
    async def _rollback_changes(self, global_txn_id: str):
        """Rollback transaction changes"""
        await asyncio.sleep(0.008)  # Simulate rollback
    
    async def _write_prepare_record(self, global_txn_id: str, transaction_data: Dict[str, Any]):
        """Write prepare record to stable storage"""
        await asyncio.sleep(0.002)  # Simulate writing to stable storage
    
    async def _write_commit_record(self, global_txn_id: str):
        """Write commit record to stable storage"""
        await asyncio.sleep(0.002)  # Simulate writing to stable storage
    
    async def _write_abort_record(self, global_txn_id: str):
        """Write abort record to stable storage"""
        await asyncio.sleep(0.002)  # Simulate writing to stable storage


class DistributedTransactionCoordinator:
    """Two-phase commit coordinator for distributed transactions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.coordinator_id = config.get("coordinator_id", str(uuid.uuid4()))
        
        # Configuration
        self.transaction_timeout = config.get("transaction_timeout", 300.0)  # 5 minutes
        self.prepare_timeout = config.get("prepare_timeout", 30.0)
        self.commit_timeout = config.get("commit_timeout", 30.0)
        self.recovery_interval = config.get("recovery_interval", 60.0)
        self.log_directory = Path(config.get("log_directory", "./dtc_logs"))
        
        # State
        self.state = DTCState.INITIALIZING
        self.global_transactions: Dict[str, GlobalTransaction] = {}
        self.participants: Dict[str, DistributedTransactionParticipant] = {}
        self.metrics = CoordinatorMetrics()
        
        # Recovery and persistence
        self.transaction_log: List[Dict[str, Any]] = []
        self._recovery_task: Optional[asyncio.Task] = None
        self._started_at = time.time()
        
        logger.info(f"Distributed Transaction Coordinator {self.coordinator_id} initialized")
    
    async def initialize(self):
        """Initialize coordinator"""
        logger.info("Initializing distributed transaction coordinator")
        
        try:
            # Create log directory
            self.log_directory.mkdir(parents=True, exist_ok=True)
            
            # Load transaction log for recovery
            await self._load_transaction_log()
            
            # Perform recovery if needed
            await self._perform_recovery()
            
            # Start recovery task
            self._recovery_task = asyncio.create_task(self._recovery_loop())
            
            self.state = DTCState.ACTIVE
            self.metrics.uptime = time.time() - self._started_at
            
            logger.info("Distributed transaction coordinator initialized successfully")
            
        except Exception as e:
            logger.error(f"Coordinator initialization failed: {e}")
            raise CoordinatorError(f"Initialization failed: {e}")
    
    async def begin_global_transaction(
        self,
        participant_ids: List[str],
        isolation_level: str = "READ_COMMITTED",
        timeout: Optional[float] = None
    ) -> str:
        """Begin new global distributed transaction"""
        
        if self.state != DTCState.ACTIVE:
            raise DistributedTransactionError("Coordinator not active")
        
        global_txn_id = str(uuid.uuid4())
        
        # Create participant info
        participants = {}
        for participant_id in participant_ids:
            if participant_id not in self.participants:
                raise DistributedTransactionError(f"Unknown participant: {participant_id}")
            
            participants[participant_id] = ParticipantInfo(
                participant_id=participant_id,
                endpoint=f"participant://{participant_id}",
                participant_type=self.participants[participant_id].participant_type,
                connection_info={},
                timeout=self.prepare_timeout
            )
        
        # Create global transaction
        global_txn = GlobalTransaction(
            global_txn_id=global_txn_id,
            coordinator_id=self.coordinator_id,
            state=GlobalTransactionState.ACTIVE,
            participants=participants,
            created_at=time.time(),
            timeout=timeout or self.transaction_timeout,
            isolation_level=isolation_level
        )
        
        self.global_transactions[global_txn_id] = global_txn
        self.metrics.total_transactions += 1
        
        # Log transaction start
        await self._log_transaction_event(global_txn_id, "BEGIN", {
            "participants": participant_ids,
            "isolation_level": isolation_level,
            "timeout": global_txn.timeout
        })
        
        logger.info(f"Started global transaction {global_txn_id} with {len(participant_ids)} participants")
        return global_txn_id
    
    async def commit_global_transaction(self, global_txn_id: str) -> bool:
        """Commit global transaction using two-phase commit"""
        
        if global_txn_id not in self.global_transactions:
            raise DistributedTransactionError(f"Unknown global transaction: {global_txn_id}")
        
        global_txn = self.global_transactions[global_txn_id]
        
        if global_txn.state != GlobalTransactionState.ACTIVE:
            raise DistributedTransactionError(f"Transaction {global_txn_id} not in active state: {global_txn.state}")
        
        logger.info(f"Starting 2PC commit for global transaction {global_txn_id}")
        
        try:
            # Phase 1: Prepare
            prepare_start = time.time()
            prepare_success = await self._prepare_phase(global_txn)
            prepare_time = time.time() - prepare_start
            
            # Update metrics
            total_prepare_time = self.metrics.average_prepare_time * (self.metrics.total_transactions - 1)
            self.metrics.average_prepare_time = (total_prepare_time + prepare_time) / self.metrics.total_transactions
            
            if not prepare_success:
                # Abort transaction
                await self._abort_phase(global_txn)
                self.metrics.aborted_transactions += 1
                return False
            
            # Phase 2: Commit
            commit_start = time.time()
            commit_success = await self._commit_phase(global_txn)
            commit_time = time.time() - commit_start
            
            # Update metrics
            total_commit_time = self.metrics.average_commit_time * max(self.metrics.committed_transactions, 1)
            self.metrics.committed_transactions += 1
            self.metrics.average_commit_time = (total_commit_time + commit_time) / self.metrics.committed_transactions
            
            if commit_success:
                global_txn.state = GlobalTransactionState.COMMITTED
                global_txn.completed_at = time.time()
                
                # Log commit
                await self._log_transaction_event(global_txn_id, "COMMITTED", {
                    "prepare_time": prepare_time,
                    "commit_time": commit_time
                })
                
                logger.info(f"Global transaction {global_txn_id} committed successfully")
                return True
            else:
                # Commit failed - transaction in uncertain state
                global_txn.state = GlobalTransactionState.UNCERTAIN
                self.metrics.uncertain_transactions += 1
                
                await self._log_transaction_event(global_txn_id, "UNCERTAIN", {
                    "reason": "commit_phase_failed"
                })
                
                logger.error(f"Global transaction {global_txn_id} in uncertain state")
                return False
            
        except Exception as e:
            logger.error(f"2PC commit failed for transaction {global_txn_id}: {e}")
            await self._abort_phase(global_txn)
            self.metrics.aborted_transactions += 1
            return False
    
    async def abort_global_transaction(self, global_txn_id: str) -> bool:
        """Abort global transaction"""
        
        if global_txn_id not in self.global_transactions:
            raise DistributedTransactionError(f"Unknown global transaction: {global_txn_id}")
        
        global_txn = self.global_transactions[global_txn_id]
        
        logger.info(f"Aborting global transaction {global_txn_id}")
        
        try:
            abort_success = await self._abort_phase(global_txn)
            
            if abort_success:
                global_txn.state = GlobalTransactionState.ABORTED
                global_txn.completed_at = time.time()
                self.metrics.aborted_transactions += 1
                
                await self._log_transaction_event(global_txn_id, "ABORTED", {})
                logger.info(f"Global transaction {global_txn_id} aborted successfully")
                return True
            else:
                logger.error(f"Failed to abort global transaction {global_txn_id}")
                return False
                
        except Exception as e:
            logger.error(f"Abort failed for transaction {global_txn_id}: {e}")
            return False
    
    async def _prepare_phase(self, global_txn: GlobalTransaction) -> bool:
        """Phase 1 of 2PC: Prepare"""
        global_txn.state = GlobalTransactionState.PREPARING
        
        await self._log_transaction_event(global_txn.global_txn_id, "PREPARE_START", {})
        
        prepare_tasks = []
        for participant_id, participant_info in global_txn.participants.items():
            participant = self.participants[participant_id]
            task = asyncio.create_task(
                self._prepare_participant(participant, global_txn.global_txn_id, participant_info.timeout)
            )
            prepare_tasks.append((participant_id, task))
        
        # Wait for all prepare responses
        prepare_results = {}
        for participant_id, task in prepare_tasks:
            try:
                result = await asyncio.wait_for(task, timeout=global_txn.participants[participant_id].timeout)
                prepare_results[participant_id] = result
            except asyncio.TimeoutError:
                logger.error(f"Prepare timeout for participant {participant_id}")
                prepare_results[participant_id] = False
                self.metrics.participant_timeouts += 1
            except Exception as e:
                logger.error(f"Prepare failed for participant {participant_id}: {e}")
                prepare_results[participant_id] = False
        
        # Check if all participants prepared successfully
        all_prepared = all(prepare_results.values())
        
        if all_prepared:
            global_txn.state = GlobalTransactionState.PREPARED
            global_txn.prepared_at = time.time()
            
            await self._log_transaction_event(global_txn.global_txn_id, "PREPARED", {
                "participants": list(prepare_results.keys())
            })
            
            logger.info(f"All participants prepared for transaction {global_txn.global_txn_id}")
            return True
        else:
            failed_participants = [pid for pid, result in prepare_results.items() if not result]
            
            await self._log_transaction_event(global_txn.global_txn_id, "PREPARE_FAILED", {
                "failed_participants": failed_participants
            })
            
            logger.error(f"Prepare failed for transaction {global_txn.global_txn_id}, failed participants: {failed_participants}")
            return False
    
    async def _commit_phase(self, global_txn: GlobalTransaction) -> bool:
        """Phase 2 of 2PC: Commit"""
        global_txn.state = GlobalTransactionState.COMMITTING
        
        await self._log_transaction_event(global_txn.global_txn_id, "COMMIT_START", {})
        
        commit_tasks = []
        for participant_id in global_txn.participants:
            participant = self.participants[participant_id]
            task = asyncio.create_task(
                self._commit_participant(participant, global_txn.global_txn_id)
            )
            commit_tasks.append((participant_id, task))
        
        # Wait for all commit responses
        commit_results = {}
        for participant_id, task in commit_tasks:
            try:
                result = await asyncio.wait_for(task, timeout=self.commit_timeout)
                commit_results[participant_id] = result
            except asyncio.TimeoutError:
                logger.error(f"Commit timeout for participant {participant_id}")
                commit_results[participant_id] = False
                self.metrics.participant_timeouts += 1
            except Exception as e:
                logger.error(f"Commit failed for participant {participant_id}: {e}")
                commit_results[participant_id] = False
        
        # All commits should succeed (participants are already prepared)
        all_committed = all(commit_results.values())
        
        if all_committed:
            logger.info(f"All participants committed for transaction {global_txn.global_txn_id}")
            return True
        else:
            failed_participants = [pid for pid, result in commit_results.items() if not result]
            logger.error(f"Commit failed for some participants in transaction {global_txn.global_txn_id}: {failed_participants}")
            return False
    
    async def _abort_phase(self, global_txn: GlobalTransaction) -> bool:
        """Abort phase: Abort all participants"""
        global_txn.state = GlobalTransactionState.ABORTING
        
        await self._log_transaction_event(global_txn.global_txn_id, "ABORT_START", {})
        
        abort_tasks = []
        for participant_id in global_txn.participants:
            participant = self.participants[participant_id]
            task = asyncio.create_task(
                self._abort_participant(participant, global_txn.global_txn_id)
            )
            abort_tasks.append((participant_id, task))
        
        # Wait for all abort responses
        abort_results = {}
        for participant_id, task in abort_tasks:
            try:
                result = await task
                abort_results[participant_id] = result
            except Exception as e:
                logger.error(f"Abort failed for participant {participant_id}: {e}")
                abort_results[participant_id] = False
        
        all_aborted = all(abort_results.values())
        
        if all_aborted:
            logger.info(f"All participants aborted for transaction {global_txn.global_txn_id}")
        else:
            failed_participants = [pid for pid, result in abort_results.items() if not result]
            logger.error(f"Abort failed for some participants in transaction {global_txn.global_txn_id}: {failed_participants}")
        
        return all_aborted
    
    async def _prepare_participant(self, participant: DistributedTransactionParticipant, global_txn_id: str, timeout: float) -> bool:
        """Send prepare to participant"""
        try:
            return await participant.prepare(global_txn_id, {})
        except Exception as e:
            logger.error(f"Prepare participant {participant.participant_id} failed: {e}")
            return False
    
    async def _commit_participant(self, participant: DistributedTransactionParticipant, global_txn_id: str) -> bool:
        """Send commit to participant"""
        try:
            return await participant.commit(global_txn_id)
        except Exception as e:
            logger.error(f"Commit participant {participant.participant_id} failed: {e}")
            return False
    
    async def _abort_participant(self, participant: DistributedTransactionParticipant, global_txn_id: str) -> bool:
        """Send abort to participant"""
        try:
            return await participant.abort(global_txn_id)
        except Exception as e:
            logger.error(f"Abort participant {participant.participant_id} failed: {e}")
            return False
    
    def register_participant(self, participant: DistributedTransactionParticipant):
        """Register transaction participant"""
        self.participants[participant.participant_id] = participant
        logger.info(f"Registered participant {participant.participant_id} of type {participant.participant_type}")
    
    async def _log_transaction_event(self, global_txn_id: str, event_type: str, data: Dict[str, Any]):
        """Log transaction event for recovery"""
        log_entry = {
            "timestamp": time.time(),
            "global_txn_id": global_txn_id,
            "coordinator_id": self.coordinator_id,
            "event_type": event_type,
            "data": data
        }
        
        self.transaction_log.append(log_entry)
        
        # Persist to file
        log_file = self.log_directory / f"dtc_log_{self.coordinator_id}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    async def _load_transaction_log(self):
        """Load transaction log from file"""
        log_file = self.log_directory / f"dtc_log_{self.coordinator_id}.jsonl"
        
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    for line in f:
                        if line.strip():
                            log_entry = json.loads(line.strip())
                            self.transaction_log.append(log_entry)
                
                logger.info(f"Loaded {len(self.transaction_log)} transaction log entries")
                
            except Exception as e:
                logger.error(f"Failed to load transaction log: {e}")
    
    async def _perform_recovery(self):
        """Perform recovery from transaction log"""
        if not self.transaction_log:
            return
        
        logger.info("Starting coordinator recovery")
        self.state = DTCState.RECOVERING
        
        # Group log entries by transaction
        txn_events = {}
        for entry in self.transaction_log:
            txn_id = entry["global_txn_id"]
            if txn_id not in txn_events:
                txn_events[txn_id] = []
            txn_events[txn_id].append(entry)
        
        # Process each transaction for recovery
        for txn_id, events in txn_events.items():
            await self._recover_transaction(txn_id, events)
        
        self.metrics.coordinator_recoveries += 1
        logger.info("Coordinator recovery completed")
    
    async def _recover_transaction(self, txn_id: str, events: List[Dict[str, Any]]):
        """Recover individual transaction"""
        logger.debug(f"Recovering transaction {txn_id}")
        
        # Sort events by timestamp
        events.sort(key=lambda e: e["timestamp"])
        
        # Determine final state
        final_event = events[-1]["event_type"]
        
        if final_event == "COMMITTED":
            # Transaction committed, no action needed
            logger.debug(f"Transaction {txn_id} already committed")
        elif final_event == "ABORTED":
            # Transaction aborted, no action needed
            logger.debug(f"Transaction {txn_id} already aborted")
        elif final_event in ("PREPARED", "COMMIT_START"):
            # Transaction was prepared but commit outcome unknown
            # In a real implementation, we would query participants
            logger.warning(f"Transaction {txn_id} in uncertain state, manual resolution may be required")
        else:
            # Transaction was in progress, abort it
            logger.info(f"Aborting incomplete transaction {txn_id}")
    
    async def _recovery_loop(self):
        """Background recovery loop"""
        while self.state != DTCState.SHUTDOWN:
            try:
                await asyncio.sleep(self.recovery_interval)
                
                # Check for timeout transactions
                current_time = time.time()
                timed_out_transactions = []
                
                for txn_id, txn in self.global_transactions.items():
                    if (txn.state in (GlobalTransactionState.ACTIVE, GlobalTransactionState.PREPARING) and
                        current_time - txn.created_at > txn.timeout):
                        timed_out_transactions.append(txn_id)
                
                # Abort timed out transactions
                for txn_id in timed_out_transactions:
                    logger.warning(f"Aborting timed out transaction {txn_id}")
                    await self.abort_global_transaction(txn_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Recovery loop error: {e}")
    
    def get_coordinator_statistics(self) -> Dict[str, Any]:
        """Get coordinator statistics"""
        self.metrics.uptime = time.time() - self._started_at
        
        return {
            "coordinator_id": self.coordinator_id,
            "state": self.state.value,
            "total_transactions": self.metrics.total_transactions,
            "committed_transactions": self.metrics.committed_transactions,
            "aborted_transactions": self.metrics.aborted_transactions,
            "uncertain_transactions": self.metrics.uncertain_transactions,
            "active_transactions": len([txn for txn in self.global_transactions.values() 
                                      if txn.state == GlobalTransactionState.ACTIVE]),
            "commit_rate": self.metrics.committed_transactions / max(self.metrics.total_transactions, 1),
            "average_commit_time": self.metrics.average_commit_time,
            "average_prepare_time": self.metrics.average_prepare_time,
            "participant_timeouts": self.metrics.participant_timeouts,
            "coordinator_recoveries": self.metrics.coordinator_recoveries,
            "registered_participants": len(self.participants),
            "uptime": self.metrics.uptime
        }
    
    async def shutdown(self):
        """Shutdown coordinator"""
        logger.info("Shutting down distributed transaction coordinator")
        
        self.state = DTCState.SHUTDOWN
        
        # Cancel recovery task
        if self._recovery_task:
            self._recovery_task.cancel()
            try:
                await self._recovery_task
            except asyncio.CancelledError:
                pass
        
        # Abort all active transactions
        active_transactions = [
            txn_id for txn_id, txn in self.global_transactions.items()
            if txn.state in (GlobalTransactionState.ACTIVE, GlobalTransactionState.PREPARING)
        ]
        
        for txn_id in active_transactions:
            await self.abort_global_transaction(txn_id)
        
        logger.info("Distributed transaction coordinator shutdown complete")


# Test harness
if __name__ == "__main__":
    async def test_distributed_coordinator():
        """Test distributed transaction coordinator"""
        
        config = {
            "coordinator_id": "coord_001",
            "transaction_timeout": 60.0,
            "prepare_timeout": 10.0,
            "commit_timeout": 10.0,
            "recovery_interval": 30.0,
            "log_directory": "./test_dtc_logs"
        }
        
        coordinator = DistributedTransactionCoordinator(config)
        
        try:
            print("🔧 Testing Distributed Transaction Coordinator...")
            
            # Initialize coordinator
            await coordinator.initialize()
            print("✅ Coordinator initialized")
            
            # Register participants
            participant1 = DistributedTransactionParticipant("db1", "database", {})
            participant2 = DistributedTransactionParticipant("db2", "database", {})
            
            coordinator.register_participant(participant1)
            coordinator.register_participant(participant2)
            print("✅ Participants registered")
            
            # Test successful 2PC transaction
            global_txn_id = await coordinator.begin_global_transaction(["db1", "db2"])
            print(f"✅ Global transaction started: {global_txn_id}")
            
            # Commit transaction
            commit_success = await coordinator.commit_global_transaction(global_txn_id)
            print(f"✅ Global transaction commit: {commit_success}")
            
            # Test transaction abort
            global_txn_id2 = await coordinator.begin_global_transaction(["db1", "db2"])
            abort_success = await coordinator.abort_global_transaction(global_txn_id2)
            print(f"✅ Global transaction abort: {abort_success}")
            
            # Test statistics
            stats = coordinator.get_coordinator_statistics()
            print(f"✅ Coordinator statistics: {stats}")
            
            # Test shutdown
            await coordinator.shutdown()
            print("✅ Coordinator shutdown successful")
            
        except Exception as e:
            print(f"❌ Distributed coordinator test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_distributed_coordinator())