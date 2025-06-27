"""
Balanced Detection Prompts for Purpose Classification

This module provides equal-sophistication prompts for detecting all five theoretical purposes:
descriptive, explanatory, predictive, causal, and intervention modeling.

CRITICAL: All prompts maintain equal analytical depth to prevent causal over-emphasis.
"""

class BalancedPrompts:
    """Balanced prompts with equal sophistication across all five purposes"""
    
    def __init__(self):
        """Initialize balanced detection prompts"""
        self.prompts = self._initialize_balanced_prompts()
    
    def _initialize_balanced_prompts(self) -> dict:
        """Initialize detection prompts with equal sophistication for all purposes"""
        return {
            'descriptive': {
                'main_prompt': """
                Analyze this theory for DESCRIPTIVE elements with full analytical sophistication:
                
                DESCRIPTIVE ANALYSIS (Equal Priority):
                1. Taxonomic Structures: Identify systematic classifications, typologies, and categorization schemes
                2. Conceptual Frameworks: Extract definitional structures and conceptual organization
                3. Dimensional Analysis: Find systematic dimensions and attribute mappings
                4. Phenomenological Description: Locate observational frameworks and systematic description
                5. Typological Sophistication: Assess theoretical typologies and ideal types
                
                EQUAL SOPHISTICATION REQUIREMENT: Apply the same analytical depth as causal analysis.
                
                Provide comprehensive evidence for each element with specific textual support.
                """,
                
                'detection_questions': [
                    "What taxonomic structures does this theory establish?",
                    "How does this theory systematically classify phenomena?",
                    "What typological frameworks are developed?",
                    "What dimensional analyses are provided?",
                    "How sophisticated is the descriptive apparatus?"
                ],
                
                'sophistication_markers': [
                    "systematic classification",
                    "taxonomic structure",
                    "typological framework",
                    "dimensional analysis",
                    "conceptual organization",
                    "definitional structure",
                    "categorization scheme",
                    "phenomenological description"
                ]
            },
            
            'explanatory': {
                'main_prompt': """
                Analyze this theory for EXPLANATORY elements with full analytical sophistication:
                
                EXPLANATORY ANALYSIS (Equal Priority):
                1. Mechanistic Explanations: Identify underlying mechanisms and generative processes
                2. Structural Relationships: Extract systematic relationships and structural patterns
                3. Process Theories: Find dynamic processes and systematic interactions
                4. Functional Explanations: Locate functional relationships and systematic functions
                5. Theoretical Mechanisms: Assess explanatory depth and mechanistic sophistication
                
                EQUAL SOPHISTICATION REQUIREMENT: Apply the same analytical depth as causal analysis.
                
                Provide comprehensive evidence for each element with specific textual support.
                """,
                
                'detection_questions': [
                    "What mechanisms does this theory identify?",
                    "How does this theory explain systematic relationships?",
                    "What processes are theorized?",
                    "What functional explanations are provided?",
                    "How sophisticated is the explanatory apparatus?"
                ],
                
                'sophistication_markers': [
                    "underlying mechanism",
                    "generative process",
                    "structural relationship",
                    "systematic interaction",
                    "functional explanation",
                    "mechanistic account",
                    "process theory",
                    "explanatory framework"
                ]
            },
            
            'predictive': {
                'main_prompt': """
                Analyze this theory for PREDICTIVE elements with full analytical sophistication:
                
                PREDICTIVE ANALYSIS (Equal Priority):
                1. Forecasting Frameworks: Identify systematic prediction capabilities and forecasting models
                2. Variable Specifications: Extract predictor variables and outcome specifications
                3. Probabilistic Models: Find statistical relationships and probability frameworks
                4. Projection Capabilities: Locate future-oriented theoretical predictions
                5. Predictive Sophistication: Assess forecasting depth and predictive apparatus
                
                EQUAL SOPHISTICATION REQUIREMENT: Apply the same analytical depth as causal analysis.
                
                Provide comprehensive evidence for each element with specific textual support.
                """,
                
                'detection_questions': [
                    "What forecasting capabilities does this theory provide?",
                    "How does this theory specify predictive variables?",
                    "What probabilistic models are established?",
                    "What future projections are made?",
                    "How sophisticated is the predictive apparatus?"
                ],
                
                'sophistication_markers': [
                    "predictive framework",
                    "forecasting model",
                    "variable specification",
                    "statistical relationship",
                    "probabilistic model",
                    "outcome prediction",
                    "projection capability",
                    "predictive validity"
                ]
            },
            
            'causal': {
                'main_prompt': """
                Analyze this theory for CAUSAL elements with EQUAL sophistication (NO over-emphasis):
                
                CAUSAL ANALYSIS (Equal Priority - NOT Higher):
                1. Causal Relationships: Identify systematic causal connections and causal pathways
                2. Intervention Points: Extract leverage points and intervention targets
                3. Causal Mechanisms: Find causal processes and mechanistic causation
                4. Treatment Effects: Locate experimental and quasi-experimental frameworks
                5. Causal Sophistication: Assess causal depth with EQUAL weight to other purposes
                
                CRITICAL: Apply EQUAL analytical sophistication - NO causal over-emphasis.
                
                Provide comprehensive evidence for each element with specific textual support.
                """,
                
                'detection_questions': [
                    "What causal relationships does this theory establish?",
                    "How does this theory identify intervention points?",
                    "What causal mechanisms are specified?",
                    "What treatment effects are theorized?",
                    "How sophisticated is the causal apparatus (with equal weighting)?"
                ],
                
                'sophistication_markers': [
                    "causal relationship",
                    "causal mechanism",
                    "intervention point",
                    "causal pathway",
                    "treatment effect",
                    "causal inference",
                    "causal process",
                    "intervention target"
                ]
            },
            
            'intervention': {
                'main_prompt': """
                Analyze this theory for INTERVENTION elements with full analytical sophistication:
                
                INTERVENTION ANALYSIS (Equal Priority):
                1. Action Specifications: Identify systematic action frameworks and implementation designs
                2. Implementation Strategies: Extract strategic approaches and implementation plans
                3. Policy Recommendations: Find policy frameworks and prescriptive guidelines
                4. Practical Applications: Locate actionable frameworks and real-world applications
                5. Intervention Sophistication: Assess practical depth and intervention apparatus
                
                EQUAL SOPHISTICATION REQUIREMENT: Apply the same analytical depth as causal analysis.
                
                Provide comprehensive evidence for each element with specific textual support.
                """,
                
                'detection_questions': [
                    "What action specifications does this theory provide?",
                    "How does this theory guide implementation?",
                    "What policy recommendations are made?",
                    "What practical applications are specified?",
                    "How sophisticated is the intervention apparatus?"
                ],
                
                'sophistication_markers': [
                    "implementation strategy",
                    "action specification",
                    "policy recommendation",
                    "practical application",
                    "intervention design",
                    "strategic approach",
                    "implementation plan",
                    "actionable framework"
                ]
            }
        }
    
    def get_purpose_prompt(self, purpose: str) -> str:
        """Get the main detection prompt for a specific purpose"""
        return self.prompts.get(purpose, {}).get('main_prompt', '')
    
    def get_detection_questions(self, purpose: str) -> list:
        """Get detection questions for a specific purpose"""
        return self.prompts.get(purpose, {}).get('detection_questions', [])
    
    def get_sophistication_markers(self, purpose: str) -> list:
        """Get sophistication markers for a specific purpose"""
        return self.prompts.get(purpose, {}).get('sophistication_markers', [])
    
    def get_balanced_analysis_prompt(self) -> str:
        """Get prompt for ensuring balanced analysis across all purposes"""
        return """
        BALANCED PURPOSE ANALYSIS - CRITICAL REQUIREMENTS:
        
        1. EQUAL SOPHISTICATION: Apply identical analytical depth to all five purposes:
           - Descriptive: taxonomies, typologies, classifications
           - Explanatory: mechanisms, processes, relationships
           - Predictive: forecasting, variables, probabilities
           - Causal: relationships, interventions, mechanisms
           - Intervention: actions, implementation, policies
        
        2. NO CAUSAL OVER-EMPHASIS: Causal analysis must receive equal (not greater) attention
        
        3. COMPREHENSIVE COVERAGE: Analyze each purpose with full theoretical sophistication
        
        4. EVIDENCE-BASED: Provide specific textual evidence for each purpose classification
        
        5. BALANCED SCORING: Use identical scoring methodology across all purposes
        
        FAILURE TO MAINTAIN BALANCE WILL RESULT IN SYSTEM FAILURE.
        """
    
    def get_multi_purpose_prompt(self) -> str:
        """Get prompt for analyzing theories with multiple purposes"""
        return """
        MULTI-PURPOSE THEORY ANALYSIS:
        
        This theory may serve multiple purposes simultaneously. Analyze with equal sophistication:
        
        1. PRIMARY PURPOSE: Identify the dominant theoretical purpose with evidence
        2. SECONDARY PURPOSES: Identify additional purposes served (threshold: 30% confidence)
        3. PURPOSE INTEGRATION: Analyze how multiple purposes work together
        4. BALANCED ASSESSMENT: Ensure no single purpose is artificially elevated
        
        EQUAL TREATMENT REQUIREMENT: All purposes must receive identical analytical attention.
        """
    
    def validate_prompt_balance(self) -> dict:
        """Validate that all prompts maintain equal sophistication"""
        validation = {
            'balance_maintained': True,
            'equal_sophistication_confirmed': True,
            'causal_overemphasis_detected': False,
            'prompt_analysis': {}
        }
        
        # Analyze each prompt for sophistication markers
        for purpose, prompt_data in self.prompts.items():
            main_prompt = prompt_data['main_prompt']
            markers = prompt_data['sophistication_markers']
            
            # Check for equal sophistication language
            has_equal_priority = 'Equal Priority' in main_prompt
            has_sophistication_requirement = 'EQUAL SOPHISTICATION REQUIREMENT' in main_prompt or 'Equal Priority' in main_prompt
            
            validation['prompt_analysis'][purpose] = {
                'has_equal_priority': has_equal_priority,
                'has_sophistication_requirement': has_sophistication_requirement,
                'marker_count': len(markers),
                'prompt_length': len(main_prompt),
                'analytical_depth_indicators': main_prompt.count('systematic') + main_prompt.count('comprehensive') + main_prompt.count('sophistication')
            }
            
            # Special check for causal over-emphasis prevention
            if purpose == 'causal':
                has_no_overemphasis = 'NO over-emphasis' in main_prompt or 'EQUAL' in main_prompt
                validation['prompt_analysis'][purpose]['overemphasis_prevention'] = has_no_overemphasis
                if not has_no_overemphasis:
                    validation['causal_overemphasis_detected'] = True
                    validation['balance_maintained'] = False
        
        # Check marker count balance
        marker_counts = [len(prompt_data['sophistication_markers']) for prompt_data in self.prompts.values()]
        if max(marker_counts) - min(marker_counts) > 2:  # Allow small variation
            validation['marker_imbalance_detected'] = True
            validation['balance_maintained'] = False
        
        return validation


# Usage examples and testing prompts
class BalancedPromptTester:
    """Test the balanced prompts with example theories"""
    
    def __init__(self):
        self.prompts = BalancedPrompts()
    
    def test_descriptive_detection(self, theory_text: str) -> dict:
        """Test descriptive purpose detection"""
        prompt = self.prompts.get_purpose_prompt('descriptive')
        questions = self.prompts.get_detection_questions('descriptive')
        markers = self.prompts.get_sophistication_markers('descriptive')
        
        return {
            'purpose': 'descriptive',
            'prompt': prompt,
            'questions': questions,
            'markers': markers,
            'theory_text': theory_text[:200] + "..." if len(theory_text) > 200 else theory_text
        }
    
    def test_all_purposes(self, theory_text: str) -> dict:
        """Test all purpose detections with equal sophistication"""
        results = {}
        
        for purpose in ['descriptive', 'explanatory', 'predictive', 'causal', 'intervention']:
            results[purpose] = {
                'prompt': self.prompts.get_purpose_prompt(purpose),
                'questions': self.prompts.get_detection_questions(purpose),
                'markers': self.prompts.get_sophistication_markers(purpose),
                'equal_sophistication_confirmed': 'Equal Priority' in self.prompts.get_purpose_prompt(purpose) or 'EQUAL' in self.prompts.get_purpose_prompt(purpose)
            }
        
        # Validate balance
        balance_validation = self.prompts.validate_prompt_balance()
        results['balance_validation'] = balance_validation
        
        return results