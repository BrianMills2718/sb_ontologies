#!/usr/bin/env python3
"""
Extract theory schema using enhanced prompt that captures operational knowledge
"""
import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def extract_with_enhanced_prompt(paper_path: Path, output_path: Path):
    """Extract theory with focus on operational knowledge"""
    
    client = OpenAI()
    
    # Load enhanced prompt
    with open("/home/brian/lit_review/prompt_enhanced_2024.txt", 'r') as f:
        enhanced_prompt = f.read()
    
    # Load meta-schema
    with open("/home/brian/lit_review/meta_schema_8.json", 'r') as f:
        meta_schema = json.load(f)
    
    # Load paper
    with open(paper_path, 'r', encoding='utf-8', errors='ignore') as f:
        paper_content = f.read()
    
    if len(paper_content) > 80000:
        print(f"Truncating paper from {len(paper_content)} to 80k chars")
        paper_content = paper_content[:80000]
    
    # Prepare system message
    system_message = f"""{enhanced_prompt}

META-SCHEMA STRUCTURE:
```json
{json.dumps(meta_schema, indent=2)}
```

Extract the theory following these enhanced guidelines that emphasize operational knowledge."""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Extract the theory from this paper:\n\n{paper_content}"}
    ]
    
    print(f"Extracting from {paper_path.name} with enhanced prompt...")
    response = client.chat.completions.create(
        model="o1",
        messages=messages,
        max_completion_tokens=100000
    )
    
    # Parse response
    content = response.choices[0].message.content
    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    
    if json_start != -1 and json_end > json_start:
        extracted = json.loads(content[json_start:json_end])
        
        with open(output_path, 'w') as f:
            json.dump(extracted, f, indent=2)
        
        print(f"✓ Saved to {output_path}")
        
        # Quick summary
        for theory_name, theory_data in extracted.items():
            print(f"\nTheory: {theory_name}")
            if 'schema' in theory_data and 'Ontology' in theory_data['schema']:
                ont = theory_data['schema']['Ontology']
                print(f"  Entities: {len(ont.get('entities', []))}")
                print(f"  Connections: {len(ont.get('connections', []))}")
                
                # Check for operational content
                has_examples = False
                has_rules = False
                for conn in ont.get('connections', []):
                    if 'coding_examples' in conn or 'examples' in conn:
                        has_examples = True
                    if 'application_rules' in conn or 'when_to_use' in conn:
                        has_rules = True
                
                print(f"  Has coding examples: {'✓' if has_examples else '✗'}")
                print(f"  Has application rules: {'✓' if has_rules else '✗'}")
                
            if 'schema' in theory_data and 'Axioms' in theory_data['schema']:
                print(f"  Axioms captured: ✓")
        
        return extracted
    else:
        print("ERROR: No valid JSON found in response")
        return None

def main():
    paper_path = Path("/home/brian/lit_review/literature/operational_code_analysis/Cognitive Mapping Meets Semantic Networks.txt")
    output_path = Path("/home/brian/lit_review/results/cognitive_mapping_enhanced_v8.json")
    
    extract_with_enhanced_prompt(paper_path, output_path)

if __name__ == "__main__":
    main()