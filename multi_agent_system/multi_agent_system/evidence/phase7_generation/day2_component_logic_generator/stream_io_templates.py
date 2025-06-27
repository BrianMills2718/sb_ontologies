#!/usr/bin/env python3
"""
StreamIOTemplateEngine: Template engine for generating stream-based I/O code
============================================================================

Generates stream-based I/O code templates for HarnessComponents including:
- Stream receive handling for multiple input streams
- Stream send code for multiple output streams  
- Stream helper methods and utilities
- Error handling for stream operations
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional

# Add evidence paths for integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))


class StreamIOTemplateEngine:
    """
    Template engine for generating stream-based I/O code in HarnessComponents.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("StreamIOTemplateEngine")
        self.logger.info("📡 StreamIOTemplateEngine initialized")
    
    def generate_stream_receive_code(self, input_streams: List[str]) -> str:
        """
        Generate code for receiving from multiple input streams
        
        Args:
            input_streams: List of input stream names
            
        Returns:
            Generated receive code
        """
        if not input_streams:
            return '''
            # No input streams configured
            await asyncio.sleep(0.1)  # Prevent tight loop'''
        
        if len(input_streams) == 1:
            stream_name = input_streams[0]
            return f'''
            # Receive from single input stream: {stream_name}
            if '{stream_name}' in self.receive_streams:
                try:
                    message = await self.receive_message('{stream_name}', timeout=1.0)
                    if message is not None:
                        result = await self.process_message(message)
                        if result:
                            await self.send_result(result)
                except Exception as e:
                    await self.handle_stream_error('{stream_name}', e)
            else:
                await asyncio.sleep(0.1)  # No streams available'''
        
        else:
            # Multiple input streams - use polling approach
            stream_checks = []
            for stream_name in input_streams:
                stream_checks.append(f'''
                # Check {stream_name} stream
                if '{stream_name}' in self.receive_streams:
                    try:
                        message = await self.receive_message('{stream_name}', timeout=0.1)
                        if message is not None:
                            result = await self.process_message(message)
                            if result:
                                await self.send_result(result)
                    except Exception as e:
                        await self.handle_stream_error('{stream_name}', e)''')
            
            return f'''
            # Poll multiple input streams
            streams_checked = 0
            {chr(10).join(stream_checks)}
            
            # Brief pause if no messages processed
            if streams_checked == 0:
                await asyncio.sleep(0.01)'''
    
    def generate_stream_send_code(self, output_streams: List[str]) -> str:
        """
        Generate code for sending to output streams
        
        Args:
            output_streams: List of output stream names
            
        Returns:
            Generated send code
        """
        if not output_streams:
            return '''
        # No output streams configured
        self.logger.debug("No output streams available for result")'''
        
        send_methods = []
        for stream_name in output_streams:
            send_methods.append(f'''
        # Send to {stream_name} stream
        if '{stream_name}' in self.send_streams:
            try:
                await self.send_message('{stream_name}', result)
                self.logger.debug(f"✅ Sent result to {stream_name}")
            except Exception as e:
                self.logger.error(f"❌ Failed to send to {stream_name}: {{e}}")''')
        
        return '\n'.join(send_methods)
    
    def generate_stream_helper_methods(self, stream_interfaces: Dict[str, List[str]]) -> List[str]:
        """
        Generate stream helper methods
        
        Args:
            stream_interfaces: Dictionary of input/output stream interfaces
            
        Returns:
            List of helper method code strings
        """
        helpers = []
        
        # Add stream error handler
        helpers.append('''
    async def handle_stream_error(self, stream_name: str, error: Exception):
        """Handle stream operation errors"""
        self.logger.warning(f"⚠️ Stream error on {stream_name}: {error}")
        
        # Record error for monitoring
        if not hasattr(self, 'stream_errors'):
            self.stream_errors = {}
        
        if stream_name not in self.stream_errors:
            self.stream_errors[stream_name] = 0
        
        self.stream_errors[stream_name] += 1
        
        # Exponential backoff for repeated errors
        if self.stream_errors[stream_name] > 3:
            await asyncio.sleep(min(2.0 ** (self.stream_errors[stream_name] - 3), 30.0))''')
        
        # Add stream status checker
        input_streams = stream_interfaces.get('input', [])
        output_streams = stream_interfaces.get('output', [])
        
        helpers.append(f'''
    def get_stream_status(self) -> Dict[str, Any]:
        """Get status of all component streams"""
        status = {{
            "input_streams": {{}},
            "output_streams": {{}},
            "stream_errors": getattr(self, 'stream_errors', {{}})
        }}
        
        # Check input streams
        for stream_name in {input_streams}:
            if stream_name in self.receive_streams:
                connection = self.receive_streams[stream_name]
                status["input_streams"][stream_name] = {{
                    "connected": True,
                    "message_count": connection.message_count,
                    "last_activity": connection.last_activity
                }}
            else:
                status["input_streams"][stream_name] = {{"connected": False}}
        
        # Check output streams  
        for stream_name in {output_streams}:
            if stream_name in self.send_streams:
                connection = self.send_streams[stream_name]
                status["output_streams"][stream_name] = {{
                    "connected": True,
                    "message_count": connection.message_count,
                    "last_activity": connection.last_activity
                }}
            else:
                status["output_streams"][stream_name] = {{"connected": False}}
                
        return status''')
        
        # Add bulk send method
        if output_streams:
            helpers.append(f'''
    async def send_to_multiple_streams(self, data: Dict[str, Any], stream_names: List[str] = None):
        """Send data to multiple output streams"""
        target_streams = stream_names or {output_streams}
        
        results = {{}}
        for stream_name in target_streams:
            try:
                success = await self.send_message(stream_name, data)
                results[stream_name] = success
            except Exception as e:
                results[stream_name] = False
                self.logger.error(f"❌ Failed to send to {{stream_name}}: {{e}}")
        
        return results''')
        
        # Add stream connectivity checker
        helpers.append('''
    async def check_stream_connectivity(self) -> Dict[str, bool]:
        """Check connectivity of all streams"""
        connectivity = {}
        
        # Check input streams
        for stream_name, connection in self.receive_streams.items():
            try:
                # Simple connectivity check - stream should not be closed
                connectivity[f"input_{stream_name}"] = not connection.stream._closed
            except:
                connectivity[f"input_{stream_name}"] = False
        
        # Check output streams
        for stream_name, connection in self.send_streams.items():
            try:
                connectivity[f"output_{stream_name}"] = not connection.stream._closed
            except:
                connectivity[f"output_{stream_name}"] = False
        
        return connectivity''')
        
        # Add stream metrics collector
        helpers.append('''
    def get_stream_metrics(self) -> Dict[str, Any]:
        """Collect stream performance metrics"""
        metrics = {
            "total_input_streams": len(self.receive_streams),
            "total_output_streams": len(self.send_streams),
            "total_messages_received": 0,
            "total_messages_sent": 0,
            "stream_errors": sum(getattr(self, 'stream_errors', {}).values()),
            "stream_details": {}
        }
        
        # Input stream metrics
        for stream_name, connection in self.receive_streams.items():
            metrics["total_messages_received"] += connection.message_count
            metrics["stream_details"][f"input_{stream_name}"] = {
                "messages": connection.message_count,
                "last_activity": connection.last_activity,
                "buffer_size": connection.buffer_size
            }
        
        # Output stream metrics
        for stream_name, connection in self.send_streams.items():
            metrics["total_messages_sent"] += connection.message_count
            metrics["stream_details"][f"output_{stream_name}"] = {
                "messages": connection.message_count,
                "last_activity": connection.last_activity,
                "buffer_size": connection.buffer_size
            }
        
        return metrics''')
        
        return helpers
    
    def generate_stream_multiplexer_code(self, input_streams: List[str]) -> str:
        """
        Generate code for multiplexing multiple input streams using anyio
        
        Args:
            input_streams: List of input stream names
            
        Returns:
            Multiplexer code
        """
        if len(input_streams) <= 1:
            return "# Single stream - no multiplexing needed"
        
        stream_tasks = []
        for stream_name in input_streams:
            stream_tasks.append(f'''
            async def handle_{stream_name}_stream():
                while self._processing_active:
                    try:
                        if '{stream_name}' in self.receive_streams:
                            message = await self.receive_message('{stream_name}', timeout=1.0)
                            if message is not None:
                                result = await self.process_message(message)
                                if result:
                                    await self.send_result(result)
                        else:
                            await asyncio.sleep(0.1)
                    except Exception as e:
                        await self.handle_stream_error('{stream_name}', e)''')
        
        task_starts = [f"tg.start_soon(handle_{stream}_stream)" for stream in input_streams]
        
        return f'''
            # Multiplexed stream handling
            import anyio
            
            {chr(10).join(stream_tasks)}
            
            # Start all stream handlers concurrently
            async with anyio.create_task_group() as tg:
                {chr(10).join(f"                {task}" for task in task_starts)}'''
    
    def generate_stream_backpressure_handler(self, output_streams: List[str]) -> str:
        """
        Generate backpressure handling code for output streams
        
        Args:
            output_streams: List of output stream names
            
        Returns:
            Backpressure handling code
        """
        if not output_streams:
            return "# No output streams - no backpressure handling needed"
        
        return f'''
    async def handle_backpressure(self, data: Dict[str, Any]) -> bool:
        """Handle backpressure on output streams"""
        failed_sends = []
        
        for stream_name in {output_streams}:
            if stream_name in self.send_streams:
                try:
                    # Try to send with short timeout to detect backpressure
                    await self.send_message(stream_name, data, timeout=0.5)
                except Exception as e:
                    failed_sends.append((stream_name, e))
        
        if failed_sends:
            self.logger.warning(f"⚠️ Backpressure detected on {{len(failed_sends)}} streams")
            
            # Implement backpressure strategy
            if len(failed_sends) >= len({output_streams}) * 0.5:
                # If more than 50% of streams are backed up, slow down
                await asyncio.sleep(0.1)
                return False
        
        return True'''
    
    def generate_stream_reconnection_logic(self, stream_interfaces: Dict[str, List[str]]) -> str:
        """
        Generate stream reconnection logic for resilience
        
        Args:
            stream_interfaces: Stream interface definitions
            
        Returns:
            Reconnection logic code
        """
        return '''
    async def check_and_reconnect_streams(self):
        """Check stream health and attempt reconnection if needed"""
        connectivity = await self.check_stream_connectivity()
        
        disconnected_streams = [
            stream_name for stream_name, connected in connectivity.items() 
            if not connected
        ]
        
        if disconnected_streams:
            self.logger.warning(f"⚠️ Detected {len(disconnected_streams)} disconnected streams")
            
            # Log disconnected streams for monitoring
            for stream_name in disconnected_streams:
                self.logger.warning(f"  - {stream_name}: disconnected")
            
            # Notify harness about stream issues
            if hasattr(self, 'harness_context') and self.harness_context:
                # Could implement stream reconnection via harness
                pass
        
        return len(disconnected_streams) == 0'''


# Export main class
__all__ = ['StreamIOTemplateEngine']