#!/usr/bin/env python3
"""
Cross-Purpose Integration for Multi-Purpose Vocabulary Extraction

This module handles terms that serve multiple theoretical purposes and ensures
proper integration across descriptive, explanatory, predictive, causal, and
intervention analytical approaches.
"""

import json
from typing import Dict, List, Set, Any, Tuple
from collections import defaultdict, Counter
import itertools
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrossPurposeIntegrator:
    """Handles integration of terms across multiple theoretical purposes"""
    
    def __init__(self):
        """Initialize the cross-purpose integrator"""
        self.purposes = ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']
        self.integration_patterns = self._initialize_integration_patterns()
        self.semantic_bridges = self._initialize_semantic_bridges()
    
    def _initialize_integration_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize patterns for cross-purpose term integration"""
        return {
            'descriptive_explanatory': {
                'bridge_terms': ['framework', 'system', 'structure', 'component', 'element'],
                'integration_focus': 'Terms that both categorize and explain mechanisms',
                'examples': ['theoretical framework', 'system architecture', 'structural component']
            },
            'explanatory_predictive': {
                'bridge_terms': ['model', 'variable', 'factor', 'parameter', 'function'],
                'integration_focus': 'Terms that both explain mechanisms and enable prediction',
                'examples': ['predictive model', 'explanatory variable', 'functional parameter']
            },
            'predictive_causal': {
                'bridge_terms': ['relationship', 'correlation', 'dependency', 'association', 'link'],
                'integration_focus': 'Terms that both predict outcomes and identify causal relationships',
                'examples': ['causal relationship', 'predictive correlation', 'dependency structure']
            },
            'causal_intervention': {
                'bridge_terms': ['pathway', 'mechanism', 'target', 'leverage', 'intervention'],
                'integration_focus': 'Terms that both identify causes and suggest interventions',
                'examples': ['intervention pathway', 'causal mechanism', 'leverage point']
            },
            'descriptive_predictive': {
                'bridge_terms': ['indicator', 'measure', 'metric', 'dimension', 'attribute'],
                'integration_focus': 'Terms that both categorize and serve as predictive measures',
                'examples': ['predictive indicator', 'measurement dimension', 'categorical metric']
            },
            'descriptive_causal': {
                'bridge_terms': ['determinant', 'factor', 'characteristic', 'property', 'feature'],
                'integration_focus': 'Terms that both describe and determine causal relationships',
                'examples': ['causal factor', 'determining characteristic', 'causal property']
            },
            'descriptive_intervention': {
                'bridge_terms': ['strategy', 'approach', 'method', 'technique', 'tool'],
                'integration_focus': 'Terms that both categorize and describe intervention methods',
                'examples': ['intervention strategy', 'methodological approach', 'categorical tool']
            },
            'explanatory_causal': {
                'bridge_terms': ['process', 'mechanism', 'pathway', 'sequence', 'chain'],
                'integration_focus': 'Terms that both explain how things work and show causal flow',
                'examples': ['causal process', 'explanatory mechanism', 'causal pathway']
            },
            'explanatory_intervention': {
                'bridge_terms': ['implementation', 'application', 'procedure', 'protocol', 'practice'],
                'integration_focus': 'Terms that both explain processes and guide implementation',
                'examples': ['implementation process', 'procedural explanation', 'practice mechanism']
            },
            'predictive_intervention': {
                'bridge_terms': ['outcome', 'result', 'effect', 'impact', 'consequence'],
                'integration_focus': 'Terms that both predict results and measure intervention effects',
                'examples': ['predicted outcome', 'intervention effect', 'measurable impact']
            }
        }
    
    def _initialize_semantic_bridges(self) -> Dict[str, Any]:
        """Initialize semantic bridges between purposes"""
        return {
            'foundational_concepts': {
                'theory', 'model', 'framework', 'system', 'structure', 'process',
                'factor', 'variable', 'element', 'component', 'relationship', 'pattern'
            },
            'methodological_concepts': {
                'analysis', 'measurement', 'assessment', 'evaluation', 'validation',
                'testing', 'examination', 'investigation', 'study', 'research'
            },
            'operational_concepts': {
                'implementation', 'application', 'practice', 'procedure', 'protocol',
                'strategy', 'approach', 'method', 'technique', 'tool'
            }
        }
    
    def integrate_cross_purpose_terms(self, purpose_extractions: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Integrate terms that serve multiple theoretical purposes
        
        Args:
            purpose_extractions: Dictionary of extractions by purpose
            
        Returns:
            Integrated cross-purpose analysis
        """
        logger.info("Starting cross-purpose integration")
        
        integration_results = {
            'multi_purpose_terms': {},
            'purpose_pairs_analysis': {},
            'semantic_bridges': {},
            'integration_matrix': {},
            'foundational_concepts': [],
            'integration_quality': {}
        }
        
        # Extract all terms by purpose
        purpose_terms = self._extract_all_terms_by_purpose(purpose_extractions)
        
        # Identify multi-purpose terms
        integration_results['multi_purpose_terms'] = self._identify_multi_purpose_terms(purpose_terms)
        
        # Analyze purpose pair relationships
        integration_results['purpose_pairs_analysis'] = self._analyze_purpose_pairs(purpose_terms)
        
        # Identify semantic bridges
        integration_results['semantic_bridges'] = self._identify_semantic_bridges(purpose_terms)
        
        # Create integration matrix
        integration_results['integration_matrix'] = self._create_integration_matrix(purpose_terms)
        
        # Identify foundational concepts
        integration_results['foundational_concepts'] = self._identify_foundational_concepts(purpose_terms)
        
        # Assess integration quality
        integration_results['integration_quality'] = self._assess_integration_quality(
            purpose_extractions, integration_results
        )
        
        return integration_results
    
    def _extract_all_terms_by_purpose(self, purpose_extractions: Dict[str, Dict]) -> Dict[str, Set[str]]:
        """Extract all terms organized by purpose"""
        purpose_terms = {}
        
        for purpose, extraction in purpose_extractions.items():
            if purpose.endswith('_terms'):
                purpose_name = purpose.replace('_terms', '')
                all_terms = set()
                
                if isinstance(extraction, dict):
                    for category, terms in extraction.items():
                        if isinstance(terms, list):
                            all_terms.update(term.lower().strip() for term in terms if term.strip())
                
                purpose_terms[purpose_name] = all_terms
        
        return purpose_terms
    
    def _identify_multi_purpose_terms(self, purpose_terms: Dict[str, Set[str]]) -> Dict[str, Any]:
        """Identify terms that appear in multiple purposes"""
        
        multi_purpose_analysis = {
            'terms_by_count': {},
            'terms_by_purposes': {},
            'high_integration_terms': [],
            'pair_specific_terms': {}
        }
        
        # Count appearances across purposes
        term_appearances = defaultdict(list)
        for purpose, terms in purpose_terms.items():
            for term in terms:
                term_appearances[term].append(purpose)
        
        # Organize by appearance count
        for term, purposes in term_appearances.items():
            count = len(purposes)
            if count > 1:  # Multi-purpose terms only
                if count not in multi_purpose_analysis['terms_by_count']:
                    multi_purpose_analysis['terms_by_count'][count] = []
                multi_purpose_analysis['terms_by_count'][count].append({
                    'term': term,
                    'purposes': purposes
                })
                
                multi_purpose_analysis['terms_by_purposes'][term] = purposes
        
        # Identify high integration terms (appearing in 3+ purposes)
        multi_purpose_analysis['high_integration_terms'] = [
            term for term, purposes in multi_purpose_analysis['terms_by_purposes'].items()
            if len(purposes) >= 3
        ]
        
        # Identify pair-specific terms
        for pair_key, pattern in self.integration_patterns.items():
            purposes_in_pair = pair_key.split('_')
            if len(purposes_in_pair) == 2:
                pair_terms = []
                for term, term_purposes in multi_purpose_analysis['terms_by_purposes'].items():
                    if (set(term_purposes) == set(purposes_in_pair) or 
                        all(p in term_purposes for p in purposes_in_pair)):
                        pair_terms.append(term)
                
                if pair_terms:
                    multi_purpose_analysis['pair_specific_terms'][pair_key] = pair_terms
        
        return multi_purpose_analysis
    
    def _analyze_purpose_pairs(self, purpose_terms: Dict[str, Set[str]]) -> Dict[str, Any]:
        """Analyze relationships between purpose pairs"""
        
        pair_analysis = {}
        purposes = list(purpose_terms.keys())
        
        for i, purpose1 in enumerate(purposes):
            for j, purpose2 in enumerate(purposes[i+1:], i+1):
                pair_key = f"{purpose1}_{purpose2}"
                
                # Calculate overlap
                overlap = purpose_terms[purpose1].intersection(purpose_terms[purpose2])
                union = purpose_terms[purpose1].union(purpose_terms[purpose2])
                
                # Calculate Jaccard similarity
                jaccard = len(overlap) / len(union) if union else 0.0
                
                # Get integration pattern if available
                pattern = self.integration_patterns.get(pair_key, {})
                
                pair_analysis[pair_key] = {
                    'purposes': [purpose1, purpose2],
                    'overlap_count': len(overlap),
                    'overlap_terms': list(overlap)[:10],  # Sample of overlap terms
                    'jaccard_similarity': jaccard,
                    'integration_pattern': pattern.get('integration_focus', 'No specific pattern'),
                    'bridge_terms_found': [
                        term for term in overlap 
                        if any(bridge in term.lower() for bridge in pattern.get('bridge_terms', []))
                    ] if pattern else [],
                    'strength': self._classify_integration_strength(len(overlap), jaccard)
                }
        
        return pair_analysis
    
    def _identify_semantic_bridges(self, purpose_terms: Dict[str, Set[str]]) -> Dict[str, Any]:
        """Identify semantic bridges between purposes"""
        
        bridge_analysis = {
            'foundational_bridges': [],
            'methodological_bridges': [],
            'operational_bridges': [],
            'custom_bridges': []
        }
        
        all_terms = set().union(*purpose_terms.values())
        
        # Check foundational concept bridges
        foundational_found = all_terms.intersection(self.semantic_bridges['foundational_concepts'])
        bridge_analysis['foundational_bridges'] = list(foundational_found)
        
        # Check methodological concept bridges  
        methodological_found = all_terms.intersection(self.semantic_bridges['methodological_concepts'])
        bridge_analysis['methodological_bridges'] = list(methodological_found)
        
        # Check operational concept bridges
        operational_found = all_terms.intersection(self.semantic_bridges['operational_concepts'])
        bridge_analysis['operational_bridges'] = list(operational_found)
        
        # Identify custom bridges (terms appearing in 4+ purposes)
        term_appearances = defaultdict(list)
        for purpose, terms in purpose_terms.items():
            for term in terms:
                term_appearances[term].append(purpose)
        
        custom_bridges = [
            term for term, purposes in term_appearances.items()
            if len(purposes) >= 4
        ]
        bridge_analysis['custom_bridges'] = custom_bridges
        
        return bridge_analysis
    
    def _create_integration_matrix(self, purpose_terms: Dict[str, Set[str]]) -> Dict[str, Any]:
        """Create integration matrix showing cross-purpose relationships"""
        
        purposes = list(purpose_terms.keys())
        matrix = {}
        
        # Create similarity matrix
        for purpose1 in purposes:
            matrix[purpose1] = {}
            for purpose2 in purposes:
                if purpose1 == purpose2:
                    matrix[purpose1][purpose2] = 1.0
                else:
                    overlap = purpose_terms[purpose1].intersection(purpose_terms[purpose2])
                    union = purpose_terms[purpose1].union(purpose_terms[purpose2])
                    similarity = len(overlap) / len(union) if union else 0.0
                    matrix[purpose1][purpose2] = round(similarity, 3)
        
        # Calculate integration metrics
        similarities = []
        for purpose1 in purposes:
            for purpose2 in purposes:
                if purpose1 != purpose2:
                    similarities.append(matrix[purpose1][purpose2])
        
        integration_metrics = {
            'similarity_matrix': matrix,
            'average_similarity': sum(similarities) / len(similarities) if similarities else 0.0,
            'max_similarity': max(similarities) if similarities else 0.0,
            'min_similarity': min(similarities) if similarities else 0.0,
            'integration_strength': self._calculate_overall_integration_strength(similarities)
        }
        
        return integration_metrics
    
    def _identify_foundational_concepts(self, purpose_terms: Dict[str, Set[str]]) -> List[Dict[str, Any]]:
        """Identify concepts that are foundational across multiple purposes"""
        
        foundational_concepts = []
        
        # Count term appearances
        term_appearances = defaultdict(list)
        for purpose, terms in purpose_terms.items():
            for term in terms:
                term_appearances[term].append(purpose)
        
        # Identify foundational terms (appearing in most purposes)
        min_appearances = max(2, len(purpose_terms) - 1)  # Must appear in most purposes
        
        for term, purposes in term_appearances.items():
            if len(purposes) >= min_appearances:
                foundational_concepts.append({
                    'term': term,
                    'purposes': purposes,
                    'coverage': len(purposes) / len(purpose_terms),
                    'foundational_score': self._calculate_foundational_score(term, purposes)
                })
        
        # Sort by foundational score
        foundational_concepts.sort(key=lambda x: x['foundational_score'], reverse=True)
        
        return foundational_concepts
    
    def _assess_integration_quality(self, purpose_extractions: Dict[str, Dict], 
                                  integration_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of cross-purpose integration"""
        
        quality_assessment = {
            'integration_completeness': 0.0,
            'balance_across_purposes': 0.0,
            'cross_purpose_coverage': 0.0,
            'semantic_coherence': 0.0,
            'overall_quality': 0.0,
            'quality_issues': [],
            'recommendations': []
        }
        
        # Assess integration completeness
        multi_purpose_count = len(integration_results['multi_purpose_terms']['terms_by_purposes'])
        total_unique_terms = len(set().union(*[
            self._extract_all_terms_by_purpose({k: v})[k.replace('_terms', '')] 
            for k, v in purpose_extractions.items() 
            if k.endswith('_terms')
        ]))
        
        quality_assessment['integration_completeness'] = min(1.0, multi_purpose_count / max(1, total_unique_terms * 0.3))
        
        # Assess balance across purposes
        purpose_term_counts = {}
        for purpose_key, extraction in purpose_extractions.items():
            if purpose_key.endswith('_terms'):
                purpose = purpose_key.replace('_terms', '')
                count = sum(len(terms) if isinstance(terms, list) else 0 
                           for terms in extraction.values() if isinstance(terms, list))
                purpose_term_counts[purpose] = count
        
        if purpose_term_counts:
            max_count = max(purpose_term_counts.values())
            min_count = min(purpose_term_counts.values())
            quality_assessment['balance_across_purposes'] = min_count / max_count if max_count > 0 else 0.0
        
        # Assess cross-purpose coverage
        high_integration_count = len(integration_results['multi_purpose_terms']['high_integration_terms'])
        quality_assessment['cross_purpose_coverage'] = min(1.0, high_integration_count / max(1, len(purpose_extractions)))
        
        # Assess semantic coherence
        bridge_count = sum(len(bridges) for bridges in integration_results['semantic_bridges'].values())
        quality_assessment['semantic_coherence'] = min(1.0, bridge_count / max(1, total_unique_terms * 0.1))
        
        # Calculate overall quality
        quality_scores = [
            quality_assessment['integration_completeness'],
            quality_assessment['balance_across_purposes'],
            quality_assessment['cross_purpose_coverage'],
            quality_assessment['semantic_coherence']
        ]
        quality_assessment['overall_quality'] = sum(quality_scores) / len(quality_scores)
        
        # Identify quality issues and recommendations
        if quality_assessment['integration_completeness'] < 0.5:
            quality_assessment['quality_issues'].append("Low integration completeness")
            quality_assessment['recommendations'].append("Increase identification of multi-purpose terms")
        
        if quality_assessment['balance_across_purposes'] < 0.7:
            quality_assessment['quality_issues'].append("Imbalanced extraction across purposes")
            quality_assessment['recommendations'].append("Improve balance in vocabulary extraction")
        
        if quality_assessment['cross_purpose_coverage'] < 0.4:
            quality_assessment['quality_issues'].append("Limited cross-purpose coverage")
            quality_assessment['recommendations'].append("Enhance identification of terms serving multiple purposes")
        
        return quality_assessment
    
    def _classify_integration_strength(self, overlap_count: int, jaccard_similarity: float) -> str:
        """Classify the strength of integration between two purposes"""
        
        if jaccard_similarity >= 0.3 or overlap_count >= 10:
            return "Strong"
        elif jaccard_similarity >= 0.15 or overlap_count >= 5:
            return "Moderate"
        elif jaccard_similarity >= 0.05 or overlap_count >= 2:
            return "Weak"
        else:
            return "Minimal"
    
    def _calculate_overall_integration_strength(self, similarities: List[float]) -> str:
        """Calculate overall integration strength across all purposes"""
        
        if not similarities:
            return "No Integration"
        
        avg_similarity = sum(similarities) / len(similarities)
        
        if avg_similarity >= 0.25:
            return "High Integration"
        elif avg_similarity >= 0.15:
            return "Moderate Integration"
        elif avg_similarity >= 0.05:
            return "Low Integration"
        else:
            return "Minimal Integration"
    
    def _calculate_foundational_score(self, term: str, purposes: List[str]) -> float:
        """Calculate foundational score for a term"""
        
        # Base score from purpose coverage
        coverage_score = len(purposes) / len(self.purposes)
        
        # Bonus for being in semantic bridges
        bridge_bonus = 0.0
        term_lower = term.lower()
        
        for bridge_type, bridge_terms in self.semantic_bridges.items():
            if any(bridge_term in term_lower for bridge_term in bridge_terms):
                bridge_bonus += 0.2
                break
        
        # Bonus for term complexity (compound terms often more foundational)
        complexity_bonus = 0.1 if len(term.split()) > 1 else 0.0
        
        return min(1.0, coverage_score + bridge_bonus + complexity_bonus)
    
    def generate_integration_report(self, integration_results: Dict[str, Any]) -> str:
        """Generate a comprehensive integration report"""
        
        report = "=== CROSS-PURPOSE INTEGRATION REPORT ===\n\n"
        
        # Multi-purpose terms summary
        multi_purpose = integration_results['multi_purpose_terms']
        report += f"MULTI-PURPOSE TERMS ANALYSIS:\n"
        report += f"- Total multi-purpose terms: {len(multi_purpose['terms_by_purposes'])}\n"
        report += f"- High integration terms (3+ purposes): {len(multi_purpose['high_integration_terms'])}\n"
        
        if multi_purpose['high_integration_terms']:
            report += f"- Examples: {', '.join(multi_purpose['high_integration_terms'][:5])}\n"
        
        report += "\n"
        
        # Purpose pairs analysis
        pairs = integration_results['purpose_pairs_analysis']
        report += "PURPOSE PAIR RELATIONSHIPS:\n"
        
        strong_pairs = [pair for pair, data in pairs.items() if data['strength'] == 'Strong']
        if strong_pairs:
            report += f"- Strong integration pairs: {', '.join(strong_pairs)}\n"
        
        report += f"- Average pair similarity: {sum(data['jaccard_similarity'] for data in pairs.values()) / len(pairs):.3f}\n\n"
        
        # Semantic bridges
        bridges = integration_results['semantic_bridges']
        report += "SEMANTIC BRIDGES:\n"
        report += f"- Foundational bridges: {len(bridges['foundational_bridges'])}\n"
        report += f"- Methodological bridges: {len(bridges['methodological_bridges'])}\n"
        report += f"- Operational bridges: {len(bridges['operational_bridges'])}\n"
        report += f"- Custom bridges: {len(bridges['custom_bridges'])}\n\n"
        
        # Integration quality
        quality = integration_results['integration_quality']
        report += "INTEGRATION QUALITY ASSESSMENT:\n"
        report += f"- Overall quality: {quality['overall_quality']:.3f}\n"
        report += f"- Integration completeness: {quality['integration_completeness']:.3f}\n"
        report += f"- Purpose balance: {quality['balance_across_purposes']:.3f}\n"
        report += f"- Cross-purpose coverage: {quality['cross_purpose_coverage']:.3f}\n"
        
        if quality['quality_issues']:
            report += f"\nQuality Issues:\n"
            for issue in quality['quality_issues']:
                report += f"- {issue}\n"
        
        if quality['recommendations']:
            report += f"\nRecommendations:\n"
            for rec in quality['recommendations']:
                report += f"- {rec}\n"
        
        return report


def main():
    """Demonstration of cross-purpose integration"""
    
    # Sample purpose extractions
    sample_extractions = {
        'descriptive_terms': {
            'categories': ['theory', 'framework', 'model', 'classification'],
            'attributes': ['variable', 'factor', 'characteristic']
        },
        'explanatory_terms': {
            'mechanisms': ['process', 'system', 'framework', 'interaction'],
            'structures': ['component', 'element', 'relationship']
        },
        'predictive_terms': {
            'variables': ['factor', 'indicator', 'measure', 'variable'],
            'models': ['model', 'equation', 'framework']
        },
        'causal_terms': {
            'relationships': ['cause', 'effect', 'relationship', 'pathway'],
            'factors': ['determinant', 'factor', 'influence']
        },
        'intervention_terms': {
            'strategies': ['intervention', 'strategy', 'approach', 'method'],
            'tools': ['technique', 'tool', 'procedure']
        }
    }
    
    # Initialize integrator
    integrator = CrossPurposeIntegrator()
    
    # Perform integration
    integration_results = integrator.integrate_cross_purpose_terms(sample_extractions)
    
    # Generate report
    report = integrator.generate_integration_report(integration_results)
    print(report)


if __name__ == "__main__":
    main()