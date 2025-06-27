#!/usr/bin/env python3
"""
Test hybrid schema generation on Young 1996
"""

import os
import openai
from pathlib import Path

# Set up OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

def test_hybrid_schema_generation(text_file, hybrid_detection_file, output_file):
    """Test hybrid schema generation"""
    
    # Read the theory text
    with open(text_file, 'r', encoding='utf-8') as f:
        theory_text = f.read()
    
    # Read the hybrid detection results
    with open(hybrid_detection_file, 'r', encoding='utf-8') as f:
        hybrid_results = f.read()
    
    # Read the schema generation prompt
    with open("experimental_testing/prompt_variations/hybrid_integration/hybrid_schema_generator.txt", 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Combine inputs
    full_prompt = f"""
{prompt_template}

THEORY TEXT:
{theory_text}

HYBRID DETECTION RESULTS:
{hybrid_results}

Generate the complete hybrid schema following the specified format:
"""
    
    # Call OpenAI API
    try:
        response = openai.chat.completions.create(
            model="o3-mini",
            messages=[{"role": "user", "content": full_prompt}],
            max_completion_tokens=3000
        )
        
        result = response.choices[0].message.content
        
        # Save result
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"HYBRID SCHEMA GENERATION TEST\n")
            f.write(f"Theory: {text_file}\n")
            f.write(f"Detection: {hybrid_detection_file}\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(result)
        
        print(f"Hybrid schema generation test completed. Results saved to {output_file}")
        return result
        
    except Exception as e:
        print(f"Error in hybrid schema generation test: {e}")
        return None

if __name__ == "__main__":
    print("Testing hybrid schema generation on Young 1996...")
    
    test_hybrid_schema_generation(
        "validation_results/academic_papers/young1996_cognitive_mapping.txt",
        "experimental_testing/prompt_variations/hybrid_integration/young1996_hybrid_result.txt",
        "experimental_testing/prompt_variations/hybrid_integration/young1996_hybrid_schema.yml"
    )
    
    print("Hybrid schema generation test completed!")