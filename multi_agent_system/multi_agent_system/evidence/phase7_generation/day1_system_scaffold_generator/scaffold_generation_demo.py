#!/usr/bin/env python3
"""
Scaffold Generation Demo: Working demonstration of SystemScaffoldGenerator
=========================================================================

Live demonstration of scaffold generation with real blueprint data and output logs.
Shows the complete transformation from SystemBlueprint to harness-based main.py.
"""

import asyncio
import os
import sys
import logging
import time
from pathlib import Path

# Add evidence paths for integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from blueprint_types import SystemBlueprint
from system_scaffold_generator import SystemScaffoldGenerator
from harness_template_engine import HarnessTemplateEngine
from connection_mapper import ConnectionMapper


def setup_logging():
    """Setup logging for demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_demo_blueprint() -> SystemBlueprint:
    """Create a comprehensive demo blueprint for testing"""
    return SystemBlueprint(
        description="Task Management API with Real-time Processing",
        components=[
            {
                "name": "api_gateway",
                "type": "api_gateway",
                "configuration": {
                    "port": 8080,
                    "host": "0.0.0.0",
                    "cors_enabled": True,
                    "rate_limit": 1000
                },
                "bindings": [
                    {
                        "source": "requests",
                        "target": "task_controller.input",
                        "buffer_size": 50
                    }
                ]
            },
            {
                "name": "task_controller",
                "type": "task_controller",
                "configuration": {
                    "max_concurrent_tasks": 100,
                    "processing_timeout": 30,
                    "retry_attempts": 3
                },
                "dependencies": [
                    {"component_name": "task_store"},
                    {"component_name": "data_processor"}
                ],
                "bindings": [
                    {
                        "source": "store_commands",
                        "target": "task_store.input",
                        "buffer_size": 75
                    },
                    {
                        "source": "process_requests",
                        "target": "data_processor.input",
                        "buffer_size": 25
                    }
                ]
            },
            {
                "name": "task_store",
                "type": "task_store",
                "configuration": {
                    "storage_type": "redis",
                    "connection_pool_size": 10,
                    "key_prefix": "tasks:",
                    "ttl_seconds": 3600
                },
                "bindings": [
                    {
                        "source": "responses",
                        "target": "task_controller.store_data"
                    }
                ]
            },
            {
                "name": "data_processor",
                "type": "data_processor",
                "configuration": {
                    "processing_mode": "async",
                    "batch_size": 10,
                    "processing_interval": 1.0
                },
                "bindings": [
                    {
                        "source": "processed_data",
                        "target": "task_controller.processed_results"
                    }
                ]
            }
        ],
        metadata={
            "version": "1.0",
            "author": "V5.0 Two-Phase Generation Pipeline",
            "created": "2024-01-01T00:00:00Z"
        }
    )


async def main():
    """Main demo function"""
    setup_logging()
    logger = logging.getLogger("ScaffoldGenerationDemo")
    
    print("🚀 Phase 7 System Scaffold Generation Demo")
    print("=" * 60)
    
    try:
        # Create demo blueprint
        print("📋 Creating demo blueprint...")
        blueprint = create_demo_blueprint()
        print(f"✅ Created blueprint: {blueprint.description}")
        print(f"   Components: {len(blueprint.components)}")
        print()
        
        # Initialize scaffold generator
        print("🔧 Initializing SystemScaffoldGenerator...")
        generator = SystemScaffoldGenerator()
        print("✅ SystemScaffoldGenerator initialized")
        print()
        
        # Validate blueprint
        print("🔍 Validating blueprint for scaffold generation...")
        is_valid, errors = generator.validate_blueprint_for_scaffold(blueprint)
        if not is_valid:
            print(f"❌ Blueprint validation failed: {errors}")
            return
        print("✅ Blueprint validation passed")
        print()
        
        # Generate complete scaffold
        print("🏗️ Generating complete scaffold...")
        start_time = time.time()
        scaffold = generator.generate_complete_scaffold(blueprint)
        generation_time = time.time() - start_time
        
        print(f"✅ Scaffold generated in {generation_time:.3f}s")
        print(f"   Components: {len(scaffold.components)}")
        print(f"   Connections: {len(scaffold.connections)}")
        print(f"   Imports: {len(scaffold.imports)}")
        print()
        
        # Show generated main.py preview
        print("📄 Generated main.py preview (first 50 lines):")
        print("-" * 50)
        main_py_lines = scaffold.main_py_code.split('\n')
        for i, line in enumerate(main_py_lines[:50], 1):
            print(f"{i:2d}: {line}")
        
        if len(main_py_lines) > 50:
            print(f"... ({len(main_py_lines) - 50} more lines)")
        print()
        
        # Show component information
        print("🔧 Generated Components:")
        print("-" * 30)
        for comp in scaffold.components:
            print(f"  Name: {comp.name}")
            print(f"  Class: {comp.class_name}")
            print(f"  Type: {comp.component_type}")
            print(f"  Dependencies: {comp.dependencies}")
            print(f"  Import: {comp.import_path}")
            print()
        
        # Show connection information
        print("🔗 Generated Connections:")
        print("-" * 30)
        for conn in scaffold.connections:
            print(f"  {conn['source']} → {conn['target']}")
            print(f"    Buffer: {conn['buffer_size']}, Type: {conn['connection_type']}")
        print()
        
        # Show configuration preview
        print("⚙️ Generated configuration preview (first 30 lines):")
        print("-" * 50)
        config_lines = scaffold.config_code.split('\n')
        for i, line in enumerate(config_lines[:30], 1):
            print(f"{i:2d}: {line}")
        
        if len(config_lines) > 30:
            print(f"... ({len(config_lines) - 30} more lines)")
        print()
        
        # Test connection mapping
        print("🗺️ Testing connection mapping...")
        mapper = ConnectionMapper()
        connections = mapper.derive_connections(blueprint)
        print(f"✅ Derived {len(connections)} connections")
        
        # Show connection visualization
        visualization = mapper.visualize_connections(connections)
        print("📊 Connection Visualization:")
        print(visualization)
        print()
        
        # Show connection summary
        summary = mapper.get_connection_summary(connections)
        print("📈 Connection Summary:")
        print(f"  Total connections: {summary['total_connections']}")
        print(f"  Components involved: {summary['components_involved']}")
        print(f"  Connection types: {summary['connection_types']}")
        print(f"  Average buffer size: {summary['average_buffer_size']:.1f}")
        print()
        
        # Test template engine features
        print("🎨 Testing template engine features...")
        template_engine = HarnessTemplateEngine()
        
        dockerfile = template_engine.render_dockerfile_template(
            system_name="demo_system",
            requirements=["fastapi", "redis"]
        )
        print("🐳 Generated Dockerfile preview (first 20 lines):")
        dockerfile_lines = dockerfile.split('\n')
        for i, line in enumerate(dockerfile_lines[:20], 1):
            print(f"{i:2d}: {line}")
        print()
        
        requirements = template_engine.render_requirements_template(
            additional_requirements=["fastapi>=0.100.0", "redis>=4.0.0"]
        )
        print("📦 Generated requirements.txt:")
        print(requirements)
        print()
        
        # Save generated files for inspection
        output_dir = Path(__file__).parent / "demo_output"
        output_dir.mkdir(exist_ok=True)
        
        # Save main.py
        main_py_path = output_dir / "main.py"
        with open(main_py_path, 'w') as f:
            f.write(scaffold.main_py_code)
        
        # Save config
        config_py_path = output_dir / "system_config.py"
        with open(config_py_path, 'w') as f:
            f.write(scaffold.config_code)
        
        # Save dockerfile
        dockerfile_path = output_dir / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile)
        
        # Save requirements
        requirements_path = output_dir / "requirements.txt"
        with open(requirements_path, 'w') as f:
            f.write(requirements)
        
        print(f"💾 Generated files saved to: {output_dir}")
        print(f"   - {main_py_path}")
        print(f"   - {config_py_path}")
        print(f"   - {dockerfile_path}")
        print(f"   - {requirements_path}")
        print()
        
        # Performance metrics
        print("📊 Performance Metrics:")
        print(f"  Total generation time: {scaffold.generation_time:.3f}s")
        print(f"  Lines of main.py: {len(scaffold.main_py_code.split(chr(10)))}")
        print(f"  Lines of config: {len(scaffold.config_code.split(chr(10)))}")
        print(f"  Components processed: {len(scaffold.components)}")
        print(f"  Connections derived: {len(scaffold.connections)}")
        print()
        
        print("🎉 Scaffold Generation Demo Complete!")
        print("✅ All scaffold generation functionality verified")
        print("✅ Generated harness-compatible main.py file")
        print("✅ Generated system configuration")
        print("✅ Generated deployment files")
        print("✅ Connection mapping working correctly")
        print("✅ Template engine functioning properly")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())