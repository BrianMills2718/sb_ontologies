#!/usr/bin/env python3
"""
Source component for Autocoder 4.3 System-First Architecture
"""
import anyio
from typing import Dict, Any
from .base import HarnessComponent


class Source(HarnessComponent):
    """
    Source components generate data from external sources using anyio streams.
    Examples: file readers, API endpoints, message queue consumers
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.component_type = "Source"
        self.data_count = config.get('data_count', 10) if config else 10
        self.data_delay = config.get('data_delay', 0.1) if config else 0.1
    
    async def process(self) -> None:
        """Generate data and send to output streams."""
        try:
            for i in range(self.data_count):
                # Generate data
                data = await self._generate_data({"index": i})
                
                # Send to all configured output streams
                for stream_name, stream in self.send_streams.items():
                    await stream.send(data)
                    self.increment_processed()
                
                await anyio.sleep(self.data_delay)
                
        except Exception as e:
            self.logger.error(f"Error in source processing: {e}")
            self.record_error(str(e))
        finally:
            # Close all output streams when done
            for stream in self.send_streams.values():
                await stream.aclose()
                
    async def _generate_data(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default implementation for data generation.
        Generated components will override this with actual data source logic.
        """
        # Default sample data generation - can be overridden by generated components
        # This ensures Zero Manual Intervention by providing working default behavior
        self.logger.info(f"Source {self.name} using default sample data generation")
        
        # Generate sample data with useful default structure
        import time
        sample_data = {
            "id": f"{self.name}_{inputs.get('index', 0)}",
            "source": self.name,
            "timestamp": time.time(),
            "data": f"sample_data_{inputs.get('index', 0)}",
            "generated_by": "default_source_implementation"
        }
        
        # Include any configuration-based data
        if hasattr(self, 'config') and self.config:
            sample_data.update(self.config.get('default_data', {}))
        
        return sample_data