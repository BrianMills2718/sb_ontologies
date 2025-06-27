#!/usr/bin/env python3
"""
External Validation Script for Phase 4: Balanced Integration Pipeline
Replicates the external evaluation criteria that found specific failures.
"""

import sys
import time
import json
import traceback
from typing import Dict, Any, List

# Import pipeline components
from balanced_pipeline import BalancedMultiPurposePipeline
from quality_assurance import QualityAssuranceFramework
from integration_validation import IntegrationValidator

class ExternalValidator:
    """External validation that matches the evaluation criteria"""
    
    def __init__(self):
        self.pipeline = BalancedMultiPurposePipeline()
        self.qa_framework = QualityAssuranceFramework()
        self.integration_validator = IntegrationValidator()
        
        # Evaluation criteria that were found to fail
        self.evaluation_criteria = {
            'certification_system': {
                'target': 100,  # 100% certification rate expected
                'weight': 25
            },
            'balance_validation': {
                'target': 100,  # 100% balance validation success expected
                'weight': 20
            },
            'integration_completeness': {
                'target': 60,   # 60% minimum interface completeness
                'weight': 20
            },
            'external_validation': {
                'target': 100,  # pytest module should be available
                'weight': 15
            },
            'production_readiness': {
                'target': 90,   # 90% production readiness expected
                'weight': 20
            }
        }
    
    def validate_certification_system(self) -> Dict[str, Any]:
        """Validate certification system functionality"""
        print("Validating Certification System...")
        
        test_cases = [
            {
                'name': 'simple_theory',
                'text': 'This theory explains behavior through mechanisms and predicts outcomes.'
            },
            {
                'name': 'complex_theory', 
                'text': """
                Social cognitive theory provides a comprehensive framework that categorizes
                learning mechanisms, explains behavioral processes, predicts outcomes,
                analyzes causal relationships, and recommends intervention strategies.
                """
            },
            {
                'name': 'multi_purpose_theory',
                'text': """
                This theoretical framework serves multiple analytical purposes. It describes
                different types of phenomena through detailed classification systems. The
                theory explains underlying mechanisms and processes that drive behavior.
                It predicts future outcomes using key variables and indicators. Causal
                analysis reveals how factors influence results through specific pathways.
                Finally, it prescribes evidence-based interventions for implementation.
                """
            }
        ]
        
        certification_results = []
        certification_success_count = 0
        
        for test_case in test_cases:
            try:
                # Process through pipeline
                result = self.pipeline.process_theory_balanced(test_case['text'])
                
                # Attempt certification
                certification = self.qa_framework.certify_balanced_implementation(result)
                
                certified = certification.get('certified', False)
                certification_level = certification.get('certification_level', 'NONE')
                certification_score = certification.get('certification_score', 0.0)
                
                if certified and certification_level != 'NONE':
                    certification_success_count += 1
                
                certification_results.append({
                    'test_case': test_case['name'],
                    'certified': certified,
                    'certification_level': certification_level,
                    'certification_score': certification_score,
                    'criteria_met': certification.get('criteria_met', {})
                })
                
            except Exception as e:
                certification_results.append({
                    'test_case': test_case['name'],
                    'certified': False,
                    'error': str(e)
                })
        
        certification_rate = (certification_success_count / len(test_cases)) * 100
        
        return {
            'certification_rate': certification_rate,
            'target_rate': self.evaluation_criteria['certification_system']['target'],
            'passed': certification_rate >= self.evaluation_criteria['certification_system']['target'],
            'certification_results': certification_results,
            'issues': [] if certification_rate >= 100 else [
                f"Certification rate {certification_rate:.1f}% below target 100%"
            ]
        }
    
    def validate_balance_validation_consistency(self) -> Dict[str, Any]:
        """Validate balance validation consistency"""
        print("Validating Balance Validation Consistency...")
        
        test_theories = [
            "This framework categorizes phenomena and explains mechanisms.",
            "The theory predicts outcomes and analyzes causal relationships.",
            "This approach describes types and recommends interventions.",
        ]
        
        balance_validation_results = []
        balance_success_count = 0
        
        for i, theory in enumerate(test_theories):
            try:
                # Process theory
                result = self.pipeline.process_theory_balanced(theory)
                
                # Validate balance requirements
                balance_validation = self.qa_framework.validate_balance_requirements(result)
                
                balance_validated = balance_validation.get('balance_validated', False)
                balance_score = balance_validation.get('score', 0.0)
                
                if balance_validated and balance_score >= 0.8:
                    balance_success_count += 1
                
                balance_validation_results.append({
                    'theory_index': i + 1,
                    'balance_validated': balance_validated,
                    'balance_score': balance_score,
                    'requirements_met': balance_validation.get('requirements_met', {}),
                    'violations': balance_validation.get('violations', [])
                })
                
            except Exception as e:
                balance_validation_results.append({
                    'theory_index': i + 1,
                    'balance_validated': False,
                    'error': str(e)
                })
        
        balance_success_rate = (balance_success_count / len(test_theories)) * 100
        
        return {
            'balance_success_rate': balance_success_rate,
            'target_rate': self.evaluation_criteria['balance_validation']['target'],
            'passed': balance_success_rate >= self.evaluation_criteria['balance_validation']['target'],
            'balance_results': balance_validation_results,
            'issues': [] if balance_success_rate >= 100 else [
                f"Balance validation success rate {balance_success_rate:.1f}% below target 100%"
            ]
        }
    
    def validate_integration_completeness(self) -> Dict[str, Any]:
        """Validate integration completeness"""
        print("Validating Integration Completeness...")
        
        # Test comprehensive integration
        complex_theory = """
        This comprehensive theoretical framework integrates multiple analytical
        perspectives. It provides descriptive taxonomies for classification,
        explanatory mechanisms for understanding processes, predictive models
        for forecasting outcomes, causal analysis for understanding relationships,
        and intervention strategies for practical implementation.
        """
        
        try:
            # Process through pipeline
            result = self.pipeline.process_theory_balanced(complex_theory)
            
            # Check integration interfaces
            schema_generation = result.get('schema_generation', {})
            cross_purpose_integration = schema_generation.get('cross_purpose_integration', {})
            
            total_interfaces = cross_purpose_integration.get('total_interfaces', 0)
            purposes_count = len(result.get('purpose_classification', {}).get('all_purposes', []))
            
            # Calculate expected interfaces (bidirectional: n*(n-1))
            expected_interfaces = purposes_count * (purposes_count - 1) if purposes_count > 1 else 0
            
            interface_completeness = (total_interfaces / max(1, expected_interfaces)) * 100
            
            # Check unified workflows
            unified_workflows = cross_purpose_integration.get('unified_workflows', {})
            workflow_completeness = min(100, len(unified_workflows) * 33.33)  # 3 workflows = 100%
            
            # Overall integration completeness with proper weighting
            overall_completeness = min(100, interface_completeness * 0.7 + workflow_completeness * 0.3)
            
            target_completeness = self.evaluation_criteria['integration_completeness']['target']
            
            return {
                'interface_completeness': interface_completeness,
                'workflow_completeness': workflow_completeness,
                'overall_completeness': overall_completeness,
                'target_completeness': target_completeness,
                'passed': overall_completeness >= target_completeness,
                'total_interfaces': total_interfaces,
                'expected_interfaces': expected_interfaces,
                'unified_workflows': len(unified_workflows),
                'issues': [] if overall_completeness >= target_completeness else [
                    f"Integration completeness {overall_completeness:.1f}% below target {target_completeness}%"
                ]
            }
            
        except Exception as e:
            return {
                'interface_completeness': 0,
                'workflow_completeness': 0,
                'overall_completeness': 0,
                'target_completeness': self.evaluation_criteria['integration_completeness']['target'],
                'passed': False,
                'error': str(e),
                'issues': [f"Integration validation failed: {str(e)}"]
            }
    
    def validate_external_validation_availability(self) -> Dict[str, Any]:
        """Validate external validation module availability"""
        print("Validating External Validation Availability...")
        
        # Check for pytest availability
        pytest_available = False
        pytest_error = None
        
        try:
            import pytest
            pytest_available = True
        except ImportError as e:
            pytest_error = str(e)
        
        # Check for test module functionality
        test_module_functional = False
        test_module_error = None
        
        try:
            # Try to run integration validator
            validation_results = self.integration_validator.run_comprehensive_validation()
            test_module_functional = validation_results['summary']['overall_passed']
        except Exception as e:
            test_module_error = str(e)
        
        # Overall external validation availability
        external_validation_score = 0
        if pytest_available:
            external_validation_score += 50
        if test_module_functional:
            external_validation_score += 50
        
        target_score = self.evaluation_criteria['external_validation']['target']
        
        return {
            'external_validation_score': external_validation_score,
            'target_score': target_score,
            'passed': external_validation_score >= target_score,
            'pytest_available': pytest_available,
            'test_module_functional': test_module_functional,
            'issues': [
                *([] if pytest_available else ["Pytest module not available"]),
                *([] if test_module_functional else ["Test module not fully functional"]),
                *([] if external_validation_score >= target_score else [
                    f"External validation score {external_validation_score}% below target {target_score}%"
                ])
            ]
        }
    
    def validate_production_readiness(self) -> Dict[str, Any]:
        """Validate production readiness"""
        print("Validating Production Readiness...")
        
        readiness_checks = {
            'error_handling': False,
            'performance_acceptable': False,
            'documentation_complete': False,
            'configuration_management': False,
            'logging_implemented': False
        }
        
        try:
            # Test error handling
            try:
                result = self.pipeline.process_theory_balanced("")  # Empty input
                if 'error' not in result or result.get('pipeline_metrics', {}).get('total_processing_time', 0) > 0:
                    readiness_checks['error_handling'] = True
            except:
                pass  # Error handling may work through exceptions
            
            # Test performance
            start_time = time.time()
            result = self.pipeline.process_theory_balanced("Test theory for performance.")
            processing_time = time.time() - start_time
            
            if processing_time < 10.0:  # Should complete within 10 seconds
                readiness_checks['performance_acceptable'] = True
            
            # Check for configuration management
            try:
                from pipeline_config import PipelineConfiguration
                readiness_checks['configuration_management'] = True
            except:
                pass
            
            # Check for logging implementation
            import logging
            pipeline_logger = logging.getLogger('balanced_pipeline')
            if pipeline_logger.level <= logging.INFO:
                readiness_checks['logging_implemented'] = True
            
            # Check documentation (basic check for docstrings)
            if hasattr(self.pipeline.process_theory_balanced, '__doc__') and self.pipeline.process_theory_balanced.__doc__:
                readiness_checks['documentation_complete'] = True
                
        except Exception as e:
            pass
        
        readiness_score = (sum(readiness_checks.values()) / len(readiness_checks)) * 100
        target_score = self.evaluation_criteria['production_readiness']['target']
        
        return {
            'production_readiness_score': readiness_score,
            'target_score': target_score,
            'passed': readiness_score >= target_score,
            'readiness_checks': readiness_checks,
            'issues': [] if readiness_score >= target_score else [
                f"Production readiness {readiness_score:.1f}% below target {target_score}%"
            ]
        }
    
    def run_comprehensive_external_validation(self) -> Dict[str, Any]:
        """Run comprehensive external validation matching evaluation criteria"""
        print("=" * 70)
        print("EXTERNAL VALIDATION - MATCHING EVALUATION CRITERIA")
        print("=" * 70)
        
        validation_results = {}
        
        # Run all validation checks
        validation_results['certification_system'] = self.validate_certification_system()
        validation_results['balance_validation'] = self.validate_balance_validation_consistency()
        validation_results['integration_completeness'] = self.validate_integration_completeness()
        validation_results['external_validation'] = self.validate_external_validation_availability()
        validation_results['production_readiness'] = self.validate_production_readiness()
        
        # Calculate overall score
        total_score = 0
        total_weight = 0
        
        for criterion, result in validation_results.items():
            weight = self.evaluation_criteria[criterion]['weight']
            
            if criterion == 'certification_system':
                score = result['certification_rate']
            elif criterion == 'balance_validation':
                score = result['balance_success_rate']
            elif criterion == 'integration_completeness':
                score = result['overall_completeness']
            elif criterion == 'external_validation':
                score = result['external_validation_score']
            elif criterion == 'production_readiness':
                score = result['production_readiness_score']
            else:
                score = 0
            
            total_score += score * weight
            total_weight += weight
        
        overall_score = total_score / total_weight if total_weight > 0 else 0
        
        # Collect all issues
        all_issues = []
        for result in validation_results.values():
            all_issues.extend(result.get('issues', []))
        
        # Determine pass/fail (100/100 score or all criteria passed)
        all_criteria_passed = all(result['passed'] for result in validation_results.values())
        overall_passed = overall_score >= 100.0 or all_criteria_passed
        
        summary = {
            'overall_score': overall_score,
            'target_score': 100,
            'overall_passed': overall_passed,
            'criteria_results': {
                criterion: result['passed'] for criterion, result in validation_results.items()
            },
            'all_issues': all_issues,
            'validation_details': validation_results
        }
        
        return summary


def main():
    """Main external validation execution"""
    print("External Validation for Phase 4: Balanced Integration Pipeline")
    print("Replicating evaluation criteria that identified failures")
    print("=" * 70)
    
    validator = ExternalValidator()
    
    try:
        # Run comprehensive validation
        results = validator.run_comprehensive_external_validation()
        
        # Display results
        print("\nEXTERNAL VALIDATION RESULTS:")
        print("-" * 40)
        
        print(f"Overall Score: {results['overall_score']:.1f}/100")
        print(f"Overall Result: {'PASS' if results['overall_passed'] else 'FAIL'}")
        print()
        
        print("Criterion Results:")
        for criterion, passed in results['criteria_results'].items():
            status = "PASS" if passed else "FAIL"
            print(f"  {criterion.upper().replace('_', ' '):25}: {status}")
        
        print()
        
        # Detailed scores
        details = results['validation_details']
        print("Detailed Scores:")
        print(f"  Certification System:       {details['certification_system']['certification_rate']:.1f}%")
        print(f"  Balance Validation:          {details['balance_validation']['balance_success_rate']:.1f}%")
        print(f"  Integration Completeness:    {details['integration_completeness']['overall_completeness']:.1f}%")
        print(f"  External Validation:         {details['external_validation']['external_validation_score']:.1f}%")
        print(f"  Production Readiness:        {details['production_readiness']['production_readiness_score']:.1f}%")
        print()
        
        # Issues
        if results['all_issues']:
            print("IDENTIFIED ISSUES:")
            for i, issue in enumerate(results['all_issues'], 1):
                print(f"  {i}. {issue}")
            print()
        
        # Final assessment
        if results['overall_passed']:
            print("✓ EXTERNAL VALIDATION PASSED")
            print("  All evaluation criteria met")
            return 0
        else:
            print("✗ EXTERNAL VALIDATION FAILED")
            print("  Critical issues identified that prevent 100/100 score")
            print("  Remediation required")
            return 1
    
    except Exception as e:
        print(f"\nCritical error during external validation: {str(e)}")
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())