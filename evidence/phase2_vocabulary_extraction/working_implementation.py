#!/usr/bin/env python3
"""
Working Implementation Demonstration for Multi-Purpose Vocabulary Extraction

This script demonstrates the complete multi-purpose vocabulary extraction system
with balanced extraction across all five theoretical purposes.
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vocabulary_extractor import MultiPurposeVocabularyExtractor
from extraction_prompts import BalancedExtractionPrompts
from cross_purpose_integration import CrossPurposeIntegrator


class WorkingImplementationDemo:
    """Demonstrates complete multi-purpose vocabulary extraction workflow"""
    
    def __init__(self):
        """Initialize the demonstration components"""
        self.extractor = MultiPurposeVocabularyExtractor()
        self.prompt_generator = BalancedExtractionPrompts()
        self.integrator = CrossPurposeIntegrator()
        
        self.demo_theories = self._load_demo_theories()
        self.results = {}
    
    def _load_demo_theories(self) -> Dict[str, str]:
        """Load demonstration theories for testing"""
        return {
            'social_cognitive_theory': """
            Social cognitive theory, developed by Albert Bandura, provides a comprehensive framework 
            for understanding human behavior through the dynamic interaction of personal, behavioral, 
            and environmental factors. This triadic reciprocal causation model explains how individuals 
            learn and modify behaviors through complex interplay between cognitive processes, behavioral 
            patterns, and environmental influences.
            
            The theory categorizes learning mechanisms into several distinct types: observational learning 
            (modeling), direct experience through trial and error, and symbolic modeling through media 
            and cultural representations. Each mechanism contributes differently to skill acquisition 
            and behavioral change processes.
            
            Key variables in the framework include self-efficacy (belief in one's capability to perform 
            behaviors), outcome expectations (anticipated consequences of actions), and behavioral capability 
            (actual skills and knowledge required). These factors work together to predict behavioral 
            engagement and persistence in the face of challenges.
            
            Causal pathways demonstrate how environmental factors influence personal cognitions and 
            emotional states, which in turn affect behavioral choices and outcomes. The theory reveals 
            bidirectional relationships where behavior also influences both personal factors and 
            environmental conditions, creating dynamic feedback loops.
            
            Interventions based on social cognitive theory typically focus on enhancing self-efficacy 
            through four primary sources: mastery experiences (successful performance), vicarious 
            learning (observing others succeed), verbal persuasion (encouragement and coaching), 
            and emotional arousal management (controlling anxiety and stress responses). These 
            intervention strategies have been successfully applied across domains including health 
            behavior change, educational achievement, and organizational performance improvement.
            """,
            
            'systems_theory': """
            General systems theory provides a meta-theoretical framework for understanding complex 
            phenomena as interconnected networks of components operating within defined boundaries. 
            The theory emerged as a response to reductionist approaches that failed to capture 
            emergent properties arising from system-level interactions.
            
            Systems classification distinguishes between open systems (exchanging matter, energy, 
            and information with environment), closed systems (energy exchange only), and isolated 
            systems (no exchange). Additional typologies include natural versus artificial systems, 
            simple versus complex systems, and adaptive versus non-adaptive systems. Each type 
            exhibits distinct characteristics and behavioral patterns.
            
            Critical indicators of system functioning include input-throughput-output relationships, 
            feedback mechanisms (both positive and negative), homeostatic processes, boundary 
            maintenance, and adaptive capacity. These measures enable assessment of system health, 
            stability, and performance over time.
            
            Predictive models derived from systems theory forecast system behavior based on initial 
            conditions, system structure, and environmental pressures. Mathematical approaches include 
            differential equations for continuous systems, difference equations for discrete systems, 
            and agent-based models for complex adaptive systems. These models help anticipate system 
            responses to various perturbations and interventions.
            
            Causal analysis in systems theory reveals how disturbances propagate through interconnected 
            subsystems via multiple pathways. Unlike linear causation, systems exhibit circular 
            causality where effects can become causes through feedback loops. This understanding 
            enables identification of leverage points where small changes can produce significant 
            system-wide transformations.
            
            Intervention strategies focus on system redesign, boundary modification, feedback loop 
            adjustment, and capacity building. Successful interventions often target structural 
            elements rather than individual components, recognizing that system-level changes are 
            more sustainable than component-level modifications.
            """,
            
            'complexity_theory': """
            Complexity theory analyzes emergent properties and nonlinear dynamics in systems where 
            collective behavior cannot be predicted from individual component properties. The framework 
            distinguishes between complicated systems (many parts but predictable relationships) and 
            complex systems (nonlinear interactions producing unpredictable emergent phenomena).
            
            The theory establishes taxonomies of complexity including deterministic chaos (sensitive 
            dependence on initial conditions), stochastic complexity (random elements), and edge-of-chaos 
            dynamics (transition zones between order and disorder). These classifications help identify 
            appropriate analytical approaches for different system types.
            
            Key variables influencing complex system behavior include agent diversity, connectivity 
            patterns, interaction rules, adaptive capacity, and environmental variability. These factors 
            combine to determine whether systems exhibit stable attractors, periodic oscillations, 
            chaotic dynamics, or phase transitions between different behavioral regimes.
            
            Predictive capabilities in complex systems are fundamentally limited due to sensitive 
            dependence on initial conditions and nonlinear amplification of small perturbations. 
            However, pattern recognition enables identification of attractor states, bifurcation points, 
            and phase transition indicators. Statistical approaches focus on probability distributions 
            rather than deterministic forecasts.
            
            Causal relationships in complex systems are typically circular, multi-directional, and 
            context-dependent rather than linear and universal. Multiple causation pathways can lead 
            to similar outcomes (equifinality), while identical causes can produce different effects 
            depending on system state and history (multifinality). This challenges traditional 
            cause-effect thinking.
            
            Intervention approaches emphasize creating conditions for positive emergence rather than 
            direct control mechanisms. Strategies include enhancing system resilience, promoting 
            adaptive capacity, facilitating self-organization processes, and designing evolutionary 
            pressures that favor desired outcomes. These approaches recognize that complex systems 
            cannot be controlled but can be influenced through skillful perturbations.
            """
        }
    
    def run_complete_demonstration(self) -> Dict[str, Any]:
        """Run complete demonstration of multi-purpose vocabulary extraction"""
        print("=== MULTI-PURPOSE VOCABULARY EXTRACTION DEMONSTRATION ===\n")
        
        demo_results = {
            'timestamp': datetime.now().isoformat(),
            'theories_processed': list(self.demo_theories.keys()),
            'extraction_results': {},
            'integration_analysis': {},
            'balance_assessment': {},
            'cross_purpose_findings': {},
            'demonstration_summary': {}
        }
        
        # Process each theory
        for theory_name, theory_text in self.demo_theories.items():
            print(f"Processing {theory_name.replace('_', ' ').title()}...")
            
            # Extract vocabulary for all purposes
            extraction_result = self.extractor.extract_comprehensive_vocabulary(theory_text)
            demo_results['extraction_results'][theory_name] = extraction_result
            
            # Analyze cross-purpose integration
            purpose_extractions = {k: v for k, v in extraction_result.items() if k.endswith('_terms')}
            integration_result = self.integrator.integrate_cross_purpose_terms(purpose_extractions)
            demo_results['integration_analysis'][theory_name] = integration_result
            
            # Display results summary
            self._display_theory_results(theory_name, extraction_result, integration_result)
        
        # Perform cross-theory analysis
        demo_results['balance_assessment'] = self._assess_overall_balance(demo_results['extraction_results'])
        demo_results['cross_purpose_findings'] = self._analyze_cross_purpose_patterns(demo_results['integration_analysis'])
        demo_results['demonstration_summary'] = self._generate_demonstration_summary(demo_results)
        
        self.results = demo_results
        return demo_results
    
    def _display_theory_results(self, theory_name: str, extraction_result: Dict[str, Any], 
                               integration_result: Dict[str, Any]):
        """Display results for a single theory"""
        print(f"\n--- {theory_name.replace('_', ' ').title()} Results ---")
        
        # Purpose-wise extraction summary
        purpose_counts = {}
        for purpose_key, purpose_data in extraction_result.items():
            if purpose_key.endswith('_terms') and isinstance(purpose_data, dict):
                purpose = purpose_key.replace('_terms', '')
                count = sum(len(terms) if isinstance(terms, list) else 0 
                          for terms in purpose_data.values())
                purpose_counts[purpose] = count
        
        print("Vocabulary extraction by purpose:")
        for purpose, count in purpose_counts.items():
            print(f"  {purpose.capitalize()}: {count} terms")
        
        # Balance assessment
        if 'extraction_balance' in extraction_result:
            balance = extraction_result['extraction_balance']
            print(f"Balance ratio: {balance.get('balance_ratio', 0):.3f}")
            print(f"Is balanced: {balance.get('is_balanced', False)}")
        
        # Cross-purpose analysis
        if 'multi_purpose_terms' in integration_result:
            multi_purpose = integration_result['multi_purpose_terms']
            print(f"Multi-purpose terms: {len(multi_purpose.get('terms_by_purposes', {}))}")
            print(f"High integration terms: {len(multi_purpose.get('high_integration_terms', []))}")
        
        # Integration quality
        if 'integration_quality' in integration_result:
            quality = integration_result['integration_quality']
            print(f"Integration quality: {quality.get('overall_quality', 0):.3f}")
        
        print()
    
    def _assess_overall_balance(self, extraction_results: Dict[str, Dict]) -> Dict[str, Any]:
        """Assess balance across all theories"""
        print("=== OVERALL BALANCE ASSESSMENT ===")
        
        # Aggregate purpose counts across all theories
        aggregate_counts = {'descriptive': 0, 'explanatory': 0, 'predictive': 0, 'causal': 0, 'intervention': 0}
        theory_balances = {}
        
        for theory_name, result in extraction_results.items():
            if 'extraction_balance' in result and 'purpose_counts' in result['extraction_balance']:
                purpose_counts = result['extraction_balance']['purpose_counts']
                theory_balances[theory_name] = purpose_counts
                
                for purpose, count in purpose_counts.items():
                    if purpose in aggregate_counts:
                        aggregate_counts[purpose] += count
        
        # Calculate overall balance metrics
        if any(count > 0 for count in aggregate_counts.values()):
            max_count = max(aggregate_counts.values())
            min_count = min(count for count in aggregate_counts.values() if count > 0)
            overall_balance_ratio = min_count / max_count if max_count > 0 else 0.0
        else:
            overall_balance_ratio = 0.0
        
        balance_assessment = {
            'aggregate_counts': aggregate_counts,
            'theory_balances': theory_balances,
            'overall_balance_ratio': overall_balance_ratio,
            'is_system_balanced': overall_balance_ratio > 0.7,
            'balance_quality': self._classify_balance_quality(overall_balance_ratio)
        }
        
        print(f"Aggregate purpose counts: {aggregate_counts}")
        print(f"Overall balance ratio: {overall_balance_ratio:.3f}")
        print(f"System balanced: {balance_assessment['is_system_balanced']}")
        print(f"Balance quality: {balance_assessment['balance_quality']}")
        print()
        
        return balance_assessment
    
    def _analyze_cross_purpose_patterns(self, integration_analyses: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze cross-purpose patterns across theories"""
        print("=== CROSS-PURPOSE PATTERN ANALYSIS ===")
        
        # Aggregate cross-purpose findings
        all_multi_purpose_terms = set()
        all_high_integration_terms = set()
        purpose_pair_strengths = {}
        
        for theory_name, integration in integration_analyses.items():
            if 'multi_purpose_terms' in integration:
                multi_purpose = integration['multi_purpose_terms']
                
                # Collect multi-purpose terms
                if 'terms_by_purposes' in multi_purpose:
                    all_multi_purpose_terms.update(multi_purpose['terms_by_purposes'].keys())
                
                # Collect high integration terms
                if 'high_integration_terms' in multi_purpose:
                    all_high_integration_terms.update(multi_purpose['high_integration_terms'])
            
            # Collect purpose pair strengths
            if 'purpose_pairs_analysis' in integration:
                pairs = integration['purpose_pairs_analysis']
                for pair_key, pair_data in pairs.items():
                    if pair_key not in purpose_pair_strengths:
                        purpose_pair_strengths[pair_key] = []
                    purpose_pair_strengths[pair_key].append(pair_data.get('jaccard_similarity', 0))
        
        # Calculate average pair strengths
        average_pair_strengths = {}
        for pair_key, similarities in purpose_pair_strengths.items():
            average_pair_strengths[pair_key] = sum(similarities) / len(similarities) if similarities else 0.0
        
        cross_purpose_patterns = {
            'total_multi_purpose_terms': len(all_multi_purpose_terms),
            'total_high_integration_terms': len(all_high_integration_terms),
            'sample_multi_purpose_terms': list(all_multi_purpose_terms)[:10],
            'sample_high_integration_terms': list(all_high_integration_terms)[:10],
            'average_pair_strengths': average_pair_strengths,
            'strongest_pairs': sorted(average_pair_strengths.items(), key=lambda x: x[1], reverse=True)[:3],
            'cross_purpose_quality': self._assess_cross_purpose_quality(all_multi_purpose_terms, all_high_integration_terms)
        }
        
        print(f"Total multi-purpose terms across theories: {len(all_multi_purpose_terms)}")
        print(f"Total high integration terms: {len(all_high_integration_terms)}")
        
        if cross_purpose_patterns['strongest_pairs']:
            print("Strongest purpose pairs:")
            for pair, strength in cross_purpose_patterns['strongest_pairs']:
                print(f"  {pair}: {strength:.3f}")
        
        print(f"Cross-purpose quality: {cross_purpose_patterns['cross_purpose_quality']}")
        print()
        
        return cross_purpose_patterns
    
    def _classify_balance_quality(self, balance_ratio: float) -> str:
        """Classify balance quality based on ratio"""
        if balance_ratio >= 0.8:
            return "Excellent"
        elif balance_ratio >= 0.7:
            return "Good"
        elif balance_ratio >= 0.5:
            return "Fair"
        elif balance_ratio >= 0.3:
            return "Poor"
        else:
            return "Very Poor"
    
    def _assess_cross_purpose_quality(self, multi_purpose_terms: set, high_integration_terms: set) -> str:
        """Assess overall cross-purpose integration quality"""
        if len(high_integration_terms) >= 5 and len(multi_purpose_terms) >= 15:
            return "Excellent"
        elif len(high_integration_terms) >= 3 and len(multi_purpose_terms) >= 10:
            return "Good"
        elif len(high_integration_terms) >= 2 and len(multi_purpose_terms) >= 5:
            return "Fair"
        elif len(multi_purpose_terms) >= 3:
            return "Poor"
        else:
            return "Very Poor"
    
    def _generate_demonstration_summary(self, demo_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive demonstration summary"""
        print("=== DEMONSTRATION SUMMARY ===")
        
        theories_count = len(demo_results['theories_processed'])
        
        # Calculate success metrics
        balanced_theories = 0
        total_terms_extracted = 0
        total_multi_purpose_terms = 0
        
        for theory_name in demo_results['theories_processed']:
            # Check balance
            if theory_name in demo_results['extraction_results']:
                extraction = demo_results['extraction_results'][theory_name]
                if 'extraction_balance' in extraction:
                    balance = extraction['extraction_balance']
                    if balance.get('is_balanced', False):
                        balanced_theories += 1
                
                # Count terms
                for purpose_key, purpose_data in extraction.items():
                    if purpose_key.endswith('_terms') and isinstance(purpose_data, dict):
                        for terms in purpose_data.values():
                            if isinstance(terms, list):
                                total_terms_extracted += len(terms)
            
            # Count multi-purpose terms
            if theory_name in demo_results['integration_analysis']:
                integration = demo_results['integration_analysis'][theory_name]
                if 'multi_purpose_terms' in integration:
                    multi_purpose = integration['multi_purpose_terms']
                    if 'terms_by_purposes' in multi_purpose:
                        total_multi_purpose_terms += len(multi_purpose['terms_by_purposes'])
        
        # Overall assessment
        balance_success_rate = balanced_theories / theories_count if theories_count > 0 else 0.0
        overall_balance_ratio = demo_results['balance_assessment'].get('overall_balance_ratio', 0.0)
        cross_purpose_quality = demo_results['cross_purpose_findings'].get('cross_purpose_quality', 'Unknown')
        
        summary = {
            'theories_processed': theories_count,
            'balanced_theories': balanced_theories,
            'balance_success_rate': balance_success_rate,
            'total_terms_extracted': total_terms_extracted,
            'total_multi_purpose_terms': total_multi_purpose_terms,
            'overall_balance_ratio': overall_balance_ratio,
            'cross_purpose_quality': cross_purpose_quality,
            'demonstration_success': self._assess_demonstration_success(balance_success_rate, overall_balance_ratio, cross_purpose_quality),
            'key_achievements': self._identify_key_achievements(demo_results),
            'areas_for_improvement': self._identify_improvements(demo_results)
        }
        
        print(f"Theories processed: {theories_count}")
        print(f"Balanced theories: {balanced_theories}/{theories_count} ({balance_success_rate:.1%})")
        print(f"Total terms extracted: {total_terms_extracted}")
        print(f"Multi-purpose terms: {total_multi_purpose_terms}")
        print(f"Overall balance ratio: {overall_balance_ratio:.3f}")
        print(f"Cross-purpose quality: {cross_purpose_quality}")
        print(f"Demonstration success: {summary['demonstration_success']}")
        
        if summary['key_achievements']:
            print("Key achievements:")
            for achievement in summary['key_achievements']:
                print(f"  - {achievement}")
        
        if summary['areas_for_improvement']:
            print("Areas for improvement:")
            for improvement in summary['areas_for_improvement']:
                print(f"  - {improvement}")
        
        return summary
    
    def _assess_demonstration_success(self, balance_success_rate: float, overall_balance_ratio: float, 
                                    cross_purpose_quality: str) -> str:
        """Assess overall demonstration success"""
        success_score = 0
        
        # Balance success component
        if balance_success_rate >= 0.8:
            success_score += 3
        elif balance_success_rate >= 0.6:
            success_score += 2
        elif balance_success_rate >= 0.4:
            success_score += 1
        
        # Overall balance component
        if overall_balance_ratio >= 0.7:
            success_score += 3
        elif overall_balance_ratio >= 0.5:
            success_score += 2
        elif overall_balance_ratio >= 0.3:
            success_score += 1
        
        # Cross-purpose quality component
        quality_scores = {'Excellent': 3, 'Good': 2, 'Fair': 1, 'Poor': 0, 'Very Poor': 0}
        success_score += quality_scores.get(cross_purpose_quality, 0)
        
        # Convert to qualitative assessment
        if success_score >= 8:
            return "Excellent"
        elif success_score >= 6:
            return "Good"
        elif success_score >= 4:
            return "Fair"
        elif success_score >= 2:
            return "Poor"
        else:
            return "Failed"
    
    def _identify_key_achievements(self, demo_results: Dict[str, Any]) -> List[str]:
        """Identify key achievements from demonstration"""
        achievements = []
        
        # Check balance achievement
        balance_ratio = demo_results['balance_assessment'].get('overall_balance_ratio', 0.0)
        if balance_ratio > 0.7:
            achievements.append("Achieved excellent balance across all five theoretical purposes")
        elif balance_ratio > 0.5:
            achievements.append("Achieved good balance across theoretical purposes")
        
        # Check cross-purpose achievement
        cross_purpose_count = demo_results['cross_purpose_findings'].get('total_multi_purpose_terms', 0)
        if cross_purpose_count >= 15:
            achievements.append("Successfully identified extensive cross-purpose vocabulary")
        elif cross_purpose_count >= 10:
            achievements.append("Identified significant cross-purpose vocabulary")
        
        # Check comprehensiveness
        total_theories = len(demo_results['theories_processed'])
        if total_theories >= 3:
            achievements.append("Demonstrated system robustness across multiple theory types")
        
        # Check integration quality
        quality = demo_results['cross_purpose_findings'].get('cross_purpose_quality', 'Unknown')
        if quality in ['Excellent', 'Good']:
            achievements.append("Achieved high-quality cross-purpose integration")
        
        return achievements
    
    def _identify_improvements(self, demo_results: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement"""
        improvements = []
        
        # Check balance issues
        balance_ratio = demo_results['balance_assessment'].get('overall_balance_ratio', 0.0)
        if balance_ratio < 0.5:
            improvements.append("Improve balance between theoretical purposes")
        
        # Check success rate
        balanced_count = 0
        total_count = len(demo_results['theories_processed'])
        for theory_name in demo_results['theories_processed']:
            if theory_name in demo_results['extraction_results']:
                extraction = demo_results['extraction_results'][theory_name]
                if 'extraction_balance' in extraction:
                    if extraction['extraction_balance'].get('is_balanced', False):
                        balanced_count += 1
        
        if balanced_count / total_count < 0.8:
            improvements.append("Increase consistency of balanced extraction across theories")
        
        # Check cross-purpose quality
        quality = demo_results['cross_purpose_findings'].get('cross_purpose_quality', 'Unknown')
        if quality in ['Poor', 'Very Poor']:
            improvements.append("Enhance cross-purpose term identification and integration")
        
        return improvements
    
    def save_results(self, filepath: str = None) -> str:
        """Save demonstration results to file"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"working_implementation_results_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filepath)
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        return filepath
    
    def generate_prompt_examples(self) -> Dict[str, str]:
        """Generate example prompts for demonstration"""
        sample_text = list(self.demo_theories.values())[0][:500] + "..."
        
        examples = {}
        
        # Comprehensive prompt
        examples['comprehensive_prompt'] = self.prompt_generator.get_comprehensive_extraction_prompt(sample_text)
        
        # Purpose-specific prompts
        for purpose in ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']:
            examples[f'{purpose}_prompt'] = self.prompt_generator.get_purpose_specific_prompt(purpose, sample_text)
        
        # Balance validation prompt
        sample_results = {
            'descriptive_terms': {'categories': ['theory', 'framework']},
            'explanatory_terms': {'mechanisms': ['process', 'system']},
            'predictive_terms': {'variables': ['factor', 'variable']},
            'causal_terms': {'relationships': ['cause', 'effect']},
            'intervention_terms': {'strategies': ['intervention', 'approach']}
        }
        examples['balance_validation_prompt'] = self.prompt_generator.get_balance_validation_prompt(sample_results)
        
        return examples


def main():
    """Main demonstration function"""
    print("Multi-Purpose Vocabulary Extraction - Working Implementation Demo")
    print("=" * 70)
    
    # Initialize demonstration
    demo = WorkingImplementationDemo()
    
    # Run complete demonstration
    results = demo.run_complete_demonstration()
    
    # Save results
    results_file = demo.save_results()
    print(f"\nResults saved to: {results_file}")
    
    # Generate prompt examples
    print("\n=== PROMPT EXAMPLES ===")
    prompt_examples = demo.generate_prompt_examples()
    print(f"Generated {len(prompt_examples)} example prompts")
    
    # Final assessment
    demonstration_success = results['demonstration_summary']['demonstration_success']
    print(f"\n=== FINAL ASSESSMENT ===")
    print(f"Demonstration Success: {demonstration_success}")
    
    if demonstration_success in ['Excellent', 'Good']:
        print("✓ Multi-purpose vocabulary extraction system working successfully")
        print("✓ Balanced extraction across all five theoretical purposes achieved")
        print("✓ Cross-purpose integration functioning properly")
    else:
        print("⚠ System needs improvement in balanced extraction")
        print("⚠ Review balance assessment and cross-purpose integration")
    
    return results, demonstration_success in ['Excellent', 'Good']


if __name__ == "__main__":
    results, success = main()
    exit(0 if success else 1)