#!/usr/bin/env python3
"""
Apply Young 1996 cognitive mapping theory to text
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment
load_dotenv()
client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "o3")

class CognitiveMapInstance(BaseModel):
    """Instance of Young 1996 cognitive map"""
    
    # Concepts extracted from text
    concepts: List[Dict[str, Any]] = Field(
        description="All unique concepts/noun-phrases found in text"
    )
    
    # Relationships between concepts
    relationships: List[Dict[str, Any]] = Field(
        description="All relationships with subject, type, object, modifiers, truth values"
    )
    
    # Conjunctions found
    conjunctions: List[Dict[str, Any]] = Field(
        description="AND/OR conjunctions grouping multiple concepts"
    )
    
    # Structural measures
    measures: Dict[str, float] = Field(
        description="Calculated structural measures",
        default_factory=dict
    )

def apply_young_to_text(text: str, schema_path: str) -> CognitiveMapInstance:
    """Apply Young 1996 theory to extract cognitive map from text"""
    
    # Load the theory schema
    with open(schema_path, 'r') as f:
        schema = yaml.safe_load(f)
    
    # Extract key theory elements
    relationship_types = []
    action_verbs = []
    for conn in schema.get('connections', []):
        if conn.get('vocabulary'):
            for vocab in conn['vocabulary']:
                if vocab.startswith('ACTION:'):
                    action_verbs.append(vocab.replace('ACTION:', '').strip())
                else:
                    relationship_types.append(vocab)
    
    modifiers = schema.get('modifiers', {})
    
    prompt = f"""Apply Young 1996 cognitive mapping theory to extract a cognitive map from this text.

THEORY ELEMENTS:
- Relationship types: {', '.join(relationship_types)}
- Action verbs: {', '.join(action_verbs)}
- Truth values: {modifiers['options']['truth_values']}
- Temporal modifiers: {modifiers['categories']['temporal']}
- Modal modifiers: {modifiers['categories']['modal']}

EXTRACTION RULES:
1. Extract ALL unique concepts (noun phrases)
2. Extract ALL relationships between concepts
3. For each relationship identify:
   - Subject concept
   - Relationship type (from vocabulary)
   - Object concept
   - Truth value
   - Modifiers (temporal/modal)
4. Group concepts connected by AND/OR
5. Calculate salience by counting occurrences

TEXT:
{text}

Return complete cognitive map as JSON:
{{
  "concepts": [
    {{"id": "c1", "label": "concept name", "salience": 1}}
  ],
  "relationships": [
    {{
      "id": "r1",
      "subject": "concept_id",
      "type": "relationship_type",
      "object": "concept_id", 
      "truth_value": "true|false|possible|etc",
      "modifiers": ["present", "goal", etc],
      "salience": 1
    }}
  ],
  "conjunctions": [
    {{"type": "AND|OR", "members": ["concept_id1", "concept_id2"]}}
  ]
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Extract cognitive map following Young 1996 theory exactly."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    
    # Calculate structural measures
    num_concepts = len(result.get('concepts', []))
    num_relationships = len(result.get('relationships', []))
    
    if num_concepts + num_relationships > 0:
        connectedness = num_relationships / (num_concepts + num_relationships)
    else:
        connectedness = 0
        
    result['measures'] = {
        'size': num_concepts,
        'num_relationships': num_relationships,
        'connectedness': connectedness
    }
    
    return CognitiveMapInstance(**result)

def save_cognitive_map(instance: CognitiveMapInstance, output_path: str):
    """Save cognitive map instance as YAML"""
    
    # Convert to YAML-friendly format
    yaml_output = {
        'theory': 'Young 1996 Cognitive Mapping',
        'concepts': instance.concepts,
        'relationships': instance.relationships,
        'conjunctions': instance.conjunctions,
        'structural_measures': instance.measures,
        'summary': {
            'total_concepts': len(instance.concepts),
            'total_relationships': len(instance.relationships),
            'unique_relationship_types': len(set(r['type'] for r in instance.relationships)),
            'connectedness': instance.measures.get('connectedness', 0)
        }
    }
    
    with open(output_path, 'w') as f:
        yaml.dump(yaml_output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\nCognitive Map Extracted:")
    print(f"- Concepts: {len(instance.concepts)}")
    print(f"- Relationships: {len(instance.relationships)}")
    print(f"- Connectedness: {instance.measures.get('connectedness', 0):.3f}")
    print(f"Saved to: {output_path}")

def main():
    if len(sys.argv) != 4:
        print("Usage: python apply_young_theory.py <text_file> <schema_file> <output_file>")
        sys.exit(1)
    
    text_path = sys.argv[1]
    schema_path = sys.argv[2]
    output_path = sys.argv[3]
    
    # Load text
    with open(text_path, 'r') as f:
        text = f.read()
    
    # Apply theory
    instance = apply_young_to_text(text, schema_path)
    
    # Save results
    save_cognitive_map(instance, output_path)

if __name__ == "__main__":
    main()