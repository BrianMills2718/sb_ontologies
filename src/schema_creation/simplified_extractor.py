#!/usr/bin/env python3
"""
Simplified Theory Extractor using 4-component meta-schema
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment
load_dotenv()
client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "o3")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class NodeUnit(BaseModel):
    """Basic unit/element in the theory"""
    id: str = Field(description="Unique identifier")
    label: str = Field(description="Human readable label")
    type: str = Field(default="", description="Theory-specific type code if any")
    description: str = Field(default="", description="What this represents")

class Connection(BaseModel):
    """How units relate to each other"""
    type: str = Field(description="Relationship type/label")
    description: str = Field(description="What this connection represents")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    vocabulary: List[str] = Field(default_factory=list, description="Complete vocabulary for this connection type")

class Mechanism(BaseModel):
    """How the theory works"""
    name: str = Field(description="Mechanism name")
    description: str = Field(description="What this mechanism does")
    process: str = Field(default="", description="How it works")

class TheoryExtraction(BaseModel):
    """Complete theory extraction"""
    model_type: str = Field(description="graph, hypergraph, table, sequence, tree, or network")
    nodes: List[NodeUnit] = Field(description="All fundamental units")
    connections: List[Connection] = Field(description="All connection types")
    properties: Dict[str, Any] = Field(description="Properties, measures, and formulas")
    modifiers: Dict[str, Any] = Field(description="Modifier categories and options")
    mechanisms: List[Mechanism] = Field(default_factory=list, description="How the theory works")
    notation: Dict[str, Any] = Field(description="Notation systems and symbols")
    rules: List[Dict[str, Any]] = Field(description="Inference rules or constraints")

def extract_theory(paper_text: str) -> TheoryExtraction:
    """Extract theory using simplified meta-schema"""
    
    # Load prompt - use v2 for better theory/application distinction
    prompt_path = Path(__file__).parent / "prompts" / "simplified" / "extract_theory_v2.txt"
    with open(prompt_path, 'r') as f:
        prompt_template = f.read()
    
    prompt = f"{prompt_template}\n\nPAPER TEXT:\n{paper_text[:180000]}"
    
    print("Extracting theory with simplified meta-schema...")
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Extract the theoretical framework exactly as presented in the paper."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    return TheoryExtraction(**result)

def extract_and_save(paper_path: str, output_path: str):
    """Extract theory and save as YAML"""
    
    # Load paper
    with open(paper_path, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    # Extract theory
    theory = extract_theory(paper_text)
    
    # Convert to YAML format
    yaml_output = {
        "model_type": theory.model_type,
        "theory_name": Path(paper_path).stem,
        "extraction_method": "simplified_meta_schema",
        
        "nodes": [
            {
                "id": node.id,
                "label": node.label,
                "type": node.type,
                "description": node.description
            } for node in theory.nodes
        ],
        
        "connections": [
            {
                "type": conn.type,
                "description": conn.description,
                "properties": conn.properties,
                "vocabulary": conn.vocabulary
            } for conn in theory.connections
        ],
        
        "properties": theory.properties,
        "modifiers": theory.modifiers,
        "mechanisms": [
            {
                "name": mech.name,
                "description": mech.description,
                "process": mech.process
            } for mech in theory.mechanisms
        ],
        "notation": theory.notation,
        "rules": theory.rules
    }
    
    # Save output
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\nExtraction complete!")
    print(f"Model type: {theory.model_type}")
    print(f"Nodes: {len(theory.nodes)}")
    print(f"Connection types: {len(theory.connections)}")
    print(f"Saved to: {output_path}")
    
    return yaml_output

def main():
    if len(sys.argv) != 3:
        print("Usage: python simplified_extractor.py <paper.txt> <output.yml>")
        sys.exit(1)
    
    paper_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not os.path.exists(paper_path):
        print(f"Error: Paper not found: {paper_path}")
        sys.exit(1)
    
    extract_and_save(paper_path, output_path)

if __name__ == "__main__":
    main()