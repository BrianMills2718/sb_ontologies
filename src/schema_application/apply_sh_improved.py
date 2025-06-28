#!/usr/bin/env python3
"""
Improved Semantic Hypergraph application with proper α-β staging
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment
load_dotenv()
client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "o3")

class AlphaStageResult(BaseModel):
    """α-stage: All tokens with type assignments"""
    tokens: List[Dict[str, Any]] = Field(
        description="All tokens with their types and positions"
    )
    type_distribution: Dict[str, int] = Field(
        description="Count of each type"
    )

class BetaStageResult(BaseModel):
    """β-stage: Basic hyperedge construction"""
    atoms: List[Dict[str, Any]] = Field(
        description="All atomic hyperedges"
    )
    basic_hyperedges: List[Dict[str, Any]] = Field(
        description="First-level non-atomic hyperedges"
    )

class RecursiveComposition(BaseModel):
    """Final stage: Recursive hyperedge composition"""
    atoms: List[Dict[str, Any]]
    hyperedges: List[Dict[str, Any]]
    discourse_structures: List[Dict[str, Any]] = Field(
        description="High-level discourse patterns"
    )

def stage1_alpha_typing(text: str, schema: dict) -> AlphaStageResult:
    """α-stage: Type every token in the text"""
    
    type_codes = schema['notation']['type_codes']
    
    prompt = f"""Perform α-stage parsing: classify EVERY meaningful token with a type code.

TYPE CODES:
{json.dumps(type_codes, indent=2)}

DETAILED TYPING RULES:
- C (concept): Nouns, noun phrases, entities, things discussed
- P (predicate): Verbs, actions, relations, states
- M (modifier): Adjectives, adverbs, qualifiers  
- B (builder): and, or, with, including - things that combine
- T (trigger): if, when, because, since - conditionals/causals
- J (conjunction): punctuation, then, therefore - connectors
- R (relation): Complex predicates formed from simpler ones
- S (specifier): Numbers, percentages, specific values

For a debate text, pay special attention to:
- Argument indicators (T types): "because", "therefore", "if...then"
- Position markers (P types): "believe", "argue", "contend"
- Qualifiers (M types): "possibly", "certainly", "allegedly"
- Evidence markers (S types): dates, statistics, quotes

TEXT (parse completely):
{text[:180000]}

Return as JSON:
{{
  "tokens": [
    {{"position": 0, "token": "Iran", "type": "C", "reason": "country entity"}},
    {{"position": 1, "token": "is", "type": "P", "reason": "copula predicate"}},
    {{"position": 2, "token": "really", "type": "M", "reason": "intensifier modifier"}},
    {{"position": 3, "token": "a", "type": null, "reason": "article - skip"}},
    {{"position": 4, "token": "threat", "type": "C", "reason": "abstract concept"}}
  ],
  "type_distribution": {{"C": 45, "P": 23, "M": 12, ...}}
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Perform systematic α-stage token typing."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return AlphaStageResult(**json.loads(response.choices[0].message.content))

def stage2_beta_construction(alpha_result: AlphaStageResult, schema: dict) -> BetaStageResult:
    """β-stage: Build hyperedges bottom-up"""
    
    type_rules = schema['properties']['formulas']['type_inference']
    tokens_json = json.dumps(alpha_result.tokens[:500], indent=2)  # Sample for prompt
    
    prompt = f"""Perform β-stage parsing: build hyperedges using type inference rules.

TYPE INFERENCE RULES:
{json.dumps(type_rules, indent=2)}

CONSTRUCTION PROCESS:
1. Create atoms for each typed token (id format: a1, a2...)
2. Apply inference rules bottom-up:
   - (M x) → x: Attach modifiers to what they modify
   - (B C C+) → C: Builders combine concepts
   - (P args) → R: Predicates with arguments form relations
   - (T R) → R: Triggers condition relations
   - (J R R) → R: Conjunctions connect relations

3. Assign argument roles:
   - s: subject (actor/agent)
   - o: object (patient/theme)  
   - a: attribute
   - c: condition
   - i: instrument
   - t: time
   - p: purpose
   - r: result

TYPED TOKENS (first 500):
{tokens_json}

Build ALL possible hyperedges following the rules. Return as JSON:
{{
  "atoms": [
    {{"id": "a1", "label": "Iran", "type": "C"}},
    {{"id": "a2", "label": "threat", "type": "C"}},
    {{"id": "a3", "label": "is", "type": "P"}},
    {{"id": "a4", "label": "really", "type": "M"}}
  ],
  "basic_hyperedges": [
    {{
      "id": "h1",
      "connector": "a3",
      "arguments": ["a1", "h2"],
      "type": "R",
      "roles": "so",
      "derivation": "(P C C) → R"
    }},
    {{
      "id": "h2", 
      "connector": "a4",
      "arguments": ["a2"],
      "type": "C",
      "roles": null,
      "derivation": "(M C) → C"
    }}
  ]
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Apply type inference rules systematically."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return BetaStageResult(**json.loads(response.choices[0].message.content))

def stage3_recursive_composition(
    beta_result: BetaStageResult, 
    text: str,
    domain: str = "debate"
) -> RecursiveComposition:
    """Compose recursive structures and identify discourse patterns"""
    
    atoms_json = json.dumps(beta_result.atoms[:50], indent=2)
    hyperedges_json = json.dumps(beta_result.basic_hyperedges[:30], indent=2)
    
    prompt = f"""Complete Semantic Hypergraph parsing with recursive composition.

CURRENT STRUCTURES:
Atoms: {atoms_json}
Basic Hyperedges: {hyperedges_json}

COMPOSITION TASKS:
1. Create nested hyperedges where hyperedges serve as arguments
2. Identify discourse patterns for {domain}:
   - Claim-Evidence structures
   - Argument-Counterargument pairs  
   - Conditional reasoning chains
   - Causal explanations

3. Build high-level structures like:
   - (T (P argue X) (P conclude Y)): "If X is argued, then Y follows"
   - (J (P claim A) (P rebut B)): "A is claimed but B rebuts it"
   - (B (P position1) (P position2)): Combined positions

4. For debate texts specifically:
   - Turn-taking structures
   - Agreement/disagreement patterns
   - Evidence citation structures
   - Rhetorical questions

ORIGINAL TEXT (for reference):
{text[:10000]}

Return as JSON with ALL atoms, ALL hyperedges (basic + recursive), and discourse structures:
{{
  "atoms": [...all atoms...],
  "hyperedges": [
    ...all basic hyperedges...,
    {{
      "id": "h50",
      "connector": "a_if",
      "arguments": ["h10", "h20"],
      "type": "R", 
      "roles": "cr",
      "level": "recursive",
      "interpretation": "conditional argument"
    }}
  ],
  "discourse_structures": [
    {{
      "pattern": "claim-evidence",
      "claim": "h15",
      "evidence": ["h16", "h17"],
      "speaker": "Stephens"
    }}
  ]
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"Complete SH parsing for {domain} text."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return RecursiveComposition(**json.loads(response.choices[0].message.content))

def apply_sh_improved(text: str, schema_path: str, domain: str = "debate") -> RecursiveComposition:
    """Apply Semantic Hypergraph with proper α-β-recursive staging"""
    
    # Load schema
    with open(schema_path, 'r') as f:
        schema = yaml.safe_load(f)
    
    print("α-stage: Typing all tokens...")
    alpha_result = stage1_alpha_typing(text, schema)
    print(f"  Typed {len(alpha_result.tokens)} tokens")
    print(f"  Distribution: {alpha_result.type_distribution}")
    
    print("β-stage: Building basic hyperedges...")
    beta_result = stage2_beta_construction(alpha_result, schema)
    print(f"  Created {len(beta_result.atoms)} atoms")
    print(f"  Built {len(beta_result.basic_hyperedges)} basic hyperedges")
    
    print("Recursive composition stage...")
    final_result = stage3_recursive_composition(beta_result, text, domain)
    print(f"  Total hyperedges: {len(final_result.hyperedges)}")
    print(f"  Discourse structures: {len(final_result.discourse_structures)}")
    
    return final_result

def visualize_improved_hypergraph(result: RecursiveComposition) -> str:
    """Create enhanced visualization with discourse structures"""
    
    atom_map = {a['id']: a for a in result.atoms}
    edge_map = {h['id']: h for h in result.hyperedges}
    
    def format_element(elem_id: str, indent: int = 0) -> str:
        prefix = "  " * indent
        
        if elem_id in atom_map:
            atom = atom_map[elem_id]
            return f"{prefix}{atom['label']}/{atom['type']}"
        elif elem_id in edge_map:
            edge = edge_map[elem_id]
            connector = atom_map.get(edge['connector'], {'label': edge['connector']})
            result = f"{prefix}({connector.get('label', connector)}"
            if edge.get('roles'):
                result += f".{edge['roles']}"
            if edge.get('level') == 'recursive':
                result += " [NESTED]"
            for arg_id in edge.get('arguments', []):
                result += "\n" + format_element(arg_id, indent + 1)
            result += f"\n{prefix})"
            return result
        return f"{prefix}[{elem_id}]"
    
    # Find root hyperedges
    used_as_args = set()
    for h in result.hyperedges:
        used_as_args.update(h.get('arguments', []))
    
    roots = [h['id'] for h in result.hyperedges if h['id'] not in used_as_args]
    
    output = ["=== HYPERGRAPH STRUCTURE ===\n"]
    for root_id in roots[:10]:  # Limit to first 10 for readability
        output.append(format_element(root_id))
    
    if result.discourse_structures:
        output.append("\n=== DISCOURSE PATTERNS ===\n")
        for ds in result.discourse_structures[:5]:
            output.append(f"Pattern: {ds.get('pattern', 'unknown')}")
            for key, value in ds.items():
                if key != 'pattern':
                    output.append(f"  {key}: {value}")
            output.append("")
    
    return "\n".join(output)

def save_improved_hypergraph(result: RecursiveComposition, output_path: str):
    """Save improved hypergraph as YAML"""
    
    yaml_output = {
        'theory': 'Semantic Hypergraph (Improved)',
        'atoms': result.atoms,
        'hyperedges': result.hyperedges,
        'discourse_structures': result.discourse_structures,
        'visualization': visualize_improved_hypergraph(result),
        'summary': {
            'total_atoms': len(result.atoms),
            'total_hyperedges': len(result.hyperedges),
            'recursive_hyperedges': len([h for h in result.hyperedges if h.get('level') == 'recursive']),
            'discourse_patterns': len(result.discourse_structures),
            'type_distribution': {}
        }
    }
    
    # Calculate type distribution
    for atom in result.atoms:
        atom_type = atom.get('type', 'unknown')
        yaml_output['summary']['type_distribution'][atom_type] = \
            yaml_output['summary']['type_distribution'].get(atom_type, 0) + 1
    
    with open(output_path, 'w') as f:
        yaml.dump(yaml_output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\nImproved Semantic Hypergraph Saved to: {output_path}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python apply_sh_improved.py <text_file> <schema_file> <output_file> [domain]")
        sys.exit(1)
    
    text_path = sys.argv[1]
    schema_path = sys.argv[2]
    output_path = sys.argv[3]
    domain = sys.argv[4] if len(sys.argv) > 4 else "debate"
    
    # Load text
    with open(text_path, 'r') as f:
        text = f.read()
    
    # Apply improved process
    result = apply_sh_improved(text, schema_path, domain)
    
    # Save results
    save_improved_hypergraph(result, output_path)

if __name__ == "__main__":
    main()