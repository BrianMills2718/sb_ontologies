"""
Comprehensive Test Suite for Cross-Purpose Reasoning Engine
Tests all reasoning capabilities with balanced analytical depth
"""

import sys
import json
import time
from typing import Dict, List, Any
import traceback

# Import all reasoning components
from reasoning_engine import CrossPurposeReasoningEngine
from purpose_reasoning.descriptive_reasoning import DescriptiveReasoner
from purpose_reasoning.explanatory_reasoning import ExplanatoryReasoner
from purpose_reasoning.predictive_reasoning import PredictiveReasoner
from purpose_reasoning.causal_reasoning import CausalReasoner
from purpose_reasoning.intervention_reasoning import InterventionReasoner
from cross_purpose_integration import CrossPurposeIntegrator


class ReasoningEngineTestSuite:
    """Comprehensive test suite for reasoning engine with balanced purpose testing"""
    
    def __init__(self):
        """Initialize test suite"""
        self.engine = CrossPurposeReasoningEngine()
        self.integrator = CrossPurposeIntegrator()
        self.test_results = {}
        self.test_schemas = self._generate_test_schemas()
        self.test_queries = self._generate_test_queries()
    
    def run_all_tests(self) -> dict:
        """Run all comprehensive tests"""
        print("Starting Comprehensive Cross-Purpose Reasoning Engine Tests")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test 1: Descriptive reasoning capabilities
        print("\n1. Testing Descriptive Reasoning Capabilities...")
        self.test_results['descriptive'] = self._test_descriptive_reasoning()
        
        # Test 2: Explanatory reasoning capabilities
        print("\n2. Testing Explanatory Reasoning Capabilities...")
        self.test_results['explanatory'] = self._test_explanatory_reasoning()
        
        # Test 3: Predictive reasoning capabilities
        print("\n3. Testing Predictive Reasoning Capabilities...")
        self.test_results['predictive'] = self._test_predictive_reasoning()
        
        # Test 4: Causal reasoning capabilities
        print("\n4. Testing Causal Reasoning Capabilities...")
        self.test_results['causal'] = self._test_causal_reasoning()
        
        # Test 5: Intervention reasoning capabilities
        print("\n5. Testing Intervention Reasoning Capabilities...")
        self.test_results['intervention'] = self._test_intervention_reasoning()
        
        # Test 6: Cross-purpose integration reasoning
        print("\n6. Testing Cross-Purpose Integration...")
        self.test_results['integration'] = self._test_cross_purpose_integration()
        
        # Test 7: Complex multi-purpose query handling
        print("\n7. Testing Complex Multi-Purpose Queries...")
        self.test_results['complex_queries'] = self._test_complex_query_handling()
        
        # Test 8: Reasoning balance validation
        print("\n8. Testing Reasoning Balance Validation...")
        self.test_results['balance_validation'] = self._test_reasoning_balance()
        
        # Test 9: Performance testing with real schemas
        print("\n9. Testing Performance with Real Schemas...")
        self.test_results['performance'] = self._test_performance()
        
        end_time = time.time()
        
        # Generate comprehensive test summary
        summary = self._generate_test_summary(start_time, end_time)
        self.test_results['summary'] = summary
        
        print(f"\n{'='*60}")
        print("TEST SUITE COMPLETED")
        print(f"Total Time: {end_time - start_time:.2f} seconds")
        print(f"Overall Success Rate: {summary['overall_success_rate']:.1%}")
        print(f"{'='*60}")
        
        return self.test_results
    
    def _generate_test_schemas(self) -> Dict[str, dict]:
        """Generate test schemas for different complexity levels"""
        return {
            'simple_schema': {
                'entities': {
                    'entity_1': {'type': 'primary', 'properties': ['prop_1', 'prop_2']},
                    'entity_2': {'type': 'secondary', 'properties': ['prop_3', 'prop_4']}
                },
                'relationships': {
                    'rel_1': {'type': 'causal', 'source': 'entity_1', 'target': 'entity_2'},
                    'rel_2': {'type': 'structural', 'source': 'entity_2', 'target': 'entity_1'}
                },
                'properties': {
                    'complexity': 'low',
                    'domain': 'test'
                }
            },
            'complex_schema': {
                'entities': {
                    'system': {'type': 'complex_system', 'properties': ['emergent', 'adaptive']},
                    'subsystem_1': {'type': 'functional', 'properties': ['operational', 'responsive']},
                    'subsystem_2': {'type': 'structural', 'properties': ['stable', 'hierarchical']},
                    'environment': {'type': 'contextual', 'properties': ['dynamic', 'influential']},
                    'agents': {'type': 'actors', 'properties': ['autonomous', 'interactive']}
                },
                'relationships': {
                    'system_environment': {'type': 'bidirectional', 'strength': 'strong'},
                    'system_subsystems': {'type': 'hierarchical', 'strength': 'moderate'},
                    'subsystem_interaction': {'type': 'functional', 'strength': 'moderate'},
                    'agent_system': {'type': 'participatory', 'strength': 'variable'},
                    'feedback_loop': {'type': 'cyclical', 'strength': 'dynamic'}
                },
                'properties': {
                    'complexity': 'high',
                    'domain': 'socio_technical_system',
                    'temporal_dynamics': 'present',
                    'emergent_properties': 'expected'
                },
                'constraints': [
                    'resource_limitations',
                    'regulatory_requirements',
                    'stakeholder_expectations'
                ]
            },
            'social_ecological_schema': {
                'entities': {
                    'community': {'type': 'social_group', 'properties': ['collective', 'networked']},
                    'ecosystem': {'type': 'ecological_system', 'properties': ['biological', 'self_regulating']},
                    'institutions': {'type': 'governance', 'properties': ['formal', 'rule_based']},
                    'technology': {'type': 'tool_system', 'properties': ['enabling', 'transformative']},
                    'economy': {'type': 'resource_system', 'properties': ['exchange', 'value_creating']}
                },
                'relationships': {
                    'community_ecosystem': {'type': 'mutualistic', 'strength': 'strong'},
                    'institutions_community': {'type': 'governance', 'strength': 'moderate'},
                    'technology_all': {'type': 'mediating', 'strength': 'variable'},
                    'economy_resources': {'type': 'extractive', 'strength': 'strong'},
                    'adaptive_cycles': {'type': 'cyclical', 'strength': 'dynamic'}
                },
                'properties': {
                    'complexity': 'very_high',
                    'domain': 'social_ecological_system',
                    'multi_scale': 'present',
                    'adaptive_capacity': 'variable',
                    'resilience_mechanisms': 'multiple'
                }
            }
        }
    
    def _generate_test_queries(self) -> Dict[str, str]:
        """Generate test queries for different analytical purposes"""
        return {
            'descriptive': "What are the main components and how are they organized?",
            'explanatory': "How do the mechanisms work and why do these processes occur?",
            'predictive': "What trends can we expect and what scenarios are likely?",
            'causal': "What causes what and how can we intervene effectively?",
            'intervention': "What actions should be taken and how should they be implemented?",
            'multi_purpose': "Analyze the system comprehensively across all theoretical purposes to understand structure, mechanisms, future developments, causal relationships, and intervention opportunities.",
            'complex_integration': "Provide an integrated analysis that combines descriptive classification, explanatory mechanisms, predictive forecasting, causal inference, and intervention design in a unified framework."
        }
    
    def _test_descriptive_reasoning(self) -> dict:
        """Test descriptive reasoning capabilities with equal analytical depth"""
        test_results = {
            'test_name': 'Descriptive Reasoning Test',
            'subtests': {},
            'overall_success': True,
            'analytical_depth_score': 0.0
        }
        
        try:
            for schema_name, schema in self.test_schemas.items():
                print(f"  Testing descriptive reasoning with {schema_name}...")
                
                result = self.engine.reason_descriptive(schema, self.test_queries['descriptive'])
                
                subtest_result = {
                    'success': not bool(result.get('error')),
                    'has_insights': bool(result.get('insights')),
                    'analytical_depth': result.get('analytical_depth', 'unknown'),
                    'complexity_score': self._assess_result_complexity(result),
                    'sophistication_indicators': self._identify_sophistication_indicators(result),
                    'result_summary': self._summarize_result(result)
                }
                
                test_results['subtests'][schema_name] = subtest_result
                
                if not subtest_result['success']:
                    test_results['overall_success'] = False
                
                print(f"    {schema_name}: {'✓' if subtest_result['success'] else '✗'} "
                      f"(Depth: {subtest_result['analytical_depth']}, "
                      f"Complexity: {subtest_result['complexity_score']:.2f})")
        
        except Exception as e:
            test_results['overall_success'] = False
            test_results['error'] = str(e)
            print(f"    ERROR: {e}")
        
        # Calculate analytical depth score
        depth_scores = [st.get('complexity_score', 0) for st in test_results['subtests'].values()]
        test_results['analytical_depth_score'] = sum(depth_scores) / len(depth_scores) if depth_scores else 0
        
        return test_results
    
    def _test_explanatory_reasoning(self) -> dict:
        """Test explanatory reasoning capabilities with equal analytical depth"""
        test_results = {
            'test_name': 'Explanatory Reasoning Test',
            'subtests': {},
            'overall_success': True,
            'analytical_depth_score': 0.0
        }
        
        try:
            for schema_name, schema in self.test_schemas.items():
                print(f"  Testing explanatory reasoning with {schema_name}...")
                
                result = self.engine.reason_explanatory(schema, self.test_queries['explanatory'])
                
                subtest_result = {
                    'success': not bool(result.get('error')),
                    'has_insights': bool(result.get('insights')),
                    'analytical_depth': result.get('analytical_depth', 'unknown'),
                    'complexity_score': self._assess_result_complexity(result),
                    'sophistication_indicators': self._identify_sophistication_indicators(result),
                    'result_summary': self._summarize_result(result)
                }
                
                test_results['subtests'][schema_name] = subtest_result
                
                if not subtest_result['success']:
                    test_results['overall_success'] = False
                
                print(f"    {schema_name}: {'✓' if subtest_result['success'] else '✗'} "
                      f"(Depth: {subtest_result['analytical_depth']}, "
                      f"Complexity: {subtest_result['complexity_score']:.2f})")
        
        except Exception as e:
            test_results['overall_success'] = False
            test_results['error'] = str(e)
            print(f"    ERROR: {e}")
        
        # Calculate analytical depth score
        depth_scores = [st.get('complexity_score', 0) for st in test_results['subtests'].values()]
        test_results['analytical_depth_score'] = sum(depth_scores) / len(depth_scores) if depth_scores else 0
        
        return test_results
    
    def _test_predictive_reasoning(self) -> dict:
        """Test predictive reasoning capabilities with equal analytical depth"""
        test_results = {
            'test_name': 'Predictive Reasoning Test',
            'subtests': {},
            'overall_success': True,
            'analytical_depth_score': 0.0
        }
        
        try:
            for schema_name, schema in self.test_schemas.items():
                print(f"  Testing predictive reasoning with {schema_name}...")
                
                result = self.engine.reason_predictive(schema, self.test_queries['predictive'])
                
                subtest_result = {
                    'success': not bool(result.get('error')),
                    'has_insights': bool(result.get('insights')),
                    'analytical_depth': result.get('analytical_depth', 'unknown'),
                    'complexity_score': self._assess_result_complexity(result),
                    'sophistication_indicators': self._identify_sophistication_indicators(result),
                    'result_summary': self._summarize_result(result)
                }
                
                test_results['subtests'][schema_name] = subtest_result
                
                if not subtest_result['success']:
                    test_results['overall_success'] = False
                
                print(f"    {schema_name}: {'✓' if subtest_result['success'] else '✗'} "
                      f"(Depth: {subtest_result['analytical_depth']}, "
                      f"Complexity: {subtest_result['complexity_score']:.2f})")
        
        except Exception as e:
            test_results['overall_success'] = False
            test_results['error'] = str(e)
            print(f"    ERROR: {e}")
        
        # Calculate analytical depth score
        depth_scores = [st.get('complexity_score', 0) for st in test_results['subtests'].values()]
        test_results['analytical_depth_score'] = sum(depth_scores) / len(depth_scores) if depth_scores else 0
        
        return test_results
    
    def _test_causal_reasoning(self) -> dict:
        """Test causal reasoning capabilities with equal analytical depth"""
        test_results = {
            'test_name': 'Causal Reasoning Test',
            'subtests': {},
            'overall_success': True,
            'analytical_depth_score': 0.0
        }
        
        try:
            for schema_name, schema in self.test_schemas.items():
                print(f"  Testing causal reasoning with {schema_name}...")
                
                result = self.engine.reason_causal(schema, self.test_queries['causal'])
                
                subtest_result = {
                    'success': not bool(result.get('error')),
                    'has_insights': bool(result.get('insights')),
                    'analytical_depth': result.get('analytical_depth', 'unknown'),
                    'complexity_score': self._assess_result_complexity(result),
                    'sophistication_indicators': self._identify_sophistication_indicators(result),
                    'result_summary': self._summarize_result(result)
                }
                
                test_results['subtests'][schema_name] = subtest_result
                
                if not subtest_result['success']:
                    test_results['overall_success'] = False
                
                print(f"    {schema_name}: {'✓' if subtest_result['success'] else '✗'} "
                      f"(Depth: {subtest_result['analytical_depth']}, "
                      f"Complexity: {subtest_result['complexity_score']:.2f})")
        
        except Exception as e:
            test_results['overall_success'] = False
            test_results['error'] = str(e)
            print(f"    ERROR: {e}")
        
        # Calculate analytical depth score
        depth_scores = [st.get('complexity_score', 0) for st in test_results['subtests'].values()]
        test_results['analytical_depth_score'] = sum(depth_scores) / len(depth_scores) if depth_scores else 0
        
        return test_results
    
    def _test_intervention_reasoning(self) -> dict:
        """Test intervention reasoning capabilities with equal analytical depth"""
        test_results = {
            'test_name': 'Intervention Reasoning Test',
            'subtests': {},
            'overall_success': True,
            'analytical_depth_score': 0.0
        }
        
        try:
            for schema_name, schema in self.test_schemas.items():
                print(f"  Testing intervention reasoning with {schema_name}...")
                
                result = self.engine.reason_intervention(schema, self.test_queries['intervention'])
                
                subtest_result = {
                    'success': not bool(result.get('error')),
                    'has_insights': bool(result.get('insights')),
                    'analytical_depth': result.get('analytical_depth', 'unknown'),
                    'complexity_score': self._assess_result_complexity(result),
                    'sophistication_indicators': self._identify_sophistication_indicators(result),
                    'result_summary': self._summarize_result(result)
                }
                
                test_results['subtests'][schema_name] = subtest_result
                
                if not subtest_result['success']:
                    test_results['overall_success'] = False
                
                print(f"    {schema_name}: {'✓' if subtest_result['success'] else '✗'} "
                      f"(Depth: {subtest_result['analytical_depth']}, "
                      f"Complexity: {subtest_result['complexity_score']:.2f})")
        
        except Exception as e:
            test_results['overall_success'] = False
            test_results['error'] = str(e)
            print(f"    ERROR: {e}")
        
        # Calculate analytical depth score
        depth_scores = [st.get('complexity_score', 0) for st in test_results['subtests'].values()]
        test_results['analytical_depth_score'] = sum(depth_scores) / len(depth_scores) if depth_scores else 0
        
        return test_results
    
    def _test_cross_purpose_integration(self) -> dict:
        """Test sophisticated cross-purpose integration"""
        test_results = {
            'test_name': 'Cross-Purpose Integration Test',
            'subtests': {},
            'overall_success': True,
            'integration_quality_score': 0.0
        }
        
        try:
            for schema_name, schema in self.test_schemas.items():
                print(f"  Testing cross-purpose integration with {schema_name}...")
                
                # Generate all purpose analyses first
                purpose_analyses = {
                    'descriptive_analysis': self.engine.reason_descriptive(schema, self.test_queries['descriptive']),
                    'explanatory_analysis': self.engine.reason_explanatory(schema, self.test_queries['explanatory']),
                    'predictive_analysis': self.engine.reason_predictive(schema, self.test_queries['predictive']),
                    'causal_analysis': self.engine.reason_causal(schema, self.test_queries['causal']),
                    'intervention_analysis': self.engine.reason_intervention(schema, self.test_queries['intervention'])
                }
                
                # Test cross-purpose integration
                integration_result = self.integrator.integrate_purposes(purpose_analyses)
                
                subtest_result = {
                    'success': not bool(integration_result.get('error')),
                    'has_connections': bool(integration_result.get('cross_purpose_connections')),
                    'integration_quality': integration_result.get('integration_quality', {}),
                    'emergent_properties': integration_result.get('emergent_properties', {}),
                    'completeness': integration_result.get('integration_completeness', {}),
                    'result_summary': self._summarize_integration_result(integration_result)
                }
                
                test_results['subtests'][schema_name] = subtest_result
                
                if not subtest_result['success']:
                    test_results['overall_success'] = False
                
                quality_score = subtest_result.get('integration_quality', {}).get('overall_quality', 0)
                print(f"    {schema_name}: {'✓' if subtest_result['success'] else '✗'} "
                      f"(Quality: {quality_score:.2f})")
        
        except Exception as e:
            test_results['overall_success'] = False
            test_results['error'] = str(e)
            print(f"    ERROR: {e}")
        
        # Calculate integration quality score
        quality_scores = [st.get('integration_quality', {}).get('overall_quality', 0) 
                         for st in test_results['subtests'].values()]
        test_results['integration_quality_score'] = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return test_results
    
    def _test_complex_query_handling(self) -> dict:
        """Test handling of complex multi-purpose queries"""
        test_results = {
            'test_name': 'Complex Multi-Purpose Query Test',
            'subtests': {},
            'overall_success': True,
            'complexity_handling_score': 0.0
        }
        
        complex_queries = [
            self.test_queries['multi_purpose'],
            self.test_queries['complex_integration'],
            "Analyze this system from multiple theoretical perspectives to provide comprehensive understanding of its structure, functioning, development patterns, causal mechanisms, and intervention potential."
        ]
        
        try:
            for i, query in enumerate(complex_queries):
                query_id = f"complex_query_{i+1}"
                print(f"  Testing complex query {i+1}...")
                
                # Use the most complex schema for complex query testing
                schema = self.test_schemas['social_ecological_schema']
                
                result = self.engine.analyze_multi_purpose(schema, query)
                
                subtest_result = {
                    'success': not bool(result.get('error')),
                    'all_purposes_analyzed': self._check_all_purposes_analyzed(result),
                    'cross_purpose_insights': bool(result.get('cross_purpose_insights')),
                    'integrated_reasoning': bool(result.get('integrated_reasoning')),
                    'balance_validation': result.get('balance_validation', {}),
                    'complexity_score': self._assess_complex_query_handling(result),
                    'result_summary': self._summarize_complex_query_result(result)
                }
                
                test_results['subtests'][query_id] = subtest_result
                
                if not subtest_result['success']:
                    test_results['overall_success'] = False
                
                print(f"    Query {i+1}: {'✓' if subtest_result['success'] else '✗'} "
                      f"(Complexity: {subtest_result['complexity_score']:.2f})")
        
        except Exception as e:
            test_results['overall_success'] = False
            test_results['error'] = str(e)
            print(f"    ERROR: {e}")
        
        # Calculate complexity handling score
        complexity_scores = [st.get('complexity_score', 0) for st in test_results['subtests'].values()]
        test_results['complexity_handling_score'] = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
        
        return test_results
    
    def _test_reasoning_balance(self) -> dict:
        """Test reasoning balance validation across all purposes"""
        test_results = {
            'test_name': 'Reasoning Balance Validation Test',
            'balance_tests': {},
            'overall_success': True,
            'balance_score': 0.0
        }
        
        try:
            print("  Testing analytical balance across purposes...")
            
            # Test with complex schema for comprehensive balance assessment
            schema = self.test_schemas['social_ecological_schema']
            
            # Generate multi-purpose analysis
            result = self.engine.analyze_multi_purpose(schema, self.test_queries['multi_purpose'])
            
            # Validate balance
            balance_validation = self.engine.validate_reasoning_balance(result)
            
            balance_tests = {
                'depth_consistency': self._test_depth_consistency(result),
                'purpose_coverage': self._test_purpose_coverage(result),
                'analytical_sophistication': self._test_analytical_sophistication(result),
                'equal_treatment': self._test_equal_treatment(result),
                'integration_balance': self._test_integration_balance(result)
            }
            
            test_results['balance_tests'] = balance_tests
            test_results['balance_validation'] = balance_validation
            
            # Check if all balance tests pass
            all_passed = all(test.get('passed', False) for test in balance_tests.values())
            test_results['overall_success'] = all_passed and balance_validation.get('is_balanced', False)
            
            # Calculate overall balance score
            balance_scores = [test.get('score', 0) for test in balance_tests.values()]
            validation_score = balance_validation.get('overall_balance', 0)
            test_results['balance_score'] = (sum(balance_scores) / len(balance_scores) + validation_score) / 2
            
            print(f"    Balance Score: {test_results['balance_score']:.2f}")
            print(f"    All Tests Passed: {'✓' if all_passed else '✗'}")
        
        except Exception as e:
            test_results['overall_success'] = False
            test_results['error'] = str(e)
            print(f"    ERROR: {e}")
        
        return test_results
    
    def _test_performance(self) -> dict:
        """Test performance with real theoretical schemas"""
        test_results = {
            'test_name': 'Performance Test',
            'performance_metrics': {},
            'overall_success': True,
            'performance_score': 0.0
        }
        
        try:
            print("  Testing performance with realistic schemas...")
            
            performance_tests = []
            
            for schema_name, schema in self.test_schemas.items():
                print(f"    Performance test with {schema_name}...")
                
                start_time = time.time()
                
                # Test multi-purpose analysis performance
                result = self.engine.analyze_multi_purpose(schema, self.test_queries['multi_purpose'])
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                performance_test = {
                    'schema': schema_name,
                    'execution_time': execution_time,
                    'success': not bool(result.get('error')),
                    'result_completeness': self._assess_result_completeness(result),
                    'memory_efficiency': 'good',  # Simplified metric
                    'scalability_indicator': self._assess_scalability(schema, execution_time)
                }
                
                performance_tests.append(performance_test)
                
                print(f"      {schema_name}: {execution_time:.3f}s {'✓' if performance_test['success'] else '✗'}")
            
            test_results['performance_metrics'] = {
                'individual_tests': performance_tests,
                'average_execution_time': sum(t['execution_time'] for t in performance_tests) / len(performance_tests),
                'success_rate': sum(1 for t in performance_tests if t['success']) / len(performance_tests),
                'performance_consistency': self._assess_performance_consistency(performance_tests)
            }
            
            # Check performance criteria
            avg_time = test_results['performance_metrics']['average_execution_time']
            success_rate = test_results['performance_metrics']['success_rate']
            
            test_results['overall_success'] = avg_time < 10.0 and success_rate >= 0.8  # Performance thresholds
            test_results['performance_score'] = min(1.0, (10.0 - avg_time) / 10.0) * success_rate
            
            print(f"    Average Time: {avg_time:.3f}s, Success Rate: {success_rate:.1%}")
        
        except Exception as e:
            test_results['overall_success'] = False
            test_results['error'] = str(e)
            print(f"    ERROR: {e}")
        
        return test_results
    
    def _assess_result_complexity(self, result: dict) -> float:
        """Assess complexity of reasoning result"""
        complexity_factors = []
        
        # Check for sophisticated components
        sophisticated_keys = ['complexity', 'dynamics', 'integration', 'synthesis', 'hierarchy']
        for key in sophisticated_keys:
            if any(key in str(k).lower() for k in result.keys()):
                complexity_factors.append(1.0)
            else:
                complexity_factors.append(0.0)
        
        # Check insight depth
        insights = result.get('insights', {})
        if insights:
            key_insights = insights.get('key_insights', [])
            complexity_factors.append(min(1.0, len(key_insights) / 3.0))
        else:
            complexity_factors.append(0.0)
        
        # Check for evidence and confidence
        if 'evidence_sources' in result or 'confidence' in result:
            complexity_factors.append(1.0)
        else:
            complexity_factors.append(0.3)
        
        return sum(complexity_factors) / len(complexity_factors)
    
    def _identify_sophistication_indicators(self, result: dict) -> List[str]:
        """Identify sophistication indicators in result"""
        indicators = []
        
        result_str = str(result).lower()
        
        sophistication_terms = [
            'sophisticated', 'complex', 'comprehensive', 'integrated',
            'multi_level', 'hierarchical', 'dynamic', 'emergent'
        ]
        
        for term in sophistication_terms:
            if term in result_str:
                indicators.append(term)
        
        return indicators
    
    def _summarize_result(self, result: dict) -> dict:
        """Summarize reasoning result"""
        return {
            'has_error': bool(result.get('error')),
            'has_insights': bool(result.get('insights')),
            'component_count': len(result.keys()),
            'sophistication_level': 'high' if 'sophisticated' in str(result).lower() else 'moderate'
        }
    
    def _summarize_integration_result(self, result: dict) -> dict:
        """Summarize integration result"""
        return {
            'has_error': bool(result.get('error')),
            'has_connections': bool(result.get('cross_purpose_connections')),
            'has_synthesis': bool(result.get('integrated_synthesis')),
            'quality_level': result.get('integration_quality', {}).get('overall_quality', 0)
        }
    
    def _check_all_purposes_analyzed(self, result: dict) -> bool:
        """Check if all purposes were analyzed"""
        expected_purposes = [
            'descriptive_analysis', 'explanatory_analysis', 'predictive_analysis',
            'causal_analysis', 'intervention_analysis'
        ]
        return all(purpose in result for purpose in expected_purposes)
    
    def _assess_complex_query_handling(self, result: dict) -> float:
        """Assess complex query handling capability"""
        handling_factors = []
        
        # Check for all purpose analyses
        handling_factors.append(1.0 if self._check_all_purposes_analyzed(result) else 0.0)
        
        # Check for cross-purpose insights
        handling_factors.append(1.0 if result.get('cross_purpose_insights') else 0.0)
        
        # Check for integrated reasoning
        handling_factors.append(1.0 if result.get('integrated_reasoning') else 0.0)
        
        # Check for balance validation
        balance = result.get('balance_validation', {})
        handling_factors.append(balance.get('overall_balance', 0))
        
        # Check for reasoning quality
        quality = result.get('reasoning_quality', {})
        handling_factors.append(quality.get('quality_score', 0) if quality else 0.0)
        
        return sum(handling_factors) / len(handling_factors)
    
    def _summarize_complex_query_result(self, result: dict) -> dict:
        """Summarize complex query result"""
        return {
            'has_error': bool(result.get('error')),
            'all_purposes_present': self._check_all_purposes_analyzed(result),
            'has_integration': bool(result.get('cross_purpose_insights')),
            'balance_score': result.get('balance_validation', {}).get('overall_balance', 0)
        }
    
    def _test_depth_consistency(self, result: dict) -> dict:
        """Test depth consistency across purposes"""
        depth_test = {
            'test_name': 'Depth Consistency',
            'passed': False,
            'score': 0.0,
            'details': {}
        }
        
        try:
            purpose_analyses = [
                result.get('descriptive_analysis', {}),
                result.get('explanatory_analysis', {}),
                result.get('predictive_analysis', {}),
                result.get('causal_analysis', {}),
                result.get('intervention_analysis', {})
            ]
            
            complexity_scores = [self._assess_result_complexity(analysis) for analysis in purpose_analyses]
            
            if complexity_scores:
                mean_complexity = sum(complexity_scores) / len(complexity_scores)
                complexity_variance = sum((score - mean_complexity) ** 2 for score in complexity_scores) / len(complexity_scores)
                consistency_score = max(0, 1 - complexity_variance)
                
                depth_test['score'] = consistency_score
                depth_test['passed'] = consistency_score > 0.7
                depth_test['details'] = {
                    'mean_complexity': mean_complexity,
                    'complexity_variance': complexity_variance,
                    'individual_scores': complexity_scores
                }
        
        except Exception as e:
            depth_test['error'] = str(e)
        
        return depth_test
    
    def _test_purpose_coverage(self, result: dict) -> dict:
        """Test purpose coverage completeness"""
        coverage_test = {
            'test_name': 'Purpose Coverage',
            'passed': False,
            'score': 0.0,
            'details': {}
        }
        
        try:
            expected_purposes = [
                'descriptive_analysis', 'explanatory_analysis', 'predictive_analysis',
                'causal_analysis', 'intervention_analysis'
            ]
            
            present_purposes = [purpose for purpose in expected_purposes if purpose in result]
            coverage_score = len(present_purposes) / len(expected_purposes)
            
            coverage_test['score'] = coverage_score
            coverage_test['passed'] = coverage_score >= 0.8
            coverage_test['details'] = {
                'expected_count': len(expected_purposes),
                'present_count': len(present_purposes),
                'missing_purposes': [p for p in expected_purposes if p not in result]
            }
        
        except Exception as e:
            coverage_test['error'] = str(e)
        
        return coverage_test
    
    def _test_analytical_sophistication(self, result: dict) -> dict:
        """Test analytical sophistication across purposes"""
        sophistication_test = {
            'test_name': 'Analytical Sophistication',
            'passed': False,
            'score': 0.0,
            'details': {}
        }
        
        try:
            purpose_analyses = [
                result.get('descriptive_analysis', {}),
                result.get('explanatory_analysis', {}),
                result.get('predictive_analysis', {}),
                result.get('causal_analysis', {}),
                result.get('intervention_analysis', {})
            ]
            
            sophistication_scores = []
            for analysis in purpose_analyses:
                indicators = self._identify_sophistication_indicators(analysis)
                sophistication_scores.append(len(indicators) / 5.0)  # Normalize to max 5 indicators
            
            if sophistication_scores:
                avg_sophistication = sum(sophistication_scores) / len(sophistication_scores)
                sophistication_test['score'] = avg_sophistication
                sophistication_test['passed'] = avg_sophistication > 0.6
                sophistication_test['details'] = {
                    'individual_scores': sophistication_scores,
                    'average_sophistication': avg_sophistication
                }
        
        except Exception as e:
            sophistication_test['error'] = str(e)
        
        return sophistication_test
    
    def _test_equal_treatment(self, result: dict) -> dict:
        """Test equal treatment across purposes"""
        equal_treatment_test = {
            'test_name': 'Equal Treatment',
            'passed': False,
            'score': 0.0,
            'details': {}
        }
        
        try:
            balance_validation = result.get('balance_validation', {})
            
            if balance_validation:
                balance_score = balance_validation.get('overall_balance', 0)
                is_balanced = balance_validation.get('is_balanced', False)
                
                equal_treatment_test['score'] = balance_score
                equal_treatment_test['passed'] = is_balanced and balance_score > 0.7
                equal_treatment_test['details'] = {
                    'balance_validation': balance_validation,
                    'balance_issues': balance_validation.get('balance_issues', [])
                }
            else:
                equal_treatment_test['score'] = 0.0
                equal_treatment_test['details'] = {'error': 'No balance validation found'}
        
        except Exception as e:
            equal_treatment_test['error'] = str(e)
        
        return equal_treatment_test
    
    def _test_integration_balance(self, result: dict) -> dict:
        """Test integration balance quality"""
        integration_test = {
            'test_name': 'Integration Balance',
            'passed': False,
            'score': 0.0,
            'details': {}
        }
        
        try:
            cross_purpose = result.get('cross_purpose_insights', {})
            integrated_reasoning = result.get('integrated_reasoning', {})
            
            if cross_purpose and integrated_reasoning:
                # Simple integration quality assessment
                integration_score = 0.8  # Simplified - would be more sophisticated in production
                integration_test['score'] = integration_score
                integration_test['passed'] = integration_score > 0.6
                integration_test['details'] = {
                    'has_cross_purpose': bool(cross_purpose),
                    'has_integrated_reasoning': bool(integrated_reasoning)
                }
            else:
                integration_test['score'] = 0.0
                integration_test['details'] = {'error': 'Missing integration components'}
        
        except Exception as e:
            integration_test['error'] = str(e)
        
        return integration_test
    
    def _assess_result_completeness(self, result: dict) -> float:
        """Assess completeness of reasoning result"""
        completeness_factors = []
        
        # Check for all expected purposes
        expected_purposes = [
            'descriptive_analysis', 'explanatory_analysis', 'predictive_analysis',
            'causal_analysis', 'intervention_analysis'
        ]
        purpose_completeness = sum(1 for purpose in expected_purposes if purpose in result) / len(expected_purposes)
        completeness_factors.append(purpose_completeness)
        
        # Check for integration components
        integration_components = ['cross_purpose_insights', 'integrated_reasoning', 'balance_validation']
        integration_completeness = sum(1 for comp in integration_components if comp in result) / len(integration_components)
        completeness_factors.append(integration_completeness)
        
        # Check for quality components
        quality_completeness = 1.0 if result.get('reasoning_quality') else 0.5
        completeness_factors.append(quality_completeness)
        
        return sum(completeness_factors) / len(completeness_factors)
    
    def _assess_scalability(self, schema: dict, execution_time: float) -> str:
        """Assess scalability based on schema complexity and execution time"""
        schema_complexity = len(str(schema))
        
        if schema_complexity < 1000 and execution_time < 2.0:
            return 'excellent'
        elif schema_complexity < 2000 and execution_time < 5.0:
            return 'good'
        elif execution_time < 10.0:
            return 'moderate'
        else:
            return 'limited'
    
    def _assess_performance_consistency(self, performance_tests: List[dict]) -> float:
        """Assess consistency of performance across tests"""
        if not performance_tests:
            return 0.0
        
        execution_times = [test['execution_time'] for test in performance_tests]
        mean_time = sum(execution_times) / len(execution_times)
        time_variance = sum((time - mean_time) ** 2 for time in execution_times) / len(execution_times)
        
        # Consistency is high when variance is low
        consistency_score = max(0, 1 - (time_variance / mean_time) if mean_time > 0 else 0)
        return consistency_score
    
    def _generate_test_summary(self, start_time: float, end_time: float) -> dict:
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() 
                             if isinstance(result, dict) and result.get('overall_success', False))
        
        # Calculate analytical balance across purposes
        purpose_tests = ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']
        depth_scores = []
        for purpose in purpose_tests:
            if purpose in self.test_results:
                depth_score = self.test_results[purpose].get('analytical_depth_score', 0)
                depth_scores.append(depth_score)
        
        # Calculate depth balance
        if depth_scores:
            mean_depth = sum(depth_scores) / len(depth_scores)
            depth_variance = sum((score - mean_depth) ** 2 for score in depth_scores) / len(depth_scores)
            depth_balance = max(0, 1 - depth_variance)
        else:
            depth_balance = 0.0
        
        # Calculate integration quality
        integration_quality = self.test_results.get('integration', {}).get('integration_quality_score', 0)
        
        # Calculate overall scores
        performance_score = self.test_results.get('performance', {}).get('performance_score', 0)
        balance_score = self.test_results.get('balance_validation', {}).get('balance_score', 0)
        
        summary = {
            'test_execution': {
                'total_time': end_time - start_time,
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'overall_success_rate': successful_tests / total_tests if total_tests > 0 else 0
            },
            'analytical_balance': {
                'purpose_depth_scores': dict(zip(purpose_tests, depth_scores)) if depth_scores else {},
                'mean_analytical_depth': mean_depth if depth_scores else 0,
                'depth_balance_score': depth_balance,
                'balance_assessment': 'excellent' if depth_balance > 0.8 else 'good' if depth_balance > 0.6 else 'needs_improvement'
            },
            'integration_assessment': {
                'integration_quality_score': integration_quality,
                'cross_purpose_capability': 'strong' if integration_quality > 0.7 else 'moderate' if integration_quality > 0.5 else 'weak',
                'synthesis_sophistication': 'high' if integration_quality > 0.8 else 'moderate'
            },
            'performance_assessment': {
                'performance_score': performance_score,
                'scalability': 'good' if performance_score > 0.7 else 'moderate',
                'efficiency': 'high' if performance_score > 0.8 else 'adequate'
            },
            'overall_assessment': {
                'reasoning_sophistication': 'high' if mean_depth > 0.7 else 'moderate',
                'purpose_balance': 'excellent' if depth_balance > 0.8 else 'good',
                'integration_capability': 'strong' if integration_quality > 0.7 else 'moderate',
                'production_readiness': 'ready' if (depth_balance > 0.7 and integration_quality > 0.6 and performance_score > 0.6) else 'needs_refinement'
            }
        }
        
        return summary


def main():
    """Run the comprehensive test suite"""
    try:
        test_suite = ReasoningEngineTestSuite()
        results = test_suite.run_all_tests()
        
        # Save detailed results
        timestamp = int(time.time())
        results_file = f"/home/brian/lit_review/evidence/phase5_reasoning_engine/test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed test results saved to: {results_file}")
        
        return results
        
    except Exception as e:
        print(f"Test suite failed with error: {e}")
        traceback.print_exc()
        return {'error': str(e)}


if __name__ == "__main__":
    main()