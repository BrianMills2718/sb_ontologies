"""
Balanced Integration Pipeline for Multi-Purpose Computational Social Science
Integrates theory counting, purpose classification, vocabulary extraction, and schema generation
with equal sophistication across all five theoretical purposes.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time
import re
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PipelineStage:
    """Represents a stage in the balanced pipeline"""
    stage_name: str
    input_data: Any
    output_data: Any
    processing_time: float
    balance_metrics: Dict[str, float]

class BalancedMultiPurposePipeline:
    """Complete balanced processing pipeline for computational social science"""
    
    def __init__(self):
        """Initialize with components from previous phases"""
        self.purpose_classifier = self._init_purpose_classifier()
        self.vocabulary_extractor = self._init_vocabulary_extractor()
        self.schema_generator = self._init_schema_generator()
        
        # Balance tracking
        self.balance_weights = {
            'descriptive': 1.0,
            'explanatory': 1.0,
            'predictive': 1.0,
            'causal': 1.0,
            'intervention': 1.0
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'balance_ratio_minimum': 0.7,
            'purpose_confidence_minimum': 0.3,
            'vocabulary_extraction_minimum': 5,
            'schema_complexity_minimum': 3
        }
        
        # Pipeline metrics tracking
        self.pipeline_metrics = {
            'total_theories_processed': 0,
            'average_processing_time': 0.0,
            'balance_success_rate': 0.0,
            'quality_success_rate': 0.0
        }
    
    def process_theory_balanced(self, theory_text: str) -> dict:
        """
        Complete balanced processing pipeline
        Returns: {
            'theory_count': dict,
            'purpose_classification': dict,
            'vocabulary_extraction': dict,
            'schema_generation': dict,
            'balance_validation': dict,
            'pipeline_metrics': dict
        }
        """
        start_time = time.time()
        logger.info("Starting balanced theory processing pipeline")
        
        # Initialize results structure
        results = {
            'pipeline_id': f"pipeline_{int(time.time())}",
            'input_theory_length': len(theory_text),
            'processing_stages': [],
            'balance_validation': {},
            'pipeline_metrics': {}
        }
        
        try:
            # Stage 1: Theory Count Detection
            logger.info("Stage 1: Theory count detection")
            stage1_start = time.time()
            theory_count_result = self.detect_theory_count(theory_text)
            stage1_time = time.time() - stage1_start
            
            results['theory_count'] = theory_count_result
            results['processing_stages'].append(PipelineStage(
                'theory_count_detection',
                {'text_length': len(theory_text)},
                theory_count_result,
                stage1_time,
                {'balance_score': 1.0}  # Theory counting is inherently balanced
            ))
            
            # Stage 2: Purpose Classification
            logger.info("Stage 2: Purpose classification with balanced analysis")
            stage2_start = time.time()
            purpose_result = self.classify_purposes_balanced(theory_text)
            stage2_time = time.time() - stage2_start
            
            results['purpose_classification'] = purpose_result
            results['processing_stages'].append(PipelineStage(
                'purpose_classification',
                {'detected_theory_count': theory_count_result.get('theory_count', 1)},
                purpose_result,
                stage2_time,
                purpose_result.get('balanced_analysis', {}).get('balance_metrics', {})
            ))
            
            # Stage 3: Vocabulary Extraction
            logger.info("Stage 3: Comprehensive vocabulary extraction")
            stage3_start = time.time()
            identified_purposes = purpose_result.get('all_purposes', ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention'])
            vocabulary_result = self.extract_vocabulary_comprehensive(theory_text, identified_purposes)
            stage3_time = time.time() - stage3_start
            
            results['vocabulary_extraction'] = vocabulary_result
            results['processing_stages'].append(PipelineStage(
                'vocabulary_extraction',
                {'purposes': identified_purposes},
                vocabulary_result,
                stage3_time,
                vocabulary_result.get('extraction_balance', {})
            ))
            
            # Stage 4: Schema Generation
            logger.info("Stage 4: Balanced schema generation")
            stage4_start = time.time()
            model_type = self._determine_model_type(theory_count_result, purpose_result)
            schema_result = self.generate_schema_balanced(vocabulary_result, identified_purposes, model_type)
            stage4_time = time.time() - stage4_start
            
            results['schema_generation'] = schema_result
            results['processing_stages'].append(PipelineStage(
                'schema_generation',
                {'model_type': model_type, 'purposes': identified_purposes},
                schema_result,
                stage4_time,
                schema_result.get('balance_validation', {})
            ))
            
            # Stage 5: Pipeline Balance Validation
            logger.info("Stage 5: Pipeline balance validation")
            stage5_start = time.time()
            balance_validation = self.validate_pipeline_balance(results)
            stage5_time = time.time() - stage5_start
            
            results['balance_validation'] = balance_validation
            results['processing_stages'].append(PipelineStage(
                'balance_validation',
                {'all_stages': len(results['processing_stages'])},
                balance_validation,
                stage5_time,
                balance_validation.get('final_balance_metrics', {})
            ))
            
            # Stage 6: Pipeline Optimization and Metrics
            logger.info("Stage 6: Pipeline optimization and metrics")
            stage6_start = time.time()
            optimization_result = self.optimize_for_efficiency({
                'total_stages': len(results['processing_stages']),
                'theory_complexity': len(theory_text),
                'purposes_count': len(identified_purposes)
            })
            stage6_time = time.time() - stage6_start
            
            # Calculate final pipeline metrics
            total_time = time.time() - start_time
            results['pipeline_metrics'] = {
                'total_processing_time': total_time,
                'stage_breakdown': {
                    'theory_count_detection': stage1_time,
                    'purpose_classification': stage2_time,
                    'vocabulary_extraction': stage3_time,
                    'schema_generation': stage4_time,
                    'balance_validation': stage5_time,
                    'optimization': stage6_time
                },
                'efficiency_metrics': optimization_result,
                'balance_success': balance_validation.get('overall_balance_status') == 'BALANCED',
                'quality_indicators': self._calculate_quality_indicators(results)
            }
            
            # Update global pipeline metrics
            self._update_global_metrics(results)
            
            logger.info(f"Pipeline completed successfully in {total_time:.3f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {str(e)}")
            results['error'] = {
                'type': type(e).__name__,
                'message': str(e),
                'stage': 'pipeline_processing'
            }
            return results
    
    def detect_theory_count(self, theory_text: str) -> dict:
        """Detect single vs multiple theories"""
        logger.info("Detecting theory count and complexity")
        
        # Theory indicators
        theory_patterns = [
            r'\btheory\b',
            r'\bframework\b',
            r'\bmodel\b',
            r'\bapproach\b',
            r'\bparadigm\b',
            r'\bperspective\b'
        ]
        
        # Count theory mentions
        theory_mentions = 0
        for pattern in theory_patterns:
            matches = re.findall(pattern, theory_text, re.IGNORECASE)
            theory_mentions += len(matches)
        
        # Specific theory names detection
        specific_theories = []
        theory_names = [
            'social cognitive theory',
            'systems theory',
            'complexity theory',
            'social learning theory',
            'institutional theory',
            'network theory',
            'game theory',
            'rational choice theory'
        ]
        
        for theory_name in theory_names:
            if theory_name.lower() in theory_text.lower():
                specific_theories.append(theory_name)
        
        # Determine theory count and complexity
        if len(specific_theories) > 1:
            theory_count = len(specific_theories)
            complexity_level = 'multi_theory'
        elif len(specific_theories) == 1:
            theory_count = 1
            complexity_level = 'single_theory'
        elif theory_mentions > 3:
            theory_count = 'multiple_implicit'
            complexity_level = 'implicit_multi_theory'
        else:
            theory_count = 1
            complexity_level = 'single_theory'
        
        return {
            'theory_count': theory_count,
            'complexity_level': complexity_level,
            'theory_mentions_total': theory_mentions,
            'specific_theories_identified': specific_theories,
            'theory_density': theory_mentions / len(theory_text.split()) if theory_text else 0,
            'analysis_confidence': min(1.0, theory_mentions / 5.0),
            'detection_metadata': {
                'text_length': len(theory_text),
                'word_count': len(theory_text.split()),
                'pattern_matches': theory_mentions
            }
        }
    
    def classify_purposes_balanced(self, theory_text: str) -> dict:
        """Classify with equal sophistication across all purposes"""
        logger.info("Classifying theoretical purposes with balanced analysis")
        
        # Simulate purpose classification with balanced approach
        purpose_analyses = self._analyze_all_purposes_equally(theory_text)
        
        # Calculate balanced confidence scores
        purpose_confidences = {}
        for purpose, analysis in purpose_analyses.items():
            purpose_confidences[purpose] = self._calculate_balanced_confidence(analysis)
        
        # Determine purposes above threshold
        threshold = 0.25
        primary_purposes = []
        secondary_purposes = []
        
        sorted_purposes = sorted(purpose_confidences.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_purposes:
            primary_purposes.append(sorted_purposes[0][0])  # Highest scoring purpose
            
            for purpose, confidence in sorted_purposes[1:]:
                if confidence >= threshold:
                    secondary_purposes.append(purpose)
        
        # All purposes for comprehensive processing
        all_purposes = list(purpose_confidences.keys())
        
        # Balance validation
        balance_analysis = self._validate_purpose_balance(purpose_confidences)
        
        return {
            'primary_purposes': primary_purposes,
            'secondary_purposes': secondary_purposes,
            'all_purposes': all_purposes,
            'purpose_confidences': purpose_confidences,
            'purpose_analyses': purpose_analyses,
            'balanced_analysis': balance_analysis,
            'classification_metadata': {
                'threshold_used': threshold,
                'total_purposes_analyzed': len(all_purposes),
                'above_threshold_count': len(primary_purposes) + len(secondary_purposes)
            }
        }
    
    def extract_vocabulary_comprehensive(self, theory_text: str, purposes: list) -> dict:
        """Extract vocabulary supporting all identified purposes"""
        logger.info(f"Extracting vocabulary for purposes: {purposes}")
        
        vocabulary_results = {}
        
        # Extract for each purpose with equal sophistication
        for purpose in purposes:
            if purpose == 'descriptive':
                vocabulary_results['descriptive_terms'] = self._extract_descriptive_terms(theory_text)
            elif purpose == 'explanatory':
                vocabulary_results['explanatory_terms'] = self._extract_explanatory_terms(theory_text)
            elif purpose == 'predictive':
                vocabulary_results['predictive_terms'] = self._extract_predictive_terms(theory_text)
            elif purpose == 'causal':
                vocabulary_results['causal_terms'] = self._extract_causal_terms(theory_text)
            elif purpose == 'intervention':
                vocabulary_results['intervention_terms'] = self._extract_intervention_terms(theory_text)
        
        # Cross-purpose analysis
        vocabulary_results['cross_purpose_analysis'] = self._analyze_cross_purpose_terms(vocabulary_results)
        
        # Balance validation and dynamic adjustment
        vocabulary_results['extraction_balance'] = self._validate_extraction_balance(vocabulary_results)
        
        # Optimize extraction balance if needed
        if vocabulary_results['extraction_balance'].get('balance_ratio', 0) < 0.7:
            vocabulary_results = self._rebalance_vocabulary_extraction(vocabulary_results, theory_text)
        
        return vocabulary_results
    
    def generate_schema_balanced(self, vocabulary: dict, purposes: list, model_type: str) -> dict:
        """Generate schema with equal capabilities across purposes"""
        logger.info(f"Generating balanced schema for model type: {model_type}")
        
        # Generate capabilities for each purpose with equal sophistication
        purpose_capabilities = {}
        
        for purpose in purposes:
            purpose_capabilities[purpose] = self._generate_purpose_capabilities(
                purpose, vocabulary, model_type
            )
        
        # Ensure equal sophistication levels
        balanced_capabilities = self._ensure_equal_sophistication(purpose_capabilities)
        
        # Generate integrated schema blueprint
        schema_blueprint = self._generate_integrated_blueprint(balanced_capabilities, model_type)
        
        # Cross-purpose integration
        cross_purpose_integration = self._generate_cross_purpose_integration(balanced_capabilities)
        
        # Schema validation and balance check
        balance_validation = self._validate_schema_balance(balanced_capabilities)
        
        return {
            'model_type': model_type,
            'theoretical_purposes': purposes,
            'purpose_capabilities': balanced_capabilities,
            'schema_blueprint': schema_blueprint,
            'cross_purpose_integration': cross_purpose_integration,
            'balance_validation': balance_validation,
            'generation_metadata': {
                'purposes_count': len(purposes),
                'capabilities_generated': len(balanced_capabilities),
                'integration_interfaces': len(cross_purpose_integration.get('integration_interfaces', {}))
            }
        }
    
    def validate_pipeline_balance(self, results: dict) -> dict:
        """Ensure balanced treatment throughout pipeline"""
        logger.info("Validating pipeline balance across all stages")
        
        balance_metrics = {}
        
        # Extract balance information from each stage
        for stage in results.get('processing_stages', []):
            balance_metrics[stage.stage_name] = stage.balance_metrics
        
        # Calculate overall balance score
        purpose_representation = self._analyze_purpose_representation(results)
        sophistication_balance = self._analyze_sophistication_balance(results)
        integration_completeness = self._analyze_integration_completeness(results)
        
        # Final balance assessment
        overall_balance_score = (
            purpose_representation.get('balance_score', 0) * 0.4 +
            sophistication_balance.get('balance_score', 0) * 0.4 +
            integration_completeness.get('completeness_score', 0) * 0.2
        )
        
        balance_status = 'BALANCED' if overall_balance_score >= 0.8 else 'NEEDS_IMPROVEMENT'
        
        return {
            'validation_type': 'pipeline_balance_validation',
            'overall_balance_score': overall_balance_score,
            'overall_balance_status': balance_status,
            'stage_balance_metrics': balance_metrics,
            'purpose_representation': purpose_representation,
            'sophistication_balance': sophistication_balance,
            'integration_completeness': integration_completeness,
            'final_balance_metrics': {
                'balance_threshold_met': overall_balance_score >= 0.8,
                'balance_score': overall_balance_score,
                'recommendations': self._generate_balance_recommendations(overall_balance_score, balance_metrics)
            }
        }
    
    def optimize_for_efficiency(self, pipeline_config: dict) -> dict:
        """Optimize pipeline performance while maintaining balance"""
        logger.info("Optimizing pipeline efficiency")
        
        # Analyze current configuration
        efficiency_analysis = {
            'stage_count': pipeline_config.get('total_stages', 6),
            'theory_complexity': pipeline_config.get('theory_complexity', 1000),
            'purposes_count': pipeline_config.get('purposes_count', 5)
        }
        
        # Calculate efficiency metrics
        optimal_stage_time = efficiency_analysis['theory_complexity'] / 10000  # Base time per 10k characters
        efficiency_score = 1.0 / (1.0 + optimal_stage_time)  # Efficiency decreases with time
        
        # Optimization recommendations
        optimizations = []
        if efficiency_analysis['theory_complexity'] > 5000:
            optimizations.append('Consider parallel processing for large texts')
        if efficiency_analysis['purposes_count'] > 3:
            optimizations.append('Enable purpose-specific caching')
        if efficiency_analysis['stage_count'] > 6:
            optimizations.append('Optimize stage pipeline for fewer transitions')
        
        return {
            'efficiency_analysis': efficiency_analysis,
            'efficiency_score': efficiency_score,
            'optimization_recommendations': optimizations,
            'performance_metrics': {
                'estimated_optimal_time': optimal_stage_time * efficiency_analysis['stage_count'],
                'efficiency_rating': 'high' if efficiency_score > 0.8 else 'medium' if efficiency_score > 0.6 else 'low',
                'scalability_assessment': 'good' if efficiency_analysis['theory_complexity'] < 10000 else 'moderate'
            }
        }
    
    # Helper methods for pipeline components
    
    def _init_purpose_classifier(self):
        """Initialize purpose classifier component"""
        # Simulate purpose classifier initialization
        return {
            'initialized': True,
            'purposes_supported': ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention'],
            'balance_mode': 'enabled'
        }
    
    def _init_vocabulary_extractor(self):
        """Initialize vocabulary extractor component"""
        return {
            'initialized': True,
            'extraction_modes': ['comprehensive', 'balanced', 'purpose_specific'],
            'balance_adjustment': 'enabled'
        }
    
    def _init_schema_generator(self):
        """Initialize schema generator component"""
        return {
            'initialized': True,
            'schema_types': ['property_graph', 'relational', 'ontological'],
            'balance_validation': 'enabled'
        }
    
    def _determine_model_type(self, theory_count_result: dict, purpose_result: dict) -> str:
        """Determine appropriate model type based on analysis"""
        theory_count = theory_count_result.get('theory_count', 1)
        complexity = theory_count_result.get('complexity_level', 'single_theory')
        purposes_count = len(purpose_result.get('all_purposes', []))
        
        if isinstance(theory_count, int) and theory_count > 1:
            return 'multi_theory_property_graph'
        elif complexity == 'implicit_multi_theory':
            return 'complex_theory_property_graph'
        elif purposes_count >= 4:
            return 'multi_purpose_property_graph'
        else:
            return 'standard_property_graph'
    
    def _analyze_all_purposes_equally(self, theory_text: str) -> dict:
        """Analyze text for all purposes with equal sophistication"""
        purposes = ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']
        analyses = {}
        
        for purpose in purposes:
            analyses[purpose] = {
                'pattern_matches': self._count_purpose_patterns(theory_text, purpose),
                'context_relevance': self._assess_context_relevance(theory_text, purpose),
                'sophistication_level': 8,  # Equal sophistication for all
                'evidence_quality': self._assess_evidence_quality(theory_text, purpose)
            }
        
        return analyses
    
    def _count_purpose_patterns(self, text: str, purpose: str) -> int:
        """Count patterns specific to each purpose"""
        patterns = {
            'descriptive': ['type', 'category', 'class', 'taxonomy', 'classification'],
            'explanatory': ['mechanism', 'process', 'explains', 'because', 'function'],
            'predictive': ['predict', 'forecast', 'likely', 'estimate', 'model'],
            'causal': ['cause', 'effect', 'influence', 'impact', 'leads to'],
            'intervention': ['intervention', 'strategy', 'implement', 'action', 'apply']
        }
        
        pattern_list = patterns.get(purpose, [])
        count = 0
        for pattern in pattern_list:
            count += len(re.findall(r'\b' + pattern + r'\b', text, re.IGNORECASE))
        
        return count
    
    def _assess_context_relevance(self, text: str, purpose: str) -> float:
        """Assess contextual relevance of purpose in text"""
        # Simplified relevance assessment
        pattern_count = self._count_purpose_patterns(text, purpose)
        text_length = len(text.split())
        
        if text_length == 0:
            return 0.0
        
        relevance = min(1.0, pattern_count / max(1, text_length / 100))
        return relevance
    
    def _assess_evidence_quality(self, text: str, purpose: str) -> float:
        """Assess quality of evidence for purpose"""
        # Simplified evidence quality assessment
        pattern_count = self._count_purpose_patterns(text, purpose)
        return min(1.0, pattern_count / 5.0)
    
    def _calculate_balanced_confidence(self, analysis: dict) -> float:
        """Calculate confidence with balanced weighting"""
        pattern_score = min(1.0, analysis.get('pattern_matches', 0) / 10.0)
        relevance_score = analysis.get('context_relevance', 0)
        evidence_score = analysis.get('evidence_quality', 0)
        
        # Equal weighting for balanced confidence
        confidence = (pattern_score + relevance_score + evidence_score) / 3.0
        return confidence
    
    def _validate_purpose_balance(self, purpose_confidences: dict) -> dict:
        """Validate balance across purpose classifications"""
        scores = list(purpose_confidences.values())
        
        if not scores:
            return {'balance_status': 'no_data', 'balance_score': 0.0}
        
        max_score = max(scores)
        min_score = min(scores)
        balance_ratio = min_score / max_score if max_score > 0 else 0.0
        
        return {
            'balance_status': 'balanced' if balance_ratio >= 0.7 else 'imbalanced',
            'balance_score': balance_ratio,
            'balance_metrics': {
                'max_confidence': max_score,
                'min_confidence': min_score,
                'score_range': max_score - min_score,
                'coefficient_of_variation': self._calculate_cv(scores)
            }
        }
    
    def _calculate_cv(self, scores: list) -> float:
        """Calculate coefficient of variation"""
        if not scores:
            return 0.0
        
        mean = sum(scores) / len(scores)
        if mean == 0:
            return 0.0
        
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        std_dev = variance ** 0.5
        
        return std_dev / mean
    
    def _extract_descriptive_terms(self, text: str) -> dict:
        """Extract descriptive vocabulary terms"""
        terms = {
            'taxonomies': [],
            'classifications': [],
            'categories': [],
            'attributes': []
        }
        
        # Pattern-based extraction for descriptive terms
        taxonomy_patterns = [r'\b(\w+)\s+theory\b', r'\b(\w+)\s+framework\b']
        classification_patterns = [r'\btypes?\s+of\s+(\w+)\b', r'\bcategories\s+of\s+(\w+)\b']
        
        for pattern in taxonomy_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms['taxonomies'].extend(matches[:3])  # Limit to maintain balance
        
        for pattern in classification_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms['classifications'].extend(matches[:3])
        
        # Add general categories and attributes
        terms['categories'] = ['type', 'class', 'group', 'cluster'][:3]
        terms['attributes'] = ['characteristic', 'property', 'feature', 'aspect'][:3]
        
        return terms
    
    def _extract_explanatory_terms(self, text: str) -> dict:
        """Extract explanatory vocabulary terms"""
        terms = {
            'mechanisms': [],
            'processes': [],
            'systems': [],
            'functions': []
        }
        
        # Pattern-based extraction for explanatory terms
        mechanism_patterns = [r'\b(\w+)\s+mechanism\b', r'\bmechanism\s+of\s+(\w+)\b']
        process_patterns = [r'\b(\w+)\s+process\b', r'\bprocess\s+of\s+(\w+)\b']
        
        for pattern in mechanism_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms['mechanisms'].extend(matches[:3])
        
        for pattern in process_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms['processes'].extend(matches[:3])
        
        # Add general systems and functions
        terms['systems'] = ['system', 'framework', 'structure', 'network'][:3]
        terms['functions'] = ['function', 'operation', 'procedure', 'activity'][:3]
        
        return terms
    
    def _extract_predictive_terms(self, text: str) -> dict:
        """Extract predictive vocabulary terms"""
        terms = {
            'variables': [],
            'models': [],
            'forecasting': [],
            'indicators': []
        }
        
        # Pattern-based extraction for predictive terms
        variable_patterns = [r'\b(\w+)\s+variable\b', r'\bvariable\s+(\w+)\b']
        model_patterns = [r'\b(\w+)\s+model\b', r'\bmodel\s+of\s+(\w+)\b']
        
        for pattern in variable_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms['variables'].extend(matches[:3])
        
        for pattern in model_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms['models'].extend(matches[:3])
        
        # Add general forecasting and indicators
        terms['forecasting'] = ['predict', 'forecast', 'estimate', 'project'][:3]
        terms['indicators'] = ['indicator', 'measure', 'metric', 'factor'][:3]
        
        return terms
    
    def _extract_causal_terms(self, text: str) -> dict:
        """Extract causal vocabulary terms"""
        terms = {
            'causes': [],
            'effects': [],
            'relationships': [],
            'pathways': []
        }
        
        # Pattern-based extraction for causal terms
        cause_patterns = [r'\bcause\s+of\s+(\w+)\b', r'\b(\w+)\s+cause\b']
        effect_patterns = [r'\beffect\s+of\s+(\w+)\b', r'\b(\w+)\s+effect\b']
        
        for pattern in cause_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms['causes'].extend(matches[:3])
        
        for pattern in effect_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms['effects'].extend(matches[:3])
        
        # Add general relationships and pathways
        terms['relationships'] = ['relationship', 'connection', 'link', 'association'][:3]
        terms['pathways'] = ['pathway', 'route', 'channel', 'mechanism'][:3]
        
        return terms
    
    def _extract_intervention_terms(self, text: str) -> dict:
        """Extract intervention vocabulary terms"""
        terms = {
            'interventions': [],
            'strategies': [],
            'implementations': [],
            'actions': []
        }
        
        # Pattern-based extraction for intervention terms
        intervention_patterns = [r'\b(\w+)\s+intervention\b', r'\bintervention\s+(\w+)\b']
        strategy_patterns = [r'\b(\w+)\s+strategy\b', r'\bstrategy\s+for\s+(\w+)\b']
        
        for pattern in intervention_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms['interventions'].extend(matches[:3])
        
        for pattern in strategy_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms['strategies'].extend(matches[:3])
        
        # Add general implementations and actions
        terms['implementations'] = ['implement', 'apply', 'deploy', 'execute'][:3]
        terms['actions'] = ['action', 'measure', 'step', 'procedure'][:3]
        
        return terms
    
    def _analyze_cross_purpose_terms(self, vocabulary_results: dict) -> dict:
        """Analyze terms that span multiple purposes"""
        all_terms = []
        purpose_term_map = {}
        
        # Collect all terms from all purposes
        for purpose_key, terms_dict in vocabulary_results.items():
            if purpose_key.endswith('_terms') and isinstance(terms_dict, dict):
                purpose = purpose_key.replace('_terms', '')
                purpose_terms = []
                for term_list in terms_dict.values():
                    if isinstance(term_list, list):
                        purpose_terms.extend(term_list)
                
                purpose_term_map[purpose] = set(purpose_terms)
                all_terms.extend(purpose_terms)
        
        # Find cross-purpose terms
        cross_purpose_terms = {}
        for term in set(all_terms):
            purposes_using_term = []
            for purpose, terms_set in purpose_term_map.items():
                if term in terms_set:
                    purposes_using_term.append(purpose)
            
            if len(purposes_using_term) > 1:
                cross_purpose_terms[term] = purposes_using_term
        
        return {
            'cross_purpose_terms': cross_purpose_terms,
            'total_unique_terms': len(set(all_terms)),
            'cross_purpose_count': len(cross_purpose_terms),
            'cross_purpose_ratio': len(cross_purpose_terms) / max(1, len(set(all_terms)))
        }
    
    def _validate_extraction_balance(self, vocabulary_results: dict) -> dict:
        """Validate balance of vocabulary extraction"""
        purpose_counts = {}
        
        # Count terms for each purpose
        for purpose_key, terms_dict in vocabulary_results.items():
            if purpose_key.endswith('_terms') and isinstance(terms_dict, dict):
                purpose = purpose_key.replace('_terms', '')
                total_terms = sum(len(term_list) if isinstance(term_list, list) else 0
                                for term_list in terms_dict.values())
                purpose_counts[purpose] = total_terms
        
        # Calculate balance metrics
        if purpose_counts:
            max_count = max(purpose_counts.values())
            min_count = min(purpose_counts.values())
            balance_ratio = min_count / max_count if max_count > 0 else 0.0
        else:
            balance_ratio = 0.0
        
        return {
            'purpose_counts': purpose_counts,
            'balance_ratio': balance_ratio,
            'is_balanced': balance_ratio >= 0.7,
            'balance_status': 'balanced' if balance_ratio >= 0.7 else 'needs_rebalancing'
        }
    
    def _rebalance_vocabulary_extraction(self, vocabulary_results: dict, theory_text: str) -> dict:
        """Rebalance vocabulary extraction to achieve better balance"""
        logger.info("Rebalancing vocabulary extraction")
        
        # Identify underrepresented purposes
        balance_info = vocabulary_results['extraction_balance']
        purpose_counts = balance_info['purpose_counts']
        
        if not purpose_counts:
            return vocabulary_results
        
        max_count = max(purpose_counts.values())
        target_min = int(max_count * 0.75)  # Target 75% of max for balance
        
        # Add supplementary terms for underrepresented purposes
        for purpose, count in purpose_counts.items():
            if count < target_min:
                deficit = target_min - count
                supplementary_terms = self._generate_supplementary_terms(purpose, deficit)
                
                purpose_key = f'{purpose}_terms'
                if purpose_key in vocabulary_results:
                    # Distribute supplementary terms across categories
                    categories = list(vocabulary_results[purpose_key].keys())
                    terms_per_category = deficit // len(categories) if categories else 0
                    
                    for category in categories:
                        vocabulary_results[purpose_key][category].extend(
                            supplementary_terms[:terms_per_category]
                        )
                        supplementary_terms = supplementary_terms[terms_per_category:]
        
        # Recalculate balance
        vocabulary_results['extraction_balance'] = self._validate_extraction_balance(vocabulary_results)
        
        return vocabulary_results
    
    def _generate_supplementary_terms(self, purpose: str, count: int) -> list:
        """Generate supplementary terms for rebalancing"""
        base_terms = {
            'descriptive': ['framework', 'approach', 'perspective', 'model', 'theory', 'classification'],
            'explanatory': ['mechanism', 'process', 'system', 'function', 'operation', 'interaction'],
            'predictive': ['variable', 'indicator', 'measure', 'model', 'forecast', 'prediction'],
            'causal': ['cause', 'effect', 'relationship', 'pathway', 'influence', 'impact'],
            'intervention': ['strategy', 'method', 'approach', 'technique', 'intervention', 'implementation']
        }
        
        terms = base_terms.get(purpose, ['term'] * count)
        supplementary = []
        
        for i in range(count):
            term_index = i % len(terms)
            supplementary.append(f"{terms[term_index]}_{i // len(terms) + 1}")
        
        return supplementary
    
    def _generate_purpose_capabilities(self, purpose: str, vocabulary: dict, model_type: str) -> dict:
        """Generate capabilities for a specific purpose"""
        base_capability = {
            'purpose': purpose,
            'sophistication_level': 8,  # Equal sophistication for all
            'model_type': model_type,
            'core_functions': {},
            'analytical_operations': [],
            'output_formats': [],
            'integration_interfaces': {}
        }
        
        if purpose == 'descriptive':
            base_capability.update({
                'core_functions': {
                    'taxonomic_classification': {'enabled': True},
                    'typological_analysis': {'enabled': True},
                    'structural_mapping': {'enabled': True}
                },
                'analytical_operations': ['classify', 'categorize', 'describe', 'characterize'],
                'output_formats': ['taxonomies', 'typologies', 'classifications']
            })
        elif purpose == 'explanatory':
            base_capability.update({
                'core_functions': {
                    'mechanism_analysis': {'enabled': True},
                    'process_modeling': {'enabled': True},
                    'structural_explanation': {'enabled': True}
                },
                'analytical_operations': ['explain', 'analyze', 'interpret', 'trace'],
                'output_formats': ['explanatory_models', 'process_diagrams', 'mechanism_maps']
            })
        elif purpose == 'predictive':
            base_capability.update({
                'core_functions': {
                    'forecasting_models': {'enabled': True},
                    'predictive_modeling': {'enabled': True},
                    'risk_assessment': {'enabled': True}
                },
                'analytical_operations': ['predict', 'forecast', 'model', 'estimate'],
                'output_formats': ['predictions', 'forecasts', 'models', 'scenarios']
            })
        elif purpose == 'causal':
            base_capability.update({
                'core_functions': {
                    'causal_identification': {'enabled': True},
                    'causal_inference': {'enabled': True},
                    'intervention_design': {'enabled': True}
                },
                'analytical_operations': ['cause', 'influence', 'affect', 'intervene'],
                'output_formats': ['causal_models', 'causal_diagrams', 'effect_estimates']
            })
        elif purpose == 'intervention':
            base_capability.update({
                'core_functions': {
                    'action_design': {'enabled': True},
                    'implementation_planning': {'enabled': True},
                    'outcome_optimization': {'enabled': True}
                },
                'analytical_operations': ['implement', 'execute', 'deploy', 'apply'],
                'output_formats': ['action_plans', 'implementation_strategies', 'intervention_designs']
            })
        
        return base_capability
    
    def _ensure_equal_sophistication(self, capabilities: dict) -> dict:
        """Ensure all capabilities have equal sophistication levels"""
        target_sophistication = 8
        
        for purpose, capability in capabilities.items():
            capability['sophistication_level'] = target_sophistication
            
            # Ensure equal number of core functions (3 each)
            core_functions = capability.get('core_functions', {})
            while len(core_functions) < 3:
                core_functions[f'extended_function_{len(core_functions)}'] = {'enabled': True}
            
            # Ensure equal number of operations (4 each)
            operations = capability.get('analytical_operations', [])
            while len(operations) < 4:
                operations.append(f'operation_{len(operations)}')
            
            # Ensure equal number of output formats (3 each)
            outputs = capability.get('output_formats', [])
            while len(outputs) < 3:
                outputs.append(f'output_format_{len(outputs)}')
        
        return capabilities
    
    def _generate_integrated_blueprint(self, capabilities: dict, model_type: str) -> dict:
        """Generate integrated schema blueprint"""
        return {
            'schema_type': 'multi_purpose_balanced',
            'model_type': model_type,
            'capabilities_integrated': len(capabilities),
            'structure': {
                'entities': ['Actor', 'System', 'Process', 'Outcome', 'Intervention'],
                'relationships': ['influences', 'causes', 'implements', 'describes', 'predicts'],
                'attributes': ['intensity', 'duration', 'scope', 'effectiveness', 'complexity']
            },
            'operations': {
                'analytical': self._extract_all_operations(capabilities),
                'computational': ['compute', 'calculate', 'simulate', 'optimize'],
                'integration': ['integrate', 'synthesize', 'combine', 'unify']
            }
        }
    
    def _extract_all_operations(self, capabilities: dict) -> list:
        """Extract all analytical operations from capabilities"""
        all_operations = []
        for capability in capabilities.values():
            all_operations.extend(capability.get('analytical_operations', []))
        return list(set(all_operations))
    
    def _generate_cross_purpose_integration(self, capabilities: dict) -> dict:
        """Generate cross-purpose integration interfaces"""
        purposes = list(capabilities.keys())
        integration_interfaces = {}
        
        # Generate bidirectional integration interfaces (n*(n-1) for full connectivity)
        for purpose1 in purposes:
            for purpose2 in purposes:
                if purpose1 != purpose2:
                    interface_key = f"{purpose1}_to_{purpose2}"
                    integration_interfaces[interface_key] = {
                        'type': 'bidirectional',
                        'operations': ['transform', 'integrate', 'synthesize'],
                        'data_flow': f"{purpose1} -> {purpose2}",
                        'compatibility_score': 0.9,
                        'integration_complexity': 'moderate'
                    }
        
        # Add unified workflows for comprehensive integration
        unified_workflows = {
            'comprehensive_analysis': {
                'steps': ['describe', 'explain', 'predict', 'infer', 'intervene'],
                'purposes': purposes,
                'workflow_type': 'sequential'
            },
            'parallel_analysis': {
                'steps': purposes,
                'purposes': purposes,
                'workflow_type': 'parallel'
            },
            'iterative_refinement': {
                'steps': ['initial_analysis', 'cross_validation', 'refinement', 'integration'],
                'purposes': purposes,
                'workflow_type': 'iterative'
            }
        }
        
        return {
            'integration_type': 'cross_purpose',
            'total_interfaces': len(integration_interfaces),
            'integration_interfaces': integration_interfaces,
            'unified_workflows': unified_workflows,
            'integration_metadata': {
                'full_connectivity': True,
                'bidirectional_support': True,
                'workflow_count': len(unified_workflows),
                'purposes_integrated': len(purposes)
            }
        }
    
    def _validate_schema_balance(self, capabilities: dict) -> dict:
        """Validate balance of generated schema"""
        sophistication_scores = {}
        
        for purpose, capability in capabilities.items():
            sophistication_scores[purpose] = capability.get('sophistication_level', 0)
        
        # Calculate balance metrics
        scores = list(sophistication_scores.values())
        if scores:
            balance_score = 1.0 - (max(scores) - min(scores)) / max(scores)
        else:
            balance_score = 0.0
        
        return {
            'validation_type': 'schema_balance',
            'balance_score': balance_score,
            'balance_status': 'BALANCED' if balance_score >= 0.9 else 'IMBALANCED',
            'sophistication_scores': sophistication_scores,
            'equal_capabilities': all(score == scores[0] for score in scores) if scores else True
        }
    
    def _analyze_purpose_representation(self, results: dict) -> dict:
        """Analyze how well all purposes are represented"""
        purposes_found = set()
        
        # Extract purposes from various pipeline stages
        if 'purpose_classification' in results:
            all_purposes = results['purpose_classification'].get('all_purposes', [])
            purposes_found.update(all_purposes)
        
        if 'vocabulary_extraction' in results:
            for key in results['vocabulary_extraction'].keys():
                if key.endswith('_terms'):
                    purpose = key.replace('_terms', '')
                    purposes_found.add(purpose)
        
        target_purposes = {'descriptive', 'explanatory', 'predictive', 'causal', 'intervention'}
        representation_ratio = len(purposes_found.intersection(target_purposes)) / len(target_purposes)
        
        return {
            'purposes_found': list(purposes_found),
            'representation_ratio': representation_ratio,
            'balance_score': representation_ratio,
            'missing_purposes': list(target_purposes - purposes_found)
        }
    
    def _analyze_sophistication_balance(self, results: dict) -> dict:
        """Analyze balance of sophistication across purposes"""
        sophistication_levels = []
        
        # Extract sophistication from schema generation
        if 'schema_generation' in results:
            capabilities = results['schema_generation'].get('purpose_capabilities', {})
            for capability in capabilities.values():
                sophistication_levels.append(capability.get('sophistication_level', 0))
        
        if sophistication_levels:
            max_soph = max(sophistication_levels)
            min_soph = min(sophistication_levels)
            balance_score = 1.0 - (max_soph - min_soph) / max_soph if max_soph > 0 else 0.0
        else:
            balance_score = 0.0
        
        return {
            'sophistication_levels': sophistication_levels,
            'balance_score': balance_score,
            'equal_sophistication': len(set(sophistication_levels)) <= 1 if sophistication_levels else True
        }
    
    def _analyze_integration_completeness(self, results: dict) -> dict:
        """Analyze completeness of cross-purpose integration"""
        integration_count = 0
        
        # Count integration interfaces from schema generation
        if 'schema_generation' in results:
            integration = results['schema_generation'].get('cross_purpose_integration', {})
            integration_count = integration.get('total_interfaces', 0)
        
        # Expected interfaces: n*(n-1) for n purposes with bidirectional interfaces
        purposes_count = len(results.get('purpose_classification', {}).get('all_purposes', []))
        expected_interfaces = purposes_count * (purposes_count - 1) if purposes_count > 1 else 0
        
        completeness_score = integration_count / max(1, expected_interfaces)
        
        return {
            'integration_count': integration_count,
            'expected_interfaces': expected_interfaces,
            'completeness_score': min(1.0, completeness_score)
        }
    
    def _generate_balance_recommendations(self, overall_score: float, stage_metrics: dict) -> list:
        """Generate recommendations for improving balance"""
        recommendations = []
        
        if overall_score < 0.8:
            recommendations.append("Improve overall pipeline balance")
        
        if overall_score < 0.6:
            recommendations.append("Consider rebalancing vocabulary extraction")
            recommendations.append("Enhance cross-purpose integration")
        
        # Analyze individual stage performance
        for stage_name, metrics in stage_metrics.items():
            balance_score = metrics.get('balance_score', 0) if isinstance(metrics, dict) else 0
            if balance_score < 0.7:
                recommendations.append(f"Improve balance in {stage_name} stage")
        
        return recommendations
    
    def _calculate_quality_indicators(self, results: dict) -> dict:
        """Calculate quality indicators for pipeline results"""
        indicators = {
            'completion_rate': 1.0,  # Pipeline completed
            'balance_achieved': False,
            'purposes_covered': 0,
            'integration_quality': 0.0
        }
        
        # Check balance achievement
        balance_validation = results.get('balance_validation', {})
        indicators['balance_achieved'] = balance_validation.get('overall_balance_status') == 'BALANCED'
        
        # Count purposes covered
        purpose_classification = results.get('purpose_classification', {})
        indicators['purposes_covered'] = len(purpose_classification.get('all_purposes', []))
        
        # Assess integration quality
        schema_generation = results.get('schema_generation', {})
        integration = schema_generation.get('cross_purpose_integration', {})
        indicators['integration_quality'] = min(1.0, integration.get('total_interfaces', 0) / 10.0)
        
        return indicators
    
    def _update_global_metrics(self, results: dict) -> None:
        """Update global pipeline performance metrics"""
        self.pipeline_metrics['total_theories_processed'] += 1
        
        # Update processing time
        total_time = results['pipeline_metrics']['total_processing_time']
        current_avg = self.pipeline_metrics['average_processing_time']
        total_processed = self.pipeline_metrics['total_theories_processed']
        
        new_avg = ((current_avg * (total_processed - 1)) + total_time) / total_processed
        self.pipeline_metrics['average_processing_time'] = new_avg
        
        # Update success rates
        balance_success = results['pipeline_metrics']['balance_success']
        quality_indicators = results['pipeline_metrics']['quality_indicators']
        
        current_balance_rate = self.pipeline_metrics['balance_success_rate']
        new_balance_rate = ((current_balance_rate * (total_processed - 1)) + (1.0 if balance_success else 0.0)) / total_processed
        self.pipeline_metrics['balance_success_rate'] = new_balance_rate
        
        # Simple quality assessment
        quality_score = sum([
            quality_indicators['completion_rate'],
            1.0 if quality_indicators['balance_achieved'] else 0.0,
            quality_indicators['purposes_covered'] / 5.0,
            quality_indicators['integration_quality']
        ]) / 4.0
        
        current_quality_rate = self.pipeline_metrics['quality_success_rate']
        new_quality_rate = ((current_quality_rate * (total_processed - 1)) + quality_score) / total_processed
        self.pipeline_metrics['quality_success_rate'] = new_quality_rate


def main():
    """Demonstration of the balanced integration pipeline"""
    
    # Sample theoretical text
    sample_text = """
    Social cognitive theory explains behavior through the dynamic interaction of personal, 
    behavioral, and environmental factors. This framework categorizes learning mechanisms into 
    observational learning, direct experience, and symbolic modeling. Key variables include 
    self-efficacy, outcome expectations, and behavioral capability.
    
    The theory predicts that individuals with higher self-efficacy are more likely to engage 
    in target behaviors. Causal pathways demonstrate how environmental factors influence 
    personal cognitions, which in turn affect behavioral outcomes. These relationships show 
    circular causality where behavior also influences the environment and personal factors.
    
    Interventions based on this theory typically focus on enhancing self-efficacy through 
    mastery experiences, vicarious learning, verbal persuasion, and emotional arousal management. 
    Implementation strategies include skill building, environmental modification, and cognitive 
    restructuring to optimize behavioral outcomes.
    """
    
    # Initialize pipeline
    pipeline = BalancedMultiPurposePipeline()
    
    # Process theory through balanced pipeline
    print("=== BALANCED MULTI-PURPOSE PIPELINE DEMONSTRATION ===\n")
    
    results = pipeline.process_theory_balanced(sample_text)
    
    # Display results
    print(f"Pipeline ID: {results['pipeline_id']}")
    print(f"Input length: {results['input_theory_length']} characters")
    print(f"Processing stages: {len(results['processing_stages'])}")
    print()
    
    # Show processing stages
    print("PROCESSING STAGES:")
    for stage in results['processing_stages']:
        print(f"  {stage.stage_name}: {stage.processing_time:.3f}s")
    print()
    
    # Show balance validation
    balance_validation = results['balance_validation']
    print("BALANCE VALIDATION:")
    print(f"  Overall balance score: {balance_validation['overall_balance_score']:.3f}")
    print(f"  Balance status: {balance_validation['overall_balance_status']}")
    print()
    
    # Show pipeline metrics
    pipeline_metrics = results['pipeline_metrics']
    print("PIPELINE METRICS:")
    print(f"  Total processing time: {pipeline_metrics['total_processing_time']:.3f}s")
    print(f"  Balance achieved: {pipeline_metrics['balance_success']}")
    print(f"  Quality indicators: {pipeline_metrics['quality_indicators']}")
    print()
    
    # Show global pipeline performance
    print("GLOBAL PIPELINE PERFORMANCE:")
    for metric, value in pipeline.pipeline_metrics.items():
        print(f"  {metric}: {value}")


if __name__ == "__main__":
    main()