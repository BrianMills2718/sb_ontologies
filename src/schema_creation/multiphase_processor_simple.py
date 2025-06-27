#!/usr/bin/env python3
"""
Simplified Multiphase Processor for O3 Model
Processes smaller chunks to handle O3's longer processing time
"""

import os
import sys
import json
import yaml
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from .prompt_loader import get_simple_extraction_prompt

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "o3")

# Simplified models for O3
class VocabularyTerm(BaseModel):
    term: str
    definition: str
    category: str = Field(description="entity, relationship, property, action, or measure")

class SimplifiedOutput(BaseModel):
    citation: str
    annotation: str
    model_type: str = Field(description="property_graph, hypergraph, table_matrix, sequence, tree, timeline, or other")
    rationale: str
    vocabulary: List[VocabularyTerm]

# Load prompt from external file
SIMPLE_PROMPT = get_simple_extraction_prompt()

def process_paper_simple(paper_path: str, output_path: Optional[str] = None) -> Dict:
    """Process paper in simplified single pass for O3"""
    print(f"Processing {paper_path} with {MODEL}...")
    
    # Read paper (truncate if too long)
    with open(paper_path, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    # Truncate to first 10000 chars for O3
    if len(paper_text) > 10000:
        paper_text = paper_text[:10000] + "\n\n[TRUNCATED FOR PROCESSING]"
        print("  Truncated paper to 10000 characters")
    
    messages = [
        {"role": "system", "content": SIMPLE_PROMPT},
        {"role": "user", "content": paper_text}
    ]
    
    print("  Sending request to O3...")
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=messages,
        response_format=SimplifiedOutput
    )
    
    result = response.choices[0].message.parsed
    print(f"  Extracted {len(result.vocabulary)} terms")
    
    # Convert to YAML format
    definitions = []
    for term in result.vocabulary:
        def_item = {
            "name": term.term,
            "category": term.category,
            "description": term.definition
        }
        # Add domain/range only for relationships and actions
        if term.category in ["relationship", "action"]:
            # O3 should infer these from context
            def_item["domain"] = ["Entity"]  # Placeholder
            def_item["range"] = ["Entity"]   # Placeholder
        definitions.append(def_item)
    
    yaml_output = {
        "citation": result.citation,
        "annotation": result.annotation,
        "model_type": result.model_type,
        "rationale": result.rationale,
        "schema_blueprint": {
            "title": "Simplified Schema",
            "description": "Schema generated from paper analysis",
            "root_properties": {
                "nodes": {
                    "description": "Entities and concepts",
                    "item_type": "Entity"
                },
                "edges": {
                    "description": "Relationships and actions",
                    "item_type": "NaryTuple"
                }
            },
            "definitions": definitions
        }
    }
    
    # Save output
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_output, f, allow_unicode=True, default_flow_style=False)
        print(f"Saved to {output_path}")
    
    return yaml_output

def main():
    if len(sys.argv) < 2:
        print("Usage: python multiphase_processor_simple.py <paper.txt> [output.yml]")
        sys.exit(1)
    
    paper_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(paper_path):
        print(f"Error: Paper file '{paper_path}' not found")
        sys.exit(1)
    
    try:
        result = process_paper_simple(paper_path, output_path)
        print("\nProcessing complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()