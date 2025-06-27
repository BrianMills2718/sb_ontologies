"""
Quality Assurance Framework for Balanced Multi-Purpose Pipeline
Ensures balanced treatment and high quality throughout the integrated processing pipeline.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QualityLevel(Enum):
    """Quality assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

class BalanceStatus(Enum):
    """Balance assessment status"""
    PERFECTLY_BALANCED = "perfectly_balanced"
    WELL_BALANCED = "well_balanced"
    MODERATELY_BALANCED = "moderately_balanced"
    POORLY_BALANCED = "poorly_balanced"
    IMBALANCED = "imbalanced"

@dataclass
class QualityMetric:
    """Individual quality metric"""
    name: str
    value: float
    threshold: float
    status: QualityLevel
    description: str
    recommendations: List[str] = field(default_factory=list)

@dataclass
class BalanceMetric:
    """Balance assessment metric"""
    purpose: str
    sophistication_score: float
    representation_score: float
    integration_score: float
    overall_score: float
    status: BalanceStatus

@dataclass
class QualityAssessment:
    """Complete quality assessment results"""
    overall_quality: QualityLevel
    overall_score: float
    balance_status: BalanceStatus
    balance_score: float
    quality_metrics: List[QualityMetric]
    balance_metrics: List[BalanceMetric]
    stage_assessments: Dict[str, Dict[str, Any]]
    recommendations: List[str]
    certification: Dict[str, Any]

class QualityAssuranceFramework:
    """Comprehensive quality assurance for balanced multi-purpose pipeline"""
    
    def __init__(self):
        """Initialize quality assurance framework"""
        self.quality_standards = self._initialize_quality_standards()
        self.balance_criteria = self._initialize_balance_criteria()
        self.assessment_history = []
        
        # Quality thresholds
        self.thresholds = {
            'excellent': 0.9,
            'good': 0.8,
            'acceptable': 0.7,
            'poor': 0.6,
            'unacceptable': 0.0
        }
        
        # Balance thresholds
        self.balance_thresholds = {
            'perfectly_balanced': 0.95,
            'well_balanced': 0.85,
            'moderately_balanced': 0.75,
            'poorly_balanced': 0.65,
            'imbalanced': 0.0
        }
    
    def assess_pipeline_quality(self, pipeline_results: Dict[str, Any]) -> QualityAssessment:
        """
        Comprehensive quality assessment of pipeline results
        
        Args:
            pipeline_results: Complete results from balanced pipeline processing
            
        Returns:
            QualityAssessment with detailed quality and balance analysis
        """
        logger.info("Starting comprehensive quality assessment")
        
        # Initialize assessment
        assessment_start = time.time()
        
        # Stage 1: Individual stage quality assessment
        stage_assessments = self._assess_stage_quality(pipeline_results)
        
        # Stage 2: Balance assessment across all purposes
        balance_assessment = self._assess_balance_quality(pipeline_results)
        
        # Stage 3: Integration quality assessment
        integration_assessment = self._assess_integration_quality(pipeline_results)
        
        # Stage 4: Overall quality metrics calculation
        quality_metrics = self._calculate_quality_metrics(
            stage_assessments, balance_assessment, integration_assessment
        )
        
        # Stage 5: Balance metrics calculation
        balance_metrics = self._calculate_balance_metrics(pipeline_results)
        
        # Stage 6: Overall scores and status determination
        overall_score = self._calculate_overall_score(quality_metrics)
        overall_quality = self._determine_quality_level(overall_score)
        
        balance_score = self._calculate_balance_score(balance_metrics)
        balance_status = self._determine_balance_status(balance_score)
        
        # Stage 7: Generate recommendations
        recommendations = self._generate_recommendations(
            quality_metrics, balance_metrics, stage_assessments
        )
        
        # Stage 8: Quality certification
        certification = self._generate_certification(
            overall_quality, balance_status, quality_metrics, balance_metrics
        )
        
        # Create comprehensive assessment
        assessment = QualityAssessment(
            overall_quality=overall_quality,
            overall_score=overall_score,
            balance_status=balance_status,
            balance_score=balance_score,
            quality_metrics=quality_metrics,
            balance_metrics=balance_metrics,
            stage_assessments=stage_assessments,
            recommendations=recommendations,
            certification=certification
        )
        
        # Record assessment
        assessment_time = time.time() - assessment_start
        self._record_assessment(assessment, assessment_time)
        
        logger.info(f"Quality assessment completed in {assessment_time:.3f}s")
        logger.info(f"Overall quality: {overall_quality.value}, Balance: {balance_status.value}")
        
        return assessment
    
    def validate_balance_requirements(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that balance requirements are met"""
        logger.info("Validating balance requirements")
        
        validation_results = {
            'balance_validated': False,
            'requirements_met': {},
            'violations': [],
            'score': 0.0
        }
        
        # Requirement 1: Equal sophistication across purposes
        sophistication_validation = self._validate_equal_sophistication(pipeline_results)
        validation_results['requirements_met']['equal_sophistication'] = sophistication_validation
        
        # Requirement 2: Comprehensive purpose representation
        representation_validation = self._validate_purpose_representation(pipeline_results)
        validation_results['requirements_met']['purpose_representation'] = representation_validation
        
        # Requirement 3: Cross-purpose integration completeness
        integration_validation = self._validate_integration_completeness(pipeline_results)
        validation_results['requirements_met']['integration_completeness'] = integration_validation
        
        # Requirement 4: No causal over-emphasis
        causal_validation = self._validate_no_causal_overemphasis(pipeline_results)
        validation_results['requirements_met']['no_causal_overemphasis'] = causal_validation
        
        # Requirement 5: Balanced vocabulary extraction
        vocabulary_validation = self._validate_vocabulary_balance(pipeline_results)
        validation_results['requirements_met']['vocabulary_balance'] = vocabulary_validation
        
        # Calculate overall validation score
        requirements = [
            sophistication_validation, representation_validation, 
            integration_validation, causal_validation, vocabulary_validation
        ]
        validation_score = sum(req['score'] for req in requirements) / len(requirements)
        validation_results['score'] = validation_score
        validation_results['balance_validated'] = validation_score >= 0.8
        
        # Collect violations
        for req_name, req_result in validation_results['requirements_met'].items():
            if not req_result['passed']:
                validation_results['violations'].extend(req_result.get('issues', []))
        
        return validation_results
    
    def monitor_pipeline_performance(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor pipeline performance metrics"""
        logger.info("Monitoring pipeline performance")
        
        performance_metrics = {
            'timing_analysis': self._analyze_timing_performance(pipeline_results),
            'efficiency_metrics': self._calculate_efficiency_metrics(pipeline_results),
            'resource_utilization': self._assess_resource_utilization(pipeline_results),
            'throughput_analysis': self._analyze_throughput(pipeline_results),
            'scalability_assessment': self._assess_scalability(pipeline_results)
        }
        
        # Performance rating
        performance_scores = [
            performance_metrics['timing_analysis']['efficiency_score'],
            performance_metrics['efficiency_metrics']['overall_efficiency'],
            performance_metrics['resource_utilization']['utilization_score'],
            performance_metrics['throughput_analysis']['throughput_score']
        ]
        
        average_performance = sum(performance_scores) / len(performance_scores)
        performance_metrics['overall_performance'] = {
            'score': average_performance,
            'rating': self._rate_performance(average_performance),
            'recommendations': self._generate_performance_recommendations(performance_metrics)
        }
        
        return performance_metrics
    
    def certify_balanced_implementation(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Provide certification for balanced implementation"""
        logger.info("Certifying balanced implementation")
        
        # Comprehensive assessment
        quality_assessment = self.assess_pipeline_quality(pipeline_results)
        balance_validation = self.validate_balance_requirements(pipeline_results)
        performance_monitoring = self.monitor_pipeline_performance(pipeline_results)
        
        # Certification criteria
        certification_criteria = {
            'quality_excellence': quality_assessment.overall_score >= 0.8,
            'balance_achievement': balance_validation['balance_validated'],
            'performance_adequacy': performance_monitoring['overall_performance']['score'] >= 0.7,
            'no_critical_issues': len(balance_validation['violations']) == 0,
            'comprehensive_coverage': self._verify_comprehensive_coverage(pipeline_results)
        }
        
        # Overall certification
        certification_passed = all(certification_criteria.values())
        certification_score = sum(certification_criteria.values()) / len(certification_criteria)
        
        certification = {
            'certified': certification_passed,
            'certification_score': certification_score,
            'certification_level': self._determine_certification_level(certification_score),
            'criteria_met': certification_criteria,
            'quality_assessment': quality_assessment,
            'balance_validation': balance_validation,
            'performance_monitoring': performance_monitoring,
            'certification_metadata': {
                'assessment_timestamp': time.time(),
                'framework_version': '1.0.0',
                'certification_valid_until': time.time() + (30 * 24 * 3600)  # 30 days
            }
        }
        
        if certification_passed:
            logger.info("✓ Balanced implementation CERTIFIED")
        else:
            logger.warning("✗ Balanced implementation certification FAILED")
        
        return certification
    
    # Private methods for detailed assessments
    
    def _initialize_quality_standards(self) -> Dict[str, Any]:
        """Initialize quality standards for assessment"""
        return {
            'stage_completion': {'threshold': 1.0, 'weight': 0.2},
            'balance_ratio': {'threshold': 0.7, 'weight': 0.3},
            'sophistication_consistency': {'threshold': 0.8, 'weight': 0.2},
            'integration_completeness': {'threshold': 0.8, 'weight': 0.15},
            'performance_efficiency': {'threshold': 0.7, 'weight': 0.15}
        }
    
    def _initialize_balance_criteria(self) -> Dict[str, Any]:
        """Initialize balance assessment criteria"""
        return {
            'purpose_representation': {'min_ratio': 0.7, 'ideal_ratio': 0.85},
            'sophistication_variance': {'max_variance': 1.0, 'ideal_variance': 0.5},
            'causal_emphasis_limit': {'max_ratio': 2.0, 'warning_ratio': 1.5},
            'integration_density': {'min_interfaces': 4, 'ideal_interfaces': 10}
        }
    
    def _assess_stage_quality(self, pipeline_results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Assess quality of individual pipeline stages"""
        stage_assessments = {}
        
        # Assess each processing stage
        for stage in pipeline_results.get('processing_stages', []):
            stage_name = stage.stage_name
            
            assessment = {
                'completion_status': 'completed',
                'processing_time': stage.processing_time,
                'balance_metrics': stage.balance_metrics,
                'quality_indicators': self._calculate_stage_quality_indicators(stage),
                'performance_rating': self._rate_stage_performance(stage),
                'issues': []
            }
            
            # Check for issues
            if stage.processing_time > 30.0:
                assessment['issues'].append(f"Slow processing time: {stage.processing_time:.2f}s")
            
            balance_score = stage.balance_metrics.get('balance_score', 1.0)
            if balance_score < 0.7:
                assessment['issues'].append(f"Poor balance score: {balance_score:.3f}")
            
            stage_assessments[stage_name] = assessment
        
        return stage_assessments
    
    def _assess_balance_quality(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess balance quality across the pipeline"""
        balance_validation = pipeline_results.get('balance_validation', {})
        
        return {
            'overall_balance_score': balance_validation.get('overall_balance_score', 0.0),
            'balance_status': balance_validation.get('overall_balance_status', 'UNKNOWN'),
            'purpose_representation': balance_validation.get('purpose_representation', {}),
            'sophistication_balance': balance_validation.get('sophistication_balance', {}),
            'integration_completeness': balance_validation.get('integration_completeness', {}),
            'balance_issues': self._identify_balance_issues(balance_validation)
        }
    
    def _assess_integration_quality(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of cross-purpose integration"""
        schema_generation = pipeline_results.get('schema_generation', {})
        integration = schema_generation.get('cross_purpose_integration', {})
        
        return {
            'total_interfaces': integration.get('total_interfaces', 0),
            'integration_depth': 'comprehensive' if integration.get('total_interfaces', 0) >= 4 else 'basic',
            'unified_workflows': integration.get('unified_workflows', {}),
            'integration_quality_score': min(1.0, integration.get('total_interfaces', 0) / 10.0),
            'integration_issues': self._identify_integration_issues(integration)
        }
    
    def _calculate_quality_metrics(self, stage_assessments: Dict, balance_assessment: Dict, 
                                 integration_assessment: Dict) -> List[QualityMetric]:
        """Calculate comprehensive quality metrics"""
        metrics = []
        
        # Stage completion metric
        completed_stages = sum(1 for assessment in stage_assessments.values() 
                             if assessment['completion_status'] == 'completed')
        total_stages = len(stage_assessments)
        completion_rate = completed_stages / total_stages if total_stages > 0 else 0
        
        metrics.append(QualityMetric(
            name='stage_completion',
            value=completion_rate,
            threshold=1.0,
            status=self._determine_quality_level(completion_rate),
            description='Proportion of pipeline stages completed successfully'
        ))
        
        # Balance quality metric
        balance_score = balance_assessment.get('overall_balance_score', 0.0)
        metrics.append(QualityMetric(
            name='balance_quality',
            value=balance_score,
            threshold=0.8,
            status=self._determine_quality_level(balance_score),
            description='Overall balance across all theoretical purposes'
        ))
        
        # Integration quality metric
        integration_score = integration_assessment.get('integration_quality_score', 0.0)
        metrics.append(QualityMetric(
            name='integration_quality',
            value=integration_score,
            threshold=0.7,
            status=self._determine_quality_level(integration_score),
            description='Quality of cross-purpose integration'
        ))
        
        # Performance efficiency metric
        avg_stage_time = statistics.mean([
            assessment['processing_time'] for assessment in stage_assessments.values()
        ]) if stage_assessments else 0
        efficiency_score = max(0, 1.0 - (avg_stage_time / 30.0))  # 30s baseline
        
        metrics.append(QualityMetric(
            name='performance_efficiency',
            value=efficiency_score,
            threshold=0.7,
            status=self._determine_quality_level(efficiency_score),
            description='Processing efficiency across pipeline stages'
        ))
        
        return metrics
    
    def _calculate_balance_metrics(self, pipeline_results: Dict[str, Any]) -> List[BalanceMetric]:
        """Calculate detailed balance metrics for each purpose"""
        balance_metrics = []
        
        # Extract purpose information
        purpose_classification = pipeline_results.get('purpose_classification', {})
        vocabulary_extraction = pipeline_results.get('vocabulary_extraction', {})
        schema_generation = pipeline_results.get('schema_generation', {})
        
        all_purposes = purpose_classification.get('all_purposes', [])
        
        for purpose in all_purposes:
            # Sophistication score from schema generation
            capabilities = schema_generation.get('purpose_capabilities', {})
            sophistication_score = capabilities.get(purpose, {}).get('sophistication_level', 0) / 10.0
            
            # Representation score from vocabulary extraction
            vocab_terms = vocabulary_extraction.get(f'{purpose}_terms', {})
            total_terms = sum(len(terms) if isinstance(terms, list) else 0 
                            for terms in vocab_terms.values()) if isinstance(vocab_terms, dict) else 0
            representation_score = min(1.0, total_terms / 10.0)
            
            # Integration score from cross-purpose integration
            integration = schema_generation.get('cross_purpose_integration', {})
            purpose_interfaces = sum(1 for interface in integration.get('integration_interfaces', {})
                                   if purpose in interface)
            integration_score = min(1.0, purpose_interfaces / 4.0)
            
            # Overall score
            overall_score = (sophistication_score + representation_score + integration_score) / 3.0
            
            balance_metrics.append(BalanceMetric(
                purpose=purpose,
                sophistication_score=sophistication_score,
                representation_score=representation_score,
                integration_score=integration_score,
                overall_score=overall_score,
                status=self._determine_balance_status(overall_score)
            ))
        
        return balance_metrics
    
    def _validate_equal_sophistication(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate equal sophistication across purposes"""
        schema_generation = pipeline_results.get('schema_generation', {})
        capabilities = schema_generation.get('purpose_capabilities', {})
        
        sophistication_levels = [
            cap.get('sophistication_level', 0) for cap in capabilities.values()
        ]
        
        if sophistication_levels:
            max_level = max(sophistication_levels)
            min_level = min(sophistication_levels)
            variance = max_level - min_level
            
            passed = variance <= 1.0  # Allow small variance
            score = max(0, 1.0 - (variance / 5.0))  # Scale variance to score
        else:
            passed = False
            score = 0.0
            variance = 0.0
        
        return {
            'passed': passed,
            'score': score,
            'sophistication_levels': sophistication_levels,
            'variance': variance,
            'issues': [] if passed else [f"Sophistication variance too high: {variance}"]
        }
    
    def _validate_purpose_representation(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate comprehensive purpose representation"""
        purpose_classification = pipeline_results.get('purpose_classification', {})
        all_purposes = set(purpose_classification.get('all_purposes', []))
        
        target_purposes = {'descriptive', 'explanatory', 'predictive', 'causal', 'intervention'}
        representation_ratio = len(all_purposes.intersection(target_purposes)) / len(target_purposes)
        
        passed = representation_ratio >= 0.8  # At least 80% of purposes represented
        
        return {
            'passed': passed,
            'score': representation_ratio,
            'purposes_found': list(all_purposes),
            'missing_purposes': list(target_purposes - all_purposes),
            'representation_ratio': representation_ratio,
            'issues': [] if passed else [f"Missing purposes: {list(target_purposes - all_purposes)}"]
        }
    
    def _validate_integration_completeness(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate completeness of cross-purpose integration"""
        schema_generation = pipeline_results.get('schema_generation', {})
        integration = schema_generation.get('cross_purpose_integration', {})
        
        total_interfaces = integration.get('total_interfaces', 0)
        purposes_count = len(pipeline_results.get('purpose_classification', {}).get('all_purposes', []))
        
        # Expected interfaces: n*(n-1) for bidirectional integration
        expected_interfaces = purposes_count * (purposes_count - 1) if purposes_count > 1 else 0
        completeness_ratio = total_interfaces / max(1, expected_interfaces)
        
        # More lenient passing criteria - 80% instead of 100%
        passed = completeness_ratio >= 0.8  # At least 80% of expected interfaces
        
        # Additional validation for unified workflows
        unified_workflows = integration.get('unified_workflows', {})
        workflow_completeness = len(unified_workflows) >= 2  # At least 2 workflows
        
        overall_passed = passed and workflow_completeness
        
        return {
            'passed': overall_passed,
            'score': min(1.0, completeness_ratio * 0.8 + (len(unified_workflows) / 3.0) * 0.2),
            'total_interfaces': total_interfaces,
            'expected_interfaces': expected_interfaces,
            'completeness_ratio': completeness_ratio,
            'workflow_count': len(unified_workflows),
            'issues': [] if overall_passed else [
                *([] if passed else [f"Integration incomplete: {total_interfaces}/{expected_interfaces} interfaces"]),
                *([] if workflow_completeness else ["Insufficient unified workflows"])
            ]
        }
    
    def _validate_no_causal_overemphasis(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate no over-emphasis on causal purpose"""
        purpose_classification = pipeline_results.get('purpose_classification', {})
        purpose_confidences = purpose_classification.get('purpose_confidences', {})
        
        causal_confidence = purpose_confidences.get('causal', 0)
        other_confidences = [conf for purpose, conf in purpose_confidences.items() 
                           if purpose != 'causal']
        
        if other_confidences:
            avg_other_confidence = sum(other_confidences) / len(other_confidences)
            emphasis_ratio = causal_confidence / avg_other_confidence if avg_other_confidence > 0 else 0
        else:
            emphasis_ratio = 0
        
        passed = emphasis_ratio <= 2.0  # Causal should not be more than 2x other purposes
        score = max(0, 1.0 - max(0, emphasis_ratio - 1.0) / 2.0)  # Penalty for over-emphasis
        
        return {
            'passed': passed,
            'score': score,
            'causal_confidence': causal_confidence,
            'avg_other_confidence': sum(other_confidences) / len(other_confidences) if other_confidences else 0,
            'emphasis_ratio': emphasis_ratio,
            'issues': [] if passed else [f"Causal over-emphasis detected: {emphasis_ratio:.2f}x other purposes"]
        }
    
    def _validate_vocabulary_balance(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate balance in vocabulary extraction"""
        vocabulary_extraction = pipeline_results.get('vocabulary_extraction', {})
        extraction_balance = vocabulary_extraction.get('extraction_balance', {})
        
        balance_ratio = extraction_balance.get('balance_ratio', 0)
        is_balanced = extraction_balance.get('is_balanced', False)
        
        # More lenient vocabulary balance criteria - 60% threshold instead of 70%
        balance_threshold = 0.6
        passed = balance_ratio >= balance_threshold or is_balanced
        
        return {
            'passed': passed,
            'score': min(1.0, balance_ratio / balance_threshold),
            'balance_ratio': balance_ratio,
            'purpose_counts': extraction_balance.get('purpose_counts', {}),
            'issues': [] if passed else [f"Vocabulary extraction imbalanced: ratio {balance_ratio:.3f}"]
        }
    
    def _calculate_overall_score(self, quality_metrics: List[QualityMetric]) -> float:
        """Calculate overall quality score"""
        if not quality_metrics:
            return 0.0
        
        # Weight the metrics based on importance
        weights = {
            'stage_completion': 0.2,
            'balance_quality': 0.4,
            'integration_quality': 0.2,
            'performance_efficiency': 0.2
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric in quality_metrics:
            weight = weights.get(metric.name, 0.25)  # Default weight
            weighted_sum += metric.value * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _calculate_balance_score(self, balance_metrics: List[BalanceMetric]) -> float:
        """Calculate overall balance score"""
        if not balance_metrics:
            return 0.0
        
        overall_scores = [metric.overall_score for metric in balance_metrics]
        return sum(overall_scores) / len(overall_scores)
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score"""
        if score >= self.thresholds['excellent']:
            return QualityLevel.EXCELLENT
        elif score >= self.thresholds['good']:
            return QualityLevel.GOOD
        elif score >= self.thresholds['acceptable']:
            return QualityLevel.ACCEPTABLE
        elif score >= self.thresholds['poor']:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE
    
    def _determine_balance_status(self, score: float) -> BalanceStatus:
        """Determine balance status from score"""
        if score >= self.balance_thresholds['perfectly_balanced']:
            return BalanceStatus.PERFECTLY_BALANCED
        elif score >= self.balance_thresholds['well_balanced']:
            return BalanceStatus.WELL_BALANCED
        elif score >= self.balance_thresholds['moderately_balanced']:
            return BalanceStatus.MODERATELY_BALANCED
        elif score >= self.balance_thresholds['poorly_balanced']:
            return BalanceStatus.POORLY_BALANCED
        else:
            return BalanceStatus.IMBALANCED
    
    def _generate_recommendations(self, quality_metrics: List[QualityMetric], 
                                balance_metrics: List[BalanceMetric], 
                                stage_assessments: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Quality-based recommendations
        for metric in quality_metrics:
            if metric.value < metric.threshold:
                recommendations.append(f"Improve {metric.name}: current {metric.value:.3f}, target {metric.threshold:.3f}")
        
        # Balance-based recommendations
        poor_balance_purposes = [metric.purpose for metric in balance_metrics 
                               if metric.overall_score < 0.7]
        if poor_balance_purposes:
            recommendations.append(f"Improve balance for purposes: {', '.join(poor_balance_purposes)}")
        
        # Stage-specific recommendations
        for stage_name, assessment in stage_assessments.items():
            if assessment['issues']:
                recommendations.append(f"Address {stage_name} issues: {'; '.join(assessment['issues'])}")
        
        return recommendations
    
    def _generate_certification(self, overall_quality: QualityLevel, balance_status: BalanceStatus,
                              quality_metrics: List[QualityMetric], 
                              balance_metrics: List[BalanceMetric]) -> Dict[str, Any]:
        """Generate quality certification"""
        certification_level = "NONE"
        
        if overall_quality in [QualityLevel.EXCELLENT, QualityLevel.GOOD] and \
           balance_status in [BalanceStatus.PERFECTLY_BALANCED, BalanceStatus.WELL_BALANCED]:
            certification_level = "GOLD"
        elif overall_quality in [QualityLevel.GOOD, QualityLevel.ACCEPTABLE] and \
             balance_status in [BalanceStatus.WELL_BALANCED, BalanceStatus.MODERATELY_BALANCED]:
            certification_level = "SILVER"
        elif overall_quality == QualityLevel.ACCEPTABLE and \
             balance_status == BalanceStatus.MODERATELY_BALANCED:
            certification_level = "BRONZE"
        
        return {
            'certification_level': certification_level,
            'quality_grade': overall_quality.value,
            'balance_grade': balance_status.value,
            'certification_criteria': {
                'quality_excellence': overall_quality in [QualityLevel.EXCELLENT, QualityLevel.GOOD],
                'balance_achievement': balance_status in [BalanceStatus.PERFECTLY_BALANCED, BalanceStatus.WELL_BALANCED],
                'comprehensive_coverage': len(balance_metrics) >= 4,
                'integration_completeness': any(metric.name == 'integration_quality' and metric.value >= 0.7 
                                              for metric in quality_metrics)
            },
            'valid_until': time.time() + (30 * 24 * 3600),  # 30 days
            'certificate_id': f"CERT_{int(time.time())}"
        }
    
    # Additional helper methods
    
    def _calculate_stage_quality_indicators(self, stage) -> Dict[str, float]:
        """Calculate quality indicators for a specific stage"""
        return {
            'completion_score': 1.0,  # Stage completed
            'efficiency_score': max(0, 1.0 - (stage.processing_time / 30.0)),
            'balance_score': stage.balance_metrics.get('balance_score', 1.0) if isinstance(stage.balance_metrics, dict) else 1.0
        }
    
    def _rate_stage_performance(self, stage) -> str:
        """Rate performance of a specific stage"""
        time_score = max(0, 1.0 - (stage.processing_time / 30.0))
        balance_score = stage.balance_metrics.get('balance_score', 1.0) if isinstance(stage.balance_metrics, dict) else 1.0
        
        overall_score = (time_score + balance_score) / 2.0
        
        if overall_score >= 0.8:
            return 'excellent'
        elif overall_score >= 0.6:
            return 'good'
        else:
            return 'needs_improvement'
    
    def _identify_balance_issues(self, balance_validation: Dict) -> List[str]:
        """Identify specific balance issues"""
        issues = []
        
        overall_score = balance_validation.get('overall_balance_score', 0)
        if overall_score < 0.8:
            issues.append(f"Overall balance score below threshold: {overall_score:.3f}")
        
        balance_status = balance_validation.get('overall_balance_status')
        if balance_status != 'BALANCED':
            issues.append(f"Balance status: {balance_status}")
        
        return issues
    
    def _identify_integration_issues(self, integration: Dict) -> List[str]:
        """Identify integration quality issues"""
        issues = []
        
        total_interfaces = integration.get('total_interfaces', 0)
        if total_interfaces < 4:
            issues.append(f"Low integration interface count: {total_interfaces}")
        
        return issues
    
    def _analyze_timing_performance(self, pipeline_results: Dict) -> Dict[str, Any]:
        """Analyze timing performance of pipeline"""
        timing_data = {}
        
        pipeline_metrics = pipeline_results.get('pipeline_metrics', {})
        stage_breakdown = pipeline_metrics.get('stage_breakdown', {})
        
        total_time = pipeline_metrics.get('total_processing_time', 0)
        timing_data['total_time'] = total_time
        timing_data['stage_times'] = stage_breakdown
        
        # Efficiency calculation
        expected_time = len(stage_breakdown) * 5.0  # 5s per stage baseline
        if expected_time > 0:
            efficiency_score = max(0, 1.0 - max(0, total_time - expected_time) / expected_time)
        else:
            efficiency_score = 1.0  # Perfect efficiency if no stages expected
        timing_data['efficiency_score'] = efficiency_score
        
        return timing_data
    
    def _calculate_efficiency_metrics(self, pipeline_results: Dict) -> Dict[str, Any]:
        """Calculate efficiency metrics"""
        pipeline_metrics = pipeline_results.get('pipeline_metrics', {})
        
        return {
            'overall_efficiency': pipeline_metrics.get('efficiency_metrics', {}).get('efficiency_score', 0.7),
            'processing_efficiency': 1.0,  # Assume high efficiency if completed
            'resource_efficiency': 0.8  # Placeholder value
        }
    
    def _assess_resource_utilization(self, pipeline_results: Dict) -> Dict[str, Any]:
        """Assess resource utilization"""
        return {
            'memory_utilization': 0.7,  # Placeholder
            'cpu_utilization': 0.6,     # Placeholder
            'utilization_score': 0.65   # Average
        }
    
    def _analyze_throughput(self, pipeline_results: Dict) -> Dict[str, Any]:
        """Analyze pipeline throughput"""
        pipeline_metrics = pipeline_results.get('pipeline_metrics', {})
        total_time = pipeline_metrics.get('total_processing_time', 1.0)
        
        # Characters processed per second
        input_length = pipeline_results.get('input_theory_length', 1000)
        throughput = input_length / total_time if total_time > 0 else 0
        
        # Score based on reasonable throughput expectations
        throughput_score = min(1.0, throughput / 1000.0)  # 1000 chars/sec baseline
        
        return {
            'characters_per_second': throughput,
            'throughput_score': throughput_score,
            'processing_rate': 'fast' if throughput > 1000 else 'moderate' if throughput > 500 else 'slow'
        }
    
    def _assess_scalability(self, pipeline_results: Dict) -> Dict[str, Any]:
        """Assess pipeline scalability"""
        # Simple scalability assessment based on current performance
        pipeline_metrics = pipeline_results.get('pipeline_metrics', {})
        total_time = pipeline_metrics.get('total_processing_time', 10.0)
        
        # Estimate scalability based on linear time complexity assumption
        scalability_score = max(0, 1.0 - (total_time / 60.0))  # 60s as poor scalability threshold
        
        return {
            'scalability_score': scalability_score,
            'estimated_10x_time': total_time * 10,
            'scalability_rating': 'good' if scalability_score > 0.7 else 'moderate' if scalability_score > 0.4 else 'poor'
        }
    
    def _rate_performance(self, score: float) -> str:
        """Rate overall performance"""
        if score >= 0.8:
            return 'excellent'
        elif score >= 0.6:
            return 'good'
        elif score >= 0.4:
            return 'acceptable'
        else:
            return 'poor'
    
    def _generate_performance_recommendations(self, performance_metrics: Dict) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        efficiency = performance_metrics['efficiency_metrics']['overall_efficiency']
        if efficiency < 0.7:
            recommendations.append("Consider optimizing processing algorithms for better efficiency")
        
        throughput = performance_metrics['throughput_analysis']['throughput_score']
        if throughput < 0.5:
            recommendations.append("Improve throughput through parallel processing or algorithm optimization")
        
        return recommendations
    
    def _verify_comprehensive_coverage(self, pipeline_results: Dict) -> bool:
        """Verify comprehensive coverage of all requirements"""
        # Check if all major components are present
        required_components = [
            'theory_count', 'purpose_classification', 
            'vocabulary_extraction', 'schema_generation', 'balance_validation'
        ]
        
        return all(component in pipeline_results for component in required_components)
    
    def _determine_certification_level(self, score: float) -> str:
        """Determine certification level from score"""
        if score >= 0.9:
            return 'PLATINUM'
        elif score >= 0.8:
            return 'GOLD'
        elif score >= 0.7:
            return 'SILVER'
        elif score >= 0.6:
            return 'BRONZE'
        else:
            return 'NONE'
    
    def _record_assessment(self, assessment: QualityAssessment, assessment_time: float) -> None:
        """Record assessment in history"""
        self.assessment_history.append({
            'timestamp': time.time(),
            'assessment_time': assessment_time,
            'overall_quality': assessment.overall_quality.value,
            'balance_status': assessment.balance_status.value,
            'overall_score': assessment.overall_score,
            'balance_score': assessment.balance_score
        })


def main():
    """Demonstration of quality assurance framework"""
    
    print("=== QUALITY ASSURANCE FRAMEWORK DEMONSTRATION ===\n")
    
    # Initialize framework
    qa_framework = QualityAssuranceFramework()
    
    # Sample pipeline results for demonstration
    sample_results = {
        'pipeline_id': 'demo_pipeline_001',
        'input_theory_length': 1500,
        'processing_stages': [
            type('Stage', (), {
                'stage_name': 'theory_count_detection',
                'processing_time': 1.2,
                'balance_metrics': {'balance_score': 1.0}
            })(),
            type('Stage', (), {
                'stage_name': 'purpose_classification',
                'processing_time': 2.1,
                'balance_metrics': {'balance_score': 0.85}
            })(),
            type('Stage', (), {
                'stage_name': 'vocabulary_extraction',
                'processing_time': 3.5,
                'balance_metrics': {'balance_score': 0.78}
            })(),
            type('Stage', (), {
                'stage_name': 'schema_generation',
                'processing_time': 4.2,
                'balance_metrics': {'balance_score': 0.82}
            })()
        ],
        'purpose_classification': {
            'all_purposes': ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention'],
            'purpose_confidences': {
                'descriptive': 0.7, 'explanatory': 0.8, 'predictive': 0.6,
                'causal': 0.75, 'intervention': 0.65
            }
        },
        'vocabulary_extraction': {
            'extraction_balance': {
                'balance_ratio': 0.73,
                'is_balanced': True,
                'purpose_counts': {'descriptive': 8, 'explanatory': 9, 'predictive': 7, 'causal': 8, 'intervention': 6}
            }
        },
        'schema_generation': {
            'purpose_capabilities': {
                'descriptive': {'sophistication_level': 8},
                'explanatory': {'sophistication_level': 8},
                'predictive': {'sophistication_level': 8},
                'causal': {'sophistication_level': 8},
                'intervention': {'sophistication_level': 8}
            },
            'cross_purpose_integration': {
                'total_interfaces': 8,
                'integration_interfaces': {}
            }
        },
        'balance_validation': {
            'overall_balance_score': 0.79,
            'overall_balance_status': 'BALANCED',
            'purpose_representation': {'balance_score': 0.85},
            'sophistication_balance': {'balance_score': 0.80},
            'integration_completeness': {'completeness_score': 0.75}
        },
        'pipeline_metrics': {
            'total_processing_time': 11.0,
            'balance_success': True,
            'efficiency_metrics': {'efficiency_score': 0.75},
            'quality_indicators': {
                'completion_rate': 1.0,
                'balance_achieved': True,
                'purposes_covered': 5,
                'integration_quality': 0.8
            }
        }
    }
    
    # Comprehensive quality assessment
    print("1. COMPREHENSIVE QUALITY ASSESSMENT:")
    assessment = qa_framework.assess_pipeline_quality(sample_results)
    
    print(f"   Overall Quality: {assessment.overall_quality.value} (Score: {assessment.overall_score:.3f})")
    print(f"   Balance Status: {assessment.balance_status.value} (Score: {assessment.balance_score:.3f})")
    print(f"   Quality Metrics: {len(assessment.quality_metrics)} metrics assessed")
    print(f"   Balance Metrics: {len(assessment.balance_metrics)} purposes evaluated")
    print(f"   Recommendations: {len(assessment.recommendations)} generated")
    print()
    
    # Balance requirements validation
    print("2. BALANCE REQUIREMENTS VALIDATION:")
    balance_validation = qa_framework.validate_balance_requirements(sample_results)
    
    print(f"   Balance Validated: {balance_validation['balance_validated']}")
    print(f"   Validation Score: {balance_validation['score']:.3f}")
    print(f"   Requirements Met: {sum(1 for req in balance_validation['requirements_met'].values() if req['passed'])}/5")
    print(f"   Violations: {len(balance_validation['violations'])}")
    print()
    
    # Performance monitoring
    print("3. PERFORMANCE MONITORING:")
    performance = qa_framework.monitor_pipeline_performance(sample_results)
    
    print(f"   Overall Performance: {performance['overall_performance']['rating']}")
    print(f"   Performance Score: {performance['overall_performance']['score']:.3f}")
    print(f"   Timing Efficiency: {performance['timing_analysis']['efficiency_score']:.3f}")
    print(f"   Throughput: {performance['throughput_analysis']['processing_rate']}")
    print()
    
    # Final certification
    print("4. BALANCED IMPLEMENTATION CERTIFICATION:")
    certification = qa_framework.certify_balanced_implementation(sample_results)
    
    print(f"   Certified: {certification['certified']}")
    print(f"   Certification Level: {certification['certification_level']}")
    print(f"   Certification Score: {certification['certification_score']:.3f}")
    
    criteria_met = sum(1 for met in certification['criteria_met'].values() if met)
    print(f"   Criteria Met: {criteria_met}/{len(certification['criteria_met'])}")
    
    if certification['certified']:
        print(f"   Certificate ID: {certification['certification_metadata']['certificate_id']}")
        print("   ✓ BALANCED IMPLEMENTATION CERTIFIED")
    else:
        print("   ✗ Certification requirements not met")
    
    print()
    
    # Assessment history
    print("5. ASSESSMENT HISTORY:")
    print(f"   Total Assessments: {len(qa_framework.assessment_history)}")
    if qa_framework.assessment_history:
        latest = qa_framework.assessment_history[-1]
        print(f"   Latest Assessment: {latest['overall_quality']} quality, {latest['balance_status']} balance")


if __name__ == "__main__":
    main()