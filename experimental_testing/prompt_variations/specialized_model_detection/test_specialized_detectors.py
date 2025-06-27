#!/usr/bin/env python3
"""
Test specialized model type detectors on known cases
"""

import os
import openai
from pathlib import Path

# Set up OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

def test_specialized_detector(text_file, detector_prompt_file, output_file):
    """Test a specialized detector prompt on a specific paper"""
    
    # Read the paper text
    with open(text_file, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    # Read the detector prompt
    with open(detector_prompt_file, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Combine prompt and text
    full_prompt = f"{prompt_template}\n\nTHEORY TO ANALYZE:\n{paper_text}"
    
    # Call OpenAI API
    try:
        response = openai.chat.completions.create(
            model="o3-mini",
            messages=[{"role": "user", "content": full_prompt}],
            max_completion_tokens=1500
        )
        
        result = response.choices[0].message.content
        
        # Save result
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"SPECIALIZED DETECTOR TEST\n")
            f.write(f"Input: {text_file}\n")
            f.write(f"Detector: {detector_prompt_file}\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(result)
        
        print(f"Specialized detector test completed. Results saved to {output_file}")
        return result
        
    except Exception as e:
        print(f"Error in specialized detector test: {e}")
        return None

def test_all_detectors_on_theory(text_file, base_name):
    """Test all three specialized detectors on a single theory"""
    
    detectors = [
        ("table_matrix_detector.txt", "table"),
        ("property_graph_detector.txt", "graph"), 
        ("sequence_detector.txt", "sequence")
    ]
    
    results = {}
    
    for detector_file, detector_type in detectors:
        detector_path = f"experimental_testing/prompt_variations/specialized_model_detection/{detector_file}"
        output_path = f"experimental_testing/prompt_variations/specialized_model_detection/{base_name}_{detector_type}_result.txt"
        
        result = test_specialized_detector(text_file, detector_path, output_path)
        results[detector_type] = result
        
    return results

if __name__ == "__main__":
    print("Testing specialized detectors on Heilman framing theory (should be table_matrix)...")
    results_heilman = test_all_detectors_on_theory(
        "validation_results/cross_domain/framing_theory_core.txt",
        "heilman_framing"
    )
    
    print("\nTesting specialized detectors on Lofland-Stark conversion theory (should be sequence)...")
    results_lofland = test_all_detectors_on_theory(
        "validation_results/complexity_testing/lofland_stark_simple_theory.txt", 
        "lofland_conversion"
    )
    
    print("\nAll specialized detector tests completed!")