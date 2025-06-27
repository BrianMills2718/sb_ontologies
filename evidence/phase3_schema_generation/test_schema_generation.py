"""
Comprehensive Test Suite for Multi-Purpose Schema Generation
Tests balanced schema generation across all theoretical purposes.
"""

import json
import sys
import os
from typing import Dict, List, Any

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schema_generator import MultiPurposeSchemaGenerator
from schema_templates import BalancedSchemaTemplates
from purpose_enhancers import PurposeEnhancers

class SchemaGenerationTester:
    """Test suite for balanced schema generation"""
    
    def __init__(self):
        self.generator = MultiPurposeSchemaGenerator()
        self.templates = BalancedSchemaTemplates()
        self.enhancers = PurposeEnhancers()
        self.test_results = {}
        
        # Test vocabulary for different purposes
        self.test_vocabulary = {
            'descriptive_terms': [
                'actor', 'institution', 'organization', 'system', 'structure',
                'type', 'category', 'classification', 'taxonomy', 'typology',
                'characteristic', 'property', 'attribute', 'feature', 'dimension'
            ],
            'explanatory_terms': [
                'mechanism', 'process', 'function', 'interaction', 'relationship',
                'cause', 'effect', 'influence', 'impact', 'pathway',
                'dynamic', 'feedback', 'emergence', 'adaptation', 'evolution'
            ],
            'predictive_terms': [
                'trend', 'pattern', 'trajectory', 'forecast', 'projection',
                'model', 'prediction', 'probability', 'likelihood', 'scenario',
                'variable', 'factor', 'indicator', 'predictor', 'outcome'
            ],
            'causal_terms': [
                'cause', 'effect', 'treatment', 'intervention', 'impact',
                'confounding', 'mediation', 'moderation', 'interaction', 'pathway',
                'randomization', 'identification', 'inference', 'estimation', 'validation'
            ],
            'intervention_terms': [
                'strategy', 'action', 'implementation', 'deployment', 'execution',
                'intervention', 'program', 'policy', 'initiative', 'project',
                'resource', 'stakeholder', 'objective', 'goal', 'outcome'
            ]
        }
    
    def run_all_tests(self) -> dict:
        """Run all test suites and return comprehensive results"""
        print("Starting comprehensive schema generation testing...")
        
        # Test 1: Descriptive schema generation
        self.test_results['test_1'] = self.test_descriptive_schema_generation()
        
        # Test 2: Explanatory schema generation
        self.test_results['test_2'] = self.test_explanatory_schema_generation()
        
        # Test 3: Predictive schema generation  
        self.test_results['test_3'] = self.test_predictive_schema_generation()
        
        # Test 4: Causal schema generation
        self.test_results['test_4'] = self.test_causal_schema_generation()
        
        # Test 5: Intervention schema generation
        self.test_results['test_5'] = self.test_intervention_schema_generation()
        
        # Test 6: Multi-purpose schema integration
        self.test_results['test_6'] = self.test_multi_purpose_integration()
        
        # Test 7: Cross-purpose capability validation
        self.test_results['test_7'] = self.test_cross_purpose_capabilities()
        
        # Test 8: Schema balance verification
        self.test_results['test_8'] = self.test_schema_balance_verification()
        
        # Generate overall test report
        self.test_results['overall_summary'] = self._generate_test_summary()
        
        return self.test_results
    
    def test_descriptive_schema_generation(self) -> dict:
        """Test 1: Descriptive schema generation (taxonomies, classifications)"""
        print("Running Test 1: Descriptive Schema Generation...")
        
        try:
            # Generate descriptive schema
            descriptive_schema = self.generator.generate_balanced_schema(
                vocabulary=self.test_vocabulary,
                purposes=['descriptive'],
                model_type='social_ecological_system'
            )
            
            # Validate schema structure
            validation_results = self._validate_schema_structure(descriptive_schema, 'descriptive')
            
            # Check descriptive-specific capabilities
            descriptive_capabilities = descriptive_schema.get('purpose_capabilities', {}).get('descriptive', {})
            
            test_result = {
                'test_name': 'Descriptive Schema Generation',
                'status': 'PASSED',
                'schema_generated': bool(descriptive_schema),
                'purpose_supported': 'descriptive' in descriptive_schema.get('theoretical_purposes', []),
                'capabilities_present': bool(descriptive_capabilities),
                'sophistication_level': descriptive_capabilities.get('sophistication_level', 0),
                'core_functions': len(descriptive_capabilities.get('core_functions', {})),
                'analytical_operations': len(descriptive_capabilities.get('analytical_operations', [])),
                'output_formats': len(descriptive_capabilities.get('output_formats', [])),
                'validation_results': validation_results,
                'balance_status': descriptive_schema.get('balance_validation', {}).get('balance_status', 'UNKNOWN')
            }
            
            # Check if test passed
            if (test_result['schema_generated'] and 
                test_result['purpose_supported'] and 
                test_result['capabilities_present'] and
                test_result['sophistication_level'] >= 8):
                test_result['status'] = 'PASSED'
            else:
                test_result['status'] = 'FAILED'
                test_result['failure_reasons'] = self._identify_failure_reasons(test_result)
            
            return test_result
            
        except Exception as e:
            return {
                'test_name': 'Descriptive Schema Generation',
                'status': 'ERROR',
                'error': str(e),
                'traceback': str(e.__class__.__name__)
            }
    
    def test_explanatory_schema_generation(self) -> dict:
        """Test 2: Explanatory schema generation (mechanisms, processes)"""
        print("Running Test 2: Explanatory Schema Generation...")
        
        try:
            explanatory_schema = self.generator.generate_balanced_schema(
                vocabulary=self.test_vocabulary,
                purposes=['explanatory'],
                model_type='institutional_theory'
            )
            
            validation_results = self._validate_schema_structure(explanatory_schema, 'explanatory')
            explanatory_capabilities = explanatory_schema.get('purpose_capabilities', {}).get('explanatory', {})
            
            test_result = {
                'test_name': 'Explanatory Schema Generation',
                'status': 'PASSED',
                'schema_generated': bool(explanatory_schema),
                'purpose_supported': 'explanatory' in explanatory_schema.get('theoretical_purposes', []),
                'capabilities_present': bool(explanatory_capabilities),
                'sophistication_level': explanatory_capabilities.get('sophistication_level', 0),
                'core_functions': len(explanatory_capabilities.get('core_functions', {})),
                'analytical_operations': len(explanatory_capabilities.get('analytical_operations', [])),
                'output_formats': len(explanatory_capabilities.get('output_formats', [])),
                'validation_results': validation_results,
                'balance_status': explanatory_schema.get('balance_validation', {}).get('balance_status', 'UNKNOWN')
            }
            
            if (test_result['schema_generated'] and 
                test_result['purpose_supported'] and 
                test_result['capabilities_present'] and
                test_result['sophistication_level'] >= 8):
                test_result['status'] = 'PASSED'
            else:
                test_result['status'] = 'FAILED'
                test_result['failure_reasons'] = self._identify_failure_reasons(test_result)
            
            return test_result
            
        except Exception as e:
            return {
                'test_name': 'Explanatory Schema Generation',
                'status': 'ERROR',
                'error': str(e)
            }
    
    def test_predictive_schema_generation(self) -> dict:
        """Test 3: Predictive schema generation (models, forecasting)"""
        print("Running Test 3: Predictive Schema Generation...")
        
        try:
            predictive_schema = self.generator.generate_balanced_schema(
                vocabulary=self.test_vocabulary,
                purposes=['predictive'],
                model_type='network_theory'
            )
            
            validation_results = self._validate_schema_structure(predictive_schema, 'predictive')
            predictive_capabilities = predictive_schema.get('purpose_capabilities', {}).get('predictive', {})
            
            test_result = {
                'test_name': 'Predictive Schema Generation',
                'status': 'PASSED',
                'schema_generated': bool(predictive_schema),
                'purpose_supported': 'predictive' in predictive_schema.get('theoretical_purposes', []),
                'capabilities_present': bool(predictive_capabilities),
                'sophistication_level': predictive_capabilities.get('sophistication_level', 0),
                'core_functions': len(predictive_capabilities.get('core_functions', {})),
                'analytical_operations': len(predictive_capabilities.get('analytical_operations', [])),
                'output_formats': len(predictive_capabilities.get('output_formats', [])),
                'validation_results': validation_results,
                'balance_status': predictive_schema.get('balance_validation', {}).get('balance_status', 'UNKNOWN')
            }
            
            if (test_result['schema_generated'] and 
                test_result['purpose_supported'] and 
                test_result['capabilities_present'] and
                test_result['sophistication_level'] >= 8):
                test_result['status'] = 'PASSED'
            else:
                test_result['status'] = 'FAILED'
                test_result['failure_reasons'] = self._identify_failure_reasons(test_result)
            
            return test_result
            
        except Exception as e:
            return {
                'test_name': 'Predictive Schema Generation',
                'status': 'ERROR',
                'error': str(e)
            }
    
    def test_causal_schema_generation(self) -> dict:
        """Test 4: Causal schema generation (relationships, interventions)"""
        print("Running Test 4: Causal Schema Generation...")
        
        try:
            causal_schema = self.generator.generate_balanced_schema(
                vocabulary=self.test_vocabulary,
                purposes=['causal'],
                model_type='causal_model'
            )
            
            validation_results = self._validate_schema_structure(causal_schema, 'causal')
            causal_capabilities = causal_schema.get('purpose_capabilities', {}).get('causal', {})
            
            test_result = {
                'test_name': 'Causal Schema Generation',
                'status': 'PASSED',
                'schema_generated': bool(causal_schema),
                'purpose_supported': 'causal' in causal_schema.get('theoretical_purposes', []),
                'capabilities_present': bool(causal_capabilities),
                'sophistication_level': causal_capabilities.get('sophistication_level', 0),
                'core_functions': len(causal_capabilities.get('core_functions', {})),
                'analytical_operations': len(causal_capabilities.get('analytical_operations', [])),
                'output_formats': len(causal_capabilities.get('output_formats', [])),
                'validation_results': validation_results,
                'balance_status': causal_schema.get('balance_validation', {}).get('balance_status', 'UNKNOWN')
            }
            
            # CRITICAL: Causal capabilities must equal other purposes (no over-emphasis)
            if (test_result['schema_generated'] and 
                test_result['purpose_supported'] and 
                test_result['capabilities_present'] and
                test_result['sophistication_level'] >= 8 and
                test_result['sophistication_level'] <= 8):  # Not higher than others
                test_result['status'] = 'PASSED'
                test_result['balance_verified'] = True
            else:
                test_result['status'] = 'FAILED'
                test_result['failure_reasons'] = self._identify_failure_reasons(test_result)
                if test_result['sophistication_level'] > 8:
                    test_result['failure_reasons'].append('CAUSAL_OVER_EMPHASIS_DETECTED')
            
            return test_result
            
        except Exception as e:
            return {
                'test_name': 'Causal Schema Generation',
                'status': 'ERROR',
                'error': str(e)
            }
    
    def test_intervention_schema_generation(self) -> dict:
        """Test 5: Intervention schema generation (actions, implementation)"""
        print("Running Test 5: Intervention Schema Generation...")
        
        try:
            intervention_schema = self.generator.generate_balanced_schema(
                vocabulary=self.test_vocabulary,
                purposes=['intervention'],
                model_type='action_theory'
            )
            
            validation_results = self._validate_schema_structure(intervention_schema, 'intervention')
            intervention_capabilities = intervention_schema.get('purpose_capabilities', {}).get('intervention', {})
            
            test_result = {
                'test_name': 'Intervention Schema Generation',
                'status': 'PASSED',
                'schema_generated': bool(intervention_schema),
                'purpose_supported': 'intervention' in intervention_schema.get('theoretical_purposes', []),
                'capabilities_present': bool(intervention_capabilities),
                'sophistication_level': intervention_capabilities.get('sophistication_level', 0),
                'core_functions': len(intervention_capabilities.get('core_functions', {})),
                'analytical_operations': len(intervention_capabilities.get('analytical_operations', [])),
                'output_formats': len(intervention_capabilities.get('output_formats', [])),
                'validation_results': validation_results,
                'balance_status': intervention_schema.get('balance_validation', {}).get('balance_status', 'UNKNOWN')
            }
            
            if (test_result['schema_generated'] and 
                test_result['purpose_supported'] and 
                test_result['capabilities_present'] and
                test_result['sophistication_level'] >= 8):
                test_result['status'] = 'PASSED'
            else:
                test_result['status'] = 'FAILED'
                test_result['failure_reasons'] = self._identify_failure_reasons(test_result)
            
            return test_result
            
        except Exception as e:
            return {
                'test_name': 'Intervention Schema Generation',
                'status': 'ERROR',
                'error': str(e)
            }
    
    def test_multi_purpose_integration(self) -> dict:
        """Test 6: Multi-purpose schema integration"""
        print("Running Test 6: Multi-Purpose Schema Integration...")
        
        try:
            # Test with all purposes
            all_purposes = ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']
            integrated_schema = self.generator.generate_balanced_schema(
                vocabulary=self.test_vocabulary,
                purposes=all_purposes,
                model_type='comprehensive_theory'
            )
            
            # Check integration capabilities
            cross_purpose_integration = integrated_schema.get('cross_purpose_integration', {})
            multi_purpose_operations = cross_purpose_integration.get('multi_purpose_operations', {})
            unified_workflows = cross_purpose_integration.get('unified_workflows', {})
            
            test_result = {
                'test_name': 'Multi-Purpose Schema Integration',
                'status': 'PASSED',
                'schema_generated': bool(integrated_schema),
                'all_purposes_supported': all([p in integrated_schema.get('theoretical_purposes', []) for p in all_purposes]),
                'cross_purpose_integration': bool(cross_purpose_integration),
                'multi_purpose_operations': len(multi_purpose_operations),
                'unified_workflows': len(unified_workflows),
                'integration_validation': cross_purpose_integration.get('cross_validation', {}),
                'balance_status': integrated_schema.get('balance_validation', {}).get('balance_status', 'UNKNOWN')
            }
            
            if (test_result['schema_generated'] and 
                test_result['all_purposes_supported'] and 
                test_result['cross_purpose_integration'] and
                test_result['multi_purpose_operations'] >= 3 and
                test_result['unified_workflows'] >= 2):
                test_result['status'] = 'PASSED'
            else:
                test_result['status'] = 'FAILED'
                test_result['failure_reasons'] = self._identify_integration_failures(test_result)
            
            return test_result
            
        except Exception as e:
            return {
                'test_name': 'Multi-Purpose Schema Integration',
                'status': 'ERROR',
                'error': str(e)
            }
    
    def test_cross_purpose_capabilities(self) -> dict:
        """Test 7: Cross-purpose capability validation"""
        print("Running Test 7: Cross-Purpose Capability Validation...")
        
        try:
            # Generate schema with multiple purposes
            test_purposes = ['descriptive', 'explanatory', 'causal']
            schema = self.generator.generate_balanced_schema(
                vocabulary=self.test_vocabulary,
                purposes=test_purposes,
                model_type='multi_theory'
            )
            
            # Test cross-purpose operations
            capabilities = schema.get('purpose_capabilities', {})
            cross_integration = schema.get('cross_purpose_integration', {})
            
            # Check for integration interfaces in each capability
            integration_interfaces = {}
            for purpose, capability in capabilities.items():
                interfaces = capability.get('integration_interfaces', {})
                integration_interfaces[purpose] = len(interfaces)
            
            test_result = {
                'test_name': 'Cross-Purpose Capability Validation',
                'status': 'PASSED',
                'schema_generated': bool(schema),
                'purposes_count': len(test_purposes),
                'capabilities_generated': len(capabilities),
                'cross_integration_present': bool(cross_integration),
                'integration_interfaces': integration_interfaces,
                'total_integration_interfaces': sum(integration_interfaces.values()),
                'cross_validation': cross_integration.get('cross_validation', {}),
                'balance_status': schema.get('balance_validation', {}).get('balance_status', 'UNKNOWN')
            }
            
            # Calculate expected interfaces: each purpose should have interfaces to others
            expected_interfaces = len(test_purposes) * (len(test_purposes) - 1)
            
            if (test_result['schema_generated'] and 
                test_result['capabilities_generated'] == len(test_purposes) and
                test_result['cross_integration_present'] and
                test_result['total_integration_interfaces'] >= expected_interfaces):
                test_result['status'] = 'PASSED'
            else:
                test_result['status'] = 'FAILED'
                test_result['failure_reasons'] = self._identify_cross_purpose_failures(test_result)
            
            return test_result
            
        except Exception as e:
            return {
                'test_name': 'Cross-Purpose Capability Validation',
                'status': 'ERROR',
                'error': str(e)
            }
    
    def test_schema_balance_verification(self) -> dict:
        """Test 8: Schema balance verification (equal sophistication)"""
        print("Running Test 8: Schema Balance Verification...")
        
        try:
            # Generate schema with all purposes to test balance
            all_purposes = ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']
            balanced_schema = self.generator.generate_balanced_schema(
                vocabulary=self.test_vocabulary,
                purposes=all_purposes,
                model_type='balanced_theory'
            )
            
            # Get balance validation results
            balance_validation = balanced_schema.get('balance_validation', {})
            sophistication_scores = balance_validation.get('sophistication_scores', {})
            balance_score = balance_validation.get('balance_score', 0.0)
            balance_status = balance_validation.get('balance_status', 'UNKNOWN')
            
            # Calculate balance metrics
            scores = list(sophistication_scores.values()) if sophistication_scores else []
            score_variance = max(scores) - min(scores) if scores else 0
            equal_capabilities = balance_validation.get('equal_capabilities', False)
            
            test_result = {
                'test_name': 'Schema Balance Verification',
                'status': 'PASSED',
                'schema_generated': bool(balanced_schema),
                'balance_validation_present': bool(balance_validation),
                'sophistication_scores': sophistication_scores,
                'balance_score': balance_score,
                'balance_status': balance_status,
                'score_variance': score_variance,
                'equal_capabilities': equal_capabilities,
                'balance_threshold_met': balance_score >= 0.9,
                'variance_acceptable': score_variance <= 1.0,
                'all_purposes_equal': len(set(scores)) <= 2 if scores else True  # Allow minimal variation
            }
            
            # CRITICAL: Balance verification must pass for equal sophistication
            if (test_result['schema_generated'] and 
                test_result['balance_validation_present'] and
                test_result['balance_status'] == 'BALANCED' and
                test_result['balance_threshold_met'] and
                test_result['variance_acceptable'] and
                test_result['equal_capabilities']):
                test_result['status'] = 'PASSED'
                test_result['balance_verified'] = True
            else:
                test_result['status'] = 'FAILED'
                test_result['failure_reasons'] = self._identify_balance_failures(test_result)
                if balance_status == 'IMBALANCED':
                    test_result['failure_reasons'].append('BALANCE_FAILURE_DETECTED')
            
            return test_result
            
        except Exception as e:
            return {
                'test_name': 'Schema Balance Verification',
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _validate_schema_structure(self, schema: dict, purpose: str) -> dict:
        """Validate basic schema structure"""
        required_keys = [
            'model_type', 'theoretical_purposes', 'schema_blueprint',
            'purpose_capabilities', 'cross_purpose_integration', 'balance_validation'
        ]
        
        validation = {
            'required_keys_present': all(key in schema for key in required_keys),
            'missing_keys': [key for key in required_keys if key not in schema],
            'purpose_in_capabilities': purpose in schema.get('purpose_capabilities', {}),
            'blueprint_present': bool(schema.get('schema_blueprint', {})),
            'balance_validation_present': bool(schema.get('balance_validation', {}))
        }
        
        return validation
    
    def _identify_failure_reasons(self, test_result: dict) -> list:
        """Identify reasons for test failure"""
        reasons = []
        
        if not test_result.get('schema_generated', False):
            reasons.append('Schema generation failed')
        
        if not test_result.get('purpose_supported', False):
            reasons.append('Purpose not supported in schema')
        
        if not test_result.get('capabilities_present', False):
            reasons.append('Capabilities not present in schema')
        
        if test_result.get('sophistication_level', 0) < 8:
            reasons.append(f"Sophistication level too low: {test_result.get('sophistication_level', 0)}")
        
        validation_results = test_result.get('validation_results', {})
        if not validation_results.get('required_keys_present', False):
            reasons.append('Required schema keys missing')
        
        return reasons
    
    def _identify_integration_failures(self, test_result: dict) -> list:
        """Identify integration failure reasons"""
        reasons = []
        
        if not test_result.get('schema_generated', False):
            reasons.append('Integrated schema generation failed')
        
        if not test_result.get('all_purposes_supported', False):
            reasons.append('Not all purposes supported')
        
        if not test_result.get('cross_purpose_integration', False):
            reasons.append('Cross-purpose integration missing')
        
        if test_result.get('multi_purpose_operations', 0) < 3:
            reasons.append('Insufficient multi-purpose operations')
        
        if test_result.get('unified_workflows', 0) < 2:
            reasons.append('Insufficient unified workflows')
        
        return reasons
    
    def _identify_cross_purpose_failures(self, test_result: dict) -> list:
        """Identify cross-purpose capability failures"""
        reasons = []
        
        if test_result.get('capabilities_generated', 0) != test_result.get('purposes_count', 0):
            reasons.append('Capabilities not generated for all purposes')
        
        if not test_result.get('cross_integration_present', False):
            reasons.append('Cross-integration capabilities missing')
        
        # Calculate expected interfaces dynamically
        purposes_count = test_result.get('purposes_count', 0)
        expected_interfaces = purposes_count * (purposes_count - 1)
        actual_interfaces = test_result.get('total_integration_interfaces', 0)
        
        if actual_interfaces < expected_interfaces:
            reasons.append(f'Insufficient integration interfaces: {actual_interfaces} < {expected_interfaces}')
        
        return reasons
    
    def _identify_balance_failures(self, test_result: dict) -> list:
        """Identify balance verification failures"""
        reasons = []
        
        if test_result.get('balance_status') != 'BALANCED':
            reasons.append(f"Balance status: {test_result.get('balance_status')}")
        
        if not test_result.get('balance_threshold_met', False):
            reasons.append(f"Balance score below threshold: {test_result.get('balance_score', 0)}")
        
        if not test_result.get('variance_acceptable', False):
            reasons.append(f"Score variance too high: {test_result.get('score_variance', 0)}")
        
        if not test_result.get('equal_capabilities', False):
            reasons.append('Equal capabilities verification failed')
        
        return reasons
    
    def _generate_test_summary(self) -> dict:
        """Generate overall test summary"""
        total_tests = len([k for k in self.test_results.keys() if k.startswith('test_')])
        passed_tests = len([r for r in self.test_results.values() 
                           if isinstance(r, dict) and r.get('status') == 'PASSED'])
        failed_tests = len([r for r in self.test_results.values() 
                           if isinstance(r, dict) and r.get('status') == 'FAILED'])
        error_tests = len([r for r in self.test_results.values() 
                          if isinstance(r, dict) and r.get('status') == 'ERROR'])
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'error_tests': error_tests,
            'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'overall_status': 'PASSED' if passed_tests == total_tests else 'FAILED',
            'critical_balance_tests': {
                'causal_balance_verified': self.test_results.get('test_4', {}).get('balance_verified', False),
                'overall_balance_verified': self.test_results.get('test_8', {}).get('balance_verified', False)
            },
            'balance_requirement_met': (
                self.test_results.get('test_4', {}).get('balance_verified', False) and
                self.test_results.get('test_8', {}).get('balance_verified', False)
            )
        }

def main():
    """Run comprehensive schema generation tests"""
    print("=== Multi-Purpose Schema Generation Test Suite ===")
    print("Testing balanced schema generation across all theoretical purposes...")
    
    tester = SchemaGenerationTester()
    results = tester.run_all_tests()
    
    # Print summary
    summary = results['overall_summary']
    print(f"\n=== TEST RESULTS SUMMARY ===")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Errors: {summary['error_tests']}")
    print(f"Pass Rate: {summary['pass_rate']:.1f}%")
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Balance Requirement Met: {summary['balance_requirement_met']}")
    
    # Print individual test results
    print(f"\n=== INDIVIDUAL TEST RESULTS ===")
    for test_key, test_result in results.items():
        if test_key.startswith('test_') and isinstance(test_result, dict):
            test_name = test_result.get('test_name', test_key)
            status = test_result.get('status', 'UNKNOWN')
            print(f"{test_name}: {status}")
            
            if status == 'FAILED' and 'failure_reasons' in test_result:
                for reason in test_result['failure_reasons']:
                    print(f"  - {reason}")
            elif status == 'ERROR':
                print(f"  - Error: {test_result.get('error', 'Unknown error')}")
    
    return results

if __name__ == "__main__":
    results = main()
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed test results saved to: test_results.json")