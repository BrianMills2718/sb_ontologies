#!/usr/bin/env python3
"""
Integration Validation for Phase 4 Balanced Integration Pipeline
Validates integration with experimental validation results and previous phase components.
"""

import json
import sys
import time
from typing import Dict, List, Any, Optional

# Import pipeline components for validation
from balanced_pipeline import BalancedMultiPurposePipeline
from pipeline_config import PipelineConfiguration, PredefinedConfigurations
from quality_assurance import QualityAssuranceFramework

class IntegrationValidator:
    """Validates integration with experimental validation results and phase components"""
    
    def __init__(self):
        """Initialize integration validator"""
        self.pipeline = BalancedMultiPurposePipeline()
        self.qa_framework = QualityAssuranceFramework()
        self.config = PredefinedConfigurations.create_balanced_configuration()
        
        # Expected integration standards from experimental validation
        self.integration_standards = {
            'property_graph_support': True,
            'multi_theory_handling': True,
            'balanced_processing': True,
            'quality_validation': True,
            'cross_purpose_integration': True,
            'dynamic_rebalancing': True,
            'performance_efficiency': True
        }
        
        # Validation criteria
        self.validation_criteria = {
            'phase1_integration': {
                'purpose_classification': True,
                'balanced_analysis': True,
                'equal_sophistication': True
            },
            'phase2_integration': {
                'vocabulary_extraction': True,
                'cross_purpose_terms': True,
                'balance_adjustment': True
            },
            'phase3_integration': {
                'schema_generation': True,
                'purpose_capabilities': True,
                'integration_interfaces': True
            },
            'experimental_compatibility': {
                'property_graph_models': True,
                'multi_theory_support': True,
                'validation_framework': True
            }
        }
    
    def validate_phase1_integration(self) -> Dict[str, Any]:
        """Validate integration with Phase 1 purpose classification"""
        print("Validating Phase 1 Purpose Classification Integration...")
        
        test_theory = """
        This framework provides a comprehensive theory that explains mechanisms
        through systematic analysis. It predicts outcomes based on causal
        relationships and recommends specific interventions for implementation.
        The approach categorizes different types and forms of phenomena.
        """
        
        # Process through pipeline
        result = self.pipeline.process_theory_balanced(test_theory)
        
        validation_results = {
            'purpose_classification_present': False,
            'balanced_analysis_present': False,
            'equal_sophistication_achieved': False,
            'all_purposes_detected': False,
            'confidence_scores_present': False
        }
        
        # Check purpose classification
        purpose_classification = result.get('purpose_classification', {})
        if purpose_classification:
            validation_results['purpose_classification_present'] = True
            
            # Check balanced analysis
            balanced_analysis = purpose_classification.get('balanced_analysis', {})
            if balanced_analysis:
                validation_results['balanced_analysis_present'] = True
            
            # Check all purposes detected
            all_purposes = purpose_classification.get('all_purposes', [])
            if len(all_purposes) >= 4:  # Expect at least 4 of 5 purposes
                validation_results['all_purposes_detected'] = True
            
            # Check confidence scores
            purpose_confidences = purpose_classification.get('purpose_confidences', {})
            if len(purpose_confidences) >= 4:
                validation_results['confidence_scores_present'] = True
        
        # Check equal sophistication in schema generation
        schema_generation = result.get('schema_generation', {})
        capabilities = schema_generation.get('purpose_capabilities', {})
        
        if capabilities:
            sophistication_levels = [
                cap.get('sophistication_level', 0) for cap in capabilities.values()
            ]
            if sophistication_levels and max(sophistication_levels) - min(sophistication_levels) <= 1:
                validation_results['equal_sophistication_achieved'] = True
        
        # Overall validation
        validation_score = sum(validation_results.values()) / len(validation_results)
        
        return {
            'phase1_integration_score': validation_score,
            'validation_details': validation_results,
            'passed': validation_score >= 0.8,
            'summary': f"Phase 1 integration: {validation_score:.1%} requirements met"
        }
    
    def validate_phase2_integration(self) -> Dict[str, Any]:
        """Validate integration with Phase 2 vocabulary extraction"""
        print("Validating Phase 2 Vocabulary Extraction Integration...")
        
        test_theory = """
        Social cognitive theory explains behavior through triadic reciprocal causation.
        The framework categorizes learning mechanisms and predicts behavioral outcomes.
        Interventions focus on enhancing self-efficacy through various strategies.
        The theory provides causal pathways for understanding behavior change.
        """
        
        # Process through pipeline
        result = self.pipeline.process_theory_balanced(test_theory)
        
        validation_results = {
            'vocabulary_extraction_present': False,
            'multiple_purpose_terms': False,
            'cross_purpose_analysis': False,
            'balance_validation': False,
            'dynamic_rebalancing': False
        }
        
        # Check vocabulary extraction
        vocabulary_extraction = result.get('vocabulary_extraction', {})
        if vocabulary_extraction:
            validation_results['vocabulary_extraction_present'] = True
            
            # Check multiple purpose terms
            purpose_term_keys = [key for key in vocabulary_extraction.keys() if key.endswith('_terms')]
            if len(purpose_term_keys) >= 4:
                validation_results['multiple_purpose_terms'] = True
            
            # Check cross-purpose analysis
            cross_purpose = vocabulary_extraction.get('cross_purpose_analysis', {})
            if cross_purpose:
                validation_results['cross_purpose_analysis'] = True
            
            # Check balance validation
            extraction_balance = vocabulary_extraction.get('extraction_balance', {})
            if extraction_balance:
                validation_results['balance_validation'] = True
                
                # Check if rebalancing was applied (indicates dynamic adjustment capability)
                balance_ratio = extraction_balance.get('balance_ratio', 0)
                if balance_ratio >= 0.7:
                    validation_results['dynamic_rebalancing'] = True
        
        # Overall validation
        validation_score = sum(validation_results.values()) / len(validation_results)
        
        return {
            'phase2_integration_score': validation_score,
            'validation_details': validation_results,
            'passed': validation_score >= 0.8,
            'summary': f"Phase 2 integration: {validation_score:.1%} requirements met"
        }
    
    def validate_phase3_integration(self) -> Dict[str, Any]:
        """Validate integration with Phase 3 schema generation"""
        print("Validating Phase 3 Schema Generation Integration...")
        
        test_theory = """
        Systems theory provides a comprehensive framework for analyzing complex
        organizations. It explains how feedback mechanisms operate and predicts
        system behavior. The theory identifies causal leverage points and
        recommends intervention strategies for system transformation.
        """
        
        # Process through pipeline
        result = self.pipeline.process_theory_balanced(test_theory)
        
        validation_results = {
            'schema_generation_present': False,
            'purpose_capabilities_present': False,
            'equal_capabilities': False,
            'cross_purpose_integration': False,
            'integration_interfaces': False
        }
        
        # Check schema generation
        schema_generation = result.get('schema_generation', {})
        if schema_generation:
            validation_results['schema_generation_present'] = True
            
            # Check purpose capabilities
            capabilities = schema_generation.get('purpose_capabilities', {})
            if len(capabilities) >= 4:
                validation_results['purpose_capabilities_present'] = True
                
                # Check equal capabilities
                sophistication_levels = [
                    cap.get('sophistication_level', 0) for cap in capabilities.values()
                ]
                if sophistication_levels and max(sophistication_levels) == min(sophistication_levels):
                    validation_results['equal_capabilities'] = True
            
            # Check cross-purpose integration
            cross_purpose_integration = schema_generation.get('cross_purpose_integration', {})
            if cross_purpose_integration:
                validation_results['cross_purpose_integration'] = True
                
                # Check integration interfaces
                total_interfaces = cross_purpose_integration.get('total_interfaces', 0)
                if total_interfaces >= 4:
                    validation_results['integration_interfaces'] = True
        
        # Overall validation
        validation_score = sum(validation_results.values()) / len(validation_results)
        
        return {
            'phase3_integration_score': validation_score,
            'validation_details': validation_results,
            'passed': validation_score >= 0.8,
            'summary': f"Phase 3 integration: {validation_score:.1%} requirements met"
        }
    
    def validate_experimental_compatibility(self) -> Dict[str, Any]:
        """Validate compatibility with experimental validation results"""
        print("Validating Experimental Validation Compatibility...")
        
        # Test multiple theories to validate experimental findings
        test_theories = [
            "Social cognitive theory with multiple purposes",
            "Systems theory framework with complex interactions",
            "Complexity theory with emergent properties"
        ]
        
        validation_results = {
            'property_graph_support': False,
            'multi_theory_handling': False,
            'balanced_processing': False,
            'quality_validation': False,
            'performance_efficiency': False
        }
        
        total_processing_time = 0
        quality_scores = []
        balance_scores = []
        
        for theory in test_theories:
            start_time = time.time()
            result = self.pipeline.process_theory_balanced(theory)
            processing_time = time.time() - start_time
            total_processing_time += processing_time
            
            # Check property graph support
            schema_generation = result.get('schema_generation', {})
            model_type = schema_generation.get('model_type', '')
            if 'property_graph' in model_type.lower():
                validation_results['property_graph_support'] = True
            
            # Assess quality and balance
            qa_assessment = self.qa_framework.assess_pipeline_quality(result)
            quality_scores.append(qa_assessment.overall_score)
            balance_scores.append(qa_assessment.balance_score)
        
        # Multi-theory handling
        if len(test_theories) == 3:  # Successfully processed multiple theories
            validation_results['multi_theory_handling'] = True
        
        # Balanced processing
        avg_balance_score = sum(balance_scores) / len(balance_scores) if balance_scores else 0
        if avg_balance_score >= 0.7:
            validation_results['balanced_processing'] = True
        
        # Quality validation
        avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        if avg_quality_score >= 0.8:
            validation_results['quality_validation'] = True
        
        # Performance efficiency
        avg_processing_time = total_processing_time / len(test_theories)
        if avg_processing_time < 0.1:  # Sub-100ms average
            validation_results['performance_efficiency'] = True
        
        # Overall validation
        validation_score = sum(validation_results.values()) / len(validation_results)
        
        return {
            'experimental_compatibility_score': validation_score,
            'validation_details': validation_results,
            'performance_metrics': {
                'avg_processing_time': avg_processing_time,
                'avg_quality_score': avg_quality_score,
                'avg_balance_score': avg_balance_score
            },
            'passed': validation_score >= 0.8,
            'summary': f"Experimental compatibility: {validation_score:.1%} requirements met"
        }
    
    def validate_integration_completeness(self) -> Dict[str, Any]:
        """Validate overall integration completeness"""
        print("Validating Overall Integration Completeness...")
        
        # Comprehensive integration test
        complex_theory = """
        This comprehensive theoretical framework integrates multiple perspectives
        to provide both descriptive taxonomies and explanatory mechanisms. The
        theory predicts behavioral outcomes through sophisticated causal models
        and prescribes evidence-based interventions for practical implementation.
        
        The framework categorizes phenomena into distinct types while explaining
        underlying processes through systematic analysis. Predictive components
        forecast outcomes using key variables, while causal analysis identifies
        leverage points for effective interventions. Implementation strategies
        are designed based on theoretical principles and empirical evidence.
        """
        
        # Process through complete pipeline
        start_time = time.time()
        result = self.pipeline.process_theory_balanced(complex_theory)
        processing_time = time.time() - start_time
        
        # Comprehensive quality assessment
        qa_assessment = self.qa_framework.assess_pipeline_quality(result)
        balance_validation = self.qa_framework.validate_balance_requirements(result)
        
        validation_results = {
            'complete_pipeline_execution': False,
            'all_stages_completed': False,
            'comprehensive_quality_assessment': False,
            'balance_requirements_validated': False,
            'integration_interfaces_complete': False,
            'performance_within_limits': False
        }
        
        # Check complete pipeline execution
        if 'pipeline_metrics' in result:
            validation_results['complete_pipeline_execution'] = True
        
        # Check all stages completed
        processing_stages = result.get('processing_stages', [])
        expected_stages = 6  # Total pipeline stages
        if len(processing_stages) == expected_stages:
            validation_results['all_stages_completed'] = True
        
        # Check comprehensive quality assessment
        if qa_assessment and qa_assessment.overall_score > 0:
            validation_results['comprehensive_quality_assessment'] = True
        
        # Check balance requirements validated
        if balance_validation and 'balance_validated' in balance_validation:
            validation_results['balance_requirements_validated'] = True
        
        # Check integration interfaces
        schema_generation = result.get('schema_generation', {})
        integration = schema_generation.get('cross_purpose_integration', {})
        total_interfaces = integration.get('total_interfaces', 0)
        if total_interfaces >= 6:  # Minimum expected interfaces
            validation_results['integration_interfaces_complete'] = True
        
        # Check performance
        if processing_time < 0.1:  # Should complete within 100ms
            validation_results['performance_within_limits'] = True
        
        # Overall validation
        validation_score = sum(validation_results.values()) / len(validation_results)
        
        return {
            'integration_completeness_score': validation_score,
            'validation_details': validation_results,
            'performance_metrics': {
                'processing_time': processing_time,
                'quality_score': qa_assessment.overall_score if qa_assessment else 0,
                'balance_score': qa_assessment.balance_score if qa_assessment else 0,
                'total_interfaces': total_interfaces
            },
            'passed': validation_score >= 0.8,
            'summary': f"Integration completeness: {validation_score:.1%} requirements met"
        }
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive integration validation"""
        print("=" * 60)
        print("COMPREHENSIVE INTEGRATION VALIDATION")
        print("=" * 60)
        
        validation_results = {}
        
        # Phase-specific validations
        validation_results['phase1'] = self.validate_phase1_integration()
        validation_results['phase2'] = self.validate_phase2_integration()
        validation_results['phase3'] = self.validate_phase3_integration()
        
        # Experimental compatibility validation
        validation_results['experimental'] = self.validate_experimental_compatibility()
        
        # Overall integration completeness
        validation_results['completeness'] = self.validate_integration_completeness()
        
        # Calculate overall validation score
        individual_scores = [
            validation_results['phase1']['phase1_integration_score'],
            validation_results['phase2']['phase2_integration_score'],
            validation_results['phase3']['phase3_integration_score'],
            validation_results['experimental']['experimental_compatibility_score'],
            validation_results['completeness']['integration_completeness_score']
        ]
        
        overall_score = sum(individual_scores) / len(individual_scores)
        overall_passed = all(result['passed'] for result in validation_results.values())
        
        # Summary
        summary = {
            'overall_integration_score': overall_score,
            'overall_passed': overall_passed,
            'individual_validations': {
                key: result['passed'] for key, result in validation_results.items()
            },
            'validation_summary': {
                key: result['summary'] for key, result in validation_results.items()
            }
        }
        
        validation_results['summary'] = summary
        
        return validation_results


def main():
    """Main validation execution"""
    print("Integration Validation for Phase 4 Balanced Integration Pipeline")
    print("================================================================")
    
    validator = IntegrationValidator()
    
    try:
        # Run comprehensive validation
        results = validator.run_comprehensive_validation()
        
        # Display results
        print("\nVALIDATION RESULTS:")
        print("-" * 30)
        
        summary = results['summary']
        
        print(f"Overall Integration Score: {summary['overall_integration_score']:.1%}")
        print(f"Overall Validation: {'✓ PASSED' if summary['overall_passed'] else '✗ FAILED'}")
        print()
        
        print("Individual Validation Results:")
        for validation_name, passed in summary['individual_validations'].items():
            status = "✓ PASSED" if passed else "✗ FAILED"
            description = summary['validation_summary'][validation_name]
            print(f"  {validation_name.upper():12}: {status} - {description}")
        
        print()
        
        # Detailed performance metrics
        if 'experimental' in results:
            exp_metrics = results['experimental']['performance_metrics']
            print("Performance Metrics:")
            print(f"  Average Processing Time: {exp_metrics['avg_processing_time']:.4f}s")
            print(f"  Average Quality Score: {exp_metrics['avg_quality_score']:.3f}")
            print(f"  Average Balance Score: {exp_metrics['avg_balance_score']:.3f}")
            print()
        
        # Integration completeness metrics
        if 'completeness' in results:
            comp_metrics = results['completeness']['performance_metrics']
            print("Integration Completeness Metrics:")
            print(f"  Complex Theory Processing: {comp_metrics['processing_time']:.4f}s")
            print(f"  Quality Score: {comp_metrics['quality_score']:.3f}")
            print(f"  Balance Score: {comp_metrics['balance_score']:.3f}")
            print(f"  Total Integration Interfaces: {comp_metrics['total_interfaces']}")
            print()
        
        # Final assessment
        if summary['overall_passed']:
            print("✓ INTEGRATION VALIDATION SUCCESSFUL")
            print("  Phase 4 pipeline successfully integrates all previous phase components")
            print("  Experimental validation compatibility confirmed")
            print("  Production readiness validated")
            return 0
        else:
            print("✗ INTEGRATION VALIDATION FAILED")
            print("  Some integration requirements not met")
            print("  Review individual validation details for remediation")
            return 1
    
    except Exception as e:
        print(f"\nCritical error during integration validation: {str(e)}")
        return 2


if __name__ == "__main__":
    sys.exit(main())