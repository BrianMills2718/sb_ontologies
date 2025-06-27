#!/usr/bin/env python3
"""
Apply Semantic Hypergraph schema to Ground News text
Demonstrates instantiation of hyperedges with claims, conflicts, and nested propositions
"""

import os
import sys
import json
import yaml
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "o3")

# SH-specific structures based on the schema
class Atom(BaseModel):
    """Atomic hyperedge - single word/concept"""
    id: str
    term: str
    type: str = Field(description="C (concept), P (predicate), M (modifier), B (builder), J (conjunction), T (trigger)")

class Hyperedge(BaseModel):
    """Non-atomic hyperedge with connector and arguments"""
    id: str
    connector: Atom
    arguments: List[str] = Field(description="IDs of atoms or other hyperedges")
    ordered: bool = True
    truth_value: Optional[str] = None
    modifiers: Optional[List[str]] = None

class SHInstance(BaseModel):
    """Complete SH representation of text"""
    atoms: List[Atom]
    hyperedges: List[Hyperedge]
    main_hyperedge: str = Field(description="ID of top-level hyperedge")

# Extraction prompt based on SH theory
SH_EXTRACTION_PROMPT = """You are an expert in Semantic Hypergraph (SH) representation.

Extract SH structures from the given news text following these rules:

1. **Atoms** - Identify atomic units:
   - C: Concepts (entities, actors, objects)
   - P: Predicates (actions, relations like "alleges", "condemns")
   - M: Modifiers (adjectives, adverbs)
   - B: Builders (compound constructors)
   - T: Triggers (temporal/spatial context)

2. **Hyperedges** - Build recursive structures:
   - Every non-atomic hyperedge starts with a connector (P, M, B, J, or T type atom)
   - Arguments are ordered and can be atoms or other hyperedges
   - Claims use predicates like "say", "allege", "describe"
   - Nested propositions for "X says that Y"

3. **Special Focus** for news:
   - Actor-claim relationships: (claim/P actor/C proposition/R)
   - Conflicts: When actors make opposing claims
   - Attribution: Link statements to sources

Example structure for "Spain PM alleges genocide":
- Atoms: spain_pm/C, allege/P, genocide/C
- Hyperedge: (allege/P spain_pm/C genocide/C)

Be systematic and capture the main claims and their nested structure."""

def extract_sh_structures(text: str) -> SHInstance:
    """Extract SH representation from text using OpenAI"""
    
    messages = [
        {"role": "system", "content": SH_EXTRACTION_PROMPT},
        {"role": "user", "content": f"Extract SH structures from this news text:\n\n{text}"}
    ]
    
    print("Extracting SH structures...")
    start = time.time()
    
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=messages,
        response_format=SHInstance
    )
    
    result = response.choices[0].message.parsed
    print(f"Extraction complete in {time.time() - start:.2f} seconds")
    
    return result

def visualize_sh_instance(instance: SHInstance) -> str:
    """Create a text visualization of SH structures"""
    output = []
    output.append("SEMANTIC HYPERGRAPH INSTANCE")
    output.append("=" * 50)
    
    # Show atoms
    output.append("\nATOMS:")
    for atom in instance.atoms:
        output.append(f"  {atom.id}: {atom.term}/{atom.type}")
    
    # Show hyperedges
    output.append("\nHYPEREDGES:")
    for he in instance.hyperedges:
        args = " ".join(he.arguments)
        mods = f" [{', '.join(he.modifiers)}]" if he.modifiers else ""
        truth = f" <{he.truth_value}>" if he.truth_value else ""
        output.append(f"  {he.id}: ({he.connector.term}/{he.connector.type} {args}){mods}{truth}")
    
    # Show main structure
    output.append(f"\nMAIN: {instance.main_hyperedge}")
    
    return "\n".join(output)

def convert_to_yaml_representation(instance: SHInstance, schema_path: str) -> Dict:
    """Convert SH instance to YAML format following the schema"""
    
    # Load the schema for reference
    with open(schema_path, 'r') as f:
        schema = yaml.safe_load(f)
    
    # Build YAML representation
    yaml_data = {
        "schema_reference": schema_path,
        "model_type": "hypergraph",
        "instance": {
            "vertices": [],
            "hyperedges": [],
            "atoms": [],
            "connectors": []
        }
    }
    
    # Add atoms as both atoms and vertices
    for atom in instance.atoms:
        atom_data = {
            "id": atom.id,
            "term": atom.term,
            "type": atom.type
        }
        yaml_data["instance"]["atoms"].append(atom_data)
        
        # Concepts become vertices
        if atom.type == "C":
            yaml_data["instance"]["vertices"].append({
                "id": atom.id,
                "label": atom.term,
                "type": "concept"
            })
        
        # Connectors tracked separately
        if atom.type in ["P", "M", "B", "J", "T"]:
            yaml_data["instance"]["connectors"].append({
                "id": atom.id,
                "term": atom.term,
                "type": atom.type
            })
    
    # Add hyperedges
    for he in instance.hyperedges:
        he_data = {
            "id": he.id,
            "connector_id": he.connector.id,
            "connector_type": he.connector.type,
            "arguments": he.arguments,
            "ordered": he.ordered
        }
        if he.truth_value:
            he_data["truth_value"] = he.truth_value
        if he.modifiers:
            he_data["modifiers"] = he.modifiers
            
        yaml_data["instance"]["hyperedges"].append(he_data)
    
    yaml_data["instance"]["main_hyperedge"] = instance.main_hyperedge
    
    return yaml_data

def main():
    """Main execution"""
    # Paths
    news_path = "/home/brian/lit_review/data/test_texts/ground_news.txt"
    schema_path = "/home/brian/lit_review/schemas/semantic_hypergraph/semantic_hypergraph_complete.yml"
    output_dir = Path("/home/brian/lit_review/results/semantic_hypergraph")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("SEMANTIC HYPERGRAPH INSTANTIATION")
    print("=" * 50)
    
    # Read news text
    print(f"\n1. Reading news from: {news_path}")
    with open(news_path, 'r') as f:
        news_text = f.read()
    
    # Limit to first section for demo
    news_excerpt = news_text[:1500]  # First ~1500 chars
    print(f"   Using excerpt: {len(news_excerpt)} characters")
    
    # Extract SH structures
    print(f"\n2. Extracting SH structures...")
    sh_instance = extract_sh_structures(news_excerpt)
    
    print(f"\n   Extracted:")
    print(f"   - {len(sh_instance.atoms)} atoms")
    print(f"   - {len(sh_instance.hyperedges)} hyperedges")
    
    # Visualize
    print(f"\n3. Visualization:")
    print("-" * 50)
    viz = visualize_sh_instance(sh_instance)
    print(viz)
    
    # Save visualization
    viz_path = output_dir / "ground_news_sh_visualization.txt"
    with open(viz_path, 'w') as f:
        f.write(viz)
    print(f"\nSaved visualization to: {viz_path}")
    
    # Convert to YAML
    print(f"\n4. Converting to YAML format...")
    yaml_data = convert_to_yaml_representation(sh_instance, schema_path)
    
    yaml_path = output_dir / "ground_news_sh_instance.yml"
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"   Saved to: {yaml_path}")
    
    # Save raw instance as JSON for debugging
    json_path = output_dir / "ground_news_sh_raw.json"
    with open(json_path, 'w') as f:
        json.dump(sh_instance.model_dump(), f, indent=2)
    
    print(f"\n5. Complete!")
    print(f"   - Visualization: {viz_path}")
    print(f"   - YAML instance: {yaml_path}")
    print(f"   - Raw JSON: {json_path}")

if __name__ == "__main__":
    main()