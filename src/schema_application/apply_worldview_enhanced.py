#!/usr/bin/env python3
"""
Apply the ENHANCED WorldView theory to Carter's speech
Using the improved schema that includes coding examples
"""
import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def apply_enhanced_worldview():
    """Apply enhanced WorldView schema with coding examples"""
    
    client = OpenAI()
    
    # Load enhanced theory schema
    with open("/home/brian/lit_review/results/cognitive_mapping_enhanced_v8.json", 'r') as f:
        theory_data = json.load(f)
    
    # Extract the theory
    theory = list(theory_data.values())[0]
    
    # Load Carter speech
    with open("/home/brian/lit_review/data/test_texts/texts/carter_speech.txt", 'r') as f:
        speech_text = f.read()
    
    # Build comprehensive prompt with ALL schema components AND examples
    system_prompt = f"""You are applying the WorldView cognitive mapping theory to analyze text.

CRITICAL THEORY CONTEXT:
{json.dumps(theory.get('classification', {}), indent=2)}

PURPOSE (Telos):
{json.dumps(theory['schema']['Telos'], indent=2)}

COMPLETE PROCESS TO FOLLOW:
{json.dumps(theory['schema']['Process'], indent=2)}

FULL ONTOLOGY WITH EXAMPLES:
{json.dumps(theory['schema']['Ontology'], indent=2)}

CRITICAL CODING EXAMPLE FROM PAPER:
The paper shows this example: "SALT attribute lowest-common-denominator"
This means when you see a statement like "SALT becomes the lowest common denominator", you code it as:
- Subject: SALT
- Relationship: attribute
- Object: lowest-common-denominator

ANALYTICS TO COMPUTE:
{json.dumps(theory['schema']['Analytics'], indent=2)}

AXIOMS (Core Principles):
{json.dumps(theory['schema']['Axioms'], indent=2)}

KEY INNOVATION - COMPOUND STATEMENTS:
WorldView's main innovation is that relationships can become nodes themselves. This allows coding complex nested statements. When you see conditional or compound statements:
1. Code the inner statement first
2. Make that relationship a node
3. Connect it to other concepts

EXTRACTION DENSITY:
Academic papers using WorldView extract 50-100+ statements from speeches. Almost every sentence contains codable beliefs. Don't just extract major policy positions - code ALL beliefs about:
- Actors and their attributes
- Causal relationships
- Conditional statements
- Value judgments
- Temporal assertions

Follow the 5-step Process EXACTLY. Extract ALL belief statements, not just major ones."""

    user_prompt = f"""Apply WorldView theory to analyze this speech by Jimmy Carter. 

Follow all 5 Process steps systematically:
1. IdentifyStatements - Extract EVERY subject-relationship-object assertion
2. AssignModifiersAndTruthValues - Add temporal, modal, truth modifiers
3. ConstructSemanticNetwork - Build the network, making relationships into nodes where needed
4. ApplySynonymFacility - Unify similar concepts
5. ConductAnalysisOrReasoning - Compute metrics and generate insights

SPEECH TEXT:
{speech_text}

Remember: Extract densely (50+ statements expected), use the full range of relationship types, and apply the SALT coding example pattern to similar statements."""

    print("Applying enhanced WorldView theory to Carter speech...")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = client.chat.completions.create(
        model="o1",
        messages=messages,
        max_completion_tokens=100000
    )
    
    result = response.choices[0].message.content
    
    # Save raw response for debugging
    with open("/home/brian/lit_review/results/carter_worldview_enhanced_raw.txt", 'w') as f:
        f.write(result)
    
    # Parse JSON from response
    json_start = result.find('{')
    json_end = result.rfind('}') + 1
    
    if json_start != -1 and json_end > json_start:
        try:
            result_data = json.loads(result[json_start:json_end])
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Attempting to extract JSON substring...")
            # Try to find a complete JSON object
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                result_data = json.loads(json_match.group())
            else:
                raise
        
        # Save results
        output_path = Path("/home/brian/lit_review/results/carter_worldview_enhanced.json")
        with open(output_path, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"\n✓ Saved to {output_path}")
        
        # Analyze results
        print("\n=== ENHANCED APPLICATION RESULTS ===")
        
        if 'process_execution' in result_data:
            beliefs = result_data['process_execution'].get('IdentifyBeliefs', [])
            print(f"\nTotal statements extracted: {len(beliefs)}")
            
            # Check for SALT example
            salt_found = False
            compound_statements = 0
            relationship_types = set()
            
            for belief in beliefs:
                if 'SALT' in belief.get('subject', '') or 'SALT' in belief.get('object', ''):
                    salt_found = True
                    print(f"\n✓ FOUND SALT REFERENCE:")
                    print(f"  {belief}")
                
                rel_type = belief.get('relationship', '')
                relationship_types.add(rel_type)
                
                # Check for compound structures
                if 'if-then' in rel_type or belief.get('nested_statement'):
                    compound_statements += 1
            
            print(f"\nRelationship types used: {len(relationship_types)}")
            print(f"Types: {sorted(relationship_types)}")
            print(f"\nCompound statements found: {compound_statements}")
            
            if not salt_found:
                print("\n❌ Still missing SALT 'lowest common denominator' example")
            
            # Check extraction density
            if len(beliefs) < 30:
                print(f"\n⚠️ Low extraction density: {len(beliefs)} statements (expected 50+)")
            else:
                print(f"\n✓ Good extraction density: {len(beliefs)} statements")
                
        return result_data
    else:
        print("ERROR: Could not parse JSON response")
        return None

def compare_with_previous():
    """Compare enhanced results with previous attempts"""
    
    # Load previous attempts
    attempts = {
        "First (partial)": "/home/brian/lit_review/results/carter_worldview_application.json",
        "Second (focused)": "/home/brian/lit_review/results/carter_worldview_focused.json", 
        "Third (complete)": "/home/brian/lit_review/results/carter_worldview_complete.json",
        "Enhanced": "/home/brian/lit_review/results/carter_worldview_enhanced.json"
    }
    
    print("\n=== COMPARISON OF ALL ATTEMPTS ===")
    
    for name, path in attempts.items():
        if Path(path).exists():
            with open(path, 'r') as f:
                data = json.load(f)
            
            beliefs = []
            if 'process_execution' in data:
                beliefs = data['process_execution'].get('IdentifyBeliefs', [])
            elif 'beliefs' in data:
                beliefs = data['beliefs']
            elif 'statements' in data:
                beliefs = data['statements']
            
            print(f"\n{name}: {len(beliefs)} statements")
            
            # Check for key content
            has_salt = any('SALT' in str(b) for b in beliefs)
            has_billy = any('Billy' in str(b) for b in beliefs)
            
            if has_salt:
                print("  ✓ Contains SALT references")
            if has_billy:
                print("  ⚠️ Contains trivial Billy Carter content")

if __name__ == "__main__":
    result = apply_enhanced_worldview()
    
    if result:
        compare_with_previous()