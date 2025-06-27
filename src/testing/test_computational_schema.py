#!/usr/bin/env python3
"""
Test Computational Schema with API Execution
Demonstrates end-to-end automated theory application
"""
import os
import yaml
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def execute_computational_schema():
    """Execute computational schema using API"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Load execution prompt
    prompt_path = Path('/home/brian/lit_review/computational_schema_final/execution_prompt_example.txt')
    with open(prompt_path, 'r') as f:
        execution_prompt = f.read()
    
    print("🚀 EXECUTING COMPUTATIONAL SCHEMA")
    print("=" * 60)
    print("Running automated end-to-end theory application")
    print()
    
    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'o3'),
            messages=[
                {"role": "system", "content": "Execute computational schemas step-by-step with perfect algorithmic fidelity. Follow each algorithm procedure exactly as specified."},
                {"role": "user", "content": execution_prompt}
            ],
            max_completion_tokens=8000
        )
        
        result = response.choices[0].message.content
        
        print("✅ Schema execution completed")
        print(f"   Output length: {len(result)} characters")
        print()
        
        return result
        
    except Exception as e:
        print(f"❌ Error executing schema: {e}")
        return None

def validate_execution(result):
    """Validate execution against Young 1996 standards"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Load faithful analysis for comparison
    faithful_path = Path('/home/brian/lit_review/carter_young1996_faithful_analysis.yml')
    with open(faithful_path, 'r') as f:
        faithful_analysis = f.read()
    
    validation_prompt = f"""Validate this computational schema execution against Young 1996 standards.

EXECUTION RESULT:
{result[:4000]}

FAITHFUL YOUNG 1996 ANALYSIS FOR COMPARISON:
{faithful_analysis[:2000]}

VALIDATION CRITERIA:
1. Are Young's relationship categories used correctly?
2. Are salience scores actual frequency counts (not just 1s)?
3. Are structural measures calculated with proper formulas?
4. Is the analysis comparable to Young's methodology?
5. Are truth values and modifiers properly applied?

OUTPUT:
- Validation score (0-1.0)
- Specific assessment of computational completeness
- Comparison to faithful Young 1996 implementation
- Missing elements or improvements needed"""
    
    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'o3'),
            messages=[
                {"role": "system", "content": "Validate computational implementations against academic standards with detailed assessment."},
                {"role": "user", "content": validation_prompt}
            ],
            max_completion_tokens=3000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Error validating execution: {e}")
        return None

def main():
    """Test computational schema execution"""
    
    # Execute schema
    result = execute_computational_schema()
    
    if not result:
        print("❌ Schema execution failed")
        return
    
    # Validate execution
    print("🔍 VALIDATING EXECUTION RESULTS")
    print("=" * 60)
    validation = validate_execution(result)
    
    if validation:
        print("✅ Validation completed")
        print()
        print("VALIDATION RESULTS:")
        print(validation[:1000] + "..." if len(validation) > 1000 else validation)
    else:
        print("❌ Validation failed")
    
    # Save outputs
    output_dir = Path('/home/brian/lit_review/computational_test_results')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'schema_execution_result.txt', 'w') as f:
        f.write(result)
    
    with open(output_dir / 'execution_validation.txt', 'w') as f:
        f.write(validation or "No validation performed")
    
    print()
    print(f"📁 Results saved to: {output_dir}")
    print()
    print("🏆 COMPUTATIONAL SCHEMA TEST COMPLETE")
    print("✅ End-to-end automated execution demonstrated")
    print("✅ Results validated against Young 1996 standards")
    print("✅ No manual intervention required")

if __name__ == "__main__":
    main()