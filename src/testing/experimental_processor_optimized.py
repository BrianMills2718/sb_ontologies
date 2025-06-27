#!/usr/bin/env python3
"""
Optimized Experimental Processor
Integrates all tested improvements: theory count detection, specialized model detection, hybrid processing
"""

import os
import openai
import json
import yaml
from pathlib import Path

# Set up OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

class OptimizedTheoryProcessor:
    def __init__(self):
        self.model = "o3-mini"
        self.base_path = Path("experimental_testing/prompt_variations")
        
    def call_openai(self, prompt, max_tokens=2000):
        """Make OpenAI API call with error handling"""
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"API Error: {e}")
            return None
    
    def detect_theory_count(self, text):
        """Phase 1: Detect if paper contains single or multiple theories"""
        with open(self.base_path / "theory_count_detection/theory_count_prompt_v1.txt", 'r') as f:
            prompt = f.read()
        
        full_prompt = f"{prompt}\n\nPAPER TO ANALYZE:\n{text}"
        result = self.call_openai(full_prompt)
        
        print("✅ Phase 1: Theory count detection completed")
        return result
    
    def specialized_detection(self, text):
        """Phase 2: Run parallel specialized detectors"""
        detectors = {
            'table_matrix': 'table_matrix_detector.txt',
            'property_graph': 'property_graph_detector_v2.txt',
            'sequence': 'sequence_detector.txt'
        }
        
        results = {}
        
        for detector_type, detector_file in detectors.items():
            with open(self.base_path / f"specialized_model_detection/{detector_file}", 'r') as f:
                prompt = f.read()
            
            full_prompt = f"{prompt}\n\nTHEORY TO ANALYZE:\n{text}"
            result = self.call_openai(full_prompt, max_tokens=1500)
            results[detector_type] = result
            print(f"✅ {detector_type} detection completed")
        
        return results
    
    def detect_hybrid(self, text):
        """Phase 3: Detect hybrid theories"""
        with open(self.base_path / "hybrid_integration/hybrid_detector.txt", 'r') as f:
            prompt = f.read()
        
        full_prompt = f"{prompt}\n\nTHEORY TO ANALYZE:\n{text}"
        result = self.call_openai(full_prompt)
        
        print("✅ Phase 3: Hybrid detection completed")
        return result
    
    def generate_hybrid_schema(self, text, hybrid_detection):
        """Phase 4: Generate hybrid schema if needed"""
        with open(self.base_path / "hybrid_integration/hybrid_schema_generator.txt", 'r') as f:
            prompt = f.read()
        
        full_prompt = f"""
{prompt}

THEORY TEXT:
{text}

HYBRID DETECTION RESULTS:
{hybrid_detection}

Generate the complete hybrid schema:
"""
        
        result = self.call_openai(full_prompt, max_tokens=3000)
        print("✅ Phase 4: Hybrid schema generation completed")
        return result
    
    def integrate_detection_results(self, specialized_results):
        """Integrate specialized detection results using optimal decision rules"""
        # Parse confidence scores (simplified - would need regex parsing in production)
        # For demo, using mock confidence extraction
        
        # Mock confidence extraction (would parse from actual results)
        table_conf = 0.3 if "2×2" in specialized_results.get('table_matrix', '') else 0.1
        graph_conf = 0.9 if "network" in specialized_results.get('property_graph', '') else 0.2
        sequence_conf = 0.8 if "sequence" in specialized_results.get('sequence', '') else 0.1
        
        print(f"Confidence scores - Table: {table_conf}, Graph: {graph_conf}, Sequence: {sequence_conf}")
        
        # Apply decision rules
        if sequence_conf >= 0.8:
            return "sequence", sequence_conf
        elif graph_conf >= 0.7 and table_conf < 0.7:
            return "property_graph", graph_conf
        elif table_conf >= 0.3:
            return "table_matrix", table_conf
        else:
            return "NEEDS_REVIEW", max(table_conf, graph_conf, sequence_conf)
    
    def process_theory(self, text_file, output_file):
        """Main processing pipeline"""
        print(f"🚀 Starting optimized processing of {text_file}")
        
        # Read input
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        results = {
            'input_file': text_file,
            'processing_pipeline': 'optimized_experimental'
        }
        
        # Phase 1: Theory count detection
        theory_count = self.detect_theory_count(text)
        results['theory_count_detection'] = theory_count
        
        # Phase 2: Specialized detection
        specialized = self.specialized_detection(text)
        results['specialized_detection'] = specialized
        
        # Phase 3: Hybrid detection
        hybrid = self.detect_hybrid(text)
        results['hybrid_detection'] = hybrid
        
        # Phase 4: Integration and decision
        if "hybrid_detected: true" in hybrid:
            print("🔄 Hybrid theory detected - generating hybrid schema")
            schema = self.generate_hybrid_schema(text, hybrid)
            results['final_output'] = schema
            results['model_type'] = 'hybrid'
        else:
            model_type, confidence = self.integrate_detection_results(specialized)
            results['model_type'] = model_type
            results['confidence'] = confidence
            print(f"✅ Single model selected: {model_type} (confidence: {confidence})")
        
        # Save results
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(results, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Processing completed. Results saved to {output_file}")
        return results

def main():
    processor = OptimizedTheoryProcessor()
    
    # Test on all our validation cases
    test_cases = [
        ("validation_results/cross_domain/framing_theory_core.txt", 
         "experimental_testing/architecture_comparison/heilman_optimized_result.yml"),
        ("validation_results/complexity_testing/lofland_stark_simple_theory.txt",
         "experimental_testing/architecture_comparison/lofland_optimized_result.yml"),
        ("validation_results/academic_papers/young1996_cognitive_mapping.txt",
         "experimental_testing/architecture_comparison/young1996_optimized_result.yml")
    ]
    
    for input_file, output_file in test_cases:
        print(f"\n{'='*60}")
        processor.process_theory(input_file, output_file)
        print(f"{'='*60}\n")

if __name__ == "__main__":
    main()