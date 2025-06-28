#!/usr/bin/env python3
"""
Apply the enhanced Semantic Hypergraph theory to Iran debate text
"""
import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def apply_semantic_hypergraph():
    """Apply semantic hypergraph theory to Iran debate"""
    
    client = OpenAI()
    
    # Load enhanced theory schema
    with open("/home/brian/lit_review/results/semantic_hypergraph_enhanced_v8.json", 'r') as f:
        theory_data = json.load(f)
    
    # Extract the theory
    theory = theory_data["Semantic_Hypergraph_Theory"]
    
    # Load Iran debate text
    with open("/home/brian/lit_review/data/test_texts/iran_debate.txt", 'r') as f:
        debate_text = f.read()
    
    # Build comprehensive prompt with ALL schema components
    system_prompt = f"""You are applying the Semantic Hypergraph theory to analyze text.

THEORY CLASSIFICATION:
{json.dumps(theory.get('classification', {}), indent=2)}

PURPOSE (Telos):
{json.dumps(theory['schema']['Telos'], indent=2)}

COMPLETE PROCESS TO FOLLOW:
{json.dumps(theory['schema']['Process'], indent=2)}

FULL ONTOLOGY WITH EXAMPLES:
{json.dumps(theory['schema']['Ontology'], indent=2)}

TYPE INFERENCE RULES (CRITICAL):
{json.dumps(theory['schema']['Axioms']['rules'], indent=2)}

These rules mean:
- (M x) -> x: Modifier + anything = that thing's type
- (B C C+) -> C: Builder + concepts = concept
- (T [C R]) -> S: Trigger + concept/relation = specifier
- (P [C R S]+) -> R: Predicate + arguments = relation
- (J x y'+) -> x: Conjunction takes type of first element

AXIOMS:
{json.dumps(theory['schema']['Axioms']['principles'], indent=2)}

CRITICAL EXAMPLES FROM PAPER:
1. "Barack Obama was born in Hawaii" → (was_born/P (+/B barack/C obama/C) (in/T hawaii/C))
2. "Berlin is nice" → (is/P berlin/C nice/C)
3. "capital of Germany" → (of/B capital/C germany/C)

KEY OPERATIONAL RULES:
- Every sentence should produce at least one hyperedge
- Multi-word entities use builders: "Barack Obama" → (+/B barack/C obama/C)
- Prepositions are usually triggers: "in Hawaii" → (in/T hawaii/C)
- Main verbs are predicates: "was born" → was_born/P
- Nested structures are allowed: relations can be arguments to other relations

Follow the 3-step Process EXACTLY:
1. Alpha: Classify each token
2. Beta: Apply type inference to build hyperedges
3. Pattern inference: Decompose conjunctions and extract additional relations"""

    user_prompt = f"""Apply Semantic Hypergraph theory to analyze this Iran debate text.

IMPORTANT: Extract semantic hypergraphs following the notation exactly:
- Use parentheses notation: (element/TYPE args...)
- Label all atoms: /C for concepts, /P for predicates, /B for builders, /T for triggers
- Build multi-word concepts with builders: (+/B word1/C word2/C)
- Apply type inference rules to determine R vs S for non-atomic edges

Extract hypergraphs for key statements about:
1. Iran's nuclear program
2. International relations and diplomacy
3. Policy positions and arguments
4. Historical events mentioned

DEBATE TEXT:
{debate_text}

For each major statement, show:
1. Original text
2. Alpha classification (token types)
3. Beta transformation (final hyperedge)
4. Any decomposed relations"""

    print("Applying Semantic Hypergraph theory to Iran debate...")
    
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
    
    # Save raw response
    with open("/home/brian/lit_review/results/iran_debate_hypergraph_raw.txt", 'w') as f:
        f.write(result)
    
    # Try to extract hypergraphs from response
    print("\n=== EXTRACTION RESULTS ===")
    
    # Count hyperedges
    hyperedge_count = result.count('(/') + result.count('(+/') + result.count('(is/') + result.count('(was/')
    print(f"Hyperedges found: ~{hyperedge_count}")
    
    # Check for key concepts
    key_concepts = ['iran', 'nuclear', 'sanctions', 'obama', 'romney']
    for concept in key_concepts:
        if f"{concept}/C" in result.lower():
            print(f"✓ Found concept: {concept}/C")
    
    # Check for relations
    if '/P' in result:
        print("✓ Found predicate relations")
    if '/B' in result:
        print("✓ Found builder constructions")
    if '/T' in result:
        print("✓ Found trigger specifiers")
    
    # Extract some example hyperedges
    print("\n=== SAMPLE HYPEREDGES ===")
    lines = result.split('\n')
    hyperedge_lines = [line for line in lines if '(/' in line or '(+/' in line]
    
    for i, line in enumerate(hyperedge_lines[:10]):
        print(f"{i+1}. {line.strip()}")
    
    # Save structured results
    structured_results = {
        "extraction_stats": {
            "approximate_hyperedges": hyperedge_count,
            "has_predicates": '/P' in result,
            "has_builders": '/B' in result,
            "has_triggers": '/T' in result,
            "has_relations": '/R' in result or '(is/P' in result
        },
        "key_concepts_found": [c for c in key_concepts if f"{c}/C" in result.lower()],
        "sample_hyperedges": hyperedge_lines[:20],
        "full_response": result
    }
    
    output_path = Path("/home/brian/lit_review/results/iran_debate_hypergraph.json")
    with open(output_path, 'w') as f:
        json.dump(structured_results, f, indent=2)
    
    print(f"\n✓ Saved to {output_path}")
    
    return structured_results

def analyze_hypergraph_quality():
    """Analyze the quality of hypergraph extraction"""
    
    with open("/home/brian/lit_review/results/iran_debate_hypergraph.json", 'r') as f:
        results = json.load(f)
    
    print("\n=== HYPERGRAPH QUALITY ANALYSIS ===")
    
    # Check complexity
    complex_edges = [e for e in results['sample_hyperedges'] if e.count('(') > 2]
    print(f"Complex nested hyperedges: {len(complex_edges)}")
    
    if complex_edges:
        print("\nExample complex edge:")
        print(complex_edges[0])
    
    # Check for all entity types
    stats = results['extraction_stats']
    coverage = sum([stats['has_predicates'], stats['has_builders'], 
                   stats['has_triggers'], stats['has_relations']])
    print(f"\nEntity type coverage: {coverage}/4")
    
    # Success criteria
    if stats['approximate_hyperedges'] > 20 and coverage >= 3:
        print("\n✅ Successful extraction - theory properly applied!")
    else:
        print("\n⚠️ Partial extraction - may need refinement")

if __name__ == "__main__":
    results = apply_semantic_hypergraph()
    
    if results:
        analyze_hypergraph_quality()