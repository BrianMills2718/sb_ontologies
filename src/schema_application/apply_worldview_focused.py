#!/usr/bin/env python3
"""
Apply WorldView theory with focus on its PURPOSE:
Analyzing political belief structures and decision-making
"""
import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class FocusedWorldViewApplicator:
    """Apply WorldView with emphasis on theory purpose"""
    
    def __init__(self):
        self.client = OpenAI()
        
    def load_theory_schema(self, schema_path: Path) -> dict:
        """Load the extracted theory schema"""
        with open(schema_path, 'r') as f:
            return json.load(f)
    
    def apply_worldview_focused(self, text: str, schema: dict) -> dict:
        """Apply WorldView with focus on political beliefs and decision-making"""
        
        # Extract theory details including Telos
        theory = list(schema.values())[0]
        components = theory.get('schema', {}).get('components', {})
        telos = theory.get('schema', {}).get('Telos', {})
        
        # Build focused prompt
        prompt = f"""Apply WorldView cognitive mapping theory to analyze this political speech.

CRITICAL CONTEXT - THEORY PURPOSE (from paper and Telos):
- PURPOSE: {telos.get('analytical_purpose', 'Explanatory')} - Explain how leaders view their external environment
- LEVEL: {telos.get('level_of_analysis', 'Individual')} - Focus on the speaker's belief structure
- GOAL: {telos.get('success_criteria', 'Capture belief structure for meaningful analysis')}
- FOCUS AREAS: Foreign policy beliefs, international relations, crisis decisions, state behavior

The paper demonstrates this with Carter's SALT treaty statement showing complex policy reasoning.

THEORY COMPONENTS:
Relationships: {[r['indigenous_term'] for r in components.get('relationships', [])[:15]]}
Actions: {[a['indigenous_term'] for a in components.get('actions', [])[:15]]}
Modifiers: past, present, future, goal, hypothetical, normative
Truth Values: true, false, partial, possible, impossible

EXTRACTION PRIORITIES:
1. FOREIGN POLICY STATEMENTS - US-Soviet relations, nuclear weapons, treaties, international cooperation
2. BELIEF STRUCTURES - What the speaker believes about international actors and their relationships
3. DECISION REASONING - If-then statements, goals, hypothetical scenarios
4. COMPLEX STATEMENTS - Nested/compound structures (WorldView's key innovation)

IGNORE trivial content (travel plans, personal anecdotes) unless they reveal beliefs about international relations.

For the SALT example pattern, look for statements like:
"If [treaty/policy] becomes [condition], then [consequence for international relations]"

REQUIRED OUTPUT:
{{
  "belief_structure": {{
    "core_beliefs": [
      {{
        "about": "what entity/relationship",
        "belief": "what speaker believes",
        "evidence": "statement(s) showing this",
        "certainty": "truth value"
      }}
    ],
    "foreign_policy_positions": [
      {{
        "topic": "SALT/nuclear/Soviet relations/etc",
        "position": "speaker's stance",
        "reasoning": "if-then logic or causal beliefs"
      }}
    ],
    "key_relationships": [
      {{
        "subject": "international actor",
        "relationship": "type from theory",
        "object": "international actor/concept",
        "modifier": "temporal/modal",
        "significance": "why this matters for policy"
      }}
    ],
    "compound_statements": [
      {{
        "structure": "nested statement description",
        "components": ["part1", "part2"],
        "original_text": "quote"
      }}
    ]
  }},
  "worldview_analysis": {{
    "dominant_concerns": ["main international issues"],
    "temporal_orientation": "past/present/future focus",
    "certainty_level": "how certain/uncertain about beliefs",
    "policy_implications": ["what actions follow from beliefs"]
  }}
}}

TEXT TO ANALYZE:
{text}

Focus on substantive foreign policy content that reveals the speaker's worldview about international relations."""

        messages = [
            {"role": "system", "content": "You are an expert in cognitive mapping of political belief systems, especially foreign policy beliefs."},
            {"role": "user", "content": prompt}
        ]
        
        print("Applying WorldView with focus on political beliefs...")
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
        """Analyze Carter speech with proper focus"""
        
        # Load Carter speech
        carter_path = Path("/home/brian/lit_review/data/test_texts/texts/carter_speech.txt")
        if not carter_path.exists():
            print(f"Error: Carter speech not found at {carter_path}")
            return
            
        with open(carter_path, 'r') as f:
            carter_text = f.read()
        
        # Load theory schema
        schema_path = Path("/home/brian/lit_review/results/cognitive_mapping_iterative_v8.iter4.json")
        if not schema_path.exists():
            # Try structured extraction instead
            schema_path = Path("/home/brian/lit_review/results/cognitive_mapping_structured_v8.json")
            
        schema = self.load_theory_schema(schema_path)
        
        # Apply focused WorldView
        analysis = self.apply_worldview_focused(carter_text, schema)
        
        # Save results
        output_path = Path("/home/brian/lit_review/results/carter_worldview_focused.json")
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\nAnalysis saved to: {output_path}")
        
        # Print summary
        self._print_summary(analysis)
        
        return analysis
    
    def _print_summary(self, analysis: dict):
        """Print analysis summary"""
        if not analysis or 'belief_structure' not in analysis:
            print("No valid analysis found")
            return
            
        beliefs = analysis['belief_structure']
        
        print("\n" + "="*60)
        print("FOCUSED WORLDVIEW ANALYSIS")
        print("="*60)
        
        print(f"\nCore Beliefs: {len(beliefs.get('core_beliefs', []))}")
        for belief in beliefs.get('core_beliefs', [])[:3]:
            print(f"  - About {belief.get('about')}: {belief.get('belief')[:60]}...")
            
        print(f"\nForeign Policy Positions: {len(beliefs.get('foreign_policy_positions', []))}")
        for pos in beliefs.get('foreign_policy_positions', [])[:3]:
            print(f"  - {pos.get('topic')}: {pos.get('position')[:60]}...")
            
        print(f"\nKey International Relationships: {len(beliefs.get('key_relationships', []))}")
        for rel in beliefs.get('key_relationships', [])[:5]:
            print(f"  - {rel.get('subject')} {rel.get('relationship')} {rel.get('object')}")
            
        print(f"\nCompound Statements: {len(beliefs.get('compound_statements', []))}")
        
        if 'worldview_analysis' in analysis:
            wa = analysis['worldview_analysis']
            print(f"\nDominant Concerns: {', '.join(wa.get('dominant_concerns', [])[:3])}")
            print(f"Temporal Orientation: {wa.get('temporal_orientation')}")
            print(f"Certainty Level: {wa.get('certainty_level')}")

def main():
    """Run focused analysis"""
    applicator = FocusedWorldViewApplicator()
    applicator.analyze_carter_speech()

if __name__ == "__main__":
    main()