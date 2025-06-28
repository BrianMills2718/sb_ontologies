#!/usr/bin/env python3
"""
Apply WorldView theory with COMPLETE schema information
Including Process steps, Analytics, Classification, etc.
"""
import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class CompleteWorldViewApplicator:
    """Apply WorldView with full schema context"""
    
    def __init__(self):
        self.client = OpenAI()
        
    def load_theory_schema(self, schema_path: Path) -> dict:
        """Load the extracted theory schema"""
        with open(schema_path, 'r') as f:
            return json.load(f)
    
    def apply_worldview_complete(self, text: str, schema: dict) -> dict:
        """Apply WorldView with complete schema information"""
        
        # Extract ALL theory components (except citation)
        theory_name = list(schema.keys())[0]
        theory = schema[theory_name]
        
        # Build comprehensive context
        theory_context = {
            "classification": theory.get("classification", {}),
            "schema": theory.get("schema", {})
        }
        
        # Build comprehensive prompt
        prompt = f"""Apply the WorldView cognitive mapping theory using the complete theory specification below.

COMPLETE THEORY SPECIFICATION:

1. CLASSIFICATION (Theory Type & Engine):
{json.dumps(theory_context['classification'], indent=2)}

2. TELOS (Purpose & Success Criteria):
{json.dumps(theory_context['schema'].get('Telos', {}), indent=2)}

3. PROCESS (How to Apply - FOLLOW THESE STEPS):
{json.dumps(theory_context['schema'].get('Process', {}), indent=2)}

4. ONTOLOGY (Vocabulary to Use):
Components Structure:
{json.dumps(list(theory_context['schema'].get('components', {}).keys()), indent=2)}

Key Relationships: {[r['indigenous_term'] for r in theory_context['schema'].get('components', {}).get('relationships', [])[:10]]}
Key Actions: {[a['indigenous_term'] for a in theory_context['schema'].get('components', {}).get('actions', [])[:10]]}
Modifiers: {[m['indigenous_term'] for m in theory_context['schema'].get('components', {}).get('modifiers', [])[:6]]}

5. ANALYTICS (What to Measure):
{json.dumps(theory_context['schema'].get('Analytics', {}), indent=2)}

CRITICAL INSTRUCTIONS:
1. Follow the PROCESS steps exactly as specified
2. Focus on the TELOS analytical purpose (Explanatory at Individual level)
3. Extract belief structures about international relations and foreign policy
4. Use the Classification to guide your analysis approach
5. Apply Analytics metrics where possible

EXPECTED OUTPUT FORMAT:
Based on the Telos output_format and Process steps, provide:

{{
  "process_execution": {{
    "IdentifyBeliefs": [
      {{
        "subject": "entity",
        "relationship": "type from ontology",
        "object": "entity",
        "modifiers": ["temporal/modal"],
        "truth_value": "true/false/partial/possible/impossible",
        "original_text": "quote"
      }}
    ],
    "RepresentBeliefs": {{
      "concept_nodes": ["unique concepts found"],
      "relationship_nodes": ["relationships used"],
      "conjunction_nodes": ["and/or combinations"]
    }},
    "SynonymAggregation": {{
      "synonyms_found": {{"concept1": ["synonym1", "synonym2"]}},
      "aggregated_concepts": ["final concept list after merging"]
    }},
    "ComputeMeasures": {{
      "dependency": "score if calculable",
      "connectedness": "score if calculable",
      "size": "number of concepts",
      "key_concepts_by_salience": ["most frequent concepts"]
    }},
    "ReasoningModel": {{
      "key_inferences": ["what can be inferred from the belief structure"],
      "predicted_decisions": ["what decisions would follow from these beliefs"]
    }}
  }},
  "semantic_network": {{
    "summary": "Overall structure description",
    "dominant_belief_patterns": ["main patterns found"],
    "foreign_policy_worldview": "characterization of speaker's international relations beliefs"
  }},
  "success_criteria_met": {{
    "captures_belief_structure": true/false,
    "enables_structural_analysis": true/false,
    "enables_process_analysis": true/false,
    "explanation": "how well the extraction meets the Telos success criteria"
  }}
}}

TEXT TO ANALYZE:
{text}

Apply WorldView comprehensively following all Process steps."""

        messages = [
            {"role": "system", "content": "You are an expert in WorldView cognitive mapping methodology. Follow the theory's Process steps exactly."},
            {"role": "user", "content": prompt}
        ]
        
        print("Applying WorldView with complete schema context...")
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=100000
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def _parse_json_response(self, content: str) -> dict:
        """Parse JSON from response"""
        try:
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(content[json_start:json_end])
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            print(f"Response preview: {content[:500]}")
        return {}
    
    def analyze_carter_speech(self):
        """Analyze Carter speech with complete schema"""
        
        # Load Carter speech
        carter_path = Path("/home/brian/lit_review/data/test_texts/texts/carter_speech.txt")
        if not carter_path.exists():
            print(f"Error: Carter speech not found at {carter_path}")
            return
            
        with open(carter_path, 'r') as f:
            carter_text = f.read()
        
        # Load theory schema - use iterative version which has complete structure
        schema_path = Path("/home/brian/lit_review/results/cognitive_mapping_iterative_v8.iter4.json")
        if not schema_path.exists():
            print(f"Error: Schema not found at {schema_path}")
            return
            
        schema = self.load_theory_schema(schema_path)
        
        # Apply complete WorldView
        analysis = self.apply_worldview_complete(carter_text, schema)
        
        # Save results
        output_path = Path("/home/brian/lit_review/results/carter_worldview_complete.json")
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\nAnalysis saved to: {output_path}")
        
        # Print detailed summary
        self._print_summary(analysis)
        
        return analysis
    
    def _print_summary(self, analysis: dict):
        """Print analysis summary"""
        if not analysis:
            print("No valid analysis found")
            return
            
        print("\n" + "="*70)
        print("COMPLETE WORLDVIEW ANALYSIS SUMMARY")
        print("="*70)
        
        # Process execution summary
        if 'process_execution' in analysis:
            proc = analysis['process_execution']
            
            # IdentifyBeliefs
            beliefs = proc.get('IdentifyBeliefs', [])
            print(f"\n1. IdentifyBeliefs: {len(beliefs)} statements extracted")
            if beliefs:
                print("   Sample statements:")
                for stmt in beliefs[:3]:
                    print(f"   - {stmt.get('subject')} {stmt.get('relationship')} {stmt.get('object')}")
                    
            # RepresentBeliefs
            network = proc.get('RepresentBeliefs', {})
            print(f"\n2. RepresentBeliefs:")
            print(f"   - Concept nodes: {len(network.get('concept_nodes', []))}")
            print(f"   - Relationship types used: {len(network.get('relationship_nodes', []))}")
            print(f"   - Conjunctions: {len(network.get('conjunction_nodes', []))}")
            
            # SynonymAggregation
            synonyms = proc.get('SynonymAggregation', {})
            print(f"\n3. SynonymAggregation:")
            print(f"   - Synonyms found: {len(synonyms.get('synonyms_found', {}))}")
            
            # ComputeMeasures
            measures = proc.get('ComputeMeasures', {})
            print(f"\n4. ComputeMeasures:")
            print(f"   - Network size: {measures.get('size', 'N/A')}")
            print(f"   - Key concepts: {', '.join(measures.get('key_concepts_by_salience', [])[:5])}")
            
            # ReasoningModel
            reasoning = proc.get('ReasoningModel', {})
            print(f"\n5. ReasoningModel:")
            print(f"   - Key inferences: {len(reasoning.get('key_inferences', []))}")
            if reasoning.get('key_inferences'):
                print(f"     * {reasoning['key_inferences'][0][:80]}...")
                
        # Semantic network summary
        if 'semantic_network' in analysis:
            net = analysis['semantic_network']
            print(f"\nSemantic Network Analysis:")
            print(f"  Summary: {net.get('summary', 'N/A')}")
            print(f"  Foreign Policy Worldview: {net.get('foreign_policy_worldview', 'N/A')[:100]}...")
            
        # Success criteria
        if 'success_criteria_met' in analysis:
            success = analysis['success_criteria_met']
            print(f"\nSuccess Criteria Assessment:")
            print(f"  Captures belief structure: {success.get('captures_belief_structure', 'N/A')}")
            print(f"  Enables structural analysis: {success.get('enables_structural_analysis', 'N/A')}")
            print(f"  Enables process analysis: {success.get('enables_process_analysis', 'N/A')}")
            print(f"  Explanation: {success.get('explanation', 'N/A')[:100]}...")

def main():
    """Run complete analysis"""
    applicator = CompleteWorldViewApplicator()
    applicator.analyze_carter_speech()

if __name__ == "__main__":
    main()