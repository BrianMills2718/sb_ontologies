#!/usr/bin/env python3
"""Run semantic hypergraph extraction with proper error handling"""

import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema_creation.multiphase_processor_improved import process_paper

def main():
    paper_path = "/home/brian/lit_review/data/papers/computational_linguistics/menezes_roth_semantic_hypergraphs.txt"
    output_path = "/home/brian/lit_review/schemas/semantic_hypergraph/semantic_hypergraph_schema.yml"
    
    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Processing Semantic Hypergraph paper...")
    print(f"Input: {paper_path}")
    print(f"Output: {output_path}")
    
    try:
        start_time = time.time()
        result = process_paper(paper_path, output_path)
        end_time = time.time()
        
        print(f"\nProcessing completed in {end_time - start_time:.2f} seconds")
        print(f"Model type selected: {result['model_type']}")
        print(f"Total definitions: {len(result['schema_blueprint']['definitions'])}")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()