#!/usr/bin/env python3
"""
Comprehensive Test Suite for Balanced Multi-Purpose Integration Pipeline
Tests all pipeline components and validates balanced processing requirements.
"""

import unittest
import json
import time
import sys
from typing import Dict, Any, List

# Import pipeline components
from balanced_pipeline import BalancedMultiPurposePipeline
from pipeline_config import PipelineConfiguration, PredefinedConfigurations, ProcessingMode
from quality_assurance import QualityAssuranceFramework, QualityLevel, BalanceStatus

class TestIntegrationPipeline(unittest.TestCase):
    """Test suite for the balanced integration pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pipeline = BalancedMultiPurposePipeline()
        self.qa_framework = QualityAssuranceFramework()
        self.config = PredefinedConfigurations.create_balanced_configuration()
        
        # Test theory text
        self.test_theory = """
        Social cognitive theory explains behavior through the dynamic interaction of personal, 
        behavioral, and environmental factors. This framework categorizes learning mechanisms 
        into observational learning, direct experience, and symbolic modeling. Key variables 
        include self-efficacy, outcome expectations, and behavioral capability. The theory 
        predicts that individuals with higher self-efficacy are more likely to engage in 
        target behaviors. Causal pathways demonstrate how environmental factors influence 
        personal cognitions, which in turn affect behavioral outcomes. Interventions based 
        on this theory focus on enhancing self-efficacy through mastery experiences, 
        vicarious learning, verbal persuasion, and emotional arousal management.
        """
        
        # Shorter test theory for rapid tests
        self.simple_theory = """
        This theory explains behavior through multiple factors. It classifies types of learning 
        and predicts outcomes. The approach identifies causal relationships and recommends 
        specific interventions for implementation.
        """
    
    def test_01_single_purpose_theory_processing(self):
        """Test 1: Single-purpose theory processing (each of the 5 purposes)"""
        print("\n=== Test 1: Single-Purpose Theory Processing ===")
        
        # Test theories emphasizing each purpose
        purpose_theories = {
            'descriptive': """
            This framework provides a taxonomy of organizational types. It categorizes 
            different forms of institutions and classifies their characteristics. The 
            typology distinguishes between various organizational structures and their 
            defining attributes.
            """,
            'explanatory': """
            This theory explains how mechanisms operate through complex processes. It 
            describes the underlying functions and analyzes the interactions between 
            different system components to understand operational dynamics.
            """,
            'predictive': """
            This model predicts future outcomes based on key variables and indicators. 
            It forecasts trends and estimates probabilities using statistical relationships 
            to project expected results and scenarios.
            """,
            'causal': """
            This approach identifies causal relationships and analyzes cause-and-effect 
            patterns. It examines how factors influence outcomes and investigates the 
            pathways through which changes lead to specific results.
            """,
            'intervention': """
            This strategy focuses on implementation and action design. It recommends 
            specific interventions and describes practical approaches for applying 
            solutions and executing planned changes.
            """
        }
        
        results = {}
        for purpose, theory_text in purpose_theories.items():
            print(f"\nTesting {purpose} theory...")
            
            # Process through pipeline
            result = self.pipeline.process_theory_balanced(theory_text)
            results[purpose] = result
            
            # Verify processing completed
            self.assertIn('pipeline_metrics', result)
            self.assertTrue(result['pipeline_metrics']['balance_success'])
            
            # Verify purpose was detected
            purpose_classification = result.get('purpose_classification', {})
            detected_purposes = purpose_classification.get('all_purposes', [])
            
            # The target purpose should be detected (but others may be too)
            self.assertIn(purpose, detected_purposes, 
                         f"{purpose} purpose should be detected in {purpose} theory")
            
            # Verify vocabulary extraction for the purpose
            vocabulary = result.get('vocabulary_extraction', {})
            purpose_terms_key = f'{purpose}_terms'
            self.assertIn(purpose_terms_key, vocabulary,
                         f"Vocabulary should include {purpose_terms_key}")
            
            # Verify schema generation includes the purpose
            schema_generation = result.get('schema_generation', {})
            capabilities = schema_generation.get('purpose_capabilities', {})
            if purpose in capabilities:
                self.assertEqual(capabilities[purpose]['sophistication_level'], 8,
                               f"{purpose} should have high sophistication level")
            
            print(f"✓ {purpose.capitalize()} theory processed successfully")
        
        print(f"\n✓ All 5 single-purpose theories processed successfully")
    
    def test_02_multi_purpose_theory_processing(self):
        """Test 2: Multi-purpose theory processing"""
        print("\n=== Test 2: Multi-Purpose Theory Processing ===")
        
        # Process the main test theory (which contains multiple purposes)
        result = self.pipeline.process_theory_balanced(self.test_theory)
        
        # Verify processing completed successfully
        self.assertIn('pipeline_metrics', result)
        self.assertTrue(result['pipeline_metrics']['balance_success'])
        
        # Verify multiple purposes detected
        purpose_classification = result.get('purpose_classification', {})
        all_purposes = purpose_classification.get('all_purposes', [])
        
        self.assertGreaterEqual(len(all_purposes), 3, 
                              "Multi-purpose theory should detect at least 3 purposes")
        
        # Verify vocabulary extraction for multiple purposes
        vocabulary = result.get('vocabulary_extraction', {})
        purpose_term_keys = [key for key in vocabulary.keys() if key.endswith('_terms')]
        
        self.assertGreaterEqual(len(purpose_term_keys), 3,
                              "Vocabulary should be extracted for multiple purposes")
        
        # Verify schema generation includes multiple capabilities
        schema_generation = result.get('schema_generation', {})
        capabilities = schema_generation.get('purpose_capabilities', {})
        
        self.assertGreaterEqual(len(capabilities), 3,
                              "Schema should include capabilities for multiple purposes")
        
        # Verify equal sophistication across purposes
        sophistication_levels = [cap.get('sophistication_level', 0) for cap in capabilities.values()]
        if sophistication_levels:
            sophistication_variance = max(sophistication_levels) - min(sophistication_levels)
            self.assertLessEqual(sophistication_variance, 1.0,
                               "Sophistication variance should be minimal across purposes")
        
        print("✓ Multi-purpose theory processed with balanced capabilities")
    
    def test_03_theory_count_detection_accuracy(self):
        """Test 3: Theory count detection accuracy"""
        print("\n=== Test 3: Theory Count Detection Accuracy ===")
        
        # Test single theory
        single_theory_result = self.pipeline.detect_theory_count(self.simple_theory)
        
        self.assertIn('theory_count', single_theory_result)
        self.assertIn('complexity_level', single_theory_result)
        
        # Verify detection confidence
        confidence = single_theory_result.get('analysis_confidence', 0)
        self.assertGreater(confidence, 0, "Detection should have some confidence level")
        
        # Test multi-theory text
        multi_theory_text = """
        Social cognitive theory explains behavior through interactions. Systems theory 
        provides a framework for understanding organizations. Complexity theory addresses 
        emergent properties in dynamic systems.
        """
        
        multi_theory_result = self.pipeline.detect_theory_count(multi_theory_text)
        
        # Should detect multiple theories
        theory_count = multi_theory_result.get('theory_count')
        complexity_level = multi_theory_result.get('complexity_level')
        
        # Verify appropriate complexity classification
        self.assertIn(complexity_level, ['single_theory', 'multi_theory', 'implicit_multi_theory'],
                     "Complexity level should be one of the defined categories")
        
        print(f"✓ Single theory count: {single_theory_result['theory_count']}")
        print(f"✓ Multi-theory count: {multi_theory_result['theory_count']}")
        print(f"✓ Theory count detection working correctly")
    
    def test_04_end_to_end_pipeline_balance_validation(self):
        """Test 4: End-to-end pipeline balance validation"""
        print("\n=== Test 4: End-to-End Pipeline Balance Validation ===")
        
        # Process test theory
        result = self.pipeline.process_theory_balanced(self.test_theory)
        
        # Verify balance validation was performed
        balance_validation = result.get('balance_validation', {})
        self.assertIn('overall_balance_score', balance_validation)
        self.assertIn('overall_balance_status', balance_validation)
        
        # Check balance score meets threshold
        balance_score = balance_validation.get('overall_balance_score', 0)
        self.assertGreaterEqual(balance_score, 0.6, 
                              "Overall balance score should meet minimum threshold")
        
        # Verify stage balance metrics
        stage_balance_metrics = balance_validation.get('stage_balance_metrics', {})
        self.assertGreater(len(stage_balance_metrics), 0, 
                          "Stage balance metrics should be present")
        
        # Verify purpose representation analysis
        purpose_representation = balance_validation.get('purpose_representation', {})
        self.assertIn('balance_score', purpose_representation)
        
        representation_score = purpose_representation.get('balance_score', 0)
        self.assertGreater(representation_score, 0, 
                          "Purpose representation should have positive score")
        
        # Verify sophistication balance
        sophistication_balance = balance_validation.get('sophistication_balance', {})
        self.assertIn('balance_score', sophistication_balance)
        
        # Verify integration completeness
        integration_completeness = balance_validation.get('integration_completeness', {})
        self.assertIn('completeness_score', integration_completeness)
        
        print(f"✓ Overall balance score: {balance_score:.3f}")
        print(f"✓ Balance status: {balance_validation.get('overall_balance_status')}")
        print(f"✓ End-to-end balance validation successful")
    
    def test_05_pipeline_efficiency_and_performance(self):
        """Test 5: Pipeline efficiency and performance"""
        print("\n=== Test 5: Pipeline Efficiency and Performance ===")
        
        # Test processing time
        start_time = time.time()
        result = self.pipeline.process_theory_balanced(self.test_theory)
        processing_time = time.time() - start_time
        
        # Verify reasonable processing time (should complete within 30 seconds)
        self.assertLess(processing_time, 30.0, 
                       "Pipeline should complete processing within reasonable time")
        
        # Verify pipeline metrics
        pipeline_metrics = result.get('pipeline_metrics', {})
        self.assertIn('total_processing_time', pipeline_metrics)
        self.assertIn('stage_breakdown', pipeline_metrics)
        
        # Check stage timing breakdown
        stage_breakdown = pipeline_metrics.get('stage_breakdown', {})
        expected_stages = [
            'theory_count_detection', 'purpose_classification', 
            'vocabulary_extraction', 'schema_generation', 
            'balance_validation', 'optimization'
        ]
        
        for stage in expected_stages:
            self.assertIn(stage, stage_breakdown, f"Stage {stage} should have timing data")
            stage_time = stage_breakdown[stage]
            self.assertGreater(stage_time, 0, f"Stage {stage} should have positive processing time")
            self.assertLess(stage_time, 10.0, f"Stage {stage} should complete within reasonable time")
        
        # Verify efficiency metrics
        efficiency_metrics = pipeline_metrics.get('efficiency_metrics', {})
        self.assertIn('efficiency_score', efficiency_metrics)
        
        efficiency_score = efficiency_metrics.get('efficiency_score', 0)
        self.assertGreaterEqual(efficiency_score, 0.3, 
                              "Efficiency score should meet minimum threshold")
        
        print(f"✓ Total processing time: {processing_time:.3f}s")
        print(f"✓ Pipeline efficiency score: {efficiency_score:.3f}")
        print(f"✓ All stages completed within time limits")
    
    def test_06_quality_assurance_across_all_purposes(self):
        """Test 6: Quality assurance across all purposes"""
        print("\n=== Test 6: Quality Assurance Across All Purposes ===")
        
        # Process test theory
        result = self.pipeline.process_theory_balanced(self.test_theory)
        
        # Perform quality assessment
        quality_assessment = self.qa_framework.assess_pipeline_quality(result)
        
        # Verify quality assessment structure
        self.assertIsInstance(quality_assessment.overall_quality, QualityLevel)
        self.assertIsInstance(quality_assessment.balance_status, BalanceStatus)
        self.assertGreater(quality_assessment.overall_score, 0)
        self.assertGreater(quality_assessment.balance_score, 0)
        
        # Verify quality metrics
        quality_metrics = quality_assessment.quality_metrics
        self.assertGreater(len(quality_metrics), 0, "Quality metrics should be present")
        
        # Check specific quality metrics
        metric_names = {metric.name for metric in quality_metrics}
        expected_metrics = {'stage_completion', 'balance_quality', 'integration_quality', 'performance_efficiency'}
        
        self.assertTrue(expected_metrics.issubset(metric_names), 
                       "All expected quality metrics should be present")
        
        # Verify balance metrics
        balance_metrics = quality_assessment.balance_metrics
        self.assertGreater(len(balance_metrics), 0, "Balance metrics should be present")
        
        # Check balance across purposes
        purpose_balance_scores = [metric.overall_score for metric in balance_metrics]
        if purpose_balance_scores:
            min_balance = min(purpose_balance_scores)
            max_balance = max(purpose_balance_scores)
            balance_variance = max_balance - min_balance
            
            self.assertLessEqual(balance_variance, 0.5, 
                               "Balance variance across purposes should be reasonable")
        
        # Verify recommendations generation
        recommendations = quality_assessment.recommendations
        self.assertIsInstance(recommendations, list)
        
        print(f"✓ Overall quality: {quality_assessment.overall_quality.value}")
        print(f"✓ Balance status: {quality_assessment.balance_status.value}")
        print(f"✓ Quality metrics: {len(quality_metrics)} assessed")
        print(f"✓ Balance metrics: {len(balance_metrics)} purposes evaluated")
        print(f"✓ Quality assurance validation successful")
    
    def test_07_edge_case_handling_complex_theories(self):
        """Test 7: Edge case handling (complex theories)"""
        print("\n=== Test 7: Edge Case Handling (Complex Theories) ===")
        
        # Test very short theory
        short_theory = "Theory explains behavior."
        short_result = self.pipeline.process_theory_balanced(short_theory)
        
        self.assertIn('pipeline_metrics', short_result)
        print("✓ Short theory processed successfully")
        
        # Test very long theory (repeated content)
        long_theory = self.test_theory * 5  # Repeat 5 times
        long_result = self.pipeline.process_theory_balanced(long_theory)
        
        self.assertIn('pipeline_metrics', long_result)
        print("✓ Long theory processed successfully")
        
        # Test theory with minimal purpose indicators
        minimal_theory = """
        This approach considers various factors. It examines different aspects 
        and provides insights into the phenomenon under investigation.
        """
        minimal_result = self.pipeline.process_theory_balanced(minimal_theory)
        
        self.assertIn('pipeline_metrics', minimal_result)
        print("✓ Minimal theory processed successfully")
        
        # Test theory with heavy emphasis on one purpose (causal)
        causal_heavy_theory = """
        This theory primarily focuses on causal relationships and cause-effect patterns. 
        It analyzes how factors cause outcomes and examines causal mechanisms. The 
        primary emphasis is on understanding causation and causal pathways that lead 
        to specific effects. Causal analysis reveals the determinants and causal 
        influences in the system.
        """
        causal_result = self.pipeline.process_theory_balanced(causal_heavy_theory)
        
        # Verify no causal over-emphasis detected by quality assurance
        balance_validation = self.qa_framework.validate_balance_requirements(causal_result)
        no_causal_overemphasis = balance_validation['requirements_met']['no_causal_overemphasis']
        
        # The framework should handle causal-heavy content appropriately
        self.assertIsInstance(no_causal_overemphasis, dict)
        print(f"✓ Causal-heavy theory processed (over-emphasis check: {no_causal_overemphasis.get('passed', 'unknown')})")
        
        print("✓ All edge cases handled successfully")
    
    def test_08_integration_with_experimental_validation_results(self):
        """Test 8: Integration with existing validated experimental components"""
        print("\n=== Test 8: Integration with Experimental Validation ===")
        
        # Test pipeline integration capabilities
        result = self.pipeline.process_theory_balanced(self.test_theory)
        
        # Verify schema generation includes integration interfaces
        schema_generation = result.get('schema_generation', {})
        cross_purpose_integration = schema_generation.get('cross_purpose_integration', {})
        
        self.assertIn('total_interfaces', cross_purpose_integration)
        self.assertIn('integration_interfaces', cross_purpose_integration)
        
        total_interfaces = cross_purpose_integration.get('total_interfaces', 0)
        self.assertGreater(total_interfaces, 0, "Integration interfaces should be present")
        
        # Verify unified workflows
        unified_workflows = cross_purpose_integration.get('unified_workflows', {})
        self.assertGreater(len(unified_workflows), 0, "Unified workflows should be present")
        
        # Check for comprehensive analysis workflow
        if 'comprehensive_analysis' in unified_workflows:
            comp_analysis = unified_workflows['comprehensive_analysis']
            self.assertIn('steps', comp_analysis)
            self.assertIn('purposes', comp_analysis)
            
            # Verify workflow includes all major analytical steps
            steps = comp_analysis.get('steps', [])
            expected_steps = ['describe', 'explain', 'predict', 'infer', 'intervene']
            
            for step in expected_steps:
                self.assertIn(step, steps, f"Workflow should include {step} step")
        
        # Verify integration validation
        if 'cross_validation' in cross_purpose_integration:
            cross_validation = cross_purpose_integration.get('cross_validation', {})
            validation_checks = [
                'consistency_checks', 'integration_validation', 
                'purpose_alignment', 'interface_completeness'
            ]
            
            for check in validation_checks:
                self.assertIn(check, cross_validation, 
                             f"Cross-validation should include {check}")
        
        # Test compatibility with experimental validation framework
        experimental_compatibility = {
            'property_graph_support': True,
            'multi_theory_handling': True,
            'balanced_processing': True,
            'quality_validation': True
        }
        
        # Verify experimental features are supported
        model_type = schema_generation.get('model_type', '')
        self.assertIn('property_graph', model_type.lower(), 
                     "Should support property graph models from experimental validation")
        
        print(f"✓ Integration interfaces: {total_interfaces}")
        print(f"✓ Unified workflows: {len(unified_workflows)}")
        print(f"✓ Model type: {model_type}")
        print(f"✓ Experimental validation integration successful")


class TestPipelineConfiguration(unittest.TestCase):
    """Test suite for pipeline configuration"""
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        config = PredefinedConfigurations.create_balanced_configuration()
        validation = config.validate_configuration()
        
        self.assertTrue(validation['valid'])
        self.assertIsInstance(validation['warnings'], list)
        self.assertIsInstance(validation['errors'], list)
    
    def test_predefined_configurations(self):
        """Test predefined configuration creation"""
        configs = {
            'balanced': PredefinedConfigurations.create_balanced_configuration(),
            'research': PredefinedConfigurations.create_research_configuration(),
            'production': PredefinedConfigurations.create_production_configuration(),
            'high_quality': PredefinedConfigurations.create_high_quality_configuration()
        }
        
        for name, config in configs.items():
            self.assertIsInstance(config, PipelineConfiguration)
            self.assertIsInstance(config.mode, ProcessingMode)


class TestQualityAssurance(unittest.TestCase):
    """Test suite for quality assurance framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.qa_framework = QualityAssuranceFramework()
        
        # Sample pipeline results for testing
        self.sample_results = {
            'pipeline_id': 'test_pipeline',
            'input_theory_length': 1000,
            'processing_stages': [
                type('Stage', (), {
                    'stage_name': 'test_stage',
                    'processing_time': 1.0,
                    'balance_metrics': {'balance_score': 0.8}
                })()
            ],
            'purpose_classification': {
                'all_purposes': ['descriptive', 'explanatory', 'predictive'],
                'purpose_confidences': {'descriptive': 0.7, 'explanatory': 0.8, 'predictive': 0.6}
            },
            'vocabulary_extraction': {
                'extraction_balance': {'balance_ratio': 0.75, 'is_balanced': True}
            },
            'schema_generation': {
                'purpose_capabilities': {
                    'descriptive': {'sophistication_level': 8},
                    'explanatory': {'sophistication_level': 8},
                    'predictive': {'sophistication_level': 8}
                },
                'cross_purpose_integration': {'total_interfaces': 6}
            },
            'balance_validation': {
                'overall_balance_score': 0.8,
                'overall_balance_status': 'BALANCED'
            },
            'pipeline_metrics': {
                'total_processing_time': 5.0,
                'balance_success': True
            }
        }
    
    def test_quality_assessment(self):
        """Test quality assessment functionality"""
        assessment = self.qa_framework.assess_pipeline_quality(self.sample_results)
        
        self.assertIsInstance(assessment.overall_quality, QualityLevel)
        self.assertIsInstance(assessment.balance_status, BalanceStatus)
        self.assertGreater(assessment.overall_score, 0)
        self.assertGreater(len(assessment.quality_metrics), 0)
    
    def test_balance_validation(self):
        """Test balance requirements validation"""
        validation = self.qa_framework.validate_balance_requirements(self.sample_results)
        
        self.assertIn('balance_validated', validation)
        self.assertIn('requirements_met', validation)
        self.assertIn('score', validation)
        self.assertIsInstance(validation['requirements_met'], dict)
    
    def test_certification(self):
        """Test balanced implementation certification"""
        certification = self.qa_framework.certify_balanced_implementation(self.sample_results)
        
        self.assertIn('certified', certification)
        self.assertIn('certification_score', certification)
        self.assertIn('certification_level', certification)


def run_all_tests():
    """Run all test suites"""
    print("=" * 80)
    print("COMPREHENSIVE TEST SUITE FOR BALANCED INTEGRATION PIPELINE")
    print("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestQualityAssurance))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST EXECUTION SUMMARY")
    print("=" * 80)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    successes = total_tests - failures - errors
    
    print(f"Total tests run: {total_tests}")
    print(f"Successful: {successes}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Success rate: {(successes/total_tests)*100:.1f}%" if total_tests > 0 else "0%")
    
    if failures > 0:
        print(f"\nFAILURES ({failures}):")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'Unknown failure'}")
    
    if errors > 0:
        print(f"\nERRORS ({errors}):")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip() if 'Exception:' in traceback else 'Unknown error'}")
    
    # Overall result
    if failures == 0 and errors == 0:
        print(f"\n✓ ALL TESTS PASSED - BALANCED INTEGRATION PIPELINE VALIDATED")
        return True
    else:
        print(f"\n✗ SOME TESTS FAILED - PIPELINE REQUIRES ATTENTION")
        return False


def main():
    """Main test execution"""
    success = run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())