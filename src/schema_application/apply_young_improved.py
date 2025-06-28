#!/usr/bin/env python3
"""
Improved Young 1996 cognitive mapping with multi-stage processing
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

class ConceptExtraction(BaseModel):
    """Stage 1: All potential concepts"""
    raw_concepts: List[Dict[str, Any]] = Field(
        description="All noun phrases with their context and frequency"
    )

class FilteredConcepts(BaseModel):
    """Stage 2: Politically relevant concepts"""
    concepts: List[Dict[str, Any]] = Field(
        description="Filtered concepts with IDs and initial salience"
    )
    filtering_rationale: Dict[str, str] = Field(
        description="Why each concept was included/excluded"
    )

class RelationshipExtraction(BaseModel):
    """Stage 3: Relationships between concepts"""
    relationships: List[Dict[str, Any]] = Field(
        description="All relationships with full specifications"
    )
    conjunctions: List[Dict[str, Any]] = Field(
        description="AND/OR groupings of concepts"
    )

class CognitiveMapFinal(BaseModel):
    """Final cognitive map with adjusted salience"""
    concepts: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    conjunctions: List[Dict[str, Any]]
    measures: Dict[str, float]

def stage1_extract_all_concepts(text: str) -> ConceptExtraction:
    """Extract ALL noun phrases as potential concepts"""
    
    prompt = f"""Extract ALL noun phrases from this text as potential concepts.

Include:
- Proper nouns (people, places, organizations)
- Common nouns (objects, ideas, abstractions)
- Compound nouns
- Noun phrases with modifiers

For each, record:
- The exact phrase
- Number of occurrences
- Sample context (first occurrence)

TEXT:
{text[:180000]}

Return as JSON:
{{
  "raw_concepts": [
    {{
      "phrase": "Soviet Union",
      "count": 5,
      "first_context": "...relations with the Soviet Union...",
      "type": "entity"
    }}
  ]
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Extract all noun phrases comprehensively."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return ConceptExtraction(**json.loads(response.choices[0].message.content))

def stage2_filter_political_relevance(raw_concepts: ConceptExtraction, speech_context: str) -> FilteredConcepts:
    """Filter for politically/diplomatically relevant concepts"""
    
    concepts_json = json.dumps([c for c in raw_concepts.raw_concepts], indent=2)
    
    prompt = f"""Filter these concepts for POLITICAL/DIPLOMATIC RELEVANCE in this {speech_context} context.

INCLUSION CRITERIA:
1. Political entities: nations, governments, leaders, institutions
2. Political concepts: policies, ideologies, political values
3. International relations: alliances, conflicts, negotiations
4. Security/military: weapons, defense, threats
5. Economic-political: trade, sanctions, resources with political implications
6. Politically-charged abstractions: peace, freedom, human rights

EXCLUSION CRITERIA:
1. Purely personal references (family members, jokes)
2. Logistical details (locations of meetings, travel plans)
3. Speech mechanics ("press conference", "I want to talk")
4. Generic terms without political significance

RAW CONCEPTS:
{concepts_json}

Return as JSON with rationale for each decision:
{{
  "concepts": [
    {{
      "id": "c1",
      "label": "Soviet Union",
      "included": true,
      "rationale": "Primary geopolitical actor in Cold War context",
      "initial_salience": 5
    }}
  ],
  "filtering_rationale": {{
    "Billy": "Excluded - personal reference to brother, not politically relevant",
    "Soviet Union": "Included - central geopolitical actor"
  }}
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Apply political science relevance filtering."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    # Filter to only included concepts
    result['concepts'] = [c for c in result['concepts'] if c.get('included', True)]
    
    return FilteredConcepts(**result)

def stage3_extract_relationships(text: str, concepts: FilteredConcepts, schema: dict) -> RelationshipExtraction:
    """Extract relationships with proper types and modifiers"""
    
    concept_list = json.dumps(concepts.concepts, indent=2)
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
    
    prompt = f"""Extract ALL relationships between these politically relevant concepts.

CONCEPTS:
{concept_list}

RELATIONSHIP TYPES: {', '.join(relationship_types)}
ACTION VERBS: {', '.join(action_verbs)}
TRUTH VALUES: {modifiers['options']['truth_values']}
TEMPORAL: {modifiers['categories']['temporal']}
MODAL: {modifiers['categories']['modal']}

EXTRACTION RULES:
1. Find every statement linking two concepts
2. Classify the relationship type precisely
3. Identify truth value from context
4. Add ALL applicable modifiers
5. Note if concepts appear together in AND/OR constructions
6. Assign relationship salience (1-3) based on:
   - Emphasis in speech
   - Repetition
   - Rhetorical importance

TEXT:
{text[:180000]}

Return as JSON:
{{
  "relationships": [
    {{
      "id": "r1",
      "subject": "c1",
      "type": "negotiate",
      "object": "c2",
      "truth_value": "present",
      "modifiers": ["present", "ongoing"],
      "salience": 2,
      "evidence": "quote from text showing this relationship"
    }}
  ],
  "conjunctions": [
    {{
      "type": "AND",
      "members": ["c1", "c2"],
      "context": "where they appear together"
    }}
  ]
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Extract political relationships following Young's methodology."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return RelationshipExtraction(**json.loads(response.choices[0].message.content))

def stage4_calculate_final_salience(
    concepts: FilteredConcepts,
    relationships: RelationshipExtraction,
    raw_concepts: ConceptExtraction
) -> CognitiveMapFinal:
    """Calculate final salience scores based on multiple factors"""
    
    concepts_json = json.dumps(concepts.concepts, indent=2)
    relationships_json = json.dumps(relationships.relationships, indent=2)
    raw_json = json.dumps(raw_concepts.raw_concepts, indent=2)
    
    prompt = f"""Calculate FINAL SALIENCE scores for concepts using Young's methodology.

FACTORS TO CONSIDER:
1. Raw frequency (from initial extraction)
2. Relationship participation (how many relationships involve this concept)
3. Relationship importance (salience of relationships)
4. Rhetorical emphasis (headlines, repetition, conclusions)
5. Structural position (subject vs object in relationships)

RAW FREQUENCIES:
{raw_json}

FILTERED CONCEPTS:
{concepts_json}

RELATIONSHIPS:
{relationships_json}

Calculate final salience (1-10+ scale) where:
- 1-3: Mentioned but peripheral
- 4-6: Important supporting concepts
- 7-10: Central to the cognitive map
- 10+: Absolutely central (e.g., US/USSR in Cold War speech)

Return complete cognitive map as JSON:
{{
  "concepts": [
    {{
      "id": "c1",
      "label": "Soviet Union",
      "salience": 15,
      "salience_factors": {{
        "frequency": 8,
        "relationships": 12,
        "rhetorical_emphasis": "high",
        "structural_centrality": "very high"
      }}
    }}
  ],
  "relationships": [...],
  "conjunctions": [...],
  "measures": {{}}
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Calculate nuanced salience scores."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    
    # Add structural measures
    num_concepts = len(result['concepts'])
    num_relationships = len(result['relationships'])
    
    if num_concepts + num_relationships > 0:
        connectedness = num_relationships / (num_concepts + num_relationships)
    else:
        connectedness = 0
        
    result['measures'] = {
        'size': num_concepts,
        'num_relationships': num_relationships,
        'connectedness': connectedness
    }
    
    return CognitiveMapFinal(**result)

def apply_young_improved(text: str, schema_path: str, speech_context: str = "diplomatic speech") -> CognitiveMapFinal:
    """Apply Young 1996 theory with improved multi-stage process"""
    
    # Load schema
    with open(schema_path, 'r') as f:
        schema = yaml.safe_load(f)
    
    print("Stage 1: Extracting all concepts...")
    raw_concepts = stage1_extract_all_concepts(text)
    print(f"  Found {len(raw_concepts.raw_concepts)} potential concepts")
    
    print("Stage 2: Filtering for political relevance...")
    filtered = stage2_filter_political_relevance(raw_concepts, speech_context)
    print(f"  Retained {len(filtered.concepts)} politically relevant concepts")
    
    print("Stage 3: Extracting relationships...")
    relationships = stage3_extract_relationships(text, filtered, schema)
    print(f"  Found {len(relationships.relationships)} relationships")
    
    print("Stage 4: Calculating final salience...")
    final_map = stage4_calculate_final_salience(filtered, relationships, raw_concepts)
    print(f"  Final map: {len(final_map.concepts)} concepts, {len(final_map.relationships)} relationships")
    
    return final_map

def save_cognitive_map(instance: CognitiveMapFinal, output_path: str):
    """Save improved cognitive map as YAML"""
    
    yaml_output = {
        'theory': 'Young 1996 Cognitive Mapping (Improved)',
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
    
    print(f"\nImproved Cognitive Map Saved to: {output_path}")

def main():
    if len(sys.argv) != 4:
        print("Usage: python apply_young_improved.py <text_file> <schema_file> <output_file>")
        sys.exit(1)
    
    text_path = sys.argv[1]
    schema_path = sys.argv[2]
    output_path = sys.argv[3]
    
    # Load text
    with open(text_path, 'r') as f:
        text = f.read()
    
    # Determine speech context
    if "carter" in text_path.lower():
        context = "1977 Cold War diplomatic speech"
    else:
        context = "diplomatic speech"
    
    # Apply improved process
    instance = apply_young_improved(text, schema_path, context)
    
    # Save results
    save_cognitive_map(instance, output_path)

if __name__ == "__main__":
    main()