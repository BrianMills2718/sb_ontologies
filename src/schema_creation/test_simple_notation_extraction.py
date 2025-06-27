#!/usr/bin/env python3
"""
Simple test to extract notation patterns from SH paper
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import yaml
from pathlib import Path

# Load environment
load_dotenv()
client = OpenAI()

def extract_notations(paper_path: str):
    """Simple extraction focused on notation"""
    
    # Load paper text
    with open(paper_path, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    # Focus on the methodology section
    prompt = f"""
Analyze this Semantic Hypergraph paper and extract ALL notation systems and patterns.

Focus on:
1. Argument role codes (like P.sa, B.ma, P.soa)
2. Special symbols (+/B, :/J, *)
3. Pattern matching rules
4. Type system (C, P, M, B, T, J, R, S)

Look in examples, figures, and methodology sections.

PAPER TEXT (methodology section):
{paper_text[15000:25000]}

Provide a detailed list of all notations found with their meanings.
"""

    response = client.chat.completions.create(
        model="o3",
        messages=[
            {"role": "system", "content": "You are an expert at extracting notation systems."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def main():
    paper_path = "/home/brian/lit_review/data/papers/computational_linguistics/menezes_roth_semantic_hypergraphs.txt"
    result = extract_notations(paper_path)
    
    # Save result
    output_dir = Path("/home/brian/lit_review/results/semantic_hypergraph/enhanced_extraction")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "sh_notation_simple.txt", 'w') as f:
        f.write(result)
    
    print("Extraction complete!")
    print("\n" + "="*60)
    print(result[:1000] + "...")

if __name__ == "__main__":
    main()