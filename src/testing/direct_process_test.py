#!/usr/bin/env python3
"""Call process_paper directly with prints"""

import os
import sys

print("Starting script...")
sys.stdout.flush()

# Add parent dir to path
sys.path.insert(0, '/home/brian/lit_review/src')
print("Added to path")
sys.stdout.flush()

# Now import
print("About to import...")
sys.stdout.flush()

from schema_creation.multiphase_processor_improved import process_paper
print("Import successful")
sys.stdout.flush()

# Process
paper_path = "/home/brian/lit_review/data/papers/computational_linguistics/sh_truncated.txt"
output_path = "/home/brian/lit_review/schemas/semantic_hypergraph/test_output.yml"

print(f"\nCalling process_paper with:")
print(f"  Input: {paper_path}")
print(f"  Output: {output_path}")
sys.stdout.flush()

try:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result = process_paper(paper_path, output_path)
    print("\nSuccess!")
    print(f"Model type: {result.get('model_type', 'NOT FOUND')}")
except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()