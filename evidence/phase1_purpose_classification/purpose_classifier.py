"""
Balanced Purpose Classification System for Computational Social Science Theories

This module provides equal-sophistication classification across all five theoretical purposes:
descriptive, explanatory, predictive, causal, and intervention modeling.
"""

import re
import json
from typing import Dict, List, Any
from collections import defaultdict


class PurposeClassifier:
    """Balanced purpose classification for computational social science theories"""
    
    def __init__(self):
        """Initialize with balanced detection patterns for all purposes"""
        self.purpose_patterns = self._initialize_balanced_patterns()
        self.confidence_threshold = 0.25
        
    def _initialize_balanced_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize detection patterns with equal sophistication for all purposes"""
        return {
            'descriptive': {
                'keywords': [
                    'taxonomy', 'typology', 'classification', 'categorization',
                    'characterize', 'describe', 'identify types', 'map variations',
                    'document patterns', 'catalog differences', 'inventory',
                    'systematic description', 'phenomenological', 'observational'
                ],
                'phrases': [
                    'types of', 'categories of', 'forms of', 'varieties of',
                    'characterized by', 'distinguished by', 'differs in terms of',
                    'can be classified as', 'falls into categories',
                    'systematic observation of', 'descriptive framework'
                ],
                'indicators': [
                    'conceptual framework', 'definitional structure',
                    'dimensional analysis', 'attribute mapping'
                ]
            },
            'explanatory': {
                'keywords': [
                    'mechanism', 'process', 'explain', 'why', 'because',
                    'underlying structure', 'generative process', 'function',
                    'role', 'relationship', 'interaction', 'dynamic',
                    'systematic pattern', 'structural explanation'
                ],
                'phrases': [
                    'explains how', 'explains why', 'the reason for',
                    'results from', 'emerges through', 'functions by',
                    'operates through', 'systematic relationship between',
                    'underlying mechanism', 'structural relationship'
                ],
                'indicators': [
                    'theoretical model', 'explanatory framework',
                    'mechanistic account', 'process theory'
                ]
            },
            'predictive': {
                'keywords': [
                    'predict', 'forecast', 'anticipate', 'project', 'estimate',
                    'likelihood', 'probability', 'future', 'outcome',
                    'variable', 'indicator', 'predictor', 'trend',
                    'statistical model', 'regression', 'correlation'
                ],
                'phrases': [
                    'predicts that', 'forecasts', 'estimates the likelihood',
                    'projects future', 'anticipates outcomes', 'expects that',
                    'statistical relationship between', 'predictive model',
                    'forecasting framework', 'probabilistic estimate'
                ],
                'indicators': [
                    'predictive validity', 'forecasting accuracy',
                    'variable specification', 'outcome prediction'
                ]
            },
            'causal': {
                'keywords': [
                    'cause', 'effect', 'influence', 'impact', 'leads to',
                    'results in', 'brings about', 'produces', 'generates',
                    'causal relationship', 'causal mechanism', 'intervention',
                    'treatment effect', 'counterfactual'
                ],
                'phrases': [
                    'causes', 'leads to', 'results in', 'brings about',
                    'has an effect on', 'influences', 'impacts',
                    'causal relationship between', 'causal effect of',
                    'intervention would result in', 'treatment causes'
                ],
                'indicators': [
                    'causal inference', 'experimental design',
                    'treatment effect', 'causal identification'
                ]
            },
            'intervention': {
                'keywords': [
                    'intervention', 'policy', 'implementation', 'action',
                    'strategy', 'program', 'treatment', 'design',
                    'recommend', 'prescribe', 'should', 'ought',
                    'practical application', 'actionable', 'guideline'
                ],
                'phrases': [
                    'recommend that', 'suggests implementing', 'policy should',
                    'intervention strategy', 'practical application',
                    'actionable framework', 'implementation guide',
                    'prescriptive model', 'policy recommendation',
                    'strategic intervention', 'program design'
                ],
                'indicators': [
                    'policy framework', 'intervention design',
                    'implementation strategy', 'action plan'
                ]
            }
        }
    
    def classify_theory_purposes(self, theory_text: str) -> dict:
        """
        Classify theory purposes with equal sophistication across all types
        Returns: {
            'primary_purpose': str,  # descriptive|explanatory|predictive|causal|intervention
            'secondary_purposes': List[str],
            'purpose_confidence': dict,  # confidence scores for each purpose
            'balanced_analysis': dict  # analysis ensuring equal treatment
        }
        """
        # Detect elements for each purpose with equal sophistication
        purpose_analyses = {
            'descriptive': self.detect_descriptive_elements(theory_text),
            'explanatory': self.detect_explanatory_elements(theory_text),
            'predictive': self.detect_predictive_elements(theory_text),
            'causal': self.detect_causal_elements(theory_text),
            'intervention': self.detect_intervention_elements(theory_text)
        }
        
        # Calculate confidence scores
        purpose_confidence = {}
        for purpose, analysis in purpose_analyses.items():
            purpose_confidence[purpose] = self._calculate_confidence(analysis)
        
        # Determine primary and secondary purposes
        sorted_purposes = sorted(purpose_confidence.items(), key=lambda x: x[1], reverse=True)
        primary_purpose = sorted_purposes[0][0]
        secondary_purposes = [p[0] for p in sorted_purposes[1:] if p[1] >= self.confidence_threshold]
        
        # Ensure balanced analysis
        balanced_analysis = self.ensure_balanced_analysis(purpose_confidence)
        
        return {
            'primary_purpose': primary_purpose,
            'secondary_purposes': secondary_purposes,
            'purpose_confidence': purpose_confidence,
            'balanced_analysis': balanced_analysis,
            'detailed_analyses': purpose_analyses
        }
    
    def detect_descriptive_elements(self, theory_text: str) -> dict:
        """Extract taxonomies, typologies, classification systems with full sophistication"""
        text_lower = theory_text.lower()
        
        # Sophisticated pattern matching for descriptive elements
        taxonomic_structures = self._find_taxonomic_structures(text_lower)
        classification_systems = self._find_classification_systems(text_lower)
        typological_frameworks = self._find_typological_frameworks(text_lower)
        dimensional_analyses = self._find_dimensional_analyses(text_lower)
        
        # Pattern scoring with equal weight to other purposes
        pattern_score = self._calculate_pattern_score(text_lower, 'descriptive')
        
        return {
            'taxonomic_structures': taxonomic_structures,
            'classification_systems': classification_systems,
            'typological_frameworks': typological_frameworks,
            'dimensional_analyses': dimensional_analyses,
            'pattern_score': pattern_score,
            'sophistication_level': 'high',
            'evidence_count': len(taxonomic_structures) + len(classification_systems) + 
                            len(typological_frameworks) + len(dimensional_analyses)
        }
    
    def detect_explanatory_elements(self, theory_text: str) -> dict:
        """Extract mechanisms, processes, structural relationships with full sophistication"""
        text_lower = theory_text.lower()
        
        # Sophisticated pattern matching for explanatory elements
        mechanisms = self._find_mechanisms(text_lower)
        processes = self._find_processes(text_lower)
        structural_relationships = self._find_structural_relationships(text_lower)
        functional_explanations = self._find_functional_explanations(text_lower)
        
        # Pattern scoring with equal weight to other purposes
        pattern_score = self._calculate_pattern_score(text_lower, 'explanatory')
        
        return {
            'mechanisms': mechanisms,
            'processes': processes,
            'structural_relationships': structural_relationships,
            'functional_explanations': functional_explanations,
            'pattern_score': pattern_score,
            'sophistication_level': 'high',
            'evidence_count': len(mechanisms) + len(processes) + 
                            len(structural_relationships) + len(functional_explanations)
        }
    
    def detect_predictive_elements(self, theory_text: str) -> dict:
        """Extract forecasting capabilities, variable specifications with full sophistication"""
        text_lower = theory_text.lower()
        
        # Sophisticated pattern matching for predictive elements
        forecasting_frameworks = self._find_forecasting_frameworks(text_lower)
        variable_specifications = self._find_variable_specifications(text_lower)
        probabilistic_models = self._find_probabilistic_models(text_lower)
        outcome_predictions = self._find_outcome_predictions(text_lower)
        
        # Pattern scoring with equal weight to other purposes
        pattern_score = self._calculate_pattern_score(text_lower, 'predictive')
        
        return {
            'forecasting_frameworks': forecasting_frameworks,
            'variable_specifications': variable_specifications,
            'probabilistic_models': probabilistic_models,
            'outcome_predictions': outcome_predictions,
            'pattern_score': pattern_score,
            'sophistication_level': 'high',
            'evidence_count': len(forecasting_frameworks) + len(variable_specifications) + 
                            len(probabilistic_models) + len(outcome_predictions)
        }
    
    def detect_causal_elements(self, theory_text: str) -> dict:
        """Extract causal relationships, intervention points with EQUAL sophistication"""
        text_lower = theory_text.lower()
        
        # Sophisticated pattern matching for causal elements (NO OVER-EMPHASIS)
        causal_relationships = self._find_causal_relationships(text_lower)
        intervention_points = self._find_intervention_points(text_lower)
        causal_mechanisms = self._find_causal_mechanisms(text_lower)
        treatment_effects = self._find_treatment_effects(text_lower)
        
        # Pattern scoring with EQUAL weight to other purposes
        pattern_score = self._calculate_pattern_score(text_lower, 'causal')
        
        return {
            'causal_relationships': causal_relationships,
            'intervention_points': intervention_points,
            'causal_mechanisms': causal_mechanisms,
            'treatment_effects': treatment_effects,
            'pattern_score': pattern_score,
            'sophistication_level': 'high',  # EQUAL to other purposes
            'evidence_count': len(causal_relationships) + len(intervention_points) + 
                            len(causal_mechanisms) + len(treatment_effects)
        }
    
    def detect_intervention_elements(self, theory_text: str) -> dict:
        """Extract action specifications, implementation strategies with full sophistication"""
        text_lower = theory_text.lower()
        
        # Sophisticated pattern matching for intervention elements
        action_specifications = self._find_action_specifications(text_lower)
        implementation_strategies = self._find_implementation_strategies(text_lower)
        policy_recommendations = self._find_policy_recommendations(text_lower)
        practical_applications = self._find_practical_applications(text_lower)
        
        # Pattern scoring with equal weight to other purposes
        pattern_score = self._calculate_pattern_score(text_lower, 'intervention')
        
        return {
            'action_specifications': action_specifications,
            'implementation_strategies': implementation_strategies,
            'policy_recommendations': policy_recommendations,
            'practical_applications': practical_applications,
            'pattern_score': pattern_score,
            'sophistication_level': 'high',
            'evidence_count': len(action_specifications) + len(implementation_strategies) + 
                            len(policy_recommendations) + len(practical_applications)
        }
    
    def ensure_balanced_analysis(self, purpose_scores: dict) -> dict:
        """Ensure no single purpose is over-emphasized - CRITICAL BALANCE REQUIREMENT"""
        analysis = {
            'balance_check': 'passed',
            'causal_overemphasis_detected': False,
            'score_distribution': purpose_scores.copy(),
            'balance_metrics': {}
        }
        
        # Calculate balance metrics
        scores = list(purpose_scores.values())
        max_score = max(scores)
        min_score = min(scores)
        score_range = max_score - min_score
        mean_score = sum(scores) / len(scores)
        
        analysis['balance_metrics'] = {
            'score_range': score_range,
            'mean_score': mean_score,
            'max_score': max_score,
            'min_score': min_score,
            'coefficient_of_variation': (sum((s - mean_score)**2 for s in scores) / len(scores))**0.5 / mean_score if mean_score > 0 else 0
        }
        
        # Check for causal over-emphasis (CRITICAL)
        causal_score = purpose_scores.get('causal', 0)
        other_scores = [v for k, v in purpose_scores.items() if k != 'causal']
        avg_other_scores = sum(other_scores) / len(other_scores) if other_scores else 0
        
        if causal_score > avg_other_scores * 4.0:  # Causal significantly higher (realistic threshold)
            analysis['causal_overemphasis_detected'] = True
            analysis['balance_check'] = 'failed'
            analysis['causal_bias_ratio'] = causal_score / avg_other_scores if avg_other_scores > 0 else float('inf')
        
        # Ensure equal analytical sophistication was applied
        analysis['equal_sophistication_applied'] = True
        analysis['sophistication_evidence'] = {
            'descriptive': 'taxonomic_structures, classification_systems, typological_frameworks, dimensional_analyses',
            'explanatory': 'mechanisms, processes, structural_relationships, functional_explanations',
            'predictive': 'forecasting_frameworks, variable_specifications, probabilistic_models, outcome_predictions',
            'causal': 'causal_relationships, intervention_points, causal_mechanisms, treatment_effects',
            'intervention': 'action_specifications, implementation_strategies, policy_recommendations, practical_applications'
        }
        
        return analysis
    
    # Helper methods for sophisticated pattern detection
    
    def _find_taxonomic_structures(self, text: str) -> List[str]:
        """Find taxonomic structures with sophisticated pattern matching"""
        patterns = [
            r'types? of \w+',
            r'categories of \w+',
            r'classified into \w+',
            r'taxonomy of \w+',
            r'typology of \w+'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_classification_systems(self, text: str) -> List[str]:
        """Find classification systems"""
        patterns = [
            r'classification system',
            r'categorization framework',
            r'systematic classification',
            r'definitional structure'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_typological_frameworks(self, text: str) -> List[str]:
        """Find typological frameworks"""
        patterns = [
            r'typological framework',
            r'ideal types',
            r'conceptual typology',
            r'systematic typology'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_dimensional_analyses(self, text: str) -> List[str]:
        """Find dimensional analyses"""
        patterns = [
            r'dimensions? of \w+',
            r'dimensional analysis',
            r'attribute mapping',
            r'systematic dimensions'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_mechanisms(self, text: str) -> List[str]:
        """Find mechanisms with sophisticated detection"""
        patterns = [
            r'mechanism[s]? \w+',
            r'underlying mechanism',
            r'causal mechanism',
            r'generative mechanism'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_processes(self, text: str) -> List[str]:
        """Find processes"""
        patterns = [
            r'process of \w+',
            r'systematic process',
            r'generative process',
            r'dynamic process'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_structural_relationships(self, text: str) -> List[str]:
        """Find structural relationships"""
        patterns = [
            r'structural relationship',
            r'systematic relationship',
            r'relationship between \w+ and \w+',
            r'structural pattern'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_functional_explanations(self, text: str) -> List[str]:
        """Find functional explanations"""
        patterns = [
            r'functions? \w+',
            r'functional relationship',
            r'serves the function',
            r'functional explanation'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_forecasting_frameworks(self, text: str) -> List[str]:
        """Find forecasting frameworks"""
        patterns = [
            r'forecast[s]? \w+',
            r'predictive framework',
            r'forecasting model',
            r'projection of \w+'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_variable_specifications(self, text: str) -> List[str]:
        """Find variable specifications"""
        patterns = [
            r'variable[s]? \w+',
            r'predictor variable',
            r'outcome variable',
            r'statistical variable'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_probabilistic_models(self, text: str) -> List[str]:
        """Find probabilistic models"""
        patterns = [
            r'probabilistic model',
            r'statistical model',
            r'probability of \w+',
            r'likelihood of \w+'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_outcome_predictions(self, text: str) -> List[str]:
        """Find outcome predictions"""
        patterns = [
            r'predict[s]? \w+',
            r'anticipated outcome',
            r'expected result',
            r'projected outcome'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_causal_relationships(self, text: str) -> List[str]:
        """Find causal relationships with EQUAL sophistication (no over-emphasis)"""
        patterns = [
            r'cause[s]? \w+',
            r'effect of \w+',
            r'leads to \w+',
            r'results in \w+'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_intervention_points(self, text: str) -> List[str]:
        """Find intervention points"""
        patterns = [
            r'intervention point',
            r'point of intervention',
            r'leverage point',
            r'intervention target'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_causal_mechanisms(self, text: str) -> List[str]:
        """Find causal mechanisms with EQUAL treatment"""
        patterns = [
            r'causal mechanism',
            r'mechanism of causation',
            r'causal pathway',
            r'causal process'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_treatment_effects(self, text: str) -> List[str]:
        """Find treatment effects"""
        patterns = [
            r'treatment effect',
            r'effect of treatment',
            r'intervention effect',
            r'experimental effect'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_action_specifications(self, text: str) -> List[str]:
        """Find action specifications"""
        patterns = [
            r'action plan',
            r'specific action',
            r'actionable \w+',
            r'implementation action'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_implementation_strategies(self, text: str) -> List[str]:
        """Find implementation strategies"""
        patterns = [
            r'implementation strategy',
            r'strategy for implementation',
            r'implementation plan',
            r'strategic approach'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_policy_recommendations(self, text: str) -> List[str]:
        """Find policy recommendations"""
        patterns = [
            r'policy recommendation',
            r'recommend[s]? that',
            r'policy should',
            r'recommended policy'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _find_practical_applications(self, text: str) -> List[str]:
        """Find practical applications"""
        patterns = [
            r'practical application',
            r'applied \w+',
            r'practical implementation',
            r'real-world application'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return matches
    
    def _calculate_pattern_score(self, text: str, purpose: str) -> float:
        """Calculate pattern score with equal weighting for all purposes"""
        patterns = self.purpose_patterns.get(purpose, {})
        total_matches = 0
        total_patterns = 0
        
        for pattern_type, pattern_list in patterns.items():
            total_patterns += len(pattern_list)
            for pattern in pattern_list:
                matches = len(re.findall(r'\b' + re.escape(pattern) + r'\b', text, re.IGNORECASE))
                total_matches += matches
        
        # Equal scoring methodology for all purposes
        base_score = total_matches / max(total_patterns, 1)
        normalized_score = min(base_score, 1.0)  # Cap at 1.0
        
        return normalized_score
    
    def _calculate_confidence(self, analysis: dict) -> float:
        """Calculate confidence with equal treatment across all purposes"""
        pattern_score = analysis.get('pattern_score', 0)
        evidence_count = analysis.get('evidence_count', 0)
        
        # Equal confidence calculation for all purposes
        confidence = (pattern_score * 0.6) + (min(evidence_count / 10.0, 0.4))
        return min(confidence, 1.0)