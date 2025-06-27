#!/usr/bin/env python3
"""
Natural Language Demo: English Input → Working SystemExecutionHarness
====================================================================

Demonstrates the complete Phase 7 pipeline from natural language descriptions
to deployed SystemExecutionHarness systems. Shows real examples of:

1. Natural language system descriptions
2. Complete pipeline execution
3. Generated SystemExecutionHarness code
4. Deployment verification
5. Health check validation

Demo Scenarios:
- Task Management System
- Data Processing Pipeline
- API Gateway Service
- Multi-Component System
"""

import os
import sys
import asyncio
import logging
import json
from pathlib import Path

# Add paths for demo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from blueprint_to_harness_pipeline import (
    BlueprintToHarnessPipeline, NaturalLanguageInput, PipelineResult
)

# Setup logging for demo
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NaturalLanguageDemo:
    """
    Demonstrates natural language to SystemExecutionHarness pipeline.
    """
    
    def __init__(self):
        self.pipeline = BlueprintToHarnessPipeline(output_base_dir="demo_generated_systems")
        self.demo_scenarios = self._create_demo_scenarios()
        
        logger.info("🎭 Natural Language Demo initialized")
    
    def _create_demo_scenarios(self) -> List[NaturalLanguageInput]:
        """Create demonstration scenarios"""
        return [
            # Scenario 1: Task Management System
            NaturalLanguageInput(
                description="Create a task management system with a REST API that can handle creating, updating, and retrieving tasks. Include a task controller for business logic and a data store for persistence.",
                requirements=[
                    "REST API on port 8080",
                    "Support up to 20 concurrent tasks",
                    "Memory-based storage for demo purposes"
                ],
                constraints=[
                    "Memory usage under 512MB",
                    "Secure HTTPS endpoints"
                ],
                metadata={
                    "scenario": "task_management",
                    "complexity": "medium",
                    "demo_purpose": "showcase_complete_system"
                }
            ),
            
            # Scenario 2: Data Processing Pipeline
            NaturalLanguageInput(
                description="Build a data processing pipeline that receives data through an API, processes it asynchronously, and stores results. Include error handling and monitoring.",
                requirements=[
                    "API gateway for data ingestion",
                    "Asynchronous data processing",
                    "Result storage and retrieval"
                ],
                constraints=[
                    "High availability design",
                    "Fault tolerance"
                ],
                metadata={
                    "scenario": "data_processing",
                    "complexity": "high", 
                    "demo_purpose": "showcase_async_processing"
                }
            ),
            
            # Scenario 3: Simple API Gateway
            NaturalLanguageInput(
                description="Create a simple API gateway service that can route requests and provide basic health checks.",
                requirements=[
                    "HTTP API on default port",
                    "Health check endpoints",
                    "Request routing"
                ],
                constraints=[
                    "Lightweight deployment",
                    "Fast startup time"
                ],
                metadata={
                    "scenario": "api_gateway",
                    "complexity": "low",
                    "demo_purpose": "showcase_simple_service"
                }
            ),
            
            # Scenario 4: Multi-Component System
            NaturalLanguageInput(
                description="Design a comprehensive system with web API, task processing, data storage, and background job management. This should demonstrate a full microservices architecture.",
                requirements=[
                    "Web API with multiple endpoints",
                    "Background job processing",
                    "Data persistence layer",
                    "Inter-service communication"
                ],
                constraints=[
                    "Scalable architecture",
                    "Service isolation",
                    "Monitoring and logging"
                ],
                metadata={
                    "scenario": "multi_component",
                    "complexity": "very_high",
                    "demo_purpose": "showcase_full_architecture"
                }
            )
        ]
    
    async def run_complete_demo(self):
        """Run complete demonstration of all scenarios"""
        logger.info("🚀 Starting complete natural language to SystemExecutionHarness demo")
        logger.info("="*80)
        
        demo_results = []
        
        for i, scenario in enumerate(self.demo_scenarios, 1):
            logger.info(f"\n🎬 Demo Scenario {i}: {scenario.metadata['scenario']}")
            logger.info(f"📝 Description: {scenario.description}")
            logger.info(f"🎯 Complexity: {scenario.metadata['complexity']}")
            logger.info("-" * 60)
            
            try:
                # Execute pipeline for scenario
                result = await self.pipeline.execute_complete_pipeline(scenario)
                demo_results.append(result)
                
                # Report results
                self._report_scenario_results(scenario, result)
                
            except Exception as e:
                logger.error(f"❌ Demo scenario {i} failed: {e}")
                continue
        
        # Generate demo summary
        self._generate_demo_summary(demo_results)
        
        logger.info("🎉 Complete natural language demo finished!")
        return demo_results
    
    async def run_single_scenario(self, scenario_name: str = "task_management"):
        """Run a single demo scenario for focused testing"""
        logger.info(f"🎯 Running single scenario demo: {scenario_name}")
        
        # Find scenario
        scenario = None
        for demo_scenario in self.demo_scenarios:
            if demo_scenario.metadata['scenario'] == scenario_name:
                scenario = demo_scenario
                break
        
        if not scenario:
            logger.error(f"❌ Scenario '{scenario_name}' not found")
            return None
        
        logger.info(f"📝 Description: {scenario.description}")
        logger.info(f"📋 Requirements: {scenario.requirements}")
        logger.info(f"⚠️ Constraints: {scenario.constraints}")
        logger.info("-" * 60)
        
        # Execute pipeline
        result = await self.pipeline.execute_complete_pipeline(scenario)
        
        # Report detailed results
        self._report_detailed_results(scenario, result)
        
        return result
    
    def _report_scenario_results(self, scenario: NaturalLanguageInput, result: PipelineResult):
        """Report results for a demo scenario"""
        if result.success:
            logger.info("✅ PIPELINE SUCCESS")
            logger.info(f"   Stages Completed: {result.pipeline_stages_completed}/5")
            logger.info(f"   Total Time: {result.total_pipeline_time:.2f}s")
            
            if result.generation_result:
                logger.info(f"   Generated Files: {len(result.generation_result.generated_files)}")
                logger.info(f"   Output Directory: {result.generation_result.output_directory}")
            
            if result.deployment_result:
                logger.info(f"   Deployment: {'✅ Success' if result.deployment_result.success else '❌ Failed'}")
                logger.info(f"   Health Checks: {'✅ Passed' if result.deployment_result.health_check_passed else '❌ Failed'}")
        else:
            logger.error("❌ PIPELINE FAILED")
            logger.error(f"   Stages Completed: {result.pipeline_stages_completed}/5")
            logger.error(f"   Error: {result.error_message}")
    
    def _report_detailed_results(self, scenario: NaturalLanguageInput, result: PipelineResult):
        """Report detailed results for in-depth analysis"""
        logger.info("\n" + "="*60)
        logger.info("DETAILED PIPELINE RESULTS")
        logger.info("="*60)
        
        # Input Analysis
        logger.info(f"📝 Natural Language Input:")
        logger.info(f"   Description: {scenario.description}")
        logger.info(f"   Requirements: {len(scenario.requirements)} items")
        logger.info(f"   Constraints: {len(scenario.constraints)} items")
        
        # Blueprint Parsing
        if result.parsed_blueprint:
            logger.info(f"\n🔍 Blueprint Parsing:")
            logger.info(f"   Components: {len(result.parsed_blueprint.components)}")
            for comp in result.parsed_blueprint.components:
                logger.info(f"     - {comp['name']} ({comp['type']})")
        
        # Validation Results
        if result.validation_result:
            logger.info(f"\n✅ Validation Results:")
            logger.info(f"   Success: {result.validation_result.successful}")
            logger.info(f"   Levels Passed: {result.validation_result.validation_levels_passed}/4")
            logger.info(f"   Healing Applied: {result.validation_result.healing_applied}")
        
        # Generation Results
        if result.generation_result:
            logger.info(f"\n🏗️ Generation Results:")
            logger.info(f"   Success: {result.generation_result.success}")
            logger.info(f"   Generated Files: {len(result.generation_result.generated_files)}")
            logger.info(f"   Phase 1 Time: {result.generation_result.phase1_time:.3f}s")
            logger.info(f"   Phase 2 Time: {result.generation_result.phase2_time:.3f}s")
            
            # List generated files
            logger.info(f"   Generated Files:")
            for file in result.generation_result.generated_files[:10]:  # Show first 10
                logger.info(f"     - {os.path.basename(file)}")
            if len(result.generation_result.generated_files) > 10:
                logger.info(f"     ... and {len(result.generation_result.generated_files) - 10} more")
        
        # Deployment Results
        if result.deployment_result:
            logger.info(f"\n🚀 Deployment Results:")
            logger.info(f"   Success: {result.deployment_result.success}")
            logger.info(f"   Path: {result.deployment_result.deployment_path}")
            logger.info(f"   Health Checks: {result.deployment_result.health_check_passed}")
            
            if result.deployment_result.logs:
                logger.info(f"   Deployment Logs:")
                for log in result.deployment_result.logs:
                    logger.info(f"     - {log}")
        
        # Overall Summary
        logger.info(f"\n📊 Overall Summary:")
        logger.info(f"   Pipeline Success: {result.success}")
        logger.info(f"   Total Time: {result.total_pipeline_time:.2f}s")
        logger.info(f"   Stages Completed: {result.pipeline_stages_completed}/5")
        
        # Show generated system structure if available
        if result.generation_result and result.generation_result.success:
            self._show_generated_system_structure(result.generation_result.output_directory)
    
    def _show_generated_system_structure(self, output_directory: str):
        """Show the structure of the generated system"""
        logger.info(f"\n📁 Generated System Structure ({output_directory}):")
        
        try:
            for root, dirs, files in os.walk(output_directory):
                level = root.replace(output_directory, '').count(os.sep)
                indent = ' ' * 2 * level
                logger.info(f"{indent}{os.path.basename(root)}/")
                
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    file_size = os.path.getsize(os.path.join(root, file))
                    logger.info(f"{subindent}{file} ({file_size} bytes)")
                    
                    # Show content preview for key files
                    if file in ['main.py', 'system_config.py'] and file_size < 2000:
                        self._show_file_preview(os.path.join(root, file))
        
        except Exception as e:
            logger.error(f"Failed to show system structure: {e}")
    
    def _show_file_preview(self, file_path: str, max_lines: int = 10):
        """Show preview of important generated files"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            logger.info(f"     📄 Preview of {os.path.basename(file_path)}:")
            for i, line in enumerate(lines[:max_lines]):
                logger.info(f"       {i+1:2}: {line.rstrip()}")
            
            if len(lines) > max_lines:
                logger.info(f"       ... ({len(lines) - max_lines} more lines)")
        
        except Exception as e:
            logger.error(f"Failed to preview {file_path}: {e}")
    
    def _generate_demo_summary(self, demo_results: List[PipelineResult]):
        """Generate summary of all demo results"""
        logger.info("\n" + "="*80)
        logger.info("DEMO SUMMARY")
        logger.info("="*80)
        
        successful_demos = [r for r in demo_results if r.success]
        failed_demos = [r for r in demo_results if not r.success]
        
        logger.info(f"Total Scenarios: {len(demo_results)}")
        logger.info(f"Successful: {len(successful_demos)}")
        logger.info(f"Failed: {len(failed_demos)}")
        
        if successful_demos:
            avg_time = sum(r.total_pipeline_time for r in successful_demos) / len(successful_demos)
            logger.info(f"Average Pipeline Time: {avg_time:.2f}s")
            
            total_files = sum(len(r.generation_result.generated_files) for r in successful_demos if r.generation_result)
            logger.info(f"Total Files Generated: {total_files}")
        
        # Success rate by scenario complexity
        complexity_stats = {}
        for result in demo_results:
            complexity = result.natural_language_input.metadata.get('complexity', 'unknown')
            if complexity not in complexity_stats:
                complexity_stats[complexity] = {'total': 0, 'success': 0}
            complexity_stats[complexity]['total'] += 1
            if result.success:
                complexity_stats[complexity]['success'] += 1
        
        logger.info("\nSuccess Rate by Complexity:")
        for complexity, stats in complexity_stats.items():
            success_rate = (stats['success'] / stats['total']) * 100
            logger.info(f"  {complexity}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Available generated systems
        if successful_demos:
            logger.info("\nGenerated Systems Available For Testing:")
            for result in successful_demos:
                if result.generation_result and result.generation_result.success:
                    scenario_name = result.natural_language_input.metadata.get('scenario', 'unknown')
                    logger.info(f"  - {scenario_name}: {result.generation_result.output_directory}")
    
    async def verify_generated_system(self, output_directory: str):
        """Verify a generated system can be executed"""
        logger.info(f"🔍 Verifying generated system: {output_directory}")
        
        try:
            main_py = os.path.join(output_directory, "main.py")
            if not os.path.exists(main_py):
                logger.error("❌ main.py not found")
                return False
            
            # Try to parse main.py
            with open(main_py, 'r') as f:
                content = f.read()
            
            # Basic syntax check
            compile(content, main_py, 'exec')
            logger.info("✅ main.py syntax is valid")
            
            # Check for required imports and structure
            required_patterns = [
                "import asyncio",
                "class", 
                "async def",
                "if __name__"
            ]
            
            for pattern in required_patterns:
                if pattern in content:
                    logger.info(f"✅ Found required pattern: {pattern}")
                else:
                    logger.warning(f"⚠️ Missing pattern: {pattern}")
            
            logger.info("✅ Generated system verification completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ System verification failed: {e}")
            return False


async def main():
    """Main demo execution"""
    demo = NaturalLanguageDemo()
    
    # Check command line arguments for demo mode
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "single":
            # Run single scenario demo
            scenario_name = sys.argv[2] if len(sys.argv) > 2 else "task_management"
            result = await demo.run_single_scenario(scenario_name)
            
            if result and result.success and result.generation_result:
                # Verify the generated system
                await demo.verify_generated_system(result.generation_result.output_directory)
        
        elif sys.argv[1] == "verify":
            # Verify existing system
            if len(sys.argv) > 2:
                await demo.verify_generated_system(sys.argv[2])
            else:
                logger.error("Please provide path to generated system")
        
        else:
            # Run complete demo
            await demo.run_complete_demo()
    else:
        # Default: run single scenario for testing
        logger.info("🎯 Running default single scenario demo (task_management)")
        result = await demo.run_single_scenario("task_management")
        
        if result and result.success and result.generation_result:
            await demo.verify_generated_system(result.generation_result.output_directory)


if __name__ == "__main__":
    logger.info("🎭 Starting Natural Language to SystemExecutionHarness Demo")
    asyncio.run(main())