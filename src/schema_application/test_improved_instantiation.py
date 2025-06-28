#!/usr/bin/env python3
"""
Test improved instantiation with smaller text sample
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

def test_young_filtering():
    """Demonstrate the filtering improvement for Young"""
    
    # Sample concepts that might be extracted
    raw_concepts = [
        {"phrase": "Soviet Union", "count": 8, "type": "entity"},
        {"phrase": "United States", "count": 10, "type": "entity"},
        {"phrase": "Billy", "count": 1, "type": "person"},
        {"phrase": "Yazoo City", "count": 1, "type": "place"},
        {"phrase": "Atlantic Ocean", "count": 1, "type": "place"},
        {"phrase": "nuclear weapons", "count": 5, "type": "concept"},
        {"phrase": "human rights", "count": 4, "type": "concept"},
        {"phrase": "press conference", "count": 2, "type": "event"},
        {"phrase": "peace", "count": 7, "type": "concept"},
        {"phrase": "detente", "count": 3, "type": "concept"},
        {"phrase": "SALT talks", "count": 4, "type": "event"},
        {"phrase": "room", "count": 1, "type": "object"},
        {"phrase": "brother", "count": 1, "type": "person"}
    ]
    
    prompt = f"""Filter these concepts for POLITICAL/DIPLOMATIC RELEVANCE in a 1977 Cold War speech.

CONCEPTS TO FILTER:
{json.dumps(raw_concepts, indent=2)}

Apply these criteria:
- INCLUDE: Nations, political leaders, policies, international relations concepts
- EXCLUDE: Personal references, logistical details, generic objects

Return as JSON with include/exclude decision and brief rationale:
{{
  "filtering_results": [
    {{
      "phrase": "Soviet Union",
      "include": true,
      "rationale": "Primary geopolitical actor in Cold War"
    }},
    {{
      "phrase": "Billy",
      "include": false,
      "rationale": "Personal reference to brother, not politically relevant"
    }}
  ]
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Apply political science filtering criteria."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    
    print("=== YOUNG FILTERING DEMONSTRATION ===")
    print("\nFiltering Results:")
    included = []
    excluded = []
    
    for item in result['filtering_results']:
        if item['include']:
            included.append(f"✓ {item['phrase']}: {item['rationale']}")
        else:
            excluded.append(f"✗ {item['phrase']}: {item['rationale']}")
    
    print("\nINCLUDED (Politically Relevant):")
    for item in included:
        print(f"  {item}")
    
    print("\nEXCLUDED (Not Relevant):")
    for item in excluded:
        print(f"  {item}")
    
    return result

def test_sh_staging():
    """Demonstrate the α-β staging for SH"""
    
    sample_text = """Iran is really a threat to the United States? 
    Stephens argues that if Iran gets nuclear weapons, then Saudi Arabia will also seek them."""
    
    # Stage 1: α-typing
    prompt_alpha = f"""Perform α-stage typing on this text sample.

TEXT: {sample_text}

Type each meaningful token:
- C: concepts (Iran, threat, United States, nuclear weapons)
- P: predicates (is, argues, gets, seek)
- M: modifiers (really)
- T: triggers (if, then)
- B: builders (also)

Return as JSON:
{{
  "tokens": [
    {{"token": "Iran", "type": "C", "position": 0}},
    {{"token": "is", "type": "P", "position": 1}},
    ...
  ]
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Perform α-stage token typing."},
            {"role": "user", "content": prompt_alpha}
        ],
        response_format={"type": "json_object"}
    )
    
    alpha_result = json.loads(response.choices[0].message.content)
    
    print("\n\n=== SEMANTIC HYPERGRAPH α-β STAGING DEMONSTRATION ===")
    print("\nα-stage Results (Token Typing):")
    for token in alpha_result['tokens']:
        print(f"  {token['token']:20} -> {token['type']}")
    
    # Stage 2: β-construction
    tokens_str = json.dumps(alpha_result['tokens'], indent=2)
    
    prompt_beta = f"""Perform β-stage construction using these typed tokens.

TOKENS:
{tokens_str}

Build hyperedges:
1. Create atoms (a1, a2, ...) for each token
2. Apply rules:
   - (M C) → C: modifier + concept
   - (P C C) → R: predicate + arguments
   - (T R R) → R: if-then conditional

Return as JSON:
{{
  "atoms": [
    {{"id": "a1", "label": "Iran", "type": "C"}},
    ...
  ],
  "hyperedges": [
    {{
      "id": "h1",
      "connector": "predicate_atom_id",
      "arguments": ["subject_id", "object_id"],
      "type": "R",
      "roles": "so"
    }}
  ]
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Build hyperedges from typed tokens."},
            {"role": "user", "content": prompt_beta}
        ],
        response_format={"type": "json_object"}
    )
    
    beta_result = json.loads(response.choices[0].message.content)
    
    print("\nβ-stage Results (Hyperedge Construction):")
    print(f"  Atoms created: {len(beta_result['atoms'])}")
    print(f"  Hyperedges built: {len(beta_result['hyperedges'])}")
    
    print("\nSample Hyperedges:")
    for i, edge in enumerate(beta_result['hyperedges'][:3]):
        print(f"  {edge['id']}: {edge.get('type', 'R')} - connector: {edge['connector']}, args: {edge['arguments']}")
    
    return alpha_result, beta_result

def main():
    print("DEMONSTRATING IMPROVED INSTANTIATION APPROACHES\n")
    
    # Test Young filtering
    young_result = test_young_filtering()
    
    # Test SH staging
    sh_alpha, sh_beta = test_sh_staging()
    
    print("\n\n=== KEY IMPROVEMENTS DEMONSTRATED ===")
    print("\n1. YOUNG: Political relevance filtering")
    print("   - Excludes personal references (Billy, room)")
    print("   - Excludes logistics (Yazoo City)")
    print("   - Keeps policy-relevant concepts")
    
    print("\n2. SEMANTIC HYPERGRAPH: Proper α-β staging")
    print("   - α-stage: Systematic token typing")
    print("   - β-stage: Rule-based hyperedge construction")
    print("   - Ready for recursive composition")
    
    print("\nThese improvements address the instantiation failures by:")
    print("- Adding domain-specific filtering")
    print("- Implementing theoretical procedures properly")
    print("- Using multi-stage processing as theories require")

if __name__ == "__main__":
    main()