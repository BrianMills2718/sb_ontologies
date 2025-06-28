#!/usr/bin/env python3
"""
Test meta_schema_8 extraction on multiple papers
"""
import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def load_prompt():
    """Load the extraction prompt"""
    prompt_path = Path("/home/brian/lit_review/prompt_2025.06280355.txt")
    with open(prompt_path, 'r') as f:
        return f.read()

def load_meta_schema():
    """Load the meta_schema_8 JSON schema"""
    schema_path = Path("/home/brian/lit_review/meta_schema_8.json")
    with open(schema_path, 'r') as f:
        return json.load(f)

def extract_theory(paper_path, output_path, client, prompt):
    """Extract theory from paper using meta_schema_8"""
    print(f"\n{'='*60}")
    print(f"Processing: {paper_path.name}")
    print(f"{'='*60}")
    
    # Read paper content
    with open(paper_path, 'r', encoding='utf-8', errors='ignore') as f:
        paper_content = f.read()
    
    if len(paper_content) > 80000:
        print(f"Warning: Paper is {len(paper_content)} chars, truncating to 80k")
        paper_content = paper_content[:80000]
    
    # Prepare extraction message
    system_message = f"""You are an expert academic theorist and knowledge engineer following the provided extraction guidelines.

EXTRACTION PROMPT:
{prompt}

META-SCHEMA STRUCTURE:
```json
{json.dumps(load_meta_schema(), indent=2)}
```

Extract the theory from the provided paper following these guidelines exactly."""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Extract the theory from this paper:\n\n{paper_content}"}
    ]
    
    print("Sending to OpenAI...")
    response = client.chat.completions.create(
        model="o1",
        messages=messages,
        max_completion_tokens=80000
    )
    
    content = response.choices[0].message.content
    
    # Extract JSON from response
    try:
        # Find JSON in the response
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = content[json_start:json_end]
            extracted_schema = json.loads(json_str)
            
            # Save to output
            with open(output_path, 'w') as f:
                json.dump(extracted_schema, f, indent=2)
            
            print(f"✓ Saved to: {output_path}")
            
            # Print summary
            print("\nExtraction Summary:")
            for theory_name, theory_data in extracted_schema.items():
                if 'classification' in theory_data:
                    cls = theory_data['classification']
                    print(f"  Theory: {theory_name}")
                    print(f"  Model Type: {cls.get('model_type', 'N/A')}")
                    print(f"  Engine: {cls.get('reasoning_engine', 'N/A')}")
                    print(f"  Summary: {cls.get('summary', 'N/A')}")
                
                if 'schema' in theory_data and 'Ontology' in theory_data['schema']:
                    ont = theory_data['schema']['Ontology']
                    print(f"  Entities: {len(ont.get('entities', []))}")
                    print(f"  Connections: {len(ont.get('connections', []))}")
                    print(f"  Properties: {len(ont.get('properties', []))}")
                    print(f"  Modifiers: {len(ont.get('modifiers', []))}")
        else:
            print("ERROR: No valid JSON found in response")
            print("Response preview:", content[:500])
            
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}")
        print("Response preview:", content[:500])
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")

def main():
    """Test extraction on multiple papers"""
    client = OpenAI()
    prompt = load_prompt()
    
    # Define test papers
    test_papers = [
        {
            "path": "/home/brian/lit_review/literature/operational_code_analysis/Cognitive Mapping Meets Semantic Networks.txt",
            "output": "/home/brian/lit_review/results/cognitive_mapping_semantic_networks_v8.json"
        },
        {
            "path": "/home/brian/lit_review/semantic_hypergraphs.txt", 
            "output": "/home/brian/lit_review/results/semantic_hypergraphs_v8.json"
        },
        {
            "path": "/home/brian/lit_review/literature/influence_operations/Foundations of Effective Influence Operations Chapter6-7 A Framework for influence operations.txt",
            "output": "/home/brian/lit_review/results/influence_operations_v8.json"
        }
    ]
    
    # Test the third paper
    paper_info = test_papers[2]
    paper_path = Path(paper_info["path"])
    output_path = Path(paper_info["output"])
    
    if paper_path.exists():
        extract_theory(paper_path, output_path, client, prompt)
    else:
        print(f"\nERROR: Paper not found: {paper_path}")

if __name__ == "__main__":
    main()