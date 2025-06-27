#!/usr/bin/env python3
"""
Balanced Extraction Prompts for Multi-Purpose Vocabulary Extraction

This module provides carefully balanced prompts that give equal attention to all five 
theoretical purposes: descriptive, explanatory, predictive, causal, and intervention.
"""

from typing import Dict, List, Any
import json


class BalancedExtractionPrompts:
    """Provides balanced prompts for multi-purpose vocabulary extraction"""
    
    def __init__(self):
        """Initialize balanced extraction prompts"""
        self.base_instructions = self._create_base_instructions()
        self.purpose_prompts = self._create_purpose_specific_prompts()
        self.integration_prompts = self._create_integration_prompts()
    
    def _create_base_instructions(self) -> str:
        """Create base instructions emphasizing balance across all purposes"""
        return """
        You are extracting theoretical vocabulary for academic analysis. Your task is to 
        identify terms that support ALL FIVE theoretical purposes with EQUAL attention:
        
        1. DESCRIPTIVE: Terms for classification, categorization, and taxonomy
        2. EXPLANATORY: Terms for mechanisms, processes, and understanding  
        3. PREDICTIVE: Terms for forecasting, modeling, and projection
        4. CAUSAL: Terms for relationships, pathways, and dependencies
        5. INTERVENTION: Terms for actions, strategies, and implementations
        
        CRITICAL BALANCE REQUIREMENT: Extract vocabulary comprehensively for each purpose.
        Do not over-emphasize any single purpose. Maintain equal depth and breadth across
        all five analytical approaches.
        """
    
    def _create_purpose_specific_prompts(self) -> Dict[str, str]:
        """Create balanced prompts for each theoretical purpose"""
        return {
            'descriptive': """
            Extract DESCRIPTIVE vocabulary with the same depth as other purposes:
            
            Focus areas (equal weight to all):
            - Taxonomies and classification systems
            - Categories, types, and typologies  
            - Attributes, properties, and characteristics
            - Structural dimensions and organizational levels
            - Patterns and regularities in phenomena
            - Definitional and conceptual frameworks
            
            Extract terms that enable:
            - Systematic categorization of phenomena
            - Identification of patterns and regularities
            - Structural organization of concepts
            - Dimensional analysis of attributes
            - Hierarchical classification systems
            
            Maintain equal comprehensiveness with explanatory, predictive, causal, 
            and intervention vocabulary extraction.
            """,
            
            'explanatory': """
            Extract EXPLANATORY vocabulary with the same depth as other purposes:
            
            Focus areas (equal weight to all):
            - Mechanisms and underlying processes
            - Systems and systemic interactions
            - Functional relationships and operations
            - Structural components and elements
            - Theoretical frameworks and principles
            - Process sequences and procedural flows
            
            Extract terms that enable:
            - Understanding of how phenomena work
            - Identification of underlying mechanisms
            - Analysis of systemic interactions
            - Comprehension of functional relationships
            - Theoretical explanation of observations
            
            Maintain equal comprehensiveness with descriptive, predictive, causal, 
            and intervention vocabulary extraction.
            """,
            
            'predictive': """
            Extract PREDICTIVE vocabulary with the same depth as other purposes:
            
            Focus areas (equal weight to all):
            - Variables and measurable factors
            - Models and forecasting frameworks
            - Indicators and predictive measures
            - Statistical and mathematical terms
            - Trend analysis and projection methods
            - Probability and risk assessment terms
            
            Extract terms that enable:
            - Forecasting of future states
            - Quantitative modeling and analysis
            - Variable identification and measurement
            - Trend analysis and projection
            - Risk and probability assessment
            
            Maintain equal comprehensiveness with descriptive, explanatory, causal, 
            and intervention vocabulary extraction.
            """,
            
            'causal': """
            Extract CAUSAL vocabulary with the same depth as other purposes:
            
            Focus areas (equal weight to all):
            - Causal relationships and dependencies
            - Pathways and causal chains
            - Mediating and moderating factors
            - Determinants and driving forces
            - Effects and consequences
            - Causal mechanisms and processes
            
            Extract terms that enable:
            - Identification of cause-effect relationships
            - Analysis of causal pathways and chains
            - Understanding of mediating mechanisms
            - Assessment of causal dependencies
            - Evaluation of determinant factors
            
            Maintain equal comprehensiveness with descriptive, explanatory, predictive, 
            and intervention vocabulary extraction.
            """,
            
            'intervention': """
            Extract INTERVENTION vocabulary with the same depth as other purposes:
            
            Focus areas (equal weight to all):
            - Intervention strategies and approaches
            - Implementation methods and procedures
            - Policy and program frameworks
            - Action-oriented tools and instruments
            - Practice guidelines and protocols
            - Solution frameworks and responses
            
            Extract terms that enable:
            - Design of targeted interventions
            - Implementation of change strategies
            - Development of action plans
            - Application of solution frameworks
            - Policy and program development
            
            Maintain equal comprehensiveness with descriptive, explanatory, predictive, 
            and causal vocabulary extraction.
            """
        }
    
    def _create_integration_prompts(self) -> Dict[str, str]:
        """Create prompts for cross-purpose integration"""
        return {
            'balance_check': """
            Review your extraction results for balance across all five purposes:
            
            BALANCE REQUIREMENTS:
            1. Each purpose should have comparable vocabulary depth
            2. No single purpose should dominate the extraction
            3. Each purpose should receive equal analytical attention
            4. Cross-purpose terms should be properly identified
            5. Overall extraction should support all analytical approaches
            
            EVALUATION CRITERIA:
            - Descriptive terms: Sufficient for comprehensive categorization
            - Explanatory terms: Sufficient for mechanism understanding  
            - Predictive terms: Sufficient for forecasting and modeling
            - Causal terms: Sufficient for relationship analysis
            - Intervention terms: Sufficient for action planning
            
            If any purpose is under-represented, enhance extraction for that area.
            """,
            
            'cross_purpose_identification': """
            Identify terms that serve multiple theoretical purposes:
            
            MULTI-PURPOSE TERM TYPES:
            1. Descriptive-Explanatory: Terms that both categorize and explain
            2. Explanatory-Predictive: Terms that both explain and forecast
            3. Predictive-Causal: Terms that both predict and identify causes
            4. Causal-Intervention: Terms that both identify causes and suggest actions
            5. Cross-cutting concepts: Terms relevant to 3+ purposes
            
            IDENTIFICATION CRITERIA:
            - Terms used in multiple analytical contexts
            - Concepts with multiple theoretical functions
            - Bridge terms connecting different purposes
            - Foundational concepts supporting multiple analyses
            
            Ensure cross-purpose terms maintain their multi-functional nature.
            """,
            
            'comprehensiveness_validation': """
            Validate comprehensive coverage across all theoretical purposes:
            
            COMPREHENSIVENESS CHECKS:
            1. Descriptive completeness: Full taxonomic and categorical coverage
            2. Explanatory completeness: Complete mechanistic understanding
            3. Predictive completeness: Comprehensive forecasting capability
            4. Causal completeness: Full relationship mapping
            5. Intervention completeness: Complete action framework
            
            VALIDATION QUESTIONS:
            - Can the extracted terms support robust descriptive analysis?
            - Can the extracted terms enable deep explanatory understanding?
            - Can the extracted terms facilitate accurate prediction?
            - Can the extracted terms reveal causal relationships?
            - Can the extracted terms guide effective intervention?
            
            Each question should receive equal analytical support.
            """
        }
    
    def get_comprehensive_extraction_prompt(self, theory_text: str) -> str:
        """Generate comprehensive extraction prompt for balanced analysis"""
        
        prompt = f"""
        {self.base_instructions}
        
        THEORY TEXT TO ANALYZE:
        {theory_text}
        
        EXTRACTION REQUIREMENTS:
        
        1. DESCRIPTIVE VOCABULARY (Equal Priority):
        {self.purpose_prompts['descriptive']}
        
        2. EXPLANATORY VOCABULARY (Equal Priority):
        {self.purpose_prompts['explanatory']}
        
        3. PREDICTIVE VOCABULARY (Equal Priority):  
        {self.purpose_prompts['predictive']}
        
        4. CAUSAL VOCABULARY (Equal Priority):
        {self.purpose_prompts['causal']}
        
        5. INTERVENTION VOCABULARY (Equal Priority):
        {self.purpose_prompts['intervention']}
        
        INTEGRATION REQUIREMENTS:
        {self.integration_prompts['cross_purpose_identification']}
        
        BALANCE VALIDATION:
        {self.integration_prompts['balance_check']}
        
        FINAL OUTPUT: Provide vocabulary extraction with equal depth and comprehensiveness
        across all five theoretical purposes. No single purpose should dominate.
        """
        
        return prompt
    
    def get_purpose_specific_prompt(self, purpose: str, theory_text: str) -> str:
        """Generate purpose-specific extraction prompt with balance emphasis"""
        
        if purpose not in self.purpose_prompts:
            raise ValueError(f"Unknown purpose: {purpose}")
        
        prompt = f"""
        {self.base_instructions}
        
        THEORY TEXT TO ANALYZE:
        {theory_text}
        
        FOCUSED EXTRACTION FOR: {purpose.upper()}
        {self.purpose_prompts[purpose]}
        
        BALANCE REMINDER: While focusing on {purpose} vocabulary, maintain awareness
        that this extraction is part of a larger multi-purpose analysis. Extract with
        the same depth and comprehensiveness you would apply to other purposes.
        
        COMPREHENSIVENESS CHECK:
        {self.integration_prompts['comprehensiveness_validation']}
        """
        
        return prompt
    
    def get_balance_validation_prompt(self, extracted_results: Dict[str, Any]) -> str:
        """Generate prompt for validating extraction balance"""
        
        results_summary = self._summarize_extraction_results(extracted_results)
        
        prompt = f"""
        {self.base_instructions}
        
        EXTRACTION RESULTS TO VALIDATE:
        {results_summary}
        
        BALANCE VALIDATION TASK:
        {self.integration_prompts['balance_check']}
        
        SPECIFIC VALIDATION REQUIREMENTS:
        1. Compare term counts across purposes (should be relatively equal)
        2. Assess depth of extraction for each purpose
        3. Identify any over-emphasized or under-emphasized purposes
        4. Verify cross-purpose term identification
        5. Ensure each purpose can support robust analysis
        
        PROVIDE:
        - Balance assessment (balanced/imbalanced)
        - Specific recommendations for improvement
        - Revised extraction if needed to achieve balance
        """
        
        return prompt
    
    def _summarize_extraction_results(self, results: Dict[str, Any]) -> str:
        """Create summary of extraction results for validation"""
        
        summary = "EXTRACTION RESULTS SUMMARY:\n"
        
        for purpose_key, terms_dict in results.items():
            if purpose_key.endswith('_terms') and isinstance(terms_dict, dict):
                purpose = purpose_key.replace('_terms', '').upper()
                term_count = sum(
                    len(term_list) if isinstance(term_list, list) else 0
                    for term_list in terms_dict.values()
                )
                
                summary += f"\n{purpose}: {term_count} terms across {len(terms_dict)} categories"
                for category, term_list in terms_dict.items():
                    if isinstance(term_list, list) and term_list:
                        summary += f"\n  - {category}: {len(term_list)} terms"
        
        if 'extraction_balance' in results:
            balance = results['extraction_balance']
            summary += f"\n\nBALANCE METRICS:"
            summary += f"\n  - Balance ratio: {balance.get('balance_ratio', 'N/A')}"
            summary += f"\n  - Is balanced: {balance.get('is_balanced', 'N/A')}"
        
        return summary
    
    def get_cross_purpose_integration_prompt(self, all_extractions: Dict[str, Dict]) -> str:
        """Generate prompt for integrating cross-purpose terms"""
        
        prompt = f"""
        {self.base_instructions}
        
        CROSS-PURPOSE INTEGRATION TASK:
        You have extracted vocabulary for each theoretical purpose separately.
        Now integrate these extractions to identify cross-purpose relationships.
        
        ALL EXTRACTIONS:
        {json.dumps(all_extractions, indent=2)}
        
        INTEGRATION REQUIREMENTS:
        {self.integration_prompts['cross_purpose_identification']}
        
        SPECIFIC TASKS:
        1. Identify terms appearing in multiple purpose extractions
        2. Classify multi-purpose terms by their functional roles
        3. Map relationships between purpose-specific vocabularies
        4. Identify bridging concepts that connect different purposes
        5. Validate that integration maintains balanced representation
        
        FINAL VALIDATION:
        {self.integration_prompts['comprehensiveness_validation']}
        """
        
        return prompt


def main():
    """Demonstration of balanced extraction prompts"""
    
    # Sample theory text
    sample_text = """
    Social cognitive theory explains behavior through the dynamic interaction of personal, 
    behavioral, and environmental factors. The theory categorizes learning mechanisms into 
    observational learning, direct experience, and symbolic modeling.
    """
    
    # Initialize prompt generator
    prompt_generator = BalancedExtractionPrompts()
    
    # Generate comprehensive extraction prompt
    comprehensive_prompt = prompt_generator.get_comprehensive_extraction_prompt(sample_text)
    
    print("=== COMPREHENSIVE EXTRACTION PROMPT ===")
    print(comprehensive_prompt[:1000] + "..." if len(comprehensive_prompt) > 1000 else comprehensive_prompt)
    print()
    
    # Generate purpose-specific prompt
    descriptive_prompt = prompt_generator.get_purpose_specific_prompt('descriptive', sample_text)
    
    print("=== DESCRIPTIVE-SPECIFIC PROMPT (SAMPLE) ===")
    print(descriptive_prompt[:800] + "..." if len(descriptive_prompt) > 800 else descriptive_prompt)
    print()
    
    # Show all available purposes
    print("=== AVAILABLE PURPOSES ===")
    for purpose in prompt_generator.purpose_prompts.keys():
        print(f"- {purpose}")


if __name__ == "__main__":
    main()