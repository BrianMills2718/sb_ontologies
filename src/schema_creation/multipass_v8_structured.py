#!/usr/bin/env python3
"""
Structured Multi-pass extraction for meta_schema_8
Enforces proper categorization and schema compliance
"""
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class StructuredMultiPassExtractor:
    """Multi-pass extraction with strict schema enforcement"""
    
    def __init__(self):
        self.client = OpenAI()
        self.max_tokens = 60000
        
    def pass1_identify_core_entities(self, content: str) -> Dict[str, Any]:
        """Pass 1: Identify what ARE the fundamental entities/nodes"""
        prompt = """Analyze this academic paper to identify the CORE ENTITIES (nodes/units) of the theory.

CRITICAL DISTINCTION:
- Entities are the THINGS being related (nodes in the network)
- NOT the relationships between them
- NOT actions or properties

For cognitive mapping/network theories:
- "Concept" or "Node" is usually THE core entity type
- Specific concepts like "United States" or "peace" are INSTANCES, not entity types

For other theories, entities might be:
- Actors, Organizations, States (for IR theories)
- Arguments, Claims, Positions (for argumentation theories)  
- Events, Situations (for narrative theories)

Extract:
1. Core entity types defined by the theory
2. Their definitions
3. Example instances (but separate from the type)
4. Properties that entities can have

Output as JSON:
{
  "core_entities": [
    {
      "indigenous_term": "exact term from paper",
      "description": "what this represents",
      "examples": ["instance1", "instance2"],
      "can_have_properties": ["property1", "property2"]
    }
  ],
  "entity_properties": [
    {
      "indigenous_term": "property name",
      "description": "what this property represents",
      "type": "numeric|categorical|boolean|string",
      "applies_to": ["entity_type1", "entity_type2"]
    }
  ]
}"""

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Identify core entities in:\n\n{content[:40000]}"}
        ]
        
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=30000
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def pass2_extract_relationships_and_actions(self, content: str) -> Dict[str, Any]:
        """Pass 2: Extract all relationships and actions"""
        prompt = """Extract ALL relationships and actions from this paper.

CRITICAL: The paper likely has a TABLE or LIST of these. Find it!

DISTINCTION:
1. RELATIONSHIPS: Static connections between entities
   - Examples: "is-a", "part-of", "causes", "equals"
   - Often have symbols: +, -, =, >
   
2. ACTIONS: Dynamic events/verbs that one entity does to another
   - Examples: "attack", "cooperate", "negotiate"
   - These are STILL connections but represent events

For each relationship/action, identify:
- The exact term used (indigenous_term)
- Description
- Symbol/notation if any
- Whether it's a relationship or action
- What types of entities it connects (domain/range)

IMPORTANT: If you find a table with 50 actions, extract ALL 50!

Output as JSON:
{
  "relationships": [
    {
      "indigenous_term": "positive-cause",
      "symbol": "+",
      "description": "...",
      "domain": ["concept"],
      "range": ["concept"]
    }
  ],
  "actions": [
    {
      "indigenous_term": "cooperate",
      "description": "...",
      "domain": ["actor"],
      "range": ["actor"]
    }
  ]
}"""

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ]
        
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=60000
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def pass3_extract_modifiers_and_metadata(self, content: str) -> Dict[str, Any]:
        """Pass 3: Extract modifiers, truth values, and other metadata"""
        prompt = """Extract modifiers and metadata elements from this paper.

MODIFIERS qualify or condition statements:
- Temporal: past, present, future
- Modal: hypothetical, goal, normative
- Certainty: certain, probable, possible
- Truth values: true, false, partial, possible, impossible

Also look for:
- Conjunctions (and, or)
- Quantifiers
- Other qualifiers

For each modifier:
- Indigenous term
- Category (temporal, modal, truth_value, etc.)
- What it can modify (entities, connections, statements)
- Possible values if categorical

Output as JSON:
{
  "modifiers": [
    {
      "indigenous_term": "past",
      "category": "temporal",
      "description": "...",
      "applies_to": ["connections", "statements"]
    }
  ],
  "truth_values": [
    {
      "value": "true",
      "description": "Statement is believed to be factual"
    }
  ],
  "other_metadata": [
    {
      "indigenous_term": "salience",
      "description": "frequency or importance",
      "type": "numeric"
    }
  ]
}"""

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": content[:40000]}
        ]
        
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=30000
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def pass4_extract_process_and_analytics(self, content: str) -> Dict[str, Any]:
        """Pass 4: Extract process steps and analytical measures"""
        prompt = """Extract the process/methodology and analytical measures from this paper.

PROCESS: How to apply the theory
- Step-by-step methodology
- Coding procedures
- Analysis workflows

ANALYTICS: Metrics and measures
- Structural measures (e.g., centrality, density)
- Comparison metrics
- Formulas and calculations
- Success criteria

Look for sections on:
- "Method" or "Methodology"
- "Measures" or "Metrics"
- "Procedure" or "Process"
- Mathematical formulas

Output as JSON:
{
  "process_steps": [
    {
      "step_name": "Identify Beliefs",
      "description": "...",
      "objective": "...",
      "completion_criteria": "..."
    }
  ],
  "metrics": [
    {
      "indigenous_term": "dependency",
      "formula": "DG = ...",
      "description": "...",
      "interpretation": "...",
      "range": "[0, 1]"
    }
  ],
  "analytical_primitives": ["compare", "aggregate", "measure"]
}"""

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ]
        
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=40000
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def pass5_determine_classification_and_telos(self, content: str, extracted_data: Dict) -> Dict[str, Any]:
        """Pass 5: Determine proper classification and telos"""
        
        # Build summary
        core_entities = [e['indigenous_term'] for e in extracted_data.get('entities', {}).get('core_entities', [])]
        rel_count = len(extracted_data.get('relationships', {}).get('relationships', []))
        action_count = len(extracted_data.get('relationships', {}).get('actions', []))
        has_modifiers = bool(extracted_data.get('modifiers', {}).get('modifiers', []))
        has_metrics = bool(extracted_data.get('analytics', {}).get('metrics', []))
        
        summary = f"""Based on extraction:
- Core entities: {core_entities}
- Relationship types: {rel_count}
- Action types: {action_count}
- Has modifiers: {has_modifiers}
- Has metrics: {has_metrics}
"""
        
        json_example = """{
  "classification": {
    "model_type": "...",
    "reasoning_engine": "...",
    "compatible_operators": [...],
    "summary": "One sentence description"
  },
  "telos": {
    "analytical_purpose": "...",
    "level_of_analysis": "...",
    "output_format": {"type": "object"},
    "success_criteria": "..."
  }
}"""
        
        prompt = f"""Determine the classification and telos for this theory.

{summary}

CLASSIFICATION:
- model_type: What data structure best represents this theory?
  * Graph: Binary relationships between entities
  * Hypergraph: N-ary relationships
  * Tree: Hierarchical structures
  * Sequence: Ordered processes
  * Table: Matrix/classification
  * Hybrid: Multiple structures
  
- reasoning_engine: What type of analysis?
  * Graph_Engine: Network analysis
  * Iterative_Table_Engine: Classification
  * Statistical_Engine: Quantitative analysis
  * Temporal_Engine: Time-based analysis
  * Hybrid_Engine: Multiple approaches

- compatible_operators: What operations does this theory enable?

TELOS:
- analytical_purpose: Descriptive, Explanatory, Predictive, or Interventionary?
- level_of_analysis: Individual, Community, System, or Text-as-Object?
- output_format: What does the analysis produce?
- success_criteria: What indicates successful application?

Output as JSON:
{json_example}"""

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Classify this theory:\n\n{content[:30000]}"}
        ]
        
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=20000
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def final_assembly(self, paper_info: Dict, all_passes: Dict) -> Dict[str, Any]:
        """Assemble all passes into proper meta_schema_8 structure"""
        
        # Start with the classification
        classification = all_passes.get('classification', {}).get('classification', {})
        telos = all_passes.get('classification', {}).get('telos', {})
        
        # Build entities list
        entities = []
        for entity in all_passes.get('entities', {}).get('core_entities', []):
            entities.append({
                "indigenous_term": entity.get('indigenous_term'),
                "name": entity.get('indigenous_term'),  # Can be standardized
                "description": entity.get('description'),
                "examples": entity.get('examples', [])
            })
        
        # Build connections list (relationships + actions)
        connections = []
        for rel in all_passes.get('relationships', {}).get('relationships', []):
            conn = {
                "indigenous_term": rel.get('indigenous_term'),
                "description": rel.get('description'),
                "domain": rel.get('domain', []),
                "range": rel.get('range', [])
            }
            if rel.get('symbol'):
                conn['notation'] = {"symbol": rel['symbol']}
            connections.append(conn)
            
        for action in all_passes.get('relationships', {}).get('actions', []):
            connections.append({
                "indigenous_term": action.get('indigenous_term'),
                "description": action.get('description'),
                "domain": action.get('domain', ['actor']),
                "range": action.get('range', ['concept']),
                "subTypeOf": "action"
            })
        
        # Build properties list
        properties = []
        for prop in all_passes.get('entities', {}).get('entity_properties', []):
            properties.append({
                "indigenous_term": prop.get('indigenous_term'),
                "description": prop.get('description'),
                "type": prop.get('type', 'string'),
                "applies_to": prop.get('applies_to', [])
            })
            
        # Add metadata properties
        for meta in all_passes.get('modifiers', {}).get('other_metadata', []):
            properties.append({
                "indigenous_term": meta.get('indigenous_term'),
                "description": meta.get('description'),
                "type": meta.get('type', 'numeric')
            })
        
        # Build modifiers list
        modifiers = []
        for mod in all_passes.get('modifiers', {}).get('modifiers', []):
            modifiers.append({
                "indigenous_term": mod.get('indigenous_term'),
                "description": mod.get('description'),
                "category": mod.get('category'),
                "applies_to": mod.get('applies_to', [])
            })
        
        # Build the complete schema
        theory_name = paper_info.get('theory_name', 'ExtractedTheory')
        
        schema = {
            theory_name: {
                "metadata": {
                    "citation": paper_info.get('citation', 'Unknown'),
                    "annotation": paper_info.get('annotation', 'Extracted theory')
                },
                "classification": classification,
                "schema": {
                    "Ontology": {
                        "entities": entities,
                        "connections": connections,
                        "properties": properties,
                        "modifiers": modifiers
                    }
                }
            }
        }
        
        # Add Analytics if metrics exist
        metrics = all_passes.get('analytics', {}).get('metrics', [])
        if metrics:
            formatted_metrics = []
            for metric in metrics:
                formatted_metrics.append({
                    "indigenous_term": metric.get('indigenous_term'),
                    "description": metric.get('description'),
                    "formula": metric.get('formula', ''),
                    "interpretation": metric.get('interpretation', ''),
                    "range": metric.get('range', '')
                })
            schema[theory_name]["schema"]["Analytics"] = {
                "metrics": formatted_metrics,
                "analytical_primitives": all_passes.get('analytics', {}).get('analytical_primitives', [])
            }
        
        # Add Process if steps exist
        steps = all_passes.get('analytics', {}).get('process_steps', [])
        if steps:
            schema[theory_name]["schema"]["Process"] = {
                "mode": "sequential",
                "steps": [
                    {
                        "stage_name": step.get('step_name'),
                        "objective": step.get('objective', step.get('description')),
                        "completion_criteria": step.get('completion_criteria', '')
                    }
                    for step in steps
                ]
            }
        
        # Add Telos
        schema[theory_name]["schema"]["Telos"] = telos
        
        return schema
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from LLM response"""
        try:
            # Try to find JSON in the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                print("Warning: No JSON found in response")
                return {}
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            print(f"Response preview: {content[:200]}")
            return {}
    
    def extract(self, paper_path: Path, output_path: Path) -> Dict[str, Any]:
        """Run structured multi-pass extraction"""
        
        print(f"\nStructured Multi-Pass Extraction: {paper_path.name}")
        print("="*70)
        
        # Read paper
        with open(paper_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Detect paper metadata
        paper_info = {
            "theory_name": "WorldView_Theory",
            "citation": "Young, Michael D. 1996. 'Cognitive Mapping Meets Semantic Networks.' The Journal of Conflict Resolution 40(3): 395-414.",
            "annotation": "Enhanced cognitive mapping using semantic networks for representing and analyzing belief structures"
        }
        
        all_passes = {}
        
        # Pass 1: Core Entities
        print("\nPass 1: Identifying core entities...")
        all_passes['entities'] = self.pass1_identify_core_entities(content)
        entity_count = len(all_passes['entities'].get('core_entities', []))
        print(f"  ✓ Found {entity_count} core entity types")
        
        # Pass 2: Relationships and Actions
        print("\nPass 2: Extracting relationships and actions...")
        all_passes['relationships'] = self.pass2_extract_relationships_and_actions(content)
        rel_count = len(all_passes['relationships'].get('relationships', []))
        action_count = len(all_passes['relationships'].get('actions', []))
        print(f"  ✓ Found {rel_count} relationships and {action_count} actions")
        
        # Pass 3: Modifiers
        print("\nPass 3: Extracting modifiers and metadata...")
        all_passes['modifiers'] = self.pass3_extract_modifiers_and_metadata(content)
        mod_count = len(all_passes['modifiers'].get('modifiers', []))
        print(f"  ✓ Found {mod_count} modifiers")
        
        # Pass 4: Process and Analytics
        print("\nPass 4: Extracting process and analytics...")
        all_passes['analytics'] = self.pass4_extract_process_and_analytics(content)
        metric_count = len(all_passes['analytics'].get('metrics', []))
        print(f"  ✓ Found {metric_count} metrics")
        
        # Pass 5: Classification
        print("\nPass 5: Determining classification and telos...")
        all_passes['classification'] = self.pass5_determine_classification_and_telos(content, all_passes)
        print(f"  ✓ Model type: {all_passes['classification'].get('classification', {}).get('model_type')}")
        
        # Final Assembly
        print("\nFinal Assembly: Building meta_schema_8 compliant structure...")
        final_schema = self.final_assembly(paper_info, all_passes)
        
        # Validation
        print("\nValidating structure...")
        self._validate_schema(final_schema)
        
        # Save
        with open(output_path, 'w') as f:
            json.dump(final_schema, f, indent=2)
        print(f"\n✓ Saved to: {output_path}")
        
        # Summary
        self._print_summary(final_schema)
        
        return final_schema
    
    def _validate_schema(self, schema: Dict) -> bool:
        """Validate schema conforms to meta_schema_8"""
        issues = []
        
        for theory_name, theory in schema.items():
            # Check required top-level keys
            if 'metadata' not in theory:
                issues.append("Missing metadata")
            if 'classification' not in theory:
                issues.append("Missing classification")
            if 'schema' not in theory:
                issues.append("Missing schema")
                
            # Check schema structure
            if 'schema' in theory:
                if 'Ontology' not in theory['schema']:
                    issues.append("Missing Ontology")
                else:
                    ont = theory['schema']['Ontology']
                    if 'entities' not in ont:
                        issues.append("Missing entities in Ontology")
                    if 'connections' not in ont:
                        issues.append("Missing connections in Ontology")
                        
                if 'Telos' not in theory['schema']:
                    issues.append("Missing Telos")
                    
        if issues:
            print(f"  ⚠️  Validation issues: {', '.join(issues)}")
        else:
            print("  ✓ Schema structure valid")
            
        return len(issues) == 0
    
    def _print_summary(self, schema: Dict):
        """Print extraction summary"""
        print("\n" + "="*70)
        print("EXTRACTION SUMMARY")
        print("="*70)
        
        for theory_name, theory in schema.items():
            print(f"\nTheory: {theory_name}")
            
            if 'classification' in theory:
                cls = theory['classification']
                print(f"  Model Type: {cls.get('model_type')}")
                print(f"  Engine: {cls.get('reasoning_engine')}")
                
            if 'schema' in theory and 'Ontology' in theory['schema']:
                ont = theory['schema']['Ontology']
                print(f"\nOntology Components:")
                print(f"  Entities: {len(ont.get('entities', []))}")
                for e in ont.get('entities', [])[:3]:
                    print(f"    - {e.get('indigenous_term')}")
                    
                print(f"\n  Connections: {len(ont.get('connections', []))}")
                # Count relationships vs actions
                rels = [c for c in ont.get('connections', []) if c.get('subTypeOf') != 'action']
                acts = [c for c in ont.get('connections', []) if c.get('subTypeOf') == 'action']
                print(f"    - Relationships: {len(rels)}")
                print(f"    - Actions: {len(acts)}")
                
                print(f"\n  Properties: {len(ont.get('properties', []))}")
                print(f"  Modifiers: {len(ont.get('modifiers', []))}")
                
            if 'schema' in theory:
                print(f"\nOther Sections:")
                for section in ['Analytics', 'Process', 'Telos']:
                    if section in theory['schema']:
                        print(f"  ✓ {section}")

def main():
    """Test structured extraction"""
    extractor = StructuredMultiPassExtractor()
    
    paper_path = Path("/home/brian/lit_review/literature/operational_code_analysis/Cognitive Mapping Meets Semantic Networks.txt")
    output_path = Path("/home/brian/lit_review/results/cognitive_mapping_structured_v8.json")
    
    if paper_path.exists():
        result = extractor.extract(paper_path, output_path)
    else:
        print(f"Error: Paper not found at {paper_path}")

if __name__ == "__main__":
    main()