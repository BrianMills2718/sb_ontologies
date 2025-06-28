#!/usr/bin/env python3
"""
Apply Semantic Hypergraph theory to text
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment
load_dotenv()
client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "o3")

class Atom(BaseModel):
    """Atomic hyperedge"""
    id: str
    label: str
    type: str  # C, P, M, B, T, J
    
class Hyperedge(BaseModel):
    """Non-atomic hyperedge"""
    id: str
    connector: str  # ID of connector atom
    arguments: List[str]  # IDs of argument atoms/hyperedges
    type: str  # R or S (inferred)
    roles: Optional[str] = None  # e.g., "soa" for subject-object-attribute

class SemanticHypergraphInstance(BaseModel):
    """Instance of Semantic Hypergraph"""
    atoms: List[Atom] = Field(description="All atomic hyperedges")
    hyperedges: List[Hyperedge] = Field(description="All non-atomic hyperedges")
    
def apply_sh_to_text(text: str, schema_path: str) -> SemanticHypergraphInstance:
    """Apply Semantic Hypergraph theory to parse text"""
    
    # Load the theory schema
    with open(schema_path, 'r') as f:
        schema = yaml.safe_load(f)
    
    # Extract theory elements
    type_codes = schema['notation']['type_codes']
    type_inference_rules = schema['properties']['formulas']['type_inference']
    
    prompt = f"""Apply Semantic Hypergraph theory to parse this text.

TYPE CODES:
{json.dumps(type_codes, indent=2)}

TYPE INFERENCE RULES:
{json.dumps(type_inference_rules, indent=2)}

PARSING PROCESS:
1. α-stage: Classify each token with type code
   - C: concepts (nouns, noun phrases)
   - P: predicates (verbs, relations)
   - M: modifiers (adjectives, adverbs)
   - B: builders (and, or, with)
   - T: triggers (if, when, because)
   - J: conjunctions (punctuation, connectors)

2. β-stage: Build hyperedges bottom-up
   - (M x) → x (modifiers attach to what they modify)
   - (B C C+) → C (builders combine concepts)
   - (P args) → R (predicates form relations)

3. Assign argument roles (s=subject, o=object, a=attribute, etc.)

TEXT:
{text[:180000]}

Parse the ENTIRE text systematically. Extract ALL concepts, predicates, modifiers, and build complete hyperedges. Return as JSON:
{{
  "atoms": [
    {{"id": "a1", "label": "Iran", "type": "C"}},
    {{"id": "a2", "label": "threat", "type": "C"}},
    {{"id": "a3", "label": "is", "type": "P"}},
    {{"id": "a4", "label": "really", "type": "M"}}
  ],
  "hyperedges": [
    {{
      "id": "h1",
      "connector": "a3",
      "arguments": ["a1", "a2"],
      "type": "R",
      "roles": "so"
    }}
  ]
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Parse text into Semantic Hypergraph following the theory exactly."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    
    # Convert to proper types
    atoms = [Atom(**a) for a in result.get('atoms', [])]
    hyperedges = [Hyperedge(**h) for h in result.get('hyperedges', [])]
    
    return SemanticHypergraphInstance(atoms=atoms, hyperedges=hyperedges)

def visualize_hypergraph(instance: SemanticHypergraphInstance) -> str:
    """Create text visualization of hypergraph"""
    
    # Create lookup maps
    atom_map = {a.id: a for a in instance.atoms}
    edge_map = {h.id: h for h in instance.hyperedges}
    
    def format_element(elem_id: str, indent: int = 0) -> str:
        """Recursively format an element"""
        prefix = "  " * indent
        
        if elem_id in atom_map:
            atom = atom_map[elem_id]
            return f"{prefix}{atom.label}/{atom.type}"
        elif elem_id in edge_map:
            edge = edge_map[elem_id]
            connector = atom_map.get(edge.connector, None)
            if connector:
                result = f"{prefix}({connector.label}/{connector.type}"
                if edge.roles:
                    result += f".{edge.roles}"
                for arg_id in edge.arguments:
                    result += "\n" + format_element(arg_id, indent + 1)
                result += f"\n{prefix})"
                return result
        return f"{prefix}[{elem_id}]"
    
    # Find root hyperedges (not used as arguments)
    used_as_args = set()
    for h in instance.hyperedges:
        used_as_args.update(h.arguments)
    
    roots = [h.id for h in instance.hyperedges if h.id not in used_as_args]
    
    output = []
    for root_id in roots:
        output.append(format_element(root_id))
    
    return "\n\n".join(output)

def save_hypergraph(instance: SemanticHypergraphInstance, output_path: str):
    """Save hypergraph instance as YAML"""
    
    # Convert to YAML-friendly format
    yaml_output = {
        'theory': 'Semantic Hypergraph',
        'atoms': [
            {
                'id': a.id,
                'label': a.label,
                'type': a.type,
                'type_name': {
                    'C': 'concept',
                    'P': 'predicate', 
                    'M': 'modifier',
                    'B': 'builder',
                    'T': 'trigger',
                    'J': 'conjunction'
                }.get(a.type, a.type)
            } for a in instance.atoms
        ],
        'hyperedges': [
            {
                'id': h.id,
                'connector': h.connector,
                'arguments': h.arguments,
                'type': h.type,
                'roles': h.roles
            } for h in instance.hyperedges
        ],
        'visualization': visualize_hypergraph(instance),
        'summary': {
            'total_atoms': len(instance.atoms),
            'total_hyperedges': len(instance.hyperedges),
            'type_distribution': {}
        }
    }
    
    # Calculate type distribution
    for atom in instance.atoms:
        yaml_output['summary']['type_distribution'][atom.type] = \
            yaml_output['summary']['type_distribution'].get(atom.type, 0) + 1
    
    with open(output_path, 'w') as f:
        yaml.dump(yaml_output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\nSemantic Hypergraph Extracted:")
    print(f"- Atoms: {len(instance.atoms)}")
    print(f"- Hyperedges: {len(instance.hyperedges)}")
    print(f"- Type distribution: {yaml_output['summary']['type_distribution']}")
    print(f"Saved to: {output_path}")

def main():
    if len(sys.argv) != 4:
        print("Usage: python apply_sh_theory.py <text_file> <schema_file> <output_file>")
        sys.exit(1)
    
    text_path = sys.argv[1] 
    schema_path = sys.argv[2]
    output_path = sys.argv[3]
    
    # Load text
    with open(text_path, 'r') as f:
        text = f.read()
    
    # Apply theory
    instance = apply_sh_to_text(text, schema_path)
    
    # Save results
    save_hypergraph(instance, output_path)

if __name__ == "__main__":
    main()