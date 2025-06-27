#!/usr/bin/env python3
"""
Standalone script to extract schema from Semantic Hypergraph paper with timing
Run this manually to avoid timeout issues
"""

import time
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from schema_creation.multiphase_processor_improved import (
    phase1_extract_vocabulary,
    phase2_classify_terms,
    phase3_generate_schema,
    convert_to_yaml_format
)
import yaml
import json

def run_extraction():
    """Run the full extraction with detailed timing"""
    
    # File paths
    paper_path = "semantic_hypergraphs.txt"
    output_path = "schemas/semantic_hypergraph/semantic_hypergraph_complete.yml"
    
    print("=" * 70)
    print("SEMANTIC HYPERGRAPH SCHEMA EXTRACTION")
    print("=" * 70)
    
    # Check if paper exists
    if not os.path.exists(paper_path):
        print(f"ERROR: Paper not found at {paper_path}")
        return
    
    # Read paper
    print(f"\n1. Reading paper from: {paper_path}")
    start_total = time.time()
    
    with open(paper_path, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    print(f"   - Paper length: {len(paper_text):,} characters")
    print(f"   - Paper length: {len(paper_text.split()):,} words (approx)")
    
    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        # Phase 1: Vocabulary Extraction
        print(f"\n2. PHASE 1: Vocabulary Extraction")
        print(f"   Starting at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        start_phase1 = time.time()
        
        phase1_output = phase1_extract_vocabulary(paper_text)
        
        end_phase1 = time.time()
        phase1_time = end_phase1 - start_phase1
        
        print(f"   ✓ Complete in: {phase1_time:.2f} seconds")
        print(f"   - Extracted terms: {len(phase1_output.vocabulary)}")
        print(f"   - Theory type: {phase1_output.theory_type}")
        print(f"   - Citation: {phase1_output.citation[:50]}...")
        
        # Save Phase 1 output
        debug_dir = Path("schemas/semantic_hypergraph/debug")
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        with open(debug_dir / "phase1_output.json", 'w') as f:
            json.dump(phase1_output.model_dump(), f, indent=2)
        
        # Phase 2: Ontological Classification
        print(f"\n3. PHASE 2: Ontological Classification")
        print(f"   Starting at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        start_phase2 = time.time()
        
        phase2_output = phase2_classify_terms(phase1_output)
        
        end_phase2 = time.time()
        phase2_time = end_phase2 - start_phase2
        
        print(f"   ✓ Complete in: {phase2_time:.2f} seconds")
        print(f"   - Entities: {len(phase2_output.entities)}")
        print(f"   - Relationships: {len(phase2_output.relationships)}")
        print(f"   - Actions: {len(phase2_output.actions)}")
        print(f"   - Properties: {len(phase2_output.properties)}")
        print(f"   - Measures: {len(phase2_output.measures)}")
        print(f"   - Modifiers: {len(phase2_output.modifiers)}")
        print(f"   - Truth values: {len(phase2_output.truth_values)}")
        print(f"   - Operators: {len(phase2_output.operators)}")
        
        # Save Phase 2 output
        with open(debug_dir / "phase2_output.json", 'w') as f:
            json.dump(phase2_output.model_dump(), f, indent=2)
        
        # Phase 3: Schema Generation
        print(f"\n4. PHASE 3: Schema Generation")
        print(f"   Starting at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        start_phase3 = time.time()
        
        phase3_output = phase3_generate_schema(phase1_output, phase2_output)
        
        end_phase3 = time.time()
        phase3_time = end_phase3 - start_phase3
        
        print(f"   ✓ Complete in: {phase3_time:.2f} seconds")
        print(f"   - Model type: {phase3_output.model_type}")
        print(f"   - Rationale: {phase3_output.rationale[:100]}...")
        print(f"   - Node types: {len(phase3_output.node_types)}")
        print(f"   - Edge types: {len(phase3_output.edge_types)}")
        
        # Save Phase 3 output
        with open(debug_dir / "phase3_output.json", 'w') as f:
            json.dump(phase3_output.model_dump(), f, indent=2)
        
        # Convert to YAML
        print(f"\n5. Converting to YAML format...")
        yaml_data = convert_to_yaml_format(phase1_output, phase2_output, phase3_output)
        
        # Save final output
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"   ✓ Saved to: {output_path}")
        
        # Total time
        end_total = time.time()
        total_time = end_total - start_total
        
        print("\n" + "=" * 70)
        print("EXTRACTION COMPLETE")
        print("=" * 70)
        print(f"Phase 1 (Vocabulary):     {phase1_time:6.2f} seconds")
        print(f"Phase 2 (Classification): {phase2_time:6.2f} seconds")
        print(f"Phase 3 (Schema):         {phase3_time:6.2f} seconds")
        print("-" * 30)
        print(f"TOTAL TIME:               {total_time:6.2f} seconds")
        print("=" * 70)
        
        # Show key results
        print(f"\nKEY RESULTS:")
        print(f"- Model Type: {phase3_output.model_type}")
        print(f"- Total Definitions: {len(yaml_data['schema_blueprint']['definitions'])}")
        
        # Check for hypergraph concepts
        hypergraph_terms = [d['name'] for d in yaml_data['schema_blueprint']['definitions'] 
                           if 'hypergraph' in d['name'].lower() or 'hyperedge' in d['name'].lower()]
        if hypergraph_terms:
            print(f"- Hypergraph concepts found: {', '.join(hypergraph_terms)}")
        
    except KeyboardInterrupt:
        print("\n\nINTERRUPTED by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("Starting Semantic Hypergraph extraction...")
    print(f"Using OpenAI model: {os.getenv('OPENAI_MODEL', 'Not set')}")
    run_extraction()