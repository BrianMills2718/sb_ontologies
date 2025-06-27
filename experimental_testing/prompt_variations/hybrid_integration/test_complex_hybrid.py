#!/usr/bin/env python3
"""
Test hybrid detection on our complex stress test case
"""

import os
import openai
from pathlib import Path

# Set up OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

def test_hybrid_detector(text_file, output_file):
    """Test hybrid detection prompt on a specific paper"""
    
    # Read the paper text
    with open(text_file, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    # Read the detector prompt
    with open("experimental_testing/prompt_variations/hybrid_integration/hybrid_detector.txt", 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Combine prompt and text
    full_prompt = f"{prompt_template}\n\nTHEORY TO ANALYZE:\n{paper_text}"
    
    # Call OpenAI API
    try:
        response = openai.chat.completions.create(
            model="o3-mini",
            messages=[{"role": "user", "content": full_prompt}],
            max_completion_tokens=2000
        )
        
        result = response.choices[0].message.content
        
        # Save result
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"COMPLEX HYBRID THEORY DETECTION TEST\n")
            f.write(f"Input: {text_file}\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(result)
        
        print(f"Complex hybrid detection test completed. Results saved to {output_file}")
        return result
        
    except Exception as e:
        print(f"Error in complex hybrid detection test: {e}")
        return None

if __name__ == "__main__":
    print("Testing hybrid detection on complex OWL stress test case...")
    
    test_hybrid_detector(
        "owl_enhanced_stress_test_schema.yml",
        "experimental_testing/prompt_variations/hybrid_integration/owl_stress_test_hybrid_result.txt"
    )
    
    print("Complex hybrid detection test completed!")