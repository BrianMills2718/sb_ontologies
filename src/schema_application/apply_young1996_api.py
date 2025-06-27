#!/usr/bin/env python3
"""
Apply Young 1996 Cognitive Mapping Schema to Carter Speech using OpenAI API
Uses the actual API-based system instead of manual interpretation
"""
import os
import json
import yaml
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_young1996_schema():
    """Load the faithful Young 1996 schema"""
    schema_path = Path('/home/brian/lit_review/literature/operational_code_analysis/young1996_faithful.yml')
    with open(schema_path, 'r') as f:
        return yaml.safe_load(f)

def load_carter_speech():
    """Load Carter's speech text"""
    speech_path = Path('/home/brian/lit_review/texts/carter_speech.txt')
    with open(speech_path, 'r') as f:
        return f.read()

def apply_schema_via_api(schema, text):
    """Use OpenAI API to apply Young 1996 schema to Carter's speech"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""You are applying the Young 1996 Cognitive Mapping schema to Carter's speech.

CRITICAL INSTRUCTIONS:
- Use ONLY elements defined in the provided schema
- Extract ONLY what is directly findable in Carter's text
- Do NOT add concepts not in the schema
- Do NOT invent measurements or scores
- Apply the schema categories systematically

YOUNG 1996 SCHEMA:
{yaml.dump(schema, default_flow_style=False)}

CARTER SPEECH TEXT:
{text}

TASK: Apply the Young 1996 schema to extract Carter's cognitive map from his speech.

OUTPUT FORMAT: Structured YAML using only schema-defined elements.

Focus on:
1. Concepts (entities) that Carter mentions
2. Relationships between concepts as defined in schema
3. Properties and actions from schema that apply
4. Only measures explicitly defined in the schema

Do not add centrality scores, network metrics, or other concepts not in the Young 1996 schema."""

    try:
        print(f"🔍 Prompt length: {len(prompt):,} characters")
        
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'o3'),
            messages=[
                {"role": "system", "content": "You are a precise academic theory application system. Apply only what is defined in the provided schema to the provided text."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=8000
        )
        
        print(f"🔍 Response object: {response}")
        print(f"🔍 Response choices: {len(response.choices)}")
        print(f"🔍 Message content: {response.choices[0].message.content}")
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"🚨 Exception details: {e}")
        return f"API Error: {str(e)}"

def main():
    """Main execution function"""
    print("🔬 APPLYING YOUNG 1996 SCHEMA TO CARTER SPEECH VIA API")
    print("=" * 70)
    print("Using OpenAI O3 model for systematic schema application")
    print()
    
    # Load data
    print("📁 Loading Young 1996 schema...")
    schema = load_young1996_schema()
    
    print("📁 Loading Carter speech...")
    speech = load_carter_speech()
    
    print(f"📊 Schema elements: {len(schema.get('schema_blueprint', {}).get('definitions', []))}")
    print(f"📊 Speech length: {len(speech):,} characters")
    print()
    
    # Apply schema via API
    print("🤖 Applying schema via OpenAI API...")
    result = apply_schema_via_api(schema, speech)
    
    print(f"🔍 API Response length: {len(result) if result else 0}")
    print(f"🔍 API Response type: {type(result)}")
    
    # Save result
    output_path = Path('/home/brian/lit_review/carter_young1996_faithful_analysis.yml')
    with open(output_path, 'w') as f:
        f.write(str(result) if result else "No response received")
    
    print("✅ ANALYSIS COMPLETE")
    print(f"📄 Output saved to: {output_path}")
    print()
    print("Result preview:")
    print("-" * 50)
    print(result[:1000] + "..." if len(result) > 1000 else result)

if __name__ == "__main__":
    main()