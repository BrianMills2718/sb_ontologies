#!/usr/bin/env python3
"""Minimal test of semantic hypergraph extraction"""

import os
import sys
import time
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional

# Load environment
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Minimal schema
class VocabularyTerm(BaseModel):
    term: str = Field(description="The theoretical term")
    definition: str = Field(description="Brief definition")

class Phase1Output(BaseModel):
    citation: str = Field(description="Citation")
    vocabulary: List[VocabularyTerm] = Field(description="Key terms")

# Read first part of paper
print("Reading paper...")
with open("/home/brian/lit_review/semantic_hypergraphs.txt", 'r') as f:
    # Just first 2000 chars to test
    paper_text = f.read(2000)

print(f"Testing with {len(paper_text)} characters...")

prompt = f"""Extract key theoretical vocabulary from this paper excerpt:

{paper_text}

Focus on core concepts like 'Semantic Hypergraph', 'hyperedge', 'connector', etc."""

try:
    print("\nCalling OpenAI API...")
    start = time.time()
    
    response = client.beta.chat.completions.parse(
        model="o3",
        messages=[
            {"role": "system", "content": "Extract theoretical vocabulary from academic papers"},
            {"role": "user", "content": prompt}
        ],
        response_format=Phase1Output
    )
    
    end = time.time()
    print(f"\nSuccess! Time: {end-start:.2f} seconds")
    
    result = response.choices[0].message.parsed
    print(f"\nCitation: {result.citation}")
    print(f"Terms found: {len(result.vocabulary)}")
    for term in result.vocabulary[:5]:
        print(f"  - {term.term}: {term.definition[:50]}...")
        
except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()