#!/usr/bin/env python3
"""
Apply Semantic Hypergraph schema to Iran debate transcript
Enhanced version with better argument role handling for debates
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

# Enhanced SH structures with argument roles
class AtomWithRoles(BaseModel):
    """Atomic hyperedge with role support"""
    id: str
    term: str
    type: str = Field(description="C (concept), P (predicate), M (modifier), B (builder), J (conjunction), T (trigger)")
    roles: Optional[str] = Field(description="Role codes like 'sa' for subject-argument")

class HyperedgeWithRoles(BaseModel):
    """Non-atomic hyperedge with enhanced role support"""
    id: str
    connector: AtomWithRoles
    arguments: List[str] = Field(description="IDs of atoms or other hyperedges")
    argument_roles: Optional[List[str]] = Field(description="Role for each argument")
    ordered: bool = True
    truth_value: Optional[str] = None
    modifiers: Optional[List[str]] = None

class EnhancedSHInstance(BaseModel):
    """Enhanced SH representation with debate-specific features"""
    atoms: List[AtomWithRoles]
    hyperedges: List[HyperedgeWithRoles]
    main_hyperedge: str = Field(description="ID of top-level hyperedge")

# Enhanced extraction prompt for debates
DEBATE_SH_EXTRACTION_PROMPT = """You are an expert in Semantic Hypergraph (SH) representation, specifically for debate transcripts.

Extract SH structures following the full theory, including ARGUMENT ROLES:

1. **Atoms with Types**:
   - C: Concepts (people, countries, programs)
   - P: Predicates with roles (e.g., P.sa for subject-argument)
   - M: Modifiers
   - B: Builders (especially +/B for compounds)
   - J: Conjunctions
   - T: Triggers (temporal/conditional)

2. **Predicate Roles** (crucial for debates):
   - Use P.xyz format where:
     - x = subject role (s=subject, a=agent)
     - y = object role (o=object, c=complement, a=argument)
     - z = other roles (x=specification)
   - Examples:
     - warn/P.soa (subject warns object about argument)
     - believe/P.sa (subject believes argument)
     - accomplish/P.so (subject accomplishes object)

3. **Debate-Specific Patterns**:
   - Claims: (claim/P.sa speaker proposition)
   - Counter-claims: (counter/P.saa speaker1 speaker2 proposition)
   - Agreement: (agree/P.sao speaker1 speaker2 topic)
   - Conditionals: (if/T condition consequence)

4. **Nested Propositions**:
   - "X thinks Y believes Z" → nested hyperedges
   - Capture debate positions as nested claims

Focus on:
- Who argues what
- Disagreements and agreements
- Conditional arguments ("if Iran gets nukes, then...")
- Evidence citations

Be precise with argument roles!"""

def extract_debate_sh_structures(text: str) -> EnhancedSHInstance:
    """Extract enhanced SH representation from debate text"""
    
    messages = [
        {"role": "system", "content": DEBATE_SH_EXTRACTION_PROMPT},
        {"role": "user", "content": f"Extract SH structures from this debate transcript:\n\n{text}"}
    ]
    
    print("Extracting SH structures with argument roles...")
    start = time.time()
    
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=messages,
        response_format=EnhancedSHInstance
    )
    
    result = response.choices[0].message.parsed
    print(f"Extraction complete in {time.time() - start:.2f} seconds")
    
    return result

def visualize_debate_sh(instance: EnhancedSHInstance) -> str:
    """Create enhanced visualization showing argument roles"""
    output = []
    output.append("SEMANTIC HYPERGRAPH - IRAN DEBATE")
    output.append("=" * 60)
    
    # Show atoms with roles
    output.append("\nATOMS:")
    for atom in instance.atoms:
        role_str = f".{atom.roles}" if atom.roles else ""
        output.append(f"  {atom.id}: {atom.term}/{atom.type}{role_str}")
    
    # Show hyperedges with argument roles
    output.append("\nHYPEREDGES:")
    for he in instance.hyperedges:
        # Build argument string with roles
        args_with_roles = []
        for i, arg in enumerate(he.arguments):
            role = he.argument_roles[i] if he.argument_roles and i < len(he.argument_roles) else ""
            role_str = f":{role}" if role else ""
            args_with_roles.append(f"{arg}{role_str}")
        
        args_str = " ".join(args_with_roles)
        connector_roles = f".{he.connector.roles}" if he.connector.roles else ""
        mods = f" [{', '.join(he.modifiers)}]" if he.modifiers else ""
        truth = f" <{he.truth_value}>" if he.truth_value else ""
        
        output.append(f"  {he.id}: ({he.connector.term}/{he.connector.type}{connector_roles} {args_str}){mods}{truth}")
    
    # Show debate positions could be added here if tracked separately
    
    output.append(f"\nMAIN: {instance.main_hyperedge}")
    
    return "\n".join(output)

def create_debate_visualization_data(instance: EnhancedSHInstance) -> Dict:
    """Create data structure for debate-specific visualization"""
    viz_data = {
        "speakers": [],
        "claims": [],
        "agreements": [],
        "disagreements": [],
        "conditionals": []
    }
    
    # Identify speakers
    speaker_atoms = [a for a in instance.atoms if a.type == "C" and any(
        name in a.term.lower() for name in ["stephens", "kelanic", "leonhardt"]
    )]
    viz_data["speakers"] = [{"id": a.id, "name": a.term} for a in speaker_atoms]
    
    # Categorize hyperedges by debate function
    for he in instance.hyperedges:
        connector_term = he.connector.term.lower()
        
        if any(word in connector_term for word in ["claim", "argue", "think", "believe"]):
            viz_data["claims"].append({
                "id": he.id,
                "speaker": he.arguments[0] if he.arguments else None,
                "content": he.arguments[1:] if len(he.arguments) > 1 else [],
                "type": he.connector.term
            })
        elif any(word in connector_term for word in ["agree", "concur"]):
            viz_data["agreements"].append({
                "id": he.id,
                "parties": he.arguments[:2] if len(he.arguments) >= 2 else he.arguments,
                "topic": he.arguments[2] if len(he.arguments) > 2 else None
            })
        elif any(word in connector_term for word in ["disagree", "counter", "push"]):
            viz_data["disagreements"].append({
                "id": he.id,
                "parties": he.arguments[:2] if len(he.arguments) >= 2 else he.arguments,
                "topic": he.arguments[2] if len(he.arguments) > 2 else None
            })
        elif connector_term == "if" or he.connector.type == "T":
            viz_data["conditionals"].append({
                "id": he.id,
                "condition": he.arguments[0] if he.arguments else None,
                "consequence": he.arguments[1] if len(he.arguments) > 1 else None
            })
    
    return viz_data

def main():
    """Main execution"""
    # Paths
    debate_path = "/home/brian/lit_review/data/test_texts/iran_debate.txt"
    output_dir = Path("/home/brian/lit_review/results/semantic_hypergraph/iran_debate")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("SEMANTIC HYPERGRAPH - IRAN DEBATE ANALYSIS")
    print("=" * 60)
    
    # Read debate text
    print(f"\n1. Reading debate from: {debate_path}")
    with open(debate_path, 'r') as f:
        debate_text = f.read()
    
    # Use a substantial excerpt (3000 chars to get good debate content)
    debate_excerpt = debate_text[:3000]
    print(f"   Using excerpt: {len(debate_excerpt)} characters")
    
    # Extract SH structures
    print(f"\n2. Extracting SH structures with argument roles...")
    sh_instance = extract_debate_sh_structures(debate_excerpt)
    
    print(f"\n   Extracted:")
    print(f"   - {len(sh_instance.atoms)} atoms")
    print(f"   - {len(sh_instance.hyperedges)} hyperedges")
    
    # Check for role usage
    roles_used = sum(1 for a in sh_instance.atoms if a.roles)
    print(f"   - {roles_used} atoms with role specifications")
    
    # Visualize
    print(f"\n3. Visualization:")
    print("-" * 60)
    viz = visualize_debate_sh(sh_instance)
    print(viz)
    
    # Save visualization
    viz_path = output_dir / "iran_debate_sh_visualization.txt"
    with open(viz_path, 'w') as f:
        f.write(viz)
    print(f"\n   Saved visualization to: {viz_path}")
    
    # Create debate-specific visualization data
    debate_viz = create_debate_visualization_data(sh_instance)
    debate_viz_path = output_dir / "iran_debate_structure.json"
    with open(debate_viz_path, 'w') as f:
        json.dump(debate_viz, f, indent=2)
    print(f"   Saved debate structure to: {debate_viz_path}")
    
    # Convert to YAML with enhanced metadata
    yaml_data = {
        "schema_reference": "/home/brian/lit_review/schemas/semantic_hypergraph/semantic_hypergraph_complete.yml",
        "model_type": "hypergraph",
        "content_type": "debate_transcript",
        "instance": {
            "atoms": [a.model_dump() for a in sh_instance.atoms],
            "hyperedges": [h.model_dump() for h in sh_instance.hyperedges],
            "main_hyperedge": sh_instance.main_hyperedge,
            "debate_metadata": debate_viz
        }
    }
    
    yaml_path = output_dir / "iran_debate_sh_instance.yml"
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\n4. Complete!")
    print(f"   - Visualization: {viz_path}")
    print(f"   - YAML instance: {yaml_path}")
    print(f"   - Debate structure: {debate_viz_path}")
    
    # Summary statistics
    print(f"\n5. Debate Analysis Summary:")
    print(f"   - Speakers identified: {len(debate_viz['speakers'])}")
    print(f"   - Claims made: {len(debate_viz['claims'])}")
    print(f"   - Agreements: {len(debate_viz['agreements'])}")
    print(f"   - Disagreements: {len(debate_viz['disagreements'])}")
    print(f"   - Conditional arguments: {len(debate_viz['conditionals'])}")

if __name__ == "__main__":
    main()