#!/usr/bin/env python3
"""
Test all refined detectors on Young 1996 cognitive mapping
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
            f.write(f"YOUNG 1996 DETECTOR TEST\n")
            f.write(f"Input: {text_file}\n")
            f.write(f"Detector: {detector_prompt_file}\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(result)
        
        print(f"Young 1996 detector test completed. Results saved to {output_file}")
        return result
        
    except Exception as e:
        print(f"Error in Young 1996 detector test: {e}")
        return None

if __name__ == "__main__":
    print("Testing all detectors on Young 1996 (should be property_graph)...")
    
    detectors = [
        ("table_matrix_detector.txt", "table"),
        ("property_graph_detector_v2.txt", "graph_v2"),  
        ("sequence_detector.txt", "sequence")
    ]
    
    for detector_file, detector_type in detectors:
        detector_path = f"experimental_testing/prompt_variations/specialized_model_detection/{detector_file}"
        output_path = f"experimental_testing/prompt_variations/specialized_model_detection/young1996_{detector_type}_result.txt"
        
        result = test_detector(
            "validation_results/academic_papers/young1996_cognitive_mapping.txt",
            detector_path, 
            output_path
        )
    
    print("All Young 1996 detector tests completed!")