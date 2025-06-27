#!/usr/bin/env python3
"""
Test theory count detection on Young 1996 cognitive mapping paper
"""

import os
import openai
from pathlib import Path

# Set up OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

def test_theory_count_detection(text_file, prompt_file, output_file):
    """Test theory count detection prompt on a specific paper"""
    
    # Read the paper text
    with open(text_file, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    # Read the prompt
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Combine prompt and text
    full_prompt = f"{prompt_template}\n\nPAPER TO ANALYZE:\n{paper_text}"
    
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
            f.write(f"THEORY COUNT DETECTION TEST\n")
            f.write(f"Input: {text_file}\n")
            f.write(f"Prompt: {prompt_file}\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(result)
        
        print(f"Theory count detection test completed. Results saved to {output_file}")
        return result
        
    except Exception as e:
        print(f"Error in theory count detection: {e}")
        return None

if __name__ == "__main__":
    # Test on Young 1996 cognitive mapping
    test_theory_count_detection(
        "validation_results/academic_papers/young1996_cognitive_mapping.txt",
        "experimental_testing/prompt_variations/theory_count_detection/theory_count_prompt_v1.txt",
        "experimental_testing/prompt_variations/theory_count_detection/young_result_v1.txt"
    )