"""
Working Implementation Demonstration - Multi-Purpose Schema Generation
Standalone script demonstrating balanced schema generation capabilities.
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schema_generator import MultiPurposeSchemaGenerator
from schema_templates import BalancedSchemaTemplates
from purpose_enhancers import PurposeEnhancers

class SchemaGenerationDemo:
    """Demonstration of balanced multi-purpose schema generation"""
    
    def __init__(self):
        self.generator = MultiPurposeSchemaGenerator()
        self.templates = BalancedSchemaTemplates()
        self.enhancers = PurposeEnhancers()
        
        # Demo vocabulary representing different theoretical domains
        self.demo_vocabulary = {
            'descriptive_terms': [
                'social_actor', 'institutional_structure', 'organizational_form', 'system_boundary',
                'actor_type', 'institution_category', 'structural_pattern', 'system_configuration',
                'behavioral_characteristic', 'institutional_property', 'organizational_attribute', 'system_feature'
            ],
            'explanatory_terms': [
                'causal_mechanism', 'institutional_process', 'organizational_dynamics', 'system_function',
                'feedback_mechanism', 'adaptation_process', 'evolutionary_dynamic', 'emergent_property',
                'interaction_pattern', 'dependency_relationship', 'influence_pathway', 'transformation_process'
            ],
            'predictive_terms': [
                'behavioral_trend', 'institutional_trajectory', 'organizational_evolution', 'system_development',
                'performance_indicator', 'outcome_predictor', 'change_signal', 'stability_measure',
                'risk_factor', 'opportunity_indicator', 'scenario_driver', 'forecast_variable'
            ],
            'causal_terms': [
                'causal_relationship', 'treatment_effect', 'intervention_impact', 'policy_outcome',
                'confounding_factor', 'mediating_variable', 'moderating_condition', 'instrumental_variable',
                'selection_bias', 'endogeneity_concern', 'identification_strategy', 'causal_inference'
            ],
            'intervention_terms': [
                'policy_intervention', 'program_implementation', 'strategic_action', 'operational_deployment',
                'resource_allocation', 'stakeholder_engagement', 'change_management', 'implementation_strategy',
                'monitoring_system', 'evaluation_framework', 'sustainability_mechanism', 'scaling_approach'
            ]
        }
    
    def run_complete_demonstration(self) -> dict:
        """Run complete demonstration of schema generation capabilities"""
        print("=== Multi-Purpose Schema Generation Demonstration ===")
        print("Generating schemas with equal analytical sophistication across all purposes...\n")
        
        demo_results = {
            'timestamp': datetime.now().isoformat(),
            'demonstration_type': 'balanced_multi_purpose_schema_generation',
            'demos': {}
        }
        
        # Demo 1: Single-purpose schemas (demonstrating equal sophistication)
        print("Demo 1: Single-Purpose Schema Generation")
        demo_results['demos']['single_purpose'] = self._demo_single_purpose_schemas()
        
        # Demo 2: Multi-purpose integrated schema
        print("\nDemo 2: Multi-Purpose Integrated Schema")
        demo_results['demos']['multi_purpose'] = self._demo_multi_purpose_schema()
        
        # Demo 3: Schema enhancement demonstration
        print("\nDemo 3: Schema Enhancement Demonstration")
        demo_results['demos']['enhanced_schemas'] = self._demo_schema_enhancement()
        
        # Demo 4: Balance verification demonstration
        print("\nDemo 4: Balance Verification Demonstration")
        demo_results['demos']['balance_verification'] = self._demo_balance_verification()
        
        # Demo 5: Cross-purpose integration demonstration
        print("\nDemo 5: Cross-Purpose Integration Demonstration")
        demo_results['demos']['cross_purpose_integration'] = self._demo_cross_purpose_integration()
        
        # Generate overall summary
        demo_results['summary'] = self._generate_demo_summary(demo_results['demos'])
        
        return demo_results
    
    def _demo_single_purpose_schemas(self) -> dict:
        """Demonstrate single-purpose schema generation with equal sophistication"""
        print("Generating schemas for each purpose with equal sophistication levels...")
        
        single_purpose_results = {}
        purposes = ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']
        
        for purpose in purposes:
            print(f"  Generating {purpose} schema...")
            
            schema = self.generator.generate_balanced_schema(
                vocabulary=self.demo_vocabulary,
                purposes=[purpose],
                model_type=f'{purpose}_theory_model'
            )
            
            # Extract key metrics
            purpose_capability = schema.get('purpose_capabilities', {}).get(purpose, {})
            
            single_purpose_results[purpose] = {
                'model_type': schema.get('model_type'),
                'sophistication_level': purpose_capability.get('sophistication_level', 0),
                'core_functions_count': len(purpose_capability.get('core_functions', {})),
                'analytical_operations_count': len(purpose_capability.get('analytical_operations', [])),
                'output_formats_count': len(purpose_capability.get('output_formats', [])),
                'balance_status': schema.get('balance_validation', {}).get('balance_status', 'UNKNOWN'),
                'schema_generated': True
            }
        
        # Verify equal sophistication
        sophistication_levels = [result['sophistication_level'] for result in single_purpose_results.values()]
        equal_sophistication = len(set(sophistication_levels)) <= 1
        
        print(f"  Equal sophistication verified: {equal_sophistication}")
        print(f"  Sophistication levels: {dict(zip(purposes, sophistication_levels))}")
        
        return {
            'purpose_schemas': single_purpose_results,
            'equal_sophistication_verified': equal_sophistication,
            'sophistication_levels': dict(zip(purposes, sophistication_levels)),
            'balance_requirement_met': equal_sophistication
        }
    
    def _demo_multi_purpose_schema(self) -> dict:
        """Demonstrate multi-purpose integrated schema generation"""
        print("Generating comprehensive multi-purpose schema...")
        
        all_purposes = ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']
        
        integrated_schema = self.generator.generate_balanced_schema(
            vocabulary=self.demo_vocabulary,
            purposes=all_purposes,
            model_type='comprehensive_social_theory'
        )
        
        # Extract integration metrics
        cross_purpose_integration = integrated_schema.get('cross_purpose_integration', {})
        multi_purpose_operations = cross_purpose_integration.get('multi_purpose_operations', {})
        unified_workflows = cross_purpose_integration.get('unified_workflows', {})
        
        # Extract balance metrics
        balance_validation = integrated_schema.get('balance_validation', {})
        sophistication_scores = balance_validation.get('sophistication_scores', {})
        
        print(f"  Purposes integrated: {len(all_purposes)}")
        print(f"  Multi-purpose operations: {len(multi_purpose_operations)}")
        print(f"  Unified workflows: {len(unified_workflows)}")
        print(f"  Balance status: {balance_validation.get('balance_status', 'UNKNOWN')}")
        
        return {
            'model_type': integrated_schema.get('model_type'),
            'purposes_integrated': len(all_purposes),
            'multi_purpose_operations_count': len(multi_purpose_operations),
            'unified_workflows_count': len(unified_workflows),
            'sophistication_scores': sophistication_scores,
            'balance_status': balance_validation.get('balance_status', 'UNKNOWN'),
            'balance_score': balance_validation.get('balance_score', 0.0),
            'equal_capabilities': balance_validation.get('equal_capabilities', False),
            'integration_successful': bool(cross_purpose_integration)
        }
    
    def _demo_schema_enhancement(self) -> dict:
        """Demonstrate schema enhancement capabilities"""
        print("Demonstrating schema enhancement for maximum sophistication...")
        
        # Generate base schema
        base_schema = self.generator.generate_balanced_schema(
            vocabulary=self.demo_vocabulary,
            purposes=['explanatory', 'causal'],
            model_type='causal_explanatory_model'
        )
        
        # Enhance schema
        enhanced_schema = self.enhancers.balance_all_enhancements(base_schema, self.demo_vocabulary)
        
        # Compare before and after
        base_capabilities = base_schema.get('purpose_capabilities', {})
        enhanced_capabilities = enhanced_schema.get('purpose_capabilities', {})
        
        enhancement_comparison = {}
        for purpose in ['explanatory', 'causal']:
            base_cap = base_capabilities.get(purpose, {})
            enhanced_cap = enhanced_capabilities.get(purpose, {})
            
            enhancement_comparison[purpose] = {
                'base_sophistication': base_cap.get('sophistication_level', 0),
                'enhanced_sophistication': enhanced_schema.get(f'{purpose}_sophistication_score', 0),
                'base_functions': len(base_cap.get('core_functions', {})),
                'enhanced_functions': len(enhanced_cap.get('core_functions', {})),
                'enhancement_present': f'{purpose}_enhancements' in enhanced_schema
            }
        
        # Validate enhancement balance
        enhancement_validation = self.enhancers.validate_enhancement_balance(enhanced_schema)
        
        print(f"  Enhancement applied to {len(enhancement_comparison)} purposes")
        print(f"  Enhancement balance status: {enhancement_validation.get('balance_status', 'UNKNOWN')}")
        
        return {
            'purposes_enhanced': list(enhancement_comparison.keys()),
            'enhancement_comparison': enhancement_comparison,
            'enhancement_validation': enhancement_validation,
            'balance_maintained': enhancement_validation.get('balance_status') in ['PERFECTLY_BALANCED', 'WELL_BALANCED']
        }
    
    def _demo_balance_verification(self) -> dict:
        """Demonstrate balance verification across all purposes"""
        print("Demonstrating comprehensive balance verification...")
        
        # Generate schema with all purposes for balance testing
        all_purposes = ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']
        
        balanced_schema = self.generator.generate_balanced_schema(
            vocabulary=self.demo_vocabulary,
            purposes=all_purposes,
            model_type='balanced_comprehensive_model'
        )
        
        # Extract detailed balance metrics
        balance_validation = balanced_schema.get('balance_validation', {})
        sophistication_scores = balance_validation.get('sophistication_scores', {})
        
        # Calculate additional balance metrics
        scores = list(sophistication_scores.values()) if sophistication_scores else []
        balance_metrics = {
            'score_range': max(scores) - min(scores) if scores else 0,
            'score_mean': sum(scores) / len(scores) if scores else 0,
            'score_std': self._calculate_std(scores) if scores else 0,
            'coefficient_of_variation': self._calculate_std(scores) / (sum(scores) / len(scores)) if scores and sum(scores) > 0 else 0
        }
        
        # Verify no causal over-emphasis
        causal_score = sophistication_scores.get('causal', 0)
        other_scores = [score for purpose, score in sophistication_scores.items() if purpose != 'causal']
        causal_over_emphasis = causal_score > max(other_scores) if other_scores else False
        
        print(f"  Balance status: {balance_validation.get('balance_status', 'UNKNOWN')}")
        print(f"  Balance score: {balance_validation.get('balance_score', 0.0):.3f}")
        print(f"  Score range: {balance_metrics['score_range']:.3f}")
        print(f"  Causal over-emphasis detected: {causal_over_emphasis}")
        
        return {
            'balance_validation': balance_validation,
            'balance_metrics': balance_metrics,
            'sophistication_scores': sophistication_scores,
            'causal_over_emphasis_detected': causal_over_emphasis,
            'balance_verified': balance_validation.get('balance_status') == 'BALANCED' and not causal_over_emphasis,
            'equal_sophistication_achieved': balance_metrics['coefficient_of_variation'] < 0.1
        }
    
    def _demo_cross_purpose_integration(self) -> dict:
        """Demonstrate cross-purpose integration capabilities"""
        print("Demonstrating cross-purpose integration workflows...")
        
        # Generate schema with complementary purposes
        test_purposes = ['descriptive', 'explanatory', 'predictive', 'intervention']
        
        integrated_schema = self.generator.generate_balanced_schema(
            vocabulary=self.demo_vocabulary,
            purposes=test_purposes,
            model_type='integrated_workflow_model'
        )
        
        # Extract integration details
        cross_purpose_integration = integrated_schema.get('cross_purpose_integration', {})
        multi_purpose_operations = cross_purpose_integration.get('multi_purpose_operations', {})
        unified_workflows = cross_purpose_integration.get('unified_workflows', {})
        cross_validation = cross_purpose_integration.get('cross_validation', {})
        
        # Test specific integration patterns
        integration_patterns = {}
        for operation_name, operation_details in multi_purpose_operations.items():
            integration_patterns[operation_name] = {
                'integration_type': operation_details.get('integration'),
                'operations_count': len(operation_details.get('operations', [])),
                'interfaces_present': 'interfaces' in operation_details
            }
        
        # Test workflow completeness
        workflow_completeness = {}
        for workflow_name, workflow_details in unified_workflows.items():
            workflow_completeness[workflow_name] = {
                'workflow_type': workflow_details.get('workflow'),
                'stages_count': len(workflow_details.get('steps', [])),
                'capabilities_specified': 'capabilities' in workflow_details,
                'outputs_defined': 'outputs' in workflow_details
            }
        
        print(f"  Integration patterns: {len(integration_patterns)}")
        print(f"  Unified workflows: {len(workflow_completeness)}")
        print(f"  Cross-validation present: {bool(cross_validation)}")
        
        return {
            'purposes_integrated': test_purposes,
            'integration_patterns': integration_patterns,
            'workflow_completeness': workflow_completeness,
            'cross_validation': cross_validation,
            'integration_successful': len(integration_patterns) >= 3 and len(workflow_completeness) >= 2,
            'comprehensive_integration': bool(cross_purpose_integration)
        }
    
    def _generate_demo_summary(self, demos: dict) -> dict:
        """Generate overall demonstration summary"""
        summary = {
            'total_demos': len(demos),
            'successful_demos': 0,
            'balance_verifications': {},
            'critical_requirements_met': {},
            'overall_success': False
        }
        
        # Check each demo success
        for demo_name, demo_results in demos.items():
            if isinstance(demo_results, dict):
                # Define success criteria for each demo
                if demo_name == 'single_purpose':
                    success = demo_results.get('equal_sophistication_verified', False)
                elif demo_name == 'multi_purpose':
                    success = (demo_results.get('integration_successful', False) and 
                              demo_results.get('balance_status') == 'BALANCED')
                elif demo_name == 'enhanced_schemas':
                    success = demo_results.get('balance_maintained', False)
                elif demo_name == 'balance_verification':
                    success = demo_results.get('balance_verified', False)
                elif demo_name == 'cross_purpose_integration':
                    success = demo_results.get('integration_successful', False)
                else:
                    success = False
                
                if success:
                    summary['successful_demos'] += 1
        
        # Extract balance verifications
        summary['balance_verifications'] = {
            'single_purpose_equal_sophistication': demos.get('single_purpose', {}).get('equal_sophistication_verified', False),
            'multi_purpose_balanced': demos.get('multi_purpose', {}).get('balance_status') == 'BALANCED',
            'enhancement_balance_maintained': demos.get('enhanced_schemas', {}).get('balance_maintained', False),
            'comprehensive_balance_verified': demos.get('balance_verification', {}).get('balance_verified', False),
            'no_causal_over_emphasis': not demos.get('balance_verification', {}).get('causal_over_emphasis_detected', True)
        }
        
        # Check critical requirements
        summary['critical_requirements_met'] = {
            'equal_sophistication_across_purposes': all([
                summary['balance_verifications']['single_purpose_equal_sophistication'],
                summary['balance_verifications']['multi_purpose_balanced']
            ]),
            'no_causal_bias': summary['balance_verifications']['no_causal_over_emphasis'],
            'comprehensive_integration': demos.get('cross_purpose_integration', {}).get('comprehensive_integration', False),
            'enhancement_capabilities': demos.get('enhanced_schemas', {}).get('balance_maintained', False)
        }
        
        # Overall success
        summary['overall_success'] = all(summary['critical_requirements_met'].values())
        summary['success_rate'] = summary['successful_demos'] / summary['total_demos'] * 100 if summary['total_demos'] > 0 else 0
        
        return summary
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

def main():
    """Run the working implementation demonstration"""
    print("Starting Multi-Purpose Schema Generation Working Implementation Demo...")
    
    demo = SchemaGenerationDemo()
    results = demo.run_complete_demonstration()
    
    # Print comprehensive summary
    summary = results['summary']
    print(f"\n=== DEMONSTRATION SUMMARY ===")
    print(f"Total Demonstrations: {summary['total_demos']}")
    print(f"Successful Demonstrations: {summary['successful_demos']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Overall Success: {summary['overall_success']}")
    
    print(f"\n=== BALANCE VERIFICATIONS ===")
    for verification, status in summary['balance_verifications'].items():
        print(f"{verification}: {'✓' if status else '✗'}")
    
    print(f"\n=== CRITICAL REQUIREMENTS ===")
    for requirement, met in summary['critical_requirements_met'].items():
        print(f"{requirement}: {'✓' if met else '✗'}")
    
    # Save results with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"working_implementation_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    results = main()