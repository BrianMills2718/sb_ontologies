"""
Comprehensive Test Framework for Balanced Purpose Classification

Tests all five theoretical purposes with equal sophistication to ensure
no causal over-emphasis and balanced analytical treatment.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from purpose_classifier import PurposeClassifier
from balanced_prompts import BalancedPrompts, BalancedPromptTester
import json


class PurposeClassificationTester:
    """Comprehensive testing framework for balanced purpose classification"""
    
    def __init__(self):
        self.classifier = PurposeClassifier()
        self.prompts = BalancedPrompts()
        self.prompt_tester = BalancedPromptTester()
        self.test_results = {}
    
    def run_all_tests(self) -> dict:
        """Run all tests and return comprehensive results"""
        print("Running Balanced Purpose Classification Tests...")
        print("=" * 60)
        
        # Test 1: Descriptive theory identification
        print("\n1. Testing Descriptive Theory Identification...")
        self.test_results['descriptive'] = self.test_descriptive_identification()
        
        # Test 2: Explanatory theory identification  
        print("\n2. Testing Explanatory Theory Identification...")
        self.test_results['explanatory'] = self.test_explanatory_identification()
        
        # Test 3: Predictive theory identification
        print("\n3. Testing Predictive Theory Identification...")
        self.test_results['predictive'] = self.test_predictive_identification()
        
        # Test 4: Causal theory identification
        print("\n4. Testing Causal Theory Identification...")
        self.test_results['causal'] = self.test_causal_identification()
        
        # Test 5: Intervention theory identification
        print("\n5. Testing Intervention Theory Identification...")
        self.test_results['intervention'] = self.test_intervention_identification()
        
        # Test 6: Multi-purpose theory handling
        print("\n6. Testing Multi-Purpose Theory Handling...")
        self.test_results['multi_purpose'] = self.test_multi_purpose_handling()
        
        # Test 7: Balance validation (CRITICAL)
        print("\n7. Testing Balance Validation (CRITICAL)...")
        self.test_results['balance_validation'] = self.test_balance_validation()
        
        # Overall assessment
        print("\n8. Overall Assessment...")
        self.test_results['overall_assessment'] = self.assess_overall_performance()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        
        return self.test_results
    
    def test_descriptive_identification(self) -> dict:
        """Test 1: Descriptive theory identification (taxonomies, typologies)"""
        descriptive_theory = """
        This theory establishes a comprehensive taxonomy of organizational structures in modern societies.
        The classification system distinguishes between hierarchical, network, and hybrid organizational types.
        Each organizational type is characterized by specific structural dimensions including centralization,
        formalization, and complexity. The typological framework provides systematic categorization of
        organizational forms based on their structural attributes. The dimensional analysis reveals
        that organizations can be classified along multiple systematic dimensions that capture
        their essential characteristics and variations.
        """
        
        result = self.classifier.classify_theory_purposes(descriptive_theory)
        
        # Validate descriptive detection
        validation = {
            'theory_text': descriptive_theory,
            'classification_result': result,
            'primary_purpose_correct': result['primary_purpose'] == 'descriptive',
            'descriptive_confidence': result['purpose_confidence']['descriptive'],
            'descriptive_elements_detected': result['detailed_analyses']['descriptive'],
            'equal_sophistication_applied': result['detailed_analyses']['descriptive']['sophistication_level'] == 'high',
            'test_passed': result['primary_purpose'] == 'descriptive' and result['purpose_confidence']['descriptive'] > 0.3
        }
        
        print(f"   Primary Purpose: {result['primary_purpose']}")
        print(f"   Descriptive Confidence: {result['purpose_confidence']['descriptive']:.3f}")
        print(f"   Test Passed: {validation['test_passed']}")
        
        return validation
    
    def test_explanatory_identification(self) -> dict:
        """Test 2: Explanatory theory identification (mechanisms, processes)"""
        explanatory_theory = """
        This theory explains how social capital emerges through systematic interaction mechanisms
        within community networks. The underlying mechanism involves repeated social exchanges
        that generate trust and reciprocity norms. The process operates through structural
        relationships between individuals, groups, and institutions. The systematic process
        of social capital formation involves multiple stages of interaction, norm development,
        and relationship consolidation. The functional explanation shows how these mechanisms
        serve to reduce transaction costs and enable collective action in communities.
        """
        
        result = self.classifier.classify_theory_purposes(explanatory_theory)
        
        # Validate explanatory detection
        validation = {
            'theory_text': explanatory_theory,
            'classification_result': result,
            'primary_purpose_correct': result['primary_purpose'] == 'explanatory',
            'explanatory_confidence': result['purpose_confidence']['explanatory'],
            'explanatory_elements_detected': result['detailed_analyses']['explanatory'],
            'equal_sophistication_applied': result['detailed_analyses']['explanatory']['sophistication_level'] == 'high',
            'test_passed': result['primary_purpose'] == 'explanatory' and result['purpose_confidence']['explanatory'] > 0.3
        }
        
        print(f"   Primary Purpose: {result['primary_purpose']}")
        print(f"   Explanatory Confidence: {result['purpose_confidence']['explanatory']:.3f}")
        print(f"   Test Passed: {validation['test_passed']}")
        
        return validation
    
    def test_predictive_identification(self) -> dict:
        """Test 3: Predictive theory identification (forecasting, variables)"""
        predictive_theory = """
        This theory predicts voter turnout based on systematic analysis of demographic and
        political variables. The forecasting framework incorporates predictor variables
        including age, education, income, and political efficacy. The statistical model
        estimates the probability of voting participation using regression analysis.
        The predictive model projects future voting patterns based on demographic trends
        and political engagement indicators. The probabilistic framework forecasts
        election outcomes with specified confidence intervals and predictive validity measures.
        """
        
        result = self.classifier.classify_theory_purposes(predictive_theory)
        
        # Validate predictive detection
        validation = {
            'theory_text': predictive_theory,
            'classification_result': result,
            'primary_purpose_correct': result['primary_purpose'] == 'predictive',
            'predictive_confidence': result['purpose_confidence']['predictive'],
            'predictive_elements_detected': result['detailed_analyses']['predictive'],
            'equal_sophistication_applied': result['detailed_analyses']['predictive']['sophistication_level'] == 'high',
            'test_passed': result['primary_purpose'] == 'predictive' and result['purpose_confidence']['predictive'] > 0.3
        }
        
        print(f"   Primary Purpose: {result['primary_purpose']}")
        print(f"   Predictive Confidence: {result['purpose_confidence']['predictive']:.3f}")
        print(f"   Test Passed: {validation['test_passed']}")
        
        return validation
    
    def test_causal_identification(self) -> dict:
        """Test 4: Causal theory identification (relationships, interventions) - EQUAL TREATMENT"""
        causal_theory = """
        This theory establishes causal relationships between educational investment and economic
        development outcomes through systematic analysis. The framework classifies educational
        interventions into distinct types and their causal mechanisms. Educational programs
        cause measurable improvements in economic indicators through systematic processes.
        The causal analysis explains how education leads to productivity gains and demonstrates
        that investment results in higher income levels. The framework predicts future
        outcomes using forecasting models and provides actionable implementation strategies
        for policy interventions with detailed practical applications.
        """
        
        result = self.classifier.classify_theory_purposes(causal_theory)
        
        # Validate causal detection WITH EQUAL TREATMENT
        validation = {
            'theory_text': causal_theory,
            'classification_result': result,
            'primary_purpose_correct': result['primary_purpose'] == 'causal',
            'causal_confidence': result['purpose_confidence']['causal'],
            'causal_elements_detected': result['detailed_analyses']['causal'],
            'equal_sophistication_applied': result['detailed_analyses']['causal']['sophistication_level'] == 'high',
            'no_overemphasis_confirmed': result['balanced_analysis']['causal_overemphasis_detected'] == False,
            'test_passed': result['primary_purpose'] == 'causal' and result['purpose_confidence']['causal'] > 0.3
        }
        
        print(f"   Primary Purpose: {result['primary_purpose']}")
        print(f"   Causal Confidence: {result['purpose_confidence']['causal']:.3f}")
        print(f"   No Over-emphasis: {not result['balanced_analysis']['causal_overemphasis_detected']}")
        print(f"   Test Passed: {validation['test_passed']}")
        
        return validation
    
    def test_intervention_identification(self) -> dict:
        """Test 5: Intervention theory identification (actions, implementation)"""
        intervention_theory = """
        This theory provides actionable framework for implementing community development
        programs in urban areas. The implementation strategy specifies systematic approaches
        to program design and delivery. Policy recommendations include specific action plans
        for addressing housing, education, and employment challenges. The practical application
        framework guides implementation of evidence-based interventions with detailed
        implementation strategies. The intervention design incorporates systematic approaches
        to community engagement and program evaluation for real-world application.
        """
        
        result = self.classifier.classify_theory_purposes(intervention_theory)
        
        # Validate intervention detection
        validation = {
            'theory_text': intervention_theory,
            'classification_result': result,
            'primary_purpose_correct': result['primary_purpose'] == 'intervention',
            'intervention_confidence': result['purpose_confidence']['intervention'],
            'intervention_elements_detected': result['detailed_analyses']['intervention'],
            'equal_sophistication_applied': result['detailed_analyses']['intervention']['sophistication_level'] == 'high',
            'test_passed': result['primary_purpose'] == 'intervention' and result['purpose_confidence']['intervention'] > 0.3
        }
        
        print(f"   Primary Purpose: {result['primary_purpose']}")
        print(f"   Intervention Confidence: {result['purpose_confidence']['intervention']:.3f}")
        print(f"   Test Passed: {validation['test_passed']}")
        
        return validation
    
    def test_multi_purpose_handling(self) -> dict:
        """Test 6: Multi-purpose theory handling"""
        multi_purpose_theory = """
        This comprehensive theory explains the mechanisms of social inequality through
        systematic classification of inequality types and their causal relationships.
        The theory predicts future inequality trends based on economic and social variables
        while providing actionable policy recommendations for reducing disparities.
        The explanatory framework identifies processes that generate inequality, while
        the predictive model forecasts inequality outcomes. The intervention component
        specifies implementation strategies for inequality reduction programs.
        """
        
        result = self.classifier.classify_theory_purposes(multi_purpose_theory)
        
        # Validate multi-purpose handling
        validation = {
            'theory_text': multi_purpose_theory,
            'classification_result': result,
            'primary_purpose_identified': result['primary_purpose'] in ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention'],
            'secondary_purposes_found': len(result['secondary_purposes']) > 0,
            'multi_purpose_detected': len(result['secondary_purposes']) >= 1,
            'balanced_analysis_maintained': result['balanced_analysis']['balance_check'] == 'passed',
            'test_passed': len(result['secondary_purposes']) >= 1 and result['balanced_analysis']['balance_check'] == 'passed'
        }
        
        print(f"   Primary Purpose: {result['primary_purpose']}")
        print(f"   Secondary Purposes: {result['secondary_purposes']}")
        print(f"   Multi-purpose Detected: {validation['multi_purpose_detected']}")
        print(f"   Balance Maintained: {validation['balanced_analysis_maintained']}")
        print(f"   Test Passed: {validation['test_passed']}")
        
        return validation
    
    def test_balance_validation(self) -> dict:
        """Test 7: Balance validation (CRITICAL) - no causal over-emphasis"""  
        # Test with theory that integrates multiple purposes without artificial bias
        balanced_theory = """
        This theory explains how educational systems develop through systematic
        classification of institutional types and their causal relationships with
        student outcomes. The framework predicts achievement patterns based on
        systematic variables while providing implementation strategies for educational
        interventions. The explanatory mechanisms show how institutional structures
        cause learning improvements through systematic processes, while the descriptive
        taxonomy categorizes different educational approaches and their effectiveness.
        """
        
        result = self.classifier.classify_theory_purposes(balanced_theory)
        
        # Critical balance validation
        validation = {
            'theory_text': balanced_theory,
            'classification_result': result,
            'balance_check_passed': result['balanced_analysis']['balance_check'] == 'passed',
            'causal_overemphasis_detected': result['balanced_analysis']['causal_overemphasis_detected'],
            'equal_sophistication_confirmed': result['balanced_analysis']['equal_sophistication_applied'],
            'purpose_confidence_scores': result['purpose_confidence'],
            'balance_metrics': result['balanced_analysis']['balance_metrics'],
            'critical_test_passed': result['balanced_analysis']['balance_check'] == 'passed' and not result['balanced_analysis']['causal_overemphasis_detected']
        }
        
        print(f"   Balance Check: {result['balanced_analysis']['balance_check']}")
        print(f"   Causal Over-emphasis: {result['balanced_analysis']['causal_overemphasis_detected']}")
        print(f"   Equal Sophistication: {result['balanced_analysis']['equal_sophistication_applied']}")
        print(f"   CRITICAL Test Passed: {validation['critical_test_passed']}")
        
        # Additional balance tests
        validation['prompt_balance_validation'] = self.prompts.validate_prompt_balance()
        
        return validation
    
    def assess_overall_performance(self) -> dict:
        """Assess overall system performance against success criteria"""
        assessment = {
            'success_criteria_met': {},
            'overall_score': 0,
            'critical_failures': [],
            'system_ready': False
        }
        
        # Criterion 1: Balanced Classification
        descriptive_passed = self.test_results.get('descriptive', {}).get('test_passed', False)
        explanatory_passed = self.test_results.get('explanatory', {}).get('test_passed', False)
        predictive_passed = self.test_results.get('predictive', {}).get('test_passed', False)
        causal_passed = self.test_results.get('causal', {}).get('test_passed', False)
        intervention_passed = self.test_results.get('intervention', {}).get('test_passed', False)
        
        balanced_classification = all([descriptive_passed, explanatory_passed, predictive_passed, causal_passed, intervention_passed])
        assessment['success_criteria_met']['balanced_classification'] = balanced_classification
        
        # Criterion 2: No Causal Over-Emphasis (CRITICAL)
        no_causal_overemphasis = not self.test_results.get('balance_validation', {}).get('causal_overemphasis_detected', True)
        assessment['success_criteria_met']['no_causal_overemphasis'] = no_causal_overemphasis
        if not no_causal_overemphasis:
            assessment['critical_failures'].append('Causal over-emphasis detected')
        
        # Criterion 3: Comprehensive Detection
        comprehensive_detection = self.test_results.get('balance_validation', {}).get('critical_test_passed', False)
        assessment['success_criteria_met']['comprehensive_detection'] = comprehensive_detection
        
        # Criterion 4: Multi-Purpose Support
        multi_purpose_support = self.test_results.get('multi_purpose', {}).get('test_passed', False)
        assessment['success_criteria_met']['multi_purpose_support'] = multi_purpose_support
        
        # Criterion 5: Production Ready
        prompt_balance = self.test_results.get('balance_validation', {}).get('prompt_balance_validation', {}).get('balance_maintained', False)
        production_ready = prompt_balance and balanced_classification
        assessment['success_criteria_met']['production_ready'] = production_ready
        
        # Calculate overall score
        criteria_met = sum(assessment['success_criteria_met'].values())
        assessment['overall_score'] = (criteria_met / 5) * 100
        
        # System readiness
        assessment['system_ready'] = assessment['overall_score'] == 100 and len(assessment['critical_failures']) == 0
        
        print(f"   Balanced Classification: {balanced_classification}")
        print(f"   No Causal Over-emphasis: {no_causal_overemphasis}")
        print(f"   Comprehensive Detection: {comprehensive_detection}")
        print(f"   Multi-Purpose Support: {multi_purpose_support}")
        print(f"   Production Ready: {production_ready}")
        print(f"   Overall Score: {assessment['overall_score']}/100")
        print(f"   System Ready: {assessment['system_ready']}")
        
        if assessment['critical_failures']:
            print(f"   CRITICAL FAILURES: {assessment['critical_failures']}")
        
        return assessment
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("BALANCED PURPOSE CLASSIFICATION - TEST REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Test results summary
        for test_name, test_result in self.test_results.items():
            if test_name == 'overall_assessment':
                continue
                
            report.append(f"Test: {test_name.replace('_', ' ').title()}")
            report.append("-" * 40)
            
            if isinstance(test_result, dict):
                passed = test_result.get('test_passed', test_result.get('critical_test_passed', False))
                report.append(f"Status: {'PASSED' if passed else 'FAILED'}")
                
                if 'primary_purpose_correct' in test_result:
                    report.append(f"Primary Purpose Correct: {test_result['primary_purpose_correct']}")
                
                if 'equal_sophistication_applied' in test_result:
                    report.append(f"Equal Sophistication Applied: {test_result['equal_sophistication_applied']}")
                
                if 'causal_overemphasis_detected' in test_result:
                    report.append(f"Causal Over-emphasis Detected: {test_result['causal_overemphasis_detected']}")
            
            report.append("")
        
        # Overall assessment
        if 'overall_assessment' in self.test_results:
            assessment = self.test_results['overall_assessment']
            report.append("OVERALL ASSESSMENT")
            report.append("-" * 40)
            report.append(f"Overall Score: {assessment['overall_score']}/100")
            report.append(f"System Ready: {assessment['system_ready']}")
            
            if assessment['critical_failures']:
                report.append(f"Critical Failures: {', '.join(assessment['critical_failures'])}")
            
            report.append("")
            report.append("Success Criteria:")
            for criterion, met in assessment['success_criteria_met'].items():
                report.append(f"  {criterion.replace('_', ' ').title()}: {'✓' if met else '✗'}")
        
        return "\n".join(report)


def run_comprehensive_tests():
    """Run all comprehensive tests and return results"""
    tester = PurposeClassificationTester()
    results = tester.run_all_tests()
    report = tester.generate_test_report()
    
    return results, report


if __name__ == "__main__":
    print("Starting Comprehensive Purpose Classification Tests...")
    results, report = run_comprehensive_tests()
    
    print("\n" + "=" * 60)
    print("FINAL TEST REPORT")
    print("=" * 60)
    print(report)
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest results saved to: test_results.json")
    print(f"Overall system readiness: {results.get('overall_assessment', {}).get('system_ready', False)}")