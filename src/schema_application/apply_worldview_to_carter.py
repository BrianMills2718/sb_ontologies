#!/usr/bin/env python3
"""
Apply WorldView theory (from iterative extraction) to Carter's speech
Then compare with Young's analysis
"""
import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class WorldViewApplicator:
    """Apply WorldView cognitive mapping to text"""
    
    def __init__(self):
        self.client = OpenAI()
        
    def load_theory_schema(self, schema_path: Path) -> dict:
        """Load the extracted theory schema"""
        with open(schema_path, 'r') as f:
            return json.load(f)
    
    def apply_worldview(self, text: str, schema: dict) -> dict:
        """Apply WorldView theory to analyze text"""
        
        # Extract the schema details
        theory = list(schema.values())[0]  # Get first theory
        components = theory.get('schema', {}).get('components', {})
        
        # Build comprehensive prompt
        prompt = f"""Apply the WorldView cognitive mapping theory to analyze this text.

WORLDVIEW THEORY COMPONENTS:

Entities:
{json.dumps(components.get('entities', []), indent=2)}

Relationships (differentiated types):
{json.dumps(components.get('relationships', []), indent=2)}

Actions (events/verbs):
{json.dumps(components.get('actions', []), indent=2)}

Modifiers (temporal/modal):
{json.dumps(components.get('modifiers', []), indent=2)}

Truth Values: true, false, partial, possible, impossible

TASK:
1. Extract all statements as subject-relationship-object triples
2. Code each relationship using the exact categories above
3. Apply modifiers (past/present/future/goal/hypothetical/normative)
4. Assign truth values where applicable
5. Note salience (frequency of repetition)
6. Identify conjunctions (and/or) combining concepts

OUTPUT FORMAT:
{{
  "cognitive_map": {{
    "concepts": [
      {{
        "concept": "exact term from text",
        "type": "what kind of concept",
        "salience": frequency count
      }}
    ],
    "statements": [
      {{
        "subject": "concept or conjunction",
        "relationship": "exact relationship type from theory",
        "object": "concept or conjunction",
        "modifier": "temporal/modal modifier if any",
        "truth_value": "true/false/partial/possible/impossible",
        "original_text": "quote from source"
      }}
    ],
    "conjunctions": [
      {{
        "type": "and/or",
        "concepts": ["concept1", "concept2"],
        "context": "how used"
      }}
    ]
  }},
  "structural_analysis": {{
    "dominant_relationships": ["most frequent relationship types"],
    "temporal_focus": "past/present/future based on modifiers",
    "key_concepts": ["most salient concepts"],
    "belief_certainty": "analysis of truth values used"
  }}
}}

TEXT TO ANALYZE:
{text}

Apply WorldView theory comprehensively, coding EVERY statement possible."""

        messages = [
            {"role": "system", "content": "You are an expert in WorldView cognitive mapping analysis."},
            {"role": "user", "content": prompt}
        ]
        
        print("Applying WorldView theory to text...")
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=80000
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def _parse_json_response(self, content: str) -> dict:
        """Parse JSON from response"""
        try:
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(content[json_start:json_end])
        except:
            pass
        return {}
    
    def analyze_carter_speech(self):
        """Main analysis workflow"""
        
        # Load Carter speech
        carter_path = Path("/home/brian/lit_review/data/test_texts/texts/carter_speech.txt")
        if not carter_path.exists():
            print(f"Error: Carter speech not found at {carter_path}")
            return
            
        with open(carter_path, 'r') as f:
            carter_text = f.read()
        
        # Load best theory schema (iterative extraction iter4)
        schema_path = Path("/home/brian/lit_review/results/cognitive_mapping_iterative_v8.iter4.json")
        if not schema_path.exists():
            print(f"Error: Schema not found at {schema_path}")
            return
            
        schema = self.load_theory_schema(schema_path)
        
        # Apply WorldView
        analysis = self.apply_worldview(carter_text, schema)
        
        # Save results
        output_path = Path("/home/brian/lit_review/results/carter_worldview_analysis.json")
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\nAnalysis saved to: {output_path}")
        
        # Print summary
        self._print_summary(analysis)
        
        return analysis
    
    def _print_summary(self, analysis: dict):
        """Print analysis summary"""
        if not analysis or 'cognitive_map' not in analysis:
            print("No valid analysis found")
            return
            
        cog_map = analysis['cognitive_map']
        
        print("\n" + "="*60)
        print("WORLDVIEW ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\nConcepts found: {len(cog_map.get('concepts', []))}")
        print(f"Statements coded: {len(cog_map.get('statements', []))}")
        print(f"Conjunctions: {len(cog_map.get('conjunctions', []))}")
        
        # Count relationship types
        rel_types = {}
        for stmt in cog_map.get('statements', []):
            rel = stmt.get('relationship', 'unknown')
            rel_types[rel] = rel_types.get(rel, 0) + 1
        
        print("\nRelationship type distribution:")
        for rel, count in sorted(rel_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {rel}: {count}")
        
        # Count modifiers
        mod_types = {}
        for stmt in cog_map.get('statements', []):
            mod = stmt.get('modifier', 'none')
            if mod and mod != 'none':
                mod_types[mod] = mod_types.get(mod, 0) + 1
        
        print("\nModifier distribution:")
        for mod, count in sorted(mod_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {mod}: {count}")
        
        # Structural analysis
        if 'structural_analysis' in analysis:
            struct = analysis['structural_analysis']
            print("\nStructural Analysis:")
            print(f"  Temporal focus: {struct.get('temporal_focus', 'N/A')}")
            print(f"  Key concepts: {', '.join(struct.get('key_concepts', [])[:5])}")
            print(f"  Dominant relationships: {', '.join(struct.get('dominant_relationships', [])[:3])}")

def main():
    """Run the analysis"""
    applicator = WorldViewApplicator()
    applicator.analyze_carter_speech()

if __name__ == "__main__":
    main()