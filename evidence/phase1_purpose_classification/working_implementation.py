#!/usr/bin/env python3
"""
Working Implementation - Balanced Purpose Classification System

Standalone demonstration script showing the complete balanced purpose
classification system in action with equal treatment across all five purposes.
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from purpose_classifier import PurposeClassifier
from balanced_prompts import BalancedPrompts
from test_purpose_classification import run_comprehensive_tests


class BalancedPurposeClassificationDemo:
    """Standalone demonstration of balanced purpose classification"""
    
    def __init__(self):
        self.classifier = PurposeClassifier()
        self.prompts = BalancedPrompts()
        print("Balanced Purpose Classification System Initialized")
        print("=" * 60)
        print("CRITICAL FEATURE: Equal sophistication across all five purposes")
        print("NO CAUSAL OVER-EMPHASIS - All purposes treated equally")
        print("=" * 60)
    
    def demonstrate_balanced_classification(self):
        """Demonstrate balanced classification across all five purposes"""
        print("\n🎯 DEMONSTRATION: Balanced Purpose Classification")
        print("-" * 50)
        
        # Example theories for each purpose
        test_theories = {
            'descriptive_example': {
                'title': 'Organizational Taxonomy Theory',
                'text': """
                This theory establishes a comprehensive taxonomy of organizational structures
                based on systematic classification of structural dimensions. The typological
                framework categorizes organizations into hierarchical, network, and hybrid types.
                Each organizational type is characterized by specific attributes including
                centralization, formalization, and complexity levels. The dimensional analysis
                provides systematic categorization based on structural characteristics.
                """
            },
            
            'explanatory_example': {
                'title': 'Social Capital Formation Theory',
                'text': """
                This theory explains how social capital emerges through systematic interaction
                mechanisms within community networks. The underlying process involves repeated
                exchanges that generate trust and reciprocity norms. The structural relationships
                between individuals create systematic patterns of cooperation. The functional
                explanation shows how these mechanisms reduce transaction costs and enable
                collective action through systematic social processes.
                """
            },
            
            'predictive_example': {
                'title': 'Voter Turnout Prediction Model',
                'text': """
                This theory predicts voter participation based on systematic analysis of
                demographic and political variables. The forecasting framework incorporates
                predictor variables including age, education, and political efficacy. The
                statistical model estimates probability of voting using regression analysis.
                The predictive framework projects future voting patterns with specified
                confidence intervals and validation measures.
                """
            },
            
            'causal_example': {
                'title': 'Education-Economic Development Theory',
                'text': """
                This theory identifies causal relationships between educational investment
                and economic outcomes. The causal mechanism operates through human capital
                formation that leads to productivity increases. Educational interventions
                cause measurable improvements through systematic causal pathways. The
                treatment effects of education programs result in higher income levels
                through well-defined causal processes.
                """
            },
            
            'intervention_example': {
                'title': 'Community Development Implementation Framework',
                'text': """
                This theory provides actionable framework for implementing community development
                programs. The implementation strategy specifies systematic approaches to program
                design and delivery. Policy recommendations include specific action plans for
                addressing urban challenges. The practical application framework guides
                evidence-based interventions with detailed implementation strategies.
                """
            }
        }
        
        # Classify each theory
        results = {}
        for example_type, theory_data in test_theories.items():
            print(f"\n📋 Analyzing: {theory_data['title']}")
            print(f"   Expected Purpose: {example_type.split('_')[0]}")
            
            classification = self.classifier.classify_theory_purposes(theory_data['text'])
            results[example_type] = classification
            
            print(f"   Detected Primary Purpose: {classification['primary_purpose']}")
            print(f"   Confidence Scores:")
            for purpose, confidence in classification['purpose_confidence'].items():
                print(f"     {purpose}: {confidence:.3f}")
            
            # Check balance
            balance_ok = not classification['balanced_analysis']['causal_overemphasis_detected']
            print(f"   Balance Check: {'✓ PASSED' if balance_ok else '✗ FAILED'}")
            
            if classification['secondary_purposes']:
                print(f"   Secondary Purposes: {', '.join(classification['secondary_purposes'])}")
        
        return results
    
    def demonstrate_balance_validation(self):
        """Demonstrate critical balance validation"""
        print("\n⚖️  DEMONSTRATION: Balance Validation (CRITICAL)")
        print("-" * 50)
        
        # Test theory with integrated multiple purposes for balance validation
        balance_test_theory = """
        This theory explains how educational systems develop through systematic
        classification of institutional types and their causal relationships with
        student outcomes. The framework predicts achievement patterns based on
        systematic variables while providing implementation strategies for educational
        interventions. The explanatory mechanisms show how institutional structures
        cause learning improvements through systematic processes, while the descriptive
        taxonomy categorizes different educational approaches and their effectiveness.
        """
        
        print("Testing theory with balanced multi-purpose language...")
        classification = self.classifier.classify_theory_purposes(balance_test_theory)
        
        print(f"Primary Purpose: {classification['primary_purpose']}")
        print(f"Balance Check: {classification['balanced_analysis']['balance_check']}")
        print(f"Causal Over-emphasis Detected: {classification['balanced_analysis']['causal_overemphasis_detected']}")
        print(f"Equal Sophistication Applied: {classification['balanced_analysis']['equal_sophistication_applied']}")
        
        # Show confidence scores
        print("\nConfidence Scores:")
        for purpose, confidence in classification['purpose_confidence'].items():
            print(f"  {purpose}: {confidence:.3f}")
        
        # Balance metrics
        balance_metrics = classification['balanced_analysis']['balance_metrics']
        print(f"\nBalance Metrics:")
        print(f"  Score Range: {balance_metrics['score_range']:.3f}")
        print(f"  Mean Score: {balance_metrics['mean_score']:.3f}")
        print(f"  Coefficient of Variation: {balance_metrics['coefficient_of_variation']:.3f}")
        
        return classification
    
    def demonstrate_prompt_balance(self):
        """Demonstrate balanced prompt system"""
        print("\n📝 DEMONSTRATION: Balanced Prompt System")
        print("-" * 50)
        
        # Validate prompt balance
        balance_validation = self.prompts.validate_prompt_balance()
        
        print(f"Prompt Balance Maintained: {balance_validation['balance_maintained']}")
        print(f"Equal Sophistication Confirmed: {balance_validation['equal_sophistication_confirmed']}")
        print(f"Causal Over-emphasis Detected: {balance_validation['causal_overemphasis_detected']}")
        
        print("\nPrompt Analysis:")
        for purpose, analysis in balance_validation['prompt_analysis'].items():
            print(f"  {purpose}:")
            print(f"    Equal Priority Language: {analysis['has_equal_priority']}")
            print(f"    Sophistication Requirement: {analysis['has_sophistication_requirement']}")
            print(f"    Sophistication Markers: {analysis['marker_count']}")
            print(f"    Analytical Depth Indicators: {analysis['analytical_depth_indicators']}")
        
        return balance_validation
    
    def demonstrate_multi_purpose_handling(self):
        """Demonstrate multi-purpose theory handling"""
        print("\n🔄 DEMONSTRATION: Multi-Purpose Theory Handling")
        print("-" * 50)
        
        multi_purpose_theory = """
        This comprehensive theory explains inequality mechanisms through systematic
        classification of inequality types and their causal relationships. The theory
        predicts future inequality trends based on economic variables while providing
        actionable policy recommendations. The explanatory framework identifies processes
        that generate inequality, the predictive model forecasts outcomes, and the
        intervention component specifies implementation strategies for reduction programs.
        """
        
        print("Analyzing multi-purpose theory...")
        classification = self.classifier.classify_theory_purposes(multi_purpose_theory)
        
        print(f"Primary Purpose: {classification['primary_purpose']}")
        print(f"Secondary Purposes: {', '.join(classification['secondary_purposes'])}")
        print(f"Total Purposes Detected: {1 + len(classification['secondary_purposes'])}")
        
        print("\nAll Purpose Confidence Scores:")
        for purpose, confidence in sorted(classification['purpose_confidence'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {purpose}: {confidence:.3f}")
        
        # Balance maintained?
        balance_ok = classification['balanced_analysis']['balance_check'] == 'passed'
        print(f"\nBalance Maintained: {'✓ YES' if balance_ok else '✗ NO'}")
        
        return classification
    
    def run_full_demonstration(self):
        """Run complete demonstration of balanced purpose classification"""
        print("🚀 BALANCED PURPOSE CLASSIFICATION SYSTEM")
        print("Complete Demonstration with Equal Treatment")
        print("=" * 60)
        
        # 1. Balanced classification demonstration
        classification_results = self.demonstrate_balanced_classification()
        
        # 2. Balance validation demonstration
        balance_results = self.demonstrate_balance_validation()
        
        # 3. Prompt balance demonstration
        prompt_results = self.demonstrate_prompt_balance()
        
        # 4. Multi-purpose handling demonstration
        multi_purpose_results = self.demonstrate_multi_purpose_handling()
        
        # 5. Summary
        print("\n📊 DEMONSTRATION SUMMARY")
        print("-" * 50)
        
        # Check if all demonstrations passed
        all_demos_passed = True
        
        # Check classification accuracy
        expected_purposes = ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']
        classification_accuracy = 0
        for i, purpose in enumerate(expected_purposes):
            example_key = f"{purpose}_example"
            if example_key in classification_results:
                if classification_results[example_key]['primary_purpose'] == purpose:
                    classification_accuracy += 1
                else:
                    all_demos_passed = False
        
        print(f"Classification Accuracy: {classification_accuracy}/5 ({classification_accuracy/5*100:.0f}%)")
        
        # Check balance validation
        balance_passed = balance_results['balanced_analysis']['balance_check'] == 'passed'
        print(f"Balance Validation: {'✓ PASSED' if balance_passed else '✗ FAILED'}")
        if not balance_passed:
            all_demos_passed = False
        
        # Check prompt balance
        prompt_balance_passed = prompt_results['balance_maintained']
        print(f"Prompt Balance: {'✓ PASSED' if prompt_balance_passed else '✗ FAILED'}")
        if not prompt_balance_passed:
            all_demos_passed = False
        
        # Check multi-purpose handling
        multi_purpose_passed = len(multi_purpose_results['secondary_purposes']) >= 1
        print(f"Multi-Purpose Handling: {'✓ PASSED' if multi_purpose_passed else '✗ FAILED'}")
        if not multi_purpose_passed:
            all_demos_passed = False
        
        print(f"\nOverall Demonstration: {'✅ ALL PASSED' if all_demos_passed else '❌ SOME FAILED'}")
        
        return {
            'classification_results': classification_results,
            'balance_results': balance_results,
            'prompt_results': prompt_results,
            'multi_purpose_results': multi_purpose_results,
            'summary': {
                'classification_accuracy': classification_accuracy,
                'balance_passed': balance_passed,
                'prompt_balance_passed': prompt_balance_passed,
                'multi_purpose_passed': multi_purpose_passed,
                'all_demos_passed': all_demos_passed
            }
        }


def main():
    """Main demonstration function"""
    print("BALANCED PURPOSE CLASSIFICATION SYSTEM")
    print("Working Implementation Demonstration")
    print("=" * 60)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize demonstration
    demo = BalancedPurposeClassificationDemo()
    
    # Run full demonstration
    results = demo.run_full_demonstration()
    
    # Run comprehensive tests
    print("\n🧪 RUNNING COMPREHENSIVE TESTS")
    print("=" * 60)
    test_results, test_report = run_comprehensive_tests()
    
    # Final summary
    print("\n🎯 FINAL SYSTEM ASSESSMENT")
    print("=" * 60)
    
    demo_passed = results['summary']['all_demos_passed']
    tests_passed = test_results.get('overall_assessment', {}).get('system_ready', False)
    
    print(f"Demonstration Status: {'✅ PASSED' if demo_passed else '❌ FAILED'}")
    print(f"Test Suite Status: {'✅ PASSED' if tests_passed else '❌ FAILED'}")
    print(f"System Ready: {'✅ YES' if demo_passed and tests_passed else '❌ NO'}")
    
    if demo_passed and tests_passed:
        print("\n🎉 SUCCESS: Balanced Purpose Classification System is ready for production!")
        print("✓ Equal sophistication across all five purposes")
        print("✓ No causal over-emphasis detected")
        print("✓ Comprehensive detection capabilities")
        print("✓ Multi-purpose theory support")
        print("✓ All tests passed")
    else:
        print("\n⚠️  ISSUES DETECTED: System requires attention before production use.")
        if not demo_passed:
            print("✗ Demonstration failures detected")
        if not tests_passed:
            print("✗ Test suite failures detected")
    
    # Save results
    output_file = f"working_implementation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'demonstration_results': results,
            'test_results': test_results,
            'execution_timestamp': datetime.now().isoformat(),
            'system_ready': demo_passed and tests_passed
        }, f, indent=2, default=str)
    
    print(f"\nResults saved to: {output_file}")
    
    return demo_passed and tests_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)