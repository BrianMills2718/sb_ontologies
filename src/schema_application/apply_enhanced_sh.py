#!/usr/bin/env python3
"""
Apply enhanced SH schema with proper notation support
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv()
client = OpenAI()

class EnhancedAtom(BaseModel):
    """Atom with full notation support"""
    id: str
    term: str
    type: str = Field(description="Single uppercase letter: C, P, M, B, T, J, R, S")
    roles: Optional[str] = Field(description="Role codes like 'sa', 'soa', 'ma' for predicates/binders")
    notation: Optional[str] = Field(description="Full notation like 'P.sa' or 'B.ma'")

class EnhancedHyperedge(BaseModel):
    """Hyperedge with argument roles"""
    id: str
    connector: EnhancedAtom
    arguments: List[str] = Field(description="Atom IDs in order")
    argument_roles: Optional[List[str]] = Field(description="Role codes for each argument (s, o, a, etc.)")
    ordered: bool = True
    modifiers: Optional[List[str]] = None
    truth_value: Optional[str] = None

class EnhancedSHInstance(BaseModel):
    """Complete SH instance with notation"""
    atoms: List[EnhancedAtom]
    hyperedges: List[EnhancedHyperedge]
    main_hyperedge: str
    notation_notes: Optional[Dict[str, str]] = Field(description="Notes on notation usage")

def apply_enhanced_sh(text_path: str, schema_path: str) -> Dict[str, Any]:
    """Apply enhanced schema with notation awareness"""
    
    # Load text and schema
    with open(text_path, 'r') as f:
        text = f.read()
    
    with open(schema_path, 'r') as f:
        schema = yaml.safe_load(f)
    
    # Build prompt with notation emphasis
    notation_section = ""
    if "notation_system" in schema:
        notation_section = f"""
CRITICAL NOTATION REQUIREMENTS:
Argument Roles: {', '.join([f"{k}={v}" for k, v in list(schema['notation_system']['argument_roles'].items())[:5]])}
- Use these role codes in the 'roles' field for P and B type atoms
- For predicates with subject+object, use 'sa' not just 's'
- For binders, use 'ma' for the modified argument

Special Symbols:
{chr(10).join([f"- {k}: {v}" for k, v in list(schema['notation_system']['special_symbols'].items())[:3]])}

Example notations:
- applaud/P with roles='sa' means "applaud as predicate with subject-argument pattern"
- warn/P with roles='soa' means "warn as predicate with subject-object-action pattern"
"""

    prompt = f"""
Apply the Semantic Hypergraph (SH) formalism to extract structure from this text.

{notation_section}

TEXT TO ANALYZE:
{text[:3000]}

Extract:
1. Atoms with proper type (C/P/M/B/T/J/R/S) and role notation
2. Hyperedges showing relationships with argument roles
3. Use proper SH notation (term/TYPE.role)

Be precise with notation - this is critical for the formalism.
"""

    response = client.beta.chat.completions.parse(
        model="o3-mini",
        messages=[
            {"role": "system", "content": "You are an expert in Semantic Hypergraph notation."},
            {"role": "user", "content": prompt}
        ],
        response_format=EnhancedSHInstance
    )
    
    instance = response.choices[0].message.parsed
    
    # Convert to standard format
    result = {
        "schema_reference": schema_path,
        "model_type": "hypergraph",
        "instance": instance.model_dump()
    }
    
    return result

def main():
    text_path = "/home/brian/lit_review/data/test_texts/iran_debate.txt"
    schema_path = "/home/brian/lit_review/schemas/semantic_hypergraph/semantic_hypergraph_enhanced.yml"
    
    print("Applying enhanced SH schema with notation support...")
    result = apply_enhanced_sh(text_path, schema_path)
    
    # Save result
    output_dir = Path("/home/brian/lit_review/results/semantic_hypergraph/enhanced_extraction")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "iran_debate_enhanced_sh.yml"
    with open(output_path, 'w') as f:
        yaml.dump(result, f, allow_unicode=True, sort_keys=False)
    
    print(f"\nExtraction complete! Saved to: {output_path}")
    
    # Summary
    instance = result['instance']
    print(f"\nAtoms: {len(instance['atoms'])}")
    print("Sample atoms with notation:")
    for atom in instance['atoms'][:5]:
        notation = f"{atom['term']}/{atom['type']}"
        if atom.get('roles'):
            notation += f".{atom['roles']}"
        print(f"  {atom['id']}: {notation}")

if __name__ == "__main__":
    main()