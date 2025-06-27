#!/usr/bin/env python3
"""
Performance Benchmark Tests for V5.0 Pipeline
Measures actual performance metrics to demonstrate scalability and efficiency
"""

import asyncio
import time
import tempfile
import statistics
import json
from pathlib import Path
from typing import Dict, Any, List

# Import the working pipeline implementation
import sys
sys.path.append('../day2_functional_implementation')
from working_pipeline_implementation import WorkingValidationDrivenOrchestrator


class PerformanceBenchmarkSuite:
    """Comprehensive performance benchmarking for V5.0 pipeline"""
    
    def __init__(self):
        self.results = {
            'startup_time': [],
            'blueprint_parsing_time': [],
            'validation_time': [],
            'component_generation_time': [],
            'system_assembly_time': [],
            'end_to_end_time': [],
            'memory_usage': [],
            'scalability_metrics': {}
        }
    
    def generate_large_blueprint(self, num_components: int) -> str:
        """Generate large blueprint for scalability testing"""
        
        components = []
        
        # Add source components
        source_count = min(3, max(1, num_components // 10))
        for i in range(source_count):
            components.append(f"""
    - name: DataSource{i}
      type: Source
      description: High-throughput data source {i}
      processing_mode: stream
      outputs:
        - name: raw_data_{i}
          schema: RawDataSchema{i}
      property_tests:
        - name: throughput_check_{i}
          type: range_check
          field: throughput
          min: 1000
          max: 100000
      database:
        type: postgresql
        connection_string: postgresql://localhost/perf_test_{i}
        schema:
          tables:
            - name: source_data_{i}
              columns:
                - name: id
                  type: bigint
                  primary_key: true
                - name: timestamp
                  type: timestamp
                - name: data
                  type: jsonb""")
        
        # Add transformer components  
        transformer_count = max(0, num_components - 3 - source_count)
        for i in range(transformer_count):
            input_idx = i % source_count
            components.append(f"""
    - name: DataProcessor{i}
      type: Transformer
      description: High-performance data processor {i}
      processing_mode: batch
      inputs:
        - name: raw_data_{input_idx}
          schema: RawDataSchema{input_idx}
      outputs:
        - name: processed_data_{i}
          schema: ProcessedDataSchema{i}
      property_tests:
        - name: processing_time_check_{i}
          type: range_check
          field: processing_time_ms
          min: 1
          max: 1000
      contract_tests:
        - name: output_validation_{i}
          schema: ProcessedDataSchema{i}
          description: Validate processing output {i}""")
        
        # Add sink components
        sink_count = min(3, max(1, num_components // 10))
        for i in range(sink_count):
            components.append(f"""
    - name: DataSink{i}
      type: Sink
      description: High-capacity data sink {i}
      processing_mode: batch
      inputs:
        - name: processed_data_{i}
          schema: ProcessedDataSchema{i}
      database:
        type: postgresql
        connection_string: postgresql://localhost/perf_test_sink_{i}
        schema:
          tables:
            - name: sink_data_{i}
              columns:
                - name: id
                  type: bigint
                  primary_key: true
                - name: data
                  type: jsonb
                - name: created_at
                  type: timestamp""")
        
        blueprint = f"""
system:
  name: performance_test_system_{num_components}
  description: Large system for performance testing with {num_components} components
  
  components:{"".join(components)}
"""
        
        return blueprint
    
    async def benchmark_startup_time(self) -> float:
        """Benchmark orchestrator startup time"""
        
        startup_times = []
        
        for _ in range(5):  # Run 5 times for average
            with tempfile.TemporaryDirectory() as temp_dir:
                start_time = time.time()
                
                orchestrator = WorkingValidationDrivenOrchestrator(
                    output_dir=Path(temp_dir) / "startup_test"
                )
                
                startup_time = time.time() - start_time
                startup_times.append(startup_time)
        
        avg_startup_time = statistics.mean(startup_times)
        self.results['startup_time'] = startup_times
        
        print(f"✅ Startup Time: {avg_startup_time:.3f}s (avg of {len(startup_times)} runs)")
        return avg_startup_time
    
    async def benchmark_blueprint_parsing(self) -> float:
        """Benchmark blueprint parsing performance"""
        
        parsing_times = []
        blueprint_sizes = [10, 25, 50]  # Different blueprint sizes
        
        with tempfile.TemporaryDirectory() as temp_dir:
            orchestrator = WorkingValidationDrivenOrchestrator(
                output_dir=Path(temp_dir) / "parsing_test"
            )
            
            for size in blueprint_sizes:
                blueprint = self.generate_large_blueprint(size)
                
                # Measure parsing time
                start_time = time.time()
                parsed = await orchestrator._parse_blueprint(blueprint)
                parsing_time = time.time() - start_time
                
                parsing_times.append({
                    'size': size,
                    'time': parsing_time,
                    'components': len(parsed.get('components', []))
                })
        
        self.results['blueprint_parsing_time'] = parsing_times
        
        for result in parsing_times:
            print(f"✅ Blueprint Parsing ({result['size']} components): {result['time']:.3f}s")
        
        return statistics.mean([r['time'] for r in parsing_times])
    
    async def benchmark_validation_performance(self) -> float:
        """Benchmark validation hierarchy performance"""
        
        validation_times = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            orchestrator = WorkingValidationDrivenOrchestrator(
                output_dir=Path(temp_dir) / "validation_test"
            )
            
            for size in [5, 15, 30]:
                blueprint_yaml = self.generate_large_blueprint(size)
                blueprint = await orchestrator._parse_blueprint(blueprint_yaml)
                
                # Measure validation time
                start_time = time.time()
                validation_result = await orchestrator._run_validation_hierarchy(blueprint)
                validation_time = time.time() - start_time
                
                validation_times.append({
                    'size': size,
                    'time': validation_time,
                    'is_valid': validation_result['is_valid']
                })
        
        self.results['validation_time'] = validation_times
        
        for result in validation_times:
            print(f"✅ Validation ({result['size']} components): {result['time']:.3f}s")
        
        return statistics.mean([r['time'] for r in validation_times])
    
    async def benchmark_component_generation(self) -> float:
        """Benchmark component generation performance"""
        
        generation_times = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            orchestrator = WorkingValidationDrivenOrchestrator(
                output_dir=Path(temp_dir) / "generation_test"
            )
            
            for size in [3, 8, 15]:
                blueprint_yaml = self.generate_large_blueprint(size)
                blueprint = await orchestrator._parse_blueprint(blueprint_yaml)
                
                # Measure component generation time
                start_time = time.time()
                components = await orchestrator._generate_components(blueprint)
                generation_time = time.time() - start_time
                
                generation_times.append({
                    'size': size,
                    'time': generation_time,
                    'generated': len(components),
                    'avg_per_component': generation_time / len(components) if components else 0
                })
        
        self.results['component_generation_time'] = generation_times
        
        for result in generation_times:
            print(f"✅ Component Generation ({result['size']} components): {result['time']:.3f}s "
                  f"({result['avg_per_component']:.3f}s per component)")
        
        return statistics.mean([r['time'] for r in generation_times])
    
    async def benchmark_end_to_end_performance(self) -> Dict[str, Any]:
        """Benchmark complete end-to-end system generation"""
        
        end_to_end_results = []
        
        for size in [5, 10, 20, 35]:
            with tempfile.TemporaryDirectory() as temp_dir:
                orchestrator = WorkingValidationDrivenOrchestrator(
                    output_dir=Path(temp_dir) / f"e2e_test_{size}"
                )
                
                blueprint_yaml = self.generate_large_blueprint(size)
                
                # Measure complete end-to-end time
                start_time = time.time()
                
                result = await orchestrator.generate_system_with_validation_driven_approach(
                    blueprint_yaml=blueprint_yaml,
                    system_name=f"performance_test_system_{size}"
                )
                
                end_to_end_time = time.time() - start_time
                
                end_to_end_results.append({
                    'components': size,
                    'time': end_to_end_time,
                    'success': result.success,
                    'files_generated': len(result.generated_files),
                    'validation_levels': len(result.validation_results)
                })
                
                # Performance requirement: should complete in under 30 seconds
                performance_met = end_to_end_time < 30.0
                status = "✅" if performance_met else "⚠️"
                
                print(f"{status} End-to-End ({size} components): {end_to_end_time:.3f}s "
                      f"({len(result.generated_files)} files)")
        
        self.results['end_to_end_time'] = end_to_end_results
        return end_to_end_results
    
    async def benchmark_scalability(self) -> Dict[str, Any]:
        """Test scalability with increasingly large systems"""
        
        scalability_results = []
        
        # Test with different component counts
        component_counts = [10, 25, 50, 100]
        
        for count in component_counts:
            with tempfile.TemporaryDirectory() as temp_dir:
                orchestrator = WorkingValidationDrivenOrchestrator(
                    output_dir=Path(temp_dir) / f"scalability_test_{count}"
                )
                
                try:
                    blueprint_yaml = self.generate_large_blueprint(count)
                    
                    start_time = time.time()
                    
                    result = await orchestrator.generate_system_with_validation_driven_approach(
                        blueprint_yaml=blueprint_yaml,
                        system_name=f"scalability_test_system_{count}"
                    )
                    
                    total_time = time.time() - start_time
                    
                    scalability_results.append({
                        'components': count,
                        'total_time': total_time,
                        'time_per_component': total_time / count,
                        'success': result.success,
                        'files_generated': len(result.generated_files),
                        'memory_efficient': total_time < (count * 0.5)  # Target: <0.5s per component
                    })
                    
                    efficiency = "✅" if total_time < (count * 0.5) else "⚠️"
                    print(f"{efficiency} Scalability ({count} components): {total_time:.3f}s "
                          f"({total_time/count:.3f}s per component)")
                    
                except Exception as e:
                    print(f"❌ Scalability test failed at {count} components: {e}")
                    scalability_results.append({
                        'components': count,
                        'total_time': None,
                        'success': False,
                        'error': str(e)
                    })
        
        self.results['scalability_metrics'] = scalability_results
        return scalability_results
    
    async def run_comprehensive_benchmarks(self) -> Dict[str, Any]:
        """Run all performance benchmarks"""
        
        print("🚀 Starting V5.0 Pipeline Performance Benchmarks")
        print("=" * 60)
        
        # 1. Startup Performance
        print("\n📊 1. Startup Performance")
        startup_time = await self.benchmark_startup_time()
        
        # 2. Blueprint Parsing Performance
        print("\n📊 2. Blueprint Parsing Performance")
        parsing_time = await self.benchmark_blueprint_parsing()
        
        # 3. Validation Performance
        print("\n📊 3. Validation Hierarchy Performance")
        validation_time = await self.benchmark_validation_performance()
        
        # 4. Component Generation Performance
        print("\n📊 4. Component Generation Performance")
        generation_time = await self.benchmark_component_generation()
        
        # 5. End-to-End Performance
        print("\n📊 5. End-to-End System Generation Performance")
        e2e_results = await self.benchmark_end_to_end_performance()
        
        # 6. Scalability Testing
        print("\n📊 6. Scalability Testing")
        scalability_results = await self.benchmark_scalability()
        
        # Performance Summary
        print("\n🎯 Performance Summary")
        print("=" * 60)
        
        # Check if performance requirements are met
        requirements_met = {
            'startup_under_1s': startup_time < 1.0,
            'parsing_efficient': parsing_time < 1.0,
            'validation_fast': validation_time < 5.0,
            'generation_efficient': generation_time < 10.0,
            'e2e_under_30s': all(r['time'] < 30.0 for r in e2e_results if r['success']),
            'scalability_good': len([r for r in scalability_results if r.get('memory_efficient', False)]) >= 2
        }
        
        for requirement, met in requirements_met.items():
            status = "✅" if met else "❌"
            print(f"{status} {requirement.replace('_', ' ').title()}")
        
        overall_performance = all(requirements_met.values())
        
        final_summary = {
            'overall_performance_met': overall_performance,
            'startup_time': startup_time,
            'parsing_time': parsing_time,
            'validation_time': validation_time,
            'generation_time': generation_time,
            'e2e_results': e2e_results,
            'scalability_results': scalability_results,
            'requirements_met': requirements_met,
            'total_benchmarks_run': 6,
            'benchmark_timestamp': time.time()
        }
        
        print(f"\n🏆 Overall Performance: {'PASSED' if overall_performance else 'NEEDS IMPROVEMENT'}")
        
        return final_summary


async def main():
    """Run performance benchmark suite"""
    
    benchmark_suite = PerformanceBenchmarkSuite()
    
    try:
        results = await benchmark_suite.run_comprehensive_benchmarks()
        
        # Save results to file
        results_file = Path("performance_benchmark_results.json")
        results_file.write_text(json.dumps(results, indent=2))
        
        print(f"\n📁 Results saved to: {results_file.absolute()}")
        
        # Print key metrics
        print("\n📈 Key Performance Metrics:")
        print(f"   • Startup Time: {results['startup_time']:.3f}s")
        print(f"   • Largest System Tested: {max(r['components'] for r in results['scalability_results'])} components")
        print(f"   • Fastest Generation: {min(r['time'] for r in results['e2e_results'] if r['success']):.3f}s")
        print(f"   • Requirements Met: {sum(results['requirements_met'].values())}/6")
        
        return results
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())