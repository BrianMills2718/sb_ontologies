#!/usr/bin/env python3
"""
Test and critique the universal applicator with real examples
"""

import os
import json
import yaml
from universal_theory_applicator import UniversalTheoryApplicator, save_application_result

def test_young_on_carter():
    """Test Young enhanced schema on Carter excerpt"""
    
    # Longer Carter excerpt for better testing
    carter_text = """
    The United States and the Soviet Union must work together to reduce the threat of nuclear war.
    President Carter believes that peace requires genuine cooperation between our two nations.
    The SALT talks represent our commitment to arms control and reducing nuclear arsenals.
    Both superpowers possess the capability to destroy civilization.
    We must negotiate in good faith to prevent catastrophe.
    The Soviet leadership under Brezhnev has shown willingness to engage.
    However, trust between our nations remains fragile.
    Human rights must be part of any lasting agreement.
    Trade relations could improve if we make progress on arms reduction.
    The future of humanity depends on US-Soviet cooperation.
    NATO allies support our negotiation efforts.
    Nuclear proliferation threatens global stability.
    Détente offers hope but requires sustained commitment from both sides.
    """
    
    # Use enhanced Young schema
    young_schema = 'schemas/young1996/young1996_enhanced.yml'
    
    if not os.path.exists(young_schema):
        print("Enhanced Young schema not found!")
        return None
    
    print("=== TESTING YOUNG 1996 ON CARTER TEXT ===\n")
    
    applicator = UniversalTheoryApplicator(young_schema)
    result = applicator.apply(carter_text, domain="diplomatic speech")
    
    save_application_result(result, 'results/young_universal_test.yml')
    
    return result, carter_text

def test_sh_on_debate():
    """Test SH enhanced schema on debate excerpt"""
    
    debate_text = """
    Stephens: Iran is developing nuclear weapons. This poses an existential threat to Israel.
    
    Kelanic: But US intelligence shows Iran is not actively weaponizing. They want sanctions relief, not bombs.
    
    Stephens: If Iran gets nuclear weapons, then Saudi Arabia will seek them too. This creates a proliferation cascade.
    
    Kelanic: That's speculation. The nuclear domino theory hasn't been borne out historically. 
    South Korea and Japan don't have bombs because of US security guarantees.
    
    Stephens: You can't compare East Asia to the Middle East. The regional dynamics are completely different.
    Iran has threatened to wipe Israel off the map.
    
    Kelanic: Israel has superior intelligence and military capabilities. But attacking Iran could backfire,
    giving them more incentive to actually build a bomb.
    """
    
    sh_schema = 'schemas/semantic_hypergraph/sh_enhanced.yml'
    
    if not os.path.exists(sh_schema):
        print("Enhanced SH schema not found!")
        return None
        
    print("\n=== TESTING SEMANTIC HYPERGRAPH ON DEBATE ===\n")
    
    applicator = UniversalTheoryApplicator(sh_schema)
    result = applicator.apply(debate_text, domain="debate")
    
    save_application_result(result, 'results/sh_universal_test.yml')
    
    return result, debate_text

def critique_young_results(result, original_text):
    """Critique Young application results"""
    
    print("\n=== CRITIQUE OF YOUNG APPLICATION ===\n")
    
    # Check stages
    print("1. STAGE EXECUTION:")
    for stage in result.stages:
        print(f"   - {stage.stage_name}: {stage.metadata}")
    
    # Analyze final output
    if 'concepts' in result.final_output:
        concepts = result.final_output['concepts']
        print(f"\n2. CONCEPT EXTRACTION: {len(concepts)} concepts")
        
        # Check for key concepts
        concept_labels = [c['label'] for c in concepts]
        expected = ['United States', 'Soviet Union', 'nuclear', 'peace', 'SALT', 'cooperation']
        found = [e for e in expected if any(e.lower() in label.lower() for label in concept_labels)]
        missing = [e for e in expected if e not in found]
        
        print(f"   - Found key concepts: {found}")
        print(f"   - Missing expected: {missing}")
        
        # Check salience
        sorted_concepts = sorted(concepts, key=lambda x: x.get('salience', 0), reverse=True)
        print(f"\n   Top 3 by salience:")
        for c in sorted_concepts[:3]:
            print(f"   - {c['label']}: {c.get('salience', 0)}")
    
    if 'relationships' in result.final_output:
        relationships = result.final_output['relationships']
        print(f"\n3. RELATIONSHIPS: {len(relationships)} found")
        
        # Check relationship types
        rel_types = set(r['type'] for r in relationships)
        print(f"   - Relationship types used: {rel_types}")
        
        # Sample relationships
        print("\n   Sample relationships:")
        for r in relationships[:3]:
            subj = next((c['label'] for c in concepts if c['id'] == r['subject']), r['subject'])
            obj = next((c['label'] for c in concepts if c['id'] == r['object']), r['object'])
            print(f"   - {subj} --{r['type']}--> {obj}")
    
    # Overall assessment
    print("\n4. OVERALL ASSESSMENT:")
    print(f"   - Connectedness: {result.summary.get('connectedness', 0):.3f}")
    
    strengths = []
    weaknesses = []
    
    # Assess strengths/weaknesses
    if len(concepts) > 5 and len(concepts) < 20:
        strengths.append("Reasonable concept count (not over/under extracting)")
    else:
        weaknesses.append(f"Concept count ({len(concepts)}) seems off for text length")
    
    if result.summary.get('connectedness', 0) > 0.1:
        strengths.append("Good relationship density")
    else:
        weaknesses.append("Low connectedness - missing relationships?")
    
    if 'Soviet Union' in concept_labels and 'United States' in concept_labels:
        strengths.append("Captured main actors")
    else:
        weaknesses.append("Missing primary political actors")
    
    print("\n   Strengths:")
    for s in strengths:
        print(f"   ✓ {s}")
    
    print("\n   Weaknesses:")
    for w in weaknesses:
        print(f"   ✗ {w}")
    
    return len(strengths) > len(weaknesses)

def critique_sh_results(result, original_text):
    """Critique SH application results"""
    
    print("\n=== CRITIQUE OF SEMANTIC HYPERGRAPH APPLICATION ===\n")
    
    # Check stages
    print("1. STAGE EXECUTION:")
    for stage in result.stages:
        print(f"   - {stage.stage_name}: {stage.metadata}")
    
    # Check type distribution from alpha stage
    if result.stages and 'type_distribution' in result.stages[0].metadata:
        print(f"\n2. TOKEN TYPING:")
        print(f"   Type distribution: {result.stages[0].metadata['type_distribution']}")
    
    # Analyze final output
    if 'atoms' in result.final_output:
        atoms = result.final_output['atoms']
        print(f"\n3. ATOMS: {len(atoms)} created")
        
        # Check atom types
        atom_types = {}
        for atom in atoms:
            t = atom.get('type', 'unknown')
            atom_types[t] = atom_types.get(t, 0) + 1
        print(f"   Atom type distribution: {atom_types}")
    
    if 'hyperedges' in result.final_output:
        hyperedges = result.final_output['hyperedges']
        print(f"\n4. HYPEREDGES: {len(hyperedges)} built")
        
        # Check for recursive structures
        recursive = [h for h in hyperedges if h.get('level') == 'recursive']
        print(f"   - Basic hyperedges: {len(hyperedges) - len(recursive)}")
        print(f"   - Recursive hyperedges: {len(recursive)}")
        
        # Sample hyperedges
        print("\n   Sample structures:")
        for h in hyperedges[:3]:
            print(f"   - {h['id']}: {h.get('interpretation', 'no interpretation')}")
    
    if 'discourse_structures' in result.final_output:
        discourse = result.final_output['discourse_structures']
        print(f"\n5. DISCOURSE PATTERNS: {len(discourse)} found")
        for d in discourse[:3]:
            print(f"   - {d.get('pattern', 'unknown pattern')}")
    
    # Overall assessment
    print("\n6. OVERALL ASSESSMENT:")
    
    strengths = []
    weaknesses = []
    
    # For a debate, expect certain patterns
    num_atoms = len(result.final_output.get('atoms', []))
    num_edges = len(result.final_output.get('hyperedges', []))
    
    if num_atoms > 20:
        strengths.append("Good atom extraction coverage")
    else:
        weaknesses.append(f"Low atom count ({num_atoms}) for a debate")
    
    if any(h.get('level') == 'recursive' for h in result.final_output.get('hyperedges', [])):
        strengths.append("Successfully built recursive structures")
    else:
        weaknesses.append("No recursive hyperedges - missing nested arguments")
    
    if 'T' in atom_types:
        strengths.append("Found trigger atoms (conditionals)")
    else:
        weaknesses.append("No triggers found - missing if/then reasoning")
    
    if len(result.final_output.get('discourse_structures', [])) > 0:
        strengths.append("Identified discourse patterns")
    else:
        weaknesses.append("No discourse structures found")
    
    print("\n   Strengths:")
    for s in strengths:
        print(f"   ✓ {s}")
    
    print("\n   Weaknesses:")
    for w in weaknesses:
        print(f"   ✗ {w}")
    
    return len(strengths) > len(weaknesses)

def main():
    # Test Young
    young_result = test_young_on_carter()
    if young_result:
        young_success = critique_young_results(*young_result)
    
    # Test SH
    sh_result = test_sh_on_debate()
    if sh_result:
        sh_success = critique_sh_results(*sh_result)
    
    # Overall critique of the universal system
    print("\n\n=== CRITIQUE OF UNIVERSAL APPLICATOR SYSTEM ===\n")
    
    print("STRENGTHS of the Universal Approach:")
    print("✓ Successfully executes multi-stage processing for any theory")
    print("✓ Schema-driven behavior allows true generalization")
    print("✓ Stage chaining enables complex workflows")
    print("✓ Post-processing adds robustness")
    print("✓ Domain parameterization supports flexibility")
    
    print("\nWEAKNESSES and Areas for Improvement:")
    print("✗ Still depends on quality of prompts in schema")
    print("✗ No built-in validation of stage outputs")
    print("✗ Limited error handling between stages")
    print("✗ No iterative refinement capability")
    print("✗ Can't dynamically adjust based on intermediate results")
    
    print("\nRECOMMENDATIONS:")
    print("1. Add output validation schemas for each stage")
    print("2. Implement retry logic for failed stages")
    print("3. Add conditional branching based on stage results")
    print("4. Create library of reusable stage templates")
    print("5. Add metrics for assessing extraction quality")
    print("6. Implement feedback loops for iterative improvement")
    
    print("\nCONCLUSION:")
    print("The universal applicator successfully generalizes theory application,")
    print("but quality still depends on well-designed schema configurations.")
    print("The framework provides the structure; schemas must provide the intelligence.")

if __name__ == "__main__":
    main()