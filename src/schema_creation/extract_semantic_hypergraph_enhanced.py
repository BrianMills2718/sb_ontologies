#!/usr/bin/env python3
"""
Extract semantic hypergraph theory using enhanced prompt with operational knowledge
"""
import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def extract_semantic_hypergraph_enhanced():
    """Extract semantic hypergraph theory with operational knowledge"""
    
    client = OpenAI()
    
    # Load enhanced prompt
    with open("/home/brian/lit_review/prompt_enhanced_2024.txt", 'r') as f:
        enhanced_prompt = f.read()
    
    # Load meta-schema
    with open("/home/brian/lit_review/meta_schema_8.json", 'r') as f:
        meta_schema = json.load(f)
    
    # Load paper
    paper_path = Path("/home/brian/lit_review/data/papers/computational_linguistics/menezes_roth_semantic_hypergraphs.txt")
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

CRITICAL FOR THIS PAPER:
- This paper introduces a formal graph representation system
- Extract ALL notation (H = <N,L,E>, etc.)
- Capture type inference algorithms and rules
- Include concrete examples of how to construct hypergraphs
- Extract patterns for identifying hyperedges vs regular edges
- Document the incremental construction process

Extract the theory following these enhanced guidelines that emphasize operational knowledge."""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Extract the theory from this paper:\n\n{paper_content}"}
    ]
    
    print(f"Extracting semantic hypergraph theory with enhanced prompt...")
    response = client.chat.completions.create(
        model="o1",
        messages=messages,
        max_completion_tokens=100000
    )
    
    # Parse response
    content = response.choices[0].message.content
    
    # Save raw response
    with open("/home/brian/lit_review/results/semantic_hypergraph_enhanced_raw.txt", 'w') as f:
        f.write(content)
    
    # Try to parse JSON
    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    
    if json_start != -1 and json_end > json_start:
        try:
            extracted = json.loads(content[json_start:json_end])
        except json.JSONDecodeError:
            print("Attempting to fix JSON...")
            # Try with regex
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
            else:
                print("ERROR: Could not parse JSON")
                return None
        
        output_path = Path("/home/brian/lit_review/results/semantic_hypergraph_enhanced_v8.json")
        with open(output_path, 'w') as f:
            json.dump(extracted, f, indent=2)
        
        print(f"✓ Saved to {output_path}")
        
        # Analyze extraction
        print("\n=== EXTRACTION ANALYSIS ===")
        for theory_name, theory_data in extracted.items():
            print(f"\nTheory: {theory_name}")
            
            if 'schema' in theory_data and 'Ontology' in theory_data['schema']:
                ont = theory_data['schema']['Ontology']
                print(f"  Entities: {len(ont.get('entities', []))}")
                print(f"  Connections: {len(ont.get('connections', []))}") 
                print(f"  Properties: {len(ont.get('properties', []))}")
                
                # Check for operational content
                has_notation = False
                has_algorithms = False
                has_examples = False
                has_patterns = False
                
                # Check entities for notation
                for entity in ont.get('entities', []):
                    if 'notation' in entity:
                        has_notation = True
                    if 'examples' in entity or 'coding_examples' in entity:
                        has_examples = True
                
                # Check for algorithms in Process or Analytics
                if 'Process' in theory_data['schema']:
                    process = theory_data['schema']['Process']
                    for step in process.get('steps', []):
                        if 'algorithm' in step.get('objective', '').lower():
                            has_algorithms = True
                        if 'pattern' in step.get('objective', '').lower():
                            has_patterns = True
                
                # Check for type inference
                if 'Analytics' in theory_data['schema']:
                    analytics = theory_data['schema']['Analytics']
                    for primitive in analytics.get('analytical_primitives', []):
                        if 'type' in primitive.lower() or 'inference' in primitive.lower():
                            has_algorithms = True
                
                print(f"\n  Operational Knowledge:")
                print(f"    Has notation: {'✓' if has_notation else '✗'}")
                print(f"    Has algorithms: {'✓' if has_algorithms else '✗'}")
                print(f"    Has examples: {'✓' if has_examples else '✗'}")
                print(f"    Has patterns: {'✓' if has_patterns else '✗'}")
                
                # Check for hypergraph-specific content
                hyperedge_found = any('hyperedge' in str(entity).lower() for entity in ont.get('entities', []))
                type_system_found = any('type' in str(entity).lower() for entity in ont.get('entities', []))
                
                print(f"\n  Hypergraph-specific:")
                print(f"    Hyperedge concept: {'✓' if hyperedge_found else '✗'}")
                print(f"    Type system: {'✓' if type_system_found else '✗'}")
        
        return extracted
    else:
        print("ERROR: No valid JSON found in response")
        return None

def main():
    extract_semantic_hypergraph_enhanced()

if __name__ == "__main__":
    main()