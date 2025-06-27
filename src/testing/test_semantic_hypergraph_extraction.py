#!/usr/bin/env python3
"""Test script to extract schema from Semantic Hypergraph paper"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema_creation.multiphase_processor_improved import (
    phase1_extract_vocabulary,
    phase2_classify_terms,
    phase3_generate_schema,
    convert_to_yaml_format
)
import yaml
import json
from pathlib import Path

def test_semantic_hypergraph():
    """Test extraction on Semantic Hypergraph paper"""
    paper_path = "/home/brian/lit_review/data/papers/computational_linguistics/menezes_roth_semantic_hypergraphs.txt"
    
    print("Reading paper...")
    with open(paper_path, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    print(f"Paper length: {len(paper_text)} characters")
    print("\nStarting Phase 1...")
    
    try:
        # Phase 1
        phase1_output = phase1_extract_vocabulary(paper_text)
        print(f"\nPhase 1 Complete!")
        print(f"- Citation: {phase1_output.citation}")
        print(f"- Theory type: {phase1_output.theory_type}")
        print(f"- Terms extracted: {len(phase1_output.vocabulary)}")
        
        # Save Phase 1 output
        output_dir = Path("/home/brian/lit_review/schemas/semantic_hypergraph")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "phase1_output.json", 'w') as f:
            json.dump(phase1_output.model_dump(), f, indent=2)
        
        # Phase 2
        print("\nStarting Phase 2...")
        phase2_output = phase2_classify_terms(phase1_output)
        print(f"\nPhase 2 Complete!")
        print(f"- Entities: {len(phase2_output.entities)}")
        print(f"- Relationships: {len(phase2_output.relationships)}")
        print(f"- Actions: {len(phase2_output.actions)}")
        
        with open(output_dir / "phase2_output.json", 'w') as f:
            json.dump(phase2_output.model_dump(), f, indent=2)
        
        # Phase 3
        print("\nStarting Phase 3...")
        phase3_output = phase3_generate_schema(phase1_output, phase2_output)
        print(f"\nPhase 3 Complete!")
        print(f"- Model type: {phase3_output.model_type}")
        print(f"- Rationale: {phase3_output.rationale[:100]}...")
        
        # Convert to YAML
        yaml_data = convert_to_yaml_format(phase1_output, phase2_output, phase3_output)
        
        with open(output_dir / "semantic_hypergraph_schema.yml", 'w') as f:
            yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"\nSchema saved to: {output_dir / 'semantic_hypergraph_schema.yml'}")
        
        # Print model type selection
        print(f"\n=== MODEL TYPE SELECTED: {phase3_output.model_type} ===")
        print(f"Rationale: {phase3_output.rationale}")
        
    except Exception as e:
        print(f"\nError during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_semantic_hypergraph()