#!/usr/bin/env python3
"""
Test refined property graph detector on known cases
"""

import os
import openai
from pathlib import Path

# Set up OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

def test_detector(text_file, detector_prompt_file, output_file):
    """Test a detector prompt on a specific paper"""
    
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
            f.write(f"REFINED DETECTOR TEST\n")
            f.write(f"Input: {text_file}\n")
            f.write(f"Detector: {detector_prompt_file}\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(result)
        
        print(f"Refined detector test completed. Results saved to {output_file}")
        return result
        
    except Exception as e:
        print(f"Error in refined detector test: {e}")
        return None

if __name__ == "__main__":
    print("Testing REFINED property graph detector...")
    
    # Test on Heilman framing (should be lower confidence now)
    print("Testing on Heilman framing (should reduce confidence)...")
    test_detector(
        "validation_results/cross_domain/framing_theory_core.txt",
        "experimental_testing/prompt_variations/specialized_model_detection/property_graph_detector_v2.txt",
        "experimental_testing/prompt_variations/specialized_model_detection/heilman_framing_graph_v2_result.txt"
    )
    
    # Test on Lofland-Stark (should be lower confidence now)
    print("Testing on Lofland-Stark conversion (should reduce confidence)...")
    test_detector(
        "validation_results/complexity_testing/lofland_stark_simple_theory.txt",
        "experimental_testing/prompt_variations/specialized_model_detection/property_graph_detector_v2.txt", 
        "experimental_testing/prompt_variations/specialized_model_detection/lofland_conversion_graph_v2_result.txt"
    )
    
    print("Refined detector tests completed!")