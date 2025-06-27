#!/usr/bin/env python3
"""
Comprehensive Test Suite for Multi-Purpose Vocabulary Extraction

Tests all aspects of balanced vocabulary extraction across five theoretical purposes:
descriptive, explanatory, predictive, causal, and intervention analysis.
"""

import unittest
import json
import sys
import os
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vocabulary_extractor import MultiPurposeVocabularyExtractor
from extraction_prompts import BalancedExtractionPrompts
from cross_purpose_integration import CrossPurposeIntegrator


class TestMultiPurposeVocabularyExtraction(unittest.TestCase):
    """Comprehensive test suite for multi-purpose vocabulary extraction"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.extractor = MultiPurposeVocabularyExtractor()
        cls.prompt_generator = BalancedExtractionPrompts()
        cls.integrator = CrossPurposeIntegrator()
        
        # Sample theory texts for testing
        cls.sample_texts = {
            'social_cognitive_theory': """
            Social cognitive theory explains behavior through the dynamic interaction of personal, 
            behavioral, and environmental factors. The theory categorizes learning mechanisms into 
            observational learning, direct experience, and symbolic modeling. Key variables include 
            self-efficacy, outcome expectations, and behavioral capability. The framework predicts 
            that individuals with higher self-efficacy are more likely to engage in target behaviors.
            
            Causal pathways demonstrate how environmental factors influence personal cognitions, 
            which in turn affect behavioral outcomes. Interventions based on this theory typically 
            focus on enhancing self-efficacy through mastery experiences, vicarious learning, 
            verbal persuasion, and emotional arousal management.
            """,
            
            'systems_theory': """
            Systems theory provides a comprehensive framework for understanding complex organizations 
            as interconnected networks of components. The theory classifies system types into open, 
            closed, and semi-permeable systems based on their boundary characteristics. Key indicators 
            of system health include feedback loops, homeostatic mechanisms, and adaptive capacity.
            
            Predictive models derived from systems theory forecast organizational performance based 
            on input-throughput-output relationships. Causal analysis reveals how system perturbations 
            propagate through interconnected subsystems. Intervention strategies focus on leverage 
            points where small changes can produce significant system-wide transformations.
            """,
            
            'complexity_theory': """
            Complexity theory analyzes emergent properties in nonlinear dynamic systems. The framework 
            distinguishes between complicated systems (many parts but predictable) and complex systems 
            (nonlinear interactions with emergent properties). Critical variables include connectivity, 
            diversity, and adaptive capacity of system agents.
            
            Predictive capabilities are limited due to sensitive dependence on initial conditions, 
            but pattern recognition enables identification of attractor states and phase transitions. 
            Causal relationships are often circular and multi-directional rather than linear. 
            Intervention approaches emphasize creating conditions for positive emergence rather than 
            direct control mechanisms.
            """
        }
    
    def test_01_descriptive_vocabulary_extraction(self):
        """Test 1: Descriptive vocabulary extraction (categories, classifications)"""
        print("\n=== TEST 1: DESCRIPTIVE VOCABULARY EXTRACTION ===")
        
        for theory_name, text in self.sample_texts.items():
            with self.subTest(theory=theory_name):
                result = self.extractor.extract_descriptive_vocabulary(text)
                
                # Verify structure
                self.assertIsInstance(result, dict)
                expected_categories = ['taxonomies', 'classifications', 'categories', 
                                     'typologies', 'attributes', 'dimensions', 'patterns']
                for category in expected_categories:
                    self.assertIn(category, result)
                    self.assertIsInstance(result[category], list)
                
                # Verify content extraction
                total_terms = sum(len(terms) for terms in result.values())
                self.assertGreater(total_terms, 0, f"No descriptive terms extracted for {theory_name}")
                
                print(f"  {theory_name}: {total_terms} descriptive terms extracted")
                
                # Verify theory-appropriate content
                if theory_name == 'social_cognitive_theory':
                    descriptive_content = ' '.join([' '.join(terms) for terms in result.values()])
                    self.assertTrue(any(term in descriptive_content.lower() for term in 
                                      ['theory', 'framework', 'learning', 'behavior']))
    
    def test_02_explanatory_vocabulary_extraction(self):
        """Test 2: Explanatory vocabulary extraction (mechanisms, processes)"""
        print("\n=== TEST 2: EXPLANATORY VOCABULARY EXTRACTION ===")
        
        for theory_name, text in self.sample_texts.items():
            with self.subTest(theory=theory_name):
                result = self.extractor.extract_explanatory_vocabulary(text)
                
                # Verify structure
                self.assertIsInstance(result, dict)
                expected_categories = ['mechanisms', 'processes', 'systems', 'frameworks', 
                                     'structures', 'components', 'interactions', 'principles']
                for category in expected_categories:
                    self.assertIn(category, result)
                    self.assertIsInstance(result[category], list)
                
                # Verify content extraction
                total_terms = sum(len(terms) for terms in result.values())
                self.assertGreater(total_terms, 0, f"No explanatory terms extracted for {theory_name}")
                
                print(f"  {theory_name}: {total_terms} explanatory terms extracted")
                
                # Verify theory-appropriate content
                if theory_name == 'systems_theory':
                    explanatory_content = ' '.join([' '.join(terms) for terms in result.values()])
                    self.assertTrue(any(term in explanatory_content.lower() for term in 
                                      ['system', 'mechanism', 'process', 'interaction']))
    
    def test_03_predictive_vocabulary_extraction(self):
        """Test 3: Predictive vocabulary extraction (variables, models)"""
        print("\n=== TEST 3: PREDICTIVE VOCABULARY EXTRACTION ===")
        
        for theory_name, text in self.sample_texts.items():
            with self.subTest(theory=theory_name):
                result = self.extractor.extract_predictive_vocabulary(text)
                
                # Verify structure
                self.assertIsInstance(result, dict)
                expected_categories = ['variables', 'models', 'indicators', 'measures', 
                                     'forecasting_terms', 'statistical_terms', 'correlations', 'parameters']
                for category in expected_categories:
                    self.assertIn(category, result)
                    self.assertIsInstance(result[category], list)
                
                # Verify content extraction
                total_terms = sum(len(terms) for terms in result.values())
                self.assertGreater(total_terms, 0, f"No predictive terms extracted for {theory_name}")
                
                print(f"  {theory_name}: {total_terms} predictive terms extracted")
                
                # Verify theory-appropriate content
                if theory_name == 'complexity_theory':
                    predictive_content = ' '.join([' '.join(terms) for terms in result.values()])
                    self.assertTrue(any(term in predictive_content.lower() for term in 
                                      ['model', 'predict', 'variable', 'pattern']))
    
    def test_04_causal_vocabulary_extraction(self):
        """Test 4: Causal vocabulary extraction (relationships, pathways)"""
        print("\n=== TEST 4: CAUSAL VOCABULARY EXTRACTION ===")
        
        for theory_name, text in self.sample_texts.items():
            with self.subTest(theory=theory_name):
                result = self.extractor.extract_causal_vocabulary(text)
                
                # Verify structure
                self.assertIsInstance(result, dict)
                expected_categories = ['causes', 'effects', 'relationships', 'pathways', 
                                     'mediators', 'moderators', 'determinants', 'consequences']
                for category in expected_categories:
                    self.assertIn(category, result)
                    self.assertIsInstance(result[category], list)
                
                # Verify content extraction
                total_terms = sum(len(terms) for terms in result.values())
                self.assertGreater(total_terms, 0, f"No causal terms extracted for {theory_name}")
                
                print(f"  {theory_name}: {total_terms} causal terms extracted")
                
                # Verify theory-appropriate content
                causal_content = ' '.join([' '.join(terms) for terms in result.values()])
                self.assertTrue(any(term in causal_content.lower() for term in 
                                  ['cause', 'effect', 'influence', 'relationship', 'pathway']))
    
    def test_05_intervention_vocabulary_extraction(self):
        """Test 5: Intervention vocabulary extraction (actions, strategies)"""
        print("\n=== TEST 5: INTERVENTION VOCABULARY EXTRACTION ===")
        
        for theory_name, text in self.sample_texts.items():
            with self.subTest(theory=theory_name):
                result = self.extractor.extract_intervention_vocabulary(text)
                
                # Verify structure
                self.assertIsInstance(result, dict)
                expected_categories = ['interventions', 'strategies', 'methods', 'implementations', 
                                     'policies', 'practices', 'tools', 'solutions']
                for category in expected_categories:
                    self.assertIn(category, result)
                    self.assertIsInstance(result[category], list)
                
                # Verify content extraction
                total_terms = sum(len(terms) for terms in result.values())
                self.assertGreater(total_terms, 0, f"No intervention terms extracted for {theory_name}")
                
                print(f"  {theory_name}: {total_terms} intervention terms extracted")
                
                # Verify theory-appropriate content
                intervention_content = ' '.join([' '.join(terms) for terms in result.values()])
                self.assertTrue(any(term in intervention_content.lower() for term in 
                                  ['intervention', 'strategy', 'approach', 'method']))
    
    def test_06_cross_purpose_term_identification(self):
        """Test 6: Cross-purpose term identification"""
        print("\n=== TEST 6: CROSS-PURPOSE TERM IDENTIFICATION ===")
        
        # Extract vocabulary for all purposes
        text = self.sample_texts['social_cognitive_theory']
        comprehensive_result = self.extractor.extract_comprehensive_vocabulary(text)
        
        # Verify cross-purpose terms are identified
        self.assertIn('cross_purpose_terms', comprehensive_result)
        cross_purpose = comprehensive_result['cross_purpose_terms']
        
        # Verify structure
        expected_keys = ['multi_purpose_terms', 'purpose_overlap_matrix', 'shared_concepts']
        for key in expected_keys:
            self.assertIn(key, cross_purpose)
        
        # Verify multi-purpose terms exist
        multi_purpose_terms = cross_purpose['multi_purpose_terms']
        self.assertIsInstance(multi_purpose_terms, dict)
        
        if multi_purpose_terms:
            print(f"  Found {len(multi_purpose_terms)} multi-purpose terms")
            # Show examples
            examples = list(multi_purpose_terms.items())[:3]
            for term, purposes in examples:
                print(f"    '{term}' appears in: {purposes}")
        
        # Test with integration module
        purpose_extractions = {k: v for k, v in comprehensive_result.items() if k.endswith('_terms')}
        integration_result = self.integrator.integrate_cross_purpose_terms(purpose_extractions)
        
        self.assertIn('multi_purpose_terms', integration_result)
        self.assertIn('semantic_bridges', integration_result)
    
    def test_07_extraction_balance_validation(self):
        """Test 7: Extraction balance validation (equal comprehensiveness)"""
        print("\n=== TEST 7: EXTRACTION BALANCE VALIDATION ===")
        
        for theory_name, text in self.sample_texts.items():
            with self.subTest(theory=theory_name):
                result = self.extractor.extract_comprehensive_vocabulary(text)
                
                # Verify balance report exists
                self.assertIn('extraction_balance', result)
                balance = result['extraction_balance']
                
                # Verify balance structure
                expected_keys = ['purpose_counts', 'balance_scores', 'balance_ratio', 
                               'is_balanced', 'recommendations']
                for key in expected_keys:
                    self.assertIn(key, balance)
                
                # Verify balance metrics
                self.assertIsInstance(balance['balance_ratio'], (int, float))
                self.assertIsInstance(balance['is_balanced'], bool)
                self.assertGreaterEqual(balance['balance_ratio'], 0.0)
                self.assertLessEqual(balance['balance_ratio'], 1.0)
                
                print(f"  {theory_name}:")
                print(f"    Balance ratio: {balance['balance_ratio']:.3f}")
                print(f"    Is balanced: {balance['is_balanced']}")
                
                if balance['purpose_counts']:
                    print(f"    Purpose counts: {balance['purpose_counts']}")
                
                # Test balance threshold
                if balance['balance_ratio'] < 0.5:
                    print(f"    WARNING: Low balance ratio for {theory_name}")
                    if balance['recommendations']:
                        print(f"    Recommendations: {balance['recommendations']}")
    
    def test_08_multi_purpose_theory_vocabulary_handling(self):
        """Test 8: Multi-purpose theory vocabulary handling"""
        print("\n=== TEST 8: MULTI-PURPOSE THEORY VOCABULARY HANDLING ===")
        
        # Test with complexity theory (inherently multi-purpose)
        text = self.sample_texts['complexity_theory']
        result = self.extractor.extract_comprehensive_vocabulary(text)
        
        # Verify all purposes are extracted
        purpose_keys = ['descriptive_terms', 'explanatory_terms', 'predictive_terms', 
                       'causal_terms', 'intervention_terms']
        
        for purpose_key in purpose_keys:
            self.assertIn(purpose_key, result)
            purpose_data = result[purpose_key]
            total_terms = sum(len(terms) if isinstance(terms, list) else 0 
                            for terms in purpose_data.values())
            self.assertGreater(total_terms, 0, f"No terms extracted for {purpose_key}")
        
        # Verify cross-purpose integration
        cross_purpose = result['cross_purpose_terms']
        self.assertGreater(len(cross_purpose['multi_purpose_terms']), 0, 
                          "No multi-purpose terms identified in complex theory")
        
        # Test integration quality
        purpose_extractions = {k: v for k, v in result.items() if k.endswith('_terms')}
        integration_result = self.integrator.integrate_cross_purpose_terms(purpose_extractions)
        
        quality = integration_result['integration_quality']
        print(f"  Integration quality: {quality['overall_quality']:.3f}")
        print(f"  High integration terms: {len(integration_result['multi_purpose_terms']['high_integration_terms'])}")
        
        # Verify reasonable quality threshold
        self.assertGreater(quality['overall_quality'], 0.3, 
                          "Integration quality too low for multi-purpose theory")
    
    def test_09_balanced_extraction_prompts(self):
        """Test 9: Balanced extraction prompts functionality"""
        print("\n=== TEST 9: BALANCED EXTRACTION PROMPTS ===")
        
        text = self.sample_texts['social_cognitive_theory']
        
        # Test comprehensive prompt generation
        comprehensive_prompt = self.prompt_generator.get_comprehensive_extraction_prompt(text)
        self.assertIsInstance(comprehensive_prompt, str)
        self.assertGreater(len(comprehensive_prompt), 1000)  # Should be substantial
        
        # Verify all purposes mentioned in prompt
        purposes = ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']
        for purpose in purposes:
            self.assertIn(purpose.upper(), comprehensive_prompt.upper())
        
        # Test purpose-specific prompts
        for purpose in purposes:
            purpose_prompt = self.prompt_generator.get_purpose_specific_prompt(purpose, text)
            self.assertIsInstance(purpose_prompt, str)
            self.assertIn(purpose.upper(), purpose_prompt.upper())
            self.assertIn('BALANCE', purpose_prompt.upper())
        
        print(f"  Generated comprehensive prompt: {len(comprehensive_prompt)} characters")
        print(f"  Generated {len(purposes)} purpose-specific prompts")
        
        # Test balance validation prompt
        sample_results = {
            'descriptive_terms': {'categories': ['theory', 'framework']},
            'explanatory_terms': {'mechanisms': ['process', 'system']},
            'predictive_terms': {'variables': ['factor', 'variable']},
            'causal_terms': {'relationships': ['cause', 'effect']},
            'intervention_terms': {'strategies': ['intervention', 'approach']}
        }
        
        balance_prompt = self.prompt_generator.get_balance_validation_prompt(sample_results)
        self.assertIsInstance(balance_prompt, str)
        self.assertIn('BALANCE', balance_prompt.upper())
    
    def test_10_integration_quality_assessment(self):
        """Test 10: Integration quality assessment"""
        print("\n=== TEST 10: INTEGRATION QUALITY ASSESSMENT ===")
        
        # Test with all sample theories
        for theory_name, text in self.sample_texts.items():
            with self.subTest(theory=theory_name):
                result = self.extractor.extract_comprehensive_vocabulary(text)
                purpose_extractions = {k: v for k, v in result.items() if k.endswith('_terms')}
                integration_result = self.integrator.integrate_cross_purpose_terms(purpose_extractions)
                
                quality = integration_result['integration_quality']
                
                # Verify quality structure
                expected_metrics = ['integration_completeness', 'balance_across_purposes', 
                                  'cross_purpose_coverage', 'semantic_coherence', 'overall_quality']
                for metric in expected_metrics:
                    self.assertIn(metric, quality)
                    self.assertIsInstance(quality[metric], (int, float))
                    self.assertGreaterEqual(quality[metric], 0.0)
                    self.assertLessEqual(quality[metric], 1.0)
                
                print(f"  {theory_name} integration quality:")
                print(f"    Overall: {quality['overall_quality']:.3f}")
                print(f"    Completeness: {quality['integration_completeness']:.3f}")
                print(f"    Balance: {quality['balance_across_purposes']:.3f}")
                print(f"    Coverage: {quality['cross_purpose_coverage']:.3f}")
                print(f"    Coherence: {quality['semantic_coherence']:.3f}")
                
                if quality['quality_issues']:
                    print(f"    Issues: {len(quality['quality_issues'])}")
                if quality['recommendations']:
                    print(f"    Recommendations: {len(quality['recommendations'])}")
    
    def test_11_purpose_balance_requirements(self):
        """Test 11: Verify no single-purpose bias exists"""
        print("\n=== TEST 11: PURPOSE BALANCE REQUIREMENTS ===")
        
        # Test across all theories to check for systematic bias
        purpose_totals = {purpose: 0 for purpose in ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']}
        
        for theory_name, text in self.sample_texts.items():
            result = self.extractor.extract_comprehensive_vocabulary(text)
            balance = result['extraction_balance']
            
            if 'purpose_counts' in balance:
                for purpose, count in balance['purpose_counts'].items():
                    if purpose in purpose_totals:
                        purpose_totals[purpose] += count
        
        # Calculate overall balance across all theories
        if any(count > 0 for count in purpose_totals.values()):
            max_total = max(purpose_totals.values())
            min_total = min(count for count in purpose_totals.values() if count > 0)
            overall_balance_ratio = min_total / max_total if max_total > 0 else 0.0
            
            print(f"  Overall purpose totals: {purpose_totals}")
            print(f"  Overall balance ratio: {overall_balance_ratio:.3f}")
            
            # Check for systematic bias (no purpose should dominate)
            avg_total = sum(purpose_totals.values()) / len(purpose_totals)
            bias_threshold = 1.5  # No purpose should be 1.5x the average
            
            biased_purposes = []
            for purpose, total in purpose_totals.items():
                if total > avg_total * bias_threshold:
                    biased_purposes.append(purpose)
            
            if biased_purposes:
                print(f"  WARNING: Potential bias toward: {biased_purposes}")
            else:
                print(f"  No systematic single-purpose bias detected")
            
            # Ensure reasonable balance (ratio > 0.4 across all theories)
            self.assertGreater(overall_balance_ratio, 0.4, 
                             f"Overall balance ratio too low: {overall_balance_ratio}")
    
    def test_12_comprehensive_coverage_validation(self):
        """Test 12: Validate comprehensive coverage of theoretical vocabulary"""
        print("\n=== TEST 12: COMPREHENSIVE COVERAGE VALIDATION ===")
        
        # Test that each theory gets comprehensive vocabulary extraction
        for theory_name, text in self.sample_texts.items():
            with self.subTest(theory=theory_name):
                result = self.extractor.extract_comprehensive_vocabulary(text)
                
                # Count total unique terms extracted
                all_terms = set()
                for purpose_key, purpose_data in result.items():
                    if purpose_key.endswith('_terms') and isinstance(purpose_data, dict):
                        for category_terms in purpose_data.values():
                            if isinstance(category_terms, list):
                                all_terms.update(term.lower().strip() for term in category_terms)
                
                total_unique_terms = len(all_terms)
                
                # Verify minimum coverage (should extract meaningful vocabulary)
                self.assertGreater(total_unique_terms, 10, 
                                 f"Insufficient vocabulary coverage for {theory_name}: {total_unique_terms} terms")
                
                # Verify each purpose contributes (excluding cross_purpose)
                purpose_contributions = {}
                main_purposes = ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']
                for purpose_key, purpose_data in result.items():
                    if purpose_key.endswith('_terms'):
                        purpose = purpose_key.replace('_terms', '')
                        if purpose in main_purposes:  # Only check main purposes
                            count = sum(len(terms) if isinstance(terms, list) else 0 
                                      for terms in purpose_data.values())
                            purpose_contributions[purpose] = count
                
                # Each main purpose should contribute at least some terms
                zero_contribution_purposes = [p for p, c in purpose_contributions.items() if c == 0]
                self.assertEqual(len(zero_contribution_purposes), 0, 
                               f"Purposes with zero contribution in {theory_name}: {zero_contribution_purposes}")
                
                print(f"  {theory_name}: {total_unique_terms} unique terms, all purposes contributing")


class TestResultCollector:
    """Collects and formats test results"""
    
    def __init__(self):
        self.results = {}
    
    def collect_results(self, test_result):
        """Collect test results for reporting"""
        self.results = {
            'tests_run': test_result.testsRun,
            'failures': len(test_result.failures),
            'errors': len(test_result.errors),
            'success_rate': (test_result.testsRun - len(test_result.failures) - len(test_result.errors)) / test_result.testsRun if test_result.testsRun > 0 else 0.0,
            'detailed_results': []
        }
        
        # Collect failure details
        for test, traceback in test_result.failures:
            self.results['detailed_results'].append({
                'test': str(test),
                'status': 'FAILURE',
                'details': traceback
            })
        
        # Collect error details
        for test, traceback in test_result.errors:
            self.results['detailed_results'].append({
                'test': str(test),
                'status': 'ERROR',
                'details': traceback
            })
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        report = "=== MULTI-PURPOSE VOCABULARY EXTRACTION TEST RESULTS ===\n\n"
        
        report += f"Tests Run: {self.results['tests_run']}\n"
        report += f"Failures: {self.results['failures']}\n"
        report += f"Errors: {self.results['errors']}\n"
        report += f"Success Rate: {self.results['success_rate']:.1%}\n\n"
        
        if self.results['detailed_results']:
            report += "DETAILED RESULTS:\n"
            for result in self.results['detailed_results']:
                report += f"\n{result['status']}: {result['test']}\n"
                report += f"Details: {result['details'][:200]}...\n"
        
        report += "\n=== TESTING COMPLETE ===\n"
        
        return report


def run_all_tests():
    """Run all tests and generate report"""
    print("Starting comprehensive multi-purpose vocabulary extraction tests...")
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMultiPurposeVocabularyExtraction)
    
    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    test_result = test_runner.run(test_suite)
    
    # Collect and report results
    collector = TestResultCollector()
    collector.collect_results(test_result)
    
    final_report = collector.generate_report()
    print(final_report)
    
    return test_result.wasSuccessful(), collector.results


if __name__ == "__main__":
    success, results = run_all_tests()
    
    # Save results to file
    results_file = os.path.join(os.path.dirname(__file__), 'test_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Test results saved to: {results_file}")
    
    # Exit with appropriate code
    exit(0 if success else 1)