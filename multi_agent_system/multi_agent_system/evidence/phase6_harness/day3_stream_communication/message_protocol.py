#!/usr/bin/env python3
"""
MessageProtocol: Message serialization and deserialization framework
===================================================================

Provides comprehensive message serialization/deserialization with support for
complex data types, message validation, and protocol versioning for the
SystemExecutionHarness stream communication framework.

Key Features:
- JSON-based message serialization with metadata
- Support for complex data types (datetime, bytes, custom objects)
- Message validation and error handling
- Protocol versioning and compatibility
- Message compression for large payloads
- Performance optimization and metrics
"""

import json
import time
import uuid
import gzip
import base64
import pickle
from typing import Any, Dict, List, Optional, Union, Type
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import logging
import hashlib


class MessageType(Enum):
    """Standard message types"""
    DATA = "data"
    CONTROL = "control"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    METADATA = "metadata"
    BATCH = "batch"


class CompressionType(Enum):
    """Supported compression types"""
    NONE = "none"
    GZIP = "gzip"


@dataclass
class MessageMetadata:
    """Metadata for all messages"""
    id: str
    type: MessageType
    timestamp: float
    sender: Optional[str] = None
    recipient: Optional[str] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl: Optional[float] = None  # Time to live in seconds
    priority: int = 0  # Higher numbers = higher priority
    protocol_version: str = "1.0"
    compression: CompressionType = CompressionType.NONE
    content_hash: Optional[str] = None
    content_size: int = 0
    
    def is_expired(self) -> bool:
        """Check if message has expired"""
        if self.ttl is None:
            return False
        return time.time() > (self.timestamp + self.ttl)
    
    def age_seconds(self) -> float:
        """Get message age in seconds"""
        return time.time() - self.timestamp


@dataclass 
class Message:
    """Complete message with metadata and payload"""
    metadata: MessageMetadata
    payload: Any
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "metadata": asdict(self.metadata),
            "payload": self.payload
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], deserializer=None) -> 'Message':
        """Create message from dictionary"""
        metadata_dict = data["metadata"].copy()  # Make a copy to avoid modifying original
        
        # Use custom deserializer if provided to handle complex enum types
        if deserializer:
            metadata_dict["type"] = deserializer(metadata_dict["type"])
            metadata_dict["compression"] = deserializer(metadata_dict["compression"])
        else:
            # Fallback for simple enum values
            if isinstance(metadata_dict["type"], str):
                metadata_dict["type"] = MessageType(metadata_dict["type"])
            if isinstance(metadata_dict["compression"], str):
                metadata_dict["compression"] = CompressionType(metadata_dict["compression"])
        
        metadata = MessageMetadata(**metadata_dict)
        return cls(metadata=metadata, payload=data["payload"])


class MessageValidationError(Exception):
    """Raised when message validation fails"""
    pass


class MessageSerializationError(Exception):
    """Raised when message serialization fails"""
    pass


class MessageDeserializationError(Exception):
    """Raised when message deserialization fails"""
    pass


class UnsupportedDataTypeError(Exception):
    """Raised when attempting to serialize unsupported data type"""
    pass


class MessageProtocol:
    """
    Message serialization/deserialization with advanced features
    
    Provides:
    - JSON-based serialization with complex type support
    - Message validation and integrity checking
    - Compression for large messages
    - Protocol versioning and compatibility
    - Performance metrics and optimization
    """
    
    def __init__(self, 
                 compression_threshold: int = 1024,
                 enable_compression: bool = True,
                 enable_validation: bool = True,
                 max_message_size: int = 10 * 1024 * 1024):  # 10MB
        
        self.compression_threshold = compression_threshold
        self.enable_compression = enable_compression
        self.enable_validation = enable_validation
        self.max_message_size = max_message_size
        
        # Performance tracking
        self.serialization_times: List[float] = []
        self.deserialization_times: List[float] = []
        self.compression_ratios: List[float] = []
        self.message_sizes: List[int] = []
        
        # Error tracking
        self.serialization_errors = 0
        self.deserialization_errors = 0
        self.validation_errors = 0
        
        # Protocol version
        self.protocol_version = "1.0"
        
        # Logging
        self.logger = logging.getLogger("MessageProtocol")
        self.logger.info(f"✨ MessageProtocol initialized (compression: {enable_compression}, validation: {enable_validation})")
    
    def create_message(self,
                      payload: Any,
                      message_type: MessageType = MessageType.DATA,
                      sender: Optional[str] = None,
                      recipient: Optional[str] = None,
                      correlation_id: Optional[str] = None,
                      ttl: Optional[float] = None,
                      priority: int = 0) -> Message:
        """
        Create a new message with metadata
        
        Args:
            payload: Message payload data
            message_type: Type of message
            sender: Sender component name
            recipient: Recipient component name  
            correlation_id: ID for message correlation
            ttl: Time to live in seconds
            priority: Message priority (higher = more important)
            
        Returns:
            Message object with metadata
        """
        metadata = MessageMetadata(
            id=str(uuid.uuid4()),
            type=message_type,
            timestamp=time.time(),
            sender=sender,
            recipient=recipient,
            correlation_id=correlation_id,
            ttl=ttl,
            priority=priority,
            protocol_version=self.protocol_version
        )
        
        message = Message(metadata=metadata, payload=payload)
        
        # Calculate content hash and size
        try:
            serialized_payload = self._serialize_payload(payload)
            metadata.content_size = len(serialized_payload)
            metadata.content_hash = hashlib.sha256(serialized_payload.encode()).hexdigest()[:16]
        except Exception:
            # If we can't serialize for hash/size, that's okay for now
            pass
        
        return message
    
    def serialize(self, message: Union[Message, Any]) -> bytes:
        """
        Serialize message to bytes
        
        Args:
            message: Message object or raw data to serialize
            
        Returns:
            Serialized message as bytes
            
        Raises:
            MessageSerializationError: If serialization fails
        """
        start_time = time.time()
        
        try:
            # Handle raw data by wrapping in message
            if not isinstance(message, Message):
                message = self.create_message(message)
            
            # Validate message if enabled
            if self.enable_validation:
                self._validate_message(message)
            
            # Serialize to JSON
            message_dict = message.to_dict()
            json_data = json.dumps(message_dict, default=self._json_serializer, separators=(',', ':'))
            
            # Apply compression if enabled and beneficial
            final_data = json_data.encode('utf-8')
            
            if (self.enable_compression and 
                len(final_data) > self.compression_threshold):
                
                compressed_data = gzip.compress(final_data)
                
                # Only use compression if it actually reduces size
                if len(compressed_data) < len(final_data):
                    message.metadata.compression = CompressionType.GZIP
                    final_data = compressed_data
                    
                    # Track compression ratio
                    ratio = len(compressed_data) / len(final_data) if len(final_data) > 0 else 1.0
                    self.compression_ratios.append(ratio)
            
            # Check size limits
            if len(final_data) > self.max_message_size:
                raise MessageSerializationError(f"Message size {len(final_data)} exceeds limit {self.max_message_size}")
            
            # Update metadata with final size and compression info
            message.metadata.content_size = len(final_data)
            
            # Re-serialize with updated metadata if compression was applied
            if message.metadata.compression != CompressionType.NONE:
                message_dict = message.to_dict()
                json_data = json.dumps(message_dict, default=self._json_serializer, separators=(',', ':'))
                final_data = json_data.encode('utf-8')
                
                if message.metadata.compression == CompressionType.GZIP:
                    final_data = gzip.compress(final_data)
            
            # Track performance
            serialization_time = time.time() - start_time
            self.serialization_times.append(serialization_time)
            self.message_sizes.append(len(final_data))
            
            # Keep only recent measurements
            if len(self.serialization_times) > 1000:
                self.serialization_times = self.serialization_times[-1000:]
                self.message_sizes = self.message_sizes[-1000:]
            
            self.logger.debug(f"📦 Serialized message {message.metadata.id[:8]} ({len(final_data)} bytes, {serialization_time:.3f}ms)")
            
            return final_data
            
        except Exception as e:
            self.serialization_errors += 1
            self.logger.error(f"❌ Serialization failed: {e}")
            raise MessageSerializationError(f"Failed to serialize message: {e}") from e
    
    def deserialize(self, data: bytes) -> Message:
        """
        Deserialize bytes to message
        
        Args:
            data: Serialized message bytes
            
        Returns:
            Deserialized Message object
            
        Raises:
            MessageDeserializationError: If deserialization fails
        """
        start_time = time.time()
        
        try:
            # Try to decompress if it looks like compressed data
            decompressed_data = data
            
            # First, try to decompress to see if it's GZIP data
            try:
                if data[:2] == b'\x1f\x8b':  # GZIP magic number
                    decompressed_data = gzip.decompress(data)
            except Exception:
                # Not compressed or decompression failed, use original data
                decompressed_data = data
            
            # Decode JSON
            json_str = decompressed_data.decode('utf-8')
            message_dict = json.loads(json_str, object_hook=self._json_deserializer)
            
            # Reconstruct message
            message = Message.from_dict(message_dict, self._json_deserializer)
            
            # Validate message if enabled
            if self.enable_validation:
                self._validate_message(message)
                
                # Check if message has expired
                if message.metadata.is_expired():
                    self.logger.warning(f"⚠️ Received expired message {message.metadata.id[:8]}")
            
            # Track performance
            deserialization_time = time.time() - start_time
            self.deserialization_times.append(deserialization_time)
            
            # Keep only recent measurements
            if len(self.deserialization_times) > 1000:
                self.deserialization_times = self.deserialization_times[-1000:]
            
            self.logger.debug(f"📦 Deserialized message {message.metadata.id[:8]} ({len(data)} bytes, {deserialization_time:.3f}ms)")
            
            return message
            
        except Exception as e:
            self.deserialization_errors += 1
            self.logger.error(f"❌ Deserialization failed: {e}")
            raise MessageDeserializationError(f"Failed to deserialize message: {e}") from e
    
    def _serialize_payload(self, payload: Any) -> str:
        """Serialize payload to JSON string"""
        return json.dumps(payload, default=self._json_serializer, separators=(',', ':'))
    
    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for complex types"""
        if isinstance(obj, datetime):
            return {
                "__type__": "datetime",
                "__value__": obj.isoformat()
            }
        elif isinstance(obj, bytes):
            return {
                "__type__": "bytes",
                "__value__": base64.b64encode(obj).decode('ascii')
            }
        elif isinstance(obj, set):
            return {
                "__type__": "set",
                "__value__": list(obj)
            }
        elif isinstance(obj, (MessageType, CompressionType)):
            # Handle enum types
            return {
                "__type__": "enum",
                "__class__": obj.__class__.__name__,
                "__value__": obj.value
            }
        elif hasattr(obj, '__dict__'):
            # Handle custom objects with __dict__
            return {
                "__type__": "object",
                "__class__": obj.__class__.__name__,
                "__value__": obj.__dict__
            }
        else:
            # Try pickle as fallback for complex objects
            try:
                pickled = pickle.dumps(obj)
                return {
                    "__type__": "pickle",
                    "__value__": base64.b64encode(pickled).decode('ascii')
                }
            except Exception:
                raise UnsupportedDataTypeError(f"Cannot serialize object of type {type(obj)}")
    
    def _json_deserializer(self, obj: Any) -> Any:
        """Custom JSON deserializer for complex types"""
        if isinstance(obj, dict) and "__type__" in obj:
            obj_type = obj["__type__"]
            value = obj["__value__"]
            class_name = obj.get("__class__")
            
            if obj_type == "datetime":
                return datetime.fromisoformat(value)
            elif obj_type == "bytes":
                return base64.b64decode(value.encode('ascii'))
            elif obj_type == "set":
                return set(value)
            elif obj_type == "enum":
                # Handle enum types
                if class_name == "MessageType":
                    return MessageType(value)
                elif class_name == "CompressionType":
                    return CompressionType(value)
            elif obj_type == "pickle":
                pickled_data = base64.b64decode(value.encode('ascii'))
                return pickle.loads(pickled_data)
            elif obj_type == "object":
                # For custom objects, return the dict representation
                # In a real implementation, you might want to reconstruct the object
                return value
        
        return obj
    
    def _validate_message(self, message: Message):
        """
        Validate message structure and content
        
        Args:
            message: Message to validate
            
        Raises:
            MessageValidationError: If validation fails
        """
        try:
            # Validate metadata
            if not message.metadata.id:
                raise MessageValidationError("Message ID is required")
            
            if not isinstance(message.metadata.type, MessageType):
                raise MessageValidationError("Invalid message type")
            
            if message.metadata.timestamp <= 0:
                raise MessageValidationError("Invalid timestamp")
            
            if message.metadata.priority < 0:
                raise MessageValidationError("Priority cannot be negative")
            
            # Validate protocol version compatibility
            if message.metadata.protocol_version != self.protocol_version:
                # For now, just warn about version mismatch
                self.logger.warning(f"⚠️ Protocol version mismatch: {message.metadata.protocol_version} vs {self.protocol_version}")
            
            # Validate payload exists
            if message.payload is None and message.metadata.type == MessageType.DATA:
                raise MessageValidationError("Data messages must have a payload")
            
        except Exception as e:
            self.validation_errors += 1
            raise MessageValidationError(f"Message validation failed: {e}") from e
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get protocol performance metrics"""
        return {
            "serialization": {
                "total_operations": len(self.serialization_times),
                "average_time_ms": sum(self.serialization_times) / len(self.serialization_times) * 1000 if self.serialization_times else 0,
                "min_time_ms": min(self.serialization_times) * 1000 if self.serialization_times else 0,
                "max_time_ms": max(self.serialization_times) * 1000 if self.serialization_times else 0,
                "errors": self.serialization_errors
            },
            "deserialization": {
                "total_operations": len(self.deserialization_times),
                "average_time_ms": sum(self.deserialization_times) / len(self.deserialization_times) * 1000 if self.deserialization_times else 0,
                "min_time_ms": min(self.deserialization_times) * 1000 if self.deserialization_times else 0,
                "max_time_ms": max(self.deserialization_times) * 1000 if self.deserialization_times else 0,
                "errors": self.deserialization_errors
            },
            "compression": {
                "total_compressed": len(self.compression_ratios),
                "average_compression_ratio": sum(self.compression_ratios) / len(self.compression_ratios) if self.compression_ratios else 1.0,
                "best_compression_ratio": min(self.compression_ratios) if self.compression_ratios else 1.0,
                "compression_threshold": self.compression_threshold,
                "enabled": self.enable_compression
            },
            "messages": {
                "total_processed": len(self.message_sizes),
                "average_size_bytes": sum(self.message_sizes) / len(self.message_sizes) if self.message_sizes else 0,
                "min_size_bytes": min(self.message_sizes) if self.message_sizes else 0,
                "max_size_bytes": max(self.message_sizes) if self.message_sizes else 0,
                "max_allowed_size": self.max_message_size
            },
            "validation": {
                "enabled": self.enable_validation,
                "errors": self.validation_errors
            }
        }
    
    def create_error_message(self, error: Exception, 
                           original_message_id: Optional[str] = None,
                           sender: Optional[str] = None) -> Message:
        """Create an error message"""
        error_payload = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "original_message_id": original_message_id,
            "timestamp": time.time()
        }
        
        return self.create_message(
            payload=error_payload,
            message_type=MessageType.ERROR,
            sender=sender,
            correlation_id=original_message_id
        )
    
    def create_heartbeat_message(self, sender: str, 
                               status: Dict[str, Any] = None) -> Message:
        """Create a heartbeat message"""
        heartbeat_payload = {
            "sender": sender,
            "timestamp": time.time(),
            "status": status or {"healthy": True}
        }
        
        return self.create_message(
            payload=heartbeat_payload,
            message_type=MessageType.HEARTBEAT,
            sender=sender
        )
    
    def create_batch_message(self, messages: List[Message],
                           sender: Optional[str] = None) -> Message:
        """Create a batch message containing multiple messages"""
        batch_payload = {
            "message_count": len(messages),
            "messages": [msg.to_dict() for msg in messages],
            "batch_created_at": time.time()
        }
        
        return self.create_message(
            payload=batch_payload,
            message_type=MessageType.BATCH,
            sender=sender
        )
    
    def extract_batch_messages(self, batch_message: Message) -> List[Message]:
        """Extract individual messages from a batch message"""
        if batch_message.metadata.type != MessageType.BATCH:
            raise MessageValidationError("Not a batch message")
        
        payload = batch_message.payload
        messages = []
        
        for msg_dict in payload["messages"]:
            message = Message.from_dict(msg_dict)
            messages.append(message)
        
        return messages


# Export main classes
__all__ = [
    'MessageProtocol',
    'Message',
    'MessageMetadata',
    'MessageType',
    'CompressionType',
    'MessageValidationError',
    'MessageSerializationError',
    'MessageDeserializationError',
    'UnsupportedDataTypeError'
]