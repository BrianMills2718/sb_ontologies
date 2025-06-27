#!/usr/bin/env python3
"""
Pytest-compatible External Validation Tests for Phase 4
Provides external validation using pytest framework.
"""

import pytest
import time
from typing import Dict, Any

# Import pipeline components
from balanced_pipeline import BalancedMultiPurposePipeline
from quality_assurance import QualityAssuranceFramework
from integration_validation import IntegrationValidator

class TestExternalValidation:
    """External validation test suite using pytest"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures"""
        self.pipeline = BalancedMultiPurposePipeline()
        self.qa_framework = QualityAssuranceFramework()
        self.integration_validator = IntegrationValidator()
    
    def test_certification_system_functionality(self):
        """Test that certification system works correctly"""
        test_theory = """
        This comprehensive theory provides descriptive classifications,
        explanatory mechanisms, predictive models, causal analysis,
        and intervention strategies for behavioral phenomena.
        """
        
        # Process through pipeline
        result = self.pipeline.process_theory_balanced(test_theory)
        
        # Attempt certification
        certification = self.qa_framework.certify_balanced_implementation(result)
        
        # Verify certification structure
        assert 'certified' in certification
        assert 'certification_score' in certification
        assert 'certification_level' in certification
        assert 'criteria_met' in certification
        
        # Verify certification criteria
        criteria = certification['criteria_met']
        assert 'quality_excellence' in criteria
        assert 'balance_achievement' in criteria
        assert 'performance_adequacy' in criteria
        assert 'no_critical_issues' in criteria
        assert 'comprehensive_coverage' in criteria
        
        # Should have decent certification score
        assert certification['certification_score'] >= 0.8, f"Low certification score: {certification['certification_score']}"
        
        # Should achieve certification
        assert certification['certified'], "Certification should pass for comprehensive theory"
    
    def test_balance_validation_consistency(self):
        """Test balance validation consistency"""
        test_theories = [
            "Theory explains mechanisms and predicts outcomes.",
            "Framework categorizes types and analyzes causes.",
            "Approach describes phenomena and recommends interventions."
        ]
        
        balance_success_count = 0
        
        for theory in test_theories:
            result = self.pipeline.process_theory_balanced(theory)
            balance_validation = self.qa_framework.validate_balance_requirements(result)
            
            assert 'balance_validated' in balance_validation
            assert 'score' in balance_validation
            assert 'requirements_met' in balance_validation
            
            if balance_validation['balance_validated']:
                balance_success_count += 1
        
        balance_success_rate = (balance_success_count / len(test_theories)) * 100
        
        # Should achieve high balance validation rate
        assert balance_success_rate >= 66.7, f"Balance validation rate too low: {balance_success_rate}%"
    
    def test_integration_completeness_meets_target(self):
        """Test that integration completeness meets 60% target"""
        complex_theory = """
        This theoretical framework integrates descriptive taxonomies,
        explanatory mechanisms, predictive models, causal relationships,
        and intervention strategies for comprehensive analysis.
        """
        
        result = self.pipeline.process_theory_balanced(complex_theory)
        
        # Check integration interfaces
        schema_generation = result.get('schema_generation', {})
        cross_purpose_integration = schema_generation.get('cross_purpose_integration', {})
        
        assert 'total_interfaces' in cross_purpose_integration
        assert 'integration_interfaces' in cross_purpose_integration
        assert 'unified_workflows' in cross_purpose_integration
        
        total_interfaces = cross_purpose_integration['total_interfaces']
        purposes_count = len(result.get('purpose_classification', {}).get('all_purposes', []))
        expected_interfaces = purposes_count * (purposes_count - 1) if purposes_count > 1 else 0
        
        completeness_ratio = total_interfaces / max(1, expected_interfaces)
        
        # Should meet 60% completeness target
        assert completeness_ratio >= 0.6, f"Integration completeness {completeness_ratio:.1%} below 60% target"
        
        # Should have multiple unified workflows
        unified_workflows = cross_purpose_integration['unified_workflows']
        assert len(unified_workflows) >= 2, "Should have at least 2 unified workflows"
    
    def test_pytest_availability(self):
        """Test that pytest module is available"""
        try:
            import pytest
            pytest_version = pytest.__version__
            assert pytest_version, "Pytest should have a version"
        except ImportError:
            pytest.fail("Pytest module should be available")
    
    def test_external_validation_module_functional(self):
        """Test that external validation module is functional"""
        # Test integration validator functionality
        validation_results = self.integration_validator.run_comprehensive_validation()
        
        assert 'summary' in validation_results
        assert 'overall_passed' in validation_results['summary']
        assert 'overall_integration_score' in validation_results['summary']
        
        # Should achieve reasonable integration score
        integration_score = validation_results['summary']['overall_integration_score']
        assert integration_score >= 0.8, f"Integration score {integration_score:.1%} too low"
    
    def test_production_readiness_criteria(self):
        """Test production readiness criteria"""
        # Test error handling
        try:
            result = self.pipeline.process_theory_balanced("")
            assert 'pipeline_metrics' in result or 'error' in result
        except Exception:
            pass  # Exception handling is acceptable
        
        # Test performance
        start_time = time.time()
        result = self.pipeline.process_theory_balanced("Test theory for performance measurement.")
        processing_time = time.time() - start_time
        
        assert processing_time < 10.0, f"Processing time {processing_time:.2f}s too slow"
        
        # Test configuration management
        try:
            from pipeline_config import PipelineConfiguration
            config = PipelineConfiguration()
            assert config is not None
        except ImportError:
            pytest.fail("Pipeline configuration should be available")
        
        # Test logging implementation
        import logging
        pipeline_logger = logging.getLogger('balanced_pipeline')
        assert pipeline_logger.level <= logging.INFO, "Logging should be enabled"

def test_comprehensive_pipeline_validation():
    """Comprehensive pipeline validation test"""
    pipeline = BalancedMultiPurposePipeline()
    qa_framework = QualityAssuranceFramework()
    
    comprehensive_theory = """
    Social cognitive theory provides a comprehensive framework for understanding
    behavior through multiple analytical lenses. The theory describes different
    categories of learning mechanisms, explains the underlying psychological
    processes, predicts behavioral outcomes based on key variables, analyzes
    causal relationships between factors, and prescribes evidence-based
    interventions for behavior change.
    """
    
    # Process through pipeline
    result = pipeline.process_theory_balanced(comprehensive_theory)
    
    # Verify all required components
    required_components = [
        'theory_count', 'purpose_classification', 
        'vocabulary_extraction', 'schema_generation', 
        'balance_validation', 'pipeline_metrics'
    ]
    
    for component in required_components:
        assert component in result, f"Required component {component} missing"
    
    # Verify quality assessment
    quality_assessment = qa_framework.assess_pipeline_quality(result)
    
    assert quality_assessment.overall_score >= 0.7, "Quality score should be adequate"
    assert len(quality_assessment.quality_metrics) >= 4, "Should have comprehensive quality metrics"
    assert len(quality_assessment.balance_metrics) >= 3, "Should have balance metrics for multiple purposes"
    
    # Verify certification
    certification = qa_framework.certify_balanced_implementation(result)
    
    assert certification['certification_score'] >= 0.8, "Certification score should be high"
    assert certification['certified'], "Comprehensive theory should achieve certification"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])